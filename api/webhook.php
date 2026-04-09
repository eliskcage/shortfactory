<?php
/**
 * REVERT FIVER — Stripe Webhook
 * Stripe fires this on payment_intent.succeeded
 * Confirms node, generates NFT SVG, pins to IPFS via Pinata
 *
 * Set webhook endpoint in Stripe Dashboard:
 *   https://stinkindigger.info/api/webhook.php
 *   Event: payment_intent.succeeded
 */
header('Content-Type: application/json');

define('STRIPE_SECRET',     'sk_test_REPLACE_WITH_SECRET_KEY');
define('STRIPE_WEBHOOK_SEC','whsec_REPLACE_WITH_WEBHOOK_SECRET'); // from Stripe Dashboard
define('PINATA_JWT',        'q1nNoGzVpNwojqD43ljtEJW6UL34HrtzZSENPpDhWjxtTTAsv8oHGkdOXmE0pnS9');

$payload = file_get_contents('php://input');
$sig     = $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '';

// Verify webhook signature
if (!verify_stripe_sig($payload, $sig, STRIPE_WEBHOOK_SEC)) {
    http_response_code(400);
    echo json_encode(['error' => 'Bad signature']);
    exit;
}

$event = json_decode($payload, true);
if ($event['type'] !== 'payment_intent.succeeded') {
    echo json_encode(['ok' => true]);
    exit;
}

$pi      = $event['data']['object'];
$node_id = $pi['metadata']['node_id'] ?? '';
$ref_by  = $pi['metadata']['ref_by']  ?? '';

if (!$node_id) { echo json_encode(['ok' => true]); exit; }

// ── DB ──
$db_path = __DIR__ . '/../data/nodes.sqlite';
$db = new SQLite3($db_path);

// Already processed?
$paid = $db->querySingle("SELECT stripe_paid FROM nodes WHERE id='$node_id'");
if ($paid) { echo json_encode(['ok' => true]); exit; }

// Mark paid
$db->exec("UPDATE nodes SET stripe_paid=1, paid_at='" . date('c') . "' WHERE id='$node_id'");

// Record chain link
if ($ref_by) {
    $db->exec("INSERT INTO chain (node_id, recruit_id, joined_at) VALUES ('$ref_by', '$node_id', '" . date('c') . "')");
}

// ── GENERATE NFT SVG ──
$svg = generate_nft_svg($node_id);
$svg_filename = 'SOUL-SFT-' . $node_id . '.svg';

// ── PIN SVG TO IPFS ──
$image_cid = pinata_pin_json([
    'pinataContent'  => $svg,
    'pinataMetadata' => ['name' => $svg_filename],
], true, $svg, $svg_filename); // pin as file

// ── PIN METADATA JSON TO IPFS ──
$metadata = [
    'name'        => 'Soul SFT — ' . $node_id,
    'description' => 'ShortFactory Soul SFT. A key to the network. Dividends, royalties and chain revenue flow through this node permanently.',
    'image'       => 'ipfs://' . $image_cid,
    'external_url'=> 'https://stinkindigger.info/node.html?id=' . $node_id,
    'attributes'  => [
        ['trait_type' => 'Network',   'value' => 'ShortFactory'],
        ['trait_type' => 'Node',      'value' => $node_id],
        ['trait_type' => 'Referred By','value'=> $ref_by ?: 'Genesis'],
        ['trait_type' => 'Minted',    'value' => date('Y-m-d')],
    ]
];
$meta_cid = pinata_pin_json($metadata);

// Store IPFS hash
$db->exec("UPDATE nodes SET ipfs_hash='$meta_cid' WHERE id='$node_id'");

echo json_encode(['ok' => true, 'node' => $node_id, 'ipfs' => $meta_cid]);

// ─────────────────────────────────────────────
// FUNCTIONS
// ─────────────────────────────────────────────

function verify_stripe_sig($payload, $sig_header, $secret) {
    $parts = explode(',', $sig_header);
    $timestamp = '';
    $signatures = [];
    foreach ($parts as $p) {
        if (strpos($p, 't=') === 0) $timestamp = substr($p, 2);
        if (strpos($p, 'v1=') === 0) $signatures[] = substr($p, 3);
    }
    if (!$timestamp) return false;
    $signed = $timestamp . '.' . $payload;
    $expected = hash_hmac('sha256', $signed, $secret);
    foreach ($signatures as $s) {
        if (hash_equals($expected, $s)) return true;
    }
    return false;
}

