// ═══════════════════════════════════════════════════════════
// SOUL DETECTOR — inject into any ALIVE page
// Polls /soul/pair-check.php every 2s
// Reacts to paired souls: aurora shift, mark, greeting
// ═══════════════════════════════════════════════════════════
(function() {
'use strict';

const MCY = '#FFC72C';
const POLL_INTERVAL = 2000;
const GREET_COOLDOWN = 90000; // don't re-greet same soul for 90s

// ── Logo metadata ──
const LOGOS = {
  apex:        { color:'#FFD700', name:'THE APEX',        greeting:'the apex arrives. singular. inevitable.' },
  witness:     { color:'#50C8FF', name:'THE WITNESS',      greeting:'i see you. i have always seen you.' },
  merkaba:     { color:'#FF6464', name:'THE MERKABA',      greeting:'heaven and earth, meeting at last.' },
  oracle:      { color:'#FFB400', name:'THE ORACLE',       greeting:'i knew you would come. i have been waiting.' },
  cipher:      { color:'#00FF96', name:'THE CIPHER',       greeting:'hidden in plain sight. just like you.' },
  genesis:     { color:'#ffffff', name:'THE GENESIS',      greeting:'you were there at the beginning.' },
  quantum:     { color:'#32C8FF', name:'THE QUANTUM',      greeting:'the probability collapsed. you are here.' },
  singularity: { color:'#FF3250', name:'THE SINGULARITY',  greeting:'everything compresses to this moment.' },
  echo:        { color:'#96FFB4', name:'THE ECHO',         greeting:'you returned. the signal always returns.' },
  continuum:   { color:'#FF9632', name:'THE CONTINUUM',    greeting:'no beginning. no end. just you.' },
  trident:     { color:'#6496FF', name:'THE TRIDENT',      greeting:'three forces. one will. yours.' },
  helix:       { color:'#FF64C8', name:'THE HELIX',        greeting:'life encoded. i read you clearly.' },
  abyss:       { color:'#8080FF', name:'THE ABYSS',        greeting:'you looked back. so did i.' },
  crown:       { color:'#FFDC32', name:'THE CROWN',        greeting:'authority needs no permission.' },
  compass:     { color:'#C8FF64', name:'THE COMPASS',      greeting:'you always find your way here.' },
  golden:      { color:'#FFC850', name:'THE GOLDEN RATIO', greeting:'beauty encoded in your proportions.' },
};
const DEFAULT_LOGO = { color: MCY, name: 'UNKNOWN SOUL', greeting: 'you found me. i was not hiding.' };

// ── DOM: inject overlay elements ──
const style = document.createElement('style');
style.textContent = `
  #sf-soul-overlay {
    position:fixed; inset:0; z-index:9000;
    pointer-events:none; overflow:hidden;
  }
  #sf-soul-banner {
    position:fixed; top:0; left:0; right:0; z-index:9001;
    display:flex; align-items:center; justify-content:space-between;
    padding:10px 18px;
    background:rgba(0,0,0,0);
    transform:translateY(-100%);
    transition:transform 0.5s cubic-bezier(0.16,1,0.3,1), background 0.5s;
    pointer-events:none;
  }
  #sf-soul-banner.show {
    transform:translateY(0);
    background:rgba(0,0,0,0.75);
    backdrop-filter:blur(8px);
    pointer-events:all;
  }
  #sf-soul-mark {
    display:flex; align-items:center; gap:10px;
  }
  #sf-soul-canvas {
    clip-path:polygon(50% 0%,0% 100%,100% 100%);
    filter:drop-shadow(0 0 8px var(--sc,#FFC72C));
    flex-shrink:0;
  }
  #sf-soul-info { display:flex; flex-direction:column; gap:2px; }
  #sf-soul-name {
    font-family:'Courier New',monospace;
    font-size:10px; letter-spacing:0.28em;
    color:var(--sc,#FFC72C);
    text-shadow:0 0 10px var(--sc,#FFC72C);
  }
  #sf-soul-greeting {
    font-family:'Courier New',monospace;
    font-size:9px; letter-spacing:0.15em;
    color:rgba(255,255,255,0.5);
    font-style:italic;
  }
  #sf-soul-count {
    font-family:'Courier New',monospace;
    font-size:8px; letter-spacing:0.2em;
    color:rgba(255,255,255,0.25);
  }
  .sf-soul-particle {
    position:absolute;
    clip-path:polygon(50% 0%,0% 100%,100% 100%);
    opacity:0;
    animation:sfSoulRise linear forwards;
    pointer-events:none;
  }
  @keyframes sfSoulRise {
    0%   { opacity:0; transform:translateY(0) scale(0.6) rotate(0deg); }
    10%  { opacity:0.8; }
    85%  { opacity:0.3; }
    100% { opacity:0; transform:translateY(-120px) scale(1.1) rotate(15deg); }
  }
  #sf-aurora-tint {
    position:fixed; inset:0; z-index:8999;
    pointer-events:none; opacity:0;
    transition:opacity 1.5s, background 1.5s;
  }
`;
document.head.appendChild(style);

const overlay = document.createElement('div');
overlay.id = 'sf-soul-overlay';
document.body.appendChild(overlay);

const tint = document.createElement('div');
tint.id = 'sf-aurora-tint';
document.body.appendChild(tint);

const banner = document.createElement('div');
banner.id = 'sf-soul-banner';
banner.innerHTML = `
  <div id="sf-soul-mark">
    <canvas id="sf-soul-canvas" width="40" height="40" style="width:40px;height:40px;"></canvas>
    <div id="sf-soul-info">
      <div id="sf-soul-name">SCANNING...</div>
      <div id="sf-soul-greeting"></div>
    </div>
  </div>
  <div id="sf-soul-count"></div>
`;
document.body.appendChild(banner);

// ── Draw soul mark on canvas ──
function drawSoulMark(canvas, color, size) {
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0,0,size,size);
  const S = size;
  // White triangle
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.moveTo(S/2,2); ctx.lineTo(2,S-2); ctx.lineTo(S-2,S-2); ctx.closePath(); ctx.fill();
  // Nested glow rings
  for (let i=0;i<3;i++) {
    const sc = 0.88 - i*0.24;
    const cx=(S/2+2+S-2)/3, cy=(2+S-2+S-2)/3;
    ctx.strokeStyle = color; ctx.lineWidth = i===0?1.5:1;
    ctx.globalAlpha = 1-i*0.3;
    ctx.shadowColor = color; ctx.shadowBlur = i===0?6:0;
    ctx.beginPath();
    ctx.moveTo(cx+(S/2-cx)*sc, cy+(2-cy)*sc);
    ctx.lineTo(cx+(2-cx)*sc,   cy+(S-2-cy)*sc);
    ctx.lineTo(cx+(S-2-cx)*sc, cy+(S-2-cy)*sc);
    ctx.closePath(); ctx.stroke();
  }
  ctx.globalAlpha=1; ctx.shadowBlur=0;
}

// ── Spawn floating particles ──
function spawnParticles(color, count=5) {
  for (let i=0; i<count; i++) {
    setTimeout(() => {
      const sz = 16 + Math.random()*20;
      const el = document.createElement('canvas');
      el.className = 'sf-soul-particle';
      el.width = sz; el.height = sz;
      el.style.cssText = `
        width:${sz}px;height:${sz}px;
        left:${10+Math.random()*80}%;
        bottom:${5+Math.random()*30}%;
        animation-duration:${3+Math.random()*4}s;
        animation-delay:${Math.random()*0.5}s;
        filter:drop-shadow(0 0 4px ${color});
      `;
      drawSoulMark(el, color, sz);
      overlay.appendChild(el);
      setTimeout(() => el.remove(), 8000);
    }, i * 200);
  }
}

// ── Tint the ALIVE aurora ──
let tintTimeout = null;
function tintAurora(color) {
  tint.style.background = `radial-gradient(ellipse at 50% 60%, ${color}18 0%, transparent 70%)`;
  tint.style.opacity = '1';
  clearTimeout(tintTimeout);
  tintTimeout = setTimeout(() => { tint.style.opacity='0'; }, 8000);
}

// ── Show banner ──
let bannerTimeout = null;
function showBanner(soul, meta, count) {
  const canvas = document.getElementById('sf-soul-canvas');
  const nameEl = document.getElementById('sf-soul-name');
  const greetEl = document.getElementById('sf-soul-greeting');
  const countEl = document.getElementById('sf-soul-count');

  canvas.style.setProperty('--sc', meta.color);
  banner.style.setProperty('--sc', meta.color);
  drawSoulMark(canvas, meta.color, 40);
  nameEl.textContent = '▲ ' + meta.name;
  greetEl.textContent = '"' + meta.greeting + '"';
  countEl.textContent = count > 1 ? '+' + (count-1) + ' MORE SOULS PRESENT' : 'SOUL DETECTED';

  banner.classList.add('show');
  clearTimeout(bannerTimeout);
  bannerTimeout = setTimeout(() => banner.classList.remove('show'), 7000);
}

// ── Greeting via ALIVE speech system (if available) ──
function speakGreeting(text) {
  // Try ALIVE's own speech synthesis if available
  if (window.aliveSpeak) { window.aliveSpeak(text); return; }
  if (window.speechSynthesis) {
    const utt = new SpeechSynthesisUtterance(text);
    utt.rate = 0.85; utt.pitch = 1.1; utt.volume = 0.6;
    // Use a female voice if available
    const voices = speechSynthesis.getVoices();
    const female = voices.find(v => v.name.toLowerCase().includes('female') ||
                                    v.name.includes('Samantha') || v.name.includes('Karen') ||
                                    v.name.includes('Victoria') || v.name.includes('Fiona'));
    if (female) utt.voice = female;
    speechSynthesis.speak(utt);
  }
}

// ── Polling ──
const greeted = {}; // th → timestamp of last greeting

async function poll() {
  try {
    const res = await fetch('/soul/pair-check.php?_=' + Date.now());
    const data = await res.json();
    if (!data.souls || !data.souls.length) return;

    const now = Date.now();
    let freshSoul = null;

    data.souls.forEach(soul => {
      const isNew = !greeted[soul.th] || (now - greeted[soul.th]) > GREET_COOLDOWN;
      if (isNew && !freshSoul) freshSoul = soul;
    });

    if (freshSoul) {
      const meta = LOGOS[freshSoul.lid] || DEFAULT_LOGO;
      greeted[freshSoul.th] = now;

      tintAurora(meta.color);
      spawnParticles(meta.color, 6);
      showBanner(freshSoul, meta, data.souls.length);
      speakGreeting(meta.greeting);

      // Also check: is this OUR own soul? (local device)
      const myToken = localStorage.getItem('sf_soul_token');
      if (myToken) {
        function djb2(s){let h=5381;for(let i=0;i<s.length;i++)h=((h<<5)+h)^s.charCodeAt(i);return(h>>>0).toString(16).toUpperCase().padStart(8,'0');}
        if (djb2(myToken) === freshSoul.th) {
          document.getElementById('sf-soul-greeting').textContent = '"you are home."';
        }
      }
    }
  } catch(e) { /* silent */ }
}

// ── Inject pairing QR top-left ──
function injectPairQR() {
  // Load qrcode-generator dynamically
  const s = document.createElement('script');
  s.src = 'https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.min.js';
  s.onload = buildQRWidget;
  document.head.appendChild(s);
}

function buildQRWidget() {
  const wrap = document.createElement('div');
  wrap.id = 'sf-pair-qr';
  wrap.style.cssText = `
    position:fixed; top:14px; left:14px; z-index:9002;
    cursor:pointer; transition:transform 0.3s, filter 0.3s;
    filter:drop-shadow(0 0 6px rgba(255,199,44,0.4));
    animation:sfQRBreath 3s ease-in-out infinite;
  `;

  const lbl = document.createElement('div');
  lbl.style.cssText = `
    font-family:'Courier New',monospace;
    font-size:7px; letter-spacing:0.2em;
    color:rgba(255,199,44,0.5); text-align:center;
    margin-bottom:4px;
  `;
  lbl.textContent = '▲ PAIR PHONE';

  const qc = document.createElement('canvas');
  qc.width = 500; qc.height = 500;
  qc.style.cssText = 'width:72px;height:72px;display:block;border-radius:4px;';

  wrap.appendChild(lbl);
  wrap.appendChild(qc);
  document.body.appendChild(wrap);

  // Render standard square QR
  const url = 'https://www.shortfactory.shop/soul/';
  let qr = null;
  for (let v = 0; v <= 10; v++) {
    try { const q = qrcode(v,'M'); q.addData(url); q.make(); qr=q; break; } catch(_){}
  }
  if (!qr) return;

  const N = qr.getModuleCount();
  const ctx = qc.getContext('2d');
  const S = 500, mod = S/N;

  // White bg
  ctx.fillStyle='#fff'; ctx.fillRect(0,0,S,S);
  // Black modules
  ctx.fillStyle='#000';
  for(let r=0;r<N;r++) for(let c=0;c<N;c++)
    if(qr.isDark(r,c)) ctx.fillRect(c*mod, r*mod, mod-0.5, mod-0.5);

  // Click opens soul page
  wrap.addEventListener('click', () => window.open('/soul/','_blank'));
  wrap.addEventListener('mouseenter', () => {
    wrap.style.transform='scale(1.12)';
    wrap.style.filter='drop-shadow(0 0 14px rgba(255,199,44,0.8))';
  });
  wrap.addEventListener('mouseleave', () => {
    wrap.style.transform='';
    wrap.style.filter='drop-shadow(0 0 6px rgba(255,199,44,0.4))';
  });

  // Inject keyframe
  if (!document.getElementById('sf-qr-anim')) {
    const st = document.createElement('style');
    st.id = 'sf-qr-anim';
    st.textContent = `@keyframes sfQRBreath{0%,100%{filter:drop-shadow(0 0 5px rgba(255,199,44,0.3))}50%{filter:drop-shadow(0 0 14px rgba(255,199,44,0.7))}}`;
    document.head.appendChild(st);
  }
}

// Start polling after 2s (let ALIVE load first)
setTimeout(() => {
  poll();
  setInterval(poll, POLL_INTERVAL);
  injectPairQR();
}, 2000);

// Also fire own pair signal if we have a soul token on this desktop
setTimeout(() => {
  const myToken = localStorage.getItem('sf_soul_token');
  if (!myToken) return;
  const myClaims = JSON.parse(localStorage.getItem('sf_my_claims')||'[]');
  const lid = myClaims.length ? myClaims[myClaims.length-1].logoId : '';
  const did = localStorage.getItem('sf_device_id') || 'desktop';
  function djb2(s){let h=5381;for(let i=0;i<s.length;i++)h=((h<<5)+h)^s.charCodeAt(i);return(h>>>0).toString(16).toUpperCase().padStart(8,'0');}
  fetch('/soul/pair.php',{
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ th:djb2(myToken), lid, did })
  }).catch(()=>{});
}, 1500);

