# SG-324r1 — Finish polish A: check SG-324's eight committed items, run the full gate, write the report (SG-324 was killed by the provider quota)

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: this slice is frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D35 (*"D35 - ok"*: one polish slice for P1–P8 before the shelf trial); D18 and the owner's standing words: *"design, look and feel are very important."* Stage C (*"d14 ok"*, L3).

## Why this exists

SG-319 photographed SG-318's screens and listed rough edges an owner sees (`docs/worklogs/SG-319_audit.md` § *Rough edges*). This slice fixes the ones that need only the frontend. Locations are `UNVERIFIED` hypotheses — **establish each from the file before changing it** (`PB-1`), and report any that is wrong.

| ID | Where | Change |
|---|---|---|
| **P1** | Asset page | *Edit* and *Clear expiry date* are white (`--card`) on paper. Give them the theme's control style (`THEMED_CONTROL_CLASS` / `CONTROL_STYLE`, as `CandidateCard.tsx` uses) — expected in `frontend/src/components/ExpiryEntryForm.tsx:150-162` and the asset page's *Edit* control (`routes/AssetDetailPage.tsx`, find it). Light and dark. |
| **P3** | Asset page, Details | Drop the *Shelf life* row when its value repeats *Kind of item*; hide the *Replaced* row when it carries nothing new (establish what it shows — `lib/labels.ts:243`, `components/ProvenanceBadge.tsx:5`); show *Amount* and *Unit* as one row (*300 ml*). |
| **P4** | Catalog table | Remove the *Dimensions/Specs* column (`components/catalog/ProductGrid.tsx:46`; it is always —). Give the row actions button (`…`) a visible label *More* or an `aria-label` *More actions for <name>* and a `title` — say which and why. |
| **P5** | Expiry page | The *Opened countdown* block (`components/OpenedCountdownSection.tsx`, mounted at `routes/ExpiryPage.tsx:239`) is about cosmetics. Show it **only when it has at least one row**; when empty, render nothing. |
| **P6** | Inbox | (a) *Progress: 6/8 complete* counts skipped steps (`components/JobCard.tsx:54`): show *4 of 4 steps done · 2 skipped* — establish how skipped steps are known from the job; (b) every job is named *Import job*: name it by when it was made, *Import · 14 Nov, 19:30* (the date form `lib/labels.ts` already uses); (c) *Skipped (AI off)* (`lib/labels.ts:39`) → *Skipped — photo reading is off*. Update `labels.sg301.test.ts` for (c), old → new. |
| **P7** | Item panel | *Re-isolate Asset* → *Cut out the item again*; *Generate Context Scene* → *Make a styled photo* (`components/shell/ItemInspectorDrawer.tsx:583, :603`). Wording only; behaviour unchanged. |
| **T1** | Review card | *Thumbnail unavailable* (SG-320 I32; `components/CandidateCard.tsx`) → *No photo yet*, as everywhere else. |
| **T2** | Several | *Untitled item* literals (`components/OpenedCountdownSection.tsx:37`, `routes/CatalogPage.tsx:313`, `routes/PantryPage.tsx:190`) → *Unnamed item*, the word SG-318 chose. |

**Not in this slice:** P2 (the native date field's order follows the viewer's browser language — no custom date field), P8 + P13 (the catalog's status column and the use-by date need the list read — slice B), P9–P12 (slice B).

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-324r1-scratch/docker-config output/SG-324r1-scratch/logs output/SG-324r1-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-324r1-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-324r1/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-324r1-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-324r1-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-324r1/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-324r1-scratch/`** — logs, captures, the build. **Never `/tmp`, for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-324r1-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — Check what SG-324 committed, change nothing unless it is broken

SG-324 (Muse) committed all eight items, each with its own test (`33cd2dc..d45aaf4`: P1 `33cd2dc`, P3 `653a60f`, P4 `dced1ef`, P5 `d46eea2`, P6 `e99962d`, P7 `3754dbe`, T1 `1dc910b`, T2 `d45aaf4`), and logged FAIL/PASS names in `docs/worklogs/SG-324_fail.log` and `SG-324_pass.log`. **Then OpenCode Go's usage limit killed the run (`killed=provider reason=provider_quota`) before the gate and the report.** Its scratch may be left on the host: `--quarantine` moves it aside.

For each commit, read its diff (`git show --stat <sha>` then the hunks) and say, with file and line, whether it does what the table above says, **in the files the scope allows**. Re-run each `*.sg324.test.tsx` once on the current tree (PASS expected). Then answer, with evidence:

- **P1:** which class and style the two controls now use; quote the lines.
- **P3:** the condition that hides *Shelf life* and *Replaced* — does it hide a *Replaced* row that carries a real older value the owner may need? Say what the row held before.
- **P6:** how "skipped" is known — from the job's own step output, or from wording? Quote it.
- **Every test:** is it fed the shape the API sends, or a hand-made object missing fields the API always sends? Name any hand-made one.

**A defect you find is fixed only if it is inside the scope ceiling and small** — one commit per fix, with its test FAIL → PASS. Anything larger is reported, not fixed.

## G2 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof — the backend is unchanged; this proves it), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg324*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-324r1_<step>.log`, exact counts.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — Each of SG-324's eight commits read and judged with file and line; the four questions answered; any fix named.
- **A3** — Every `*.sg324.test.tsx` PASS on the current tree; any fix FAIL → PASS, logged in `docs/worklogs/SG-324r1_fix.log`.
- **A4** — Gate green with exact counts; the named files twice green.
- **A5** — Frontend files only; no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like a white button on paper, *Shelf life* repeating *Kind of item*, *Dimensions/Specs* still a column, an empty *Opened countdown* heading, *8 complete* counting skipped steps, two jobs with one name, *Re-isolate Asset* on screen, *Thumbnail unavailable* or *Untitled item* anywhere in `frontend/src` outside tests (quote the grep), a test fed a hand-made shape, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** the files named above, the ones you establish instead (named, with why), `lib/labels.ts`, new `*.sg324.test.tsx`, older tests only where they assert replaced wording.
- **Any backend file, any other product file, any style rule outside the controls named** is a STOP for that item — report it and go on (`PG-EV-03`).
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2. Expected ≈600 s (`UNVERIFIED — my estimate`: SG-322's gate ≈330 s plus the read).

## Report

Destination: `docs/worklogs/SG-324r1_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; each item with file and line, its before and after wording or style; each premise confirmed or falsified; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-324r1`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-324r1 | Report: docs/worklogs/SG-324r1_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
