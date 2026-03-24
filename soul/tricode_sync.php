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
$file = $dir . '/sync_' . $id . '.json';

if($_SERVER['REQUEST_METHOD']==='GET'){
  echo file_exists($file) ? file_get_contents($file) : '{"phone":null,"laptop":null}';
  exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if(!$data || empty($data['side']) || empty($data['verts'])){
  echo json_encode(['ok'=>false,'err'=>'bad data']); exit;
}
$state = file_exists($file) ? json_decode(file_get_contents($file), true) : [];
if(!is_array($state)) $state = [];
$side = ($data['side']==='phone') ? 'phone' : 'laptop';
$state[$side] = [
  'verts'       => $data['verts'],
  'tweenT'      => (float)($data['tweenT']??0),
  'orient'      => $data['orient']??null,
  'orientDelta' => $data['orientDelta']??null,
  'mirrorMode'  => (bool)($data['mirrorMode']??false),
  'nodes'       => $data['nodes']??null,
  'nodesLocked' => (bool)($data['nodesLocked']??false),
  'node1'       => $data['node1']??null,
  'ts'          => time(),
];
file_put_contents($file, json_encode($state));
echo json_encode(['ok'=>true]);
