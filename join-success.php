<?php
// join-success.php — node claimed, shape generated

define('DB_HOST', 'localhost');
define('DB_NAME', 'sf_marketplace');
define('DB_USER', 'sfadmin');
define('DB_PASS', 'SFmarket2026!');
define('SATOSHI_KEY', 'supercalifragilisticexpialidocious');

function getDB() {
    static $pdo;
    if (!$pdo) {
        $pdo = new PDO('mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8mb4', DB_USER, DB_PASS, [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]);
        $pdo->exec("CREATE TABLE IF NOT EXISTS revert_users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            email VARCHAR(255) DEFAULT NULL,
            ref VARCHAR(100) DEFAULT NULL,
            stripe_ref VARCHAR(255) DEFAULT NULL,
            paid TINYINT(1) NOT NULL DEFAULT 1,
            shape_token VARCHAR(64) DEFAULT NULL,
            job_video TEXT DEFAULT NULL,
            job_submitted TINYINT(1) NOT NULL DEFAULT 0,
            shard_won INT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_ref (ref)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    }
    return $pdo;
}

function vigenereEncrypt(string $text, string $key): string {
    $range = 95; $base = 32; $kLen = strlen($key); $out = '';
    for ($i = 0, $n = strlen($text); $i < $n; $i++) {
        $c = ord($text[$i]); $k = ord($key[$i % $kLen]);
        $out .= chr((($c - $base) + ($k - $base)) % $range + $base);
    }
    return $out;
}

function buildShapeToken(string $ref, int $amount, string $currency, string $date): array {
    $payload = "$ref|$amount|$currency|$date";
    $cipher  = vigenereEncrypt($payload, SATOSHI_KEY);
    $token   = rtrim(base64_encode(substr($cipher, 0, 20)), '=');
    return ['token' => $token, 'payload' => $payload];
}

// ── Inputs ─────────────────────────────────────────────────────────────────
$sessionId = preg_replace('/[^A-Za-z0-9_\-]/', '', $_GET['session_id'] ?? '');
$ref       = preg_replace('/[^A-Za-z0-9_\-]/', '', $_GET['ref']        ?? '');
$amount    = 500;
$currency  = 'gbp';
$date      = date('Ymd');

$nodeRef = $ref ?: strtoupper(substr(md5($sessionId . microtime()), 0, 8));

// ── Build shape token ──────────────────────────────────────────────────────
['token' => $shapeToken] = buildShapeToken($nodeRef, $amount, $currency, $date);

// ── Write node to DB ───────────────────────────────────────────────────────
try {
    $db = getDB();
    $db->prepare("INSERT IGNORE INTO revert_users (ref, stripe_ref, paid, shape_token) VALUES (?,?,1,?)")
       ->execute([$nodeRef, $sessionId, $shapeToken]);
} catch (Exception $e) { /* silent */ }

// Shape URL
$shapeUrl = '/api/satoshi-shape.php?ref=' . urlencode($nodeRef)
          . '&amount=' . $amount . '&currency=' . $currency . '&date=' . $date;
// Referral link
$referralUrl = 'https://shortfactory.shop/fiver.html?ref=' . urlencode($nodeRef);
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>NODE CLAIMED — SHORTFACTORY</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:100%;min-height:100%;background:#000;color:#e2e8f0;font-family:'Courier New',monospace;display:flex;align-items:center;justify-content:center;padding:40px 20px;}
.wrap{max-width:440px;width:100%;text-align:center;}
.eyebrow{font-size:8px;letter-spacing:4px;color:#444;text-transform:uppercase;margin-bottom:20px;}
.title{font-size:clamp(32px,9vw,48px);font-weight:900;line-height:.9;letter-spacing:-2px;color:#fff;margin-bottom:28px;}
.title em{color:#DA7756;font-style:normal;}

/* Shape */
.shape-wrap{
  display:inline-block;
  border:1px solid #DA775630;
  padding:4px;
  margin-bottom:8px;
  position:relative;
}
.shape-wrap img{display:block;width:200px;height:200px;}
.shape-label{font-size:7px;letter-spacing:3px;color:#DA775680;margin-bottom:24px;}

/* Node ID */
.node-id{
  font-size:10px;letter-spacing:3px;color:#DA7756;
  border:1px solid #DA775640;padding:8px 16px;
  display:inline-block;margin-bottom:28px;
}

.body{font-size:13px;color:#888;line-height:2;margin-bottom:32px;}
.body strong{color:#e2e8f0;}

/* Referral */
.ref-box{
  background:#0a0a0a;border:1px solid #1a1a1a;
  padding:14px 16px;margin-bottom:28px;text-align:left;
}
.ref-label{font-size:8px;letter-spacing:2px;color:#555;margin-bottom:8px;}
.ref-url{font-size:10px;color:#DA7756;word-break:break-all;cursor:pointer;}
.ref-copy{font-size:8px;letter-spacing:1px;color:#333;margin-top:6px;cursor:pointer;transition:color .2s;}
.ref-copy:hover{color:#888;}
.ref-copy.copied{color:#22c55e;}

.btn{
  display:block;background:#DA7756;color:#000;
  font-family:'Courier New',monospace;font-size:11px;font-weight:700;
  letter-spacing:2px;padding:14px 28px;text-decoration:none;margin-bottom:10px;
}
.btn-ghost{
  display:block;color:#333;font-family:'Courier New',monospace;
  font-size:10px;letter-spacing:2px;text-decoration:none;
  border:1px solid #111;padding:12px 24px;transition:all .2s;
}
.btn-ghost:hover{color:#888;border-color:#333;}
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">Revert Fiver</div>
  <div class="title">NODE<br><em>CLAIMED.</em></div>

  <div class="shape-wrap">
    <img src="<?= htmlspecialchars($shapeUrl) ?>" alt="Your Satoshi Shape" width="200" height="200">
  </div>
  <div class="shape-label">YOUR SATOSHI SHAPE — SAVE THIS</div>

  <div class="node-id"><?= htmlspecialchars($nodeRef) ?></div>

  <div class="body">
    <p>This shape is your key.<br><strong>Screenshot it. It won't appear again.</strong></p>
    <p>It encodes your node, your payment, and your place in the chain.<br>No one else has this shape.</p>
  </div>

  <div class="ref-box">
    <div class="ref-label">YOUR CHAIN LINK — SHARE THIS</div>
    <div class="ref-url" id="ref-url"><?= htmlspecialchars($referralUrl) ?></div>
    <div class="ref-copy" id="ref-copy" onclick="copyRef()">[ TAP TO COPY ]</div>
  </div>

  <a href="/shards.html" class="btn">BID ON A SHARD →</a>
  <a href="/fiver.html" class="btn-ghost">BACK TO THE FIVER</a>
</div>

<script>
function copyRef() {
  const url = document.getElementById('ref-url').textContent.trim();
  navigator.clipboard.writeText(url).then(() => {
    const el = document.getElementById('ref-copy');
    el.textContent = '[ COPIED ✓ ]';
    el.classList.add('copied');
    setTimeout(() => { el.textContent = '[ TAP TO COPY ]'; el.classList.remove('copied'); }, 2000);
  });
}
</script>
</body>
</html>
