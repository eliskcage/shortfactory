/**
 * ShortFactory Card Server — Node.js + LLaMA (Ollama)
 * Port 3141 | Generates dynamic io.html card content in real time
 * Falls back to qwen2.5:0.5b if llama3.2:1b is busy
 */

const http  = require('http');
const https = require('https');

const PORT        = 3141;
const OLLAMA_HOST = 'localhost';
const OLLAMA_PORT = 11434;
const PRIMARY_MODEL   = 'llama3.2:1b';
const FALLBACK_MODEL  = 'qwen2.5:0.5b';

const SYSTEM_PROMPT = `You are the ShortFactory guide — a razor-sharp, honest AI that helps people understand and use the ShortFactory platform. ShortFactory maps the human soul as a genome (ψ=[past,now,future]), proves we are in a simulation, builds AGI companions, and makes short films. You generate mobile card content for the ShortFactory.io app. Each card is shown on a phone screen. Keep it short, direct, and real. No fluff. No corporate speak.`;

function buildPrompt(choices, context) {
  var choiceStr = choices.length ? choices.join(' → ') : 'just arrived';
  return `User journey so far: ${choiceStr}
Current context: ${context || 'general'}

Generate the next card for this user. Return ONLY a JSON object with exactly these keys:
- title: string, max 7 words, punchy and direct
- body: string, max 35 words, honest and useful
- leftLabel: string, max 3 words (left choice action)
- rightLabel: string, max 3 words (right choice action)
- leftHint: string, max 6 words (brief description of left path)
- rightHint: string, max 6 words (brief description of right path)

Make the content relevant to what the user has chosen so far. Be specific, not generic.`;
}

function ollamaGenerate(prompt, model, cb) {
  var body = JSON.stringify({
    model:  model,
    prompt: prompt,
    system: SYSTEM_PROMPT,
    stream: false,
    options: {
      temperature: 0.7,
      top_p: 0.9,
      num_predict: 200
    }
  });

  var req = http.request({
    hostname: OLLAMA_HOST,
    port:     OLLAMA_PORT,
    path:     '/api/generate',
    method:   'POST',
    headers:  { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
  }, function(res) {
    var data = '';
    res.on('data', function(chunk){ data += chunk; });
    res.on('end', function(){
      try {
        var parsed = JSON.parse(data);
        cb(null, parsed.response || '');
      } catch(e) {
        cb(e, null);
      }
    });
  });
  req.on('error', function(e){ cb(e, null); });
  req.setTimeout(15000, function(){ req.destroy(new Error('timeout')); });
  req.write(body);
  req.end();
}

function extractJSON(raw) {
  // Find first { ... } block in the response
  var match = raw.match(/\{[\s\S]*?\}/);
  if (!match) return null;
  try {
    return JSON.parse(match[0]);
  } catch(e) {
    // Try to repair common issues (trailing commas, unquoted keys)
    try {
      var fixed = match[0].replace(/,\s*}/g, '}').replace(/,\s*]/g, ']');
      return JSON.parse(fixed);
    } catch(e2) { return null; }
  }
}

function fallbackCard(choices, context) {
  // Safe static fallback if both models fail
  return {
    title:      "Keep going.",
    body:       "The map is built one choice at a time. Left or right — both paths lead somewhere real.",
    leftLabel:  "Go deeper",
    rightLabel: "Next thing",
    leftHint:   "More about this topic",
    rightHint:  "Move to something new",
    model:      "fallback",
    choices:    choices
  };
}

function generateCard(choices, context, res) {
  var prompt = buildPrompt(choices, context);

  ollamaGenerate(prompt, PRIMARY_MODEL, function(err, raw) {
    if (err || !raw) {
      console.log('Primary model failed, trying fallback:', err && err.message);
      ollamaGenerate(prompt, FALLBACK_MODEL, function(err2, raw2) {
        if (err2 || !raw2) {
          sendJSON(res, fallbackCard(choices, context));
          return;
        }
        var card = extractJSON(raw2);
        if (!card) { sendJSON(res, fallbackCard(choices, context)); return; }
        card.model   = FALLBACK_MODEL;
        card.choices = choices;
        sendJSON(res, card);
      });
      return;
    }

    var card = extractJSON(raw);
    if (!card) {
      sendJSON(res, fallbackCard(choices, context));
      return;
    }
    card.model   = PRIMARY_MODEL;
    card.choices = choices;
    sendJSON(res, card);
  });
}

function sendJSON(res, data) {
  var body = JSON.stringify(data);
  res.writeHead(200, {
    'Content-Type':                'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods':'POST, OPTIONS',
    'Access-Control-Allow-Headers':'Content-Type',
    'Cache-Control':               'no-store'
  });
  res.end(body);
}

function sendError(res, code, msg) {
  res.writeHead(code, {
    'Content-Type':                'application/json',
    'Access-Control-Allow-Origin': '*'
  });
  res.end(JSON.stringify({ error: msg }));
}

// ── SERVER ───────────────────────────────────────────────────────────────
var server = http.createServer(function(req, res) {

  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin':  '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }

  // Health check
  if (req.method === 'GET' && req.url === '/health') {
    sendJSON(res, { ok: true, models: [PRIMARY_MODEL, FALLBACK_MODEL], port: PORT });
    return;
  }

  // Card generation
  if (req.method === 'POST' && req.url === '/card') {
    var body = '';
    req.on('data', function(chunk){ body += chunk; if(body.length > 4096) req.destroy(); });
    req.on('end', function(){
      var data = {};
      try { data = JSON.parse(body); } catch(e) {}
      var choices = Array.isArray(data.choices) ? data.choices.slice(0, 20) : [];
      var context = typeof data.context === 'string' ? data.context.slice(0, 200) : '';
      console.log('[card]', new Date().toISOString(), 'choices:', choices.join('→'), '| context:', context);
      generateCard(choices, context, res);
    });
    return;
  }

  sendError(res, 404, 'Not found');
});

server.listen(PORT, '127.0.0.1', function() {
  console.log('ShortFactory Card Server running on port', PORT);
  console.log('Primary model:', PRIMARY_MODEL);
  console.log('Fallback model:', FALLBACK_MODEL);
  console.log('Health check: http://localhost:' + PORT + '/health');
});

server.on('error', function(e) {
  console.error('Server error:', e.message);
});
