<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }

$cache = sys_get_temp_dir() . '/sf_brain_cache.json';
$ttl   = 30; // seconds

// Serve cache if fresh
if (file_exists($cache) && (time() - filemtime($cache)) < $ttl) {
    echo file_get_contents($cache);
    exit;
}

function curl_brain($url) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => '{}',
        CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 12,
        CURLOPT_CONNECTTIMEOUT => 3,
    ]);
    $r = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return ($r && $code === 200) ? $r : false;
}

// Try local brain first (fast, always running)
$resp = curl_brain('http://127.0.0.1:8643/api/brain-live');

// Fall back to medium server (bigger brain, may be offline)
if (!$resp) {
    $resp = curl_brain('http://185.230.216.235:8643/alive/studio/api/brain-live');
}

if ($resp) {
    @file_put_contents($cache, $resp);
    echo $resp;
} else {
    // Return stale cache rather than blank screen
    if (file_exists($cache)) {
        echo file_get_contents($cache);
    } else {
        echo json_encode(['error'=>'brain offline']);
    }
}
