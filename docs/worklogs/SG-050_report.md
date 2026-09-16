SG-050 — drawer click wiring: onSelect props + catalog mount (opencode, medium)

Dispatch-ID: SG-050 · Coder: opencode · Effort: medium (process args `--variant medium`) ·
Model: `unknown` (no `--model` on argv; per policy the CLI default is the model and is omitted —
provider banner in `output/dispatch/SG-050.log:2` prints `build · deepseek-v4.1-flash`, recorded as
provider metadata, not an argv fact, CO-78) · Contract: 0.27.0.
BASE REF: `origin/automation` — BASE COMMIT (resolved): `7c15083dc20867bcfa74d195d23dd461029e98cd`
(start HEAD; worktree clean at start, `git status --porcelain` empty).
WORK_HEAD: the commit carrying this report + worklog + verify log (resolved hash published in the
receipt note; labelled work commit, not a tip, per CO-55c).
Work dir: `/home/andrei/StorageGenie` · Remote: `git@github.com:Andovol/StorageGenie.git` (as on host).
Spend: `$0` metered · Network: none (AI OFF, no npm install, no fetch beyond the receipt git
refspecs) · DB: none new · Restart: none. Autonomy: L3 (D63 wardrobe track).
Live-state ledger: **no live writes.** The drawer form was exercised only under vitest with
`apiPatch` mocked (catalog.test.tsx + drawer.test.tsx); no user-confirmed PATCH reached a running
service, no DB row changed. Live spend `$0`.

## (a) Issues / deviations / surprises

- **Premise correction (F-1) — the invalidation already lives in the drawer, not in `CatalogPage`.**
  G2 says "drawer PATCHes invalidate the `assets` + `asset` query keys (the pattern SG-046 prepared
  but reverted)". Verified: `ItemInspectorDrawer.tsx:115-124` already contains
  `qc.invalidateQueries({ queryKey: ["assets"] })` and `qc.invalidateQueries({ queryKey: ["asset",
  asset.id] })` — shipped by SG-046 and passing its 96 rating. SG-046 reverted only the *CatalogPage*
  hunk, not the drawer's own invalidation. Mounting the drawer therefore satisfies G2's invalidation
  requirement with no duplicate code (G-A7: "two props + one mount"). Proven end-to-end from the
  mount (catalog.test.tsx) and at unit level (drawer.test.tsx); M2 mutation falsifies the key.
- **Premise correction (F-2) — click-owner line numbers.** The packet cites table row clicks at
  `ProductGrid.tsx:99-100`. `:100` is the `openDetail` navigate definition; the row handlers are
  `:139` (`onClick`) and `:140-142` (`onKeyDown` Enter), with the `...` action at `:206-212`. Same
  owner, different line anchors — corrected, not contradicted. Card owner `ProductCard.tsx:73-74`
  (`<Link>`) and `CatalogPage` owning no click event both confirmed exactly.
- **No STOP.** Unlike SG-046, every requirement this time names a file the ceiling enables
  (`ProductCard.tsx`, `ProductGrid.tsx`, `CatalogPage.tsx`, the two test files, worklogs). No
  out-of-ceiling edit was needed and none was shipped.
- **Mutation touched a non-ceiling file, temporarily only (disclosed).** M2 mutates
  `ItemInspectorDrawer.tsx` because the invalidation key lives there. It was applied and reverted in
  the same slice; `diff` against the saved original reports "Files are identical" and the final
  `git diff` names no drawer file. The drawer is not edited by this slice.
- **No existing caller changes behaviour.** `onSelect` is optional; when absent React receives
  `onClick={undefined}` / `onKeyDown={undefined}`, so no handler attribute is rendered and the `Link`
  DOM is unchanged. `AssetCard.tsx` and every other consumer of `ProductCard`/`ProductGrid` is
  untouched. The pre-existing "without onSelect, a click still navigates" test proves today's nav.
- **Not a "pre-existing failure" claim anywhere.** No failure is reported as pre-existing.

## (b) Actions

Changed paths (all inside the ceiling; no others):
- `frontend/src/components/catalog/ProductCard.tsx` (G1) — optional `onSelect?: (id) => void`;
  when present the card's click `preventDefault`s and calls `onSelect(item.id)` (Enter/Space on
  keydown likewise); when absent handlers are undefined and `Link` behaviour is unchanged.
- `frontend/src/components/catalog/ProductGrid.tsx` (G1) — optional `onSelect` on `ProductGrid` and
  `TableView`; `openDetail` becomes `onSelect ? onSelect(item.id) : navigate(...)`, so the row click,
  the Enter key, and the `...` button all route through it; the grid passes `onSelect` to each card.
- `frontend/src/routes/CatalogPage.tsx` (G2) — `selectedAssetId` state, `selectedAsset` looked up in
  the already-loaded page, `onSelect={setSelectedAssetId}` on the grid, and
  `<ItemInspectorDrawer asset={selectedAsset} householdId onClose={() => setSelectedAssetId(null)} />`.
  Deep links (`/assets/:id`) untouched.
- `frontend/src/components/catalog/catalog.test.tsx` (G3) — +9 tests: ProductCard onSelect
  (click/Enter/Space no-nav, no-prop nav), ProductGrid onSelect (row click, Enter, `...`, grid
  pass-through), CatalogPage mount open/close + invalidation-on-save (spy on the QueryClient).
- `frontend/src/components/shell/drawer.test.tsx` (G3) — +1 test: save invalidates `["assets"]` +
  `["asset","asset-1"]`.
- `docs/worklogs/SG-050.log`, `SG-050_report.md`, `SG-050_verify.log`.

