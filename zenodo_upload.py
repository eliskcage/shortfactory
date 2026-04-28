"""
zenodo_upload.py — upload disclosure archive to Zenodo and publish (DOI assigned).

Usage:
  ZENODO_TOKEN=your_token python zenodo_upload.py [archive.zip]

The script creates a deposit, uploads the archive, sets metadata, and PUBLISHES
(which is what assigns the DOI and establishes the public timestamp). Once
published, content is immutable (metadata can still be edited).

If you want to review before publishing, comment out the publish step at the
bottom and visit https://zenodo.org/deposit/<id> to publish manually.
"""
import sys, os, json, requests
from datetime import date

ZENODO_API = 'https://zenodo.org/api'

DESCRIPTION_HTML = '''
<p>Technical disclosure of four coordinated inventions for <b>GPU-free intelligible speech compression with content-addressed fractal storage</b>, developed in a single working session on 28 April 2026.</p>

<h3>1. CRUMB Audio Codec (v1-v4)</h3>
<p>Mel-spectrogram + sparse spectral peak phase fingerprint with carrier-seeded Griffin-Lim reconstruction. Sub-30 kbps voice without GPU or neural network. The development arc is preserved through four codec versions:</p>
<ul>
<li><b>v1</b> — mel + random-phase Griffin-Lim baseline (0.80 spectral similarity)</li>
<li><b>v2</b> — phase-aware hybrid with 6-peak fingerprint + 1 kHz "propeller" fix (0.90 spectral similarity)</li>
<li><b>v3</b> — smear-the-teeth decoder: 2× time-upsample + 5-frame Hann smear + ISTFT at hop/2</li>
<li><b>v4</b> — "Japanese garden" multi-pass decoder: 4 passes with varied parameters, cross-pass median-combine + variance-derived confidence mask + max-blend rake-back. Artifact tonality drops 8.8 → 6.2 (semi-structured to noise-like, perceptually masked).</li>
</ul>

<h3>2. Biscuit Voice Packet</h3>
<p>Self-describing JSON container wrapping a binary crumb with SHA-256-prefix CID for IPFS-ready content addressing. Empirical sizing measurements: ~20 kbps marginal, 319-byte fixed overhead, ~500 ms intelligibility floor, ~1 KB per spoken word.</p>

<h3>3. Visible IPFS DAG (Recursive Spiral Cipher)</h3>
<p>Method of representing IPLD/Merkle tree as visual recursive cipher. Each pinned spiral = one DAG node. Dots in the cipher encode either inline data OR CID pointers to child spirals. Tamper-evident by construction (modifying one byte changes the parent CID). Demonstrated end-to-end with 16 word biscuits across 4 leaf manifests pointed to by 1 root manifest = 38.7 KB total for 22.6 s of speech library.</p>

<h3>4. Industrial-Scale Implications</h3>
<ul>
<li>GPU-free real-time speech synthesis on $5-class embedded devices (ESP32, Pi)</li>
<li>Content-addressed deduplication: phoneme appearing in 1000 words is pinned once</li>
<li>Voice swap by pointer (re-pin phoneme set, publish new root manifest)</li>
<li>Tamper-proof distribution: customers verify root CID against publisher signature</li>
<li>Locality via redundancy: regional pin caches eliminate IPFS retrieval latency</li>
</ul>

<h3>Reproducibility</h3>
<p>Pure Python (numpy + scipy) + ffmpeg. No neural network. No GPU. All source code, encoded test artifacts, manifests, and the chronological build diary are included in this archive.</p>

<h3>Related prior inventions by the same inventor</h3>
<ul>
<li><b>GB2607623.2</b> — Biscuit compression (parent patent for this audio extension)</li>
<li><b>GB2605683.8</b> — Computanium / geometric virtual machine</li>
<li><b>GB2605704.2</b> — Geometric VM</li>
<li><b>GB2605434.6</b> — Domino exemption / image-as-equation</li>
</ul>

<h3>Git provenance</h3>
<p>Commit <code>2e683c2</code> on:</p>
<ul>
<li>gitlab.com/eliskcage/eliskcage-project</li>
<li>github.com/eliskcage/shortfactory</li>
</ul>
'''


