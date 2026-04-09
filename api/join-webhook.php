<?php
// api/join-webhook.php — Stripe webhook on £5 Revert Fiver payment
// Register in Stripe Dashboard → Webhooks → checkout.session.completed
// Set STRIPE_WEBHOOK_SECRET as the signing secret

header('Content-Type: application/json');

define('DB_HOST', 'localhost');
define('DB_NAME', 'sf_marketplace');
define('DB_USER', 'sfadmin');
define('DB_PASS', 'SFmarket2026!');

// !! SET THIS — copy from Stripe Dashboard → Webhooks → your endpoint → Signing secret
define('STRIPE_WEBHOOK_SECRET', 'whsec_pH3W2qQU6QsQ6nYk1GDeUVfaZeQkrTGE');

function getDB() {
    static $pdo;
    if (!$pdo) {
        $pdo = new PDO('mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8mb4', DB_USER, DB_PASS, [
            PDO::ATTR_ERRMODE           => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
        $pdo->exec("CREATE TABLE IF NOT EXISTS revert_users (
            id            INT PRIMARY KEY AUTO_INCREMENT,
            email         VARCHAR(255) NOT NULL,
            ref           VARCHAR(100) DEFAULT NULL UNIQUE,
            stripe_ref    VARCHAR(255) DEFAULT NULL,
            paid          TINYINT(1) NOT NULL DEFAULT 0,
            job_video     TEXT DEFAULT NULL,
            job_submitted TINYINT(1) NOT NULL DEFAULT 0,
            shard_won     INT DEFAULT NULL,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_email (email),
            INDEX idx_ref   (ref)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    }
    return $pdo;
}

// Read raw body FIRST — must happen before anything that touches $_POST
$payload   = file_get_contents('php://input');
$sigHeader = $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '';

// Empty body = likely a browser hit or Stripe connectivity test — just acknowledge
if (!$payload) {
    http_response_code(200);
    echo json_encode(['received'=>true]);
    exit;
}

// Verify Stripe signature (skip if secret not yet configured)
function verifyStripeSignature($payload, $sigHeader, $secret) {
    if (!$sigHeader) return false;
    $parts = [];
    foreach (explode(',', $sigHeader) as $chunk) {
        $pair = explode('=', $chunk, 2);
        if (count($pair) === 2) $parts[$pair[0]][] = $pair[1];
    }
    $ts       = $parts['t'][0] ?? 0;
    $expected = hash_hmac('sha256', $ts.'.'.$payload, $secret);
    foreach ($parts['v1'] ?? [] as $sig) {
        if (hash_equals($expected, $sig)) return true;
    }
    return false;
}

if (STRIPE_WEBHOOK_SECRET !== 'whsec_REPLACE_ME') {
    if (!verifyStripeSignature($payload, $sigHeader, STRIPE_WEBHOOK_SECRET)) {
        http_response_code(400);
        echo json_encode(['error'=>'Invalid signature']);
        exit;
    }
}

$event = json_decode($payload, true);
if (!$event || !isset($event['type'])) {
    // Unrecognised payload — still return 200 so Stripe doesn't retry
    http_response_code(200);
    echo json_encode(['received'=>true, 'note'=>'unrecognised payload']);
    exit;
}

$type = $event['type'] ?? '';

// We care about completed checkout sessions
if ($type === 'checkout.session.completed') {
    $session   = $event['data']['object'];
    $email     = strtolower(trim($session['customer_email'] ?? $session['customer_details']['email'] ?? ''));
    $ref       = $session['client_reference_id'] ?? null;  // the ?ref= we pass in join.html
    $stripeRef = $session['id'] ?? null;

    if ($email) {
        $db = getDB();
        // Upsert: mark as paid, store stripe session
        $existing = $db->prepare("SELECT id FROM revert_users WHERE email=? LIMIT 1");
        $existing->execute([$email]);
        $user = $existing->fetch();

        if ($user) {
            $db->prepare("UPDATE revert_users SET paid=1, stripe_ref=? WHERE id=?")
               ->execute([$stripeRef, $user['id']]);
        } else {
            $newRef = $ref ?: strtoupper(substr(md5($email.time()), 0, 8));
            $db->prepare("INSERT INTO revert_users (email, ref, stripe_ref, paid) VALUES (?,?,?,1)")
               ->execute([$email, $newRef, $stripeRef]);
        }
    }
}

http_response_code(200);
echo json_encode(['received'=>true]);
