# SG-153 — merge Batch D: independents (#32 + #35 + #38 + #41, unserved)

**Settings travel on the trigger** (`SG-153 coder=opencode effort=high`, merge-batch arc, owner 2nd word "Approved" 2026-09-29 on D-0929-3 batches A→B→C→D) — this packet carries no settings line; a settings line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** SG-149 audit 98 verdicts, all MERGE, mutually independent (verified no line-conflict in the overlap matrix): **#32** expiry-engine batch map (+ `.jules/bolt.md` journal line; tie-break caveat → run `test_sg107_expiry_engine.py`) · **#35** pure `__all__` reorder (prove set-equal, nothing added/dropped) · **#38** behavior-preserving synthesis logging + its real-path test · **#41** loser-candidates batch fetch (land AFTER #39's candidates change — SG-151 moved that file: re-verify 3-way applies). Apply the four heads' real hunks (`refs/pull/32,35,38,41/head`) — reimplementation from memory is not applying (`PG-SC-12`); blob-identity proof per applied hunk. Branch moved since the audit: re-verify every hunk applies 3-way at runtime; a hunk that no longer applies is a STOP, never a silent resolve. Served code changes go live via the standing close-out rider — NO rebuild/recreate in this slice (Deploy: none). **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** MERGE slice, unserved. Writes: ONLY files touched by the four PR diffs (enumerated at runtime from the diffs and quoted — any touched file outside those four diffs is a STOP) + `{{WORKLOG_DIR}}` (3 files). No other write. No live-DB write (`DATABASE none`). No secret in any capture (`CO-100`).
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

SG-149 (rated 98) quoted all four: #32's batch map over `Assertion` with first-wins maps (journal line included); #35's set-equal reorder; #38's two `logger.debug` lines preserving the terminal `SynthesisFormatError` + a test asserting both messages; #41's `loser_map` batch with identical 404/403/409 checks in order. CONFIRMED (audit + Architect spot-checks 2026-09-29). INFERRED: the four land independently in any order. **The ordering turns on one fact: whether #41 still applies 3-way after SG-151's candidates.py change** — check this FIRST; if it conflicts, land #32/#35/#38 and STOP with the #41 conflict quoted (partial landing beats a forced merge).

Given facts, each re-verified against the current tree before building (`PG-IC-09`): suite 2/648 with 2 known base-reds (`test_signals` env pair, SG-152) · `test_sg107_expiry_engine.py` exists (tie-break caveat leg) · #38's `_extract_json` + `SynthesisFormatError` at `synthesize.py:192` · alembic single head `sg114` (untouched by this slice).

## G0 — land #32 + #35, prove semantics preserved (`PG-EV-08`, `PG-SC-12`)

- Fetch both heads; apply by real hunks with blob-identity proofs. #32: batch map equals per-asset semantics (run `test_sg107_expiry_engine.py` + quote the tie-break behavior); journal line lands with the diff. #35: BASE vs landed `__all__` are the same SET (prove by set-compare, not eyeball).
- Fail-pre/post committed (`PG-EV-09`): #32's expiry assertions red-then-green on the batch shape (or the suite leg that discriminates, stated); #35 needs no behavior gate beyond set-equality + import.

## G1 — land #38 + #41 by their real hunks

- #38: logging + its test (asserts BOTH debug messages through the real `_extract_json("invalid json {also invalid}")`, ending in `SynthesisFormatError` — a test asserting only the terminal error is a placebo: say it drives the changed lines).
- #41: batch fetch with identical check order; prove the per-id checks (404/403/409 + blocking-task count) run in the same order on the same values. If SG-151's candidates change blocks 3-way apply → land the other three and STOP with the conflict quoted (stated partial success, not failure).

## G2 — gates (`PG-EV-01`)

- Affected suites (`test_sg107_expiry_engine`, asset/candidate/synthesis legs per the derived set) + FULL backend suite + ruff + mypy-delta + secret scan over the diff. Blast-radius (`PG-IC-08`, a stop condition): expected delta is exactly the landed tests green with base-reds identical — ANY other delta stops the slice before further writes.

## Constraints

- **Scope ceiling — WRITES:** ONLY files appearing in the four PR diffs (enumerate at runtime, quote the list — a fifth file is a STOP) · `{{WORKLOG_DIR}}/SG-153.log`, `SG-153_report.md`, `SG-153_verify.log`. **Any other write is a STOP.** Reads: the tree, the four pull-ref heads, the suite. `PG-PR-03` stated.
- Cross-product (`PG-IC-01`): G0/G1 need pull-ref fetch + apply (120s class); G2 needs affected + full suite (600s class) + lint/type/secret gates (120s class). No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): four independent landings, one slice; no rider — the close-out deploy serves.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): landed — is each landed hunk blob-identical to its head (or STOP-quoted)? equal — do the batch maps preserve per-item semantics (tie-break quoted) and the check order? clean — is the diff exactly the four PRs' files?
- A correct run tripping the blast-radius bound is a STOP with the delta quoted. No vacuous pass (a reimplementation from memory, an origin-only test, or a skipped suite evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-153 | Report: docs/worklogs/SG-153_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. RECOMMENDED-NEXT: close-out deploy rider (standing directive) then hue screenshots verdict.

## Budget

120s ordinary · 600s suite class · 2400s overall; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
