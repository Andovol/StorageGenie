# SG-045 — catalog grid, product cards, table view, skeletons, mocks (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Wardrobe track (D63, L3) step 3 of 5: SG-046 drawer (row/card click target) → SG-047 import modal. Prompt 3 + DQ answers are the spec; the badge table and column spec below are EMBEDDED (M19 — `docs/design/DQ-answers.md` committed, citable by path). **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (receipt echoes it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no file under `backend/` is touched** (frontend-only; a needed backend change is a finding: STOP if it blocks, otherwise report and ship the rest); **no migration** (an alembic diff is a STOP); **AI stays OFF**: no provider calls, **$0 metered**; no new dependencies; NETWORK: none.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` omission-traced · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-SC-11` end-relative-assertions · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live. (`PG-EV-06`/`PG-EV-08`/`PG-DP-02..04` do not fire: no live writes, no delivery change, no entry point, no reported failure.)

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. NETWORK: none.**

## Why this exists

The Catalog route renders the old `AssetCard` grid (`AssetCard.tsx:1-71` — gray bordered card, cover thumb or "no image", name/type-status/counts; thumb route `/v1/evidence/{id}/thumb/256?household_id=` per `AssetCard.tsx:9` + `EvidenceGallery.tsx:17`, with `onError` hiding); density state exists (`Density = "grid" | "table"` in `CatalogToolbar.tsx`, state held in `CatalogPage`) but both options render the grid. This slice ships the wardrobe grid: new cards, both density views, skeletons, empty state, honest mocks.

## G1 — `ProductCard.tsx` + `ProductCardSkeleton.tsx` (new, `frontend/src/components/catalog/`)

