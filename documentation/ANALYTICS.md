# Analytics by design

**Status (version 0.4.0): sections 3.1 to 3.8 are built.** Items still needing action in Google Analytics (not in code) are in section 3.10 and 3.11.

Principle: decide the questions first, collect only what answers them, ask permission, and write it down. Nothing here identifies a person.

## 1. What we want to learn (and why)
| Question | Why it matters | Measure |
|---|---|---|
| Does it reach the three audiences? (Pakistanis in the West style: diaspora and intellectuals; middle-class professionals; leaders) | Programme objective | Visits by tagged link (`audience`), country |
| Do people play? | Is the hook working | Spin rate = sessions with `spin` / sessions |
| Do they go deeper? | Is the content worth reading | `paper_open` rate; sections reached (`paper_section`) |
| Do they spread it? | The hashtag only travels if people share | `share_ready`, `share` and `share_result` outcome; `shared_link_visit` |
| Is it believable, and does it change minds? | The research aim | `feedback_submit` believability and changed_view, by future |
| Is anything broken or frustrating? | Fix before scaling | `problem` events; drop-off before first spin |
| What did we not see? | Consent bias | Banner choice shown to us only for those who allow; see section 5 |

## 2. Events (all sent only after Allow)
Every event carries `ui_language`, `app_version`, and, when present, `audience` and `traffic_type`. Names are lower case, no spaces.

| Event | Params | When |
|---|---|---|
| `page_view` | title, page_location | after Allow (sent by hand) |
| `consent_allowed`, `analytics_opt_out` | none | permission given or withdrawn |
| `dial_pick` | dial (gains, world), value, action (select, clear) | someone chooses a dial instead of spinning |
| `first_spin` | seconds_bucket (`<5`, `5-15`, `15-60`, `60+`) | first spin of the visit, bucketed time since the page opened |
| `spin` | future, future_name, spin_number, picked (0, 1, 2) | a spin or pick lands |
| `result_view` | future, future_name, source (spin, pick, pick_partial, matrix, camera), skipped_pause | a result shows |
| `result_dwell` | bucket, next_action (spin_again, front_page, react, leave) | once per result, when the person does something next |
| `tell_me_more`, `matrix_pick`, `info_open`, `info_tab` | state / future / tab, source | card expanded, four-futures sheet and About |
| `paper_open`, `paper_nav`, `paper_close`, `paper_print` | future, page, source / to | full front page |
| `paper_section` | section_name, page, future | each section reached once per opening |
| `react_open`, `reaction_added` | type (emoji, selfie, voice), source | reaction sheet; which emoji is **not** recorded |
| `share_ready`, `share`, `share_result`, `save_media` | kind, method, outcome, has_selfie, has_voice, has_emoji | picture or video built, shared, saved |
| `camera_open`, `camera_spin`, `camera_photo`, `camera_clip` | future, mode | forehead-card version |
| `shared_link_visit` | future | arrived from a shared link |
| `feedback_open`, `feedback_skip` | future, source | feedback form |
| `feedback_submit` | believable (1-5), changed_view (yes, little, no), feedback_code (FB01-FB15), future, future_name | form submitted |
| `feedback_b1_yes` ... `feedback_b5_no` | same | **legacy**, sent alongside `feedback_submit` while `legacyFeedbackEvents` is true; remove after one release |
| `visit_summary` | max_stage (menu, spun, result, paper, reacted, shared), spins, sections | once when the page is hidden or closed |
| `effects_toggle`, `sound_toggle`, `vibration_toggle`, `language_change` | state / to_language | settings |
| `problem` | type (camera_denied, mic_denied, record_failed, share_failed), source | something failed |

