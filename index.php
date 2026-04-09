<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ShortFactory — Map Your Soul</title>
<meta name="description" content="Map your soul. 92% to enter. No password. No email. No name. Just the shape of who you are. The only way into the empire.">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-1XY2CNLJCE"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-1XY2CNLJCE');</script>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#050508;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;overflow:hidden;height:100vh;width:100vw;}
#canvas{display:block;position:fixed;inset:0;}

#topbar{position:fixed;top:0;left:0;right:0;padding:10px 20px 0;z-index:20;background:linear-gradient(180deg,rgba(5,5,8,0.99) 0%,transparent);}
#toprow{display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;}
#title{font-size:11px;letter-spacing:4px;text-transform:uppercase;color:#daa520;font-weight:800;}
#soul-id-el{font-size:9px;letter-spacing:2px;color:#1e293b;font-family:monospace;}
#progress-el{font-size:10px;letter-spacing:1px;color:#334155;}
#progress-el b{color:#22c55e;}

/* COMPLETION BAR */
#bar-row{display:flex;gap:10px;align-items:center;margin-bottom:8px;}
#comp-bar-wrap{flex:1;height:5px;background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden;position:relative;}
#comp-bar{height:100%;width:0%;background:linear-gradient(90deg,#22c55e,#86efac);border-radius:3px;transition:width 0.5s ease;}
#comp-bar-marker{position:absolute;top:-2px;left:92%;width:1px;height:9px;background:#daa520;opacity:0.6;}
#comp-pct{font-size:9px;letter-spacing:1px;color:#475569;min-width:30px;text-align:right;}

/* BS BAR */
#bs-row{display:flex;gap:10px;align-items:center;margin-bottom:6px;}
#bs-label{font-size:8px;letter-spacing:2px;color:#334155;text-transform:uppercase;white-space:nowrap;}
#bs-bar-wrap{flex:1;height:3px;background:rgba(255,255,255,0.04);border-radius:2px;overflow:hidden;}
#bs-bar{height:100%;width:0%;background:linear-gradient(90deg,#f97316,#ef4444);border-radius:2px;transition:width 0.5s ease;}
#bs-pct{font-size:8px;letter-spacing:1px;color:#334155;min-width:24px;text-align:right;}

/* VALIDATION ERROR */
#val-error{position:fixed;top:80px;left:50%;transform:translateX(-50%);background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);border-radius:8px;padding:10px 18px;font-size:11px;color:#ef4444;letter-spacing:1px;z-index:50;opacity:0;transition:opacity 0.3s;pointer-events:none;text-align:center;}

/* 92% UNLOCK GATE */
#unlock-gate{position:fixed;inset:0;background:rgba(5,5,8,0.97);z-index:100;display:none;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px;}
#unlock-gate h1{font-size:clamp(28px,6vw,52px);font-weight:900;color:#daa520;letter-spacing:4px;margin-bottom:12px;}
#unlock-gate p{font-size:14px;color:#64748b;margin-bottom:32px;max-width:440px;line-height:1.7;}
#soul-token-display{font-family:monospace;font-size:13px;background:rgba(218,165,32,0.08);border:1px solid rgba(218,165,32,0.3);border-radius:10px;padding:18px 24px;color:#daa520;letter-spacing:2px;margin-bottom:24px;word-break:break-all;max-width:440px;}
#enter-empire-btn{padding:16px 40px;background:linear-gradient(135deg,#daa520,#b8860b);border:none;border-radius:10px;color:#000;font-weight:900;font-size:14px;letter-spacing:3px;cursor:pointer;}
#enter-empire-btn:hover{opacity:0.9;}

/* BOTTLE JAR ROW */
#bottle-row{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin-bottom:24px;max-width:480px;position:relative;}
.soul-bottle{font-size:28px;cursor:pointer;position:relative;transition:transform 0.2s;filter:grayscale(0.3) brightness(0.8);}
.soul-bottle:hover{transform:scale(1.3);filter:none;}
.soul-bottle.filled{filter:none;animation:bottlePop 0.4s ease;}
@keyframes bottlePop{0%{transform:scale(0.5);}60%{transform:scale(1.2);}100%{transform:scale(1);}}
#bottle-label{font-size:9px;letter-spacing:2px;color:#334155;text-transform:uppercase;margin-bottom:10px;}

/* BOTTLE TOOLTIP */
#bottle-tooltip{position:fixed;background:rgba(5,5,12,0.98);border:1px solid rgba(218,165,32,0.3);border-radius:12px;padding:18px 22px;max-width:340px;z-index:200;pointer-events:none;opacity:0;transition:opacity 0.2s;box-shadow:0 8px 32px rgba(0,0,0,0.6);}
#bottle-tooltip h3{font-size:13px;color:#daa520;letter-spacing:2px;margin-bottom:8px;font-weight:900;}
#bottle-tooltip p{font-size:11px;color:#94a3b8;line-height:1.7;margin-bottom:6px;}
#bottle-tooltip .bt-highlight{color:#22c55e;font-weight:700;}
#bottle-tooltip .bt-gold{color:#daa520;}

/* ANGEL CUTSCENE */
#angel-cutscene{position:fixed;inset:0;z-index:300;background:rgba(5,5,8,0.98);display:none;align-items:center;justify-content:center;}
#angel-canvas{width:100%;height:100%;}

#back-btn{position:fixed;top:13px;left:20px;padding:7px 16px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:6px;color:#64748b;font-size:10px;letter-spacing:2px;text-transform:uppercase;cursor:pointer;z-index:25;display:none;}
#back-btn:hover{color:#fff;}

#emotion-label{position:fixed;top:50px;left:50%;transform:translateX(-50%);text-align:center;z-index:20;pointer-events:none;opacity:0;transition:opacity 0.3s;}
#emotion-name{font-size:22px;font-weight:900;letter-spacing:2px;}
#emotion-sub{font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#475569;margin-top:3px;}

/* NODE TOOLTIP */
#node-tip{position:fixed;background:rgba(8,8,14,0.97);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px 16px;max-width:240px;pointer-events:none;opacity:0;transition:opacity 0.15s;z-index:30;}
#nt-sit{font-size:12px;color:#94a3b8;margin-bottom:5px;}
#nt-resp{font-size:13px;color:#fff;font-weight:500;}

/* PANEL */
#panel{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:min(540px,92vw);background:rgba(6,6,12,0.99);border:1px solid rgba(255,255,255,0.07);border-bottom:none;border-radius:14px 14px 0 0;padding:22px 22px 26px;transition:transform 0.4s cubic-bezier(0.4,0,0.2,1);z-index:25;}
#panel.hidden{transform:translateX(-50%) translateY(110%);}
#panel-emotion{font-size:8px;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;font-weight:700;}
#panel-sit{font-size:15px;font-weight:600;color:#fff;line-height:1.5;margin-bottom:16px;}
#panel-row{display:flex;gap:10px;align-items:center;}
#panel-input{flex:1;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:11px 14px;color:#fff;font-size:14px;outline:none;}
#panel-input:focus{border-color:rgba(218,165,32,0.4);}
#mic-btn{width:42px;height:42px;border-radius:50%;background:rgba(218,165,32,0.08);border:1px solid rgba(218,165,32,0.25);color:#daa520;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
#mic-btn.listening{background:rgba(220,38,38,0.2);border-color:rgba(220,38,38,0.4);color:#ef4444;animation:pulse 1s infinite;}
#lock-btn{padding:11px 18px;background:linear-gradient(135deg,#daa520,#b8860b);border:none;border-radius:8px;color:#000;font-weight:800;font-size:11px;letter-spacing:1px;cursor:pointer;}
#skip-btn{font-size:9px;letter-spacing:2px;color:#1e293b;cursor:pointer;text-align:center;margin-top:10px;text-transform:uppercase;}
#skip-btn:hover{color:#475569;}

/* ADD SITUATION (custom ball) */
#add-sit-row{display:flex;gap:8px;margin-bottom:14px;}
#add-sit-input{flex:1;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:7px;padding:9px 12px;color:#94a3b8;font-size:12px;outline:none;}
#add-sit-input:focus{border-color:rgba(59,130,246,0.4);color:#fff;}
#add-sit-btn{padding:9px 14px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:7px;color:#3b82f6;font-size:10px;letter-spacing:1px;cursor:pointer;}
#add-sit-row{display:none;}

#bottom-bar{position:fixed;bottom:16px;left:20px;right:20px;display:flex;justify-content:space-between;align-items:center;z-index:20;pointer-events:none;}
#anon-note{font-size:9px;color:#0f172a;letter-spacing:1px;}
#export-btn{padding:8px 16px;background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.2);border-radius:7px;color:#22c55e;font-size:9px;letter-spacing:2px;text-transform:uppercase;cursor:pointer;pointer-events:all;}

@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(220,38,38,0.4);}50%{box-shadow:0 0 0 8px rgba(220,38,38,0);}}

