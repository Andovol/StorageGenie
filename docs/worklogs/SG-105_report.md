# SG-105 — UI centering + control consistency repair, Inbox/Capture/Catalog

- **Coder:** `opencode`
- **Effort:** `high` — read from the process arguments (`opencode run --auto --dir /home/andrei/StorageGenie --variant high`)
- **Model:** `unknown` — no model id is sent; the CLI default is the model (per policy). Not guessed.
- **Contract:** recorded **`0.33.0`** == published (`b232b84`; D129 adoption). **Source path:** `STATE.md:3` (recorded `0.33.0`, FETCH_HEAD `b232b84`) + `AGENTS.md` rule-set version. **`.rules-cache/` is ABSENT on this checkout** — the contract is echoed from the checkout, not from a fetched cache (same as SG-104).
- **BASE:** `origin/automation` = `66c7e78de8140e266a609bea6781321ee356b983` (the packet-requested ref, and the commit it resolved to — two fields).
- **WORK_HEAD:** `3b18e93806eb668cb30676c25984bff41b14b0b4`
- **DATABASE:** none · **Restart:** none · **Deploy:** none · **Container actions:** none
- **Spend (real $):** **$0.000000** — zero provider calls, no network.

## Premises re-verified against the tree (a difference is a finding)

| Packet premise | Reality on the tree | Action |
|---|---|---|
| `frontend/src/pages/InboxPage.tsx`, `CapturePage.tsx` | Live at **`frontend/src/routes/`** | Re-verified every quoted line, then edited the real files |
| `frontend/src/components/AppShell.tsx`, `AppHeader.tsx` | Live at **`frontend/src/components/shell/`** | Same |
| `InboxPage.tsx:22` `padding:24, maxWidth:1100` | Confirmed at `InboxPage.tsx:27` | Container introduced |
| `CapturePage.tsx:22` padding only; `AssetForm.tsx:112` `maxWidth:520` | Confirmed (`AssetForm.tsx:112`) | Form width moved into the container's `form` variant |
| `AppShell.tsx:77` `main` padding only | Confirmed | `main` now the shared container |
| Bare Inbox select / inline-only Capture+AssetForm selects / themed toolbar select | Confirmed | One shared control treatment |
| Raw file inputs `AssetForm.tsx:169-186` | Confirmed | Label-triggered visually-hidden real inputs |
| `JobCard.tsx:9` no text colour | Confirmed (black-on-dark titles) | `text-foreground` + state tones |
| Unclassed review `Link`s (`InboxPage.tsx:28`) | Confirmed (default purple) | `text-primary` link treatment |
| Brand twice on Catalog (`App.tsx` nav + `AppHeader.tsx`) | Confirmed | Dropped the `AppHeader` brand (global nav kept) |
| Cards fixed `aspectRatio: 3/4` (`ProductCard.tsx:113`) | Confirmed | Removed; content-sized |
| Pills speak raw `asset_type`; cards speak `toProductCategory` | Confirmed | Pills now display the card vocabulary |
| `.rules-cache/` present | **Absent** | Contract echoed from `STATE.md`/`AGENTS.md` (F-SG105-2) |

## G1 — one centered page container on all three pages

- New shared component **`frontend/src/components/shell/PageContainer.tsx`** (`PAGE_MAX_WIDTH = 1100`, `FORM_MAX_WIDTH = 520`, `pageContainerStyle(variant)`, `PageContainer`). It renders `width:100%`, `maxWidth` (1100 page / 520 form), `marginLeft/Right:auto`, `padding:24`.
- **Inbox** (`InboxPage.tsx`): outer `div` with hand-rolled `padding+maxWidth` replaced by `<PageContainer className="text-foreground">`.
- **Capture** (`CapturePage.tsx`): outer `div` replaced by `<PageContainer>`; the `AssetForm` is wrapped in `<PageContainer variant="form">` — the old `AssetForm.tsx:112 maxWidth:520` is **removed**, so the narrow width is the container's `form` variant, not a per-file constant.
- **Catalog** (`AppShell.tsx`): `<main style={{padding:24}}>` replaced by `<PageContainer as="main">` (keeps the `<main>` landmark).
- `PG-SC-07`: empty states untouched and still covered — Inbox "No import jobs yet." / "No review tasks." (existing tests), catalog empty dashed canvas (existing test). A **new** filtered-empty message ("No open review tasks.") was added so an all-resolved queue is never blank/misleading.
- **Question answered (`PG-SC-09`):** does every page share one centered layout? **Yes** — the same `.page-container` class/style renders on Inbox, Capture and the Catalog `main`, asserted in the DOM (not pixels).

