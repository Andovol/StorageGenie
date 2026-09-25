# SG-125 — Ledger retention instrument: month-boxed spend + purge vehicle (temp-proven, live NOT run)

**Settings travel on the trigger** (`SG-125 coder=opencode effort=high`, D17 L3 stage) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.37.0).

**Context and standing lines.** D17-approved slice (fourth of the L3 residual-completion stage; SG-124 price-foundation 98). D17's "ledger retention" has NO code today (Architect grep 2026-09-25 over `backend/app` for `retention|purge|prune`: zero hits — SG-089 deferred it to the production-datastore slice, and this is that slice). The load-bearing interaction, read by the Architect (`PG-SC-01` — write path + read path, stated not solved): WRITE — `_write_ledger` (`reader.py:200-222`, plus chat/planning/analytics mirrors) appends one `provider_call` row per call, unbounded, `created_at` via `TimestampMixin` (`models/base.py:21-22`); READ — `_recorded_spend` (`reader.py:237-251`) sums **all-time** per household with **no month filter**, yet the cap it feeds is named monthly (`sg_monthly_cap`, "estimated monthly cost", `:405-416`). Consequence: a purge that deletes old rows silently LOOSENS the cap (fail-open) unless the query is month-boxed first — so this slice does BOTH, in that order. THIS slice ships the instrument and proves it on a TEMP database; the LIVE purge is OUT (takes its own owner word — the exact production command is recorded below, never run). Verdicts: INSTRUMENTED (spend month-boxed with proof, purge vehicle temp-proven, suite holds) / BLOCKED (a premise below falsified — commit, receipt, clean tree). **No live leg, no rebuild, no recreate** — the spend-query change alters served behavior only when a later rider serves it (`PG-PR-05`: the interim is named below, not production). **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.37.0` == published (`1acd773`, D15 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** offline + temp-DB ONLY. No live database touch of any kind (the live purge command is recorded, never run — running it is a STOP). Writes: the spend-query change, the purge vehicle + constant, tests, `docs/worklogs` (3 files) — and NOTHING else. No migration (no model change — prove by empty diff over `models/`+`alembic/`), no endpoint, no scheduler (none exists — a scheduled purger is OUT, stated), no sender. $0 — scripted transports only; a metered call is a STOP-and-report.
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path. `PG-PR-07` success-delta, stated upfront: after this slice's code ships, caps bind the calendar month as named (previously lifetime-tightening); a household with old spend becomes able to spend again up to the monthly cap — that loosening is the documented correction, not a side effect.
**Guards invoked (0.37.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-01` · `PG-SC-07` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-05` · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: temp-only (fresh SQLite in a scratch dir, removed after — SG-086/SG-111 precedent). Production: reads NEVER, writes NEVER.** The live purge command is recorded below word-for-word and never executed. **Restart: none. Deploy: none. Container actions: none.**

## G0 — read paths before drafting the change (`PG-SC-01`, reads only — stated, not solved)

- Re-read `_recorded_spend` (`reader.py:237-251`) + its call site (`:405-416`) + `_write_ledger` (`:200-222`) + `TimestampMixin.created_at` (`models/base.py:21-22`) + `ProviderCall` columns. Confirm or correct: no month filter anywhere on the spend path; `created_at` usable as the purge predicate; `guardrail_event`/audit rows are NOT spend inputs (they stay — state which tables the purge will never touch).
- Month definition, DECIDED here (not delegated): calendar month in the server's timezone at execution (the live clock, `PG-IC-07`) — a row counts toward the month its `created_at` falls in. If the tree already month-filters spend somewhere I did not read, that finding re-scopes everything below.

## G1 — month-box the spend query (fail-then-pass against the OLD behavior — `PG-EV-08`, `PG-EV-09`)

- Change `_recorded_spend` (and any mirror the G0 reads surface — chat/planning/analytics spend readers, each named or stated-absent) to sum the CURRENT calendar month only.
- Proof, both runs committed: a temp-DB/unit fixture with last-month + this-month rows where OLD code returns the lifetime total and NEW code returns this-month-only (numbers quoted). Empty-household sample spends `0.0` and purges nothing (`PG-SC-07` — the empty world is named: 0.0, no-op, still correct).
- `PG-IC-08` blast radius, stated as a stop: the fixture's expected totals are written in the test — a measured total differing in either direction stops the run before any further change.

## G2 — purge vehicle + retention constant + temp proof (live NEVER run)

- Constant `LEDGER_RETENTION_MONTHS = 12`, declared UNCALIBRATED (`G-A9`) with the one-line reason (a year of audit trail on local disk; the project never set one). Vehicle: an explicit function (module placement yours — decide and report) deleting `provider_call` rows older than the cutoff, returning the deleted ids/count. No scheduler, no endpoint, no auto-run anywhere.
- Temp-DB proof: seed old (13+ months) + recent rows, run the vehicle, quote before/after counts (old gone, recent intact, `guardrail_event`/audit tables untouched), then re-run the G1 month-math on the purged temp DB (unchanged — the purge cannot move the monthly figure, quoted).
- Record the LIVE command word-for-word for its own future word (backup-first per the SG-086 runbook, then the vehicle invocation, then before/after counts) — recorded, NEVER executed here. Executing it is a STOP.
- Full suite green-except-base-proved-reds (bound 600s); ruff clean; mypy quoted. Empty diff over `models/`+`alembic/` quoted (no schema change).

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-125.log`, `SG-125_report.md`, `SG-125_verify.log` (both spend runs + temp purge captures + every empty diff + the recorded live command). First token `SG-125`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the spend-query change (+ named mirrors or stated-absent), the purge vehicle + constant, tests, `docs/worklogs` (3 files). **Any other hunk — schema, endpoints, schedulers, caps values, suite files beyond the new tests — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs file reads only; G1 needs the query change + unit/temp proof; G2 needs the vehicle + temp proof + suite; nothing else. No criterion touches the live DB, containers, the network, keys, or the running service. Reads explicitly INCLUDE running tests + temp-DB scripts in-process; pulling any image or launching any other runtime is NOT included and is a STOP.
- Interim (`PG-PR-05`): this code is NOT live until a later rider serves it — until then the running service still sums lifetime. Stated, not assumed; the rider is a later slice, not this one.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): box the query, build the broom, prove on temp. No archiving layer, no per-provider windows, no UI — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): read-path — does the cap math still count lifetime rows? write-fate — what happens to rows past the window, and what proves the vehicle only takes those? live-safety — what stops this slice from touching production?
- Old-vs-new spend totals quoted from committed runs (lifetime vs month-only); empty-household 0.0 quoted.
- Temp purge before/after quoted (old gone by id/count, recent intact, non-spend tables untouched); post-purge month-math unchanged and quoted.
- Live command recorded word-for-word, never executed (its absence from every shell history quoted or stated with the check used); no vacuous pass (a purge proven only by its own return value evidences nothing — the before/after SELECTs are the proof).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-125 | Report: docs/worklogs/SG-125_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite; expected ~600s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
