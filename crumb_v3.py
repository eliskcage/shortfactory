"""
CRUMB v3 — Smear-The-Teeth (28 Apr 2026)
=========================================
Decoder-only evolution of v2. Same encoded `.crumb.v2` file format —
the encoder is unchanged. v3 changes how playback reads the genome.

DAN'S DIAGNOSIS: "the noise feels like a needle being dragged on a
comb so smear the teeth and we have real smooth compression."

WHY v2 STILL CLICKED: the encoded file gives one mag/peak/phase
slice per 23 ms frame. Playback applies these as discrete steps —
each frame boundary is a tooth. Tiny discontinuities pile up into
narrow spectral lines distributed through the mid band.

v3 SMEARS THE TEETH THREE WAYS:
  1. Time-smooth the linear magnitude with a 5-frame Hann (softens
     the sharp edge between frames).
  2. Upsample mel + peaks 2× along time (linear interp, phase
     unwrap-then-wrap) — finer transitions, no hard steps.
  3. Synthesise + Griffin-Lim at hop/2 = 256 → 87.5% overlap-add,
     a much smoother reconstruction window.

WHAT GETS STORED (vs v1):
  v1:  zlib(header + 6-bit mel-dB)             → 186 KB
  v2:  zlib(header + 6-bit mel + peak block)   → ~229 KB
       peak block = K=6 peaks/frame × (10-bit bin, 5-bit phase)
  v3:  same format as v2 — file is identical, decoder is the change.

DECODER:
  unpack mel + peaks → stabilize peak tracks → upsample 2× along
  time → smear mag → sharpen at peak bins → 1 kHz safety notch →
  carrier seed at fine hop → Griffin-Lim 80 iters at fine hop → ISTFT

Honest expectation: should bring spectral sim from 0.80 → ~0.88+
and reduce the whispery character on pitched content (vocals,
sustained notes). Noise/transients still ride on the mel path.

Usage: python crumb_v2.py <audiofile.mp3|wav>
"""

import numpy as np
import scipy.io.wavfile as wavfile
import scipy.signal as ssig
import json, sys, os, subprocess, tempfile, zlib, struct
from pathlib import Path


# ─── CONFIG ──────────────────────────────────────────────────────────────────

SR        = 22050
N_FFT     = 2048
HOP       = 512
N_MELS    = 80
MEL_BITS  = 6        # 64 levels per mel bin
N_PEAKS   = 6        # peaks per frame
FREQ_BITS = 10       # bin index 0..1023 (n_fft/2 = 1024)
PHASE_BITS = 5       # 32 phase levels = ~11° steps
GL_ITERS  = 80       # Griffin-Lim iterations


# ─── AUDIO IO ────────────────────────────────────────────────────────────────

def load_audio(path, target_sr=SR):
    ext = Path(path).suffix.lower()
    if ext == '.wav':
        sr, data = wavfile.read(path)
    else:
        tmp = tempfile.mktemp(suffix='.wav')
        subprocess.run([
            'ffmpeg', '-y', '-i', path, '-ar', str(target_sr),
            '-ac', '1', '-sample_fmt', 's16', tmp
        ], capture_output=True)
        sr, data = wavfile.read(tmp)
        os.unlink(tmp)
    if data.ndim > 1:
        data = data.mean(axis=1)
    data = data.astype(np.float32)
    if np.max(np.abs(data)) > 1.0:
        data /= 32768.0
    if sr != target_sr:
        data = ssig.resample(data, int(len(data) * target_sr / sr))
        sr = target_sr
    return data, sr


# ─── STFT / ISTFT ────────────────────────────────────────────────────────────

def stft(audio, n_fft=N_FFT, hop=HOP):
    win = np.hanning(n_fft).astype(np.float32)
    pad = n_fft // 2
    audio = np.pad(audio, pad, mode='reflect')
    n_frames = 1 + (len(audio) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n_frames)[:, None]
    frames = audio[idx] * win
    return np.fft.rfft(frames, axis=1).T

