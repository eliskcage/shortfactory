<?php
// Log soul sphere completions — called from soul-sphere.html on unlockEmpire()
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$file = __DIR__ . '/soul/completions.json';
if(!is_dir(__DIR__.'/soul')) mkdir(__DIR__.'/soul', 0755, true);

$id = trim($_POST['id'] ?? '');
if(!$id || !preg_match('/^soul-[a-z0-9]+-[a-z0-9]+$/', $id)){
    echo json_encode(['ok'=>false]); exit;
}

$data = file_exists($file) ? json_decode(file_get_contents($file), true) : [];
if(!is_array($data)) $data = [];

// Deduplicate by soul ID
$ids = array_column($data, 'id');
if(!in_array($id, $ids)){
    $data[] = ['id'=>$id, 't'=>time()];
    file_put_contents($file, json_encode($data));
}

echo json_encode(['ok'=>true, 'count'=>count($data)]);
