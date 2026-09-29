# SG-142 — Fix the cap-join so None-job ledger rows count toward monthly spend

**Settings travel on the trigger** (`SG-142 coder=opencode effort=high`, L3 finish chain P1) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** L3 finish-chain slice 1 of 5 (design `docs/superpowers/specs/2026-09-29-roadmap-finish-design.md`, plan `docs/superpowers/plans/2026-09-29-roadmap-finish.md`): `F-SG132-5` carried that `_recorded_spend` inner-joins `Job` and ignores `None`-job rows — the live cap sees 0.0067 vs 0.0104 true. Architect-verified 2026-09-29 on this tree: `backend/app/services/providers/reader.py:270-288` sums `ProviderCall.cost` through `.join(Job, ProviderCall.job_id == Job.id)` filtered by `Job.household_id` and current-month start; a row with `job_id NULL` can never satisfy the join. WRITE path read same day: `backend/app/services/enrich/snapshots.py:99-144` `record_jina_search_call` stamps `job_id=job.id` on every new Jina row — so joined rows are post-SG-132 Jina rows and NULL-job rows are older/other-writer rows. Consumers (grep-sourced, VERIFY — never inherited): `backend/app/api/v1/enrich.py:93` gate read + `reader.py:471-477` cap refusal. THIS slice decides the correct semantics, fixes the reader, and serves it. **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** FIX slice. Writes: `reader.py` (the spend-reader ONLY — any other product hunk is a STOP), backend tests pinning the decided semantics, `docs/worklogs` (3 files) — and NOTHING else. No migration (query-only change; if you find a migration is needed, STOP — `PG-PR-05` interim is NOT authorized here). Served code changes so this slice owns its refresh per D145: rebuild + exactly ONE recreate + verify (production restart, carried by the L3 stage approval + D145 standing). No secret in fixtures (`CO-100` — assert it).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). `PG-PR-06` stated upfront; actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-06` · `PG-EV-08` · `PG-EV-09` · `PG-SC-01` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06` · `PG-PR-10`.

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

**DATABASE: none (temp SQLite only). Restart: exactly one recreate of the served stack (D145 owned refresh). Deploy: rebuild + one recreate + verify, this slice.**

## G0 — reproduce the miscount on BASE (fail-pre, committed — `PG-EV-09`)

- On the unmodified tree, seed ONE `provider_call` row with `job_id NULL` and cost `0.003700` plus ONE joined current-month row with cost `0.006700` for the same household shape, then quote `_recorded_spend` returning the joined-only figure (expectation: `0.006700`, the NULL row invisible — differenced either way; if the NULL row IS counted, the premise is falsified and that is a finding, not a failure).
- The load-bearing fact this turns on (say it back before deciding): `household_id` is reachable ONLY through `Job`, so a NULL-job row carries no household — the fix's semantics (attribute, pool, or exclude-and-disclose) depend on what those rows ARE in this tree (which writers leave `job_id NULL`: enumerate them). Decide and report; a delegated guess ships a defect.
- Commit the capture BEFORE any edit — a fix without a committed red proves nothing.
- `PG-IC-08` blast radius: the ONLY permitted figure movement is households owning NULL-job rows; a household with all-joined rows must read byte-identical before/after (name that no-change case). Any movement anywhere else stops the run (report, don't fix around it).

## G1 — fix the reader + prove it (fail-post, both runs committed)

- Fix `_recorded_spend` to the decided semantics (expected shape: NULL-job rows counted without inventing a household they do not carry — e.g. a household-scoped pool or an explicitly-disclosed exclusion; NEVER attribute a NULL-job row to a household by guessing).
- Fail-post through the REAL reader (`PG-SC-12`): the G0 seed now reads the decided-correct total; the no-change case reads identical; existing `test_sg132_jina_ledger_wiring.py` + `test_sg125_ledger_retention.py` green UNCHANGED (if either needs editing to stay green, that edit is itself a finding — justify it line by line or STOP). Full backend suite green-except-base-proved-reds (reds, if any, stash-reproved on bare BASE); ruff + mypy-delta + secret gates quoted. Both runs committed to the verification log.
- No-change files proof: `git diff --stat` shows ONLY `reader.py` + tests + worklogs.

## G2 — serve it: rebuild + exactly ONE recreate + verify (`PG-PR-04`, `PG-EV-08`)

- BEFORE the recreate, capture the live month figure through the served read path (read-only) and quote it — a served claim without a BEFORE capture evidences nothing.
- Rebuild, exactly ONE recreate (container-id change is the proof, never RestartCount), health ×6 exact, gate 301/401, alembic head unmoved, table counts delta exactly zero (no live rows created — `PG-EV-06`: this slice creates NO live rows; a live press is NOT authorized here).
- AFTER capture through the same read path: quote the figure and its delta vs BEFORE (expectation: moves only if live NULL-job rows exist for the read household — differenced either way, explained always).

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-142.log`, `SG-142_report.md`, `SG-142_verify.log` (fail-pre + fail-post captures, suite/lint/mypy, BEFORE/AFTER served captures, diff ceiling proof). First token `SG-142`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — `reader.py` spend-reader + backend tests + the 3 worklog files. **Any other write — migration, API route, writer, frontend — is a STOP.** Reads: the tree, temp-DB runs, served read-only captures, one image rebuild + one recreate (D145). Pulling/running the service image for the owned refresh counts as authorized execution, not a read excess.
- Cross-product (`PG-IC-01`): G0 needs temp-DB seeding + reader calls (120s class); G1 needs the edit + full suite (600s class); G2 needs rebuild + recreate + served captures (recreate is the authorized production restart — `PG-PR-03` stated: a denial stops the slice, never routes around); G3 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 600s suite / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- `PG-PR-10`: no live-production write is asked for anywhere in this packet — resolution is scoped to temp DB + served reads; the recreate is the only production mutation and rides D145 + the L3 stage approval.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): correct the join, prove the figure, serve it. No ledger redesign, no backfill, no cap-value change — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): miscount — was the NULL-job invisibility captured pre-edit on BASE? fixed — does the REAL reader return the decided-correct total with the no-change case identical and both ledger test files green? served — is the new code live (container-id change) with BEFORE/AFTER figures quoted and counts delta zero? clean — is the diff exactly reader + tests + worklogs?
- Fail-pre capture quoted from the commit + fail-post figure quoted + suite/lint/mypy greens quoted (or base-proved reds) + BEFORE/AFTER served captures + $0.000000 USD; no vacuous pass (a figure without the seed, a suite silence read as green, or a migration smuggled in evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-142 | Report: docs/worklogs/SG-142_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 2400s overall; expected ~900s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
