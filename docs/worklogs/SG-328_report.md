# SG-328 — The catalog always opens in Standard Grid (width rule retired)

SG-328 | model and effort: not visible in process arguments, so not stated and not inferred | workdir /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation resolved to 16e5d608b7947568da35e19b577182495419756c | WORK_HEAD pre-report 52283be7 (SG-328 G1 commit; post-report hash quoted in publish)

Contract: packet records 0.61.0 (AGENTS.md, D36). This lane denies reading the contract folder; I did not try. Host evidence: I received none — I received no contract version line in process args/env. I do not echo the project file's line as host evidence.

Elapsed 456 s (END 1794853529 minus G0_START 1794853073) vs expected ≈450 s (UNVERIFIED — my estimate: one small change plus SG-328 gate ≈300 s plus backend image proof). Phases: G0 26 s (3073→3099: preflight + BASE resolve), G1 207 s (3099→3306: FAIL run 3170, PASS run 3245, older 6-file run 3254, commit 3306), G2 223 s (3306→3529: lint 3314, tsc 3329, build 3343, backend 3356→3478, frontend 3478, named x1 3510, named x2 3516, end health 3529). Runtime against RUN_BUDGET_S 2100 s: 456/2100, inside. 1100 s stop not reached, no early stop.

Change (frontend only, one default value and the code that computes it):
- frontend/src/routes/CatalogPage.tsx:38-40 new SG-328 comment (owner 2026-11-16 directive; SG-212/D-21 width rule retired); import line 1 now `useEffect, useMemo, useState` (removed `useLayoutEffect, useRef` — comparison: `grep useLayoutEffect|useRef` in file now returns NO_MATCH_REMOVED_OK); removed `CATALOG_TABLE_FIT_MIN_PX = 860`, `measureContentColumnWidth`, `resolveInitialDensity` (old lines 38-52; comparison: `grep -n CATALOG_TABLE|resolveInitial|measureContent` now returns no match); state line 52 `useState<Density>("grid")` unchanged as the single default; removed `contentColumnRef` + mount `useLayoutEffect` (old lines 66-75); div line 262 now `<div data-testid="catalog-content-column">` with no `ref` (comparison: `grep -n catalog-content-column` returns only line 262, no `ref=`). Toggle (`CatalogToolbar.tsx`, `DENSITY_LABELS`) unchanged.
- Removed because nothing else reads it: `grep -r resolveInitialDensity|CATALOG_TABLE_FIT_MIN_PX|measureContentColumnWidth|contentColumnRef` in frontend/src returns only the retired tests' history (now updated) and no product file — comparison proves single use in CatalogPage.tsx; `grep -r clientWidth` in frontend/src after change returns no product match (the spy in updated tests now asserts `not.toHaveBeenCalled()` and passes, proving no read); `useLayoutEffect`/`useRef` removed from import because no other statement in the file uses them (comparison: file compiles with `tsc --noEmit` exit 0, and `eslint` shows no new error in this file).

Premises (PB-1, each confirmed or falsified):
- State already starts as `"grid"` (old :65): CONFIRMED — line 52 still `useState<Density>("grid")`.
- Width rule + mount effect is the change (old :38-52, :69-75): CONFIRMED — removed exactly those.
- `measureContentColumnWidth` and `contentColumnRef` have no other use: CONFIRMED — grep shows only CatalogPage.tsx used them; div kept without ref for the test anchor.
- Toggle stays one click away: CONFIRMED — CatalogToolbar.tsx untouched; new tests click Compact Table → table and back.

Test changes (each named, old → new):
- NEW frontend/src/sg328-grid-default.sg328.test.tsx (3 tests, shape copied from catalog.test.tsx drawer-wiring Asset): wide 1280 px opens Standard Grid; narrow 320 px opens Standard Grid; Compact Table switches to table and back. FAIL 2 failed/1 passed (wide + toggle failed on table-first), PASS 3 passed. Logs docs/worklogs/SG-328_fail.log, SG-328_pass.log name the file and first assertion `expect(...Standard Grid...).toHaveAttribute("aria-pressed","true")` (got false before, true after).
- UPDATED frontend/src/components/catalog/catalog.test.tsx describe `CatalogPage width-adaptive density default (SG-212 / D-21)` → `CatalogPage grid default (SG-328; width rule retired)`: `a content column >=860 px at mount initialises the table` → `a wide content column (1280 px) opens in Standard Grid (was >=860 table)`; `a content column <860 px at mount initialises the grid` → `a narrow content column (320 px) still opens in Standard Grid (was <860 grid)`; `an unreadable measure ... falls back to the grid` → `an unreadable measure still shows the grid (was fallback to grid)`; `the toggle flips ... recomputes (no stored choice)` → `the toggle flips ... stays on the grid (was recomputes from width)` (remount now expects Standard Grid + product-card, not Compact Table + product-row). Each now asserts `spy not.toHaveBeenCalled()` proving retirement. Comparison: old file asserted `spy toHaveBeenCalled()` + table at 860; new asserts grid at 1280 + spy never called.
- UPDATED frontend/src/sg325-p8.sg325.test.tsx (established instead: renders CatalogPage and depended on 900 px width for the table, not asserting the rule but broken by its removal): removed `mockContentColumnWidth` helper + `mockContentColumnWidth(900)` calls; `the table replaces Status with Use by...` now renders → awaits product-card (proves grid default) → clicks Compact Table → awaits product-row (was: 900 px → directly product-row); `the card view shows the same dates...` now renders → directly awaits product-card (was: 900 px → product-row → click Standard Grid). Comparison: `grep -n mockContentColumnWidth` in that file now returns no match; suite passes 2/2.

