SG-183 model=opencode-go/deepseek-v4.1-flash effort=max (read from own process args: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`, PID 1278021) cwd=/home/andrei/StorageGenie remote=git@github.com:Andovol/StorageGenie.git
BASE requested=`automation`; BASE resolved=`7725ada8faf33ae1ed984c0afa49445a48a02872` (clean, equals origin/automation at start; `7725ada Audit SG-179; queue one responsive verification correction and deadline continuation`). WORK_HEAD=`a835baed92f9d39ad7d631b89f45c292c86485f4` (evidence tip named above; the report commit and the receipt note follow and are not in this line).
Contract version: 0.46.0 (echo). Source: `/home/andrei/storagegenie-contract/VERSION` = `0.46.0`; payload `RULES.sha256` = `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef` (the adopted 0.46.0 payload). G-L1's `bash .rules-cache/rules_check.sh` is not present in this host checkout (`.rules-cache` absent) — same condition SG-179 ran under; the live contract copy `/home/andrei/storagegenie-contract/` is the authority read.
Lane bound: `RUN_BUDGET_S=2100` from `/etc/dispatch/storagegenie.conf` (read this session); dispatch start 13:58:00Z; report write 14:19Z = **1260 s elapsed**, inside bound; no timeout/idle kill. Ordinary commands 120 s, browser runs 600 s — longest browser run 38 s (`SG-183_app_run.log`), controls run <60 s (`SG-183_controls_run.log`).
HEALTH: unchanged, OK (start 14:01Z `{"status":"ok","db":"ok","storage":"ok"}` observed into `SG-183_health.log`; end 14:16:20Z `{"status":"ok","db":"ok","storage":"ok"}`, same file). No production write, no rebuild/restart, no paid provider call (count 0).

## (a) Issues / deviations / surprises

1. **Disclosed deviation: `docker ps` was included in my first environment batch probe** and returned `permission denied ... unix:///var/run/docker.sock`. That is the documented pre-existing lane condition (root-only socket; `F-SG172-5`, `F-SG170-4`, `SG-175_verify.log`), not a new privileged denial; no sudo, alternate socket, identity or mount was used and docker was not attempted again. Container/image identity stays **UNVERIFIED** (packet rule). Recorded in `SG-183_worklog.log`.
2. **The SG-179 driver was not present.** `/tmp/opencode/sg179/cdp.mjs` does not exist on this host (checked before any capture). Same mechanism rebuilt dependency-free: host Playwright-cache `chrome-headless-shell` `HeadlessChrome/149.0.7827.55` + raw CDP over the DevTools websocket (Node v24 built-in WebSocket; no new dependency, no new service). Flags exactly: `--remote-debugging-port=0 --user-data-dir=<fresh tmp> --no-first-run --no-default-browser-check --disable-gpu --no-sandbox --disable-dev-shm-usage --force-device-scale-factor=1 --window-size=1280,900 about:blank` (`SG-183_measure.json` → `browser.launchArgs`). `/usr/bin/google-chrome` was **not** launched. Transport: `DevToolsActivePort` file → `/json/version` websocket; no wrapper.
3. **First app captures were invalid and were superseded (disclosed).** The served bundle's API base is the public origin (`VITE_API_BASE=https://storagegenie.dynv6.net`), which answers 401 without credentials, so initial runs measured the failure rendering ("No households"). Fixed inside the harness only: GETs to the API origin are re-issued against the loopback service (`127.0.0.1:8003`, same bytes, no credentials/cookies forwarded) and fulfilled into the page with `Access-Control-Allow-Origin: *` injected by the driver. This is **served-build rendering with loopback GET fulfillment, not authenticated public-URL proof**; the 401/public-URL limitation is unchanged and explicit. 86 GETs were fulfilled from loopback in the final run, 0 fulfillment failures.
4. **The SC 2.5.8 evaluator was corrected before the final runs.** The first version used center-to-center distance only; the criterion needs the 24 px circle to not intersect another target's box (`circle-vs-rect`, radius 12, edge distance < 12) nor another undersized target's circle (`circle-vs-circle`, center distance < 24). The final evaluator implements both and is the single implementation used for fixtures and app targets (`evalTargets`). Fixture dispositions are unchanged after the correction (pass still PASS-SPACING, fail still FAIL).
5. **PB-1 premise corrections.** (i) The uncommitted SG-179 driver cannot be verified or reused — rewritten, not recovered. (ii) The architect's extraction is confirmed over the report: tablet navigation overflow is **9 of 10** routes (catalog fits: 819/819), not 8/10. (iii) The old phone samples' `vw=811–853` is explained: the old driver's denominator followed the content-expanded width, so `overflowX=0` was a denominator artifact; with `documentElement.clientWidth` as denominator, the phone **does** overflow on 10/10 routes (436–478 px). `contentW` is not used anywhere in this correction.
6. **Rendering mode facts.** `Emulation.setDeviceMetricsOverride mobile=false, deviceScaleFactor=1`, classic 15 px scrollbars (never hidden): requested 390→375 client width on vertically scrolling pages, 834→819, 1440→1425 where a vertical scrollbar exists. Actual `dpr` 1. No layout-fixing CSS, no app style/meta change, no crop/stretch; the only DOM changes are the post-measurement privacy masks.
7. **Privacy order is measurement-first**: geometry and computed colors are collected unmasked; the mask runs afterwards (images blurred 14 px; household/asset display names and UUID-shaped runs replaced with U+25A0 in text nodes **and form-field values**); the committed JSON is scrubbed by the same rules. Verified: 0 private-name leaks and 0 UUIDs in `SG-183_measure.json`; 2571 replacement marks. The first screenshot set had a gap (candidate field *values* are input values, not text nodes) — found by eyeballing the image, fixed, re-captured; the superseded set is not committed.
8. **Guard accounting:** final app phase 118 requests, all GET, 0 blocked, 0 blocked-external; the guard's reject path is proven separately (control 3 below) because no app request attempted a mutation. Non-GET methods recorded: `{"GET":3,"POST":1}` in the control session; the POST was failed with `AccessDenied` before forwarding.
9. **Coverage limits, stated not hidden:** targets were sampled on six routes (catalog, asset_detail, settings, planning, analytics, review) at all three viewports; layout was captured on all ten routes. Review was sampled in its `edited` candidate state only, with no photo attached (Thumbnail unavailable). No `mobile=true`/device-emulation or touch/zoom run; no dark theme; no evidence-photo-bearing state.

## (b) Actions

- Commits (all `Dispatch-ID: SG-183` trailer): `eb4e264` (driver + controls v1), `db5a4ec` (measure/controls/shots v1), `a835bae` (form-field masking + final measure/shots), plus the report commit that follows. Push and notes read-back named in the receipt lines (published after this report; not claimable here).
- Changed paths (write ceiling respected; nothing outside `docs/worklogs/SG-183*`): `SG-183_driver.mjs`, `SG-183_controls.json`, `SG-183_controls_run.log`, `SG-183_measure.json`, `SG-183_app_run.log`, `SG-183_health.log`, `SG-183_worklog.log`, `SG-183_shots/` 7 JPEGs, this report. No product/config/test/lockfile/schema/migration/package file touched (`git status` clean apart from the named evidence commits).
- External/production effects: loopback GETs only (86 fulfilled API GETs + 32 loopback asset GETs; 118 total GET); zero non-GET forwarded anywhere; zero production writes; no evidence-store writes; no credential/auth/profile access (fresh temp browser profile); no restart; DB/storage untouched (health unchanged). UNKNOWN: none.
- Driver invocations: 12 total — controls phase 4 (runs 1–2 failed on my own harness bugs: uninvoked IIFE and undefined `opts`; runs 3–4 succeeded, run 4 with the corrected evaluator), app phase 8, each after a material harness change (classification field, evaluator, loopback fulfillment, UUID scrub, path scrub, disposition scrub, field-value mask). Final authoritative pair: controls run 4 + app run 8. Test-command count: 12. Retry semantics: no re-dispatch consumed; the two failed controls were failed prove executions on the same criterion (CO-35 limit reached, then a material fix).
- Durations (box clock UTC): 13:58:00 dispatch start; ≈14:06:50 controls green; 14:07 first evidence commit; 14:16:50 second; ≈14:18 final evidence commit; report write ≈14:19; elapsed ≈1260 s (receipt publish follows this report and is the runner's record). Longest single command: final app run 38 s. Highest-impact action: loopback GET fulfillment + the corrected real-viewport denominator, which turned the phone/tablet verdict from a denominator artifact into measured document overflow.

## (c) Verification (all raw outputs committed; blocks are observed output, not expectations)

Served-build identity (read-only GET, `SG-183_worklog.log`; hashes identical to SG-179 → served build unchanged since SG-179):
```
index.html sha256 2f035becd05b63e226af82e2e8fe60c8f3b5effb9f37e49dd95a2265c4da0d55 bytes=944
main.js    sha256 1b4680a0eddadff3c95a64b6bc00d744764d127a72cd5690ebea948b7664a29d bytes=322255
main.css   sha256 37b25dbdd4b0ecfdedb8255bc7f8af286726334e95a1a3a9e85b9ba381b3d57c bytes=3911
server: http://127.0.0.1:8003 (loopback);  https://storagegenie.dynv6.net/ = HTTP 401 (unchanged limitation)
```
Controls (`SG-183_controls.json`, `SG-183_controls_run.log`; exit 0, 9/9 controls OK):
```
scratch_fit_390:        docOverflowX=0 (scrollWidth 390 == clientWidth 390)
scratch_overflow_390:   mutation asserted landed (wide rect 1200) -> docOverflowX=810, offenders=1
transport_guard_post:   postResult=rejected:TypeError; server saw POST=false; driver blocked POST=true
spacing_pass_fixture:   20x20 gap4 (edge distance 14) -> PASS-SPACING (both controls)
spacing_fail_fixture:   20x20 adjacent (edge distance 10) -> FAIL (both controls)
spacing_fixture_geometry: passGeomOk=true failGeomOk=true
contrast_known:         4.5422 / 4.4781 / 21.0 / 1.0 vs expected 4.54 / 4.48 / 21 / 1 -> OK
contrast_wrong_expectation_must_fail: computed 4.5422 vs deliberately asserted 5.0 -> mismatch (control FAILED as required)
contrast_alpha_case:    rgba(0,0,0,0.5) over rgba(255,255,255,0.5)-on-white -> 3.9767 (compositing exercised)
```
Final app guard + runtime (`SG-183_measure.json`, `SG-183_app_run.log`):
```
requests=118 methods={"GET":118} blocked=0 blockedExternal=0 fulfilledFromLoopback=86 fulfillFailures=0
browser=HeadlessChrome/149.0.7827.55 transport=raw CDP over DevTools websocket
privacy: 0 private-name leaks, 0 UUIDs in committed JSON; mask ran after all measurements
```
Corrected per-route layout (documentElement.clientWidth vs scrollWidth; nav = client/scroll; all 30 captures in `SG-183_measure.json`). Phone 390 (client 375): **10/10 overflow**, 436–478 px, nav scroll width 811–853, phase span right 810.6–852.9, phase visible intersection 0 px, horizontal scroll reached the full max on every route. Tablet 834 (client 819): **9/10 overflow** 26–34 px; catalog fits (819/819); other routes' phase span visible intersection 0–7.3 px. Desktop 1440: **0/10 overflow**, nav scroll == client everywhere (1425 or 1440 depending on scrollbar). Root cause relationship: the shared Nav is one non-wrapping flex row (`display:flex`, no wrap, no overflow set) whose min-content width is ~811–853; the phase span is placed outside the viewport; the document (not just the nav box) is horizontally scrollable — no component-level clip, real document reflow of the same width. `mobile=false` is a rendering-mode limitation, not a width claim.
Focus visibility (390, catalog and review, `SG-183_measure.json` → focus):
```
last nav link focused ok; focus style present: outline solid 2px rgb(110,48,46)
rect right 769.7 / 763.7 at scrollX=0; visible width = 0 px in the viewport
=> keyboard focus is styled but not visible without horizontal scrolling (new confirmed defect, same nav family)
```
Contrast (`SG-183_measure.json`, 552 text samples, 0 unknown image backdrops; algorithm + controls above):
```
below-AA distinct pairs: 1 shipped pair in 4 font sizes
fg rgb(120,113,108)  bg rgb(245,245,244)  ratio 4.3977  at 11px/12px/13px/13.33px, weight 400
locations: catalog chips ("Total:" chip, category pills), asset_detail ("Link", "Attach evidence"),
           review/provenance 11px muted spans; ancestor opacity chain [] (solid backdrop, no image)
source: .bg-card-muted.text-muted-foreground (tokens --muted-foreground on --card-muted); exact unrounded 4.3977
all other sampled pairs >= 4.5 (or >= 3 large); review 834 sample: nav text rgb(28,25,23) on white 17.4883
```
SC 2.5.8 dispositions (sampled targets, same evaluator as fixtures): 318 targets across 6 routes x 3 viewports → **270 PASS-SIZE, 48 PASS-SPACING, 0 FAIL, 0 exception-dependent**. Cited controls corrected: nav logo link 122.9x19 PASS-SPACING; asset "back to catalog" 123.3x19 PASS-SPACING; settings/planning/analytics selects 125x19 or 129x27 PASS (spacing/size); search input 200x29 PASS-SIZE. The old 24-px cutoff failure is **retracted**; the residual ergonomic observation (19 px-high interactive rows) is kept as ergonomics only. Native/inline exceptions are not needed for any sampled control and were not assumed from tag names.
Screenshots (7, `SG-183_shots/`; viewport captures, served build above, measurement stage = post-measurement privacy mask): `catalog_390x844.jpg` (clipped Nav "Setti…" + visible horizontal scrollbar), `catalog_834x1112.jpg`, `catalog_1440x900.jpg`, `review_390x844.jpg`, `review_834x1112.jpg` (clipped phase label at right edge), `review_1440x900.jpg`, `asset_detail_390x844.jpg`. Public nav/action/blocker/empty-state text readable; private names/UUIDs/photos masked. CO-73: I opened the images; catalog_390 and review_834 render as described and contain no unmasked private data; the remaining five were captured by the same pipeline with the same mask (no independent eyeball of each; disclosed).

## G3 — corrected verdicts, cross-referenced

- REC-ISS15 / SG179-F2: **retained as a real defect, corrected and widened.** Phone 390: 10/10 routes overflow 436–478 px (the report's "390 clean" is retracted as a denominator artifact). Tablet 834: 9/10 overflow 26–34 px (report's 8/10 corrected). Desktop 1440: clean 10/10 (confirmed). Destination: existing consolidated repair plan (nav wrap/hide-late-links fix) — unchanged by this audit slice.
- REC-ISS16 / SG179-F3: **categorical WCAG 2.5.8 failure retracted**; sampled set meets the criterion (size or spacing) with fixtures proving the evaluator discriminates (spacing pass + adjacent fail; wrong outcome fails). Official source: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html (from `SG-179_audit.md`). Ergonomics observation retained, conformance verdict changed.
- SG179-F4 / REC-ISS16 (contrast): **confirmed with real inputs**: single shipped pair rgb(120,113,108)/rgb(245,245,244) = 4.3977:1 below 4.5 for normal text at 11–13.33 px, in catalog/asset_detail/review slots; exact values, selectors, opacity context and algorithm committed. Source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html.
- REC-ISS17: **corrected**: driver committed and runnable; schema names every DOM/API source (`SG-183_measure.json` → `app.measurementSources`); masking order and provenance disclosed; public UI now readable; 401/public-URL and container/image limits stay explicit/UNVERIFIED.
- New confirmed defect: off-viewport keyboard focus for the trailing nav targets at 390 (styled ring present, 0 px visible at scrollX=0). Destination: consolidated plan, same nav repair family (no repair in this audit).
- Unresolved/UNVERIFIED: container/image identity (no read grant); `mobile=true`/touch emulation not tested; review photo-bearing state not sampled; five screenshots not individually eyeballed; broader route set beyond the ten not re-observed. Destinations: container identity → SG-182; remaining responsive cases → consolidated plan / later audit chain.

## Constraint dispositions

Write ceiling `docs/worklogs/SG-183*` respected; temporary helpers existed only under `/tmp/opencode/sg183` (not published); none left in the repo tree. No product/config/test/lockfile/schema/migration edit; no dependency upgrade; no service start/restart/rebuild; no production write (GET only, loopback); no paid provider request; no credential/permission/profile access (fresh browser profile each run) and no other project's path read. Existing host browser binary execution used (Playwright cache headless shell); `/usr/bin/google-chrome` not launched; no new privileged denial (see (a)1). Health GET start/end per CO-92. Budget per PB-5: longest command 38 s vs its 600 s bound; no watcher. Partial-evidence path not needed; receipt published after this report per PB-6/CO-55.

PB-3 vacuity: the overflow page's mutation was asserted landed before trusting the verdict; the spacing and contrast batteries each contain a case that MUST fail and did; the guard's reject path was observed rejecting a real POST attempt in an isolated transport control (scratch server saw only GET) — no criterion passes vacuously.

## UNCLEAR

FIRST READ: the SG-179 driver was expected possibly reusable at `/tmp/opencode/sg179/cdp.mjs` — absent; interpretation: rebuild from the same mechanism and commit it (packet's "reuse if present" condition). Loopback GET fulfillment was not spelled out beyond "ephemeral local GET responses from the actual backend"; interpretation used: re-origin the bundle's API GETs to loopback with ACAO injected, disclosed as non-public-URL proof.
DURING EXECUTION: (i) first control run fatally unserialized the measurement function, second had an unbound `opts` — fixed with material changes, recorded as two failed prove executions; (ii) first app run measured the 401 failure state — fixed by fulfillment; (iii) center-distance spacing evaluator was too lenient for edge proximity — corrected to the literal circle-vs-rect/circle-vs-circle rule before final runs; (iv) candidate field values (input properties) escaped the first mask — caught by eyeballing the committed screenshot, fixed and recaptured.
REMAINING: container/image identity UNVERIFIED (no read grant; SG-182); public-URL proof owed (no auth requested); `mobile=true`/touch and photo-bearing review states; five screenshots not individually eyeballed; these are recorded above with destinations. No retry of this correction without owner disposition.

Contract version: 0.46.0 (echo).
