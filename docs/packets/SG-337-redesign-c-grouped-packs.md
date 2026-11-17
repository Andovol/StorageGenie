# SG-337 — Redesign C, part 2: same-name packs show as one card in the catalog grid (*2 packs*, the next date)

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: this slice is frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Your **own** contract's version line, as you received it, is the host evidence: echo it — **never the project file's line (`AGENTS.md`); if you received none, say exactly that.** A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-17: *"Then: redesign C — item page as in the mockup (one row per pack, Used up, Add another pack) and same-name packs grouped as one card"*. Stage C (*"d14 ok"*, L3).

**Tier: STANDARD** (`CODER.md` §11): display only, no write. **New behaviour, said plainly: today every pack is its own card; after this slice the grid shows one card per name.** Part 1 (SG-336) built the item page that lists every pack; this card opens it.

## Why this exists

Two *Olive Oil* bottles are two cards today (`frontend/src/components/catalog/ProductGrid.tsx:259` `ProductGrid`, `ProductCard.tsx:96`). The same-name rule already exists and, after SG-336, lives in one shared module (`findSameNamePacks`'s rule: name trimmed and lower-cased, exact match, live items only — `UNVERIFIED`, establish it from SG-336's commit). Use **that rule's matching function**, never a second copy.

| ID | Change |
|---|---|
| **G1** | In the **grid** view, live items whose names match by the shared rule render as **one card**. The card's name is the soonest-dated pack's name as written; its date line is the **soonest** pack's date in today's wording (past / this week / date / *No date* only when no pack has a date); under it, muted, *<N> packs* when N ≥ 2 (nothing for one pack). Its photo is the soonest pack's, else the first pack in date order that has one. Clicking it opens the item page of the soonest pack (SG-336 shows them all). |
| **G2** | **Sort and counts:** the grid's sort places a group by its soonest date (*Use by, soonest first*) or its name. **The attention line keeps counting packs**, not cards (two past bottles are *2 items are past their date*) — state the wording you find and keep it. The result count, if one is shown, says what it counts (cards or packs) — establish and name it. |
| **G3** | **The table view is unchanged** — one row per pack — and the *Gone* view is unchanged (one entry per gone pack). Search narrows the packs first, then groups what is left (a search for *olive* shows one card *2 packs*). |
| **G4** | **Date chip fits its card (SG-333 I23).** At 390 px and 4 per row the past chip *Past · 16 Nov* overflows its 79.5 px column into the next card (`docs/worklogs/SG-333_shots/04-catalog-light-390-4.png`; `ProductCard.tsx:190,205` `whiteSpace: "nowrap"`). The date line and its chip never extend past the card's right edge: let it wrap inside the card, or shorten it at that width — your choice, named. Test: at a 79.5 px card width the chip's box stays within the card (assert the style that guarantees it, e.g. `max-width: 100%` with wrapping allowed). |
| **G5** | **Desktop grid aligns with the title (SG-333 I24).** At 1280 the title and toolbar start at x≈24 while the attention line and grid sit inset at x≈114–1166 (`01-catalog-light-1280-5.png`). Establish the wrapper that insets them (`UNVERIFIED` — a max-width container) and make the grid and attention line share the title's left edge and the page's content width. Name the cause and the change. |

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-337-scratch/docker-config output/SG-337-scratch/logs output/SG-337-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-337-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-337/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-337-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-337-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-337/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-337-scratch/`** — logs, captures, the build. **Never `/tmp`, for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-337-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — Tests first, then the change

Test file `frontend/src/sg337-grouped-packs.sg337.test.tsx`, fed **the shape the API really sends** (copy from an existing catalog test that uses the API client — never a hand-made shape, SG-322). **Run it before the change (FAIL), log `docs/worklogs/SG-337_fail.log`.** Data: *Olive Oil* 6 May 2030 (no photo), *olive oil* 3 Feb 2031 (photo), *Olive Oil* no date, *Rice* no date, one item past its date. It asserts:

- **T1** grid: one *Olive Oil* card reading *3 packs* with the 6 May 2030 date line; one *Rice* card with no *packs* line; card count equals 3 (Olive Oil, Rice, the past item).
- **T2** the *Olive Oil* card's photo is the 3 Feb 2031 pack's (the soonest has none).
- **T3** clicking the card navigates to the 6 May 2030 pack's id.
- **T4** the attention line counts packs (add a second past pack of the same name: the line says 2).
- **T5** table view: three *Olive Oil* rows.
- **T6** search *olive*: one card, *3 packs*.
- **T7** (G4) a card at 79.5 px width with a past date: the chip cannot extend past the card (style asserted).
- **T8** (G5) the grid and attention line carry no inset the title does not (the wrapper style asserted).

Then the change in the catalog's grid path (`CatalogPage.tsx`, `ProductGrid.tsx`, `ProductCard.tsx`, a new `frontend/src/components/catalog/groupPacks.ts` if it helps). **Run again (PASS), log `docs/worklogs/SG-337_pass.log`.** Older tests that assert one card per pack in the grid are updated, **each named old → new**. Commits `SG-337 G1: …` (tests) and `SG-337 G2: …` (change).

## G2 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof — the backend is unchanged; this proves it), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg337*` and `*sg336*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-337_<step>.log`, exact counts.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — G1–G5 done with file and line; every wrong premise named; the attention-line and count wording quoted before and after; G4 and G5 causes named.
- **A3** — Tests FAIL before, PASS after; logs named.
- **A4** — Gate green with exact counts; the named files twice green.
- **A5** — Frontend files only; no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like two *Olive Oil* cards, a *1 packs* line, the later date on the card, a grouped table, an attention line counting cards, a second copy of the matching rule, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** the catalog files named above, new `*.sg337.test.tsx`, older tests only where they assert one card per pack. **The item page (SG-336), the nav, the toolbar's controls and the theme tokens** are not touched; the layout wrapper G5 names may be changed. Any backend file, any other product file is a STOP for that item — report it and go on (`PG-EV-03`).
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no dependency, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit what is green, write the report, publish.** **No optional goal.** Order G0, G1, G2. Expected ≈700 s (`UNVERIFIED — my estimate`: SG-330/SG-331 screen slices). A stop leaves the rest `REMAINING`, named per T-line.

## Report

Destination: `docs/worklogs/SG-337_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; the change with file and line; each premise confirmed or falsified; test changes named old → new; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-337`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-337 | Report: docs/worklogs/SG-337_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
