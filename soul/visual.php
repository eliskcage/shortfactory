<?php
// Visual pairing session code manager
// POST: register a new visual code from ALIVE desktop
// GET:  return current active codes (for validation)
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

$data_dir = __DIR__ . '/data/';
if (!is_dir($data_dir)) mkdir($data_dir, 0750, true);

$codes_file = $data_dir . 'visual_codes.jsonl';
$ttl        = 120; // visual codes expire after 2 minutes

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $body = json_decode(file_get_contents('php://input'), true) ?? [];
    $code = preg_replace('/[^a-fA-F0-9]/', '', strtolower(substr($body['code'] ?? '', 0, 3)));
    if (!$code) { echo json_encode(['ok'=>false]); exit; }
    $entry = json_encode(['code'=>$code, 'at'=>time()]) . "\n";
    file_put_contents($codes_file, $entry, FILE_APPEND | LOCK_EX);
    echo json_encode(['ok'=>true, 'code'=>$code]);
    exit;
}

// GET — return active codes for validation (not exposed to UI, used by pair confirmation)
$since = time() - $ttl;
$active = [];
if (file_exists($codes_file)) {
    $lines = array_slice(file($codes_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES), -50);
    foreach (array_reverse($lines) as $line) {
        $e = json_decode($line, true);
        if (!$e || $e['at'] < $since) continue;
        $active[$e['code']] = $e['at'];
        if (count($active) >= 10) break;
    }
}
echo json_encode(['codes' => array_keys($active), 'ts' => time()]);