def istft(spec, hop=HOP, n_fft=N_FFT):
    win = np.hanning(n_fft).astype(np.float32)
    n_frames = spec.shape[1]
    pad = n_fft // 2
    out_len = n_fft + hop * (n_frames - 1)
    out = np.zeros(out_len, dtype=np.float32)
    norm = np.zeros(out_len, dtype=np.float32)
    frames = np.fft.irfft(spec.T, n=n_fft, axis=1).astype(np.float32)
    for i in range(n_frames):
        out[i * hop:i * hop + n_fft] += frames[i] * win
        norm[i * hop:i * hop + n_fft] += win ** 2
    out /= np.maximum(norm, 1e-8)
    return out[pad:-pad] if out.shape[0] > 2 * pad else out


# ─── MEL FILTERBANK ──────────────────────────────────────────────────────────

def hz_to_mel(f): return 2595.0 * np.log10(1.0 + f / 700.0)
def mel_to_hz(m): return 700.0 * (10.0 ** (m / 2595.0) - 1.0)

def make_mel_filterbank(sr=SR, n_fft=N_FFT, n_mels=N_MELS, fmin=20.0, fmax=None):
    if fmax is None:
        fmax = sr / 2
    mel_pts = np.linspace(hz_to_mel(fmin), hz_to_mel(fmax), n_mels + 2)
    hz_pts = mel_to_hz(mel_pts)
    bin_freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    fb = np.zeros((n_mels, len(bin_freqs)), dtype=np.float32)
    for i in range(n_mels):
        lo, mid, hi = hz_pts[i], hz_pts[i + 1], hz_pts[i + 2]
        left = (bin_freqs - lo) / (mid - lo + 1e-12)
        right = (hi - bin_freqs) / (hi - mid + 1e-12)
        fb[i] = np.clip(np.minimum(left, right), 0, None)
        area = (hi - lo) / 2
        if area > 0:
            fb[i] /= area
    return fb


# ─── PEAK PICKING ────────────────────────────────────────────────────────────

def pick_peaks(mag, k=N_PEAKS, min_dist=4):
    """For each frame, return the top-k bin indices with min distance between picks."""
    n_bins, n_frames = mag.shape
    peaks = np.zeros((k, n_frames), dtype=np.int32)
    for f in range(n_frames):
        col = mag[:, f].copy()
        for j in range(k):
            idx = int(np.argmax(col))
            if col[idx] < 1e-8:
                peaks[j, f] = 0
                continue
            peaks[j, f] = idx
            lo = max(0, idx - min_dist)
            hi = min(n_bins, idx + min_dist + 1)
            col[lo:hi] = 0.0
    return peaks


# ─── ENCODE ──────────────────────────────────────────────────────────────────

def pack_bits(values, bits):
    """Pack uint values (each fits in `bits` bits) into a byte array (MSB first)."""
    flat = np.asarray(values, dtype=np.uint32).flatten()
    out_bits = np.zeros(len(flat) * bits, dtype=np.uint8)
    for b in range(bits):
        out_bits[b::bits] = (flat >> (bits - 1 - b)) & 1
    if len(out_bits) % 8:
        out_bits = np.concatenate([out_bits, np.zeros(8 - len(out_bits) % 8, dtype=np.uint8)])
    return np.packbits(out_bits).tobytes()


def unpack_bits(blob, bits, n_values):
    bits_arr = np.unpackbits(np.frombuffer(blob, dtype=np.uint8))[:n_values * bits]
    out = np.zeros(n_values, dtype=np.uint32)
    for b in range(bits):
        out |= bits_arr[b::bits].astype(np.uint32) << (bits - 1 - b)
    return out


