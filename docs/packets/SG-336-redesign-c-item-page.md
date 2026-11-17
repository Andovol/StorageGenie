# SG-336 — Redesign C, part 1: the item page as in the mockup — one row per pack, *Used up*, *Add another pack*, history folded

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration**, **no backend change**: this slice is frontend only; a fix that needs the backend is a STOP for that item (report it, do the rest).
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend. **No control on this page may start a provider call that did not already exist on it** (stage C: no provider or image spend).

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Your **own** contract's version line, as you received it, is the host evidence: echo it — **never the project file's line (`AGENTS.md`); if you received none, say exactly that.** A denial on that folder is expected and is not a STOP.

**Approval:** owner, 2026-11-17: *"Then: redesign C — item page as in the mockup (one row per pack, Used up, Add another pack) and same-name packs grouped as one card"*. Owner D40 mockup, D41 Midnight (2026-11-16). Stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that."*

**Tier: STANDARD** (`CODER.md` §11): a page rebuilt; one existing write (*Used up* = the existing mark-gone call) and one existing create (*Add another pack* = the existing create call) placed on it. **New behaviour, said plainly: the item page today shows one item; after this slice it shows every live pack with the same name.** The catalog grouping is part 2 (SG-337), not here.

## Why this exists

Today a pack is its own item: two *Olive Oil* bottles are two items, each with its own page (`frontend/src/routes/AssetDetailPage.tsx`, 998 lines). The capture form already treats a same-name live item as "another pack" (`frontend/src/components/AssetForm.tsx:28` `findSameNamePacks`: name trimmed and lower-cased, exact match, live items only — `UNVERIFIED`, establish it). The owner-approved mockup (described below; you cannot open it) puts all packs of one thing on one page.

