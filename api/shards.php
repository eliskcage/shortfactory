<?php
// api/shards.php — Shard Auction API
// Actions: GET ?action=status | POST action=bid | POST action=close (admin)

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://www.shortfactory.shop');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

define('DB_HOST', 'localhost');
define('DB_NAME', 'sf_marketplace');
define('DB_USER', 'sfadmin');
define('DB_PASS', 'SFmarket2026!');

// Auction config
define('MIN_FIRST_BID',  50.00);   // £50 minimum opening bid
define('MIN_INCREMENT',  10.00);   // £10 minimum raise
define('ANTISHILL_SECS', 60);      // same IP can't bid twice on same shard within 60s
define('ADMIN_KEY',      'SF_SHARD_ADMIN_2026'); // change before prod

function getDB() {
    static $pdo;
    if (!$pdo) {
        $pdo = new PDO('mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8mb4', DB_USER, DB_PASS, [
            PDO::ATTR_ERRMODE           => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
    }
    return $pdo;
}

// ── Satoshi cipher (Vigenere ASCII 32–126) ──────────────────────────────────
// Decrypt only — plaintext never leaves server
function satoshi_decrypt($ciphertext, $passphrase) {
    $p = strtoupper($passphrase);
    $out = '';
    $pl = strlen($p);
    for ($i = 0, $n = strlen($ciphertext); $i < $n; $i++) {
        $c = ord($ciphertext[$i]);
        $k = ord($p[$i % $pl]);
        $out .= chr((($c - 32) - ($k - 32) + 95) % 95 + 32);
    }
    return $out;
}

function satoshi_encrypt($plaintext, $passphrase) {
    $p = strtoupper($passphrase);
    $out = '';
    $pl = strlen($p);
    for ($i = 0, $n = strlen($plaintext); $i < $n; $i++) {
        $c = ord($plaintext[$i]);
        $k = ord($p[$i % $pl]);
        $out .= chr((($c - 32) + ($k - 32)) % 95 + 32);
    }
    return $out;
}

function ipHash() {
    $ip = $_SERVER['HTTP_CF_CONNECTING_IP']
       ?? $_SERVER['HTTP_X_FORWARDED_FOR']
       ?? $_SERVER['REMOTE_ADDR']
       ?? 'unknown';
    return hash('sha256', $ip . 'SF_SHARD_SALT_2026');
}

function ok($data) { echo json_encode(['ok' => true] + $data); exit; }
function fail($msg, $code = 400) { http_response_code($code); echo json_encode(['ok' => false, 'error' => $msg]); exit; }

// ── ROUTER ──────────────────────────────────────────────────────────────────
$method = $_SERVER['REQUEST_METHOD'];
$action = $_GET['action'] ?? (json_decode(file_get_contents('php://input'), true)['action'] ?? 'status');

if ($method === 'GET' && $action === 'status') {
    // Return all 10 shards (no sensitive data)
    $db = getDB();
    $rows = $db->query("SELECT shard_num, title, teaser, state, top_bid, bid_count FROM shards ORDER BY shard_num")->fetchAll();
    ok(['shards' => $rows]);
}

if ($method === 'POST' && $action === 'bid') {
    $body  = json_decode(file_get_contents('php://input'), true);
    $shard = (int)($body['shard'] ?? 0);
    $email = trim(strtolower($body['email'] ?? ''));
    $amount= (float)($body['amount'] ?? 0);
    $ref   = trim($body['ref'] ?? '');

    // Basic validation
    if ($shard < 1 || $shard > 10)     fail('Invalid shard number.');
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) fail('Valid email required.');
    if ($amount < MIN_FIRST_BID)        fail('Minimum bid is £'.number_format(MIN_FIRST_BID,0).'.');

    $db = getDB();
    $row = $db->prepare("SELECT * FROM shards WHERE shard_num = ? FOR UPDATE");
    $db->beginTransaction();
    try {
        $row->execute([$shard]);
        $s = $row->fetch();
        if (!$s) { $db->rollBack(); fail('Shard not found.'); }
        if ($s['state'] === 'sold') { $db->rollBack(); fail('This shard has already been sold.'); }

        // Must beat current top bid by min increment
        $required = $s['top_bid'] > 0 ? $s['top_bid'] + MIN_INCREMENT : MIN_FIRST_BID;
        if ($amount < $required) {
            $db->rollBack();
            fail('Minimum bid is £'.number_format($required, 2).($s['top_bid'] > 0 ? ' (current top + £'.number_format(MIN_INCREMENT,0).')' : '.'));
        }

        // Can't outbid yourself
        if ($s['top_email'] && strtolower($s['top_email']) === $email) {
            $db->rollBack();
            fail('You already hold the top bid on this shard.');
        }

        // Anti-shill: same IP hash can't bid on same shard within ANTISHILL_SECS
        $ip_hash = ipHash();
        $chk = $db->prepare("SELECT COUNT(*) FROM shard_bids WHERE shard_id = ? AND ip_hash = ? AND created_at > DATE_SUB(NOW(), INTERVAL ".ANTISHILL_SECS." SECOND)");
        $chk->execute([$s['id'], $ip_hash]);
        if ($chk->fetchColumn() > 0) {
            $db->rollBack();
            fail('Please wait '.ANTISHILL_SECS.' seconds between bids.');
        }

        // Record bid
        $ins = $db->prepare("INSERT INTO shard_bids (shard_id, bidder_email, bidder_ref, amount, ip_hash) VALUES (?,?,?,?,?)");
        $ins->execute([$s['id'], $email, $ref ?: null, $amount, $ip_hash]);

        // Update shard
        $upd = $db->prepare("UPDATE shards SET state='bidding', top_bid=?, top_email=?, top_ref=?, bid_count=bid_count+1 WHERE id=?");
        $upd->execute([$amount, $email, $ref ?: null, $s['id']]);

        $db->commit();
        ok(['message' => 'Bid registered. You hold the top bid on Shard #'.$shard.'.', 'top_bid' => $amount]);

    } catch (Exception $e) {
        $db->rollBack();
        fail('Server error. Try again.');
    }
}

// Admin: manually close a shard (mark as sold)
if ($method === 'POST' && $action === 'close') {
    $body = json_decode(file_get_contents('php://input'), true);
    if (($body['key'] ?? '') !== ADMIN_KEY) fail('Unauthorized.', 403);
    $shard  = (int)($body['shard'] ?? 0);
    $stripe = trim($body['stripe_ref'] ?? '');
    if ($shard < 1 || $shard > 10) fail('Invalid shard.');
    $db = getDB();
    $db->prepare("UPDATE shards SET state='sold', stripe_ref=?, sold_price=top_bid WHERE shard_num=?")->execute([$stripe ?: null, $shard]);
    ok(['message' => 'Shard #'.$shard.' marked as sold.']);
}

fail('Unknown action.', 404);
