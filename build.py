#!/usr/bin/env python3
"""Builds the two versions of the site from src/.

  docs/   for hosting (GitHub Pages): index.html + img/*.webp loaded on demand, an install manifest and an offline service worker
  dist/   one self-contained index.html with everything embedded: for itch.io, a USB stick, or double-clicking

    python3 build.py                         build both
    python3 build.py --mode pages | single   build one
    python3 build.py --check                 fail if docs/ or dist/ is out of date (used by the automatic check)
    python3 build.py --base-url https://USER.github.io/REPO/    add link-preview tags (or set "baseUrl" in config.json)

Needs only Python 3."""
import argparse, base64, hashlib, json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'src')
ap = argparse.ArgumentParser(); ap.add_argument('--mode', choices=['pages', 'single', 'all'], default='all'); ap.add_argument('--base-url', default=''); ap.add_argument('--check', action='store_true')
a = ap.parse_args()
cfgp = os.path.join(HERE, 'config.json'); cfg = json.load(open(cfgp, encoding='utf-8')) if os.path.exists(cfgp) else {}
base = (a.base_url or cfg.get('baseUrl', '')).strip(); base = base if (not base or base.endswith('/')) else base + '/'
VERSION = cfg.get('version', '0.4.0')
rd = lambda n: open(os.path.join(SRC, n), encoding='utf-8').read()
js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
content, ui, site, tpl = json.loads(rd('content.json')), json.loads(rd('ui.json')), json.loads(rd('site.json')), rd('template.html')
imgs = {os.path.splitext(f)[0]: f for f in sorted(os.listdir(os.path.join(SRC, 'img'))) if f.lower().endswith('.webp')}
mime = lambda f: 'image/webp'
def og():
    if not base: return ''
    return ('<meta property="og:type" content="website">\n<meta property="og:url" content="%s">\n<meta property="og:image" content="%sassets/social-preview.png">\n'
            '<meta property="og:image:width" content="1280"><meta property="og:image:height" content="640">\n<meta name="twitter:card" content="summary_large_image">\n'
            '<meta name="twitter:image" content="%sassets/social-preview.png">\n<link rel="canonical" href="%s">') % (base, base, base, base)
PWA = ('<link rel="manifest" href="manifest.webmanifest">\n<link rel="apple-touch-icon" href="assets/icon-192.png">\n'
       "<script>if ('serviceWorker' in navigator && /^https?:/.test(location.protocol) && window.top === window) addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () { }); });</script>")
def html(mode):
    if mode == 'single':
        im = {k: 'data:%s;base64,%s' % (mime(f), base64.b64encode(open(os.path.join(SRC, 'img', f), 'rb').read()).decode()) for k, f in imgs.items()}; pwa = ''
    else:
        im = {k: 'img/' + f for k, f in imgs.items()}; pwa = PWA
    out = (tpl.replace('/*__SITE__*/{}', js(site)).replace('/*__CONTENT__*/{}', js(content)).replace('/*__UI__*/{}', js(ui)).replace('/*__IMG__*/{}', js(im))
              .replace('<!--__OG__-->', og()).replace('<!--__PWA__-->', pwa))
    assert '/*__' not in out and '<!--__' not in out, 'a placeholder was not filled'; return out
manifest = json.dumps({'name': 'Singapore 2065: spin your future', 'short_name': 'Singapore 2065', 'description': 'A two-minute scenario game about Singapore in its hundredth year.', 'start_url': './', 'scope': './',
                       'display': 'standalone', 'orientation': 'portrait', 'background_color': '#041634', 'theme_color': '#0b2f5b',
                       'icons': [{'src': 'assets/icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': 'assets/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'}]}, indent=1)
def sw(h):
    return ("/* Offline support. Pages and pictures are kept after the first visit. Bump the version in config.json to refresh. */\nconst V = 's65-%s';\nconst CORE = ['./', 'index.html', 'manifest.webmanifest', 'assets/icon-192.png'];\n"
            "self.addEventListener('install', e => e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting())));\n"
            "self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())));\n"
            "self.addEventListener('fetch', e => {\n  const r = e.request; if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;\n"
            "  if (r.mode === 'navigate') { e.respondWith(fetch(r).then(x => { const c = x.clone(); caches.open(V).then(k => k.put('index.html', c)); return x; }).catch(() => caches.match('index.html'))); return; }\n"
            "  e.respondWith(caches.match(r).then(m => m || fetch(r).then(x => { const c = x.clone(); caches.open(V).then(k => k.put(r, c)); return x; })));\n});\n") % h
files = {}
if a.mode in ('pages', 'all'):
    h = html('pages'); files['docs/index.html'] = h.encode('utf-8'); files['docs/manifest.webmanifest'] = manifest.encode('utf-8'); files['docs/sw.js'] = sw(hashlib.md5(h.encode('utf-8')).hexdigest()[:8]).encode('utf-8')
    for f in imgs.values(): files['docs/img/' + f] = open(os.path.join(SRC, 'img', f), 'rb').read()
    for f in ('icon-192.png', 'icon-512.png'): files['docs/assets/' + f] = open(os.path.join(SRC, 'assets', f), 'rb').read()
if a.mode in ('single', 'all'): files['dist/index.html'] = html('single').encode('utf-8')
if a.check:
    bad = [p for p, d in files.items() if not os.path.exists(os.path.join(HERE, p)) or open(os.path.join(HERE, p), 'rb').read() != d]
    sys.exit(0 if not bad else 'out of date, run python3 build.py: ' + ', '.join(bad[:5]))
for p, d in files.items():
    fp = os.path.join(HERE, p); os.makedirs(os.path.dirname(fp), exist_ok=True); open(fp, 'wb').write(d)
open(os.path.join(HERE, 'docs', '.nojekyll'), 'w').close()
for p in ('docs/index.html', 'dist/index.html'):
    if p in files: print('built', p, round(len(files[p]) / 1024), 'KB')
print('pictures:', len(imgs), '| link previews:', 'on' if base else 'off (set baseUrl in config.json)')
