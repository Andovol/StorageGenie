# SG-144 — Pin the README runbook commands with a guard test (F-SG126-3)

**Settings travel on the trigger** (`SG-144 coder=opencode effort=high`, L3 finish chain P1) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** L3 finish-chain slice 3 of 5 (design `docs/superpowers/specs/2026-09-29-roadmap-finish-design.md`, plan `docs/superpowers/plans/2026-09-29-roadmap-finish.md`): `F-SG126-3` is open — no guard pins README runbook command strings (instances: SG-126 doubled-`/_data` drift across 40+ slices, `F-SG131-1` `/_data` doubling). Architect-verified 2026-09-29 on this tree: `README.md:26` (`docker compose up --build -d`), `:33-34` + `:64-65` (alembic + seed exec lines), `:121-136` (backup drill runbook block), `:510-515` (drill + test references); the SG-086 runbook form lives in `backend/scripts/backup_restore_drill.py` with tests in `backend/tests/test_backup_drill.py` (VERIFY both paths on the target — never inherit a path). THIS slice adds the guard and repairs drift ONLY if the strings drifted. **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** GUARD slice. Writes: ONE new guard test file (expected beside `test_backup_drill.py` — verify the directory on the target) + `README.md` surgical repair ONLY if drifted (any other product hunk is a STOP) + `docs/worklogs` (3 files) — and NOTHING else. No rebuild/recreate/restart (no served-behavior change; state the empty backend-diff reason, never silence). No secret in fixtures (`CO-100` — assert it).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). Actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none.**

## G0 — quote the strings + state drifted-or-clean (committed, no edit yet)

- Quote verbatim the README command strings at the expected lines (differenced either way) plus the SG-086 drill invocation form from `backup_restore_drill.py`, and state CLEAN (strings match the runbook form — then no product edit ships and that is a SUCCESS, not a gap) or DRIFTED (quote the drift exactly).
- Commit the capture BEFORE any edit.

## G1 — the guard, seen-to-fail then green (both runs committed — `PG-EV-09`, `PG-EV-01`)

- Add ONE guard test that reads the REAL `README.md` bytes from the tree (`PG-SC-12` — never a copied fixture) and asserts each runbook command string equals the SG-086 form (name the exact set the test pins: compose-up, alembic-upgrade, seed, drill invocation — enumerate on the target and report the set either way).
- Seen-to-fail leg: feed the guard a deliberately-wrong string (e.g. the doubled-`/_data` form) and commit the failing run — a guard never shown failing is decoration. Then green on the real file, committed.
- If G0 was DRIFTED: repair the strings surgically first (minimal hunk, disclosed), then green. If CLEAN: no product hunk — the diff is test + worklogs only.
- Full backend suite green-except-base-proved-reds (reds, if any, stash-reproved on bare BASE); ruff + secret gates quoted.

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-144.log`, `SG-144_report.md`, `SG-144_verify.log` (G0 capture + fail-then-pass captures, suite/lint, diff ceiling proof). First token `SG-144`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the ONE guard test file + `README.md` surgical repair (drift-only) + the 3 worklog files. **Any other write — product code, other tests, config — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs file reads only (120s class); G1 needs the test write + suite (600s class, modify-versus-call: the guard CALLS no service, it reads file bytes); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 600s suite / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): pin the strings, repair drift if present. No runbook rewrite, no drill change, no scheduler — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): pinned — does the guard fail on the mutated string and pass on the real file, both runs committed? true — if drifted, is the repair the minimal disclosed hunk, else is the product diff empty? clean — is the diff exactly test (+ drift repair) + worklogs?
- G0 capture quoted from the commit + fail-then-pass captures + suite/lint greens (or base-proved reds) + $0.000000 USD; no vacuous pass (a guard fed only passing input, a README edit without the guard, or a suite silence read as green evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-144 | Report: docs/worklogs/SG-144_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 2400s overall; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
