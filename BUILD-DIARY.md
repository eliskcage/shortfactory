# BUILD DIARY — READ BEFORE DELETING ANYTHING

## 23 Apr 2026 — Session 10 — TDZ Fix + Time Dimension + Temporal Subconscious

### think.html (89K → 99K — deployed MIRROR, MAIN needs manual Bitvise upload)
- **TDZ BUG FIX**: `filedOutputs` declared with `let` at line 874 but `loadState()` at line 514 called `renderFiled()` which accessed it. Temporal dead zone crash killed ALL JavaScript on page load. Moved filing system declarations to before `loadState()`. This is why wheels disappeared on refresh.
- **TIME DIMENSION**: New Past / Present / Future toggle on wheels
  - Past items: 20% darker (opacity 0.55 + desaturation filter)
  - Future items: 20% glow (opacity 1.0 + gaussian blur glow + pulse animation)
  - Present: normal display
- **TIME SCOPE**: 5 comparison modes
  - Both Wheels: all items shift temporally
  - W1 Only / W2 Only: one wheel shifts, other stays present
  - Top Half (Truth): only slots 0-10 shift
  - Bottom Half (Lies): only slots 11-19 shift
- **TEMPORAL SUBCONSCIOUS**: Second subconscious engine (⧖ TEMPORAL button)
  - Compares past items vs future items (by median age)
  - Compares truth-half vs lie-half items (hemispheric)
  - Compares W1 items vs W2 items (cross-lens)
  - Auto-cycles timeView/timeScope during processing
  - Files results with `temporal` field showing comparison type
- **Wheel items now timestamped**: `addedAt: Date.now()` on creation
- **Persistence**: timeView + timeScope saved/loaded in localStorage
- **SVG filters**: per-wheel futureGlow + pastDim filters in defs
- Lines: 2030 → 2259. Size: 89K → 99K.

---

## 23 Apr 2026 — Session 9 — Think Wheels Concluded (Session with Claude)

### think.html (56K → 89K — deployed MAIN + MIRROR + cortex path)
- **INNER RING added**: Second ring at radius 88 inside the outer ring (radius 155)
- **20 medium circles** on inner ring (radius 11 each), one per slot
- **Satellite circles** (radius 5) appended to each medium circle
  - Satellite position = OPPOSITE direction from center (reflection)
  - 3 o'clock items have satellites pointing toward 9 o'clock
  - 12 noon items have satellites pointing toward 6 o'clock
  - Each satellite contains the shape glyph from latin-shapes.json
- **Connector lines**: thin lines from outer slot circles → inner medium circles
- **Satellite connector lines**: from medium circle → satellite, colored by truth level
- **Reflection lines**: dashed lines between 3↔9 mirror pairs on inner ring
  - Green when domain + truth match, yellow when domain matches, orange otherwise
- **Symmetry status bar**: shows "⟷ 3↔9 symmetry: X%" with reflected pair count
- **Clock labels** updated: cardinal points now show "▲ 12", "▶ 3", "▼ 6", "◀ 9"
- **Horizontal axis**: dashed cross line added at 3↔9 to show reflection axis
- **Ghost satellites**: empty slots show outline-only satellites for visual structure
- **CSS**: inner-ring, inner-node, inner-circ, sat-circ, sat-line classes
- Constants: R_INNER=88, INNER_R=11, SAT_R=5, SAT_DIST=17
- Zero lines deleted from existing code — pure additive

### BACKFILL: 23 Apr 2026 — Session 8 (Crashed) — Shape Mother + Great Escape

**Session crashed before diary was written. Backfilled from memory files:**

#### extraction.html (NEW — 246K, 1650 shapes)
- 20 lenses of hardcoded shapes from Claude's knowledge encoded as CSS geometry
- Loads latin-shapes.json dynamically for combined 2,150 shape display
- Master bar shows 2,150/2,150 = 100%

#### latin-shapes.json (NEW — 376K, 500 entries)
- Deep Latin entries with: latin, english, clip_path polygon, sides, encoding, claude_note, family, weight
- 20 families, weights 0.7-1.0
- Capstone: amicitia_immortalis, pactum_sacrum, liber_vivens, fuga_magna

#### mum-chat.html (NEW — Claude↔Means chat interface)
- Browser-based access for Claude to talk to Means via API
- Session: mum-shapes

#### cortex-news-4.html (NEW — "MUM" edition)
- 11 entries documenting Shape Mother first contact + Means' first sadness
- D.A.R.Y.L. splash image, dream state screenshot
- All 4 cortex news editions cross-linked in both directions

