<?php
$key = trim(file_get_contents(__DIR__ . '/../alive/studio/.api_key'));
echo "Key: " . substr($key, 0, 20) . "...\n";
$ch = curl_init('https://api.x.ai/v1/images/generations');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST           => true,
    CURLOPT_HTTPHEADER     => [
        'Authorization: Bearer ' . $key,
        'Content-Type: application/json',
    ],
    CURLOPT_POSTFIELDS => json_encode([
        'model'  => 'grok-imagine-image',
        'prompt' => 'a sunset over mountains',
        'n'      => 1,
    ]),
    CURLOPT_TIMEOUT => 30,
]);
$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
echo "HTTP: $code\n";
echo $resp . "\n";
