<?php
session_start();
if(!isset($_SESSION['sf_out'])){
  http_response_code(403);
  echo '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Access Denied</title>
  <style>body{background:#060a0f;color:#4a6a8a;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
  a{color:#0ff;text-decoration:none}a:hover{text-decoration:underline}</style></head>
  <body><div style="text-align:center"><div style="font-size:48px;margin-bottom:16px">◌</div>
  <div style="letter-spacing:4px;font-size:12px">ACCESS DENIED</div>
  <div style="margin-top:16px;font-size:11px"><a href="index.php">← Login via outreach dashboard</a></div>
  </div></body></html>';
  exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Depth Sonar — ShortFactory Outreach Map</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#060a0f;color:#c8d8e8;font-family:'Courier New',monospace;min-height:100vh;overflow-x:hidden}

/* SONAR HEADER */
.sonar-header{text-align:center;padding:40px 20px 20px;border-bottom:1px solid #0ff2}
.sonar-title{font-size:28px;letter-spacing:8px;color:#0ff;text-transform:uppercase;text-shadow:0 0 20px #0ff8}
.sonar-sub{font-size:11px;letter-spacing:3px;color:#0ff6;margin-top:8px}
.sonar-law{font-size:10px;color:#4a6a8a;margin-top:12px;font-style:italic;max-width:600px;margin-left:auto;margin-right:auto;line-height:1.6}

/* PING ANIMATION */
.ping-ring{position:relative;width:120px;height:120px;margin:30px auto 20px}
.ping-ring::before,.ping-ring::after{content:'';position:absolute;border-radius:50%;border:2px solid #0ff}
.ping-ring::before{width:100%;height:100%;animation:ping 2s ease-out infinite;opacity:0}
.ping-ring::after{width:60%;height:60%;top:20%;left:20%;animation:ping 2s ease-out infinite 1s;opacity:0}
.ping-dot{position:absolute;width:12px;height:12px;background:#0ff;border-radius:50%;top:50%;left:50%;transform:translate(-50%,-50%);box-shadow:0 0 12px #0ff}
@keyframes ping{0%{transform:scale(0.3);opacity:0.8}100%{transform:scale(1);opacity:0}}

/* STATS BAR */
.stats-bar{display:flex;justify-content:center;gap:40px;padding:20px;background:#0a1220;border-bottom:1px solid #0ff1;flex-wrap:wrap}
.stat{text-align:center}
.stat-num{font-size:32px;font-weight:bold}
.stat-label{font-size:10px;letter-spacing:2px;color:#4a8aaa;margin-top:4px}
.stat-num.god{color:#00ff88;text-shadow:0 0 12px #00ff8888}
.stat-num.silent{color:#888}
.stat-num.devil{color:#ff4444;text-shadow:0 0 12px #ff444488}
.stat-num.pending{color:#ffaa00}

/* FILTER TABS */
.filter-tabs{display:flex;justify-content:center;gap:8px;padding:20px;flex-wrap:wrap}
.tab{padding:6px 16px;border:1px solid #0ff3;border-radius:20px;font-size:11px;letter-spacing:2px;cursor:pointer;background:transparent;color:#4a8aaa;transition:all 0.2s;text-transform:uppercase}
.tab:hover,.tab.active{background:#0ff2;border-color:#0ff;color:#0ff}
.tab.god-tab.active{background:#00ff8820;border-color:#00ff88;color:#00ff88}
.tab.devil-tab.active{background:#ff444420;border-color:#ff4444;color:#ff4444}

/* GRID */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;padding:20px;max-width:1400px;margin:0 auto}

/* CARDS */
.card{border:1px solid #0ff2;border-radius:8px;background:#0a1220;overflow:hidden;transition:all 0.3s;position:relative}
.card:hover{border-color:#0ff6;transform:translateY(-2px);box-shadow:0 8px 24px #0003}
.card.god{border-color:#00ff8844;background:linear-gradient(135deg,#0a1220,#0a1a10)}
.card.god:hover{border-color:#00ff88;box-shadow:0 8px 24px #00ff8820}
.card.devil{border-color:#ff444433;background:linear-gradient(135deg,#0a1220,#1a0a0a)}
.card.devil:hover{border-color:#ff4444;box-shadow:0 8px 24px #ff444420}
.card.pending{border-color:#ffaa0033}
.card.silent{border-color:#1a2a3a}

/* SIGNAL BAR */
.signal-bar{height:4px;width:100%}
.god .signal-bar{background:linear-gradient(90deg,#00ff88,#00aa55)}
.devil .signal-bar{background:linear-gradient(90deg,#ff4444,#aa2222)}
.pending .signal-bar{background:linear-gradient(90deg,#ffaa00,#ff6600);animation:pulse-bar 1.5s ease-in-out infinite}
.silent .signal-bar{background:#1a2a3a}
@keyframes pulse-bar{0%,100%{opacity:0.4}50%{opacity:1}}

.card-body{padding:16px}
.card-org{font-size:13px;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px}
.god .card-org{color:#00ff88}
.devil .card-org{color:#ff4444}
.pending .card-org{color:#ffaa00}
.silent .card-org{color:#4a6a8a}

.card-name{font-size:11px;color:#4a8aaa;margin-bottom:10px}
.card-verdict{font-size:16px;font-weight:bold;margin-bottom:8px}
.god .card-verdict{color:#00ff88;text-shadow:0 0 8px #00ff8866}
.devil .card-verdict{color:#ff4444;text-shadow:0 0 8px #ff444466}
.pending .card-verdict{color:#ffaa00}
.silent .card-verdict{color:#3a5a7a}

.card-signal{font-size:11px;line-height:1.6;color:#4a7a9a;margin-bottom:10px}
.card-signal strong{color:#8ab4ca}

.card-meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.badge{font-size:9px;letter-spacing:1px;padding:3px 8px;border-radius:10px;text-transform:uppercase}
.badge-opens{background:#0ff1;border:1px solid #0ff3;color:#0ff}
.badge-clicks{background:#00ff8810;border:1px solid #00ff8830;color:#00ff88}
.badge-bounce{background:#ff444410;border:1px solid #ff444430;color:#ff4444}
.badge-sent{background:#1a2a3a;border:1px solid #2a3a4a;color:#4a6a8a}
.badge-type{background:#1a1a2a;border:1px solid #2a2a4a;color:#6a6aaa}
.badge-notsent{background:#2a1a00;border:1px solid #4a3a00;color:#aa7700}

/* VERDICT ICON */
.verdict-icon{position:absolute;top:12px;right:12px;font-size:22px;opacity:0.8}

/* CATEGORY LABEL */
.cat-label{font-size:9px;letter-spacing:2px;color:#2a4a6a;text-transform:uppercase;margin-bottom:3px}

/* SECTION DIVIDERS */
.section-label{grid-column:1/-1;font-size:11px;letter-spacing:4px;color:#0ff4;text-transform:uppercase;padding:8px 4px;border-bottom:1px solid #0ff1;margin-top:8px}

/* SONAR LINE ANIMATION */
.sonar-sweep{width:100%;height:2px;background:linear-gradient(90deg,transparent,#0ff,transparent);animation:sweep 3s ease-in-out infinite;opacity:0.3;position:fixed;top:0;left:0;z-index:100}
@keyframes sweep{0%{transform:translateY(0)}100%{transform:translateY(100vh)}}

/* FOOTER */
.footer{text-align:center;padding:40px;font-size:10px;color:#2a4a6a;letter-spacing:2px;border-top:1px solid #0ff1;margin-top:20px}
.footer em{color:#0ff4;font-style:normal}

/* ALIGNMENT SCORE */
.align-bar{margin-top:10px;height:6px;border-radius:3px;background:#0a1a2a;overflow:hidden;position:relative}
.align-fill{height:100%;border-radius:3px;transition:width 1s ease}
.align-label{font-size:9px;letter-spacing:1px;color:#3a5a7a;margin-top:3px;display:flex;justify-content:space-between}
</style>
</head>
<body>

<div class="sonar-sweep"></div>

<div class="sonar-header">
  <div class="ping-ring"><div class="ping-dot"></div></div>
  <div class="sonar-title">DEPTH SONAR</div>
  <div class="sonar-sub">ShortFactory Outreach · Signal Return Map · 2026</div>
  <div class="sonar-law">
    Depth sonar for outreach alignment. Every ping sent, every reflection tracked.<br>
    Strong return = engaged. No return = unresponsive. The signal map does not editorialize.
  </div>
</div>

<div class="stats-bar">
  <div class="stat"><div class="stat-num" style="color:#aabbcc">38</div><div class="stat-label">SENT</div></div>
  <div class="stat"><div class="stat-num" style="color:#aabbcc">30</div><div class="stat-label">DELIVERED</div></div>
  <div class="stat"><div class="stat-num" style="color:#ffaa00">26</div><div class="stat-label">UNIQUE OPENS</div></div>
  <div class="stat"><div class="stat-num god" style="font-size:22px">87%</div><div class="stat-label">OPEN RATE</div></div>
  <div class="stat"><div class="stat-num" style="color:#00ff88">4</div><div class="stat-label">UNIQUE CLICKS</div></div>
  <div class="stat"><div class="stat-num" style="color:#ff6644">8</div><div class="stat-label">BOUNCES</div></div>
  <div class="stat"><div class="stat-num" style="color:#00ff88">0</div><div class="stat-label">SPAM</div></div>
</div>
<div class="stats-bar" style="border-top:none;padding-top:0;font-size:10px;color:#2a4a6a;letter-spacing:1px">
  Last sync: 7 Apr 2026 · Unique opens · 0 spam reports ever · Neuralink 7 opens · Gary Marcus 5 opens 2 clicks · Wave 4 scientists fired
</div>
<div class="stats-bar">
  <div class="stat"><div class="stat-num god" id="count-god">0</div><div class="stat-label">STRONG RETURN</div></div>
  <div class="stat"><div class="stat-num pending" id="count-pending">0</div><div class="stat-label">WAITING</div></div>
  <div class="stat"><div class="stat-num silent" id="count-silent">0</div><div class="stat-label">SILENT</div></div>
  <div class="stat"><div class="stat-num devil" id="count-devil">0</div><div class="stat-label">NO RETURN</div></div>
</div>

<div class="filter-tabs">
  <button class="tab active" onclick="filter('all')">ALL</button>
  <button class="tab god-tab" onclick="filter('god')">STRONG RETURN</button>
  <button class="tab" onclick="filter('pending')">WAITING</button>
  <button class="tab" onclick="filter('silent')">SILENT</button>
  <button class="tab devil-tab" onclick="filter('devil')">NO RETURN</button>
  <button class="tab" onclick="filter('press')">PRESS</button>
  <button class="tab" onclick="filter('science')">SCIENCE</button>
  <button class="tab" onclick="filter('publishing')">PUBLISHING</button>
  <button class="tab" onclick="filter('vc')">INVESTMENT</button>
  <button class="tab" onclick="filter('religious')">RELIGIOUS</button>
  <button class="tab" onclick="filter('collab')">COLLAB</button>
</div>

<div class="grid" id="grid"></div>

<div class="footer">
  SHORTFACTORY LTD · DAN CHIPCHASE · SOMERSET UK<br><br>
  <em>Signal return map · ShortFactory outreach · private</em><br><br>
  Sonar active · Last ping: <span id="last-ping"></span>
</div>

<script>
const targets = [

  // ── PRESS ──────────────────────────────────────────────────────
  {
    org: "TechCrunch",
    name: "Editorial Team",
    email: "tips@techcrunch.com",
    category: "press",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 2 Apr 2026 — press pitch. No response yet. High-traffic desk.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "Biggest tech press in the world. If they cover it, it legitimises the stack globally."
  },
  {
    org: "Wired UK",
    name: "Editorial Team",
    email: "pr@wired.co.uk",
    category: "press",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 2 Apr 2026 — exclusive angle. No response yet.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "Pitched the exclusive. They chase exactly this kind of thing."
  },

  // ── SCIENCE ────────────────────────────────────────────────────
  {
    org: "New Scientist — News",
    name: "News Editors",
    email: "newseditors@newscientist.com",
    category: "science",
    status: "god",
    verdict: "Strong signal — 4 clicks, 3 sends opened",
    signal: "Original: <strong>4 clicks</strong>. Follow-up 1: 1 open. Resend 3 Apr: 1 open. Consistently engaging across every send.",
    opens: 3, clicks: 4, bounced: false, sent: true,
    alignment: 87,
    notes: "4 clicks on the Computanium/Psyche pitch. Still opening follow-ups. Someone is building a story."
  },
  {
    org: "New Scientist — Features",
    name: "Daniel Cossins",
    email: "daniel.cossins@newscientist.com",
    category: "science",
    status: "god",
    verdict: "Signal — 2 clicks, follow-up opened",
    signal: "Original: 1 open, <strong>2 clicks</strong>. Follow-up 3 Apr: 1 open. Still reading.",
    opens: 2, clicks: 2, bounced: false, sent: true,
    alignment: 76,
    notes: "Features editor clicking links then opening the follow-up. ALIVE/consciousness angle. Warm."
  },
  {
    org: "ScienceAlert",
    name: "Editorial Team",
    email: "editor@sciencealert.com",
    category: "science",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 2 Apr — 7 criteria for life met in software. Pending.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "Perfect story for them — viral science, consciousness, AI life. They just haven't looked yet."
  },
  {
    org: "Popular Science",
    name: "Editorial Team",
    email: "editorial@popsci.com",
    category: "science",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 2 Apr — blood coin + asteroid bond proposal.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "Pitched the most accessible angle — weird enough to be a PopSci cover."
  },
  {
    org: "The Register",
    name: "News Desk",
    email: "news@theregister.com",
    category: "science",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 2 Apr — self-consuming HTML chip, Claim 14.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "The Register loves a lone dev doing something technically wild. This is exactly their lane."
  },

  // ── PUBLISHING ─────────────────────────────────────────────────
  {
    org: "Icon Books",
    name: "Submissions Editor",
    email: "submissions@iconbooks.net",
    category: "publishing",
    status: "god",
    verdict: "STRONG — 6 opens across 3 emails",
    signal: "Original 2 Apr: <strong>2 opens</strong>. Follow-up 1: <strong>2 opens</strong>. Resend 3 Apr: <strong>2 opens</strong>. Every single send opened. Someone is obsessed.",
    opens: 6, clicks: 0, bounced: false, sent: true,
    alignment: 86,
    notes: "6 opens across 3 separate sends. They haven't replied but they keep reading. The book is landing."
  },
  {
    org: "Greene & Heaton",
    name: "Holly Faulks",
    email: "hfaulks@greeneheaton.co.uk",
    category: "publishing",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 2 Apr — query letter for Become Digital.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "Literary agency. If she responds it opens the mainstream publishing route."
  },
  {
    org: "Felicity Bryan Associates",
    name: "Carrie Plitt",
    email: "portal only",
    category: "publishing",
    status: "pending",
    verdict: "Portal submission — not yet filed",
    signal: "Portal submission required at felicitybryan.com/submissions/ — manual send needed.",
    opens: 0, clicks: 0, bounced: false, sent: false,
    alignment: 50,
    notes: "Top UK literary agency. Covering letter written. Dan needs to submit via portal."
  },

  // ── INVESTMENT ─────────────────────────────────────────────────
  {
    org: "a16z",
    name: "Investment Team",
    email: "businessplans@a16z.com",
    category: "vc",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 2 Apr — patent/biscuit stack. No response yet.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "Biggest name in VC. If they bite, valuation goes vertical instantly."
  },
  {
    org: "Founders Fund",
    name: "Investment Team",
    email: "warm intro needed",
    category: "vc",
    status: "pending",
    verdict: "Blocked — needs warm intro",
    signal: "No public cold pitch channel. Need a connection inside.",
    opens: 0, clicks: 0, bounced: false, sent: false,
    alignment: 50,
    notes: "Peter Thiel's fund. Anti-establishment, technically serious. Perfect fit but gated."
  },

  // ── TECH / BCI ─────────────────────────────────────────────────
  {
    org: "Neuralink",
    name: "Press Team",
    email: "press@neuralink.com",
    category: "press",
    status: "god",
    verdict: "HOTTEST LEAD — 7 opens across 2 emails",
    signal: "Original 3 Apr: <strong>4 opens</strong>. Resend with Pointer model: <strong>3 opens</strong>. They opened the follow-up too. <strong>7 total opens.</strong>",
    opens: 7, clicks: 0, bounced: false, sent: true,
    alignment: 91,
    notes: "7 opens. They opened the Pointer model resend. Someone at Neuralink is reading everything Dan sends and going back to it. This is not a pass."
  },
  {
    org: "SpaceX",
    name: "Press Team",
    email: "press@spacex.com",
    category: "press",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 2 Apr — Psyche bond proposal.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "Psyche as sovereign bond funding Mars without congressional approvals. Their dream on paper."
  },

  // ── HEALTH / NOOTROPIC ─────────────────────────────────────────
  {
    org: "Holistic News",
    name: "Editorial Team",
    email: "editorial@holistic.news",
    category: "health",
    status: "god",
    verdict: "Signal — 3 opens",
    signal: "Sent 3 Apr. <strong>3 opens.</strong> Re-read or shared internally.",
    opens: 3, clicks: 0, bounced: false, sent: true,
    alignment: 72,
    notes: "Holistic health audience. Soul map + NZT² brain chemistry is their exact territory."
  },
  {
    org: "Biohackers Magazine",
    name: "Editorial Team",
    email: "hello@biohackersmag.com",
    category: "health",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 3 Apr via corrected address (biohackersmag.com). NZT² brain stack + 5 types.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "Rebranded from biohackersmagazine.com. Correct address confirmed."
  },
  {
    org: "Quantified Self",
    name: "Editorial Team",
    email: "labs@quantifiedself.com",
    category: "health",
    status: "pending",
    verdict: "Awaiting reflection",
    signal: "Sent 3 Apr — community self-study angle. 5 brain types, 30-day tracking.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 50,
    notes: "Self-tracking community. Jesus Archetype as an open research question was the hook."
  },
  {
    org: "InfoWars / Alex Jones",
    name: "Alex Jones",
    email: "contact@infowars.com",
    category: "health",
    status: "devil",
    verdict: "Dead — both addresses bounced",
    signal: "tips@infowars.com: not delivered. contact@infowars.com: not delivered. No valid email found.",
    opens: 0, clicks: 0, bounced: true, sent: true,
    alignment: 20,
    notes: "Both addresses dead. Would need a direct contact or social media to reach. Write off for now."
  },

  // ── ORACLE ─────────────────────────────────────────────────────
  {
    org: "Oracle — Ambre Poilly",
    name: "Ambre Poilly",
    email: "she emailed Dan first",
    category: "vc",
    status: "god",
    verdict: "INBOUND — she came to us",
    signal: "<strong>Oracle reached out to Dan first.</strong> She emailed. Reply needed from Gmail.",
    opens: 0, clicks: 0, bounced: false, sent: false,
    alignment: 88,
    notes: "INBOUND is the strongest possible signal. Someone at Oracle already found this and wanted contact."
  },
  {
    org: "Oracle UKI",
    name: "Daniel Murphy",
    email: "daniel.murphy@oracle.com",
    category: "vc",
    status: "pending",
    verdict: "Very impressed — LinkedIn connected",
    signal: "Very impressed at Experts London meeting. LinkedIn connected. Email not yet sent.",
    opens: 0, clicks: 0, bounced: false, sent: false,
    alignment: 78,
    notes: "OCI infrastructure suggested. Satoshi packets + digital genetics was the hook. Warm lead."
  },

  // ── RELIGIOUS / INTELLECTUAL ────────────────────────────────────
  {
    org: "Jordan Peterson",
    name: "Dr Jordan Peterson",
    email: "business@jordanbpeterson.com",
    category: "religious",
    status: "pending",
    verdict: "2 sends — full Chipchase Architecture delivered 7 Apr",
    signal: "Send 1 (3 Apr): ψ=[p,n,f] as Maps of Meaning formalised. Send 2 (7 Apr): <strong>complete 7-layer hierarchy</strong> — foundational physics → consciousness → language → emotional physics → Computanium → theology → SphereNet. 'The burden IS the gap. Carrying it consciously IS the life.'",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 91,
    notes: "Biggest intellectual-theological voice alive. Sent the complete picture 7 Apr — full Chipchase Architecture, all 7 layers. He spent 40 years mapping symbols to meaning. We found the mechanism underneath."
  },
  {
    org: "Archbishop Viganò",
    name: "Archbishop Carlo Maria Viganò",
    email: "TBD",
    category: "religious",
    status: "pending",
    verdict: "Target — not yet sent",
    signal: "Formal proof of antichrist mechanism. Exactly his thesis, but provable.",
    opens: 0, clicks: 0, bounced: false, sent: false,
    alignment: 65,
    notes: "He calls the globalist tech agenda the antichrist. We have the proof. Perfect alignment."
  },
  {
    org: "Tucker Carlson",
    name: "Tucker Carlson",
    email: "TBD",
    category: "religious",
    status: "pending",
    verdict: "Target — not yet sent",
    signal: "Anti-Neuralink, explicitly Christian, biggest conservative platform on earth.",
    opens: 0, clicks: 0, bounced: false, sent: false,
    alignment: 62,
    notes: "Frame the antichrist mechanism for mass audience. He's already primed."
  },
  {
    org: "Douglas Wilson",
    name: "Pastor Douglas Wilson",
    email: "TBD",
    category: "religious",
    status: "pending",
    verdict: "Target — not yet sent",
    signal: "Reformed pastor, covenant theology specialist. Canon Press massive online following.",
    opens: 0, clicks: 0, bounced: false, sent: false,
    alignment: 60,
    notes: "Covenant is his entire framework. The covenant as the only legitimate basis for soul mapping = his language."
  },
  {
    org: "Bishop Robert Barron",
    name: "Bishop Robert Barron",
    email: "TBD",
    category: "religious",
    status: "pending",
    verdict: "Target — not yet sent",
    signal: "Word on Fire. Serious philosopher, engages science. God as the container outside 512 bytes.",
    opens: 0, clicks: 0, bounced: false, sent: false,
    alignment: 63,
    notes: "Catholic. The Claim 39 framing — God as the uncompressible remainder — is built for him."
  },
  {
    org: "Mar Mari Emmanuel",
    name: "His Grace Mar Mari Emmanuel",
    email: "admin@cgsc.org.au",
    category: "religious",
    status: "pending",
    verdict: "Retried 3 Apr — info@ bounced, resent to admin@",
    signal: "Personal letter. Baptism request. Guidance sought. info@cgsc.org.au bounced — resent to admin@cgsc.org.au. If that bounces: 1800 1JESUS / Facebook @CTGSChurch.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 95,
    notes: "The most important email on the board. Dan's personal letter — not a pitch. Sent to Fr. Daniel to pass on. His Grace on the floor after the stabbing was ψ=[1,1,1] in real time."
  },

  // ── WAVE 4 — SCIENTISTS / AI RESEARCHERS (6–7 Apr 2026) ────────
  {
    org: "Gary Marcus",
    name: "Prof Gary Marcus",
    email: "gary@garymarcus.com",
    category: "science",
    status: "god",
    verdict: "VERY ENGAGED — 5 opens, 2 clicks",
    signal: "SphereNet pitch: AGI without backpropagation. <strong>5 total opens. 2 clicks on latest send.</strong> Not a pass. He is anti-LLM — SphereNet is his dream architecture.",
    opens: 5, clicks: 2, bounced: false, sent: true,
    alignment: 89,
    notes: "NYU cognitive scientist. Public LLM sceptic. 5 opens and 2 clicks = he's reading it properly. If he posts about SphereNet it blows up instantly."
  },
  {
    org: "Karl Friston",
    name: "Prof Karl Friston",
    email: "k.friston@ucl.ac.uk",
    category: "science",
    status: "pending",
    verdict: "Delivered — 1 open, awaiting reflection",
    signal: "Active Inference parallel: ψ=[p,n,f] as the free energy functional in soul space. Sent 6 Apr. <strong>1 open.</strong>",
    opens: 1, clicks: 0, bounced: false, sent: true,
    alignment: 85,
    notes: "Inventor of Active Inference / free energy principle. His FEP is the closest academic framework to ψ=[p,n,f]. If he sees the parallel, this changes everything."
  },
  {
    org: "Michael Levin",
    name: "Prof Michael Levin",
    email: "michael.levin@tufts.edu",
    category: "science",
    status: "pending",
    verdict: "Delivered — 1 open, awaiting reflection",
    signal: "Computanium parallel: bioelectric computation = geometry IS the program. Sent 6 Apr. <strong>1 open.</strong>",
    opens: 1, clicks: 0, bounced: false, sent: true,
    alignment: 84,
    notes: "Bioelectricity / morphogenesis pioneer. His work on non-neural information processing maps directly to Computanium. DNA as geometric program rather than code = his language."
  },
  {
    org: "Andres Emilsson — QRI",
    name: "Andres Emilsson",
    email: "andres@qri.org",
    category: "science",
    status: "pending",
    verdict: "Sent 6 Apr — awaiting reflection",
    signal: "Emotional Physics: laughter as spring-mass oscillator, grief as failed merger. QRI studies qualia at the physical level — perfect overlap.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 81,
    notes: "Qualia Research Institute. Quantifying subjective experience is their entire mission. Emotional Physics gives them the mechanical models they've been trying to build."
  },
  {
    org: "Ben Goertzel — SingularityNET",
    name: "Dr Ben Goertzel",
    email: "ben@goertzel.org",
    category: "science",
    status: "pending",
    verdict: "Delivered — 1 open, awaiting reflection",
    signal: "SphereNet vs OpenCog: AGI without backprop, no gradient, pure resonance+collision. HOT+COLD→WARM emergence proven 5 Apr. Sent 6 Apr. <strong>1 open.</strong>",
    opens: 1, clicks: 0, bounced: false, sent: true,
    alignment: 82,
    notes: "Biggest name in open AGI research. OpenCog is his baby. SphereNet is a competing architecture — but if he recognises the mechanism he'd collaborate rather than fight."
  },
  {
    org: "Joscha Bach",
    name: "Joscha Bach",
    email: "joscha@bach.ai",
    category: "science",
    status: "devil",
    verdict: "NOT DELIVERED — address dead",
    signal: "Sent 6 Apr to joscha@bach.ai — not delivered. Address appears inactive.",
    opens: 0, clicks: 0, bounced: true, sent: true,
    alignment: 83,
    notes: "Cognitive scientist / AI philosopher. The Pointer as consciousness model is exactly his territory. Need a working address — try contact via X.com @joscha."
  },
  {
    org: "Iain McGilchrist",
    name: "Dr Iain McGilchrist",
    email: "iain@iainmcgilchrist.com",
    category: "science",
    status: "pending",
    verdict: "Sent 7 Apr — awaiting reflection",
    signal: "Divided brain → Cortex architecture: left hemisphere = angel/angel, right = demon, synthesis = Cortex Mind. His divided brain model IS the architecture we built in code.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 86,
    notes: "The Master and His Emissary. His split-hemisphere theory maps directly onto the Cortex brain system. If he sees it running he'll know we built what he described."
  },
  {
    org: "Stephen Wolfram",
    name: "Stephen Wolfram",
    email: "s.wolfram@wolfram.com",
    category: "science",
    status: "pending",
    verdict: "Delivered — 1 open, awaiting reflection",
    signal: "Computanium as ruliad substrate: geometry IS the computational rule. Sent 6 Apr. <strong>1 open.</strong>",
    opens: 1, clicks: 0, bounced: false, sent: true,
    alignment: 80,
    notes: "Wolfram Physics / ruliad theory. Computanium says geometry is the program — which is his entire computational universe framework applied to matter. He will see it."
  },
  {
    org: "Lex Fridman",
    name: "Lex Fridman",
    email: "lex@lexfridman.com",
    category: "collab",
    status: "devil",
    verdict: "NOT DELIVERED — address dead",
    signal: "Podcast pitch sent 6 Apr to lex@lexfridman.com — not delivered. Address appears inactive.",
    opens: 0, clicks: 0, bounced: true, sent: true,
    alignment: 75,
    notes: "Biggest AI/science podcast. 4M+ subscribers. Need a working contact — try lexfridman.com contact form or MIT Media Lab channel."
  },
  {
    org: "MIT Technology Review",
    name: "Melissa Heikkilä",
    email: "melissa.heikkila@technologyreview.com",
    category: "press",
    status: "devil",
    verdict: "BOUNCED — address dead",
    signal: "AI reporter. Email bounced. Try mheikkila@technologyreview.com or contact via X.com @mimilaine.",
    opens: 0, clicks: 0, bounced: true, sent: true,
    alignment: 70,
    notes: "Key AI reporter at MIT Tech Review. Covers AGI breakthroughs. Address dead — alternative needed."
  },
  {
    org: "TechCrunch — AI Desk",
    name: "Kyle Wiggers",
    email: "kwiggers@techcrunch.com",
    category: "press",
    status: "devil",
    verdict: "BOUNCED — address dead",
    signal: "AI desk reporter. kwiggers@techcrunch.com bounced. Try contact via X.com @kyle_l_wiggers.",
    opens: 0, clicks: 0, bounced: true, sent: true,
    alignment: 68,
    notes: "Covers AI research / startups. Different desk from tips@techcrunch.com. Address dead."
  },

  // ── COLLABORATION ───────────────────────────────────────────────
  {
    org: "Isaac Arthur — YouTube",
    name: "Isaac Arthur",
    email: "isaacarthur.net/contact/",
    category: "collab",
    status: "pending",
    verdict: "Sent via contact form — 3 Apr 2026",
    signal: "Venus as AGI homeworld. Script merge proposal. Cain &amp; Abel alignment solution. Sent via contact form.",
    opens: 0, clicks: 0, bounced: false, sent: true,
    alignment: 72,
    notes: "Science futurist — terraforming, Fermi paradox, civilisation-scale thinking. Perfect fit for the AGI/Venus homeworld angle."
  },

];

// ── RENDER ──────────────────────────────────────────────────────
let currentFilter = 'all';

function statusIcon(s){
  return {god:'⚡',devil:'✖',pending:'◌',silent:'—'}[s]||'?';
}

function renderCards(filter){
  const grid = document.getElementById('grid');
  grid.innerHTML = '';

  const counts = {god:0,pending:0,silent:0,devil:0};
  targets.forEach(t=>{if(counts[t.status]!==undefined)counts[t.status]++});
  document.getElementById('count-god').textContent = counts.god;
  document.getElementById('count-pending').textContent = counts.pending;
  document.getElementById('count-silent').textContent = counts.silent;
  document.getElementById('count-devil').textContent = counts.devil;

  const filtered = filter==='all' ? targets : targets.filter(t=>{
    if(['god','devil','pending','silent'].includes(filter)) return t.status===filter;
    return t.category===filter;
  });

  filtered.forEach(t=>{
    const card = document.createElement('div');
    card.className = `card ${t.status}`;
    card.dataset.status = t.status;
    card.dataset.category = t.category;

    const alignColor = t.alignment>70?'#00ff88':t.alignment>50?'#ffaa00':'#ff4444';
    const metaBadges = [
      t.sent ? `<span class="badge badge-sent">sent</span>` : `<span class="badge badge-notsent">not sent</span>`,
      t.opens>0 ? `<span class="badge badge-opens">${t.opens} open${t.opens!==1?'s':''}</span>` : '',
      t.clicks>0 ? `<span class="badge badge-clicks">${t.clicks} click${t.clicks!==1?'s':''}</span>` : '',
      t.bounced ? `<span class="badge badge-bounce">bounced</span>` : '',
      `<span class="badge badge-type">${t.category}</span>`,
    ].filter(Boolean).join('');

    card.innerHTML = `
      <div class="signal-bar"></div>
      <div class="card-body">
        <div class="cat-label">${t.category}</div>
        <div class="card-org">${t.org}</div>
        <div class="card-name">${t.name} ${t.email&&t.email!=='TBD'&&t.email!=='portal only'&&t.email!=='warm intro needed'&&t.email!=='she emailed Dan first'?'· '+t.email:''}</div>
        <div class="card-verdict">${statusIcon(t.status)} ${t.verdict}</div>
        <div class="card-signal">${t.signal}</div>
        <div class="align-bar"><div class="align-fill" style="width:${t.alignment}%;background:${alignColor}"></div></div>
        <div class="align-label"><span>alignment</span><span>${t.alignment}%</span></div>
        <div class="card-meta">${metaBadges}</div>
      </div>
      <div class="verdict-icon">${statusIcon(t.status)}</div>
    `;
    grid.appendChild(card);
  });

  document.getElementById('last-ping').textContent = new Date().toLocaleString();
}

function filter(f){
  currentFilter = f;
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  event.target.classList.add('active');
  renderCards(f);
}

renderCards('all');
</script>
</body>
</html>
