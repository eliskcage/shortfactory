"""
crumb_isolate_artifact.py — extract the pure artifact (recon - source).

Aligns the reconstructed audio to the source via cross-correlation,
RMS-matches the levels, and writes the difference as a wav. If the
artifact sounds structured (a tone, a pattern) it's modelable for
active cancellation. If it's chaotic, it isn't.

Usage: python crumb_isolate_artifact.py <source> <recon> [<out.wav>]
"""
import sys, os, subprocess, tempfile
import numpy as np
import scipy.io.wavfile as wf
import scipy.signal as ss
from pathlib import Path

SR = 22050


def load_audio(path, target_sr=SR):
    ext = Path(path).suffix.lower()
    if ext == '.wav':
        sr, data = wf.read(path)
    else:
        tmp = tempfile.mktemp(suffix='.wav')
        subprocess.run(['ffmpeg', '-y', '-i', path, '-ar', str(target_sr),
                        '-ac', '1', '-sample_fmt', 's16', tmp], capture_output=True)
        sr, data = wf.read(tmp); os.unlink(tmp)
    if data.ndim > 1: data = data.mean(axis=1)
    data = data.astype(np.float32)
    if np.max(np.abs(data)) > 1: data /= 32768.0
    if sr != target_sr:
        data = ss.resample(data, int(len(data) * target_sr / sr))
    return data, target_sr


def best_offset(a, b, search=2048):
    """Find sample offset that best aligns b to a (correlate first ~5s for speed)."""
    n = min(220500, len(a), len(b))
    a_seg = a[:n] - a[:n].mean()
    b_seg = b[:n] - b[:n].mean()
    xc = ss.correlate(a_seg, b_seg, mode='full')
    center = len(xc) // 2
    # search only ±`search` samples around 0
    lo = center - search
    hi = center + search
    rel = np.argmax(np.abs(xc[lo:hi]))
    offset = (lo + rel) - center
    return offset


