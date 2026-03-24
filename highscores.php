<?php
/**
 * High Scores API - Trump Game Leaderboard
 * Handles saving and retrieving top scores
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');
header('Access-Control-Allow-Headers: Content-Type');

// Database connection
$db_file = '/var/www/vhosts/shortfactory.shop/httpdocs/trump/data/trump_scores.db';

// Create SQLite database if it doesn't exist
try {
    $db = new PDO('sqlite:' . $db_file);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Create table if not exists
    $db->exec("CREATE TABLE IF NOT EXISTS highscores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        purity INTEGER NOT NULL,
        timestamp INTEGER NOT NULL,
        ip_address TEXT
    )");

    // Create index for faster queries
    $db->exec("CREATE INDEX IF NOT EXISTS idx_purity ON highscores(purity DESC)");

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database error']);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    // Save new score
    $input = json_decode(file_get_contents('php://input'), true);

    if (!isset($input['name']) || !isset($input['purity'])) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing name or purity']);
        exit;
    }

    $name = substr(trim($input['name']), 0, 12); // Max 12 chars
    $purity = intval($input['purity']);
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

    if (empty($name)) {
        $name = 'ANON';
    }

    // Insert score
    try {
        $stmt = $db->prepare("INSERT INTO highscores (player_name, purity, timestamp, ip_address) VALUES (?, ?, ?, ?)");
        $stmt->execute([$name, $purity, time(), $ip]);

        echo json_encode([
            'success' => true,
            'id' => $db->lastInsertId(),
            'rank' => getRank($db, $purity)
        ]);
    } catch (PDOException $e) {
        http_response_code(500);
        echo json_encode(['error' => 'Failed to save score']);
    }

} elseif ($method === 'GET') {
    // Get top 10 scores
    try {
        $stmt = $db->query("SELECT player_name, purity, timestamp FROM highscores ORDER BY purity DESC, timestamp ASC LIMIT 10");
        $scores = $stmt->fetchAll(PDO::FETCH_ASSOC);

        echo json_encode([
            'success' => true,
            'scores' => $scores
        ]);
    } catch (PDOException $e) {
        http_response_code(500);
        echo json_encode(['error' => 'Failed to fetch scores']);
    }
}

function getRank($db, $purity) {
    $stmt = $db->prepare("SELECT COUNT(*) as rank FROM highscores WHERE purity > ?");
    $stmt->execute([$purity]);
    $result = $stmt->fetch(PDO::FETCH_ASSOC);
    return $result['rank'] + 1;
}
?>
