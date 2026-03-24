/**
 * ai-browser.shortfactory.shop
 * Headless Chrome via Cloudflare Browser Rendering.
 * Gives Claude eyes + hands on the live site.
 *
 * POST /screenshot  {url, width?, height?}         → PNG
 * POST /click       {url, selector, waitFor?}       → {ok, screenshot_b64}
 * POST /test-game   {}                              → {ok, state, screenshot_b64}
 * POST /crawl       {url, depth?}                  → {ok, links[], errors[]}
 * GET  /ping
 */

import puppeteer from '@cloudflare/puppeteer';

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

async function getPage(env, width = 1280, height = 800) {
  const browser = await puppeteer.launch(env.BROWSER);
  const page    = await browser.newPage();
  await page.setViewport({ width, height });
  return { browser, page };
}

async function screenshot64(page) {
  const buf = await page.screenshot({ type: 'jpeg', quality: 70 });
  return 'data:image/jpeg;base64,' + Buffer.from(buf).toString('base64');
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
    const json = (d, s=200) => new Response(JSON.stringify(d), { status: s, headers: CORS });

    if (url.pathname === '/ping') return json({ status: 'ok', version: '1.0', engine: 'browser-rendering' });

    // ── POST /screenshot ──────────────────────────────────────────────────
    if (url.pathname === '/screenshot' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      const { browser, page } = await getPage(env, body.width || 1280, body.height || 800);
      try {
        await page.goto(body.url || 'https://www.shortfactory.shop', { waitUntil: 'domcontentloaded', timeout: 25000 });
        await new Promise(r => setTimeout(r, body.wait || 1500));
        const img = await screenshot64(page);
        await browser.close();
        return json({ ok: true, screenshot: img, url: body.url });
      } catch (e) { await browser.close(); return json({ ok: false, error: e.message }); }
    }

    // ── POST /click ───────────────────────────────────────────────────────
    if (url.pathname === '/click' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      const { browser, page } = await getPage(env);
      try {
        await page.goto(body.url, { waitUntil: 'domcontentloaded', timeout: 25000 });
        await new Promise(r => setTimeout(r, 1000));
        if (body.selector) {
          await page.click(body.selector);
          await new Promise(r => setTimeout(r, body.waitMs || 1000));
        }
        const img = await screenshot64(page);
        const title = await page.title();
        await browser.close();
        return json({ ok: true, screenshot: img, title });
      } catch (e) { await browser.close(); return json({ ok: false, error: e.message }); }
    }

    // ── POST /test-game ───────────────────────────────────────────────────
    if (url.pathname === '/test-game' && request.method === 'POST') {
      const { browser, page } = await getPage(env, 1280, 900);
      try {
        await page.goto('https://www.shortfactory.shop/trump/game/', { waitUntil: 'domcontentloaded', timeout: 25000 });
        await new Promise(r => setTimeout(r, 2000));

        // Read game state from window.G
        const state = await page.evaluate(() => {
          if (typeof G === 'undefined') return { loaded: false };
          return {
            loaded:      true,
            purity:      G.purity      || 0,
            deepStateHP: G.deepStateHP || 0,
            trumpHP:     G.trumpHP     || 100,
            oilCash:     G.oilCash     || 0,
            moves:       G.moves       || 0,
          };
        });

        const img = await screenshot64(page);
        await browser.close();
        return json({ ok: true, state, screenshot: img });
      } catch (e) { await browser.close(); return json({ ok: false, error: e.message }); }
    }

    // ── POST /crawl ───────────────────────────────────────────────────────
    if (url.pathname === '/crawl' && request.method === 'POST') {
      let body; try { body = await request.json(); } catch { return json({ error: 'invalid json' }, 400); }
      const { browser, page } = await getPage(env);
      const results = [];
      try {
        await page.goto(body.url || 'https://www.shortfactory.shop', { waitUntil: 'domcontentloaded', timeout: 25000 });
        const links = await page.evaluate(() =>
          Array.from(document.querySelectorAll('a[href]'))
            .map(a => a.href).filter(h => h.startsWith('http')).slice(0, 30)
        );
        const title = await page.title();
        const img   = await screenshot64(page);
        await browser.close();
        return json({ ok: true, title, links, screenshot: img });
      } catch (e) { await browser.close(); return json({ ok: false, error: e.message }); }
    }

    return json({ error: 'not found' }, 404);
  }
};