**The mockup, desktop, light (Midnight colours from `frontend/src/theme/tokens.css` replace the mockup's own hex values):**

- A back link *‹ Your things* to the catalog.
- **Left:** the photo, a large square tile (520 px at 1440 wide; the catalog card's tile treatment, `object-fit: contain`), and under it a row of plain text links for photo actions **that already exist on the page today** — **do not add** *Cut out the item again* or *Make a styled photo* if they would call a provider; if a photo action exists that calls a provider, leave it where it is and name it in the report.
- **Right, top:** the name as the page heading (≈44 px, weight 600), then one muted line: *<Kind of item> · <Where> · <N> packs* (each part only when known; *1 pack* singular).
- **Packs:** a list, one row per live pack, rows divided by a 1 px line, soonest date first, no date last. Each row: a bold line *Use by <d Month yyyy>* (*No date* when none; a past date in the catalog's past wording and colour, `ProductCard.tsx:59`); under it a muted line with what is known of that pack — its amount (`detailAmountText`, `AssetDetailPage.tsx:446`) and *added <d Mon>*; then two plain bordered buttons, **Edit** (opens that pack's date and amount editing inline, using the existing `ExpiryEntryForm` and amount controls) and **Used up** (the existing mark-gone call with reason `used_up`, for **that pack only**).
- **Add another pack** — the one dark primary button (`--primary` / `--primary-foreground`), with a plus icon: creates a new live item with the same name, kind of item and place as this one, no date, through the same create call the capture form's *Add another pack* uses (`AssetForm.tsx:~326`), then shows its row with *Edit* open so the date can be typed. **No photo is copied or uploaded.**
- A definition list: *Kind of item*, *Where*, *Brand* (only rows with a value).
- **History** folded behind one link *History (<n> changes)* with a chevron, opening in place.

**After *Used up*:** the row leaves the list and one notice shows *<name> used up · Undo* (the Pantry page's wording, `PantryPage.tsx:452`); **Undo restores that pack only** — no other pack's date, amount or status changes (the shelf trial checks exactly this). When the last pack is used up, the page says so plainly and offers the way back to the catalog.

**Everything the page has today and the mockup does not show** (Locations, Relations, Amount left, the other gone reasons *Thrown away* / *Given away*, enrich, evidence, any other section — establish the list from the code): **nothing is removed.** Put each under one folded *More about this item* section below History, in today's order, restyled only enough to match (square corners, Instrument Sans, Midnight tokens). Name each section and where it went.

**Which item's page:** the route stays `/assets/:id`. The page shows the packs matching that item's name by the `findSameNamePacks` rule (move that function to a shared module and import it in both places — no copy). The photo and the definition list come from the opened item; if it has no photo, the first pack in the list that has one.

**Phone (390):** one column — photo full width, then heading, packs, button, list, History. Rows keep *Edit* and *Used up* on one line beside the date or wrap them below it, whichever keeps every button ≥ 44 px tall and nothing clipped. No sideways scroll.

## G0 — Preflight

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-336-scratch/docker-config output/SG-336-scratch/logs output/SG-336-scratch/pytest
export DOCKER_CONFIG="$PWD/output/SG-336-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-336/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
export TMPDIR="$PWD/output/SG-336-scratch"
export PYTEST_ADDOPTS="--basetemp=$PWD/output/SG-336-scratch/pytest"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-336/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside tracked paths goes under `output/SG-336-scratch/`** — logs, captures, the build. **Never `/tmp`, for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-336-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — Tests first

Test file `frontend/src/sg336-item-page.sg336.test.tsx`, fed **the shape the API really sends** (copy from an existing `AssetDetailPage` test that uses the API client — never a hand-made shape, SG-322). **Run it before the change (FAIL), log to `docs/worklogs/SG-336_fail.log`.** It asserts:

- **T1** two live items *Olive Oil* (dates 6 May 2030 and 3 Feb 2031) and one *olive oil* with no date, plus one *Rice*: the page of the first shows three pack rows in order 6 May 2030, 3 Feb 2031, *No date*; the muted line ends *3 packs*; no *Rice* row.
- **T2** *Used up* on the second row calls mark-gone for **that id only** with `used_up`; the row leaves; the notice reads *Olive Oil used up · Undo*; **Undo** calls the existing restore for that id only; **no request touches the other two ids** (assert on the mocked calls).
- **T3** *Add another pack* calls the create with the same name, kind of item and place, no date and no photo; a fourth row appears with its date editor open.
- **T4** *Edit* on a row opens the date editor for that pack's id; saving calls the existing expiry write for that id only.
- **T5** History is folded (its entries not in the document) until its link is clicked; *More about this item* is folded and, opened, holds every section listed in the report as moved.
- **T6** No ISO date (`\d{4}-\d{2}-\d{2}`), no raw status word (`ACTIVE`, `ARCHIVED`), no `[object Object]` in the page text.
- **T7** The opened item has no photo, the second pack has one: the tile shows the second pack's photo.

## G2 — The change

Rebuild `AssetDetailPage.tsx` (and new components under `frontend/src/components/item/` if it helps) to the layout above. Shared `findSameNamePacks` moved, both callers importing it. **Run G1's file again (PASS), log `docs/worklogs/SG-336_pass.log`.** Older tests that assert the old layout are updated, **each named old → new**, never deleted to make the suite green; a behaviour an old test protects that the new page drops is a STOP for that item. Commits `SG-336 G1: …` (tests) and `SG-336 G2: …` (change).

## G3 — The full gate, never skipped

`eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof — the backend is unchanged; this proves it), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg336*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-336_<step>.log`, exact counts.

## Acceptance criteria

- **A1** — Preflight; health 200 start and end; phase seconds from stamps.
- **A2** — The page built as described, with file and line per part; every wrong premise named; the list of today's sections and where each went.
- **A3** — G1 FAIL before, PASS after; logs named; T2's "no other id touched" asserted on the mock, quoted.
- **A4** — Gate green with exact counts; the named files twice green.
- **A5** — Frontend files only; no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; no new provider call; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like one row only, a *Rice* row, *Used up* or Undo touching another id, *Add another pack* copying a photo or a date, a section of today's page gone, an ISO date, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Frontend only:** `AssetDetailPage.tsx`, new files under `frontend/src/components/item/`, `AssetForm.tsx` (only the import of the moved function), the shared module it moves to, new `*.sg336.test.tsx`, older tests only where they assert the old layout.
- **The catalog, the card, the toolbar, the nav, the theme tokens** are not touched (part 2 and other slices). Any backend file, any other product file is a STOP for that item — report it and go on (`PG-EV-03`).
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no dependency (no Tailwind, no component library), no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit what is green, write the report, publish.** **No optional goal.** Order G0, G1, G2, G3. Expected ≈900 s (`UNVERIFIED — my estimate`: SG-331, a screen slice of similar size). A stop leaves the rest `REMAINING`, named per T-line.

## Report

Destination: `docs/worklogs/SG-336_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; the change with file and line; each premise confirmed or falsified; the moved-sections list; test changes named old → new; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it. Check your verdict line against every criterion before you write it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-336`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-336 | Report: docs/worklogs/SG-336_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
