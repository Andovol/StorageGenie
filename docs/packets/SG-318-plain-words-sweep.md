# SG-318 — Plain words everywhere the screenshots caught developer text: catalog chips, the asset page's Details and History, the item panel's missing photo, nameless items, Inbox and Expiry

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write.
**Restart: none.** No deploy; a screenshot slice and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D18, D33 (*"D33 approved."*: the wording slice after SG-307); stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that."*

## Why this exists

Screenshots SG-313 and SG-316 (`docs/worklogs/SG-313_audit.md` I2, I5; `docs/worklogs/SG-316_audit.md` I19–I23; shots in `docs/worklogs/SG-312_shots/` and `docs/worklogs/SG-307_shots/`) show developer text an owner should never see. Locations are `UNVERIFIED` hypotheses — **establish each from the file before changing it**:

| # | Screen | What shows | Where (expected) | Plain version |
|---|---|---|---|---|
| W1 | Catalog card | raw keys `food_beverages`, `documents_other`, `non_perishable` | `frontend/src/components/catalog/ProductCard.tsx:227` `{item.category}`; the table view's chip in `ProductGrid.tsx` too | `labelAssetType` (`frontend/src/lib/labels.ts`), as the toolbar and panel already do |
| W2 | Asset page, Details table | `[object Object]` for *Shelf life* and *Expiry date*; raw `food_beverages`, `ACTIVE`, `ml`; rows all named *Detail* | `frontend/src/routes/AssetDetailPage.tsx` around `:817` | each value as the owner reads it (a date as *7 Nov 2026*, a category through `labelAssetType`, a status through the label map); each row named for what it is (*Kind of item*, *Status*, *Unit*) |
| W3 | Asset page, History | ISO stamps `2026-11-12T19:06:54.601245`; *Asset Create*, *Asset Accepted* | same file, around `:851` | the date format Inbox uses (*Today, 19:06* / *12 Nov, 19:06*); event names in plain words (*Added*, *Accepted*, *Date entered by you*) |
| W4 | Asset page | *Thumbnail unavailable* at 11 px | same file | ≥ 13 px, the words *No photo yet* (as Pantry and catalog) |
| W5 | Item panel | a broken-image icon and the alt text when the photo does not load | `frontend/src/components/shell/ItemInspectorDrawer.tsx:360`, `:373` | the same *No photo yet* placeholder as the catalog card, on load error too |
| W6 | Everywhere | *noname*, *Untitled asset*, *Unnamed item* | establish each source (`UNNAMED_ITEM` in `labels.ts:119` exists) | one word everywhere: *Unnamed item* |
| W7 | Expiry | ISO dates *2026-11-07 · Expiry date* | `frontend/src/routes/ExpiryPage.tsx` around `:252` | *7 Nov 2026 · Expiry date* (one shared date formatter for W2, W3, W7 — say which) |
| W8 | Expiry | a *Long lead* item under the *Safe* heading; tier pills repeating the heading | `ExpiryPage.tsx:32` `TIER_LABELS` | **show a tier pill only for *Use first* and *Use soon***; no pill for *Upcoming*, *Long lead*, *Safe* (the heading and *45 days remaining* already say it) |
| W9 | Inbox | *Saving: In progress* while the job only waits for review | `labels.ts:17` maps `PENDING` to *In progress* | `PENDING` → *Not started*; *In progress* only for running states |
| W10 | Inbox | *Validating input*, *Analyzing with ai*, *Building candidates* | `labels.ts:142` `STEP_NAME_LABELS` lacks them | *Checking your upload*, *Reading the photo*, *Making items* (your better words; say why) |

**Do not change** behaviour, routes, API calls, data, layout beyond what a word needs, or anything the table does not name.

## G0 — Preflight

```
mkdir -p output/SG-318-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-318-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-318/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-318/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** Scratch only in `output/SG-318-scratch/` (npm's cache there too). **No `/tmp` for anything.** Run every command from the repository root; give the build an absolute `--outDir "$PWD/output/SG-318-scratch/build"`. `git status --short` clean except `output/` before the report; `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — The words, W1–W10

In table order; commit after W1–W5 and again after W6–W10. A row whose fix needs a backend byte is reported and left — no backend file.

## G2 — Tests, FAIL-then-PASS, then the full gate

In `*.sg318.test.tsx`, one test per row at least: the rendered text has the plain word and **not** the old one (`food_beverages`, `[object Object]`, an ISO stamp, *Thumbnail unavailable*, a broken `<img>` with no fallback, *noname* / *Untitled asset*, *Long lead* pill, *In progress* for `PENDING`, *Analyzing with ai*). FAIL on base, PASS on candidate; logs `docs/worklogs/SG-318_fail.log`, `SG-318_pass.log` (names and first assertion only). Older tests asserting replaced wording updated, each named, **old → new quoted, none loosened**.

**The full gate, never skipped:** `eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof), `make frontend-test` (**0 failed — the whole suite, not only your files**), then every `*.sg318*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-318_<step>.log`, exact counts.

**Time rule: if G1 is not committed by 600 s by your stamps, commit what is done, mark the rest `REMAINING`, and run G2. G2 is never skipped for G1.**

## Acceptance criteria

- **A1** — W1–W10 each met or reported, the file named; the shared date formatter named.
- **A2** — G2 FAIL on base, PASS on candidate; older tests named old → new.
- **A3** — Gate green: eslint only the known error, the whole frontend suite 0 failed, host and image green; files twice green; exact counts.
- **A4** — Zero backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; tree clean except `output/`; scratch removed before the report.
- **A5** — Preflight; health 200 start and end; phase seconds from stamps.
- **A6** — `PB-3` vacuity: a failure would look like an old string still rendered, a test passing on base, a loosened assertion, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product:** `frontend/src/lib/labels.ts` (and a date helper beside it if one does not exist, named); `frontend/src/components/catalog/{ProductCard,ProductGrid}.tsx`; `frontend/src/routes/{AssetDetailPage,ExpiryPage,InboxPage}.tsx`; `frontend/src/components/shell/ItemInspectorDrawer.tsx`; `frontend/src/components/JobCard.tsx`; and only for W6, the file that produces *noname* or *Untitled asset*, named. **Displayed text and its styling only.** Any other product file is a STOP and report (`PG-EV-03`).
- **Tests:** new `*.sg318*` files; older tests only where they assert replaced wording, each named.
- **No backend file.**
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser.
- Evidence: `docs/worklogs/SG-318*` only. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2. Expected ≈950 s (`UNVERIFIED — my estimate`: ten small text changes ≈400 s; tests ≈150 s; SG-315's gate ≈200 s plus the twice runs).

## Report

Destination: `docs/worklogs/SG-318_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; W1–W10 one line each (premise confirmed or falsified with file and line, old → new words, file); test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-318`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-318 | Report: docs/worklogs/SG-318_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
