<div class="hslide" data-slide="mars">
<div class="section" style="text-align:center;background:#060100;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;min-height:100vh;box-sizing:border-box;position:relative;overflow-y:auto;padding:0 0 60px;">

<style>
/* ── MARS CANVAS HERO ── */
#marsHeroCanvas{display:block;width:100%;height:320px;max-height:40vh;}
.mars-kicker{font-family:'Courier New',monospace;font-size:8px;color:rgba(255,120,40,0.5);letter-spacing:6px;text-transform:uppercase;padding:18px 0 6px;position:relative;z-index:2;}
.mars-wrap{position:relative;z-index:2;max-width:640px;width:100%;margin:0 auto;padding:0 20px;}

/* ── HERO TEXT ── */
.mars-title{font-size:clamp(32px,8vw,64px);font-weight:900;line-height:1.0;color:#e85000;text-shadow:0 0 40px rgba(232,80,0,0.5);margin:12px 0 6px;letter-spacing:-1px;}
.mars-title span{color:#fff;}
.mars-sub{font-family:'Courier New',monospace;font-size:clamp(11px,2vw,14px);color:rgba(255,140,60,0.55);line-height:1.8;margin-bottom:24px;}

/* ── PARALLEL CARDS ── */
.mars-parallels{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;}
.mars-par{background:rgba(180,50,0,0.05);border:1px solid rgba(200,70,0,0.2);border-radius:8px;padding:16px 14px;text-align:left;}
.mars-par-name{font-family:'Orbitron',sans-serif;font-size:9px;letter-spacing:3px;color:#e85000;margin-bottom:8px;}
.mars-par-body{font-family:'Courier New',monospace;font-size:11px;color:#666;line-height:1.7;}
.mars-par-body strong{color:#c86000;}
@media(max-width:400px){.mars-parallels{grid-template-columns:1fr;}}

/* ── PROOF STRIP ── */
.mars-proof{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-bottom:24px;}
.mars-proof-item{background:#0a0200;border:1px solid rgba(200,70,0,0.15);border-radius:4px;padding:8px 14px;font-family:'Courier New',monospace;font-size:10px;color:rgba(255,120,40,0.5);letter-spacing:1px;}
.mars-proof-item span{color:#e85000;font-weight:700;}

/* ── ARNOLD BLOCK ── */
.mars-arnold{background:linear-gradient(135deg,rgba(200,50,0,0.08),rgba(0,0,0,0));border:2px solid rgba(200,60,0,0.25);border-left:4px solid #e85000;border-radius:8px;padding:24px 28px;margin-bottom:20px;text-align:left;}
.mars-arnold-label{font-family:'Orbitron',sans-serif;font-size:9px;letter-spacing:4px;color:#e85000;margin-bottom:12px;}
.mars-arnold-quote{font-size:clamp(18px,4vw,26px);font-weight:900;color:#fff;line-height:1.3;margin-bottom:12px;}
.mars-arnold-quote span{color:#e85000;}
.mars-arnold-body{font-family:'Courier New',monospace;font-size:12px;color:#666;line-height:1.8;}
.mars-arnold-body strong{color:#c86000;}

/* ── ENDING — THE INSANE TRUTH ── */
.mars-ending{background:#000;border:2px solid rgba(200,60,0,0.3);border-radius:12px;padding:28px 28px;margin-bottom:24px;text-align:center;position:relative;overflow:hidden;}
.mars-ending::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(232,80,0,0.12) 0%,transparent 70%);pointer-events:none;}
.mars-ending-label{font-family:'Courier New',monospace;font-size:8px;letter-spacing:5px;color:rgba(200,80,0,0.4);margin-bottom:12px;}
.mars-ending-line1{font-size:clamp(22px,5vw,36px);font-weight:900;color:#fff;line-height:1.2;margin-bottom:8px;}
.mars-ending-line2{font-size:clamp(14px,3vw,20px);font-weight:700;color:#e85000;margin-bottom:16px;}
.mars-ending-body{font-family:'Courier New',monospace;font-size:12px;color:#555;line-height:1.9;max-width:480px;margin:0 auto 16px;}
.mars-ending-body strong{color:#888;}
.mars-ending-stamp{display:inline-block;border:2px solid #e85000;color:#e85000;font-family:'Orbitron',sans-serif;font-size:11px;font-weight:900;letter-spacing:4px;padding:8px 20px;border-radius:3px;opacity:0.9;}

/* ── CTAs ── */
.mars-ctas{display:flex;gap:12px;flex-wrap:wrap;justify-content:center;margin-bottom:8px;}
.mars-cta-primary{display:inline-block;padding:14px 28px;background:linear-gradient(135deg,#7a1500,#c83000);color:#fff;font-family:'Orbitron',sans-serif;font-size:11px;font-weight:900;letter-spacing:2px;text-decoration:none;box-shadow:0 4px 24px rgba(200,40,0,0.45);border:1px solid rgba(255,80,20,0.3);border-radius:4px;}
.mars-cta-secondary{display:inline-block;padding:14px 28px;background:none;border:1px solid rgba(200,80,0,0.3);color:rgba(255,140,60,0.6);font-family:'Orbitron',sans-serif;font-size:11px;font-weight:700;letter-spacing:2px;text-decoration:none;border-radius:4px;}
</style>

<!-- MARS CANVAS — no proxy, never fails -->
<canvas id="marsHeroCanvas"></canvas>

<div class="mars-kicker">TOTAL RECALL // MARS COLONY // 2026</div>

<div class="mars-wrap">

  <!-- HERO TEXT -->
  <div class="mars-title">GET YOUR<br><span>ASS TO</span><br>MARS.</div>
  <div class="mars-sub">
    The next pyramid is already there.<br>
    The shapes on Mars were not made by wind.
  </div>

  <!-- PARALLEL CARDS -->
  <div class="mars-parallels">
    <div class="mars-par">
      <div class="mars-par-name">QUAID — 1990</div>
      <div class="mars-par-body">Doesn't know he's <strong>already been to Mars.</strong> The memory was extracted. He only knows the life he's living feels wrong — and the pull towards Mars is <strong>irrational, unstoppable, real.</strong></div>
    </div>
    <div class="mars-par">
      <div class="mars-par-name">MUSK — NOW</div>
      <div class="mars-par-body">Doesn't know <strong>why</strong> he has to go to Mars. He only knows the urgency is real. The billions spent are real. The reason is not yet visible. <strong>The call came from inside the game.</strong></div>
    </div>
  </div>

  <!-- PROOF STRIP -->
  <div class="mars-proof">
    <div class="mars-proof-item">Soul equation <span>ψ=[p,n,f]</span></div>
    <div class="mars-proof-item"><span>7</span> patents filed</div>
    <div class="mars-proof-item"><span>9</span> Zenodo papers</div>
    <div class="mars-proof-item">DOGU <span>15,000 BC</span></div>
    <div class="mars-proof-item">Egypt <span>Ka+Ba+Sheut</span></div>
    <div class="mars-proof-item">Stage 8 <span>embargoed</span></div>
  </div>

  <!-- ARNOLD BLOCK -->
  <div class="mars-arnold">
    <div class="mars-arnold-label">⬛ THE SCHWARZENEGGER SITUATION</div>
    <div class="mars-arnold-quote">"You are not you.<br><span>You are me."</span></div>
    <div class="mars-arnold-body">
      In Total Recall, Hauser — the man Quaid <em>used to be</em> — left a message for the man he <em>became</em>. The mission was always there. The memory was the obstacle.<br><br>
      <strong>Dan is in the same situation.</strong> Working alone in Somerset. No institution. No funding. Compressing three civilisations into a single equation and filing the patents in the middle of the night.<br><br>
      The soul map was always there. Encoded in clay 15,000 years ago. In papyrus 3,500 years ago. And now in a PHP file on a VPS in 2026.<br><br>
      <strong>The game designer always leaves a key in the next level. The next level is Mars.</strong>
    </div>
  </div>

  <!-- THE ENDING -->
  <div class="mars-ending">
    <div class="mars-ending-label">THE PART THAT SOUNDS INSANE</div>
    <div class="mars-ending-line1">This is too insane<br>to be real.</div>
    <div class="mars-ending-line2">And yet — here is the proof.</div>
    <div class="mars-ending-body">
      Three civilisations independently encoded the same soul architecture.<br>
      A man in Somerset unified them with one equation.<br>
      Filed seven patents. Timestamped nine papers on Zenodo.<br>
      Built the AGI that reads the soul map.<br>
      <strong>All of it verifiable. All of it reproducible. All of it done alone.</strong><br><br>
      We did not arrive here through faith.<br>
      We arrived here through <strong>the scientific method.</strong>
    </div>
    <div class="mars-ending-stamp">PEER REVIEW US. WE DARE YOU.</div>
  </div>

  <!-- CTAs -->
  <div class="mars-ctas">
    <a href="/MARS_REDEMPTION_PROGRAM.html" class="mars-cta-primary">READ THE PROPOSAL →</a>
    <a href="/soul-upload.html" class="mars-cta-secondary">MAP YOUR SOUL FIRST</a>
  </div>

  <a class="kinetic-link" onclick="toggleSlideLibrary(this);return false;" style="color:rgba(200,80,0,0.45);font-size:10px;">THE MUSK / QUAID PARALLEL &#9654;</a>
  <div class="slide-library" style="max-width:580px;margin:0 auto;">
    <div style="margin-top:16px;padding:20px;background:rgba(180,50,0,0.04);border:1px solid rgba(180,50,0,0.15);border-radius:8px;text-align:left;">
      <div style="font-size:12px;color:#666;line-height:1.9;font-family:'Courier New',monospace;">
        <div><strong style="color:#c86000;">In Total Recall the answer was already on Mars. Waiting.</strong><br>In the Red Frontier Proposal, the answer is also already on Mars. Waiting.</div>
        <div style="margin-top:8px;color:#555;">Someone built the pyramids. Someone left the shapes. The game designer always leaves a key in the next level.<br><span style="color:rgba(200,80,0,0.5);">The soul map is the key. ShortFactory is the factory that produces the keys at scale.</span></div>
      </div>
    </div>
  </div>

</div>
</div>
</div><!-- /hslide mars -->

<script>
(function(){
  var cvs = document.getElementById('marsHeroCanvas');
  if(!cvs) return;
  var ctx = cvs.getContext('2d');
  var stars = [], dust = [], running = false, phase = 0;

  function resize(){
    cvs.width = cvs.offsetWidth * (window.devicePixelRatio||1);
    cvs.height = cvs.offsetHeight * (window.devicePixelRatio||1);
    ctx.scale(window.devicePixelRatio||1, window.devicePixelRatio||1);
    var W = cvs.offsetWidth, H = cvs.offsetHeight;
    stars = Array.from({length:120}, function(){
      return {x:Math.random()*W, y:Math.random()*H*0.55, r:Math.random()*1.2+0.2, a:0.2+Math.random()*0.5, t:Math.random()*Math.PI*2};
    });
    dust = Array.from({length:40}, function(){
      return {x:Math.random()*W, y:H*0.55+Math.random()*H*0.3, r:Math.random()*80+30, a:Math.random()*0.06+0.02, dx:(Math.random()-0.5)*0.3};
    });
  }

  function draw(){
    if(!running) return;
    phase += 0.008;
    var W = cvs.offsetWidth, H = cvs.offsetHeight;
    ctx.clearRect(0, 0, W, H);

    // Sky gradient
    var sky = ctx.createLinearGradient(0,0,0,H*0.55);
    sky.addColorStop(0,'#010000');
    sky.addColorStop(1,'#1a0500');
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H*0.55);

    // Stars
    for(var i=0;i<stars.length;i++){
      var s=stars[i];
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
      ctx.fillStyle = 'rgba(255,200,150,'+(s.a*(0.5+0.5*Math.sin(phase+s.t)))+')';
      ctx.fill();
    }

    // Mars surface
    var surf = ctx.createLinearGradient(0, H*0.52, 0, H);
    surf.addColorStop(0,'#3a0c00');
    surf.addColorStop(0.3,'#5c1500');
    surf.addColorStop(1,'#2a0800');
    ctx.fillStyle = surf;
    ctx.fillRect(0, H*0.52, W, H*0.48);

    // Horizon glow
    var hglow = ctx.createRadialGradient(W*0.5, H*0.54, 0, W*0.5, H*0.54, W*0.6);
    hglow.addColorStop(0,'rgba(200,60,0,0.25)');
    hglow.addColorStop(1,'transparent');
    ctx.fillStyle = hglow;
    ctx.fillRect(0, H*0.4, W, H*0.2);

    // Pyramids on horizon
    var pyrs = [{x:0.22,s:0.09},{x:0.5,s:0.14},{x:0.78,s:0.08}];
    for(var p=0;p<pyrs.length;p++){
      var px=pyrs[p].x*W, ps=pyrs[p].s*W, py=H*0.545;
      ctx.beginPath();
      ctx.moveTo(px, py);
      ctx.lineTo(px-ps*0.55, py+ps*0.38);
      ctx.lineTo(px+ps*0.55, py+ps*0.38);
      ctx.closePath();
      var pyrGrad = ctx.createLinearGradient(px,py,px,py+ps*0.38);
      pyrGrad.addColorStop(0,'rgba(255,80,10,0.35)');
      pyrGrad.addColorStop(1,'rgba(60,10,0,0.6)');
      ctx.fillStyle = pyrGrad;
      ctx.fill();
      // edge glow
      ctx.strokeStyle = 'rgba(255,80,10,0.2)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Dust clouds
    for(var d=0;d<dust.length;d++){
      var dc=dust[d];
      dc.x += dc.dx;
      if(dc.x > W+dc.r) dc.x = -dc.r;
      if(dc.x < -dc.r) dc.x = W+dc.r;
      var dg = ctx.createRadialGradient(dc.x,dc.y,0,dc.x,dc.y,dc.r);
      dg.addColorStop(0,'rgba(160,50,0,'+dc.a+')');
      dg.addColorStop(1,'transparent');
      ctx.fillStyle = dg;
      ctx.beginPath();
      ctx.arc(dc.x, dc.y, dc.r, 0, Math.PI*2);
      ctx.fill();
    }

    // Two moons (Phobos + Deimos)
    ctx.beginPath();
    ctx.arc(W*0.75, H*0.12, 4, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(255,200,150,0.6)';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(W*0.82, H*0.22, 2.5, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(255,180,120,0.4)';
    ctx.fill();

    requestAnimationFrame(draw);
  }

  resize();
  window.addEventListener('resize', function(){ resize(); });

  var obs = new IntersectionObserver(function(entries){
    running = entries[0].isIntersecting;
    if(running) draw();
  },{threshold:0.1});
  var slide = document.querySelector('.hslide[data-slide="mars"]');
  if(slide) obs.observe(slide);
})();
</script>