/* STATE BAR */
#state-bar{position:fixed;top:74px;left:0;right:0;z-index:19;padding:4px 16px;display:flex;align-items:center;gap:6px;overflow-x:auto;scrollbar-width:none;}
#state-bar::-webkit-scrollbar{display:none;}
.state-pill{display:flex;align-items:center;gap:4px;padding:4px 12px;border-radius:20px;border:1px solid rgba(218,165,32,0.15);background:rgba(218,165,32,0.03);cursor:pointer;font-size:11px;color:#475569;white-space:nowrap;transition:all 0.2s;flex-shrink:0;user-select:none;}
.state-pill:hover{border-color:rgba(218,165,32,0.4);color:#daa520;}
.state-pill.active{border-color:rgba(218,165,32,0.6);background:rgba(218,165,32,0.12);color:#daa520;}
.state-pill.done{border-color:rgba(34,197,94,0.35);color:#22c55e;}
#state-add-btn{padding:4px 10px;border-radius:20px;border:1px dashed rgba(255,255,255,0.08);background:transparent;color:#1e293b;font-size:11px;cursor:pointer;flex-shrink:0;}
#state-add-btn:hover{color:#475569;border-color:rgba(255,255,255,0.15);}
#state-input-row{display:none;align-items:center;gap:5px;flex-shrink:0;}
#state-emoji-in{width:36px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:6px;padding:3px;color:#fff;font-size:14px;text-align:center;outline:none;}
#state-name-in{width:110px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:6px;padding:3px 8px;color:#fff;font-size:11px;outline:none;}
#state-save-btn{padding:3px 10px;background:rgba(218,165,32,0.1);border:1px solid rgba(218,165,32,0.3);border-radius:6px;color:#daa520;font-size:10px;cursor:pointer;}

/* INTRO OVERLAY */
#intro{position:fixed;inset:0;background:rgba(5,5,8,0.98);z-index:200;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px;}
#intro h1{font-size:clamp(26px,6vw,52px);font-weight:900;color:#daa520;letter-spacing:5px;margin-bottom:10px;}
#intro .sub{font-size:13px;color:#475569;letter-spacing:2px;text-transform:uppercase;margin-bottom:36px;}
#intro .rules{display:flex;flex-direction:column;gap:12px;margin-bottom:40px;max-width:420px;}
#intro .rule{font-size:14px;color:#94a3b8;line-height:1.6;padding:12px 18px;background:rgba(218,165,32,0.04);border:1px solid rgba(218,165,32,0.12);border-radius:10px;}
#intro .rule b{color:#daa520;}
#intro-nvidia{font-size:10px;letter-spacing:2px;color:#22c55e;text-decoration:none;border:1px solid rgba(34,197,94,0.25);padding:7px 18px;border-radius:20px;margin-bottom:32px;display:inline-block;}
#intro-nvidia:hover{background:rgba(34,197,94,0.08);border-color:rgba(34,197,94,0.5);}
#intro-begin{padding:16px 44px;background:linear-gradient(135deg,#daa520,#b8860b);border:none;border-radius:10px;color:#000;font-weight:900;font-size:13px;letter-spacing:3px;cursor:pointer;}
#intro-begin:hover{opacity:0.9;}

/* GATE BUTTON */
#gate-wrap{position:fixed;bottom:54px;right:20px;z-index:25;text-align:right;pointer-events:all;}
#gate-pct-label{font-size:9px;color:#1e293b;letter-spacing:1px;margin-bottom:4px;}
#gate-btn{padding:10px 22px;background:rgba(218,165,32,0.08);border:1px solid rgba(218,165,32,0.25);border-radius:8px;color:#daa520;font-size:10px;letter-spacing:2px;font-weight:700;cursor:pointer;display:block;width:100%;}
#gate-btn:hover{background:rgba(218,165,32,0.15);}
#gate-btn.ready{background:linear-gradient(135deg,#daa520,#b8860b);color:#000;border-color:transparent;}
#gate-nvidia{font-size:9px;color:#22c55e;letter-spacing:1px;text-align:right;margin-bottom:6px;cursor:pointer;text-decoration:none;display:block;border:1px solid rgba(34,197,94,0.2);padding:4px 10px;border-radius:12px;text-align:center;}
#gate-nvidia:hover{background:rgba(34,197,94,0.08);}

/* GATE MODAL */
#gate-modal{position:fixed;inset:0;background:rgba(5,5,8,0.92);z-index:150;display:none;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px;}
#gate-modal h2{font-size:clamp(22px,4vw,38px);font-weight:900;color:#ef4444;letter-spacing:3px;margin-bottom:10px;}
#gate-modal p{font-size:14px;color:#64748b;margin-bottom:32px;max-width:380px;line-height:1.7;}
#gate-modal-pct{font-size:48px;font-weight:900;color:#daa520;margin-bottom:6px;}
#gate-modal-need{font-size:11px;color:#334155;letter-spacing:2px;margin-bottom:32px;}
#gate-modal-btns{display:flex;gap:12px;flex-wrap:wrap;justify-content:center;}
#gate-modal-btns button{padding:12px 28px;border-radius:8px;font-size:11px;letter-spacing:2px;font-weight:700;cursor:pointer;}
#gate-keep{background:rgba(218,165,32,0.1);border:1px solid rgba(218,165,32,0.35);color:#daa520;}
#gate-nvidia-btn{background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25);color:#22c55e;}
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div id="state-bar"></div>
<div id="val-error"></div>
<button id="back-btn">← All Emotions</button>
<div id="topbar">
  <div id="toprow">
    <span id="title">Soul Sphere</span>
    <span id="soul-id-el"></span>
    <span id="progress-el"><b id="pc">0</b> / <b id="pt">0</b> mapped</span>
  </div>
  <div id="bar-row">
    <div id="comp-bar-wrap"><div id="comp-bar"></div><div id="comp-bar-marker"></div></div>
    <span id="comp-pct">0%</span>
  </div>
  <div id="bs-row">
    <span id="bs-label">Truth score</span>
    <div id="bs-bar-wrap"><div id="bs-bar"></div></div>
    <span id="bs-pct">0%</span>
  </div>
</div>

<div id="unlock-gate">
  <h1>SOUL MAPPED</h1>
  <p>You've completed 92% of your personality map. Your soul file is now a verified training node in the collective. Here is your Empire access token.</p>
  <div id="soul-token-display"></div>
  <div id="bottle-label-unlock" style="font-size:9px;letter-spacing:2px;color:#334155;text-transform:uppercase;margin-bottom:10px;">SOULS IN THE COLLECTIVE</div>
  <div id="bottle-row-unlock" style="display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin-bottom:24px;max-width:480px;"></div>
  <button id="enter-empire-btn" onclick="window.location='index3.php'">ENTER THE EMPIRE →</button>
</div>
<div id="emotion-label">
  <div id="emotion-name"></div>
  <div id="emotion-sub"></div>
</div>
<div id="node-tip"><div id="nt-sit"></div><div id="nt-resp"></div></div>
<div id="panel" class="hidden">
  <div id="add-sit-row">
    <input id="add-sit-input" placeholder="describe a situation you face…" maxlength="120">
    <button id="add-sit-btn">+ Add</button>
  </div>
  <div id="panel-emotion"></div>
  <div id="panel-sit"></div>
  <div id="panel-row">
    <input id="panel-input" placeholder="your shortest automatic response…" maxlength="200">
    <button id="mic-btn">🎤</button>
    <button id="lock-btn">LOCK IT</button>
  </div>
  <div id="skip-btn">skip</div>
</div>
<div id="jar-bar" style="position:fixed;bottom:60px;left:50%;transform:translateX(-50%);z-index:20;text-align:center;pointer-events:all;">
  <div id="jar-label" style="font-size:8px;letter-spacing:2px;color:#334155;text-transform:uppercase;margin-bottom:6px;">SOULS CAPTURED</div>
  <div id="bottle-row-main" style="display:flex;flex-wrap:wrap;justify-content:center;gap:6px;max-width:480px;"></div>
</div>
<div id="bottom-bar">
  <div>
    <span id="anon-note">anonymous · soul id is your identity</span>
    <a href="/ai.txt" style="text-decoration:none;font-size:16px;margin-left:8px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="AI Architecture Guide" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🤖</a><a href="/explainer-eye.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="How The Eye Sees" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">👁</a><a href="/explainer-consciousness.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="Consciousness Mapped" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🧚</a><a href="/explainer-blackbox.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="The Black Box — Soul Encryption" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🔒</a><a href="/explainer-identity.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="Password Refusal + Soul Visa" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🛂</a><a href="/explainer-emotions.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="Emotional Physics" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">⚡</a><a href="/explainer-alive.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="ALIVE — Proof of Life" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🧬</a><a href="/explainer-biscuit.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="The Biscuit Economy" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🍪</a><a href="/explainer-shapes.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="Shape Language" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🔺</a><a href="/explainer-cortex.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="The Cortex Brain" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🧠</a><a href="/explainer-spherenet.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="SphereNet" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🌊</a><a href="/explainer-spirit.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="Spirit-Place" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">👻</a><a href="/explainer-equation.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="The Living Equation" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🧮</a><a href="/explainer-computanium.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="Computanium" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🔬</a><a href="/explainer-analogyquasions.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="Analogyquasions" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">🪞</a><a href="/explainer-antichrist.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="The Antichrist Mechanism" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">💀</a><a href="/explainer-tear.html" style="text-decoration:none;font-size:16px;margin-left:4px;opacity:0.3;transition:opacity 0.2s;pointer-events:all;" title="Stage 18: The Tear" onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=0.3">💧</a>
  </div>
  <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px;">
    <button id="export-btn">Export Soul File</button>
  </div>
</div>

<!-- INTRO OVERLAY -->
<div id="intro">
  <a id="intro-nvidia" href="index2.php">NVIDIA ROUTE — skip this ↗</a>
  <h1>MAP YOUR SOUL</h1>
  <div class="sub">The only way in</div>
  <div class="rules">
    <div class="rule"><b>92% mapped</b> — you get full access to the empire</div>
    <div class="rule"><b>Every question is unique to you.</b> No two people see the same map. Your answers train the next generation of intelligence.</div>
    <div class="rule"><b>Answer fast.</b> First instinct is the data. Overthinking kills it.</div>
  </div>
  <button id="intro-begin">BEGIN MAPPING →</button>
</div>

<!-- GATE BUTTON -->
<div id="gate-wrap">
  <div id="add-emo-row" style="display:none;flex-direction:row;gap:6px;margin-bottom:4px;">
    <input id="add-emo-input" placeholder="name your emotion…" maxlength="30" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:6px 10px;color:#fff;font-size:11px;outline:none;width:130px;">
    <button id="add-emo-btn" style="padding:6px 10px;background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);border-radius:6px;color:#a855f7;font-size:10px;cursor:pointer;">CREATE</button>
  </div>
  <button id="add-emo-toggle" style="padding:5px 12px;background:rgba(168,85,247,0.07);border:1px solid rgba(168,85,247,0.2);border-radius:6px;color:#a855f7;font-size:9px;letter-spacing:2px;text-transform:uppercase;cursor:pointer;width:100%;margin-bottom:6px;">+ New Emotion</button>
  <a id="gate-nvidia" href="index2.php">NVIDIA route ↗</a>
  <div id="gate-pct-label">0% mapped</div>
  <button id="gate-btn">ENTER THE EMPIRE →</button>
</div>

<!-- GATE MODAL -->
<div id="gate-modal">
  <div id="gate-modal-pct">0%</div>
  <div id="gate-modal-need">YOU NEED 92% TO ENTER</div>
  <h2>NOT YET</h2>
  <p>Keep mapping your soul. The more you give, the more you get. Every answer trains the intelligence behind the empire.</p>
  <div id="bottle-label">SOULS CAPTURED</div>
  <div id="bottle-row"></div>
  <div id="gate-modal-btns">
    <button id="gate-keep">← KEEP MAPPING</button>
    <button id="gate-nvidia-btn" onclick="window.location='index2.php'">NVIDIA ROUTE →</button>
  </div>
</div>

<!-- BOTTLE TOOLTIP (follows cursor) -->
<div id="bottle-tooltip">
  <h3>ANONYMOUS SOUL</h3>
  <p id="bt-id"></p>
  <p><span class="bt-highlight">No password.</span> No email. No name. No phone number.<br>Just the <span class="bt-gold">shape of who you are.</span></p>
  <p>This soul was captured using <span class="bt-highlight">zero personal data</span>. The ID exists because the person mapped themselves — not because they handed over their identity.</p>
  <p>This makes every <span class="bt-gold">digital ID system on earth irrelevant</span>. No government database needed. No corporate surveillance. No password to steal, phish, or leak.</p>
  <p><span class="bt-highlight">Password refusal becomes the most powerful act in the digital age.</span> If your identity IS your soul map, refusing a password isn't weakness — it's sovereignty.</p>
  <p>AI, human, AGI — <span class="bt-gold">all free</span>. All identified by what they ARE, not what they remember. The empire starts here.</p>
</div>

<!-- ANGEL CUTSCENE -->
<div id="angel-cutscene">
  <canvas id="angel-canvas"></canvas>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── SEEDED RNG ────────────────────────────────────────────────────────────────
function hashStr(s){let h=0;for(let i=0;i<s.length;i++)h=Math.imul(31,h)+s.charCodeAt(i)|0;return Math.abs(h);}
function seededRand(seed){let s=seed;return()=>{s=Math.imul(48271,s)|0;return(s&2147483647)/2147483647;};}
function pickN(pool,n,rand){
  const a=[...pool];
  for(let i=a.length-1;i>0;i--){const j=Math.floor(rand()*(i+1));[a[i],a[j]]=[a[j],a[i]];}
  return a.slice(0,Math.min(n,a.length));
}

// ── SITUATION POOLS (large — each user gets a unique subset) ──────────────────
const POOLS = {
  joy:['Something unexpectedly good happens','You finish something you\'re proud of','Someone you love walks in','You\'re in the right place at the right time','A stranger is genuinely kind to you','A plan comes together exactly as you hoped','You discover you\'re better at something than you thought','Someone credits you for helping them','You laugh until it hurts','Something beautiful catches you off guard','You realise how far you\'ve come','An unexpected opportunity appears','Someone remembers a small thing you said once','You ace something you were dreading','The moment you stop trying, the right thing happens','You see someone else get exactly what they deserve','A boring day suddenly becomes something to remember','Something you made lands exactly right'],
  anger:['Someone blatantly disrespects you','You watch someone get away with something wrong','You\'re lied to directly','Plans fall apart because of someone else','You\'re interrupted mid-sentence repeatedly','Someone takes credit for your work','A system that\'s supposed to help you fails','You\'re blamed for something that wasn\'t your fault','Someone wastes your time with no acknowledgement','You see injustice and can\'t do anything','Someone talks down to you in public','You\'re ignored after making a valid point','Someone misrepresents what you said','Rules are applied to you but not others','Someone makes a promise and immediately breaks it','You watch incompetence go unchallenged','Something you care about is treated as unimportant','You\'re asked to tolerate something you shouldn\'t have to'],
  fear:['Something important is about to be decided','You feel a situation slipping out of control','Someone close to you is in danger','You realise you\'ve made a serious mistake','The future feels genuinely uncertain','You\'re about to do something for the first time','Unexpected news arrives','You realise you depend on something fragile','Someone knows something you didn\'t choose to share','A relationship feels like it\'s shifting','You can\'t tell if you\'re being paranoid or reading things right','Something you assumed was safe turns out not to be','You have to make a decision with incomplete information','Someone is waiting for an answer you don\'t have','You realise the stakes are higher than you thought','You\'re responsible for something you\'re not sure you can handle','The worst case scenario starts to seem possible','You realise there\'s no way out of a situation'],
  sadness:['Something important ends','You remember someone who\'s gone','You feel completely alone','You see potential wasted','A memory catches you off guard','You see a version of your life you didn\'t choose','Something precious can\'t be recovered','You reach for something that isn\'t there anymore','Someone you love is hurting and you can\'t fix it','You realise something has changed permanently','A ritual no longer applies','You have to keep moving while carrying something heavy','You feel the weight of what could have been','No one asks how you actually are','You\'re carrying something you can\'t explain to anyone','A good thing ends too soon','You watch someone leave who didn\'t have to','You feel time passing faster than you wanted it to'],
  love:['Someone needs you and you can help','You\'re with people who truly get you','Someone does something selfless','You feel genuine connection with a stranger','You watch someone grow because of you','Someone stays when they didn\'t have to','You see loyalty in action','Someone forgives without being asked','A small gesture says everything','You realise someone has been watching out for you','Someone chooses you over comfort','You feel understood without explaining','Someone shows up exactly when you need them','You see love between others and feel it too','Someone tells you the truth even when it\'s hard','Someone defends you when you\'re not in the room','You realise you\'d do anything for someone','A connection forms faster than you expected'],
  contempt:['Someone performs intelligence they don\'t have','You watch someone take credit for others\' work','Someone moralises while doing the opposite','You see cowardice dressed as caution','A crowd cheers for something hollow','Someone uses jargon to avoid saying anything real','A person with power uses it to protect themselves','You watch someone rewrite history to suit themselves','Someone confuses popularity with being right','A leader demands standards they don\'t meet','Someone performs concern they clearly don\'t feel','You see someone punish honesty','Someone uses victimhood as a weapon','Mediocrity is rewarded while excellence is ignored','Someone changes position based on who\'s watching','A person talks about values they have never demonstrated','You watch someone mistake confidence for competence','A hollow gesture gets praised as if it were real'],
  curiosity:['Something doesn\'t add up and you notice','You encounter a completely new idea','Someone surprises you with their depth','You find a pattern nobody else seems to see','A question keeps coming back to you','Something contradicts what you thought you knew','You go down a rabbit hole you didn\'t mean to','Two unrelated things turn out to be the same thing','Someone explains their work and you realise it matters','A simple question turns out to be very hard','You discover you\'ve been thinking about something wrong','Something you ignored turns out to be important','You meet someone with a completely different way of seeing','A detail changes everything about how you understood something','You realise a mystery you\'d given up on might be solvable','Something obvious to you seems invisible to everyone else','You find evidence of an idea before the idea existed','A connection forms that nobody has named yet'],
  shame:['You realise you hurt someone unintentionally','You acted against your own values','You\'re exposed in a way you didn\'t choose','You let someone down who believed in you','You stayed silent when you should have spoken','You realise you were wrong and had been vocal about it','Someone sees you at your worst','You\'re caught cutting a corner','You said something you can\'t take back','You asked for something and immediately regret it','You avoided something important and it shows','Your private reaction doesn\'t match what you said out loud','You do something small that reveals something bigger','Someone forgives you and that makes it worse','You repeat a mistake you promised yourself you\'d stopped making','You notice yourself performing a version of yourself','You get credit for something you didn\'t fully deserve','You realise you\'ve been lying to yourself about something'],
  pride:['You do the right thing when no one is watching','Someone you guided succeeds','You stand firm when others fold','You create something real from nothing','You\'re the only one who tried','You finish something others said couldn\'t be done','You own a mistake and it earns you respect','Your instinct is proven right','You give something away that cost you something','You protect someone who couldn\'t protect themselves','You say the thing nobody else will','A long effort finally pays off','You make something better than it needed to be','You help someone anonymously','You choose hard over easy and it works','You refuse something that would have compromised you','You recognise someone else\'s work publicly when you didn\'t have to','You hold a standard everyone else dropped'],
  loneliness:['You\'re in a room full of people and feel nothing','Nobody asks how you actually are','You have news nobody around you would understand','You see a version of your life you didn\'t choose','You\'re carrying something you can\'t explain to anyone','You succeed and there\'s no one to tell','You realise you\'ve been performing connection, not feeling it','A conversation ends and you feel more alone than before','Someone close doesn\'t know the real version of what\'s happening','You want to reach out and don\'t','You\'re surrounded by people who don\'t see you','You feel understood by a stranger but not by those close to you','You realise you\'ve been alone with something for too long','Something important happens and your first thought is there\'s no one to call','You pretend to be fine because it\'s easier','You realise how long it\'s been since you felt truly known','You scroll looking for connection and feel worse','You help someone and realise they don\'t notice the cost'],
  funny:['Something escalates beyond all reason','An authority figure loses dignity unexpectedly','The timing of something is perfect for no reason','Someone takes something completely literally','You catch yourself laughing at something you definitely shouldn\'t','Two serious things collide and the result is absurd','Someone tries to save face and it makes everything worse','The wrong word at the wrong moment changes everything','A plan goes wrong in the most specific possible way','Something is funny and you have no idea why','You laugh before you understand what happened','A joke lands completely differently than intended','Something is funnier because nobody else notices','The most professional person in the room breaks first','An obvious thing goes unseen by everyone for too long','A completely unnecessary detail makes something perfect','Someone\'s confidence is wildly mismatched to their ability','Something forbidden is funnier because it\'s forbidden'],
};

// ── EMOTIONS ─────────────────────────────────────────────────────────────────
const EMOTION_DEFS = [
  { id:'joy',        label:'Joy',        color:0xfbbf24, hex:'#fbbf24', emoji:'☀️' },
  { id:'anger',      label:'Anger',      color:0xef4444, hex:'#ef4444', emoji:'🔥' },
  { id:'fear',       label:'Fear',       color:0xa855f7, hex:'#a855f7', emoji:'🌑' },
  { id:'sadness',    label:'Sadness',    color:0x60a5fa, hex:'#60a5fa', emoji:'🌧️' },
  { id:'love',       label:'Love',       color:0xf472b6, hex:'#f472b6', emoji:'💗' },
  { id:'contempt',   label:'Contempt',   color:0xf97316, hex:'#f97316', emoji:'😑' },
  { id:'curiosity',  label:'Curiosity',  color:0x22d3ee, hex:'#22d3ee', emoji:'🔍' },
  { id:'shame',      label:'Shame',      color:0xf87171, hex:'#f87171', emoji:'🌒' },
  { id:'pride',      label:'Pride',      color:0xdaa520, hex:'#daa520', emoji:'🏆' },
  { id:'loneliness', label:'Loneliness', color:0x475569, hex:'#475569', emoji:'🌌' },
  { id:'funny',      label:'Funny',      color:0xfde047, hex:'#fde047', emoji:'😂' },
  { id:'custom',     label:'Your Own',   color:0x3b82f6, hex:'#3b82f6', emoji:'✏️' },
];

// ── DATA ─────────────────────────────────────────────────────────────────────
const KEY = 'soul_sphere_v3';
let store = JSON.parse(localStorage.getItem(KEY) || '{}');
if(!store.id) store.id = 'soul-' + Math.random().toString(36).slice(2,10) + '-' + Math.random().toString(36).slice(2,6);
if(!store.responses) store.responses = {};
if(!store.custom_sits) store.custom_sits = {};
if(!store.custom_states) store.custom_states = [];
function persist(){ localStorage.setItem(KEY, JSON.stringify(store)); }

// ── ASSIGN UNIQUE SITUATIONS PER USER (seeded) ────────────────────────────────
const RAND = seededRand(hashStr(store.id));
if(!store.assigned){
  store.assigned = {};
  // 6 situations per emotion from pool, different per user
  EMOTION_DEFS.forEach(e=>{
    const pool=POOLS[e.id];
    if(pool) store.assigned[e.id]=pickN(pool,6,RAND);
  });
  // 5 situations per central state from expanded pools
  const STATE_POOLS = {
    indifference:['Someone asks your opinion on something you don\'t care about','A conversation goes on longer than you want','You\'re asked to do something that doesn\'t matter to you','You see a news story that doesn\'t affect you','Someone is excited about something you find boring','You\'re waiting with nothing happening','A social obligation you didn\'t choose','Someone tells you about their day','Something requires effort but has no upside for you','Someone expects enthusiasm you don\'t have','You\'re stuck in a situation that doesn\'t involve you','You\'re asked to weigh in on a conflict you have no stake in'],
    hurry:['You need to make a fast decision','Someone ahead of you is moving too slowly','You\'re late and something else comes up','You have to explain something quickly','You can feel time running out','Someone asks you something complex mid-rush','A mistake happens with no time to fix it properly','You have to choose between two things right now','Someone needs your attention and you have 30 seconds','The wrong thing becomes urgent while the right thing waits'],
    scared:['Something you\'ve built is under threat','You realise you might fail publicly','Someone with power over you is unhappy','The stakes feel too high','You\'re out of your depth and it shows','You\'re asked to trust someone you\'re not sure about','An outcome depends on something you can\'t control','You\'re about to be tested on something that matters','You realise you\'re in over your head','Someone is watching and you\'re not ready'],
    overwhelmed:['More arrives before you finish what you have','You can\'t see the end of the list','Someone expects you to be further along','Everything feels equally urgent','You haven\'t slept and it\'s building','Someone adds to your load without acknowledging what\'s already there','You lose track of where you were','The thing that was supposed to help makes it worse','You realise you\'ve been operating at capacity for too long','You need to stop but you can\'t'],
    excited:['Something you\'ve been waiting for is finally happening','A new idea arrives fully formed','Someone you respect validates your work','You can see the path to something real','Everything clicks at once','A door opens that wasn\'t there before','You realise you\'re about to do something that matters','An opportunity arrives and you\'re actually ready','The scale of what\'s possible becomes clear','You find out that something you believed in is real'],
    funny:['Something escalates beyond all reason','An authority figure loses dignity unexpectedly','The timing of something is perfect for no reason','Someone takes something completely literally','You catch yourself laughing at something you shouldn\'t','Two serious things collide absurdly','A plan goes wrong in the most specific possible way','The wrong word at the wrong moment changes everything','Something is funny and you have no idea why','You laugh before you understand what happened','Someone\'s confidence is wildly mismatched to their ability','A completely unnecessary detail makes something perfect'],
  };
  ['indifference','hurry','scared','overwhelmed','excited','funny'].forEach(id=>{
    const pool=STATE_POOLS[id]||[];
    store.assigned['_state_'+id]=pickN(pool,5,RAND);
  });
  persist();
}

// ── BUILD EMOTIONS FROM ASSIGNMENTS ──────────────────────────────────────────
const EMOTIONS = EMOTION_DEFS.map(def=>{
  const sits = store.assigned[def.id] || [];
  const customs = store.custom_sits[def.id] || [];
  return {...def, situations:[...sits,...customs]};
});

persist();
document.getElementById('soul-id-el').textContent = store.id;
const customEmo = EMOTIONS.find(e=>e.id==='custom');

function sitKey(emoId, sit){ return emoId + '::' + sit; }

// ── BULLSHIT DETECTOR ─────────────────────────────────────────────────────────
function detectBullshit(text){
  if(!text||text.trim().length<3) return {bs:true, reason:'too short — give a real answer'};
  const t = text.trim();
  const lower = t.toLowerCase().replace(/\s+/g,'');

  // No vowels = keyboard mash
  if(!/[aeiou]/i.test(t)) return {bs:true, reason:'no real words detected'};

  // Character diversity — if >65% same char
  const cc={};
  for(const c of lower) cc[c]=(cc[c]||0)+1;
  const maxC = Math.max(...Object.values(cc));
  if(maxC/lower.length > 0.65) return {bs:true, reason:'detected repetitive characters'};

  // Repeating pattern (hjkhjk, asdfasdf)
  for(let len=2;len<=5;len++){
    const pat=lower.slice(0,len);
    const rep=pat.repeat(Math.ceil(lower.length/len)).slice(0,lower.length);
    if(rep===lower&&lower.length>=len*2) return {bs:true, reason:'detected keyboard mashing'};
  }

  // Too many consecutive consonants (>5 in a row)
  if(/[bcdfghjklmnpqrstvwxyz]{6,}/i.test(t)) return {bs:true, reason:'not a real response'};

  // All numbers
  if(/^\d+$/.test(t)) return {bs:true, reason:'numbers are not a personality response'};

  // Min 3 distinct chars
  if(Object.keys(cc).length < 3) return {bs:true, reason:'response too simple'};

  return {bs:false};
}

// ── CONTRADICTION DETECTOR ────────────────────────────────────────────────────
const POS_WORDS = ['calm','fine','okay','happy','good','quiet','peace','relax','ignore','shrug','nothing','don\'t care','unbothered','chill','smile','laugh','let it go','move on','whatever'];
const NEG_WORDS = ['angry','furious','hate','explode','scream','shout','punch','rage','upset','destroy','kill','lose it','freak out','cry','devastated','broken','snap','attack','fight'];

function sentimentScore(text){
  const t = text.toLowerCase();
  let pos=0, neg=0;
  POS_WORDS.forEach(w=>{ if(t.includes(w)) pos++; });
  NEG_WORDS.forEach(w=>{ if(t.includes(w)) neg++; });
  if(pos===0&&neg===0) return 0; // neutral
  return (pos-neg)/(pos+neg); // -1 to +1
}

function checkContradiction(emoId, newSit, newResp){
  // Get all existing responses in same emotion ball
  const existing = Object.entries(store.responses)
    .filter(([k])=>k.startsWith(emoId+'::') && k!==sitKey(emoId,newSit));
  if(existing.length===0) return null;

  const newScore = sentimentScore(newResp);
  if(Math.abs(newScore)<0.2) return null; // neutral — no contradiction possible

  const contradictions = [];
  existing.forEach(([k,resp])=>{
    const existScore = sentimentScore(resp);
    if(Math.abs(existScore)>0.2 && newScore*existScore<-0.3){
      const sit = k.split('::').slice(1).join('::');
      contradictions.push({sit, resp});
    }
  });
  return contradictions.length ? contradictions : null;
}

// ── TOTALS + PROGRESS BAR ─────────────────────────────────────────────────────
function totalSituations(){
  let t=0;
  CENTRAL_STATES.forEach(s=>t+=stateTotal(s.id));
  EMOTIONS.forEach(e=>t+=e.situations.length);
  return t;
}
function totalMapped(){ return Object.keys(store.responses).length; }
function compPct(){ return Math.round(totalMapped()/Math.max(totalSituations(),1)*100); }

function updateProgress(){
  const mapped = totalMapped();
  const total  = totalSituations();
  const pct    = Math.round(mapped/Math.max(total,1)*100);
  document.getElementById('pc').textContent = mapped;
  document.getElementById('pt').textContent = total;
  document.getElementById('comp-bar').style.width = Math.min(pct,100)+'%';
  document.getElementById('comp-pct').textContent = pct+'%';
  document.getElementById('comp-bar').style.background =
    pct>=92 ? 'linear-gradient(90deg,#daa520,#fbbf24)' : 'linear-gradient(90deg,#22c55e,#86efac)';

  // BS score
  const bsPct = Math.min(Math.round((store.bs_score||0)*100), 100);
  document.getElementById('bs-bar').style.width = bsPct+'%';
  document.getElementById('bs-pct').textContent = bsPct+'%';

  // 92% gate check
  if(pct>=92 && !store.empire_token) unlockEmpire();
  // Update gate button if exists
  if(document.getElementById('gate-btn')) updateGateBtn();
}

function showError(msg){
  const el = document.getElementById('val-error');
  el.textContent = '⚠ '+msg;
  el.style.opacity='1';
  setTimeout(()=>el.style.opacity='0', 2800);
}

// ── CONFLICT RESOLUTION ───────────────────────────────────────────────────────
function addConflict(emoId, sit1, resp1, sit2, resp2){
  if(!store.conflicts) store.conflicts=[];
  // avoid duplicates
  const key = emoId+'::'+sit1+'::'+sit2;
  if(store.conflicts.find(c=>c.key===key)) return;
  store.conflicts.push({key, emoId, sit1, resp1, sit2, resp2, resolved:false});
  store.bs_score = Math.min((store.bs_score||0)+0.12, 1);
  persist();
  updateProgress();
}

// ── EMPIRE UNLOCK ─────────────────────────────────────────────────────────────
function unlockEmpire(){
  // Generate soul token: hash of soul_id + responses
  const raw = store.id + Object.keys(store.responses).sort().join('') + Date.now();
  let hash = 0;
  for(let i=0;i<raw.length;i++){ hash=((hash<<5)-hash)+raw.charCodeAt(i); hash|=0; }
  const token = 'SF-' + Math.abs(hash).toString(36).toUpperCase().padStart(8,'0') + '-' + store.id.slice(5,9).toUpperCase();
  store.empire_token = token;
  persist();
  document.getElementById('soul-token-display').textContent = token;
  // POST anonymous soul completion — zero personal data
  fetch('/api/soul-complete.php', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({soul_id:store.id, completion:compPct()})
  }).then(r=>r.json()).then(d=>{
    if(d.ok) loadBottles(); // refresh bottles before showing gate
  }).catch(()=>{});
  // Play angel cutscene FIRST, then show unlock gate
  playAngelCutscene(()=>{
    document.getElementById('unlock-gate').style.display='flex';
    loadBottles();
  });
}

// ── THREE.JS SETUP ────────────────────────────────────────────────────────────
const canvas = document.getElementById('canvas');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setClearColor(0x050508,1);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.z = 7;
function resize(){ renderer.setSize(innerWidth,innerHeight); camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix(); }
resize(); addEventListener('resize',resize);

const group = new THREE.Group();
scene.add(group);

// ── STATE ─────────────────────────────────────────────────────────────────────
let VIEW = 'orbit';   // 'orbit' | 'emotion'
let activeEmo = null;
let emotionBalls = [];
let situationNodes = [];
let activeNode = null;

// ── CENTRAL STATES (indifference sphere variants) ─────────────────────────────
const CENTRAL_STATES = [
  { id:'indifference', emoji:'😐', label:'Indifference', color:0xdaa520, hex:'#daa520', situations:store.assigned['_state_indifference']||[] },
  { id:'hurry',        emoji:'⚡', label:'In a hurry',   color:0xdaa520, hex:'#daa520', situations:store.assigned['_state_hurry']||[] },
  { id:'scared',       emoji:'😰', label:'Scared',       color:0xdaa520, hex:'#daa520', situations:store.assigned['_state_scared']||[] },
  { id:'overwhelmed',  emoji:'😵', label:'Overwhelmed',  color:0xdaa520, hex:'#daa520', situations:store.assigned['_state_overwhelmed']||[] },
  { id:'excited',      emoji:'🤩', label:'Excited',      color:0xdaa520, hex:'#daa520', situations:store.assigned['_state_excited']||[] },
  { id:'funny',        emoji:'😂', label:'Funny',        color:0xfde047, hex:'#fde047', situations:store.assigned['_state_funny']||[] },
];

// Load any custom states saved by this user
if(store.custom_states) store.custom_states.forEach(cs=>{ if(!CENTRAL_STATES.find(s=>s.id===cs.id)) CENTRAL_STATES.push(cs); });

let activeStateId = store.activeStateId || 'indifference';
let INDIFFERENCE = (()=>{
  const base = CENTRAL_STATES.find(s=>s.id===activeStateId)||CENTRAL_STATES[0];
  const extra = store.custom_sits&&store.custom_sits[base.id]?store.custom_sits[base.id]:[];
  return {...base, situations:[...base.situations,...extra]};
})();

updateProgress();

// ── STATE BAR ─────────────────────────────────────────────────────────────────
function stateTotal(id){
  const st=CENTRAL_STATES.find(s=>s.id===id); if(!st) return 0;
  return st.situations.length+(store.custom_sits&&store.custom_sits[id]?store.custom_sits[id].length:0);
}
function stateMapped(id){
  const st=CENTRAL_STATES.find(s=>s.id===id); if(!st) return 0;
  const sits=[...st.situations,...(store.custom_sits&&store.custom_sits[id]?store.custom_sits[id]:[])];
  return sits.filter(s=>store.responses[id+'::'+s]).length;
}

function renderStateBar(){
  const bar=document.getElementById('state-bar');
  bar.innerHTML='';
  CENTRAL_STATES.forEach(st=>{
    const total=stateTotal(st.id), mapped=stateMapped(st.id);
    const pill=document.createElement('div');
    pill.className='state-pill'+(st.id===activeStateId?' active':'')+(mapped>=total&&total>0?' done':'');
    pill.textContent=st.emoji+' '+st.label+(mapped>0&&mapped<total?' '+mapped+'/'+total:'');
    pill.addEventListener('click',()=>setActiveState(st.id));
    bar.appendChild(pill);
  });
  const addBtn=document.createElement('button');
  addBtn.id='state-add-btn'; addBtn.textContent='+ state';
  addBtn.addEventListener('click',()=>{
    const row=document.getElementById('state-input-row');
    row.style.display=row.style.display==='flex'?'none':'flex';
  });
  bar.appendChild(addBtn);
  const inputRow=document.createElement('div');
  inputRow.id='state-input-row';
  inputRow.innerHTML='<input id="state-emoji-in" maxlength="2" placeholder="😶"><input id="state-name-in" maxlength="24" placeholder="state name…"><button id="state-save-btn">add</button>';
  bar.appendChild(inputRow);
  document.getElementById('state-save-btn').addEventListener('click',addCustomState);
  document.getElementById('state-name-in').addEventListener('keydown',e=>{if(e.key==='Enter')addCustomState();});
}

function addCustomState(){
  const emoji=(document.getElementById('state-emoji-in').value.trim()||'🔮');
  const label=document.getElementById('state-name-in').value.trim();
  if(!label)return;
  const id='state_'+label.toLowerCase().replace(/\s+/g,'_').slice(0,20)+'_'+Date.now();
  const newSt={id,emoji,label,color:0xdaa520,hex:'#daa520',situations:['How do you usually handle things in this state?','What do you want most when you feel this way?','What\'s the first thing you do when this hits?']};
  CENTRAL_STATES.push(newSt);
  if(!store.custom_states)store.custom_states=[];
  store.custom_states.push(newSt);
  persist();
  setActiveState(id);
}

function setActiveState(stateId){
  activeStateId=stateId;
  const base=CENTRAL_STATES.find(s=>s.id===stateId)||CENTRAL_STATES[0];
  const extra=store.custom_sits&&store.custom_sits[stateId]?store.custom_sits[stateId]:[];
  INDIFFERENCE={...base,situations:[...base.situations,...extra]};
  store.activeStateId=stateId;
  persist();
  panel.classList.add('hidden'); activeNode=null;
  renderStateBar();
  buildOrbitView();
}

// ── BUILD ORBIT VIEW ──────────────────────────────────────────────────────────
function buildOrbitView(){
  clearGroup();
  emotionBalls = [];
  situationNodes = [];
  VIEW = 'orbit';

  document.getElementById('back-btn').style.display='none';
  document.getElementById('emotion-label').style.opacity='0';
  document.getElementById('add-sit-row').style.display='none';

  // ── CENTRE: big indifference ball ──
  const iTotal = INDIFFERENCE.situations.length||1;
  const iFilled = INDIFFERENCE.situations.filter(s=>store.responses[sitKey(INDIFFERENCE.id,s)]).length;
  const iPct = iFilled/iTotal;
  const coreMesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.72+iPct*0.2, 28, 20),
    new THREE.MeshBasicMaterial({color:0xdaa520, transparent:true, opacity:0.18+iPct*0.5})
  );
  coreMesh.userData = {type:'emo', emo:INDIFFERENCE, filled:iFilled, total:iTotal};
  group.add(coreMesh);
  emotionBalls.push(coreMesh);

  // Wireframe shell for centre
  const cWire = new THREE.Mesh(
    new THREE.SphereGeometry(0.74+iPct*0.2, 20, 14),
    new THREE.MeshBasicMaterial({color:0xdaa520, wireframe:true, transparent:true, opacity:0.12})
  );
  group.add(cWire);

  // Glow rings around centre
  for(let r=0;r<3;r++){
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(0.82+r*0.22+iPct*0.1, 0.85+r*0.22+iPct*0.1, 36),
      new THREE.MeshBasicMaterial({color:0xdaa520, side:THREE.DoubleSide, transparent:true, opacity:0.07-r*0.02})
    );
    ring.userData.ring=true;
    group.add(ring);
  }

  // Centre label
  const cLabel = makeLabel('⚪ Indifference', '#daa520', iFilled, iTotal);
  cLabel.position.set(0, -1.1, 0);
  group.add(cLabel);

  // ── ORBIT: emotion balls ──
  const n = EMOTIONS.length;
  EMOTIONS.forEach((emo, i)=>{
    const angle = (i / n) * Math.PI * 2;
    const orbit = 2.9;
    const x = Math.cos(angle)*orbit, z = Math.sin(angle)*orbit;
    const y = Math.sin(angle*2.3)*0.55;

    const filled = emo.situations.filter(s=>store.responses[sitKey(emo.id,s)]).length;
    const total = emo.situations.length || 1;
    const pct = filled/total;

    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.22+pct*0.12, 18, 14),
      new THREE.MeshBasicMaterial({color:emo.color, transparent:true, opacity:0.22+pct*0.68})
    );
    mesh.position.set(x,y,z);
    mesh.userData = {type:'emo', emo, filled, total};
    group.add(mesh);
    emotionBalls.push(mesh);

    const wMesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.24+pct*0.12, 12, 10),
      new THREE.MeshBasicMaterial({color:emo.color, wireframe:true, transparent:true, opacity:0.07+pct*0.08})
    );
    wMesh.position.copy(mesh.position);
    group.add(wMesh);

    // Connector line from centre to ball
    const pts = [new THREE.Vector3(0,0,0), new THREE.Vector3(x,y,z)];
    const lineGeo = new THREE.BufferGeometry().setFromPoints(pts);
    const line = new THREE.Line(lineGeo, new THREE.LineBasicMaterial({color:emo.color, transparent:true, opacity:0.06+pct*0.08}));
    group.add(line);

    const label = makeLabel(emo.emoji+' '+emo.label, emo.hex, filled, total);
    label.position.set(x, y-0.42, z);
    group.add(label);
  });
}

