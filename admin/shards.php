<?php
// admin/shards.php — Shard Auction Admin
// Access: /admin/shards.php?key=SF_SHARD_ADMIN_2026

define('ADMIN_KEY', 'SF_SHARD_ADMIN_2026');
define('DB_HOST', 'localhost');
define('DB_NAME', 'sf_marketplace');
define('DB_USER', 'sfadmin');
define('DB_PASS', 'SFmarket2026!');

// Satoshi cipher
function satoshi_encrypt($plaintext, $pass) {
    $p = strtoupper($pass); $out = ''; $pl = strlen($p);
    for ($i=0,$n=strlen($plaintext);$i<$n;$i++) {
        $c=ord($plaintext[$i]); $k=ord($p[$i%$pl]);
        $out .= chr((($c-32)+($k-32))%95+32);
    }
    return $out;
}
function satoshi_decrypt($ciphertext, $pass) {
    $p = strtoupper($pass); $out = ''; $pl = strlen($p);
    for ($i=0,$n=strlen($ciphertext);$i<$n;$i++) {
        $c=ord($ciphertext[$i]); $k=ord($p[$i%$pl]);
        $out .= chr((($c-32)-($k-32)+95)%95+32);
    }
    return $out;
}

if (($_GET['key']??'') !== ADMIN_KEY) {
    http_response_code(403);
    die('<h1>403</h1>');
}

$pdo = new PDO('mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8mb4', DB_USER, DB_PASS, [
    PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC
]);

$msg = '';

// Handle POST actions
if ($_SERVER['REQUEST_METHOD']==='POST') {
    $action = $_POST['action']??'';

    if ($action==='close') {
        $id = (int)$_POST['shard_id'];
        $pdo->prepare("UPDATE shards SET state='sold', sold_price=top_bid WHERE id=?")->execute([$id]);
        // Link shard to winner in revert_users
        $sh = $pdo->prepare("SELECT shard_num, top_email FROM shards WHERE id=? LIMIT 1");
        $sh->execute([$id]);
        $sw = $sh->fetch();
        if ($sw && $sw['top_email']) {
            $pdo->prepare("UPDATE revert_users SET shard_won=? WHERE email=?")
                ->execute([$sw['shard_num'], strtolower($sw['top_email'])]);
        }
        $msg = 'Shard #'.$id.' closed as SOLD.'
             . ($sw['top_email'] ? ' Winner: '.$sw['top_email'] : '');
    }

    if ($action==='reopen') {
        $id = (int)$_POST['shard_id'];
        $pdo->prepare("UPDATE shards SET state='available', top_bid=0, top_email=NULL, bid_count=0, sold_price=NULL WHERE id=?")->execute([$id]);
        $pdo->prepare("DELETE FROM shard_bids WHERE shard_id=?")->execute([$id]);
        $msg = 'Shard #'.$id.' reopened.';
    }

    if ($action==='set_story') {
        $id = (int)$_POST['shard_id'];
        $plain = trim($_POST['story_plain']??'');
        $key   = trim($_POST['story_key']??'KILLIAN');
        if ($plain) {
            $enc = satoshi_encrypt($plain, $key);
            $pdo->prepare("UPDATE shards SET story_enc=? WHERE id=?")->execute([$enc, $id]);
            $msg = 'Story content encrypted + saved for shard #'.$id.'.';
        }
    }

    if ($action==='send_key') {
        // Mark winner notified (email sending not implemented here — SMTP blocked on server)
        $id = (int)$_POST['shard_id'];
        $msg = 'Key send: email SMTP blocked on server. Send manually from junky4joy@gmail.com with key: KILLIAN';
    }
}

// Load shards
$shards = $pdo->query("SELECT * FROM shards ORDER BY shard_num")->fetchAll();

// Load recent bids
$bids = $pdo->query("SELECT sb.*, s.shard_num, s.title FROM shard_bids sb JOIN shards s ON sb.shard_id=s.id ORDER BY sb.created_at DESC LIMIT 50")->fetchAll();

