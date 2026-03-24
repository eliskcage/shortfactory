<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }

$cache    = __DIR__ . '/brain_cache.json';
$lockfile = __DIR__ . '/brain_refresh.lock';
$ttl      = 60; // seconds before background refresh triggers

// Always return cache immediately if it exists (stale-while-revalidate)
if (file_exists($cache)) {
    $age = time() - filemtime($cache);
    echo file_get_contents($cache);

    // Trigger background refresh if stale and not already running
    if ($age > $ttl && !file_exists($lockfile)) {
        touch($lockfile);
        // Flush response to browser first
        if (function_exists('fastcgi_finish_request')) {
            fastcgi_finish_request();
        } else {
            ignore_user_abort(true);
            ob_end_flush();
            @ob_flush();
            flush();
        }
        // Background: fetch fresh data via Apache proxy
        $ch = curl_init('http://185.230.216.235/alive/studio/brain-proxy.php');
        curl_setopt_array($ch, [
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => '{}',
            CURLOPT_HTTPHEADER     => ['Content-Type: application/json', 'Host: shortfactory.shop'],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT        => 25,
            CURLOPT_CONNECTTIMEOUT => 3,
        ]);
        $fresh = curl_exec($ch);
        $code  = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($fresh && $code === 200 && strlen($fresh) > 1000) {
            file_put_contents($cache, $fresh);
        }
        @unlink($lockfile);
    }
    exit;
}

// No cache yet — fetch synchronously (first ever request only)
$ch = curl_init('http://185.230.216.235/alive/studio/brain-proxy.php');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => '{}',
    CURLOPT_HTTPHEADER     => ['Content-Type: application/json', 'Host: shortfactory.shop'],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 25,
    CURLOPT_CONNECTTIMEOUT => 3,
]);
$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
if ($resp && $code === 200 && strlen($resp) > 1000) {
    file_put_contents($cache, $resp);
    echo $resp;
} else {
    echo json_encode(['error'=>'brain offline']);
}
