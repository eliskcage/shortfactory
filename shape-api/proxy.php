<?php
/**
 * shape-api/proxy.php
 * Forwards requests from shortfactory.shop/shape-api/* to Python shape_api.py on port 8644
 */
$target = 'http://127.0.0.1:8644';
$path   = $_SERVER['REQUEST_URI'];
// Strip /shape-api prefix if called via rewrite
$path   = preg_replace('#^/shape-api#', '', $path);
if (!$path) $path = '/';

$url    = $target . $path;
$method = $_SERVER['REQUEST_METHOD'];

$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_CUSTOMREQUEST  => $method,
    CURLOPT_TIMEOUT        => 10,
    CURLOPT_HTTPHEADER     => [
        'Content-Type: application/json',
        'X-SF-Key: ' . ($_SERVER['HTTP_X_SF_KEY'] ?? ''),
    ],
]);

if (in_array($method, ['POST','PUT','PATCH'])) {
    curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents('php://input'));
}

$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

http_response_code($code ?: 503);
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
echo $resp ?: json_encode(['error' => 'shape API offline']);
