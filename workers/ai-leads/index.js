/**
 * ai-leads.shortfactory.shop
 * Lead capture, enrichment, and outreach pipeline.
 *
 * POST /submit   {name, email, company, url, notes}  → store lead (plaintext, B2B)
 * POST /enrich   {lead_id}  → AI generates company profile + pitch angle
 * POST /draft    {lead_id}  → AI writes personalized outreach email
 * GET  /leads    ?status=new|contacted|converted  → list leads
 * GET  /ping
 *
 * VAULT (Satoshi-encrypted apprentice applications — zero plaintext stored):
 * POST /vault    {name, email, domain, work, vision, link, source} → encrypt, verify, store shape
 * GET  /shapes   → public list of {id, seed, submitted_at} for glyph rendering
 * POST /reveal   {id, secret} → Dan-only decrypt + return plaintext
 */

// ── SATOSHI CIPHER (Vigenere ASCII 32-126) ────────────────────────────────────
const SAT_KEY = 'SKYDADDY';
const LO = 32, HI = 126, RANGE = 95;

function satEnc(text, key) {
  let out = '';
  for (let i = 0; i < text.length; i++) {
    const c = text.charCodeAt(i);
    if (c < LO || c > HI) { out += '?'; continue; } // strip non-printable
    const k = key.charCodeAt(i % key.length) - LO;
    out += String.fromCharCode(LO + (c - LO + k) % RANGE);
  }
  return out;
}

function satDec(text, key) {
  let out = '';
  for (let i = 0; i < text.length; i++) {
    const c = text.charCodeAt(i);
    if (c < LO || c > HI) { out += '?'; continue; }
    const k = key.charCodeAt(i % key.length) - LO;
    out += String.fromCharCode(LO + (c - LO - k + RANGE * 100) % RANGE);
  }
  return out;
}

// ── SCRAMBLE (Fisher-Yates with seeded xorshift) ──────────────────────────────
function hashStr(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = Math.imul(31, h) + s.charCodeAt(i) | 0;
  return h >>> 0;
}

function xorshift(seed) {
  let s = (seed >>> 0) || 0xdeadbeef;
  return function() { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return (s >>> 0) / 4294967296; };
}

function scramble(text, salt) {
  const rng = xorshift(hashStr(salt));
  const arr = text.split('');
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr.join('');
}

function unscramble(text, salt) {
  const rng = xorshift(hashStr(salt));
  const arr = text.split('');
  const swaps = [];
  for (let i = arr.length - 1; i > 0; i--) swaps.push([i, Math.floor(rng() * (i + 1))]);
  for (let k = swaps.length - 1; k >= 0; k--) {
    const [i, j] = swaps[k]; [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr.join('');
}

// ── VAULT SCHEMA ──────────────────────────────────────────────────────────────
const VAULT_SCHEMA = 'CREATE TABLE IF NOT EXISTS vault (id INTEGER PRIMARY KEY AUTOINCREMENT, blob TEXT NOT NULL, salt TEXT NOT NULL, seed INTEGER NOT NULL, verified INTEGER DEFAULT 0, submitted_at INTEGER DEFAULT (unixepoch()))';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

const GATEWAY = 'https://gateway.ai.cloudflare.com/v1/2783e78b87a0ffd54f8e91017e2695b7/default/compat/chat/completions';
const MODEL = 'workers-ai/@cf/meta/llama-3.3-70b-instruct-fp8-fast';

async function llm(messages, token, max_tokens = 400) {
  const r = await fetch(GATEWAY, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ model: MODEL, messages, max_tokens }),
    signal: AbortSignal.timeout(15000),
  });
  if (!r.ok) throw new Error(`llm ${r.status}`);
  const d = await r.json();
  return d.choices?.[0]?.message?.content || '';
}

