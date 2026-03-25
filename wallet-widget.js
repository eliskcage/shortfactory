/**
 * ShortFactory Wallet Widget
 * Drop onto any page: <script src="wallet-core.js"></script><script src="wallet-widget.js"></script>
 * Injects a floating wallet button + slide-in panel
 */
(function() {
  const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700&display=swap');
  #sf-wallet-btn {
    position:fixed; bottom:1.5rem; right:1.5rem; z-index:9000;
    background:#c8a84b; color:#04040a;
    font-family:'Orbitron',monospace; font-size:0.45rem; letter-spacing:0.4em;
    border:none; padding:0.85rem 1.4rem; cursor:pointer;
    box-shadow:0 0 20px rgba(200,168,75,0.3);
    display:flex; align-items:center; gap:0.6rem;
    transition:all 0.3s;
  }
  #sf-wallet-btn:hover { box-shadow:0 0 35px rgba(200,168,75,0.55); }
  #sf-wallet-btn .sf-dot { width:7px; height:7px; border-radius:50%; background:#04040a; }
  #sf-wallet-btn.no-token { background:transparent; color:#c8a84b; border:1px solid rgba(200,168,75,0.4); }
  #sf-wallet-btn.no-token .sf-dot { background:#c8a84b; }

  #sf-wallet-panel {
    position:fixed; top:0; right:-380px; width:360px; max-width:100vw; height:100vh;
    background:#080812; border-left:1px solid rgba(200,168,75,0.08);
    z-index:9001; transition:right 0.4s cubic-bezier(0.4,0,0.2,1);
    display:flex; flex-direction:column; overflow:hidden;
  }
  #sf-wallet-panel.open { right:0; }

  .sfp-header {
    display:flex; justify-content:space-between; align-items:center;
    padding:1.2rem 1.4rem; border-bottom:1px solid rgba(200,168,75,0.07);
  }
  .sfp-logo { font-family:'Orbitron',monospace; font-size:0.42rem; letter-spacing:0.5em; color:rgba(200,168,75,0.4); }
  .sfp-close { background:none; border:none; color:rgba(200,168,75,0.4); font-size:1.2rem; cursor:pointer; padding:0.2rem 0.4rem; transition:color 0.2s; }
  .sfp-close:hover { color:#c8a84b; }

  .sfp-body { flex:1; overflow-y:auto; padding:1.4rem; display:flex; flex-direction:column; gap:1.5rem; }
  .sfp-body::-webkit-scrollbar { width:2px; }
  .sfp-body::-webkit-scrollbar-thumb { background:rgba(200,168,75,0.15); }

  /* NO TOKEN STATE */
  .sfp-forge { text-align:center; padding:2rem 1rem; display:flex; flex-direction:column; gap:1rem; align-items:center; }
  .sfp-forge-title { font-family:'IM Fell English',serif; font-size:1.1rem; color:#c8a84b; line-height:1.4; }
  .sfp-forge-sub { font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:rgba(216,216,232,0.45); line-height:1.7; }
  .sfp-forge-btn { font-family:'Orbitron',monospace; font-size:0.5rem; letter-spacing:0.4em; background:#c8a84b; color:#04040a; border:none; padding:0.9rem 2rem; cursor:pointer; transition:all 0.3s; width:100%; }
  .sfp-forge-btn:hover { box-shadow:0 0 20px rgba(200,168,75,0.4); }

  /* BALANCE */
  .sfp-balance { text-align:center; padding:1rem 0; }
  .sfp-bal-label { font-family:'Orbitron',monospace; font-size:0.38rem; letter-spacing:0.5em; color:rgba(200,168,75,0.35); margin-bottom:0.5rem; }
  .sfp-bal-num { font-family:'Orbitron',monospace; font-size:2.4rem; color:#c8a84b; line-height:1; }
  .sfp-bal-unit { font-family:'Orbitron',monospace; font-size:0.5rem; letter-spacing:0.4em; color:rgba(200,168,75,0.4); margin-top:0.3rem; }

  /* TOKEN */
  .sfp-token { display:flex; flex-direction:column; align-items:center; gap:0.6rem; }
  .sfp-token canvas { display:block; }
  .sfp-token-id { font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:rgba(200,168,75,0.4); }
  .sfp-iq { font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:rgba(216,216,232,0.45); }

  /* ACTIONS */
  .sfp-actions { display:flex; flex-direction:column; gap:0.6rem; }
  .sfp-action { display:flex; justify-content:space-between; align-items:center; padding:0.7rem 0.8rem; border:1px solid rgba(200,168,75,0.07); background:rgba(200,168,75,0.03); cursor:pointer; transition:all 0.2s; }
  .sfp-action:hover { border-color:rgba(200,168,75,0.2); }
  .sfp-action-name { font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#d8d8e8; }
  .sfp-action-cost { font-family:'Orbitron',monospace; font-size:0.5rem; color:#c8a84b; }

  /* TX */
  .sfp-tx-label { font-family:'Orbitron',monospace; font-size:0.38rem; letter-spacing:0.5em; color:rgba(200,168,75,0.35); }
  .sfp-tx-list { display:flex; flex-direction:column; gap:0.4rem; }
  .sfp-tx { display:flex; justify-content:space-between; align-items:center; padding:0.5rem 0; border-bottom:1px solid rgba(200,168,75,0.04); }
  .sfp-tx-r { font-family:'Share Tech Mono',monospace; font-size:0.62rem; color:rgba(216,216,232,0.6); }
  .sfp-tx-a { font-family:'Orbitron',monospace; font-size:0.55rem; }
  .sfp-tx-a.credit { color:#4ba84b; }
  .sfp-tx-a.debit { color:#a84b4b; }
  .sfp-tx-a.mint { color:#c8a84b; }

  .sfp-wallet-link { font-family:'Orbitron',monospace; font-size:0.42rem; letter-spacing:0.4em; color:rgba(200,168,75,0.5); text-align:center; cursor:pointer; transition:color 0.2s; text-decoration:none; display:block; padding:0.5rem; }
  .sfp-wallet-link:hover { color:#c8a84b; }

  #sf-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:8999; }
  #sf-overlay.on { display:block; }

  #sf-toast { position:fixed; bottom:5rem; right:1.5rem; background:#c8a84b; color:#04040a; font-family:'Orbitron',monospace; font-size:0.45rem; letter-spacing:0.3em; padding:0.7rem 1.2rem; transform:translateY(60px); opacity:0; transition:all 0.35s; z-index:9999; pointer-events:none; }
  #sf-toast.on { transform:translateY(0); opacity:1; }
  `;

  const style = document.createElement('style');
  style.textContent = CSS;
  document.head.appendChild(style);

  // DOM
  const overlay = document.createElement('div'); overlay.id = 'sf-overlay';
  const btn = document.createElement('button'); btn.id = 'sf-wallet-btn';
  const panel = document.createElement('div'); panel.id = 'sf-wallet-panel';
  const toastEl = document.createElement('div'); toastEl.id = 'sf-toast';
  document.body.appendChild(overlay);
  document.body.appendChild(btn);
  document.body.appendChild(panel);
  document.body.appendChild(toastEl);

  function sfToast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('on');
    setTimeout(() => toastEl.classList.remove('on'), 2200);
  }

  function openPanel() {
    panel.classList.add('open');
    overlay.classList.add('on');
    renderPanel();
  }

  function closePanel() {
    panel.classList.remove('open');
    overlay.classList.remove('on');
  }

  overlay.addEventListener('click', closePanel);
  btn.addEventListener('click', openPanel);

  function renderBtn(w) {
    const hasTok = w && w.soulToken;
    btn.className = hasTok ? '' : 'no-token';
    if (hasTok) {
      btn.innerHTML = `<div class="sf-dot"></div>${SFWallet.fmt(w.sft)} SFT`;
    } else {
      btn.innerHTML = `<div class="sf-dot"></div>FORGE SOUL TOKEN`;
    }
  }

  function renderPanel() {
    const w = SFWallet.get();
    panel.innerHTML = '';

    const hdr = document.createElement('div'); hdr.className = 'sfp-header';
    hdr.innerHTML = `<div class="sfp-logo">SFT WALLET</div><button class="sfp-close" onclick="document.getElementById('sf-wallet-panel').classList.remove('open');document.getElementById('sf-overlay').classList.remove('on');">✕</button>`;
    panel.appendChild(hdr);

    const body = document.createElement('div'); body.className = 'sfp-body';

    if (!w || !w.soulToken) {
      body.innerHTML = `<div class="sfp-forge">
        <div class="sfp-forge-title">You have not forged your soul token yet.</div>
        <div class="sfp-forge-sub">Complete the IQ Mirror to mint your unique soul token and receive your first SFT allocation.</div>
        <button class="sfp-forge-btn" onclick="location.href='iq-test.html'">TAKE THE IQ MIRROR</button>
      </div>`;
      panel.appendChild(body);
      return;
    }

    // Balance
    const bal = document.createElement('div'); bal.className = 'sfp-balance';
    bal.innerHTML = `<div class="sfp-bal-label">BALANCE</div><div class="sfp-bal-num">${SFWallet.fmt(w.sft)}</div><div class="sfp-bal-unit">SFT</div>`;
    body.appendChild(bal);

    // Token
    if (w.soulToken) {
      const tok = document.createElement('div'); tok.className = 'sfp-token';
      const c = document.createElement('canvas');
      tok.appendChild(c);
      tok.innerHTML += `<div class="sfp-token-id">${w.soulToken.id}</div><div class="sfp-iq">ψ_iq = [${w.soulToken.iq.depth}, ${w.soulToken.iq.compression}, ${w.soulToken.iq.alignment}]</div>`;
      tok.insertBefore(c, tok.firstChild);
      body.appendChild(tok);
      setTimeout(() => SFWallet.drawSoulToken(c, w.soulToken, 140), 50);
    }

    // Actions
    const acts = document.createElement('div'); acts.className = 'sfp-actions';
    const items = [
      ['Generate AI Short', '100 SFT', 100, null],
      ['Soul Map Session', '50 SFT', 50, 'soul-map.html'],
      ['Cortex API 7 Days', '500 SFT', 500, null],
      ['Launch Your Fork', '1000 SFT', 1000, null],
    ];
    items.forEach(([name, costStr, cost, url]) => {
      const d = document.createElement('div'); d.className = 'sfp-action';
      d.innerHTML = `<div class="sfp-action-name">${name}</div><div class="sfp-action-cost">${costStr}</div>`;
      d.style.opacity = w.sft >= cost ? '1' : '0.4';
      d.style.cursor = w.sft >= cost ? 'pointer' : 'not-allowed';
      if (w.sft >= cost) {
        d.addEventListener('click', () => {
          if (SFWallet.spendSFT(cost, name)) {
            sfToast('SPENT ' + cost + ' SFT');
            renderBtn(SFWallet.get());
            renderPanel();
            if (url) location.href = url;
          }
        });
      }
      acts.appendChild(d);
    });
    body.appendChild(acts);

    // Recent TX
    if (w.txs && w.txs.length) {
      const txSection = document.createElement('div');
      txSection.innerHTML = `<div class="sfp-tx-label" style="margin-bottom:0.8rem">RECENT</div>`;
      const txList = document.createElement('div'); txList.className = 'sfp-tx-list';
      w.txs.slice(0, 8).forEach(tx => {
        const sign = tx.type === 'credit' ? '+' : tx.type === 'debit' ? '-' : '';
        const amtStr = tx.type === 'mint' ? 'MINTED' : sign + SFWallet.fmt(tx.amount) + ' SFT';
        const d = document.createElement('div'); d.className = 'sfp-tx';
        d.innerHTML = `<div class="sfp-tx-r">${tx.reason.slice(0,28)}</div><div class="sfp-tx-a ${tx.type}">${amtStr}</div>`;
        txList.appendChild(d);
      });
      txSection.appendChild(txList);
      body.appendChild(txSection);
    }

    // Link to full wallet
    const link = document.createElement('a'); link.href = 'wallet.html'; link.className = 'sfp-wallet-link';
    link.textContent = 'OPEN FULL WALLET →';
    body.appendChild(link);

    panel.appendChild(body);
    renderBtn(w);
  }

  // Initial render
  renderBtn(SFWallet.get());

})();
