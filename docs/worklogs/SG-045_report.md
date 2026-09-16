# SG-045 — catalog grid: product cards, both density views, skeletons, empty state, honest mocks

**Dispatch-ID:** SG-045 · **Coder:** opencode · **Effort:** medium (`--variant medium`, from process args) · **Model:** `unknown` (no `--model` on argv; per policy the CLI default is the model and is omitted — provider metadata banner in `output/dispatch/SG-045.log` prints `deepseek-v4.1-flash`, recorded as provider metadata, not an argv fact) · **Contract:** 0.27.0
**BASE REF:** `origin/automation` — **BASE COMMIT (resolved):** `9a84bbdf79fbe15b6d1a3f8a9adab975cbcf6bc5` (start HEAD; worktree clean)
**WORK:** `2d5bed3` (fail leg) → `d08de8c` (implementation) → `WORK_HEAD` (this worklog/report/verify log commit; resolved hash published in the receipt note and the delivery message)
**Spend:** `$0` metered · **Network:** none (AI OFF, no npm, no fetch beyond the receipt git refspecs) · **DB:** none · **Restart:** none

---

## 1. Starting tree and premise verification (quoted reads)

`git status --porcelain` empty; `git rev-parse HEAD` = `git rev-parse origin/automation` = `9a84bbd…`. Clean start, no dirt.

| Packet premise | Verified read | Result |
|---|---|---|
| `AssetCard.tsx:1-71` old gray card | read all 71 lines: inline `#e5e7eb` border, `Cover thumb or "no image"`, `name / asset_type · status / counts` | CONFIRMED |
| `AssetCard.tsx:9` thumb route | `${base}/v1/evidence/${thumbEvidence.id}/thumb/256?household_id=${householdId}` | CONFIRMED |
| `AssetCard.tsx:18` click destination | `to={`/assets/${asset.id}?household_id=${householdId}`}` | CONFIRMED |
| `EvidenceGallery.tsx:17` thumb route | `${base}/v1/evidence/${e.id}/thumb/256?household_id=${householdId}` | CONFIRMED |
| density state both options render grid | `CatalogToolbar.tsx:6` `export type Density = "grid" | "table"`; `:14` `DENSITY_LABELS`; `CatalogPage.tsx:123-127` single `AssetCard` grid map | CONFIRMED |
| DQ3 badge pairs embedded | `docs/design/DQ-answers.md:41-50` four pairs (gray/blue/green/rose) | CONFIRMED (committed, citable) |
| DQ5 columns embedded | `docs/design/DQ-answers.md:66-73` seven columns with px widths | CONFIRMED |
| `ProductStatus` gains `failed` | `product.ts:18` was `"raw" | "processed" | "rendered"`; mapper `:86` defaults `"raw"` | CONFIRMED |
| SG-045 grid mocks are a named future input | `product.ts:82` "tags: populated by the SG-045 grid mocks / SG-047 import modal." | CONFIRMED |

No premise produced a STOP. Premise differences are findings (§7).

One extra check not in the packet: Tailwind is **not installed** (no `tailwindcss` in `frontend/node_modules`, no Tailwind config, no `tailwind` in `package.json`). This matters for the DQ3/DQ2 tension (F-1, F-2).

## 2. G1 — `frontend/src/components/catalog/ProductCard.tsx` + `ProductCardSkeleton.tsx`

