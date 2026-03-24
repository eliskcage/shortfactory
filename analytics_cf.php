<?php
/**
 * analytics_cf.php — Cloudflare Analytics API bridge
 * Fetches last-24h zone analytics via CF GraphQL API.
 *
 * Requires:  CF_API_TOKEN  and  CF_ZONE_ID  in .env or defined below.
 * Get token: dash.cloudflare.com → My Profile → API Tokens → Create Token → Analytics Read
 * Get zone:  dash.cloudflare.com → shortfactory.shop → Overview → Zone ID (bottom-right)
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: no-store');

// ── Satoshi cipher — Vigenere ASCII 32-126, key SKYDADDY ──────────────────
function satoshi_decrypt($text, $key = 'SKYDADDY') {
    $min = 32; $range = 95; $out = ''; $ki = 0;
    for ($i = 0; $i < strlen($text); $i++) {
        $c = ord($text[$i]);
        if ($c >= $min && $c <= 126) {
            $shift = ord($key[$ki % strlen($key)]) - $min;
            $out  .= chr((($c - $min - $shift + $range * 10) % $range) + $min);
            $ki++;
        } else {
            $out .= $text[$i];
        }
    }
    return $out;
}

// ── Credentials ────────────────────────────────────────────────────────────
$token   = ''; $zone_id = ''; $api_key = ''; $email = '';

$cred_file = __DIR__ . '/.cf_credentials';
if (file_exists($cred_file)) {
    $lines = array_filter(array_map('trim', file($cred_file)));
    foreach ($lines as $line) {
        if ($line[0] === '#') continue;
        if (strpos($line, 'CF_API_TOKEN=') === 0) $token   = satoshi_decrypt(substr($line, 13));
        if (strpos($line, 'CF_API_KEY=')   === 0) $api_key = satoshi_decrypt(substr($line, 11));
        if (strpos($line, 'CF_ZONE_ID=')   === 0) $zone_id = satoshi_decrypt(substr($line, 11));
        if (strpos($line, 'CF_EMAIL=')     === 0) $email   = satoshi_decrypt(substr($line,  9));
    }
}

if (!$zone_id) {
    echo json_encode(['ok' => false, 'error' => 'CF credentials not configured']);
    exit;
}

// Prefer Global API Key for GraphQL (analytics token lacks graphql:read permission)
$use_global = ($api_key && $email);

// ── Date range: last 24 h ─────────────────────────────────────────────────
$end   = gmdate('Y-m-d\TH:i:s\Z');
$start = gmdate('Y-m-d\TH:i:s\Z', strtotime('-24 hours'));

// ── GraphQL query ──────────────────────────────────────────────────────────
$query = <<<GQL
{
  viewer {
    zones(filter: {zoneTag: "$zone_id"}) {
      httpRequests1hGroups(
        limit: 24
        filter: {datetime_geq: "$start", datetime_leq: "$end"}
        orderBy: [datetime_ASC]
      ) {
        dimensions { datetime }
        sum {
          requests
          pageViews
          bytes
          cachedRequests
          cachedBytes
          encryptedRequests
          encryptedBytes
          responseStatusMap { edgeResponseStatus requests }
          clientHTTPVersionMap { clientHTTPProtocol requests }
          countryMap { clientCountryName requests bytes }
        }
        uniq { uniques }
      }
    }
  }
}
GQL;

$headers = $use_global
    ? ["X-Auth-Email: $email", "X-Auth-Key: $api_key", "Content-Type: application/json"]
    : ["Authorization: Bearer $token",                  "Content-Type: application/json"];

$ch = curl_init('https://api.cloudflare.com/client/v4/graphql');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_HTTPHEADER     => $headers,
    CURLOPT_POSTFIELDS     => json_encode(['query' => $query]),
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 10,
]);
$raw  = curl_exec($ch);
$err  = curl_error($ch);
curl_close($ch);

if ($err) {
    echo json_encode(['ok' => false, 'error' => $err]);
    exit;
}

$cf = json_decode($raw, true);
if (!$cf || isset($cf['errors'])) {
    echo json_encode(['ok' => false, 'error' => $cf['errors'] ?? 'CF API error', 'raw' => substr($raw, 0, 500)]);
    exit;
}

$groups = $cf['data']['viewer']['zones'][0]['httpRequests1hGroups'] ?? [];

// ── Aggregate ──────────────────────────────────────────────────────────────
$totals = [
    'requests' => 0, 'pageViews' => 0, 'bytes' => 0,
    'cachedRequests' => 0, 'cachedBytes' => 0,
    'encryptedRequests' => 0, 'visits' => 0,
];
$statusMap   = [];
$httpMap     = [];
$countryMap  = [];
$hourly      = [];

foreach ($groups as $g) {
    $s = $g['sum'];
    $totals['requests']          += $s['requests'] ?? 0;
    $totals['pageViews']         += $s['pageViews'] ?? 0;
    $totals['bytes']             += $s['bytes'] ?? 0;
    $totals['cachedRequests']    += $s['cachedRequests'] ?? 0;
    $totals['cachedBytes']       += $s['cachedBytes'] ?? 0;
    $totals['encryptedRequests'] += $s['encryptedRequests'] ?? 0;
    $totals['visits']            += $g['uniq']['uniques'] ?? 0;

    $hour = substr($g['dimensions']['datetime'], 11, 5);
    $hourly[] = ['hour' => $hour, 'requests' => $s['requests'] ?? 0];

    foreach ($s['responseStatusMap'] ?? [] as $sc) {
        $code = (string)$sc['edgeResponseStatus'];
        $statusMap[$code] = ($statusMap[$code] ?? 0) + $sc['requests'];
    }
    foreach ($s['clientHTTPVersionMap'] ?? [] as $hv) {
        $proto = $hv['clientHTTPProtocol'];
        $httpMap[$proto] = ($httpMap[$proto] ?? 0) + $hv['requests'];
    }
    foreach ($s['countryMap'] ?? [] as $c) {
        $cc = $c['clientCountryName'];
        if (!isset($countryMap[$cc])) $countryMap[$cc] = ['requests' => 0, 'bytes' => 0];
        $countryMap[$cc]['requests'] += $c['requests'];
        $countryMap[$cc]['bytes']    += $c['bytes'];
    }
}

// Sort countries
arsort($countryMap);
$countries = [];
foreach ($countryMap as $name => $d) {
    $countries[] = array_merge(['country' => $name], $d);
}

// Sort status codes
arsort($statusMap);

echo json_encode([
    'ok'      => true,
    'period'  => '24h',
    'totals'  => $totals,
    'cache'   => [
        'rate'       => $totals['requests'] ? round($totals['cachedRequests'] / $totals['requests'] * 100, 1) : 0,
        'bytes_rate' => $totals['bytes']    ? round($totals['cachedBytes']    / $totals['bytes']    * 100, 1) : 0,
    ],
    'encryption_rate' => $totals['requests'] ? round($totals['encryptedRequests'] / $totals['requests'] * 100, 1) : 0,
    'status_codes'    => $statusMap,
    'http_versions'   => $httpMap,
    'countries'       => array_slice($countries, 0, 10),
    'hourly'          => $hourly,
]);
