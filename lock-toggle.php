<?php
// Admin lock toggle — only callable with BISCUIT key
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$key = $_GET['key'] ?? $_POST['key'] ?? '';
if($key !== 'BISCUIT'){
    http_response_code(403);
    echo json_encode(['ok'=>false,'error'=>'denied']);
    exit;
}

$file = __DIR__.'/soul/lock.json';
if(!is_dir(__DIR__.'/soul')) mkdir(__DIR__.'/soul', 0755, true);

$state = file_exists($file) ? json_decode(file_get_contents($file), true) : ['locked'=>false];
if(!is_array($state)) $state = ['locked'=>false];

// Toggle
$state['locked'] = !$state['locked'];
$state['by'] = $_SERVER['REMOTE_ADDR'];
$state['at'] = time();
file_put_contents($file, json_encode($state));

// Set admin cookie (30 days)
setcookie('sf_admin', '1', time()+60*60*24*30, '/', '', false, false);

echo json_encode(['ok'=>true, 'locked'=>$state['locked']]);
