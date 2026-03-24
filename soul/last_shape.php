<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: no-store');
$f = __DIR__ . '/data/last_shape.json';
echo file_exists($f) ? file_get_contents($f) : '{}';
