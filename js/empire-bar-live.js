/**
 * empire-bar.js — persistent empire progress bar + guide
 * Drop <script src="/js/empire-bar.js"></script> on any page
 */
(function() {
  'use strict';

  const GOOGLE_CLIENT_ID = '246057462897-mui96hjeuk9abvlkgvvqdfdeiknbmojb.apps.googleusercontent.com';
  const API_BASE = '/empire';
  const MAX_FRAGMENTS = 6;

  const rooms = [
    { key:'game',        name:'The Chocolate River',      short:'THE GAME',        url:'/trump/game/',        color:'#FF6D00', icon:'🎮' },
    { key:'alive',       name:'The Inventing Room',       short:'ALIVE CREATURE',  url:'/alive/',             color:'#00E676', icon:'🫁' },
    { key:'soulforge',   name:'The Nut Room',             short:'SOUL FORGE',      url:'/dares4dosh/soulforge/', color:'#F50057', icon:'🥜' },
    { key:'cortex',      name:'The Television Room',      short:'CORTEX BRAIN',    url:'/alive/studio/',      color:'#2979FF', icon:'🧠' },
    { key:'fuel',        name:'The Fizzy Lifting Drinks', short:'FUEL DASHBOARD',  url:'/fuel/',              color:'#B967FF', icon:'🎈' },
    { key:'screensaver', name:'The Great Glass Elevator', short:'SCREENSAVER',     url:'/screensaver/',       color:'#00E5FF', icon:'🛸' }
  ];

  // ── Voice Guide (Web Speech API — swap for Chatterbox endpoint later) ──
  const Guide = {
    _synth: window.speechSynthesis || null,
    _voice: null,
    _ready: false,

    init() {
      if (!this._synth) return;
      const setVoice = () => {
        const voices = this._synth.getVoices();
        // prefer a British English or US English voice
        this._voice = voices.find(v => v.lang === 'en-GB') ||
                      voices.find(v => v.lang.startsWith('en')) ||
                      voices[0] || null;
        this._ready = true;
      };
      if (this._synth.getVoices().length) setVoice();
      else this._synth.addEventListener('voiceschanged', setVoice);
    },

    say(text, priority = false) {
      if (!this._synth || !this._ready) return;
      if (priority) this._synth.cancel();
      const u = new SpeechSynthesisUtterance(text);
      if (this._voice) u.voice = this._voice;
      u.rate = 0.95;
      u.pitch = 1.05;
      u.volume = 0.85;
      this._synth.speak(u);
    },

    // TODO: swap this method for Chatterbox TTS endpoint when ready
    // async sayClone(text) {
    //   const res = await fetch('/voice/tts.php', { method:'POST', body: JSON.stringify({text}), headers:{'Content-Type':'application/json'} });
    //   const blob = await res.blob();
    //   new Audio(URL.createObjectURL(blob)).play();
    // }
  };

  // ── Styles ──────────────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
    #empire-bar {
      position: fixed;
      bottom: 0; left: 0; right: 0;
      z-index: 99999;
      background: rgba(5,0,15,0.97);
      border-top: 2px solid #FFD700;
      font-family: 'Fredoka One','Arial Black',sans-serif;
      transition: transform 0.4s cubic-bezier(.4,0,.2,1);
    }
    #empire-bar.empire-hidden { transform: translateY(100%); }
    #empire-bar-inner {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 16px;
      max-width: 1200px;
      margin: 0 auto;
    }
    #empire-avatar {
      width: 32px; height: 32px;
      border-radius: 50%;
      border: 2px solid #FFD700;
      flex-shrink: 0;
      cursor: pointer;
      background: #1a0033;
    }
    #empire-name {
      color: #FFD700;
      font-size: 0.8rem;
      white-space: nowrap;
      flex-shrink: 0;
      min-width: 70px;
    }
    #empire-track {
      flex: 1;
      height: 18px;
      background: #1a0033;
      border-radius: 9px;
      border: 1px solid rgba(255,215,0,0.3);
      overflow: hidden;
      position: relative;
      cursor: pointer;
      min-width: 60px;
    }
    #empire-fill {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #FFD700, #FF6D00, #FF1744);
      border-radius: 9px;
      transition: width 1.2s cubic-bezier(.4,0,.2,1);
      position: relative;
    }
    #empire-fill::after {
      content: '';
      position: absolute; inset: 0;
      background: repeating-linear-gradient(90deg,transparent 0,transparent 14px,rgba(255,255,255,0.12) 14px,rgba(255,255,255,0.12) 16px);
      animation: empireStripe 1s linear infinite;
    }
    @keyframes empireStripe { from{background-position:0} to{background-position:16px} }

    #empire-pct {
      color: #FFD700;
      font-size: 0.85rem;
      white-space: nowrap;
      flex-shrink: 0;
      min-width: 38px;
      text-align: right;
    }

    #empire-signin-btn {
      background: linear-gradient(135deg,#FFD700,#FF6D00);
      color: #0a0008;
      border: none;
      border-radius: 20px;
      padding: 6px 16px;
      font-family: inherit;
      font-size: 0.8rem;
      font-weight: bold;
      cursor: pointer;
      flex-shrink: 0;
      white-space: nowrap;
      letter-spacing: 1px;
      animation: btnPulse 2s ease-in-out infinite;
    }
    @keyframes btnPulse {
      0%,100%{box-shadow:0 0 8px rgba(255,215,0,0.4);}
      50%{box-shadow:0 0 20px rgba(255,215,0,0.9),0 0 40px rgba(255,109,0,0.4);}
    }
    #empire-signin-btn:hover { filter: brightness(1.15); }

    /* FRAGMENT DOTS */
    #empire-fragments-row { display:flex; gap:5px; flex-shrink:0; position:relative; }
    .empire-frag {
      width: 14px; height: 14px;
      border-radius: 3px;
      border: 1px solid rgba(255,255,255,0.15);
      background: #1a0033;
      cursor: pointer;
      position: relative;
      transition: all 0.3s;
    }
    .empire-frag.earned {
      background: var(--fc);
      box-shadow: 0 0 6px var(--fc);
      border-color: var(--fc);
    }
    .empire-frag.next-room {
      animation: nextFlash 0.8s ease-in-out infinite;
      border-color: #FFD700 !important;
      cursor: pointer;
    }
    @keyframes nextFlash {
      0%,100%{box-shadow:0 0 4px rgba(255,215,0,0.4);transform:scale(1);}
      50%{box-shadow:0 0 14px rgba(255,215,0,1),0 0 28px rgba(255,215,0,0.5);transform:scale(1.3);}
    }

    /* NEXT ROOM PILL */
    #empire-next-pill {
      display: none;
      align-items: center;
      gap: 6px;
      background: rgba(255,215,0,0.12);
      border: 1px solid rgba(255,215,0,0.4);
      border-radius: 20px;
      padding: 4px 12px;
      font-size: 0.72rem;
      color: #FFD700;
      white-space: nowrap;
      flex-shrink: 0;
      cursor: pointer;
      animation: pillGlow 2s ease-in-out infinite;
      text-decoration: none;
      max-width: 160px;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    #empire-next-pill.visible { display:flex; }
    @keyframes pillGlow {
      0%,100%{border-color:rgba(255,215,0,0.4);background:rgba(255,215,0,0.08);}
      50%{border-color:rgba(255,215,0,0.9);background:rgba(255,215,0,0.2);}
    }
    .pill-arrow {
      font-size: 0.9rem;
      animation: arrowBounce 0.8s ease-in-out infinite;
    }
    @keyframes arrowBounce {
      0%,100%{transform:translateX(0);}
      50%{transform:translateX(3px);}
    }

    /* TOAST */
    #empire-toast {
      position: fixed;
      bottom: 70px; left: 50%;
      transform: translateX(-50%) translateY(20px);
      background: rgba(5,0,15,0.97);
      border: 2px solid #FFD700;
      border-radius: 12px;
      padding: 14px 24px;
      color: #FFD700;
      font-family: 'Fredoka One','Arial Black',sans-serif;
      font-size: 1rem;
      text-align: center;
      z-index: 100000;
      opacity: 0;
      transition: opacity 0.4s, transform 0.4s;
      pointer-events: none;
      max-width: 90vw;
    }
    #empire-toast.show { opacity:1; transform:translateX(-50%) translateY(0); }

    /* PANEL */
    #empire-panel {
      position: fixed;
      bottom: 70px; left: 50%;
      transform: translateX(-50%) scale(0.95);
      background: rgba(5,0,15,0.99);
      border: 2px solid #FFD700;
      border-radius: 16px;
      padding: 24px;
      z-index: 100000;
      width: 340px;
      max-width: 95vw;
      display: none;
      box-shadow: 0 0 60px rgba(255,215,0,0.3);
    }
    #empire-panel.show { display:block; }
    .ep-title { font-family:'Fredoka One','Arial Black',sans-serif; color:#FFD700; font-size:1.1rem; margin-bottom:16px; text-align:center; }
    .ep-frag-list { list-style:none; padding:0; margin:0 0 16px; }
    .ep-frag-list li {
      display:flex; align-items:center; gap:10px;
      padding:10px 0;
      border-bottom:1px solid rgba(255,255,255,0.08);
      font-family:sans-serif; font-size:0.8rem; color:#aaa;
      cursor: pointer;
      transition: background 0.2s;
      border-radius: 6px;
      padding-left: 6px;
    }
    .ep-frag-list li:hover { background: rgba(255,255,255,0.04); }
    .ep-frag-list li.ep-earned { color:#fff; }
    .ep-frag-list li.ep-next { color:#FFD700; }
    .ep-frag-list li.ep-next .ep-dot { animation: nextFlash 0.8s ease-in-out infinite; }
    .ep-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
    .ep-room-icon { font-size:1.1rem; flex-shrink:0; }
    .ep-room-info { flex:1; }
    .ep-room-name { font-size:0.82rem; }
    .ep-room-status { font-size:0.65rem; opacity:0.6; margin-top:2px; }
    .ep-arrow { font-size:0.8rem; opacity:0.5; }
    .ep-signout {
      width:100%; background:rgba(255,255,255,0.05);
      border:1px solid rgba(255,255,255,0.2); color:#aaa;
      border-radius:8px; padding:8px; cursor:pointer;
      font-family:inherit; font-size:0.8rem; margin-top:4px;
    }
    .ep-signout:hover { background:rgba(255,0,0,0.2); color:#fff; }

    /* GUIDE BUBBLE */
    #empire-guide-bubble {
      position: fixed;
      bottom: 70px; right: 20px;
      background: rgba(5,0,15,0.97);
      border: 2px solid #FFD700;
      border-radius: 16px 16px 4px 16px;
      padding: 12px 18px;
      max-width: 260px;
      font-family: 'Fredoka One','Arial Black',sans-serif;
      font-size: 0.85rem;
      color: #FFD700;
      z-index: 100000;
      opacity: 0;
      transform: translateY(10px);
      transition: opacity 0.4s, transform 0.4s;
      pointer-events: none;
      line-height: 1.5;
    }
    #empire-guide-bubble.show { opacity:1; transform:translateY(0); }
    #empire-guide-bubble::after {
      content: '🎩';
      position: absolute;
      bottom: -18px; right: 10px;
      font-size: 1.4rem;
    }

    @media(max-width:600px) {
      #empire-next-pill { max-width:100px; font-size:0.65rem; }
      #empire-name { min-width:50px; font-size:0.7rem; }
    }
  `;
  document.head.appendChild(style);

  // ── DOM ─────────────────────────────────────────────────────────────
  const bar = document.createElement('div');
  bar.id = 'empire-bar';
  bar.innerHTML = `
    <div id="empire-bar-inner">
      <img id="empire-avatar" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='16' fill='%231a0033'/%3E%3Ccircle cx='16' cy='12' r='6' fill='%23FFD700'/%3E%3Cellipse cx='16' cy='26' rx='10' ry='7' fill='%23FFD700'/%3E%3C/svg%3E" alt="you" title="Your empire">
      <span id="empire-name">SIGN IN</span>
      <div id="empire-track" title="Your journey to the factory">
        <div id="empire-fill"></div>
      </div>
      <span id="empire-pct">0%</span>
      <div id="empire-fragments-row"></div>
      <a id="empire-next-pill" href="#" title="Next room">
        <span class="pill-arrow">▶</span>
        <span id="empire-next-label">START HERE</span>
      </a>
      <div id="empire-google-btn-wrap" style="flex-shrink:0"></div>
      <button id="empire-signin-btn" style="display:none">🎫 ENTER</button>
    </div>
  `;

  const toast    = document.createElement('div'); toast.id = 'empire-toast';
  const panel    = document.createElement('div'); panel.id = 'empire-panel';
  const bubble   = document.createElement('div'); bubble.id = 'empire-guide-bubble';

  document.body.appendChild(toast);
  document.body.appendChild(panel);
  document.body.appendChild(bubble);
  document.body.appendChild(bar);

  // ── State ────────────────────────────────────────────────────────────
  let state = { user: null, fragments: [], percent: 0 };
  let panelOpen = false;
  let bubbleTimer = null;

  // ── Guide Bubble ─────────────────────────────────────────────────────
  function showBubble(msg, duration = 5000) {
    bubble.innerHTML = msg;
    bubble.classList.add('show');
    clearTimeout(bubbleTimer);
    bubbleTimer = setTimeout(() => bubble.classList.remove('show'), duration);
  }

  // ── Guide Voice ──────────────────────────────────────────────────────
  function guideSpeak(text, priority = false) {
    Guide.say(text, priority);
    showBubble(text);
  }

  // ── Next Room Logic ──────────────────────────────────────────────────
  function getNextRoom() {
    const earned = state.fragments.map(f => f.room_key);
    return rooms.find(r => !earned.includes(r.key)) || null;
  }

  // ── Render ───────────────────────────────────────────────────────────
  function render() {
    const fill     = document.getElementById('empire-fill');
    const pct      = document.getElementById('empire-pct');
    const name     = document.getElementById('empire-name');
    const avatar   = document.getElementById('empire-avatar');
    const btn      = document.getElementById('empire-signin-btn');
    const fragsRow = document.getElementById('empire-fragments-row');
    const pill     = document.getElementById('empire-next-pill');
    const pillLbl  = document.getElementById('empire-next-label');

    const p = Math.round((state.percent / MAX_FRAGMENTS) * 100);
    fill.style.width = p + '%';
    pct.textContent = p + '%';

    const gWrap = document.getElementById('empire-google-btn-wrap');
    if (state.user) {
      name.textContent = (state.user.name || state.user.email).split(' ')[0].toUpperCase();
      if (state.user.avatar) avatar.src = state.user.avatar;
      btn.style.display = 'none';
      if (gWrap) gWrap.style.display = 'none';
    } else {
      name.textContent = 'SIGN IN';
      btn.style.display = 'none';
      if (gWrap) gWrap.style.display = '';
      pill.classList.remove('visible');
    }

    // Fragment dots
    fragsRow.innerHTML = '';
    const next = getNextRoom();
    rooms.forEach(r => {
      const earned = state.fragments.find(f => f.room_key === r.key);
      const dot = document.createElement('div');
      dot.className = 'empire-frag' + (earned ? ' earned' : '') + (!earned && r === next && state.user ? ' next-room' : '');
      dot.style.setProperty('--fc', r.color);
      dot.title = r.name + (earned ? ' ✓' : r === next ? ' ← GO HERE' : ' — locked');
      dot.onclick = () => { if (!earned && r === next) window.location.href = r.url; else togglePanel(); };
      fragsRow.appendChild(dot);
    });

    // Next pill
    if (state.user && next && p < 100) {
      pill.classList.add('visible');
      pill.href = next.url;
      pillLbl.textContent = next.icon + ' ' + next.short;
      pill.style.borderColor = next.color;
      pill.style.color = next.color;
    } else if (p >= 100) {
      pill.classList.add('visible');
      pill.href = '/factory.html';
      pillLbl.textContent = '🏭 YOUR FACTORY';
      pill.style.borderColor = '#FFD700';
      pill.style.color = '#FFD700';
    } else {
      pill.classList.remove('visible');
    }
  }

  // ── Toast ─────────────────────────────────────────────────────────────
  let toastTimer;
  function showToast(msg, duration = 3500) {
    toast.innerHTML = msg;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), duration);
  }

  // ── Panel ─────────────────────────────────────────────────────────────
  function togglePanel() {
    if (!state.user) return;
    panelOpen = !panelOpen;
    if (panelOpen) {
      const next = getNextRoom();
      panel.innerHTML = `
        <div class="ep-title">🎩 YOUR FACTORY JOURNEY</div>
        <ul class="ep-frag-list">
          ${rooms.map(r => {
            const f = state.fragments.find(x => x.room_key === r.key);
            const isNext = !f && r === next;
            return `<li class="${f ? 'ep-earned' : ''} ${isNext ? 'ep-next' : ''}" onclick="window.location.href='${r.url}'">
              <div class="ep-dot" style="background:${f ? r.color : isNext ? r.color : '#333'};box-shadow:${f || isNext ? '0 0 6px '+r.color : 'none'}"></div>
              <span class="ep-room-icon">${r.icon}</span>
              <div class="ep-room-info">
                <div class="ep-room-name">${r.name}</div>
                <div class="ep-room-status">${f ? '✓ Fragment earned' : isNext ? '← GO HERE NEXT' : 'Not yet earned'}</div>
              </div>
              <span class="ep-arrow">${isNext ? '▶' : f ? '✓' : '🔒'}</span>
            </li>`;
          }).join('')}
        </ul>
        <button class="ep-signout" id="ep-signout-btn">Sign out</button>
      `;
      panel.classList.add('show');
      document.getElementById('ep-signout-btn').onclick = signOut;
    } else {
      panel.classList.remove('show');
    }
  }

  // ── API ────────────────────────────────────────────────────────────────
  async function loadMe() {
    try {
      const r = await fetch(API_BASE + '/auth.php?me=1', { credentials:'include' });
      const d = await r.json();
      state = { user: d.user, fragments: d.fragments || [], percent: d.percent || 0 };
      render();
      if (state.user) {
        const next = getNextRoom();
        if (next) {
          setTimeout(() => guideSpeak(`Welcome back! Your next room is ${next.name}. ${next.icon}`, false), 1500);
        } else if (state.percent >= MAX_FRAGMENTS) {
          setTimeout(() => guideSpeak('You have collected all fragments. Your empire awaits!', false), 1500);
        }
      }
    } catch(e) {}
  }

  async function loginWithToken(token) {
    try {
      const r = await fetch(API_BASE + '/auth.php', {
        method:'POST', credentials:'include',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ token })
      });
      const d = await r.json();
      if (d.ok) {
        const wasNew = d.fragments.length === 0;
        state = { user: d.user, fragments: d.fragments || [], percent: d.percent || 0 };
        render();
        const firstName = d.user.name.split(' ')[0];
        const next = getNextRoom();
        if (wasNew) {
          showToast(`🎫 Welcome to the factory, <strong>${firstName}</strong>!`);
          setTimeout(() => guideSpeak(
            `Welcome ${firstName}! I am your guide. You are at zero percent. Your first room is ${next ? next.name : 'the game'}. Find it at the bottom of the screen and click the flashing light.`, true
          ), 600);
        } else {
          showToast(`🎩 Welcome back, <strong>${firstName}</strong>! ${state.percent}% complete.`);
          setTimeout(() => guideSpeak(
            `Welcome back ${firstName}! You are at ${Math.round((state.percent/MAX_FRAGMENTS)*100)} percent. ${next ? 'Your next room is ' + next.name : 'You have completed all rooms!'}`, true
          ), 600);
        }
      }
    } catch(e) {}
  }

  async function signOut() {
    panel.classList.remove('show');
    panelOpen = false;
    await fetch(API_BASE + '/auth.php?logout=1', { credentials:'include' });
    state = { user:null, fragments:[], percent:0 };
    render();
  }

  // ── Public API ────────────────────────────────────────────────────────
  window.EmpireFactory = {
    award: async function(roomKey) {
      if (!state.user) {
        showToast('🎫 Sign in to earn your fragment!');
        guideSpeak('You need to sign in first. Look for the enter button.');
        return;
      }
      try {
        const r = await fetch(API_BASE + '/progress.php', {
          method:'POST', credentials:'include',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ room: roomKey })
        });
        const d = await r.json();
        if (d.already_earned) return;
        if (d.ok) {
          state.fragments = d.fragments;
          state.percent   = d.percent;
          render();
          const room = rooms.find(r => r.key === roomKey);
          const pct  = Math.round((d.percent / MAX_FRAGMENTS) * 100);
          const next = getNextRoom();

          showToast(`🔑 Fragment #${d.position} unlocked!<br><strong>${d.room_name}</strong><br>Empire: ${pct}%`, 5000);

          setTimeout(() => {
            if (d.percent >= MAX_FRAGMENTS) {
              guideSpeak(`Incredible! You have collected all six fragments! Your empire is one hundred percent complete. The factory is yours!`, true);
            } else if (next) {
              guideSpeak(`Excellent! Fragment ${d.position} earned. You are at ${pct} percent. Your next room is ${next.name}. Keep going!`, true);
            }
          }, 800);
        }
      } catch(e) {}
    },
    getState:   () => state,
    isLoggedIn: () => !!state.user,
    guideSpeak
  };

  // ── Google Sign-In ─────────────────────────────────────────────────────
  function initGoogle() {
    if (typeof google === 'undefined' || !google.accounts) return;
    google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: (res) => loginWithToken(res.credential),
      auto_select: false,
      use_fedcm_for_prompt: false
    });
    // Render the official Google button — much more reliable than prompt()
    const wrap = document.getElementById('empire-google-btn-wrap');
    if (wrap && !state.user) {
      google.accounts.id.renderButton(wrap, {
        type: 'standard',
        theme: 'filled_black',
        size: 'small',
        text: 'signin',
        shape: 'pill',
        logo_alignment: 'left'
      });
    }
  }

  document.getElementById('empire-track').onclick  = togglePanel;
  document.getElementById('empire-avatar').onclick = togglePanel;

  document.addEventListener('click', (e) => {
    if (panelOpen &&
        !panel.contains(e.target) &&
        !document.getElementById('empire-track').contains(e.target) &&
        !document.getElementById('empire-avatar').contains(e.target)) {
      panel.classList.remove('show');
      panelOpen = false;
    }
  });

  // ── Boot ───────────────────────────────────────────────────────────────
  function boot() {
    Guide.init();
    loadMe();
    if (!document.querySelector('script[src*="accounts.google.com/gsi"]')) {
      const s = document.createElement('script');
      s.src = 'https://accounts.google.com/gsi/client';
      s.async = true;
      s.onload = initGoogle;
      document.head.appendChild(s);
    } else {
      setTimeout(initGoogle, 100);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

})();
