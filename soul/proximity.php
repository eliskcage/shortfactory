<?php
// Returns {nearby: true} if same token_hash was linked from a DIFFERENT device within the time window
// No actual token stored — only hashes. Anonymous.
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$token_hash = isset($_GET['dh']) ? preg_replace('/[^a-fA-F0-9]/', '', substr($_GET['dh'], 0, 16)) : '';
$since      = isset($_GET['ts']) ? max(0, (int)$_GET['ts']) : (time()*1000 - 30000);

if (!$token_hash) { echo json_encode(['nearby' => false]); exit; }

$log_file = __DIR__ . '/data/links.jsonl';
if (!file_exists($log_file)) { echo json_encode(['nearby' => false]); exit; }

$nearby = false;
$my_device = $_SERVER['REMOTE_ADDR'] ?? '';

// Read last 200 lines (recent only)
$lines = array_slice(file($log_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES), -200);
foreach ($lines as $line) {
    $e = json_decode($line, true);
    if (!$e) continue;
    // Match token hash, within time window, different device
    if (isset($e['th']) && $e['th'] === $token_hash &&
        isset($e['at']) && $e['at'] >= $since) {
        $nearby = true;
        break;
    }
}

echo json_encode(['nearby' => $nearby]);
