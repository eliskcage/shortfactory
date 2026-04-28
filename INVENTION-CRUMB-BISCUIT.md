# INVENTION DISCLOSURE — CRUMB CODEC + BISCUIT VOICE PACKETS + VISIBLE IPFS DAG

**Date of disclosure**: 28 April 2026
**Inventor**: Daniel Eliskcage (ShortFactory)
**Status**: Pre-filing technical disclosure — establishing prior art / date of invention via signed git commit + IPFS pin.

This document discloses a coordinated set of inventions developed in a single working session on **28 April 2026**, evidenced by source code, build artifacts, and a chronological build diary in this repository. The full development arc is preserved as four codec versions (v1 → v4) with milestone files frozen at each step.

---

## 1. CRUMB AUDIO CODEC — Compressed Audio DNA

A method of encoding audio as a compressed mel-spectrogram + sparse spectral peak phase fingerprint, suitable for sub-30 kbps voice transmission **without GPU or neural network requirements**.

### 1.1 Encoder
- Resample to 22.05 kHz mono.
- Compute STFT with `n_fft = 2048`, `hop = 512`.
- Project STFT magnitude through 80-band mel filterbank (perceptual scale, fmin = 20 Hz, fmax = sr/2).
- Convert to log-dB, clip to [-80, +20] dB range.
- Quantize each mel bin to 6 bits (64 levels).
- Per frame, identify top-K=6 spectral peaks (with min-bin-distance enforcement). Store each peak as: 10-bit bin index, 5-bit quantized phase (32 levels in [-π, π)).
- Bit-pack the mel data + peak data, prepend a fixed binary header, compress with zlib.
- Output binary container: ~20 kbps for voice content (2.55 bytes/ms), with 319-byte fixed overhead per crumb.

### 1.2 Decoder (v3 — "Smear-The-Teeth")
- Decompress and unpack mel + peaks.
- Stabilise peak tracks via 3-frame median filter on bin indices (suppresses inter-frame bin-jitter that creates audible AM beating in mid-band).
- 2× linear time-upsample of mel-spectrogram and peak data; phase unwrapped per slot before interpolation to avoid wrap-around discontinuities at ±π.
- Mel pseudo-inverse to obtain linear magnitude.
- 5-frame Hann time-smoothing of magnitude (softens frame-boundary discontinuities).
- Sharpen magnitude at encoded peak bin positions by factor 2.0 (compensates for mel-pseudo-inverse smearing of partials).
- Construct sparse complex STFT from peak phases at peak bins (carrier audio).
- ISTFT carrier → seed audio.
- Run Griffin-Lim 80 iterations seeded with carrier audio (not random phase) at fine hop = 256 → 87.5% overlap-add, target magnitude clamped each iteration.

### 1.3 Decoder (v4 — "Japanese Garden")
**Multi-pass dither + variance-aware rake-back**, novel per-cell artifact suppression:
- Decode the same crumb N=4 times with varied parameters (smear kernel ∈ {3,5,7,9}, sharpen ∈ {1.5,1.7,2.0,2.3}, peak-stabilize window ∈ {1,3,3,5}, GL iterations ∈ {50,50,60,70}, multiplicative magnitude dither ∈ {0,0,0.02,0.03}).
- Each pass places its frame-boundary artifact at a slightly different time-frequency position; music content remains invariant across passes.
- Compute per-cell median magnitude across passes (artifact median-suppressed, music preserved).
- Compute per-cell variance across passes → confidence mask: `confidence = median / (std + 0.5*median)`. Low variance = music agreement, high variance = artifact disagreement.
- Final magnitude per cell = `(1 - confidence) * median + confidence * max-across-passes`. In confident cells, restore the maximum across passes (preserves fine detail); in unconfident cells, keep the median (rejects artifact).
- Phase taken from baseline (pass 0).
- Bake user-tuned EQ into decoder: -12 dB peaking notches at 1 kHz, 3 kHz, 6 kHz Q=3 (the "Cipher" preset, established by perceptual testing).

### 1.4 Container: `.crumb` binary format
```
[magic 'CRMB'][version 1B][sr 4B][n_fft 4B][hop 4B][n_mels 1B][mel_bits 1B]
[n_peaks 1B][freq_bits 1B][phase_bits 1B][n_frames 4B][len_mel 4B][len_peaks 4B]
[zlib(mel_packed)][zlib(peaks_packed)]
```
Total header: 34 bytes. Self-describing, future-extensible via version byte.

