<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if($_SERVER['REQUEST_METHOD']==='OPTIONS'){echo '{}';exit;}

$dir = __DIR__ . '/data';
if(!is_dir($dir)) mkdir($dir, 0755, true);
$file = $dir . '/tricode_genomes.json';

// GET — return all stored genomes
if($_SERVER['REQUEST_METHOD']==='GET'){
  echo file_exists($file) ? file_get_contents($file) : '[]';
  exit;
}

// POST — save a new genome
$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if(!$data || empty($data['type']) || empty($data['vertices'])){
  echo json_encode(['ok'=>false,'err'=>'missing fields']);
  exit;
}

// Normalise vertices to 0-1 relative to screen size
$sw = max(1, (int)($data['screen']['w'] ?? 1));
$sh = max(1, (int)($data['screen']['h'] ?? 1));
$normVerts = array_map(function($v) use($sw,$sh){
  return ['x'=>round($v['x']/$sw,4), 'y'=>round($v['y']/$sh,4)];
}, $data['vertices']);

// Genome ID = hash of type + normalised verts
$idStr = $data['type'] . json_encode($normVerts);
$id = substr(hash('sha256', $idStr), 0, 12);

$genome = [
  'id'       => $id,
  'type'     => strtoupper(preg_replace('/[^A-Z0-9]/','',$data['type'])),
  'payload'  => $data['payload'] ?? ('SF:'.$data['type']),
  'vertices' => $normVerts,
  'raw'      => $data['vertices'],   // keep raw px too
  'screen'   => ['w'=>$sw,'h'=>$sh],
  'ts'       => time(),
  'ua'       => substr($_SERVER['HTTP_USER_AGENT']??'',0,80),
];

// Load existing, deduplicate by id, append
$all = file_exists($file) ? json_decode(file_get_contents($file), true) : [];
if(!is_array($all)) $all = [];
$all = array_values(array_filter($all, function($g) use($id){ return $g['id']!==$id; }));
$all[] = $genome;

file_put_contents($file, json_encode($all, JSON_PRETTY_PRINT));

// Mirror backup to second server (fire and forget)
$backup = $dir . '/tricode_genomes_backup_' . date('Ymd') . '.json';
file_put_contents($backup, json_encode($all, JSON_PRETTY_PRINT));

echo json_encode(['ok'=>true,'id'=>$id,'total'=>count($all)]);
