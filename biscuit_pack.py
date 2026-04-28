"""
biscuit_pack.py — wrap a crumb binary in a biscuit JSON for spiral-cipher use.

A biscuit is a self-describing audio-DNA token suitable for IPFS pinning.
It contains the encoded crumb (base64), addressing metadata (CID = sha256
prefix), and a reference to the decoded WAV for playback.

Usage:
  python biscuit_pack.py <input.wav> [transcript]
"""
import sys, os, base64, hashlib, json
sys.path.insert(0, '.')
from crumb_v3 import load_audio, encode_v2
import scipy.io.wavfile as wf
import numpy as np


def pack(wav_path, transcript=''):
    audio, sr = load_audio(wav_path)
    blob, _ = encode_v2(audio, sr)
    duration_ms = round(len(audio) / sr * 1000)
    cid = 'sha256:' + hashlib.sha256(blob).hexdigest()[:16]
    stem = os.path.splitext(wav_path)[0]
    biscuit = {
        'v': 1,
        'type': 'audio_crumb',
        'codec': 'crumb_v3',
        'sr': sr,
        'duration_ms': duration_ms,
        'size_bytes': len(blob),
        'cid': cid,
        'created': '2026-04-28',
        'transcript': transcript,
        'wav_url': f'{stem}.crumb.v3.wav',
        'crumb_url': f'{stem}.crumb.v3',
        'payload_b64': base64.b64encode(blob).decode('ascii'),
    }
    out_path = f'{stem}.biscuit.json'
    with open(out_path, 'w') as f:
        json.dump(biscuit, f, indent=2)
    print(f"  packed: {out_path}")
    print(f"    duration:  {duration_ms} ms")
    print(f"    crumb:     {len(blob)} bytes")
    print(f"    cid:       {cid}")
    return biscuit


def main():
    if len(sys.argv) < 2:
        # batch-pack all voice-*ms.wav clips
        import glob
        clips = sorted(glob.glob('voice-*ms.wav'))
        print(f"[biscuit] batch-packing {len(clips)} voice clips...")
        biscuits = []
        for clip in clips:
            ms = clip.replace('voice-', '').replace('ms.wav', '')
            transcripts = {
                '100':   'q—',
                '250':   'quick',
                '500':   'quick brown',
                '1000':  'quick brown fox',
                '2000':  'quick brown fox jumps over',
                '5000':  'quick brown fox jumps over the lazy dog. cor—',
                '10000': 'first sentence + half of second',
            }
            tr = transcripts.get(ms, '')
            b = pack(clip, transcript=tr)
            biscuits.append(b)
        # write a manifest with all biscuits embedded
        manifest = {
            'v': 1,
            'type': 'biscuit_manifest',
            'name': 'voice-test',
            'codec': 'crumb_v3',
            'total_size': sum(b['size_bytes'] for b in biscuits),
            'total_duration_ms': sum(b['duration_ms'] for b in biscuits),
            'biscuits': biscuits,
        }
        with open('voice-test.manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        print()
        print(f"[biscuit] wrote manifest: voice-test.manifest.json")
        print(f"          total: {manifest['total_size']:,} bytes, "
              f"{manifest['total_duration_ms']} ms")
    else:
        pack(sys.argv[1], transcript=sys.argv[2] if len(sys.argv) > 2 else '')


if __name__ == '__main__':
    main()