def encode_v2(audio, sr=SR):
    spec = stft(audio)
    mag = np.abs(spec).astype(np.float32)
    phase = np.angle(spec).astype(np.float32)

    # ── mel block (same as v1) ────────────────────────────────────
    fb = make_mel_filterbank(sr)
    mel = fb @ (mag ** 2)
    mel_db = np.clip(10 * np.log10(mel + 1e-10), -80.0, 20.0)
    mel_levels = (1 << MEL_BITS) - 1
    mel_q = np.round(((mel_db + 80.0) / 100.0) * mel_levels).astype(np.uint8)
    mel_packed = pack_bits(mel_q, MEL_BITS)

    # ── peak block ────────────────────────────────────────────────
    peaks_idx = pick_peaks(mag, N_PEAKS)                # (k, n_frames) bin idx
    # phase at those bins:
    n_bins, n_frames = mag.shape
    peaks_phase = np.zeros((N_PEAKS, n_frames), dtype=np.float32)
    for j in range(N_PEAKS):
        peaks_phase[j] = phase[peaks_idx[j], np.arange(n_frames)]
    # quantize phase to PHASE_BITS levels in [-π, π)
    p_levels = 1 << PHASE_BITS
    phase_q = np.mod(peaks_phase + np.pi, 2 * np.pi)
    phase_q = np.floor(phase_q / (2 * np.pi) * p_levels).astype(np.uint8)
    phase_q = np.clip(phase_q, 0, p_levels - 1)

    peaks_packed = pack_bits(peaks_idx, FREQ_BITS) + pack_bits(phase_q, PHASE_BITS)

    # ── header + payload ──────────────────────────────────────────
    header = struct.pack(
        '<4sBIIIBBBBBI',
        b'CRMB', 5,                           # magic, version
        sr, N_FFT, HOP,                       # audio shape
        N_MELS, MEL_BITS,                     # mel
        N_PEAKS, FREQ_BITS, PHASE_BITS,       # peaks
        n_frames,                             # frames
    )
    mel_zlib = zlib.compress(mel_packed, 9)
    peaks_zlib = zlib.compress(peaks_packed, 9)
    payload = (
        header
        + struct.pack('<II', len(mel_zlib), len(peaks_zlib))
        + mel_zlib
        + peaks_zlib
    )
    return payload, mel_db


def decode_v2(blob):
    HSIZE = struct.calcsize('<4sBIIIBBBBBI')
    header = struct.unpack('<4sBIIIBBBBBI', blob[:HSIZE])
    magic, ver, sr, n_fft, hop, n_mels, mel_bits, n_peaks, freq_bits, phase_bits, n_frames = header
    assert magic == b'CRMB' and ver == 5
    p = HSIZE
    len_mel, len_peaks = struct.unpack('<II', blob[p:p+8])
    p += 8
    mel_zlib  = blob[p:p+len_mel];   p += len_mel
    peaks_zlib = blob[p:p+len_peaks]; p += len_peaks

    mel_packed = zlib.decompress(mel_zlib)
    mel_q = unpack_bits(mel_packed, mel_bits, n_mels * n_frames).reshape(n_mels, n_frames)
    mel_levels = (1 << mel_bits) - 1
    mel_db = mel_q.astype(np.float32) / mel_levels * 100.0 - 80.0

    peaks_packed = zlib.decompress(peaks_zlib)
    n_peak_vals = n_peaks * n_frames
    bytes_freq = (n_peak_vals * freq_bits + 7) // 8
    peaks_idx = unpack_bits(peaks_packed[:bytes_freq], freq_bits, n_peak_vals).reshape(n_peaks, n_frames).astype(np.int32)
    phase_q = unpack_bits(peaks_packed[bytes_freq:], phase_bits, n_peak_vals).reshape(n_peaks, n_frames).astype(np.float32)
    p_levels = 1 << phase_bits
    peaks_phase = phase_q / p_levels * 2 * np.pi - np.pi

    return mel_db, peaks_idx, peaks_phase, sr, n_fft, hop, n_mels


