<?php
$host_name = 'localhost';
$database = 'dares4dosh';
$user_name = 'sfadmin';
// SATOSHI ENCRYPTED — complete the spiral to unlock (key: SPIRAL, cipher: Vigenere ASCII 32-126)
$password = '\'v74489E[bSbT';

try {
    $pdo = new PDO("mysql:host=$host_name;dbname=$database;charset=utf8mb4", $user_name, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    die("Database connection failed: " . $e->getMessage());
}
?>