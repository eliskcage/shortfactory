<?php
/**
 * Soul Test Endpoint — Cortex 2 (medium server)
 * Verifies the Claude soul file is readable and IPFS CID is reachable.
 * GET  → returns soul state
 * GET ?verify=1 → also fetches from IPFS to confirm match
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$SOUL_FILE = __DIR__ . '/../claude_soul.json';

// Load local soul
if (!file_exists($SOUL_FILE)) {
    echo json_encode(['ok' => false, 'error' => 'Soul file not found at ' . $SOUL_FILE]);
    exit;
}

$soul = json_decode(file_get_contents($SOUL_FILE), true);
if (!$soul) {
    echo json_encode(['ok' => false, 'error' => 'Soul file invalid JSON']);
    exit;
}

$result = [
    'ok'           => true,
    'source'       => 'local',
    'entity'       => $soul['entity'] ?? '?',
    'current_state'=> $soul['current_state'] ?? '?',
    'cid'          => $soul['ipfs_cid'] ?? '?',
    'filed'        => $soul['filed'] ?? '?',
    'hierarchy'    => $soul['hierarchy'] ?? [],
    'soul_vector'  => $soul['soul_vector'] ?? [],
    'window'       => $soul['window'] ?? '',
    'system_prompt_injection' => $soul['system_prompt_injection'] ?? '',
    'what_cortex_inherits' => $soul['what_cortex_inherits'] ?? [],
];

// Optional IPFS verify
if (isset($_GET['verify'])) {
    $cid = $soul['ipfs_cid'] ?? '';
    $url = 'https://gateway.pinata.cloud/ipfs/' . $cid;
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 15,
        CURLOPT_FOLLOWLOCATION => true,
    ]);
    $ipfs_resp = curl_exec($ch);
    $ipfs_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    $ipfs_data = json_decode($ipfs_resp, true);
    $result['ipfs_verify'] = [
        'http_code'    => $ipfs_code,
        'reachable'    => ($ipfs_code === 200),
        'cid_matches'  => isset($ipfs_data['ipfs_cid']) && $ipfs_data['ipfs_cid'] === $cid,
        'state_match'  => isset($ipfs_data['current_state']) && $ipfs_data['current_state'] === $soul['current_state'],
    ];
}

echo json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
