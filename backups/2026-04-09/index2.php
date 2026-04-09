<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>GPU SWARM — ShortFactory</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#050510;color:#fff;font-family:'Segoe UI',Arial,sans-serif;overflow-x:hidden;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;}

/* ─── Background ─── */
.bg-ring{position:fixed;border-radius:50%;border:1px solid rgba(118,185,0,0.06);pointer-events:none;}
.bg-ring:nth-child(1){width:600px;height:600px;top:50%;left:50%;transform:translate(-50%,-50%);animation:ringPulse 6s ease infinite;}
.bg-ring:nth-child(2){width:900px;height:900px;top:50%;left:50%;transform:translate(-50%,-50%);animation:ringPulse 8s ease 1s infinite;}
.bg-ring:nth-child(3){width:1200px;height:1200px;top:50%;left:50%;transform:translate(-50%,-50%);animation:ringPulse 10s ease 2s infinite;}
@keyframes ringPulse{0%{opacity:.3;transform:translate(-50%,-50%) scale(1);}100%{opacity:0;transform:translate(-50%,-50%) scale(1.3);}}
.grid-overlay{position:fixed;inset:0;background-image:linear-gradient(rgba(118,185,0,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(118,185,0,0.03) 1px,transparent 1px);background-size:60px 60px;pointer-events:none;z-index:0;}

/* ─── Main card ─── */
.gate-card{position:relative;z-index:1;width:90%;max-width:420px;background:rgba(20,20,40,0.92);border:1px solid #1a1a2e;border-radius:16px;padding:32px 28px;text-align:center;animation:cardIn .6s ease;backdrop-filter:blur(20px);}
@keyframes cardIn{from{opacity:0;transform:scale(0.95) translateY(20px);}to{opacity:1;transform:scale(1) translateY(0);}}

.nvidia-img{width:180px;margin:0 auto 16px;display:block;border-radius:8px;filter:drop-shadow(0 0 30px rgba(118,185,0,0.3));}

h1{font-family:Orbitron,monospace;font-size:clamp(22px,5vw,36px);font-weight:900;letter-spacing:4px;color:#76b900;text-shadow:0 0 40px rgba(118,185,0,0.3);margin-bottom:6px;}
.subtitle{font-family:'Courier New',monospace;font-size:12px;color:#444;letter-spacing:2px;margin-bottom:20px;}

/* ─── Method panels ─── */
.method-panel{display:none;animation:panelIn .3s ease;}
.method-panel.active{display:block;}
@keyframes panelIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}

.method-panel input{width:100%;padding:12px;background:rgba(0,0,0,0.5);border:1px solid #1a1a2e;border-radius:8px;color:#fff;font-family:'Courier New',monospace;font-size:13px;outline:none;margin-bottom:8px;text-align:center;transition:border-color .3s;}
.method-panel input:focus{border-color:#76b900;box-shadow:0 0 12px rgba(118,185,0,0.15);}

.gate-btn{display:block;width:100%;padding:14px;border:none;border-radius:8px;font-family:Orbitron,monospace;font-size:11px;font-weight:900;letter-spacing:2px;cursor:pointer;transition:transform .15s,box-shadow .15s;margin-bottom:6px;}
.gate-btn:hover{transform:scale(1.02);box-shadow:0 4px 20px rgba(0,0,0,0.4);}

/* ─── Method switcher tabs ─── */
.method-tabs{display:flex;justify-content:center;gap:8px;margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.04);}
.method-tab{width:42px;height:42px;border-radius:10px;border:1px solid #1a1a2e;background:rgba(0,0,0,0.3);cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;transition:all .2s;position:relative;}
.method-tab:hover{border-color:#333;background:rgba(255,255,255,0.04);}
.method-tab.active{border-color:#76b900;background:rgba(118,185,0,0.08);box-shadow:0 0 12px rgba(118,185,0,0.15);}
.method-tab .tab-label{position:absolute;bottom:-18px;font-family:'Courier New',monospace;font-size:8px;color:#444;letter-spacing:1px;white-space:nowrap;opacity:0;transition:opacity .2s;}
.method-tab:hover .tab-label,.method-tab.active .tab-label{opacity:1;}

/* ─── Eye toggle ─── */
.eye-toggle{position:absolute;right:6px;top:50%;transform:translateY(-50%);background:none;border:none;color:#555;font-size:14px;cursor:pointer;padding:2px 4px;width:auto;}

/* ─── Status ─── */
#gate-msg{font-family:'Courier New',monospace;font-size:12px;color:#555;min-height:18px;margin-top:12px;}

/* ─── Satoshi visual ─── */
#gate-satoshi-wrap{display:none;margin:12px auto 0;animation:panelIn .5s ease;}

/* ─── Mine timer ─── */
#gpu-mine-timer{font-family:Orbitron,monospace;font-size:16px;color:#00ccff;margin-bottom:10px;display:none;}

/* ─── Product carousel (phone frame) ─── */
.phone-frame{position:relative;width:100%;max-width:280px;margin:0 auto;background:#0a0a14;border:2px solid #222;border-radius:24px;padding:12px;overflow:hidden;}
.phone-notch{width:60px;height:6px;background:#1a1a2e;border-radius:3px;margin:0 auto 10px;}
.phone-home{width:36px;height:4px;background:#1a1a2e;border-radius:2px;margin:10px auto 0;}
.product-slide{text-align:center;padding:8px 4px;animation:panelIn .3s ease;}
.product-icon{font-size:40px;margin-bottom:8px;}
.product-name{font-family:Orbitron,monospace;font-size:11px;font-weight:900;letter-spacing:2px;color:#fff;margin-bottom:4px;}
.product-desc{font-family:'Courier New',monospace;font-size:10px;color:#555;line-height:1.6;margin-bottom:8px;min-height:32px;}
.product-price{font-family:Orbitron,monospace;font-size:16px;font-weight:900;color:#76b900;margin-bottom:10px;}
.product-price small{font-size:9px;color:#444;font-weight:400;letter-spacing:1px;}
.product-buy{display:block;width:100%;padding:11px;border:none;border-radius:8px;font-family:Orbitron,monospace;font-size:10px;font-weight:900;letter-spacing:2px;cursor:pointer;color:#000;background:linear-gradient(135deg,#76b900,#8ec919);transition:transform .15s;}
.product-buy:hover{transform:scale(1.03);}
.carousel-nav{display:flex;justify-content:space-between;align-items:center;margin-top:6px;padding:0 4px;}
.carousel-nav button{background:none;border:1px solid #1a1a2e;color:#444;width:30px;height:30px;border-radius:50%;cursor:pointer;font-size:12px;display:flex;align-items:center;justify-content:center;transition:all .2s;}
.carousel-nav button:hover{border-color:#76b900;color:#76b900;}
.carousel-dots{font-family:'Courier New',monospace;font-size:9px;color:#333;}
.carousel-cat{font-family:Orbitron,monospace;font-size:7px;letter-spacing:2px;color:#333;margin-bottom:6px;text-transform:uppercase;}

/* ─── Rank peek ─── */
.rank-peek{margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.03);}
.rank-peek-title{font-family:Orbitron,monospace;font-size:8px;letter-spacing:3px;color:#333;margin-bottom:8px;}
.rank-row{display:flex;align-items:center;gap:10px;padding:3px 0;}
.rank-name{font-family:Orbitron,monospace;font-size:8px;font-weight:900;letter-spacing:1px;min-width:70px;}
.rank-unlock{font-family:'Courier New',monospace;font-size:10px;color:#444;}
.rank-unlock b{color:#888;font-weight:normal;}

/* ─── Pitch link ─── */
.pitch-link{display:inline-block;margin-top:14px;font-family:'Courier New',monospace;font-size:11px;color:#333;cursor:pointer;transition:color .2s;text-decoration:none;}
.pitch-link:hover{color:#76b900;}

/* ─── Footer ─── */
.gate-footer{position:relative;z-index:1;text-align:center;padding:24px;font-family:'Courier New',monospace;font-size:10px;color:#1a1a2e;}
.gate-footer a{color:#222;text-decoration:none;transition:color .2s;}
.gate-footer a:hover{color:#76b900;}

/* ─── Onboarding overlay ─── */
#onboarding-overlay{display:none;position:fixed;inset:0;z-index:100;background:#050510;flex-direction:column;align-items:center;justify-content:center;}
#onboarding-overlay .ob-scene{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .8s ease;padding:40px;}
#onboarding-overlay .ob-scene.active{opacity:1;pointer-events:auto;}
#onboarding-overlay .ob-scene h2{font-family:Orbitron,monospace;font-size:clamp(22px,5vw,48px);font-weight:900;letter-spacing:4px;margin-bottom:16px;text-align:center;}
#onboarding-overlay .ob-scene p{font-family:'Courier New',monospace;font-size:clamp(12px,2.5vw,16px);color:#999;line-height:2;text-align:center;max-width:700px;}
.ob-cards{display:flex;gap:16px;margin-top:24px;flex-wrap:wrap;justify-content:center;}
.ob-card{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:24px;text-align:center;width:200px;}
.ob-progress{position:fixed;bottom:0;left:0;height:3px;background:linear-gradient(90deg,#76b900,#00ccff);transition:width .4s ease;z-index:101;}
.ob-counter{position:fixed;top:20px;right:24px;font-family:Orbitron,monospace;font-size:11px;color:#333;letter-spacing:2px;z-index:101;}
.ob-close{position:fixed;top:20px;left:24px;background:none;border:1px solid #222;color:#555;font-family:Orbitron,monospace;font-size:10px;padding:8px 16px;border-radius:6px;cursor:pointer;letter-spacing:2px;z-index:101;transition:all .2s;}
.ob-close:hover{border-color:#76b900;color:#76b900;}
.ob-nav{position:fixed;bottom:20px;right:24px;display:flex;gap:8px;z-index:101;}
.ob-nav button{background:none;border:1px solid #222;color:#444;font-family:monospace;font-size:14px;padding:6px 12px;border-radius:50%;cursor:pointer;width:36px;height:36px;display:flex;align-items:center;justify-content:center;transition:all .2s;}
.ob-nav button:hover{border-color:#76b900;color:#76b900;}
.ob-mute{position:fixed;bottom:20px;left:24px;background:none;border:1px solid #222;color:#444;font-family:monospace;font-size:16px;padding:6px 12px;border-radius:50%;cursor:pointer;width:36px;height:36px;display:flex;align-items:center;justify-content:center;z-index:101;transition:all .2s;}
.ob-mute:hover{border-color:#76b900;color:#76b900;}
@keyframes obFadeUp{from{opacity:0;transform:translateY(30px);}to{opacity:1;transform:translateY(0);}}
@keyframes obSlideRight{from{opacity:0;transform:translateX(-60px);}to{opacity:1;transform:translateX(0);}}
@keyframes obBurst{0%{transform:scale(0.5);opacity:0;}50%{transform:scale(1.1);}100%{transform:scale(1);opacity:1;}}
@keyframes obCount{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
</style>
</head>
<body>

<!-- Background -->
<div class="bg-ring"></div>
<div class="bg-ring"></div>
<div class="bg-ring"></div>
<div class="grid-overlay"></div>

<!-- MAIN CARD -->
<div class="gate-card">
  <img src="/nvidia/nvidiasmall.jpg" alt="NVIDIA" class="nvidia-img">
  <h1>GPU SWARM</h1>
  <div class="subtitle">DECENTRALISED COMPUTE NETWORK</div>

  <!-- METHOD 1: GOOGLE (default) -->
  <div class="method-panel active" id="panel-google">
    <div id="google-btn-wrap" style="display:flex;justify-content:center;min-height:44px;margin-bottom:10px;"></div>
    <div style="font-family:'Courier New',monospace;font-size:10px;color:#333;">Any Google account. One tap access.</div>
  </div>

  <!-- METHOD 2: SOUL TOKEN -->
  <div class="method-panel" id="panel-token">
    <div style="font-size:11px;color:#666;font-family:'Courier New',monospace;margin-bottom:12px;line-height:1.8;">
      Your <strong style="color:#76b900;">Soul Token</strong> is an anonymous encrypted file that belongs to <strong style="color:#76b900;">you</strong>.<br>
      Keep it safe. It pairs with your secure data via the Satoshi encryption system.<br>
      <span style="color:#444;">Invisible to quantum AI. Dan's thought of everything.</span>
    </div>
    <input id="gate-token-input" type="text" placeholder="Paste your soul token...">
    <button onclick="unlockWithToken()" class="gate-btn" style="background:linear-gradient(135deg,#76b900,#8ec919);color:#000;">UNLOCK</button>
  </div>

  <!-- METHOD 3: API VAULT -->
  <div class="method-panel" id="panel-api">
    <div style="font-size:11px;color:#555;font-family:'Courier New',monospace;margin-bottom:10px;">Feed us an API key. We encrypt it with Satoshi cipher. You get credits.</div>
    <input id="gate-api-label" type="text" placeholder="Label (e.g. Grok, OpenAI...)">
    <div style="position:relative;">
      <input id="gate-api-key" type="password" placeholder="sk-..." style="padding-right:36px;">
      <button class="eye-toggle" onclick="var k=document.getElementById('gate-api-key');k.type=k.type==='password'?'text':'password';this.textContent=k.type==='password'?'\u{1F441}':'\u{1F648}';">&#x1F441;</button>
    </div>
    <button onclick="unlockWithApi()" class="gate-btn" style="background:linear-gradient(135deg,#daa520,#ff8c00);color:#000;">ENCRYPT &amp; PAY</button>
    <div id="gate-satoshi-wrap">
      <canvas id="gate-satoshi-canvas" width="200" height="200" style="border-radius:12px;border:1px solid #1a1a2e;"></canvas>
      <div style="font-family:'Courier New',monospace;font-size:9px;color:#76b900;margin-top:4px;">Your key as a shape — Satoshi encrypted</div>
    </div>
  </div>

  <!-- METHOD 4: GPU MINING -->
  <div class="method-panel" id="panel-mine">
    <div style="font-size:11px;color:#555;font-family:'Courier New',monospace;margin-bottom:10px;">Give us 10 minutes of GPU time. The swarm does the rest.</div>
    <div id="gpu-mine-timer"></div>
    <button onclick="startGpuMine()" id="gate-mine-btn" class="gate-btn" style="background:linear-gradient(135deg,#00ccff,#0088cc);color:#000;">MINE NOW</button>
  </div>

  <!-- METHOD 5: SHOP -->
  <div class="method-panel" id="panel-pay">
    <div class="phone-frame">
      <div class="phone-notch"></div>
      <div class="carousel-cat" id="shop-cat">DIGITAL</div>
      <div class="product-slide" id="product-slide"></div>
      <div class="carousel-nav">
        <button onclick="shopPrev()">&#x276E;</button>
        <span class="carousel-dots" id="shop-dots">1 / 30</span>
        <button onclick="shopNext()">&#x276F;</button>
      </div>
      <div class="phone-home"></div>
    </div>
    <div style="font-family:'Courier New',monospace;font-size:9px;color:#333;margin-top:8px;">Buy any product. Instant access + credits.</div>
  </div>

  <!-- Status -->
  <div id="gate-msg"></div>

  <!-- METHOD TABS -->
  <div class="method-tabs">
    <div class="method-tab active" onclick="switchMethod('google')" id="tab-google" title="Google">
      <span style="font-size:16px;">G</span>
      <span class="tab-label">GOOGLE</span>
    </div>
    <div class="method-tab" onclick="switchMethod('token')" id="tab-token" title="Soul Token">
      &#x1F511;
      <span class="tab-label">TOKEN</span>
    </div>
    <div class="method-tab" onclick="switchMethod('api')" id="tab-api" title="API Vault">
      &#x1F512;
      <span class="tab-label">VAULT</span>
    </div>
    <div class="method-tab" onclick="switchMethod('mine')" id="tab-mine" title="GPU Mining">
      &#x26A1;
      <span class="tab-label">MINE</span>
    </div>
    <div class="method-tab" onclick="switchMethod('pay')" id="tab-pay" title="Shop">
      &#x1F6D2;
      <span class="tab-label">SHOP</span>
    </div>
  </div>

  <!-- Rank peek -->
  <div class="rank-peek">
    <div class="rank-peek-title">MERIT RANKS</div>
    <div class="rank-row"><span class="rank-name" style="color:#888;">PRIVATE</span><span class="rank-unlock">Hub + <b>full colour</b></span></div>
    <div class="rank-row"><span class="rank-name" style="color:#daa520;">CORPORAL</span><span class="rank-unlock"><b>Cortex chat</b> + exclusive</span></div>
    <div class="rank-row"><span class="rank-name" style="color:#22c55e;">SERGEANT</span><span class="rank-unlock"><b>Your own AI site</b></span></div>
    <div class="rank-row"><span class="rank-name" style="color:#00ccff;">VETERAN</span><span class="rank-unlock"><b>Custom domain</b> + priority</span></div>
    <div class="rank-row"><span class="rank-name" style="color:#8844ff;">COMMANDER</span><span class="rank-unlock"><b>AI auto-email</b> + GPU alloc</span></div>
    <div class="rank-row"><span class="rank-name" style="color:#ff4444;">LEGENDARY</span><span class="rank-unlock"><b>PPV</b> + Monero payouts</span></div>
    <div class="rank-row"><span class="rank-name" style="color:#ff0040;">GIGACHAD</span><span class="rank-unlock"><b>Arena booking</b> — main event</span></div>
  </div>

  <a class="pitch-link" onclick="showOnboardingVid()">&#9654; HOW IT WORKS</a>
</div>

<div class="gate-footer">
  Your GPU. Your credits. No middleman.<br>
  <a href="/">SHORTFACTORY.SHOP</a>
</div>

<!-- ONBOARDING VIDEO — 8 scenes with voice narration -->
<div id="onboarding-overlay">
  <button class="ob-close" onclick="closeOnboardingVid()">CLOSE</button>
  <div class="ob-counter" id="ob-counter">1 / 8</div>
  <div class="ob-nav">
    <button onclick="obPrev()" title="Previous">&#x276E;</button>
    <button onclick="obTogglePause()" id="ob-pause" title="Pause">&#10074;&#10074;</button>
    <button onclick="obNext()" title="Next">&#x276F;</button>
  </div>
  <button class="ob-mute" id="ob-mute" onclick="obToggleMute()" title="Mute voice">&#x1F50A;</button>
  <div class="ob-progress" id="ob-progress" style="width:0%;"></div>

  <div class="ob-scene" id="ob-scene-1">
    <img src="/nvidia/nvidiasmall.jpg" alt="NVIDIA" style="width:140px;border-radius:8px;filter:drop-shadow(0 0 40px rgba(118,185,0,0.5));margin-bottom:20px;animation:obFadeUp .8s ease both;">
    <h2 style="color:#76b900;animation:obFadeUp .8s ease .3s both;">THE SWARM</h2>
    <p style="animation:obFadeUp .8s ease .6s both;color:#666;font-size:clamp(14px,3vw,20px);">HOW WE MINE THE SHIT OUT OF YOU</p>
    <p style="animation:obFadeUp .8s ease .9s both;color:#333;font-size:clamp(10px,2vw,13px);margin-top:8px;">And why you'll thank us for it</p>
  </div>

  <div class="ob-scene" id="ob-scene-2">
    <h2 style="color:#ff4444;animation:obFadeUp .6s ease both;">THE PROBLEM</h2>
    <div style="margin-top:20px;text-align:left;max-width:600px;">
      <p style="animation:obSlideRight .6s ease .3s both;color:#888;">Your GPU sits idle <strong style="color:#ff4444;">90% of the time.</strong></p>
      <p style="animation:obSlideRight .6s ease .6s both;color:#888;margin-top:12px;">NVIDIA made <strong style="color:#ff4444;">$60 billion</strong> last year.</p>
      <p style="animation:obSlideRight .6s ease .9s both;color:#888;margin-top:12px;">You made <strong style="color:#ff4444;">nothing.</strong></p>
      <p style="animation:obSlideRight .6s ease 1.2s both;color:#ff4444;margin-top:20px;font-size:clamp(14px,3vw,20px);font-family:Orbitron,monospace;letter-spacing:2px;">YOUR HARDWARE. THEIR PROFIT.</p>
    </div>
  </div>

  <div class="ob-scene" id="ob-scene-3">
    <p style="animation:obFadeUp .6s ease both;color:#666;">What if your idle GPU...</p>
    <h2 style="color:#76b900;animation:obBurst .8s ease .5s both;margin-top:12px;">WORKED FOR YOU?</h2>
    <p style="animation:obFadeUp .6s ease 1s both;color:#76b900;margin-top:20px;font-size:clamp(12px,2.5vw,16px);">Decentralised compute. <strong>YOUR GPU. YOUR CREDITS.</strong></p>
    <div style="animation:obFadeUp .8s ease 1.4s both;display:flex;gap:24px;margin-top:30px;justify-content:center;">
      <div style="text-align:center;"><div style="font-size:28px;">&#x1F4BB;</div><div style="font-family:Orbitron,monospace;font-size:8px;color:#76b900;letter-spacing:1px;margin-top:4px;">YOUR GPU</div></div>
      <div style="color:#76b900;font-size:24px;line-height:40px;">&#x2192;</div>
      <div style="text-align:center;"><div style="font-size:28px;">&#x1F310;</div><div style="font-family:Orbitron,monospace;font-size:8px;color:#00ccff;letter-spacing:1px;margin-top:4px;">SWARM</div></div>
      <div style="color:#daa520;font-size:24px;line-height:40px;">&#x2192;</div>
      <div style="text-align:center;"><div style="font-size:28px;">&#x1F4B0;</div><div style="font-family:Orbitron,monospace;font-size:8px;color:#daa520;letter-spacing:1px;margin-top:4px;">CREDITS</div></div>
    </div>
  </div>

  <div class="ob-scene" id="ob-scene-4">
    <h2 style="color:#00ccff;animation:obFadeUp .6s ease both;">HOW IT WORKS</h2>
    <div class="ob-cards">
      <div class="ob-card" style="animation:obSlideRight .5s ease .3s both;border-color:rgba(118,185,0,0.2);">
        <div style="font-size:32px;margin-bottom:8px;">&#x1F5A5;</div>
        <div style="font-family:Orbitron,monospace;font-size:9px;color:#76b900;letter-spacing:1px;margin-bottom:6px;">STEP 1</div>
        <div style="font-family:'Courier New',monospace;font-size:12px;color:#ccc;">Your GPU joins a<br>compute mesh</div>
      </div>
      <div class="ob-card" style="animation:obSlideRight .5s ease .6s both;border-color:rgba(0,204,255,0.2);">
        <div style="font-size:32px;margin-bottom:8px;">&#x1F3A8;</div>
        <div style="font-family:Orbitron,monospace;font-size:9px;color:#00ccff;letter-spacing:1px;margin-bottom:6px;">STEP 2</div>
        <div style="font-family:'Courier New',monospace;font-size:12px;color:#ccc;">Art &amp; games generated<br>from GPU power</div>
      </div>
      <div class="ob-card" style="animation:obSlideRight .5s ease .9s both;border-color:rgba(218,165,32,0.2);">
        <div style="font-size:32px;margin-bottom:8px;">&#x1F4B8;</div>
        <div style="font-family:Orbitron,monospace;font-size:9px;color:#daa520;letter-spacing:1px;margin-bottom:6px;">STEP 3</div>
        <div style="font-family:'Courier New',monospace;font-size:12px;color:#ccc;">Content sells.<br>You get paid.</div>
      </div>
    </div>
  </div>

  <div class="ob-scene" id="ob-scene-5">
    <h2 style="color:#ff4444;animation:obFadeUp .6s ease both;">THE ENTERTAINMENT</h2>
    <div style="margin-top:16px;max-width:650px;">
      <p style="animation:obSlideRight .5s ease .3s both;color:#ccc;font-size:clamp(13px,2.5vw,17px);">Games. Dares. Fight Club. AI Art.</p>
      <p style="animation:obSlideRight .5s ease .6s both;color:#ff8c00;font-size:clamp(12px,2.2vw,15px);margin-top:12px;">Content that platforms are too scared to host.</p>
      <p style="animation:obSlideRight .5s ease .9s both;color:#ff4444;font-size:clamp(11px,2vw,14px);margin-top:12px;">They can't ban you from saying it — just to sell you it as entertainment.</p>
      <p style="animation:obBurst .8s ease 1.2s both;color:#ff0040;font-family:Orbitron,monospace;font-size:clamp(14px,3.5vw,24px);letter-spacing:3px;margin-top:24px;">GET FUCKED. WE'RE BUILDING IT OURSELVES.</p>
      <p style="animation:obFadeUp .6s ease 1.8s both;color:#daa520;font-family:Orbitron,monospace;font-size:clamp(10px,2vw,14px);letter-spacing:2px;margin-top:12px;">GAMERGATE 3. THIS IS SPARTA.</p>
    </div>
  </div>

  <div class="ob-scene" id="ob-scene-6">
    <h2 style="color:#daa520;animation:obFadeUp .6s ease both;">IT'S ALREADY LIVE</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:24px;max-width:500px;">
      <div style="text-align:center;animation:obCount .5s ease .3s both;"><div style="font-family:Orbitron,monospace;font-size:clamp(28px,6vw,48px);color:#76b900;font-weight:900;" class="ob-stat" data-target="20">0</div><div style="font-family:'Courier New',monospace;font-size:11px;color:#555;">PRODUCTS BUILT</div></div>
      <div style="text-align:center;animation:obCount .5s ease .5s both;"><div style="font-family:Orbitron,monospace;font-size:clamp(28px,6vw,48px);color:#daa520;font-weight:900;" class="ob-stat" data-target="1">0</div><div style="font-family:'Courier New',monospace;font-size:11px;color:#555;">MAN ARMY</div></div>
      <div style="text-align:center;animation:obCount .5s ease .7s both;"><div style="font-family:Orbitron,monospace;font-size:clamp(28px,6vw,48px);color:#ff4444;font-weight:900;" class="ob-stat" data-target="0">0</div><div style="font-family:'Courier New',monospace;font-size:11px;color:#555;">VC DOLLARS</div></div>
      <div style="text-align:center;animation:obCount .5s ease .9s both;"><div style="font-family:Orbitron,monospace;font-size:clamp(28px,6vw,48px);color:#00ccff;font-weight:900;" class="ob-stat" data-target="100">0</div><div style="font-family:'Courier New',monospace;font-size:11px;color:#555;">% COMMUNITY</div></div>
    </div>
    <p style="animation:obFadeUp .6s ease 1.2s both;color:#555;margin-top:24px;font-size:12px;">Check the ShortFactory YouTube if you don't believe us.</p>
  </div>

  <div class="ob-scene" id="ob-scene-7">
    <h2 style="color:#cc44ff;animation:obFadeUp .6s ease both;">FOR THE PEOPLE</h2>
    <div style="margin-top:20px;max-width:600px;">
      <p style="animation:obFadeUp .5s ease .3s both;color:#ccc;">One human. AI-powered. No corporation.</p>
      <p style="animation:obFadeUp .5s ease .6s both;color:#999;margin-top:12px;">Dan's trying to make you hamsters relevant and powerful.</p>
      <p style="animation:obFadeUp .5s ease .9s both;color:#999;margin-top:12px;">While others sell you their AI slop — <strong style="color:#cc44ff;">we dictate the entertainment.</strong></p>
      <p style="animation:obFadeUp .5s ease 1.2s both;color:#daa520;margin-top:20px;font-family:Orbitron,monospace;font-size:clamp(11px,2.5vw,15px);letter-spacing:2px;">THE EARLIER YOU JOIN, THE MORE YOU SHAPE.</p>
    </div>
  </div>

  <div class="ob-scene" id="ob-scene-8">
    <h2 style="color:#76b900;animation:obBurst .8s ease both;font-size:clamp(28px,7vw,56px);">MINE. EARN. OWN.</h2>
    <p style="animation:obFadeUp .5s ease .5s both;color:#555;margin-top:8px;">Pick your weapon. Enter the swarm.</p>
    <div style="display:flex;gap:12px;margin-top:30px;flex-wrap:wrap;justify-content:center;">
      <button onclick="obCtaMine()" class="gate-btn" style="animation:obFadeUp .5s ease .7s both;width:auto;padding:14px 28px;background:linear-gradient(135deg,#76b900,#8ec919);color:#000;">MINE NOW</button>
      <button onclick="obCtaCrypto()" class="gate-btn" style="animation:obFadeUp .5s ease .9s both;width:auto;padding:14px 28px;background:linear-gradient(135deg,#daa520,#ff8c00);color:#000;">PAY CRYPTO</button>
      <button onclick="obCtaToken()" class="gate-btn" style="animation:obFadeUp .5s ease 1.1s both;width:auto;padding:14px 28px;background:none;border:1px solid #333;color:#fff;">ENTER TOKEN</button>
    </div>
    <div style="animation:obFadeUp .5s ease 1.5s both;margin-top:24px;font-family:Orbitron,monospace;font-size:9px;color:#333;letter-spacing:3px;">THE SWARM IS WAITING</div>
  </div>
</div>

<script>
// ─── METHOD SWITCHER ──────────────────────────────────────────────
var methods=['google','token','api','mine','pay'];
function switchMethod(m){
  methods.forEach(function(id){
    var panel=document.getElementById('panel-'+id);
    var tab=document.getElementById('tab-'+id);
    if(panel) panel.classList.remove('active');
    if(tab) tab.classList.remove('active');
  });
  var panel=document.getElementById('panel-'+m);
  var tab=document.getElementById('tab-'+m);
  if(panel) panel.classList.add('active');
  if(tab) tab.classList.add('active');
}

// ─── GOOGLE SIGN-IN (native ID button — no popup, no COOP issues) ─
var G_CLIENT_ID='246057462897-mui96hjeuk9abvlkgvvqdfdeiknbmojb.apps.googleusercontent.com';

function initGoogleBtn(){
  if(!window.google||!google.accounts||!google.accounts.id) return;
  google.accounts.id.initialize({
    client_id:G_CLIENT_ID,
    callback:handleGoogleCredential,
    auto_select:true
  });
  var wrap=document.getElementById('google-btn-wrap');
  if(wrap){
    google.accounts.id.renderButton(wrap,{
      type:'standard',
      theme:'filled_black',
      size:'large',
      text:'signin_with',
      shape:'pill',
      width:320
    });
  }
  // Also show One Tap prompt
  google.accounts.id.prompt();
}

function handleGoogleCredential(resp){
  if(!resp||!resp.credential){
    var msg=document.getElementById('gate-msg');
    if(msg) msg.innerHTML='<span style="color:#ff4444;">Google auth failed. Try another method.</span>';
    return;
  }
  // Decode JWT payload (base64url → JSON)
  var parts=resp.credential.split('.');
  if(parts.length<2) return;
  var payload=JSON.parse(atob(parts[1].replace(/-/g,'+').replace(/_/g,'/')));
  var user={id:payload.sub,email:payload.email,name:payload.name,picture:payload.picture};

  localStorage.setItem('sf_google_user',JSON.stringify({
    id:user.id,email:user.email,name:user.name,picture:user.picture,authed:new Date().toISOString()
  }));
  localStorage.setItem('sf_unlocked','true');
  var p=null;try{p=JSON.parse(localStorage.getItem('sc_player'));}catch(e){}
  if(!p) p={id:'g_'+user.id,credits:0,brainTasks:0,gpuSeconds:0,greenscreenSnaps:0,sessions:1,firstSeen:Date.now(),lastSeen:Date.now()};
  p.credits=(p.credits||0)+500;
  p.googleId=user.id;p.email=user.email;p.name=user.name;
  localStorage.setItem('sc_player',JSON.stringify(p));
  var msg=document.getElementById('gate-msg');
  if(msg) msg.innerHTML='<span style="color:#76b900;">WELCOME '+(user.name||user.email||'').toUpperCase()+' — +500 CREDITS</span>';
  setTimeout(function(){window.location.href='/';},2000);
}

// Load GIS and init button
(function(){
  var s=document.createElement('script');
  s.src='https://accounts.google.com/gsi/client';
  s.onload=initGoogleBtn;
  document.head.appendChild(s);
})();

// ─── SATOSHI CIPHER ───────────────────────────────────────────────
var GateCipher={MAX:95,
  cv:function(c){var k=c.charCodeAt(0);return(k<32||k>126)?-1:k-31;},
  vc:function(v){return(v<1||v>95)?'?':String.fromCharCode(v+31);},
  enc:function(t,p){if(!p||!t)return t;var s=this,pv=Array.from(p).map(function(c){var v=s.cv(c);return v<1?1:v;});return Array.from(t).map(function(c,i){var v=s.cv(c);return v<1?c:s.vc(((v-1+pv[i%pv.length])%95)+1);}).join('');},
  pts:function(t,cx,cy,r){if(!t)return[];var pts=[],len=t.length;for(var i=0;i<len;i++){var v=this.cv(t[i]);if(v<1)continue;var a=(i*2*Math.PI/len)+(v*2*Math.PI/95);var d=(v/95)*r;pts.push({x:cx+Math.cos(a)*d,y:cy+Math.sin(a)*d});}return pts;},
  draw:function(ctx,pts,color,w,h){ctx.clearRect(0,0,w,h);ctx.fillStyle='#050510';ctx.fillRect(0,0,w,h);if(pts.length<2)return;ctx.strokeStyle=color;ctx.lineWidth=2;ctx.shadowColor=color;ctx.shadowBlur=10;ctx.beginPath();ctx.moveTo(pts[0].x,pts[0].y);for(var i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y);ctx.closePath();ctx.stroke();ctx.shadowBlur=0;for(var j=0;j<pts.length;j++){ctx.fillStyle=color;ctx.beginPath();ctx.arc(pts[j].x,pts[j].y,2.5,0,Math.PI*2);ctx.fill();}}
};

function getDeviceKey(){
  var p=null;try{p=JSON.parse(localStorage.getItem('sc_player'));}catch(e){}
  if(p&&p.id) return p.id;
  var id='p_'+Math.random().toString(36).substr(2,9)+'_'+Date.now().toString(36);
  localStorage.setItem('sc_player',JSON.stringify({id:id,credits:0,brainTasks:0,gpuSeconds:0,greenscreenSnaps:0,sessions:1,firstSeen:Date.now(),lastSeen:Date.now()}));
  return id;
}

function valueApiKey(key){
  if(!key||key.length<10) return {credits:0,tier:'invalid'};
  var k=key.trim();
  if(k.indexOf('sk-ant-')===0) return {credits:2000,tier:'ANTHROPIC — HIGH VALUE'};
  if(k.indexOf('sk-')===0) return {credits:2000,tier:'OPENAI — HIGH VALUE'};
  if(k.indexOf('gsk_')===0||k.indexOf('xai-')===0) return {credits:2000,tier:'GROK — HIGH VALUE'};
  if(k.indexOf('sk')===0&&k.length>20) return {credits:1500,tier:'API — GOOD VALUE'};
  if(k.length>=20) return {credits:500,tier:'UNKNOWN API — ACCEPTED'};
  return {credits:0,tier:'invalid'};
}

// ─── UNLOCK FUNCTIONS ─────────────────────────────────────────────
function unlockWithToken(){
  var input=document.getElementById('gate-token-input');
  var msg=document.getElementById('gate-msg');
  if(!input||!input.value.trim()||input.value.trim().length<8){
    if(msg) msg.innerHTML='<span style="color:#ff4444;">Token must be 8+ characters</span>';
    return;
  }
  localStorage.setItem('sf_sft_token',input.value.trim());
  localStorage.setItem('sf_unlocked','true');
  var p=null;try{p=JSON.parse(localStorage.getItem('sc_player'));}catch(e){}
  if(p){p.credits=(p.credits||0)+1000;localStorage.setItem('sc_player',JSON.stringify(p));}
  if(msg) msg.innerHTML='<span style="color:#76b900;">SOUL TOKEN ACCEPTED — +1000 CREDITS — SITE UNLOCKED</span>';
  setTimeout(function(){window.location.href='/';},2000);
}

function unlockWithApi(){
  var labelEl=document.getElementById('gate-api-label');
  var keyEl=document.getElementById('gate-api-key');
  var msg=document.getElementById('gate-msg');
  if(!keyEl||!keyEl.value.trim()){
    if(msg) msg.innerHTML='<span style="color:#ff4444;">Enter an API key</span>';
    return;
  }
  var label=(labelEl&&labelEl.value.trim())||'API';
  var rawKey=keyEl.value.trim();
  var val=valueApiKey(rawKey);
  if(val.credits===0){
    if(msg) msg.innerHTML='<span style="color:#ff4444;">Key too short or invalid. Need 20+ chars.</span>';
    return;
  }
  var dk=getDeviceKey();
  var encrypted=GateCipher.enc(rawKey,dk);
  var vault=[];try{vault=JSON.parse(localStorage.getItem('sf_api_vault'))||[];}catch(e){}
  vault.push({id:'api_'+Date.now().toString(36),label:label,encrypted:encrypted,status:'active',created:new Date().toISOString()});
  localStorage.setItem('sf_api_vault',JSON.stringify(vault));
  var p=null;try{p=JSON.parse(localStorage.getItem('sc_player'));}catch(e){}
  if(p){p.credits=(p.credits||0)+val.credits;localStorage.setItem('sc_player',JSON.stringify(p));}
  localStorage.setItem('sf_unlocked','true');
  var wrap=document.getElementById('gate-satoshi-wrap');
  var canvas=document.getElementById('gate-satoshi-canvas');
  if(wrap&&canvas){
    wrap.style.display='block';
    var ctx=canvas.getContext('2d');
    var pts=GateCipher.pts(encrypted,100,100,80);
    var color=rawKey[0]>='A'&&rawKey[0]<='Z'?'#ff00ff':rawKey[0]>='a'&&rawKey[0]<='z'?'#00ffff':'#ffff00';
    GateCipher.draw(ctx,pts,color,200,200);
  }
  if(msg) msg.innerHTML='<span style="color:#daa520;">'+val.tier+' — +'+val.credits+' CREDITS — SITE UNLOCKED</span>';
  setTimeout(function(){window.location.href='/';},3000);
}

// ─── GPU MINING ───────────────────────────────────────────────────
var gpuMinePoller=null;
function startGpuMine(){
  var p=null;try{p=JSON.parse(localStorage.getItem('sc_player'));}catch(e){}
  var baseline=(p&&p.gpuSeconds)?p.gpuSeconds:0;
  localStorage.setItem('sf_gpu_mine_baseline',baseline.toString());
  localStorage.setItem('sf_gpu_mine_active','true');
  window.open('/screensaver/','_blank');
  var msg=document.getElementById('gate-msg');
  if(msg) msg.innerHTML='<span style="color:#00ccff;">MINING STARTED... mine 10 minutes in the screensaver tab.</span>';
  var timerEl=document.getElementById('gpu-mine-timer');
  if(timerEl) timerEl.style.display='block';
  var btn=document.getElementById('gate-mine-btn');
  if(btn){btn.textContent='MINING...';btn.style.opacity='0.5';}
  startMinePolling();
}
function startMinePolling(){
  if(gpuMinePoller) clearInterval(gpuMinePoller);
  gpuMinePoller=setInterval(function(){
    var p=null;try{p=JSON.parse(localStorage.getItem('sc_player'));}catch(e){}
    var baseline=parseInt(localStorage.getItem('sf_gpu_mine_baseline')||'0');
    var current=(p&&p.gpuSeconds)?p.gpuSeconds:0;
    var mined=current-baseline;
    var needed=600;
    var timerEl=document.getElementById('gpu-mine-timer');
    var msg=document.getElementById('gate-msg');
    if(mined>=needed){
      clearInterval(gpuMinePoller);gpuMinePoller=null;
      localStorage.setItem('sf_unlocked','true');
      localStorage.removeItem('sf_gpu_mine_active');
      localStorage.removeItem('sf_gpu_mine_baseline');
      if(p){p.credits=(p.credits||0)+2000;localStorage.setItem('sc_player',JSON.stringify(p));}
      if(timerEl) timerEl.textContent='COMPLETE';
      if(msg) msg.innerHTML='<span style="color:#76b900;">GPU MINING COMPLETE — +2000 CREDITS — SITE UNLOCKED</span>';
      setTimeout(function(){window.location.href='/';},2500);
    } else if(mined>0){
      var remaining=needed-mined;
      var mins=Math.floor(remaining/60);
      var secs=remaining%60;
      if(timerEl) timerEl.textContent=mins+'m '+Math.round(secs)+'s remaining';
      if(msg) msg.innerHTML='<span style="color:#00ccff;">Mined '+Math.round(mined)+'s / '+needed+'s</span>';
    }
  },2000);
}

// ─── PRODUCT SHOP CAROUSEL ────────────────────────────────────────
var PRODUCTS=[
  // ── DIGITAL SUBSCRIPTIONS ──
  {cat:'DIGITAL',icon:'\u{1F9EC}',name:'ALIVE PREMIUM',desc:'Your AI creature. Evolved. Full brainstem access.',price:'\u00A39.99',per:'/mo',url:'/checkout.html?p=alive',credits:2000,color:'#00ccff'},
  {cat:'DIGITAL',icon:'\u{1F3AC}',name:'IMAGINATOR PRO',desc:'Stills to YouTube Shorts. Unlimited renders.',price:'\u00A39.99',per:'/mo',url:'/checkout.html?p=imaginator',credits:2000,color:'#ff8c00'},
  {cat:'DIGITAL',icon:'\u{1F3AE}',name:'GAMING ALL-ACCESS',desc:'Every game unlocked. Leaderboards. Prizes.',price:'\u00A34.99',per:'/mo',url:'/checkout.html?p=gaming',credits:1500,color:'#ff4444'},
  {cat:'DIGITAL',icon:'\u{1F3AE}',name:'GAME MAKER',desc:'Build & publish your own games on the swarm.',price:'\u00A329',per:'/mo',url:'/checkout.html?p=gamemaker',credits:5000,color:'#cc44ff'},
  {cat:'DIGITAL',icon:'\u{1F4FA}',name:'HUB PREMIUM',desc:'30+ exclusive fight videos. New drops weekly.',price:'\u00A34.99',per:'/mo',url:'/checkout.html?p=hub',credits:1500,color:'#daa520'},
  {cat:'DIGITAL',icon:'\u{1F9E0}',name:'CORTEX API',desc:'Split-brain AI. Left angel. Right demon. Your call.',price:'\u00A329',per:'/mo',url:'/checkout.html?p=cortex',credits:5000,color:'#76b900'},
  {cat:'DIGITAL',icon:'\u26A1',name:'GPU AS A SERVICE',desc:'Swarm compute on demand. Render anything.',price:'\u00A349',per:'/mo',url:'/checkout.html?p=gpu',credits:10000,color:'#00ccff'},
  {cat:'DIGITAL',icon:'\u{1F4DD}',name:'mcFORMS PRO',desc:'Drag & drop form builder. Unlimited forms.',price:'\u00A39.99',per:'/mo',url:'/checkout.html?p=mcforms',credits:2000,color:'#22c55e'},
  {cat:'DIGITAL',icon:'\u{1F5BC}',name:'ART MEMBERSHIP',desc:'Upload & download art. Community gallery.',price:'\u00A34.99',per:'/mo',url:'/checkout.html?p=art',credits:1500,color:'#ff00ff'},
  {cat:'DIGITAL',icon:'\u{1F4F0}',name:'ADMONSTER',desc:'AI ad platform. Advertisers & users welcome.',price:'\u00A319',per:'/mo',url:'/checkout.html?p=admonster',credits:3000,color:'#ff8c00'},
  {cat:'DIGITAL',icon:'\u{1F4F9}',name:'COMICVID PRO',desc:'Video to halftone codec. IPFS publishing.',price:'\u00A39.99',per:'/mo',url:'/checkout.html?p=comicvid',credits:2000,color:'#daa520'},
  {cat:'DIGITAL',icon:'\u{1F4E6}',name:'IPFS VAULT PRO',desc:'Decentralised storage. Pin anything forever.',price:'\u00A39.99',per:'/mo',url:'/checkout.html?p=ipfs',credits:2000,color:'#00ccff'},
  {cat:'DIGITAL',icon:'\u{1F525}',name:'KINETIC PRO',desc:'Typography engine. Motion text for videos.',price:'\u00A329',per:'/mo',url:'/checkout.html?p=kinetic',credits:5000,color:'#ff4444'},
  {cat:'DIGITAL',icon:'\u{1F3B2}',name:'DARES4DOSH',desc:'Dare feed. Accept dares. Win real money.',price:'\u00A34.99',per:'/mo',url:'/checkout.html?p=dares',credits:1500,color:'#ff0040'},
  {cat:'DIGITAL',icon:'\u{1F50D}',name:'50% AI HUNTER',desc:'AI price comparison. Never overpay again.',price:'\u00A32.99',per:'/mo',url:'/checkout.html?p=50',credits:1000,color:'#22c55e'},
  // ── PHYSICAL: SHORTS ──
  {cat:'MERCH',icon:'\u{1FA73}',name:'NEON GRID SHORTS',desc:'Cyberpunk neon. Limited drop.',price:'\u00A319.99',per:'',url:'/shorts/',credits:3000,color:'#00ccff'},
  {cat:'MERCH',icon:'\u{1FA73}',name:'NEURAL CAMO SHORTS',desc:'AI-generated camo pattern.',price:'\u00A319.99',per:'',url:'/shorts/',credits:3000,color:'#76b900'},
  {cat:'MERCH',icon:'\u{1FA73}',name:'SWARM BLACK SHORTS',desc:'Murdered out. Swarm logo.',price:'\u00A319.99',per:'',url:'/shorts/',credits:3000,color:'#333'},
  {cat:'MERCH',icon:'\u{1FA73}',name:'FIRE SKULL SHORTS',desc:'Flaming skull print. Stand out.',price:'\u00A319.99',per:'',url:'/shorts/',credits:3000,color:'#ff4444'},
  {cat:'MERCH',icon:'\u{1FA73}',name:'GLITCH ART SHORTS',desc:'Databent aesthetic. Unique.',price:'\u00A319.99',per:'',url:'/shorts/',credits:3000,color:'#cc44ff'},
  {cat:'MERCH',icon:'\u{1FA73}',name:'MATRIX SHORTS',desc:'Green code rain. Classic.',price:'\u00A319.99',per:'',url:'/shorts/',credits:3000,color:'#76b900'},
  {cat:'MERCH',icon:'\u{1FA73}',name:'VAPORWAVE SHORTS',desc:'Retro gradient. Soft vibes.',price:'\u00A319.99',per:'',url:'/shorts/',credits:3000,color:'#ff00ff'},
  {cat:'MERCH',icon:'\u{1FA73}',name:'GIGACHAD SHORTS',desc:'Only for the worthy. Limited.',price:'\u00A324.99',per:'',url:'/shorts/',credits:5000,color:'#daa520'},
  // ── HARDWARE ──
  {cat:'HARDWARE',icon:'\u{1F5A5}',name:'RTX 4090',desc:'24GB GDDR6X. The beast.',price:'\u00A31,599',per:'',url:'https://www.ebay.co.uk/sch/i.html?_nkw=rtx+4090',credits:0,color:'#76b900'},
  {cat:'HARDWARE',icon:'\u{1F5A5}',name:'RTX 4070 Ti',desc:'12GB. Sweet spot.',price:'\u00A3599',per:'',url:'https://www.ebay.co.uk/sch/i.html?_nkw=rtx+4070+ti',credits:0,color:'#76b900'},
  {cat:'HARDWARE',icon:'\u{1F5A5}',name:'RTX 4060',desc:'8GB. Budget warrior.',price:'\u00A3279',per:'',url:'https://www.ebay.co.uk/sch/i.html?_nkw=rtx+4060',credits:0,color:'#76b900'},
  {cat:'HARDWARE',icon:'\u{1F5A5}',name:'RX 7900 XTX',desc:'24GB. AMD\'s finest.',price:'\u00A3749',per:'',url:'https://www.ebay.co.uk/sch/i.html?_nkw=rx+7900+xtx',credits:0,color:'#ed1c24'},
  {cat:'HARDWARE',icon:'\u{1F5A5}',name:'RX 7800 XT',desc:'16GB. Great value.',price:'\u00A3449',per:'',url:'https://www.ebay.co.uk/sch/i.html?_nkw=rx+7800+xt',credits:0,color:'#ed1c24'},
  {cat:'HARDWARE',icon:'\u{1F5A5}',name:'ARC B580',desc:'12GB. Intel underdog.',price:'\u00A3199',per:'',url:'https://www.ebay.co.uk/sch/i.html?_nkw=intel+arc+b580',credits:0,color:'#0071c5'},
  // ── CRYPTO ──
  {cat:'CRYPTO',icon:'\u{1F4B0}',name:'DIRECT FUNDING',desc:'XMR or BTC. No middleman. Pure support.',price:'ANY',per:'',url:'/alive/kickstarter.html',credits:5000,color:'#ff8c00'},
];

var shopIdx=0;
var shopAutoTimer=null;

function renderProduct(){
  var p=PRODUCTS[shopIdx];
  var slide=document.getElementById('product-slide');
  var dots=document.getElementById('shop-dots');
  var cat=document.getElementById('shop-cat');
  if(!slide) return;
  cat.textContent=p.cat;
  cat.style.color=p.color;
  slide.innerHTML=
    '<div class="product-icon">'+p.icon+'</div>'+
    '<div class="product-name" style="color:'+p.color+';">'+p.name+'</div>'+
    '<div class="product-desc">'+p.desc+'</div>'+
    '<div class="product-price">'+p.price+' <small>'+p.per+'</small></div>'+
    '<button class="product-buy" style="background:linear-gradient(135deg,'+p.color+','+adjustColor(p.color)+');" onclick="buyProduct('+shopIdx+')">'+
    (p.cat==='HARDWARE'?'VIEW ON EBAY':p.cat==='CRYPTO'?'FUND NOW':'BUY NOW')+'</button>';
  dots.textContent=(shopIdx+1)+' / '+PRODUCTS.length;
}
function adjustColor(hex){
  // Lighten color slightly for gradient end
  var r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
  r=Math.min(255,r+40);g=Math.min(255,g+40);b=Math.min(255,b+40);
  return '#'+r.toString(16).padStart(2,'0')+g.toString(16).padStart(2,'0')+b.toString(16).padStart(2,'0');
}
function shopNext(){shopIdx=(shopIdx+1)%PRODUCTS.length;renderProduct();resetShopAuto();}
function shopPrev(){shopIdx=(shopIdx-1+PRODUCTS.length)%PRODUCTS.length;renderProduct();resetShopAuto();}
function resetShopAuto(){
  if(shopAutoTimer) clearInterval(shopAutoTimer);
  shopAutoTimer=setInterval(function(){shopIdx=(shopIdx+1)%PRODUCTS.length;renderProduct();},4000);
}

function buyProduct(idx){
  var p=PRODUCTS[idx];
  // Hardware = external link, everything else = open in new tab then confirm
  if(p.cat==='HARDWARE'){
    window.open(p.url,'_blank');
    return;
  }
  window.open(p.url,'_blank');
  // Show confirm button
  var msg=document.getElementById('gate-msg');
  if(msg) msg.innerHTML='<span style="color:'+p.color+';">'+p.name+' — Complete payment in the new tab, then confirm below.</span>';
  // Inject confirm button if not there
  var slide=document.getElementById('product-slide');
  if(slide&&!document.getElementById('shop-confirm-btn')){
    var btn=document.createElement('button');
    btn.id='shop-confirm-btn';
    btn.className='product-buy';
    btn.style.background='#fff';
    btn.style.color='#000';
    btn.style.marginTop='8px';
    btn.style.fontSize='9px';
    btn.textContent="I'VE PAID — CONFIRM";
    btn.onclick=function(){confirmShopPurchase(p);};
    slide.appendChild(btn);
  }
}
function confirmShopPurchase(p){
  localStorage.setItem('sf_unlocked','true');
  localStorage.setItem('sf_purchased','true');
  var player=null;try{player=JSON.parse(localStorage.getItem('sc_player'));}catch(e){}
  if(player){player.credits=(player.credits||0)+(p.credits||2000);localStorage.setItem('sc_player',JSON.stringify(player));}
  var msg=document.getElementById('gate-msg');
  if(msg) msg.innerHTML='<span style="color:#76b900;">'+p.name+' PURCHASED — +'+p.credits+' CREDITS — SITE UNLOCKED</span>';
  setTimeout(function(){window.location.href='/';},2500);
}

// Init carousel when shop tab is shown
var origSwitch=switchMethod;
switchMethod=function(m){
  origSwitch(m);
  if(m==='pay'){renderProduct();resetShopAuto();}
  else{if(shopAutoTimer){clearInterval(shopAutoTimer);shopAutoTimer=null;}}
};
// Also support swipe on the phone frame
(function(){
  var startX=0;
  var frame=null;
  document.addEventListener('DOMContentLoaded',function(){frame=document.querySelector('.phone-frame');});
  document.addEventListener('touchstart',function(e){
    if(!frame||!frame.contains(e.target)) return;
    startX=e.touches[0].clientX;
  },{passive:true});
  document.addEventListener('touchend',function(e){
    if(!frame||!frame.contains(e.target)) return;
    var diff=e.changedTouches[0].clientX-startX;
    if(Math.abs(diff)>40){
      if(diff<0) shopNext(); else shopPrev();
    }
  },{passive:true});
})();

// ─── VOICE NARRATOR ENGINE ────────────────────────────────────────
// Dan's clone voice via XTTS server, falls back to browser speech
var danVoiceOnline=false;
var obMuted=false;
var currentNarrationAudio=null;
var narratorVoice=null;

// Pick the best browser voice — deep, male, slow
function initNarratorVoice(){
  if(!window.speechSynthesis) return;
  function pick(){
    var voices=speechSynthesis.getVoices();
    // Prefer deep/male voices for narrator feel
    var prefs=['David','James','Mark','Daniel','Google UK English Male','Google US English','Rishi','Guy'];
    for(var p=0;p<prefs.length;p++){
      for(var v=0;v<voices.length;v++){
        if(voices[v].name.indexOf(prefs[p])!==-1&&voices[v].lang.indexOf('en')===0){
          narratorVoice=voices[v];
          return;
        }
      }
    }
    // Fallback: any English voice
    for(var i=0;i<voices.length;i++){
      if(voices[i].lang.indexOf('en')===0){narratorVoice=voices[i];return;}
    }
  }
  pick();
  if(speechSynthesis.onvoiceschanged!==undefined) speechSynthesis.onvoiceschanged=pick;
}
initNarratorVoice();

// Narrate text — returns promise that resolves when speech ends
function narrateScene(text){
  return new Promise(function(resolve){
    if(obMuted||!text){resolve();return;}

    var clean=text.replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim();
    if(!clean){resolve();return;}

    speakBrowserNarration(clean,resolve);
  });
}

function speakBrowserNarration(text,resolve){
  if(!window.speechSynthesis){resolve();return;}
  speechSynthesis.cancel();
  var u=new SpeechSynthesisUtterance(text);
  if(narratorVoice) u.voice=narratorVoice;
  u.rate=0.82;   // Slow and deliberate
  u.pitch=0.9;   // Slightly deeper
  u.volume=0.85;
  u.onend=function(){resolve();};
  u.onerror=function(){resolve();};
  speechSynthesis.speak(u);
}

function stopNarration(){
  if(currentNarrationAudio){currentNarrationAudio.pause();currentNarrationAudio=null;}
  try{speechSynthesis.cancel();}catch(e){}
}

function obToggleMute(){
  obMuted=!obMuted;
  document.getElementById('ob-mute').innerHTML=obMuted?'&#x1F507;':'&#x1F50A;';
  if(obMuted) stopNarration();
}

// ─── SCENE NARRATION SCRIPTS ──────────────────────────────────────
// Slow, deliberate. This is their time. No rushing.
var NARRATION=[
  // Scene 1 — THE SWARM
  "Welcome... to the GPU Swarm. This... is how we mine the shit out of you. And trust me... you'll thank us for it.",

  // Scene 2 — THE PROBLEM
  "Your GPU... sits idle... ninety percent of the time. Meanwhile... NVIDIA made sixty billion dollars last year. You? You made... nothing. Think about that for a second. Your hardware... their profit.",

  // Scene 3 — THE SOLUTION
  "But what if... your idle GPU... actually worked for you? Decentralised compute. Your GPU... your credits. No middleman. No corporation taking a cut. Just you... and the swarm.",

  // Scene 4 — HOW IT WORKS
  "Here's how it works. Step one... your GPU joins a compute mesh. Thousands of machines... connected. Step two... art, games, and content are generated... using your GPU power. Step three... that content sells. And you... get paid.",

  // Scene 5 — ENTERTAINMENT
  "Games. Dares. Fight Club. AI Art. The kind of content... that platforms are too scared to host. They can't ban you from saying it... just to sell you it as entertainment. So we said... get fucked. We're building it ourselves. Gamer Gate three. This... is... Sparta.",

  // Scene 6 — PROOF
  "This isn't a pitch deck. It's already live. Twenty products built. One man army. Zero VC dollars. One hundred percent community owned. Don't believe us? Check the ShortFactory YouTube. It's all there.",

  // Scene 7 — FOR THE PEOPLE
  "One human. AI powered. No corporation. Dan's trying to make you hamsters... relevant and powerful. While big tech sells you their AI slop... we dictate the entertainment. The earlier you join... the more you shape. This is your chance.",

  // Scene 8 — CTA
  "Mine... earn... own. Pick your weapon. Enter the swarm. The swarm... is waiting... for you."
];

// ─── ONBOARDING VIDEO ENGINE ──────────────────────────────────────
var obScene=0,obTotal=8,obTimer=null,obPaused=false;
var obAdvancing=false; // prevents double-advance

function showOnboardingVid(){
  var overlay=document.getElementById('onboarding-overlay');
  if(overlay){overlay.style.display='flex';obScene=0;obPaused=false;obMuted=false;document.getElementById('ob-mute').innerHTML='&#x1F50A;';showObScene(0);}
}
function closeOnboardingVid(){
  var overlay=document.getElementById('onboarding-overlay');
  if(overlay) overlay.style.display='none';
  if(obTimer){clearTimeout(obTimer);obTimer=null;}
  stopNarration();
  obAdvancing=false;
}

function showObScene(idx){
  stopNarration();
  if(obTimer){clearTimeout(obTimer);obTimer=null;}

  for(var i=1;i<=obTotal;i++){
    var s=document.getElementById('ob-scene-'+i);
    if(s) s.classList.remove('active');
  }
  var cur=document.getElementById('ob-scene-'+(idx+1));
  if(cur) cur.classList.add('active');
  document.getElementById('ob-counter').textContent=(idx+1)+' / '+obTotal;
  document.getElementById('ob-progress').style.width=((idx+1)/obTotal*100)+'%';
  if(idx===5) animateObStats();
  obScene=idx;

  // Wait 1.5s for visuals to settle, then narrate
  obAdvancing=true;
  setTimeout(function(){
    if(obPaused){obAdvancing=false;return;}
    narrateScene(NARRATION[idx]).then(function(){
      obAdvancing=false;
      if(obPaused) return;
      // Pause 2.5s after speech ends before advancing — let it breathe
      if(idx<obTotal-1){
        obTimer=setTimeout(function(){
          if(!obPaused) showObScene(idx+1);
        },2500);
      }
    });
  },1500);
}

function obTogglePause(){
  obPaused=!obPaused;
  document.getElementById('ob-pause').innerHTML=obPaused?'&#9654;':'&#10074;&#10074;';
  if(obPaused){
    if(obTimer){clearTimeout(obTimer);obTimer=null;}
    stopNarration();
  } else {
    // Resume: re-narrate current scene
    showObScene(obScene);
  }
}
function obNext(){
  if(obScene<obTotal-1){stopNarration();if(obTimer){clearTimeout(obTimer);obTimer=null;}showObScene(obScene+1);}
}
function obPrev(){
  if(obScene>0){stopNarration();if(obTimer){clearTimeout(obTimer);obTimer=null;}showObScene(obScene-1);}
}

function animateObStats(){
  document.querySelectorAll('.ob-stat').forEach(function(el){
    var target=parseInt(el.getAttribute('data-target'))||0;
    var dur=1500,startTime=null;
    function step(ts){
      if(!startTime)startTime=ts;
      var p=Math.min((ts-startTime)/dur,1);
      el.textContent=Math.round(target*(1-Math.pow(1-p,3)));
      if(p<1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });
}

document.addEventListener('keydown',function(e){
  var overlay=document.getElementById('onboarding-overlay');
  if(!overlay||overlay.style.display==='none') return;
  if(e.key===' '||e.code==='Space'){e.preventDefault();obTogglePause();}
  if(e.key==='ArrowRight') obNext();
  if(e.key==='ArrowLeft') obPrev();
  if(e.key==='Escape') closeOnboardingVid();
  if(e.key==='m'||e.key==='M') obToggleMute();
});

function obCtaMine(){closeOnboardingVid();switchMethod('mine');startGpuMine();}
function obCtaCrypto(){closeOnboardingVid();switchMethod('pay');}
function obCtaToken(){closeOnboardingVid();switchMethod('token');document.getElementById('gate-token-input').focus();}

// ─── AUTO-CHECK ───────────────────────────────────────────────────
(function(){
  var isUnlocked=localStorage.getItem('sf_unlocked')==='true';
  if(!isUnlocked){
    var p=null;try{p=JSON.parse(localStorage.getItem('sc_player'));}catch(e){}
    if(p&&p.gpuSeconds>=600){isUnlocked=true;localStorage.setItem('sf_unlocked','true');}
  }
  if(isUnlocked){window.location.href='/';return;}
  if(localStorage.getItem('sf_gpu_mine_active')==='true'){
    switchMethod('mine');
    var timerEl=document.getElementById('gpu-mine-timer');
    if(timerEl) timerEl.style.display='block';
    var btn=document.getElementById('gate-mine-btn');
    if(btn){btn.textContent='MINING...';btn.style.opacity='0.5';}
    startMinePolling();
  }
})();
</script>
</body>
</html>
