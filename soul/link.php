<?php
// Anonymous soul link tracker
// Stores: device_id (opaque hash), token_hash (not the token itself), timestamp
// NO PII. NO actual soul token stored server-side. Just presence + timing.

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }

$body = json_decode(file_get_contents('php://input'), true);
$device_id  = isset($body['device_id'])   ? preg_replace('/[^A-Za-z0-9\-]/', '', substr($body['device_id'], 0, 64))  : '';
$token_hash = isset($body['token_hash'])  ? preg_replace('/[^a-f0-9]/', '', substr($body['token_hash'], 0, 32))        : '';
$linked_at  = isset($body['linked_at'])   ? (int)$body['linked_at']                                                    : time() * 1000;

if (!$device_id || !$token_hash) {
    echo json_encode(['ok' => false]);
    exit;
}

// Append to log (flat file, anonymous)
$log_dir  = __DIR__ . '/data/';
$log_file = $log_dir . 'links.jsonl';

if (!is_dir($log_dir)) mkdir($log_dir, 0750, true);

$entry = json_encode([
    'd' => $device_id,
    'th' => $token_hash,
    'at' => $linked_at
]) . "\n";

file_put_contents($log_file, $entry, FILE_APPEND | LOCK_EX);

echo json_encode(['ok' => true]);