### 1.5 Empirical performance (on 136-second 128 kbps MP3 source)
| version | size | vs MP3 | spectral sim | character |
|---|---|---|---|---|
| v1 | 186 KB | 11.4× | 0.80 | whispery |
| v2 | 229 KB | 9.3× | 0.90 | partials lock |
| v3 | 229 KB | 9.3× | 0.886 | smoothed |
| v4 | 229 KB | 9.3× | 0.886 (tonality 6.2 vs v3's 8.8 = noise-like) | production |

For voice content: 2.55 bytes/ms = ~20 kbps, ~1 KB per spoken word, ~40 KB per minute.

---

## 2. BISCUIT VOICE PACKET — Content-Addressed Audio Token

A method of packaging a `.crumb` binary as a self-describing IPFS-pinnable token suitable for fractal aggregation into voice libraries.

### 2.1 Biscuit JSON schema
```json
{
  "v": 1, "type": "audio_crumb", "codec": "crumb_v3",
  "sr": 22050, "duration_ms": 500, "size_bytes": 1545,
  "cid": "sha256:b7916d5db31cb385",
  "transcript": "quick brown",
  "wav_url": "...crumb.v3.wav",
  "crumb_url": "...crumb.v3",
  "payload_b64": "<base64 of binary crumb>"
}
```
- `cid` = SHA-256 prefix of the binary crumb (IPFS-ready content addressing).
- `payload_b64` carries the binary inline for transport, OR can be omitted with the binary pinned separately.

### 2.2 Empirical biscuit sizing
| duration | crumb bytes | role |
|---|---|---|
| 100 ms | 320 | dot/phoneme (below codec floor, ~0.50 spectral sim) |
| 250 ms | 730 | word (below floor) |
| 500 ms | 1,545 | **word — codec floor, sweet spot** |
| 1,000 ms | 3,019 | phrase |
| 2,000 ms | 6,052 | phrase |
| 5,000 ms | 12,763 | sentence |
| 10,000 ms | 25,776 | paragraph |

- Fixed overhead per crumb: 319 bytes (header + zlib metadata).
- Marginal cost: 2.55 bytes/ms.
- Break-even (overhead = content): ~125 ms.
- **Honest biscuit floor** (below which intelligibility breaks): ~500 ms.

---

## 3. VISIBLE IPFS DAG — Recursive Spiral Cipher as Data Manifest

A method of representing a Merkle/IPLD tree as a human-readable visual recursive cipher, enabling visible content-addressed fractal storage.

### 3.1 The mapping
| Spiral cipher concept | IPFS / IPLD equivalent |
|---|---|
| One spiral image | One DAG node |
| Pinned spiral → CID | The node's content-address |
| Inline-data dot | Inline byte (DAG node body) |
| Container dot | CID pointer to child node |
| Recursive nesting | Merkle tree descent |
| Audio crumb at leaf | Terminal raw-blob payload |

The spiral cipher functions as the **human-visible representation of an IPLD DAG**. Most IPFS users never see the DAG; this draws it.

### 3.2 Three manifest types
- **`root_spiral`**: top-level manifest, contains array of `branch_pointer` objects each carrying a child manifest CID and metadata.
- **`leaf_spiral`**: terminal manifest containing array of biscuit objects (no further children).
- **`branch_pointer`**: lightweight reference object: `{ branch_id, name, glyph, cid, leaf_count, total_size, total_duration_ms, manifest_url }`.

### 3.3 Tamper-evidence
Each manifest's CID is the SHA-256 prefix of its canonical-JSON serialisation. Modifying any contained byte changes the manifest's CID, which breaks the parent's pointer. Trust descends from the root CID with cryptographic verifiability at every level.

### 3.4 Sizing (with current cipher alphabet ○=5, ●=1, ▪=space)
- Each cipher dot encodes ~3 bits of information.
- A SHA-256 CID = 256 bits ≈ 85 dots in the cipher alphabet.
- A spiral with ~256 dots holds ~3 CID pointers + small metadata payload.
- Natural fanout per spiral ≈ 3.
- Tree depth 10 = 59,049 leaves = ~10 hours of speech library, addressable by a single root CID.

### 3.5 Cortex word-formation flow (use case)
To synthesise the word "FATHER":
1. Load root manifest (single CID fetch, ~1.4 KB).
2. Decode root's dots → identify F-branch CID.
3. Fetch F-spiral → A-branch CID → A-spiral → T → H → E → R.
4. Each leaf spiral references its terminal crumb CID.
5. Fetch crumb binaries (~1.5 KB each).
6. Decode via crumb v3/v4 codec → concatenate audio fragments → output speech.
7. Total: ~10 KB of fetches per word, all content-addressed, all immortal once pinned.

---

## 4. INDUSTRIAL-SCALE IMPLICATIONS

The combined system enables:
- **GPU-free real-time speech synthesis** on $5-class embedded devices (ESP32, Pi).
- **Content-addressed deduplication**: a phoneme appearing in 1000 words is pinned once, referenced 1000 times; storage scales sub-linearly with vocabulary size.
- **Voice swap by pointer**: re-publishing a new root manifest with different leaf CIDs swaps the entire voice without re-deploying decoder code.
- **Tamper-proof distribution**: customers verify root CID against publisher's signed CID; chain integrity is provably untouched.
- **Zero-egress libraries**: customers fetch from IPFS public network or local pinning nodes; publisher pays only for pinning, not bandwidth.
- **Locality via redundancy**: regional pin caches eliminate IPFS retrieval latency for real-time use.

---

## 5. RELATIONSHIP TO PRIOR INVENTIONS BY THE SAME INVENTOR

This invention extends and connects to:
- **GB2607623.2** — Biscuit compression patent. The crumb codec extends the biscuit principle to audio.
- **GB2605683.8** — Computanium / geometric VM. The spiral-DAG is a visualisation of computanium-style geometric storage.
- **GB2605704.2** — Geometric VM patent.
- **GB2605434.6** — Domino exemption / image-as-equation.
- **The Living Equation** (39 claims, not yet filed) — broader symbolic computation framework.
- **SphereNet** — biological cochlea model; the natural neural decoder for crumb's mel representation.

---

## 6. FILES IN THIS REPOSITORY EVIDENCING THE INVENTION

### Source code (Python)
- `crumb_v1.py` — v1 baseline encoder/decoder (mel + Griffin-Lim).
- `crumb_v2.py` — v2 phase-aware hybrid (mel + peak fingerprint + propeller fix).
- `crumb_v3.py` — v3 smear-the-teeth decoder.
- `crumb_v4.py` — v4 Japanese-garden multi-pass + rake-back decoder.
- `biscuit_pack.py` — biscuit container packager.
- `biscuit_sizing.py` — empirical sizing measurement tool.
- `build_nested_demo.py` — end-to-end recursive manifest demo builder.
- `crumb_isolate_artifact.py` — perceptual artifact extractor (for diagnosis).
- `crumb_diagnose.py` — frame-rate harmonic detector.

### HTML interfaces
- `crumb-studio_v3.html` — A/B/C/D codec studio with EQ, routing, transport.
- `spiral-cipher_music.html` — recursive visible-IPFS-DAG demo with breadcrumb navigation.
- `crumb-player_v1.html`, `crumb-player_v2.html`, `crumb-studio_v2.html` — earlier versions preserved.

### Encoded artifacts
- `observer-bed.crumb.v1`, `.v2`, `.v3`, `.v4` — binary crumb files (music test).
- `voice-test.crumb.v3`, `voice-Nms.crumb.v3` — voice test crumbs at various durations.
- `word-{a,b,c,d}-*.crumb.v3` — 16 word-level voice biscuits.

### Manifests
- `voice-test.manifest.json` — flat manifest (precursor).
- `branch-{a,b,c,d}.manifest.json` — leaf spirals (4 branches × 4 word biscuits).
- `root.manifest.json` — root spiral with 4 branch pointers.
- 16 individual `*.biscuit.json` files.

### Chronological evidence
- `BUILD-DIARY.md` — complete chronological log of the development arc, including verbatim quotes from the inventor's diagnosis at each stage.

---

## 7. DATE OF INVENTION

The development arc described above occurred in a single working session on **28 April 2026** (UTC). The git commit timestamp on this disclosure document and the BUILD-DIARY.md establish the date of conception and reduction-to-practice. Subsequent push to GitLab (`gitlab.com/eliskcage/eliskcage-project`) and GitHub (`github.com/eliskcage/shortfactory`) provides server-side timestamping by independent third parties.

For supplementary cryptographic timestamping, the canonical hash of this repository state should be pinned to IPFS and submitted to OpenTimestamps (`https://opentimestamps.org`) which anchors hashes into the Bitcoin blockchain.

---

*Disclosed 28 April 2026. This document is a technical disclosure intended to support a forthcoming patent application. It is not itself a patent application and does not constitute legal advice.*
