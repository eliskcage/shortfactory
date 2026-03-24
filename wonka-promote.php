<?php
/**
 * Wonka Promote — copies index2.html → index.html
 * Dan presses the save button, this fires, the Wonka ending becomes live.
 */
header('Content-Type: application/json');

$dir = __DIR__;
$src = $dir . '/index2.html';
$dst = $dir . '/index.html';

if (!file_exists($src)) {
    echo json_encode(['success' => false, 'error' => 'index2.html not found']);
    exit;
}

// Backup current index.html first
$backup = $dir . '/index_pre_wonka_' . date('Ymd_His') . '.html';
if (file_exists($dst)) {
    copy($dst, $backup);
}

if (copy($src, $dst)) {
    echo json_encode(['success' => true, 'message' => 'Wonka ending is now live.', 'backup' => basename($backup)]);
} else {
    echo json_encode(['success' => false, 'error' => 'Copy failed — check file permissions']);
}
?>
