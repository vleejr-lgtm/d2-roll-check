/* Service worker: makes the site installable and quick to open.
   - Pages (navigations, .html): network first, cached copy only when offline, so a deploy shows at once.
   - Versioned files (?v=<build>): cache first; a new deploy has a new ?v so it never serves an old script.
   - Never touches bungie.net, the god roll lists or anything on another site, and never caches config.js. */
const CACHE = 'd2rc-__BUILD__';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil((async () => {
  for (const k of await caches.keys()) if (k !== CACHE) await caches.delete(k);
  await self.clients.claim();
})()));
self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin || /config\.js$/.test(url.pathname)) return;
  const page = req.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname.endsWith('/');
  if (page){
    e.respondWith((async () => {
      try { const r = await fetch(req); if (r.ok){ const c = await caches.open(CACHE); c.put(url.pathname, r.clone()); } return r; }
      catch { return (await caches.match(url.pathname)) || (await caches.match('index.html')) || Response.error(); }
    })());
    return;
  }
  if (url.searchParams.has('v') || /\/icons\//.test(url.pathname) || url.pathname.endsWith('.webmanifest')){
    e.respondWith((async () => {
      const hit = await caches.match(req); if (hit) return hit;
      const r = await fetch(req); if (r.ok){ const c = await caches.open(CACHE); c.put(req, r.clone()); } return r;
    })());
  }
});
