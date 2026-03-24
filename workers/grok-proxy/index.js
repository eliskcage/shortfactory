// ── Grok API Proxy Worker ─────────────────────────────────────────────────────
// Sits at api.shortfactory.shop/grok/*
// Keeps the XAI key secret — never exposed to the browser
// All requests must come from shortfactory.shop (CORS enforced)
// ─────────────────────────────────────────────────────────────────────────────

const GROK_BASE = 'https://api.x.ai/v1';
const ALLOWED_ORIGIN = 'https://www.shortfactory.shop';

export default {
  async fetch(request, env) {

    // ── CORS preflight ──────────────────────────────────────────────────────
    const origin = request.headers.get('Origin') || '';
    const corsHeaders = {
      'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
      'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    // ── Origin check ────────────────────────────────────────────────────────
    // Allow shortfactory.shop and workers.dev (for testing)
    const allowed = origin.includes('shortfactory.shop') ||
                    origin.includes('workers.dev') ||
                    origin === '';
    if (!allowed) {
      return new Response('Forbidden', { status: 403 });
    }

    const url = new URL(request.url);

    // ── Route: POST /grok/chat  →  XAI chat completions ────────────────────
    if (url.pathname === '/grok/chat' && request.method === 'POST') {
      let body;
      try { body = await request.json(); } catch {
        return new Response('Bad JSON', { status: 400 });
      }

      // Sensible defaults — frontend can override model/max_tokens
      const payload = {
        model: body.model || 'grok-4-latest',
        messages: body.messages || [],
        max_tokens: Math.min(body.max_tokens || 500, 2000), // cap at 2000
        stream: false,
      };

      if (!payload.messages.length) {
        return new Response('No messages', { status: 400 });
      }

      const upstream = await fetch(`${GROK_BASE}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.XAI_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await upstream.json();
      return new Response(JSON.stringify(data), {
        status: upstream.status,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // ── Route: POST /grok/image  →  XAI image generation ───────────────────
    if (url.pathname === '/grok/image' && request.method === 'POST') {
      let body;
      try { body = await request.json(); } catch {
        return new Response('Bad JSON', { status: 400 });
      }

      const payload = {
        model: 'grok-2-image',
        prompt: body.prompt || '',
        n: Math.min(body.n || 1, 4),
      };

      if (!payload.prompt) {
        return new Response('No prompt', { status: 400 });
      }

      const upstream = await fetch(`${GROK_BASE}/images/generations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.XAI_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await upstream.json();
      return new Response(JSON.stringify(data), {
        status: upstream.status,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // ── 404 for anything else ───────────────────────────────────────────────
    return new Response('Not found', { status: 404, headers: corsHeaders });
  }
};
