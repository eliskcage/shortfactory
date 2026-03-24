<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }

$body = file_get_contents('php://input');
if (!$body || !trim($body)) $body = '{"text":"ping"}';

// Forward via Apache on medium server (port 80, not 8643 which is firewalled)
$ch = curl_init('http://185.230.216.235/alive/studio/api/chat-cortex.php');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $body,
    CURLOPT_HTTPHEADER     => ['Content-Type: application/json', 'Host: shortfactory.shop'],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 30,
    CURLOPT_CONNECTTIMEOUT => 5,
]);
$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

echo ($resp && $code === 200) ? $resp : json_encode(['reply' => 'brain offline', 'error' => true]);
