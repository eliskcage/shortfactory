<div class="hslide" data-slide="blackbox">
<div class="section" style="background:linear-gradient(165deg,#000000 0%,#050010 50%,#000000 100%);display:flex;flex-direction:column;align-items:center;justify-content:flex-start;min-height:100vh;box-sizing:border-box;padding:24px 16px 40px;overflow-y:auto;" data-voice="Black Box. Alien technology. Your code never exists in plaintext. Time-locked. Quantum proof. Shipped.">

<style>
.bb-hero{text-align:center;max-width:600px;margin:0 auto 20px;}
.bb-icon{font-size:44px;line-height:1;margin-bottom:8px;filter:drop-shadow(0 0 24px rgba(0,247,255,0.7));}
.bb-title{font-family:'Orbitron',sans-serif;font-size:clamp(16px,4vw,28px);font-weight:900;letter-spacing:4px;color:#00f7ff;margin-bottom:6px;}
.bb-sub{font-family:'Courier New',monospace;font-size:clamp(10px,1.5vw,12px);color:#666;line-height:1.6;max-width:480px;margin:0 auto 14px;}
.bb-badge{display:inline-block;background:#00f7ff;color:#000;font-family:'Orbitron',sans-serif;font-size:9px;font-weight:900;letter-spacing:3px;padding:4px 12px;border-radius:2px;margin-bottom:16px;}

.bb-stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;max-width:580px;width:100%;margin:0 auto 16px;}
.bb-stat{background:#050010;border:1px solid #0a0030;border-radius:4px;padding:12px 8px;text-align:center;}
.bb-stat-val{font-family:'Orbitron',sans-serif;font-size:clamp(14px,3vw,20px);font-weight:900;color:#00f7ff;}
.bb-stat-label{font-family:'Courier New',monospace;font-size:9px;color:#444;margin-top:4px;letter-spacing:1px;}

.bb-demo{background:#000;border:1px solid #0a0030;border-radius:6px;padding:16px;max-width:580px;width:100%;margin:0 auto 16px;}
.bb-demo-title{font-family:'Orbitron',sans-serif;font-size:10px;letter-spacing:3px;color:#00f7ff;margin-bottom:10px;}
.bb-terminal{background:#000;border:1px solid #001a1a;border-radius:4px;padding:12px;font-family:'Courier New',monospace;font-size:11px;color:#00f7ff;min-height:80px;overflow:hidden;position:relative;}
.bb-terminal .dim{color:#333;}
.bb-terminal .ok{color:#00ff88;}
.bb-terminal .warn{color:#ff8800;}
.bb-cursor{display:inline-block;width:7px;height:12px;background:#00f7ff;animation:bbBlink .8s step-end infinite;vertical-align:middle;}
@keyframes bbBlink{0%,100%{opacity:1;}50%{opacity:0;}}

.bb-features{max-width:580px;width:100%;margin:0 auto 16px;display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.bb-feat{background:#050010;border:1px solid #0a0030;border-radius:4px;padding:10px 12px;display:flex;gap:8px;align-items:flex-start;}
.bb-feat-icon{font-size:16px;flex-shrink:0;margin-top:1px;}
.bb-feat-text{font-family:'Courier New',monospace;font-size:10px;color:#888;line-height:1.4;}
.bb-feat-text strong{color:#00f7ff;display:block;margin-bottom:2px;font-size:10px;}
@media(max-width:400px){.bb-features{grid-template-columns:1fr;}}

.bb-tiers{max-width:580px;width:100%;margin:0 auto 16px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;}
.bb-tier{background:#050010;border:1px solid #0a0030;border-radius:4px;padding:12px 8px;text-align:center;}
.bb-tier.hot{border-color:#00f7ff;box-shadow:0 0 16px rgba(0,247,255,0.15);}
.bb-tier-name{font-family:'Orbitron',sans-serif;font-size:9px;letter-spacing:2px;color:#444;margin-bottom:6px;}
.bb-tier.hot .bb-tier-name{color:#00f7ff;}
.bb-tier-price{font-family:'Orbitron',sans-serif;font-size:clamp(14px,3vw,20px);font-weight:900;color:#e0e0e0;margin-bottom:4px;}
.bb-tier-desc{font-family:'Courier New',monospace;font-size:9px;color:#444;line-height:1.4;}

.bb-cta{display:block;max-width:580px;width:100%;margin:0 auto 8px;padding:14px;background:transparent;border:2px solid #00f7ff;color:#00f7ff;font-family:'Orbitron',sans-serif;font-size:12px;font-weight:900;letter-spacing:3px;text-align:center;cursor:pointer;transition:all .2s;border-radius:3px;text-decoration:none;}
.bb-cta:hover{background:#00f7ff;color:#000;}
.bb-patent{text-align:center;font-family:'Courier New',monospace;font-size:9px;color:#333;margin-top:8px;letter-spacing:1px;}
.bb-patent span{color:#00f7ff;}
</style>

<div class="bb-hero">
  <div class="bb-icon">⬛</div>
  <div class="bb-title">BLACK BOX</div>
  <div class="bb-sub">Your code never exists in plaintext. Not in transit. Not at rest. Not even in memory — outside the box.</div>
  <div class="bb-badge">✓ SHIPPED · v1.1.0 · WEB SECURITY SOLVED</div>
</div>

<div class="bb-stats">
  <div class="bb-stat">
    <div class="bb-stat-val">3D</div>
    <div class="bb-stat-label">TEMPORAL SPHERE</div>
  </div>
  <div class="bb-stat">
    <div class="bb-stat-val">O(1)</div>
    <div class="bb-stat-label">LOOKUP SPEED</div>
  </div>
  <div class="bb-stat">
    <div class="bb-stat-val">0</div>
    <div class="bb-stat-label">PLAINTEXT ON DISK</div>
  </div>
</div>

<div class="bb-demo">
  <div class="bb-demo-title">LIVE ROUND-TRIP</div>
  <div class="bb-terminal" id="bbTerminal">
    <span class="dim">&gt; </span>encode("your_code") → <span id="bbPoints">...</span><br>
    <span class="dim">&gt; </span>blackbox.run() → <span id="bbStatus">initialising</span><br>
    <span id="bbLine3" style="display:none;"></span>
    <span class="bb-cursor" id="bbCursor"></span>
  </div>
</div>

<div class="bb-features">
  <div class="bb-feat">
    <div class="bb-feat-icon">🔐</div>
    <div class="bb-feat-text"><strong>HMAC SIGNED</strong>Tampered blobs rejected at decode. Every payload signed.</div>
  </div>
  <div class="bb-feat">
    <div class="bb-feat-icon">🔑</div>
    <div class="bb-feat-text"><strong>HOT KEY ROTATION</strong>Live key swap, no restart. Thread-safe atomic replacement.</div>
  </div>
  <div class="bb-feat">
    <div class="bb-feat-icon">⏱</div>
    <div class="bb-feat-text"><strong>TEMPORAL LOCK</strong>Code valid only inside the encoded time window. Self-destructs.</div>
  </div>
  <div class="bb-feat">
    <div class="bb-feat-icon">📋</div>
    <div class="bb-feat-text"><strong>AUDIT TRAIL</strong>10,000-entry rolling log. SIEM-ready. SOC 2 / PCI compliant.</div>
  </div>
</div>

<div class="bb-tiers">
  <div class="bb-tier">
    <div class="bb-tier-name">FREE</div>
    <div class="bb-tier-price">$0</div>
    <div class="bb-tier-desc">Dev access. 100 encodes/day.</div>
  </div>
  <div class="bb-tier hot">
    <div class="bb-tier-name">STANDARD</div>
    <div class="bb-tier-price">£79<span style="font-size:10px;color:#006677;">/mo</span></div>
    <div class="bb-tier-desc">Unlimited. Hot rotation. Audit trail.</div>
  </div>
  <div class="bb-tier">
    <div class="bb-tier-name">ENTERPRISE</div>
    <div class="bb-tier-price">£POA</div>
    <div class="bb-tier-desc">Air-gapped. TEE. PCI DSS. Banks &amp; AI.</div>
  </div>
</div>

<a href="/blackbox-demo.html" class="bb-cta">▶ WATCH IT DECODE LIVE</a>
<a href="https://github.com/eliskcage/satoshi-cypher" class="bb-cta" target="_blank" style="margin-top:8px;border-color:#003a42;color:#004a52;font-size:10px;">ACCESS BLACK BOX API →</a>

<div class="bb-patent">
  Patent pending · <span>Computanium 3D Programming</span> · Dan Chipchase · shortfactory.shop
</div>

</div>
</div>

<script>
(function(){
  var lines = [
    {points:'[232.16, 235.84, 239.51...]', status:'<span style="color:#ff8800;">decoding</span>', line3:''},
    {points:'[232.16, 235.84, 239.51...]', status:'<span style="color:#ff8800;">rebuilding in RAM</span>', line3:''},
    {points:'[232.16, 235.84, 239.51...]', status:'<span style="color:#00ff88;">executed ✓</span>', line3:'<span class="ok">&gt; integrity: PASS · plaintext: WIPED · elapsed: 0.4ms</span><br>'},
  ];
  var i = 0;
  function tick(){
    var l = lines[i % lines.length];
    document.getElementById('bbPoints').textContent = l.points;
    document.getElementById('bbStatus').innerHTML = l.status;
    var l3 = document.getElementById('bbLine3');
    l3.innerHTML = l.line3;
    l3.style.display = l.line3 ? 'block' : 'none';
    i++;
    setTimeout(tick, i % lines.length === 0 ? 2400 : 900);
  }
  // Only run when slide is visible
  var started = false;
  var obs = new IntersectionObserver(function(entries){
    if(entries[0].isIntersecting && !started){ started=true; setTimeout(tick,600); }
  },{threshold:0.3});
  var el = document.querySelector('.hslide[data-slide="blackbox"]');
  if(el) obs.observe(el);
})();
</script>