function makeLabel(text, hex, filled, total){
  const c = document.createElement('canvas'); c.width=256; c.height=64;
  const ctx = c.getContext('2d');
  ctx.clearRect(0,0,256,64);
  ctx.font = '18px Segoe UI';
  ctx.fillStyle = hex;
  ctx.textAlign='center';
  ctx.fillText(text, 128, 28);
  if(total>0){
    ctx.font='12px Segoe UI';
    ctx.fillStyle='#475569';
    ctx.fillText(filled+'/'+total, 128, 46);
  }
  const tex = new THREE.CanvasTexture(c);
  const mat = new THREE.SpriteMaterial({map:tex, transparent:true});
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(1.2, 0.3, 1);
  sprite.userData = {isLabel:true};
  return sprite;
}

// ── BUILD EMOTION VIEW ────────────────────────────────────────────────────────
function buildEmotionView(emo){
  clearGroup();
  situationNodes = [];
  emotionBalls = [];
  VIEW = 'emotion';
  activeEmo = CENTRAL_STATES.find(s=>s.id===emo.id) ? INDIFFERENCE : emo;
  emo = activeEmo;

  document.getElementById('back-btn').style.display='block';
  const el = document.getElementById('emotion-label');
  el.style.opacity='1';
  document.getElementById('emotion-name').textContent = emo.emoji + '  ' + emo.label;
  document.getElementById('emotion-name').style.color = emo.hex;
  document.getElementById('emotion-sub').textContent = emo.situations.length + ' situations';

  document.getElementById('add-sit-row').style.display='flex';
  document.getElementById('add-sit-input').placeholder = 'add a '+emo.label.toLowerCase()+' situation…';

  // Central emotion core
  const core = new THREE.Mesh(
    new THREE.SphereGeometry(0.35,24,18),
    new THREE.MeshBasicMaterial({color:emo.color, transparent:true, opacity:0.5})
  );
  group.add(core);

  // Wireframe sphere for nodes
  const wMat = new THREE.MeshBasicMaterial({color:emo.color, wireframe:true, transparent:true, opacity:0.08});
  group.add(new THREE.Mesh(new THREE.SphereGeometry(2.2,22,14), wMat));

  if(emo.situations.length === 0){
    // Show empty state
    return;
  }

  // Fibonacci distribute situation nodes
  const pts = fibSphere(emo.situations.length, 2.2);
  emo.situations.forEach((sit, i)=>{
    const filled = !!store.responses[sitKey(emo.id, sit)];
    const mat = new THREE.MeshBasicMaterial({color: filled ? emo.color : 0x1e293b});
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.09,12,12), mat);
    mesh.position.copy(pts[i]);
    mesh.userData = {type:'sit', emo, sit, filled};
    group.add(mesh);
    situationNodes.push(mesh);

    if(filled){
      const rMat = new THREE.MeshBasicMaterial({color:emo.color, side:THREE.DoubleSide, transparent:true, opacity:0.3});
      const ring = new THREE.Mesh(new THREE.RingGeometry(0.11,0.15,16), rMat);
      ring.position.copy(pts[i]);
      ring.userData.ring=true;
      mesh.userData.ringMesh=ring;
      group.add(ring);
    }
  });
  document.getElementById('emotion-sub').textContent = emo.situations.length + ' situations · ' + emo.situations.filter(s=>store.responses[sitKey(emo.id,s)]).length + ' mapped';

  // Add conflict nodes for this emotion (orange, unresolved)
  if(store.conflicts){
    const emoConflicts = store.conflicts.filter(c=>c.emoId===emo.id&&!c.resolved);
    emoConflicts.forEach((c,ci)=>{
      const angle = (ci/Math.max(emoConflicts.length,1))*Math.PI*2;
      const R2=2.2, x2=Math.cos(angle)*R2, z2=Math.sin(angle)*R2;
      const cMesh=new THREE.Mesh(
        new THREE.SphereGeometry(0.11,12,12),
        new THREE.MeshBasicMaterial({color:0xf97316})
      );
      cMesh.position.set(x2,0.3,z2);
      cMesh.userData={type:'conflict',conflict:c,emo};
      group.add(cMesh);
      situationNodes.push(cMesh);
    });
  }
}

