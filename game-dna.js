/**
 * GameDNA — Session Recorder for Trump v Deep State
 * Records every action, state change, and event as a timestamped DNA strand.
 * Paste the DNA to Wonka and he'll know exactly what broke and when.
 */
(function() {
  'use strict';

  const DNA = {
    version: '1.0',
    session: Date.now(),
    strand: [],
    _t0: Date.now(),

    // Record an event
    log(event, data) {
      const entry = {
        ms: Date.now() - this._t0,   // ms since game load
        e: event,
        d: data || null
      };
      this.strand.push(entry);
      // Keep last 2000 events max to avoid memory bloat
      if (this.strand.length > 2000) this.strand.shift();
      this._save();
    },

    // Snapshot current G state (key fields only)
    snap() {
      if (typeof G === 'undefined') return null;
      return {
        purity:    Math.round(G.purity),
        trumpHP:   Math.round(G.trumpHP),
        dsHP:      Math.round(G.deepStateHP),
        impeach:   G.impeachmentCount || 0,
        round:     G.round || 0,
        moves:     G.moves,
        oilCash:   G.oilCash || 0,
        muslim:    G.muslimThreat || 0,
        feminist:  G.feministThreat || 0
      };
    },

    // Save to localStorage
    _save() {
      try {
        localStorage.setItem('gameDNA', JSON.stringify({
          version: this.version,
          session: this.session,
          strand: this.strand
        }));
      } catch(e) {}
    },

    // Load previous session
    load() {
      try {
        const raw = localStorage.getItem('gameDNA');
        if (raw) {
          const d = JSON.parse(raw);
          // Only restore if same session
          if (d.session === this.session) {
            this.strand = d.strand || [];
          }
        }
      } catch(e) {}
    },

    // Serialise to shareable string (base64)
    export() {
      const payload = JSON.stringify({
        version: this.version,
        session: this.session,
        ua: navigator.userAgent.slice(0,80),
        strand: this.strand
      });
      return btoa(unescape(encodeURIComponent(payload)));
    },

    // Copy DNA to clipboard
    copy() {
      const str = this.export();
      if (navigator.clipboard) {
        navigator.clipboard.writeText(str).then(() => {
          console.log('🧬 DNA copied to clipboard (' + this.strand.length + ' events)');
          _dnaToast('🧬 DNA copied! Paste to Wonka.');
        });
      } else {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = str;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        _dnaToast('🧬 DNA copied! Paste to Wonka.');
      }
    },

    // Post DNA to server silently
    async report(trigger) {
      try {
        await fetch('/trump/game/dna-report.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            trigger,
            session: this.session,
            strand: this.strand,
            ua: navigator.userAgent.slice(0, 80)
          })
        });
      } catch(e) {}
    }
  };

  function _dnaToast(msg) {
    let t = document.getElementById('dna-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'dna-toast';
      t.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#111;border:2px solid #f5c518;color:#f5c518;font-family:"Press Start 2P",monospace;font-size:8px;padding:10px 16px;z-index:999999;border-radius:4px;transition:opacity 0.4s;pointer-events:none;';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = '1';
    clearTimeout(t._tid);
    t._tid = setTimeout(() => { t.style.opacity = '0'; }, 2500);
  }

  // ── HOOKS ────────────────────────────────────────────────────────────

  // Wait for game to be ready, then hook in
  function hookGame() {
    DNA.log('SESSION_START', { url: location.href });

    // Hook purity changes via polling (every 2s — light touch)
    let lastPurity = -1;
    setInterval(() => {
      if (typeof G === 'undefined') return;
      const p = Math.round(G.purity);
      if (p !== lastPurity) {
        DNA.log('PURITY_CHANGE', { from: lastPurity, to: p, snap: DNA.snap() });
        lastPurity = p;
        // Key milestones get extra detail
        if ([97,98,99,100].includes(p)) {
          DNA.log('PURITY_MILESTONE', { purity: p, snap: DNA.snap() });
        }
      }
    }, 2000);

    // Hook all action buttons
    const actionButtons = [
      'btn-oil', 'btn-war', 'btn-nuke', 'btn-tweet', 'btn-drill',
      'btn-wall', 'btn-tariff', 'btn-deport', 'btn-audit', 'btn-space'
    ];
    actionButtons.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('click', () => {
          DNA.log('ACTION', { btn: id, snap: DNA.snap() });
        }, true);
      }
    });

    // Hook audio failures globally
    document.addEventListener('error', (e) => {
      if (e.target && (e.target.tagName === 'AUDIO' || e.target.tagName === 'VIDEO')) {
        DNA.log('AUDIO_ERROR', { src: (e.target.src||'').split('/').pop(), tag: e.target.tagName });
      }
    }, true);

    // Hook localStorage saves (state.js calls safeSetLocal)
    const _origSetItem = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function(key, value) {
      if (key === 'trumpGameSave') {
        try {
          const g = JSON.parse(value);
          DNA.log('GAME_SAVE', {
            purity: g.purity, trumpHP: g.trumpHP,
            deepStateHP: g.deepStateHP, round: g.round
          });
        } catch(e) {}
      }
      return _origSetItem(key, value);
    };

    DNA.log('HOOKS_READY', null);
  }

  // Hook startFinale
  function hookFinale() {
    const _orig = window.startFinale;
    if (typeof _orig === 'function') {
      window.startFinale = function() {
        DNA.log('FINALE_START', { snap: DNA.snap() });
        return _orig.apply(this, arguments);
      };
    }

    // Hook showNameEntry
    const _origSNE = window.showNameEntry;
    if (typeof _origSNE === 'function') {
      window.showNameEntry = function(purity) {
        DNA.log('WONKA_ENTRY_SHOWN', { purity, snap: DNA.snap() });
        return _origSNE.apply(this, arguments);
      };
    }

    // Hook finaleActive watching
    if (typeof finaleActive !== 'undefined') {
      DNA.log('FINALE_ACTIVE_CHECK', { finaleActive });
    }

    DNA.log('FINALE_HOOKS_READY', null);
  }

  // Wait for DOM + game init
  function init() {
    // Pick up factory2 handoff if present
    try {
      const handoff = localStorage.getItem('dnaHandoff');
      if (handoff) {
        const h = JSON.parse(handoff);
        // Merge factory strand into this session
        if (h.strand && Array.isArray(h.strand)) {
          DNA.strand = h.strand.concat(DNA.strand);
        }
        DNA.session = h.session || DNA.session;
        localStorage.removeItem('dnaHandoff');
        console.log('🧬 DNA handoff from factory2 — ' + h.strand.length + ' pre-game events merged');
      }
    } catch(e) {}

    DNA.load();
    hookGame();

    // Hook finale functions after a beat (they're defined later in main.js)
    setTimeout(hookFinale, 1500);

    // Auto-report on page unload if anything interesting happened
    window.addEventListener('beforeunload', () => {
      if (DNA.strand.length > 5) {
        DNA.report('unload');
      }
    });

    // Expose globally
    window.GameDNA = DNA;
    console.log('🧬 GameDNA recorder active');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