Temporary mutations (reverted, not in the shipped diff): `ProductCard.tsx` M1, `ItemInspectorDrawer.tsx` M2.
Push: `automation`. No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. External/production effects: none.

Durations (UTC): start 15:25:00 (first read 15:25:45), end ~15:29 → ~212 s of 2100 s overall (10%).
Per leg (actual vs budget): premise+design ~70 s/120 s · pre-change run 3.17 s · implementation ~15 s ·
green suite+lint+build ~20 s/600 s · M1 1.28 s · M2 2.09 s · post-revert suite+lint+build ~9 s/600 s ·
gates+commit/report ~60 s. Early-close 1500 s not approached. Retries: 0. Provider calls: 0.
Test-command count: 6 vitest runs (pre-change, green, M1, M2, post-revert green, plus the same-run
subsets). HIGHEST-IMPACT action: keeping the mount minimal and proving the existing drawer
invalidation rather than duplicating it into `CatalogPage`.

## (c) Verification

Artifacts (rendered DOM / committed outputs, never exits — `PG-EV-02`; raw in `SG-050_verify.log`):
- Pre-change run (base source, new tests present): `8 failed | 32 passed (40)` in 3.17 s — the 8 are
  exactly the new G1/G2 assertions failing because `onSelect`/mount do not exist. LABEL: pre-change
  FAIL, hollow context (feature absent), **not evidence** — the failure-property is the absence of the
  implementation, quoted (`git show HEAD:… | grep onSelect` exit 1 on all three files).
- Green run (post-change, post-revert): `20 files / 117 tests passed` in 3.94 s (was 107; +10).
- `eslint src` exit 0; `tsc` exit 0; `vite build` exit 0 (285.40 kB JS, 1.63 s).
- Mutation run (`PG-EV-01`, discriminating), each wrong value fed singly, each reverted byte-identical:
  M1 navigate-vs-select branch (drop `preventDefault` in ProductCard) → `2 failed | 38 passed` ·
  M2 invalidation key (`["assets"]` → `["assets_mutant"]`) → `2 failed | 38 passed`.
- Properties asserted (`PG-EV-05`), not commands: "click WITH `onSelect` selects the id and does NOT
  navigate"; "click WITHOUT it navigates as today"; "table row + Enter + `...` with `onSelect` select
  without navigating"; "a catalog click opens the drawer for that asset and close clears it"; "a save
  invalidates the `assets` + `asset` query keys".
- `PG-EV-09`: pre-change run, green run, and mutation values are all committed in `SG-050_verify.log`;
  hollowness labelled.
- Gates (`PG-SC-02`/`05`/`10`, `PG-IC-07`, raw §5): changed files exactly the 5 in the ceiling ·
  `backend/` diff empty · `backend/alembic` diff empty (no migration) · `package.json`+lock diff empty
  (no new dependency) · secret scan 0 matches · `git check-ignore` exit 1 on all 5 paths (none ignored)
  · index empty (no ignored file staged) · nothing pushed to `storagegenie-evidence` · no DB / restart /
  network · live spend `$0`.
- **Vacuous-pass statement.** No acceptance criterion is claimed vacuously. The new tests invoke the
  real components and assert on rendered DOM + spy call records; the pre-change run shows them failing
  before the implementation and the mutation run shows them failing when the implementation is wrong.
  The invalidation test asserts on `invalidateQueries` calls with both exact keys, and M2 proves the
  key is load-bearing. No empty-diff or empty-set pass is reported.
- INTENT (behaviour-changing item): code now routes catalog card/row clicks to an inspector drawer
  instead of the detail route when a parent supplies `onSelect`; `CatalogPage` supplies it. Test
  suites exercise both the select branch and the unchanged navigate branch. X (code) and Y (checks)
  and Z (approved packet G1+G2) agree; nothing is bent.
- TWINS: `AssetDetailPage.tsx` remains the deep-link editor and is read-only here; the drawer still
  owns its own PATCH + invalidation. The mount adds a second entry point to the same drawer component,
  not a second editor.

## Receipt (note on the coder-reports notes ref)

Work committed and pushed to `automation`, worktree clean (CO-55). No push to
`storagegenie-evidence`; no `{{RECEIPT_CMD}}` (per this packet's M20-corrected block). The note was
added on WORK_HEAD with the first line carrying both `Dispatch-ID:` and `Report:` (CO-97), the notes
ref pushed explicitly to `origin`, the refspec fetched explicitly (`<ref>:<ref>`, M21 — a bare fetch
never updates a notes ref), and the `git notes --ref=… show <WORK_HEAD>` output is pasted verbatim in
the delivery message (it cannot live inside this file, which is itself part of the commit the note is
attached to). If that `show` output is absent, this step was not executed and should be called out
loudly. Final line: `note=yes`.

## (d) UNCLEAR

- **FIRST READ:** whether G2 wanted `CatalogPage` itself to add invalidation, or whether the drawer's
  existing invalidation (shipped SG-046) already satisfies it. The tree showed the latter; I added no
  duplicate and proved the property from the mount instead.
- **DURING EXECUTION:** whether to render a non-link element when `onSelect` is present (to remove the
  `href` entirely) or to keep the `Link` and intercept the click. Chose interception: it is the
  smallest change, preserves the existing DOM/tests, and satisfies "selects instead of navigating"
  for click + Enter + Space. A future a11y slice may prefer a `role="button"` card.
- **REMAINING:** (1) SG-047 import modal closes the wardrobe track; (2) the drawer's "no live PATCH"
  path is untested against a real backend in this slice (frontend-only ceiling); (3) delete control —
  still no slice assigned (DELETE route exists, no UI ships); (4) `ProductCard`'s intercepted `Link`
  still exposes an `href` for middle-click/open-in-new-tab — intentional for now, unassigned.
