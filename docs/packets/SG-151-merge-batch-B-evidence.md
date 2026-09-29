# SG-151 — merge Batch B: asset-evidence bulk insert (#36 + folded #39 + repathed #34, unserved)

**Settings travel on the trigger** (`SG-151 coder=opencode effort=high`, merge-batch arc, owner 2nd word "Approved" 2026-09-29 on D-0929-3 batches A→B→C→D) — this packet carries no settings line; a settings line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** SG-149 audit 98 verdicts: **#36 MERGE** (dedup + bulk `asset_evidence` insert in `create_asset`/`attach_evidence`, removing the latent duplicate-key `IntegrityError` the base loop swallows) → **#39 REWRITE** (same `create_asset` region duplicated — DROP it; fold ONLY its unique `candidates.py:_create_asset_for_candidate` bulk hunk) → **#34 REWRITE** (log-on-failure repathed onto the bulk path — its caplog test cannot pass on the old loop once #36 lands). Benchmark scripts are NOT landed (`backend/scripts/benchmark_asset_evidence.py`, `backend/tests/benchmark_asset_evidence_insert.py` — perf one-offs with no gate value; stated exclusion). Apply the PR heads' real hunks (`refs/pull/36/head`, `refs/pull/39/head`, `refs/pull/34/head`) — reimplementation from memory is not applying (`PG-SC-12`); verify byte-effect. Branch moved since the audit: re-verify every hunk applies 3-way at runtime; a hunk that no longer applies is a STOP, never a silent resolve. Served code changes go live via the standing close-out rider — NO rebuild/recreate in this slice (Deploy: none). **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** MERGE slice, unserved. Writes: the ceiling files named below — and NOTHING else. No rebuild/recreate/restart/deploy (liveness proof rides the close-out rider — `PG-PR-04`, stated). No live-DB write (`DATABASE none`; temp SQLite per standing). No secret in any capture (`CO-100`).
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

SG-149 (rated 98) quoted the regions: #36's dedup (`dict.fromkeys`) + bulk `asset_evidence.insert()` + pre-read of existing links in `create_asset`/`attach_evidence` (`asset_service.py`); #39's duplicate of that region plus its unique `_create_asset_for_candidate` bulk hunk (`candidates.py`); #34's `logger.warning("Failed to attach evidence_id=…")` inside the loop #36 deletes. CONFIRMED (audit + evidence table). INFERRED: landing #36, folding only #39's candidates hunk, and repathing #34's logging onto the bulk insert yields the N+1 fix with failure visibility. **The choice turns on: whether all three heads still apply 3-way onto this BASE, and what the reconciled failure-visibility test asserts** — establish the former before editing; the latter is yours inside the acceptance below.

Given facts, each re-verified against the current tree before building (`PG-IC-09`): base `create_asset`/`attach_evidence` still per-item loop with swallowed failures · `attach_evidence` has ZERO test references (SG-149 grep) · suite 2/637 with 2 known base-reds (`test_signals` env pair, SG-150) · SQLAlchemy 2.0.52 (`Session.scalars`/`select` available) · alembic single head `sg114` (untouched by this slice).

## G0 — land #36 by its real hunks, prove the bulk path (`PG-EV-08`, `PG-SC-12`)

- Fetch `refs/pull/36/head`; apply its `asset_service.py` hunks (dedup + bulk insert + pre-read); blob-identity proof for each applied hunk (landed blob == head blob). Fail-pre at BASE committed: duplicate evidence attach leaves duplicates-or-swallow (quote the behavior); pass-post: one row per link, no `IntegrityError`. Both runs committed (`PG-EV-09`).
- STOP conditions: head no longer applies 3-way (report CONFLICT quoted — no silent resolve, no memory reimplementation); the change needs anything outside the ceiling.

## G1 — fold #39's candidates hunk, repath #34's logging

- Fetch `refs/pull/39/head`; land ONLY its `candidates.py:_create_asset_for_candidate` bulk hunk (drop its duplicate `create_asset` region + its benchmark script — stated exclusions). Fetch `refs/pull/34/head`; repath its failure logging onto the bulk path so a failed attach logs `evidence_id` + `asset_id` (adapt its caplog test to the bulk path — the old-loop assertion cannot pass and must not be bent to).
- One reconciled failure-visibility test through the real service (duplicate/failed attach → single row + warning logged); it must fail at BASE and pass after (no vacuous `xfail`, no mock of the path under test).

## G2 — gates (`PG-EV-01`)

- Targeted (`test_assets_crud`, `test_candidates*`) + FULL backend suite + ruff + mypy-delta + secret scan over the diff. Blast-radius (`PG-IC-08`, a stop condition): expected delta is exactly the reconciled test(s) green with base-reds identical — ANY other delta stops the slice before further writes.

## Constraints

- **Scope ceiling — WRITES:** `backend/app/services/asset_service.py` · `backend/app/services/candidates.py` (the one folded hunk only — a second hunk is a STOP) · reconciled test changes inside existing `backend/tests/test_*.py` (ONE new test file only if no existing file fits — state which) · `{{WORKLOG_DIR}}/SG-151.log`, `SG-151_report.md`, `SG-151_verify.log`. Benchmark scripts are NOT landed (stated exclusion). **Any other write is a STOP.** Reads: the tree, the three pull-ref heads, the suite. `PG-PR-03` stated.
- Cross-product (`PG-IC-01`): G0 needs pull-ref fetch + apply (120s class); G1 needs fold + repath (120s class); G2 needs targeted + full suite (600s class) + lint/type/secret gates (120s class). No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): land the pair, fold one hunk, repath one log line; no rider — the close-out deploy serves.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): bulked — is the N+1 loop gone on both paths (quote the landed code)? visible — does a failed attach log with both IDs through the real service? faithful — is the landed effect byte-equal to #36 + (#39 candidates hunk) + (repathed #34 log)? clean — is the diff exactly the ceiling files?
- A correct run tripping the blast-radius bound is a STOP with the delta quoted, not a bent gate. No vacuous pass (an unrun service call, a skipped suite, or a mock of the bulk path evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-151 | Report: docs/worklogs/SG-151_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. RECOMMENDED-NEXT: Batch C per SG-149 order (#33 + folded #37).

## Budget

120s ordinary · 600s suite class · 2400s overall; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
