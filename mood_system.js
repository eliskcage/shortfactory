// ==================== MOOD SYSTEM ====================
// Icons are GREY and disabled. They light up when Trump uses them in-game.
// Hooks into doAction, playBlackOps, nukeDecision, applyWheelEffects.
(function(){
  var MM_ITEMS = [
    {id:'oil',icon:'\u{1F6E2}\uFE0F',name:'OIL',cat:'action',mood:5,msg:'Oil pumping!'},
    {id:'home',icon:'\u{1F3E0}',name:'HOME',cat:'action',mood:8,msg:'Homeland secured!'},
    {id:'psyop',icon:'\u{1F9E0}',name:'PSYOP',cat:'action',mood:10,msg:'Deep State exposed!'},
    {id:'aid',icon:'\u{1F3E5}',name:'AID',cat:'action',mood:3,msg:'Aid cut!'},
    {id:'war',icon:'\u2694\uFE0F',name:'WAR',cat:'action',mood:-5,msg:'War declared!'},
    {id:'audit',icon:'\u{1F50D}',name:'AUDIT',cat:'action',mood:15,msg:'AUDIT DROPPED!'},
    {id:'drone',icon:'\u2708\uFE0F',name:'DRONE',cat:'action',mood:4,msg:'Target eliminated!'},
    {id:'loan',icon:'\u{1F4B0}',name:'LOAN',cat:'action',mood:-2,msg:'Elon loan!'},
    {id:'tweet',icon:'\u{1F4F1}',name:'TWEET',cat:'action',mood:2,msg:'Mean tweet!'},
    {id:'regime',icon:'\u{1F3F4}',name:'REGIME',cat:'ops',mood:15,msg:'REGIME CHANGE!'},
    {id:'extract',icon:'\u{1F4E6}',name:'EXTRACT',cat:'ops',mood:10,msg:'ASSET EXTRACTION!'},
    {id:'flag',icon:'\u{1F6A9}',name:'FLAG',cat:'ops',mood:18,msg:'FALSE FLAG!'},
    {id:'cyber',icon:'\u{1F4BB}',name:'CYBER',cat:'ops',mood:12,msg:'CYBER ATTACK!'},
    {id:'strike',icon:'\u{1F680}',name:'STRIKE',cat:'ops',mood:8,msg:'DRONE STRIKE!'},
    {id:'wet',icon:'\u{1F52A}',name:'WETWORK',cat:'ops',mood:22,msg:'WETWORK!'},
    {id:'coup',icon:'\u{1F464}',name:'COUP',cat:'ops',mood:28,msg:'SHADOW COUP!'},
    {id:'jesus',icon:'\u271D\uFE0F',name:'JESUS',cat:'wheel',mood:35,msg:'JESUS RETURNS!'},
    {id:'timewarp',icon:'\u23F0',name:'TIME',cat:'wheel',mood:22,msg:'TIME TRAVEL!'},
    {id:'zombie',icon:'\u{1F9DF}',name:'ZOMBIE',cat:'wheel',mood:-18,msg:'ZOMBIE PLAGUE!'},
    {id:'tsunami',icon:'\u{1F30A}',name:'TSUNAMI',cat:'wheel',mood:-14,msg:'MEGA TSUNAMI!'},
    {id:'plague',icon:'\u{1F9A0}',name:'PLAGUE',cat:'wheel',mood:-22,msg:'SUPER PLAGUE!'},
    {id:'pest',icon:'\u{1F41B}',name:'PEST',cat:'wheel',mood:-10,msg:'PESTILENCE!'},
    {id:'nazi',icon:'\u{1F480}',name:'NAZI',cat:'wheel',mood:-20,msg:'NAZI UPRISING!'},
    {id:'famine',icon:'\u{1F33E}',name:'FAMINE',cat:'wheel',mood:-16,msg:'GLOBAL FAMINE!'},
    {id:'alien',icon:'\u{1F47D}',name:'ALIEN',cat:'wheel',mood:-28,msg:'ALIEN INVASION!'},
    {id:'asteroid',icon:'\u2604\uFE0F',name:'ASTEROID',cat:'wheel',mood:-35,msg:'ASTEROID IMPACT!'},
    {id:'biowar',icon:'\u2623\uFE0F',name:'BIO',cat:'wheel',mood:-22,msg:'BIO WARFARE!'},
    {id:'locust',icon:'\u{1F997}',name:'LOCUST',cat:'wheel',mood:-10,msg:'LOCUST SWARM!'},
    {id:'skynet',icon:'\u{1F916}',name:'SKYNET',cat:'wheel',mood:-30,msg:'SKYNET AWAKENS!'},
    {id:'volcano',icon:'\u{1F30B}',name:'VOLCANO',cat:'wheel',mood:-22,msg:'SUPER VOLCANO!'},
    {id:'ruwins',icon:'\u{1F1F7}\u{1F1FA}',name:'RU WIN',cat:'wheel',mood:-20,msg:'RUSSIA WINS!'},
    {id:'rufalls',icon:'\u{1F3C6}',name:'RU FALL',cat:'wheel',mood:12,msg:'RUSSIA FALLS!'},
    {id:'cnwins',icon:'\u{1F1E8}\u{1F1F3}',name:'CN WIN',cat:'wheel',mood:-25,msg:'CHINA WINS!'},
    {id:'cnfalls',icon:'\u{1F389}',name:'CN FALL',cat:'wheel',mood:15,msg:'CHINA FALLS!'},
    {id:'nk_somalia',icon:'\u2622\uFE0F',name:'SOMALIA',cat:'nuke',mood:20,msg:'NUKED SOMALIA!'},
    {id:'nk_iran',icon:'\u2622\uFE0F',name:'IRAN',cat:'nuke',mood:22,msg:'NUKED IRAN!'},
    {id:'nk_nkorea',icon:'\u2622\uFE0F',name:'N.KOREA',cat:'nuke',mood:25,msg:'NUKED N.KOREA!'},
    {id:'nk_syria',icon:'\u2622\uFE0F',name:'SYRIA',cat:'nuke',mood:18,msg:'NUKED SYRIA!'},
    {id:'nk_venez',icon:'\u2622\uFE0F',name:'VENEZ',cat:'nuke',mood:20,msg:'NUKED VENEZUELA!'},
    {id:'nk_afghan',icon:'\u2622\uFE0F',name:'AFGHAN',cat:'nuke',mood:15,msg:'NUKED AFGHANISTAN!'},
    {id:'nk_iraq',icon:'\u2622\uFE0F',name:'IRAQ',cat:'nuke',mood:18,msg:'NUKED IRAQ!'},
    {id:'nk_china',icon:'\u2622\uFE0F',name:'CHINA',cat:'nuke',mood:-15,msg:'NUKED CHINA!'},
    {id:'nk_russia',icon:'\u2622\uFE0F',name:'RUSSIA',cat:'nuke',mood:-20,msg:'NUKED RUSSIA!'},
    {id:'nk_mexico',icon:'\u2622\uFE0F',name:'MEXICO',cat:'nuke',mood:10,msg:'NUKED MEXICO!'}
  ];

  // Mappings from game events to mood IDs
  var OPS_MAP = ['regime','extract','flag','cyber','strike','wet','coup'];
  var NUKE_MAP = {'SOMALIA':'nk_somalia','IRAN':'nk_iran','NORTH KOREA':'nk_nkorea','SYRIA':'nk_syria','VENEZUELA':'nk_venez','AFGHANISTAN':'nk_afghan','IRAQ':'nk_iraq','CHINA':'nk_china','RUSSIA':'nk_russia','MEXICO':'nk_mexico'};
  var WHEEL_MAP = {'jesus':'jesus','timetravel':'timewarp','zombie':'zombie','tsunami':'tsunami','plague':'plague','pestilence':'pest','nazi':'nazi','famine':'famine','alien':'alien','asteroid':'asteroid','biowar':'biowar','locust':'locust','skynet':'skynet','volcano':'volcano','russiawins':'ruwins','russialoose':'rufalls','chinawins':'cnwins','chinaloose':'cnfalls'};

  var mmMood=0,mmHist=[0],mmCounts={},mmTotal=0,MM_MAX=50,mmEvents=[];
  for(var i=0;i<MM_ITEMS.length;i++)mmCounts[MM_ITEMS[i].id]=0;

  // Build grids — NO onclick, icons start GREY
  function mmBuildGrid(elId,cat){
    var el=document.getElementById(elId);if(!el)return;var h='';
    for(var i=0;i<MM_ITEMS.length;i++){var it=MM_ITEMS[i];if(it.cat!==cat)continue;
      h+='<div class="mm-tile" id="mm-'+it.id+'"><div class="ico">'+it.icon+'</div><div class="cnt" id="mmc-'+it.id+'">0</div><div class="lbl">'+it.name+'</div></div>';
    }el.innerHTML=h;
  }

  setTimeout(function(){
    mmBuildGrid('mmGridActions','action');
    mmBuildGrid('mmGridOps','ops');
    mmBuildGrid('mmGridWheel','wheel');
    mmBuildGrid('mmGridNukes','nuke');
    mmUpdateMeter();mmUpdateChart();
  },200);

  // Called by game hooks — lights up icon, updates mood + chart
  function mmActivate(id){
    var item=null;for(var i=0;i<MM_ITEMS.length;i++){if(MM_ITEMS[i].id===id){item=MM_ITEMS[i];break;}}if(!item)return;
    mmCounts[id]++;mmTotal++;
    var tile=document.getElementById('mm-'+id);
    var cntEl=document.getElementById('mmc-'+id);
    if(cntEl){cntEl.textContent=mmCounts[id];cntEl.classList.add('has');}
    // Light it up (remove grey)
    if(tile)tile.classList.add('lit');
    var raw=item.mood;if(mmCounts[id]>5)raw=Math.round(raw*(5/mmCounts[id]));
    mmMood=Math.max(-100,Math.min(100,mmMood+raw));mmHist.push(mmMood);if(mmHist.length>MM_MAX)mmHist.shift();
    if(tile){
      var fc=item.cat==='nuke'?'flash-nuke':(item.mood>=0?'flash-good':'flash-bad');
      tile.classList.add(fc);setTimeout(function(){tile.classList.remove(fc);},300);
      var fl=document.createElement('div');fl.className='mm-imp';fl.style.color=raw>=0?'#00ff88':'#ff4444';fl.textContent=(raw>=0?'+':'')+raw;tile.appendChild(fl);setTimeout(function(){fl.remove();},800);
    }
    mmAddEvent(item.msg,raw>=0?'good':(item.cat==='nuke'?'nuke':'bad'));
    mmUpdateMeter();mmUpdateChart();
    setTimeout(function(){mmMood=Math.round(mmMood*0.93);mmHist.push(mmMood);if(mmHist.length>MM_MAX)mmHist.shift();mmUpdateMeter();mmUpdateChart();},1500);
  }

  function mmAddEvent(msg,type){
    mmEvents.unshift({msg:msg,type:type});if(mmEvents.length>8)mmEvents.pop();
    var h='';for(var i=0;i<mmEvents.length;i++){h+='<div class="mm-ev '+mmEvents[i].type+'">'+mmEvents[i].msg+'</div>';}
    var el=document.getElementById('mmEventLog');if(el)el.innerHTML=h;
    var el2=document.getElementById('mmEventLog2');if(el2)el2.innerHTML=h;
  }

  function mmUpdateMeter(){
    var pct=((mmMood+100)/200)*100;var ptr=document.getElementById('mmPtr');if(ptr)ptr.style.left=pct+'%';
    var label,color;
    if(mmMood<=-60){label='\u{1F480} DEPRESSION';color='#ff0000';}
    else if(mmMood<=-30){label='\u{1F4C9} CRASHING';color='#ff4444';}
    else if(mmMood<=-10){label='\u{1F4C9} BEARISH';color='#ff8844';}
    else if(mmMood<10){label='\u{1F610} NEUTRAL';color='#ffcc00';}
    else if(mmMood<30){label='\u{1F4C8} BULLISH';color='#aaff00';}
    else if(mmMood<60){label='\u{1F4C8} ROARING';color='#44ff44';}
    else{label='\u{1F680} ECSTASY';color='#00ff88';}
    var lbl=document.getElementById('mmLabel');
    if(lbl){lbl.textContent=label;lbl.style.color=color;lbl.style.textShadow='0 0 10px '+color;
      if(mmMood<=-60||mmMood>=60)lbl.classList.add('extreme');else lbl.classList.remove('extreme');}
    var sc=document.getElementById('mmScore');if(sc)sc.textContent='MOOD: '+mmMood+' | ACTIONS: '+mmTotal;
  }

  var W=340,H=55,MID=27.5;
  function mmUpdateChart(){
    var len=mmHist.length;if(len<1)return;var step=len>1?W/(len-1):0;
    var lP=[],uP=[],dP=[];
    for(var i=0;i<len;i++){var x=len===1?W/2:Math.round(i*step);var y=MID-Math.round((mmHist[i]/100)*MID);y=Math.max(1,Math.min(H-1,y));lP.push(x+','+y);uP.push(x+','+Math.min(y,MID));dP.push(x+','+Math.max(y,MID));}
    var lastX=len===1?W/2:Math.round((len-1)*step);
    var ln=document.getElementById('mmLine');if(ln)ln.setAttribute('points',lP.join(' '));
    var lastY=MID-Math.round((mmHist[len-1]/100)*MID);lastY=Math.max(1,Math.min(H-1,lastY));
    var d=document.getElementById('mmDot');if(d){d.setAttribute('cx',lastX);d.setAttribute('cy',lastY);d.setAttribute('fill',mmMood>=0?'#00ff88':'#ff4444');}
    if(ln){if(mmMood>=30){ln.style.stroke='#00ff88';ln.style.filter='drop-shadow(0 0 4px #00ff88)';}else if(mmMood<=-30){ln.style.stroke='#ff4444';ln.style.filter='drop-shadow(0 0 4px #ff4444)';}else{ln.style.stroke='#ffd700';ln.style.filter='drop-shadow(0 0 4px #ffd700)';}}
    var fu=document.getElementById('mmFillUp');if(fu)fu.setAttribute('points',uP.join(' ')+' '+lastX+','+MID+' 0,'+MID);
    var fd=document.getElementById('mmFillDn');if(fd)fd.setAttribute('points',dP.join(' ')+' '+lastX+','+MID+' 0,'+MID);
    // Also update big chart if visible
    mmUpdateBigChart();
  }

  // ==================== BIG CHART (GRAPH VIEW) ====================
  var BW=340,BH=160,BMID=80;
  function mmUpdateBigChart(){
    var len=mmHist.length;if(len<1)return;var step=len>1?BW/(len-1):0;
    var lP=[],uP=[],dP=[];
    for(var i=0;i<len;i++){
      var x=len===1?BW/2:Math.round(i*step);
      var y=BMID-Math.round((mmHist[i]/100)*BMID*0.9);
      y=Math.max(2,Math.min(BH-2,y));
      lP.push(x+','+y);uP.push(x+','+Math.min(y,BMID));dP.push(x+','+Math.max(y,BMID));
    }
    var lastX=len===1?BW/2:Math.round((len-1)*step);
    var ln=document.getElementById('mmBLine');if(ln)ln.setAttribute('points',lP.join(' '));
    var lastY=BMID-Math.round((mmHist[len-1]/100)*BMID*0.9);lastY=Math.max(2,Math.min(BH-2,lastY));
    var d=document.getElementById('mmBDot');if(d){d.setAttribute('cx',lastX);d.setAttribute('cy',lastY);d.setAttribute('fill',mmMood>=0?'#00ff88':'#ff4444');}
    if(ln){if(mmMood>=30){ln.style.stroke='#00ff88';ln.style.filter='drop-shadow(0 0 6px #00ff88)';}else if(mmMood<=-30){ln.style.stroke='#ff4444';ln.style.filter='drop-shadow(0 0 6px #ff4444)';}else{ln.style.stroke='#ffd700';ln.style.filter='drop-shadow(0 0 6px #ffd700)';}}
    var fu=document.getElementById('mmBFillUp');if(fu)fu.setAttribute('points',uP.join(' ')+' '+lastX+','+BMID+' 0,'+BMID);
    var fd=document.getElementById('mmBFillDn');if(fd)fd.setAttribute('points',dP.join(' ')+' '+lastX+','+BMID+' 0,'+BMID);
    // Update mood value display
    var mv=document.getElementById('mmBigMoodVal');
    if(mv){mv.textContent=(mmMood>=0?'+':'')+mmMood;mv.style.color=mmMood>=0?'#00ff88':'#ff4444';mv.style.textShadow='0 0 6px '+(mmMood>=0?'#00ff88':'#ff4444');}
    // Update health hearts from game state
    var hp=document.getElementById('mmBigHP');
    if(hp && typeof G!=='undefined' && G.trumpHP!==undefined){
      var maxHP=G.trumpMaxHP||100;var cur=G.trumpHP;var full=Math.floor(cur/20);var half=(cur%20>=10)?1:0;var empty=Math.max(0,Math.floor(maxHP/20)-full-half);
      var h='';for(var i=0;i<full;i++)h+='\u2764\uFE0F';if(half)h+='\u{1FA76}';for(var i=0;i<empty;i++)h+='\u{1F5A4}';
      hp.innerHTML=h+'<div style="font-family:\'Press Start 2P\',monospace;font-size:4px;color:#ff6666;text-align:right;margin-top:1px">'+cur+'/'+maxHP+' HP</div>';
    }
  }

  // ==================== TOGGLE ICONS / GRAPH ====================
  var mmViewMode = 'icons';
  window.mmToggleView = function(mode){
    mmViewMode = mode || (mmViewMode === 'icons' ? 'graph' : 'icons');
    var icons = document.getElementById('mood-icons-panel');
    var graph = document.getElementById('mood-graph-panel');
    var tabI = document.getElementById('mm-tab-icons');
    var tabG = document.getElementById('mm-tab-graph');
    if(mmViewMode === 'graph'){
      if(icons) icons.style.display = 'none';
      if(graph){graph.style.display = 'flex';graph.style.flexDirection='column';}
      if(tabI){tabI.style.border='1px solid #333';tabI.style.background='transparent';tabI.style.color='#666';tabI.style.textShadow='none';}
      if(tabG){tabG.style.border='1px solid #ffd700';tabG.style.background='rgba(255,215,0,0.2)';tabG.style.color='#ffd700';tabG.style.textShadow='0 0 4px #ffd700';}
      mmUpdateBigChart();
    } else {
      if(icons){icons.style.display='flex';icons.style.flexDirection='column';}
      if(graph) graph.style.display = 'none';
      if(tabG){tabG.style.border='1px solid #333';tabG.style.background='transparent';tabG.style.color='#666';tabG.style.textShadow='none';}
      if(tabI){tabI.style.border='1px solid #ffd700';tabI.style.background='rgba(255,215,0,0.2)';tabI.style.color='#ffd700';tabI.style.textShadow='0 0 4px #ffd700';}
    }
  };

  // ==================== HOOK INTO REAL GAME ====================
  // Wrap doAction
  var _origDoAction = window.doAction;
  window.doAction = function(action, mult, playVideo) {
    _origDoAction.apply(this, arguments);
    var mmId = (action === 'meantweet') ? 'tweet' : action;
    mmActivate(mmId);
  };

  // Wrap playBlackOps
  var _origPlayBlackOps = window.playBlackOps;
  window.playBlackOps = function(idx) {
    _origPlayBlackOps.apply(this, arguments);
    if(OPS_MAP[idx]) mmActivate(OPS_MAP[idx]);
  };

  // Wrap nukeDecision
  var _origNukeDecision = window.nukeDecision;
  window.nukeDecision = function(yes) {
    _origNukeDecision.apply(this, arguments);
    if(yes){
      var targetEl = document.getElementById('nuke-target');
      if(targetEl){
        var tgt = targetEl.textContent.trim();
        var mmId = NUKE_MAP[tgt];
        if(mmId) mmActivate(mmId);
      }
    }
  };

  // Wrap applyWheelEffects
  var _origApplyWheel = window.applyWheelEffects;
  window.applyWheelEffects = function(effects) {
    _origApplyWheel.apply(this, arguments);
    if(effects && effects.name){
      var name = effects.name.toLowerCase().replace(/\s+/g,'');
      for(var key in WHEEL_MAP){
        if(name.indexOf(key)!==-1){mmActivate(WHEEL_MAP[key]);return;}
      }
    }
  };

  // ==================== KILL ALL MAP-ONLY ELEMENTS ====================
  function killMapStuff(){
    if(typeof stopSlotMachine==='function')stopSlotMachine();
    var wo=document.getElementById('wheel-overlay');if(wo)wo.classList.remove('show');
    if(typeof wheelTimer!=='undefined')clearInterval(wheelTimer);
    if(typeof wheelSpinning!=='undefined')wheelSpinning=false;
    var ed=document.getElementById('emergency-drop');if(ed)ed.classList.remove('show');
    var smi=document.getElementById('slot-machine-icon');if(smi){smi.style.display='none';smi.classList.remove('active');}
    var bai=document.getElementById('blackops-alert-icon');if(bai)bai.classList.remove('show');
    var bat=document.getElementById('blackops-alert-text');if(bat)bat.classList.remove('show');
    var bo=document.getElementById('blackops-overlay');if(bo)bo.classList.remove('show');
    var nc=document.getElementById('nuke-confirm');if(nc)nc.classList.remove('show');
    var dw=document.getElementById('danger-warning');if(dw)dw.classList.remove('show');
  }
  function restoreMapStuff(){
    var smi=document.getElementById('slot-machine-icon');if(smi)smi.style.display='';
  }

  // ==================== OVERRIDE TOGGLESTATS: 3-STATE CYCLE ====================
  // State 0: MAP (closed). State 1: MOOD. State 2: STOCKS.
  var statsState = 0;
  window.toggleStats = function() {
    var overlay = document.getElementById('stats-overlay');
    var moodV = document.getElementById('mood-view');
    var stocksV = document.getElementById('stocks-view');
    var btn = document.getElementById('stats-btn');
    var mapSec = document.getElementById('map-section');
    var smOverlay = document.getElementById('stock-market-overlay');
    var threats = document.getElementById('threat-meters');

    if (statsState === 0) {
      // CLOSED -> MOOD
      statsState = 1;
      statsOpen = true;
      killMapStuff();
      overlay.classList.add('show');
      mapSec.classList.add('expanded');
      moodV.style.display = 'flex';
      stocksV.style.display = 'none';
      btn.textContent = 'STOCKS';
      btn.classList.add('active');
      if(threats) threats.style.display='none';
    } else if (statsState === 1) {
      // MOOD -> COMPACT STOCKS
      statsState = 2;
      killMapStuff();
      moodV.style.display = 'none';
      stocksV.style.display = 'flex';
      btn.textContent = 'MAP';
      btn.classList.add('active');
      if(smOverlay){smOverlay.classList.remove('show');smOverlay.style.display='none';}
      if(threats) threats.style.display='none';
    } else {
      // STOCKS -> CLOSED (back to map)
      statsState = 0;
      statsOpen = false;
      overlay.classList.remove('show');
      mapSec.classList.remove('expanded');
      moodV.style.display = 'flex';
      stocksV.style.display = 'none';
      btn.textContent = 'STATS';
      btn.classList.remove('active');
      restoreMapStuff();
      if(threats){threats.style.display='flex';threats.style.opacity='0';threats.style.transition='opacity 0.5s ease';setTimeout(function(){threats.style.opacity='1';},50);threats.style.pointerEvents='auto';}
    }
  };
})();
