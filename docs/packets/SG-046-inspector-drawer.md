# SG-046 — inspector drawer: viewer tabs, metadata form, honest AI block (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Wardrobe track (D63, L3) step 4 of 5: SG-047 import modal closes the track. Prompt 4 + DQ answers are the spec; D64 (AI buttons present-but-honest) + D65 (non-schema fields read-only) decided as recommended under the D63 cover. Load-bearing brief content is EMBEDDED below (M19 — `docs/design/DQ-answers.md` committed). **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (receipt echoes it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no file under `backend/` is touched** (frontend-only; a needed backend change is a finding: STOP if it blocks, otherwise report and ship the rest); **no migration** (an alembic diff is a STOP); **AI stays OFF**: no provider calls, **$0 metered**; no new dependencies; NETWORK: none.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` omission-traced · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-SC-11` end-relative-assertions · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live. (`PG-EV-06`/`PG-EV-08`/`PG-DP-02..04` do not fire: no live writes beyond the user-confirmed PATCH the form exists for, no delivery change, no entry point, no reported failure.)

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none new (the form PATCHes through the existing asset endpoint — user-confirmed edits only, same as today's detail screen). Restart: none. NETWORK: none.**

## Why this exists

Cards and table rows navigate to the old detail route; the wardrobe flow opens an inspector drawer instead. Verified current shape: `AssetDetailPage.tsx:1-183` edits via `PATCH /v1/assets/{id}` with `If-Match` version (`:24-32`, fields name/qty/unit/condition at `:100-104`); `PATCH` + `DELETE /v1/assets/{asset_id}` both exist (`backend/app/api/v1/assets.py:202,229` — delete exists; no delete control ships this slice, destination a future slice); evidence file route `/v1/evidence/{id}/file` + thumb route (`EvidenceGallery.tsx:11,17`); assertions carry `field_path/value/source_type/review_state/confidence/source_evidence_ids` (`api/types.ts:11-20`).

## G1 — `ItemInspectorDrawer.tsx` (new, `frontend/src/components/shell/`)

- Slide-over from the right (`max-w-2xl w-full border-l border-border bg-card p-6 overflow-y-auto z-50`), token classes only, focus ring both themes. Header: item title, category mono badge, close button; `Esc` closes; focus moves to close on open and returns to the invoking element on close.
- Viewer tabs (all three switch smoothly; each state labeled truthfully): `Isolated Cutout` → honest empty well (no cutout pipeline exists — the well says cutouts arrive with the AI stages, never a spinner implying work); `Scene / Context` → honest placeholder panel (same rule); `Source Photo` → the REAL evidence image (file route) at full-bleed; bounding-box overlay OMITTED with a stated reason (no bbox data exists — never draw a decorative box, `PG-SC-02`).
- Metadata form: Title → PATCH `display_name`; Category → PATCH `asset_type` (canonical six + passthrough, same mapper); Quantity/Unit/Condition → PATCH (same fields as today's screen, same `If-Match` version pattern at `AssetDetailPage.tsx:24-32`). Observed color tags + functional description: READ-ONLY rows fed by assertions where present, absent rows say so (D65 — no schema home, no editable control pretending otherwise).
- AI action block (D64): `Re-isolate Asset` (secondary) + `Generate Context Scene` (primary) render with icons and, on click, an honest notice ("scene rendering lands with the AI stages — nothing was sent anywhere"). NO model/cost micro-text (DQ7's strings would be fabricated without a backend — omitted with this reason stated, not silently).
- Raw data panel: collapsible mono JSON of the asset + its assertions (coordinates/confidence shown where present, never synthesized).

## G2 — wiring + F-3 cleanup (`CatalogPage.tsx` hunk, `CatalogToolbar.tsx` + shell test hunks)

- `CatalogPage` holds the selected asset: card/table clicks open the drawer (replacing detail-route nav on those clicks; the `/assets/:id` route stays for deep links). Drawer edits invalidate the `assets` + `asset` query keys (same pattern as `AssetDetailPage.tsx:27-32`).
- F-3 cleanup (queued from SG-045): remove the stale "Table view arrives…" note (table shipped) and update `shell.test.tsx:251-259` to assert the table (`PG-SC-11` — fix where the end moved, in this slice).

## G3 — tests: new `frontend/src/components/shell/drawer.test.tsx`, mutation proof, both runs committed

- Drawer opens/closes (click, close button, `Esc`), focus moves + returns; tabs switch with honest cutout/scene states and the real source image; Title/Category save PATCHes with `If-Match` (mocked client); colors/description read-only; AI buttons show the honest notice and send nothing (assert no fetch beyond the mocked PATCH); raw panel expands with asset JSON; F-3 note gone + table asserted.
- **Pre-change honesty (class 8):** new module fails on unresolvable imports — quote + label hollow, never evidence. Discriminating proof is a post-change mutation run (2–3: a tab label, the PATCH payload key, the Esc handler — each caught singly, reverted clean, raw committed).
- Full frontend suite green, lint clean, build clean — the §3 conditional derived-test-set block is NOT pasted.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-046.log`, `{{WORKLOG_DIR}}/SG-046_report.md`, `{{WORKLOG_DIR}}/SG-046_verify.log` (hollow labeled, mutations raw). First token `SG-046`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0`); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/components/shell/ItemInspectorDrawer.tsx` (new) · `frontend/src/components/shell/drawer.test.tsx` (new) · `frontend/src/routes/CatalogPage.tsx` (drawer-state hunk only) · `frontend/src/components/shell/CatalogToolbar.tsx` (F-3 note-removal hunk only) · `frontend/src/components/shell/shell.test.tsx` (F-3 test-update hunk only) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every file under `backend/` (excluded BY RULE per `PG-SC-05`, grep-gated), `AssetDetailPage.tsx` (pattern source, read-only), `tokens.css`/`product.ts` (owned slices; a needed change is a finding, not a silent edit). No new dependencies.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): G1 the drawer + test files; G2 the three gated hunks; G3 the test file; G4 worklogs. No blanket exclusion is issued. No stop-gate shares a condition with a remediation step (`PG-IC-03`) — stops win, stated not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-01`: mutations fed wrong values in the same run, shown failing singly. `PG-EV-02`: rendered DOM / committed outputs, never exits. `PG-EV-05`: properties ("Esc closes and returns focus", "PATCH carries `If-Match` + edited title", "AI click sends no request", "cutout tab states cutouts are not available").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · **1500s early-close** · **2100s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): drawer + wiring + F-3 cleanup; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises verified in-slice with quoted reads — in particular `AssetDetailPage.tsx:24-32` + `:100-104`, `assets.py:202,229`, the evidence routes, `api/types.ts:11-20`, F-3 note + test lines.
- **FAIL-then-PASS honestly (`PG-EV-09`):** hollow run labeled hollow; green run; mutation run caught-singly + reverted; all three raw committed.
- Suite + lint + build green; secret scan 0; no `backend/` diff; no migration; dep list unchanged; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.
- No control implies a working backend (AI notice, cutout/scene honesty, read-only rows labeled); every deferred item named with its destination slice.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: user-confirmed PATCHes only (by id), live spend `$0`, no network.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-046 | Report: docs/worklogs/SG-046_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly (`<ref>:<ref>`, M21 — a bare fetch never updates a notes ref), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1500s early-close · 2100s overall; $0 metered; actual-versus-budget per leg with units.
