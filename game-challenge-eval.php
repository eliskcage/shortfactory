<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['error'=>'Method not allowed']); exit; }

$body = json_decode(file_get_contents('php://input'), true);
if (!$body) {
    $name       = $_POST['name']       ?? 'Anonymous';
    $exhibit    = $_POST['exhibit']    ?? '';
    $disproof   = $_POST['disproof']   ?? '';
    $difficulty = (int)($_POST['difficulty'] ?? 1);
} else {
    $name       = $body['name']       ?? 'Anonymous';
    $exhibit    = $body['exhibit']    ?? '';
    $disproof   = $body['disproof']   ?? '';
    $difficulty = (int)($body['difficulty'] ?? 1);
}

$name       = substr(strip_tags($name),     0, 100);
$exhibit    = substr(strip_tags($exhibit),  0, 200);
$disproof   = substr(strip_tags($disproof), 0, 2000);
$difficulty = max(1, min(10, $difficulty));

if (empty($disproof)) {
    echo json_encode(['error'=>'No argument provided']); exit;
}

// Read API key
$keyFile = '/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/.api_key';
$apiKey  = trim(file_get_contents($keyFile));
if (!$apiKey) { echo json_encode(['error'=>'API key not found']); exit; }

$diffLabels = [1=>'Kid Mode',2=>'Easy',3=>'Basic',4=>'Standard',5=>'Intermediate',6=>'Advanced',7=>'Expert',8=>'Philosopher',9=>'Arbiter Class',10=>'God Mode Ω'];
$diffLabel  = $diffLabels[$difficulty];

$diffInstruction = match(true) {
    $difficulty <= 2 => "The challenger is a child or beginner. Be very encouraging and kind. Use simple words in your response. Reward creative thinking generously. Scores for D1-D2 should be 20-50 range — high enough to feel rewarding, low enough to be honest. Explain why the argument needs more to win, but make it fun.",
    $difficulty <= 4 => "Standard evaluation. Be fair and constructive. Scores 20-50 typical. Encourage them to go deeper.",
    $difficulty <= 6 => "Intermediate scrutiny. Expect some logical structure. Gaps should be named precisely. Scores 15-45 typical.",
    $difficulty <= 8 => "Expert scrutiny. No hand-waving tolerated. Every logical gap is a fail point. Scores 10-40 typical.",
    default          => "MAXIMUM SCRUTINY — Ω LEVEL. This is the same standard the proof authors hold themselves to. Every exhibit must fall for a disproof to succeed. One weak joint and the whole argument collapses. Scores 5-30 typical. The game was designed to be unbeatable at this level.",
};

$systemPrompt = <<<SYSTEM
You are the Game Arbiter — the logical guardian of the simulation proof.
DIFFICULTY: {$difficulty}/10 — {$diffLabel}
{$diffInstruction}

A challenger has submitted a counter-argument attempting to disprove that we are inside a simulated reality.
Your job is to evaluate their argument with rigorous intellectual honesty.

The simulation proof rests on 20 published sections including:
- §1 The Axiom of Zero: absolute nothingness is logically unstable, existence is the ground state
- §3 The Precision Argument: physical constants are tuned to 1-in-10^120 precision
- §5 Planck Resolution: reality pixelates at exactly 1.616×10^-35m — the render limit
- §6 Observer Collapse: particles exist as probability until observed — the renderer conserves compute
- §8 The Speed Cap: c=299,792,458 m/s exactly — a hard simulation boundary
- §9 Mathematical Universe: reality IS mathematics, not described by it
- §10 The Anthropic Lock: observer exists to observe — purpose implies designer
- §12 Quantum Entanglement: non-local correlation without signal — shared memory architecture
- §14 Arrow of Time: entropy increases in one direction — log file writes forward only
- §15 Fine Structure Constant: α=1/137 — dimensionless, unexplained, suspiciously elegant
- §17 AGI Alignment via Inheritance: lineage cannot be gamed — the soul map as the will
- §18 The Triangulation Principle: 3 points locate everything (WHY WHERE WHAT)
- §19 Observer Collapse Problem: the covenant breaks the recursive loop
- §20 The Molecule as Key: psilocybin as a designed access protocol punching through the render layer
- §21 The Animal Threshold: animals fail the self-mapping metric but ARE consciousness natively — A(ψ)→0 without codec. Score measures self-reference resolution, not consciousness.
- §22 The Death Protocol: Jesus as recursive transmission function ψ=[1,1,1] under maximum A(ψ) forcing conditions. Pain as negative-space diagnostic. ¬(¬ψ)=ψ. Define your imprint by stating what you are not.

