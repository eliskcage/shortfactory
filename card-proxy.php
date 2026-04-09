<?php
set_time_limit(0);
ignore_user_abort(true);
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['error'=>'POST only']); exit; }

$body = file_get_contents('php://input');
if (strlen($body) > 4096) { http_response_code(400); echo json_encode(['error'=>'too large']); exit; }

$ch = curl_init('http://185.230.216.235/api/card');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $body,
    CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 35,
    CURLOPT_CONNECTTIMEOUT => 5,
]);
$result = curl_exec($ch);
$code   = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($result === false || $code !== 200) {
    http_response_code(502);
    echo json_encode(['error' => 'Card service unavailable', 'code' => $code]);
    exit;
}
http_response_code(200);
echo $result;
