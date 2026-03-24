<?php
// Desktop ALIVE polls this every 2s
// Returns souls paired within last 60 seconds
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: no-cache, no-store');

$data_dir  = __DIR__ . '/data/';
$pairs_file = $data_dir . 'pairs.jsonl';
$window    = 60; // seconds
$since     = time() - $window;

if (!file_exists($pairs_file)) { echo json_encode(['souls'=>[]]); exit; }

// Read last 100 lines
$lines  = array_slice(file($pairs_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES), -100);
$souls  = [];
$seen   = [];

foreach (array_reverse($lines) as $line) {
    $e = json_decode($line, true);
    if (!$e || !isset($e['at']) || $e['at'] < $since) continue;
    $th = $e['th'] ?? '';
    if (isset($seen[$th])) continue; // dedupe
    $seen[$th] = true;
    $souls[] = [
        'th'  => $th,
        'lid' => $e['lid'] ?? '',
        'at'  => $e['at']
    ];
    if (count($souls) >= 5) break; // max 5 active souls
}

echo json_encode(['souls' => $souls, 'ts' => time()]);
