# SG-148 — offline `--sql`: four `_has_table` guards (unserved)

**Settings travel on the trigger** (`SG-148 coder=opencode effort=high`, L3 finish chain, word D-0929-1, runs AFTER the pile audit per the approved order) — this packet carries no settings line; a settings line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** SG-147 BLOCKED-correct 98 (`docs/worklogs/SG-147_report.md`): sg017 + `fts.py` + sg048 are landed and online-identical; the remaining end-to-end blockers are four identical idempotency guards — `20260917_sg068_saved_search.py:20-21`, `20260923_sg100_enrich_snapshot.py:20-21`, `20260924_sg113_location.py:20-21`, `20260924_sg114_relation.py:21` — each `sa.inspect(op.get_bind()).has_table(name)`, which raises `NoInspectionAvailable` under `MockConnection` (quoted in `SG-147_verify.log:21-22`). Idiomatic fix per R1: skip the guard when `op.get_context().as_sql` (in `--sql` mode there is no DB, so the idempotency check is meaningless — render unconditionally). **Size S.** **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** FIX slice, unserved. Writes: the ceiling files named below — and NOTHING else. No rebuild/recreate/restart/deploy. No live-DB write (`DATABASE none`; the suite uses temp SQLite per standing). No secret in any capture (`CO-100`).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). Actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-01` · `PG-SC-09` · `PG-SC-11` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-03`.

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

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one. ("Before" for every fail-then-pass here means this BASE, which already contains the SG-145→147 partial fixes — the remaining failure is the four guards.)

**DATABASE: none (offline SQL generation + temp-DB suite only). Restart: none. Deploy: none.**

## Why this exists

SG-147's re-drive, quoted: post-sg048 `upgrade head --sql` aborts at `sg068:21` with `NoInspectionAvailable: No inspection system is available for object of type MockConnection`; 3 of 7 post-FTS markers emit. CONFIRMED (committed log). INFERRED: skipping the no-DB idempotency guard in `as_sql` mode renders all four revisions. **The choice turns on one fact: whether the guarded statement is safe to render unconditionally offline** — the guard exists for hand-created DBs; offline has no DB. Establish per file before choosing; silence fails, not ignorance.

Given facts, each re-verified against the current tree before building (`PG-IC-09`): the four guards at the paths above, one idiom (workstation grep 2026-09-29) · sg017 + `fts.py` + sg048 landed (verify present, do not revert) · emitted literal is `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts` (assert THIS) · alembic single head `sg114` · suite 2/635 with 2 known base-reds (`test_signals` env pair).

## G0 — fail-pre at BASE (`PG-EV-08`, `PG-SC-12`)

- Run the REAL CLI from `backend/venv` — `alembic upgrade head --sql`, stdout+stderr to the verify log (300s class). Expected: exit 1 aborting at sg068 (`NoInspectionAvailable`). BOTH runs (fail-pre here, pass-post in G2) committed (`PG-EV-09`).
- STOP conditions (stopping is a SUCCESS): exit is already 0 at BASE (report FIXED-ELSEWHERE with output quoted — do not manufacture a change); observing it needs a live-DB write (report UNOBSERVABLE, never execute). What does NOT count as grounds to stop: an unfamiliar migration layout.

## G1 — four guards offline-safe, online byte-identical (`PG-SC-01`)

- Read all four migration files in full FIRST (they share one idiom — confirm it, do not assume it).
- Skip each `_has_table` early-return when `op.get_context().as_sql` (offline renders unconditionally; online keeps the idempotency guard byte-for-byte).
- Online-equivalence rail: related migration tests + full backend suite show NO delta versus BASE except the new test (2 known base-reds stash-reproved both sides); `alembic heads` single `sg114` before == after (no new revision — `PG-SC-11`: grep every end-relative assertion over the migration chain and list the hits).

## G2 — end-to-end offline test + gates (`PG-EV-01`, `CO-101`)

- New test in `backend/tests/` named for what it proves: `upgrade head --sql` exits 0 AND stdout contains `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts` + the 3 `asset_fts_after_*` triggers + all 7 post-FTS revision markers (non-vacuity: an early-prefix-only output FAILS).
- Seen-to-fail against BASE (G0 capture, exit 1); seen-to-pass post-fix. Gate reports which files it checked; a gateless PASS is a FAIL.
- Run the FULL backend suite + ruff + mypy-delta + secret scan. Blast-radius (`PG-IC-08`, a stop condition): expected delta is exactly +1 green file with base-reds identical — ANY other delta stops the slice before further writes.

## Constraints

- **Scope ceiling — WRITES:** the four guard migration files (`20260917_sg068_saved_search.py`, `20260923_sg100_enrich_snapshot.py`, `20260924_sg113_location.py`, `20260924_sg114_relation.py`) · ONE new `backend/tests/test_sg148_*.py` · `{{WORKLOG_DIR}}/SG-148.log`, `SG-148_report.md`, `SG-148_verify.log`. sg017/`fts.py`/sg048 byte-identical unless the shape demands otherwise — state which. **Any other write is a STOP.** Reads: the tree, the venv, offline CLI runs, the temp-DB suite. `PG-PR-03` stated: a denied probe stops that leg, never routes around.
- Cross-product (`PG-IC-01`): G0 needs the offline CLI drive (300s class); G1 needs the code edit (no per-command bound beyond overall); G2 needs the suite (600s class) + lint/type/secret gates (120s class). No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): one idiom, four files, one test; no rider — unserved by construction.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): fixed — does `upgrade head --sql` exit 0 with the `IF NOT EXISTS` FTS DDL plus all 7 post-FTS markers? equivalent — is the online schema byte-identical (suite delta == +1 file, base-reds identical, heads unchanged)? clean — is the diff exactly the ceiling files?
- The world where fixed passes yet the outcome is wrong (markers present, online schema silently changed) is covered by equivalent; the world where the feature working fails a criterion (a correct run tripping the blast-radius bound) is a STOP with the delta quoted, not a bent gate. No vacuous pass (an unrun drive, a skipped suite, or a marker-grep scoped to pass evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-148 | Report: docs/worklogs/SG-148_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. RECOMMENDED-NEXT: chain position (merge batch per SG-149 verdicts on its second word, hue verdict, close-out deploy per `docs/superpowers/plans/2026-09-29-roadmap-finish.md`).

## Budget

120s ordinary · 600s suite class · 2400s overall; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
