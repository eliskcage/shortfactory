<?php
/**
 * Grok Art Generator — violence + retro screensaver categories
 * Run via CLI: php generate_art.php [violence|retro|all]
 * Run via browser: ?cat=violence&n=5&secret=BISCUIT
 */

$isCli = php_sapi_name() === 'cli';
if (!$isCli) {
    header('Content-Type: text/plain');
    $secret = isset($_GET['secret']) ? $_GET['secret'] : '';
    if ($secret !== 'BISCUIT') { http_response_code(403); die("Forbidden\n"); }
}

$API_KEY  = trim(file_get_contents(__DIR__ . '/../alive/studio/.api_key'));
$GALLERY  = __DIR__ . '/gallery.json';
$IMG_DIR  = __DIR__ . '/images/';

$cat      = $isCli ? ($argv[1] ?? 'all') : ($_GET['cat'] ?? 'all');
$n        = $isCli ? intval($argv[2] ?? 8) : min(intval($_GET['n'] ?? 8), 12);

$PROMPTS = [
  'violence' => [
    ['title'=>'Warfront Dawn',       'prompt'=>'Epic cinematic battlefield at sunrise, soldiers silhouetted against orange sky, explosions, dramatic war photography style, ultra-detailed, 8k'],
    ['title'=>'Steel Rain',          'prompt'=>'Fighter jets in dogfight over storm clouds, missile trails, cinematic aerial combat, dramatic lighting, photorealistic'],
    ['title'=>'The Last Stand',      'prompt'=>'Lone warrior in medieval armour holding a sword, ruins burning around him, dust and embers, dark fantasy oil painting style'],
    ['title'=>'Urban Breach',        'prompt'=>'Special forces breaching a door in slow motion, dynamic pose, tactical gear, muzzle flash, dramatic lighting, hyper-realistic'],
    ['title'=>'Clash of Titans',     'prompt'=>'Two armoured giants fighting in an apocalyptic landscape, digital painting, Greg Rutkowski style, cinematic drama'],
    ['title'=>'Thunder Cavalry',     'prompt'=>'Hundreds of cavalry charging across a misty plain, motion blur, epic scale, renaissance oil painting realism'],
    ['title'=>'Colosseum',           'prompt'=>'Gladiator in the Roman Colosseum facing a lion, crowds roaring, golden afternoon light, oil painting hyperrealism'],
    ['title'=>'Siege Engine',        'prompt'=>'Massive siege catapult launching a fireball at a medieval castle at night, cinematic, dramatic fire lighting, oil painting style'],
  ],
  'retro' => [
    ['title'=>'Chrome Horizons',     'prompt'=>'1980s retro sci-fi city skyline, chrome and neon, flying cars, synthwave aesthetic, sunset gradient pink to purple, digital art'],
    ['title'=>'Neon Arcade',         'prompt'=>'Retro 1980s arcade, neon glow, pixel art elements mixed with photorealism, VHS scanlines, nostalgia'],
    ['title'=>'Cassette Future',     'prompt'=>'Futuristic 1980s technology aesthetic, cassette tapes, walkman, chrome robots, synthwave colours purple and pink, digital painting'],
    ['title'=>'Space Cowboy',        'prompt'=>'Lone astronaut on a alien planet, retro 1970s sci-fi poster art style, saturated colours, bold graphic design'],
    ['title'=>'Retrowave Drive',     'prompt'=>'Sports car driving through a neon grid landscape at night, synthwave retrowave aesthetic, grid horizon, digital art'],
    ['title'=>'Starship Command',    'prompt'=>'Inside a retro sci-fi starship bridge, analogue controls, CRT screens, 1980s aesthetic, warm yellow and orange lighting'],
    ['title'=>'Laser City',          'prompt'=>'Aerial view of a 1980s sci-fi city at night, grid streets, purple and pink neon, flying vehicles, retrowave'],
    ['title'=>'The Operator',        'prompt'=>'Woman with a mohawk in leather jacket, neon-lit rain-soaked street, cyberpunk 1980s aesthetic, blade runner vibes, cinematic'],
  ],
];

$gallery = json_decode(file_get_contents($GALLERY), true);

function grok_image($prompt, $apiKey) {
    $ch = curl_init('https://api.x.ai/v1/images/generations');
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . $apiKey,
            'Content-Type: application/json',
        ],
        CURLOPT_POSTFIELDS => json_encode([
            'model'  => 'grok-imagine-image',
            'prompt' => $prompt,
            'n'      => 1,
        ]),
        CURLOPT_TIMEOUT => 60,
    ]);
    $resp = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($code >= 200 && $code < 300) {
        $data = json_decode($resp, true);
        return $data['data'][0]['url'] ?? null;
    }
    return null;
}

function download_image($url, $dest) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT        => 30,
    ]);
    $data = curl_exec($ch);
    curl_close($ch);
    if ($data && strlen($data) > 1000) {
        file_put_contents($dest, $data);
        return true;
    }
    return false;
}

$cats = ($cat === 'all') ? ['violence', 'retro'] : [$cat];
$shaders = ['bloom','chromatic','colorgrade'];

foreach ($cats as $c) {
    if (!isset($PROMPTS[$c])) { echo "Unknown category: $c\n"; continue; }
    $dir = $IMG_DIR . $c . '/';
    if (!is_dir($dir)) mkdir($dir, 0755, true);

    $items = array_slice($PROMPTS[$c], 0, $n);
    $existing = isset($gallery['categories'][$c]['images']) ? $gallery['categories'][$c]['images'] : [];
    $existingTitles = array_column($existing, 'title');

    echo "=== Category: $c ===\n";

    foreach ($items as $i => $item) {
        if (in_array($item['title'], $existingTitles)) {
            echo "  SKIP (exists): {$item['title']}\n";
            continue;
        }

        echo "  Generating: {$item['title']} ... ";
        $url = grok_image($item['prompt'], $API_KEY);
        if (!$url) { echo "FAILED (API error)\n"; continue; }

        $filename = preg_replace('/[^a-z0-9_]/', '-', strtolower($item['title'])) . '.jpg';
        $dest = $dir . $filename;
        if (!download_image($url, $dest)) { echo "FAILED (download)\n"; continue; }

        $shader = $shaders[$i % count($shaders)];
        $gallery['categories'][$c]['images'][] = [
            'url'    => "/screensaver/images/$c/$filename",
            'title'  => $item['title'],
            'shader' => $shader,
            'nsfw'   => false,
        ];
        file_put_contents($GALLERY, json_encode($gallery, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
        echo "OK → $filename\n";
        sleep(1); // Grok rate limit buffer
    }
}

echo "\nDone. Gallery updated.\n";
