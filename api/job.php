<?php
// api/job.php — King's Penny job submission
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://www.shortfactory.shop');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

define('DB_HOST', 'localhost');
define('DB_NAME', 'sf_marketplace');
define('DB_USER', 'sfadmin');
define('DB_PASS', 'SFmarket2026!');

function getDB() {
    static $pdo;
    if (!$pdo) {
        $pdo = new PDO('mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8mb4', DB_USER, DB_PASS, [
            PDO::ATTR_ERRMODE           => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
        // Create table if not exists (self-healing)
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

function ok($data)       { echo json_encode(['ok'=>true]+$data); exit; }
function fail($msg,$c=400){ http_response_code($c); echo json_encode(['ok'=>false,'error'=>$msg]); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') fail('POST only.', 405);

$body  = json_decode(file_get_contents('php://input'), true);
$email = trim(strtolower($body['email'] ?? ''));
$video = trim($body['video'] ?? '');
$ref   = trim($body['ref']   ?? '');

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) fail('Valid email required.');
if (!$video || !filter_var($video, FILTER_VALIDATE_URL)) fail('Valid video URL required.');

// Basic URL safety — must be YouTube or Vimeo
if (!preg_match('#^https://(www\.)?(youtube\.com|youtu\.be|vimeo\.com)/#i', $video)) {
    fail('Video must be a YouTube or Vimeo link.');
}

$db = getDB();

// Upsert user record — create if not exist, update job fields
$existing = $db->prepare("SELECT id, ref FROM revert_users WHERE email=? LIMIT 1");
$existing->execute([$email]);
$user = $existing->fetch();

if ($user) {
    $db->prepare("UPDATE revert_users SET job_video=?, job_submitted=1, updated_at=NOW() WHERE id=?")
       ->execute([$video, $user['id']]);
    $outRef = $user['ref'] ?: $ref;
} else {
    // New user — generate ref if none provided
    $newRef = $ref ?: strtoupper(substr(md5($email.time()), 0, 8));
    $db->prepare("INSERT INTO revert_users (email, ref, job_video, job_submitted) VALUES (?,?,?,1)")
       ->execute([$email, $newRef, $video]);
    $outRef = $newRef;
}

ok(['message'=>'Job submitted.', 'ref'=>$outRef]);
