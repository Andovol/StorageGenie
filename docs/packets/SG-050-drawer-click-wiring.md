# SG-050 — drawer click wiring: onSelect props + catalog mount (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Wardrobe track (D63, L3): closes the SG-046 STOP remainder (G2 wiring); SG-047 import modal follows. The drawer itself ships complete in SG-046 (`shell/ItemInspectorDrawer.tsx`, tested) — this slice ONLY wires clicks to it. **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (receipt echoes it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no file under `backend/` is touched** (frontend-only; a needed backend change is a STOP); **no migration** (an alembic diff is a STOP); **AI stays OFF**: no provider calls, **$0 metered**; no new dependencies; NETWORK: none.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` omission-traced · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live. (`PG-EV-06`/`PG-EV-08`/`PG-DP-02..04` do not fire: no live writes beyond the drawer form's own user-confirmed PATCHes, no delivery change, no entry point, no reported failure.)

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none new. Restart: none. NETWORK: none.**

## Why this exists

SG-046 stopped exactly here: the drawer is complete but unmounted, because the click owners live outside its ceiling. Verified in the SG-046 report: card clicks are owned by `ProductCard.tsx:73-74` (`<Link to="/assets/:id?...">`), table row clicks by `ProductGrid.tsx:99-100` (`navigate(`/assets/${item.id}?...`)`), and `CatalogPage.tsx` renders `<ProductGrid>` owning no card/row click event. This slice walks to those exact event owners (M23: name them in the ceiling — done below).

## G1 — additive `onSelect` on both click owners (no behaviour change when absent)

- `ProductCard.tsx`: accept optional `onSelect?: (id: string) => void`; when present, clicking the card calls it INSTEAD of navigating (keyboard: Enter/Space likewise); when absent, today's `Link` behaviour is byte-identical.
- `ProductGrid.tsx`: accept optional `onSelect?: (id: string) => void`, pass through to cards + table rows (row click + Enter key + the `...` button's inspector action); absent → today's navigate behaviour byte-identical.
- Additive-only: no existing call site changes behaviour (`PG-DP-01` permissive-only — `AssetCard.tsx` and every other consumer untouched).

## G2 — mount the drawer in `CatalogPage.tsx` (+ query invalidation)

- `CatalogPage` holds the selected asset id, renders `ItemInspectorDrawer` for it, clears on close (focus returns per the drawer's own contract); drawer PATCHes invalidate the `assets` + `asset` query keys (the pattern SG-046 prepared but reverted — `AssetDetailPage.tsx:27-32` is the read-only reference).
- Deep links (`/assets/:id`) keep working untouched.

## G3 — tests: extend `catalog.test.tsx` + `drawer.test.tsx` patterns, mutation proof, both runs committed

- Card click with `onSelect` calls it with the id and does NOT navigate; without it navigates as today; table row + Enter + `...` inspector action likewise; drawer opens from a catalog click with the right asset and closes back; invalidation fires on save.
- **Pre-change honesty (class 8):** the `onSelect` prop does not exist on base — quote + label hollow, never evidence. Discriminating proof is a post-change mutation run (2: the navigate-vs-select branch, the invalidation key — each caught singly, reverted clean, raw committed).
- Full frontend suite green, lint clean, build clean — the §3 conditional derived-test-set block is NOT pasted.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-050.log`, `{{WORKLOG_DIR}}/SG-050_report.md`, `{{WORKLOG_DIR}}/SG-050_verify.log` (hollow labeled, mutations raw). First token `SG-050`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0`); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/components/catalog/ProductCard.tsx` (G1 hunk only) · `frontend/src/components/catalog/ProductGrid.tsx` (G1 hunk only) · `frontend/src/routes/CatalogPage.tsx` (G2 hunk only) · `frontend/src/components/catalog/catalog.test.tsx` + `frontend/src/components/shell/drawer.test.tsx` (test hunks only) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every file under `backend/` (excluded BY RULE per `PG-SC-05`, grep-gated), the drawer component itself (ships complete in SG-046; a needed change there is a finding, not a silent edit), and any new dependency.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): G1 the two owner files; G2 the `CatalogPage` hunk; G3 the two test files; G4 worklogs. No blanket exclusion is issued. No stop-gate shares a condition with a remediation step (`PG-IC-03`) — stops win, stated not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-01`: mutations fed wrong values in the same run, shown failing singly. `PG-EV-02`: rendered DOM / committed outputs, never exits. `PG-EV-05`: properties ("click with `onSelect` selects without navigating", "click without it navigates as today", "save invalidates the catalog queries").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · **1500s early-close** · **2100s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): two props + one mount; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises verified in-slice with quoted reads — in particular the two click-owner lines, the drawer component path, the invalidation pattern.
- **FAIL-then-PASS honestly (`PG-EV-09`):** hollow run labeled hollow; green run; mutation run caught-singly + reverted; all three raw committed.
- Suite + lint + build green; secret scan 0; no `backend/` diff; no migration; dep list unchanged; absent-prop behaviour byte-identical (today's nav provable); no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: user-confirmed PATCHes only (by id, only if the drawer form is exercised), live spend `$0`, no network.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-050 | Report: docs/worklogs/SG-050_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly (`<ref>:<ref>`, M21 — a bare fetch never updates a notes ref), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1500s early-close · 2100s overall; $0 metered; actual-versus-budget per leg with units.
