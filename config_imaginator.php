<?php
// config.php - SQLite VERSION

$dbPath = '/tmp/shortfactory.db';

$dsn = "sqlite:$dbPath";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
];

try {
    $pdo = new PDO($dsn, null, null, $options);

    // Create tables if they don't exist
    $pdo->exec("CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )");

    $pdo->exec("CREATE TABLE IF NOT EXISTS scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        creator_id INTEGER,
        theme_data TEXT,
        code_template TEXT,
        votes INTEGER DEFAULT 0,
        purchases INTEGER DEFAULT 0,
        price REAL DEFAULT 4.99,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (creator_id) REFERENCES users(id)
    )");

    $pdo->exec("CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        scenario_id INTEGER,
        original_path TEXT,
        processed_path TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
    )");

    $pdo->exec("CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        scenario_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (user_id, scenario_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
    )");

} catch (PDOException $e) {
    die("DB Connection failed: " . $e->getMessage());
}

session_start();

// STRIPE — TEST KEYS
// Check if Stripe library exists before requiring it
if (file_exists(__DIR__ . '/vendor/autoload.php')) {
    require_once __DIR__ . '/vendor/autoload.php';
} elseif (file_exists(__DIR__ . '/stripe-php/init.php')) {
    require_once __DIR__ . '/stripe-php/init.php';
}

// Only set Stripe key if class exists
if (class_exists('\Stripe\Stripe')) {
    // SATOSHI ENCRYPTED — complete the spiral to unlock (key: SPIRAL, cipher: Vigenere ASCII 32-126)
    \Stripe\Stripe::setApiKey('G<)G\'@H0^ct!Ay4wQ`7E,#3/jK2,vCifj>oo:2"M/ -:-+{! d- 1#9~p@UGwb3Hrw{u>d1Gg x|Tq+vk!ia%6u>kd|!]:v3M`YxQ""~^xy');
}

define('STRIPE_PUBLISHABLE_KEY', 'pk_test_51STmIjE04ctbPqb7dDlcJwdszPNvMwtV9YRduG7WzTvfAuIqCze5DcAW15FawJ4Bmag119ra3cCVrGxMErY79QIp008QC40kGZ');
define('GOOGLE_PAY_MERCHANT_ID', '5683189564');
define('SITE_URL', 'https://s1061738678.websitehome.co.uk');
// SATOSHI ENCRYPTED — complete the spiral to unlock (key: SPIRAL, cipher: Vigenere ASCII 32-126)
define('GEMINI_API_KEY', 'tyD4tFvD=xo&)#\>(ogs7*)7BCq&bE\'wx4+|Mrj');
?>