<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
$file = __DIR__.'/soul/lock.json';
$state = file_exists($file) ? json_decode(file_get_contents($file), true) : ['locked'=>false];
echo json_encode(['locked'=> !empty($state['locked'])]);