function pinata_pin_json($data, $as_file = false, $file_content = '', $filename = 'metadata.json') {
    $jwt = PINATA_JWT;
    if ($as_file) {
        // pin file content
        $boundary = uniqid();
        $body  = "--$boundary\r\n";
        $body .= "Content-Disposition: form-data; name=\"file\"; filename=\"$filename\"\r\n";
        $body .= "Content-Type: image/svg+xml\r\n\r\n";
        $body .= $file_content . "\r\n";
        $body .= "--$boundary\r\n";
        $body .= "Content-Disposition: form-data; name=\"pinataMetadata\"\r\n\r\n";
        $body .= json_encode(['name' => $filename]) . "\r\n";
        $body .= "--$boundary--";
        $ch = curl_init('https://api.pinata.cloud/pinning/pinFileToIPFS');
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => $body,
            CURLOPT_HTTPHEADER     => [
                "Authorization: Bearer $jwt",
                "Content-Type: multipart/form-data; boundary=$boundary",
            ],
        ]);
    } else {
        $ch = curl_init('https://api.pinata.cloud/pinning/pinJSONToIPFS');
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => json_encode($data),
            CURLOPT_HTTPHEADER     => [
                "Authorization: Bearer $jwt",
                "Content-Type: application/json",
            ],
        ]);
    }
    $resp = json_decode(curl_exec($ch), true);
    curl_close($ch);
    return $resp['IpfsHash'] ?? 'pending';
}

function generate_nft_svg($node_id) {
    // Deterministic seed from node ID
    $seed = crc32($node_id);
    srand($seed);

    $num = intval(preg_replace('/[^0-9]/', '', $node_id));
    $hue = ($seed % 360 + 360) % 360; // unique hue per node, mostly gold range
    // Keep it in gold/amber range: 35-55 degrees
    $hue = 35 + ($seed % 20);

    $dots = [];
    for ($i = 0; $i < 10; $i++) {
        $angle = (rand(0, 3600) / 3600) * 2 * M_PI;
        $dist  = 60 + rand(0, 100);
        $dots[] = [
            'x' => 200 + $dist * cos($angle),
            'y' => 200 + $dist * sin($angle),
            'r' => 2 + rand(0, 4),
            'o' => (0.3 + rand(0, 70) / 100),
        ];
    }

    $dot_svg = '';
    foreach ($dots as $d) {
        $dot_svg .= sprintf('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="hsl(%d,85%%,55%%)" opacity="%.2f"/>', $d['x'], $d['y'], $d['r'], $hue, $d['o']);
    }

    // connecting lines
    $lines = '';
    for ($i = 0; $i < count($dots) - 1; $i++) {
        if (rand(0, 1)) {
            $lines .= sprintf('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="hsl(%d,85%%,55%%)" stroke-width="0.5" opacity="0.12"/>', $dots[$i]['x'], $dots[$i]['y'], $dots[$i+1]['x'], $dots[$i+1]['y'], $hue);
        }
    }

    return <<<SVG
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" fill="#000"/>
  <!-- grid -->
  <g stroke="hsl({$hue},85%,55%)" stroke-width="0.5" opacity="0.05">
    <line x1="100" y1="0" x2="100" y2="400"/><line x1="200" y1="0" x2="200" y2="400"/>
    <line x1="300" y1="0" x2="300" y2="400"/><line x1="0" y1="100" x2="400" y2="100"/>
    <line x1="0" y1="200" x2="400" y2="200"/><line x1="0" y1="300" x2="400" y2="300"/>
  </g>
  <!-- soul rings -->
  <circle cx="200" cy="200" r="140" fill="none" stroke="hsl({$hue},85%,55%)" stroke-width="0.8" opacity="0.06"/>
  <circle cx="200" cy="200" r="100" fill="none" stroke="hsl({$hue},85%,55%)" stroke-width="0.8" opacity="0.08"/>
  <circle cx="200" cy="200" r="60"  fill="none" stroke="hsl({$hue},85%,55%)" stroke-width="0.8" opacity="0.10"/>
  <!-- dots + lines -->
  {$lines}
  {$dot_svg}
  <!-- central diamond -->
  <polygon points="200,168 220,200 200,232 180,200" fill="none" stroke="hsl({$hue},85%,55%)" stroke-width="1.5" opacity="0.8"/>
  <circle cx="200" cy="200" r="4" fill="hsl({$hue},95%,75%)" opacity="0.95"/>
  <!-- node ID -->
  <text x="200" y="370" text-anchor="middle" font-family="Courier New,monospace" font-size="11" fill="hsl({$hue},85%,55%)" opacity="0.35" letter-spacing="3">{$node_id}</text>
  <text x="200" y="385" text-anchor="middle" font-family="Courier New,monospace" font-size="8" fill="hsl({$hue},85%,55%)" opacity="0.15" letter-spacing="2">SHORTFACTORY · SOUL SFT</text>
</svg>
SVG;
}
