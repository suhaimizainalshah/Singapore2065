#!/usr/bin/env python3
"""Smoke test for both builds.   pip install playwright && playwright install chromium && python3 tests/smoke_test.py
docs/ is tested over http (as GitHub Pages serves it), dist/ from a file. Checks the promises that matter: nothing is sent before permission,
events fire after it, the dials are real choices, the flows work in every language, pictures load on demand, the page installs offline, motion is off when asked."""
import functools, http.server, os, socketserver, sys, threading
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); fails = []
def check(name, ok, extra=''):
    print(('  PASS ' if ok else '  FAIL ') + name + (' ' + str(extra) if extra and not ok else ''))
    if not ok: fails.append(name)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    h = functools.partial(Q, directory=os.path.join(ROOT, 'docs')); srv = socketserver.TCPServer(('127.0.0.1', 0), h); threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv
EV = "(window.dataLayer||[]).filter(a=>a[0]==='event').map(a=>[a[1],a[2]||{}])"
def run(b, url, label, pages):
    print('\n== ' + label)
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, permissions=['camera', 'microphone']); pg = ctx.new_page(); errs, reqs = [], []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('request', lambda r: reqs.append(r.url))
    pg.goto(url + ('&' if '?' in url else '?') + 'utm_source=west&internal=1'); pg.wait_for_timeout(1200)
    check('consent banner shown first', pg.is_visible('#consent'))
    check('consent buttons look equal', pg.evaluate("(()=>{const a=getComputedStyle(document.getElementById('consentYes')),b=getComputedStyle(document.getElementById('consentNo'));return a.backgroundColor===b.backgroundColor&&a.color===b.color&&a.borderTopColor===b.borderTopColor})()"))
    check('no Google request before permission', not [r for r in reqs if 'googletagmanager' in r])
    check('hashtag in the title', '#Singapore2065' in pg.inner_text('.hashline'))
    check('purpose line visible', 'two-minute' in pg.inner_text('.purpose'))
    webp0 = len([r for r in reqs if r.endswith('.webp')])
    if pages: check('pictures load on demand (none before the first result)', webp0 == 0, webp0)
    pg.click('#consentYes'); pg.wait_for_timeout(500)
    check('Google script only after Allow', bool([r for r in reqs if 'googletagmanager.com/gtag/js?id=G-' in r]))
    # dials are real choices
    opts = pg.locator('.opt'); check('dial options are buttons', pg.evaluate("[...document.querySelectorAll('.opt')].every(o=>o.tagName==='BUTTON')"))
    pg.locator('#reel1O .opt').nth(0).click(); pg.locator('#reel2O .opt').nth(0).click(); pg.wait_for_timeout(200)
    check('picking both dials relabels the button', 'Show this future' in pg.inner_text('#spin'), pg.inner_text('#spin'))
    check('picked state is exposed to assistive tech', pg.locator('#reel1O .opt').nth(0).get_attribute('aria-pressed') == 'true')
    pg.click('#spin'); pg.wait_for_timeout(9500)
    check('picked many + open gives Open Commons', pg.inner_text('#cName') == 'Open Commons', pg.inner_text('#cName'))
    check('focus moved to the result', pg.evaluate("document.activeElement.id") == 'cName')
    check('feedback link not shown yet', not pg.is_visible('#fbOpen'))
    if pages:
        n1 = len([r for r in reqs if r.endswith('.webp')]); check('only the card picture loaded so far', 1 <= n1 <= 3, n1)
    pg.click('#paperBtn'); pg.wait_for_timeout(700)
    check('full front page opens', pg.is_visible('#ppBody .pp-sheet'))
    if pages: check('front-page pictures load once opened', len([r for r in reqs if r.endswith('.webp')]) > n1)
    pg.click('#ppNav button[data-k=numbers]'); pg.wait_for_timeout(300); check('numbers table opens', pg.is_visible('table.pp-num'))
    pg.click('#ppClose'); pg.wait_for_timeout(300)
    check('feedback link appears after the front page is closed', pg.is_visible('#fbOpen'))
    pg.click('#fbOpen'); pg.wait_for_timeout(300); pg.click('#fbB label:nth-child(4)'); pg.click('#fbC label:nth-child(2)'); pg.click('#fbSend'); pg.wait_for_timeout(300)
    ev = pg.evaluate(EV); names = [e[0] for e in ev]
    for need in ['dial_pick', 'first_spin', 'spin', 'result_view', 'paper_open', 'result_dwell', 'feedback_open', 'feedback_submit', 'feedback_b4_little']: check('event: ' + need, need in names, names)
    sp = [e[1] for e in ev if e[0] == 'result_view'][0]; check('result_view source is pick', sp.get('source') == 'pick', sp)
    check('events carry app_version, audience and internal flag', all(e[1].get('app_version') == '0.4.0' and e[1].get('audience') == 'west' and e[1].get('traffic_type') == 'internal' for e in ev if e[0] in ('spin', 'feedback_submit')))
    pg.click('#fbClose'); pg.evaluate("window.dispatchEvent(new Event('pagehide'))"); pg.wait_for_timeout(200)
    vs = [e[1] for e in pg.evaluate(EV) if e[0] == 'visit_summary']; check('visit_summary sent once with max_stage', len(vs) == 1 and vs[0].get('max_stage') == 'paper', vs)
    r = pg.evaluate("async()=>{const H=window.__s65r; await H.buildAsset(); const a=H.S.asset; return {w:a.w,h:a.h}}"); check('share picture is 1080x1350', r['w'] == 1080 and r['h'] == 1350, r)
    # languages
    for code, word in [('zh', '百年'), ('ms', 'Seratus'), ('ta', 'நூறாண்டு')]:
        pg.click('#langs button[data-l=%s]' % code); pg.wait_for_timeout(400)
        body = pg.inner_text('body'); check('%s: interface translated' % code, word in pg.inner_text('#title') and 'undefined' not in body and '{' not in pg.inner_text('#cHead'), pg.inner_text('#title'))
        check('%s: result card translated' % code, pg.inner_text('#cName') not in ('Open Commons',), pg.inner_text('#cName'))
    pg.click('#langs button[data-l=en]')
    check('no script errors', not errs, errs)
    if pages:
        pg.wait_for_timeout(800); sw = pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!r)"); check('service worker registered', sw)
        check('install manifest linked', pg.evaluate("!!document.querySelector('link[rel=manifest]')"))
        pg.wait_for_timeout(1200); ctx.set_offline(True)
        try: pg.reload(); pg.wait_for_timeout(1500); check('opens offline after the first visit', pg.is_visible('#spin'))
        except Exception as e: check('opens offline after the first visit', False, e)
        ctx.set_offline(False)
    # declined permission
    p2 = b.new_context(viewport={'width': 390, 'height': 844}).new_page(); r2 = []; p2.on('request', lambda r: r2.append(r.url)); p2.goto(url); p2.wait_for_timeout(900); p2.click('#consentNo'); p2.click('#spin'); p2.wait_for_timeout(9500)
    check('declined: nothing sent to Google', not [r for r in r2 if 'google' in r]); check('declined: feedback hidden', not p2.is_visible('#fbOpen'))
    p3 = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce').new_page(); p3.goto(url); p3.wait_for_timeout(900)
    check('reduced motion: background animation off', p3.evaluate("window.__s65r.FX.enabled()") is False)
    p4 = b.new_context(viewport={'width': 390, 'height': 844}).new_page(); p4.goto(url); p4.wait_for_timeout(900); p4.click('#consentNo'); p4.keyboard.press('Space'); p4.wait_for_timeout(9500)
    check('Space bar spins', p4.is_visible('#result'))
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'])
    srv = serve(); run(b, 'http://127.0.0.1:%d/index.html' % srv.server_address[1], 'docs/ (GitHub Pages build, over http)', True)
    run(b, 'file://' + os.path.join(ROOT, 'dist', 'index.html'), 'dist/ (single file, from disk)', False); b.close()
print('\n%d check(s) failed' % len(fails) if fails else '\nAll checks passed'); sys.exit(1 if fails else 0)