- 3:4 vertical card, token classes only, focus ring both themes; cutout well (`aspect-square`, `bg-card-muted`) with `object-contain` media + `onError` fallback well (same honesty as today's `onError` hide — a broken image never renders a broken icon).
- Status badge top-right, EXACT DQ3 pairs embedded here (do not infer, do not "improve"): raw gray = light `bg-stone-100 text-stone-700 border-stone-200` / dark `bg-stone-800/50 text-stone-400 border-stone-700/50`; processed blue = light `bg-sky-50 text-sky-800 border-sky-200` / dark `bg-sky-950/40 text-sky-400 border-sky-800/50`; rendered green = light `bg-emerald-50 text-emerald-800 border-emerald-200` / dark `bg-emerald-950/40 text-emerald-400 border-emerald-800/50`; failed rose = light `bg-rose-50 text-rose-800 border-rose-200` / dark `bg-rose-950/40 text-rose-400 border-rose-800/50`. Failed adds the hairline rose well border + centered warning icon + title error icon (DQ10).
- Footer: name (truncate), category mono micro-pill, primary-color dots (8px; absent when metadata has none — never placeholder dots).
- `ProductStatus` gains `'failed'` (type-only extension per the DQ10 state machine; mapper default stays `'raw'`).
- Click target: the existing asset detail route (`/assets/:id?household_id=` — today's `AssetCard.tsx:18` destination). The SG-046 drawer takes over clicks next slice; no click leads nowhere this slice.
- Skeleton: same 3:4 shape, `bg-muted/50 animate-pulse`, aria-hidden.

## G2 — `ProductGrid.tsx` with BOTH density views + empty state (new, same dir)

- Grid: 2 cols mobile → 3 tablet → 4 desktop → 5 ultrawide, `gap-4 md:gap-5` equivalents in the token CSS idiom (no Tailwind installed — plain classes).
- Compact Table per DQ5, embedded columns: Asset 56px (40px thumb on `bg-card-muted`, same thumb route + `onError` fallback) · Name min-200 trunc · Category 140px mono micro-badge · Status 130px badge + dot · Dimensions/Specs 120px (metadata or honest `—`, never invented) · Added 110px right mono relative date · Actions 48px ghost `...` (opens the asset detail route; delete does NOT exist — no delete control ships, `PG-SC-02`: never ship UI asserting behaviour the inventory says doesn't happen). Row click → asset detail route (drawer takes over SG-046).
- Empty state (filter yields zero): dashed-border canvas + `Import New Item` CTA routing to `/capture` (the DQ9 modal arrives SG-047 — labeled truthfully).
- Loading: skeletons (count = page limit shape, aria-busy on the region).

## G3 — mocks (`frontend/src/components/catalog/mockProducts.ts`, new) + `CatalogPage` swap hunk

- 8 products spanning the DQ1 six (at least 4 distinct categories), built through the REAL `assetToProductItem` mapper where fields exist; mock-only fields (cutout/scene URLs, colors) use **inline SVG data-URIs** (no network, no binaries committed, deterministic).
- `CatalogPage` grid-swap hunk: render `ProductGrid` (density-aware) instead of the `AssetCard` map; `AssetCard.tsx` itself stays on disk untouched (dead-file removal is a later cleanup, not this slice — say so).

## G4 — tests: new `frontend/src/components/catalog/catalog.test.tsx`, mutation proof, both runs committed

- Mapper-driven (real `assetToProductItem`, mock assets): card renders name/category/dots, badge per status incl. failed visuals, table columns + order, empty state + CTA route, skeleton aria, click-through routes, `—` for absent specs, no-`rawResponse` still holds.
- **Pre-change honesty (class 8):** new modules fail on unresolvable imports — quote + label hollow, never evidence. Discriminating proof is a post-change mutation run (2–3: a badge class, the table column order, a mock status — each caught singly, reverted clean, raw committed).
- Full frontend suite green, lint clean, build clean — the §3 conditional derived-test-set block is NOT pasted.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-045.log`, `{{WORKLOG_DIR}}/SG-045_report.md`, `{{WORKLOG_DIR}}/SG-045_verify.log` (hollow labeled, mutations raw). First token `SG-045`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0`); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/components/catalog/` (4–5 files, new) · `frontend/src/routes/CatalogPage.tsx` (grid-swap hunk only) · `frontend/src/types/product.ts` (`'failed'` status hunk only) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every file under `backend/` (excluded BY RULE per `PG-SC-05`, grep-gated), `AssetCard.tsx` (left on disk), `tokens.css`/`product.test.ts` (owned by SG-043/044; a needed change there is a finding, not a silent edit). No new dependencies.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): G1 the card files; G2 the grid file + `CatalogPage` hunk; G3 mocks + the same hunk; G4 the test file; G5 worklogs. No blanket exclusion is issued. No stop-gate shares a condition with a remediation step (`PG-IC-03`) — stops win, stated not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-01`: mutations fed wrong values in the same run, shown failing singly. `PG-EV-02`: rendered DOM / committed outputs, never exits. `PG-EV-05`: properties ("failed card shows the rose badge + warning icon", "table renders 7 columns in DQ5 order", "empty filter shows the CTA", "absent specs render `—`").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · **1500s early-close** · **2100s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): cards + grid + table + skeleton + mocks; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises verified in-slice with quoted reads — in particular `AssetCard.tsx:1-71`, the thumb routes (`AssetCard.tsx:9`, `EvidenceGallery.tsx:17`), toolbar density exports, the DQ3 badge pairs + DQ5 columns (embedded above), `docs/design/DQ-answers.md` path.
- **FAIL-then-PASS honestly (`PG-EV-09`):** hollow run labeled hollow; green run; mutation run caught-singly + reverted; all three raw committed.
- Suite + lint + build green; secret scan 0; no `backend/` diff; no migration; dep list unchanged; badge classes match the embedded pairs exactly (a greppable property, not eyeballing); no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.
- Every click lands somewhere real (detail route); every deferred item (drawer clicks, delete, modal, server aggregation) named with its destination slice.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: no DB writes, live spend `$0`, no network.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-045 | Report: docs/worklogs/SG-045_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly (`<ref>:<ref>`, M21 — a bare fetch never updates a notes ref), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1500s early-close · 2100s overall; $0 metered; actual-versus-budget per leg with units.