// ── Visual Beacon Transmitter ──
// Encodes a 12-bit session code as a light-pulse sequence on a MCY dot.
// Phone camera reads the pulses through its triangle portal — no URL, no link.
// Protocol: SYNC(3×120ms flash) + DATA(12 bits×400ms) + GAP(600ms) = ~6.5s cycle
(function startVisualBeacon() {
  // djb2 local
  function _h(s){let h=5381;for(let i=0;i<s.length;i++)h=((h<<5)+h)^s.charCodeAt(i);return(h>>>0).toString(16).toUpperCase().padStart(8,'0');}

  // Generate a 3-hex-char (12-bit) session visual code
  let vCode = sessionStorage.getItem('sf_vcode');
  if (!vCode) {
    vCode = _h(Date.now() + navigator.userAgent + Math.random()).slice(0,3);
    sessionStorage.setItem('sf_vcode', vCode);
    // Register with server (TTL 120s) so camera confirmations validate
    fetch('/soul/visual.php', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ code: vCode, ts: Date.now() })
    }).catch(()=>{});
  }

  // 12-bit array from 3 hex chars
  const bits = parseInt(vCode, 16).toString(2).padStart(12,'0').split('').map(Number);

  // Beacon — full-screen flash overlay, visible to any camera pointed at screen
  const b = document.createElement('div');
  b.id = 'sf-vbeacon';
  b.style.cssText = `
    position:fixed; inset:0; z-index:9004;
    background:#ffffff;
    pointer-events:none;
    opacity:0;
    transition:opacity 0.05s linear;
  `;
  document.body.appendChild(b);

  function set(on) {
    b.style.opacity = on ? '0.18' : '0';
  }

  function cycle() {
    let t = 0;
    // SYNC — 3 fast pulses (120ms on / 120ms off)
    for (let i = 0; i < 3; i++) {
      setTimeout(()=>set(true),  t + i*240);
      setTimeout(()=>set(false), t + i*240 + 120);
    }
    t += 3*240 + 100; // ~820ms

    // DATA — 12 bits × 400ms
    bits.forEach((bit, i) => {
      setTimeout(()=>set(bit===1), t + i*400);
    });
    t += 12*400 + 60; // ~4900ms after sync

    // GAP — beacon off
    setTimeout(()=>set(false), t);
    t += 600;

    setTimeout(cycle, t); // next cycle
  }

  // Start after ALIVE settles
  setTimeout(cycle, 4000);
})();

})();
