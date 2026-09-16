# SG-044 — catalog shell: header, toolbar, DQ1 taxonomy correction, note recovery

**Dispatch-ID:** SG-044 · **Coder:** opencode · **Effort:** medium (`--variant medium`, from process args) · **Model:** `unknown` (no `--model` on argv; provider metadata banner in `output/dispatch/SG-044.log` prints `deepseek-v4.1-flash` — recorded as metadata, not an argv fact) · **Contract:** 0.27.0
**BASE REF:** `origin/automation` — **BASE COMMIT (resolved):** `ecbad87a0f024804c59ec64ce618304eb693d0a9` (start HEAD; worktree clean)
**WORK:** `de61973` (fail leg) → `0ecb035` (implementation) → `WORK_HEAD` (this worklog/report/verify log commit; resolved hash published in the receipt note and the delivery message)
**Spend:** `$0` metered · **Network:** none (AI OFF, no npm, no fetch beyond the required G0/receipt git refspecs) · **DB:** none · **Restart:** none

---

## 1. Starting tree and premise verification (quoted reads)

`git status --porcelain` empty; `git rev-parse HEAD` = `git rev-parse origin/automation` = `ecbad87…`. Clean start, no dirt.

| Packet premise | Verified read | Result |
|---|---|---|
| `App.tsx:11-47` gray `Nav`, `:49-65` App | read 65 lines; `Nav` = six `NavLink`s + `Phase 0 · local-first`, inline `#f9fafb`/`#111827`; root div `background: "white"` | CONFIRMED (untouched by rule) |
| `CatalogPage.tsx:15-58` state | read: `householdId`, `qRaw`+debounced `q`, `assetType`, `status`, `cursor`, `allItems`; reset effect on `[effectiveHousehold, q, assetType, status]` | CONFIRMED |
| `CatalogPage.tsx:62-102` filter row / `:108-127` grid | read: household select, search input, asset-type select, status select; grid of `AssetCard`; Load-more with inline `#d1d5db`/`white` | CONFIRMED |
| `useAssets.ts:5-25` plumbing | read: `useAssets(householdId, q, cursor?, assetType?, status?)` → `apiGet("/v1/assets", …)` via react-query | CONFIRMED |
| DQ1 six embedded | `docs/design/DQ-answers.md:11-16`: `Hardware & Tools`, `Electronics & Gadgets`, `Apparel & Textiles`, `Home & Decor`, `Packaging & Materials`, `Uncategorized` | CONFIRMED (committed, citable) |
| Old fashion six in `product.ts` | `product.ts:7-14`: `Tops, Bottoms, Dresses, Outerwear, Footwear, Accessories` | CONFIRMED (the M19 fallout) |
| SG-042 note HEAD / SG-043 note HEAD | `git cat-file -e` both `RESOLVES` (G0) | CONFIRMED (see F-1) |

No premise produced a STOP. Premise differences are findings (§7).

## 2. G0 — note recovery (`notes-recovered`) — elapsed **8 s** vs 120 s ordinary

Read the runner's own classifier (`/usr/local/bin/dispatch:219-299`, `classify_receipt`): it greps the `$NOTES_FULL` tree for `Dispatch-ID: <ID>`, prefers a note object that is an ancestor of HEAD, then tests `git cat-file -e "$obj:$path"` and prints `report_missing` only when that fails.

In-slice result (raw: `SG-044_verify.log` §1):

- SG-042 note present on `0c3b5702…`; `git cat-file -e 0c3b5702…:docs/worklogs/SG-042_report.md` → **RESOLVES (exit 0)**.
- SG-043 note present on `307ae8c8…`; `git cat-file -e 307ae8c8…:docs/worklogs/SG-043_report.md` → **RESOLVES (exit 0)**.

By the runner's own code both classify as `done`, **not `report_missing`**. The `notes-recovered` branch was executed anyway, idempotently: `git push origin refs/notes/storagegenie-coder-reports` → `Everything up-to-date` (remote already `a849a47`); explicit refspec fetch `refs/notes/…:refs/notes/…-remote` advanced the stale verify ref `e8adff2 → a849a47`; `git notes --ref=refs/notes/…-remote show <obj>` printed both note lines verbatim for both work HEADs. Outcome: **`notes-recovered`** (nothing needed re-pointing). See F-1.

## 3. G1 — taxonomy correction (`frontend/src/types/product.ts` + test)

