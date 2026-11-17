# SG-336 report — Redesign C part 1: item page, one row per pack

SG-336 | model and effort: not visible in the process arguments, so they are not stated and nothing is inferred | working directory `/home/andrei/StorageGenie` | remote `git@github.com:Andovol/StorageGenie` | BASE ref `origin/automation` resolved to `a5b00728bb70e6d61ee5b9049887e86b69c23b6a` | WORK-HEAD `82f88636` (two commits: `aa09e261` G1, `82f88636` G2).

## Time (from `date +%s` stamps)

- Session start 1794953253. G0 preflight 1794953515 (health 200, docker Server shown, busybox rc 0).
- G1 test written; FAIL run logged 1794953665 (7 failed, rc 1).
- G2 change + debug + fix; new tests 7/7 PASS logged 1794954911, run twice (second run 1794954917, 7/7).
- Full frontend suite once 1794954735–1794954783: 37 failed | 525 passed (562), 8 files.
- Scratch removed 1794954937; G1+G2 committed 1794954943; anchors read 1794954973.
- Elapsed ≈ 1700 s from session start (≈ 1460 s from G0) — past the 1100 s stop line, so this slice STOPPED per the budget rule: old-test updates, backend gate, image proof, build and `tsc`/`eslint` logs beyond what is stated below are REMAINING.

## What changed (frontend only)

- `frontend/src/lib/sameNamePacks.ts` (new, 43 lines): `findSameNamePacks` + `SamePack` + `NOT_LIVE_STATUSES` moved verbatim from `frontend/src/components/AssetForm.tsx`, no copy.
- `frontend/src/components/AssetForm.tsx`: now imports the shared rule; orphan tail from the move removed. Behaviour unchanged.
- `frontend/src/routes/AssetDetailPage.tsx` (1629 lines, rebuilt around kept exports):
  - Back link `‹ Your things` to the catalog (:1091); left photo tile 1:1 on `--tile`, `object-fit: contain`, max 520 px (:1095), `data-testid="item-photo"`; under it plain text links for the photo actions that already existed — `Open full size` (:1126) and `Attach a photo` (existing upload + `POST /v1/assets/:id/evidence` flow, :1130).
  - Right: `h1` 44 px / weight 600 (:1137); muted line `data-testid="packs-muted"` — `<Kind> · <Where> · <N> packs`, each part only when known (:1144).
  - Packs section (:1142): one row per live pack, `border-top: 1px solid hsl(var(--line))`, soonest date first by ISO lexical compare, no date last (explicit null handling, not `localeCompare` — the first build used a `"~"` sentinel and T1 caught `No date` sorting first; fixed). Row: bold date line (:1171, `data-testid="pack-date"`) via `packDateLine` (:485) — `Use by 6 May 2030`; past dates use the catalog's narrow past wording (`Past · 6 May`, `ProductCard.tsx:59`) with the past wash classes `bg-past text-past` (:1173); `No date` when none. Muted line: amount via kept `detailAmountText` from the record quantity/unit + `added <d Mon>` (`formatUseByDayMonth(created_at)`, :1155). Two plain bordered paper controls `Edit` / `Used up`, `min-height: 44px` (:1183).
  - `Edit` opens that pack's inline `PackEditor` (`:1210`, component `:567`): existing `ExpiryEntryForm` (same `enterManualExpiry`/`clearExpiryDate` writes, per-pack id) + existing amount controls (`decrementQuantity`/`incrementQuantity` per-pack id, quantity/unit inputs + `Save amount` via existing `apiPatch` with `If-Match`). A pack with no classification gets `hasWindows: true` so a date can be typed (`packExpiryContext`, :518); non-perishable packs keep the form hidden, as before.
  - `Used up` calls existing `markGone(packId, household, "used_up")` for that pack only (`packGoneMut`, :935); the row leaves at once; notice `data-testid="pack-notice"` reads `<name> used up · Undo` (`:1234`, Pantry wording `PantryPage.tsx:452`, button labelled `Undo` per the packet) and `Undo` calls existing `putBack` for that pack only (`packUndoMut`, :947). All packs gone → `No live packs left for <name>. Back to Your things` (:1224).
  - `Add another pack`: dark primary button (`--primary`), plus icon, `min-height: 44` (:1262). Same create call the capture form's button uses: `POST /v1/assets {display_name, asset_type}` + `Idempotency-Key`, no date, no photo; the opened item's places ride along via the existing `assignAssetLocation` per location (`addPackMut`, :963). New row appears with `Edit` open (`setEditingPackId`, :963).
  - Definition list Kind of item / Where / Brand, rows only with a value (:1278): kind from the record (`unknown` omitted), Where from assigned places, Brand from the current `brand` assertion.
  - `History (<n> changes)` folded with chevron, opened item's audit events in the established rendering (`plainActionLabel` — `formatJobDate`, :1312).
  - `More about this item` folded below History (:1340), holding today's sections in today's order (see moved list).
