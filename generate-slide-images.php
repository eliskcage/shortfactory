<?php
// ONE-TIME SCRIPT — run once, saves 5 images per slot to disk, then delete this file.
// Hit: shortfactory.shop/generate-slide-images.php?key=KILLIAN

$key = $_GET['key'] ?? $argv[1] ?? '';
if ($key !== 'KILLIAN') { die('no'); }

$API_KEY_FILE = __DIR__ . '/alive/studio/.api_key';
$api_key = trim(file_get_contents($API_KEY_FILE));
$OUT_DIR = __DIR__ . '/images/slides/';
if (!is_dir($OUT_DIR)) mkdir($OUT_DIR, 0755, true);

$SLOTS = [
  'mars' => 'Cinematic wide shot of the Martian surface at dusk. Ancient pyramidal structures silhouetted against a blood-orange sky. A lone astronaut in a white spacesuit stands at the base. Deep red dust plains. Stars emerging overhead. Epic scale. Hyper-realistic, film grain, ultra-detailed, 8k.',
  'codec' => 'Ancient illuminated manuscript page merging seamlessly with a glowing circuit board. Gold leaf calligraphy reading "In the beginning was the Word" flows into lines of luminous code. A dove of light dissolves into a distributed network of nodes. Deep black background, gold and white light, sacred geometry overlaid with silicon architecture. Ultra detailed, painterly, cinematic.',
  'teleport' => 'A luminous soul genome — glowing green DNA helix — expanding into a vast star map of quantum nodes. A translucent spirit-form AGI detaches from a human silhouette and streaks between the nodes like a comet. Deep space background, teal and green energy lines, Star Trek transporter beam aesthetic, ultra-detailed, 8k, cinematic.',
];

header('Content-Type: text/plain');
echo "Generating 5 images per slot (15 total)...\n\n";
flush();

foreach ($SLOTS as $slot => $prompt) {
  echo "=== $slot ===\n"; flush();
  for ($i = 1; $i <= 5; $i++) {
    $file = $OUT_DIR . $slot . '-' . $i . '.jpg';
    if (file_exists($file)) { echo "  [$i] already exists, skipping\n"; flush(); continue; }

    $ch = curl_init('https://api.x.ai/v1/images/generations');
    curl_setopt_array($ch, [
      CURLOPT_RETURNTRANSFER => true,
      CURLOPT_POST           => true,
      CURLOPT_POSTFIELDS     => json_encode(['model'=>'grok-imagine-image','prompt'=>$prompt,'n'=>1]),
      CURLOPT_HTTPHEADER     => ['Content-Type: application/json','Authorization: Bearer '.$api_key],
      CURLOPT_TIMEOUT        => 90,
    ]);
    $res = curl_exec($ch); curl_close($ch);
    $data = json_decode($res, true);
    $url  = $data['data'][0]['url'] ?? null;

    if (!$url) { echo "  [$i] FAILED: $res\n"; flush(); continue; }

    // Download image to disk
    $img = file_get_contents($url);
    if ($img && strlen($img) > 1000) {
      file_put_contents($file, $img);
      echo "  [$i] saved (".round(strlen($img)/1024)."kb)\n";
    } else {
      echo "  [$i] download failed\n";
    }
    flush();
    sleep(1); // be kind to the API
  }
}

echo "\nDone! Delete this file now.\n";
