<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

$data_dir = __DIR__ . '/data/';
if (!is_dir($data_dir)) mkdir($data_dir, 0750, true);

$body     = json_decode(file_get_contents('php://input'), true) ?? [];
$th       = preg_replace('/[^a-fA-F0-9]/', '', substr($body['th']  ?? '', 0, 16));
$lid      = preg_replace('/[^a-zA-Z0-9_]/', '', substr($body['lid'] ?? '', 0, 32));
$device   = preg_replace('/[^a-zA-Z0-9\-]/', '', substr($body['did'] ?? '', 0, 40));
$vis      = preg_replace('/[^a-fA-F0-9_]/', '', substr($body['vis'] ?? '', 0, 16));

if (!$th) { echo json_encode(['ok'=>false]); exit; }

// Cross-validate: if vis=myCode_theirCode, verify theirCode was registered in visual_codes
$vis_valid = true;
$vis_reason = '';
if ($vis && strpos($vis, '_') !== false) {
    $parts = explode('_', $vis, 2);
    $their = strtolower($parts[1] ?? '');
    if ($their) {
        $vc_file = $data_dir . 'visual_codes.jsonl';
        $registered_codes = [];
        if (file_exists($vc_file)) {
            $now = time();
            foreach (file($vc_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
                $entry = json_decode($line, true);
                if ($entry && isset($entry['code']) && ($now - ($entry['at']??0)) < 300) {
                    $registered_codes[] = strtolower($entry['code']);
                }
            }
        }
        if (!in_array($their, $registered_codes)) {
            $vis_valid = false;
            $vis_reason = 'their_code_' . $their . '_not_registered';
        }
    }
}

if (!$vis_valid) {
    echo json_encode(['ok'=>false, 'reason'=>$vis_reason]);
    exit;
}

// Shape code (3-char hex genome identifier from phone)
$sc = preg_replace('/[^a-fA-F0-9]/', '', substr($body['sc'] ?? '', 0, 3));

// Write pair event
$entry = json_encode(array_filter([
    'th'  => $th,
    'lid' => $lid,
    'did' => $device,
    'vis' => $vis,
    'sc'  => $sc ?: null,
    'at'  => time()
])) . "\n";

file_put_contents($data_dir . 'pairs.jsonl', $entry, FILE_APPEND | LOCK_EX);

// If shape code present, update last_shape.json so beacon can read it
if ($sc) {
    file_put_contents($data_dir . 'last_shape.json',
        json_encode(['sc' => $sc, 'lid' => $lid, 'at' => time()]),
        LOCK_EX);
}

echo json_encode(['ok' => true, 'at' => time()]);