// Load job submissions
$jobs = $pdo->query("SELECT * FROM revert_users ORDER BY created_at DESC LIMIT 50")->fetchAll();
?><!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SHARD ADMIN — SF</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#000;color:#e2e8f0;font-family:'Courier New',monospace;padding:24px;}
h1{font-size:18px;font-weight:900;color:#DA7756;letter-spacing:2px;margin-bottom:4px;}
.sub{font-size:8px;color:#222;letter-spacing:3px;margin-bottom:28px;}
.msg{background:#001a00;border:1px solid #004400;color:#2ecc71;padding:10px 14px;font-size:11px;margin-bottom:20px;}
h2{font-size:11px;letter-spacing:3px;color:#333;text-transform:uppercase;margin:32px 0 14px;padding-bottom:8px;border-bottom:1px solid #0a0a0a;}
table{width:100%;border-collapse:collapse;font-size:10px;margin-bottom:8px;}
th{text-align:left;font-size:7px;letter-spacing:2px;color:#222;padding:6px 8px;border-bottom:1px solid #0a0a0a;}
td{padding:8px;border-bottom:1px solid #050505;vertical-align:top;}
.state-available{color:#DA7756;}
.state-bidding{color:#F5C78A;}
.state-sold{color:#333;}
.bid-val{color:#daa520;font-weight:700;}
input[type=text],input[type=number],textarea{background:#050505;border:1px solid #111;color:#e2e8f0;font-family:'Courier New',monospace;font-size:11px;padding:6px 8px;width:100%;}
textarea{height:80px;resize:vertical;}
button{background:#DA7756;color:#000;border:none;font-family:'Courier New',monospace;font-size:9px;font-weight:900;letter-spacing:2px;padding:7px 12px;cursor:pointer;text-transform:uppercase;}
button:hover{background:#E8896A;}
button.danger{background:#c0392b;color:#fff;}
button.grey{background:#1a1a1a;color:#555;}
.inline-form{display:flex;gap:6px;align-items:flex-start;flex-wrap:wrap;margin-top:6px;}
.story-form{margin-top:8px;display:none;}
.story-toggle{font-size:8px;color:#444;cursor:pointer;text-decoration:underline;margin-top:4px;display:inline-block;}
a{color:#DA7756;text-decoration:none;}
a:hover{text-decoration:underline;}
.email-val{color:#888;}
.ref-val{color:#daa520;}
</style>
</head>
<body>
<h1>SHARD AUCTION ADMIN</h1>
<div class="sub">SF_SHARD_ADMIN · <?=date('Y-m-d H:i')?></div>

<?php if($msg): ?><div class="msg"><?=htmlspecialchars($msg)?></div><?php endif; ?>

<!-- SHARDS TABLE -->
<h2>SHARDS (<?=count($shards)?>)</h2>
<table>
<tr><th>NUM</th><th>TITLE</th><th>STATE</th><th>TOP BID</th><th>BIDS</th><th>TOP EMAIL</th><th>STORY</th><th>ACTIONS</th></tr>
<?php foreach($shards as $s): ?>
<tr>
  <td><?=$s['shard_num']?></td>
  <td style="color:#888"><?=htmlspecialchars($s['title'])?></td>
  <td class="state-<?=$s['state']?>"><?=strtoupper($s['state'])?></td>
  <td class="bid-val"><?=$s['top_bid']>0 ? '£'.number_format($s['top_bid'],0) : '—'?></td>
  <td><?=$s['bid_count']?></td>
  <td class="email-val"><?=$s['top_email'] ? htmlspecialchars($s['top_email']) : '—'?></td>
  <td><?=$s['story_enc'] ? '<span style="color:#2ecc71">✓ SET</span>' : '<span style="color:#222">EMPTY</span>'?></td>
  <td>
    <?php if($s['state']!=='sold'): ?>
    <form method="POST" style="display:inline">
      <input type="hidden" name="action" value="close">
      <input type="hidden" name="shard_id" value="<?=$s['id']?>">
      <button class="danger" onclick="return confirm('Close shard #<?=$s['shard_num']?> as SOLD to <?=htmlspecialchars($s['top_email'])?> for £<?=number_format($s['top_bid'],0)?>?')">CLOSE SOLD</button>
    </form>
    <?php else: ?>
    <form method="POST" style="display:inline">
      <input type="hidden" name="action" value="reopen">
      <input type="hidden" name="shard_id" value="<?=$s['id']?>">
      <button class="grey" onclick="return confirm('Reopen shard #<?=$s['shard_num']?> — this CLEARS all bids!')">REOPEN</button>
    </form>
    <?php if($s['top_email']): ?>
    <form method="POST" style="display:inline;margin-left:4px">
      <input type="hidden" name="action" value="send_key">
      <input type="hidden" name="shard_id" value="<?=$s['id']?>">
      <button>SEND KEY</button>
    </form>
    <?php endif; ?>
    <?php endif; ?>
    <br>
    <span class="story-toggle" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'block':'none'">
      <?=$s['story_enc']?'edit story':'+ add story'?>
    </span>
    <form method="POST" class="story-form">
      <input type="hidden" name="action" value="set_story">
      <input type="hidden" name="shard_id" value="<?=$s['id']?>">
      <textarea name="story_plain" placeholder="Paste plaintext story content here (will be encrypted with KILLIAN key)..."
      ><?php if($s['story_enc']) echo htmlspecialchars(satoshi_decrypt($s['story_enc'],'KILLIAN')); ?></textarea>
      <div class="inline-form" style="margin-top:4px">
        <input type="text" name="story_key" value="KILLIAN" style="width:100px">
        <button>ENCRYPT + SAVE</button>
      </div>
    </form>
  </td>
</tr>
<?php endforeach; ?>
</table>

<!-- RECENT BIDS -->
<h2>RECENT BIDS (last 50)</h2>
<table>
<tr><th>TIME</th><th>SHARD</th><th>EMAIL</th><th>AMOUNT</th><th>REF</th></tr>
<?php foreach($bids as $b): ?>
<tr>
  <td style="color:#333"><?=date('d/m H:i',strtotime($b['created_at']))?></td>
  <td><?=$b['shard_num']?> — <?=htmlspecialchars($b['title'])?></td>
  <td class="email-val"><?=htmlspecialchars($b['bidder_email'])?></td>
  <td class="bid-val">£<?=number_format($b['amount'],0)?></td>
  <td class="ref-val"><?=htmlspecialchars($b['bidder_ref']??'—')?></td>
</tr>
<?php endforeach; ?>
<?php if(!$bids): ?><tr><td colspan="5" style="color:#222">No bids yet.</td></tr><?php endif; ?>
</table>

<!-- JOB SUBMISSIONS -->
<h2>JOB SUBMISSIONS — KING'S PENNY (last 50)</h2>
<table>
<tr><th>TIME</th><th>EMAIL</th><th>REF</th><th>PAID</th><th>FILM</th><th>SHARD WON</th></tr>
<?php foreach($jobs as $j): ?>
<tr>
  <td style="color:#333"><?=date('d/m H:i',strtotime($j['created_at']))?></td>
  <td class="email-val"><?=htmlspecialchars($j['email'])?></td>
  <td class="ref-val"><?=htmlspecialchars($j['ref']??'—')?></td>
  <td><?=$j['paid']?'<span style="color:#2ecc71">✓</span>':'<span style="color:#c0392b">✗</span>'?></td>
  <td><?=$j['job_video']?'<a href="'.htmlspecialchars($j['job_video']).'" target="_blank">VIEW ↗</a>':'—'?></td>
  <td><?=$j['shard_won']??'—'?></td>
</tr>
<?php endforeach; ?>
<?php if(!$jobs): ?><tr><td colspan="6" style="color:#222">No submissions yet.</td></tr><?php endif; ?>
</table>
</body>
</html>