def main():
    if len(sys.argv) < 3:
        print("Usage: python crumb_isolate_artifact.py <source> <recon> [<out.wav>]")
        return
    src_path, rec_path = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else \
        str(Path(rec_path).with_suffix('.artifact.wav'))

    src, sr = load_audio(src_path)
    rec, _  = load_audio(rec_path)

    # align
    offset = best_offset(src, rec)
    print(f"[isolate] alignment offset: {offset} samples ({offset/sr*1000:.1f} ms)")
    if offset > 0:
        # source is delayed → trim source from start
        src = src[offset:]
    elif offset < 0:
        # rec is delayed → trim rec from start
        rec = rec[-offset:]
    n = min(len(src), len(rec))
    src, rec = src[:n], rec[:n]

    # RMS-match
    src_rms = np.sqrt(np.mean(src ** 2)) + 1e-12
    rec_rms = np.sqrt(np.mean(rec ** 2)) + 1e-12
    rec_matched = rec * (src_rms / rec_rms)
    print(f"[isolate] source RMS={src_rms:.4f}, recon RMS={rec_rms:.4f}, matched.")

    # ── 1. SAMPLE-DOMAIN DIFFERENCE (mostly phase-mismatch, not perceptual) ──
    artifact_raw = rec_matched - src
    art_rms = np.sqrt(np.mean(artifact_raw ** 2))
    snr_db = 20 * np.log10(src_rms / (art_rms + 1e-12))
    print(f"[isolate] sample-domain artifact RMS={art_rms:.4f}")
    print(f"[isolate] sample-domain SNR vs source: {snr_db:.2f} dB")
    print(f"           (low SNR mostly = phase mismatch, not audible)")

    # ── 2. SPECTRAL-EXCESS ARTIFACT (perceptual: where recon has MORE
    #      energy than source in any time-frequency cell — that's the
    #      'tooth needle' the ear actually hears) ──────────────────────
    n_fft = 2048
    hop = 512
    win = np.hanning(n_fft).astype(np.float32)
    pad = n_fft // 2
    s_pad = np.pad(src, pad, mode='reflect')
    r_pad = np.pad(rec_matched, pad, mode='reflect')
    n_frames = 1 + (min(len(s_pad), len(r_pad)) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n_frames)[:, None]
    s_frames = s_pad[idx] * win
    r_frames = r_pad[idx] * win
    S = np.fft.rfft(s_frames, axis=1).T   # (n_bins, n_frames)
    R = np.fft.rfft(r_frames, axis=1).T

    # excess magnitude in recon over source, keep only positive
    excess = np.maximum(np.abs(R) - np.abs(S), 0).astype(np.float32)
    # use recon's phase for the audible reconstruction
    excess_complex = (excess * np.exp(1j * np.angle(R))).astype(np.complex64)

    # ISTFT
    out_len = n_fft + hop * (n_frames - 1)
    audible_art = np.zeros(out_len, dtype=np.float32)
    norm = np.zeros(out_len, dtype=np.float32)
    eframes = np.fft.irfft(excess_complex.T, n=n_fft, axis=1).astype(np.float32)
    for i in range(n_frames):
        audible_art[i*hop:i*hop+n_fft] += eframes[i] * win
        norm[i*hop:i*hop+n_fft]       += win ** 2
    audible_art /= np.maximum(norm, 1e-8)
    audible_art = audible_art[pad:-pad]
    audible_rms = np.sqrt(np.mean(audible_art ** 2))
    audible_snr = 20 * np.log10(src_rms / (audible_rms + 1e-12))
    print(f"[isolate] AUDIBLE artifact RMS={audible_rms:.4f}")
    print(f"[isolate] AUDIBLE-only SNR: {audible_snr:.2f} dB  (this is what your ear hears)")
    print()

    # use audible artifact for the analysis below (the perceptual one)
    artifact = audible_art

    # normalize artifact for listening (loud, so you can actually hear the structure)
    peak = np.max(np.abs(artifact)) + 1e-12
    art_norm = artifact / peak * 0.9
    art_16 = (art_norm * 32767).astype(np.int16)
    wf.write(out_path, sr, art_16)
    print(f"[isolate] written: {out_path}  ({len(art_16):,} samples)")
    # also write the raw-difference one for completeness
    raw_path = out_path.replace('.wav', '.raw.wav')
    raw_norm = artifact_raw / (np.max(np.abs(artifact_raw)) + 1e-12) * 0.9
    wf.write(raw_path, sr, (raw_norm * 32767).astype(np.int16))
    print(f"[isolate] raw-diff:  {raw_path}")
    print(f"[isolate] gain applied for listening: {20*np.log10(0.9/peak):+.1f} dB")
    print()

    # spectral analysis of the artifact
    print("[isolate] artifact spectral character:")
    chunk = 2 ** 18
    mid = max(0, n // 2 - chunk // 2)
    a = artifact[mid:mid + chunk]
    if len(a) < chunk:
        a = np.pad(a, (0, chunk - len(a)))
    A = np.abs(np.fft.rfft(a * np.hanning(chunk)))
    freqs = np.fft.rfftfreq(chunk, 1.0 / sr)

    # broad-band energy partition
    bands = [(20, 200), (200, 600), (600, 1500), (1500, 4000), (4000, 8000), (8000, 11025)]
    total = np.sum(A ** 2)
    for lo, hi in bands:
        m = (freqs >= lo) & (freqs < hi)
        e = np.sum(A[m] ** 2) / total * 100
        bar = '#' * int(e / 2)
        print(f"  {lo:>5}-{hi:<5} Hz : {e:>5.1f}%  {bar}")
    print()

    # tonality test: ratio of peak to median in the spectrum
    # high ratio = tonal/structured (bandwidth low, peaks sharp)
    # low ratio = noise-like
    A_smooth = ss.medfilt(A, kernel_size=21)
    sharpness = np.max(A / (A_smooth + 1e-10))
    print(f"[isolate] artifact tonality (peak/local-median): {sharpness:.1f}")
    if sharpness > 20:
        print("  -> STRUCTURED (modellable for noise cancellation)")
    elif sharpness > 8:
        print("  -> SEMI-STRUCTURED (partly modellable)")
    else:
        print("  -> NOISE-LIKE (hard to model without a learned denoiser)")


if __name__ == '__main__':
    main()
