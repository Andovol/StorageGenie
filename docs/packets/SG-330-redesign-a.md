# SG-330 — Redesign A: the Midnight palette, photo-first catalog cards, items-per-row setting, the header in plain words

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: this slice is frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D40 (*"Okay, lets do a mockup first."*), the mockup feedback (*"…we need to have 3 or 4 items per row at least. Maybe items per row should be configurable desktop and mobile? Desktop view overall is pretty clean…"*) and D41 (*"Lets use Midnight."*), all 2026-11-16 (`docs/decisions/2026-10-30-session-approvals.md`). Stage C (*"d14 ok"*, L3). The design is the owner-approved mockup https://claude.ai/artifact/BswTM1Tj1LHdgcibTPeLTh (you may not reach it; this packet carries every value you need).

## Why this exists

The owner found the live catalog *"so bad"*: tiny photos, a toolbar of equal boxes, maroon on paper. The owner approved a mockup: **photo-first cards, near-white ground, deep navy for the one main action, soft red only for past dates and soft amber only for this week, Instrument Sans and square corners kept.** This slice builds the colours, the cards, the grid and the header. **No new dependency** (no Tailwind, no component library — a later slice decides that). Locations are `UNVERIFIED` hypotheses — **establish each from the file before changing it** (`PB-1`) and report any that is wrong.