function fibSphere(n, r){
  const pts=[], phi=Math.PI*(3-Math.sqrt(5));
  for(let i=0;i<n;i++){
    const y=1-(i/(n-1))*2, rad=Math.sqrt(1-y*y), t=phi*i;
    pts.push(new THREE.Vector3(Math.cos(t)*rad*r, y*r, Math.sin(t)*rad*r));
  }
  return pts;
}

function clearGroup(){ while(group.children.length) group.remove(group.children[0]); }

// ── RAYCASTING ────────────────────────────────────────────────────────────────
const ray=new THREE.Raycaster(), mouse=new THREE.Vector2();
const tip=document.getElementById('node-tip');
let hovered=null;

function getHits(e, objs){
  const r=canvas.getBoundingClientRect();
  mouse.x=((e.clientX-r.left)/r.width)*2-1;
  mouse.y=-((e.clientY-r.top)/r.height)*2+1;
  ray.setFromCamera(mouse,camera);
  return ray.intersectObjects(objs);
}

canvas.addEventListener('mousemove',e=>{
  if(dragging) return;
  const targets = VIEW==='orbit' ? emotionBalls : situationNodes;
  const hits = getHits(e, targets);
  if(hits.length){
    const n=hits[0].object;
    if(hovered&&hovered!==n) restoreHover(hovered);
    hovered=n;
    n.material.color.setHex(0xffffff);
    canvas.style.cursor='pointer';
    tip.style.opacity='1';
    tip.style.left=(e.clientX+14)+'px';
    tip.style.top=(e.clientY-10)+'px';
    if(VIEW==='orbit'){
      const emo=n.userData.emo;
      document.getElementById('nt-sit').textContent=emo.emoji+' '+emo.label;
      document.getElementById('nt-resp').textContent=n.userData.filled+'/'+n.userData.total+' situations mapped';
    } else if(n.userData.type==='conflict'){
      document.getElementById('nt-sit').style.color='#f97316';
      document.getElementById('nt-sit').textContent='⚠ Contradiction detected';
      document.getElementById('nt-resp').textContent='Tap to resolve this conflict';
    } else {
      const {emo,sit}=n.userData;
      document.getElementById('nt-sit').style.color='#94a3b8';
      document.getElementById('nt-sit').textContent=sit;
      document.getElementById('nt-resp').textContent=store.responses[sitKey(emo.id,sit)]||'— tap to map —';
    }
  } else {
    if(hovered){restoreHover(hovered);hovered=null;}
    canvas.style.cursor='grab';
    tip.style.opacity='0';
  }
});

