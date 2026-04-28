"""
CRUMB v4 — The DNA of Sound
=============================
Real codec: STFT → mel-spectrogram → quantized binary → Griffin-Lim → audio.

What v3 got wrong: 8 sines per 1-second segment. No time evolution.
Sounded nothing like the source.

What v4 does:
  - Encode: 23ms-hop STFT, 80 mel bands, 6-bit quantization, zlib pack.
  - Decode: unpack mel → linear mag (mel-pseudo-inverse) → Griffin-Lim
    60 iterations → ISTFT → PCM.

The .crumb file is the binary-packed compressed audio.
The .crumb.json file is the SphereNet-readable cochlea form.

Realistic limit: Griffin-Lim from quantized mel sounds "whispery" — the
song is clearly recognizable but the texture is robotic. That's the
fundamental limit of magnitude-only reconstruction. Transparent quality
needs a neural vocoder.

Usage: python crumb.py <audiofile.mp3|wav>
"""

import numpy as np
import scipy.io.wavfile as wavfile
import scipy.signal as ssig
import json, sys, os, subprocess, tempfile, zlib, struct
from pathlib import Path


# ─── CONFIG ──────────────────────────────────────────────────────────────────

SR = 22050
N_FFT = 2048
HOP = 512
N_MELS = 80
QUANT_BITS = 6        # 64 levels per mel bin
GL_ITERS = 60         # Griffin-Lim iterations


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
        n_samples = int(len(data) * target_sr / sr)
        data = ssig.resample(data, n_samples)
        sr = target_sr

    return data, sr


# ─── STFT / ISTFT ────────────────────────────────────────────────────────────

def stft(audio, n_fft=N_FFT, hop=HOP):
    win = np.hanning(n_fft).astype(np.float32)
    pad = n_fft // 2
    audio = np.pad(audio, pad, mode='reflect')
    n_frames = 1 + (len(audio) - n_fft) // hop
    # vectorized framing
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n_frames)[:, None]
    frames = audio[idx] * win
    return np.fft.rfft(frames, axis=1).T  # (n_bins, n_frames)


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
    # un-pad
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
        # area-norm
        area = (hi - lo) / 2
        if area > 0:
            fb[i] /= area
    return fb


# ─── ENCODE ──────────────────────────────────────────────────────────────────

def encode_crumb(audio, sr=SR):
    spec = stft(audio)
    mag = np.abs(spec).astype(np.float32)

    fb = make_mel_filterbank(sr)
    mel = fb @ (mag ** 2)                  # power mel
    mel_db = 10 * np.log10(mel + 1e-10)
    mel_db = np.clip(mel_db, -80.0, 20.0)  # 100 dB range

    # quantize to QUANT_BITS
    n_levels = (1 << QUANT_BITS) - 1
    norm = (mel_db + 80.0) / 100.0          # 0..1
    norm = np.clip(norm, 0.0, 1.0)
    q = np.round(norm * n_levels).astype(np.uint8)  # 0..63

    # bit-pack (6 bits per sample)
    flat = q.flatten()
    bits = np.zeros(len(flat) * QUANT_BITS, dtype=np.uint8)
    for b in range(QUANT_BITS):
        bits[b::QUANT_BITS] = (flat >> (QUANT_BITS - 1 - b)) & 1
    # pad to multiple of 8
    if len(bits) % 8:
        bits = np.concatenate([bits, np.zeros(8 - len(bits) % 8, dtype=np.uint8)])
    packed = np.packbits(bits)

    # header: magic | version | sr | n_fft | hop | n_mels | bits | n_frames
    header = struct.pack('<4sBIIIBBI', b'CRMB', 4, sr, N_FFT, HOP, N_MELS, QUANT_BITS, mel.shape[1])
    payload = header + packed.tobytes()
    compressed = zlib.compress(payload, 9)
    return compressed, mel_db, q


def decode_crumb(blob):
    payload = zlib.decompress(blob)
    magic, ver, sr, n_fft, hop, n_mels, bits_per, n_frames = struct.unpack('<4sBIIIBBI', payload[:23])
    assert magic == b'CRMB' and ver == 4
    packed = np.frombuffer(payload[23:], dtype=np.uint8)
    bits = np.unpackbits(packed)
    bits = bits[:n_mels * n_frames * bits_per]
    n_levels = (1 << bits_per) - 1
    flat = np.zeros(n_mels * n_frames, dtype=np.uint8)
    for b in range(bits_per):
        flat |= bits[b::bits_per].astype(np.uint8) << (bits_per - 1 - b)
    q = flat.reshape(n_mels, n_frames)
    mel_db = q.astype(np.float32) / n_levels * 100.0 - 80.0
    return mel_db, sr, n_fft, hop, n_mels


# ─── RECONSTRUCT ─────────────────────────────────────────────────────────────

def mel_to_linear(mel_db, sr, n_fft, n_mels):
    fb = make_mel_filterbank(sr, n_fft, n_mels)
    mel_power = 10.0 ** (mel_db / 10.0)
    # least-squares pseudo-inverse: linear power = fb_pinv @ mel_power
    fb_pinv = np.linalg.pinv(fb)
    lin_power = fb_pinv @ mel_power
    lin_power = np.maximum(lin_power, 0)
    return np.sqrt(lin_power).astype(np.float32)


