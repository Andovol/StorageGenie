# SG-043 — design-system infra: semantic tokens, theme provider + toggle, product view types

**Dispatch-ID:** SG-043 · **Coder:** opencode · **Effort:** medium (from process args) · **Model:** unknown (CLI default omitted per policy; see ledger) · **Contract:** 0.27.0
**BASE REF:** `origin/automation` — **BASE COMMIT (resolved):** `1bc4551` (start HEAD; worktree clean)
**WORK:** `d456af8` (fail leg) → `e61f93b` (implementation) → `WORK_HEAD` (worklogs+report; resolved hash quoted in the delivery message)
**Spend:** `$0` metered · **Network:** one `npm install lucide-react` only · **DB:** none · **Restart:** none

---

## 1. Starting tree and premise verification (quoted reads)

`git status --short` empty; `git rev-parse HEAD` = `git rev-parse origin/automation` = `1bc4551…fe0`. Clean start, no dirt.

| Packet premise | Verified read | Result |
|---|---|---|
| zero `.css` in `frontend/src` | `glob frontend/src/**/*.css` → `No files found` | CONFIRMED |
| `main.tsx:1-19` no stylesheet, no provider | read: 19 lines, `import App from "./App"` last import, `<QueryClientProvider><BrowserRouter><App/>` | CONFIRMED |
| `index.html:1-12` bare `<head>` | read: 12 lines, `<title>StorageGenie</title>` then `</head>` | CONFIRMED |
| `package.json:12-31` no lucide/tailwind; scripts | `test: vitest run`, `lint: eslint src`, `build: tsc && vite build`; deps only react/query/router | CONFIRMED |
| `api/types.ts:1-197` domain fields | `Asset:29-44` (`display_name`, `asset_type`, `created_at`), `Evidence:3-10` (`id`, `sha256`, `storage_key`, …), `Job:61-71` (`id`, `state`, …), `AiSettings:115-123` (`consent` + provider/model ids) | CONFIRMED |
| `EvidenceGallery.tsx` is the URL authority | line 11: ``href={`${base}/v1/evidence/${e.id}/file?household_id=${householdId}`}`` with `base = import.meta.env.VITE_API_BASE || "http://localhost:8000"` (line 4) | CONFIRMED |

**Premise difference (finding F-1):** the packet asserts *"Prompts 1–4 + DQ1–DQ10 answers are the spec"*. That text is **not present in this tree or in any reachable artifact**. I searched: tracked files (`git grep` across all commits), every git blob (`git cat-file --batch-all-objects`), `docs/`, `docs/launcher-relay/`, `docs/superpowers/`, `.scratch/`, local opencode session storage, and the host filesystem. Only the packet and `STATE.md` summarise DQ1–DQ10; neither enumerates the DQ1 six names nor the DQ3 badge hex pairs. This is a premise difference, not an obstacle — see §6.

## 2. G1 — semantic tokens (`frontend/src/theme/tokens.css`, new)

