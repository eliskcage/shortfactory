<?php
header('Content-Type: application/json');
$dir = '/var/www/vhosts/shortfactory.shop/httpdocs/trump/';
$src = $dir . 'factory2.html';
$dst = $dir . 'factory.html';
if (!file_exists($src)) { echo json_encode(['success'=>false,'error'=>'factory2.html not found']); exit; }
$backup = $dir . 'factory_pre_' . date('Ymd_His') . '.html';
if (file_exists($dst)) copy($dst, $backup);
echo copy($src, $dst) ? json_encode(['success'=>true]) : json_encode(['success'=>false,'error'=>'copy failed']);
?>
