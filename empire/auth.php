<?php
// empire/auth.php — Google OAuth verify + empire user session
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://www.shortfactory.shop');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

session_start();

define('GOOGLE_CLIENT_ID', '246057462897-mui96hjeuk9abvlkgvvqdfdeiknbmojb.apps.googleusercontent.com');
define('DB_HOST', 'localhost');
define('DB_NAME', 'sf_marketplace');
define('DB_USER', 'sfadmin');
define('DB_PASS', 'SFmarket2026!');

function getDB() {
    static $pdo;
    if (!$pdo) {
        $pdo = new PDO('mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8mb4', DB_USER, DB_PASS, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
        // Create table if not exists
        $pdo->exec("CREATE TABLE IF NOT EXISTS empire_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            google_id VARCHAR(64) UNIQUE NOT NULL,
            email VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            avatar VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )");
        $pdo->exec("CREATE TABLE IF NOT EXISTS empire_fragments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            fragment_code VARCHAR(128) NOT NULL,
            room_key VARCHAR(64) NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            position INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES empire_users(id),
            UNIQUE KEY unique_user_room (user_id, room_key)
        )");
    }
    return $pdo;
}

function verifyGoogleToken($token) {
    $url = 'https://oauth2.googleapis.com/tokeninfo?id_token=' . urlencode($token);
    $ctx = stream_context_create(['http' => ['timeout' => 10]]);
    $res = file_get_contents($url, false, $ctx);
    if (!$res) return null;
    $data = json_decode($res, true);
    if (!isset($data['sub'])) return null;
    if ($data['aud'] !== GOOGLE_CLIENT_ID) return null;
    return $data;
}

$input = json_decode(file_get_contents('php://input'), true);

if (isset($_GET['logout'])) {
    session_destroy();
    echo json_encode(['ok' => true]);
    exit;
}

if (isset($_GET['me'])) {
    if (isset($_SESSION['empire_user'])) {
        $db = getDB();
        $uid = $_SESSION['empire_user']['id'];
        $frags = $db->prepare("SELECT room_key, fragment_code, position, earned_at FROM empire_fragments WHERE user_id=? ORDER BY position ASC");
        $frags->execute([$uid]);
        $fragments = $frags->fetchAll();
        echo json_encode([
            'user' => $_SESSION['empire_user'],
            'fragments' => $fragments,
            'percent' => count($fragments)
        ]);
    } else {
        echo json_encode(['user' => null, 'fragments' => [], 'percent' => 0]);
    }
    exit;
}

// Login via Google token
if (!isset($input['token'])) {
    http_response_code(400);
    echo json_encode(['error' => 'No token']);
    exit;
}

$google = verifyGoogleToken($input['token']);
if (!$google) {
    http_response_code(401);
    echo json_encode(['error' => 'Invalid token']);
    exit;
}

try {
    $db = getDB();
    // Upsert user
    $stmt = $db->prepare("INSERT INTO empire_users (google_id, email, name, avatar) VALUES (?,?,?,?)
        ON DUPLICATE KEY UPDATE email=VALUES(email), name=VALUES(name), avatar=VALUES(avatar)");
    $stmt->execute([$google['sub'], $google['email'], $google['name'] ?? '', $google['picture'] ?? '']);

    $user = $db->prepare("SELECT * FROM empire_users WHERE google_id=?");
    $user->execute([$google['sub']]);
    $row = $user->fetch();

    $_SESSION['empire_user'] = [
        'id' => $row['id'],
        'email' => $row['email'],
        'name' => $row['name'],
        'avatar' => $row['avatar']
    ];

    // Get fragments
    $frags = $db->prepare("SELECT room_key, fragment_code, position, earned_at FROM empire_fragments WHERE user_id=? ORDER BY position ASC");
    $frags->execute([$row['id']]);
    $fragments = $frags->fetchAll();

    echo json_encode([
        'ok' => true,
        'user' => $_SESSION['empire_user'],
        'fragments' => $fragments,
        'percent' => count($fragments)
    ]);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
