# Design review: UI, UX and accessibility

## Status at version 0.4.0
| # | Item | Status |
|---|---|---|
| 1 | Dial options were not tappable | **Done.** They are real buttons. Pick one or both dials; the button then reads "Spin the other dial" or "Show this future". Logged as `dial_pick` |
| 2 | Consent buttons unequal | **Done.** Identical style; "How we use statistics" link opens About |
| 3 | Jargon in the first question | **Done.** "Who shares in the gains?" with "Many people / Few people". The word "compact" stays in About and the matrix. **Still to do:** test with five people |
| 4 | Landmarks, headings, keyboard-reachable scroll areas | **Done.** Footer landmark, h3 under h2, focusable front-page and table areas. Axe-core: 0 violations in all 8 states checked |
| 5 | Page weight | **Done.** WebP (2.3 MB to 1.6 MB). Hosted build is about 280 KB and loads pictures when needed; the single file is 2.2 MB |
| 6 | Link previews | **Built.** Set `baseUrl` in `config.json` once the public address is known |
| 7 | Purpose and time in one line | **Done.** "A two-minute scenario game. No sign-up." |
| 8 | Clearer path after the result | **Done.** React and share first; front-page button full width; feedback link appears after the front page is closed or after a share |
| 9 | Languages | **Built, drafts.** 中文, Bahasa Melayu, தமிழ் for the interface and the result cards. Long front-page text stays English with a note. **Needs native-speaker review** |
| 10 | Rain and legibility | **Monitor.** `effects_toggle` is logged. If more than about 15% of first sessions switch motion off, reduce the default rain |
| 11 | Offline and install | **Done** for the hosted build (manifest, service worker, icons) |
| 12 | Result card order | **Done.** The three signals moved into "Tell me more"; the card reads name, headline, voice |
| 13 | Challenge a friend | **Done.** The caption now says "I got X ... What do you get?" |
| 14 | Haptics, softer sound, quiet mode | **Partly.** Vibration on landing with an About setting; sounds about 25% softer. Browsers cannot read a phone's silent switch, so there is no automatic quiet mode; the sound button stays in the top bar |
| 15 | "Why did I get this?" | **Already in the app** (the mini matrix with "you are here"); the card now explains it under "Tell me more" |
| 16 | Space bar to spin, focus rings | **Done.** Rings are dark on light surfaces and yellow on dark ones |
| 17 | Print stylesheet | **Done.** "Print this page" on each front page prints only the page |

The sections below are the original review (what was measured and why).


Reviewed build: 0.3 (before these changes) (flag logo, amber action button, water and rain theme). Evidence from automated checks on 10 November 2026; confirm with real people on real phones.

## What is already strong (measured)
- **Tap targets:** no interactive element under 44 x 44 px at 390 px width.
- **Above the fold:** the Spin button is fully visible on 375 x 667 (iPhone SE), 360 x 640 and phone landscape 844 x 390.
- **Focus and announcements:** after a spin, focus moves to the result name and a live region reads "Your 2065: ..." to screen readers.
- **Automated audit (axe-core, WCAG 2.2 AA plus best practice):** no violations on the front-page dialog or the feedback dialog; three minor ones elsewhere (below).
- **Contrast:** buttons against their surroundings 4.0 to 9.5 : 1 (needs 3), labels 6.5 to 10.6 : 1, white links 4.8 : 1 or better.
- **Respectful by default:** consent first, Do Not Track honoured, reduced motion honoured, motion switch in the top bar, no script errors.