- `:root` (light) and `.dark` (class on `<html>`) each carry all ten tokens as HSL channel triplets used via `hsl(var(--x))` (DQ2's tokens-over-Tailwind). Light canvas = Stone-50 `#FAFAF9`.
- Dark layers implemented **EXACTLY** as the packet's DQ3 text: `--background #0F0E0D`, `--card #1C1A18`, `--card-muted #262320`, `--border #2C2926` (stored as `30 7.1% 5.5%` / `30 7.7% 10.2%` / `30 8.6% 13.7%` / `30 7.3% 16.1%`; a test converts each back to hex — see G4).
- Status badge palettes for both themes: stone (raw), sky (processed), emerald (rendered), rose (failed), as bg/fg token pairs. **Their exact hexes were not available in-slice (F-1)**; chosen from the Tailwind emerald/sky/stone/rose scales, light `-100`/`-800` and dark `-950`/`-300`, for AA contrast. Marked in §6.
- Utility classes for every token: `.bg-*`, `.text-*`, `.border-*`, `.badge-*`, `.font-sans`, `.font-mono`, `.focus-ring`.
- Fonts per DQ8: `--font-sans` system stack, `--font-mono` `ui-monospace…`; no webfont, no `@import`.
- **Zero arbitrary colors:** every color rule is `hsl(var(--token))`; a test asserts the file contains no `#rrggbb`. (The DQ3 hexes live only in the test as expected conversions.)

## 3. G2 — provider, toggle, wiring

- `ThemeProvider.tsx`: `system|light|dark`; toggles `.dark`/`.light` on `<html>`; `localStorage` key `sg-theme`; OS-preference default + live `matchMedia` change listener; `useTheme()` hook.
- `ThemeToggle.tsx`: `Sun`/`Moon` from `lucide-react`, dynamic `aria-label` ("Switch to dark/light theme"), native `<button>` (keyboard-focusable) with `focus-ring` class whose outline uses `hsl(var(--primary))` — visible in both themes.
- `index.html`: **ONE hunk**, the FOUC guard inline in `<head>` (byte-diff in §5).
- `main.tsx`: **TWO hunks only** — `import "./theme/tokens.css";` + `import { ThemeProvider }` (one hunk) and wrapping the tree in `<ThemeProvider>` (second hunk). No other behaviour change.

**Unmounted-toggle decision (reported, not hidden):** the toggle is delivered and tested but **NOT mounted in `App`**. No screen reads tokens yet, so a mounted toggle would flip nothing; mounting arrives with the SG-044 shell. `App.tsx` is untouched by rule.

## 4. G3 — product view types + mappers (`frontend/src/types/product.ts`, new)

- Types: `ProductItem`, `AssetMedia`, `RenderJob` (+ `BoundingBox`, `RenderModelInfo`, `ProductStatus`, `RenderJobStatus`). **No `rawResponse` field exists anywhere** (DQ4 retention); a recursive-key test asserts mapper output never carries one.
- `CANONICAL_CATEGORIES` exported; `toProductCategory` normalises canonical casing and **passes custom strings through** (user-extensible per DQ1); `""`/`"unknown"` → `Uncategorized`.
- Mappers read only `api/types.ts`: `assetToProductItem` (name←`display_name`, dateAdded←`created_at`, status defaults `raw` per DQ10, `tags: []` and `metadata: {}` with comments naming the filling slice); `evidenceToAssetMedia` (originalUrl built on the `EvidenceGallery.tsx:11` route; cutout/scene/bbox absent until the S3 era, with comments); `jobToRenderJob` (explicit state map + `idle` default, `modelInfo` reserved for SG-046+). No user-facing text asserts derivation that does not happen.

## 5. Gated hunks, byte-quoted

`frontend/index.html` — ONE hunk (`git diff 1bc4551..e61f93b`):

```
@@ -4,6 +4,21 @@
     <title>StorageGenie</title>
+    <script>
+      (function () {
+        try {
+          var stored = localStorage.getItem("sg-theme");
+          var dark =
+            stored === "dark" ||
+            ((stored === null || stored === "system") &&
+              window.matchMedia("(prefers-color-scheme: dark)").matches);
+          document.documentElement.classList.toggle("dark", dark);
+          document.documentElement.classList.toggle("light", !dark);
+        } catch (error) {
+          document.documentElement.classList.add("light");
+        }
+      })();
+    </script>
   </head>
```

`frontend/src/main.tsx` — TWO hunks:

```
@@ -3,6 +3,8 @@ import ReactDOM from "react-dom/client";
+import "./theme/tokens.css";
+import { ThemeProvider } from "./theme/ThemeProvider";

@@ -11,9 +13,11 @@ const qc = new QueryClient({
-      <BrowserRouter>
-        <App />
-      </BrowserRouter>
+      <ThemeProvider>
+        <BrowserRouter>
+          <App />
+        </BrowserRouter>
+      </ThemeProvider>
```

## 6. Findings (reported loudly)

- **F-1 — the DQ spec text is not in the tree.** The packet's premise that prompts 1–4 + DQ1–DQ10 answers are the spec is unbacked (search method in §1). Consequence: `CANONICAL_CATEGORIES` names and the badge palette hexes are **inferences**, not quotes. The six I shipped are `Tops, Bottoms, Dresses, Outerwear, Footwear, Accessories` — the wardrobe-domain reading of DQ1 ("canonical 6-category taxonomy", top-5 + All + Uncategorized + overflow). If the DQ1 answer names differ, it is a one-line change to `CANONICAL_CATEGORIES` (tests are parameterised over the list). **Destination:** Architect confirmation against the DQ1 text; fold into SG-044 if it differs. The DQ3 dark-elevation hexes that *were* given verbatim are exact and tested.
- **F-2 — `~/.npm` is read-only on this VPS.** The first `npm install lucide-react` failed with `EROFS … /home/andrei/.npm/_cacache/tmp/…`. Re-ran the same install with `--cache /tmp/opencode/npm-cache`; added exactly one package (`lucide-react ^1.46.0`), no vendoring, no substitution. One registry call either way. **Destination:** environment note; no project change.
- **F-3 — Vitest `css:false` makes `tokens.css?raw` empty.** The CSS-value assertions therefore read the file with `node:fs` under a documented `@ts-expect-error` (no `@types/node` dep added, no `vite.config.ts` change — both outside the scope ceiling). The token-mutation run proves the assertion is live, not vacuous.
- **F-4 — `lucide-react` resolved to `^1.46.0`.** Installed exactly one registry package per the single-network exception, `^` range preserved as required.

No stop-gate conditions fired: no `backend/` change, no migration, no frozen-prompt change, no needed-but-out-of-ceiling file, `App.tsx` untouched.

## 7. G4 — FAIL-then-PASS honestly

- **Pre-change (LABELED HOLLOW, class 8, not evidence).** On BASE the two test modules' imports do not resolve:
  ```
  FAIL  src/theme/theme.test.tsx  Error: Failed to resolve import "./ThemeProvider" from "src/theme/theme.test.tsx". Does the file exist?
  FAIL  src/types/product.test.ts Error: Failed to resolve import "./product" from "src/types/product.test.ts". Does the file exist?
  Test Files  2 failed (2)   Tests  no tests
  ```
  It is hollow (import failure, not an assertion failure) and is quoted only as context. Raw in `SG-043_verify.log` §1.
- **Post-change green.** `npm test` → **17 files / 65 tests passed** (elapsed 3 s); `npm run lint` → exit 0 (1 s); `npm run build` → `tsc && vite build` exit 0, CSS `2.65 kB` emitted (3 s). Raw in `SG-043_verify.log` §3.
- **Mutation run (PG-EV-01, discriminating).** Three deliberately wrong values, each caught then reverted clean:
  1. `tokens.css .dark --card 30 7.7% 10.2% → 30 7.7% 12%` → `expected '#211F1C' to be '#1C1A18'` (FAIL, 1 failed / 9 passed).
  2. `product.ts` job default `idle → failed` → `expected 'failed' to be 'idle'` (FAIL, 1 / 11).
  3. `CANONICAL_CATEGORIES` drop `Accessories` → `length 6 but got 5` (FAIL, 1 / 11).
  Raw in `SG-043_verify.log` §2; `git status` clean after reverts.
- Both runs committed (`d456af8` fail leg, `e61f93b` implementation), verify log committed with them.

## 8. Acceptance / ledger

| Check | Result |
|---|---|
| suite + lint + build | green (65 tests) |
| secret scan | 0 real secret shapes (only `tokenizer`/`token` substrings + npm integrity hashes) |
| `backend/` diff | empty (`git diff --name-only 1bc4551..HEAD -- backend/` → empty) |
| migration (`alembic`/`versions`) diff | empty |
| frozen-prompt diff | empty |
| deps added | `lucide-react` only (package.json +1 line, lock +10) |
| ignored file staged | none (status clean; `.env` stays ignored) |
| pushed to `storagegenie-evidence` | no |
| vacuous pass | none claimed; hollow leg explicitly labelled |
| DB writes / live spend | none / `$0` |
| `originalUrl` source | `EvidenceGallery.tsx:11` (quoted §1) |

`git diff --stat 1bc4551..e61f93b` = 10 files, +772/−3, all inside the scope ceiling. Nothing outside the ceiling was modified.

## 9. Receipt (note on the coder-reports notes ref)

Push the work to `automation`, worktree clean (`CO-55`); no `storagegenie-evidence` push, no `{{RECEIPT_CMD}}`. Then, last, with a 120 s bound:

```
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-043 | Report: docs/worklogs/SG-043_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`). The executed `show` output is pasted **in the delivery message** (the standing receipt-paste gate from SG-042); result `note=yes`. If `show` had no output, this subsection would say so loudly — it is not being written as done ahead of execution.

## 10. UNCLEAR

- **FIRST READ:** whether the packet intended me to receive the DQ1–DQ10 answer text out-of-band; it is not in the repo, so I inferred the two unspecified values (F-1) while implementing the verbatim DQ3 hexes exactly.
- **DURING EXECUTION:** whether the canonical six are wardrobe categories or StorageGenie asset categories — the packet's "view-map from our `asset_type` enum" phrase pulls one way, the wardrobe track and clothing-ProductCard mocks pull the other; I chose wardrobe names and made them a one-line change.
- **REMAINING:** confirming the six names + badge hexes against the DQ1/DQ3 text, and mounting `ThemeToggle` in the SG-044 shell (the deliberate non-mount is decision, reported).

END: note=yes (executed `show` output pasted in the delivery message).
