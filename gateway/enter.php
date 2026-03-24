<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

$data_dir   = __DIR__ . '/data/';
$start_date = '2026-03-23';
$today      = date('Y-m-d');
$cookie_key = 'sf_entered_' . $today;

if (!is_dir($data_dir)) mkdir($data_dir, 0750, true);

// Already entered today?
if (isset($_COOKIE[$cookie_key])) {
    echo json_encode(['ok'=>true,'already'=>true]); exit;
}

$days_since = max(0,(int)floor((strtotime('today')-strtotime($start_date))/86400));
$limit = 10 + $days_since;

$count_file = $data_dir . 'daily_' . $today . '.json';
$count_data = file_exists($count_file) ? json_decode(file_get_contents($count_file), true) : ['count'=>0,'entries'=>[]];
$count = (int)($count_data['count'] ?? 0);

if ($count >= $limit) {
    echo json_encode(['ok'=>false,'full'=>true,'limit'=>$limit]);
    exit;
}

// Log entry
$body = json_decode(file_get_contents('php://input'), true) ?? [];
$device_hash = preg_replace('/[^a-fA-F0-9]/', '', substr($body['dh']??'', 0, 16));
$logo_id     = preg_replace('/[^a-zA-Z0-9_]/', '', substr($body['lid']??'', 0, 32));
$token_hash  = preg_replace('/[^a-fA-F0-9]/', '', substr($body['th']??'', 0, 16));

$count_data['count'] = $count + 1;
$count_data['entries'][] = ['dh'=>$device_hash,'at'=>time()];
file_put_contents($count_file, json_encode($count_data), LOCK_EX);

// Log soul to display wall (if has soul token)
if ($token_hash) {
    $souls_file = $data_dir . 'souls.jsonl';
    file_put_contents($souls_file,
        json_encode(['th'=>$token_hash,'lid'=>$logo_id,'at'=>time()*1000])."\n",
        FILE_APPEND|LOCK_EX
    );
}

// Set cookie (session-length, no expiry = browser session)
setcookie($cookie_key, '1', 0, '/', '', false, true);

echo json_encode([
    'ok'        => true,
    'count'     => $count + 1,
    'limit'     => $limit,
    'remaining' => max(0, $limit - $count - 1)
]);
