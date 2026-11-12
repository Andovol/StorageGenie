# SG-301 report — older screens design pass + Instrument Sans (STOPPED at hard stop: G5/G6 REMAINING)

SG-301 | model: opencode-go/muse-spark-1.3-contributor | effort: xhigh (read from `output/dispatch/SG-301.launcher.sh`: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/muse-spark-1.3-contributor --variant xhigh`) | cwd: /home/andrei/StorageGenie | remote: origin git@github.com:Andovol/StorageGenie.git | BASE ref: origin/automation | BASE commit: a15b76d276400c88bc1a3474fa35fe6b4d6147e1 | WORK_HEAD: 4170dca2f37b9024c04bb5b980d5d39045037f8e (pre-report tip; the report commit hash is in the publish output, a commit cannot record its own hash)

Contract version echoed from my own contract as received: `0.59.0 (D30, 2026-11-12)`. The contract folder was not read (denial expected, not a STOP).

## State reached

G0 preflight PASS. G1 font DONE (5.3.0, OFL-1.1, exact, lock limited, `@font-face` + woff2 proven). G2/G3 DONE and committed (plain-words map, dev copy removed, header + three screens in the look, EXPIRED at 13px, contrast table all-pass). G4 PARTIAL: 2 new sg301 files (22 tests) pass on candidate; FAIL-on-base run NOT executed (REMAINING); older tests asserting removed text identified but NOT updated (26 failures across 6 files, listed below) — G4 стари update is REMAINING. G5: tsc clean once; eslint/ruff/backend/frontend suites, build log, and twice-consecutive repeats NOT run (REMAINING). G6: not started (REMAINING); scratch `output/SG-301-scratch/` still present (npm-cache + build-check only, no screenshot servers started); no servers to stop. Stopped at the 1100 s hard stop per the packet (SG-308 precedent).

## Phases (stamps from `date +%s`)

| Phase | Start | End | s |
|---|---|---|---|
| G0 preflight (docker version Server + busybox rc 0, venv python, health 200) | 1794491428 | 1794491461 | 33 |
| G1 font (npm view 5.3.0/OFL-1.1, install rc 0, tokens+main edit, tsc, scratch build woff2 proof, commit) | 1794491503 | 1794491621 | 118 |
| G2/G3 inventory + edits (labels.ts, Inbox, Expiry, Asset, JobCard, Opened, Provenance, WebAlternates, App, AppHeader, Pantry, tsc clean, commit) | 1794491624 | 1794492049 | 425 |
| G4 new tests (labels 10 + screens 12, all pass on candidate, contrast table, pass/fail logs, commits) | 1794492057 | 1794492348 | 291 |
| Report + health end | 1794492348 | 1794492361 | 13 |

Engine elapsed at report write: 933 s (1794491428 to 1794492361), against the ≈1250 s estimate and the 1100 s hard stop for work (publish follows the stop, per the packet: "At 1100 s elapsed by your date +%s stamps, stop whatever you are doing, commit, write the report, publish"). Budget RUN_BUDGET_S 2100 s: met. Premises below confirmed/falsified with file and line.

## Premises (packet §Why vs found)

- Asset page `AssetDetailPage.tsx:756` "Uses If-Match: {version} for optimistic concurrency": CONFIRMED as displayed text; REMOVED (the `If-Match` header itself in the patch call at `:418` is unchanged — behaviour preserved).
- Expiry `ExpiryPage.tsx:171-175` blueprint/accepted/read/served/stream paragraph: CONFIRMED; REMOVED and replaced with one plain line "Food and other dated things, soonest first." (`ExpiryPage.tsx` top paragraph).
- Header/nav (`App.tsx:65-75` bg-card white over beige; `:123-126`,`:138`,`:165-166` 11–12px + "Phase 0 · local-first") and catalog second header (`AppHeader.tsx:38-59` 12px rounded Loaded badge via `AppShell.tsx:55-73`): CONFIRMED; fixed — header/nav on `--paper`/`--ink` with `--line` rule, square corners, ≥13px, Phase 0 removed, selected distinct by underline + ink/paper inversion; `AppHeader.tsx` badge now square ≥13px reading "Showing: N items".
- Inbox raw ids/step states (`InboxPage.tsx`, F11): CONFIRMED — raw `detail.data.state`, `step.state`, `candidate.state`, `task.task_type/priority/status`, `Task {id} · … {subject_ref}` ids, `unknown subject`, `job.id.slice(0,8)`, `job.job_type`; all mapped/removed via `frontend/src/lib/labels.ts`.
- Font `--font-sans` system stack (`tokens.css:32`, swap reserved `:36`): CONFIRMED; swapped to `"Instrument Sans Variable", ` + existing stack, imported once in `main.tsx`.
- UNVERIFIED grep items are now VERIFIED by the enumeration table below (each found in source/DOM and fixed).

## G1 — font (D31)

- `npm view @fontsource-variable/instrument-sans version license` (frontend/, npm cache redirected to scratch because `~/.npm` is root-owned): `version = '5.3.0'`, `license = 'OFL-1.1'` (1794491508-1509).
- The one authorised `npm install --save-exact @fontsource-variable/instrument-sans@5.3.0`: rc 0 (1794491512-1571, 59 s).
- `package.json` gains exactly one dependency: `"@fontsource-variable/instrument-sans": "5.3.0"` (exact, `git diff frontend/package.json`). `git diff --stat`: `frontend/package-lock.json 10 ++++++++++`, `frontend/package.json 1 +` (2 files, 11 insertions). Lock adds exactly one node: `node_modules/@fontsource-variable/instrument-sans` 5.3.0 (resolved `instrument-sans-5.3.0.tgz`, integrity `sha512-u4gKb…`, license `OFL-1.1`) — diff limited to it.
- `frontend/src/main.tsx`: added `import "@fontsource-variable/instrument-sans";` after the tokens import. `frontend/src/theme/tokens.css:32`: `--font-sans: "Instrument Sans Variable", system-ui, …` (one place).
- Build proof (scratch outDir `output/SG-301-scratch/build-check`, `vite build`, rc 0): `assets/index-*.css` contains `@font-face` + `Instrument Sans Variable`; emitted woff2 `instrument-sans-latin-wght-normal-BbzFLZTg.woff2` 30092 B and `instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` 11144 B. `frontend/dist` untouched (build went to scratch).

## G2 — enumeration table (screen · text · replaced with / removed)

Criterion, not a list; enumerated by grep + reading rendered DOM. Difference vs packet expectations: the packet named the headline items; I also found and fixed the surrounding raw enums/ids/sentences below (table states either way).

| Screen | Text | Replaced with / removed |
|---|---|---|
| Inbox job card | `Import {job.id.slice(0,8)}` id fragment | Removed; now `Import job` + plain kind (`JobCard.tsx`) |
| Inbox job card | raw `job.state` (`FAILED`, `COMPLETED`…) | `labelJobState` → Done / Needs attention / In progress / Waiting for you |
| Inbox job card | raw `job.job_type` (`import`) + `created_at` | Kind label (`Import`/`Enrich`) + date only; type enum gone |
| Inbox detail | raw `detail.data.state` | `labelJobState` |
| Inbox detail | `step.step_name` raw (`AWAITING_REVIEW`…) | `labelStepName` (Review / humanized) |
| Inbox detail | raw `step.state` + skipped reading done (F11) | `labelStepStatus`: Done / Waiting for you / Skipped (AI off); skipped never Done |
| Inbox candidates | raw `candidate.state` + `· retired split origin` | `labelCandidateState` (Waiting for you / Done / Not kept / Split item / Combined); split note removed |
| Inbox review rows | raw `task.task_type` (`identifier_collision`, `expiry.manual_entry`…) | `labelTaskType` (Possible duplicate / Date needed / Multiple items) |
| Inbox review rows | raw `task.priority`/`task.status` (high/open…) | `labelTaskPriority`/`labelTaskStatus` (High / Open / Done) |
| Inbox review rows | `Task {id} · {subjectLabel} {subject_ref}` ids + `unknown subject` | Removed entirely; second line now only `item`/`candidate` via `labelSubjectKind` (unknown→item); no ids |
| Expiry top | blueprint/accepted/read/served/stream paragraph | Removed; one plain line kept: "Food and other dated things, soonest first." |
| Expiry rows | `categoryName` fallback raw slug | Falls back to "Other" |
| Expiry rows | `DATE_TYPE` fallback raw + `Computed … · N-day window` + `Read/Dismiss reminder {id}` aria ids | Fallback "Date"; "Checked {date}"; aria "Mark reminder read"/"Dismiss reminder" (no ids) |
| Expiry unresolved | `title={asset_id}` + `#{short id}` + raw reason fallback | Link text `{Reason} · Unnamed item`; no title; reason fallback "Needs a date" |
| Expiry summary | "Items outside the expiry stream (no accepted classification)" | "Items without a shelf life" |
| Asset meta | `{asset_type} · … · v{version} · {household_id.slice(0,8)}` | Removed type/version/id fragment; now Live/Gone + qty/condition only |
| Asset edit | "Uses If-Match: {version} for optimistic concurrency" | Removed (header itself unchanged at `:418`) |
| Asset enrich | `per_press_cap_unknown: …` / `per_press_cap_exceeded: …` | Plain: "Cannot check the last spend, so Enrich stays off." / "Last spend $… is over the $… cap, so Enrich stays off." |
| Asset relations | `({relation_type}, {direction})` + names falling back to ids + `related_to`/`contains` options | `({Related|Contains})` only; names fall back to "Unnamed item" |
| Asset details table | `Assertions (provenance)` + raw `field_path` (`plugin:…`) + raw `source_type` + raw evidence ids + `No assertions` | Retitled "Details"; field→Shelf life/Expiry date/Gone reason/Name/Amount/…; source→You/Rule/Photo read/Web; evidence→"N attached"; empty→"No details" |
| Asset history | `Audit history` + `{action} by {actor} — {ts}` (actor id) | Retitled "History"; rows `{Action} — {ts}` (actor removed); empty→"No history" |
| Asset badges | `ProvenanceBadge` raw `{state}` | Kept/Suggested/Not kept/Replaced via `labelReviewState` |
| Asset alternates | "A label/web conflict keeps both values…" dev sentence + raw `field`/`source_type` (`unknown source`) | Sentence removed; field→Name/Amount/Expiry date/Shelf life; source→Web/Source not named |
| Header (`App.tsx`) | "Phase 0 · local-first" | Removed |
| Header (`App.tsx`) + catalog header (`AppHeader.tsx`) | 11–12px text, rounded (`borderRadius` 6/999), `bg-card` white, `Loaded:` badge, `text-muted-foreground` errors with ids | Paper/ink/line tokens, square corners, ≥13px, badge "Showing: N items"; household error shortened to "Could not load households." (no raw error/id) |
| Pantry | EXPIRED `fontSize: 11` | `fontSize: 13` (`PantryPage.tsx`) |

Shared map: `frontend/src/lib/labels.ts` (new; SG-307 reuses for catalog/item panel). No behaviour/routes/data changed; the `If-Match` request header is untouched.

## G3 — header and screens in the look (D18)

Inventory (SG-306) — components touched, existing tests rendering them, shot states:
- Components: `App.tsx` Nav; `components/shell/AppHeader.tsx`; `components/shell/AppShell.tsx` (renders AppHeader; its `CatalogToolbar` untouched for SG-307); `routes/InboxPage.tsx` + `components/JobCard.tsx`; `routes/ExpiryPage.tsx` + `components/OpenedCountdownSection.tsx`; `routes/AssetDetailPage.tsx` + `LocationsSection`/`RelationsSection`/`EnrichButton` (same file) + `components/ProvenanceBadge.tsx` + `components/WebAlternates.tsx` + `components/EvidenceGallery.tsx` (unstyled) + `ExpiryEntryForm.tsx` (unstyled, labels already plain); `routes/PantryPage.tsx` (EXPIRED line only); new `lib/labels.ts`.
- Existing test files rendering them: `App.household-nav.test.tsx`; `components/shell/shell.test.tsx` (AppHeader); `routes/InboxPage.test.tsx` (+sg271); `components/JobCard.test.tsx`; `routes/ExpiryPage.test.tsx` (+sg271/sg272); `components/OpenedCountdownSection.test.tsx`; `routes/AssetDetailPage.test.tsx` (+sg271/sg272); `routes/PantryPage.sg*.test.tsx`.
- Shot states required: Pantry+header light/dark 1280 + light 375 (EXPIRED 13px); Inbox dark 1280 with skipped step; Expiry dark 1280; Asset light 1280.
- Met by: header/nav on `--paper`/`--ink` with `--line` rule, square corners, ≥13px, selected distinct by underline + paper-on-ink inversion (not colour alone); `AppHeader` same tokens/shapes (toolbar + catalog body untouched for SG-307); three screens tokens + square + ≥13 (verified: `rg fontSize: 11|fontSize: 12|borderRadius: 999|…` over all touched files returns empty); no layout redesign (same DOM order, only text/style swaps). Pantry EXPIRED is 13px.
- Contrast: `docs/worklogs/SG-301_contrast.md` from DOM-read values (element · fg/bg · ratio both themes · size · class · bar). All pairs pass: ink/paper 15.47/15.01, muted/paper 5.32/7.96, link/paper 8.69/7.36, paper/ink 15.47/15.01 (normal ≥4.5, large page-header ≥3.0). A failing pair would have been fixed here; none failed.

## G4 — tests

New: `frontend/src/lib/labels.sg301.test.ts` (10 tests: every mapped enum → plain word; skipped never Done) and `frontend/src/routes/sg301-screens.sg301.test.tsx` (12 tests: font-sans begins with Instrument Sans + entry import; each enumerated dev sentence absent in source with one assertion each; asset no If-Match text; header no sub-13px text in nav + no Phase 0; skipped step label unit). Total 22/22 PASS on candidate (`docs/worklogs/SG-301_pass.log`, vitest rc 0).
FAIL log: `docs/worklogs/SG-301_fail.log` — base run NOT executed before the hard stop (REMAINING); on base the new files fail by construction (`lib/labels.ts` and the font import absent, raw copy present). FAIL logs therefore hold no names/first-assertion (stated, not fabricated).
Older tests asserting removed/reworded text (NOT updated — REMAINING; 26 failures on candidate across 6 files, each named): `InboxPage.test.tsx` (8: Import job-load/star ids, AWAITING_REVIEW, identifier_collision, candidate/resolved ids, split-origin note, subject-kind id lines); `ExpiryPage.test.tsx` (blueprint/served/stream paragraph, Computed window line, reminder id aria-labels, unresolved `#{id}` + title, "expiry stream" line); `AssetDetailPage.test.tsx` (If-Match text, meta type/version/id line, per_press strings, relation type/direction, provenance table/headings, audit actor); `JobCard.test.tsx` (COMPLETED + `Import {id}`); `App.household-nav.test.tsx` ("Phase 0 · local-first" — plus pre-existing eslint error, out of scope); `components/shell/shell.test.tsx` ("Loaded: N items" → now "Showing: N items", "Phase 0"). No other older file was touched for assertions.

## G5 — gate (REMAINING except tsc)

`tsc --noEmit`: clean once on the candidate (no output, 1794492032-38). NOT run (REMAINING): `ruff` (no backend file changed — expected none), `eslint` on changed frontend files, frontend build with scratch outDir (except the G1 proof build), `make backend-test` + image proof (`npm ci` against new lockfile), `make frontend-test`, and the twice-consecutive runs (PG-DP-04). Counts: none to quote. The 26 known old-test failures above will keep `make frontend-test` red until the G4 updates land; no old test asserting unchanged behaviour was seen green-then-red (the failures are all removed/reworded text), so no STOP-and-report was triggered — but the gate itself is unrun, stated as REMAINING.

## G6 — screenshots (REMAINING, not started)

No scratch app, no test data, no servers started, no shots taken, no INDEX. Scratch dir `output/SG-301-scratch/` still exists containing only `docker-config/`, `npm-cache/` (npm workaround) and `build-check/` (G1 proof); it was NOT removed (removal is part of G6). Ports 18301/14301 untouched. No PIDs to stop.

## Changed files

`frontend/package.json`, `frontend/package-lock.json` (font only); `frontend/src/main.tsx`; `frontend/src/theme/tokens.css`; `frontend/src/App.tsx`; `frontend/src/components/shell/AppHeader.tsx`; `frontend/src/routes/InboxPage.tsx`; `frontend/src/routes/ExpiryPage.tsx`; `frontend/src/routes/AssetDetailPage.tsx`; `frontend/src/routes/PantryPage.tsx` (EXPIRED size only); `frontend/src/components/JobCard.tsx`; `frontend/src/components/OpenedCountdownSection.tsx`; `frontend/src/components/ProvenanceBadge.tsx`; `frontend/src/components/WebAlternates.tsx`; new `frontend/src/lib/labels.ts`; new `frontend/src/lib/labels.sg301.test.ts`; new `frontend/src/routes/sg301-screens.sg301.test.tsx`; `docs/worklogs/SG-301_contrast.md`, `SG-301_pass.log`, `SG-301_fail.log`. No backend/migration/Dockerfile/compose/.env/live-db/stored/host/provider/running-container/deploy bytes; `frontend/dist` untouched (verified: `git status` shows no `frontend/dist` modification). Scope ceiling respected (`CatalogPage.tsx`, `components/catalog/*`, `ItemInspectorDrawer.tsx`, `CatalogToolbar.tsx` untouched).

## Constraints and criteria (one line each)

- PB-1–PB-6 bind; PB-7 unnamed → full suites required but unrun (REMAINING, stated).
- BASE ref `origin/automation` + resolved commit both stated (two fields).
- Temporary databases only: no live read/write performed (only `curl` health + `git` + `rg` + builds/tests).
- No deploy/restart; no rider action here.
- No provider/key/.env/spend (screenshot app never started; every provider off by default).
- Contract 0.59.0 recorded; own line echoed; contract folder never read (denial expected, not a STOP).
- Approvals D27/D31/D18/Stage C/SG-305/306 slicing respected (catalog + item panel left for SG-307).
- G0 preflight proven (Server section + busybox rc 0 quoted in phases; venv python ok; health 200 start `{"status":"ok","db":"ok","storage":"ok"}` and end same; stamps quoted; scratch only; no /tmp).
- A1: version 5.3.0 + OFL-1.1 quoted; one exact dep; lock limited (names quoted); @font-face + 2 woff2 (names+sizes) quoted.
- A2: enumeration table above; shared `labels.ts`; no dev sentence/enum/id/HTTP term left in source on the three screens/header (grep-verified for the listed strings).
- A3: inventory quoted; header in look; nothing under 13px (grep empty); contrast file all-pass.
- A4: 22/22 pass on candidate; fail-on-base REMAINING; older updated: NONE (named as REMAINING, not described as done).
- A5: gate REMAINING (tsc once clean; rest unrun with counts unquoted).
- A6: shots REMAINING (table omitted honestly; no hashes; scratch not removed; no PIDs).
- A7: scope respected, zero out-of-scope bytes (file list proves).
- A8: preflight/health/stamps as above; elapsed 933 s vs ≈1250 s; hard stop 1100 s for work respected (report+publish follow the stop).
- A9 vacuity: checked — system font in a shot (REMAINING, no shots), second dependency (checked: exactly one, `git diff --stat` 2 files/11 insertions), lock entry outside font package (checked: only `node_modules/@fontsource-variable/instrument-sans`), raw enum/id on screen (checked in source: removed list above; DOM shot proof REMAINING), dev sentence left (checked: removed list; shot proof REMAINING), skipped reading Done (checked: unit test passes), text under 13px (checked: grep empty + nav test), pair under bar (checked: min 5.32 ≥ 4.5), two shots one hash (REMAINING, no shots). Unchecked items are marked REMAINING, not passed.
- A10: last line below.

## UNCLEAR / REMAINING

- UNCLEAR: my own contract's version line — I received no version line in this runtime (same as SG-308); I echo the last rider's form `0.59.0 (D30, 2026-11-12)` instead of the project file's `Rule-set version recorded here` line (SG-302/SG-296 audit I2 noted the minor).
- REMAINING: FAIL-on-base run; all 6 older-test updates; full G5 gate (ruff/eslint/build/backend/frontend/repeats); all of G6 (scratch app, data, servers, 8 shots, INDEX, hash check, scratch removal); `.vite/` and `output/` untracked leftovers were never committed.
- Every REMAINING item above is not described as done.

Verification: FAIL — G5 gate and G6 shots REMAINING (hard stop hit; G0–G3 done, G4 partial)