# ─── RECONSTRUCT ─────────────────────────────────────────────────────────────

def mel_to_linear(mel_db, sr, n_fft, n_mels):
    fb = make_mel_filterbank(sr, n_fft, n_mels)
    mel_power = 10.0 ** (mel_db / 10.0)
    fb_pinv = np.linalg.pinv(fb)
    lin_power = np.maximum(fb_pinv @ mel_power, 0)
    return np.sqrt(lin_power).astype(np.float32)


def carrier_from_peaks(peaks_idx, peaks_phase, mag, n_fft, hop):
    """Build a sparse complex STFT containing ONLY the encoded partials,
    using the peak phases (correct) and target magnitude at those bins
    (approximate). ISTFT of this gives a tonal-only carrier signal whose
    phase pattern across time is consistent and locked to the partials."""
    n_bins, n_frames = mag.shape
    spec = np.zeros((n_bins, n_frames), dtype=np.complex64)
    n_peaks = peaks_idx.shape[0]
    cols = np.arange(n_frames)
    for j in range(n_peaks):
        idx = peaks_idx[j]
        ph = peaks_phase[j]
        valid = idx > 0
        # use target magnitude at the peak bin for amplitude
        amp = mag[idx, cols] * valid
        spec[idx, cols] = (amp * np.exp(1j * ph)).astype(np.complex64)
    return istft(spec, hop, n_fft)


def griffin_lim_seeded(mag, seed_audio, n_fft, hop, n_iter=GL_ITERS):
    """Griffin-Lim starting from a seed audio signal (carrier from peaks)
    instead of random phase. The seed's STFT phase carries our encoded
    partial information; GL fills in the missing magnitude/noise content
    while the strong partials anchor the iteration."""
    audio = seed_audio.copy()
    for _ in range(n_iter):
        new_spec = stft(audio, n_fft, hop)
        m = min(new_spec.shape[1], mag.shape[1])
        new_spec = new_spec[:, :m]
        ref_mag = mag[:, :m]
        angles = new_spec / (np.abs(new_spec) + 1e-8)
        spec = (ref_mag * angles).astype(np.complex64)
        audio = istft(spec, hop, n_fft)
    return audio


def sharpen_peaks(mag, peaks_idx, scale=2.0):
    """Mel pseudo-inverse blurs partials across neighbouring bins. This
    concentrates the local energy back at the encoded peak bins so the
    partials dominate the noise floor in the reconstruction."""
    out = mag.copy()
    cols = np.arange(mag.shape[1])
    for j in range(peaks_idx.shape[0]):
        idx = peaks_idx[j]
        valid = idx > 0
        out[idx[valid], cols[valid]] *= scale
    return out


def stabilize_peaks(peaks_idx, window=3):
    """3-frame median filter on each peak slot's bin index. Kills the
    1-bin jitter that creates frame-rate AM beating ('propeller') in
    the mid band when a partial sits between two STFT bins."""
    if window <= 1:
        return peaks_idx
    pad = window // 2
    n_peaks, n_frames = peaks_idx.shape
    padded = np.pad(peaks_idx, ((0, 0), (pad, pad)), mode='edge')
    out = np.empty_like(peaks_idx)
    for f in range(n_frames):
        out[:, f] = np.median(padded[:, f:f + window], axis=1).astype(peaks_idx.dtype)
    return out


def baked_eq(mag, sr, n_fft, freq, gain_db, q=3.0):
    """Apply a narrow peaking-EQ baked into the codec. Used to surgically
    attenuate residual frame-rate artifacts at known problem frequencies."""
    bin_freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    bw = freq / q
    weight = np.exp(-((bin_freqs - freq) / (bw / 2)) ** 2)
    gain_lin = 10 ** (gain_db / 20)
    curve = (1 + (gain_lin - 1) * weight).astype(np.float32)
    return mag * curve[:, None]