**Midnight, exact values (hex; convert to the file's HSL form):**

| Role | Light | Dark |
|---|---|---|
| Ground (`--paper`, `--background`) | `#F3F2EF` | `#121419` |
| Field / raised surface (`--card`) | `#FBFAF8` | `#1A1D24` |
| Text (`--ink`, `--foreground`) | `#191B22` | `#E8EAF0` |
| Muted text (`--ink-muted`, `--muted-foreground`) | `#5F626B` | `#A2A6B1` |
| Lines (`--line`, `--border`) | `#DADBDF` | `#272B34` |
| Main action (`--primary`, `--link`) | `#1F2A44` | `#B9C7E8` |
| Text on main action (`--primary-foreground`) | `#F3F2EF` | `#121419` |
| Past its date (new `--past-bg` / `--past-fg`) | `#F3E1DD` / `#7A2E22` | `#3A1F1F` / `#F0C4BE` |
| This week (new `--soon-bg` / `--soon-fg`) | `#EFE7D3` / `#5F4511` | `#37301B` / `#EBD7A6` |
| Photo tile behind a cut-out (new `--tile`) | `#E3E4E8` | `#1F232B` |

Every other token in `frontend/src/theme/tokens.css` (`:root` from `:1`, `.dark` from `:43`: `--card-muted`, `--muted`, `--accent`, the badges) moves to the nearest Midnight role — name the role you chose for each and why.

| ID | Where | Change |
|---|---|---|
| **R1** | `theme/tokens.css` | The Midnight values above, light and dark; add the five new tokens and their utility classes. **A test computes the WCAG contrast ratio from the token values read out of the file** for every text-on-ground pair above (ink, muted and link on ground; primary-foreground on primary; past; soon — light and dark) and asserts ≥ 4.5:1. |
| **R2** | Header (`components/shell/AppHeader.tsx`) | *Import Asset* (`:98`, `:118`) → *Add item*, the one filled button in the main-action colour; search placeholder *Search…* (`:82`) → *Search your things*, accessible name the same; drop the *Showing: N items* box (`:72`) — the count moves to R3. Phone width keeps today's one-row header rule (`tokens.css` `@media (max-width: 480px)` `.sg-header*`). |
| **R3** | Catalog page (`routes/CatalogPage.tsx`) | Above the toolbar: heading *Your things* (h1; 40 px wide screens, 28 px narrow; weight 600) and a muted line *N things* (live items loaded). |
| **R4** | Catalog grid (`components/catalog/ProductGrid.tsx`, grid branch) | **Items per row is a setting:** wide screens 4 / 5 / 6 (default 5); narrow screens (viewport < 640 px) 3 / 4 (default 3). A *Per row* control — a labelled group of buttons with `aria-pressed`, ≥ 44 px tall on narrow screens — in the catalog toolbar. The choice is **remembered per device** in `localStorage` under `sg-per-row-wide` and `sg-per-row-narrow`, read and written inside try/catch, falling back to the default. Grid `repeat(n, minmax(0, 1fr))`; gaps 40 × 24 px wide, 16–20 × 8–10 px narrow. |
| **R5** | Catalog card (`components/catalog/ProductCard.tsx`) | **Photo first:** a square tile filling the column (photo `object-fit: contain` on `--tile`), no border, no status dot or badge. Under it: the name (16 px / 600 wide; 13 px / 600 narrow, one line with ellipsis); then the date line — **past** (`days_remaining < 0`): *Past its date · 27 Oct* as a small block in the past colours; **this week** (0–7 days): *Use by 21 Nov · 5 days* in the soon colours; **later**: *Use by 6 May 2030* in ink; **none**: *No date yet* in muted (narrow: *Past · 27 Oct*, *21 Nov*, *6 May 2030*, *No date*); then, wide only, the kind of item in muted 13 px. The date comes from the catalog's existing use-by join (`routes/CatalogPage.tsx` `useByById`, SG-325) — carry `days_remaining` the same way. Same-name packs stay separate cards in this slice. |

**Not in this slice:** the toolbar's tabs, sort and *Gone* link (SG-331), the attention line, the item page, grouping same-name packs, any component library.

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-330-scratch/docker-config output/SG-330-scratch/logs output/SG-330-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-330-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-330/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-330-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-330-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-330/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-330-scratch/`** — logs, captures, the build. **Never `/tmp`, for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-330-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — The changes, one item per step

Do **R1, R5, R4, R3, R2, in that order** (R2 is the most droppable), one item per step, and **commit each item as soon as it is done** (`SG-330 R1: …`). Each commit holds that item's product change **and** its test in `frontend/src/**/*.sg330.test.tsx` (one file per item, or one shared file extended per item — say which). Each test fails without the change and passes with it: **write the test first and run it (FAIL), then change the product file and run it again (PASS)**; log names and first assertion to `docs/worklogs/SG-330_fail.log` and `SG-330_pass.log`. **Older tests asserting replaced wording or labels are updated in the same commit, each named, old → new, none loosened** — SG-324 left eight such tests red for its gate to find; find yours before committing by running every older test file that renders the component you changed.

**Tests read what the user sees:** query by role and visible text, and feed a component **the shape the API sends** — copy it from an existing test that uses the API client or a captured response; never a hand-made object missing fields the API always sends (SG-304's lesson). For R4/R5 feed the asset list page and the expiry status response in their real shapes (`api/types.ts` `AssetListResponse`, `ExpiryStatusResponse`) with one item past its date, one within 7 days, one later and one with no date; for R4 also prove the stored choice is read back after a remount and that a broken `localStorage` falls back to the default.

**Time rule — a stop rule: at 750 s by your stamps, finish the item in hand, commit it, mark every item not started `REMAINING`, and go to the gate.** The gate is never skipped.

## G2 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof — the backend is unchanged; this proves it), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg330*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-330_<step>.log`, exact counts.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — Each item done or `REMAINING`, with file and line; every wrong premise named; every moved token's chosen role named.
- **A3** — Each item's test FAIL before, PASS after; logs named; the contrast test lists every pair with its ratio.
- **A4** — Gate green with exact counts; the named files twice green.
- **A5** — Frontend files only; no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like a maroon (`2 41% 30.6%`) or paper (`40 35.3% 93.3%`) value left in `tokens.css`, a pair under 4.5:1, *Import Asset* or *Showing:* on screen, a status dot or *Photo only* on a card, a past date not marked, a per-row choice lost on remount, a `localStorage` error that breaks the page, a test fed a hand-made shape, a red suite. Say which you checked; quote each grep.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** the files named above, the ones you establish instead (named, with why), `lib/labels.ts`, new `*.sg330.test.tsx`, older tests only where they assert replaced wording, colours or layout.
- **Any backend file, or any product file outside the catalog, the header and `tokens.css`,** is a STOP for that item — report it and go on (`PG-EV-03`).
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2. Expected ≈1000 s (`UNVERIFIED — my estimate`: SG-330 five items 940 s).

## Report

Destination: `docs/worklogs/SG-330_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; each item with file and line, its before and after wording or style; each premise confirmed or falsified; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-330`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-330 | Report: docs/worklogs/SG-330_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
