<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

$data_dir = __DIR__ . '/data/';
if (!is_dir($data_dir)) mkdir($data_dir, 0750, true);

$body = json_decode(file_get_contents('php://input'), true);
if (!$body) { echo json_encode(['ok'=>false,'err'=>'NO DATA']); exit; }

// Sanitise / limit
$report = [
    'id'  => strtoupper(substr(md5(uniqid(mt_rand(), true)), 0, 8)),
    'at'  => time(),
    'ip'  => substr($_SERVER['REMOTE_ADDR'] ?? '', 0, 45),
    'ua'  => substr($body['ua'] ?? '', 0, 200),
    'url' => substr($body['url'] ?? '', 0, 200),
    'ref' => substr($body['ref'] ?? '', 0, 200),
    'note'=> substr($body['note'] ?? '', 0, 500),
    'sections' => $body['sections'] ?? [],
];

// Determine severity
$severity = 'OK';
foreach ($report['sections'] as $sec) {
    $s = $sec['status'] ?? 'OK';
    if ($s === 'FAIL') { $severity = 'FAIL'; break; }
    if ($s === 'WARN' && $severity !== 'FAIL') $severity = 'WARN';
}
$report['severity'] = $severity;

// Write to flat log
$line = json_encode($report) . "\n";
file_put_contents($data_dir . 'reports.jsonl', $line, FILE_APPEND | LOCK_EX);

echo json_encode(['ok'=>true, 'id'=>$report['id'], 'severity'=>$severity]);
