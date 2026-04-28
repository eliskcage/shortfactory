"""
crumb_diagnose.py — find the exact spectral lines of the artifact.

Compares source vs reconstruction in a long FFT, finds narrow spectral
peaks that exist in the recon but not in source (or are exaggerated).
Reports their frequency AND their position relative to the frame-rate
harmonics (sr/hop = 43.07 Hz multiples) — if they line up, the cause
is confirmed.

Usage: python crumb_diagnose.py <source> <recon>
       python crumb_diagnose.py observer-bed.mp3 observer-bed.crumb.v2.wav
"""
import sys, os, subprocess, tempfile
import numpy as np
import scipy.io.wavfile as wf
import scipy.signal as ss
from scipy.ndimage import uniform_filter1d
from pathlib import Path

SR = 22050
HOP = 512
FRAME_RATE = SR / HOP


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


def main():
    src_path, rec_path = sys.argv[1], sys.argv[2]
    src, sr = load_audio(src_path)
    rec, _  = load_audio(rec_path)
    n = min(len(src), len(rec))
    src, rec = src[:n], rec[:n]

    # take a long stable middle chunk
    chunk = 2 ** 18
    mid = max(0, n // 2 - chunk // 2)
    s = src[mid:mid + chunk]
    r = rec[mid:mid + chunk]
    if len(s) < chunk:
        s = np.pad(s, (0, chunk - len(s)))
    if len(r) < chunk:
        r = np.pad(r, (0, chunk - len(r)))

    win = np.hanning(chunk)
    S = np.abs(np.fft.rfft(s * win))
    R = np.abs(np.fft.rfft(r * win))
    freqs = np.fft.rfftfreq(chunk, 1.0 / sr)

    # smoothed envelopes (the "music" baseline)
    S_smooth = uniform_filter1d(S, size=128) + 1e-12
    R_smooth = uniform_filter1d(R, size=128) + 1e-12

    # narrow peaks in recon = R sticking up sharply above its own smoothed envelope
    rec_excess = R - R_smooth
    src_excess = S - S_smooth

    # artifact score: where recon has a narrow peak that the source does NOT
    artifact = rec_excess / R_smooth - np.maximum(src_excess, 0) / S_smooth

    peaks, props = ss.find_peaks(artifact, prominence=0.3, distance=8)
    mask = (freqs[peaks] > 100) & (freqs[peaks] < 4000)
    peaks = peaks[mask]
    prominences = props['prominences'][mask]

    if len(peaks) == 0:
        print("No prominent narrow artifacts found in 100-4000 Hz.")
        return

    order = np.argsort(prominences)[::-1][:25]

    print()
    print("=" * 64)
    print(f"  ARTIFACT LINES — {Path(rec_path).name}")
    print(f"  frame rate = {FRAME_RATE:.3f} Hz  (sr/hop = {sr}/{HOP})")
    print("=" * 64)
    print(f"  {'freq (Hz)':>10}  {'frame-h':>8}  {'d(Hz)':>8}  {'score':>7}")
    print(f"  {'':>10}  {'(n× FR)':>8}  {'':>8}  {'':>7}")
    print(f"  {'-'*10}  {'-'*8}  {'-'*8}  {'-'*7}")

    matches_frame_rate = 0
    for i in order:
        p = peaks[i]
        f = freqs[p]
        n_h = f / FRAME_RATE
        nearest_h = round(n_h)
        delta = f - nearest_h * FRAME_RATE
        score = prominences[i]
        marker = ' <- frame-rate' if abs(delta) < 3.0 else ''
        if abs(delta) < 3.0:
            matches_frame_rate += 1
        print(f"  {f:>10.2f}  {nearest_h:>8d}  {delta:>+8.2f}  {score:>7.3f}{marker}")

    print()
    print(f"  {matches_frame_rate}/{len(order)} top artifacts within 3 Hz of a frame-rate harmonic.")
    if matches_frame_rate >= len(order) * 0.6:
        print(f"  --> CAUSE CONFIRMED: frame-boundary periodicity at {FRAME_RATE:.2f} Hz.")
        print(f"  --> FIX: comb-notch every multiple of {FRAME_RATE:.2f} Hz between 200-3000 Hz.")
    else:
        print(f"  --> Artifacts are NOT predominantly frame-rate. Investigate further.")
    print()


if __name__ == '__main__':
    main()
