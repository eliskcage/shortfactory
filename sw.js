/**
 * SHORTFACTORY SERVICE WORKER
 * Cache-first for static assets, network-first for API/dynamic content.
 * Enables offline mode + Play Store TWA installability.
 */

var CACHE_NAME = 'sf-v18';
var PRECACHE = [
  '/',
  '/hub/',
  '/screensaver/',
  '/contribution.js',
  '/screensaver/player.js',
  '/screensaver/shaders.js',
  '/screensaver/supercharge.js',
  '/screensaver/greenscreen.js',
  '/manifest.json'
];

// Install — precache core assets
self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(PRECACHE);
    }).then(function() {
      return self.skipWaiting();
    })
  );
});

// Activate — clean old caches
self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE_NAME; })
            .map(function(k) { return caches.delete(k); })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Message — allow pages to force immediate activation
self.addEventListener('message', function(e) {
  if (e.data === 'SKIP_WAITING') self.skipWaiting();
});

// Fetch — cache-first for static, network-first for dynamic
self.addEventListener('fetch', function(e) {
  var url;
  try { url = new URL(e.request.url); } catch(_) { return; }

  // Skip non-GET and non-http(s) — let browser handle these natively
  if (e.request.method !== 'GET') return;
  if (url.protocol !== 'https:' && url.protocol !== 'http:') return;
  // Skip localhost/127.0.0.1 — never cacheable, always direct
  if (url.hostname === 'localhost' || url.hostname === '127.0.0.1') return;

  var isDynamic = url.pathname.indexOf('api')  !== -1 ||
                  url.pathname.indexOf('.php')  !== -1 ||
                  url.pathname.indexOf('sync')  !== -1;

  // Wrap everything in async IIFE with a top-level catch —
  // this guarantees e.respondWith() ALWAYS receives a real Response.
  e.respondWith((async function() {
    try {
      if (isDynamic) {
        // Network-first
        try { return await fetch(e.request); } catch(_) {}
        var c = await caches.match(e.request);
        return c || new Response('', { status: 503, statusText: 'Offline' });

      } else {
        // Cache-first
        var cached = await caches.match(e.request);
        if (cached) return cached;

        try {
          var response = await fetch(e.request);
          if (response && response.status === 200) {
            var cache = await caches.open(CACHE_NAME);
            cache.put(e.request, response.clone()).catch(function() {});
          }
          return response;
        } catch(_) {
          // Offline fallback
          if (e.request.destination === 'document') {
            var root = await caches.match('/');
            return root || new Response('Offline', { status: 503, statusText: 'Offline' });
          }
          return new Response('', { status: 503, statusText: 'Offline' });
        }
      }
    } catch(_) {
      // Nuclear fallback — no code path can escape without a Response
      return new Response('', { status: 503, statusText: 'Offline' });
    }
  })());
});