def griffin_lim(mag, n_fft, hop, n_iter=GL_ITERS):
    # init with random phase
    rng = np.random.default_rng(0)
    angles = np.exp(2j * np.pi * rng.random(mag.shape)).astype(np.complex64)
    spec = mag.astype(np.complex64) * angles
    audio = istft(spec, hop, n_fft)
    for _ in range(n_iter):
        new_spec = stft(audio, n_fft, hop)
        # match shape
        m = min(new_spec.shape[1], mag.shape[1])
        new_spec = new_spec[:, :m]
        ref_mag = mag[:, :m]
        angles = new_spec / (np.abs(new_spec) + 1e-8)
        spec = ref_mag * angles
        audio = istft(spec, hop, n_fft)
    return audio


def reconstruct(mel_db, sr, n_fft, hop, n_mels):
    mag = mel_to_linear(mel_db, sr, n_fft, n_mels)
    audio = griffin_lim(mag, n_fft, hop)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.95
    return audio


# ─── SPHERENET-READABLE JSON (LIGHTWEIGHT) ───────────────────────────────────

def make_sphere_json(mel_db, sr, hop, n_mels):
    # one row per ~100ms (decimate) so it's a readable cochlea trace
    decim = max(1, int((sr / hop) * 0.1))
    rows = []
    for i in range(0, mel_db.shape[1], decim):
        row = mel_db[:, i:i + decim].mean(axis=1)
        rows.append([round(float(v), 1) for v in row])
    return {
        'v': 4,
        'sr': sr,
        'n_mels': n_mels,
        'hop_ms': round(decim * hop * 1000.0 / sr, 1),
        'mel_db': rows,
    }


# ─── METRICS ─────────────────────────────────────────────────────────────────

def spectral_similarity(orig, recon, sr):
    n = min(len(orig), len(recon))
    o = stft(orig[:n])
    r = stft(recon[:n])
    m = min(o.shape[1], r.shape[1])
    o_mag = np.abs(o[:, :m]).flatten()
    r_mag = np.abs(r[:, :m]).flatten()
    o_mag /= (np.max(o_mag) + 1e-10)
    r_mag /= (np.max(r_mag) + 1e-10)
    return float(np.corrcoef(o_mag, r_mag)[0, 1])


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python crumb.py <audiofile.mp3|wav>")
        return

    path = sys.argv[1]
    out_dir = Path(path).parent
    stem = Path(path).stem

    print(f"[CRUMB v4] Loading: {path}")
    audio, sr = load_audio(path)
    pcm_bytes = len(audio) * 2  # 16-bit equivalent
    orig_bytes = os.path.getsize(path)
    print(f"           {len(audio):,} samples @ {sr}Hz ({len(audio)/sr:.2f}s)")
    print(f"           Source: {orig_bytes:,} bytes ({orig_bytes/1024:.1f} KB)")
    print(f"           PCM equiv: {pcm_bytes:,} bytes ({pcm_bytes/1024:.1f} KB)")
    print()

    print(f"[CRUMB v4] Encoding (STFT n_fft={N_FFT} hop={HOP}, {N_MELS} mel, {QUANT_BITS}-bit)...")
    blob, mel_db, q = encode_crumb(audio, sr)

    crumb_path = out_dir / (stem + '.crumb')
    with open(crumb_path, 'wb') as f:
        f.write(blob)

    sphere = make_sphere_json(mel_db, sr, HOP, N_MELS)
    json_path = out_dir / (stem + '.crumb.json')
    with open(json_path, 'w') as f:
        json.dump(sphere, f, separators=(',', ':'))

    crumb_bytes = len(blob)
    json_bytes = os.path.getsize(json_path)

    print(f"           Crumb binary: {crumb_bytes:,} bytes ({crumb_bytes/1024:.1f} KB)")
    print(f"           Cochlea JSON: {json_bytes:,} bytes ({json_bytes/1024:.1f} KB)")
    print(f"           Compression vs source: {orig_bytes/crumb_bytes:.1f}x")
    print(f"           Compression vs PCM:    {pcm_bytes/crumb_bytes:.1f}x")
    print()

    print(f"[CRUMB v4] Decoding (Griffin-Lim {GL_ITERS} iterations)...")
    with open(crumb_path, 'rb') as f:
        blob = f.read()
    mel_db_dec, dsr, dn_fft, dhop, dn_mels = decode_crumb(blob)
    recon = reconstruct(mel_db_dec, dsr, dn_fft, dhop, dn_mels)

    recon_path = out_dir / (stem + '.crumb.wav')
    recon_16 = (np.clip(recon, -1, 1) * 32767).astype(np.int16)
    wavfile.write(str(recon_path), dsr, recon_16)

    ss = spectral_similarity(audio, recon, sr)

    print()
    print("=" * 60)
    print("  CRUMB v4 — The DNA of Sound")
    print("=" * 60)
    print(f"  Source:        {orig_bytes:>12,} bytes  ({orig_bytes/1024:.1f} KB)")
    print(f"  Crumb:         {crumb_bytes:>12,} bytes  ({crumb_bytes/1024:.1f} KB)")
    print(f"  Compression:   {orig_bytes/crumb_bytes:>12.1f}x  vs source")
    print(f"                 {pcm_bytes/crumb_bytes:>12.1f}x  vs PCM")
    print(f"  Spectral sim:  {ss:>12.4f}")
    print(f"  Duration:      {len(audio)/sr:>12.2f}s")
    print()
    if ss > 0.85:
        print("  THE CRUMB IS ALIVE — close to source.")
    elif ss > 0.7:
        print("  CRUMB BREATHES — clearly the same song, whispery texture.")
    elif ss > 0.5:
        print("  CRUMB STIRS — shape recognised, character lost.")
    else:
        print("  CRUMB SLEEPS — try smaller hop or more iterations.")
    print()
    print(f"  Listen: http://localhost:8888/crumb-player.html")
    print()


if __name__ == '__main__':
    main()
