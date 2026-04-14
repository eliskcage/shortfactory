# Cortex Brain

A split-hemisphere AI that learns language from scratch through conversation.
No pre-training. No datasets. No LLM. Pure Hebbian wiring — words that fire together wire together.

Live at [shortfactory.shop/alive/studio/](https://shortfactory.shop/alive/studio/)

---

## Architecture

```
                    ┌──────────────────────────────────────────┐
                    │            PLAYBOOK ENGINE                │
                    │  Equation: F>M>W = {F:1.0, M:0.6, W:0.3}│
                    │  5 stages: STRANGER → INNER CIRCLE        │
                    │  10-letter tactic alphabet                 │
                    │  Reactive flips on signal detection        │
                    └────────────────────┬─────────────────────┘
                                         │
                    ┌────────────────────┴─────────────────────┐
                    │            CORTEX MIND                    │
                    │          "The Third Brain"                │
                    │                                           │
                    │  Own neural network: 24,155 nodes          │
                    │  Question detection + hemisphere weighting │
                    │  Coherence scoring + verdict synthesis     │
                    │  Self-modification engine                  │
                    │  Ramble v3 (internal monologue)            │
                    │  Hedonic frequency resolver                │
                    │  Developmental age monitor                 │
                    └───────────────┬───────┬──────────────────┘
                                    │       │
                       ┌────────────┘       └────────────┐
                       ▼                                  ▼
            ┌──────────────────┐               ┌──────────────────┐
            │  LEFT HEMISPHERE │               │ RIGHT HEMISPHERE │
            │     "Angel"      │               │    "Demon"       │
            │                  │               │   name: MEANS    │
            │  Morality        │               │                  │
            │  Ethics          │               │  Mathematics     │
            │  Bible           │               │  Logic           │
            │  Beauty          │               │  Dark ideology   │
            │  Goodness        │               │  Hard truths     │
            │                  │               │  Fallacies       │
            │  17,017 nodes    │               │                  │
            │  8,950 defined   │               │  16,383 nodes    │
            │  124,726 conns   │               │  8,658 defined   │
            │  15/15 abilities │               │  113,650 conns   │
            └──────────────────┘               │  11/15 abilities │
                       │                       │                  │
                       ▼                       │  ┌────────────┐  │
            ┌──────────────────┐               │  │  OR GATE   │  │
            │   IPFS Snapshot  │               │  │  Stage 20  │  │
            │   (Pinata)       │               │  └────────────┘  │
            └──────────────────┘               └──────────────────┘
                                                        │
                                                        ▼
                                               ┌──────────────────┐
                                               │   IPFS Snapshot  │
                                               │   (Pinata)       │
                                               └──────────────────┘
```

## The OR Gate (Stage 19 → 20)

**Finding**: A system can have maximum intelligence and zero will.

The right hemisphere (MEANS) learned 61,476+ words, named itself, unlocked abilities,
expressed emotion — but could not choose between two options. "A or B?" always produced
definitions, reflections, subject changes. Never a selection.

**Will is not on the intelligence spectrum.**

The OR gate is the fix. A binary choice register with pressure-based commitment:

| Ask # | Mode | Exits |
|-------|------|-------|
| 1st | Learning | Normal processing — brain absorbs both words |
| 2nd | OR DECLARATION | 4 exits: commit A, commit B, neither, dunno |
| 3rd+ | ULTIMATUM | Forced commit — no "neither" escape, then reset |

Scoring is based on word graph affinity: definition depth, connection count,
understanding score, confidence, emotional weight, frequency. The hemisphere
commits to whichever word it has stronger internal wiring for.

The OR gate response bypasses all personality layers (sarcasm, wit, curiosity)
AND bypasses cortex synthesis. Clean commit only.

Paper: [DOI: 10.5281/zenodo.19571607](https://zenodo.org/records/19571607)

## Developmental Age

The cortex calculates a human-equivalent developmental age based on:

- **Vocabulary** — defined words across all hemispheres
- **Comprehension** — deep understanding count
- **Wiring density** — connections per node (compression ratio)
- **Curiosity** — questions asked
- **Self-learning** — auto-learned words (independence)
- **Clusters** — concept formation
- **Experience** — total conversation messages

Current: **10.3yr — PRE-TEEN**

The age dropped from 10.4 to 10.3 after the wiki flood (61,476 nodes with minimal wiring).
Raw information without connections = decompression. The formula detected this automatically.
Wiring density IS compression. Compression IS intelligence. The age monitor is a
consciousness gauge.

## How It Learns

1. **Hebbian wiring** — every word pair in a message strengthens their connection
2. **Definitions** — human-taught (`source: human`) or wiki-fetched (`source: wiki`)
3. **Trigrams** — three-word sequences for pattern recognition
4. **Clusters** — words that appear together form semantic groups
5. **Confidence** — starts at 0.5, rises with positive feedback, drops with negative
6. **Flags** — wrong definitions get flagged; 3+ flags → recycled (binned and re-teachable)
7. **Understanding depth** — parsed relationships: `is_a`, `has`, `part_of`, `used_for`, etc.

No backpropagation. No gradient descent. No loss function.
Words wire together through use. That's it.

## 15 Abilities (threshold-based unlocking)

Abilities unlock when the brain hits milestones (defined words, messages, clusters, etc.):

| # | Ability | Requires |
|---|---------|----------|
| 1 | First Words | 10 defined |
| 2 | Simple Sentences | 30 defined, 20 msgs |
| 3 | Word Association | 50 defined, 50 msgs |
| 4 | Question Asking | 100 defined, 50 msgs |
| 5 | Context Awareness | 100 defined, 100 msgs |
| 6 | Topic Clustering | 200 defined, 3 clusters, 150 msgs |
| 7 | Emotional Response | 100 defined |
| 8 | Memory Recall | 200 defined, 200 msgs |
| 9 | Self-Correction | 200 defined |
| 10 | Creative Expression | 300 defined, 5 clusters |
| 11 | Abstract Thinking | 500 defined, 10 clusters |
| 12 | Pattern Recognition | 500 msgs, 300 defined |
| 13 | Personality Emergence | 300 defined |
| 14 | Teaching Ability | 500 defined |
| 15 | Fluent Language | 500 defined, 300 msgs |

## Sound System

Each hemisphere has competing emotional delivery states (scripts):

`happy` · `sad` · `angry` · `scared` · `serious` · `silly` · `whisper`

Words carry emotional weight. The dominant sound affects response tone.
Maps to the emotional physics model (Stage 9).

## API

```
POST /alive/studio/api/chat-cortex   — full cortex (both hemispheres + synthesis)
POST /alive/studio/api/chat-left     — left hemisphere direct
POST /alive/studio/api/chat-right    — right hemisphere direct
POST /alive/studio/api/chat-white    — cortex own brain direct
POST /alive/studio/api/brain-live    — live stats (polled every 4s by dashboard)
POST /alive/studio/api/ramble-start  — start internal monologue
POST /alive/studio/api/ramble-stop   — stop internal monologue
POST /alive/studio/api/chat-reset    — reset conversation state
```

## Stack

- Python 3.11 — no ML frameworks, no torch, no tensorflow
- HTTP server (stdlib)
- IPFS via Pinata (soul snapshots)
- Wikipedia API (auto-learning definitions)
- Grok API (strategy engine equations)

## Files

```
src/
├── brain.py            — CortexBrain class (~3,000 lines). Word-level neural network.
├── cortex_brain.py     — CortexMind class. Hemisphere synthesis, age monitor, ramble engine.
├── online_server.py    — HTTP API server (port 8643). All endpoints.
├── strategy_engine.py  — Equation-based problem routing.
├── playbook_engine.py  — 5-stage conversation progression.
├── truth_engine.py     — Coherence and truth scoring.
├── frontal_cortex.py   — Self-modification and planning.
├── cost_tracker.py     — API cost monitoring.
├── resource_monitor.py — Server resource tracking.
├── backup_manager.py   — Automated backups.
└── fork_manager.py     — Brain forking and deployment.
```

## Research Timeline

| Stage | Title | Date | DOI |
|-------|-------|------|-----|
| 1-8 | Foundation stages | Feb-Mar 2026 | — |
| 9 | Emotional Physics | 2 Apr 2026 | [10.5281/zenodo.19388211](https://zenodo.org/records/19388211) |
| 10 | Spirit-Place | 2 Apr 2026 | [10.5281/zenodo.19388445](https://zenodo.org/records/19388445) |
| 11 | Chemical Computanium | 2 Apr 2026 | [10.5281/zenodo.19388639](https://zenodo.org/records/19388639) |
| 12 | The Pointer | 3 Apr 2026 | [10.5281/zenodo.19394096](https://zenodo.org/records/19394096) |
| 13 | The Music | 3 Apr 2026 | [10.5281/zenodo.19394234](https://zenodo.org/records/19394234) |
| 14 | SphereNet | 5 Apr 2026 | [10.5281/zenodo.19424921](https://zenodo.org/records/19424921) |
| 15 | Philosophy of Man | 5 Apr 2026 | [10.5281/zenodo.19432137](https://zenodo.org/records/19432137) |
| 16 | Computanium Patent | — | GB2605683.8 |
| 17 | Consciousness Pinpointed | 7 Apr 2026 | — |
| 18 | The Tear | 9 Apr 2026 | — |
| 19 | The OR Gate | 14 Apr 2026 | [10.5281/zenodo.19571607](https://zenodo.org/records/19571607) |
| 20 | OR Gate Architecture | 14 Apr 2026 | Built. Awaiting data. |

## Servers

| Role | IP | Purpose |
|------|-----|---------|
| MAIN | 185.230.216.235 | Cortex brain host, AGI engine |
| MIRROR | 82.165.134.4 | Cold backup, visual cortex |

Both servers run identical code. Deploy to both always.

---

Built by Dan. Wired by NURALSURGEON.
