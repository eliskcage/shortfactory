// ==================== COMPACT STOCKS BRIDGE ====================
// Arrow on oil button: down = cash to game, rotated = cash to debt
// Click debt pill to rotate arrow toward it. Click arrow to rotate back.
(function(){

  var debtPayMode = false;
  var debtPaid = true; // Always unlocked — debt system is cosmetic progression, not a gate
  var _lastDebtVal = null; // Track last displayed debt value for tally animation
  var _debtTallyTimer = null; // Active tally animation

  // Ensure safeCash exists (defined in stockmarket.js but we need a fallback)
  if(typeof window.safeCash==='undefined') window.safeCash=function(v){return isNaN(v)||!isFinite(v)?0:Math.max(0,v);};

  function fmtCS(val){
    if(isNaN(val)||!isFinite(val)) return '0';
    if(Math.abs(val)>=1000000) return (val/1000000).toFixed(1)+'M';
    if(Math.abs(val)>=1000) return (val/1000).toFixed(1)+'K';
    return Math.floor(val).toString();
  }
  function greyBtn(el){
    if(!el) return;
    el.style.opacity='0.3';el.style.filter='grayscale(1)';el.style.pointerEvents='none';
    el.style.border='1px solid #333';el.style.color='#555';el.style.background='rgba(30,30,30,0.3)';
  }
  function litBtn(el,border,color,bg){
    if(!el) return;
    el.style.opacity='1';el.style.filter='none';el.style.pointerEvents='auto';
    el.style.border='1px solid '+border;el.style.color=color;el.style.background=bg;
  }

  // ==================== ARROW ON OIL BUTTON ====================

  function addCashArrow(){
    var btn = document.getElementById('oil-sell-button');
    if(!btn) return;
    btn.style.overflow = 'visible';
    var ws = document.getElementById('wealth-stack');
    if(ws) ws.style.overflow = 'visible';
    var arrow = document.getElementById('cash-dir-arrow');
    if(arrow){ updateArrow(); return; }
    arrow = document.createElement('div');
    arrow.id = 'cash-dir-arrow';
    arrow.style.cssText = 'position:absolute;bottom:-70px;left:50%;transform:translateX(-50%) rotate(0deg);font-size:78px;color:#0f0;cursor:pointer;z-index:10000;text-shadow:0 0 15px #0f0;transition:transform 0.3s ease,color 0.3s ease;padding:10px;line-height:1';
    arrow.textContent = '\u2B07';
    btn.appendChild(arrow);
    updateArrow();
  }

  function updateArrow(){
    var arrow = document.getElementById('cash-dir-arrow');
    if(!arrow) return;
    if(debtPayMode){
      arrow.style.color = '#ffd700';
      arrow.style.textShadow = '0 0 10px #ffd700';
      arrow.style.transform = 'translateX(-50%) rotate(90deg)';
    } else {
      arrow.style.color = '#0f0';
      arrow.style.textShadow = '0 0 10px #0f0';
      arrow.style.transform = 'translateX(-50%) rotate(0deg)';
    }
  }

  // Re-add arrow when oil button rebuilds
  var _origWS = window.updateWealthStack;
  window.updateWealthStack = function(){
    if(_origWS) _origWS.apply(this, arguments);
    addCashArrow();
  };

  // ==================== DEBT PILL ====================

  function tallyDebtTo(targetVal, disp, prefix){
    // Cancel any running tally
    if(_debtTallyTimer) clearInterval(_debtTallyTimer);
    if(_lastDebtVal === null) { _lastDebtVal = targetVal; disp.textContent = prefix + targetVal.toFixed(1) + 'T'; return; }
    if(Math.abs(_lastDebtVal - targetVal) < 0.05) { _lastDebtVal = targetVal; disp.textContent = prefix + targetVal.toFixed(1) + 'T'; return; }

    var startVal = _lastDebtVal;
    var diff = targetVal - startVal;
    var steps = Math.min(20, Math.max(8, Math.ceil(Math.abs(diff) * 4)));
    var step = 0;
    var tallySound = document.getElementById('breath-sound');
    if(tallySound){ tallySound.currentTime = 0; tallySound.volume = 0.3; tallySound.play().catch(function(){}); }

    _debtTallyTimer = setInterval(function(){
      step++;
      var t = step / steps;
      var current = startVal + diff * t;
      disp.textContent = prefix + current.toFixed(1) + 'T';
      if(step >= steps){
        clearInterval(_debtTallyTimer);
        _debtTallyTimer = null;
        disp.textContent = prefix + targetVal.toFixed(1) + 'T';
        _lastDebtVal = targetVal;
        if(tallySound){ tallySound.pause(); tallySound.currentTime = 0; }
      }
    }, 60);
    _lastDebtVal = targetVal;
  }

  function updateDebtPill(){
    if(!G) return;
    var pill = document.getElementById('pill-debt');
    var disp = document.getElementById('disp-debt');
    if(!pill) return;

    if(G.debt <= 0 && !debtPaid) G.debt = 38;

    if(debtPaid && G.debt <= 0){
      var surplus = Math.abs(G.debt);
      if(pill.childNodes[0] && pill.childNodes[0].nodeType===3) pill.childNodes[0].textContent='';
      if(surplus > 0.1){ tallyDebtTo(surplus, disp, 'SURPLUS: $'); }
      else { disp.textContent = 'SURPLUS'; _lastDebtVal = 0; }
      pill.style.color='#00ff88';pill.style.borderColor='#00ff88';pill.style.textShadow='0 0 8px #00ff88';
      pill.style.background=debtPayMode?'rgba(0,80,0,0.6)':'';
      pill.style.animation=debtPayMode?'blink 1s infinite':'';
      pill.style.boxShadow=debtPayMode?'0 0 12px rgba(0,255,136,0.5)':'';
      return;
    }

    if(disp && G.debt > 0) tallyDebtTo(G.debt, disp, '$');

    if(debtPayMode){
      pill.style.color='#ffd700';pill.style.borderColor='#ffd700';pill.style.textShadow='0 0 8px #ffd700';
      pill.style.background='rgba(100,80,0,0.6)';pill.style.animation='blink 1s infinite';pill.style.boxShadow='0 0 12px rgba(255,215,0,0.5)';
    } else {
      pill.style.color='';pill.style.borderColor='';pill.style.textShadow='';
      pill.style.background='';pill.style.animation='';pill.style.boxShadow='';
    }
  }

  // Click debt pill = toggle arrow direction
  function wireDebtPill(){
    var pill = document.getElementById('pill-debt');
    if(!pill) return;
    pill.style.cursor = 'pointer';
    pill.onclick = function(){
      debtPayMode = !debtPayMode;
      updateArrow();
      updateDebtPill();
      if(typeof smPlayWin==='function') smPlayWin();
      if(debtPayMode){
        if(typeof showNews==='function') showNews(debtPaid ? 'FLOW → SURPLUS' : 'FLOW → DEBT');
      } else {
        if(typeof showNews==='function') showNews('FLOW ↓ GAME');
      }
    };
  }

  // ==================== DEBT PAYMENT (round tick only) ====================

  var _safe = function(v){ return typeof safeCash==='function' ? safeCash(v) : Math.max(0,v); };

  function processDebtPayment(){
    if(!debtPayMode || !G) return;
    var payment = G.oilCash; // ALL cash goes to debt when arrow points there
    if(payment <= 0) return;
    G.debt = G.debt - (payment / 1000);
    G.oilCash = 0;

    if(G.debt > 0){
      if(typeof showNews==='function') showNews('-$'+fmtCS(payment)+'M to debt | $'+G.debt.toFixed(1)+'T left');
    } else {
      if(typeof showNews==='function') showNews('SURPLUS: $'+Math.abs(G.debt).toFixed(1)+'T');
    }

    if(G.debt <= 0 && !debtPaid){
      debtPaid = true;
      localStorage.setItem('debtPaidOff','true');
      if(typeof smPlayTrumpWin==='function') smPlayTrumpWin();
      if(typeof showNews==='function') showNews('DEBT PAID OFF! BUILD $1T SURPLUS FOR STATS!');
    }
    checkStatsUnlock(); // Check after every payment
    updateDebtPill();
    if(typeof updateDisplay==='function') updateDisplay();
  }

  // ==================== STATS LOCK ====================
  // Stats button greyed until debt cleared + $1T surplus (G.debt <= -1)

  function greyStatsBtn(){
    var btn = document.getElementById('stats-btn');
    if(!btn) return;
    btn.style.opacity='0.3';btn.style.filter='grayscale(1)';btn.style.pointerEvents='none';
    btn.style.textShadow='none';btn.style.borderColor='#333';btn.style.color='#555';
  }

  function unlockStatsBtn(){
    var btn = document.getElementById('stats-btn');
    if(!btn) return;
    btn.style.opacity='1';btn.style.filter='none';btn.style.pointerEvents='auto';
    btn.style.textShadow='0 0 8px #00ff88';btn.style.borderColor='#00ff88';btn.style.color='';
  }

  function checkStatsUnlock(){
    if(!G) return;
    var btn = document.getElementById('stats-btn');
    if(!btn) return; // button not in DOM yet — skip
    // Need debt cleared AND at least $1T surplus (debt <= -1)
    if(G.debt <= -1){
      unlockStatsBtn();
    } else {
      greyStatsBtn();
    }
  }

  var _origToggle = window.toggleStats;
  window.toggleStats = function(){
    if(_origToggle) _origToggle();
    var sv = document.getElementById('stocks-view');
    if(sv && sv.style.display!=='none'){
      // Force-init G.stocks if missing (prevents silent button failures)
      if(typeof _csForceInitStocks==='function') _csForceInitStocks();
      if(G){ G.stockMarketUnlocked=true; if(typeof calculateStockPrices==='function') calculateStockPrices(); }
      setTimeout(function(){ wireButtons(); updateCompactUI(); }, 100);
    }
  };

  // ==================== AUTO HEARTS ====================
  // Auto ON + round tick = 1 heart floats up. When animation ends, +1% HP.

  function spawnAutoHearts(){
    if(!G || !G.stockAutoMode) return;

    // Find spawn anchor — AUTO button on stocks view, trump video on map
    var sv = document.getElementById('stocks-view');
    var onStocks = sv && sv.style.display !== 'none';
    var anchor = onStocks ? document.getElementById('cs-auto-btn') : (document.getElementById('trump-video') || document.getElementById('trump-stage'));
    if(!anchor) return;
    var rect = anchor.getBoundingClientRect();

    var h = document.createElement('div');
    h.textContent = '\u2764\uFE0F';
    h.style.cssText = 'position:fixed;font-size:20px;z-index:99999;pointer-events:none;left:'+(rect.left+rect.width/2-10)+'px;top:'+rect.top+'px;transition:all 1.5s ease-out;opacity:1';
    document.body.appendChild(h);
    requestAnimationFrame(function(){h.style.top=(rect.top-120)+'px';h.style.opacity='0';});
    setTimeout(function(){
      h.remove();
      G.trumpHP=Math.min(200,G.trumpHP+1);
      if(typeof updateDisplay==='function')updateDisplay();
      if(typeof showNews==='function')showNews('\u2764 +1% HP ('+Math.round(G.trumpHP)+'%)');
    },1600);
  }

  // ==================== INTERCEPT OIL SELL ONLY → REDIRECT TO DEBT ====================
  // Capture click on oil-sell-button. Record cash BEFORE click, check AFTER, redirect difference.

  document.addEventListener('click', function(e){
    if(!debtPayMode || !G) return; // only intercept when arrow points at debt
    // Check if this click is on the oil sell button or its children
    var target = e.target;
    var isOilSell = false;
    while(target && target !== document.body){
      if(target.id === 'oil-sell-button'){ isOilSell = true; break; }
      target = target.parentElement;
    }
    if(!isOilSell) return;

    var cashBefore = G.oilCash;

    // Wait for the sell to complete (tally or instant)
    function checkRedirect(){
      // If tally overlay still showing, wait more
      var tallyEl = document.getElementById('tally-counter-overlay');
      if(tallyEl){ setTimeout(checkRedirect, 300); return; }

      var gained = G.oilCash - cashBefore;
      if(gained > 0){
        G.oilCash = cashBefore; // undo — cash goes to debt not pocket
        G.debt = G.debt - (gained / 1000);
        if(typeof showNews==='function') showNews('-$'+fmtCS(gained)+'M → DEBT | '+(G.debt>0?'$'+G.debt.toFixed(1)+'T left':'SURPLUS $'+Math.abs(G.debt).toFixed(1)+'T'));
        updateDebtPill();
        if(typeof updateDisplay==='function') updateDisplay();
      }
    }
    // Small delay to let the sell handler run first
    setTimeout(checkRedirect, 200);
  }, false); // bubble phase — runs AFTER the sell handler

  // ==================== FIX DEBT DISPLAY (main.js updateDisplay clobbers ours) ====================

  var _origUD = window.updateDisplay;
  window.updateDisplay = function(){
    if(_origUD) _origUD.apply(this, arguments);
    checkStatsUnlock(); // Keep stats button state synced
    // Fix debt pill after main.js writes it
    if(G && G.debt <= 0 && debtPaid){
      var disp = document.getElementById('disp-debt');
      if(disp){
        var surplus = Math.abs(G.debt);
        disp.textContent = surplus > 0.1 ? 'SURPLUS: $'+surplus.toFixed(1)+'T' : 'SURPLUS';
      }
      var pill = document.getElementById('pill-debt');
      if(pill){
        if(pill.childNodes[0] && pill.childNodes[0].nodeType===3) pill.childNodes[0].textContent='';
        pill.style.color='#00ff88';pill.style.borderColor='#00ff88';pill.style.textShadow='0 0 8px #00ff88';
      }
    }
  };

  // ==================== ROUND TICK ====================

  var _origRT = window.stockMarketRoundTick;
  window.stockMarketRoundTick = function(){
    if(G && !G.stockMarketUnlocked) G.stockMarketUnlocked = true;
    if(_origRT) _origRT();
    processDebtPayment();
    updateDebtPill();
    checkStatsUnlock(); // Re-check each round
    if(debtPaid) csAutoNow();
    spawnAutoHearts();
    updateCompactUI();
  };

  // ==================== COMPACT UI ====================

  function updateCompactUI(){
    if(!G || !G.stocks) return;
    var sv = document.getElementById('stocks-view');
    if(!sv || sv.style.display==='none') return;

    var pVal = typeof getPortfolioValue==='function' ? getPortfolioValue() : 0;
    var pChange = typeof getPortfolioChange==='function' ? getPortfolioChange() : 0;
    var elPV = document.getElementById('cs-portfolio');
    var elPC = document.getElementById('cs-change');
    var elCash = document.getElementById('cs-cash');
    var elRound = document.getElementById('cs-round');
    if(elPV) elPV.textContent = '$' + fmtCS(pVal);
    if(elPC){ elPC.textContent = (pChange>=0?'+':'-') + '$' + fmtCS(Math.abs(pChange)); elPC.style.color = pChange>=0 ? '#00ff88' : '#ff4444'; }
    if(elCash) elCash.textContent = '$' + fmtCS(G.oilCash);
    if(elRound) elRound.textContent = G.round;

    var power = typeof getCorpVsPeoplePower==='function' ? getCorpVsPeoplePower() : {peoplePct:50,corpPct:50};
    var elCL=document.getElementById('cs-corp-label'),elPL=document.getElementById('cs-people-label');
    var elCF=document.getElementById('cs-corp-fill'),elPF=document.getElementById('cs-people-fill');
    if(elCL) elCL.textContent='\u2620 CORPS '+power.corpPct+'%';
    if(elPL) elPL.textContent='\u270A PEOPLE '+power.peoplePct+'%';
    if(elCF) elCF.style.width=power.corpPct+'%';
    if(elPF) elPF.style.width=power.peoplePct+'%';

    updateCompactChart(G.stockSelectedTicker || 'MAGA');
    updateCompactRows();
    updateCompactTicker();

    // Trade buttons — always lit, always clickable (like STATS_DEMO2)
    var buyBtn=document.getElementById('cs-buy-btn'),sellBtn=document.getElementById('cs-sell-btn'),autoBtn=document.getElementById('cs-auto-btn');
    if(buyBtn) litBtn(buyBtn,'#0a0','#00ff88','rgba(0,100,0,0.3)');
    if(sellBtn) litBtn(sellBtn,'#a00','#ff4444','rgba(100,0,0,0.3)');
    if(autoBtn){
      if(G.stockAutoMode){ litBtn(autoBtn,'#0ff','#0ff','rgba(0,200,255,0.3)'); autoBtn.textContent='\uD83E\uDD16 AUTO ON'; }
      else { litBtn(autoBtn,'#00a','#00ffff','rgba(0,0,100,0.3)'); autoBtn.textContent='\uD83E\uDD16 AUTO'; }
    }
    var intEl=document.getElementById('cs-intensity');
    if(intEl) intEl.textContent=(G.stockAutoIntensity||10)+'%';
  }

  // ==================== CHART ====================

  function updateCompactChart(ticker){
    if(!G||!G.stocks) return;
    var stock=G.stocks[ticker];
    if(!stock||!stock.history||!stock.history.length) return;
    G.stockSelectedTicker=ticker;
    var h=stock.history,W=340,H=60,pad=3,min=Infinity,max=-Infinity;
    for(var i=0;i<h.length;i++){if(h[i]<min)min=h[i];if(h[i]>max)max=h[i];}
    min*=0.9;max*=1.1;var range=max-min||1;
    var pts=[];
    for(var i=0;i<h.length;i++){
      var x=pad+(i/Math.max(h.length-1,1))*(W-pad*2);
      var y=H-pad-((h[i]-min)/range)*(H-pad*2);
      pts.push(x.toFixed(1)+','+y.toFixed(1));
    }
    var lastX=(pad+((h.length-1)/Math.max(h.length-1,1))*(W-pad*2)).toFixed(1);
    var lastY=(H-pad-((h[h.length-1]-min)/range)*(H-pad*2)).toFixed(1);
    var line=document.getElementById('cs-chart-line'),fill=document.getElementById('cs-chart-fill'),dot=document.getElementById('cs-chart-dot');
    if(line) line.setAttribute('points',pts.join(' '));
    if(fill) fill.setAttribute('points',pts.join(' ')+' '+lastX+','+H+' '+pad+','+H);
    if(dot){dot.setAttribute('cx',lastX);dot.setAttribute('cy',lastY);}
    var isUp=h.length>1&&h[h.length-1]>=h[h.length-2];
    var color=isUp?'#00ff88':'#ff4444';
    if(line){line.style.stroke=color;line.style.filter='drop-shadow(0 0 3px '+color+')';}
    if(dot) dot.setAttribute('fill',color);
    var grad=document.getElementById('csChartGrad');
    if(grad){var s=grad.querySelectorAll('stop');if(s[0])s[0].setAttribute('stop-color',color);}
    var nameEl=document.getElementById('cs-chart-name'),priceEl=document.getElementById('cs-chart-price');
    var cfg=typeof STOCK_CONFIG!=='undefined'?STOCK_CONFIG[ticker]:null;
    if(nameEl) nameEl.textContent=(cfg?cfg.icon+' ':'')+'$'+ticker;
    if(priceEl){
      var lastP=h[h.length-1],prevP=h.length>1?h[h.length-2]:lastP;
      var pct=prevP>0?((lastP-prevP)/prevP*100).toFixed(1):'0.0';
      priceEl.textContent='$'+lastP.toFixed(2)+' '+(parseFloat(pct)>=0?'\u25B2':'\u25BC')+' '+Math.abs(parseFloat(pct))+'%';
      priceEl.style.color=color;priceEl.style.textShadow='0 0 3px '+color;
    }
  }

  // ==================== STOCK ROWS ====================

  function updateCompactRows(){
    var container=document.getElementById('cs-stock-list');
    if(!container||!G||!G.stocks) return;
    if(typeof STOCK_TICKERS==='undefined'||typeof STOCK_CONFIG==='undefined') return;
    var html='';
    for(var i=0;i<STOCK_TICKERS.length;i++){
      var t=STOCK_TICKERS[i],cfg=STOCK_CONFIG[t],stock=G.stocks[t];
      if(!cfg||!stock) continue;
      var prevP=stock.history.length>1?stock.history[stock.history.length-2]:stock.price;
      var pct=prevP>0?((stock.price-prevP)/prevP*100).toFixed(1):'0.0';
      var isUp=parseFloat(pct)>=0,color=isUp?'#00ff88':'#ff4444';
      var borderColor=cfg.faction==='people'?'#00ff88':'#ff4444';
      var sel=(t===G.stockSelectedTicker)?'background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.3);':'';
      var sharesInfo=stock.shares>0?'<div style="font-size:2.5px;color:#ffd700">'+stock.shares+' HELD ($'+fmtCS(stock.shares*stock.price)+')</div>':'';
      html+='<div class="cs-row" data-ticker="'+t+'" style="display:flex;justify-content:space-between;align-items:center;padding:3px 6px;background:rgba(255,255,255,0.02);border-radius:5px;border-left:3px solid '+borderColor+';cursor:pointer;'+sel+'">';
      html+='<div style="display:flex;align-items:center;gap:5px"><span style="font-size:12px">'+cfg.icon+'</span><div><div style="font-size:5px;color:#fff">$'+t+'</div><div style="font-size:2.5px;color:#444">'+cfg.name+'</div>'+sharesInfo+'</div></div>';
      html+='<div style="display:flex;align-items:center"><div style="font-size:7px;color:'+color+';text-shadow:0 0 3px '+color+'">$'+Math.round(stock.price)+'</div><div style="font-size:4px;color:'+color+';margin-left:3px">'+(isUp?'\u25B2':'\u25BC')+' '+Math.abs(parseFloat(pct))+'%</div></div>';
      html+='</div>';
    }
    container.innerHTML=html;
    var rows=container.querySelectorAll('.cs-row');
    for(var i=0;i<rows.length;i++){
      rows[i].onclick=(function(tk){return function(){updateCompactChart(tk);updateCompactRows();};})(rows[i].getAttribute('data-ticker'));
    }
  }

  // ==================== TICKER ====================

  function updateCompactTicker(){
    var el=document.getElementById('cs-ticker-bar');
    if(!el||!G||!G.stocks||typeof STOCK_TICKERS==='undefined') return;
    var parts=[];
    for(var i=0;i<STOCK_TICKERS.length;i++){
      var t=STOCK_TICKERS[i],stock=G.stocks[t];
      var prev=stock.history.length>1?stock.history[stock.history.length-2]:stock.price;
      var pct=prev>0?((stock.price-prev)/prev*100).toFixed(1):'0.0';
      var isUp=parseFloat(pct)>=0;
      parts.push('<span style="color:'+(isUp?'#00ff88':'#ff4444')+'">$'+t+' '+(isUp?'\u25B2':'\u25BC')+pct+'%</span>');
    }
    el.innerHTML=parts.join(' <span style="color:#333">|</span> ');
  }

  // ==================== JUICE ====================

  function csFlash(type){
    var sv=document.getElementById('stocks-view');if(!sv)return;
    var fl=document.createElement('div');fl.className='mm-sflash';
    fl.style.background=type==='win'?'rgba(0,255,136,0.2)':'rgba(255,0,0,0.2)';
    sv.appendChild(fl);setTimeout(function(){fl.remove();},300);
  }
  function csFloatProfit(amount){
    var sv=document.getElementById('stocks-view');if(!sv)return;
    var el=document.createElement('div');
    el.style.cssText='position:absolute;top:30%;left:50%;transform:translateX(-50%);font-family:"Press Start 2P",monospace;font-size:10px;color:'+(amount>=0?'#00ff88':'#ff4444')+';text-shadow:0 0 10px '+(amount>=0?'#00ff88':'#ff4444')+';z-index:99;pointer-events:none;animation:mmFUp 1.2s ease-out forwards';
    el.textContent=(amount>=0?'+$':'-$')+fmtCS(Math.abs(amount));
    sv.appendChild(el);setTimeout(function(){el.remove();},1500);
  }
  function csConfetti(count){
    var sv=document.getElementById('stocks-view');if(!sv)return;
    var colors=['#ff0','#00ff88','#0ff','#ff00ff','#ff8800','#fff'];
    for(var i=0;i<(count||15);i++){
      var c=document.createElement('div');
      c.style.cssText='position:absolute;top:-5px;left:'+(Math.random()*90+5)+'%;width:'+(3+Math.random()*5)+'px;height:'+(3+Math.random()*5)+'px;background:'+colors[Math.floor(Math.random()*colors.length)]+';border-radius:50%;z-index:99;pointer-events:none;animation:smConfettiFall '+(1+Math.random()*1.5)+'s linear forwards;animation-delay:'+(Math.random()*0.3)+'s';
      sv.appendChild(c);(function(el){setTimeout(function(){el.remove();},3000);})(c);
    }
  }
  function csBigText(text){
    var sv=document.getElementById('stocks-view');if(!sv)return;
    var el=document.createElement('div');
    el.style.cssText='position:absolute;top:40%;left:50%;transform:translate(-50%,-50%);font-family:"Press Start 2P",monospace;font-size:8px;color:#ffd700;text-shadow:0 0 15px #ffd700,0 0 30px #ff8800;z-index:99;pointer-events:none;animation:mmFUp 1.8s ease-out forwards;white-space:nowrap';
    el.textContent=text;sv.appendChild(el);setTimeout(function(){el.remove();},2000);
  }

  var _origJW=window.smJuiceWin;
  window.smJuiceWin=function(a){if(_origJW)_origJW(a);var sv=document.getElementById('stocks-view');if(sv&&sv.style.display!=='none'){csFlash('win');csFloatProfit(a);if(a>500){csConfetti(25);csBigText('+$'+fmtCS(a)+' PROFIT!');}else if(a>100)csConfetti(10);}};
  var _origJD=window.smJuiceDanger;
  window.smJuiceDanger=function(a){if(_origJD)_origJD(a);var sv=document.getElementById('stocks-view');if(sv&&sv.style.display!=='none'){csFlash('fail');csFloatProfit(a);if(a<-300)csBigText('REKT -$'+fmtCS(Math.abs(a)));}};
  var _origJF=window.smJuiceFail;
  window.smJuiceFail=function(){if(_origJF)_origJF();var sv=document.getElementById('stocks-view');if(sv&&sv.style.display!=='none')csFlash('fail');};
  var _origSSN=window.showStockNews;
  window.showStockNews=function(t){if(_origSSN)_origSSN(t);var sv=document.getElementById('stocks-view');if(sv&&sv.style.display!=='none')csBigText(t);};

  // ==================== TRADE BUTTONS (GLOBAL — called via inline onclick) ====================

  // Screen shake for drama
  function csShake(intensity){
    var sv=document.getElementById('stocks-view');if(!sv)return;
    var orig=sv.style.transform;
    var count=0;
    function shake(){
      count++;
      var x=(Math.random()-0.5)*intensity*2;
      var y=(Math.random()-0.5)*intensity*2;
      sv.style.transform='translate('+x+'px,'+y+'px)';
      if(count<6) requestAnimationFrame(shake);
      else sv.style.transform=orig||'';
    }
    shake();
  }

  // Money rain for big wins
  function csMoneyRain(count){
    var sv=document.getElementById('stocks-view');if(!sv)return;
    var emojis=['💰','💵','💲','🤑','💎'];
    for(var i=0;i<(count||20);i++){
      (function(delay){
        setTimeout(function(){
          var m=document.createElement('div');
          m.textContent=emojis[Math.floor(Math.random()*emojis.length)];
          m.style.cssText='position:absolute;top:-10px;left:'+(Math.random()*90+5)+'%;font-size:'+(12+Math.random()*14)+'px;z-index:99;pointer-events:none;opacity:1';
          sv.appendChild(m);
          var startX=parseFloat(m.style.left);var elapsed=0;
          function fall(){
            elapsed+=16;var t=elapsed/1000;
            m.style.top=(t*120)+'px';
            m.style.left=(startX+Math.sin(t*3)*5)+'%';
            m.style.opacity=Math.max(0,1-t/2);
            if(parseFloat(m.style.opacity)>0)requestAnimationFrame(fall);
            else m.remove();
          }
          requestAnimationFrame(fall);
        },delay*80);
      })(i);
    }
  }

  // Red danger pulse for losses
  function csDangerPulse(){
    var sv=document.getElementById('stocks-view');if(!sv)return;
    var fl=document.createElement('div');
    fl.style.cssText='position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(255,0,0,0.4);z-index:98;pointer-events:none;border:3px solid #ff0000;box-shadow:inset 0 0 40px rgba(255,0,0,0.6)';
    sv.appendChild(fl);
    setTimeout(function(){fl.style.transition='opacity 0.5s';fl.style.opacity='0';},200);
    setTimeout(function(){fl.remove();},800);
  }

  window.csBuy = function(){
    if(!G||!G.stocks)return;
    var t=G.stockSelectedTicker||'MAGA',stock=G.stocks[t];if(!stock)return;
    var spend=Math.max(Math.floor(G.oilCash*0.1),Math.ceil(stock.price));
    var qty=Math.max(1,Math.floor(spend/stock.price));
    if(G.oilCash<stock.price){csDangerPulse();csShake(3);if(typeof smPlayBuzzer==='function')smPlayBuzzer();csBigText('💸 NO CASH!');return;}
    if(stock.shares+qty>200)qty=200-stock.shares;
    if(qty<=0){csBigText('MAX 200!');csDangerPulse();return;}
    var cost=stock.price*qty;G.oilCash=safeCash(G.oilCash-cost);stock.shares+=qty;
    if(typeof smPlayBuy==='function')smPlayBuy();
    csFlash('win');csShake(2);csFloatProfit(-cost);csBigText('📈 BOUGHT '+qty+'x $'+t);
    csConfetti(8);
    if(typeof addStockEvent==='function')addStockEvent('BOUGHT '+qty+'x $'+t);
    if(typeof vibrate==='function')vibrate([50,30,50]);
    updateCompactUI();if(typeof updateDisplay==='function')updateDisplay();if(typeof saveGameState==='function')saveGameState();
  };
  window.csSell = function(){
    if(!G||!G.stocks)return;
    var t=G.stockSelectedTicker||'MAGA',stock=G.stocks[t];
    if(!stock||stock.shares<=0){csDangerPulse();csShake(3);if(typeof smPlayBuzzer==='function')smPlayBuzzer();csBigText('❌ NO SHARES!');return;}
    var sellQty=Math.max(1,Math.floor(stock.shares/2));
    var revenue=sellQty*stock.price;
    var baseVal=(typeof STOCK_CONFIG!=='undefined'?STOCK_CONFIG[t].basePrice:stock.price)*sellQty;
    var profit=revenue-baseVal;
    G.oilCash=safeCash(G.oilCash+revenue);stock.shares-=sellQty;
    if(typeof addStockEvent==='function')addStockEvent('SOLD '+sellQty+'x $'+t);
    if(profit>0){
      // WIN — money rain, confetti, big sound
      if(typeof smPlayBigWin==='function')smPlayBigWin();
      csFlash('win');csMoneyRain(Math.min(30,Math.max(10,Math.floor(profit/100))));csConfetti(25);
      csFloatProfit(profit);csBigText('🤑 +$'+fmtCS(profit)+' PROFIT!');csShake(4);
      if(typeof vibrate==='function')vibrate([100,50,100,50,100]);
    } else {
      // LOSS — red danger, shake, bad sound
      if(typeof smPlayBuzzer==='function')smPlayBuzzer();
      csDangerPulse();csShake(5);csFloatProfit(profit);
      csBigText('📉 -$'+fmtCS(Math.abs(profit))+' LOSS');
      if(typeof vibrate==='function')vibrate([200,100,200]);
    }
    updateCompactUI();if(typeof updateDisplay==='function')updateDisplay();if(typeof saveGameState==='function')saveGameState();
  };
  window.csAutoToggle = function(){
    if(!G||!G.stocks)return;
    G.stockAutoMode=!G.stockAutoMode;
    if(G.stockAutoMode){
      if(typeof smPlayWin==='function')smPlayWin();csFlash('win');csBigText('🤖 AUTO ON');
      if(G.oilCash>50)csAutoNow();
    }
    else { csBigText('AUTO OFF'); csFlash('fail'); }
    if(typeof saveGameState==='function')saveGameState();updateCompactUI();
  };
  window.csIntUp = function(){if(typeof smAdjIntensity==='function')smAdjIntensity(1);var el=document.getElementById('cs-intensity');if(el)el.textContent=(G.stockAutoIntensity||10)+'%';};
  window.csIntDn = function(){if(typeof smAdjIntensity==='function')smAdjIntensity(-1);var el=document.getElementById('cs-intensity');if(el)el.textContent=(G.stockAutoIntensity||10)+'%';};

  function wireButtons(){
    // Backup: also wire via JS in case inline onclick somehow doesn't work
    var buyBtn=document.getElementById('cs-buy-btn');if(buyBtn) buyBtn.onclick=window.csBuy;
    var sellBtn=document.getElementById('cs-sell-btn');if(sellBtn) sellBtn.onclick=window.csSell;
    var autoBtn=document.getElementById('cs-auto-btn');if(autoBtn) autoBtn.onclick=window.csAutoToggle;
    var upBtn=document.getElementById('cs-int-up');if(upBtn) upBtn.onclick=window.csIntUp;
    var dnBtn=document.getElementById('cs-int-dn');if(dnBtn) dnBtn.onclick=window.csIntDn;
  }

  // ==================== AUTO TRADE ====================

  function csAutoNow(){
    if(!G||!G.stocks||!G.stockAutoMode) return;
    var pct=(G.stockAutoIntensity||10)/100,bestBuy=null,bestPrice=Infinity;
    for(var i=0;i<PEOPLE_TICKERS.length;i++){var t=PEOPLE_TICKERS[i],s=G.stocks[t];if(s.shares<200&&s.price<bestPrice){bestBuy=t;bestPrice=s.price;}}
    if(bestBuy&&G.oilCash>=G.stocks[bestBuy].price){
      var spend=Math.min(Math.max(Math.floor(G.oilCash*pct),Math.ceil(G.stocks[bestBuy].price)),G.oilCash);
      var qty=Math.max(1,Math.floor(spend/G.stocks[bestBuy].price));
      if(G.stocks[bestBuy].shares+qty>200)qty=200-G.stocks[bestBuy].shares;
      if(qty>0){G.oilCash=safeCash(G.oilCash-G.stocks[bestBuy].price*qty);G.stocks[bestBuy].shares+=qty;if(typeof smPlayBuy==='function')smPlayBuy();}
    }
    for(var i=0;i<PEOPLE_TICKERS.length;i++){
      var t=PEOPLE_TICKERS[i],stock=G.stocks[t];
      if(stock.shares>=2&&stock.history.length>2){
        var entry=stock.history[Math.max(0,stock.history.length-3)];
        if(stock.price>entry*1.15){var sq=Math.max(1,Math.floor(stock.shares/2));G.oilCash=safeCash(G.oilCash+stock.price*sq);stock.shares-=sq;}
      }
    }
  }

  // ==================== ARROW CLICK (capture phase — fires BEFORE oil sell) ====================

  document.addEventListener('click', function(e){
    if(e.target && e.target.id === 'cash-dir-arrow'){
      e.stopPropagation();
      e.stopImmediatePropagation();
      e.preventDefault();
      // Toggle arrow direction
      debtPayMode = !debtPayMode;
      updateArrow();
      updateDebtPill();
      if(typeof showNews==='function') showNews(debtPayMode ? 'FLOW \u2192 DEBT' : 'FLOW \u2193 GAME');
    }
  }, true); // true = capture phase

  // ==================== INIT ====================

  function csInit(){
    wireButtons();
    wireDebtPill();
    addCashArrow();
    updateDebtPill();
    greyStatsBtn(); // Start greyed — unlocks at $1T surplus
    checkStatsUnlock();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(csInit,500); });
  else setTimeout(csInit,500);

  window.updateCompactUI = updateCompactUI;

  // ==================== LIVE MARKET MICRO-TICKS ====================
  // Small random price movements every 3s when stocks view is open
  // Creates natural peaks and troughs like a real day-trading chart

  var _csMomentum = {};
  var _csLiveTimer = null;

  function csLiveTick(){
    if(!G || !G.stocks || !G.stockMarketUnlocked) return;
    var sv = document.getElementById('stocks-view');
    if(!sv || sv.style.display==='none') return;

    for(var i=0; i<STOCK_TICKERS.length; i++){
      var t = STOCK_TICKERS[i];
      var stock = G.stocks[t];
      if(!stock) continue;

      // Init momentum
      if(typeof _csMomentum[t] === 'undefined') _csMomentum[t] = 0;

      // Gaussian-ish random walk (Box-Muller)
      var u1 = Math.random(), u2 = Math.random();
      var randNorm = Math.sqrt(-2 * Math.log(u1 || 0.001)) * Math.cos(2 * Math.PI * u2);

      // Micro-volatility — small moves between rounds
      var vol = 0.01 + Math.random() * 0.006;
      var noise = randNorm * vol;

      // Momentum with decay (creates runs/trends)
      _csMomentum[t] = _csMomentum[t] * 0.82 + noise * 0.35;

      // Mean reversion toward base
      var baseP = STOCK_CONFIG[t] ? STOCK_CONFIG[t].basePrice : 100;
      var meanPull = (baseP - stock.price) / baseP * 0.004;

      // 4% chance of micro-spike
      var spike = 0;
      if(Math.random() < 0.04) spike = (Math.random() - 0.5) * vol * 5;

      var pctChange = _csMomentum[t] + meanPull + spike;
      stock.price = Math.max(2, Math.round(stock.price * (1 + pctChange) * 100) / 100);

      // Push to history (60 points for smooth chart)
      stock.history.push(stock.price);
      if(stock.history.length > 60) stock.history.shift();
    }
    updateCompactUI();
  }

  // Start live ticks when stocks view opens, stop when it closes
  var _csOrigToggle2 = window.toggleStats;
  window.toggleStats = function(){
    if(_csOrigToggle2) _csOrigToggle2();
    var sv = document.getElementById('stocks-view');
    var visible = sv && sv.style.display !== 'none';
    if(visible && !_csLiveTimer){
      _csLiveTimer = setInterval(csLiveTick, 3000);
    } else if(!visible && _csLiveTimer){
      clearInterval(_csLiveTimer);
      _csLiveTimer = null;
    }
  };

})();
