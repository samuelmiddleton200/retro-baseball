const CACHE = 'retro-baseball-202610261955';
const APP = ['./', 'index.html', 'manifest.webmanifest', 'icon-180.png', 'icon-192.png', 'icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(APP.map(u => new Request(u, { cache:'reload' })))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const own = new URL(e.request.url).origin === location.origin;
  e.respondWith(caches.open(CACHE).then(async c => {
    try {
      // our own files are asked for with a one-off query on the end: GitHub's servers keep a copy of each address for
      // up to 10 minutes, so the plain address could come back as the version before the one just published
      let r;
      if (own) { const u = new URL(e.request.url); u.searchParams.set('fresh', Date.now()); r = await fetch(u.href, { cache:'no-store' }); }
      else r = await fetch(e.request);
      if (r.ok || r.type === 'opaque') c.put(e.request, r.clone());
      return r;
    } catch { return (await c.match(e.request)) || (await c.match('./')) || Response.error(); }   // offline
  }));
});
