<?php
/**
 * REVERT FIVER — Join API
 * POST {action:'create_intent', ref:'SFNODE-XXXX'}
 * Returns: {client_secret, node_id}
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

// ── CONFIG ──
// Stripe test key — swap for live sk_live_... when ready
// The live key is Satoshi-encrypted in config_imaginator.php (key: SPIRAL)
define('STRIPE_SECRET', 'sk_test_REPLACE_WITH_SECRET_KEY');
define('SITE_URL', 'https://stinkindigger.info');

// ── DB ──
$db_path = __DIR__ . '/../data/nodes.sqlite';
if (!is_dir(dirname($db_path))) mkdir(dirname($db_path), 0755, true);
$db = new SQLite3($db_path);
$db->exec("CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    num INTEGER,
    ref_by TEXT DEFAULT '',
    stripe_intent TEXT DEFAULT '',
    stripe_paid INTEGER DEFAULT 0,
    ipfs_hash TEXT DEFAULT '',
    created_at TEXT,
    paid_at TEXT DEFAULT '',
    email TEXT DEFAULT ''
)");
$db->exec("CREATE TABLE IF NOT EXISTS chain (
    node_id TEXT,
    recruit_id TEXT,
    joined_at TEXT
)");

$body = json_decode(file_get_contents('php://input'), true) ?? [];
$action = $body['action'] ?? $_GET['action'] ?? '';

// ── CREATE PAYMENT INTENT ──
if ($action === 'create_intent') {
    $ref = preg_replace('/[^A-Z0-9\-]/', '', strtoupper($body['ref'] ?? ''));

    // generate node ID
    $count = $db->querySingle("SELECT COUNT(*) FROM nodes") + 1;
    $node_id = 'SFNODE-' . str_pad($count, 4, '0', STR_PAD_LEFT);

    // insert pending node
    $stmt = $db->prepare("INSERT OR IGNORE INTO nodes (id, num, ref_by, created_at) VALUES (?, ?, ?, ?)");
    $stmt->bindValue(1, $node_id);
    $stmt->bindValue(2, $count);
    $stmt->bindValue(3, $ref);
    $stmt->bindValue(4, date('c'));
    $stmt->execute();

    // create Stripe PaymentIntent for £5 (500 pence)
    $pi = stripe_post('https://api.stripe.com/v1/payment_intents', [
        'amount'   => 500,
        'currency' => 'gbp',
        'metadata[node_id]' => $node_id,
        'metadata[ref_by]'  => $ref,
        'description' => 'Revert Fiver — Soul SFT Node ' . $node_id,
    ]);

    if (isset($pi['error'])) {
        echo json_encode(['error' => $pi['error']['message'] ?? 'Stripe error']);
        exit;
    }

    // store intent ID
    $db->exec("UPDATE nodes SET stripe_intent='{$pi['id']}' WHERE id='$node_id'");

    echo json_encode([
        'client_secret' => $pi['client_secret'],
        'node_id'       => $node_id,
    ]);
    exit;
}

echo json_encode(['error' => 'Unknown action']);

// ── STRIPE HELPER (no library needed) ──
function stripe_post($url, $params) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query($params),
        CURLOPT_USERPWD        => STRIPE_SECRET . ':',
        CURLOPT_HTTPHEADER     => ['Content-Type: application/x-www-form-urlencoded'],
    ]);
    $resp = curl_exec($ch);
    curl_close($ch);
    return json_decode($resp, true);
}
