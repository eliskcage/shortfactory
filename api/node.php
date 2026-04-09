<?php
/**
 * REVERT FIVER — Node data API
 * GET ?id=SFNODE-0001
 * Returns node stats, chain, tokens, ipfs hash
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$node_id = preg_replace('/[^A-Z0-9\-]/', '', strtoupper($_GET['id'] ?? ''));
if (!$node_id) { echo json_encode(['error' => 'No ID']); exit; }

$db_path = __DIR__ . '/../data/nodes.sqlite';
if (!file_exists($db_path)) { echo json_encode(['error' => 'Not found']); exit; }

$db = new SQLite3($db_path);
$node = $db->querySingle("SELECT * FROM nodes WHERE id='$node_id'", true);
if (!$node) { echo json_encode(['error' => 'Node not found']); exit; }

// Chain: who joined under this node
$chain_res = $db->query("SELECT recruit_id, joined_at FROM chain WHERE node_id='$node_id' ORDER BY joined_at DESC");
$chain = [];
while ($row = $chain_res->fetchArray(SQLITE3_ASSOC)) {
    $chain[] = [
        'id'    => $row['recruit_id'],
        'since' => date('d M Y', strtotime($row['joined_at'])),
    ];
}

// Chain depth: recursive count
function count_depth($db, $node_id, $depth = 0) {
    if ($depth > 20) return $depth; // cap
    $res = $db->query("SELECT recruit_id FROM chain WHERE node_id='$node_id'");
    $max = $depth;
    while ($row = $res->fetchArray()) {
        $d = count_depth($db, $row['recruit_id'], $depth + 1);
        if ($d > $max) $max = $d;
    }
    return $max;
}
$depth = count_depth($db, $node_id);

// Total chain earn (£5 per recruit, tiered: direct=100%, depth2=20%, depth3+=5%)
$direct = count($chain);
$earned = $direct > 0 ? $direct * 5.00 : 0; // simplified for now

// Token unlocks — based on activity
// In future: check video submissions table
// For now: simulate based on chain count
$tokens = [];
if ($direct >= 1) $tokens[] = 'ism';
if ($direct >= 3) $tokens[] = 'ist';
if ($depth >= 2)  $tokens[] = 'phobe';

// Shard ownership — look up in MariaDB by ref param
$shard_data = null;
$ref_param  = preg_replace('/[^A-Za-z0-9_\-]/', '', $_GET['ref'] ?? '');
if ($ref_param) {
    try {
        $pdo = new PDO('mysql:host=localhost;dbname=sf_marketplace;charset=utf8mb4', 'sfadmin', 'SFmarket2026!', [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
        $usr = $pdo->prepare("SELECT shard_won FROM revert_users WHERE ref=? LIMIT 1");
        $usr->execute([$ref_param]);
        $u = $usr->fetch();
        if ($u && $u['shard_won']) {
            $sh = $pdo->prepare("SELECT shard_num, title, teaser, story_enc FROM shards WHERE shard_num=? LIMIT 1");
            $sh->execute([$u['shard_won']]);
            $s = $sh->fetch();
            if ($s) {
                $shard_data = [
                    'num'       => (int)$s['shard_num'],
                    'title'     => $s['title'],
                    'teaser'    => $s['teaser'],
                    'story_enc' => $s['story_enc'] ?? '',
                ];
            }
        }
    } catch (Exception $e) { /* silent */ }
}

echo json_encode([
    'id'       => $node_id,
    'ipfs'     => $node['ipfs_hash'] ?: 'pending',
    'paid'     => (bool)$node['stripe_paid'],
    'recruits' => $direct,
    'earned'   => $earned,
    'depth'    => $depth,
    'tokens'   => $tokens,
    'chain'    => $chain,
    'ref_by'   => $node['ref_by'],
    'since'    => date('d M Y', strtotime($node['created_at'])),
    'shard'    => $shard_data,
]);
