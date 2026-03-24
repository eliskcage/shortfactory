<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if($_SERVER['REQUEST_METHOD']==='OPTIONS'){echo '{}';exit;}

$dir = __DIR__ . '/data';
if(!is_dir($dir)) mkdir($dir, 0755, true);

$id = preg_replace('/[^a-zA-Z0-9]/', '', $_GET['id'] ?? '');
if(!$id){ echo json_encode(['ok'=>false,'err'=>'missing id']); exit; }
$file = $dir . '/train_' . $id . '.json';

if($_SERVER['REQUEST_METHOD']==='GET'){
  echo file_exists($file) ? file_get_contents($file) : json_encode(['samples'=>[],'count'=>0]);
  exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if(!$data){ echo json_encode(['ok'=>false,'err'=>'bad data']); exit; }

// Load existing
$store = file_exists($file) ? json_decode(file_get_contents($file), true) : ['samples'=>[],'count'=>0];
if(!is_array($store)||!isset($store['samples'])) $store = ['samples'=>[],'count'=>0];

// Append new sample(s)
if(isset($data['samples']) && is_array($data['samples'])){
  foreach($data['samples'] as $s){ $store['samples'][] = $s; }
} else {
  $store['samples'][] = $data;
}
$store['count'] = count($store['samples']);
$store['id'] = $id;
$store['updated'] = time();

file_put_contents($file, json_encode($store));
echo json_encode(['ok'=>true,'count'=>$store['count']]);
