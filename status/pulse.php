<?php
/**
 * PROJECT GENOME PULSE
 * Checks 8 systems × 2 bits = 16-bit health genome
 * Bit encoding per system: 11=OK  10=WARN  01=FAIL  00=DOWN
 *
 * Systems (high bit to low):
 *  [15:14] Old server (82.165.134.4)
 *  [13:12] New server (185.230.216.235)
 *  [11:10] Soul pair-check API
 *  [9:8]   Gateway check API
 *  [7:6]   ALIVE page load
 *  [5:4]   Cortex brain API
 *  [3:2]   Soul pairings active (activity)
 *  [1:0]   Error rate (troubleshoot reports)
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: no-cache, no-store');

$start = microtime(true);

// ── Helper: HTTP check ──
function check_url($url, $timeout=3) {
    $ctx = stream_context_create(['http'=>['timeout'=>$timeout,'ignore_errors'=>true]]);
    $t0  = microtime(true);
    $res = @file_get_contents($url, false, $ctx);
    $ms  = round((microtime(true)-$t0)*1000);
    if ($res === false) return ['status'=>'DOWN', 'ms'=>$ms, 'body'=>''];
    $code = 0;
    foreach ($http_response_header??[] as $h) {
        if (preg_match('#HTTP/\S+ (\d+)#', $h, $m)) $code = (int)$m[1];
    }
    if ($code >= 500) return ['status'=>'FAIL', 'ms'=>$ms, 'body'=>substr($res,0,200)];
    if ($code >= 400) return ['status'=>'WARN', 'ms'=>$ms, 'body'=>substr($res,0,200)];
    if ($ms > 2000)   return ['status'=>'WARN', 'ms'=>$ms, 'body'=>substr($res,0,200)];
    return ['status'=>'OK', 'ms'=>$ms, 'body'=>substr($res,0,200)];
}

function status_bits($status) {
    return match($status) { 'OK'=>'11', 'WARN'=>'10', 'FAIL'=>'01', default=>'00' };
}

$results = [];
$bits    = '';

// ── [15:14] Old server ──
$r = check_url('http://82.165.134.4/', 3);
$results['old_server'] = $r;
$bits .= status_bits($r['status']);

// ── [13:12] New server ──
$r = check_url('http://185.230.216.235/', 3);
$results['new_server'] = $r;
$bits .= status_bits($r['status']);

// ── [11:10] Soul pair-check API ──
$r = check_url('https://www.shortfactory.shop/soul/pair-check.php?_='.time(), 4);
// Validate JSON
$valid = !empty($r['body']) && isset(json_decode($r['body'],true)['souls']);
if ($r['status']==='OK' && !$valid) $r['status']='WARN';
$results['soul_api'] = $r;
$bits .= status_bits($r['status']);

// ── [9:8] Gateway check API ──
$r = check_url('https://www.shortfactory.shop/gateway/check.php?_='.time(), 4);
$valid = !empty($r['body']) && isset(json_decode($r['body'],true)['allowed']);
if ($r['status']==='OK' && !$valid) $r['status']='WARN';
$results['gateway_api'] = $r;
$bits .= status_bits($r['status']);

// ── [7:6] ALIVE page ──
$r = check_url('https://www.shortfactory.shop/alive/', 5);
$has_alive = str_contains($r['body'],'ALiVE') || str_contains($r['body'],'alive') || strlen($r['body'])>5000;
if ($r['status']==='OK' && !$has_alive) $r['status']='WARN';
$results['alive_page'] = $r;
$bits .= status_bits($r['status']);

// ── [5:4] Cortex brain API ──
$r = check_url('http://185.230.216.235/cortex/live/proxy.php?ep=brain-live', 4);
$valid = !empty($r['body']) && (str_contains($r['body'],'{') || str_contains($r['body'],'brain'));
if ($r['status']==='OK' && !$valid) $r['status']='WARN';
$results['brain_api'] = $r;
$bits .= status_bits($r['status']);

// ── [3:2] Soul activity (pairings in last hour) ──
$pairs_file = __DIR__ . '/../soul/data/pairs.jsonl';
$pair_count = 0;
if (file_exists($pairs_file)) {
    $since = time() - 3600;
    $lines = array_slice(file($pairs_file, FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES), -200);
    foreach ($lines as $l) {
        $e = json_decode($l,true);
        if ($e && ($e['at']??0) >= $since) $pair_count++;
    }
}
$activity_status = $pair_count >= 5 ? 'OK' : ($pair_count >= 1 ? 'WARN' : 'FAIL');
$results['soul_activity'] = ['status'=>$activity_status, 'count'=>$pair_count];
$bits .= status_bits($activity_status);

// ── [1:0] Error rate (troubleshoot reports last hour) ──
$reports_file = __DIR__ . '/../troubleshoot/data/reports.jsonl';
$err_count = 0;
if (file_exists($reports_file)) {
    $since = time() - 3600;
    $lines = array_slice(file($reports_file, FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES), -100);
    foreach ($lines as $l) {
        $e = json_decode($l,true);
        if ($e && ($e['at']??0) >= $since && ($e['severity']??'OK') === 'FAIL') $err_count++;
    }
}
$err_status = $err_count === 0 ? 'OK' : ($err_count <= 3 ? 'WARN' : 'FAIL');
$results['error_rate'] = ['status'=>$err_status, 'count'=>$err_count];
$bits .= status_bits($err_status);

// ── Build genome ──
$genome_int  = bindec($bits);
$genome_hex  = strtoupper(dechex($genome_int));
$genome_hex  = str_pad($genome_hex, 4, '0', STR_PAD_LEFT); // always 4 hex chars

// Overall health
$ok_count = substr_count($bits,'11')/strlen('11') * 2; // crude — count 11 pairs
$ok_count   = 0; $warn_count = 0; $fail_count = 0;
for ($i=0;$i<16;$i+=2) {
    $pair = substr($bits,$i,2);
    if ($pair==='11') $ok_count++;
    elseif ($pair==='10') $warn_count++;
    else $fail_count++;
}
$overall = $fail_count > 0 ? 'FAIL' : ($warn_count > 0 ? 'WARN' : 'OK');

$elapsed = round((microtime(true)-$start)*1000);

echo json_encode([
    'genome'   => $genome_hex,
    'bits'     => $bits,
    'overall'  => $overall,
    'ok'       => $ok_count,
    'warn'     => $warn_count,
    'fail'     => $fail_count,
    'systems'  => [
        'old_server'    => $results['old_server'],
        'new_server'    => $results['new_server'],
        'soul_api'      => $results['soul_api'],
        'gateway_api'   => $results['gateway_api'],
        'alive_page'    => $results['alive_page'],
        'brain_api'     => $results['brain_api'],
        'soul_activity' => $results['soul_activity'],
        'error_rate'    => $results['error_rate'],
    ],
    'elapsed_ms' => $elapsed,
    'ts'         => time(),
]);
