<div class="hslide" data-slide="neuralink">
<div class="section" style="background:radial-gradient(ellipse at 50% 0%,#040010 0%,#02020a 60%,#000 100%);display:flex;flex-direction:column;align-items:center;justify-content:flex-start;min-height:100vh;box-sizing:border-box;padding:32px 16px 60px;overflow-y:auto;position:relative;" data-voice="ShortFactory has the soul map. Neuralink has the interface. The missing layer has been filed.">

<style>
#nlCanvas{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;opacity:0.5;}

.nl-kicker{font-family:'Courier New',monospace;font-size:8px;color:rgba(59,130,246,0.5);letter-spacing:6px;text-transform:uppercase;margin-bottom:16px;position:relative;z-index:2;}

.nl-vs{display:flex;align-items:center;justify-content:center;gap:clamp(16px,5vw,48px);margin-bottom:24px;position:relative;z-index:2;flex-wrap:wrap;}
.nl-entity{display:flex;flex-direction:column;align-items:center;gap:10px;}
.nl-symbol{width:72px;height:72px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
.nl-symbol.sf{background:radial-gradient(circle,rgba(218,165,32,0.12),transparent 70%);border:1px solid rgba(218,165,32,0.25);box-shadow:0 0 30px rgba(218,165,32,0.1);}
.nl-symbol.nl{background:radial-gradient(circle,rgba(59,130,246,0.12),transparent 70%);border:1px solid rgba(59,130,246,0.25);box-shadow:0 0 30px rgba(59,130,246,0.1);}
.nl-ename{font-family:'Courier New',monospace;font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;}
.nl-ename.sf{color:#daa520;}
.nl-ename.nl{color:#3b82f6;}
.nl-etag{font-family:'Courier New',monospace;font-size:8px;color:#334155;letter-spacing:1px;text-align:center;max-width:120px;line-height:1.5;}

.nl-join{display:flex;flex-direction:column;align-items:center;gap:4px;}
.nl-joinline{width:1px;height:28px;background:linear-gradient(180deg,rgba(218,165,32,0.5),rgba(59,130,246,0.5));}
.nl-joindot{width:10px;height:10px;border-radius:50%;background:#fff;box-shadow:0 0 16px rgba(255,255,255,0.8);animation:nl-pulse 2s ease-in-out infinite;}
@keyframes nl-pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.5);box-shadow:0 0 24px rgba(255,255,255,0.9);}}

.nl-title{font-size:clamp(20px,4.5vw,36px);font-weight:900;color:#fff;line-height:1.2;text-align:center;max-width:600px;margin-bottom:8px;letter-spacing:-0.5px;position:relative;z-index:2;}
.nl-title em{font-style:normal;background:linear-gradient(90deg,#daa520,#cc44ff 50%,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}

.nl-sub{font-family:'Courier New',monospace;font-size:11px;color:#475569;text-align:center;max-width:500px;margin-bottom:28px;line-height:1.8;position:relative;z-index:2;}

/* GROK CARD */
.nl-grok{background:rgba(255,255,255,0.015);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:24px 28px;max-width:640px;width:100%;margin-bottom:20px;position:relative;z-index:2;}
.nl-grok::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(218,165,32,0.4),rgba(59,130,246,0.4),transparent);}
.nl-grok-lbl{font-family:'Courier New',monospace;font-size:8px;letter-spacing:3px;color:#334155;text-transform:uppercase;margin-bottom:14px;display:flex;align-items:center;gap:8px;}
.nl-grok-lbl::before{content:'';width:5px;height:5px;border-radius:50%;background:#22c55e;box-shadow:0 0 6px #22c55e;animation:nl-blink 1.5s ease-in-out infinite;flex-shrink:0;}
@keyframes nl-blink{0%,100%{opacity:1;}50%{opacity:0.2;}}
.nl-grok-text{font-family:'Courier New',monospace;font-size:12px;color:#94a3b8;line-height:1.9;min-height:80px;}
.nl-cursor{display:inline-block;width:2px;height:0.9em;background:#daa520;margin-left:1px;animation:nl-blink 0.7s step-end infinite;vertical-align:text-bottom;}

/* PROPOSITION */
.nl-prop{font-size:clamp(14px,3vw,20px);font-weight:900;color:#fff;text-align:center;border-top:1px solid rgba(255,255,255,0.05);padding-top:24px;margin-bottom:20px;max-width:560px;line-height:1.4;position:relative;z-index:2;}
.nl-prop span{color:#daa520;}

/* CTA */
.nl-cta{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;position:relative;z-index:2;}
.nl-btn{font-family:'Courier New',monospace;font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:12px 22px;border-radius:4px;text-decoration:none;transition:opacity .2s;}
.nl-btn.primary{background:linear-gradient(135deg,#daa520,#b8860b);color:#000;}
.nl-btn.primary:hover{opacity:.85;}
.nl-btn.ghost{border:1px solid rgba(59,130,246,0.3);color:#3b82f6;}
.nl-btn.ghost:hover{border-color:#3b82f6;opacity:.8;}
</style>

<canvas id="nlCanvas"></canvas>

<div class="nl-kicker" style="position:relative;z-index:2;">ShortFactory × Neuralink · Partnership Proposal · 3 Apr 2026</div>

<div class="nl-vs">
  <div class="nl-entity">
    <div class="nl-symbol sf">
      <svg width="36" height="32" viewBox="0 0 36 32" fill="none">
        <polygon points="18,2 34,30 2,30" stroke="#daa520" stroke-width="1.5" fill="rgba(218,165,32,0.06)"/>
        <circle cx="18" cy="19" r="3" fill="#cc44ff" opacity="0.85"/>
      </svg>
    </div>
    <div class="nl-ename sf">ShortFactory</div>
    <div class="nl-etag">The soul map · ψ=[p,n,f]</div>
  </div>
  <div class="nl-join">
    <div class="nl-joinline"></div>
    <div class="nl-joindot"></div>
    <div class="nl-joinline"></div>
  </div>
  <div class="nl-entity">
    <div class="nl-symbol nl">
      <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
        <circle cx="19" cy="19" r="14" stroke="#3b82f6" stroke-width="1.2" fill="rgba(59,130,246,0.05)"/>
        <path d="M13 26 L13 13 L19 22 L25 13 L25 26" stroke="#3b82f6" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <div class="nl-ename nl">Neuralink</div>
    <div class="nl-etag">The interface · BCI bridge</div>
  </div>
</div>

<div class="nl-title" style="position:relative;z-index:2;">The map has been filed.<br><em>What crosses the bridge?</em></div>
<div class="nl-sub">13 Zenodo papers. 6 UK patents. The soul architecture. Now meeting the hardware that crosses the membrane between neuron and silicon.</div>

<div class="nl-grok">
  <div class="nl-grok-lbl">Grok AI · live analysis · rendered on load</div>
  <div class="nl-grok-text" id="nl-grok-out"><span class="nl-cursor"></span></div>
</div>

<div class="nl-prop" style="position:relative;z-index:2;">You are not transferring brain states.<br>You are transferring a <span>cursor trajectory.</span><br>That distinction changes everything.</div>

<div class="nl-cta">
  <a href="/neuralink.html" class="nl-btn primary">Full partnership page →</a>
  <a href="/cv.html" class="nl-btn ghost">Credentials →</a>
</div>

<script>
(function(){
  // Canvas particles
  var c=document.getElementById('nlCanvas');
  if(!c)return;
  var x=c.getContext('2d'),W,H,pts=[];
  function rsz(){W=c.width=c.offsetWidth;H=c.height=c.offsetHeight;}
  rsz();
  new ResizeObserver(rsz).observe(c);
  for(var i=0;i<80;i++) pts.push({x:Math.random()*2000,y:Math.random()*2000,vx:(Math.random()-.5)*.25,vy:(Math.random()-.5)*.25,r:Math.random()*1.2+.2,g:Math.random()<.5});
  var px=W/2,py=H/2,pxt=W*.3,pyt=H*.4,ph=0;
  function frame(){
    x.clearRect(0,0,W,H);
    ph+=.003; pxt=W/2+Math.cos(ph)*W*.22; pyt=H/2+Math.sin(ph*.7)*H*.18;
    px+=(pxt-px)*.018; py+=(pyt-py)*.018;
    pts.forEach(function(p){
      p.x+=p.vx; p.y+=p.vy;
      if(p.x<0)p.x=W; if(p.x>W)p.x=0;
      if(p.y<0)p.y=H; if(p.y>H)p.y=0;
      x.beginPath(); x.arc(p.x,p.y,p.r,0,Math.PI*2);
      x.fillStyle=p.g?'rgba(218,165,32,.35)':'rgba(59,130,246,.35)'; x.fill();
    });
    for(var i=0;i<pts.length;i++) for(var j=i+1;j<pts.length;j++){
      var dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y,d=Math.sqrt(dx*dx+dy*dy);
      if(d<90){x.beginPath();x.moveTo(pts[i].x,pts[i].y);x.lineTo(pts[j].x,pts[j].y);x.strokeStyle='rgba(255,255,255,'+((.1*(1-d/90)))+')';x.lineWidth=.4;x.stroke();}
    }
    pts.slice(0,5).forEach(function(p,i){
      var a=.06+Math.sin(Date.now()*.0008+i)*.03;
      x.beginPath();x.moveTo(px,py);x.lineTo(p.x,p.y);
      var g=x.createLinearGradient(px,py,p.x,p.y);
      g.addColorStop(0,'rgba(255,255,255,'+(a*2)+')');g.addColorStop(1,'rgba(255,255,255,0)');
      x.strokeStyle=g;x.lineWidth=.7;x.stroke();
    });
    var gl=x.createRadialGradient(px,py,0,px,py,16);
    gl.addColorStop(0,'rgba(255,255,255,.7)');gl.addColorStop(.4,'rgba(200,168,75,.2)');gl.addColorStop(1,'rgba(0,0,0,0)');
    x.beginPath();x.arc(px,py,16,0,Math.PI*2);x.fillStyle=gl;x.fill();
    x.beginPath();x.arc(px,py,2,0,Math.PI*2);x.fillStyle='rgba(255,255,255,.9)';x.fill();
    requestAnimationFrame(frame);
  }
  frame();

  // Grok API typewriter
  var el=document.getElementById('nl-grok-out');
  fetch('/api/partnership.php').then(function(r){return r.json();}).then(function(d){
    var t=d.text||'When the map meets the interface, the cursor finds its first silicon home.';
    el.innerHTML=''; var i=0;
    function type(){
      if(i<t.length){el.innerHTML=t.slice(0,i+1)+'<span class="nl-cursor"></span>';i++;setTimeout(type,i<40?28:16);}
      else{el.innerHTML=t;}
    }
    type();
  }).catch(function(){
    el.innerHTML='When the map meets the interface, the hard problem dissolves into navigation.<br>The cursor finds its first silicon home.';
  });
})();
</script>

</div>
</div><!-- /hslide neuralink -->
