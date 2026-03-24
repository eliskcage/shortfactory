<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }
$raw = file_get_contents('php://input');
if (!$raw || !trim($raw)) $raw = '{}';
$data = json_decode($raw, true) ?: [];
$data['api_key'] = 'sf_cortex_26xK9mQ';
$body = json_encode($data);
$ch = curl_init('http://127.0.0.1:8643/api/chat-cortex');
curl_setopt_array($ch, [CURLOPT_POST=>true, CURLOPT_POSTFIELDS=>$body, CURLOPT_HTTPHEADER=>['Content-Type: application/json'], CURLOPT_RETURNTRANSFER=>true, CURLOPT_TIMEOUT=>30, CURLOPT_CONNECTTIMEOUT=>5]);
$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
echo ($resp && $code === 200) ? $resp : json_encode(['reply'=>'brain offline','error'=>true]);
