<?php
$key = trim(file_get_contents(__DIR__ . '/../alive/studio/.api_key'));
$ch = curl_init('https://api.x.ai/v1/models');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => ['Authorization: Bearer ' . $key],
    CURLOPT_TIMEOUT => 15,
]);
$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
echo "HTTP: $code\n";
$data = json_decode($resp, true);
if (isset($data['data'])) {
    foreach ($data['data'] as $m) {
        echo "  - " . $m['id'] . "\n";
    }
} else {
    echo $resp . "\n";
}