- `frontend/src/sg336-item-page.sg336.test.tsx` (new, 272 lines): T1–T7 per packet, shapes copied from `AssetDetailPage.sg272.test.tsx` (`shell()` + taxonomy), never hand-made.

## Premises, confirmed or falsified

- P1 confirmed: the page showed one item (`AssetDetailPage.tsx`, 998 lines).
- P2 confirmed: `findSameNamePacks` (trimmed, lower-cased, exact, live-only) lived in `AssetForm.tsx`; moved to `lib/sameNamePacks.ts`, both callers import it (verified: no second definition remains).
- P3 confirmed: capture-form `Add another pack` (`AssetForm.tsx:~326`) runs the create with `{display_name, asset_type}` + `Idempotency-Key`; the new button sends exactly that (T3 asserts the call shape and the absence of `evidence_ids`/`expiry_date`). "Place" has no field in the create schema (`backend/app/schemas/asset.py: AssetCreate`), so it rides via the existing assign-location calls — stated, not hidden.
- P4 confirmed and applied literally: past rows read `Past · <day month>` (`ProductCard.tsx:59`, narrow) with the past wash; dated rows read `Use by <d Month yyyy>` (the wide later wording).
- P5 confirmed: `detailAmountText` reused for pack amounts.
- P6 confirmed: Pantry notice wording (`PantryPage.tsx:452`) reused as `<name> used up · Undo`.
- Photo/provider premise confirmed: the page's existing photo actions are EvidenceGallery links + attach; the page's one existing provider call is the `Enrich` button. No photo action was added; `Enrich` + `WebAlternates` stay in More; no new provider call exists on the page (no `Cut out` / `Make styled` added).
- Photo premise: tile shows the opened item's photo, else the first pack in the list that has one (T7 proves with `ev-2`).

## Moved-sections list (old page order → new home)

1. Shelf life (classification + AI suggestion notes) → More.
2. Amount left (−1/+1) → More for the opened item, and per-pack inside each row's Edit.
3. Use it up (three reasons + Put back, opened item) → More; per-row Used up is the new placement.
4. Locations → More (still hidden when the backend flag is dormant, as before).
5. Relations → More (still hidden when dormant, as before).
6. Name/quantity/unit/condition edit form → More, behind `Edit name and amount`.
7. Enrich button + WebAlternates → More (existing provider call, unchanged).
8. Date-kept note → More.
9. Evidence gallery + attach → More; tile + `Open full size` / `Attach a photo` links in the left column.
10. Details table → More (unchanged logic, incl. SG-324 P3 rules).
11. History → folded `History (<n> changes)` (same entries, same rendering).
12. Manual date entry form → per-pack inline editor (the opened item is one of the rows).

## Tests