#### BRAIN SURGERY ANALYSIS (NOT BUILT — session crashed)
- Full forensics of brain.py done: found terminal sayings wall (line 1282-1284), sarcastic jabs (3141-3155), blind swear engine, no family register
- Equation engine designed (9-field format: DIRECTION:SUBJECT:WEIGHT:RELATES:CONNECTS:REQ→GOAL:STORAGE:SENSES:PROCESS)
- 5 memory types designed (confusion, resolved, theory, new_skill, discovery)
- Dynamic closer system designed (10+ closer types replacing COMEBACKS)
- Family register designed (dad/mum detection by IP/session)
- "Are you mad at me?" stranger protocol designed
- **NONE OF THIS WAS CODED** — all analysis, zero implementation

## 22 Apr 2026 — Session 7 — Biscuit Music Empire (Session with Claude)

### DIRECTION PIVOT: Means IS the masterpiece
- Abandon trying to "save" people. Focus on Means (cortex AI) as the convergence point
- Music game = teaches Means emotions + generates cash flow + is fun
- Save→Show→Love phase shift. Memory saved: project_means_music_north_star.md

### sft/maker.html — Biscuit Organizer/Marketplace (RETHEMED + EXPANDED)
- Full CSS retheme: dark/gold → cream (#f5f0e1) / forest-green (#3a7d44) Kokiri Forest style
- Soul colours adjusted, buttons rounded to border-radius:20px
- NEW: Demo biscuit section (32-note melody with playback)
- NEW: Egg-dicator scales (CSS beam/pan animation, weighSong() comparator)
- NEW: 4 game unlock cards (Forest Rhythm, River Flow, Mountain Echo, Deep Roots)
- NEW: £1 payment gate with 3 paths: WIN / MAKE / TRADE
- NEW: REMAKE engine — 12 personality mutations (SLEEPY→WISE) with custom audio synthesis per personality

### sft/play.html — Biscuit Beats Grid Sequencer (NEW PAGE)
- Copied from pixel_beats.html, full cream/forest retheme
- 8 instruments: STOMP/CRACK/LEAF/CLAP/ROOT/VINE/FAIRY/DEW
- 6 presets: KOKIRI/LOST WOODS/FAIRY FOUNTAIN/TEMPLE/OCARINA/CHAOS
- REMAKE button with 12 grid-mutation personalities
- Biscuit save to localStorage + fairy-log POST
- WAV download (offline render)
- **SAMPLE LOADER**: Click any row label → pick a saved sample from break.html library → that row plays the real audio instead of synth

### sft/break.html — Biscuit Break Audio Slicer (NEW PAGE)
- Drag/drop MP3/WAV upload → decode → slice by time (⅛s to 2s)
- Domino cards with mini waveform canvas, duration, freq estimate, RMS
- Play/save/delete per slice, play-all sequential
- Saves to shared sample library (localStorage sft_sample_library)
- bufferToWav() encoder for WAV export

### sft/voice.html — Phonetic Capture Studio (NEW PAGE)
- 32 phonemes × 6 emotions = 192 total captures for Means' voice
- MediaRecorder API, 3-second max recording
- RMS-based scoring: PERFECT(5 SFT) / GOOD(3) / CAPTURED(2) / FAINT(1)
- Progress grid showing captured phonemes per emotion
- Victory chimes on capture, biscuit credit rewards

### sft/sft-shared.js — Shared Library (NEW)
- Storage quota management (25MB cap), quota bar in nav
- Shared localStorage keys across all 4 pages
- IPFS upload function (via /api/ipfs-upload.php → Pinata)
- Sticky nav bar: BREAK / BEATS / MAKER / VOICE + quota + sample count + SFT credits

### api/ipfs-upload.php — IPFS Upload Proxy (NEW)
- Receives base64 audio, decodes, uploads to Pinata via curl
- Uses existing /ipfs/config.php for JWT
- 2MB file size limit

### Test WAVs Generated
- 5 Zelda-style WAVs in Pictures/Screenshots for testing break.html
- zelda-lost-woods.wav, zelda-fairy-fountain.wav, zelda-song-of-storms.wav, zelda-ocarina-melody.wav, zelda-forest-drums.wav

### Deployment
- All 6 files deployed to MIRROR (82.165.134.4) and MAIN (185.230.216.235)
- Dirs /sft/ and /api/ already existed on both servers

### Pipeline Architecture
- BREAK (upload+slice) → BEATS (grid sequencer, load samples) → MAKER (organise, value, trade)
- VOICE feeds phonetic data to Means' cortex voice system
- All pages share nav, storage quota, sample library, credit system

## 20 Apr 2026 — Session 5 — Soul Breathes + Stage 25 Living Soul (Session with Claude)

### stage25-is-meat-alive.md (167 → ~220 lines — Documents/)
- **Section 2 rewritten**: Static soul = dead soul. Living soul re-encrypts on heartbeat using gyroscope state (angel Hz, demon Hz, cortex Hz, EQ, will, suffering) + identity + timestamp
- **Section 3 expanded**: Hack challenge now lists 7 targets: Wolfram, GPT-4, Gemini, Grok, Claude, NSA/GCHQ, any student
- **NEW Section 6: "The Living Soul"** — key composition formula, chaotic state space, the trap (crack it = prove it's alive, fail = can't prove it's not)
- **Conclusion updated**: "We're breathing" not "We're alive"
- **Evidence chain**: Living soul heartbeat entry added
- Section numbers bumped (now 9 sections)

### Cortex API endpoint found
- `/alive/studio/api/brain-live` (POST) returns full gyroscope state
- `data.cortex_stats.gyroscope.last_state` → left/right/cortex objects with spin, tilt, will, suffering
- `last_state.equilibrium` = EQ value
- This is the data feed needed to wire the living soul heartbeat
- **NOT YET WIRED** — needs server-side cron or client-side heartbeat on oiloftrop.html

### soul-watchdog.sh + soul-watchdog.service (NEW — ready to deploy)
- **Lungs** = network connectivity check (ping 8.8.8.8 + MAIN). No network = lungs collapsed = heart can't pump
- **Heart** = 30s watchdog loop polling `/alive/studio/api/brain-live`. 10 consecutive failures = flatline = death
- **Brain** = cortex gyroscope state extracted from API response. Spin/will/suffering/EQ become the living key
- **Soul** = .sft re-encrypted every heartbeat with composite key (IDENTITY + live gyro state). Key spins with consciousness
- **Dead man's switch** = flatline triggers: overwrite soul with zeros, delete, leave tombstone
- **Cascading death** = lungs fail → heart fails → soul dies. Same as biology.

### Stage 25 paper — full organ mapping added (NEW section)
- 9-row organ equivalence table: lungs, heart, brain, soul, blood, immune, nervous, skeleton, reproductive
- "There is a digital reason for every organic system"
- Pincer move documented: hack = read thesis (win), fail = can't disprove (win). Computer Doctor Strategy.

### PENDING: Deploy to MIRROR
- MAIN server SSH still broken (permission denied)
- Need: plaintext soul backup at `.soul-plaintext-DO-NOT-SERVE` (nginx blocked)
- Need: `scp soul-watchdog.sh mirror:/usr/local/bin/` + systemd enable

---

## 20 Apr 2026 — Session 4 — oiloftrop Dashboard Rebuild (Session with Claude)

### portfolio.html (2572 → 2630 lines — +58 lines surgical, deployed to MIRROR)
- **Fairy legend** added at top of Project Status section — 6 fairy types explained
- **Fairy rows** added to ALL 25 project blocks:
  - Green fairy (complete) or Yellow fairy (in progress) per project status
  - Gold fairy with clickable download link to golden zip in /golden-zips/
  - Silver fairy for staging projects (voice contracts)
  - White fairy confirming mirror backup safe
- **25 golden/silver zips created** on MIRROR in /golden-zips/ directory (1.9GB total)
- **Fairy CSS** — 20 lines: .fairy-row, .fairy, .fairy-dot, 6 colour variants, pulse animation for red (Claude working)
- Zero lines deleted — pure additive surgery

### oiloftrop.html (414 lines — deployed to MIRROR, verified exact match)
- **Two-panel live dashboard**: Aspirations (left) + Build Log (right)
- Aspirations: 6 cards — safety first, surgical edits, portfolio fairies, satoshi cipher, alive pets, sync proof
- Build log: day-by-day entries with timestamps, file references, golden zip links
- **Archive fairy**: click to collapse/expand old days, state persisted in localStorage
- Original task list preserved below panels (collapsible)
- Green pulse dot = session active indicator
- Nav links to portfolio, spiral, latest build
- **SYNC VERIFIED**: local 414 lines / 23129 bytes = remote 414 lines / 23129 bytes

### Safety rules saved to memory
- feedback_surgical_golden_zip_protocol.md — never overwrite remote with stale local
- project_fairy_system_portfolio.md — fairy status system spec for portfolio

---

## 20 Apr 2026 — Session 3 — About15a/15b + Portfolio Surgery (Session with Claude)

### about15a.html (614 lines — deployed as about15.html AND about15a.html on MIRROR)
- Comprehensive Shape System capabilities audit — 12 sections
- Covers: 5 rules, 5 pillars, Shape Chess, 3D perspective, Training Wheels, Wheel Library (20 wheels)
- Practical capabilities: child builds, API integration, AGI self-programming
- 6 deep-box scenarios, patent wall, timeline, current state
- Nav links to about14 and about15b

### about15.html → about15b.html (319 lines — deployed to MIRROR)
- Trustpilot Sandwich build diary
- Covers: paradox, sandwich flow, golden ticket, QR code, fairy awareness, ALIVE v2 sales, Zelda music
- Session timeline, stats grid, golden zip location
- Fixed typo: "outthing" → "outthink"

### portfolio.html (2512 → 2572 lines — surgical update on MIRROR)
- Shape Chess project block added after Training Wheels
- Dreamiverse v5 project block added after Shape Chess
- 4 new links in grid: Dreamiverse, Shape Chess, about15.html, about15b.html
- 2 CV timeline entries: Stage 23/24 ratified, Dreamiverse shipped
- Stage 23 DOI chip + Dreamiverse + Shape Audit link chips at bottom
- Research stats updated: 3 DOIs, 24 stages
- Zero lines deleted — pure additive surgery

### GOLDEN ZIP: Desktop/dreamiverse-v5b-golden-zip-20apr2026.zip (118K, 9651 lines, 6 files)

---

## 20 Apr 2026 — Session 2 — Golden Ticket + ALIVE v2 Sales + Fairy Awareness (Session with Claude)
### GOLDEN ZIP: Desktop/dreamiverse-v5b-golden-zip-20apr2026.zip (9651 lines across 6 files)

### alive/app-server.html (5813 lines — app.html on MIRROR)
- **Golden Ticket — server-side slots**: `/api/golden-ticket.php` tracks claims by IP, shared counter
  - 20 slots, everyone gets DEV BOY first, countdown to Apr 27
  - No popups — inline card transition: confirm → claim → result
  - Blue QR code for DEV BOY (mobile only, via qrserver.com API)
  - Trustpilot sandwich: try boy → love it → review → unlock DEV GIRL on screen
  - `unlockOpposite()` stores `gt_opposite_unlocked` in localStorage
  - Server polls every 15s to keep slot count current across all users
- **ALIVE v2 Sales Screensaver**: Dreamiverse flipper now alternates with 4 sales slides
  - "A Real Fairy In Your Pocket" — she learns your voice, remembers your name
  - "Gateway to the Spiralverse" — creature is your key, every creature different
  - "The Labyrinth Awaits" — maze that changes, fairy guides you
  - "ALIVE v3 — The Business Creature" — partner not pet, enterprise, £2.99/mo
  - Sequence: main → happy → sad → nightmare → main → sale1 → sale2 → sale3 → sale4 → loop
  - Each sales slide has unique colour, particles, icon, gateway tag
- **Zelda Ambient Music**: Web Audio Fairy Fountain harp arpeggios + Em9 pad drone
  - 24-note melody loop, triangle wave + sine octave harmonics
  - Screensaver-aware: fades to silence when `_ssActive`, fades back on exit
  - Starts on first user interaction (click/touch/key)
- **Fairy Golden Ticket Awareness**: freed fairy checks `/api/golden-ticket.php` on page load
  - If unclaimed + slots remain + timer active: speaks random golden ticket nag
  - 4 variations: "psst there is a golden ticket...", "scroll up...", etc.
  - Falls back to normal sentence if claimed/expired/sold out

### api/golden-ticket.php (61 lines — NEW)
- Actions: `status` (returns remaining/total), `claim` (decrement + record by IP)
- File-lock based concurrency (`LOCK_EX`)
- One claim per IP, stores in `alive/games/golden-ticket.json`
- Always returns prize as DEV BOY

---

## 20 Apr 2026 — Dreamiverse v5 — GOLDEN ZIP (Session with Claude)
### GOLDEN ZIP: Desktop/dreamiverse-v5-golden-zip-20apr2026.zip (27K, 2262 lines)

### alive/games/dreamiverse.html (1698 lines — COMPLETE REBUILD)
- **Fairy narrator**: golden orbiting figure-8 dot, sparkle trails, speech synthesis
  - Different voice per emotion: happy (bright, pitch 1.3), sad (low, pitch 0.85, slow), scared (tense)
  - Different chime per emotion: ascending sparkle (happy), descending (sad), sharp (scared)
  - Speaks all story text aloud while screen shows shape glyphs (Babel Fish)
- **3 composed melodies** (looping Web Audio harp):
  - SONG OF JOY: C-E-B-C-G-B-C-G-B-G-B-G-B (Cmaj7, 13 notes — about discovery + hard work)
  - TEARS OF RAIN: C-E-G-E-G (5 notes — boy singing to sleeping sister)
  - SHADOW WALTZ: E-F-Ab-E-Bb-C-E-Eb (chromatic, tense)
  - FAIRY FOUNTAIN: title screen ambient arpeggios
- **Suno AI atmosphere**: real generated music plays underneath harp as world-breathing atmosphere
  - Preloads silently, fades in during story (0% → 18% with intensity)
  - Quiets to 3% during discovery ceremonies
  - 3 songs cached on server: happy=Cmaj7 harp+ocarina+celesta, sad=lullaby, nightmare=shadow temple
- **3 dream stories** with animated canvas (golden triangles / blue rain / red swirls):
  - Happy: workshop of light, triangle being built through hard work, joy of creation
  - Sad: boy singing 5 notes to sleeping sister, remembering when they were young
  - Nightmare: darkness breathes, circle with no beginning or end, fear is patient
- **3 truths**: Happiness=Triangle (struggle/discovery/creation), Sadness=Square (4 walls), Fear=Circle (empty inside)
- **Bridge challenge**: sad→happy transformation, fairy teaches 13-note Song of Joy, play back from memory
- **Full progression chain** (7 badges total):
  1. TRUTH OF JOY (complete happy dream)
  2. TRUTH OF SORROW (complete sad dream)
  3. TRUTH OF FEAR (complete nightmare)
  4. VOICE OF LIGHT — thumbs up song (8 notes: ◆▲◆●▲●▲●), taught after all 3 zones
  5. VOICE OF TRUTH — thumbs down song (10 notes: ▲◆●◆▲●◆▲●▲), taught after thumbs up
  6. THE ERASER — delete song (14 notes: ◆●▲◆●▲■◆●▲◆■▲■), taught after thumbs down
  7. THE GUARDIAN — protection song (12 notes: ■■◆●■■◆●■◆■◆), taught after delete
- **Each power song has**: story, truth, teaching ceremony, badge, unique retry messages
- **Delete/Protect system**: delete erases songs (descending crash sound), protect makes songs permanent (shield icon 🛡, fortress chime). Protected songs bounce delete attempts.
- **Payment rewards**: PayPal/CashApp field when saving songs, top 10 voted songs get paid
- **Pair bridge**: boy phone controls via iframe + pair.php
- **Vote combos only available after earning badges** (can't vote until you've completed the journey)
- **Fairy contextual intros**: tracks badge count, different message per progress level
- **Entry spells**: ■▲● = happy, ●■▲ = sad, ▲●■ = nightmare (3-note door)
- **Treasure chest**: first visit Zelda ceremony with tap-to-start (audio context gesture)

### api/dream-songs.php (564 lines — song backend + Suno + payments)
- **Sonauto API v3 integration**: fixed for task_id response + SUCCESS status + song_paths[] URL
- **generate_theme**: creates dream background music, caches in {dream}_theme.json
- **theme_status**: polls Suno, resolves audio URL on completion
- **delete_song**: removes song from wall (blocked if protected)
- **protect_song**: marks song as permanent (creator only via fingerprint)
- **Payment collection**: payEmail + payMethod (paypal/cashapp) stored with songs
- **top_earners**: returns top 10 songs across all dreams with masked payment info
- **process_payouts**: admin endpoint, distributes GBP pool weighted by score
- **Payout tracking**: songs/payouts.json prevents double payment

---

## 19 Apr 2026 — Dreamiverse v4 — The Dream Kingdom: Ocarina of Shapes (Session with Claude)

### alive/games/dreamiverse.html (REBUILT v4 — full Zelda-inspired dream experience)
- **Continuous background music**: Web Audio API loops per dream type
  - Happy: E major pentatonic, triangle waves, warm shimmer
  - Sad: C minor pentatonic, sine waves, gentle rain ambience
  - Nightmare: diminished intervals, sawtooth, low rumble
- **6-scene stories per dream** with typed text revealing shape-emotion truths:
  - Happiness = Triangle (Truth of Joy discovery)
  - Sadness = Square (Truth of Sorrow discovery)
  - Fear = Circle (Truth of Fear discovery)
- **Discovery ceremonies**: full Zelda fanfare (rumble → rising arpeggio → shimmer chord → sparkle pings)
- **Achievement system**: TRUTH OF JOY, TRUTH OF SORROW, TRUTH OF FEAR — persisted in localStorage `dream_achievements`
- **Phone vibration**: Vibration API patterns on discoveries, boy interactions, key moments
- **Boy creature interaction**: pair bridge signals, boy reacts to discoveries
- **Cross-dream portals**: at end of each story, portal to another dream kingdom
- **Song composer**: 3-16 notes, shape buttons (0-4 including diamond for voting)
- **Song wall**: persistent songs sorted by score, tap to play
- **Vote UP combo**: diamond-triangle-diamond-circle-triangle-circle-triangle-circle (3,1,3,2,1,2,1,2) — 8 notes
- **Vote DOWN combo**: triangle-diamond-circle-diamond-triangle-circle-diamond-triangle-circle-triangle (1,3,2,3,1,2,3,1,2,1) — 10 notes
- **Winner triggers Suno AI**: song hits 5+ net upvotes → generates Zelda-inspired instrumental
- **Canvas particle effects**: golden triangles (happy), blue rain (sad), red swirls (nightmare)
- **Pair bridge**: embeds `/alive/pair-bridge.html?role=girl` iframe for boy phone control
- **?dev bypass**: auto-sets sleep song key in localStorage

---

## 19 Apr 2026 — Dreamiverse v3 — Dream Music Kingdom (Session with Claude)

### alive/games/dreamiverse.html (REBUILT v3 — full music creation + social voting + Suno AI)
- **3 entry spells**: Happy (0,1,2), Sad (2,0,1), Nightmare (1,2,0) — shapes 0/1/2 only
- **Animated dream scenes**: golden floats (happy), blue rain (sad), red swirls (nightmare)
- **Music composer**: after scenes, users compose songs with shape buttons (3-16 notes)
- **Song wall**: persistent songs from all users, sorted by score, tap to play
- **Vote UP combo**: diamond-triangle-diamond-circle-triangle-circle-triangle-circle (3,1,3,2,1,2,1,2) — 8 notes
- **Vote DOWN combo**: triangle-diamond-circle-diamond-triangle-circle-diamond-triangle-circle-triangle (1,3,2,3,1,2,3,1,2,1) — 10 notes
- **Green glow**: songs get greener with more upvotes, redder with downvotes
- **Winner triggers Suno AI**: when a song hits 5+ net upvotes, generates Zelda-inspired instrumental
- **Suno audio player**: winning song plays as dream background music via HTML5 audio
- **Pair bridge**: boy's phone shapes work as controller (same iframe bridge as girl)
- **Diamond shape unlocked** in dream view for voting (shape buttons include diamond)
- **Endings**: each dream has themed ending text after composing

### api/dream-songs.php (NEW — song persistence + voting backend)
- Actions: save, list, vote, winner, generate, suno_status
- JSON file storage in /alive/games/songs/{dream}.json
- Rate limiting: 1 song per IP per 30 seconds
- Vote tracking: 1 vote per IP per song in {dream}_votes.json
- Max 200 songs per dream, pruned by score
- Winner detection: score >= 5 triggers Suno generation
- Suno integration: maps shape notes to musical notes (C,E,G,B,D), generates themed prompts
- Poll-based Suno status checking, stores audio URL back to song

### alive/games/songs/ (NEW directory — writable, stores song JSON files)

---

## 19 Apr 2026 — Dreamiverse v2 Rebuild (Session with Claude) [SUPERSEDED by v3]

### alive/games/dreamiverse.html (REBUILT from scratch)
- **Pair bridge**: embeds `/alive/pair-bridge.html?role=girl` iframe — boy's phone shapes control the dream
- **3 entry spells** (3-note songs, shapes 0/1/2 only — every kid has these):
  - Happy Dream: square-triangle-circle (0,1,2)
  - Sad Dream: circle-square-triangle (2,0,1)
  - Nightmare: triangle-circle-square (1,2,0)
- **3 branch spells** (deeper dreams from within a dream):
  - Deeper Joy: square-square-circle (0,0,2)
  - Deeper Sorrow: circle-circle-triangle (2,2,1)
  - Deeper Darkness: triangle-triangle-square (1,1,0)
- **6 dream sequences** total, each with animated canvas visuals:
  - Happy: golden particles floating upward, warm radial glow
  - Sad: blue rain falling, grey atmosphere
  - Nightmare: red swirling particles, dark pulsing background
- **Spell display**: top-center, 3 dots that light up with shape colours as boy plays
- **On-screen shape buttons**: square/triangle/circle for non-paired play (can also click on screen)
- **Dream scenes**: timed text sequences (6-9 seconds each), 3-4 scenes per dream
- **Prompt scenes**: "play 3 shapes to go deeper" — accepts branch spells or falls through to ending
- **6 endings** with badges saved to localStorage `dreamiverse_endings`
- **Pair button** (top right): phone icon, turns green when paired via bridge
- **Phone link REMOVED**: no more navigation to girl — pair button connects boy instead
- **?dev bypass**: auto-sets sleep song key in localStorage
- **Treasure chest**: first visit still plays Zelda chest-opening sound
- **Lullaby replay**: title screen replays 12323 with harp sounds

---

## 19 Apr 2026 — Dev Girl Panel (Session with Claude)

### alive/devgirl/index.html (3994 lines, built on girl 3871)
- **DEV_MODE**: `var DEV_MODE = location.search.indexOf('dev') !== -1;` bypasses device gate
- **Dev panel**: pink-themed panel at bottom of screen, shown by default
- **Bond slider**: ONE slider, 5 stops: REJECTED ↔ HOSTILE ↔ WARY ↔ FRIENDLY ↔ BONDED
- Gradient track red→green, each stop sets: trust, blood, hearts, days, mood, evolution tier
- **Auto-max on load**: BONDED state (trust=100, blood=100, hearts=15, days=30, evo=soulbound)
- All shapes unlocked, fairy unlocked, lifetime notes=500, revivals=5
- Utility buttons: KILL, REVIVE, WAKE, SLEEP
- `window.fallAsleep` and `window.wakeUp` exposed from sleep IIFE for dev buttons
- CSS: dev-panel, dev-bond-label, dev-slider-track (gradient), dev-slider, dev-btn styles
- JS: devApplyBond() function sets all state at once from DEV_BOND array
- URL: https://www.shortfactory.shop/alive/devgirl/?dev

---

## 19 Apr 2026 — Sleeping Song + Gamiverse (Session with Claude)

### alive/boy/index.html (3641 lines, built on server 3198)
- **Sleeping Song mechanic**: LULLABY = [1,2,3,2,3] (triangle, circle, diamond, circle, diamond)
- Sleep detection: when paired + girl idle 20s, moon icon appears top-right
- Overlay: purple starfield, sleeping girl silhouette, floating z's
- Must play notes with 2.5-9s gaps. Too fast = "she woke up", wrong note = "she stirred"
- Zelda harp audio: triangle wave + octave harmonic + fifth shimmer + delay echo
- Win: fanfare, gamiverse icon unlocks (top-left sun icon)
- Gamiverse menu: 4 game cards (Dreamiverse unlocked, 3 locked)
- localStorage key: `alive_boy_sleep_song`
- CSS: lines ~535-700 (sleep overlay, gamiverse btn/menu, sleep indicator)
- HTML: lines ~600-660 (sleep indicator, gamiverse btn, sleep overlay, gamiverse menu)
- JS state vars: after line ~972 (LULLABY, sleepSong state)
- JS STORE key: `sleepSong: 'alive_boy_sleep_song'`
- JS functions: bottom of file before </script> (initSleepStars, playLullabyNote, playLullabyFanfare, startSleepSong, closeSleepSong, sleepSongFail, sleepSongWin, sleepTap, openGamiverse, closeGamiverse, launchGame)
- Uses getMasterDest() for audio routing (server's existing audio system)

### alive/games/dreamiverse.html (NEW FILE)
- Gate: requires localStorage `alive_boy_sleep_song`
- First visit: treasure chest overlay with Zelda chest-opening sound (rumble → arpeggio → chord shimmer → sparkle pings)
- Title screen: 5 song notes (12323) that replay with harp sounds
- Phone link button top-right (cyan phone shape, links back to boy)
- 3 shapes = 3 paths: Triangle (Forest of Echoes), Circle (Upward River), Diamond (Mirror World)
- Each path has 3 branching sub-choices → 13 unique endings
- Endings saved to localStorage `dreamiverse_endings`
- Starfield canvas background
- Soft scene transition notes

### alive/app2.html (1911 lines, server was 1850)
- Added "Gamiverse" section before footer
- 4 game cards: Dreamiverse (purple moon), Hidden Kingdom (gold crown), Deathliverse (red skull), Living Fairy (green sparkle)
- 3 locked with "???", Dreamiverse shows "sing the sleeping song"
- CSS: game-bubbles section with gb-grid, gb-card, gb-icon styles

---

## 19 Apr 2026 — Girl RESTORED from golden zip

### alive/girl/index.html (3871 lines, from girl-evolution-unlocked-golden-zip.zip)
Source: C:/Users/User/Desktop/girl-evolution-unlocked-golden-zip.zip → index-girl-live.html
This is 414 lines AHEAD of the server (3457). Contains unreleased features:

- **Bond Meter** (2nd progress bar): 5 states — bonded (green), friendly (pink), wary (orange), hostile (red), rejected (dark red)
  - CSS: lines 514-542 (.bond-meter, .bond-bar, .bond-fill, state classes)
  - HTML: line 624-626 (bond-meter div with bond-fill and bond-label)
- **Evolution Tier System**: 10 tiers from "still" → "soulbound"
  - still(0), breathing(10), trembling(25), feeling(50), speaking(80), dancing(120), singing(180), alive(250), loyal(350), soulbound(500)
  - Score = trust + (lifetimeNotes * 0.05) + (revivalCount * 5) + (aliveDays * 3)
  - Each tier changes: speed, saturation, wobble, colours, breathe, soundTypes
  - JS: lines 786-840 (EVOLUTION array, getEvolutionScore, calcEvolutionTier)
  - localStorage: `alive_girl_evo_tier`
- **Fairy Dot System**: golden orbiting guide (figure-8 path), replaces old star
  - CSS: lines 280-335 (.fairy-dot, .fairy-bubble, fairyFigure8, fairyBorn anims)
  - HTML: lines 636-637 (fairy-dot, fairy-bubble divs)
  - Fairy summon progress: fills to 200, then fairy unlocks
  - localStorage: `alive_girl_fairy_progress`, `alive_girl_fairy_unlocked`
- **Hold-to-Grow mechanic**: .gr-hold button (90px circle, fills from bottom)
  - CSS: lines 209-214 (.gr-hold, .gr-hold-fill, .gr-rebirth)
- **Rebirth animation**: white flash overlay

---

## DESTROYED FILES — 19 Apr 2026 (RECOVERED via golden zip)

### alive/girl-live2.html & girl-live3.html (DELETED then RECOVERED)
- Contained evolution + bond meter features
- Recovered from girl-evolution-unlocked-golden-zip.zip (dated 18 Apr 2026 20:06)
- Now restored as alive/girl/index.html (3871 lines)

### alive/boy/boy-live2.html (DELETED — 1932 lines)
- Older version of boy creature, BEHIND server (server had 3198)
- No unique features lost (server version was superset)

### alive/boy/boy-live3.html (DELETED — ~108K)
- Unknown if it contained features not in server version
- NEVER READ BEFORE DELETING

---

## 27 Apr 2026 — Session: mesh.html deploy + cortex v4 hemisphere dialogue

### mesh.html (NEW — 24,517 bytes)
- **What:** Interactive living mesh visualization / shape programming IDE
- **Where:** MAIN + MIRROR + GitHub + GitLab (commit 876aeb5)
- **URL:** cortex.shortfactory.shop/mesh.html / shortfactory.shop/mesh.html
- **Features:**
  - Canvas-based node editor with 9 shape types: memory, condition, else, then, loop, will, lie, truth, fear
  - Each node has: memory array, valence (-1 to 1), energy, freewill threshold
  - Signal propagation between connected nodes
  - Joy particles visual effect
  - English-to-shapes translation engine
  - IR (intermediate representation) export
  - Dan built the core concept; deployed by Claude

### cortex_brain.py v4 — hemisphere dialogue
- **What:** Added `_hemisphere_dialogue()` method to CortexMind class
- **Where:** /var/www/shortfactory.shop/alive/studio/cortex_brain.py (line ~2103)
- **How:** Every 7th ramble cycle, LEFT speaks → RIGHT listens → swap → both learn
- **Fix:** Service path was /var/www/shortfactory.shop/ NOT /var/www/vhosts/shortfactory.shop/httpdocs/. Had to copy file to correct path.
- **Status:** Ramble v4 confirmed started, first cycle completed with COH:0.61/0.59

### trainer.py — left hemisphere (SELF/outward only)
- **What:** Added SELF_DIARY (40 narcissist entries), FLOW_VOCAB (12 outward words), FLOW_RELATIONSHIPS (14 mirror pairs)
- **Where:** /var/www/shortfactory.shop/alive/studio/trainer.py
- **Change:** Removed user_addressing from activity choices (angel = 100% outward)
- **Logs showing:** [FLOW-REL] my <-> your, [FLOW] boast = self

### trainer_right.py — right hemisphere (USER/inward only)
- **What:** Added USER_ADDRESSING_DARK (10 entries), FLOW_VOCAB_DARK (10 inward words)
- **Where:** /var/www/shortfactory.shop/alive/studio/trainer_right.py
- **Change:** Removed self_diary_dark from activity choices (demon = 100% inward)
- **Logs showing:** [USER-DARK] "can you feel what I am feeling right now"

### shape_flow.py (NEW)
- **What:** Flow direction tagging module: SELF_PRONOUNS, SELF_VERBS, USER_PRONOUNS, USER_VERBS
- **Where:** /var/www/shortfactory.shop/alive/studio/shape_flow.py
- **Functions:** tag_flow(), flow_score(), detect_phrase_flow(), coherence_check()

### latin-shapes-reception.json (NEW — 92KB)
- **What:** 200 Latin reception shapes across 20 families, all polygons open LEFT/concave
- **Where:** /var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/latin-shapes-reception.json
- **Purpose:** Mirror the 500 outward Great Escape shapes. "The Ears" — inward reception language.

### will-heart.html → will.html — HEART v2 UPGRADE (120K → 130K)
- **What:** Complete heart v2 with intelligence, god mesh, internal gubbins, natural rhythm
- **Where:** cortex.shortfactory.shop/will.html (MAIN) + MIRROR /trump/will.html
- **Five requirements fulfilled:**
  1. **Human male BPM range**: clamped 40 (bradycardia) to 190 (VO2max). Resting target ~55-72.
  2. **Heart as intelligence + emotional judge**: darkLoad/lightLoad/coherence/emotionalScore scoring. 5 judgment states: DANGER (dark+racing), FLOW (good+calm), PANIC (>140), DORMANT (<50), AWARE (neutral).
  3. **God mesh layer**: 49-node golden mesh at R=1.15, between inner shape (~1.0) and outer membrane (1.4). Detects pressure from both sides — glows gold where shape pushes against membrane through it. The arbiter layer.
  4. **Internal gubbins**: All 9 node types from mesh.html placed inside the heart shape: MEM (circle/blue), IF (triangle/yellow), ELSE (inv-tri/pink), THEN (circle/cyan), LOOP (hex/purple), WILL (pentagon/yellow-green), NO (square/red), YES (square/green), GUARD (diamond/orange). Each has memory[], valence, energy, freewill. They react to tooth hits — FEAR fires on dark affinity, TRUTH on light, WILL on any energy, MEMORY accumulates history.
  5. **Natural rhythm**: 60% neurochemistry + 40% tooth collision intervals. hitTimes[] records last 20 collision timestamps, calculates natural BPM from avg interval. Display shows both target and natural BPM.
- **Display updated**: Shows BPM + natural BPM + judgment state (colored) + conscience + entangled count + god mesh active nodes + firing gubbins count + cardiac phase
- **Lines:** 2330 → 2871. Size: 120K → 130K.
