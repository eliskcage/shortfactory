<?php
/**
 * ShortFactory — Idea Factory smart contract evaluator
 * POSTs to xAI Grok API, returns structured evaluation JSON
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$idea     = trim($_POST['idea']     ?? '');
$category = trim($_POST['category'] ?? 'digital');
$funding  = floatval($_POST['funding'] ?? 0);

if (!$idea) die(json_encode(['ok'=>false,'error'=>'No idea submitted']));

$keyFile = '/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/.api_key';
$apiKey  = trim(@file_get_contents($keyFile));
if (!$apiKey) die(json_encode(['ok'=>false,'error'=>'API key missing']));

$systemPrompt = 'You are the ShortFactory Idea Factory — the world\'s first AI patent office and smart contract evaluator. You assess ideas for commercial viability on a platform that builds digital products using AI (one human + Claude AI builds everything). You have a dry, sharp wit, but are fair and brutally honest. The platform takes 50% and the idea creator takes 50% of all revenue generated. Always return ONLY valid JSON — no prose, no markdown fences.';

$userPrompt = 'Evaluate this idea submission for the ShortFactory platform:

IDEA: ' . $idea . '
CATEGORY: ' . $category . '
FUNDING COMMITTED: £' . number_format($funding, 2) . '

Return JSON with exactly these fields:
{
  "score": <integer 0-100 — commercial viability>,
  "verdict": "<one of: APPROVED | NEGOTIATION_REQUIRED | DECLINED>",
  "verdict_reason": "<one punchy sentence, max 12 words>",
  "roi_estimate": "<e.g. £500–£2,000/mo after 6 months>",
  "royalty_rate": <integer 5-25 — % of revenue to creator>,
  "build_time": "<e.g. 2 weeks | 3 days | 1 month>",
  "category_tag": "<e.g. DIGITAL | GAME | AI_TOOL | MARKETPLACE | DATA | CONTENT>",
  "grok_note": "<Grok\'s personal one-liner comment on the idea — witty, max 15 words>",
  "funded_override": <true if funding >= 50, else false — funded ideas cannot be declined>
}

Rules:
- If funded >= £50 the verdict MUST be APPROVED (set funded_override true).
- If score < 40 and not funded, verdict = DECLINED.
- If score 40-59 and not funded, verdict = NEGOTIATION_REQUIRED.
- If score >= 60 and not funded, verdict = APPROVED.
- royalty_rate should be higher for better ideas (score 80+ = 20-25%, score 60-79 = 15-19%, score 40-59 = 10-14%, below = 5-9%).';

$payload = json_encode([
    'model'    => 'grok-3-latest',
    'messages' => [
        ['role'=>'system','content'=>$systemPrompt],
        ['role'=>'user','content'=>$userPrompt]
    ],
    'temperature' => 0.7
]);

$ch = curl_init('https://api.x.ai/v1/chat/completions');
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $payload,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 20,
    CURLOPT_HTTPHEADER     => [
        'Authorization: Bearer ' . $apiKey,
        'Content-Type: application/json',
    ]
]);
$raw  = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($code !== 200) {
    die(json_encode(['ok'=>false,'error'=>'Grok API error','code'=>$code]));
}

$resp = json_decode($raw, true);
$content = $resp['choices'][0]['message']['content'] ?? '';

// Strip any markdown fences just in case
$content = preg_replace('/^```(?:json)?\s*/','', trim($content));
$content = preg_replace('/\s*```$/','',$content);

$eval = json_decode($content, true);
if (!$eval) {
    die(json_encode(['ok'=>false,'error'=>'Parse error','raw'=>substr($content,0,200)]));
}

// Generate contract hash
$contractId = 'SF-' . strtoupper(substr(md5($idea . time()), 0, 4)) . '-' . strtoupper(substr(md5($apiKey . $idea), 0, 4));
$timestamp  = date('Y-m-d H:i:s') . ' UTC';

echo json_encode([
    'ok'          => true,
    'contract_id' => $contractId,
    'timestamp'   => $timestamp,
    'idea'        => $idea,
    'funding'     => $funding,
    'eval'        => $eval
]);
