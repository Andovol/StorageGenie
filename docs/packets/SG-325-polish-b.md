# SG-325 — Polish B: use-by date in the catalog, no date lost on a duplicate, theme controls and plain words on capture and review

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: this slice is frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner, 2026-11-16: *"Then … polish B on Muse (P8+P13, P9–P12, listed in STATE)"*; D35; D18 and the owner's standing words: *"design, look and feel are very important."* Stage C (*"d14 ok"*, L3).

## Why this exists

The owner's shelf trial is next. Before it, the owner must be able to tell two packs with one name apart in the catalog, must not lose a date on a duplicate photo, and must not meet developer words on the two screens every new item passes through. Sources: `docs/worklogs/SG-319_audit.md` (P8), `SG-321_audit.md` (I9, I10), `SG-321r1_audit.md` (I18, I19), `SG-304r2_audit.md` (I4, gap G-1). Polish A (SG-324, gated by SG-324r1) is on this base; do not redo it.

Locations are `UNVERIFIED` hypotheses — **establish each from the file before changing it** (`PB-1`), and report any that is wrong. Wording below is the owner-facing text to use exactly; where you must add a word not given here, say which and why.

| ID | Where | Change |
|---|---|---|
| **P9** | Review card, duplicate | *Save edits* shows on a duplicate (`components/CandidateCard.tsx:147-155`, not gated by `isDuplicate`); it posts `edit` and the commit then takes the duplicate path, so an edited date is lost (G-1). **Hide *Save edits* when `isDuplicate`**, as *Accept* and *Hold* already are. Prove the edited values still travel with *It's another pack* (`onDecision("accept", values, { asNewPack: true })`, `:96`). |
| **P8 + P13** | Catalog table and cards | The *Status* column says *Photo only* for every item (`components/catalog/ProductGrid.tsx:45`, `:197-217`); same-name packs cannot be told apart. **Replace the *Status* column with *Use by*:** each row shows its date in the form `lib/labels.ts` already uses for dates (e.g. *6 May 2030*), or *No date*. Read dates the way the Pantry does — the asset list joined with `fetchExpiryStatus` (`api/client.ts:375`; Pantry's join `routes/PantryPage.tsx:256-271`), **no category**, so every module's items get their date. The card view (`ProductCard`) shows the same date in place of the status badge. Establish where the catalog builds its rows (`routes/CatalogPage.tsx`, `types/product.ts:93` `assetToProductItem`) and say where the date joins. If the status read without a category does not return every dated item, that is a STOP for this item. |
| **P10** | Same-name warning, capture form | SG-321 measured the warning's buttons as browser-default grey, **2.02:1 in dark**. The current code may already differ (`components/AssetForm.tsx:305-336` shows `text-link`; the preview *remove* button `:295` is unstyled, `fontSize: 11`). **Establish what renders now**; give every button in the warning and the preview *remove* the theme's control style (`THEMED_CONTROL_CLASS` / `CONTROL_STYLE`, as `CandidateCard.tsx` uses), light and dark, 13 px or more. The duplicate card's three choices (`CandidateCard.tsx:95-106`) already use it — confirm, change nothing there. |
| **P11** | Capture form | Heading *Capture — Manual Create* (`routes/CapturePage.tsx:21`) → *Add an item*. Button *Create asset* / *Creating...* (`AssetForm.tsx:342`) → *Add to catalog* / *Adding…*. Hint *Left blank, we use the photo's filename* at 11 px (`:206`) → *Leave it blank and we use the photo's file name* at 13 px. *Kind of item: unknown* (establish where; near `:209`) → *Kind of item: not chosen yet*. |
| **P12** | Review card | (a) Heading *Candidate <id>* and the line *State: … · Job: …* (`CandidateCard.tsx:86`) → heading *Check this item*, no id, no state or job line; drop the *Candidate review* tag (`:87`). (b) *Possible duplicates or collisions* (`:91`) → *This may already be in your catalog*. (c) *This match is advisory; review it before accepting.* (`:108`) → remove it. (d) Section headings *Candidate fields* → *What we read*, *Source evidence* → *Photo*. (e) Field labels: every key gets a plain label (`FIELD_LABELS`, `:38-41`; today unknown keys show raw, e.g. `display_name`, `expiry_date`, `status`): *Name*, *Use by*, *Status*, and plain words for any other key you find in the API's candidate shape — name each. A value with a label in `lib/labels.ts` (e.g. `ACTIVE`) shows that label. (f) The use-by field is a date field (`type="date"`), so the browser shows the viewer's date order, not `2032-06-18`; its value posted stays `YYYY-MM-DD`. (g) The *Confidence: … · Source: …* line (`:120`, 11 px) is 13 px; source words come from `lib/labels.ts` if a label exists, else name the raw words you leave. (h) No evidence id shown under the photo. Inputs keep an accessible name — use the plain label. |

**Not in this slice:** P2 (native date order follows the browser language — owner-settled), any backend change, any new route.

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-325-scratch/docker-config output/SG-325-scratch/logs output/SG-325-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-325-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-325/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-325-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-325-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-325/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-325-scratch/`** — logs, captures, the build. **Never `/tmp`, for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-325-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — The changes, one item per step

Do **P9, P8+P13, P10, P11, P12, in that order** (the trial needs the first two most; P12 is the most droppable), one item per step, and **commit each item as soon as it is done** (`SG-325 P9: …`). Each commit holds that item's product change **and** its test in `frontend/src/**/*.sg325.test.tsx` (one file per item, or one shared file extended per item — say which). Each test fails without the change and passes with it: **write the test first and run it (FAIL), then change the product file and run it again (PASS)**; log names and first assertion to `docs/worklogs/SG-325_fail.log` and `SG-325_pass.log`. **Older tests asserting replaced wording or labels are updated in the same commit, each named, old → new, none loosened** — SG-324 left eight such tests red for its gate to find; find yours before committing by running every older test file that renders the component you changed.

**Tests read what the user sees:** query by role and visible text, and feed a component **the shape the API sends** — copy it from an existing test that uses the API client or a captured response; never a hand-made object missing fields the API always sends (SG-304's lesson). For P8+P13 feed both the asset list page and the expiry status response in their real shapes (`api/types.ts` `AssetListResponse`, `ExpiryStatusResponse`), with **two items of one name and different dates** and one item with no date.

**Time rule — a stop rule: at 750 s by your stamps, finish the item in hand, commit it, mark every item not started `REMAINING`, and go to the gate.** The gate is never skipped.

## G2 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof — the backend is unchanged; this proves it), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg325*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-325_<step>.log`, exact counts.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — Each item done or `REMAINING`, with file and line of the change; every wrong premise named (P10's current state stated as found).
- **A3** — Each item's test FAIL before, PASS after; logs named.
- **A4** — Gate green with exact counts; the named files twice green.
- **A5** — Frontend files only; no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like *Save edits* on a duplicate card, an edited date not sent with *It's another pack*, two same-name rows with no date or the same date shown for both, *Photo only* in the catalog, a grey or 11 px button in the warning, *Capture — Manual Create* / *Create asset* / *Candidate <id>* / *Possible duplicates or collisions* / *This match is advisory* / a raw key like `expiry_date` as a label anywhere in `frontend/src` outside tests (quote each grep), an ISO date in a text input, a test fed a hand-made shape, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** the files named above, the ones you establish instead (named, with why), `lib/labels.ts`, new `*.sg325.test.tsx`, older tests only where they assert replaced wording or labels.
- **Any backend file, any other product file, any style rule outside the controls named** is a STOP for that item — report it and go on (`PG-EV-03`).
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2. Expected ≈1000 s (`UNVERIFIED — my estimate`: SG-324's eight items committed before its kill; SG-324r1's gate ≈300 s of its 709 s).

## Report

Destination: `docs/worklogs/SG-325_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; each item with file and line, its before and after wording or style; each premise confirmed or falsified; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-325`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-325 | Report: docs/worklogs/SG-325_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
