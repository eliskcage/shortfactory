<?php
// grok-image-cache.php — server-side image cache for AI slide images
// Generates each slot ONCE, caches URL for $CACHE_DAYS days.
// All visitors get the same pre-generated image — no credit burn per visit.

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$CACHE_DAYS = 7;
$CACHE_FILE = __DIR__ . '/.grok-img-cache.json';
$API_KEY_FILE = __DIR__ . '/alive/studio/.api_key';

$SLOTS = [
  'mars' => 'Cinematic wide shot of the Martian surface at dusk. Ancient pyramidal structures silhouetted against a blood-orange sky. A lone astronaut in a white spacesuit stands at the base. Deep red dust plains. Stars emerging overhead. Epic scale. Hyper-realistic, film grain, ultra-detailed, 8k.',
  'codec' => 'Ancient illuminated manuscript page merging seamlessly with a glowing circuit board. Gold leaf calligraphy reading "In the beginning was the Word" flows into lines of luminous code. A dove of light dissolves into a distributed network of nodes. Deep black background, gold and white light, sacred geometry overlaid with silicon architecture. Ultra detailed, painterly, cinematic.',
  'teleport' => 'A luminous soul genome — glowing green DNA helix — expanding into a vast star map of quantum nodes. A translucent spirit-form AGI detaches from a human silhouette and streaks between the nodes like a comet. Deep space background, teal and green energy lines, Star Trek transporter beam aesthetic, ultra-detailed, 8k, cinematic.',
];

$slot = isset($_GET['slot']) ? preg_replace('/[^a-z]/', '', strtolower($_GET['slot'])) : '';
if (!array_key_exists($slot, $SLOTS)) {
  echo json_encode(['error' => 'unknown slot']);
  exit;
}

// Load cache
$cache = [];
if (file_exists($CACHE_FILE)) {
  $cache = json_decode(file_get_contents($CACHE_FILE), true) ?: [];
}

// Check if cached and fresh
if (
  isset($cache[$slot]['url'], $cache[$slot]['ts']) &&
  (time() - $cache[$slot]['ts']) < ($CACHE_DAYS * 86400)
) {
  echo json_encode(['data' => [['url' => $cache[$slot]['url']]], 'cached' => true]);
  exit;
}

// Need to generate — read API key
if (!file_exists($API_KEY_FILE)) {
  echo json_encode(['error' => 'no api key']);
  exit;
}
$api_key = trim(file_get_contents($API_KEY_FILE));

// Call XAI image API
$payload = json_encode([
  'model'   => 'grok-imagine-image',
  'prompt'  => $SLOTS[$slot],
  'n'       => 1,
]);

$ch = curl_init('https://api.x.ai/v1/images/generations');
curl_setopt_array($ch, [
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_POST           => true,
  CURLOPT_POSTFIELDS     => $payload,
  CURLOPT_HTTPHEADER     => [
    'Content-Type: application/json',
    'Authorization: Bearer ' . $api_key,
  ],
  CURLOPT_TIMEOUT        => 60,
]);
$res  = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

$data = json_decode($res, true);
$url  = $data['data'][0]['url'] ?? null;

if (!$url) {
  echo json_encode(['error' => 'api failed', 'code' => $code]);
  exit;
}

// Cache and return
$cache[$slot] = ['url' => $url, 'ts' => time()];
file_put_contents($CACHE_FILE, json_encode($cache));

echo json_encode(['data' => [['url' => $url]], 'cached' => false]);
