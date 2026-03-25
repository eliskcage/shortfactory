/**
 * ShortFactory Wallet Core
 * localStorage-based SFT wallet + Soul Token engine
 * Phase 1: local. Phase 2: chain (Base L2)
 */

const SFWallet = (() => {

  const KEY = 'sf_wallet_v1';

  function get() {
    try { return JSON.parse(localStorage.getItem(KEY)) || null; } catch { return null; }
  }

  function save(w) {
    localStorage.setItem(KEY, JSON.stringify(w));
  }

  function create() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let addr = 'SF';
    for (let i = 0; i < 14; i++) addr += chars[Math.random() * chars.length | 0];
    const w = { address: addr, sft: 0, soulToken: null, txs: [], created: Date.now() };
    save(w);
    return w;
  }

  function ensure() {
    return get() || create();
  }

  function addSFT(amount, reason) {
    const w = ensure();
    w.sft += amount;
    w.txs.unshift({ type: 'credit', amount, reason, ts: Date.now() });
    if (w.txs.length > 100) w.txs.length = 100;
    save(w);
    return w;
  }

  function spendSFT(amount, reason) {
    const w = get();
    if (!w || w.sft < amount) return false;
    w.sft -= amount;
    w.txs.unshift({ type: 'debit', amount, reason, ts: Date.now() });
    save(w);
    return true;
  }

  function mintSoulToken(iqVec, name) {
    const w = ensure();
    if (w.soulToken) return w;
    const id = 'ST' + Date.now().toString(36).toUpperCase() + (Math.random()*999|0);
    w.soulToken = { id, iq: iqVec, name: name || 'Anonymous', ts: Date.now(), seed: Math.random() * 1e7 | 0 };
    w.txs.unshift({ type: 'mint', amount: 0, reason: 'Soul Token ' + id, ts: Date.now() });
    save(w);
    return w;
  }

  // ---- SOUL TOKEN CANVAS RENDERER ----
  // Draws a unique mandala from token data onto a canvas element
  function drawSoulToken(canvas, token, size) {
    size = size || 200;
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    const cx = size / 2, cy = size / 2;

    // Seeded pseudo-random
    let rs = token.seed;
    function sr() { rs = (rs * 1664525 + 1013904223) & 0xffffffff; return (rs >>> 0) / 0xffffffff; }

    const { depth, compression, alignment } = token.iq;
    const D = Math.max(1, depth);
    const C = Math.max(1, compression);
    const A = Math.max(1, alignment);

    ctx.clearRect(0, 0, size, size);

    // Background glow
    const bg = ctx.createRadialGradient(cx, cy, 0, cx, cy, size * 0.55);
    bg.addColorStop(0, 'rgba(200,168,75,0.06)');
    bg.addColorStop(1, 'rgba(4,4,10,0)');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, size, size);

    const gold = '#c8a84b';
    const goldDim = 'rgba(200,168,75,0.25)';
    const goldGlow = 'rgba(200,168,75,0.5)';

    function poly(sides, r, rot, strokeStyle, lw, fill) {
      ctx.beginPath();
      for (let i = 0; i <= sides; i++) {
        const a = (i / sides) * Math.PI * 2 + rot;
        i === 0 ? ctx.moveTo(cx + Math.cos(a)*r, cy + Math.sin(a)*r)
                : ctx.lineTo(cx + Math.cos(a)*r, cy + Math.sin(a)*r);
      }
      ctx.closePath();
      if (fill) { ctx.fillStyle = fill; ctx.fill(); }
      ctx.strokeStyle = strokeStyle; ctx.lineWidth = lw; ctx.stroke();
    }

    function orbit(count, r, dotR, col) {
      for (let i = 0; i < count; i++) {
        const a = (i / count) * Math.PI * 2 + sr() * 0.5;
        const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
        ctx.beginPath(); ctx.arc(x, y, dotR, 0, Math.PI * 2);
        ctx.fillStyle = col; ctx.fill();
      }
    }

    // Outer ring
    ctx.beginPath(); ctx.arc(cx, cy, size*0.44, 0, Math.PI*2);
    ctx.strokeStyle = goldDim; ctx.lineWidth = 0.5; ctx.stroke();

    // Depth polygon (outer)
    const outerSides = D + 3;
    const outerRot = sr() * Math.PI * 2;
    poly(outerSides, size*0.38, outerRot, goldGlow, 1);

    // Compression polygon (mid)
    const midSides = Math.min(C + 2, 10);
    poly(midSides, size*0.25, outerRot + Math.PI/midSides, goldDim, 0.7);

    // Star lines from outer poly to center
    ctx.save();
    ctx.globalAlpha = 0.15;
    for (let i = 0; i < outerSides; i++) {
      const a = (i / outerSides) * Math.PI * 2 + outerRot;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(a) * size*0.38, cy + Math.sin(a) * size*0.38);
      ctx.lineTo(cx, cy);
      ctx.strokeStyle = gold; ctx.lineWidth = 0.5; ctx.stroke();
    }
    ctx.restore();

    // Alignment orbital dots
    orbit(A, size*0.32, 1.8, gold);
    orbit(Math.max(1, A-2), size*0.20, 1.2, goldDim);

    // Center core
    const coreGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, size*0.07);
    coreGrad.addColorStop(0, 'rgba(200,168,75,0.9)');
    coreGrad.addColorStop(1, 'rgba(200,168,75,0)');
    ctx.beginPath(); ctx.arc(cx, cy, size*0.07, 0, Math.PI*2);
    ctx.fillStyle = coreGrad; ctx.fill();

    // Token ID (tiny, bottom)
    ctx.font = `${size*0.045}px 'Share Tech Mono', monospace`;
    ctx.fillStyle = 'rgba(200,168,75,0.3)';
    ctx.textAlign = 'center';
    ctx.fillText(token.id, cx, cy + size*0.47);
  }

  // Utility: format SFT number
  function fmt(n) {
    if (n >= 1000000) return (n/1000000).toFixed(1)+'M';
    if (n >= 1000) return (n/1000).toFixed(1)+'K';
    return n.toFixed(0);
  }

  function timeAgo(ts) {
    const d = Date.now() - ts;
    if (d < 60000) return 'just now';
    if (d < 3600000) return Math.floor(d/60000)+'m ago';
    if (d < 86400000) return Math.floor(d/3600000)+'h ago';
    return Math.floor(d/86400000)+'d ago';
  }

  return { get, save, create, ensure, addSFT, spendSFT, mintSoulToken, drawSoulToken, fmt, timeAgo };

})();
