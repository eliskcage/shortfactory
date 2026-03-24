<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }

$body = json_decode(file_get_contents('php://input'), true);
$prompt = isset($body['prompt']) ? trim($body['prompt']) : '';

if (!$prompt) {
    echo json_encode(['error' => 'No prompt']);
    exit;
}

$xai_key = 'xai-' . file_get_contents(__DIR__ . '/../.xai_key_suffix') ?: '';

// Read key from parent .api_key if exists
$key_file = __DIR__ . '/../../alive/studio/.api_key';
if (file_exists($key_file)) {
    $xai_key = trim(file_get_contents($key_file));
}

// Fallback: read from local .xai_key
$local_key = __DIR__ . '/.xai_key';
if (file_exists($local_key)) {
    $xai_key = trim(file_get_contents($local_key));
}

if (!$xai_key) {
    echo json_encode(['error' => 'No API key configured']);
    exit;
}

$payload = json_encode([
    'model' => 'grok-2-image',
    'prompt' => $prompt,
    'n' => 1,
    'response_format' => 'url'
]);

$ch = curl_init('https://api.x.ai/v1/images/generations');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $payload,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'Authorization: Bearer ' . $xai_key
    ],
    CURLOPT_TIMEOUT => 60
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http_code !== 200) {
    echo json_encode(['error' => 'XAI API error', 'code' => $http_code]);
    exit;
}

$data = json_decode($response, true);
$url = $data['data'][0]['url'] ?? null;

if (!$url) {
    echo json_encode(['error' => 'No image returned', 'raw' => $data]);
    exit;
}

echo json_encode(['url' => $url]);
