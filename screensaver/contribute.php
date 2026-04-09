<?php
/**
 * Gallery Contribute Endpoint
 * POST: { url, title, category, prompt, contributor_handle }
 * - Downloads image from Grok temp URL, saves to /screensaver/images/{cat}/
 * - Appends to gallery.json
 * - Returns biscuit receipt
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

$GALLERY   = __DIR__ . '/gallery.json';
$IMG_BASE  = __DIR__ . '/images/';
$SHADERS   = ['bloom','chromatic','colorgrade'];
$CATS      = ['violence','retro','cortex','lilleth','community'];

$body = json_decode(file_get_contents('php://input'), true);
if (!$body) { echo json_encode(['ok'=>false,'error'=>'Invalid JSON']); exit; }

$url       = isset($body['url'])       ? trim($body['url'])       : '';
$title     = isset($body['title'])     ? trim($body['title'])     : '';
$category  = isset($body['category'])  ? trim($body['category'])  : 'community';
$prompt    = isset($body['prompt'])    ? trim($body['prompt'])    : '';
$handle    = isset($body['handle'])    ? trim($body['handle'])    : 'anonymous';

// Validate
if (!$url || !filter_var($url, FILTER_VALIDATE_URL)) {
    echo json_encode(['ok'=>false,'error'=>'Invalid image URL']); exit;
}
if (!$title) { echo json_encode(['ok'=>false,'error'=>'Title required']); exit; }
if (!in_array($category, $CATS)) { $category = 'community'; }
$title  = substr(preg_replace('/[^\w\s\-]/', '', $title), 0, 80);
$handle = substr(preg_replace('/[^\w\-@\.]/', '', $handle), 0, 40);
$prompt = substr($prompt, 0, 300);

// Load gallery
$gallery = json_decode(file_get_contents($GALLERY), true);

// Ensure community category exists
if (!isset($gallery['categories']['community'])) {
    $gallery['categories']['community'] = [
        'label'       => 'COMMUNITY',
        'color'       => '#00e676',
        'description' => 'User-generated art — powered by contributor Grok keys',
        'images'      => [],
    ];
}

// Check for duplicate title in category
$existing = array_column($gallery['categories'][$category]['images'] ?? [], 'title');
if (in_array($title, $existing)) {
    echo json_encode(['ok'=>false,'error'=>'Title already exists in this category']); exit;
}

// Download image
$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_TIMEOUT        => 30,
    CURLOPT_USERAGENT      => 'ShortFactory/1.0',
]);
$imageData = curl_exec($ch);
$code      = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if (!$imageData || strlen($imageData) < 1000 || $code >= 400) {
    echo json_encode(['ok'=>false,'error'=>'Could not download image (URL may have expired)']); exit;
}

// Verify it's actually an image
$finfo = new finfo(FILEINFO_MIME_TYPE);
$mime  = $finfo->buffer($imageData);
if (!in_array($mime, ['image/jpeg','image/png','image/webp'])) {
    echo json_encode(['ok'=>false,'error'=>'File is not a valid image']); exit;
}
$ext = $mime === 'image/png' ? 'png' : ($mime === 'image/webp' ? 'webp' : 'jpg');

// Save file
$dir = $IMG_BASE . $category . '/';
if (!is_dir($dir)) mkdir($dir, 0755, true);
$slug     = preg_replace('/[^a-z0-9]+/', '-', strtolower($title));
$filename = $slug . '-' . substr(md5(microtime()), 0, 6) . '.' . $ext;
$dest     = $dir . $filename;
file_put_contents($dest, $imageData);

// Add to gallery
$shader = $SHADERS[count($gallery['categories'][$category]['images']) % count($SHADERS)];
$entry  = [
    'url'         => "/screensaver/images/$category/$filename",
    'title'       => $title,
    'shader'      => $shader,
    'nsfw'        => false,
    'contributor' => $handle,
    'prompt'      => $prompt,
    'submitted'   => date('Y-m-d H:i:s'),
];
$gallery['categories'][$category]['images'][] = $entry;
file_put_contents($GALLERY, json_encode($gallery, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

// Generate Biscuit receipt
$biscuitId  = 'BSC-' . strtoupper(substr(md5($filename . microtime()), 0, 12));
$timestamp  = date('Y-m-d\TH:i:s\Z');

echo json_encode([
    'ok'       => true,
    'image'    => $entry,
    'biscuit'  => [
        'id'        => $biscuitId,
        'title'     => $title,
        'category'  => $category,
        'handle'    => $handle,
        'issued'    => $timestamp,
        'status'    => 'PENDING_VALUATION',
        'claim_url' => 'https://shortfactory.shop/biscuit.html?id=' . $biscuitId,
        'note'      => 'This Biscuit receipt records your creative contribution. Value is determined by community funding. Honoured when GB2607623.2 economy goes live.',
    ],
]);
