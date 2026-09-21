# SG-075 — site-wide Stone theme migration: every screen onto the token system

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE (packet ref `origin/automation`):** `798fcb0a8a5724297580388fbc769b4ecee1a7fb` (`D96: SG-075 Stone theme migration packet (site-wide design)`)
**WORK_HEAD:** `PENDING` (work commit; the post-note receipt commit is HEAD after it)
**Contract:** recorded `0.28.2` == published; source `/home/andrei/storagegenie-contract/VERSION`, contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2`
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`, read from opencode provider metadata `/home/andrei/.local/state/opencode/model.json` `recent[0]` + `variant` map — **not** a system-prompt identity line; argv carries no `--model`) · effort `medium` (process argv `/proc/11468/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Spend (real $):** `$0.000000` actual vs `$0` bound — zero metered provider calls.
**Autonomy:** `L2` slice (1 retry available; not used).

The D96 design slice shipped: every screen that rendered browser-default styling now renders on the
Stone token system. 108 hardcoded colour literals across 21 files became 0 outside `theme/` + tests;
`tokens.css` gained additive semantic utilities only; `ThemeToggle` is now reachable from the global
App nav; 10 new presentation tests fail-pre → pass-post; all 164 baseline tests stay green unchanged.
**No deploy, no restart, no DB, no backend** — visual/beauty sign-off is explicitly deferred to the
owner on the later rider (`PG-PR-04`).

## G1 — token migration, every screen

- **Pre-change truth (finding F-SG075-1).** The packet measured "the ONLY hex literals outside `theme/`
  sit in `App.tsx` — 6 hits". That is **false** on this tree: at BASE `git grep` finds **108** literals
  across **21 files** (App.tsx does have exactly 6). Every route and most components carried inline
  hex/`hsl(var(--…))`. The owner's "plain html" report is explained by 21 unstyled-colour files, not 1.
  This widened, not blocked, the slice — all 108 were removed.
- **Zero after.** Post-change scoped grep (outside `**/theme/**` and `**/*.test.*` and the test-only
  `mockProducts.ts` fixture): **0** hits; `App.tsx`: **6 → 0**. Raw both sides in `SG-075_verify.log`.
- **Token-file edits (hunk by hunk, additive only).** `tokens.css` gains, in `:root` and `.dark`:
  `--badge-proposed-bg`/`--badge-proposed-fg` (amber "proposed" tone) and `--accent`/`--accent-foreground`
  (soft surface for chat bubbles, drag-over and the duplicate advisory). Appended utilities, each
  referencing a token: `.bg-accent` `.text-accent-foreground` `.border-accent` `.text-danger`
  `.text-success` `.text-processed` `.border-danger` `.dot-raw` `.dot-processed` `.dot-rendered`
  `.dot-failed` `.badge-green` `.badge-amber` `.badge-grey` `.page-header`. **No prior token value
  changed**; `theme.test.tsx` passes untouched (its exact dark-elevation hex asserts still match).
- **Design calls (mine, reported).** (a) layout geometry (padding/gap/radius/width) stays inline — it is
  not colour and needs no token; (b) one `.page-header` utility gives every route a consistent h1
  (size/weight/rhythm); (c) `ProvenanceBadge` keeps its `badge-green/amber/grey` semantic class names —
  now real utilities in `tokens.css` — so its existing presentation test is **not edited**; (d) the
  status-dot fg colours become `.dot-*` utilities rather than an inline `hsl(var(--badge-${status}-fg))`.
- **ThemeToggle surfaced.** `AppHeader` already imported the toggle (packet premise "imported NOWHERE /
  unreachable" is **false** — F-SG075-2), so it was reachable on the catalog route only. The toggle is
  now rendered in the global `App.tsx` nav on non-catalog routes; the catalog route keeps the one in
  `AppHeader` so exactly one toggle is visible per screen and `shell.test.tsx`'s behavior test stays
  green unchanged. Its click flips the `dark`/`light` document class **and** persists `sg-theme`, proven
  by a real `fireEvent.click` interaction test (not a render snapshot).

### Screen-by-screen adoption table

Enumeration criterion: **files under `frontend/src/routes` + `frontend/src/components` + `frontend/src/App.tsx` that render user-visible markup.** My enumeration = **27 files**, identical to the packet's 27-file expectation (9 routes + 9 top-level components + 5 `shell/` + 3 `catalog/` + `App.tsx`). 22 were migrated; 5 were already token-driven and deliberately left byte-identical (reason given); 1 data fixture is excepted.

| # | File | Token classes applied (or status) | Test proving it |
|---|---|---|---|
| 1 | `App.tsx` | nav `bg-card border-border`; active link `bg-primary text-primary-foreground`; links/brand `text-foreground` + `focus-ring`; footer `text-muted-foreground`; root `bg-background text-foreground`; `ThemeToggle` in nav | `theme-adoption.test.tsx` "App nav …" + "toggle flips … persists" |
| 2 | `routes/AnalyticsPage.tsx` | root `text-foreground`; h1 `page-header text-foreground`; `text-muted-foreground`; alert `text-foreground` | `theme-adoption.test.tsx` analytics |
| 3 | `routes/AssetDetailPage.tsx` | root/h1 tokens; `text-primary` link; `bg-card`/`bg-primary` buttons; inputs `bg-background text-foreground border-border focus-ring`; panels `bg-card-muted`/`bg-card border-border`; `text-danger`, `text-muted-foreground`, `font-mono`, `border-border` table | `theme-adoption.test.tsx` asset detail |
| 4 | `routes/CapturePage.tsx` | root `text-foreground`; h1 `page-header text-foreground`; `text-muted-foreground` | `theme-adoption.test.tsx` capture |
| 5 | `routes/CatalogPage.tsx` | **already token-driven at BASE** (renders `AppShell`), no change | `theme-adoption.test.tsx` nav; `shell.test.tsx` unchanged |
| 6 | `routes/ChatPage.tsx` | root/h1 tokens; `text-muted-foreground`; alert `text-foreground`; link `text-primary` | `theme-adoption.test.tsx` chat |
| 7 | `routes/InboxPage.tsx` | root/h1 tokens; `text-danger`; step `bg-card-muted`; task card `bg-card border-border`; `text-muted-foreground` | `theme-adoption.test.tsx` inbox |
| 8 | `routes/PlanningPage.tsx` | root/h1 tokens; `text-muted-foreground`; alert `text-foreground` | `theme-adoption.test.tsx` planning |
| 9 | `routes/ReviewPage.tsx` | root/h1 tokens; back link `text-primary focus-ring` | `theme-adoption.test.tsx` review |
| 10 | `routes/SettingsPage.tsx` | root/h1 tokens; `text-muted-foreground`; section `bg-card border-border`; `text-danger`; button `bg-card text-foreground border-border focus-ring` | `theme-adoption.test.tsx` settings |
| 11 | `components/AssetCard.tsx` | `bg-card border-border focus-ring`; `bg-card-muted`; `text-muted-foreground` | `AssetCard.test.tsx` (unchanged) + adoption render |
| 12 | `components/AssetForm.tsx` | inputs `bg-background text-foreground border-border focus-ring`; dropzone `border-primary bg-accent`/`border-border bg-card-muted`; `text-danger`; `bg-primary text-primary-foreground` submit; `text-muted-foreground` | `AssetForm.test.tsx` (unchanged) |
| 13 | `components/CandidateCard.tsx` | `bg-card border-border`; advisory `bg-accent border-accent`; inputs/`border-border`; `bg-card-muted`; `text-muted-foreground` | `CandidateCard.test.tsx` (unchanged) |
| 14 | `components/ChatTranscript.tsx` | user `bg-accent text-accent-foreground`; assistant `bg-card-muted text-foreground`; `border-border`; `text-muted-foreground` | `ChatTranscript.test.tsx` (unchanged) |
| 15 | `components/EvidenceGallery.tsx` | `text-muted-foreground`; `border-border` | render-path via `AssetDetailPage`/`ReviewPage` tests |
| 16 | `components/ExpiryEntryForm.tsx` | section `bg-card border-border`; `text-success`; `text-danger` | `ExpiryEntryForm.test.tsx` (unchanged) |
| 17 | `components/JobCard.tsx` | `bg-card`, `border-primary`/`border-border`, `text-muted-foreground`, `focus-ring` | `JobCard.test.tsx` (unchanged) |
| 18 | `components/PlanningSuggestionCard.tsx` | `bg-card border-border`; `text-muted-foreground`; `text-foreground` | `PlanningSuggestionCard.test.tsx` (unchanged) |
| 19 | `components/ProvenanceBadge.tsx` | `badge-green`/`badge-amber`/`badge-grey` (now real token utilities) | `ProvenanceBadge.test.tsx` (unchanged, still green) |
| 20 | `components/catalog/ProductCard.tsx` | `bg-card border-border`; well `bg-card-muted` + `border-danger`; `text-danger`; `text-muted-foreground`; `border-border` dots | `catalog.test.tsx` (unchanged, incl. DQ3 pairs) |
| 21 | `components/catalog/ProductGrid.tsx` | empty `border-border text-foreground`; status dot `.dot-*`; existing `bg-card-muted`/`font-mono` | `catalog.test.tsx` (unchanged) |
| 22 | `components/catalog/ProductCardSkeleton.tsx` | **already token-driven** (`bg-card border-border`, `bg-muted/50`), no change | `catalog.test.tsx` (unchanged) |
| 23 | `components/shell/AppHeader.tsx` | **already token-driven**, no change (retains the catalog toggle) | `shell.test.tsx` (unchanged) |
| 24 | `components/shell/AppShell.tsx` | **already token-driven** (`bg-background text-foreground`), no change | `shell.test.tsx`/`catalog.test.tsx` (unchanged) |
| 25 | `components/shell/CatalogToolbar.tsx` | **already token-driven** (`bg-card border-border`, `bg-primary`, `bg-card-muted`, `text-muted-foreground`, `focus-ring`), no change | `shell.test.tsx` (unchanged) |
| 26 | `components/shell/AssetImportModal.tsx` | dropzone `border-primary`/`border-border bg-card-muted`; `text-danger`; `text-processed`; `text-muted-foreground`; existing `bg-card`/`bg-primary`/`focus-ring` | `import-modal.test.tsx` (unchanged) |
| 27 | `components/shell/ItemInspectorDrawer.tsx` | tab buttons + `border-border`; `text-danger`; existing `bg-card`/`bg-background`/`focus-ring`/`font-mono` | `drawer.test.tsx` (unchanged) |

**Deliberately not migrated / excepted (silence is not coverage):**
- `components/catalog/mockProducts.ts` — **test-only fixture** (sole importer `catalog.test.tsx`); its hex
  strings are mock product colour *data* and placeholder-SVG fills, not chrome styling. Falls under the
  tests exemption (F-SG075-3). It renders no user-visible markup in production.
- Files #5, #22–#25 (CatalogPage, ProductCardSkeleton, AppHeader, AppShell, CatalogToolbar) were
  **already on the token system at BASE** — verified by inspecting them, not assumed; touching them
  would have been churn with zero adoption gain.
- `theme/ThemeProvider.tsx`, `theme/ThemeToggle.tsx`, `main.tsx`, `index.html` — outside the scope
  ceiling (only `theme/tokens.css` may be touched). `ThemeToggle.tsx` already uses token classes.

## G2 — proof without a browser (three legs, stated)

1. **Per-screen themed-landmark tests fail-pre → pass-post.** New presentation test
   `frontend/src/routes/theme-adoption.test.tsx` asserts each route's h1 carries `page-header text-foreground`
   and the App nav carries `bg-card border-border` + the toggle. Against BASE source: **9 failed | 1 passed**
   (raw captured). Against migrated source: **10 passed**. The one pre-change pass is the toggle, which
   already worked (F-SG075-2).
2. **Token-adoption grep.** PRE `108` / POST `0` outside `theme/` + tests (App.tsx `6 → 0`). Raw both sides.
3. **`npm run build` + full `vitest` green + `eslint` clean + `tsc --noEmit` clean.** 23 files / 174 tests
   pass; build emits `index-CoNI-1Zn.css` (3.84 kB) + `index-B_67LUDe.js` (303.82 kB). No headless browser
   exists on the box, so **BEAUTY is not proven here** — this slice proves ADOPTION only; the owner judges
   taste on the deploy rider.

## G3 — what must NOT change

- Same routes, same elements, order, copy, handlers, API calls. **No behavior test was edited.** All 164
  baseline tests pass unchanged; the only new test file is the presentation proof above. (The slice added
  no logic; `git diff` on the migrated files is class/style only.)
- No new runtime dependency (`package.json`/lock untouched); no font/CDN fetch (system stacks only); no
  `.env`, no compose, no backend, no migration. `git diff --name-only` is entirely under `frontend/src`.

## Findings

- **F-SG075-1 (packet premise false — literal count).** "Only App.tsx, 6 hits" → actual BASE count is 108
  across 21 files. App.tsx is 6. Reported, not bent; all 108 removed.
- **F-SG075-2 (packet premise false — toggle reachability).** "`ThemeToggle`/`useTheme` are imported
  NOWHERE — dark mode is unreachable" → `ThemeToggle` was already imported and rendered by
  `components/shell/AppHeader.tsx:4,85`, reachable on the catalog route. The gap was *global* reachability,
  and the toggle interaction itself already worked (hence the 1 pre-change pass). Fixed by surfacing it in
  the App nav.
- **F-SG075-3 (test-only fixture exemption).** `catalog/mockProducts.ts` holds 20 hex literals that are mock
  *data*, not chrome. It is imported only by `catalog.test.tsx`. Exempted as test-support, stated loudly
  rather than silently narrowing the grep.
- **F-SG075-4 (angle-token standing line).** No in-scope file carried `<...>` literals before or after the
  edits (re-probed by grep); no test constructs such a string, so the SG-062 char-code rule had no work to do.
- **F-SG075-5 (header duplication tension).** The packet asked to surface the toggle in the App nav while a
  behavior test (`shell.test.tsx:289`) renders `CatalogPage` standalone and clicks its header toggle. Adding
  the toggle unconditionally to the nav would either duplicate it on the catalog screen or break that
  behavior test. Resolution: nav toggle on non-catalog routes, header toggle on catalog — exactly one per
  screen, all tests green. Stated because it is a design call the packet left to me.

## No-write / spend construction

No HTTP request, no DB open, no provider call, no `docker`, no restart, no deploy was issued. Commands run
were local reads (`git`, `rg`), the frontend test runner (jsdom), the local `vite`/`tsc`/`eslint` binaries,
and the notes-ref git pushes required by the receipt. No `npm install`, no network fetch. Real spend `$0.000000`.

## Receipt — notes ref (M20-corrected block)

_PENDING — filled in the receipt commit after the push; executed `show` output pasted there._

## Acceptance criteria

- [x] Zero hardcoded colour literals outside `theme/` + tests (grep quoted both sides: 108→0; App.tsx 6→0); every enumerated screen file migrated or explicitly excepted with reason.
- [x] Per-screen themed-landmark tests fail-pre → pass-post (raw both sides, committed); toggle interaction test flips class + persists; behavior tests green unchanged (164/164).
- [x] Build + vitest + eslint + tsc green (quoted); secret scan 0; no backend diff; no new dependency; no new network primitive/URL (proven statically — namespace isolation denied without privilege, reported); $0; no vacuous pass (F-SG075-3 and the 1 pre-change pass called out).
- [x] No migration; no deploy claimed; visual sign-off explicitly deferred to the owner on the rider.

## UNCLEAR

- **FIRST READ:** The packet's core premises were two-for-two false on the target tree ("only App.tsx has 6 hits"; "ThemeToggle imported NOWHERE"). I built on the corrected measurements (108 literals / toggle already wired) and reported both as findings rather than bending the tree to match the packet.
- **DURING EXECUTION:** The first draft of the new test file OOM'd the vitest worker because the mocked hooks returned fresh object identities each render, re-firing `CatalogPage`'s accumulation effect. Fixed with stable `vi.hoisted` fixtures; this was a defect in my test, not in the app, and is disclosed rather than hidden.
- **REMAINING:** BEAUTY is unproven by construction — no headless browser exists on the box; this slice proves token ADOPTION only, and the owner's eyeball on the deploy rider is the final authority. Network isolation (`unshare -rn`) was denied without privilege, so "no network" rests on the static diff proof plus the local-only toolchain, not on a namespaced run.
