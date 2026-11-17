# SG-338 report — finish SG-336: 36/37 old tests to the new item page, pack copies shelf-life category, gate 1 STOP short

SG-338 | model and effort: not visible in the process arguments, so they are stated as not visible and nothing is inferred | working directory `/home/andrei/StorageGenie` | remote `git@github.com:Andovol/StorageGenie` | BASE ref `origin/automation` resolved to `1205a63cc5a1e51ec46e1466fce256cd295662d8` | WORK-HEAD `043d85e5` (9 commits: G2 + 7× G1 + G3 logs; report commit follows).

## Time (from `date +%s` stamps)

- Session start 1794955142. G0 preflight 1794955152–1794955153 (health 200, `docker version` shows Server, busybox rc 0).
- Before run `docs/worklogs/SG-338_before.log` ≈1794955171–1794955209: **37 failed | 525 passed (562); 8 files failed | 73 passed (81)** — exact SG-336 map, confirmed per file (PB-1): AssetDetailPage.test 18, sg272 6, sg271 3, sg312 3, sg324-p3 3, sg318 2, sg324-p1 1, theme-adoption 1.
- G2 T8 written 1794955241–1794955292; FAIL run `SG-338_fail.log` 1794955294–1794955298 (1 failed | 7 passed of 8, `classifyAsset` 0 calls); fix 1794955305; PASS run `SG-338_pass.log` 1794955307–1794955310 (8/8); committed 1794955315.
- G1: theme+p1 1794955431–1794955446; p3 to 1794955502; sg318 to 1794955571; sg271 to 1794955598; sg272 to 1794955655; sg312 to 1794955709; big file to 1794955910 (22/23, Clear STOP).
- G3 started 1794955912 (770 s by stamps, inside the 800 s line): eslint 1794955912–1794955916; tsc 1794955929–1794955935; build 1794955938–1794955947; backend 1794955951–1794956058; frontend full 1794956065–1794956094; twice runs 1794956103–1794956125; end health 200 at 1794956125.
- Scratch removed 1794956141; gate-log commit 1794956149. Elapsed ≈1024 s — inside the 1100 s stop line.

## G2 — Add another pack copies the shelf-life category

- `frontend/src/routes/AssetDetailPage.tsx` `addPackMut` (≈963–1005): after the create + per-location assigns, reads the opened item's classification via the existing helpers (`latestActiveAssertion` + `valueRecord` on `plugin:expiry-tracker/classification`) and, when a category exists, calls the existing `classifyAsset(created.id, householdId, openedCategory)`; a copy failure keeps the pack and sets `Kept the new pack, but its shelf life would not copy.` No backend change.
- T8 (`frontend/src/sg336-item-page.sg336.test.tsx:272–286`): create asserted as before, then `expect(api.classifyAsset).toHaveBeenCalledWith("pack-4", "hh", "food_beverages")` plus no-other-id isolation `filter(([id]) => id !== "pack-4")` → `[]`. FAIL before (0 calls, `SG-338_fail.log`), PASS after (`SG-338_pass.log`, 8/8).

## G1 — per file, old → new (no assertion deleted without a same-behaviour replacement)

Common to every file except theme-adoption: the `apiGet` mock now serves the packs list read (`path === "/v1/assets"` → `{ items: [{ id, display_name, status }] }`) so `findSameNamePacks` resolves and pack rows render; detail reads unchanged. Comparison proving the list shape is what the page really sends: `frontend/src/lib/sameNamePacks.ts:22–26` (`/v1/assets` + `q`/`limit`, `items` filtered by trimmed lower-cased name).