## G2 — one themed control treatment (selects + file pickers)

- **Shared treatment** exported from `CatalogToolbar.tsx`: `THEMED_CONTROL_CLASS = "bg-background text-foreground border-border focus-ring"` and `CONTROL_STYLE` (the toolbar's own select classes, now reused — the packet's "reuse the toolbar's classes" option). The toolbar's three selects now use the constants.
- Applied to: **Inbox household select**, **Capture household select**, **AssetForm asset-type select**.
- **File pickers** (`AssetForm.tsx`): the raw native inputs are gone from the visual layout. Two `<label>`s ("Choose files" multiple / "Take a photo" camera) carry the themed control class; each wraps a **real `<input type="file">`** that is visually hidden (`position:absolute; clip:rect(0 0 0 0)`), so it stays in the DOM, in the tab order and in the accessibility tree. The existing camera test (`capture=environment`, image-only accept, not multiple) still passes unchanged.
- **Question answered (`PG-SC-09`):** is every control themed? **Yes** — every select and file input on the three pages carries the theme class / themed label, asserted at DOM class level.

## G3 — readable Inbox (cards, links, queue)

- **`JobCard.tsx`**: the button now carries `text-foreground` (no more browser-default black titles on the dark card). Status is toned by state via exported `jobStateTone`: `FAILED|ERROR → text-danger`, `COMPLETED|SUCCEEDED → text-success`, `PROCESSING|RUNNING|IN_PROGRESS → text-processed`, everything else `→ text-muted-foreground`. No browser-default text remains in the card.
- **Review links** (`InboxPage.tsx`): `Link` carries `className="text-primary focus-ring"` + underline — the in-tree link treatment (same token as the ReviewPage back-link and the toolbar Delete/Clear-all), no default purple.
- **Resolved hidden by default**: a **Review status** select (`open` default / `resolved` / `all`) — the Planning status-filter precedent. The queue renders only the selected scope; resolved rows appear only under `resolved`/`all`.
- **Question answered (`PG-SC-09`):** is the Inbox readable and honest about resolved work? **Yes** — themed text throughout, resolved work is filtered by an explicit, visible control (not silently dropped), and an all-resolved queue says so.

## G4 — coherent Catalog (chrome, grid, vocabulary)

- **Single brand row**: the duplicate `StorageGenie` brand `Link` was **dropped from `AppHeader.tsx`**; the global nav keeps the brand on this route and all others. The pre-existing test asserting two brand rows on `/` was updated to assert **one** (a real behaviour change).
- **Grid**: `ProductGrid.tsx` breakpoints are **kept** (2/3/4/5). No card is clipped at the viewport edge because the columns are `repeat(N, minmax(0, 1fr))` (min-content cannot force overflow) and the G1 container supplies centered max-width + 24px padding. Reported decision: keep the counts; no `auto-fill` move.
- **Cards size to content**: `aspectRatio: "3 / 4"` removed from `ProductCard.tsx`. The media well stays uniform (`1 / 1`, `object-contain`), and the DQ3 badge keeps its semantic token classes plus its dead Tailwind utility strings — **untouched, out of scope** (asserted intact in the gate log).
- **One vocabulary**: `CatalogPage.tsx` pills now display `toProductCategory(key)` (so the raw `unknown` facet renders as **Uncategorized**), while selecting that pill still sends the **REAL server filter `asset_type=unknown`**. Counts aggregate per display name. `types/product.ts` was **not** changed — the existing map already carries the mapping (disclosed).
- **Question answered (`PG-SC-09`):** is the Catalog one coherent surface? **Yes** — one brand, one centered grid, content-sized cards, and pills/cards sharing one vocabulary through the real filter.

## G5 — tests + gates