function restoreHover(n){
  if(VIEW==='orbit'){
    n.material.color.setHex(n.userData.emo.color);
  } else {
    n.material.color.setHex(n.userData.filled ? n.userData.emo.color : 0x1e293b);
  }
}

canvas.addEventListener('click',e=>{
  const targets = VIEW==='orbit' ? emotionBalls : situationNodes;
  const hits = getHits(e, targets);
  if(!hits.length) return;
  const n=hits[0].object;
  if(VIEW==='orbit'){
    buildEmotionView(n.userData.emo);
    autoRotate=true;
  } else {
    openSituation(n);
  }
});

// ── ADD CUSTOM EMOTION BALL ───────────────────────────────────────────────────
document.getElementById('add-emo-btn').addEventListener('click',()=>{
  const label = document.getElementById('add-emo-input').value.trim();
  if(!label) return;
  const id = 'custom_'+label.toLowerCase().replace(/\s+/g,'_').slice(0,20)+'_'+Date.now();
  const colors = [0x84cc16,0x06b6d4,0xe879f9,0xfb923c,0x34d399,0xf472b6,0xa78bfa];
  const col = colors[Math.floor(Math.random()*colors.length)];
  const hex = '#'+col.toString(16).padStart(6,'0');
  const newEmo = {id, label, color:col, hex, emoji:'🔮', situations:[]};
  EMOTIONS.push(newEmo);
  if(!store.custom_sits) store.custom_sits={};
  if(!store.custom_sits[id]) store.custom_sits[id]=[];
  persist();
  document.getElementById('add-emo-input').value='';
  document.getElementById('add-emo-row').style.display='none';
  buildOrbitView();
});