- `theme-adoption.test.tsx:182–193` (1): old `expectPageHeader(/theme asset/i)` (required `page-header` class) → new: `h1` keeps `text-foreground`, NOT `page-header`, `fontSize 44px`/`fontWeight 600` — the mockup wording (page `AssetDetailPage.tsx:1159`). File green with p1: 14/14.
- `sg324-p1.sg324.test.tsx:66–117` (1): old bare `findByRole Edit` → new `findByTestId pack-row-asset-1` + `within(row) Edit`, same `toHaveClass(themedToken())` (`sg-paper-control`). 2/2.
- `sg324-p3.sg324.test.tsx:47–61,91–141` (3): old sections on load → new `openMore()` helper (clicks `More about this item`) then same table/rows; row assertions scoped via `findByRole table` (the Kind-of-item heading fact above the packs duplicates the words). 3/3.
- `sg318-plain-words.sg318.test.tsx:155–224` (2): W2 old Details on load → new open More, rows scoped to the Details `table` (Kind/Status/Unit; the `dl` heading fact collides on Kind of item); W3 old History on load → new open `History (` then history-row-anchored `/^Added \u2014/` and `/^Accepted \u2014/` (the pack row's `1 pcs · added 14 Sep` muted line otherwise matches loose `Added`). 10/10.
- `AssetDetailPage.sg271.test.tsx:86–145` (3): proposed-date Accept/prefill old global form → new `openPackEditor` (pack row Edit, `pack-row-asset-271`) with `within(row)` scoping; shelf-life preselect + unmapped-note old global → new `openMore()`. 3/3.
- `AssetDetailPage.sg272.test.tsx:87–185` (6): −1/+1, amount-edit, None-left, three gone reasons, Gone+Put back, AI note size all old global → new `openMore()`; three-reasons scoped to `region Use it up` (pack rows carry their own Used up); `markGone("asset-272","hh","used_up")` / `putBack("asset-272","hh")` arg assertions unchanged. 7/7.
- `sg312-screens.sg312.test.tsx:189–260` (3): header `Live · 500 ml left` → pack row `500 ml · added 14 Sep` (same amount, same no-`qty` rule; test renamed to `the pack row reads 500 ml, not qty`); Enrich line → new open More, same line; Manual expiry card → new pack-row Edit, same card/needs-date/paper assertions. 10/10.
- `AssetDetailPage.test.tsx:139–700` (18 → 17 green + 1 STOP): edit-quantity old `Edit` → new More > `Edit name and amount` (`Quantity` label, `Save`), same PATCH args; History old visible → new `openHistory()`, same `Updated`/no-`Replaced`; manual form (needs_evidence, prefill, clear-part, accept, documents) old global → new `openPackEdit("asset-1")`; non-perishable old hidden-form → new opened pack editor still hides (`hasWindows` false); unclassified message → new open More (form absence asserted at page level — the opened per-pack editor deliberately offers a date field even unclassified per T3, so the check stays at page level by design, noted not hidden); classification ×4, Locations ×3, Relations ×3, Enrich ×3 all old global → new `await openMore()` (async helper waits for load); assigned-locations row scoped via the select's own `section` (the Where heading fact also reads Fridge).

STOP item (reported, rest done): `AssetDetailPage.test.tsx` `Clear writes the null active and empties the form` — after Clear, `Date` empties and `Date cleared.` shows (local form state, both pass), but `Clear expiry date` does NOT disappear: `ExpiryEntryForm.clear()` (`ExpiryEntryForm.tsx:92–107`) invalidates only `["asset", id, householdId]` (the `useAsset` key), never `item-packs`, while `PackEditor` reads its detail from the packs query — so the row keeps the stale active date. Old page read the section from `useAsset` directly, so it refreshed. Fixing the page (invalidate `item-packs` on form writes) changes `AssetDetailPage.tsx` beyond G2 — out of scope per the ceiling, so STOP for that item. File committed fully updated (22/23, twice confirmed).

## Gate (G3)

- `eslint` (`SG-338_eslint.log`): only the known pre-existing `App.household-nav.test.tsx` `fireEvent` error — comparison `grep` shows no other file errors.
- `tsc --noEmit` (`SG-338_tsc.log`): clean, rc 0.
- Build into scratch (`SG-338_build.log`): `✓ built in 2.79s`, rc 0; `frontend/dist` untouched (`git status` clean except listed files).
- `make backend-test` (`SG-338_backend.log`): host `817 passed, 2 deselected`; image proof `2 passed, 6 deselected`; rc 0 — backend unchanged, as required.
- `make frontend-test` (`SG-338_frontend.log`): **1 failed | 562 passed (563); 1 file failed | 80 passed (81)** — the single failure is the Clear STOP above; before was 37/525.
- Twice (`SG-338_twice.log`): `*sg336*` + 7 green files 55/55 twice; `AssetDetailPage.test.tsx` 22+1 twice (same STOP both runs).
- Health 200 at start and end (end probe with the twice-run command output).

## Changed files

Frontend only: `AssetDetailPage.tsx` (G2 block only), `sg336-item-page.sg336.test.tsx` (T8), the 8 test files above, 9 `docs/worklogs/SG-338_*.log` + this report. No backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp` writes (never touched; SG-336's `/tmp/opencode/probe.tsx` left alone for the Architect); tree clean except `output/` logs; scratch `output/SG-338-scratch/` removed (verified `rm -rf` rc 0 before this report).

## Contract, UNCLEAR, REMAINING

- Contract: I received no contract version line.
- UNCLEAR: none.
- REMAINING: (1) the Clear STOP test above (needs a page-scope slice: invalidate `item-packs` on `PackEditor` form writes); (2) nothing else — 36/37 old assertions green, T8 green, gate green except the STOP.

## Criteria

- A1 — Preflight ran literally (socket listed, Server shown, busybox rc 0, health 200 start/end); phase seconds from stamps above. G3 started at 770 s, inside the 800 s line; total ≈1024 s, inside 1100 s.
- A2 — Every updated assertion named old → new with file:line above; none deleted without a same-behaviour replacement (unclassified form-level check documented with its T3 rationale); the one truly lost behaviour (immediate row refresh after Clear) named as STOP.
- A3 — T8 FAIL (`SG-338_fail.log`, 0 calls) before, PASS (`SG-338_pass.log`, 8/8) after.
- A4 — Gate counts exact: eslint known-only, tsc clean, build rc 0, backend 817+2, frontend 1 failed | 562 passed; named files twice green (55/55 ×2; big file 22+1 ×2).
- A5 — Frontend files only (test files + G2 page block); no backend/migration/lockfile/`.env`/live-DB/provider/container/deploy bytes; `frontend/dist` untouched; tree clean except `output/`; no `/tmp`; scratch removed.
- A6 — Vacuity checked: FAIL-before red suite shown; no assertion removed without replacement; every folded-section test opens More/History/pack-Edit first (async helpers wait for load); T8 asserts the classification write on the new id only and none on other ids; the one red assertion is the STOP, not a hidden deletion.
- A7 — See last line.

Verification: FAIL — Clear STOP: 1 test red (pack row keeps the stale date after Clear; page fix out of scope), gate 562/563.