Gate counts (exact, logs docs/worklogs/SG-328_<step>.log):
- eslint: 1 problem (1 error, 0 warnings) only in frontend/src/App.household-nav.test.tsx:2 `fireEvent defined but never used` — the known error; zero errors in changed/new files. Log SG-328_lint.log shows exactly that block.
- tsc: `./frontend/node_modules/.bin/tsc --noEmit -p frontend/tsconfig.json` exit 0, empty log SG-328_tsc.log (0 errors).
- build: `npm --prefix frontend run build -- --outDir $PWD/output/SG-328-scratch/build` exit 0, 1973 modules transformed, built in 3.05 s, outDir absolute under scratch. Log SG-328_build.log.
- backend-test (backend unchanged, proves it): host `817 passed, 2 deselected` in 89.95 s; image proof `docker build` + `docker run --rm --network none ... requires_native_libs tests/test_signals.py` → `2 passed, 6 deselected`. Log SG-328_backend.log shows both counts verbatim.
- frontend-test (whole suite): `73 passed (73 files), 529 passed (529 tests), 0 failed`. Log SG-328_frontend.log shows `Test Files 73 passed (73)` and `Tests 529 passed (529)`.
- named twice (sg328 + 2 older changed): x1 `3 passed (3 files), 42 passed (42 tests)`; x2 identical `3 passed, 42 passed`. Logs SG-328_named_x1.log, SG-328_named_x2.log.
- older catalog renderers pre-commit: `6 passed (6 files), 87 passed (87 tests)` (catalog.test, sg325-p8, query-error-alerts, CatalogPage.sg272, shell, panel.sg307). Raw log output/SG-328-scratch/logs/catalog-older.log (removed with scratch; counts quoted here).

Changed files (frontend only):
- M frontend/src/routes/CatalogPage.tsx
- M frontend/src/components/catalog/catalog.test.tsx
- M frontend/src/sg325-p8.sg325.test.tsx
- A frontend/src/sg328-grid-default.sg328.test.tsx
- A docs/worklogs/SG-328_fail.log, SG-328_pass.log (G1 commit 52283be7)
- A docs/worklogs/SG-328_lint.log, SG-328_tsc.log, SG-328_build.log, SG-328_backend.log, SG-328_frontend.log, SG-328_named_x1.log, SG-328_named_x2.log, SG-328_report.md (report commit)
- No backend, migration, Dockerfile, compose, lockfile, dependency, .env, live database, stored file, host, provider, container or deploy byte; frontend/dist untouched (build went to absolute scratch outDir); no /tmp (TMPDIR, DOCKER_CONFIG, PYTEST_ADDOPTS all under output/SG-328-scratch; comparison: `git status` shows no /tmp path); tree clean except output/ (untracked scratch only, removed before report: `rm -rf output/SG-328-scratch`); .vite removed.

UNCLEAR: none. REMAINING: none — G0, G1, G2 all done; no STOP fired (no backend-needing item, no denied privileged op, no refused push yet — publish next).

Criteria (one line each):
- A1 — Preflight ran literally with date +%s 1794853073; docker version shows Server 29.9.2/API 1.56, busybox rc 0; health 200 at start (1794853073 block) and end (1794853529 `200`); phase seconds from stamps above.
- A2 — G1 done with file+line above; every wrong premise named (all 4 confirmed, none falsified to STOP); removed code named with `grep` no-match comparisons proving nothing else reads it.
- A3 — FAIL before (2 failed/1 passed, wide expects grid got table) and PASS after (3 passed) with logs SG-328_fail.log / SG-328_pass.log naming file + first assertion.
- A4 — Gate green with exact counts above; named 3-file set green twice (42 + 42).
- A5 — Frontend files only (4 listed); no backend/migration/Dockerfile/compose/lockfile/.env/live-DB/stored-file/host/provider/container/deploy byte; frontend/dist untouched; no /tmp; tree clean except output/; scratch `output/SG-328-scratch` removed before report.
- A6 — PB-3 vacuity checked: wide-first table would have been the failure (saw it in FAIL run: aria-pressed false + no product-card); toggle that no longer switches would fail (covered by third new test + updated toggle test, both green); a test that never sets a width would miss the regression (wide test sets 1280 px explicitly, narrow sets 320 px); a red suite would block (whole suite 529 green, named twice green).
- A7 — This report's last line is the Verification line below.

Verification: PASS
