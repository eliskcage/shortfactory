<?php
/**
 * ShortFactory Fluid Checkout API
 * POST /api/checkout.php
 *
 * Body (JSON):
 * {
 *   "product":     "Revert Fiver",          // display name on Stripe page
 *   "description": "Your £5 soul node",     // optional
 *   "amount":      500,                      // pence/cents (500 = £5.00)
 *   "currency":    "gbp",                    // default: gbp
 *   "ref":         "SFNODE-0001",            // optional referral/node ref
 *   "success_url": "https://shortfactory.shop/join-success.php", // optional override
 *   "cancel_url":  "https://shortfactory.shop/fiver.html"        // optional override
 * }
 *
 * Returns:
 * { "url": "https://checkout.stripe.com/..." }
 * or
 * { "error": "message" }
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

// ── KEYS — swap sk_test_ for sk_live_ when ready ──────────────────────────
define('STRIPE_SECRET',  'sk_test_51STmI1Ceoin99ZsP91IPZyCfvTTnifKouRfsqxKtNE9paI0trs3VvjzljfVyduuvggQAueHv5ZyWUEupReBAByYo00Mm16NJL5');
define('DEFAULT_SUCCESS', 'https://shortfactory.shop/join-success.php');
define('DEFAULT_CANCEL',  'https://shortfactory.shop/fiver.html');
define('SITE_NAME',       'ShortFactory');

// ── Parse input — accepts JSON body or form POST ──────────────────────────
$raw  = file_get_contents('php://input');
$body = $raw ? (json_decode($raw, true) ?? []) : $_POST;

// Minimal required field
$product     = trim($body['product']     ?? 'Payment');
$description = trim($body['description'] ?? '');
$amount      = (int)($body['amount']     ?? 500);   // pence
$currency    = strtolower($body['currency'] ?? 'gbp');
$ref         = preg_replace('/[^A-Za-z0-9_\-]/', '', $body['ref'] ?? '');
$successUrl  = filter_var($body['success_url'] ?? DEFAULT_SUCCESS, FILTER_VALIDATE_URL)
               ? $body['success_url'] : DEFAULT_SUCCESS;
$cancelUrl   = filter_var($body['cancel_url']  ?? DEFAULT_CANCEL,  FILTER_VALIDATE_URL)
               ? $body['cancel_url']  : DEFAULT_CANCEL;

// Append session ID + ref to success URL so join-success.php can log them
$successUrl .= (str_contains($successUrl, '?') ? '&' : '?')
             . 'session_id={CHECKOUT_SESSION_ID}'
             . ($ref ? '&ref=' . urlencode($ref) : '');

if ($amount < 50) {
    http_response_code(400);
    echo json_encode(['error' => 'Amount must be at least 50 pence']);
    exit;
}

// ── Build Stripe Checkout Session ─────────────────────────────────────────
$params = [
    'mode'                               => 'payment',
    'line_items[0][quantity]'            => 1,
    'line_items[0][price_data][currency]'                        => $currency,
    'line_items[0][price_data][unit_amount]'                     => $amount,
    'line_items[0][price_data][product_data][name]'              => $product,
    'success_url'                        => $successUrl,
    'cancel_url'                         => $cancelUrl,
    'client_reference_id'                => $ref ?: null,
];

if ($description) {
    $params['line_items[0][price_data][product_data][description]'] = $description;
}

// Remove nulls
$params = array_filter($params, fn($v) => $v !== null);

$result = stripePost('https://api.stripe.com/v1/checkout/sessions', $params);

if (isset($result['error'])) {
    http_response_code(502);
    echo json_encode(['error' => $result['error']['message'] ?? 'Stripe error']);
    exit;
}

echo json_encode(['url' => $result['url'], 'session_id' => $result['id']]);

// ── Stripe HTTP helper ─────────────────────────────────────────────────────
function stripePost(string $url, array $params): array {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query($params),
        CURLOPT_USERPWD        => STRIPE_SECRET . ':',
        CURLOPT_HTTPHEADER     => ['Content-Type: application/x-www-form-urlencoded'],
        CURLOPT_TIMEOUT        => 15,
    ]);
    $resp = curl_exec($ch);
    curl_close($ch);
    return json_decode($resp, true) ?? ['error' => ['message' => 'No response from Stripe']];
}