## Priority 1: do before a public launch
| # | Issue | Evidence | Fix |
|---|---|---|---|
| 1 | **Dial options look clickable but are not.** "Broad / Narrow" and "Open / Fragmented" have radio circles, but are plain `div.opt` with no role or tabindex. People will tap them. | DOM check | Either (a) make them real buttons so people can **pick a future instead of spinning** ("Choose your own" is also research data, see ANALYTICS item 9), or (b) turn the circles into small status dots and mark the rows `aria-hidden`. (a) is the stronger design. |
| 2 | **Consent buttons are not equal.** "Allow" is filled dark teal, "No thanks" is a white outline. Regulators expect equal prominence. | computed styles | Give both the same shape, size and weight (for example both outlined, or both filled in different neutral tones). Add a "Privacy" link to the notice. |
| 3 | **Jargon in the first question.** "How broad is the compact?" is the least obvious phrase on the first screen. | read-through | Test plain options: "Who shares in the gains?" with answers "Many people / Few people". Keep "compact" for the About page. Try a 5-second test with five people. |
| 4 | **Landmarks and headings.** The page has no `<main>` or `<footer>`; the expanded card jumps from h2 to h4; the front-page scroll areas cannot be reached by keyboard. | axe: `region`, `heading-order`, `scrollable-region-focusable` | Wrap the app in `<main>`, the credit line in `<footer>`; change the h4 in "Tell me more" to h3; give `#ppBody` and `.pp-scroll` `tabindex="0"`, `role="region"` and an `aria-label`. About 30 minutes. |
| 5 | **Weight: 3.3 MB single file.** Everything downloads before the first spin; on a slow connection this is the main drop-off risk. | build size | Convert pictures to WebP (2.3 MB to 1.5 MB, about 33% smaller). Only 12 pictures are needed for the first result (1.2 MB); the other 16 (1.1 MB) are front-page only and can load on demand once the site is on GitHub Pages. Keep the single-file build for itch.io and offline. |
| 6 | **Link previews.** Shared links show a blank card in WhatsApp, Telegram and LinkedIn. | no `og:image` | Run `python3 build.py --base-url https://USER.github.io/REPO/` once hosted. The social image is ready in `docs/assets/social-preview.png`. |

## Priority 2: next release
7. **Purpose and time in one line** under the title: "A two-minute scenario game. No sign-up." Today the programme is only named in the small footer.
8. **A clearer path after the result.** One strong next step, then two quieter ones. Suggest: primary "React and share"; secondary "Read the full front page"; the feedback link appears after the front page is closed or after a share, not before (ask when people have something to say).
9. **Languages.** Chinese (Simplified), Bahasa Melayu and Tamil, translated by native speakers. The engine already switches language; the content file needs a block per language.
10. **Rain and legibility.** The rain is behind the text and passes contrast, but it is the busiest element on screen. Watch `effects_toggle`: if more than about 15% of first sessions turn motion off, lower the default rain (try 60% opacity) or fade it over the text column. Consider starting new visitors in a calmer setting.
11. **Offline and install.** Add a web-app manifest and a small service worker so the site opens offline after the first visit and can be added to the home screen. Useful in low-signal places and for events.
12. **Result card scan order.** Name, headline, then one voice, then "see more". Keep the three signal chips only if they help; test whether people read them.
13. **Shareable by design.** The picture already carries the hashtag and link. Add "Challenge a friend": a share that says "I got Gilded Hub. What do you get?" The question invites a reply and is easy to measure with `shared_link_visit`.

## Priority 3: later
14. Haptics on landing (a short vibration), a softer sound set, and a quiet mode when the phone is on silent.
15. A "why did I get this?" panel showing the two dial answers on the matrix.
16. Keyboard shortcut for Spin (space), and visible focus ring review on every dark surface.
17. Print stylesheet for the front pages, for panel meetings.

## Test plan with real people (ten people, thirty minutes each)
- **Five-second test:** show the start screen for five seconds; ask what it is and what they would do next.
- **Tasks:** "Get a result"; "find out why you got it"; "send it to a friend"; "tell us what you think".
- **Watch for:** tapping the dial rows; hunting for Spin; missing the feedback link; confusion about "compact"; the consent banner choice.
- **Devices:** one older Android, one iPhone, one laptop, one screen reader user, one person who prefers reduced motion.

## Targets to aim for (starting points, to adjust once you see real data)
Spin rate 70%+, front-page open rate 25%+, share rate 10%+, feedback rate 8%+, motion switched off in under 15% of first sessions.