const SCHEMA = `CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  company TEXT,
  url TEXT,
  notes TEXT,
  status TEXT DEFAULT 'new',
  score INTEGER DEFAULT 0,
  profile TEXT,
  pitch TEXT,
  email_draft TEXT,
  created_at INTEGER DEFAULT (unixepoch()),
  contacted_at INTEGER,
  UNIQUE(email)
);`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
    const json = (d, s = 200) => new Response(JSON.stringify(d), { status: s, headers: CORS });

    // Init DB schema
    try { await env.DB.exec(SCHEMA); } catch (_) {}

    if (url.pathname === '/ping') return json({ status: 'ok', version: '1.0', service: 'ai-leads' });

    // ── POST /submit ──────────────────────────────────────────
    if (url.pathname === '/submit' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      const { name, email, company = '', url: leadUrl = '', notes = '' } = body;
      if (!name || !email) return json({ error: 'name and email required' }, 400);

      try {
        const result = await env.DB.prepare(
          'INSERT OR IGNORE INTO leads (name, email, company, url, notes) VALUES (?, ?, ?, ?, ?)'
        ).bind(name, email, company, leadUrl, notes).run();

        const lead = await env.DB.prepare('SELECT * FROM leads WHERE email = ?').bind(email).first();
        return json({ ok: true, lead_id: lead.id, message: 'Lead captured' });
      } catch (e) {
        return json({ ok: false, error: e.message });
      }
    }

    // ── POST /enrich ──────────────────────────────────────────
    if (url.pathname === '/enrich' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      const lead = await env.DB.prepare('SELECT * FROM leads WHERE id = ?').bind(body.lead_id).first();
      if (!lead) return json({ error: 'lead not found' }, 404);

      const prompt = `You are a B2B sales intelligence analyst for ShortFactory — an AI-powered creative platform that automates YouTube Shorts, ad creation, and AI creature experiences.

Analyse this prospect and write a sales intelligence brief:
Company: ${lead.company || 'Unknown'}
Website: ${lead.url || 'Not provided'}
Contact: ${lead.name} (${lead.email})
Notes: ${lead.notes || 'None'}

Return a JSON object with:
{
  "score": 1-10 (fit score for ShortFactory services),
  "profile": "2-3 sentence company description",
  "pain_points": ["pain1", "pain2", "pain3"],
  "best_service": "which ShortFactory service fits best",
  "pitch_angle": "one sentence custom pitch hook"
}
Return ONLY valid JSON.`;

      try {
        const raw = await llm([{ role: 'user', content: prompt }], env.CF_AIG_TOKEN, 500);
        const parsed = JSON.parse(raw.replace(/```json\n?|\n?```/g, '').trim());

        await env.DB.prepare(
          'UPDATE leads SET profile = ?, score = ?, pitch = ? WHERE id = ?'
        ).bind(
          parsed.profile || '',
          parsed.score || 5,
          JSON.stringify({ pain_points: parsed.pain_points, best_service: parsed.best_service, pitch_angle: parsed.pitch_angle }),
          body.lead_id
        ).run();

        return json({ ok: true, lead_id: body.lead_id, ...parsed });
      } catch (e) {
        return json({ ok: false, error: e.message });
      }
    }

    // ── POST /draft ───────────────────────────────────────────
    if (url.pathname === '/draft' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      const lead = await env.DB.prepare('SELECT * FROM leads WHERE id = ?').bind(body.lead_id).first();
      if (!lead) return json({ error: 'lead not found' }, 404);

      const pitch = lead.pitch ? JSON.parse(lead.pitch) : {};

      const prompt = `Write a short, punchy cold outreach email from Dan Chipchase at ShortFactory.

Target: ${lead.name} at ${lead.company || 'their company'} (${lead.email})
Our pitch angle: ${pitch.pitch_angle || 'AI-powered video advertising that creates itself'}
Their pain points: ${(pitch.pain_points || []).join(', ') || 'manual content creation, high ad costs'}
Best service for them: ${pitch.best_service || 'Imaginator — automated YouTube Shorts'}

Rules:
- Subject line first (prefix with "SUBJECT: ")
- Max 120 words in body
- Conversational, not corporate
- One specific call to action (book 15min call or try the tool free)
- Sign off as Dan, ShortFactory
- No fluff, no filler`;

      try {
        const draft = await llm([{ role: 'user', content: prompt }], env.CF_AIG_TOKEN, 300);
        await env.DB.prepare('UPDATE leads SET email_draft = ? WHERE id = ?').bind(draft, body.lead_id).run();
        return json({ ok: true, lead_id: body.lead_id, draft });
      } catch (e) {
        return json({ ok: false, error: e.message });
      }
    }

    // ── GET /leads ────────────────────────────────────────────
    if (url.pathname === '/leads' && request.method === 'GET') {
      const status = url.searchParams.get('status') || 'new';
      const limit = Math.min(50, parseInt(url.searchParams.get('limit') || '20'));
      try {
        const rows = await env.DB.prepare(
          'SELECT id, name, email, company, url, status, score, profile, created_at FROM leads WHERE status = ? ORDER BY score DESC, created_at DESC LIMIT ?'
        ).bind(status, limit).all();
        return json({ ok: true, count: rows.results.length, leads: rows.results });
      } catch (e) {
        return json({ ok: false, error: e.message });
      }
    }

    // ── POST /mark ────────────────────────────────────────────
    if (url.pathname === '/mark' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      await env.DB.prepare('UPDATE leads SET status = ?, contacted_at = unixepoch() WHERE id = ?')
        .bind(body.status || 'contacted', body.lead_id).run();
      return json({ ok: true });
    }

    // ── POST /vault ─────────────────────────────────────────────────────────
    if (url.pathname === '/vault' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      if (!body.email) return json({ error: 'email required' }, 400);

      // Strip to ASCII 32-126 only, serialize
      const plaintext = JSON.stringify(body).replace(/[^\x20-\x7e]/g, '?');

      // Random 8-char hex salt
      const saltBytes = new Uint8Array(4);
      crypto.getRandomValues(saltBytes);
      const salt = Array.from(saltBytes).map(b => b.toString(16).padStart(2,'0')).join('');

      // Full key = SKYDADDY + salt (extra entropy layer)
      const fullKey = SAT_KEY + salt;

      // Scramble then Satoshi-encrypt
      const scrambled = scramble(plaintext, salt);
      const blob = satEnc(scrambled, fullKey);

      // ── VERIFY ROUND-TRIP BEFORE STORING ──────────────────────────────────
      const roundtrip = unscramble(satDec(blob, fullKey), salt);
      if (roundtrip !== plaintext) {
        return json({ error: 'vault verification failed — plaintext NOT stored', verified: false }, 500);
      }

      // Derive genome seed from encrypted blob (never from plaintext)
      const seed = hashStr(blob);

      try {
        await env.DB.prepare(VAULT_SCHEMA).run();
        await env.DB.prepare(
          'INSERT INTO vault (blob, salt, seed, verified) VALUES (?, ?, ?, 1)'
        ).bind(blob, salt, seed).run();
      } catch(e) {
        return json({ ok: false, error: e.message });
      }

      // Return ONLY the shape data — no plaintext, no salt
      return json({ ok: true, seed, verified: true, blob_preview: blob.substring(0, 16) + '...' });
    }

    // ── GET /shapes ──────────────────────────────────────────────────────────
    if (url.pathname === '/shapes' && request.method === 'GET') {
      const limit = Math.min(50, parseInt(url.searchParams.get('limit') || '20'));
      try {
        await env.DB.prepare(VAULT_SCHEMA).run();
        const rows = await env.DB.prepare(
          'SELECT id, seed, submitted_at FROM vault WHERE verified = 1 ORDER BY submitted_at DESC LIMIT ?'
        ).bind(limit).all();
        return json({ ok: true, count: rows.results.length, shapes: rows.results });
      } catch(e) {
        return json({ ok: false, error: e.message });
      }
    }

    // ── POST /reveal (Dan-only — requires secret) ────────────────────────────
    if (url.pathname === '/reveal' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      if (body.secret !== 'SKYDADDY_REVEAL_9x') return json({ error: 'unauthorized' }, 401);
      if (!body.id) return json({ error: 'id required' }, 400);

      try {
        await env.DB.prepare(VAULT_SCHEMA).run();
        const row = await env.DB.prepare('SELECT blob, salt FROM vault WHERE id = ?').bind(body.id).first();
        if (!row) return json({ error: 'not found' }, 404);

        const fullKey = SAT_KEY + row.salt;
        const decrypted = satDec(row.blob, fullKey);
        const plaintext = unscramble(decrypted, row.salt);

        let data;
        try { data = JSON.parse(plaintext); } catch { data = plaintext; }
        return json({ ok: true, id: body.id, data });
      } catch(e) {
        return json({ ok: false, error: e.message });
      }
    }

    return json({ error: 'not found' }, 404);
  },
};
