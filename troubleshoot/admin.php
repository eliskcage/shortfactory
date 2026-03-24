<?php
// ── Password gate ──
define('ADMIN_PW', 'SKYDADDY');
$auth = false;
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['pw'] ?? '') === ADMIN_PW) {
    setcookie('sf_diag_auth', md5(ADMIN_PW . 'sf'), time()+3600, '/', '', false, true);
    $auth = true;
} elseif (($_COOKIE['sf_diag_auth'] ?? '') === md5(ADMIN_PW . 'sf')) {
    $auth = true;
}

if (!$auth) { ?>
<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>▲ DIAGNOSTICS ADMIN</title>
<style>
* {margin:0;padding:0;box-sizing:border-box;}
body{background:#05050d;display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:'Courier New',monospace;}
form{display:flex;flex-direction:column;align-items:center;gap:12px;}
h1{font-size:10px;letter-spacing:0.4em;color:#FFC72C;text-shadow:0 0 16px #FFC72C;}
input{background:rgba(255,199,44,0.06);border:1px solid rgba(255,199,44,0.2);color:#fff;font-family:'Courier New',monospace;font-size:12px;letter-spacing:0.3em;padding:10px 16px;text-align:center;width:200px;}
button{background:#FFC72C;color:#000;border:none;font-family:'Courier New',monospace;font-size:9px;letter-spacing:0.3em;font-weight:bold;padding:10px 24px;cursor:pointer;}
</style>
</head><body>
<form method="POST">
  <h1>▲ DIAGNOSTICS ADMIN</h1>
  <input type="password" name="pw" placeholder="PASSWORD" autofocus>
  <button type="submit">ENTER</button>
</form>
</body></html>
<?php exit; }

// ── Load reports ──
$data_dir = __DIR__ . '/data/';
$file = $data_dir . 'reports.jsonl';
$reports = [];
if (file_exists($file)) {
    $lines = array_slice(file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES), -200);
    foreach (array_reverse($lines) as $line) {
        $r = json_decode($line, true);
        if ($r) $reports[] = $r;
    }
}

// ── Filters ──
$filter_sev = $_GET['sev'] ?? '';
$filter_id  = $_GET['id']  ?? '';
if ($filter_sev) $reports = array_filter($reports, fn($r) => $r['severity'] === $filter_sev);
if ($filter_id)  $reports = array_filter($reports, fn($r) => $r['id'] === strtoupper($filter_id));

$counts = ['total'=>0,'FAIL'=>0,'WARN'=>0,'OK'=>0];
if (file_exists($file)) {
    foreach (file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        $r = json_decode($line,true); if (!$r) continue;
        $counts['total']++;
        $counts[$r['severity'] ?? 'OK'] = ($counts[$r['severity'] ?? 'OK'] ?? 0) + 1;
    }
}

function sev_class($s) {
    return $s==='FAIL'?'fail':($s==='WARN'?'warn':'ok');
}
function sev_icon($s) {
    return $s==='FAIL'?'❌':($s==='WARN'?'⚠️':'✅');
}
function fmt_time($ts) {
    return date('d M H:i', $ts);
}
function short_ua($ua) {
    if (preg_match('/Android/', $ua)) return 'Android';
    if (preg_match('/iPhone|iPad/', $ua)) return 'iOS';
    if (preg_match('/Windows/', $ua)) return 'Windows';
    if (preg_match('/Mac/', $ua)) return 'macOS';
    return substr($ua, 0, 20);
}
function short_browser($ua) {
    if (preg_match('/Chrome\/([\d]+)/', $ua, $m) && !strpos($ua,'Edg')) return 'Chrome '.$m[1];
    if (preg_match('/Firefox\/([\d]+)/', $ua, $m)) return 'Firefox '.$m[1];
    if (preg_match('/Safari/', $ua) && !strpos($ua,'Chrome')) return 'Safari';
    if (preg_match('/Edg\/([\d]+)/', $ua, $m)) return 'Edge '.$m[1];
    return substr($ua,0,12);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>▲ DIAGNOSTICS ADMIN</title>
<style>
* {margin:0;padding:0;box-sizing:border-box;}
body{background:#05050d;font-family:'Courier New',monospace;color:rgba(255,255,255,0.8);}
header{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid rgba(255,199,44,0.12);}
header h1{font-size:10px;letter-spacing:0.4em;color:#FFC72C;text-shadow:0 0 12px #FFC72C;}
header a{font-size:7px;letter-spacing:0.2em;color:rgba(255,199,44,0.4);text-decoration:none;}

/* Stats bar */
.stats{display:flex;gap:12px;padding:14px 20px;border-bottom:1px solid rgba(255,199,44,0.08);}
.stat{display:flex;flex-direction:column;align-items:center;gap:3px;}
.stat-val{font-size:22px;font-weight:bold;color:#FFC72C;text-shadow:0 0 10px #FFC72C;}
.stat-lbl{font-size:7px;letter-spacing:0.2em;color:rgba(255,199,44,0.35);}
.stat-val.fail{color:#ff3250;text-shadow:0 0 10px #ff3250;}
.stat-val.warn{color:#ffa000;text-shadow:0 0 10px #ffa000;}
.stat-val.ok  {color:#00c850;text-shadow:0 0 10px #00c850;}

/* Filter bar */
.filters{display:flex;gap:8px;padding:12px 20px;flex-wrap:wrap;}
.filter-btn{background:transparent;border:1px solid rgba(255,199,44,0.2);color:rgba(255,199,44,0.5);
  font-family:'Courier New',monospace;font-size:7px;letter-spacing:0.2em;padding:5px 12px;cursor:pointer;}
.filter-btn.active,.filter-btn:hover{background:rgba(255,199,44,0.1);color:#FFC72C;}
.filter-form{display:flex;gap:4px;}
.filter-form input{background:rgba(255,199,44,0.05);border:1px solid rgba(255,199,44,0.15);
  color:#fff;font-family:'Courier New',monospace;font-size:7px;letter-spacing:0.2em;padding:5px 8px;width:90px;}
.filter-form button{background:#FFC72C;color:#000;border:none;font-family:'Courier New',monospace;
  font-size:7px;letter-spacing:0.2em;padding:5px 8px;cursor:pointer;}

/* Table */
table{width:100%;border-collapse:collapse;}
th{font-size:7px;letter-spacing:0.2em;color:rgba(255,199,44,0.4);text-align:left;
  padding:8px 10px;border-bottom:1px solid rgba(255,199,44,0.1);white-space:nowrap;}
td{font-size:8px;letter-spacing:0.05em;padding:10px 10px;border-bottom:1px solid rgba(255,255,255,0.04);
  vertical-align:top;}
tr:hover td{background:rgba(255,199,44,0.03);}
tr.clickable{cursor:pointer;}
.sev-fail{color:#ff3250;} .sev-warn{color:#ffa000;} .sev-ok{color:#00c850;}
.id-cell{color:#FFC72C;letter-spacing:0.2em;font-size:9px;}
.note-cell{color:rgba(255,255,255,0.5);font-style:italic;max-width:200px;word-break:break-word;}
.no-data{padding:30px;text-align:center;font-size:9px;letter-spacing:0.3em;color:rgba(255,199,44,0.2);}

/* Detail panel */
#detail{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.9);z-index:100;overflow-y:auto;}
.detail-inner{max-width:700px;margin:0 auto;padding:24px 20px 60px;}
.detail-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;}
.detail-id{font-size:14px;letter-spacing:0.4em;color:#FFC72C;text-shadow:0 0 16px #FFC72C;}
.close-btn{background:transparent;border:1px solid rgba(255,199,44,0.3);color:rgba(255,199,44,0.6);
  font-family:'Courier New',monospace;font-size:8px;letter-spacing:0.2em;padding:6px 14px;cursor:pointer;}
.close-btn:hover{background:rgba(255,199,44,0.1);}
.detail-section{margin-bottom:14px;border:1px solid rgba(255,199,44,0.1);}
.detail-section h3{font-size:8px;letter-spacing:0.3em;color:#FFC72C;padding:8px 12px;
  background:rgba(255,199,44,0.05);border-bottom:1px solid rgba(255,199,44,0.08);}
.detail-rows{padding:6px 12px;}
.detail-row{display:flex;justify-content:space-between;align-items:flex-start;
  padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:7px;gap:10px;}
.detail-row:last-child{border:none;}
.dr-label{color:rgba(255,255,255,0.4);letter-spacing:0.1em;flex-shrink:0;}
.dr-val{color:rgba(255,255,255,0.75);text-align:right;word-break:break-word;max-width:70%;}
.dr-val.ok{color:#00c850;} .dr-val.warn{color:#ffa000;} .dr-val.fail{color:#ff3250;}
.err-block{background:rgba(255,50,80,0.06);border-left:2px solid rgba(255,50,80,0.3);
  padding:6px 10px;margin:4px 0;font-size:7px;color:#ff6464;line-height:1.7;word-break:break-word;}
.ok-block{font-size:8px;letter-spacing:0.2em;color:#00c850;padding:8px 12px;}
.meta-row{display:flex;flex-wrap:wrap;gap:6px;padding:8px 12px;}
.meta-pill{font-size:7px;letter-spacing:0.1em;color:rgba(255,199,44,0.5);
  background:rgba(255,199,44,0.06);padding:3px 8px;border:1px solid rgba(255,199,44,0.1);}
</style>
</head>
<body>

<header>
  <h1>▲ DIAGNOSTICS ADMIN</h1>
  <a href="/troubleshoot/">USER VIEW</a>
</header>

<div class="stats">
  <div class="stat"><span class="stat-val"><?= $counts['total'] ?></span><span class="stat-lbl">TOTAL</span></div>
  <div class="stat"><span class="stat-val fail"><?= $counts['FAIL'] ?></span><span class="stat-lbl">FAIL</span></div>
  <div class="stat"><span class="stat-val warn"><?= $counts['WARN'] ?></span><span class="stat-lbl">WARN</span></div>
  <div class="stat"><span class="stat-val ok"><?= $counts['OK'] ?></span><span class="stat-lbl">OK</span></div>
</div>

<div class="filters">
  <a href="?"><button class="filter-btn <?= !$filter_sev?'active':'' ?>">ALL</button></a>
  <a href="?sev=FAIL"><button class="filter-btn <?= $filter_sev==='FAIL'?'active':'' ?>">❌ FAIL</button></a>
  <a href="?sev=WARN"><button class="filter-btn <?= $filter_sev==='WARN'?'active':'' ?>">⚠️ WARN</button></a>
  <a href="?sev=OK"><button class="filter-btn <?= $filter_sev==='OK'?'active':'' ?>">✅ OK</button></a>
  <form class="filter-form" method="GET">
    <input type="text" name="id" value="<?= htmlspecialchars($filter_id) ?>" placeholder="REPORT ID">
    <button type="submit">GO</button>
  </form>
</div>

<?php if (empty($reports)): ?>
  <div class="no-data">▲ NO REPORTS YET</div>
<?php else: ?>
<table>
  <thead>
    <tr>
      <th>ID</th><th>TIME</th><th>SEV</th><th>DEVICE</th><th>BROWSER</th>
      <th>ERRORS</th><th>NET FAILS</th><th>NOTE</th>
    </tr>
  </thead>
  <tbody>
  <?php foreach ($reports as $r):
    $secs   = $r['sections'] ?? [];
    $jsErrs = count($secs['errors']['js']  ?? []);
    $netFls = count($secs['errors']['net'] ?? []);
    $sev    = $r['severity'] ?? 'OK';
  ?>
    <tr class="clickable" onclick="showDetail(<?= htmlspecialchars(json_encode($r)) ?>)">
      <td class="id-cell"><?= htmlspecialchars($r['id']) ?></td>
      <td><?= fmt_time($r['at']) ?></td>
      <td class="sev-<?= strtolower($sev) ?>"><?= sev_icon($sev) ?> <?= $sev ?></td>
      <td><?= htmlspecialchars(short_ua($r['ua']??'')) ?></td>
      <td><?= htmlspecialchars(short_browser($r['ua']??'')) ?></td>
      <td class="<?= $jsErrs?'sev-fail':'' ?>"><?= $jsErrs ?: '—' ?></td>
      <td class="<?= $netFls?'sev-fail':'' ?>"><?= $netFls ?: '—' ?></td>
      <td class="note-cell"><?= $r['note'] ? htmlspecialchars(substr($r['note'],0,60)) : '' ?></td>
    </tr>
  <?php endforeach; ?>
  </tbody>
</table>
<?php endif; ?>

<!-- Detail overlay -->
<div id="detail">
  <div class="detail-inner" id="detail-inner"></div>
</div>

<script>
function showDetail(r) {
  const secs = r.sections || {};
  const sev = r.severity || 'OK';
  const sevCls = sev==='FAIL'?'fail':sev==='WARN'?'warn':'ok';

  let html = `
    <div class="detail-header">
      <div class="detail-id">▲ ${r.id}</div>
      <button class="close-btn" onclick="closeDetail()">✕ CLOSE</button>
    </div>
  `;

  // Meta
  html += `<div class="detail-section"><h3>META</h3><div class="meta-row">
    <span class="meta-pill">${new Date(r.at*1000).toLocaleString()}</span>
    <span class="meta-pill">${r.ip||'?'}</span>
    <span class="meta-pill sev-${sevCls}">${sev}</span>
    ${r.note ? `<span class="meta-pill" style="color:rgba(255,255,255,0.6)">"${esc(r.note)}"</span>` : ''}
  </div>
  <div class="detail-rows">
    <div class="detail-row"><span class="dr-label">URL</span><span class="dr-val">${esc(r.url||'')}</span></div>
    <div class="detail-row"><span class="dr-label">REFERRER</span><span class="dr-val">${esc(r.ref||'—')}</span></div>
    <div class="detail-row"><span class="dr-label">USER AGENT</span><span class="dr-val">${esc(r.ua||'')}</span></div>
  </div></div>`;

  // Each section
  const secLabels = {
    device:'DEVICE & BROWSER', apis:'SERVER ENDPOINTS',
    storage:'LOCAL STORAGE & SOUL', caps:'BROWSER CAPABILITIES',
    perf:'PERFORMANCE', errors:'ERROR LOG'
  };

  for (const [key, label] of Object.entries(secLabels)) {
    const sec = secs[key];
    if (!sec) continue;
    const s = sec.status || 'INFO';
    const sCls = s==='FAIL'?'fail':s==='WARN'?'warn':s==='OK'?'ok':'';
    html += `<div class="detail-section"><h3>${label} <span class="sev-${sCls}" style="float:right">${s}</span></h3>`;

    if (key === 'errors') {
      const js = sec.js || [], net = sec.net || [];
      if (!js.length && !net.length) {
        html += `<div class="ok-block">✅ NO ERRORS</div>`;
      } else {
        html += `<div class="detail-rows">`;
        js.forEach(e => {
          html += `<div class="err-block"><strong>JS: ${esc(e.type)}</strong><br>${esc(e.msg)}`;
          if (e.src) html += `<br><span style="opacity:0.5">${esc(e.src)}:${e.line}</span>`;
          html += `</div>`;
        });
        net.forEach(e => {
          html += `<div class="err-block"><strong>NET: ${esc(e.url)}</strong><br>Status: ${esc(String(e.status))} · ${e.ms}ms`;
          if (e.err) html += `<br><span style="opacity:0.5">${esc(e.err)}</span>`;
          html += `</div>`;
        });
        html += `</div>`;
      }
    } else if (sec.rows) {
      html += `<div class="detail-rows">`;
      sec.rows.forEach(row => {
        html += `<div class="detail-row">
          <span class="dr-label">${row.icon||''} ${esc(row.label||'')}</span>
          <span class="dr-val ${row.cls||''}">${esc(row.val||'')}</span>
        </div>`;
      });
      html += `</div>`;
    }
    html += `</div>`;
  }

  html += `<div style="margin-top:16px;">
    <button class="close-btn" onclick="closeDetail()" style="width:100%">✕ CLOSE DETAIL</button>
  </div>`;

  document.getElementById('detail-inner').innerHTML = html;
  document.getElementById('detail').style.display = 'block';
  document.getElementById('detail').scrollTop = 0;
}

function closeDetail() {
  document.getElementById('detail').style.display = 'none';
}

function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

document.getElementById('detail').addEventListener('click', e => {
  if (e.target === document.getElementById('detail')) closeDetail();
});
</script>
</body>
</html>
