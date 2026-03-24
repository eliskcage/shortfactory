<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') exit;

$body = json_decode(file_get_contents('php://input'), true);
$prompt = trim($body['prompt'] ?? '');
if (!$prompt) { echo json_encode(['error'=>'No prompt']); exit; }

// SATOSHI ENCRYPTED — complete the spiral to unlock (key: SPIRAL, cipher: Vigenere ASCII 32-126)
$key = 'L23_(#{iy\'p?J@`iUAg3adu?H 9yq0FA}6;BA:k*47v?0=6 )(Y}5v|:~*+ye}^*tclKZ:m\'.[hd]Mu,94G';

$payload = json_encode([
    'model'           => 'grok-2-image',
    'prompt'          => $prompt,
    'n'               => 1,
    'response_format' => 'b64_json'
]);

$ch = curl_init('https://api.x.ai/v1/images/generations');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $payload,
    CURLOPT_HTTPHEADER     => [
        'Authorization: Bearer ' . $key,
        'Content-Type: application/json',
        'Content-Length: ' . strlen($payload)
    ],
    CURLOPT_TIMEOUT => 60
]);
$resp = curl_exec($ch);
$err  = curl_error($ch);
curl_close($ch);

if ($err) { echo json_encode(['error' => $err]); exit; }
echo $resp;
