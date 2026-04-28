"""
build_nested_demo.py — generate the nested-spiral demo data.

Tree:
  root.manifest.json
    └─ branch-a.manifest.json  ("the lead")     --> 4 word biscuits
    └─ branch-b.manifest.json  ("the leap")     --> 4 word biscuits
    └─ branch-c.manifest.json  ("the voice")    --> 4 word biscuits
    └─ branch-d.manifest.json  ("the dna")      --> 4 word biscuits
  = 16 leaf voice biscuits, recursive 2-level descent.

Pipeline:
  1. TTS each word via Windows System.Speech.Synthesis (offline, no model)
  2. Encode each as a crumb biscuit (v3 codec)
  3. Decode each to WAV for playback
  4. Build leaf manifest per branch (CID = sha256-prefix of canonical JSON)
  5. Build root manifest with 4 branch pointers
"""
import subprocess, json, hashlib, base64, os, sys
sys.path.insert(0, '.')
from crumb_v3 import load_audio, encode_v2, decode_v2, reconstruct_v2
import numpy as np
import scipy.io.wavfile as wf

BRANCHES = {
    'a': {'name': 'the lead',  'glyph': '○', 'words': ['the', 'quick', 'brown', 'fox']},
    'b': {'name': 'the leap',  'glyph': '●', 'words': ['jumps', 'over', 'the', 'lazy']},
    'c': {'name': 'the voice', 'glyph': '○', 'words': ['dog', 'cortex', 'speaks', 'in']},
    'd': {'name': 'the dna',   'glyph': '●', 'words': ['crumbs', 'and', 'biscuits', 'forever']},
}


def tts(text, out_path):
    """Generate TTS via Windows System.Speech.Synthesis."""
    cmd = (
        'Add-Type -AssemblyName System.Speech; '
        '$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        f'$s.SetOutputToWaveFile("{os.path.abspath(out_path)}"); '
        '$s.Rate = 0; '
        f'$s.Speak("{text}"); $s.Dispose()'
    )
    subprocess.run(['powershell', '-NoProfile', '-Command', cmd], capture_output=True)


def encode_biscuit(wav_path, transcript):
    audio, sr = load_audio(wav_path)
    blob, _ = encode_v2(audio, sr)
    cid = 'sha256:' + hashlib.sha256(blob).hexdigest()[:16]
    duration_ms = round(len(audio) / sr * 1000)
    biscuit = {
        'v': 1,
        'type': 'audio_crumb',
        'codec': 'crumb_v3',
        'sr': sr,
        'duration_ms': duration_ms,
        'size_bytes': len(blob),
        'cid': cid,
        'transcript': transcript,
        'wav_url': wav_path.replace('.wav', '.crumb.v3.wav'),
        'crumb_url': wav_path.replace('.wav', '.crumb.v3'),
        'payload_b64': base64.b64encode(blob).decode('ascii'),
    }
    return biscuit, blob


def decode_to_wav(blob, out_path):
    mel_db, peaks_idx, peaks_phase, dsr, dn_fft, dhop, dn_mels = decode_v2(blob)
    recon = reconstruct_v2(mel_db, peaks_idx, peaks_phase, dsr, dn_fft, dhop, dn_mels)
    recon_16 = (np.clip(recon, -1, 1) * 32767).astype(np.int16)
    wf.write(out_path, dsr, recon_16)


def cid_of_json(obj):
    canonical = json.dumps(obj, sort_keys=True, separators=(',', ':'))
    return 'sha256:' + hashlib.sha256(canonical.encode()).hexdigest()[:16]


def main():
    print('[1/3] TTS-generating 16 word clips...')
    for branch_id, branch in BRANCHES.items():
        for word in branch['words']:
            path = f'word-{branch_id}-{word}.wav'
            if not os.path.exists(path):
                tts(word, path)
                print(f'      [tts]  {word:<12}  -> {path}')
            else:
                print(f'      [skip] {word:<12}  (already exists)')

    print()
    print('[2/3] encoding + decoding biscuits...')
    leaf_manifests = {}
    for branch_id, branch in BRANCHES.items():
        biscuits = []
        for word in branch['words']:
            wav_path = f'word-{branch_id}-{word}.wav'
            biscuit, blob = encode_biscuit(wav_path, transcript=word)
            # decode to wav for playback (skip if already done)
            if not os.path.exists(biscuit['wav_url']):
                decode_to_wav(blob, biscuit['wav_url'])
            biscuits.append(biscuit)
            print(f'      {word:<12} {biscuit["duration_ms"]:>4}ms  {biscuit["size_bytes"]:>5}B  {biscuit["cid"]}')
        total_size = sum(b['size_bytes'] for b in biscuits)
        total_dur = sum(b['duration_ms'] for b in biscuits)
        leaf = {
            'v': 1,
            'type': 'leaf_spiral',
            'name': branch['name'],
            'codec': 'crumb_v3',
            'total_size': total_size,
            'total_duration_ms': total_dur,
            'biscuits': biscuits,
        }
        leaf['cid'] = cid_of_json(leaf)
        leaf_manifests[branch_id] = leaf
        with open(f'branch-{branch_id}.manifest.json', 'w') as f:
            json.dump(leaf, f, indent=2)
        print(f'      --> branch-{branch_id} "{branch["name"]}":  {total_size}B  {total_dur}ms  {leaf["cid"]}')
        print()

    print('[3/3] building root manifest...')
    root_branches = []
    for branch_id, branch in BRANCHES.items():
        m = leaf_manifests[branch_id]
        root_branches.append({
            'v': 1,
            'type': 'branch_pointer',
            'branch_id': branch_id,
            'name': branch['name'],
            'glyph': branch['glyph'],
            'cid': m['cid'],
            'leaf_count': len(m['biscuits']),
            'total_size': m['total_size'],
            'total_duration_ms': m['total_duration_ms'],
            'manifest_url': f'branch-{branch_id}.manifest.json',
        })
    root_total = sum(b['total_size'] for b in root_branches)
    root_dur   = sum(b['total_duration_ms'] for b in root_branches)
    root = {
        'v': 1,
        'type': 'root_spiral',
        'name': 'cortex first vocabulary',
        'total_size': root_total,
        'total_duration_ms': root_dur,
        'branches': root_branches,
    }
    root['cid'] = cid_of_json(root)
    with open('root.manifest.json', 'w') as f:
        json.dump(root, f, indent=2)

    print()
    print('=' * 60)
    print(f'  root cid: {root["cid"]}')
    print(f'  branches: {len(root_branches)}')
    print(f'  leaves:   {sum(b["leaf_count"] for b in root_branches)} biscuits')
    print(f'  total:    {root_total} bytes  ({root_total/1024:.1f} KB) for {root_dur}ms speech')
    print('=' * 60)


if __name__ == '__main__':
    main()
