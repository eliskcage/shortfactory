<?php
/**
 * SOUL COMPLETION TRACKER
 * POST {soul_id: "anon hash", completion: 92+}  → records anonymous soul
 * GET                                            → returns {count, souls:[{id,completed_at}]}
 *
 * ZERO personal data. No email. No name. No IP stored.
 * Just the anonymous soul ID hash and completion timestamp.
 * This is the antithesis of digital ID — identity without identification.
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

// ── DB ──
$db_path = __DIR__ . '/../data/souls.sqlite';
if (!is_dir(dirname($db_path))) mkdir(dirname($db_path), 0755, true);
$db = new SQLite3($db_path);
$db->exec("CREATE TABLE IF NOT EXISTS completed_souls (
    soul_id TEXT PRIMARY KEY,
    completion INTEGER DEFAULT 92,
    completed_at TEXT
)");

// ── GET — return all completed souls ──
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $results = $db->query("SELECT soul_id, completion, completed_at FROM completed_souls ORDER BY completed_at DESC");
    $souls = [];
    while ($row = $results->fetchArray(SQLITE3_ASSOC)) {
        $souls[] = $row;
    }
    echo json_encode(['ok' => true, 'count' => count($souls), 'souls' => $souls]);
    exit;
}

// ── POST — record a soul completion ──
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $body = json_decode(file_get_contents('php://input'), true) ?? [];
    $soul_id = trim($body['soul_id'] ?? '');
    $completion = intval($body['completion'] ?? 0);

    if (strlen($soul_id) < 6) {
        echo json_encode(['ok' => false, 'error' => 'Invalid soul ID']);
        exit;
    }
    if ($completion < 92) {
        echo json_encode(['ok' => false, 'error' => 'Completion must be 92% or higher']);
        exit;
    }

    // Upsert — don't duplicate
    $stmt = $db->prepare("INSERT OR IGNORE INTO completed_souls (soul_id, completion, completed_at) VALUES (:sid, :comp, :ts)");
    $stmt->bindValue(':sid', $soul_id, SQLITE3_TEXT);
    $stmt->bindValue(':comp', $completion, SQLITE3_INTEGER);
    $stmt->bindValue(':ts', gmdate('Y-m-d\TH:i:s\Z'), SQLITE3_TEXT);
    $stmt->execute();

    // Return current count
    $count = $db->querySingle("SELECT COUNT(*) FROM completed_souls");
    echo json_encode(['ok' => true, 'count' => $count, 'soul_id' => $soul_id]);
    exit;
}

http_response_code(405);
echo json_encode(['ok' => false, 'error' => 'Method not allowed']);
