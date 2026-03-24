<?php
/**
 * Eye Feed — alive/eye-feed.php
 * Stores + serves the last 50 shape-genome observations from the live eye.
 *
 * POST {objects, mode, frames, ts}  — store observation
 * GET                               — return last 50 as JSON array
 */

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }

$file = __DIR__ . '/eye-feed.json';
$MAX  = 50;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    if (!$data || empty($data['objects'])) {
        echo json_encode(['ok' => false, 'error' => 'no data']);
        exit;
    }

    // Load existing feed
    $feed = [];
    if (file_exists($file)) {
        $feed = json_decode(file_get_contents($file), true) ?: [];
    }

    // Append new observation
    $obs = [
        'ts'      => isset($data['ts'])     ? (int)$data['ts']     : time() * 1000,
        'mode'    => isset($data['mode'])   ? $data['mode']        : 'qubit',
        'frames'  => isset($data['frames']) ? (int)$data['frames'] : 0,
        'objects' => array_slice($data['objects'], 0, 8),
    ];
    array_unshift($feed, $obs);          // newest first
    $feed = array_slice($feed, 0, $MAX); // keep last 50

    file_put_contents($file, json_encode($feed), LOCK_EX);
    echo json_encode(['ok' => true, 'total' => count($feed)]);

} else {
    // GET — serve the feed
    if (file_exists($file)) {
        $feed = json_decode(file_get_contents($file), true) ?: [];
    } else {
        $feed = [];
    }
    echo json_encode([
        'ok'    => true,
        'count' => count($feed),
        'feed'  => $feed,
    ]);
}
