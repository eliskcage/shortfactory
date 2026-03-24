/**
 * ai-image.shortfactory.shop
 * Text-to-image at the edge. Powers Imaginator + game art.
 * Model: @cf/black-forest-labs/flux-1-schnell
 *
 * POST /generate  {prompt, steps?}  → PNG binary
 * POST /json      {prompt, steps?}  → {ok, image_b64}
 * GET  /ping
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

const MODEL = '@cf/black-forest-labs/flux-1-schnell';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS_HEADERS });

    if (url.pathname === '/ping') {
      return new Response(JSON.stringify({ status: 'ok', model: 'flux-1-schnell', version: '2.0' }), {
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    }

    if ((url.pathname === '/generate' || url.pathname === '/json') && request.method === 'POST') {
      let body;
      try { body = await request.json(); } catch {
        return new Response(JSON.stringify({ error: 'invalid json' }), { status: 400, headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' } });
      }

      const prompt = body.prompt || 'abstract digital art';
      const steps  = Math.min(8, Math.max(1, body.steps || 4));

      try {
        const result = await env.AI.run(MODEL, { prompt, num_steps: steps });

        // result is a ReadableStream of PNG bytes
        const blob = await new Response(result).arrayBuffer();

        if (url.pathname === '/json') {
          const b64 = btoa(String.fromCharCode(...new Uint8Array(blob)));
          return new Response(JSON.stringify({ ok: true, image: b64, image_b64: 'data:image/png;base64,' + b64 }), {
            headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
          });
        }

        return new Response(blob, {
          headers: { ...CORS_HEADERS, 'Content-Type': 'image/png', 'Content-Length': String(blob.byteLength) }
        });

      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: e.message }), {
          status: 500, headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
        });
      }
    }

    return new Response(JSON.stringify({ error: 'not found' }), { status: 404, headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' } });
  }
};
