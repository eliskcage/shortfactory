<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Upload-Content-Type, X-Upload-Content-Length, Content-Range');
header('Access-Control-Allow-Methods: POST, OPTIONS');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') exit;

$body   = json_decode(file_get_contents('php://input'), true);
$action = $body['action'] ?? '';
$token  = $body['token']  ?? '';

if (!$token) { http_response_code(401); echo json_encode(['error'=>'No token']); exit; }

// ── ACTION: init — start a resumable upload session ──
if ($action === 'init') {
    $meta    = $body['meta']        ?? [];
    $ctype   = $body['contentType'] ?? 'video/webm';
    $clen    = $body['contentLength'] ?? 0;

    $metaJson = json_encode($meta);

    $url = 'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status';
    $ch  = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $metaJson,
        CURLOPT_HEADER         => true,
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . $token,
            'Content-Type: application/json; charset=UTF-8',
            'Content-Length: ' . strlen($metaJson),
            'X-Upload-Content-Type: ' . $ctype,
            'X-Upload-Content-Length: ' . $clen,
        ],
        CURLOPT_TIMEOUT => 30
    ]);
    $resp    = curl_exec($ch);
    $hdrSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $headers = substr($resp, 0, $hdrSize);
    curl_close($ch);

    // Extract Location header (the resumable upload URI)
    $location = '';
    foreach (explode("\r\n", $headers) as $line) {
        if (stripos($line, 'Location:') === 0) {
            $location = trim(substr($line, 9));
        }
    }
    header('Content-Type: application/json');
    echo json_encode(['uploadUri' => $location]);
    exit;
}

// ── ACTION: chunk — forward one chunk to the upload URI ──
if ($action === 'chunk') {
    $uploadUri  = $body['uploadUri']  ?? '';
    $chunkB64   = $body['chunk']      ?? '';
    $rangeStart = (int)($body['rangeStart'] ?? 0);
    $totalSize  = (int)($body['totalSize']  ?? 0);
    $ctype      = $body['contentType'] ?? 'video/webm';

    if (!$uploadUri || !$chunkB64) {
        http_response_code(400); echo json_encode(['error'=>'Missing uploadUri or chunk']); exit;
    }

    $chunkData = base64_decode($chunkB64);
    $chunkLen  = strlen($chunkData);
    $rangeEnd  = $rangeStart + $chunkLen - 1;
    $isLast    = ($rangeEnd + 1 >= $totalSize);

    $ch = curl_init($uploadUri);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CUSTOMREQUEST  => 'PUT',
        CURLOPT_POSTFIELDS     => $chunkData,
        CURLOPT_HEADER         => true,
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . $token,
            'Content-Type: ' . $ctype,
            'Content-Length: ' . $chunkLen,
            'Content-Range: bytes ' . $rangeStart . '-' . $rangeEnd . '/' . $totalSize,
        ],
        CURLOPT_TIMEOUT => 120
    ]);
    $resp    = curl_exec($ch);
    $hdrSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $httpCode= curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $body2   = substr($resp, $hdrSize);
    curl_close($ch);

    header('Content-Type: application/json');
    if ($httpCode === 200 || $httpCode === 201) {
        // Upload complete
        $vid = json_decode($body2, true);
        echo json_encode(['done' => true, 'videoId' => $vid['id'] ?? '', 'raw' => $vid]);
    } elseif ($httpCode === 308) {
        // Resume incomplete — return range received
        echo json_encode(['done' => false, 'status' => 308]);
    } else {
        echo json_encode(['error' => 'HTTP '.$httpCode, 'raw' => $body2]);
    }
    exit;
}

http_response_code(400);
echo json_encode(['error' => 'Unknown action: ' . $action]);
