// ShortFactory Admin Lock
// Activate: visit any page with ?admin=BISCUIT
// Then lock/unlock emoji appears bottom-right, only for you
(function(){
  // Activate admin mode via URL param
  if(location.search.indexOf('admin=BISCUIT')>-1){
    localStorage.setItem('sf_admin','1');
    // Clean URL without reload
    history.replaceState(null,'',location.pathname);
  }

  if(localStorage.getItem('sf_admin')!=='1') return;

  var locked = false;
  var el = document.createElement('div');
  el.id = 'sf-admin-lock';
  el.style.cssText = 'position:fixed;bottom:14px;right:14px;z-index:999999;cursor:pointer;font-size:26px;line-height:1;user-select:none;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.9));transition:transform .15s;';
  document.body.appendChild(el);

  function render(){
    el.textContent = locked ? '🔒' : '🔓';
    el.title = locked ? 'LOCKED — Claude cannot deploy. Click to unlock.' : 'UNLOCKED — Claude can deploy. Click to lock.';
  }

  el.addEventListener('click', function(){
    fetch('/lock-toggle.php?key=BISCUIT',{method:'POST'})
      .then(r=>r.json())
      .then(d=>{ locked=d.locked; render(); })
      .catch(()=>{});
  });

  el.addEventListener('mouseenter',function(){ el.style.transform='scale(1.2)'; });
  el.addEventListener('mouseleave',function(){ el.style.transform='scale(1)'; });

  fetch('/lock-status.php')
    .then(r=>r.json())
    .then(d=>{ locked=d.locked; render(); })
    .catch(()=>{ render(); });
})();