def time_upsample_mag(mag, factor=2):
    """Linear interp along time axis: doubles (or more) the frame rate.
    More frames in the ISTFT means finer overlap-add and a smoother
    transition between every old frame ('smearing the teeth')."""
    if factor <= 1:
        return mag
    n_bins, n_frames = mag.shape
    new_n = (n_frames - 1) * factor + 1
    x_old = np.arange(n_frames, dtype=np.float32)
    x_new = np.linspace(0, n_frames - 1, new_n, dtype=np.float32)
    out = np.empty((n_bins, new_n), dtype=mag.dtype)
    for b in range(n_bins):
        out[b] = np.interp(x_new, x_old, mag[b])
    return out


def time_upsample_peaks(peaks_idx, peaks_phase, factor=2):
    """Upsample peak tracks to match the upsampled magnitude. Bin idx
    rounded; phase unwrapped per slot before interp so it doesn't fold
    through 0 when crossing ±π."""
    if factor <= 1:
        return peaks_idx, peaks_phase
    n_peaks, n_frames = peaks_idx.shape
    new_n = (n_frames - 1) * factor + 1
    x_old = np.arange(n_frames, dtype=np.float32)
    x_new = np.linspace(0, n_frames - 1, new_n, dtype=np.float32)
    new_idx = np.empty((n_peaks, new_n), dtype=peaks_idx.dtype)
    new_phase = np.empty((n_peaks, new_n), dtype=np.float32)
    for j in range(n_peaks):
        new_idx[j] = np.round(np.interp(x_new, x_old, peaks_idx[j].astype(np.float32))).astype(peaks_idx.dtype)
        ph_un = np.unwrap(peaks_phase[j])
        ph_new = np.interp(x_new, x_old, ph_un)
        new_phase[j] = ((ph_new + np.pi) % (2 * np.pi)) - np.pi
    return new_idx, new_phase


def smear_mag_time(mag, kernel_frames=5):
    """5-frame Hann smoothing along time axis. Softens the hard edge
    between frames (Dan: 'smear the teeth')."""
    if kernel_frames <= 1:
        return mag
    k = np.hanning(kernel_frames + 2)[1:-1].astype(np.float32)
    k /= k.sum()
    pad = kernel_frames // 2
    padded = np.pad(mag, ((0, 0), (pad, pad)), mode='edge')
    out = np.zeros_like(mag)
    for i, w in enumerate(k):
        out += w * padded[:, i:i + mag.shape[1]]
    return out


def reconstruct_v2(mel_db, peaks_idx, peaks_phase, sr, n_fft, hop, n_mels):
    # 1. stabilize peak tracks (kills bin-jitter propeller)
    peaks_idx = stabilize_peaks(peaks_idx, window=3)

    # 2. SMEAR THE TEETH — upsample frame rate 2x, halve the hop.
    upsample = 2
    fine_hop = hop // upsample
    peaks_idx, peaks_phase = time_upsample_peaks(peaks_idx, peaks_phase, upsample)

    # 3. mel → linear magnitude
    mag = mel_to_linear(mel_db, sr, n_fft, n_mels)
    # 3b. upsample mag along time to match the fine hop
    mag = time_upsample_mag(mag, upsample)
    # 3c. additional 5-frame Hann smear along time
    mag = smear_mag_time(mag, kernel_frames=5)

    # 4. sharpen at peak bins (less aggressive — was 2.5)
    mag = sharpen_peaks(mag, peaks_idx, scale=2.0)

    # 5. surgical notch at 1 kHz (Dan-discovered residual safety net)
    mag = baked_eq(mag, sr, n_fft, freq=1000, gain_db=-3, q=3.0)

    # 6. seed-audio carrier (now at fine hop)
    seed = carrier_from_peaks(peaks_idx, peaks_phase, mag, n_fft, fine_hop)

    # 7. Griffin-Lim convergence at fine hop (87.5% overlap, very smooth)
    audio = griffin_lim_seeded(mag, seed, n_fft, fine_hop)

    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.95
    return audio