- 3:4 card (`aspectRatio: "3 / 4"`), `bg-card border-border focus-ring` token classes; whole card is a `Link` to `/assets/:id?household_id=` (same destination as today's `AssetCard.tsx:18`).
- Cutout well `aspect-square bg-card-muted` with `object-contain` media; `onError` flips a `broken` flag and the well renders empty — a broken image never renders a broken icon (same honesty as today's `AssetCard`/`EvidenceGallery` `onError` hide). `cardMedia` prefers `cutoutUrl → sceneUrl → thumbUrl(evidenceId)`; `thumbUrl` mirrors the live thumb route.
- Status badge top-right: the exact DQ3 pairs are embedded verbatim in `BADGE_CLASS`; the element also carries the matching SG-043 token class (`badge-raw|processed|rendered|failed`). `ProductStatus` gained `'failed'` (type-only; mapper default stays `'raw'`).
- Failed adds the hairline rose well border (`border-rose-500/30` string + inline `hsl(var(--badge-failed-fg) / 0.3)`), a centered `AlertTriangle`, and a title `AlertTriangle` (DQ10).
- Footer: truncated name, mono category micro-pill, 8px primary-color dots rendered only when `metadata.primaryColors` is non-empty (never placeholder dots).
- Skeleton: same 3:4 shape, `bg-muted` + the exact `bg-muted/50 animate-pulse` string, `aria-hidden="true"`.

## 3. G2 — `ProductGrid.tsx` (grid, compact table, empty, loading)

- Grid: a component-scoped `<style>` defines `.catalog-grid` with 2 cols mobile → 3 (`min-width:768px`) → 4 (`1024px`) → 5 (`1536px`), `gap: 16px` / `20px` (the `gap-4 md:gap-5` equivalents). Tailwind is absent, so plain CSS classes are the DQ2-compliant implementation.
- Compact table: 7 columns in exact DQ5 order — Asset 56px (40px `bg-card-muted` thumb, `cardMedia` + `onError` fallback) · Name min-200 trunc · Category 140px mono micro-badge · Status 130px badge + dot · Dimensions/Specs 120px (`dimensions ?? material ?? "—"`) · Added 110px right mono relative date · Actions 48px ghost `...`. Row click and the `...` button navigate to `/assets/:id?household_id=` (Enter key also works). **No delete control ships** (`PG-SC-02`) — the inventory has no delete behaviour to assert.
- Empty state (zero items): dashed-border canvas + `Import New Item` `Link` to `/capture`, labelled truthfully ("the DQ9 import modal arrives with SG-047").
- Loading: `limit` skeletons (20 in `CatalogPage`, the `useAssets` page-limit shape), region has `aria-busy="true"` and `aria-label="Product results"`.
- `formatRelativeDate(iso, nowMs = Date.now())` reads the live clock in production; tests inject `nowMs` so no fixed calendar date is asserted (`PG-IC-07`).

## 4. G3 — `mockProducts.ts` + `CatalogPage` swap hunk

- 8 products spanning all six DQ1 categories (six distinct), statuses raw×3 / processed×2 / rendered×2 / failed×1. Each is built through the **real** `assetToProductItem`, then augmented with mock-only media/metadata. `MOCK_PRODUCTS` is consumed by `catalog.test.tsx`.
- Cutout/scene media are deterministic inline `data:image/svg+xml,` URIs (no network, no binaries). `created_at` is generated from the live clock at module load (`daysAgo(n)`), not a fixed date.
- `CatalogPage` grid-swap hunk: the `AssetCard` map and the two old empty-message blocks are replaced by one density-aware `<ProductGrid>`; loading renders the skeleton grid. `visibleItems` is built through `assetToProductItem` and carries `evidenceId` from `asset.evidence[0]` so live thumbnails still resolve. `AssetCard.tsx` stays on disk untouched (dead-file removal is a later cleanup).

## 5. G4 — tests, FAIL-then-PASS, mutations

- `frontend/src/components/catalog/catalog.test.tsx` (new, 19 tests): mapper-driven card name/category/dots, dots-absent when no colors, exact DQ3 pair per status (and `BADGE_CLASS[status]` equality), failed visuals (rose badge + well border + both warning icons), card href, broken-image fallback, skeleton aria/shape/pulse, grid card count, responsive breakpoint strings, table 7 columns + order, `—` for absent specs, row-click route, actions-button route + no-delete, empty-state CTA route, loading skeleton count + `aria-busy`, `formatRelativeDate` with injected now, mocks span categories/statuses, inline-SVG media, no-`rawResponse`.
- **Pre-change (class 8, LABELED HOLLOW, not evidence):** `npm test` on the fail leg `2d5bed3` → `catalog.test.tsx` fails to resolve `./ProductCard` (hollow); 18 files / 77 existing tests pass. Raw in `SG-045_verify.log` §2.
- **Post-change GREEN:** 19 files / **96 tests passed** (3.65 s); lint exit 0; build `tsc && vite build` exit 0 (CSS 2.65 kB, JS 272.41 kB, 1.68 s). Raw in `SG-045_verify.log` §3.
- **Mutation run (`PG-EV-01`, discriminating):** 3 wrong values fed, each caught singly, each reverted clean (`git status` empty after each):
  1. raw badge class `bg-stone-100` → `bg-stone-200` → FAIL (1 failed / 18 passed);
  2. table column order swap `Status`/`Dimensions/Specs` → FAIL (1 / 18);
  3. mock `failed` status → `raw` → FAIL (1 / 18).
  Raw in `SG-045_verify.log` §4.
- Both runs committed: fail leg `2d5bed3`, implementation `d08de8c` (`PG-EV-09`).

## 6. Gates / ledger

| Check | Result |
|---|---|
| suite + lint + build | green (19 files / 96 tests) |
| secret scan on added lines | 0 matches |
| `backend/` diff | empty (`git diff --name-only 9a84bbd..HEAD -- backend/` → empty) |
| migration (`alembic`/`versions`) diff | empty |
| dependency diff (`package.json` + lock) | 0 lines |
| DQ3 badge pairs greppable | each of the four exact strings occurs once in `ProductCard.tsx` |
| arbitrary hex in changed card/grid/route/types | none (mock data colors are in `mockProducts.ts` only — F-4) |
| ignored file staged | none (`git check-ignore` exit 1 on all new files; `git ls-files -ci` empty) |
| pushed to `storagegenie-evidence` | no |
| DB writes / restart / live spend | none / none / `$0` |
| vacuous pass | none claimed; hollow leg explicitly labelled |

`git diff --stat 9a84bbd..HEAD` = 7 files, +939/−30, all inside the scope ceiling (`catalog/` 5 files, `CatalogPage.tsx`, `product.ts`). No file under `backend/`, `AssetCard.tsx`, `tokens.css`, or `product.test.ts` touched.

## 7. Findings (reported loudly)

- **F-1 — DQ3 Tailwind pairs vs DQ2 "no Tailwind".** The packet's badge pairs are Tailwind utility strings, but Tailwind is not installed (no dep, no config, no CSS). Shipping only those utilities would be a vacuous (unstyled) badge. I embedded the exact DQ3 strings **and** paired each with the SG-043 semantic token class (`badge-raw`/`badge-processed`/`badge-rendered`/`badge-failed`), whose light/dark swatches are the same palette. **Destination:** if the Architect intended the DQ3 utilities to be the sole source, a global utility-mapping/Tailwind decision is required (`tokens.css`/build, outside this ceiling).
- **F-2 — Other inert utilities.** `bg-muted/50 animate-pulse` (skeleton) and `border-rose-500/30` (failed well) are Tailwind utilities and therefore inert; the skeleton keeps `bg-muted` and the failed well gets the inline token hairline, but **no pulse keyframe animation ships**. Same destination as F-1.
- **F-3 — stale toolbar note.** `CatalogToolbar.tsx:156-160` still renders "Table view arrives with the new cards (SG-045) — showing the grid for now." The table now ships, so the note is false whenever density is `table`. `CatalogToolbar.tsx` is outside the ceiling (SG-044 owns it) and `shell.test.tsx:251-259` asserts the note, so I did **not** edit either. **Destination:** SG-046 / a shell cleanup slice removes the note and updates that test.
- **F-4 — mock data colors are data, not design tokens.** `mockProducts.ts` holds hex strings for inline SVG fills and `metadata.primaryColors`; the card/grid chrome is token-class only. Reported so the "no arbitrary hex in changed design sources" convention is not asserted falsely.
- **F-5 — one empty state for two causes.** `CatalogPage` previously distinguished "no assets yet" from "no matches"; the grid now shows one dashed empty state with the CTA for both. **Destination:** a richer empty copy if the owner wants the distinction back.
- **F-6 — `AssetCard.tsx` left on disk** (dead file) per the packet; **destination:** later cleanup slice.
- **F-7 — pre-existing `ProvenanceBadge` classes.** `badge-green|amber|grey` are referenced but undefined in `tokens.css` (pre-existing, out of scope, untouched). Noted for the token-completeness slice.

## 8. Receipt (note on the coder-reports notes ref)

Work pushed to `automation`, worktree clean (`CO-55`); no `storagegenie-evidence` push, no `{{RECEIPT_CMD}}`. Steps executed after this report's commit (raw `show` output pasted **in the delivery message**, per the SG-042/SG-043/SG-044 standing gate — it cannot be pasted inside this file because the note is attached to this file's commit):

```
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-045 | Report: docs/worklogs/SG-045_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
git push origin refs/notes/storagegenie-coder-reports
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-remote
git notes --ref=refs/notes/storagegenie-coder-reports-remote show <WORK_HEAD>
```

If that `show` produced no output, this subsection would say so loudly; it is not being written as done ahead of execution. Final line: `note=yes`.

## 9. UNCLEAR

- **FIRST READ:** whether `CatalogPage` should render the committed mocks or live assets. Chose live assets (every click lands on a real `/assets/:id` route); mocks are the deterministic test fixture the backend cannot yet supply (F-4).
- **DURING EXECUTION:** how to reconcile DQ3's Tailwind strings with DQ2's "no Tailwind". Shipped both — exact DQ3 strings for greppability plus the SG-043 token class for real styling — and reported the inert-utility tension (F-1, F-2).
- **REMAINING:** SG-046 inspector drawer (card/row click target), SG-047 import modal, delete (does not exist; no control ships), server-side category aggregation (backend slice, excluded by rule `PG-SC-05`), and the stale `CatalogToolbar` table note (F-3).