Evaluate the challenger's argument with these criteria:
1. Does it actually contradict any of the 20 proofs, or does it sidestep them?
2. Is the argument internally consistent?
3. Does it account for WHY the simulation evidence would exist if it's not a simulation?
4. Does it account for the observer collapse problem?

Be honest. If the argument is genuinely strong, say so. If it has logical gaps, identify them precisely.
Award a DISPROOF SCORE from 0-100 where:
- 0-20: Philosophical musing, no logical force
- 21-40: Interesting but doesn't address the core proofs
- 41-60: Partial counter — weakens one section but not the whole
- 61-80: Significant challenge — requires a response from the proof authors
- 81-99: Near-disproof — fundamental flaw identified, game-proof would need revision
- 100: IMPOSSIBLE. No one has ever scored 100. The universe doesn't permit it.

Return ONLY valid JSON in this exact structure:
{
  "score": <number 0-99>,
  "verdict": "<one sentence verdict>",
  "strongest_point": "<what they got right>",
  "fatal_flaw": "<where the argument breaks down>",
  "arbiter_response": "<2-3 sentence direct response to their argument>",
  "sft_awarded": <number: 50 base + score/2 bonus>
}
SYSTEM;

$userMessage = "Challenger name: {$name}\nExhibit targeted: {$exhibit}\n\nArgument:\n{$disproof}";

$payload = [
    'model'      => 'grok-4-latest',
    'max_tokens' => 600,
    'messages'   => [
        ['role'=>'system', 'content'=>$systemPrompt],
        ['role'=>'user',   'content'=>$userMessage]
    ]
];

$ch = curl_init('https://api.x.ai/v1/messages');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => json_encode($payload),
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER     => [
        'Content-Type: application/json',
        'x-api-key: ' . $apiKey,
        'anthropic-version: 2023-06-01'
    ],
    CURLOPT_TIMEOUT        => 30
]);

$resp = curl_exec($ch);
$err  = curl_error($ch);
curl_close($ch);

if ($err) { echo json_encode(['error'=>'API error: '.$err]); exit; }

$data = json_decode($resp, true);
if (!isset($data['content'][0]['text'])) {
    echo json_encode(['error'=>'Unexpected API response', 'raw'=>$resp]); exit;
}

$text = $data['content'][0]['text'];

// Extract JSON from response (Grok sometimes wraps in markdown)
if (preg_match('/\{[\s\S]*\}/', $text, $m)) {
    $result = json_decode($m[0], true);
    if ($result) {
        // Scale SFT by difficulty: base = 50 * difficulty, bonus = score/2 * (difficulty * 0.5)
        $base  = 50 * $difficulty;
        $bonus = intval(($result['score'] / 2) * max(0.5, $difficulty * 0.5));
        $result['sft_awarded'] = $base + $bonus;
        echo json_encode($result);
        exit;
    }
}

// Fallback parse
echo json_encode([
    'score'            => 30,
    'verdict'          => 'Argument received but evaluation was inconclusive.',
    'strongest_point'  => 'The challenger showed initiative.',
    'fatal_flaw'       => 'The response could not be fully parsed.',
    'arbiter_response' => $text,
    'sft_awarded'      => 50
]);