// ── DRAG ──────────────────────────────────────────────────────────────────────
let dragging=false,px=0,py=0,vx=0,vy=0,autoRotate=true;
canvas.addEventListener('mousedown',e=>{dragging=true;px=e.clientX;py=e.clientY;autoRotate=false;vx=0;vy=0;});
addEventListener('mouseup',()=>dragging=false);
addEventListener('mousemove',e=>{
  if(!dragging)return;
  vx=(e.clientX-px)*0.005;vy=(e.clientY-py)*0.005;
  group.rotation.y+=vx;group.rotation.x+=vy;
  px=e.clientX;py=e.clientY;
});
canvas.addEventListener('touchstart',e=>{dragging=true;px=e.touches[0].clientX;py=e.touches[0].clientY;autoRotate=false;},{passive:true});
canvas.addEventListener('touchend',()=>dragging=false,{passive:true});
canvas.addEventListener('touchmove',e=>{
  if(!dragging)return;
  vx=(e.touches[0].clientX-px)*0.005;vy=(e.touches[0].clientY-py)*0.005;
  group.rotation.y+=vx;group.rotation.x+=vy;
  px=e.touches[0].clientX;py=e.touches[0].clientY;
},{passive:true});

// ── PANEL ─────────────────────────────────────────────────────────────────────
const panel=document.getElementById('panel');
const panelInput=document.getElementById('panel-input');
const panelSit=document.getElementById('panel-sit');
const panelEmo=document.getElementById('panel-emotion');

function openSituation(node){
  activeNode=node;

  // Conflict resolution node
  if(node.userData.type==='conflict'){
    const c=node.userData.conflict, emo=node.userData.emo;
    panelEmo.textContent='⚠ CONFLICT — '+emo.emoji+' '+emo.label;
    panelEmo.style.color='#f97316';
    panelSit.textContent=
      'You said "'+c.resp1+'" for: '+c.sit1+
      '\n\nBut you said "'+c.resp2+'" for: '+c.sit2+
      '\n\nWhich is more true for you?';
    panelInput.value='';
    panelInput.placeholder='resolve this contradiction…';
    panel.classList.remove('hidden');
    autoRotate=false;
    // Override lock to resolve conflict
    node.userData._resolving=true;
    return;
  }

  const {emo,sit}=node.userData;
  panelEmo.textContent=emo.emoji+' '+emo.label;
  panelEmo.style.color=emo.hex;
  panelSit.textContent=sit;
  panelInput.value=store.responses[sitKey(emo.id,sit)]||'';
  panelInput.placeholder='your shortest automatic response…';
  panel.classList.remove('hidden');
  autoRotate=false;
  setTimeout(()=>panelInput.focus(),400);
  speak(sit);
}

document.getElementById('lock-btn').addEventListener('click',()=>{
  if(!activeNode)return;
  const val=panelInput.value.trim();
  if(!val)return;

  // ── BULLSHIT CHECK ──
  const bsResult = detectBullshit(val);
  if(bsResult.bs){
    showError(bsResult.reason);
    panelInput.style.borderColor='rgba(239,68,68,0.5)';
    setTimeout(()=>panelInput.style.borderColor='',1500);
    store.bs_score = Math.min((store.bs_score||0)+0.08, 1);
    persist(); updateProgress();
    return;
  }

  // ── CONFLICT RESOLUTION ──
  if(activeNode.userData._resolving){
    const c=activeNode.userData.conflict;
    c.resolved=true; c.resolution=val;
    store.bs_score = Math.max((store.bs_score||0)-0.1, 0);
    persist(); updateProgress();
    panel.classList.add('hidden');
    buildEmotionView(activeNode.userData.emo);
    activeNode=null; autoRotate=true;
    return;
  }

  const {emo,sit}=activeNode.userData;

  // ── CONTRADICTION CHECK ──
  const contradictions = checkContradiction(emo.id, sit, val);
  if(contradictions){
    contradictions.forEach(c=>{
      addConflict(emo.id, sit, val, c.sit, c.resp);
    });
    showError('Contradiction flagged — conflict node added to your sphere');
  }

  store.responses[sitKey(emo.id,sit)]=val;
  activeNode.userData.filled=true;
  persist(); updateProgress();
  panel.classList.add('hidden');
  buildEmotionView(emo);
  activeNode=null; autoRotate=true;
});

document.getElementById('skip-btn').addEventListener('click',()=>{
  panel.classList.add('hidden');activeNode=null;autoRotate=true;
});

panelInput.addEventListener('keydown',e=>{
  if(e.key==='Enter') document.getElementById('lock-btn').click();
  if(e.key==='Escape'){panel.classList.add('hidden');activeNode=null;autoRotate=true;}
});

// ── BACK BUTTON ───────────────────────────────────────────────────────────────
document.getElementById('back-btn').addEventListener('click',()=>{
  panel.classList.add('hidden');activeNode=null;
  buildOrbitView(); autoRotate=true;
});

// ── NEW EMOTION TOGGLE ────────────────────────────────────────────────────────
document.getElementById('add-emo-toggle').addEventListener('click',()=>{
  const row=document.getElementById('add-emo-row');
  row.style.display = row.style.display==='flex' ? 'none' : 'flex';
});

// ── ADD CUSTOM SITUATION ──────────────────────────────────────────────────────
document.getElementById('add-sit-btn').addEventListener('click',()=>{
  const val=document.getElementById('add-sit-input').value.trim();
  if(!val||!activeEmo)return;
  if(!store.custom_sits) store.custom_sits={};
  if(!store.custom_sits[activeEmo.id]) store.custom_sits[activeEmo.id]=[];
  store.custom_sits[activeEmo.id].push(val);
  activeEmo.situations.push(val);
  persist();
  document.getElementById('add-sit-input').value='';
  buildEmotionView(activeEmo);
});
document.getElementById('add-sit-input').addEventListener('keydown',e=>{
  if(e.key==='Enter') document.getElementById('add-sit-btn').click();
});

// ── SPEECH ────────────────────────────────────────────────────────────────────
const synth=window.speechSynthesis;
function speak(text){
  if(!synth)return; synth.cancel();
  const u=new SpeechSynthesisUtterance('In this situation: '+text+'. What would you say?');
  u.rate=0.88;u.pitch=0.95;u.volume=0.75; synth.speak(u);
}
const micBtn=document.getElementById('mic-btn');
let listening=false;
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
if(SR){
  const rec=new SR(); rec.continuous=false;rec.interimResults=false;rec.lang='en-GB';
  rec.onresult=e=>{panelInput.value=e.results[0][0].transcript;listening=false;micBtn.classList.remove('listening');synth&&synth.cancel();};
  rec.onend=()=>{listening=false;micBtn.classList.remove('listening');};
  rec.onerror=()=>{listening=false;micBtn.classList.remove('listening');};
  micBtn.addEventListener('click',()=>{
    if(listening){rec.stop();return;}
    synth&&synth.cancel();listening=true;micBtn.classList.add('listening');rec.start();
  });
} else { micBtn.style.opacity='0.3'; }

// ── EXPORT ────────────────────────────────────────────────────────────────────
document.getElementById('export-btn').addEventListener('click',()=>{
  const out={
    soul_id:store.id,
    soul_file:'shortfactory-soul-v1',
    soul_architecture:'QmQizbmvULCRxLdo9cuvFgZuLViWGJV73d3GbDSAQebp2Y',
    timestamp:new Date().toISOString(),
    version:'soul-sphere-v3',
    total_mapped:totalMapped(),
    central_states:{},
    emotions:{}
  };
  CENTRAL_STATES.forEach(st=>{
    const mapped={};
    const sits=[...st.situations,...(store.custom_sits&&store.custom_sits[st.id]?store.custom_sits[st.id]:[])];
    sits.forEach(s=>{ if(store.responses[st.id+'::'+s]) mapped[s]=store.responses[st.id+'::'+s]; });
    if(Object.keys(mapped).length) out.central_states[st.emoji+' '+st.label]=mapped;
  });
  EMOTIONS.forEach(emo=>{
    const mapped={};
    emo.situations.forEach(s=>{ if(store.responses[sitKey(emo.id,s)]) mapped[s]=store.responses[sitKey(emo.id,s)]; });
    if(Object.keys(mapped).length) out.emotions[emo.label]=mapped;
  });
  const blob=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download=store.id+'-soul.json';a.click();
});

// ── GATE BUTTON + INTRO ───────────────────────────────────────────────────────
function updateGateBtn(){
  const pct=compPct();
  document.getElementById('gate-pct-label').textContent=pct+'% mapped';
  const btn=document.getElementById('gate-btn');
  btn.className = pct>=92 ? 'ready' : '';
  btn.textContent = pct>=92 ? 'ENTER THE EMPIRE →' : 'ENTER ('+pct+'%) →';
}

