# CRUMB Codec + Biscuit Voice Packets + Visible IPFS DAG

**Discovery date**: 28 April 2026
**Inventor**: Daniel Chipchase / ShortFactory (eliskcage)
**Git timestamp**: commit `2e683c2` on `gitlab.com/eliskcage/eliskcage-project` and `github.com/eliskcage/shortfactory`

## What this archive contains

A coordinated set of four inventions for **GPU-free intelligible speech compression** with content-addressed fractal storage, developed in a single working session:

1. **CRUMB audio codec** (4 versions, evolutionary arc preserved):
   - `crumb_v1.py` — mel + Griffin-Lim baseline (0.80 spectral sim)
   - `crumb_v2.py` — phase-aware hybrid + 1 kHz propeller fix (0.90 spectral sim)
   - `crumb_v3.py` — smear-the-teeth decoder
   - `crumb_v4.py` — Japanese-garden multi-pass + variance-aware rake-back (production)

2. **Biscuit voice packet** container format (`biscuit_pack.py`):
   - JSON wrapper around binary crumb
   - SHA-256 prefix CID for IPFS-ready content addressing
   - Empirical sizing: ~20 kbps, 319-byte fixed overhead, ~500 ms intelligibility floor

3. **Visible IPFS DAG** (`spiral-cipher_music.html`, `build_nested_demo.py`):
   - Recursive cipher = human-readable IPLD/Merkle tree
   - Demo: 16 word biscuits / 4 leaf manifests / 1 root manifest = 38.7 KB for 22.6 s of speech
   - Tamper-evident by construction (CID-chained)

4. **Industrial-scale architecture**:
   - GPU-free real-time speech on $5-class embedded devices
   - Content-addressed deduplication (phoneme pinned once, referenced thousands of times)
   - Voice swap by pointer (re-pin set, publish new root)

## Files in this archive

- `INVENTION-CRUMB-BISCUIT.md` — formal technical disclosure with 5 sections and reproducible empirical numbers
- `BUILD-DIARY.md` — chronological record of the development session including verbatim diagnostic quotes from the inventor
- Source code (Python): codec, container, sizing, isolation, diagnostic, demo builder
- HTML interfaces: studio, recursive spiral viewer, A/B/C/D player
- Encoded artifacts: binary `.crumb` files for music + 7 voice durations
- Manifests: root + 4 leaf spirals + 7 individual biscuits (JSON)

## Reproducibility

To reproduce:
1. Install: `numpy`, `scipy`, `ffmpeg` (no neural network or GPU required).
2. Run `python crumb_v3.py <audiofile>` → produces `.crumb.v3` binary + reconstructed `.wav`.
3. Run `python crumb_v4.py <audiofile>` for production-quality decode.
4. Run `python build_nested_demo.py` to generate the recursive spiral cipher demo from Windows TTS voice.
5. Open `spiral-cipher_music.html` via a local web server to navigate the visible IPFS DAG.

## Related prior inventions by the same inventor

- **GB2607623.2** — Biscuit compression (parent patent for this audio extension)
- **GB2605683.8** — Computanium / geometric VM
- **GB2605704.2** — Geometric VM
- **GB2605434.6** — Domino exemption / image-as-equation

## Citation

If you cite this work, please use the Zenodo DOI assigned to this deposit.
