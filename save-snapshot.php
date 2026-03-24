<?php
if ($_GET['token'] !== 'sf2026') { http_response_code(403); die('no'); }
$src = __DIR__ . '/genomic-cats2.html';
$dst = __DIR__ . '/genomic-cats1.html';
$content = file_get_contents($src);
if ($content === false) { http_response_code(500); echo 'failed'; exit; }
@unlink($dst);
if (file_put_contents($dst, $content) !== false) {
    chmod($dst, 0444);
    echo 'saved';
} else {
    http_response_code(500);
    echo 'failed';
}