- **Extended vitest files (decided: extend colocated suites rather than a new file):** `JobCard.test.tsx`, `InboxPage.test.tsx`, `AssetForm.test.tsx`, `catalog.test.tsx`, `shell.test.tsx`, `theme-adoption.test.tsx`. Every new gate asserts **DOM classes / style tokens**, never pixels; the vocabulary gate drives the **real** `CatalogPage` + `toProductCategory` + server-filter call (`PG-SC-12`, no re-implemented seam).
- **FAIL-then-PASS, both raw in `SG-105_verify.log` (`PG-EV-09`/`PG-EV-01`):**
  - FAIL-pre (tests present, source unchanged): **13 failed / 178 passed** — every failure is one of the new/updated gates (container absent, control classes absent, JobCard tones absent, link unthemed, resolved row visible, pill labelled `unknown (1)`, brand count 2, card aspect 3/4).
  - PASS-post (source applied): **191 passed / 23 files**.
- **Gates:** `npm test` green (191); `npm run build` (tsc + vite) clean → the type gate; `eslint src` clean; **backend suite explicitly WAIVED** — no backend file in the ceiling (`git diff --stat -- backend/` empty, quoted); `PG-SC-11` end-relative grep over the six touched test files → **0 hits (exit 1)**; secret gates → **0** (value-shape scan over the added diff exit 1; literal secret-assignment grep exit 1).
- **Visual proof BAN honoured:** no screenshot, no visual claim anywhere; all assertions are DOM/token-level.
- **No vacuous pass:** the container/control/tone/vocabulary gates each fail on the pre-change tree at their own assertion (not a skipped or scoped-out check); the vocabulary gate asserts the pill label AND the real `asset_type=unknown` server call; the resolved gate uses a real resolved fixture and proves it hidden then revealed.
- **Question answered (`PG-SC-09`):** does the suite prove it through the real components? **Yes** — the tests mount the real pages/components and assert the real DOM/filter path.

## G6 — worklog and report

`docs/worklogs/SG-105.log`, `SG-105_report.md`, `SG-105_verify.log` (raw outputs + both fail-then-pass runs + every gate). First token `SG-105`; elapsed-versus-budget per leg with units; MODEL/effort from process arguments; spend **real $** $0.000000.

## Design calls (mine, reported)

