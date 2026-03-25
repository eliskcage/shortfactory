<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

$dataFile = __DIR__ . '/soul-suggestions-data.json';

function loadData($f) {
    if (!file_exists($f)) return ['suggestions'=>[]];
    $d = json_decode(file_get_contents($f), true);
    return $d ?: ['suggestions'=>[]];
}
function saveData($f, $d) {
    file_put_contents($f, json_encode($d), LOCK_EX);
}

// ── GET — return all suggestions sorted by count ──────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $data = loadData($dataFile);
    usort($data['suggestions'], fn($a,$b) => $b['count'] <=> $a['count']);
    echo json_encode($data);
    exit;
}

// ── POST ──────────────────────────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $body   = json_decode(file_get_contents('php://input'), true) ?: [];
    $action = $body['action'] ?? '';

    if ($action === 'suggest') {
        $name = substr(strip_tags(trim($body['name'] ?? '')), 0, 50);
        $desc = substr(strip_tags(trim($body['desc'] ?? '')), 0, 400);
        if (strlen($name) < 2) { echo json_encode(['error'=>'Dimension name too short']); exit; }

        $data = loadData($dataFile);

        // merge if same name (case-insensitive)
        foreach ($data['suggestions'] as &$s) {
            if (strtolower($s['name']) === strtolower($name)) {
                $s['count']++;
                saveData($dataFile, $data);
                echo json_encode(['ok'=>true, 'merged'=>true, 'id'=>$s['id'], 'count'=>$s['count']]);
                exit;
            }
        }
        unset($s);

        // new dimension
        $entry = [
            'id'    => bin2hex(random_bytes(6)),
            'name'  => $name,
            'desc'  => $desc,
            'count' => 1,
            'ts'    => time()
        ];
        $data['suggestions'][] = $entry;
        saveData($dataFile, $data);
        echo json_encode(['ok'=>true, 'merged'=>false, 'id'=>$entry['id'], 'count'=>1]);
        exit;
    }

    if ($action === 'upvote') {
        $id = $body['id'] ?? '';
        $data = loadData($dataFile);
        foreach ($data['suggestions'] as &$s) {
            if ($s['id'] === $id) {
                $s['count']++;
                saveData($dataFile, $data);
                echo json_encode(['ok'=>true, 'count'=>$s['count']]);
                exit;
            }
        }
        echo json_encode(['error'=>'Not found']);
        exit;
    }

    echo json_encode(['error'=>'Unknown action']);
    exit;
}

http_response_code(405);
echo json_encode(['error'=>'Method not allowed']);
