# SG-331 — Redesign B: the catalog toolbar in plain text, use-by sort first, one attention line, the grid gaps fixed

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: this slice is frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D40 (*"Okay, lets do a mockup first."*), the mockup feedback (*"…we need to have 3 or 4 items per row at least. Maybe items per row should be configurable desktop and mobile? Desktop view overall is pretty clean…"*) and D41 (*"Lets use Midnight."*), all 2026-11-16 (`docs/decisions/2026-10-30-session-approvals.md`). Stage C (*"d14 ok"*, L3). The design is the owner-approved mockup https://claude.ai/artifact/BswTM1Tj1LHdgcibTPeLTh (you may not reach it; this packet carries every value you need).

## Why this exists

SG-330 built the Midnight colours, the photo-first cards, the items-per-row setting and the header. This slice finishes the catalog toolbar the owner approved in the mockup: **plain text, nothing boxed except the per-row control, one sort that puts what needs you first, and one line that says what is past its date.** **No new dependency.** Locations are `UNVERIFIED` hypotheses — **establish each from the file before changing it** (`PB-1`) and report any that is wrong. Colours come only from the tokens SG-330 added (`--past-bg`, `--past-fg`, `--soon-*`, `--ink`, `--ink-muted`, `--line`, `--primary`).

| ID | Where | Change |
|---|---|---|
| **T7** | `components/catalog/ProductGrid.tsx:269-272` | SG-330 swapped the gaps (my packet's wording was ambiguous). CSS `gap` is *row column*: wide `40px 24px`, narrow `16px 8px`. Fix the comment too. |
| **T2** | Sort (`components/shell/CatalogToolbar.tsx:7-11` `SORT_LABELS`, `sortCatalog` `:28`; `routes/CatalogPage.tsx:81`, `:255`, `:263`) | Replace `status` (*Processing Status*) with **`useby`, *Use by, soonest first***: past dates first (oldest first), then soonest, then items with no date, ties by name. **It becomes the default sort** (`:81`), and *Clear all* resets to it (`:263`); the filter summary (`:255`) leaves it out as the default. Other labels: *Recently added*, *Name, A to Z*. The control is a plain select with no box: ink text, a chevron, accessible name *Sort*. Establish where `sortCatalog` gets the use-by date (SG-325/SG-330 join on `CatalogPage.tsx`); if the sort runs before the join, move it after. |
| **T1** | Kind-of-item pills (`CatalogToolbar.tsx` around `:170-190`) | Pills → **text tabs**: no border or fill; the active one ink, weight 600, a 2 px ink underline; the rest muted; 15 px; buttons with `aria-pressed`; no counts in the labels. The row scrolls sideways on narrow screens instead of wrapping. |
| **T6** | Catalog page, above the grid | **One attention line**, shown only in the live view with *All* selected and only when something needs the owner: *1 item is past its date and 2 run out this week.*; *1 item is past its date.*; *2 run out this week.* (singular and plural right), on `--past-bg` / `--past-fg`, then a link *Show them* to `/expiry`. Counts from the expiry status response the catalog already fetches — establish which field or bucket means "past" and which "within 7 days" (`api/types.ts` `ExpiryStatusResponse`, `ExpiryBucket`) and say so. No line when both are zero. |
| **T4** | View switch (`CatalogToolbar.tsx:211-231`, `DENSITY_LABELS`) | *Standard Grid* / *Compact Table* text buttons → **two icon buttons** in one small bordered group: lucide `LayoutGrid` and `List` (`lucide-react` is already a dependency), accessible names *Photo grid* and *List*, `aria-pressed`, `title` the same. Default stays the grid (SG-328). Update tests that click by the old names, old → new. |
| **T3** | Live / Gone (`CatalogToolbar.tsx:147`) | The two-box *Live / Gone* group → **one quiet text link** at the right of the title row: *Gone* in the live view; in the gone view the title reads *Gone* and the link reads *Back to your things*. Add a count (*Gone (3)*) only if a count is already loaded without a new request — say which. |
| **T5** | Save search, saved searches, Clear all (`CatalogToolbar.tsx:279-340`) | *Save search* and *Clear all* show **only when a search or a non-default filter or sort is active**; the saved-searches menu shows **only when at least one saved search exists**. Same behaviour otherwise. |

**Not in this slice:** the item page, grouping same-name packs, the header, any component library.

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-331-scratch/docker-config output/SG-331-scratch/logs output/SG-331-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-331-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-331/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-331-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-331-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-331/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-331-scratch/`** — logs, captures, the build. **Never `/tmp`, for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-331-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — The changes, one item per step

Do **T7, T2, T1, T6, T4, T3, T5, in that order** (T5 is the most droppable), one item per step, and **commit each item as soon as it is done** (`SG-331 T7: …`). Each commit holds that item's product change **and** its test in `frontend/src/**/*.sg331.test.tsx` (one file per item, or one shared file extended per item — say which). Each test fails without the change and passes with it: **write the test first and run it (FAIL), then change the product file and run it again (PASS)**; log names and first assertion to `docs/worklogs/SG-331_fail.log` and `SG-331_pass.log`. **Older tests asserting replaced wording or labels are updated in the same commit, each named, old → new, none loosened** — SG-324 left eight such tests red for its gate to find; find yours before committing by running every older test file that renders the component you changed.

**Tests read what the user sees:** query by role and visible text, and feed a component **the shape the API sends** — copy it from an existing test that uses the API client or a captured response; never a hand-made object missing fields the API always sends (SG-304's lesson). For T2 and T6 feed the asset list page and the expiry status response in their real shapes (`api/types.ts` `AssetListResponse`, `ExpiryStatusResponse`) with two items past their date, one within 7 days, one later and one with no date.

**Time rule — a stop rule: at 750 s by your stamps, finish the item in hand, commit it, mark every item not started `REMAINING`, and go to the gate.** The gate is never skipped.

## G2 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof — the backend is unchanged; this proves it), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg330*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-331_<step>.log`, exact counts.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — Each item done or `REMAINING`, with file and line; every wrong premise named; T6's past and this-week sources named.
- **A3** — Each item's test FAIL before, PASS after; logs named.
- **A4** — Gate green with **exact counts for every suite, backend included** (SG-330 gave none for the host suite); the named files twice green.
- **A5** — Frontend files only; no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like a column gap wider than the row gap, *Processing Status* or *Recently Added* still offered, a default sort that is not use-by, a no-date item sorted before a dated one, a boxed kind-of-item pill, an attention line with zero counts or wrong plural, *Standard Grid* / *Compact Table* text on screen, a *Live* box, *Save search* with nothing active, a test fed a hand-made shape, a red suite. Say which you checked; quote each grep.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** the files named above, the ones you establish instead (named, with why), `lib/labels.ts`, new `*.sg331.test.tsx`, older tests only where they assert replaced wording, colours or layout.
- **Any backend file, or any product file outside the catalog page, `CatalogToolbar.tsx`, `ProductGrid.tsx`, `AppShell.tsx` and `lib/labels.ts`,** is a STOP for that item — report it and go on (`PG-EV-03`).
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2. Expected ≈1000 s (`UNVERIFIED — my estimate`: SG-330 five items 1060 s; these are smaller).

## Report

Destination: `docs/worklogs/SG-331_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; each item with file and line, its before and after wording or style; each premise confirmed or falsified; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-331`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-331 | Report: docs/worklogs/SG-331_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