- `CANONICAL_CATEGORIES` replaced with the DQ1 six EXACTLY: `Hardware & Tools`, `Electronics & Gadgets`, `Apparel & Textiles`, `Home & Decor`, `Packaging & Materials`, `Uncategorized`.
- `toProductCategory` unchanged in behaviour: custom strings pass through; `""`/`"unknown"` → `Uncategorized`; canonical casing normalised (`hardware & tools` → `Hardware & Tools`).
- SG-043's fashion-six lock in `product.test.ts:50-58` was **updated in this slice, not left red** (`PG-SC-11`): it now asserts the six by `toEqual`, and the fixture `asset_type` moved from `Tops` to `Apparel & Textiles`.
- Badge hexes in `tokens.css` **untouched** (SG-045 owns them).

## 4. G2 — shell (`frontend/src/components/shell/`, 4 files new)

- `AppHeader.tsx`: left wordmark `StorageGenie` + count pill `Total: N items` (N = `loadedCount` prop; `aria-label="Total loaded items: N"` + `title` saying it is the loaded page count, never a household total); centre reserved (empty flex spacer); right search input wired to `qRaw` (`aria-label="Search catalog"`), `document` keydown `⌘K`/`Ctrl+K` → `focus()` + `select()` (DQ6 MVP fallback; no palette promised); `ThemeToggle` mounted (SG-043's deferred mount lands); `Import Asset` primary `Link` to `/capture`.
- `CatalogToolbar.tsx`: `All` + the six = 7 pills (see F-3), active pill `bg-primary text-primary-foreground`, inactive `bg-card-muted`; sort `<select>` = `Recently Added` (`created_at` desc), `Name (A-Z)`, `Processing Status` (`ProductItem.status`) applied CLIENT-SIDE; density group `Standard Grid` (active) / `Compact Table` present but keeps the grid with the honest note "Table view arrives with the new cards (SG-045) — showing the grid for now."; active-filter tags (`Search: q`, category, sort label) + `Clear all` resetting all three. Household select preserved here (F-5).
- `AppShell.tsx`: sticky header+toolbar block + `<main>` children.
- `CatalogPage.tsx`: the old filter row (`:62-102`) is replaced by `AppShell`; the `AssetCard` grid and Load-more remain, fed by `filterAndSortCatalog` over the loaded page. `assetType`/`status` server filters removed with the old row; `useAssets` called as `(effectiveHousehold, q, cursor)`. Empty-filtered message added.
- Styling: SG-043 token utility classes only; `grep '#[0-9a-fA-F]{3,8}'` over the changed frontend source → **none** (the pre-existing Load-more inline `#d1d5db`/`white` were token-ised, F-7).
- **Server-side category aggregation does not exist** (no endpoint returns per-category counts). Pills filter the loaded page via `toProductCategory`; the queued backend destination is a per-category counts endpoint slice (F-6).
- `App.tsx` and `AssetCard.tsx` untouched; global `Nav` stays for other routes.

## 5. G3 — tests, FAIL-then-PASS, mutations

- `frontend/src/components/shell/shell.test.tsx` (new): mocks the api client (F-2 path), renders `CatalogPage` in QueryClient + ThemeProvider + MemoryRouter; mock assets are mapped through the real `assetToProductItem`. Integration tests cover loaded-count labelling, the seven pills, pill filtering + active primary style, query narrowing, client-side sort ordering, `Clear all` resetting all three, `⌘K`/`Ctrl+K` focus, theme-class flip, `Import Asset` → `/capture`, and Compact-Table-keeps-grid. A `filterAndSortCatalog` unit block proves category/query filtering and recent/name/status ordering.
- **Pre-change (class 8, LABELED HOLLOW, not evidence):** `npm test` on the base tree → `shell.test.tsx` fails to resolve `./CatalogToolbar` (hollow), and `product.test.ts` shows **2 real** taxonomy assertion failures. 2 failed files / 63 passed. Raw in `SG-044_verify.log` §2.
- **Post-change GREEN:** 18 files / **77 tests passed** (2.99 s); lint exit 0 (1.37 s); build `tsc && vite build` exit 0, CSS 2.65 kB (3.56 s). Raw in `SG-044_verify.log` §3.
- **Mutation run (`PG-EV-01`, discriminating):** 3 wrong values fed, each caught singly, each reverted clean (`git status` empty after each):
  1. pill label `All` → `Everything` → FAIL (2 failed / 10 passed);
  2. sort comparator name `a→b` → `b→a` → FAIL (2 / 12);
  3. taxonomy list drop `Uncategorized` → FAIL (1 / 11).
  Raw in `SG-044_verify.log` §4.
- Both runs committed: fail leg `de61973`, implementation `0ecb035` (`PG-EV-09`).

## 6. Gates / ledger

| Check | Result |
|---|---|
| suite + lint + build | green (18 files / 77 tests) |
| secret scan on diff | 0 real secret shapes |
| `backend/` diff | empty (`git diff --name-only ecbad87..HEAD -- backend/` → empty) |
| migration (`alembic`/`versions`) diff | empty |
| dependency diff (`package.json` + lock) | empty — lucide-react already present |
| arbitrary hex in changed sources | none |
| ignored file staged | none (status clean) |
| pushed to `storagegenie-evidence` | no |
| DB writes / restart / live spend | none / none / `$0` |
| vacuous pass | none claimed; hollow leg explicitly labelled |

`git diff --stat ecbad87..HEAD` = 7 files, +706/−70, all inside the scope ceiling (shell/ 4 files, CatalogPage, product.ts, product.test.ts). No file under `backend/`, `App.tsx`, or `AssetCard.tsx` touched.

## 7. Findings (reported loudly)

- **F-1 — G0 premise did not reproduce.** `report_missing` did not occur in-slice: both notes are in the lane-local ref and `obj:path` resolves, so the runner's `classify_receipt` returns `done`. What *was* stale is `refs/notes/storagegenie-coder-reports-remote` (Sep-8 `e8adff2`); the explicit refspec fetch repaired it. No re-pointing was needed. Destination: none (informational; the packet's premise was stale).
- **F-2 — mock path.** `vi.mock("../api/client")` cannot resolve from `frontend/src/components/shell/`; the correct specifier there is `../../api/client`. Used the correct path.
- **F-3 — pill count wording.** "`All` + the DQ1 six + `Uncategorized`" would render `Uncategorized` twice, since the DQ1 six already includes it. Shipped `All` + the six = **7 pills**, matching DQ1's "top 5 + `All` + `Uncategorized`".
- **F-4 — Processing Status sort is stable today.** `assetToProductItem` hardcodes `status: "raw"` (DQ10), so the `Processing Status` comparator orders equal keys until processing-status derivation lands. The comparator is proven with mapper-derived items whose `status` is overridden in the unit test; the production no-op is deliberate and reported.
- **F-5 — household selector.** It was part of the replaced filter row but is not named in the header/toolbar spec; dropping it would remove household switching, so it is kept in the toolbar as a design call.
- **F-6 — missing backend aggregation.** No per-category counts endpoint; pills filter the loaded page. **Destination:** a backend aggregation slice (e.g. `SG-048 — GET /v1/assets/category-counts`), not this slice (backend excluded by rule `PG-SC-05`).
- **F-7 — Load-more de-hexed.** The pre-existing Load-more button carried arbitrary `#d1d5db`/`white`; token-ised to satisfy "zero arbitrary colors" (small within-file change beyond the filter row, reported).
- **F-8 — `App.tsx` inline white/#111827 untouched.** Out of the ceiling by rule; the shell's `bg-background` covers the catalog route, but other routes still inherit the old inline palette. Destination: the later shell/global restyle.

