<?php
// empire/progress.php — award fragments + retrieve progress
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://www.shortfactory.shop');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

session_start();

// Room definitions — each room key maps to a human name and fragment seed
define('ROOMS', [
    'game'        => ['name' => 'The Chocolate River',       'product' => 'Trump v Deep State',     'pct' => 16],
    'alive'       => ['name' => 'The Inventing Room',        'product' => 'ALIVE Creature',         'pct' => 16],
    'soulforge'   => ['name' => 'The Nut Room',              'product' => 'Soul Forge / D4D',       'pct' => 17],
    'cortex'      => ['name' => 'The Television Room',       'product' => 'Cortex Brain',           'pct' => 17],
    'fuel'        => ['name' => 'The Fizzy Lifting Drinks',  'product' => 'Fuel / Battery Economy', 'pct' => 17],
    'screensaver' => ['name' => 'The Great Glass Elevator',  'product' => 'Screensaver / IPFS',     'pct' => 17],
]);

// Satoshi cipher (Vigenere ASCII 32-126)
function satoshiEncode($text, $key) {
    $range = 95; // 126 - 32 + 1
    $out = '';
    $klen = strlen($key);
    for ($i = 0; $i < strlen($text); $i++) {
        $c = ord($text[$i]);
        $k = ord($key[$i % $klen]);
        $out .= chr((($c - 32 + $k - 32) % $range) + 32);
    }
    return base64_encode($out);
}

function getDB() {
    static $pdo;
    if (!$pdo) {
        $pdo = new PDO('mysql:host=localhost;dbname=sf_marketplace;charset=utf8mb4', 'sfadmin', 'SFmarket2026!', [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
    }
    return $pdo;
}

if (!isset($_SESSION['empire_user'])) {
    http_response_code(401);
    echo json_encode(['error' => 'Not logged in']);
    exit;
}

$uid = $_SESSION['empire_user']['id'];
$db = getDB();

// GET — return current progress
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $frags = $db->prepare("SELECT room_key, fragment_code, position, earned_at FROM empire_fragments WHERE user_id=? ORDER BY position ASC");
    $frags->execute([$uid]);
    $fragments = $frags->fetchAll();
    echo json_encode([
        'fragments' => $fragments,
        'percent' => count($fragments),
        'rooms' => ROOMS
    ]);
    exit;
}

// POST — award a fragment
$input = json_decode(file_get_contents('php://input'), true);
$room = $input['room'] ?? '';
$proof = $input['proof'] ?? ''; // room-specific proof of completion

if (!isset(ROOMS[$room])) {
    http_response_code(400);
    echo json_encode(['error' => 'Unknown room']);
    exit;
}

// Check not already earned
$check = $db->prepare("SELECT id FROM empire_fragments WHERE user_id=? AND room_key=?");
$check->execute([$uid, $room]);
if ($check->fetch()) {
    // Already earned — return current state
    $frags = $db->prepare("SELECT room_key, fragment_code, position, earned_at FROM empire_fragments WHERE user_id=? ORDER BY position ASC");
    $frags->execute([$uid]);
    $fragments = $frags->fetchAll();
    echo json_encode(['already_earned' => true, 'fragments' => $fragments, 'percent' => count($fragments)]);
    exit;
}

// Get current position
$pos = $db->prepare("SELECT COUNT(*) as c FROM empire_fragments WHERE user_id=?");
$pos->execute([$uid]);
$position = (int)$pos->fetch()['c'] + 1;

// Generate unique satoshi cipher fragment
// Seed = user email + room + position + timestamp + secret
$secret = 'wonka_factory_' . $uid . '_' . $room . '_' . $position;
$key = substr(md5($_SESSION['empire_user']['email'] . $room . $position), 0, 16);
$fragment = satoshiEncode($secret, $key);

// Store
$db->prepare("INSERT INTO empire_fragments (user_id, fragment_code, room_key, position) VALUES (?,?,?,?)")
   ->execute([$uid, $fragment, $room, $position]);

// Return updated state
$frags = $db->prepare("SELECT room_key, fragment_code, position, earned_at FROM empire_fragments WHERE user_id=? ORDER BY position ASC");
$frags->execute([$uid]);
$fragments = $frags->fetchAll();

$roomName = ROOMS[$room]['name'];
$pct = count($fragments);

echo json_encode([
    'ok' => true,
    'fragment' => $fragment,
    'position' => $position,
    'room_name' => $roomName,
    'fragments' => $fragments,
    'percent' => $pct,
    'message' => "Fragment #$position earned: $roomName"
]);
