/**
 * Game Autopilot + Dual Progress Bars — Trump v Deep State
 * Left bars: WHITE = empire progress (fragments/6), RED = room 1 purity
 * Auto-starts if ap_autostart flag set in localStorage (from dev login)
 *
 * GAME MECHANICS (from config.js ACTIONS):
 *   oil:   p:0,  ds:0,   cash:+500  — earns money only, NO purity
 *   home:  p:+5, ds:-5,  cash:-200  — BUILDS purity + reduces deep state
 *   psyop: p:0,  ds:-8,  cash:-300  — reduces deep state + feminism
 *   audit: p:0,  ds:-15, trumpHP:-5, cash:0 — biggest DS reducer, free, costs trump HP
 *   war:   p:-5, ds:0,   cash:-300  — REDUCES PURITY (never use near win!)
 *   drone: p:-3, ds:0,   cash:-400  — REDUCES PURITY (never use near win!)
 *   loan:  p:0,  ds:0,   cash:+1000 — emergency cash
 *   aid:   p:0,  ds:0,   cash:0     — reduces debt + israelGDP
 *
 * WIN:  purity >= 97%
 * LOSE: trumpHP<=0 | deepStateHP>=100 | purity<=0 | impeach>=3
 */
(function() {
  'use strict';

  let running    = false;
  let tickTimer  = null;
  let idleCount  = 0;
  let barPurityFill, barEmpireFill, barPurityPct, barEmpirePct, bubbleEl;

  const SPEED = { think: 800, click: 400, idle: 1400 };

  // ── BRAIN ────────────────────────────────────────────────────────────
  function think() {
    if (!running) return;
    // Menu still up — dismiss it then wait for game to fully initialise
    if (isStartOverlayUp()) { isModalOpen(); schedule(2000); return; }
    if (typeof G === 'undefined') { bubble('Waiting for game...'); schedule(SPEED.idle); return; }
    if (isModalOpen()) { schedule(SPEED.idle); return; }

    const s = snap();

    // Mean tweet mode — always handle immediately
    if (s.tweet) {
      const btn = document.querySelector('.tweet-option:not([disabled])');
      if (btn) { act('📣 Tweet!', btn); return; }
    }

    // Sell barrels before deciding anything else — barrels != cash
    if (s.barrels > 0 && trySellOil(s)) return;

    // Roll for more moves when low
    if (s.moves <= 1) {
      const pill = document.getElementById('pill-moves');
      if (pill && pill.classList.contains('clickable')) { act('🎲 Roll for moves', pill); return; }
    }

    if (s.moves <= 0) { schedule(SPEED.idle); return; }

    const action = pickAction(s);
    if (action) { act('🤖 ' + action.label, action.el); return; }

    idleCount++;
    if (idleCount > 8) { bubble('Thinking...'); idleCount = 0; }
    schedule(SPEED.idle);
  }

  function snap() {
    return {
      purity:   Math.round(G.purity      || 0),
      moves:    G.moves                  || 0,
      muslim:   G.muslimThreat           || 0,
      feminism: G.feminism               || 0,
      oil:      G.oilCash                || 0,
      barrels:  G.oilBarrels             || 0,   // unsold barrels sitting in the pile
      dsHP:     G.deepStateHP            || 0,
      trumpHP:  G.trumpHP                || 100,
      tweet:    G.meanTweetMode          || false
    };
  }

  // Click the oil sell button if barrels are sitting unsold
  function trySellOil(s) {
    if (s.barrels <= 0) return false;
    const sellBtn = document.getElementById('oil-sell-button');
    if (sellBtn && isVisible(sellBtn)) {
      act('💰 Sell ' + s.barrels + ' barrels!', sellBtn);
      return true;
    }
    return false;
  }

  // ── STRATEGY ─────────────────────────────────────────────────────────
  // Core logic: home builds purity (+5 each use). That is the win path.
  // war/drone DRAIN purity — never use when near the 97% finish line.
  // audit is the best deepState reducer (-15) and is free.
  // oil/loan are only for getting cash to afford home/psyop.
  function pickAction(s) {
    const btns = Array.from(document.querySelectorAll('.game-btn:not(.locked):not([disabled])'))
      .filter(isVisible);
    if (!btns.length) return null;

    const nearWin   = s.purity >= 75;   // stop using purity-draining moves
    const canHome   = s.oil >= 200;     // home costs $200
    const canPsyop  = s.oil >= 300;     // psyop costs $300
    const trumpSafe = s.trumpHP > 30;   // safe to use audit (costs 5 trumpHP)
    const dsUrgent  = s.dsHP >= 80;     // deep state dangerously high
    const dsCritical = s.dsHP >= 92;    // about to lose to deep state

    return btns.map(btn => {
      const a = btn.dataset.action;
      let score = 1, label = a;
      switch(a) {

        // HOME: only purity builder (+5 purity, -5 DS). ALWAYS prioritise.
        case 'home':
          if (!canHome) { score = 0; break; }
          score = 12;  // highest baseline — this is the win button
          if (s.dsHP > 70) score += 2;    // extra urgent when DS high
          label = 'Build purity 🏠'; break;

        // AUDIT: -15 deepState for free. Best DS move but costs trumpHP.
        case 'audit':
          if (!trumpSafe && !dsCritical) { score = 1; break; }
          score = dsCritical ? 11 : (dsUrgent ? 8 : (s.dsHP > 50 ? 5 : 3));
          label = 'Audit DS 📋'; break;

        // PSYOP: -8 deepState, costs $300. Good secondary DS move.
        case 'psyop':
          if (!canPsyop) { score = 0; break; }
          score = dsCritical ? 9 : (dsUrgent ? 7 : (s.dsHP > 50 ? 5 : 3));
          label = 'Psyop 📺'; break;

        // OIL: earns $500, no purity. Only pump to afford home/psyop.
        case 'oil':
          score = !canHome ? 8 : (s.oil < 1000 ? 5 : 2);
          label = 'Pump oil 🛢️'; break;

        // LOAN: $1000 but adds debt. Emergency only.
        case 'loan':
          score = !canHome && s.oil < 500 ? 6 : 1;
          label = 'Take loan 💵'; break;

        // AID: reduces israelGDP + debt. Low priority.
        case 'aid':
          score = 2;
          label = 'Cut aid ✈️'; break;

        // WAR: REDUCES purity by 5! Never use when purity > 60.
        // Only if muslim threat is extreme and we're safely below win threshold.
        case 'war':
          if (nearWin || s.purity > 60) { score = 0; break; }
          score = s.muslim > 75 ? 4 : 1;
          label = 'Military ⚔️'; break;

        // DRONE: REDUCES purity by 3! Same restriction as war.
        case 'drone':
          if (nearWin || s.purity > 65) { score = 0; break; }
          score = s.muslim > 80 ? 3 : 1;
          label = 'Drone 🎯'; break;

        default: score = 1; label = a;
      }
      return { el: btn, score: score + Math.random() * 0.3, label };
    }).sort((a,b) => b.score - a.score)[0] || null;
  }

  function isVisible(el) {
    let p = el;
    while (p) {
      const s = window.getComputedStyle(p);
      if (s.display === 'none' || s.visibility === 'hidden') return false;
      p = p.parentElement;
    }
    return true;
  }

  // ── ACT ──────────────────────────────────────────────────────────────
  function act(label, el) {
    idleCount = 0;
    bubble(label);
    flash(el);
    if (window.GameDNA) window.GameDNA.log('AI_CLICK', { label });
    setTimeout(() => { try { el.click(); } catch(e) {} schedule(SPEED.think); }, SPEED.click);
  }

  function flash(el) {
    if (!el) return;
    el.style.outline   = '4px solid #ff0';
    el.style.transform = 'scale(1.18)';
    el.style.zIndex    = '99999';
    setTimeout(() => { el.style.outline = ''; el.style.transform = ''; el.style.zIndex = ''; }, 450);
  }

  // ── MODALS ───────────────────────────────────────────────────────────

  // Check if game start overlay is still up (blocks everything, z-index 99999)
  function isStartOverlayUp() {
    const el = document.getElementById('game-start-overlay');
    return el && !el.classList.contains('hidden');
  }

  function dismissStartOverlay() {
    const el = document.getElementById('game-start-overlay');
    if (!el) return;
    bubble('Clicking menu to start... 🎮');
    setTimeout(() => { try { el.click(); } catch(e) {} }, 800);
  }

  function isModalOpen() {
    // Start overlay must be checked first — it sits at z-index 99999 above everything
    if (isStartOverlayUp()) { dismissStartOverlay(); return true; }

    const ids = ['hs-ticket-modal','hs-hall-of-charlies','hs-welcome-flash',
                 'litigation-overlay','emergency-overlay','ending-overlay',
                 'trump-card-overlay','wheel-overlay','blackops-overlay',
                 'powerup-tap-overlay','stock-market-overlay'];
    for (const id of ids) {
      const el = document.getElementById(id);
      if (el && (el.classList.contains('active') ||
          el.style.display === 'flex' || el.style.display === 'block')) {
        dismiss(id); return true;
      }
    }

    // Deep state popup
    const dsPop = document.getElementById('ds-popup');
    if (dsPop && dsPop.style.display !== 'none' && dsPop.offsetParent !== null) {
      setTimeout(() => { const b = document.querySelector('.popup-close-btn'); if(b) b.click(); }, 1500);
      return true;
    }

    return false;
  }

  function dismiss(id) {
    if (id === 'hs-ticket-modal') {
      setTimeout(() => { const b = document.querySelector('.hs-decline-btn'); if(b){bubble('Skipping entry...');b.click();} }, 2000);
    }
    if (id === 'hs-hall-of-charlies') {
      setTimeout(() => { const b = document.querySelector('.hs-hall-close-btn'); if(b){bubble('Closing board...');b.click();} }, 3000);
    }
    if (id === 'trump-card-overlay' || id === 'wheel-overlay' || id === 'blackops-overlay' ||
        id === 'powerup-tap-overlay' || id === 'stock-market-overlay') {
      // These overlays need a tap/click to continue
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) { bubble('Tapping overlay...'); el.click(); }
      }, 1500);
    }
  }

  function schedule(ms) { clearTimeout(tickTimer); if (running) tickTimer = setTimeout(think, ms); }

  // ── START / STOP ─────────────────────────────────────────────────────
  function start() {
    running = true;
    updateBtn();
    bubble('AI taking control 🎩');
    if (window.GameDNA) window.GameDNA.log('AUTOPILOT_ON', null);
    if (barPurityFill) barPurityFill.style.background = 'rgba(255,30,30,0.9)';
    schedule(SPEED.think);
  }

  function stop() {
    running = false;
    clearTimeout(tickTimer);
    updateBtn();
    bubble('You have control.');
    if (window.GameDNA) window.GameDNA.log('AUTOPILOT_OFF', null);
    if (barPurityFill) barPurityFill.style.background = 'rgba(200,200,200,0.7)';
  }

  function toggle() { running ? stop() : start(); }

  function updateBtn() {
    const btn = document.getElementById('ap-toggle-btn');
    if (!btn) return;
    if (running) {
      btn.innerHTML = '⏹<br>STOP<br>AI';
      btn.style.background   = '#c00';
      btn.style.borderColor  = '#f55';
      btn.style.color        = '#fff';
    } else {
      btn.innerHTML = '🤖<br>AUTO<br>PLAY';
      btn.style.background   = 'linear-gradient(180deg,#6b2fa0,#9b4fcc)';
      btn.style.borderColor  = '#9b4fcc';
      btn.style.color        = '#fff';
    }
  }

  // ── BARS UPDATE ──────────────────────────────────────────────────────
  function updateBars() {
    if (typeof G !== 'undefined') {
      const purity = Math.min(100, Math.max(0, Math.round(G.purity || 0)));
      if (barPurityFill) barPurityFill.style.height = purity + '%';
      if (barPurityPct)  barPurityPct.textContent   = purity + '%';
    }

    // White bar = empire fragments earned (0-6 rooms = 0-100%)
    let empPct = 0;
    try {
      if (window.EmpireFactory && window.EmpireFactory._state) {
        empPct = Math.round((window.EmpireFactory._state.percent || 0) / 6 * 100);
      } else {
        const dots = document.querySelectorAll('.ef-dot.earned');
        empPct = Math.round((dots.length / 6) * 100);
      }
    } catch(e) {}
    if (barEmpireFill) barEmpireFill.style.height = empPct + '%';
    if (barEmpirePct)  barEmpirePct.textContent   = empPct + '%';
  }

  function bubble(text) {
    if (!bubbleEl) return;
    bubbleEl.textContent = text;
    bubbleEl.style.opacity = '1';
    clearTimeout(bubbleEl._t);
    bubbleEl._t = setTimeout(() => { bubbleEl.style.opacity = '0'; }, 3500);
  }

  // ── BIND UI ───────────────────────────────────────────────────────────
  function injectUI() {
    barEmpireFill = document.getElementById('ap-empire-fill');
    barPurityFill = document.getElementById('ap-purity-fill');
    barEmpirePct  = document.getElementById('ap-empire-pct');
    barPurityPct  = document.getElementById('ap-purity-pct');
    bubbleEl      = document.getElementById('ap-bubble');
    setInterval(updateBars, 800);
  }

  // ── INIT ─────────────────────────────────────────────────────────────
  function init() {
    injectUI();
    window.GameAutopilot = { start, stop, toggle };

    try {
      if (localStorage.getItem('ap_autostart') === '1') {
        localStorage.removeItem('ap_autostart');
        setTimeout(start, 1500);
        console.log('🤖 Auto-start triggered by dev login');
      }
    } catch(e) {}

    console.log('🤖 Autopilot ready — strategy: home > audit > psyop > oil/loan — never war/drone near win');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    setTimeout(init, 900);
  }

})();
