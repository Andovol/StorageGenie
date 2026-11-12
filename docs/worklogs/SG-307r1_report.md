SG-307r1 | model and effort: not visible to me (no process arguments were received, so I state that and infer nothing) | cwd /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation -> resolved 21d5761aff036fd481f95dc305d957163c66b1e4 | WORK_HEAD f22cb4b8874f57eb00df28f69bb054062b61a988 (this report's commit follows it)

# SG-307r1 report: SG-307's three fixes, then the full gate SG-307 did not reach

**Result: G0, R1 done and committed (FAIL-then-PASS 4/0 on base, 4/4 on candidate); R2 gate run to completion — tsc green, build green, backend host + image green, new+changed files twice green (71/71 x2) — but eslint shows 2 errors (one beyond the known one) and the frontend suite shows 8 failures identical on base. Verification: FAIL.**

## Elapsed and phase seconds (stamps from `date +%s`)

- Start 1794508842. G0 preflight 1794508842 to 1794508843 (1 s): `docker version` shows a Server section, `docker run --rm busybox true` rc 0; health 200 at start.
- Reads + R1 fixes 1794508843 to 1794509141 (~298 s). R1 committed 1794509141 (299 s elapsed — inside the 500 s rule; nothing marked REMAINING).
- R2 gate 1794509141 to 1794509491 (~350 s): eslint red 1794509197; tsc red-then-green (type fix in the new test) 1794509274; build rc 0 1794509284; `make backend-test` rc 0 1794509395; `make frontend-test` rc 1 1794509425 (8 pre-existing failures, same 8 on base); twice runs 71/71 and 71/71 at 1794509473; health 200 at end 1794509479; scratch + base worktree removed 1794509479; R2 committed 1794509491 (649 s elapsed — inside the 1100 s line).
- Base worktree `output/SG-307r1-scratch/base` added at 21d5761 (node_modules symlinked, the one new file copied in; FAIL run there) and removed with `git worktree remove --force` before scratch removal.

## Premises, each confirmed or falsified (file:line as read before edits)

- **Band-aid on Pantry buttons CONFIRMED:** `frontend/src/theme/tokens.css:237-243` forces paper on `[data-testid="pantry-tile"] button` / `[data-testid="pantry-notice"] button` with four `!important` declarations, because SG-307's packet kept `PantryPage.tsx` out of scope while its inline `ACTION_STYLE` (`frontend/src/routes/PantryPage.tsx:51`) still says `backgroundColor: "hsl(var(--card))"`.
- **Title-cased category CONFIRMED:** `labelAssetType` (`frontend/src/lib/labels.ts:102-105`) title-cases unknown keys, so `food_beverages` reads *Food Beverages*.
- **Source of the Expiry words ESTABLISHED:** the Expiry page does not hold the words statically — it reads them at runtime from the served taxonomy (`frontend/src/routes/ExpiryPage.tsx:118-119`: `taxonomy?.plugins.find(plugin => plugin.plugin_id === "expiry-tracker")?.categories`, `categoryName` maps id to `name`). That taxonomy is defined in `backend/app/plugins/expiry_tracker.py:160-194` (`CATEGORIES`: `food_beverages` → *Food & beverages*, `medicine_pharma` → *Medicine/pharma*, `cosmetics_personal_care` → *Cosmetics/personal care*, `household_chemicals` → *Household chemicals*, `documents_other` → *Documents/other*, `non_perishable` → *Non-perishable*; mirrored in `backend/app/plugins/descriptor.py:134-174`). The one source named for `labelAssetType` is therefore the served taxonomy `GET /v1/taxonomy` (expiry-tracker categories), spelled as in `expiry_tracker.py` CATEGORIES.
- **Version on the panel CONFIRMED:** `frontend/src/components/shell/ItemInspectorDrawer.tsx:447-449` renders `Version {current.version}` beside Save; the `If-Match` header is sent at `:148`.

## How each fix was met (file named for each)

- **Fix 1 — Pantry at the source:** `ACTION_STYLE` in `frontend/src/routes/PantryPage.tsx:42-56` now uses `backgroundColor: "hsl(var(--paper))"` (the `--line` border and `--ink` text it already had are unchanged; `minHeight: 40` kept per SG-300). The `!important` Pantry block in `frontend/src/theme/tokens.css` (old `:233-243`) is removed and replaced with an SG-307r1 comment recording the removal — no band-aid rule remains.
- **Fix 2 — taxonomy words:** `ASSET_TYPE_LABELS` in `frontend/src/lib/labels.ts:97-112` gains one entry per taxonomy key, spelled exactly as the Expiry source (`Food & beverages`, `Medicine/pharma`, `Cosmetics/personal care`, `Household chemicals`, `Documents/other`, `Non-perishable`); existing `product`/`unknown` entries unchanged; the title-case fallback stays for truly unknown keys.
- **Fix 3 — Version off the screen:** `frontend/src/components/shell/ItemInspectorDrawer.tsx` renders `<span data-version={current.version} style={{ display: "none" }} />` where the Version line was — no *Version* text on screen, the value kept as a `data-version` attribute. The `If-Match` header behaviour (`:148`) is unchanged.

## Test changes (all named)

- New `frontend/src/routes/sg307r1-fixes.sg307r1.test.tsx` (4 tests): (1) no Pantry tile button inline style contains `--card`, and the *Use it up* button is paper with `minHeight 40px`; (2) `tokens.css` contains no `pantry-tile` selector and no `pantry-tile`/`pantry-notice` rule block; (3) the Expiry page renders *Food & beverages* (from the mocked served taxonomy) and `labelAssetType` equals that word for `food_beverages` and for every taxonomy key, with `unknown`/`product` unchanged; (4) the panel renders no `Version` text while a `[data-version="1"]` hook keeps the value. One post-R1 edit, test-only: the `filter` callback parameter typed `(block: string)` to satisfy `tsc` (committed in R2).
- Older tests updated: **none** — greps over all `*.test.*` for `Version`, `--card`, and `Food Beverages` return zero matches (comparison: `rg` output empty), so no older test asserts replaced wording or styling. Behaviour tests (e.g. the drawer `If-Match` PATCH test) are untouched and still pass.

## FAIL-then-PASS (R1)

- FAIL on base worktree at `origin/automation` 21d5761 (node_modules symlinked, the new file copied in): **4 failed, 0 passed** (`docs/worklogs/SG-307r1_fail.log` holds names + first assertion only). First assertions: inline style `not to contain '--card'`; `tokens.css` `not to contain 'pantry-tile'`; `expected 'Food Beverages' to be 'Food & beverages'`; `expected <span …> to be null`.
- PASS on candidate: **4 passed** (`docs/worklogs/SG-307r1_pass.log`).

## Gate counts (R2)

- `eslint src`: **rc 1, 2 errors** (`docs/worklogs/SG-307r1_eslint.log`). (a) `src/App.household-nav.test.tsx:2` — `fireEvent` unused: the one known pre-existing error the packet names. (b) `src/components/shell/AssetImportModal.tsx:76` — `dragOver` unused: introduced by SG-307 G1 (`8c62201` edited that file and dropped the only read at old line 206 — proven by `git show 0dd3fa7:...AssetImportModal.tsx` which uses `dragOver` in a ternary vs current which only calls `setDragOver`); byte-identical on base 21d5761, so pre-existing on base and out of this slice's product scope (touching that file is a STOP), left unfixed.
- `tsc --noEmit`: **rc 0**, empty log (`docs/worklogs/SG-307r1_tsc.log`), after the one test-only type fix above.
- Frontend build: **rc 0** in 3.25 s (`docs/worklogs/SG-307r1_build.log`). Deviation disclosed: the shell ran with cwd `frontend/`, so `--outDir $PWD/output/...` resolved to `frontend/output/SG-307r1-scratch/frontend-build`; that whole `frontend/output/` tree was removed afterwards — `git status` is clean of it.
- `make backend-test`: **rc 0** (`docs/worklogs/SG-307r1_backend-test.log`) — host suite **805 passed, 2 deselected** (81 s); image proof **2 passed, 6 deselected**.
- `make frontend-test`: **rc 1** (`docs/worklogs/SG-307r1_frontend-test.log`) — **458 passed, 8 failed of 466** (4 files: AssetForm 2, InboxPage 2, theme-adoption 1, shell 3). The same 4 files fail identically on the base worktree (**8 failed, 48 passed of 56** there) — pre-existing SG-307 fallout (e.g. `shell.test.tsx:320` expects `bg-primary`, received `sg-paper-control`), out of this slice's scope, named here and left untouched.
- Twice runs (every `*.sg307*` file + every older file SG-307 or this retry changed — `catalog.sg307`, `panel.sg307`, `sg307r1-fixes`, `catalog.test`, `drawer.test`): **71 passed / 5 files, twice consecutively, rc 0 both** (`docs/worklogs/SG-307r1_twice-1.log`, `SG-307r1_twice-2.log`; 71 equals 71).

## Changed files

Product: `frontend/src/routes/PantryPage.tsx`, `frontend/src/theme/tokens.css`, `frontend/src/lib/labels.ts`, `frontend/src/components/shell/ItemInspectorDrawer.tsx`. Tests: `frontend/src/routes/sg307r1-fixes.sg307r1.test.tsx` (new). Evidence: `docs/worklogs/SG-307r1_fail.log`, `SG-307r1_pass.log`, `SG-307r1_eslint.log`, `SG-307r1_tsc.log`, `SG-307r1_build.log`, `SG-307r1_backend-test.log`, `SG-307r1_frontend-test.log`, `SG-307r1_twice-1.log`, `SG-307r1_twice-2.log`, `SG-307r1_report.md`. Zero backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; tree clean except `output/` (which holds only the pre-existing `SG-301-scratch` and `output/dispatch`, both untouched); scratch `output/SG-307r1-scratch/` removed before the report (comparison: `git status --short` shows only the files named here).

## Contract line

Contract line: I received none. (The packet records `0.59.0` but gives no line of my own; this lane denies the contract folder, so I did not read it.)

## UNCLEAR / REMAINING

- **UNCLEAR (/tmp):** one eslint re-run redirected its tail through `/tmp/eslint_tail.txt`; subsequent `/tmp` access is denied by the tool permissions, so I could neither verify nor remove that path. No other command used `/tmp` (npm cache lived in the removed scratch).
- **Not fixed (out of scope, both pre-existing on base):** the `AssetImportModal.tsx:76 dragOver` eslint error (SG-307-introduced, fixing it means touching a product file outside the scope ceiling — a STOP) and the 8 frontend-suite failures (SG-307 styling fallout, identical on base).
- **No REMAINING gate work:** every R2 step ran and is logged; only the two red findings above stand.

## One line per criterion

- **A1** — All three fixes made and each says how with its file above; the category-word source (served taxonomy `GET /v1/taxonomy`, expiry-tracker categories per `expiry_tracker.py` CATEGORIES) is named. Met.
- **A2** — R1 FAIL 4/0 on base, PASS 4/4 on candidate, logs hold names + first assertions; no older test asserted replaced wording (empty-grep comparison), so none updated. Met.
- **A3** — Gate NOT green: eslint has a second error beyond the known one and the frontend suite has 8 pre-existing failures (counts exact above); twice runs green 71/71 both times. Not met.
- **A4** — Zero backend/migration/Dockerfile/compose/lockfile/dependency/`.env`/live-DB/stored-files/host/provider/container/deploy bytes; `frontend/dist` untouched; tree clean except `output/`; scratch removed — with the one UNCLEAR `/tmp` redirect disclosed above. Met except that disclosure.
- **A5** — Preflight proven (Server section, busybox rc 0); health 200 at start and end; phase seconds from stamps above. Met.
- **A6** — Vacuity: a failure would look like an `!important` Pantry rule still present (asserted absent — `not.toContain('pantry-tile')`), `--card` in `ACTION_STYLE` (asserted absent from every tile button style), *Food Beverages* rendered (asserted equal to *Food & beverages*), *Version* rendered (asserted null with `data-version` present), a red gate step (the eslint second error and 8 suite failures are red and reported as such, not hidden), a twice-run that differs (71 equals 71). Checked.
- **A7** — The last line is FAIL because A3 is not met.

Verification: FAIL — A3 (eslint shows a second error beyond the known one in AssetImportModal.tsx:76; the frontend suite has 8 failures that are identical on base).
