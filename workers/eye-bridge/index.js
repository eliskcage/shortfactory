/**
 * Eye Bridge Worker — edge replacement for eye_bridge.py
 * Uses Cloudflare Workers AI (@cf/microsoft/resnet-50) for real image classification.
 *
 * Routes:
 *   GET  /ping      → {status, version, engine}
 *   POST /classify  → {frame, mode, time} → {objects, focus, frames}
 *   POST /learn     → {label, signal}     → Hebbian stub
 *   GET  /          → redirect to eye.html
 *   GET  /favicon.ico → redirect to eye.html
 */

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

const MODE_VOCAB = {
  qubit:       ['superposition','entangle','wave','coherent','phase','tunnel','observe','collapse'],
  singularity: ['horizon','consume','rupture','singular','infinite','crush','devour','escape'],
};

function cleanLabel(raw) {
  return raw.toLowerCase()
    .replace(/,.*$/, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .trim().split(/\s+/).slice(0, 2).join('_').substring(0, 20);
}

function decodeFrame(b64) {
  const data = b64.includes(',') ? b64.split(',')[1] : b64;
  const bin  = atob(data);
  const buf  = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  return buf;
}

function estimateFocus(bytes) {
  const step = Math.max(1, Math.floor(bytes.length / 64));
  const grid = new Float32Array(64);
  for (let i = 0; i < 64; i++) grid[i] = (bytes[i * step] || 128) / 255;
  let cx = 0, cy = 0, n = 0;
  for (let i = 0; i < 64; i++) {
    if (grid[i] > 0.5) {
      cx += ((i % 8) / 7) * 2 - 1;
      cy += (Math.floor(i / 8) / 7) * 2 - 1;
      n++;
    }
  }
  if (!n) return { x: 0, y: 0, locked: false };
  cx /= n; cy /= n;
  return { x: parseFloat(cx.toFixed(3)), y: parseFloat(cy.toFixed(3)), locked: Math.sqrt(cx*cx+cy*cy) < 0.5 };
}

let frameCount = 0;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
    const json = (d, s=200) => new Response(JSON.stringify(d), { status: s, headers: CORS });

    // Root and favicon → redirect to eye.html
    if (url.pathname === '/' || url.pathname === '/favicon.ico') {
      return Response.redirect('https://www.shortfactory.shop/alive/eye.html', 302);
    }

    if (url.pathname === '/ping') {
      return json({ status: 'ok', version: '2.0', engine: 'workers-ai', frames: frameCount });
    }

    if (url.pathname === '/classify' && request.method === 'POST') {
      let body;
      try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      const frameB64 = body.frame || '';
      const mode     = body.mode  || 'qubit';
      if (!frameB64) return json({ error: 'no frame' }, 400);

      let objects = [], focus = { x: 0, y: 0, locked: false };
      try {
        const bytes = decodeFrame(frameB64);
        focus = estimateFocus(bytes);
        const result = await env.AI.run('@cf/microsoft/resnet-50', { image: Array.from(bytes) });
        objects = (Array.isArray(result) ? result : result?.result || [])
          .slice(0, 4)
          .map(item => ({ label: cleanLabel(item.label || item.class || 'field'), confidence: parseFloat((item.score || 0.5).toFixed(2)) }))
          .filter(o => o.label.length > 1);
      } catch {
        objects = [{ label: 'field', confidence: 0.60 }, { label: 'presence', confidence: 0.55 }];
      }

      const pool = MODE_VOCAB[mode] || MODE_VOCAB.qubit;
      objects.push({ label: pool[Math.floor(Math.random() * pool.length)], confidence: 0.65 });
      frameCount++;
      return json({ objects, focus, frames: frameCount });
    }

    if (url.pathname === '/learn' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { body = {}; }
      return json({ ok: true, label: body.label, signal: body.signal });
    }

    return json({ error: 'not found' }, 404);
  },
};
