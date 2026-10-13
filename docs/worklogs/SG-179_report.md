# SG-179 — Recovery audit: user journeys and the actual deployed UI

SG-179 model=opencode-go/deepseek-v4.1-flash effort=max (read from own process args: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`, PID 1228655) cwd=/home/andrei/StorageGenie remote=git@github.com:Andovol/StorageGenie.git
BASE requested=`automation`; BASE resolved=`06ff99824c824257b23ed2aad673845d0b74fa46` (clean, equals origin/automation). WORK_HEAD=`631c5e2c51903435a50166224b7828d352d73cd4` (evidence commit; this report is the receipt commit that follows it).
Contract echo: 0.46.0 from `/home/andrei/storagegenie-contract/VERSION`; `RULES.sha256` = `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef` (matches the adopted 0.46.0 payload). Lane runtime budget: `RUN_BUDGET_S=2100` (from `/etc/dispatch/storagegenie.conf` via `DISPATCH.md` contract); actual elapsed **1437 s to report write** (13:09:44Z start health → 13:33:41Z report write; see health/runtime below), inside budget, no timeout kill occurred.
HEALTH: unchanged, OK (start 13:09:44Z `{"status":"ok","db":"ok","storage":"ok"}`; end `{"status":"ok","db":"ok","storage":"ok"}`, see SG-179_health.log).

## (a) Issues / deviations / surprises

1. **No privileged denial occurred; the known-denied Docker read was not attempted** (packet excluded it). Container/image identity/start remains **UNVERIFIED** — no alternate socket, identity, mount or sudo used (REC-ISS11 rule preserved). Served-bytes identity below is an independent axis, not container proof.
2. **Public URL observation limited by auth**: `https://storagegenie.dynv6.net/` answers `HTTP/2 401` with `www-authenticate: Basic realm="StorageGenie Restricted"` (nginx/1.24.0). No credential was sought or entered; the deployed frontend bytes were observed read-only on the loopback port the same service binds (`127.0.0.1:8003`, the health-granted path), and browser rendering was done on those served bytes.
3. **Harness deviations (disclosed)**: `/usr/bin/google-chrome` 150 crashes under this session's AppArmor state (zygote sandbox fatal, then crashpad); the host's pre-existing Playwright cache `chrome-headless-shell` 149 (host tool, no project dependency added) was used with a dependency-free raw-CDP driver. One frontend probe attempt failed on a harness mistake (`screen.unmount`), fixed once and re-run (`verification_attempt` 1 of 1 allowed; re-run count 1).
4. **Probe first run exposed a real failure path** (kept as evidence): running an import for an evidence row whose original file is absent yields `state=FAILED` with `errors=["quarantined: original missing at storage key ..."]` (T1F) — honest failure state, captured before the fixture file existed.
5. **REC-ISS02 confirmed non-vacuously**: an unchecked import creates a real `CREATED` job and **no Inbox control can run it**. Only production frontend caller of `/v1/imports/{id}/run` is `AssetImportModal.tsx:140` (checked branch); `InboxPage`/`JobCard` offer select + FAILED Retry only. Backend `/run` exists and works when called (probe T1). Disconnected transition recorded, not repaired.
6. **Tablet (834×1112) horizontal overflow 11–19 px on 8 of 10 routes**; offender is the trailing `Phase 0 · local-first` span in the shared Nav (measured `right` 845–853 > 834; catalog/inbox occasionally fit). Narrow phone 390 and desktop 1440 show no document overflow. The span is visibly clipped at the right edge in `SG-179_shots/catalog_834x1112.jpg`.
7. **Tap-target sizes below WCAG 2.2 SC 2.5.8 (24×24 CSS px)**: shared-nav link `StorageGenie` 123×19; selects/buttons 19–23 px high (settings select 196×19, planning/analytics selects 142×19, buttons 95×21 / 130×21, review Accept 60×23). Measured, `SG-179_browser_prod_results.json`.
8. **Contrast**: muted text at 11–13 px computes to 4.4:1 (catalog "Total loaded items: 7", card-muted/muted-foreground spans on catalog/asset/review) — below WCAG 2.2 AA 4.5:1 for normal text. Not a preference finding; computed values in the same JSON.
9. **Deployed build predates SG-175 (as held) and the separation was demonstrated**: served `main.js` still contains the pre-repair dedup-alert sentence and the rendered deployed review page shows the duplicate "Acceptance is blocked…" sentence inside the dedup alert; local source at BASE removed exactly that branch (diff `803cf52..06ff998`, CandidateCard.tsx). Local (UNSERVED) source behavior measured in probe T2 (live projection 409 → resolve → accept 200). No fix inferred for the deployed build.
10. **Still-unrepaired paths re-measured at this BASE** (probe T4): bare resolve of `expiry.manual_entry` returns 200 with zero expiry data; ACTIVE unclassified asset absent from expiry `rows` and `unresolved_rows`. Expiry page renders "No expiry items" + Uncategorized 7 — consistent, not a new defect.
11. **Capture vs import file types differ**: manual create accepts `image/*,.pdf` plus `capture="environment"` camera input; import modal accepts only `image/png,image/jpeg,image/webp` (no camera attribute). Source lines: AssetForm.tsx:196,211-212; AssetImportModal.tsx:209.
12. **Settings scope gap confirmed on the deployed UI** (REC-ISS03): model select + clear-household only; export exists as API (`/v1/export`) without a control; no privacy/storage/taxonomy/backup controls.
13. **Inherited limitations preserved, not re-probed**: SG-175 REC-ISS12/13/14 (uncaptured failed probe, names/sizes fingerprint, ephemeral benchmark vs engine clock) remain UNVERIFIED limitations owned by SG-180/182.

## (b) Actions (changed paths, commits, effects, counts, durations)

- Commits: `631c5e2c51903435a50166224b7828d352d73cd4` (evidence), plus this report commit; trailer `Dispatch-ID: SG-179` on both. Push of `automation` and the notes ref reported in the receipt/read-back lines below.
- Paths (all under allowed ceiling): docs/worklogs/SG-179_report.md, SG-179_probe.py, SG-179_probe_out.log, SG-179_inbox_probe.test.tsx, SG-179_fe_regression.log, SG-179_fe_probe.log, SG-179_be_regression.log, SG-179_deployed_bundle.log, SG-179_browser_prod_results.json, SG-179_browser_unauth_results.json, SG-179_health.log, SG-179_worklog.log, SG-179_shots/*.jpg (masked recaptures: text transparent, images blurred — privacy sanitisation stated; the transient vitest file was removed from the product tree).
- External/production effects: read-only GETs against the production backend (households/assets/jobs/review-tasks) and served bundle bytes; no production write of any method; probe built its own temp SQLite + temp storage root under /tmp; production DB hash `e6bef157…` unchanged before/after probe; both production evidence roots unchanged/absent; no restart/rebuild; no paid provider calls (fake provider forced, all keys nulled); no config/auth change. UNKNOWN: none.
- Test-command count: 3 (backend pytest once; frontend vitest twice: combined run, then probe re-run). Probe runs: 3 (1 failed before fixture file fix — kept; 1 diagnostic; 1 PROBE_OK). Provider-call count: 0 paid.
- Durations (box clock, UTC): start 13:09:44; first evidence commit ≈13:31Z; report write ≈13:33Z; total 1437 s against 2100 s budget as of this report write — the receipt-note publish follows the report and is the runner's record, not this report's. Longest single commands: deployed browser audit 30 navigations ≈ 150 s; masked recapture ≈ 150 s; probe ≈ 20 s; vitest ≈ 7 s; pytest ≈ 7 s.
- Highest-impact action: the isolated import-transition probe plus the Inbox render control, which converts REC-ISS02 from a source comment into a measured, non-vacuous disconnected transition.

## (c) Verification (summary blocks; full raw output committed)

Deployed bundle (read-only); renderer `HeadlessChrome/149.0.7827.55` (host Playwright cache build), screenshots masked; measurements from the deployed served bundle with API GETs fulfilled from the same service on loopback (non-GET blocked 405, zero blocked):
```
index.html sha256 2f035becd05b63e226af82e2e8fe60c8f3b5effb9f37e49dd95a2265c4da0d55 bytes=944
main.js    sha256 1b4680a0eddadff3c95a64b6bc00d744764d127a72cd5690ebea948b7664a29d bytes=322255
main.css   sha256 37b25dbdd4b0ecfdedb8255bc7f8af286726334e95a1a3a9e85b9ba381b3d57c
marker 'Acceptance is blocked until the open review task(s) are resolved.' count=1 (pre-SG-175 dedup sentence still served)
routes rendered: 10/10 at 390x844, 834x1112, 1440x900; unauth set additionally 1 route (silent "No households")
```
Isolated probe (real routes + real services, disposable /tmp SQLite + /tmp storage root, fake provider, prod DB/stores fingerprinted):
```
docs/worklogs/SG-179_probe_out.log: [RESULT] PROBE_OK, checks_passed=40
T1 unchecked import -> 201 state=CREATED no candidates (wrong COMPLETED expectation rejected)
T1 explicit /run -> 200 state=AWAITING_REVIEW candidates=1
T1F missing original -> 200 state=FAILED errors=['quarantined: original missing at storage key ...']
T2 live projection 409 blocked; resolve clears; accept -> 200 accepted (wrong accept=200 expectation rejected)
T3 manual expiry entry -> 200 resolved; accepted readback source=user (wrong-date expectation rejected)
T4 still-unrepaired: bare resolve zero-data; unclassified asset absent from expiry visibility
ISO prod_db_untouched=True; prod evidence stores untouched=True; provider=fake keys nulled
```
Focused regression controls (property each observes; exclusions named):
```
backend pytest tests/test_import_jobs.py tests/test_candidate_read.py tests/test_plugin_expiry.py -> 19 passed
  (properties: import run/retry state machine; candidate live-ID projection read path; expiry plugin classification/manual-entry)
frontend vitest import-modal.test.tsx shell.test.tsx ReviewPage.test.tsx InboxPage.test.tsx -> 52 passed
  (properties: modal process branches incl. unchecked create; shell/nav/toolbar render; ReviewPage blocked/pending paths; Inbox job select/retry)
frontend vitest __sg179__/probe.test.tsx -> 1 passed (CREATED job: no Run/start/Retry control; FAILED control shows enabled Retry)
  excluded by design: full suites, e2e directories, migration/backup suites (SG-182), live mutations
```
The probe's wrong-outcome controls are real failures observed and rejected (T1W/T2W/T3W in the log), and the Inbox probe has a known-working control (FAILED Retry) proving the selectors find controls when they exist.

## G1 — Route and story coverage matrix (state: working / partial / broken / absent / deferred / unverified)

Routes all render (shared Nav on every route; Catalog adds its toolbar/header section, not a duplicate nav — visual check `SG-179_shots/catalog_*.jpg`). Reachable surfaces inventoried: household selector (Inbox/Planning/Chat/Analytics/Capture/Expiry), import dialog (Catalog header), capture form + camera/file inputs, catalog facets/search/sort/save-search, item drawer (source), review workspace (fields, dedup alert, classify absent, expiry form), planning run + status filter, chat category + correction, analytics summary, expiry filter, settings model + clear household.

| Story | Start → action → expected outcome | Caller / API / readback | State at this BASE (scope) |
|---|---|---|---|
| REC-ST01 | open app → select household → catalog | Nav+Catalogue/`GET /v1/households`,`/v1/assets`; observed loaded 7 items | working (read-only); empty-household path shows "No households" honestly |
| REC-ST02 | capture/upload → see processing → reach review | Capture (image/*,.pdf+camera), Import modal (png/jpeg/webp); `/v1/imports`,`/run` checked; Inbox job detail | partial: both surfaces render; import only 3 file types; no camera on import; SEE REC-ST03 gap |
| REC-ST03 | import unchecked → run from Inbox → review | Modal help promises Inbox run; only caller is modal checked branch; `/run` exists | **broken (disconnected transition)**: CREATED job, no Run control (probe T1 + Inbox probe test) |
| REC-ST04 | open candidate → accept/edit/hold/reject with blockers | ReviewPage/CandidateCard; `/v1/candidates/{id}`,`decision`,`/review-tasks`; blocked 409 observed | partial: gate + blocked reason work; classification has no UI; deployed build predates SG-175 (duplicate reason still served); merge/split UI source exists (not exercised) |
| REC-ST05 | search/filter/sort → saved search reuse | Catalog + hooks; `/v1/assets`(q,cursor), facets, `/saved-searches` | partial: facets/search/save rendered; sort is page-local (source); multi-page population not exercised live (backend pagination tests pass) |
| REC-ST06 | inspect/correct details, evidence, provenance | AssetDetail; `/v1/assets/{id}`, assertions, `/evidence/*` GETs | partial read-only: rendered with real item (thumb fallback "Thumbnail unavailable"); writes not exercised |
| REC-ST07 | lifecycle/location/relations with history | AssetDetail sections; `/locations`,`/relations` source; settings flags default off (REC-ISS10) | unverified effective-state: sections render empty; no flag readback attempted |
| REC-ST08 | classify/enter unknown dates → correct states | Expiry page; classification API has no UI; manual entry via review expiry form; probe T3/T4 | partial: readback works (T3); classification absent (UI); bare resolve erases (T4); unclassified invisible (T4) |
| REC-ST09 | see urgency → complete the underlying task | Inbox tasks + Expiry; `/review-tasks` (2 live types) | partial: task list renders; live Inbox showed "No open review tasks" under Open filter while 8 tasks exist (status mix unverified); links per task type not exercised |
| REC-ST10 | run planning → confirm/dismiss proposals | Planning page + `/planning/run`,`/suggestions` | partial (not executed): UI + disclaimer + status filter render; no live trigger (generation excluded) |
| REC-ST11 | ask grounded question → correct answer | Chat + `/chat/{category}` | partial (not executed): UI + grounding/uncertainty copy render; persistence deferred per backlog |
| REC-ST12 | enrich → accept proposed fields | Asset Enrich button + WebAlternates + spend cap display; `/enrich/{id}` | partial (not executed): control + cap text render; per-field acceptance deferred |
| REC-ST13 | read analytics vs generated | Analytics + `/analytics/summary` | working read-only: numbers rendered (7 assets; all no-date; categories 0/Uncategorized 7); summary generation not triggered |
| REC-ST14 | settings/privacy/export/backup | Settings; `/settings/ai` | partial: model select + clear household only; export API-only; privacy/backup absent (REC-ISS03) |
| REC-ST15 | same journeys narrow/wide, keyboard, states | all routes at 3 viewports; Tab traversal | partial with defects: tablet overflow (8/10), tap targets 19–23 px, muted contrast 4.4:1; focus rings solid 2px observed across nav/buttons; 390/1440 clean |

Deferred/rejected preserved: Scheduled planning (deferred), push reminders (UV-4 in-app only), per-field acceptance + chat persistence (deferred), asset_type fallback grounding (rejected D-1012-10), Context Scene UI wiring (parked D-1012-6). No phase marker counted as a journey; API presence noted separately from UI callers (classification, export).

## Findings (status, severity judgement, root-cause hypothesis, story, smallest repair scope proposal — no repairs performed)

| ID | Finding | Severity | Root cause hypothesis | Story | Smallest repair proposal |
|---|---|---|---|---|---|
| SG179-F1 | Unchecked import creates CREATED job with no way to run it from the UI | HIGH (broken promise) | Help text written for a Run control that was never added to Inbox/JobCard | REC-ST03 | Add a Run action on CREATED JobCard calling existing `/run` + Inbox probe test |
| SG179-F2 | Tablet 834px nav overflow/clipped Phase span | MEDIUM | Single non-wrapping flex row with `margin-left:auto` trailing span | REC-ST15 | Make shared Nav wrap or hide the phase label under a width media query |
| SG179-F3 | Tap targets 19–23 px (<24 WCAG 2.5.8) | MEDIUM (AA) | Inline compact styles (padding 6px 10px, font 13) | REC-ST15 | Raise control min-height/padding via existing tokens; no structural change |
| SG179-F4 | Muted text 4.4:1 (<4.5 AA) at 11–13 px | LOW–MEDIUM | Token pair slightly under ratio on light theme | REC-ST15 | Darken `--muted-foreground` one step; verify computed ratio |
| SG179-F5 | Deployed review still shows duplicate blocked sentence (pre-SG-175) | LOW (cosmetic while blocked) | Served build predates held SG-175 candidate | REC-ST04 | None now — deployment decision on SG-175 is separate and flagged |
| SG179-F6 | Classification has no UI; bare Resolve erases expiry task; unclassified items invisible | HIGH (journey gaps) | Known SG-173 diagnosis; repair grants SG-176–178 pending plan | REC-ST08/09 | Per approved D-1012-14 chain (separate scope) |
| SG179-F7 | Import accepts fewer file types than manual capture (no PDF/camera) | LOW | Modal `accept` narrowed to 3 image types | REC-ST02 | Align accept list with manual form if product intends parity |
| SG179-F8 | Settings exposes only model + clear household; export API-only | MEDIUM (scope gap) | Blueprint §11.1 scope not delivered in UI | REC-ST14 | Reconcile scope first (register item), then add controls per decision |
| SG179-F9 | Unauthenticated/API-failure state renders as "No households" with no error message | MEDIUM (truthfulness) | Empty-state chosen when queries fail; no error branch on households | REC-ST01/15 | Show an error state when households request fails |

## Minimal reuse direction (short table; no rewrite in this slice)

| Option | What it reuses | Cost | What it replaces |
|---|---|---|---|
| A (recommended): consolidate existing shell/tokens | Shared `Nav` + `AppShell`/tokens.css; add wrap rule, one token contrast step, min-height for controls | Small CSS + Nav JSX (one slice) | Ad-hoc inline paddings; tablet overflow; two contrast/tap-target classes of findings |
| B: single app-wide header | Replace shared `Nav` + catalog toolbar split with one AppShell header owning search/import/household context | Medium (route-level refactor, regression surface) | Duplication between Nav and catalog header; no measured defect requires it now |

## Constraint dispositions

- Write ceiling respected (only docs/worklogs/SG-179* + transient probe test removed before publish); canonical register untouched.
- No product/config/test/lockfile/schema/migration edits; no dependency upgrades; no new auth; no service start/restart/rebuild; no production POST/PUT/PATCH/DELETE (browser harness blocked non-GET with 405; zero blocked); no direct DB writes; no evidence-store writes; no imports/resolving against live data; no paid API requests.
- Disposable isolation: temp SQLite + temp storage root created before first write; provider forced `fake`; all keys nulled; dependency override captured and popped; prod DB hash and both store fingerprints unchanged (probe ISO block).
- Health start/end GET per CO-92: unchanged, OK (SG-179_health.log).
- Budget: 2100 s lane budget; visible command timeouts (ordinary 120 s / isolated 600 s per packet; node/browser runs capped at 300–380 s); no command killed by timeout; no idle kill.
- Focused controls only; no full-suite/e2e run; node IDs named above with properties and exclusions.
- No silent truncation: every route/story above has an observation or an explicit UNVERIFIED reason; remaining gaps listed under REMAINING with destinations.

## UNCLEAR

FIRST READ: the packet's premises matched the tree except (i) public-URL proof is impossible without credentials — substituted with loopback served-bytes rendering, clearly labelled; (ii) Docker identity excluded — identity fields reported UNVERIFIED; (iii) SG-175 separation is provable only for the frontend half (bundle marker + render), backend-half separation rests on the code hold, not a runtime read of the container.
DURING EXECUTION: probe first run failed on a missing original (kept as T1F evidence; fixture file then added); frontend probe attempt 1 failed on harness misuse (screen.unmount), fixed and re-run (1 re-run). Deployed review page's live `review_task_ids` cannot be inspected without mutation; only the rendered blocker string was observed.
REMAINING: REC-ST05 multi-page/saved-search lifecycle; REC-ST07 effective location/relation flags; REC-ST09 task-type link destinations (fixture-limited); REC-ST10/11/12 generation paths (excluded, no paid calls); REC-ST02 error/retry UI per-file-type matrix; container/image identity; SG-175 backend-half deployed separation. Destinations: SG-181 (API/domain), SG-180 (ingestion/providers), SG-182 (ops/test-trust), and the consolidated repair plan; container identity to stays UNVERIFIED without an approved grant.
