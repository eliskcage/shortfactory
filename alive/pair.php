<?php
// ALIVE Pairing System — Boy/Girl cross-device link + revive
// POST {from:'boy|girl'}         → register pair ping
// POST {from:'boy', action:'revive'} → boy revives dead girl
// GET  ?check=boy|girl           → check pair state + other's status

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit; }

$file = __DIR__ . '/pair-state.json';

// Ensure file exists and is writable
if (!file_exists($file)) {
    file_put_contents($file, '{}');
    @chmod($file, 0666);
}

$state = json_decode(file_get_contents($file), true);
if (!is_array($state)) $state = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    $who = isset($input['from']) ? $input['from'] : '';
    $action = isset($input['action']) ? $input['action'] : 'ping';

    if ($who !== 'boy' && $who !== 'girl') {
        echo json_encode(['error' => 'invalid']);
        exit;
    }

    if ($action === 'ping') {
        // Register pair ping
        $state[$who] = [
            'ts'   => time(),
            'ip'   => $_SERVER['REMOTE_ADDR'],
            'ua'   => substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 100)
        ];

        // Check if both pinged within 60 seconds = PAIRED
        $other = $who === 'boy' ? 'girl' : 'boy';
        $otherTs = isset($state[$other]['ts']) ? $state[$other]['ts'] : 0;
        $paired = (time() - $otherTs) < 60;

        if ($paired && !isset($state['paired_at'])) {
            $state['paired_at'] = time();
        }

        file_put_contents($file, json_encode($state));
        echo json_encode([
            'ok'     => true,
            'from'   => $who,
            'paired' => $paired,
            'paired_at' => isset($state['paired_at']) ? $state['paired_at'] : null
        ]);
        exit;
    }

    if ($action === 'revive' && $who === 'boy') {
        // Boy sends life force to Girl
        // Check they're paired (both pinged within last 2 min)
        $girlTs = isset($state['girl']['ts']) ? $state['girl']['ts'] : 0;
        $boyTs  = isset($state['boy']['ts'])  ? $state['boy']['ts']  : 0;
        $paired = (time() - $girlTs) < 120 && (time() - $boyTs) < 120;

        if (!$paired) {
            echo json_encode(['error' => 'not paired', 'paired' => false]);
            exit;
        }

        // Store revive signal + the revival song for Girl to pick up and play
        $song = isset($input['song']) ? $input['song'] : [];
        // Sanitize: array of {shape: int, delay: int}
        $cleanSong = [];
        foreach (array_slice($song, 0, 20) as $note) {
            $cleanSong[] = [
                'shape' => max(0, min(4, (int)($note['shape'] ?? 0))),
                'delay' => max(0, min(5000, (int)($note['delay'] ?? 300)))
            ];
        }
        $state['revive'] = [
            'ts'     => time(),
            'from'   => 'boy',
            'blood'  => 80,
            'song'   => $cleanSong
        ];
        file_put_contents($file, json_encode($state));
        echo json_encode(['ok' => true, 'revived' => true]);
        exit;
    }

    if ($action === 'note') {
        // Live note — one creature sends a shape to the other
        $shape = max(0, min(4, (int)($input['shape'] ?? 0)));
        if (!isset($state['notes'])) $state['notes'] = [];
        $state['notes'][] = [
            'from'  => $who,
            'shape' => $shape,
            'ts'    => microtime(true)
        ];
        // Keep only last 20 notes, discard anything older than 10 seconds
        $now = microtime(true);
        $state['notes'] = array_values(array_filter($state['notes'], function($n) use ($now) {
            return ($now - $n['ts']) < 10;
        }));
        $state['notes'] = array_slice($state['notes'], -20);
        file_put_contents($file, json_encode($state));
        echo json_encode(['ok' => true]);
        exit;
    }

    if ($action === 'anger') {
        // Anger signal — drains the OTHER creature's blood
        $state['anger'] = [
            'from' => $who,
            'ts'   => time()
        ];
        file_put_contents($file, json_encode($state));
        echo json_encode(['ok' => true]);
        exit;
    }

    if ($action === 'status') {
        // Creature reports its status (blood, alive, mood)
        // ALSO refresh the pair ping so the link stays alive while both pages are open
        if (isset($state[$who])) {
            $state[$who]['ts'] = time();
        } else {
            $state[$who] = [
                'ts' => time(),
                'ip' => $_SERVER['REMOTE_ADDR'],
                'ua' => substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 100)
            ];
        }
        $state[$who . '_status'] = [
            'blood' => isset($input['blood']) ? (float)$input['blood'] : 0,
            'alive' => isset($input['alive']) ? (bool)$input['alive'] : false,
            'mood'  => isset($input['mood'])  ? $input['mood'] : 'unknown',
            'ts'    => time()
        ];
        file_put_contents($file, json_encode($state));
        echo json_encode(['ok' => true]);
        exit;
    }

    if ($action === 'poll') {
        // COMBINED: report status + check other + consume notes — ONE atomic read/write
        // 1. Update own ping + status
        if (isset($state[$who])) {
            $state[$who]['ts'] = time();
        } else {
            $state[$who] = [
                'ts' => time(),
                'ip' => $_SERVER['REMOTE_ADDR'],
                'ua' => substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 100)
            ];
        }
        $state[$who . '_status'] = [
            'blood' => isset($input['blood']) ? (float)$input['blood'] : 0,
            'alive' => isset($input['alive']) ? (bool)$input['alive'] : false,
            'mood'  => isset($input['mood'])  ? $input['mood'] : 'unknown',
            'ts'    => time()
        ];

        // 2. Check pair state
        $other = $who === 'boy' ? 'girl' : 'boy';
        $otherPing = isset($state[$other]) ? $state[$other] : null;
        $myPing    = $state[$who];
        $otherAlive = $otherPing && (time() - $otherPing['ts']) < 120;
        $myAlive    = (time() - $myPing['ts']) < 120;
        $paired     = $otherAlive && $myAlive;

        if ($paired && !isset($state['paired_at'])) {
            $state['paired_at'] = time();
        }

        // 3. Other's status
        $otherStatus = isset($state[$other . '_status']) ? $state[$other . '_status'] : null;
        $statusFresh = $otherStatus && (time() - $otherStatus['ts']) < 30;

        // 4. Consume notes from the OTHER creature
        $pendingNotes = [];
        if ($paired && isset($state['notes'])) {
            $now = microtime(true);
            $remaining = [];
            foreach ($state['notes'] as $note) {
                if ($note['from'] === $other && ($now - $note['ts']) < 10) {
                    $pendingNotes[] = $note;
                } else if ($note['from'] !== $other) {
                    $remaining[] = $note;
                }
            }
            $state['notes'] = $remaining;
        }

        // 5. Check for revive signal (girl only)
        $revive = null;
        if ($who === 'girl' && isset($state['revive']) && (time() - $state['revive']['ts']) < 30) {
            $revive = $state['revive'];
            unset($state['revive']);
        }

        // 5b. Check for anger signal from the OTHER creature
        $anger = null;
        if (isset($state['anger']) && $state['anger']['from'] === $other && (time() - $state['anger']['ts']) < 5) {
            $anger = $state['anger'];
            unset($state['anger']);
        }

        // 6. Single atomic write
        file_put_contents($file, json_encode($state));

        echo json_encode([
            'ok'           => true,
            'paired'       => $paired,
            'other'        => $other,
            'other_ping'   => $otherPing ? (time() - $otherPing['ts']) : null,
            'other_status' => $statusFresh ? $otherStatus : null,
            'revive'       => $revive,
            'paired_at'    => isset($state['paired_at']) ? $state['paired_at'] : null,
            'notes'        => $pendingNotes,
            'anger'        => $anger
        ]);
        exit;
    }

    echo json_encode(['error' => 'unknown action']);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $who = isset($_GET['check']) ? $_GET['check'] : '';
    if ($who !== 'boy' && $who !== 'girl') {
        echo json_encode(['error' => 'invalid']);
        exit;
    }

    $other = $who === 'boy' ? 'girl' : 'boy';
    $otherPing = isset($state[$other]) ? $state[$other] : null;
    $myPing    = isset($state[$who])   ? $state[$who]   : null;

    // Paired = both pinged within 120 seconds
    $otherAlive = $otherPing && (time() - $otherPing['ts']) < 120;
    $myAlive    = $myPing    && (time() - $myPing['ts'])    < 120;
    $paired     = $otherAlive && $myAlive;

    // Other creature's status
    $otherStatus = isset($state[$other . '_status']) ? $state[$other . '_status'] : null;
    $statusFresh = $otherStatus && (time() - $otherStatus['ts']) < 30;

    // Check for revive signal (for girl only)
    $revive = null;
    if ($who === 'girl' && isset($state['revive']) && (time() - $state['revive']['ts']) < 30) {
        $revive = $state['revive'];
        // Clear it after reading
        unset($state['revive']);
        file_put_contents($file, json_encode($state));
    }

    // Collect notes from the OTHER creature for this one to play
    $pendingNotes = [];
    if ($paired && isset($state['notes'])) {
        $now = microtime(true);
        $remaining = [];
        foreach ($state['notes'] as $note) {
            if ($note['from'] === $other && ($now - $note['ts']) < 10) {
                $pendingNotes[] = $note;
            } else if ($note['from'] !== $other) {
                $remaining[] = $note; // keep own notes for the other to read
            }
            // else: consumed — drop it
        }
        $state['notes'] = $remaining;
        if (count($pendingNotes) > 0) {
            file_put_contents($file, json_encode($state));
        }
    }

    echo json_encode([
        'paired'       => $paired,
        'other'        => $other,
        'other_ping'   => $otherPing ? (time() - $otherPing['ts']) : null,
        'other_status' => $statusFresh ? $otherStatus : null,
        'revive'       => $revive,
        'paired_at'    => isset($state['paired_at']) ? $state['paired_at'] : null,
        'notes'        => $pendingNotes
    ]);
    exit;
}