## 8. Receipt (note on the coder-reports notes ref)

Work pushed to `automation`, worktree clean (`CO-55`); no `storagegenie-evidence` push, no `{{RECEIPT_CMD}}`. Steps executed after this report's commit (raw `show` output pasted **in the delivery message**, per the SG-042/SG-043 standing gate — it cannot be pasted inside this file because the note is attached to this file's commit):

```
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-044 | Report: docs/worklogs/SG-044_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
git push origin refs/notes/storagegenie-coder-reports
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-remote
git notes --ref=refs/notes/storagegenie-coder-reports-remote show <WORK_HEAD>
```

If that `show` produced no output, this subsection would say so loudly; it is not being written as done ahead of execution. Final line: `note=yes`.

## 9. UNCLEAR

- **FIRST READ:** whether G0 wanted me to treat the already-resolving notes as `notes-recovered` (I did, idempotently) or to prefer a re-point; F-1 records that `report_missing` never reproduced.
- **DURING EXECUTION:** whether the `Processing Status` sort should order by `ProductItem.status` (all `raw` today) or by the underlying `Asset.status` (ACTIVE/DRAFT/…); I followed the product model (status field) and reported the no-op (F-4).
- **REMAINING:** the backend per-category counts endpoint (F-6), the SG-045 cards/density views, and the SG-047 import modal.