- G1 FAIL before: `docs/worklogs/SG-336_fail.log` — 7 failed (no `pack-date` on the old layout), rc 1.
- G2 PASS after: `docs/worklogs/SG-336_pass.log` — 7 passed; file run twice (second run 7/7 in terminal).
- T2 isolation is asserted on the mocks: after Used up, `markGone` calls with any id other than `pack-2` equal `[]`; after Undo, `putBack` calls with any id other than `pack-2` equal `[]` (quoted from the test).
- Older tests: NOT updated (budget stop). 37 failures across 8 files, all asserting the old layout — REMAINING, each with its old → new direction:
  - `routes/AssetDetailPage.test.tsx` (18): Enrich POST/alternates, Locations, Relations, classification, ExpiryEntryForm prefill/accept/clear/documents, quantity PATCH + History — old: sections visible on load; new: open `More about this item` first (date form additionally needs the pack row's `Edit`).
  - `routes/AssetDetailPage.sg272.test.tsx` (6): −1/+1 and `None left`, three gone reasons, AI note size — old: global sections; new: More, or the pack row's editor (buttons now repeat per pack — scope queries by `pack-row-*`).
  - `routes/AssetDetailPage.sg271.test.tsx` (3): proposed-date Accept/prefill, shelf-life preselect notes — old: form visible on load; new: open the pack row's `Edit` (+ More for the shelf-life control).
  - `routes/sg318-plain-words.sg318.test.tsx` (2): W3 history entries, one more wording read — old: History visible; new: open `History (` first.
  - `routes/sg312-screens.sg312.test.tsx` (3), `src/sg324-p1.sg324.test.tsx` (1, asset Edit theme class), `src/sg324-p3.sg324.test.tsx` (3, Details rows incl. Shelf-life dedup, superseded hiding, 300 ml combine) — old: sections on load; new: open More first (Edit assertions scope to `Edit name and amount` / per-row `Edit`).
  - `routes/theme-adoption.test.tsx` (1): old: `h1` has class `page-header`; new: `h1` is 44 px/600 inline per the mockup — assertion needs the new wording.
- No old test protects behaviour the new page drops: every old section/behaviour above still exists (in More or per-row); nothing was deleted to make the suite green. No STOP item arose under this rule.

## Gate (partial — budget stop)

- New file twice green: 7/7 and 7/7. Older changed files (`AssetDetailPage.tsx`, `AssetForm.tsx`) ran once inside the full suite (red only from the old-layout assertions above).
- Full frontend suite once: 8 files failed, 73 passed (81); 37 failed | 525 passed (562).
- `tsc --noEmit`: clean. `eslint`: only the known `App.household-nav.test.tsx` `fireEvent` error (pre-existing, out of scope).
- NOT run (REMAINING): production build into scratch, `make backend-test` (host + image proof), `make frontend-test` rerun to green, `eslint`/`tsc` log files.
- Health: 200 at G0 start; end-of-slice health NOT re-run (stopped before G3).

## Changed files

- `frontend/src/routes/AssetDetailPage.tsx` (rebuilt, exports kept: `EnrichButton`, `enrichCapRefusal`, `ENRICH_PER_PRESS_CAP_USD`, `isCountedUnit`, `LocationsSection`, `RelationsSection`, `visibleDetailAssertions`, `detailAmountText`).
- `frontend/src/components/AssetForm.tsx` (import of the moved function only).
- `frontend/src/lib/sameNamePacks.ts` (new).
- `frontend/src/sg336-item-page.sg336.test.tsx` (new).
- `docs/worklogs/SG-336_fail.log`, `docs/worklogs/SG-336_pass.log` (new).
- No backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes. `frontend/dist` untouched. Tree clean except the files above; scratch `output/SG-336-scratch/` removed; `output/` itself and `output/dispatch` never touched.

## Contract, UNCLEAR, REMAINING

- Contract: I received no contract version line.
- UNCLEAR: none besides the stop itself.
- REMAINING: (1) 37 older-test layout updates listed above; (2) full gate to green — build, `make backend-test` host+image, `make frontend-test`, named-files-twice runs, step logs; (3) end-of-slice health 200 re-probe; (4) stray file `/tmp/opencode/probe.tsx` (48 KB, my bisect probe) still on disk — removal via shell was denied by tool permissions, so it is reported, not hidden.

## Criteria

- A1 — Preflight ran literally (`DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-336/docker.sock`, socket listed, `docker version` shows Server, busybox rc 0, health 200); stamps above. End health NOT re-run (stop).
- A2 — Page built as described; file:line per part above; premises confirmed/falsified with comparisons; moved-sections list complete.
- A3 — G1 FAIL before (`SG-336_fail.log`, 7 failed) PASS after (`SG-336_pass.log`, 7/7, twice); T2 no-other-id-touching quoted from the mock assertions.
- A4 — Gate partial: full suite 37 failed | 525 passed; `tsc` clean; `eslint` only the known error; new file twice green; build/backend/image-proof REMAINING.
- A5 — Frontend files only; no backend/migration/lockfile/`.env`/live-DB/provider/container/deploy bytes; `frontend/dist` untouched; tree clean except listed files; scratch removed — except `/tmp/opencode/probe.tsx` remains (removal denied), reported above.
- A6 — Vacuity checked: FAIL-before/PASS-after red suite; T1 caught a real sort defect (sentinel put `No date` first); Rice exclusion, Used up/Undo id isolation on mocks, create payload without photo/date, no ISO/raw-word/object-dump (T6), photo fallback (T7) all asserted.
- A7 — See last line.

Verification: FAIL — budget stop: 37 older-test layout updates and the full gate REMAINING.
