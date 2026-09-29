# SG-147 — offline `--sql` end-to-end fix (sg048 in ceiling, unserved)

**Settings travel on the trigger** (`SG-147 coder=opencode effort=high`, L3 finish chain P1, owner word "D1 - D2 both ok" 2026-09-29 for the SG-147 re-packet) — this packet carries no settings line; a settings line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** SG-146 BLOCKED-correct 98 (`docs/worklogs/SG-146_report.md`): the within-ceiling sg017 + `fts.py` helper split landed (`1488438`) and is online-identical, but end-to-end offline fails at `20260916_sg048_name_optional.py` — its `_drop_fts` calls online-only `connection.exec_driver_sql` (:36-40) and its `op.batch_alter_table("asset")` (:55, :73) cannot render offline without `copy_from` (quoted `CommandError` in `SG-146_verify.log:112`). This slice answers SG-146 REMAINING (a)+(b) and fixes the packet defects F-SG146-1/2/3/5. **Size M** (structural batch change — explicitly NOT size S). **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
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

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one. ("Before" for every fail-then-pass here means this BASE, which already contains the SG-146 partial fix — the remaining failure is sg048.)

**DATABASE: none (offline SQL generation + temp-DB suite only). Restart: none. Deploy: none.**

## Why this exists

SG-146's drives, quoted: post-fix `upgrade head --sql` advances past sg017 (FTS DDL emits: `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts USING fts5(`) then aborts at sg048 with `CommandError: … batch mode with dialect sqlite requires a live database connection … "copy_from" …`. CONFIRMED (committed log). INFERRED: `_drop_fts`/`_reinstall_fts` through `op.execute` in offline mode plus `copy_from=` on the batch alters renders end-to-end. **The choice turns on two facts: whether `copy_from`-equipped batch renders identical DDL online and offline, and whether the online migrated schema stays byte-identical** — establish both before choosing; silence on either fails, not ignorance.

Given facts, each re-verified against the current tree before building (`PG-IC-09`): sg048 `_drop_fts` `exec_driver_sql` at :36-40 + `batch_alter_table("asset")` at :55/:73 (workstation grep 2026-09-29) · sg017 offline branch + `fts.py:ddl_statements()` landed in `1488438` (verify present, do not revert; extend only if the shape demands) · emitted DDL text is `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts` (assert THIS literal — F-SG146-3) · alembic single head `sg114` · suite 2/635 with 2 known base-reds (`test_signals` env pair, SG-146 verify log).

## G0 — fail-pre at BASE (`PG-EV-08`, `PG-SC-12`)

- Run the REAL CLI from `backend/venv` — `alembic upgrade head --sql`, stdout+stderr to the verify log (300s class). Expected: exit 1 aborting at sg048 (the `copy_from` CommandError). BOTH runs (fail-pre here, pass-post in G2) committed (`PG-EV-09`).
- STOP conditions (stopping is a SUCCESS): exit is already 0 at BASE (report FIXED-ELSEWHERE with output quoted — do not manufacture a change); observing it needs a live-DB write (report UNOBSERVABLE, never execute). What does NOT count as grounds to stop: an unfamiliar migration layout.

## G1 — sg048 offline-safe, online byte-identical (`PG-SC-01`)

- Read the WRITE path (sg048 in full, `fts.py` helper, sg017 offline branch) and the READ path (`env.py` offline branch) FIRST.
- Make `_drop_fts`/`_reinstall_fts` offline-safe: DROP statements via `op.execute` in offline mode (analogous to the sg017 helper), rebuild/backfill gated online-only; give the `batch_alter_table` calls `copy_from` (or restructure the alter for offline — decide and report, with the render proof).
- Symmetry candidate (F-SG146-5, decide and report): sg017 `downgrade()` and sg048's own downgrade path — make offline-safe in the same shape or state why not.
- Online-equivalence rail: existing migration tests (notably `test_sg048_name_optional.py`) + full backend suite show NO delta versus BASE except the new test (2 known base-reds stash-reproved both sides); `alembic heads` single `sg114` before == after (no new revision — `PG-SC-11`: grep every end-relative assertion over the migration chain and list the hits).

## G2 — end-to-end offline test + gates (`PG-EV-01`, `CO-101`)

- New test in `backend/tests/` named for what it proves: `upgrade head --sql` exits 0 AND stdout contains `CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts` + the 3 `asset_fts_after_*` triggers + all 7 post-FTS revision markers (non-vacuity: an early-prefix-only output FAILS).
- Seen-to-fail against BASE (G0 capture, exit 1); seen-to-pass post-fix. Gate reports which files it checked; a gateless PASS is a FAIL.
- Run the FULL backend suite + ruff + mypy-delta + secret scan. Blast-radius (`PG-IC-08`, a stop condition): expected delta is exactly +1 green file with base-reds identical — ANY other delta stops the slice before further writes.

## Constraints

- **Scope ceiling — WRITES:** `backend/alembic/versions/20260916_sg048_name_optional.py` · `backend/alembic/versions/20260908_sg017_fts.py` (only if the landed shape needs adjustment, else byte-identical — state which) · `backend/app/services/fts.py` (only if the helper needs extension, else byte-identical — state which) · ONE new `backend/tests/test_sg147_*.py` · `{{WORKLOG_DIR}}/SG-147.log`, `SG-147_report.md`, `SG-147_verify.log`. **Any other write is a STOP.** Reads: the tree, the venv, offline CLI runs, the temp-DB suite. `PG-PR-03` stated: a denied probe stops that leg, never routes around.
- Cross-product (`PG-IC-01`): G0 needs the offline CLI drive (300s class); G1 needs the code edit (no per-command bound beyond overall); G2 needs the suite (600s class) + lint/type/secret gates (120s class). No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): extend the proven SG-146 shape, nothing else; no rider — unserved by construction.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): fixed — does `upgrade head --sql` exit 0 with the `IF NOT EXISTS` FTS DDL plus all 7 post-FTS markers? equivalent — is the online schema byte-identical (suite delta == +1 file, base-reds identical, heads unchanged)? clean — is the diff exactly the ceiling files?
- The world where fixed passes yet the outcome is wrong (markers present, online schema silently changed) is covered by equivalent; the world where the feature working fails a criterion (a correct run tripping the blast-radius bound) is a STOP with the delta quoted, not a bent gate. No vacuous pass (an unrun drive, a skipped suite, or a marker-grep scoped to pass evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-147 | Report: docs/worklogs/SG-147_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. RECOMMENDED-NEXT: chain position (PR-pile triage per owner word, hue verdict, close-out deploy per `docs/superpowers/plans/2026-09-29-roadmap-finish.md`).

## Budget

120s ordinary · 600s suite class · 2400s overall; expected ~900s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
