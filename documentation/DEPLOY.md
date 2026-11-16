# Deploy

## Before the repository goes public
1. Ask LSE IDEAS communications to approve publishing, the wording, the images and the use of the project name. The repository uses no LSE logo.
2. Decide a licence ([LICENSING.md](LICENSING.md)).
3. Start with the repository set to **private**; make it public after sign-off.

## GitHub Pages (recommended home)
1. Push to GitHub. Settings > Pages > Source: **Deploy from a branch**, branch `main`, folder `/docs`.
2. Your address will be `https://USER.github.io/REPO/`.
3. Put the address in `config.json` (`"baseUrl": "https://USER.github.io/REPO/"`), run `python3 build.py`, and commit `docs/`. This adds link-preview tags. Also set `canonicalUrl` in the `CONFIG` block of `src/template.html` so Google Analytics reports one address.
4. Point the short link (`tinyurl.com/Singapore2065`) at the Pages address, or at the itch.io page if you keep both.

Why Pages helps analytics: the app is then served from its own address, so campaign tags such as `?utm_source=west` reach Google Analytics. Inside itch.io's frame they may not. Camera, microphone and sharing also work more predictably at top level.

## itch.io
Zip **`dist/index.html`** (the single-file build; the hosted build needs its image folder) and upload as an HTML game; tick "play in browser". Test camera, microphone and share on a real iPhone and Android phone through the live page.

## After each change
`python3 build.py`, run `python3 tests/smoke_test.py`, open the page, and watch the events in GA4 DebugView (add `?gadebug=1`).

## Settings you will touch (in `src/template.html`, the `CONFIG` block)
`analyticsId` (G-M187SMM0J7), `shareUrl` (https://tinyurl.com/Singapore2065), `hashtags` (#Singapore2065 #SG100), `appVersion`, `canonicalUrl`, `legacyFeedbackEvents`, `audiences`. Bump `version` in `config.json` when you release, so installed copies refresh.

## Tagged links for your three audiences
`https://USER.github.io/REPO/?utm_source=west`, `...?utm_source=professionals`, `...?utm_source=leaders`. Team testing: open once with `?internal=1`.
