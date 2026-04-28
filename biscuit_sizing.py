"""
biscuit_sizing.py — measure crumb size vs clip duration.

Tells us what KB budget a biscuit needs at each clip length, and
the bytes-per-ms rate. This is the input to deciding fractal
recursion granularity for spiral-cipher.html biscuit pins.
"""
import sys, os
sys.path.insert(0, '.')
from crumb_v3 import load_audio, encode_v2, decode_v2, reconstruct_v2
import numpy as np
import scipy.io.wavfile as wf

DURATIONS_MS = [100, 250, 500, 1000, 2000, 5000, 10000]

def main():
    print()
    print("=" * 72)
    print("  CRUMB VOICE BISCUIT SIZING — bytes per duration")
    print("=" * 72)
    print(f"  {'duration':>10}  {'src bytes':>10}  {'crumb bytes':>12}  {'B/ms':>6}  {'kbps':>6}  {'verdict':<14}")
    print(f"  {'-'*10}  {'-'*10}  {'-'*12}  {'-'*6}  {'-'*6}  {'-'*14}")

    rows = []
    for ms in DURATIONS_MS:
        path = f'voice-{ms}ms.wav'
        if not os.path.exists(path):
            continue
        audio, sr = load_audio(path)
        if len(audio) < 256:
            print(f"  {ms:>9}ms  TOO SHORT")
            continue
        try:
            blob, _ = encode_v2(audio, sr)
        except Exception as e:
            print(f"  {ms:>9}ms  ENCODE FAILED: {e}")
            continue
        src_size = os.path.getsize(path)
        crumb_size = len(blob)
        bpms = crumb_size / ms
        kbps = (crumb_size * 8) / ms     # bits per second / 1000 = kbps
        # rough verdict bands
        if crumb_size < 200:    verdict = "tiny / dot"
        elif crumb_size < 600:  verdict = "phoneme"
        elif crumb_size < 2000: verdict = "word"
        elif crumb_size < 8000: verdict = "phrase"
        else:                   verdict = "sentence+"

        out_path = f'voice-{ms}ms.crumb.v3'
        with open(out_path, 'wb') as f:
            f.write(blob)
        print(f"  {ms:>9}ms  {src_size:>10,}  {crumb_size:>12,}  {bpms:>6.2f}  {kbps:>6.2f}  {verdict:<14}")
        rows.append((ms, src_size, crumb_size, bpms, kbps, verdict))

    print()
    print("=" * 72)
    print("  HEADROOM ANALYSIS")
    print("=" * 72)

    # what's the fixed overhead?
    # extrapolate: at ms=0, crumb = overhead bytes; slope = bytes/ms
    if len(rows) >= 2:
        # linear fit to find header overhead
        msarr = np.array([r[0] for r in rows], dtype=np.float64)
        bytesarr = np.array([r[2] for r in rows], dtype=np.float64)
        slope, intercept = np.polyfit(msarr, bytesarr, 1)
        print(f"  fixed overhead per clip:    {intercept:>6.0f} bytes")
        print(f"  marginal cost per ms audio: {slope:>6.2f} bytes/ms ({slope*8:.1f} kbps)")
        print()
        print("  → break-even (overhead == content): clip ≈ {:.0f} ms".format(intercept / slope))
        print("  → fractal recursion sweet spot: ~500-1000ms biscuits")
        print("    (small enough to chain, big enough to amortize overhead)")
    print()


if __name__ == '__main__':
    main()
