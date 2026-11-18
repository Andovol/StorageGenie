# SG-337 report — same-name packs show as one card in the catalog grid

SG-337 | model and effort: not visible in the process arguments, so they are stated as not visible and nothing is inferred | working directory `/home/andrei/StorageGenie` | remote `git@github.com:Andovol/StorageGenie` | BASE ref `origin/automation` resolved to `c52e74048afbb3b09700611bf2637279bf00428e` | WORK-HEAD `7de555db` (3 commits: G1 tests, G2 change, G2 test-update + gate logs; report commit follows).

## Time (from `date +%s` stamps)

- Session start 1794994230. G0 preflight 1794994230–1794994231 (health 200, `docker version` shows a Server section, busybox rc 0).
- G0 premises 1794994234–1794994444 (files, rule, wordings, counts, G4/G5 causes). G1 test write + FAIL run 1794994444–1794994459 (`SG-337_fail.log`: 6 failed | 2 passed); G1 commit 1794994469.
- G1 change + PASS run 1794994469–1794994538 (`SG-337_pass.log`: 8 passed); G2 change commit 1794994542.
- G2 gate: eslint 1794994561–1794994565; tsc 1794994587–1794994593 (clean); build 1794994568–1794994578 (rc 0); backend 1794994596–1794994704 (817 passed host + 2 passed image); frontend-first 1794994710–1794994743 (572 passed, 1 failed → sg325-p8 old→new fix); frontend 1794994766–1794994797 (573 passed); twice 1794994803–1794994833 (all green); end health 200 at 1794994838.
- Scratch `output/SG-337-scratch/` removed 1794994849 (`output/` itself and `output/dispatch` never touched); test-update + logs commit 1794994852. Elapsed ≈ 622 s — inside the 1100 s stop line. No stop triggered; nothing REMAINING.

## G0 — Preflight and premises

- Health 200 at start (1794994231) and end (1794994838); `docker version` shows a Server section and `docker run --rm busybox true` is rc 0 — proved by the preflight output, not assumed.
- Contract line received with this task: none — I received no contract version line (stating this exactly as instructed, never the project file's `AGENTS.md` line). The `contract` folder was never read; the denial was never probed, so no STOP arose.
- Wrong premise in the packet, named: the catalog page is not at `frontend/src/pages/CatalogPage.tsx` — it lives at `frontend/src/routes/CatalogPage.tsx`. All work used the real path.
- Same-name rule, established from the current `frontend/src/lib/sameNamePacks.ts` (moved there by SG-336 commit `82f88636`, which the log confirms): name trimmed and lower-cased, exact match, live items only via `NOT_LIVE_STATUSES` (`ARCHIVED`, `DISPOSED`, `MERGED`) — `sameNamePacks.ts:9,35-45`. Confirmed, not UNVERIFIED.
- Attention-line wording, found and kept (before = after): `1 item is past its date` / `<N> items are past their date`, `1 runs out this week` / `<N> run out this week`, joined with ` and ` plus trailing `.` — `CatalogPage.tsx:76-82`.
- Result count, established and named: the `Your things` title carries `{titleCount} things` (`AppShell.tsx:77-80`) with `titleCount={displayed.length}` (`CatalogPage.tsx:344`) — it counts loaded packs, not cards. Kept as packs.
- G4 cause, named: both date chips carried `whiteSpace: "nowrap"` with no width cap (`ProductCard.tsx` old lines 190/205), so the past chip `Past · <day>` overflowed its 79.5 px column at 390 px / 4-per-row.
- G5 cause, named: the attention line and grid rode `PageContainer` (max-width 1100, auto margins, padding 24 → inner content at x≈114 at 1280) while the title (`AppShell.tsx` padding `16px 24px 4px`) and toolbar (padding `8px 24px`) sit full-bleed at x≈24. `AppShell` is used only by `CatalogPage` (proved by grep: no other route imports it), so changing its content wrapper touches only the catalog; other pages keep `PageContainer`.

## G1–G5 — The change (frontend only, no backend/migration/deploy)

- `frontend/src/lib/sameNamePacks.ts:16-24` — added the pure `sameNameKey` / `isSameName` helpers; `findSameNamePacks` (`:35-45`) now uses `sameNameKey` with byte-identical behaviour (no empty-name guard added, so the SG-336 item page and capture form are unaffected).
- `frontend/src/components/catalog/groupPacks.ts` (new) — grid-only grouping by `sameNameKey` (the shared rule, never a second copy): date order soonest-first / no-date-last (`:30-39`, same comparator the SG-336 page uses), representative = soonest pack's name-as-written/date/id with the first-with-media photo fallback (`:41-59`), groups re-sorted by the live sort (`useby` → soonest date, `name` → name, `recent` → soonest pack's added date, `:62-79`).
- `frontend/src/routes/CatalogPage.tsx:14,268-286,444` — `visibleItems` stays one entry per pack (table, Gone view, attention line, title count all read it, unchanged); the grid reads `groupedItems`. Search still narrows packs server-side first, then groups what is left.
- `frontend/src/components/catalog/ProductCard.tsx:16-19,100-103,194-236` — card shows `<N> packs` (muted, `data-testid="product-packs"`) only when N ≥ 2; G4 fix: both date chips get `maxWidth: "100%"` with wrapping allowed (`whiteSpace: "normal"`, `overflowWrap: "break-word"`) instead of `nowrap` — wrapping chosen over shortening so the full date stays readable.
- `frontend/src/components/shell/AppShell.tsx:125-141` — the catalog `main` keeps `data-testid="page-container"` / `page-container` class but is full-width with explicit 24 px sides and no 1100 px cap or auto margins, so the grid and attention line share the title's left edge and content width. `PageContainer.tsx` itself untouched (other pages keep the 1100 px container; `PageContainer.test.tsx` still green).
- G1: one card per name (soonest name/date/photo, `3 packs`); G2: groups sort by soonest date or name while attention/title keep counting packs; G3: table one row per pack and Gone one entry per pack unchanged (no code touched there).