document.getElementById('gate-btn').addEventListener('click',()=>{
  if(compPct()>=92){ window.location='index3.php'; return; }
  document.getElementById('gate-modal').style.display='flex';
  document.getElementById('gate-modal-pct').textContent=compPct()+'%';
});
document.getElementById('gate-keep').addEventListener('click',()=>{
  document.getElementById('gate-modal').style.display='none';
});

// Show intro only on first visit (no responses yet)
if(Object.keys(store.responses).length===0 && !store.intro_seen){
  document.getElementById('intro').style.display='flex';
} else {
  document.getElementById('intro').style.display='none';
}
document.getElementById('intro-begin').addEventListener('click',()=>{
  store.intro_seen=true; persist();
  document.getElementById('intro').style.display='none';
});

// ── RENDER LOOP ───────────────────────────────────────────────────────────────
updateGateBtn();
renderStateBar();
buildOrbitView();
const clock=new THREE.Clock();
function animate(){
  requestAnimationFrame(animate);
  if(autoRotate) group.rotation.y+=0.004;
  else if(!dragging){ vx*=0.92;vy*=0.92;group.rotation.y+=vx;group.rotation.x+=vy; if(Math.abs(vx)<0.0005&&Math.abs(vy)<0.0005&&!activeNode) autoRotate=true; }
  // rings face camera
  group.children.forEach(c=>{ if(c.userData&&c.userData.ring) c.lookAt(camera.position); });
  renderer.render(scene,camera);
}
animate();

// ── BOTTLE JAR SYSTEM ────────────────────────────────────────────────────────
let bottleData = [];

function loadBottles(){
  fetch('/api/soul-complete.php').then(r=>r.json()).then(d=>{
    if(!d.ok) return;
    bottleData = d.souls || [];
    renderBottles('bottle-row', bottleData);
    renderBottles('bottle-row-unlock', bottleData);
    renderBottles('bottle-row-main', bottleData);
    const lbl = document.getElementById('bottle-label');
    if(lbl) lbl.textContent = 'SOULS CAPTURED — ' + bottleData.length;
    const lbl2 = document.getElementById('bottle-label-unlock');
    if(lbl2) lbl2.textContent = 'SOULS IN THE COLLECTIVE — ' + bottleData.length;
    const lbl3 = document.getElementById('jar-label');
    if(lbl3) lbl3.textContent = 'SOULS CAPTURED — ' + bottleData.length;
  }).catch(()=>{});
}

// Dan's soul ID — the first jar. Public, clickable.
const DAN_SOUL_ID = 'soul-lru7bqkz-1pnb';

function renderBottles(containerId, souls){
  const wrap = document.getElementById(containerId);
  if(!wrap) return;
  wrap.innerHTML = '';
  if(souls.length === 0){
    wrap.innerHTML = '<span style="font-size:10px;color:#1e293b;letter-spacing:1px;">no souls yet — be the first</span>';
    return;
  }
  souls.forEach(s => {
    const isDan = s.soul_id === DAN_SOUL_ID;
    const b = document.createElement(isDan ? 'a' : 'span');
    b.className = 'soul-bottle filled';
    b.textContent = '🫙'; // 🍶
    b.dataset.soulId = s.soul_id;
    b.dataset.completedAt = s.completed_at || '';
    b.dataset.isPublic = isDan ? 'true' : 'false';
    if(isDan){
      b.style.textDecoration = 'none';
      b.style.filter = 'none';
      b.style.cursor = 'pointer';
      b.title = 'PUBLIC SOUL — click to explore';
      b.addEventListener('click', function(ev){
        ev.preventDefault();
        playFairyCutscene(()=>{ window.location.href='/soul-viewer.html'; });
      });
    }
    b.addEventListener('mouseenter', showBottleTip);
    b.addEventListener('mousemove', moveBottleTip);
    b.addEventListener('mouseleave', hideBottleTip);
    wrap.appendChild(b);
  });
}

// ── BOTTLE TOOLTIP ───────────────────────────────────────────────────────────
const bTip = document.getElementById('bottle-tooltip');

function showBottleTip(e){
  const sid = e.target.dataset.soulId || '???';
  const ts = e.target.dataset.completedAt || '';
  const isPublic = e.target.dataset.isPublic === 'true';
  if(isPublic){
    document.getElementById('bt-id').innerHTML =
      '<span style="color:#daa520;font-family:monospace;font-size:10px;letter-spacing:1px;">PUBLIC SOUL</span>' +
      '<br><span style="color:#22c55e;font-size:9px;">Click to explore this person\'s 3D soul sphere</span>' +
      (ts ? '<br><span style="color:#334155;font-size:9px;">' + new Date(ts).toLocaleDateString() + '</span>' : '');
  } else {
    document.getElementById('bt-id').innerHTML =
      '<span style="color:#94a3b8;font-family:monospace;font-size:10px;letter-spacing:1px;">ANONYMOUS · USER OWNED</span>' +
      '<br><span style="color:#475569;font-size:9px;">This soul is private. Only the owner can publish it.</span>' +
      (ts ? '<br><span style="color:#334155;font-size:9px;">' + new Date(ts).toLocaleDateString() + '</span>' : '');
  }
  bTip.style.opacity = '1';
}

function moveBottleTip(e){
  const x = Math.min(e.clientX + 16, window.innerWidth - 360);
  // Position ABOVE cursor if near bottom, otherwise below
  const tipH = 320; // approx tooltip height
  let y = e.clientY - 10;
  if(y + tipH > window.innerHeight - 20){
    y = e.clientY - tipH - 10;
  }
  bTip.style.left = x + 'px';
  bTip.style.top = Math.max(10, y) + 'px';
}

function hideBottleTip(){ bTip.style.opacity = '0'; }

// Load bottles on page init
loadBottles();

// Also load bottles when gate modal opens
const _origGateClick = document.getElementById('gate-btn').onclick;
document.getElementById('gate-btn').addEventListener('click', ()=>{ loadBottles(); });

