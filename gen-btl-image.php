<?php
$apiKey = trim(file_get_contents('/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/.api_key'));

$prompt = 'Official title card for "BETTER THAN LIFE" — a Red Dwarf universe total immersion game. Deep royal purple background, rich violet and amethyst tones. Bold retro-futuristic logo typography: "BETTER THAN LIFE" in large chrome/gold letters with dramatic lighting. Subtitle text: "TOTAL IMMERSION VIRTUAL REALITY GAME" in smaller letters. Visual style: 1980s British sci-fi TV show title card, VHS era aesthetic mixed with neon synthwave. Glowing purple neon lights, stars, deep space backdrop. Crown or royal insignia subtly integrated. Red Dwarf spaceship silhouette faintly visible in background. The colour palette screams love, honour and power — deep purples, royal violets, gold accents. Cinematic, epic, nostalgic. No people, no faces. Pure title card art.';

$payload = json_encode([
    'model'   => 'grok-2-image',
    'prompt'  => $prompt,
    'n'       => 1,
    'response_format' => 'b64_json'
]);

$ch = curl_init('https://api.x.ai/v1/images/generations');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $payload,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER     => [
        'Content-Type: application/json',
        'Authorization: Bearer ' . $apiKey
    ],
    CURLOPT_TIMEOUT => 120
]);

$resp = curl_exec($ch);
$err  = curl_error($ch);
curl_close($ch);

if ($err) { die('CURL ERROR: ' . $err); }

$data = json_decode($resp, true);
if (!isset($data['data'][0]['b64_json'])) {
    die('API ERROR: ' . $resp);
}

$imgData = base64_decode($data['data'][0]['b64_json']);
$savePath = '/var/www/vhosts/shortfactory.shop/httpdocs/images/btl-logo.jpg';
file_put_contents($savePath, $imgData);
echo 'SAVED: ' . $savePath . ' (' . strlen($imgData) . ' bytes)';
