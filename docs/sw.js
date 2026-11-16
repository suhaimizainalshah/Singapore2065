/* Offline support. Pages and pictures are kept after the first visit. Bump the version in config.json to refresh. */
const V = 's65-ec6d4e3d';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'assets/icon-192.png'];
self.addEventListener('install', e => e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  if (r.mode === 'navigate') { e.respondWith(fetch(r).then(x => { const c = x.clone(); caches.open(V).then(k => k.put('index.html', c)); return x; }).catch(() => caches.match('index.html'))); return; }
  e.respondWith(caches.match(r).then(m => m || fetch(r).then(x => { const c = x.clone(); caches.open(V).then(k => k.put(r, c)); return x; })));
});
