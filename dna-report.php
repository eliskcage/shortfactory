<?php
/**
 * GameDNA Report Receiver
 * Stores session DNA strands for debug replay
 */
header('Content-Type: application/json');

$dir = __DIR__ . '/dna/';
if (!is_dir($dir)) mkdir($dir, 0755, true);

$input = json_decode(file_get_contents('php://input'), true);
if (!$input || empty($input['strand'])) {
    echo json_encode(['ok' => false]);
    exit;
}

$session  = preg_replace('/[^a-zA-Z0-9_]/', '', (string)($input['session'] ?? 'unknown'));
$trigger  = preg_replace('/[^a-zA-Z0-9_]/', '', (string)($input['trigger'] ?? 'auto'));
$filename = $dir . date('Ymd_His') . '_' . $trigger . '_' . substr($session, -6) . '.json';

$payload = [
    'session'  => $session,
    'trigger'  => $trigger,
    'ua'       => substr((string)($input['ua'] ?? ''), 0, 120),
    'ip'       => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
    'saved_at' => date('c'),
    'events'   => count($input['strand']),
    'strand'   => $input['strand']
];

file_put_contents($filename, json_encode($payload, JSON_PRETTY_PRINT));

echo json_encode(['ok' => true, 'events' => count($input['strand'])]);
?>
