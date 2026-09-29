# SG-150 — merge Batch A: CORS lockdown (#42 + rewritten #40, unserved)

**Settings travel on the trigger** (`SG-150 coder=opencode effort=high`, merge-batch arc, owner 2nd word "Approved" 2026-09-29 on D-0929-3 batches A→B→C→D) — this packet carries no settings line; a settings line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** SG-149 audit 98 verdicts: **#42 MERGE** (`allow_methods ["*"]` → `["GET","POST","PUT","PATCH","DELETE","OPTIONS"]`) then **#40 REWRITE** (header allowlist + ADD `If-Match`, rebased over #42 — landing #40 as-is breaks cross-origin PATCH: its list omits `If-Match` while `ItemInspectorDrawer.tsx:135` + `AssetDetailPage.tsx:287` send it). Order is load-bearing (same `main.py`/`test_cors.py` region). Apply the PR heads' real hunks (`refs/pull/42/head`, `refs/pull/40/head`) — reimplementation from memory is not applying (`PG-SC-12`); verify byte-effect equal to the heads. Branch moved since the audit (SG-148 landed): re-verify every hunk applies 3-way at runtime; a hunk that no longer applies is a STOP, never a silent resolve. Served code changes go live via the standing close-out rider — NO rebuild/recreate in this slice (Deploy: none). **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** MERGE slice, unserved. Writes: the ceiling files named below — and NOTHING else. No rebuild/recreate/restart/deploy (liveness proof rides the close-out rider — `PG-PR-04`, stated). No live-DB write (`DATABASE none`). No secret in any capture (`CO-100`).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). Actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite class, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none (close-out rider serves).**

## Why this exists

SG-149 (rated 98) quoted the hunks: #42 replaces the method wildcard with the explicit six-method set (its test asserts the exact set + `TRACE → 400`); #40 replaces the header wildcard with six headers but omits `If-Match`, which the frontend sends on every asset PATCH. CONFIRMED (audit + Architect re-grounding 2026-09-29). INFERRED: landing #42 then #40-with-`If-Match` yields a coherent lockdown with one reconciled CORS test. **The choice turns on: whether both heads still apply 3-way onto this BASE, and what the reconciled test asserts** — establish the former before editing; the latter is yours inside the acceptance below.

Given facts, each re-verified against the current tree before building (`PG-IC-09`): current `main.py` still `allow_methods=["*"], allow_headers=["*"]` (scaffold wildcards) · `test_cors.py` asserts origins only · frontend `If-Match` sends at the two quoted sites · suite 2/636 with 2 known base-reds (`test_signals` env pair) · alembic single head `sg114` (untouched by this slice).

## G0 — apply #42, prove the methods lockdown (`PG-EV-08`, `PG-SC-12`)

- Fetch `refs/pull/42/head`; apply its `main.py` hunk (methods allowlist) + reconcile its `test_cors.py` hunk (exact-set + TRACE-400 assertions). Fail-pre at BASE (wildcard TRACE-200, committed) → pass-post, both committed (`PG-EV-09`).
- STOP conditions: head no longer applies 3-way (report CONFLICT with the hunk quoted — do not rebase silently, do not reimplement from memory); the change needs anything outside the ceiling.

## G1 — rewrite #40 over #42 with `If-Match`

- Fetch `refs/pull/40/head`; apply its header allowlist shape PLUS `If-Match` (seven headers), reconciled with G0's test into ONE coherent CORS test (methods set + headers set incl `If-Match` + TRACE-400). Preflight proof through the real middleware stack (not only config text): a disallowed header/method is refused, `If-Match` passes.
- Online-equivalence rail for the rest of the app: full backend suite delta == the reconciled test only, base-reds identical; frontend suite untouched (no frontend files in ceiling).

## G2 — gates + report (`PG-EV-01`)

- Full backend suite + ruff + mypy-delta + secret scan over the diff. Blast-radius (`PG-IC-08`, a stop condition): expected delta is exactly the reconciled CORS test green with base-reds identical — ANY other delta stops the slice before further writes.

## Constraints

- **Scope ceiling — WRITES:** `backend/app/main.py` · `backend/tests/test_cors.py` · `{{WORKLOG_DIR}}/SG-150.log`, `SG-150_report.md`, `SG-150_verify.log`. **Any other write — including a third file a rebase would need — is a STOP.** Reads: the tree, the two pull-ref heads, the suite. `PG-PR-03` stated.
- Cross-product (`PG-IC-01`): G0 needs the pull-ref fetch + apply (120s class); G1 needs the rewrite + preflight (120s class); G2 needs the suite (600s class) + lint/type/secret gates (120s class). No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): land the pair, reconcile one test; no rider — the close-out deploy serves.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): locked — do TRACE/missing-method and disallowed-header fail while `If-Match` passes, through the real stack? faithful — is the landed effect byte-equal to #42 + (#40 + `If-Match`)? clean — is the diff exactly the ceiling files?
- The world where locked passes yet the outcome is wrong (assertions on config text while the middleware runs stale) is covered by the real-stack preflight; a correct run tripping the blast-radius bound is a STOP with the delta quoted. No vacuous pass (an unrun preflight, a skipped suite, or a test asserting only origins evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-150 | Report: docs/worklogs/SG-150_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. RECOMMENDED-NEXT: Batch B per SG-149 order (#36, folded #39, repathed #34).

## Budget

120s ordinary · 600s suite class · 2400s overall; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
