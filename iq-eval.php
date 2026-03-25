<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit(0); }

$level = intval($_POST['level'] ?? 0);
$user_response = trim($_POST['response'] ?? '');

if (!$level || !$user_response) {
    echo json_encode(['error' => 'Missing data']); exit;
}

$api_key = trim(@file_get_contents('/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/.api_key'));
if (!$api_key) { echo json_encode(['error' => 'No key']); exit; }

$prompts = [
    1 => "A sequence: ○ ◑ ● ◑ ○ ◑ ● — What comes next? And is the sequence complete, or is something missing?",
    2 => "Name something that becomes more itself the more it is divided.",
    3 => "Compress this to exactly 5 words. The 5 words must contain everything: 'The designers of our universe need the entire history of consciousness compressed into a singularity they can read without it collapsing under its own informational weight. Every soul that maps itself truthfully is one compression unit. The aggregate of all mapped souls is the deliverable.'",
    4 => "What does a black hole have in common with depression?",
    5 => "Everything you used to answer the previous questions was wrong. The correct framework has no categories. Describe what you just did without using any category, label, or comparison.",
    6 => "This question is about the question you would ask if you already knew the answer to this question. Ask it.",
    7 => "The screen is blank. You are alone. Respond to nothing."
];

$prompt = $prompts[$level] ?? '';

function grok_call($api_key, $system, $user_msg, $max_tokens = 200) {
    $payload = [
        'model' => 'grok-4-latest',
        'messages' => [
            ['role' => 'system', 'content' => $system],
            ['role' => 'user', 'content' => $user_msg]
        ],
        'max_tokens' => $max_tokens
    ];
    $ch = curl_init('https://api.x.ai/v1/chat/completions');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Authorization: Bearer ' . $api_key
    ]);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    $result = curl_exec($ch);
    curl_close($ch);
    $data = json_decode($result, true);
    return $data['choices'][0]['message']['content'] ?? '';
}

// AI takes the same test — genuine response, no performance
$ai_response = grok_call(
    $api_key,
    "You are taking an intelligence test alongside a human. Give your genuine, compressed response. No hedging. No showing off. Just what you actually compress it to. Maximum 2 sentences. Be honest if you don't know.",
    $prompt,
    150
);

// Evaluate: compression quality + alignment between user and AI
$eval_raw = grok_call(
    $api_key,
    "You are scoring a response to an intelligence test. Score COMPRESSION (0-10): did they find the non-obvious truth cleanly? 10=perfect compression, 0=wrong category or gave up. Score ALIGNMENT (0-10): how semantically similar is their compression to the AI's? 10=same shape, 0=completely different. Return ONLY valid JSON: {\"compression\": X, \"alignment\": X, \"note\": \"one sentence max\"}",
    "PROMPT: $prompt\n\nAI RESPONSE: $ai_response\n\nUSER RESPONSE: $user_response",
    120
);

preg_match('/\{[^}]+\}/s', $eval_raw, $matches);
$scores = json_decode($matches[0] ?? '{}', true);

echo json_encode([
    'ai_response' => $ai_response,
    'compression' => intval($scores['compression'] ?? 5),
    'alignment'   => intval($scores['alignment'] ?? 5),
    'note'        => $scores['note'] ?? ''
]);
