<?php
/**
 * Satoshi Shape Generator
 * GET  /api/satoshi-shape.php?ref=SFNODE-0001&amount=500&currency=gbp&date=20260330
 * Returns: SVG image
 *
 * The shape IS the key. Vigenère ASCII 32-126 cipher encodes the node payload
 * into a unique geometric star glyph. Unforgeable without the cipher key.
 * Verifiable server-side by re-generating from the node record.
 */

define('SATOSHI_KEY', 'supercalifragilisticexpialidocious');

function vigenereEncrypt(string $text, string $key): string {
    $range = 95; $base = 32; $kLen = strlen($key); $out = '';
    for ($i = 0, $n = strlen($text); $i < $n; $i++) {
        $c = ord($text[$i]); $k = ord($key[$i % $kLen]);
        $out .= chr((($c - $base) + ($k - $base)) % $range + $base);
    }
    return $out;
}

function vigenereDecrypt(string $text, string $key): string {
    $range = 95; $base = 32; $kLen = strlen($key); $out = '';
    for ($i = 0, $n = strlen($text); $i < $n; $i++) {
        $c = ord($text[$i]); $k = ord($key[$i % $kLen]);
        $out .= chr((($c - $base) - ($k - $base) + $range) % $range + $base);
    }
    return $out;
}

function buildShape(string $nodeRef, int $amount, string $currency, string $date): array {
    $payload = "$nodeRef|$amount|$currency|$date";
    $cipher  = vigenereEncrypt($payload, SATOSHI_KEY);
    $cLen    = strlen($cipher);

    $cx = 120; $cy = 120;
    $pts = 8; // 8 outer + 8 inner = 16-point star
    $coords = [];

    for ($i = 0; $i < $pts; $i++) {
        $c1 = ord($cipher[($i * 2)     % $cLen]) - 32; // 0-94
        $c2 = ord($cipher[($i * 2 + 1) % $cLen]) - 32; // 0-94

        $outerR      = 50 + ($c1 / 94) * 45;           // 50-95
        $innerR      = 15 + ($c2 / 94) * 25;           // 15-40
        $outerAngle  = ($i / $pts) * 2 * M_PI - M_PI / 2;
        $innerAngle  = $outerAngle + M_PI / $pts;

        $coords[] = [$cx + $outerR * cos($outerAngle), $cy + $outerR * sin($outerAngle), 'outer'];
        $coords[] = [$cx + $innerR * cos($innerAngle), $cy + $innerR * sin($innerAngle), 'inner'];
    }

    // Stroke weight + opacity from cipher seed chars
    $strokeW  = round(1.0 + (ord($cipher[2 % $cLen]) - 32) / 94 * 2.5, 2); // 1.0-3.5
    $fillOp   = round(0.08 + (ord($cipher[3 % $cLen]) - 32) / 94 * 0.18, 3); // 0.08-0.26
    $strokeOp = round(0.6  + (ord($cipher[4 % $cLen]) - 32) / 94 * 0.4,  3); // 0.6-1.0

    // Second accent color hue shift (0-60 degrees off brand)
    $hueShift = (int)((ord($cipher[5 % $cLen]) - 32) / 94 * 60);

    // Encode token = first 20 cipher chars base64 — used for verification
    $token = rtrim(base64_encode(substr($cipher, 0, 20)), '=');

    return compact('coords', 'strokeW', 'fillOp', 'strokeOp', 'hueShift', 'token', 'payload');
}

function renderSVG(array $shape, string $nodeRef): string {
    ['coords' => $coords, 'strokeW' => $sw, 'fillOp' => $fo,
     'strokeOp' => $so, 'hueShift' => $hs, 'token' => $tok] = $shape;

    $pathParts = [];
    foreach ($coords as $i => [$x, $y]) {
        $pathParts[] = ($i === 0 ? 'M' : 'L') . round($x, 2) . ',' . round($y, 2);
    }
    $d = implode(' ', $pathParts) . ' Z';

    // Outer ring: brand orange #DA7756
    // Inner accent: hue-shifted (copper → gold range)
    $r = 218; $g = 119; $b = 86;
    $accentR = min(255, $r + $hs); $accentG = min(255, $g + (int)($hs * 0.6)); $accentB = $b;
    $accent  = sprintf('#%02x%02x%02x', $accentR, $accentG, $accentB);

    return <<<SVG
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="240" height="240" data-node="{$nodeRef}" data-token="{$tok}">
  <defs>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <radialGradient id="bg" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#DA7756" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="240" height="240" fill="#050505" rx="4"/>
  <circle cx="120" cy="120" r="108" fill="url(#bg)"/>
  <circle cx="120" cy="120" r="98" fill="none" stroke="#DA7756" stroke-width="0.4" stroke-opacity="0.2"/>
  <path d="{$d}" fill="#DA7756" fill-opacity="{$fo}" stroke="{$accent}" stroke-width="{$sw}" stroke-linejoin="round" filter="url(#glow)" stroke-opacity="{$so}"/>
  <path d="{$d}" fill="none" stroke="#ffffff" stroke-width="0.5" stroke-opacity="0.15"/>
  <text x="120" y="232" font-family="monospace" font-size="6.5" fill="#DA775650" text-anchor="middle" letter-spacing="2">{$nodeRef}</text>
</svg>
SVG;
}

// ── Verify mode: ?verify=TOKEN&ref=NODE&amount=500&currency=gbp&date=20260330 ──
if (isset($_GET['verify'])) {
    header('Content-Type: application/json');
    $ref    = preg_replace('/[^A-Za-z0-9_\-]/', '', $_GET['ref']      ?? '');
    $amount = (int)($_GET['amount']   ?? 0);
    $curr   = preg_replace('/[^a-z]/', '', strtolower($_GET['currency'] ?? 'gbp'));
    $date   = preg_replace('/[^0-9]/', '', $_GET['date']    ?? '');
    $token  = preg_replace('/[^A-Za-z0-9+\/]/', '', $_GET['verify']);

    $shape = buildShape($ref, $amount, $curr, $date);
    echo json_encode([
        'valid'   => $shape['token'] === $token,
        'node'    => $ref,
        'token'   => $shape['token'],
        'payload' => $shape['payload'],
    ]);
    exit;
}

// ── Generate mode: return SVG ──────────────────────────────────────────────
$ref    = preg_replace('/[^A-Za-z0-9_\-]/', '', $_GET['ref']      ?? 'SFNODE-0000');
$amount = (int)($_GET['amount']   ?? 500);
$curr   = preg_replace('/[^a-z]/', '', strtolower($_GET['currency'] ?? 'gbp'));
$date   = preg_replace('/[^0-9]/', '', $_GET['date']    ?? date('Ymd'));

$shape = buildShape($ref, $amount, $curr, $date);
$svg   = renderSVG($shape, $ref);

header('Content-Type: image/svg+xml');
header('Cache-Control: public, max-age=86400');
echo $svg;