## Tests

- New `frontend/src/sg337-grouped-packs.sg337.test.tsx` (shapes copied from `catalog.test.tsx`'s drawer-wiring asset and the sg331 `row()` expiry shape, never hand-made): FAIL before (`SG-337_fail.log`, 6 failed | 2 passed — T4 packs-count and T5 table already passed, documenting unchanged behaviour), PASS after (`SG-337_pass.log`, 8 passed).
- Older tests updated, each named old → new:
  1. `frontend/src/components/shell/shell.test.tsx:310` — old: catalog main rides the shared centered container (maxWidth 1100, auto margins); new: catalog main is full-bleed with the title's 24 px sides (G5).
  2. `frontend/src/sg325-p8.sg325.test.tsx:139` — old: card view shows 3 cards with both same-name dates; new: 2 cards, one Olive Oil card with the soonest date + `2 packs`, the later date absent from the grid (lives on the item page/table, which the unchanged table test still proves per-pack).
- No other older test asserted one card per pack in the grid (`catalog.test.tsx` grid-count uses 8 distinct mock names; sg331 fixtures are distinct names) — verified by the green full suite, not assumed.

## Gate (exact counts)

- eslint `SG-337_eslint.log`: 1 error, only the known `App.household-nav.test.tsx` unused-`fireEvent` — no other finding.
- `tsc --noEmit` `SG-337_tsc.log`: rc 0, 0 bytes.
- Build into scratch `SG-337_build.log`: rc 0 (`index-BGZFjW5B.js` 387.47 kB) with absolute `--outDir "$PWD/output/SG-337-scratch/build"`; `frontend/dist` (git-ignored, pre-existing) untouched.
- `make backend-test` `SG-337_backend.log`: host 817 passed, 2 deselected + image proof 2 passed, 6 deselected (backend unchanged — this only proves it).
- `make frontend-test`: first run 572 passed + 1 failed (sg325-p8, fixed old→new, kept as `SG-337_frontend-first.log`); rerun `SG-337_frontend.log`: 82 files passed, 573 passed, 0 failed.
- Twice `SG-337_twice.log`: `sg337` 8×2, `sg336` 10×2, `shell.test.tsx` 23×2, `sg325-p8` 2×2 — all rc 0.
- Scope: frontend files only (5 modified + 1 new + 2 test updates); no backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, provider, container or deploy bytes; no `/tmp` anywhere (proved by grep over every touched source file); tree clean except `output/` (pre-existing `SG-324-scratch` + `dispatch` left alone) and the new worklog logs.

## PB-3 vacuity (what a vacuous pass would look like — each checked)

- Two `Olive Oil` cards instead of one — checked by T1 (3 cards total, one `3 packs` card).
- A `1 packs` line — the line renders only when N ≥ 2 (`ProductCard.tsx:227`); T1's Rice card asserts no `product-packs` line for a single pack.
- The later date on the card — T1 asserts `Use by 6 May 2030` (soonest), and the updated sg325-p8 test asserts `3 Feb 2031` is absent from the grid.
- A grouped table — T5 asserts 5 rows with three Olive rows (table reads ungrouped `visibleItems`).
- An attention line counting cards — T4 renders two same-name past packs (one card) and asserts the line reads `2 items are past their date`.
- A second copy of the matching rule — `groupPacks.ts` imports `sameNameKey` from `sameNamePacks.ts`; `rg` shows the trim/lowercase logic exists only there.
- A red suite — full suite 573/573 green plus the four named files twice green.

## Criteria

- A1 — Preflight green (Server section, busybox rc 0), health 200 at 1794994231 and 1794994838; elapsed ≈ 622 s from stamps, inside the stop line.
- A2 — G1–G5 done with file:line above; the `pages/` path premise falsified and named; attention/count wordings quoted before = after; G4/G5 causes named.
- A3 — FAIL 6|2 then PASS 8|8, logs named.
- A4 — Gate green with exact counts above; sg337, sg336, shell, sg325-p8 each twice green.
- A5 — Frontend-only file list above; no forbidden bytes; `frontend/dist` untouched; no `/tmp`; tree clean except `output/`; scratch removed before this report.
- A6 — PB-3 checks listed above, each with the assertion that would catch it.
- A7 — The last line of this report is `Verification: PASS`.

Verification: PASS
