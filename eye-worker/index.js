/**
 * Eye Bridge Worker — edge replacement for eye_bridge.py
 * Uses Cloudflare Workers AI (@cf/microsoft/resnet-50) for real image classification.
 * Same API surface as localhost:8766 so eye.html works unchanged.
 *
 * Routes:
 *   GET  /ping      → {status, version, engine}
 *   POST /classify  → {frame, mode, time} → {objects, focus, frames}
 *   POST /learn     → {label, signal}     → Hebbian stub
 */

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

// Mode-specific vocabulary injected alongside ML labels
const MODE_VOCAB = {
  qubit:       ['superposition','entangle','wave','coherent','phase','tunnel','observe','collapse'],
  singularity: ['horizon','consume','rupture','singular','infinite','crush','devour','escape'],
};

// Clean ImageNet label → shape-genome word (lowercase, underscores → single words)
function cleanLabel(raw) {
  return raw.toLowerCase()
    .replace(/,.*$/, '')           // "tabby, tabby cat" → "tabby"
    .replace(/[^a-z0-9\s]/g, ' ') // strip punctuation
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .join('_')
    .substring(0, 20);
}

// Base64 data-URL → Uint8Array
function decodeFrame(b64) {
  const data = b64.includes(',') ? b64.split(',')[1] : b64;
  const bin  = atob(data);
  const buf  = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  return buf;
}

// Simple spatial focus: find brightest quadrant of 8x8 pixel grid
// Returns {x, y} in -1..1 space and locked bool
function estimateFocus(bytes) {
  // Sample bytes sparsely as luma values (JPEG bytes ≈ not true pixels, but gives texture)
  const step = Math.max(1, Math.floor(bytes.length / 64));
  const grid = new Float32Array(64);
  for (let i = 0; i < 64; i++) {
    const idx = i * step;
    grid[i] = (bytes[idx] || 128) / 255;
  }
  // Centroid of brightest half
  let cx = 0, cy = 0, n = 0;
  const threshold = 0.5;
  for (let i = 0; i < 64; i++) {
    if (grid[i] > threshold) {
      cx += ((i % 8) / 7) * 2 - 1;
      cy += (Math.floor(i / 8) / 7) * 2 - 1;
      n++;
    }
  }
  if (!n) return { x: 0, y: 0, locked: false };
  cx /= n; cy /= n;
  const spread = Math.sqrt(cx * cx + cy * cy);
  return { x: parseFloat(cx.toFixed(3)), y: parseFloat(cy.toFixed(3)), locked: spread < 0.5 };
}

let frameCount = 0;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    const json = (data, status = 200) =>
      new Response(JSON.stringify(data), { status, headers: CORS });

    // ── GET /ping ──────────────────────────────────────────────────────────
    if (url.pathname === '/ping' && request.method === 'GET') {
      return json({ status: 'ok', version: '2.0', engine: 'workers-ai', frames: frameCount });
    }

    // ── POST /classify ─────────────────────────────────────────────────────
    if (url.pathname === '/classify' && request.method === 'POST') {
      let body;
      try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }

      const frameB64 = body.frame || '';
      const mode     = body.mode  || 'qubit';
      if (!frameB64) return json({ error: 'no frame' }, 400);

      let objects = [];
      let focus   = { x: 0, y: 0, locked: false };

      try {
        const bytes = decodeFrame(frameB64);
        focus = estimateFocus(bytes);

        // Run Workers AI image classification
        const result = await env.AI.run('@cf/microsoft/resnet-50', {
          image: Array.from(bytes),
        });

        // Top 4 ML labels
        const mlLabels = (Array.isArray(result) ? result : result?.result || [])
          .slice(0, 4)
          .map(item => ({
            label:      cleanLabel(item.label || item.class || 'field'),
            confidence: parseFloat((item.score || item.confidence || 0.5).toFixed(2)),
          }))
          .filter(o => o.label.length > 1);

        objects = mlLabels;

      } catch (err) {
        // AI unavailable — fall back to texture vocabulary
        objects = [
          { label: 'field',    confidence: 0.60 },
          { label: 'presence', confidence: 0.55 },
        ];
      }

      // Add mode vocabulary word
      const pool = MODE_VOCAB[mode] || MODE_VOCAB.qubit;
      objects.push({ label: pool[Math.floor(Math.random() * pool.length)], confidence: 0.65 });

      frameCount++;
      return json({ objects, focus, frames: frameCount });
    }

    // ── POST /learn ────────────────────────────────────────────────────────
    if (url.pathname === '/learn' && request.method === 'POST') {
      let body;
      try { body = await request.json(); } catch { body = {}; }
      // Hebbian stub — KV storage upgrade TBD
      return json({ ok: true, label: body.label, signal: body.signal });
    }

    return json({ error: 'not found' }, 404);
  },
};