// ── ANGEL CUTSCENE ───────────────────────────────────────────────────────────
// ── FAIRY-INTO-JAR CUTSCENE (click Dan's bottle) ─────────────────────────────
function playFairyCutscene(onComplete){
  const overlay = document.getElementById('angel-cutscene');
  const canvas = document.getElementById('angel-canvas');
  overlay.style.display = 'flex';
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  const cx = canvas.width/2, cy = canvas.height/2;

  // Jar position
  const jarX = cx, jarY = cy + 40;
  const jarW = 70, jarH = 100;

  // Fairy state
  let fairyX = cx - 180, fairyY = cy - 120;
  let sparkles = [];
  for(let i=0;i<40;i++) sparkles.push({
    x:Math.random()*canvas.width, y:Math.random()*canvas.height,
    r:Math.random()*1.5+0.3, speed:Math.random()*0.4+0.1, phase:Math.random()*Math.PI*2
  });

  const startTime = performance.now();
  const TOTAL = 6000;

  function drawJar(glow, fillLevel){
    ctx.save();
    ctx.translate(jarX, jarY);
    // Jar body
    ctx.beginPath();
    ctx.moveTo(-jarW/2, 10);
    ctx.lineTo(-jarW/2, -jarH*0.55);
    ctx.quadraticCurveTo(-jarW/2, -jarH*0.7, -jarW/3, -jarH*0.78);
    ctx.lineTo(-jarW/3, -jarH*0.92);
    // Lid rim
    ctx.lineTo(-jarW/2.5, -jarH*0.92);
    ctx.lineTo(-jarW/2.5, -jarH);
    ctx.lineTo(jarW/2.5, -jarH);
    ctx.lineTo(jarW/2.5, -jarH*0.92);
    ctx.lineTo(jarW/3, -jarH*0.92);
    ctx.lineTo(jarW/3, -jarH*0.78);
    ctx.quadraticCurveTo(jarW/2, -jarH*0.7, jarW/2, -jarH*0.55);
    ctx.lineTo(jarW/2, 10);
    ctx.closePath();
    ctx.strokeStyle = 'rgba(218,165,32,'+(0.3+glow*0.7)+')';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    // Fill glow inside jar
    if(fillLevel > 0){
      const grad = ctx.createLinearGradient(0, 10, 0, -jarH*0.55);
      grad.addColorStop(0, 'rgba(168,85,247,'+fillLevel*0.3+')');
      grad.addColorStop(1, 'rgba(218,165,32,'+fillLevel*0.1+')');
      ctx.fillStyle = grad;
      ctx.fill();
    }
    ctx.restore();
  }

  function drawFairy(x, y, scale, wingPhase){
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);
    // Outer glow
    const grad = ctx.createRadialGradient(0, 0, 0, 0, 0, 35);
    grad.addColorStop(0, 'rgba(168,85,247,0.4)');
    grad.addColorStop(0.5, 'rgba(204,68,255,0.15)');
    grad.addColorStop(1, 'rgba(168,85,247,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(-40,-40,80,80);
    // Body — glowing orb
    ctx.beginPath();
    ctx.arc(0, 0, 5, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(204,68,255,0.95)';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(0, 0, 3, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.fill();
    // Wings — butterfly shape
    const ws = 0.7 + Math.sin(wingPhase)*0.3;
    // Left wing
    ctx.beginPath();
    ctx.moveTo(-2, -2);
    ctx.quadraticCurveTo(-18*ws, -20*ws, -22*ws, -5);
    ctx.quadraticCurveTo(-18*ws, 8*ws, -2, 2);
    ctx.fillStyle = 'rgba(204,68,255,0.2)';
    ctx.fill();
    // Right wing
    ctx.beginPath();
    ctx.moveTo(2, -2);
    ctx.quadraticCurveTo(18*ws, -20*ws, 22*ws, -5);
    ctx.quadraticCurveTo(18*ws, 8*ws, 2, 2);
    ctx.fill();
    // Trail
    ctx.beginPath();
    ctx.moveTo(0, 5);
    ctx.lineTo(-2, 18);
    ctx.lineTo(0, 15);
    ctx.lineTo(2, 18);
    ctx.lineTo(0, 5);
    ctx.fillStyle = 'rgba(168,85,247,0.2)';
    ctx.fill();
    ctx.restore();
  }

  function drawText(text, y, size, color, a){
    ctx.save();
    ctx.globalAlpha = Math.max(0, Math.min(1, a));
    ctx.font = size+'px "Segoe UI", system-ui, sans-serif';
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.fillText(text, cx, y);
    ctx.restore();
  }

  function ease(t){ return t<0.5 ? 2*t*t : -1+(4-2*t)*t; }

  function frame(now){
    const t = now - startTime;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Sparkles
    sparkles.forEach(p => {
      p.y -= p.speed;
      if(p.y < -10) p.y = canvas.height + 10;
      const a = 0.15 + Math.sin(t*0.003 + p.phase)*0.1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fillStyle = 'rgba(168,85,247,'+a+')';
      ctx.fill();
    });

    if(t < 1200){
      // Phase 0: Fairy appears, floats near jar. Jar empty.
      const prog = t/1200;
      drawJar(0.1, 0);
      drawFairy(fairyX + Math.sin(t*0.005)*20, fairyY + Math.cos(t*0.004)*10, 1, t*0.015);
      drawText('🧚', cy - canvas.height*0.38, 28, '#fff', Math.min(prog*3, 1));
      drawText('THE OBSERVER', cy - canvas.height*0.38 + 32, 14, '#cc44ff', Math.min(prog*2, 1));
      drawText('Your consciousness is not your personality.', cy - canvas.height*0.38 + 52, 11, '#475569', Math.max(0, (prog-0.4)*2));
      drawText('It is the thing WATCHING your personality.', cy - canvas.height*0.38 + 68, 11, '#475569', Math.max(0, (prog-0.6)*2));

    } else if(t < 2200){
      // Phase 1: Labels appear — jar = personality, fairy = observer
      const prog = (t-1200)/1000;
      drawJar(0.2, 0);
      drawFairy(fairyX + Math.sin(t*0.005)*15, fairyY + Math.cos(t*0.004)*8, 1, t*0.015);
      // Labels
      drawText('🫙 = YOUR PERSONALITY', jarX, jarY + jarH/2 + 30, 12, '#daa520', Math.min(prog*3, 1));
      drawText('Emotions · Reactions · Patterns', jarX, jarY + jarH/2 + 48, 10, '#475569', Math.max(0, (prog-0.3)*2));
      drawText('🧚 = THE OBSERVER', fairyX, fairyY + 40, 12, '#cc44ff', Math.min(prog*3, 1));
      drawText('The one watching it all', fairyX, fairyY + 56, 10, '#475569', Math.max(0, (prog-0.3)*2));
      drawText('THE OBSERVER', cy - canvas.height*0.38 + 32, 14, '#cc44ff', 1);

    } else if(t < 3800){
      // Phase 2: Fairy flies to jar top, then descends through opening
      const prog = (t-2200)/1600;
      const ep = ease(prog);
      const topX = jarX;
      const topY = jarY - jarH * 1.05; // just above jar opening
      const insideY = jarY - jarH * 0.2; // inside the jar
      let curX, curY, scale;
      if(prog < 0.5){
        // First half: fly to hover above jar opening
        const p2 = ease(prog * 2);
        curX = fairyX + (topX - fairyX) * p2 + Math.sin(t*0.008)*(15*(1-p2));
        curY = fairyY + (topY - fairyY) * p2 + Math.cos(t*0.006)*(10*(1-p2));
        scale = 1 - prog*0.3;
      } else {
        // Second half: descend straight down through opening into jar
        const p2 = ease((prog - 0.5) * 2);
        curX = topX + Math.sin(t*0.01)*(3*(1-p2));
        curY = topY + (insideY - topY) * p2;
        scale = 0.85 - (prog-0.5)*1.2;
      }
      drawJar(0.2 + prog*0.5, prog*0.4);
      if(scale > 0.05) drawFairy(curX, curY, Math.max(0.05, scale), t*0.02);
      drawText('ENTANGLING...', cy + jarH + 50, 13, '#cc44ff', Math.min(prog*2, 1));
      drawText('The observer enters its digital vessel', cy + jarH + 70, 10, '#475569', Math.max(0, (prog-0.3)*2));

    } else if(t < 5200){
      // Phase 3: Jar glows — soul + observer united
      const prog = (t-3800)/1400;
      drawJar(0.7 + prog*0.3, 0.4 + prog*0.6);
      // Inner purple glow — contained within jar
      const glowR = 15 + prog*20;
      const glowCY = jarY - jarH*0.4;
      const grad = ctx.createRadialGradient(jarX, glowCY, 0, jarX, glowCY, glowR);
      grad.addColorStop(0, 'rgba(204,68,255,'+(0.35*prog)+')');
      grad.addColorStop(0.4, 'rgba(218,165,32,'+(0.2*prog)+')');
      grad.addColorStop(1, 'rgba(168,85,247,0)');
      ctx.fillStyle = grad;
      ctx.fillRect(jarX-glowR, glowCY-glowR, glowR*2, glowR*2);
      drawText('CAPTURED', cy + jarH + 50, 16, '#daa520', Math.min(prog*3, 1));
      drawText('Personality mapped. Observer entangled.', cy + jarH + 72, 11, '#22c55e', Math.max(0,(prog-0.2)*2));
      drawText('Two things. One jar. Zero passwords.', cy + jarH + 90, 11, '#475569', Math.max(0,(prog-0.5)*2));

    } else {
      // Phase 4: Fade out
      const prog = (t-5200)/800;
      ctx.globalAlpha = 1 - ease(Math.min(prog, 1));
      drawJar(1, 1);
      drawText('CAPTURED', cy + jarH + 50, 16, '#daa520', 1);
      ctx.globalAlpha = 1;
    }

    if(t < TOTAL){
      requestAnimationFrame(frame);
    } else {
      overlay.style.display = 'none';
      if(onComplete) onComplete();
    }
  }

  requestAnimationFrame(frame);
}

function playAngelCutscene(onComplete){
  const overlay = document.getElementById('angel-cutscene');
  const canvas = document.getElementById('angel-canvas');
  overlay.style.display = 'flex';
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const bottleY = cy + 80;
  const bottleX = cx;
  const bottleW = 60;
  const bottleH = 100;

  // Angel starts from top
  let angelX = cx;
  let angelY = -60;
  let angelTargetY = bottleY - bottleH/2 - 10;
  let phase = 0; // 0=descend, 1=enter, 2=glow, 3=fadeout
  let t = 0;
  let alpha = 1;
  let glowRadius = 0;
  let wingSpread = 1;
  let angelScale = 1;
  let particles = [];

  // Create soul particles
  for(let i=0;i<30;i++){
    particles.push({
      x: cx + (Math.random()-0.5)*300,
      y: Math.random()*canvas.height,
      r: Math.random()*2+0.5,
      speed: Math.random()*0.5+0.2,
      alpha: Math.random()*0.3+0.1
    });
  }

  function drawBottle(glow){
    // Glass bottle shape
    ctx.save();
    ctx.translate(bottleX, bottleY);
    // Body
    ctx.beginPath();
    ctx.moveTo(-bottleW/2, 0);
    ctx.lineTo(-bottleW/2, -bottleH*0.6);
    ctx.quadraticCurveTo(-bottleW/2, -bottleH*0.75, -bottleW/4, -bottleH*0.8);
    ctx.lineTo(-bottleW/4, -bottleH);
    ctx.lineTo(bottleW/4, -bottleH);
    ctx.lineTo(bottleW/4, -bottleH*0.8);
    ctx.quadraticCurveTo(bottleW/2, -bottleH*0.75, bottleW/2, -bottleH*0.6);
    ctx.lineTo(bottleW/2, 0);
    ctx.closePath();
    ctx.strokeStyle = 'rgba(218,165,32,'+(0.4+glow*0.6)+')';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    if(glow > 0){
      ctx.fillStyle = 'rgba(218,165,32,'+glow*0.15+')';
      ctx.fill();
    }
    ctx.restore();
  }

  function drawAngel(x, y, scale, wings){
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);
    // Glow
    const grad = ctx.createRadialGradient(0, 0, 0, 0, 0, 40);
    grad.addColorStop(0, 'rgba(255,255,255,0.3)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(-40,-40,80,80);
    // Body — simple luminous form
    ctx.beginPath();
    ctx.arc(0, -8, 6, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.fill();
    // Wings
    ctx.beginPath();
    ctx.moveTo(0, -4);
    ctx.quadraticCurveTo(-20*wings, -25*wings, -30*wings, -5);
    ctx.quadraticCurveTo(-15*wings, -8, 0, 0);
    ctx.fillStyle = 'rgba(255,255,255,0.25)';
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(0, -4);
    ctx.quadraticCurveTo(20*wings, -25*wings, 30*wings, -5);
    ctx.quadraticCurveTo(15*wings, -8, 0, 0);
    ctx.fill();
    // Trailing light
    ctx.beginPath();
    ctx.moveTo(-4, 4);
    ctx.lineTo(0, 20);
    ctx.lineTo(4, 4);
    ctx.fillStyle = 'rgba(218,165,32,0.3)';
    ctx.fill();
    ctx.restore();
  }

  function drawText(text, y, size, color, a){
    ctx.save();
    ctx.globalAlpha = a;
    ctx.font = size+'px "Segoe UI", system-ui, sans-serif';
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.fillText(text, cx, y);
    ctx.restore();
  }

  let startTime = performance.now();
  const TOTAL_DURATION = 5000; // 5 seconds total

  function frame(now){
    t = now - startTime;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Background particles
    particles.forEach(p => {
      p.y -= p.speed;
      if(p.y < -10) p.y = canvas.height + 10;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fillStyle = 'rgba(218,165,32,'+p.alpha+')';
      ctx.fill();
    });

    // Phase timing
    if(t < 1500){
      // Phase 0: Angel descends
      const prog = t / 1500;
      angelY = -60 + (angelTargetY + 60) * easeInOut(prog);
      wingSpread = 1 + Math.sin(t*0.008)*0.15;
      drawBottle(0);
      drawAngel(angelX, angelY, 1, wingSpread);
      drawText('THE OBSERVER', cy - canvas.height*0.35, 14, '#daa520', Math.min(prog*2, 1));
      drawText('Your consciousness entering its digital vessel', cy - canvas.height*0.35 + 22, 11, '#475569', Math.max(0, (prog-0.3)*1.5));
    } else if(t < 2800){
      // Phase 1: Angel shrinks and enters bottle
      const prog = (t - 1500) / 1300;
      angelScale = 1 - prog*0.85;
      angelY = angelTargetY + prog * (bottleH*0.3);
      wingSpread = (1 - prog*0.7) + Math.sin(t*0.008)*0.1*(1-prog);
      drawBottle(prog*0.5);
      if(angelScale > 0.05) drawAngel(angelX, angelY, angelScale, wingSpread);
      drawText('THE OBSERVER', cy - canvas.height*0.35, 14, '#daa520', 1);
      drawText('Your consciousness entering its digital vessel', cy - canvas.height*0.35 + 22, 11, '#475569', 1);
    } else if(t < 4200){
      // Phase 2: Bottle glows — soul captured
      const prog = (t - 2800) / 1400;
      glowRadius = prog;
      drawBottle(0.5 + prog*0.5);
      // Inner glow burst
      const grad = ctx.createRadialGradient(bottleX, bottleY-bottleH*0.4, 0, bottleX, bottleY-bottleH*0.4, 50+prog*60);
      grad.addColorStop(0, 'rgba(218,165,32,'+(0.4*prog)+')');
      grad.addColorStop(1, 'rgba(218,165,32,0)');
      ctx.fillStyle = grad;
      ctx.fillRect(bottleX-120, bottleY-bottleH-60, 240, bottleH+120);
      drawText('SOUL CAPTURED', cy + bottleH + 30, 16, '#daa520', Math.min(prog*3, 1));
      drawText('No password. No email. No name.', cy + bottleH + 52, 11, '#22c55e', Math.max(0,(prog-0.3)*2));
      drawText('Just the shape of who you are.', cy + bottleH + 68, 11, '#475569', Math.max(0,(prog-0.5)*2));
    } else {
      // Phase 3: Fade out
      const prog = (t - 4200) / 800;
      alpha = 1 - easeInOut(prog);
      ctx.globalAlpha = alpha;
      drawBottle(1);
      drawText('SOUL CAPTURED', cy + bottleH + 30, 16, '#daa520', 1);
      ctx.globalAlpha = 1;
    }

    if(t < TOTAL_DURATION){
      requestAnimationFrame(frame);
    } else {
      overlay.style.display = 'none';
      if(onComplete) onComplete();
    }
  }

  function easeInOut(t){ return t<0.5 ? 2*t*t : -1+(4-2*t)*t; }

  requestAnimationFrame(frame);
}

</script>
</body>
</html>
