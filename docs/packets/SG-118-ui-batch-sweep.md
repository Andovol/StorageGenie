# SG-118 — Group B UI batch: six leftover threads, one sweep, served (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D12-approved UI sweep under D10 L3 (the SG-105 shape: one frontend sweep, owns its refresh per D145). Six threads, all with file pointers verified 2026-09-25 — every premise below is a hypothesis under the frame, re-verify on the target and correct loudly. F-SG105-3 skeleton (`ProductCardSkeleton.tsx` + `3/4` aspect pin + 3-pulse test at `catalog.test.tsx:144-151` exist — establish whether anything remains). F-SG105-4 link contrast (`.text-primary` at `theme/tokens.css:119`, link instances e.g. `AssetDetailPage.tsx:329`, `ChatPage.tsx:121`, `CatalogToolbar.tsx:224,255`, `ExpiryPage.tsx:60,196`). F-SG105-5 hand-rolled widths (`InboxPage.tsx:45`, `ReviewPage.tsx:55` carry inline widths; `PageContainer` is the shared treatment). F-SG105-6 pill edge (`CatalogPage.tsx:75` pills from the real `asset_type` population; `CatalogToolbar.tsx:18`). F-SG108-1 unresolved rows (`ExpiryPage.tsx:188-197` render raw `asset_id` as link text; engine carries no display names). F-SG110-1 thumbnail suffix (`backend/app/storage/local_store.py:12` keeps the SOURCE suffix for JPEG bytes; writer `evidence_service.py:139-212`, reader `evidence.py:108-117` share `thumbnail_path`). **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.36.0` == published (`a9324d5`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** served-code change → rebuild + exactly ONE recreate + verify as this slice's final goal (D145); the recreate is the D12-authorized production mutation (`G-K2`). Behavioural backend proofs on temp DBs only — no production writes (`PG-PR-10`). Secrets: none involved; `docker compose config` FORBIDDEN (`PG-SC-05`). $0 — no metered call on any path (a metered call is a STOP-and-report).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.36.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-DP-02` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03` · `PG-PR-04` · `PG-PR-06` · `PG-PR-10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 60s ordinary, 1200s overall (frontend build + backend suite need it). A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none touched (temp DBs for backend proofs). Restart: exactly ONE recreate (D12-authorized). Deploy: rebuild + recreate + verify, this slice.**

## G0 — establish F-SG105-3 (reporting already-fixed is a successful outcome)

- Read `ProductCardSkeleton.tsx` + the `catalog.test.tsx:144-151` pins against the F-SG105-3 record ("skeleton still 3/4"). If the skeleton is complete and pinned, close F-SG105-3 HERE with the file:line proof and change nothing for it. If a gap remains (a fourth block, a wrong ratio, an unpinned shape), fix it with a fail-then-pass test. Either outcome is success — manufacturing a change is a defect.

## G1 — link contrast F-SG105-4 (decide token vs scoped, then pin)

- Measure `.text-primary` (`tokens.css:119`) against the backgrounds its link instances sit on; decide a token tweak vs scoped per-link treatment and report the measurement that forced the choice. Fail-then-pass: a test asserting the decided contrast treatment on at least the cited instances.

## G2 — widths sweep F-SG105-5 (enumerate on the target, never trust my list)

- Enumerate every route/component with hand-rolled widths vs the shared `PageContainer` (mine found `InboxPage:45`, `ReviewPage:55` — give yours as expectation, report the difference either way) and convert them. Before/after count quoted.

## G3 — pill edge F-SG105-6 (multi-key fixture decides)

- Read `CatalogPage.tsx:75` + `CatalogToolbar.tsx:18`; construct a multi-key `asset_type` population fixture exposing the first-key-wins edge; decide the correct aggregation and pin it fail-then-pass.

## G4 — unresolved rows F-SG108-1 (frontend-only; engine stays untouched)

- `ExpiryPage.tsx:188-197`: rows show a human label (reason text + short-id affordance), `asset_id` stays in the link href, never as the visible text. If no frontend-only label honest exists without engine display names, do NOT widen into the backend — report the follow-up outline instead (shape + files, implemented nowhere here).

## G5 — thumbnail suffix F-SG110-1 (writer + reader move together, `PG-SC-02`)

- Verify `_thumbnail_bytes` emits JPEG, then make `thumbnail_path` (`local_store.py:12`) always carry the JPEG suffix; the reader (`evidence.py:117`) shares the function so both sides move as one — quote both call sites post-change. Enumerate orphaned old-suffix files policy: leave vs migrate, decide and report (leaving needs the reason; migrating needs the bound). Fail-then-pass on temp (HEIC-suffixed source fixture producing a `.jpg` thumb through the real writer).

## G6 — rebuild + exactly ONE recreate + served proof

- Rebuild (frontend build non-cached), exactly ONE recreate (container-id change is the proof; `RestartCount+1` never asserted — M42). Verify: bundle hash differs with a route-path marker for the touched routes, health 6× exact, gate 301/401, alembic head unchanged, all counts delta 0, `/expiry` + catalog-list 200 through the fresh server (`PG-DP-02`: these post-restart HTTP probes are the authority; the full E2E directory sweep is waived, targeted vitest + pytest legs are the named substitutes).
- Containment (`PG-PR-06`): lane `RUN_BUDGET_S` + the 1200s overall bound; actual-versus-budget per leg with units. How the code becomes live is this goal (`PG-PR-04`).

## G7 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-118.log`, `SG-118_report.md`, `SG-118_verify.log` (fail-pre + pass-post raw per fix, widths before/after, served proofs). First token `SG-118`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — `frontend/src` (routes, catalog components, toolbar, theme tokens, tests), `backend/app/storage/local_store.py` + its tests, `docs/worklogs` (3 files). READS — `backend/app/services/evidence_service.py`, `backend/app/api/v1/evidence.py`, suite, daemon (read-only). **Anything else written is a STOP** — compose, `.env` (rule-excluded), migrations, STATE/AGENTS, backend beyond the thumbnail writer.
- Cross-product (`PG-IC-01`): G0–G5 need component/test edits + suite runs + 3 worklog files; G6 needs rebuild + one recreate + HTTP probes. No criterion writes the DB or touches secrets. No criterion demands what the ceiling forbids.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): establish, pin, sweep, serve. No new feature is added here, however small.

## Acceptance criteria

- F-SG105-3 closed with file:line proof, or fixed fail-then-pass; no manufactured change.
- Contrast treatment decided by measurement + pinned; widths before/after quoted; pill edge pinned on a multi-key fixture.
- Unresolved rows human-labelled with asset_id in href only, or a backend follow-up outline (nothing widened silently).
- Thumbs carry the JPEG suffix through the real writer (temp fixture); reader call sites quoted post-change; orphan policy decided.
- Exactly ONE recreate (container-id change); bundle/health/gate/alembic/counts/`/expiry`+catalog 200s as stated.
- $0; no production writes; no writes outside the ceiling; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-118 | Report: docs/worklogs/SG-118_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

60s ordinary · 1200s overall; expected ~1200s (Architect's record; the lane enforces `RUN_BUDGET_S`); $0; actual-versus-budget per leg with units.
