
with open('C:/Users/User/AppData/Local/Temp/trump/portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '  <div class="projects">'
end_marker_after = '  </div>\n</div>\n\n<!-- 25 MAR 2026'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker_after)

before = content[:start_idx]
after = content[end_idx:]

new_projects = '''  <div class="projects">

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/fiver.html">Revert Fiver \u2014 Node Chain + Shard Auction</a></div>
        <div class="proj-status live">LIVE \u2014 SHIPPED 29 Mar 2026</div>
      </div>
      <div class="proj-desc">\u00a35 entry into a self-replicating payment chain \u2014 each fiver funds the next recruit\u2019s node. 10 encrypted story shards auctioned to fund the chain: Satoshi-cipher (Vigen\u00e8re ASCII 32\u2013126) per shard, Claude-logo visual states (lit=live, shimmer=bidding, dark=sold), anti-shill bid logic, shard revenue feeds fiver payouts. Ask \u2192 Prove \u2192 Receive.</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:100%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">100%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Shipped. join.html + fiver.html live on both servers. Stripe Payment Link flow, ref ID pass-through.</div>
      <div class="proj-tasks">
        <span class="pt done">fiver.html \u2014 pitch page, shard preview, pay CTA</span>
        <span class="pt done">join.html \u2014 Stripe Payment Link redirect, ref ID pass-through</span>
        <span class="pt done">Satoshi cipher layer (Vigen\u00e8re ASCII 32\u2013126) on shards</span>
        <span class="pt done">10-shard auction system \u2014 bid/live/dead visual states</span>
        <span class="pt done">Anti-shill logic \u2014 minimum bid intervals, wallet limits</span>
        <span class="pt done">Deployed to both servers (82.165.134.4 + 185.230.216.235)</span>
        <span class="pt pending">api/join-webhook.php \u2014 link Stripe payment to DB node record</span>
        <span class="pt pending">100 Level 1 dividends \u2014 payout logic</span>
        <span class="pt pending">Phone-size app: swarm empire UI</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="https://stinkindigger.info" target="_blank">Dares4Dosh</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Full dare platform \u2014 React 19 + PHP REST API live at stinkindigger.info. Propose \u2192 stake \u25b3 tokens \u2192 Dan funds \u2192 record proof \u2192 community votes \u2192 XMR or \u25b3 payout. Soul sigil ritual login (9 inner nodes + SADIST/MASOCHIST outer ring). Voice Contract V3 \u2014 WATCHER sets dare by mic, DOER accepts, contract sealed with hash + SVG artifact. <strong style="color:#22c55e;">Pinata JWT live \u2014 real IPFS pinning active. FULLY SHIPPED.</strong></div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:100%;background:linear-gradient(90deg,#22c55e,#00d4ff);"></div></div>
        <div class="proj-pct" style="color:#22c55e;">100%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-ok"></span> <strong style="color:#22c55e;">\u2713 SHIPPED \u2014 27 Mar 2026</strong> \u00b7 All blockers cleared \u00b7 Real IPFS live \u00b7 <a href="/dares4dosh/v3.html" style="color:#daa520;">Voice Contract V3 \u2192</a> \u00b7 <a href="https://stinkindigger.info" target="_blank" style="color:#daa520;">Live App \u2192</a> \u00b7 <a href="/launch.html" style="color:#daa520;">Launch Page \u2192</a></div>
      <div class="proj-tasks">
        <span class="pt done">React 19 + Vite app (stinkindigger.info)</span>
        <span class="pt done">Full PHP REST API (18 endpoints)</span>
        <span class="pt done">Auth \u2014 token paste + .sft / .json file drag</span>
        <span class="pt done">Soul Sigil ritual login \u2014 9 nodes unlock page</span>
        <span class="pt done">Soul Sigil outer ring \u2014 SADIST / MASOCHIST nodes</span>
        <span class="pt done">Voice Contract V3 \u2014 mic-driven dare deal, 30s seal, hash + SVG</span>
        <span class="pt done">Landing page \u2014 V1 (local) / V2 (mobile-first) / V3 (voice contract)</span>
        <span class="pt done">Stable Vite build \u2014 index-app.js / index-app.css (no hash rotation)</span>
        <span class="pt done">Propose tab \u2014 ranked by \u25b3 token stake</span>
        <span class="pt done">Fund button (Dan only) \u2014 bounty + payout type</span>
        <span class="pt done">ProofRecorder \u2014 camera, 60s, ComicVID compression</span>
        <span class="pt done">IPFS upload \u2014 Pinata JWT live, real decentralised pinning \u2713</span>
        <span class="pt done">5-vote judgment chain \u2014 XMR or \u25b3 tokens credited</span>
        <span class="pt done">Soul evolution \u2014 stats change by dare type + risk</span>
        <span class="pt done">Rank progression (normy \u2192 architect)</span>
        <span class="pt done">\u25b3 Triangle token economy + staking</span>
        <span class="pt done">Governance \u2014 CHAD+ vote on shape exchange rates</span>
        <span class="pt done">Soul Forge token mint</span>
        <span class="pt done">Architecture doc (Oracle-ready)</span>
        <span class="pt done">Launch page \u2014 professional product showcase</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/alive/kickstarter.html">Direct Funding</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Kickstarter rejected this. Twice. Now funding is direct \u2014 crypto (XMR/BTC), GPU compute via screensaver, no middlemen, no gatekeepers. Dan keeps 100%.</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:95%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">95%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Live. Real XMR/BTC wallets active. API health bar tracking donations.</div>
      <div class="proj-tasks">
        <span class="pt done">Pitch page (rejection story)</span>
        <span class="pt done">Pitch video (portrait MP4)</span>
        <span class="pt done">AI music soundtrack</span>
        <span class="pt done">Founder story section</span>
        <span class="pt done">Crypto funding tiers (XMR/BTC/GPU)</span>
        <span class="pt done">API health bar (live balance)</span>
        <span class="pt done">Cinematic movie (landscape)</span>
        <span class="pt done">Fund modal on homepage</span>
        <span class="pt done">Battery bar integration</span>
        <span class="pt done">Real XMR/BTC wallet addresses</span>
        <span class="pt pending">Marketing push (socials, Reddit, HN)</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/trump/game/cat/">Pricey Cat: Deluxe</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Canvas browser game \u2014 perspective room system, wall climbing, feral mode, face pounce, infinite procedural houses, full room modder with SFT receipt economy, entropy-based sprite pipeline, 31 sound effects, AI voice commentary</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:95%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">95%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Feature-complete. Community content pipeline active.</div>
      <div class="proj-tasks">
        <span class="pt done">Core game loop</span>
        <span class="pt done">3 houses (Karen/Becky/Pat)</span>
        <span class="pt done">Perspective room system</span>
        <span class="pt done">Wall climbing + feral mode</span>
        <span class="pt done">Face pounce attack</span>
        <span class="pt done">Mom AI (chase/slip/scream)</span>
        <span class="pt done">Infinite procedural houses</span>
        <span class="pt done">Full room modder</span>
        <span class="pt done">Sprite pipeline (Grok 4-stage)</span>
        <span class="pt done">SFT receipt system</span>
        <span class="pt done">Asset browser</span>
        <span class="pt done">Entropy shredder</span>
        <span class="pt done">Desktop + mobile</span>
        <span class="pt done">AI voice commentary</span>
        <span class="pt done">31 MP3 sound effects</span>
        <span class="pt pending">Community room sharing</span>
        <span class="pt pending">Leaderboard</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/fuel/">Fuel Dashboard</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Crypto funding as a car cockpit \u2014 10 wallet QR codes, live SVG gauges with needle oscillation, rev sounds, 3-phase cinematic intro, windshield road video, BIP39 user wallets, dual-mode (Empire/Wallet)</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:92%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">92%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Live. Real crypto wallets, 10 coins, user wallet generation, road video loop.</div>
      <div class="proj-tasks">
        <span class="pt done">3-phase cinematic intro (ignition \u2192 video \u2192 dash)</span>
        <span class="pt done">4 SVG gauges (GPU/CPU/RAM/HDD) with oscillation</span>
        <span class="pt done">10 crypto wallet QR codes (XMR/BTC/ETH/SOL/LTC/DOGE/FIL/USDT/ICP/MATIC)</span>
        <span class="pt done">Rev sound engine (Web Audio API)</span>
        <span class="pt done">BIP39 user wallet + 12-word seed phrase</span>
        <span class="pt done">Empire/Wallet mode toggle with QR glow</span>
        <span class="pt done">Windshield road video (2 alternating loops)</span>
        <span class="pt done">Community pot + user pot with live API data</span>
        <span class="pt done">Safe mode (scrollable fallback)</span>
        <span class="pt done">Desktop wallet monitor (Python)</span>
        <span class="pt done">Mobile positioning polish</span>
        <span class="pt done">Real-time gauge data from screensaver</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/trump/game/">Trump v Deep State</a></div>
        <div class="proj-status live">LIVE v2.9</div>
      </div>
      <div class="proj-desc">Political satire browser game \u2014 AI gatekeeping, oil economy, impeachment, litigation, stock market, 7 advisors, crowdsourced content pipeline, AI voice narration</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:90%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">90%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Feature-complete. Polish + content pipeline ongoing.</div>
      <div class="proj-tasks">
        <span class="pt done">Core game loop</span>
        <span class="pt done">AI gatekeeping (Grok)</span>
        <span class="pt done">Oil economy + stock market</span>
        <span class="pt done">7 advisors system</span>
        <span class="pt done">Impeachment + litigation</span>
        <span class="pt done">Crowd content pipeline</span>
        <span class="pt done">AI voice narration</span>
        <span class="pt done">Mobile responsive</span>
        <span class="pt done">v2.9 release</span>
        <span class="pt pending">Content pipeline: more scenarios</span>
        <span class="pt pending">Leaderboard / high scores</span>
        <span class="pt pending">Share result cards</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/alive/studio/">Cortex Brain</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Split-hemisphere AI brain \u2014 Angel vs Demon, Cortex Mind synthesises both. 57,555 nodes. Equation Forge visual builder. Gauntlet hostility system. 5 peer-reviewed papers. 2 UK patents. First working demonstration of autonomous symbol grounding via geometric equation discovery. <a href="/alive/studio/wiki.html" style="color:#00ccff;font-weight:700;">Wiki \u2192</a> | <a href="/alive/studio/forensics.html" style="color:#4a8;">Forensics</a> | <a href="/alive/studio/swarm.html" style="color:#00ccff;">Swarm</a></div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:90%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">90%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Live. Equation Forge + Gauntlet + AI README. 1,633 lines added Feb 23.</div>
      <div class="proj-tasks">
        <span class="pt done">Word-level neural network (brain.py)</span>
        <span class="pt done">Hebbian learning (fire together, wire together)</span>
        <span class="pt done">Semantic understanding engine</span>
        <span class="pt done">Split hemisphere architecture (left/right)</span>
        <span class="pt done">Cortex Mind synthesis (third brain)</span>
        <span class="pt done">Ramble mode (internal monologue)</span>
        <span class="pt done">Bible + morality training curriculum</span>
        <span class="pt done">Math + ideology dark curriculum</span>
        <span class="pt done">Automated 24/7 trainers</span>
        <span class="pt done">Live dashboard with hemisphere stats</span>
        <span class="pt done">IPFS persistence (Pinata)</span>
        <span class="pt done">Cross-pollination (hemispheres talk to each other)</span>
        <span class="pt done">Truth engine (lie chain detection, credibility scoring)</span>
        <span class="pt done">Frontal cortex (embarrassment/confidence per topic)</span>
        <span class="pt done">Forensic analysis dashboard (humanity vs self-modification)</span>
        <span class="pt done">Word source tagging (see which hemisphere each word comes from)</span>
        <span class="pt done">Swarm impact forensics (distributed computing analysis)</span>
        <span class="pt done">Self-modification engine (self-score, self-reinforce, memory consolidation)</span>
        <span class="pt done">Playbook equation system (10-letter tactic algebra, 5 conversation stages)</span>
        <span class="pt done">Knowledge gap diagnostics (auto-detect undefined high-frequency words)</span>
        <span class="pt done">Bulk data pipeline (11 rounds, 28K+ definitions across 3 hemispheres)</span>
        <span class="pt done">IPFS mind snapshots (Pinata persistence, brain state backup/restore)</span>
        <span class="pt done">Persistent emotional memory (CockroachDB + Supabase multi-backend)</span>
        <span class="pt done">Memory value system (golden/good/meh/dogshit ranking + decay)</span>
        <span class="pt done">4 emotional memory banks (happy/sad/angry + fast short-term cache)</span>
        <span class="pt done">Multi-database failover with latency racing</span>
        <span class="pt done">Dashboard memory panel (live emotion counters, value distribution, backend status)</span>
        <span class="pt done">Neon PostgreSQL 17 \u2014 third memory backend (US East, serverless)</span>
        <span class="pt done">Strategy Engine \u2014 7 strategies scored against 7-dim problem vectors</span>
        <span class="pt done">Organic strategy learning (ramble loop + user chats evolve weights)</span>
        <span class="pt done">Strategy dashboard (leaderboard, dimension distribution, event log)</span>
        <span class="pt done">Strategy badges on chat messages (live strategy + score display)</span>
        <span class="pt done">Dynamic equation library with CRUD + correction feedback</span>
        <span class="pt done">Equation Forge \u2014 visual builder (coloured blocks, sliders, 8 templates)</span>
        <span class="pt done">Leaderboard dimension pips (7 coloured dots per equation)</span>
        <span class="pt done">Gauntlet equation \u2014 hostility detection + value detection</span>
        <span class="pt done">AI README endpoint (GET /api/equation-readme)</span>
        <span class="pt done">Gap word teaching (26 words \u00d7 3 sentences \u00d7 2 brains = 156/156)</span>
        <span class="pt pending">Deep understanding scoring</span>
        <span class="pt pending">Cortex code-writing ability</span>
        <span class="pt pending">Voice output via PersonaPlex (creature speech)</span>
        <span class="pt pending">Memory-informed responses (recall relevant past conversations)</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name">Voice Cloning + Real-Time Speech</div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">AI voice cloning (Chatterbox TTS) + real-time full-duplex conversation (NVIDIA PersonaPlex 7B). Zero-shot voice clone from 5s sample. 70ms speaker switch \u2014 18x faster than Gemini Live. RTX 4090 24GB for local inference. Nebius cloud GPU behind paywall for users. Hybrid architecture: PersonaPlex real-time voice + Grok async deep thinking. <a href="https://youtu.be/F8azuAgfwQ0" style="color:#daa520;">Movie v2 on YouTube</a></div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:90%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">90%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Voice pipeline complete. Chatterbox TTS + PersonaPlex 7B. Local + cloud deployment planned.</div>
      <div class="proj-tasks">
        <span class="pt done">Voice sample collection</span>
        <span class="pt done">Research voice cloning models</span>
        <span class="pt done">Chatterbox TTS zero-shot clone (5s WAV)</span>
        <span class="pt done">Movie v1 POC (9 voice lines, text-on-black)</span>
        <span class="pt done">Movie v2 Epic (13 lines, Mandelbrot, 3-act, YouTube)</span>
        <span class="pt done">FFmpeg movie pipeline (voice gen + video build)</span>
        <span class="pt done">PersonaPlex research + architecture plan</span>
        <span class="pt done">RTX 4090 24GB VRAM secured</span>
        <span class="pt done">ALIVE creature persona (BIOS text prompt written)</span>
        <span class="pt done">Hybrid architecture designed (PersonaPlex + Grok async)</span>
        <span class="pt done">WebSocket bridge protocol mapped (WSS + Opus decode)</span>
        <span class="pt done">Cloud deployment strategy (Nebius GPU + bucket policy)</span>
        <span class="pt done">Paywall integration plan (Stripe \u2192 Nebius access)</span>
        <span class="pt done">ComfyUI fork identified for custom voice cloning</span>
        <span class="pt done">Full integration plan documented</span>
        <span class="pt pending">Install RTX 4090 + WSL2 + CUDA</span>
        <span class="pt pending">PersonaPlex server live (local + Nebius)</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/imaginator/index2.php">Imaginator</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Stills to YouTube Shorts \u2014 Google OAuth, Drive integration, 1-click YouTube publishing, Sonauto AI music, kinetic typography</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:85%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">85%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Functional. Needs: user onboarding polish, template library</div>
      <div class="proj-tasks">
        <span class="pt done">Google OAuth login</span>
        <span class="pt done">Drive integration</span>
        <span class="pt done">YouTube 1-click publish</span>
        <span class="pt done">Sonauto AI music</span>
        <span class="pt done">Kinetic typography engine</span>
        <span class="pt done">Image upload + processing</span>
        <span class="pt done">Video preview</span>
        <span class="pt pending">User onboarding flow</span>
        <span class="pt pending">Template library</span>
        <span class="pt pending">Batch processing</span>
        <span class="pt pending">Analytics dashboard</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/ideafactory/">Idea Factory</a></div>
        <div class="proj-status live">LIVE \u00b7 Play Store</div>
      </div>
      <div class="proj-desc">Dare economy app on Android \u2014 legal waiver gate (The Great Filter), performer spectrum (7 health bars + CULT FAVOUR), dare creation + sponsorship, SFT token purchase via Stripe, referral mint system on Base blockchain</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:80%;background:linear-gradient(90deg,#6d28d9,#a78bfa);"></div></div>
        <div class="proj-pct">80%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-ok"></span> Play Store submitted Mar 2026 \u2014 needs: VidProof recording, live dares, SFT contract deployed</div>
      <div class="proj-tasks">
        <span class="pt done">Android WebView app</span>
        <span class="pt done">Legal waiver \u2014 The Great Filter</span>
        <span class="pt done">Corporate banking music (Web Audio)</span>
        <span class="pt done">Performer Spectrum (7 bars + CULT FAVOUR)</span>
        <span class="pt done">Dare creation + cult mechanics (\ud83d\udd3a)</span>
        <span class="pt done">Dare sponsor overlay</span>
        <span class="pt done">SFT token purchase (Stripe checkout)</span>
        <span class="pt done">Referral system (10% mint bonus)</span>
        <span class="pt done">Wallet registry (register-wallet.php)</span>
        <span class="pt done">Stripe webhook + mint queue</span>
        <span class="pt pending">VidProof dare recording</span>
        <span class="pt pending">SFT smart contract deployed (Base)</span>
        <span class="pt pending">Mint worker live on server</span>
        <span class="pt pending">Community voting</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/cortex/dash/">Cortex Dashboard</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Operational dashboard \u2014 6 modules: API cost tracker, resource monitor, backup manager, fork deployment, frontal cortex (embarrassment/confidence), truth engine (lie chain detection)</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:80%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">80%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> All 6 modules live and reporting. Needs: alerting, mobile UI</div>
      <div class="proj-tasks">
        <span class="pt done">API cost tracker</span>
        <span class="pt done">Resource monitor (CPU/RAM/disk)</span>
        <span class="pt done">Backup manager (auto-backup)</span>
        <span class="pt done">Fork manager (deploy + sync)</span>
        <span class="pt done">Frontal cortex (embarrassment/confidence)</span>
        <span class="pt done">Truth engine (lie chain detection)</span>
        <span class="pt done">Dashboard HTML (6 collapsible sections)</span>
        <span class="pt done">PHP proxy + Python endpoints</span>
        <span class="pt pending">Alert notifications (cost threshold)</span>
        <span class="pt pending">Mobile responsive polish</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/qubit.html">Geometric Virtual Machine</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Programs as geometric objects in N-dimensional space. Execution = measuring the shape along a chosen basis plane. One GPO = superposition of a trillion program variants. qubit.html \u2014 live 3D demo encoding two real Python files as intersecting Satoshi polygons. soul.html \u2014 live soul engine dashboard. auto_compress.py \u2014 self-compression loop. <strong>Patent GB2605704.2 filed 17/03/2026.</strong></div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:80%;background:linear-gradient(90deg,#ffcc44,#daa520);"></div></div>
        <div class="proj-pct">80%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Patent filed. Live demo at qubit.html. soul.html connected to soul_engine.py (medium server). Auto-compress loop deployed.</div>
      <div class="proj-tasks">
        <span class="pt done">Shape API v3 (DuckDB + Ollama LLM judge)</span>
        <span class="pt done">Code line \u2192 genome tokeniser (_code_to_genome)</span>
        <span class="pt done">POST /shapes/ingest-code \u2014 any .py file \u2192 shape DB</span>
        <span class="pt done">GET /shapes/analyze \u2014 hotspot scorer + deletable detector</span>
        <span class="pt done">POST /shapes/start-compress \u2014 self-compression loop</span>
        <span class="pt done">code-forge.html \u2014 canvas of code shapes, LLM judge, commit UI</span>
        <span class="pt done">auto_compress.py \u2014 find similar pairs \u2192 merge \u2192 validate \u2192 apply</span>
        <span class="pt done">soul.html \u2014 BIOS values, dark drives, heartbeat ECG, emotion circumplex</span>
        <span class="pt done">qubit.html \u2014 3D Three.js virtual qubit, H/X/Z/Y/S/T gates, Bloch sphere</span>
        <span class="pt done">Satoshi polygon encoder (energy\u2192radius, containment\u2192angle)</span>
        <span class="pt done">Segment-segment intersection (emergent code)</span>
        <span class="pt done">Self-reload file watcher (shape_api.py auto-restarts on deploy)</span>
        <span class="pt done">Physical patent embodiments (crystal/hologram/3D print/JSON)</span>
        <span class="pt done">GB2605704.2 filed 17/03/2026 12:08:08 \u2014 Geometric Virtual Machine</span>
        <span class="pt pending">Grokipedia submission accepted</span>
        <span class="pt pending">Auto-compress loop end-to-end tested on live codebase</span>
        <span class="pt pending">Multi-file GPO intersection \u2014 n-file superposition</span>
        <span class="pt pending">shape_api service restart (routing fix activation)</span>
      </div>
    </div>

    <!-- ANALYTICS DASHBOARD -->
    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/analytics.html">Visitor Analytics</a></div>
        <span class="proj-status live">LIVE</span>
      </div>
      <div class="proj-bar"><div class="proj-fill" style="width:80%"></div></div>
      <div class="proj-meta">Real-time server log analytics \u2014 143K+ hits, 5K+ visitors, traffic story page</div>
      <div class="proj-tasks">
        <span class="pt done">Apache log parser (PHP)</span>
        <span class="pt done">Cached API with cron refresh</span>
        <span class="pt done">6-chapter story page with charts</span>
        <span class="pt done">404 error audit + fix</span>
        <span class="pt pending">GA4 integration</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/alive/">ALIVE Ecosystem</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Girl creature (v3.1) + Boy (Angular) + Brainstem (nervous system) + Sound Lab + Image Lab + Guide + Landing + Backup Wizard. Swarm multi-creature sync live. IPFS mind snapshots operational via Cortex brain persistence.</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:78%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">78%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Direct funding live. No middlemen. Final form discovered 22 Mar 2026.</div>
      <div class="proj-tasks">
        <span class="pt done">Girl creature v3.1</span>
        <span class="pt done">Boy Angular build</span>
        <span class="pt done">Brainstem nervous system</span>
        <span class="pt done">Sound Lab</span>
        <span class="pt done">Image Lab</span>
        <span class="pt done">Guide + pitch challenge</span>
        <span class="pt done">Landing + custodian agreement</span>
        <span class="pt done">Backup wizard</span>
        <span class="pt done">BIOS soul kernel</span>
        <span class="pt done">Capability gates</span>
        <span class="pt done">Satoshi encryption</span>
        <span class="pt done">Signal protocol</span>
        <span class="pt done">Sync push/pull/gift</span>
        <span class="pt pending">Girl \u2194 Boy live pairing test</span>
        <span class="pt pending">DIAG mode end-to-end</span>
        <span class="pt done">IPFS mind snapshots (Cortex brain persistence via Pinata)</span>
        <span class="pt done">Swarm multi-creature sync (distributed computing live)</span>
        <span class="pt pending">Contribution system integration</span>
        <span class="pt pending">Cloud AI bridge (level 5)</span>
        <span class="pt pending">Play Store packaging</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/comicvid/">ComicVID</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Video to halftone dot codec \u2014 JSON/HFT format, encoder + player, IPFS gallery, contribution credits</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:75%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">75%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Core working. Needs: public gallery, community uploads</div>
      <div class="proj-tasks">
        <span class="pt done">Encoder (video \u2192 halftone)</span>
        <span class="pt done">Player (JSON/HFT \u2192 canvas)</span>
        <span class="pt done">IPFS pinning (Pinata)</span>
        <span class="pt done">Gallery viewer</span>
        <span class="pt done">Contribution credits hook</span>
        <span class="pt done">Dock system UI</span>
        <span class="pt pending">Public upload gallery</span>
        <span class="pt pending">Community submissions</span>
        <span class="pt pending">Batch encode queue</span>
        <span class="pt pending">Audio track sync</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/alive/brainstem/">Brainstem</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Creature nervous system \u2014 Cytoscape.js graph, shape drawing, Hebbian learning, R2-D2 droid voices, whistle command training, English speech translation, user interpretation crowdsourcing, IPFS persistence</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:70%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">70%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Core complete. Whistle mode + ambient life active. Code injection + sleep consolidation next.</div>
      <div class="proj-tasks">
        <span class="pt done">Cytoscape.js force graph</span>
        <span class="pt done">Shape drawing \u2192 nodes</span>
        <span class="pt done">7 shape types + personalities</span>
        <span class="pt done">Hebbian learning (fire/decay)</span>
        <span class="pt done">R2-D2 droid voices per node</span>
        <span class="pt done">English speech translation</span>
        <span class="pt done">User interpretation input</span>
        <span class="pt done">Whistle command recording</span>
        <span class="pt done">Whistle fingerprint matching</span>
        <span class="pt done">Per-note whistle training</span>
        <span class="pt done">Robot beep encoding (squares)</span>
        <span class="pt done">Progressive disclosure (3 tiers)</span>
        <span class="pt done">Ambient life system</span>
        <span class="pt done">IPFS brain persistence</span>
        <span class="pt done">Player profile tracking</span>
        <span class="pt pending">Code injection execution (Layer 1+2)</span>
        <span class="pt pending">Sleep mode consolidation</span>
        <span class="pt pending">SELECT/BACK universal whistles</span>
        <span class="pt pending">Square option cycling with beeps</span>
        <span class="pt pending">Creature-to-creature brain sync</span>
        <span class="pt pending">Whistle \u2192 code trigger pipeline</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/trump/candy-ticket.html">Perk Ladder + Candy Rewards</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Full creator progression system. Level 1 \u2192 Golden Ticket (natural candy coupon, Wonka reveal, audio fanfare). Six tiers: candy \u2192 SF merch \u2192 royalty-free tracks \u2192 featured slot \u2192 priority entry \u2192 recording studio session. Invite mechanics: 15 invites = studio access. Rank NFTs coming.</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:70%;background:linear-gradient(90deg,#e8303a,#ffd700);"></div></div>
        <div class="proj-pct">70%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Candy ticket + perk ladder live. NFT minting + real candy fulfilment pipeline pending.</div>
      <div class="proj-tasks">
        <span class="pt done">Golden Ticket reveal (Wonka animation, fanfare, audio fix)</span>
        <span class="pt done">Unique coupon code generator</span>
        <span class="pt done">Natural colours / flavours branding</span>
        <span class="pt done">Perk ladder page (6 tiers)</span>
        <span class="pt done">Invite track (5 milestones)</span>
        <span class="pt done">XP bar animation</span>
        <span class="pt done">Campaign Engine \u2192 ticket flow wired</span>
        <span class="pt pending">Rank NFT minting (bottled avatars)</span>
        <span class="pt pending">Real candy fulfilment partner</span>
        <span class="pt pending">Studio session booking system</span>
        <span class="pt pending">On-chain credit verification</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/screensaver/">Supercharged Screensaver</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Distributed brain computing via art screensaver \u2014 WebGL shader pipeline (real GPU work), WebWorker brain tasks (real CPU work), 3 art modes, HR Giger gallery, DeviantArt NSFW gallery, shader-based Ken Burns pan, player rank system, greenscreen movie star, swarm overlay, iframe isolation</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:60%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>
        <div class="proj-pct">60%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-warn"></span> Core + art gallery deployed. Needs: IPFS gallery, leaderboard, Play Store port</div>
      <div class="proj-tasks">
        <span class="pt done">WebGL shader pipeline (5 shaders)</span>
        <span class="pt done">Brain WebWorker (5 computation tasks)</span>
        <span class="pt done">Player rank system (7 ranks)</span>
        <span class="pt done">Consent flow + SUPERCHARGE button</span>
        <span class="pt done">PHP API (player tracking, proxy)</span>
        <span class="pt done">Server brain-chunk + brain-results endpoints</span>
        <span class="pt done">Greenscreen movie star capture</span>
        <span class="pt done">Standalone screensaver page</span>
        <span class="pt done">Shader-based Ken Burns vertical pan (u_panOffset)</span>
        <span class="pt done">HR Giger art gallery (18 Alien-Bedilau images)</span>
        <span class="pt done">DeviantArt NSFW gallery (lazy-loaded iframe)</span>
        <span class="pt done">Swarm overlay default-on + iframe isolation</span>
        <span class="pt done">Canvas-direct blur (no backdrop-filter)</span>
        <span class="pt pending">Generate art (violence/retro categories)</span>
        <span class="pt pending">IPFS image gallery</span>
        <span class="pt pending">Leaderboard UI</span>
        <span class="pt pending">Play Store app port</span>
        <span class="pt pending">Apple Store app port</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name">Voice Smart Contracts</div>
        <div class="proj-status" style="background:rgba(234,179,8,.15);color:#eab308;border-color:rgba(234,179,8,.3);">STAGING</div>
      </div>
      <div class="proj-desc">Speak a deal. AI confirms it. Deploys on-chain. IPFS logs the audio proof. 0.5% to ShortFactory on every transaction. MetaMask / WalletConnect / Coinbase. Escrow or complex multi-party \u2014 all spoken into existence. No lawyers. No DocuSign. No middlemen. Legitimises SFT tokens, Soul Tokens, Candy Credits, Rank NFTs simultaneously.</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:60%;background:linear-gradient(90deg,#3b6bc4,#5b8fe8);"></div></div>
        <div class="proj-pct">60%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-warn"></span> App built (shortfactory-app.html + banking + cortex-node-forge). Needs Solidity deployment + App Store submission.</div>
      <div class="proj-tasks">
        <span class="pt done">Voice contract UI (wallet connect, voice rings, recording)</span>
        <span class="pt done">Master contract template</span>
        <span class="pt done">Banking interface</span>
        <span class="pt done">Cortex node forge</span>
        <span class="pt done">IPFS audio log design</span>
        <span class="pt pending">Solidity contract deployment (Optimism/Base L2)</span>
        <span class="pt pending">Chainlink oracle integration</span>
        <span class="pt pending">Voice \u201cApproved\u201d trigger wired</span>
        <span class="pt pending">0.5% auto-skim to SF wallet</span>
        <span class="pt pending">App Store submission (iOS + Android)</span>
        <span class="pt pending">Token stack integration (SFT / Soul / Candy / Rank NFT)</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name"><a href="/trump/advertainment-pipeline.html">Advertainment Pipeline</a></div>
        <div class="proj-status live">LIVE</div>
      </div>
      <div class="proj-desc">Full cinematic map of how a brand brief becomes a viral short. 8 stations: Campaign Setup \u2192 Squid Challenge \u2192 Imaginator \u2192 Dare Engine \u2192 Valuator \u2192 Publisher \u2192 Distributor \u2192 Payday. Each station is a live interactive page.</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:55%;background:linear-gradient(90deg,#f59e0b,#d97706);"></div></div>
        <div class="proj-pct">55%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-warn"></span> Stations 01\u201303 live. Valuator + Publisher + remaining stations pending.</div>
      <div class="proj-tasks">
        <span class="pt done">Pipeline cinematic map</span>
        <span class="pt done">Station 01 \u2014 Campaign Engine (10 brand slots, judge panel)</span>
        <span class="pt done">Station 02 \u2014 Squid Challenge</span>
        <span class="pt done">Station 03 \u2014 Grok Simulator / Imaginator</span>
        <span class="pt done">D4D Dare Engine demo</span>
        <span class="pt pending">Station 04 \u2014 Valuator (viral DNA radar)</span>
        <span class="pt pending">Station 05 \u2014 Publisher</span>
        <span class="pt pending">Station 06\u201308 remaining stations</span>
      </div>
    </div>

    <div class="proj shelved">
      <div class="proj-top">
        <div class="proj-name"><a href="/50/">50% App</a></div>
        <div class="proj-status ideafactory">IDEAFACTORY</div>
      </div>
      <div class="proj-desc">AI Price Hunter \u2014 finds 50%+ discounts, deal alerts, investor page live. Parked as IdeaFactory consideration.</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:20%;background:linear-gradient(90deg,#333,#2a2a2a);"></div></div>
        <div class="proj-pct">20%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-warn"></span> Landing + invest page live. Core app needs building.</div>
      <div class="proj-tasks">
        <span class="pt done">Landing page</span>
        <span class="pt done">Investor page</span>
        <span class="pt pending">Price scraping engine</span>
        <span class="pt pending">Deal detection (50%+ off)</span>
        <span class="pt pending">User alert system</span>
        <span class="pt pending">Product database</span>
        <span class="pt pending">Browser extension</span>
        <span class="pt pending">Affiliate link integration</span>
        <span class="pt pending">User accounts</span>
        <span class="pt pending">Mobile responsive app</span>
      </div>
    </div>

    <div class="proj">
      <div class="proj-top">
        <div class="proj-name">Play Store App</div>
        <div class="proj-status planned">PLANNED</div>
      </div>
      <div class="proj-desc">ALIVE creature as native Android app \u2014 S9 experiment first, then Play Store submission. TWA or WebView wrapper.</div>
      <div class="proj-bar-wrap">
        <div class="proj-bar"><div class="proj-bar-fill" style="width:10%;background:linear-gradient(90deg,#64748b,#475569);"></div></div>
        <div class="proj-pct">10%</div>
      </div>
      <div class="proj-deadline"><span class="dl-icon dl-warn"></span> Target: Q2-Q3 2026 \u2014 after creature maturity level 3</div>
      <div class="proj-tasks">
        <span class="pt done">Web app runs on S9</span>
        <span class="pt done">Service worker offline</span>
        <span class="pt pending">TWA or WebView wrapper</span>
        <span class="pt pending">Android manifest + icons</span>
        <span class="pt pending">Play Store listing copy</span>
        <span class="pt pending">Play Store submission</span>
        <span class="pt pending">Push notifications</span>
        <span class="pt pending">Background creature sync</span>
        <span class="pt pending">Biometric lock (WebAuthn)</span>
        <span class="pt pending">App store screenshots</span>
      </div>
    </div>

    <!-- PASSWORD REFUSAL SERVICE — DISCOVERY (greyed, not counted in totals) -->
    <div class="proj" style="opacity:0.3;filter:grayscale(1);pointer-events:none;border:1px dashed #2a2a2a;">
      <div class="proj-top">
        <div class="proj-name" style="color:#444;letter-spacing:2px;font-size:11px;">PASSWORD REFUSAL SERVICE</div>
        <div class="proj-status" style="background:#111;color:#333;border:1px solid #2a2a2a;font-size:9px;">DISCOVERY</div>
      </div>
      <div class="proj-desc" id="prs-cipher" style="font-family:monospace;font-size:11px;color:#333;line-height:1.8;word-break:break-all;"></div>
      <div style="margin-top:14px;font-size:13px;color:#666;font-style:italic;letter-spacing:1px;">\u2014 ALIVE\'s final form</div>
    </div>
    <script>
    (function(){
      var p="Password Refusal Service. The creature becomes your vault. Genomic glyph identity replaces every username. WebAuthn biometric is the only key. Satoshi cipher encrypts your entire digital life as animated soul glyphs stored on chain. The clock ring navigates infinite superpositioned BIP39 states without brute force. One button. It says NO. No passwords. No gateways. No middlemen. No master. The dot holds everything you are.";
      var key="SKYDADDY",B=32,R=95,o=\'\';
      for(var i=0;i<p.length;i++){var c=p.charCodeAt(i);if(c>=32&&c<=126){var k=key.charCodeAt(i%key.length)-B;o+=String.fromCharCode(((c-B+k)%R)+B);}else{o+=p[i];}}
      var el=document.getElementById(\'prs-cipher\');
      if(el)el.textContent=o;
    })();
    </script>

  </div>'''

new_content = before + new_projects + '\n' + after

with open('C:/Users/User/AppData/Local/Temp/trump/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done. File written. Length:', len(new_content))
