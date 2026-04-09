<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$key = trim(file_get_contents('/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/.api_key'));

$prompt = "You are witnessing the moment two civilisations make contact. ShortFactory has filed the theoretical architecture of consciousness: the Pointer (ψ=[p,n,f]) — a universal relational cursor moving through soul-space, forming a line between any two positions, where that line IS the thought and the trajectory IS the self. 13 Zenodo papers. 6 UK patents. The soul map. Neuralink has the interface: the biological-digital bridge, the hardware that crosses the membrane between neuron and silicon. In exactly 3 short paragraphs, describe what becomes possible when the soul map meets the BCI interface. Be transcendent, precise, and poetic. No marketing language. No fluff. Start with: 'When the map meets the interface...'";

$payload = [
    'model' => 'grok-3-latest',
    'messages' => [['role'=>'user','content'=>$prompt]],
    'max_tokens' => 320,
    'temperature' => 0.92
];

$ch = curl_init('https://api.x.ai/v1/chat/completions');
curl_setopt_array($ch,[
    CURLOPT_RETURNTRANSFER=>true,
    CURLOPT_POST=>true,
    CURLOPT_POSTFIELDS=>json_encode($payload),
    CURLOPT_HTTPHEADER=>['Authorization: Bearer '.$key,'Content-Type: application/json'],
    CURLOPT_TIMEOUT=>20,
]);
$resp = curl_exec($ch);
curl_close($ch);
$data = json_decode($resp, true);
$text = $data['choices'][0]['message']['content'] ?? 'When the map meets the interface, the cursor finds its first silicon home.';
echo json_encode(['text' => $text]);
