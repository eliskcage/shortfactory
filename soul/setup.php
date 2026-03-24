<?php
// One-shot: creates data dir with correct permissions, then self-destructs
$d = __DIR__ . '/data/';
$ok = true;
if (!is_dir($d)) {
    $ok = mkdir($d, 0777, true);
}
if (is_dir($d)) {
    chmod($d, 0777);
    // test write
    $test = $d . 'test.txt';
    file_put_contents($test, 'ok');
    $wrote = file_exists($test);
    if ($wrote) unlink($test);
    echo json_encode(['dir'=>$d, 'created'=>$ok, 'writable'=>$wrote]);
} else {
    echo json_encode(['error'=>'mkdir failed', 'dir'=>$d]);
}
// Self-destruct
unlink(__FILE__);