- **Container**: a small shared **component** (not just a style) so the three pages literally share one source; the `form` variant owns the 520 width.
- **Control treatment**: reuse the toolbar's existing classes via exported constants (no new class invented).
- **File pickers**: label-triggered visually-hidden real inputs (keyboard + SR preserved), not a styled fake button.
- **Job status tones**: reuse the existing `text-danger`/`text-success`/`text-processed`/`text-muted-foreground` tokens.
- **Brand**: drop the `AppHeader` brand, keep the global nav (the packet's stated constraint "the other seven routes keep the global nav untouched").
- **Grid**: keep the 2/3/4/5 counts (no `auto-fill`).
- **Resolved filter**: an explicit Review-status select (Planning precedent) rather than a silent hide.
- **Pills**: aggregate counts per display name to keep the pill set collision-free; the filter chip now shows the display name (coherence beyond the literal requirement).

## Findings / disagreements

- **F-SG105-1 (paths):** the packet's `src/pages/` + `src/components/` paths do not exist; the real tree is `src/routes/` + `src/components/shell/`. All quoted line numbers were re-verified; no premise was bent to match.
- **F-SG105-2 (`.rules-cache/` absent):** contract echoed from `STATE.md:3` + `AGENTS.md` (recorded `0.33.0`, FETCH_HEAD `b232b84`). Same as SG-104's F-SG104-3 tail.
- **F-SG105-3 (`ProductCardSkeleton.tsx` still `3 / 4`):** the loading placeholder is outside the packet's ceiling (`ProductCard.tsx` named, skeleton not). Cards are content-sized; the skeleton keeps its shape, so the loaded card may be shorter than the skeleton it replaced. Disclosed; a later slice can align it.
- **F-SG105-4 (link contrast):** `--primary` is the same dark maroon in both themes, so `text-primary` links are the themed treatment but may be low-contrast on the dark card. `tokens.css` is outside the ceiling; reported for a later token slice.
- **F-SG105-5 (other routes):** Analytics/Chat/Settings/Planning/Review/AssetDetail still hand-roll `maxWidth` (900/520/1100). The G1 criterion is scoped to the three named pages; they are untouched.
- **F-SG105-6 (pill aggregation edge):** if a literal `asset_type` value "Uncategorized" coexists with `unknown`, both collapse to one display pill whose filter sends the first-seen raw key. Edge case, disclosed.

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| All three pages share the centered container; no hand-rolled page `maxWidth` | **MET** | `.page-container` on Inbox/Capture/Catalog `main`; `maxWidth` grep over the four files = 0 hits |
| Every select + file picker themed; no native white control | **MET** | class assertions in Inbox/AssetForm tests; label-triggered hidden inputs |
| Job titles/status legible; review links themed; resolved hidden by default | **MET** | `text-foreground` + tone classes; `text-primary`; Review-status filter test |
| One brand row; grid unclipped; cards content-sized; pills/cards share vocabulary via real filter | **MET** | brand count 1; `minmax(0,1fr)` + container; no `aspectRatio`; `asset_type=unknown` call asserted |
| Tests fail-pre/post-pass both raw; suite + build + lint green; backend waived; secret 0; no vacuous pass; no visual claim | **MET** | `SG-105_verify.log` |

**Vacuous-pass check (`PG-EV-01`, loudly):** every new gate was seen to fail on the unchanged tree at its own assertion (13 distinct failures quoted raw), so none can pass vacuously. **Where this slice is weaker than it looks:** (a) it is presentation-only and the served bundle is **not** rebuilt — the running service still shows the old UI until a later rider (said in as many words); (b) the visual result is asserted only at DOM/token level — the owner signs off pixels post-deploy; (c) the skeleton/card height mismatch (F-SG105-3) and the link-contrast token question (F-SG105-4) remain.

## Receipt note on the notes ref (M20-corrected block)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. Note added on `WORK_HEAD`; notes ref pushed; verified against the **fetched, mapped** ref. Executed, verbatim:

```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   66c7e78..3b18e93  automation -> automation
push_automation_exit=0

$ git notes --ref=refs/notes/storagegenie-coder-reports show 3b18e93806eb668cb30676c25984bff41b14b0b4   # pre-check
error: no note found for object 3b18e93806eb668cb30676c25984bff41b14b0b4.
precheck_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-105 | Report: docs/worklogs/SG-105_report.md | Work-HEAD: 3b18e93806eb668cb30676c25984bff41b14b0b4" 3b18e93806eb668cb30676c25984bff41b14b0b4
note_add_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   97ddaec..14d01de  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg105-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg105-verify
fetch_exit=0

$ git notes --ref=refs/notes/storagegenie-coder-reports-sg105-verify show 3b18e93806eb668cb30676c25984bff41b14b0b4
Dispatch-ID: SG-105 | Report: docs/worklogs/SG-105_report.md | Work-HEAD: 3b18e93806eb668cb30676c25984bff41b14b0b4
show_exit=0
```

The final tip (the docs-only receipt commit) is dual-annotated too (note-anchor inoculation, SG-092 precedent). `note=yes`.

---

## UNCLEAR

- **FIRST READ:** the packet's file paths (`src/pages/`, `src/components/`) are hypotheses that do not exist on this tree; the real layout is `src/routes/` + `src/components/shell/`. I re-verified every quoted line and edited the real files rather than bending the tree to the packet. The contract cache (`.rules-cache/`) is also absent, so `0.33.0`/`b232b84` is echoed from `STATE.md`/`AGENTS.md`.
- **DURING EXECUTION:** the G4 brand change necessarily rewrote an existing assertion (`shell.test.tsx` brand count 2 → 1) — a real, intended behaviour change, not a bent test; the pill vocabulary change likewise rewrote the existing `unknown (1)` pill assertion to `Uncategorized (1)`. Both are inside the packet's test-file ceiling. The `ProductCardSkeleton` (out of ceiling) still carries the old `3/4`, disclosed as F-SG105-3.
- **REMAINING:** the served bundle is not rebuilt (presentation rider owed before the owner sees pixels); F-SG105-3 (skeleton shape) and F-SG105-4 (link contrast token) are parked; other routes' hand-rolled `maxWidth` (F-SG105-5) is untouched by scope.
