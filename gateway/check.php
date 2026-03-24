<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$data_dir  = __DIR__ . '/data/';
$start_date = '2026-03-23'; // day 0 — limit starts at 10

if (!is_dir($data_dir)) mkdir($data_dir, 0750, true);

// ── Daily limit ──
$days_since = max(0, (int)floor((strtotime('today') - strtotime($start_date)) / 86400));
$limit = 10 + $days_since; // +1 per day automatically

// ── Today's entry count ──
$today      = date('Y-m-d');
$count_file = $data_dir . 'daily_' . $today . '.json';
$count_data = file_exists($count_file) ? json_decode(file_get_contents($count_file), true) : ['count'=>0,'entries'=>[]];
$count      = (int)($count_data['count'] ?? 0);

// ── Time to midnight reset ──
$midnight    = strtotime('tomorrow');
$resets_in   = $midnight - time();

// ── Recent soul captures (last 20) ──
$souls_file = $data_dir . 'souls.jsonl';
$souls = [];
if (file_exists($souls_file)) {
    $lines = array_slice(file($souls_file, FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES), -20);
    foreach (array_reverse($lines) as $line) {
        $s = json_decode($line, true);
        if ($s) $souls[] = ['th'=>substr($s['th']??'',0,8), 'lid'=>$s['lid']??'', 'at'=>$s['at']??0];
    }
}

// ── Cookie: already entered today? ──
$cookie_key = 'sf_entered_' . $today;
$already_in = isset($_COOKIE[$cookie_key]);

echo json_encode([
    'allowed'   => $already_in || $count < $limit,
    'full'      => !$already_in && $count >= $limit,
    'count'     => $count,
    'limit'     => $limit,
    'remaining' => max(0, $limit - $count),
    'resets_in' => $resets_in,
    'day'       => $days_since,
    'souls'     => $souls
]);
