<?php
// api/slots.php — returns remaining slots for the earn £5 offer
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

define('TOTAL_SLOTS', 10);
define('DB_HOST', 'localhost');
define('DB_NAME', 'sf_marketplace');

try {
    $pdo = new PDO('mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8mb4',
        'sfadmin', 'SFmarket2026!',
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);

    // Count paid + submitted nodes
    $used = (int)$pdo->query("SELECT COUNT(*) FROM revert_users WHERE paid=1")->fetchColumn();
    $remaining = max(0, TOTAL_SLOTS - $used);
} catch (Exception $e) {
    $remaining = TOTAL_SLOTS; // fallback
}

echo json_encode(['total' => TOTAL_SLOTS, 'remaining' => $remaining]);