# ─── METRICS ─────────────────────────────────────────────────────────────────

def spectral_similarity(orig, recon, sr):
    n = min(len(orig), len(recon))
    o_mag = np.abs(stft(orig[:n])).flatten()
    r_mag = np.abs(stft(recon[:n])).flatten()
    m = min(len(o_mag), len(r_mag))
    o_mag = o_mag[:m] / (np.max(o_mag) + 1e-10)
    r_mag = r_mag[:m] / (np.max(r_mag) + 1e-10)
    return float(np.corrcoef(o_mag, r_mag)[0, 1])


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python crumb_v2.py <audiofile.mp3|wav>")
        return

    path = sys.argv[1]
    out_dir = Path(path).parent
    stem = Path(path).stem

    print(f"[CRUMB v3] Loading: {path}")
    audio, sr = load_audio(path)
    pcm_bytes = len(audio) * 2
    orig_bytes = os.path.getsize(path)
    print(f"           {len(audio):,} samples @ {sr}Hz ({len(audio)/sr:.2f}s)")
    print(f"           Source: {orig_bytes:,} bytes ({orig_bytes/1024:.1f} KB)")
    print()

    print(f"[CRUMB v3] Encoding (same as v2: mel + {N_PEAKS}-peak phase fingerprint)...")
    blob, mel_db = encode_v2(audio, sr)
    crumb_path = out_dir / (stem + '.crumb.v3')
    with open(crumb_path, 'wb') as f:
        f.write(blob)
    crumb_bytes = len(blob)
    print(f"           Crumb v3 binary: {crumb_bytes:,} bytes ({crumb_bytes/1024:.1f} KB)")
    print(f"           Compression vs source: {orig_bytes/crumb_bytes:.1f}x")
    print(f"           Compression vs PCM:    {pcm_bytes/crumb_bytes:.1f}x")
    print()

    print(f"[CRUMB v3] Decoding (smear-the-teeth: 2x time-upsample, 5-frame mag smear, hop/2)...")
    with open(crumb_path, 'rb') as f:
        blob = f.read()
    mel_db_d, peaks_idx, peaks_phase, dsr, dn_fft, dhop, dn_mels = decode_v2(blob)
    recon = reconstruct_v2(mel_db_d, peaks_idx, peaks_phase, dsr, dn_fft, dhop, dn_mels)

    recon_path = out_dir / (stem + '.crumb.v3.wav')
    recon_16 = (np.clip(recon, -1, 1) * 32767).astype(np.int16)
    wavfile.write(str(recon_path), dsr, recon_16)

    ss = spectral_similarity(audio, recon, sr)

    print()
    print("=" * 60)
    print("  CRUMB v3 — Smear-The-Teeth")
    print("=" * 60)
    print(f"  Source:        {orig_bytes:>12,} bytes  ({orig_bytes/1024:.1f} KB)")
    print(f"  Crumb v3:      {crumb_bytes:>12,} bytes  ({crumb_bytes/1024:.1f} KB)")
    print(f"  Compression:   {orig_bytes/crumb_bytes:>12.1f}x  vs source")
    print(f"                 {pcm_bytes/crumb_bytes:>12.1f}x  vs PCM")
    print(f"  Spectral sim:  {ss:>12.4f}")
    print(f"  Duration:      {len(audio)/sr:>12.2f}s")
    print()
    if ss > 0.92:
        print("  THE CRUMB IS ALIVE — close to source.")
    elif ss > 0.85:
        print("  CRUMB SINGS — clearly the song, much less whispery.")
    elif ss > 0.75:
        print("  CRUMB BREATHES — improvement over v1.")
    else:
        print("  CRUMB STIRS — needs more peaks or finer phase quantization.")
    print()
    print(f"  Listen: http://localhost:8888/crumb-studio_v3.html")
    print()


if __name__ == '__main__':
    main()