def main():
    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        print('ERROR: set ZENODO_TOKEN env var')
        print('       get a token at https://zenodo.org/account/settings/applications/')
        sys.exit(1)

    zip_file = sys.argv[1] if len(sys.argv) > 1 else 'crumb-biscuit-discovery-28apr2026.zip'
    if not os.path.exists(zip_file):
        print(f'ERROR: {zip_file} not found')
        sys.exit(1)

    headers = {'Content-Type': 'application/json'}
    params = {'access_token': token}

    # 1. create deposit
    print('[1/4] creating Zenodo deposit...')
    r = requests.post(f'{ZENODO_API}/deposit/depositions', params=params, json={}, headers=headers)
    r.raise_for_status()
    dep = r.json()
    dep_id = dep['id']
    bucket_url = dep['links']['bucket']
    print(f'      deposit id: {dep_id}')
    print(f'      draft url:  https://zenodo.org/deposit/{dep_id}')

    # 2. upload file
    print(f'[2/4] uploading {zip_file} ({os.path.getsize(zip_file):,} bytes)...')
    fname = os.path.basename(zip_file)
    with open(zip_file, 'rb') as f:
        r = requests.put(f'{bucket_url}/{fname}', data=f, params=params)
        r.raise_for_status()
    print(f'      upload complete')

    # 3. set metadata
    print('[3/4] setting metadata...')
    metadata = {
        'metadata': {
            'title': 'CRUMB Audio Codec + Biscuit Voice Packets + Visible IPFS DAG: GPU-free intelligible speech compression with content-addressed fractal storage',
            'upload_type': 'software',
            'description': DESCRIPTION_HTML.strip(),
            'creators': [{
                'name': 'Chipchase, Daniel',
                'affiliation': 'ShortFactory',
            }],
            'keywords': [
                'audio codec', 'speech compression', 'mel spectrogram',
                'IPFS', 'IPLD', 'content-addressed storage', 'fractal storage',
                'Griffin-Lim', 'edge computing', 'embedded speech synthesis',
                'biscuit', 'crumb', 'spiral cipher', 'audio DNA',
                'GPU-free', 'voice biscuit', 'recursive cipher',
            ],
            'access_right': 'open',
            'license': 'cc-by-4.0',
            'language': 'eng',
            'publication_date': str(date.today()),
            'related_identifiers': [
                {'identifier': 'https://github.com/eliskcage/shortfactory',
                 'relation': 'isSupplementTo', 'resource_type': 'software'},
                {'identifier': 'https://gitlab.com/eliskcage/eliskcage-project',
                 'relation': 'isSupplementTo', 'resource_type': 'software'},
            ],
        }
    }
    r = requests.put(f'{ZENODO_API}/deposit/depositions/{dep_id}',
                     params=params, headers=headers, json=metadata)
    r.raise_for_status()
    print(f'      metadata set')

    # 4. publish (assigns DOI, locks content immutably)
    print('[4/4] publishing (assigns DOI, locks content)...')
    r = requests.post(f'{ZENODO_API}/deposit/depositions/{dep_id}/actions/publish',
                      params=params)
    r.raise_for_status()
    pub = r.json()
    doi = pub.get('doi') or pub.get('metadata', {}).get('doi')
    record_url = pub.get('links', {}).get('record_html') or f'https://zenodo.org/record/{dep_id}'

    print()
    print('=' * 64)
    print('  ZENODO DEPOSIT PUBLISHED — DOI ASSIGNED, TIMESTAMP LOCKED')
    print('=' * 64)
    print(f'  DOI:    {doi}')
    print(f'  URL:    {record_url}')
    print(f'  cite:  Chipchase, D. ({date.today().year}). CRUMB Audio Codec...')
    print(f'         doi:{doi}')
    print('=' * 64)
    print()


if __name__ == '__main__':
    main()
