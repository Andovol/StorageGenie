# SG-152 — merge Batch C: schemas-common tests (#33 + folded #37, test-only)

**Settings travel on the trigger** (`SG-152 coder=opencode effort=high`, merge-batch arc, owner 2nd word "Approved" 2026-09-29 on D-0929-3 batches A→B→C→D) — this packet carries no settings line; a settings line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** SG-149 audit 98 verdicts: **#33 MERGE** (new `backend/tests/test_schemas_common.py` covering `decode_cursor`/`encode_cursor`/`loads_json`/`dumps_json`/`ProblemDetail` — existing coverage EMPTY, Architect-verified 2026-09-29) → **#37 REWRITE** (same new path, add/add conflict — fold ONLY its unique cases: `loads_json` list/int/bool, unicode `dumps_json`; DROP the duplicate file). Single adopted file, no duplicate. Apply the PR heads' real test hunks (`refs/pull/33/head`, `refs/pull/37/head`) — rewritten-from-memory assertions are not applying (`PG-SC-12`); verify each assertion against the real `app/schemas/common.py` branches (spec `f"{id}:{created_at.isoformat()}"` + legacy `ts|id`). Branch moved since the audit: verify the path is still absent and no conflicting file landed; a present conflicting file is a STOP, never an overwrite. Test-only slice: NO served-code change, no live proof owed. **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** MERGE slice, test-only. Writes: the ONE new test file + `{{WORKLOG_DIR}}` (3 files) — and NOTHING else. No product/config change however trivial. No secret in any capture (`CO-100`).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). Actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-03`.

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

**DATABASE: none (temp-DB suite only). Restart: none. Deploy: none.**

## Why this exists

SG-149 (rated 98) established: zero test references to `decode_cursor`/`loads_json`; #33's file asserts the real branches; #37's file collides on the exact path but carries unique list/int/bool + unicode cases. CONFIRMED (audit + Architect grep 2026-09-29). INFERRED: one union file gives the coverage with no duplication. **The union turns on: which cases are unique to #37 vs duplicated** — enumerate both heads' case lists before merging; a case dropped silently is a finding, never an edit.

Given facts, each re-verified against the current tree before building (`PG-IC-09`): `test_schemas_common.py` absent at BASE · `common.py:15-36` carries both cursor branches · suite 2/638 with 2 known base-reds (`test_signals` env pair, SG-151) · alembic single head `sg114` (untouched by this slice).

## G0 — absence proof at BASE (`PG-EV-08`)

- Prove the coverage gap at BASE: `ls` the path (absent) + grep `decode_cursor|loads_json` over `backend/tests/` (empty) — committed to the verify log. This absence IS the fail-pre (there is no red run for unborn coverage); the non-vacuity obligation moves to G1: every assertion must name a real implementation branch.
- STOP conditions: the path exists at BASE with real content (report SUPERSEDED with the file quoted — do not overwrite, do not duplicate); observing the gap needs anything beyond reads (report UNOBSERVABLE, never execute).

## G1 — union file from the real heads (`PG-SC-12`)

- Fetch `refs/pull/33/head` + `refs/pull/37/head`; land #33's file by its real hunks (blob-identity proof), then fold #37's UNIQUE cases only (list every case from both heads; mark each kept/folded/dropped-duplicate).
- Every assertion must exercise a real `common.py` branch (spec + legacy cursor, `loads_json` types incl list/int/bool, unicode `dumps_json`, `ProblemDetail`) — a passing assertion true of a stub is a placebo test (AUDIT §4 family): say which branch each case pins.

## G2 — gates (`PG-EV-01`)

- New file fully + FULL backend suite + ruff + mypy-delta + secret scan over the diff. Blast-radius (`PG-IC-08`, a stop condition): expected delta is exactly +1 green file with base-reds identical — ANY other delta stops the slice before further writes.

## Constraints

- **Scope ceiling — WRITES:** ONE new `backend/tests/test_schemas_common.py` · `{{WORKLOG_DIR}}/SG-152.log`, `SG-152_report.md`, `SG-152_verify.log`. **Any product file, second test file, or overwrite of an existing file is a STOP.** Reads: the tree, the two pull-ref heads, the suite. `PG-PR-03` stated.
- Cross-product (`PG-IC-01`): G0 needs absence proof (120s class); G1 needs the union (120s class); G2 needs file + full suite (600s class) + lint/type/secret gates (120s class). No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): one file, two heads' cases, no product touch.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): covered — does every `common.py` branch under test have a case that fails if the branch breaks (mutation-stated, not merely asserted)? united — is every unique #37 case present with no duplicated file? clean — is the diff exactly the ceiling files?
- A correct run tripping the blast-radius bound is a STOP with the delta quoted. No vacuous pass (an assertion true of a stub, a dropped #37 case unreported, or a skipped suite evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-152 | Report: docs/worklogs/SG-152_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. RECOMMENDED-NEXT: Batch D per SG-149 order (#32, #35, #38, #41).

## Budget

120s ordinary · 600s suite class · 2400s overall; expected ~300s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