## 3. Changes (analytics by design). Built items are marked [x]
**Fix the foundations first**
1. [x] **One feedback event, not fifteen.** GA4 works best with few event names and parameters carrying the variation. Send `feedback_submit` with `believable`, `changed_view`, `future`, `feedback_code`. Keep the old names for one release so charts do not break, then drop them.
2. [x] **Stamp every event with `app_version`** (for example `0.3.0`) via `gtag('set', {app_version:'0.3.0'})`. Without it you cannot tell which build produced which data.
3. [x] **Fix `page_location` for embeds.** Set `canonicalUrl` in CONFIG once the public address is known. Inside itch.io's frame the address is not your page. Send `page_location` and `page_referrer` explicitly in `config`, using your public address.
4. [x] **Serve from your own address (GitHub Pages)** so `?utm_source=...` reaches Google Analytics. Tags may not pass through itch.io's frame. Then give each audience a link: `?utm_source=west`, `?utm_source=pk_pros`, `?utm_source=leaders`.
5. [x] **Internal traffic filter.** Your team will test a lot. Open the site once with `?internal=1` on each team device (it stores a flag and sends `traffic_type: internal` with every event; `?internal=0` clears it). Then in GA4 Admin > Data settings > Data filters, create an **Internal Traffic** filter for `traffic_type = internal` and switch it from Testing to Active. Otherwise the first week of data is mostly you.

**Add the few measures that explain behaviour**
6. [x] `first_spin` with `seconds_bucket` (`<5`, `5-15`, `15-60`, `60+`): how long people hesitate. Bucket numbers so there is no high-cardinality noise.
7. [x] `result_dwell` with `bucket`: time on the result card before the next action.
8. [x] `visit_summary` sent once on page hide with `max_stage` (`menu`, `spun`, `result`, `paper`, `reacted`, `shared`), `spins`, `sections`: a single funnel in one event, even for people who leave early.
9. [x] If you let people pick (built as `dial_pick`) a future instead of spinning (see the design review), add `dial_pick` with `compact` and `world`. Comparing picks with random landings shows which futures people want, which is research data.

**Governance and care**
10. [ ] (in Google Analytics Admin) Set a **data retention** of 14 months (default is 2 months for event data) only if the notice says so. Turn **Google signals off** (the code already does), turn **Enhanced measurement** off (we send our own events and do not want automatic scroll and outbound-click events duplicating them), and turn **granular location and device data** off.
11. [ ] (in Google Analytics Admin) Register custom dimensions before launch or the parameters will not be reportable: `future`, `future_name`, `source`, `kind`, `type`, `outcome`, `tab`, `mode`, `state`, `page`, `to`, `section_name`, `believable`, `changed_view`, `feedback_code`, `app_version`, `traffic_type`, `audience`, `dial`, `value`, `picked`, `seconds_bucket`, `bucket`, `next_action`, `max_stage`, `sections`. Metric: `spin_number`. Keep the list small; GA4 caps custom dimensions.
12. [ ] Name an owner, a review date (monthly), and who may see the data. Keep this document and the notice in step with the code.

## 4. KPIs and how to read them
| KPI | Definition |
|---|---|
| Spin rate | sessions with `spin` / sessions with `page_view` |
| Depth rate | sessions with `paper_open` / sessions with `result_view` |
| Share rate | sessions with `share_result` outcome `completed` / sessions with `result_view` |
| Feedback rate | `feedback_submit` / `result_view` |
| Believability by future | average `believable` by `future_name` |
| Mind-change | share of `changed_view` = yes or little, by future |
| Loop | `shared_link_visit` / `share_result` completed (rough virality) |

## 5. Read the numbers with care
- Only people who tap Allow are counted, so every figure is a **lower bound** and the people who allow may differ from those who decline. Say this in any report.
- Ad blockers hide some visitors. Small numbers (under about 100 sessions) move a lot. Feedback is self-selected.
- You cannot measure the banner choice itself without consent. Do not use "consent mode advanced" (cookieless pings before consent) unless your data-protection team approves it in writing.
- A cookie-free counter such as GoatCounter, Plausible or Umami needs no banner and counts everyone (page views only). Consider it as a second, privacy-light source for reach, and keep GA4 for the deeper events.

## 6. QA checklist before each release
- [ ] Open with GA4 DebugView (`?gadebug=1`): spin, front page, feedback, share. Every event appears once, with its parameters.
- [ ] Decline the banner: DevTools Network shows no request to a Google domain.
- [ ] Allow, then withdraw in About: counting stops.
- [ ] Reduced motion set on the device: no animation, button disabled.
- [ ] `python3 tests/smoke_test.py` passes (both builds, all four languages).

## 7. Funnel to build in GA4 (Explore > Funnel exploration)
`page_view` > `first_spin` > `result_view` > `paper_open` > `react_open` > `share_result` (outcome completed). Break down by `audience` and `ui_language`. Add `visit_summary` `max_stage` as a second view for people who left early.
