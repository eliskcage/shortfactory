<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { echo json_encode(['ok'=>false,'err'=>'POST only']); exit; }

$src = __DIR__ . '/shape-qr-beacon2.html';
$dst = __DIR__ . '/shape-qr-beacon.html';

if (!file_exists($src)) { echo json_encode(['ok'=>false,'err'=>'src missing']); exit; }
if (copy($src, $dst)) {
    echo json_encode(['ok'=>true,'at'=>time()]);
} else {
    echo json_encode(['ok'=>false,'err'=>'copy failed']);
}
