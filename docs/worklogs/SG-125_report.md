# SG-125 — Ledger retention instrument: report (INSTRUMENTED)

**Dispatch-ID:** SG-125 · **Coder:** opencode · **Effort:** high · **Model:** opencode-go/deepseek-v4.1-flash
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE REF:** `origin/automation` · **BASE_RESOLVED:** `7bbf082d52260518bf6676006d9f70ba64182951` · **START_HEAD:** `7bbf082d52260518bf6676006d9f70ba64182951` · **WORK_HEAD:** `5e61ae58de3a7ac073f9add8841e822c62e8f0ab` (the work commit carrying product + tests + worklog; receipt note below).
**Spend (real $):** $0.000000 — zero metered calls on any path; no provider call; no key read; no network.
**Contract:** recorded `0.37.0` == published `1acd7730e5fa6de5b7403aacce71207e9946461d`; source path `/home/andrei/storagegenie-contract/{VERSION, HEAD}`; `RULES.md` sha256 `18de7fd7…` == payload `RULES.sha256`.

## MODEL + EFFORT provenance
- EFFORT `high` read from process arguments: `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>` (`output/dispatch/SG-125.launcher.sh`).
- MODEL `deepseek-v4.1-flash` read from provider metadata in the run log (`> build · deepseek-v4.1-flash`, `output/dispatch/SG-125.log`). No model id rode the trigger (contract-legal omitted-model subset, D302).

## (a) Issues / deviations / surprises
- **F-SG125-1 (M45 suite collision — privacy line pin, the only out-of-ceiling touch).** Adding the retention helpers shifted the reader `redact_image(` call site `reader.py:402 → :465`; `test_privacy_audit.py::test_g0_redact_call_sites_are_reader_and_direct_adapter` hardcodes that line. Per **M45** (suite-green binds on collision with the STOP-ceiling; STATE.md) and the **SG-101 / F-SG101-1** precedent, the pin was repaired minimally (line number + one docstring line), no weakening: the caller set is unchanged — still exactly `opencode_go.py:310` and `reader.py:465`, the two image paths. Disclosed, not silent.
- **F-SG125-2 (premise corrected).** The packet's "chat/planning/analytics spend readers" **do not exist**. `chat/planning/analytics service.py` and `enrich/synthesize.py` carry ledger **writers** (`_write_ledger` / `_write_error_ledger`), not readers. There is exactly one spend reader, `reader._recorded_spend` (grep: one def, one call site). The G1 month filter is therefore **single-site**, and that one sum already covers every writer's rows because it joins `provider_call → job → household_id`.
- **F-SG125-3 (premise confirmed).** Every line reference in the packet matched BASE exactly (`reader.py:200-222` `_write_ledger`, `:237-251` `_recorded_spend`, `:405-416` cap call site, `models/base.py:21-22` `TimestampMixin`). After the change the same symbols sit at `reader.py:208-223`, `:269-285`, `:477-488`; the drift is exactly F-SG125-1.
- **F-SG125-4 (carried, outside scope).** `STATE.md` open-threads already lists "brittle reader line-pin (accepted risk)"; this slice hit it (F-SG125-1). A caller-set assertion (not a line number) would retire the risk when the pin is next touched.

## (b) Actions
- Changed paths: `backend/app/services/providers/reader.py` (+67/-5: `LEDGER_RETENTION_MONTHS`, `_current_month_start_utc`, `_retention_cutoff_utc`, month-boxed `_recorded_spend`, `purge_old_provider_calls`); new `backend/tests/test_sg125_ledger_retention.py` (+5 tests); `backend/tests/test_privacy_audit.py` (M45 pin repair, F-SG125-1); evidence `docs/worklogs/{SG-125.log, SG-125_report.md, SG-125_verify.log}`.
- Commits: work commit = `WORK_HEAD`; a docs-only follow-up fills the receipt note (SG-124 precedent). Push `origin automation`.
- No schema change (empty diff `backend/app/models` + `backend/alembic`), no endpoint, no scheduler, no cap value, no model, no live DB, no container, no rebuild/recreate, no network.
- Retry count: 0. Test-command count: fail-pre 1, pass-post 2 (one rewrite after the boundary test proved clock-flaky), purge-capture 1, cap tests 2, candidate suite 2, base suite 1, base mypy 1, candidate mypy 1, ruff candidate 2, ruff base 1. Provider-call count: 0. Health: not run (packet declares no service/db and the slice is offline).
- Highest-impact action: making the purge **not fail-open** — boxing `_recorded_spend` to the calendar month first, so a later live purge cannot silently loosen the cap.

## G0 — read paths (PG-SC-01), stated not solved
- **No month filter on the spend path:** `_recorded_spend` at BASE summed all-time per household. Confirmed by reading it and the call site; no mirror reader exists (F-SG125-2).
- **`created_at` usable as the predicate:** `ProviderCall` has `TimestampMixin.created_at` (`models/base.py:21-22`), `DateTime(timezone=True) server_default=func.now()`. SQLite stores it UTC; the code converts the server-local boundary to naive UTC.
- **Non-spend tables:** the sum reads only `ProviderCall.cost` via `Job.household_id`; the purge deletes only `provider_call`. `guardrail_event`, `audit_event`, `job`, `job_step`, `evidence`, `household` are never written or deleted by this slice (proved by before/after counts).
- **Month definition (decided):** calendar month in the server's timezone at execution (`PG-IC-07`) — a row counts toward the month its `created_at` falls in.
- **No scheduler:** grep `scheduler|apscheduler|cron|celery` over `backend/app` = only negative docstrings; nothing calls the vehicle.

## G1 — month-box the spend query (fail-then-pass, PG-EV-08/PG-EV-09)
- New test `test_sg125_ledger_retention.py::test_recorded_spend_boxes_to_current_month` writes **last-month 5.00 + this-month 2.00 + 3.00** (plus another household's 100.00).
  - **OLD (BASE `_recorded_spend`, all-time):** `10.0` (`assert 10.0 == 5.0` red in the fail-pre run).
  - **NEW (candidate):** `5.0`; other household `100.0` (household scoping preserved).
- **Empty household:** `_recorded_spend == 0.0` and `purge_old_provider_calls == []` (0.0, no-op, still correct; `PG-SC-07`).
- **PG-IC-08 blast radius:** the expected totals are written in the test (`10.0`, `5.0`, `100.0`, `2.0`); a measured total differing either way fails the run. Both existing durable-cap tests still pass unchanged (current-month rows): `test_ai_pipeline.py::test_monthly_cap_binds_across_jobs_from_durable_ledger` and `test_sg080_ingest_pipeline.py::test_monthly_ledger_refuses_before_any_call`.

## G2 — purge vehicle + retention constant + temp proof (live NEVER run)
- `LEDGER_RETENTION_MONTHS = 12`, declared **UNCALIBRATED (G-A9)**: a year of audit trail on local disk; the project never set a retention window. One consumer only.
- `purge_old_provider_calls(db, *, retention_months=LEDGER_RETENTION_MONTHS)` deletes `provider_call` rows with `created_at < cutoff` (cutoff = live clock shifted back 12 calendar months, day-clamped), returns the deleted ids; **no scheduler, endpoint or auto-run**.
- **Temp-DB capture (scratch SQLite, removed after):** before = `provider_call/guardrail_event/audit_event = (5,1,1)`, `month_before = 2.0`, `lifetime_before = 5.0`; after vehicle: `deleted_ids = 3`, counts `(2,1,1)`, `month_after = 2.0`, `lifetime_after = 2.0`, `scratch_removed = True`. Old ~13-month rows gone, recent rows intact, non-spend tables untouched; the monthly figure never moved. Happy-path test also proves the strictly-older predicate (~11-month row kept).
- Empty diff over `backend/app/models` + `backend/alembic` (no schema change); empty diff over `backend/app/config.py` (no cap value touched).

## Acceptance criteria check (PG-SC-09)
- **read-path — does the cap math still count lifetime rows?** No: it now sums the current calendar month only (OLD 10.0 → NEW 5.0 quoted).
- **write-fate — what happens to rows past the window, and what proves the vehicle only takes those?** An explicit call deletes only `provider_call` rows strictly older than the month cutoff; proved by before/after SELECT counts and id sets (not by the return value alone), plus the ~11-month boundary test.
- **live-safety — what stops this slice from touching production?** Temp-DB only; the live command is recorded and never run; `purge_old_provider_calls` absent from shell history; no docker/sqlite/DB command touched the live path.
- **No vacuous pass:** the fail-pre run is red with the lifetime number; the purge is proved by before/after SELECTs and non-spend counts; the call-site grep lists its hits; the empty diffs are quoted.

## Actual versus budget (units: seconds, live clock UTC; early legs approximate)
| Leg | Actual | Budget |
|---|---|---|
| G0 read path + mirror/scheduler census | ~150s | 120s ordinary — **over** |
| G1 query + fail-pre/pass-post tests | ~180s (one clock-flaky test rewritten) | 120s ordinary — **over** |
| G2 vehicle + temp capture + cap tests + suites/ruff/mypy | ~150s (suites 31.14s / 32.92s) | 600s suite bound |
| G3 worklogs + receipt | from ~13:39:00Z | 600s overall |

No command was killed or timed out. The two ordinary legs exceeded 120s (recon breadth and the test rewrite); reported, not hidden.

## Receipt (note on `refs/notes/storagegenie-coder-reports`) — pasted verbatim
Work committed and pushed to `automation` (worktree clean, `CO-55`). No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. WORK_HEAD = `5e61ae58de3a7ac073f9add8841e822c62e8f0ab`. The note was added on WORK_HEAD, the notes ref pushed, the refspec fetched into a mapped local name, and `git notes --ref=refs/notes/sg125-verify show 5e61ae58de3a7ac073f9add8841e822c62e8f0ab` pasted verbatim below. **Paste executed after the work commit; see `SG-125_verify.log` §9.**

```text
$ git notes --ref=refs/notes/storagegenie-coder-reports show 5e61ae58de3a7ac073f9add8841e822c62e8f0ab
error: no note found for object 5e61ae58de3a7ac073f9add8841e822c62e8f0ab.
pre_show_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-125 | Report: docs/worklogs/SG-125_report.md | Work-HEAD: 5e61ae58de3a7ac073f9add8841e822c62e8f0ab" 5e61ae58de3a7ac073f9add8841e822c62e8f0ab
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   e8e7626..2e8e22a  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg125-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg125-verify
fetch_exit=0

$ git notes --ref=refs/notes/sg125-verify show 5e61ae58de3a7ac073f9add8841e822c62e8f0ab
Dispatch-ID: SG-125 | Report: docs/worklogs/SG-125_report.md | Work-HEAD: 5e61ae58de3a7ac073f9add8841e822c62e8f0ab
show_exit=0
```

note=yes

## UNCLEAR
- **FIRST READ:** whether a spend reader other than `reader._recorded_spend` existed (the packet's "chat/planning/analytics mirrors"). Read: none — those are writers (F-SG125-2). Also whether the packet's exact line numbers held at BASE (they did, F-SG125-3).
- **DURING EXECUTION:** my first boundary test compared a row created at a cutoff computed in the test against a cutoff recomputed microseconds later inside the vehicle — clock-flaky; it was rewritten to margin-based day offsets before it was committed. The privacy-audit line pin collision (F-SG125-1) was self-caught by the full suite and repaired under M45.
- **REMAINING:** the month-box change is **not live** until a later rider serves it (`PG-PR-05`) — the running service still sums lifetime until then. The live purge is deliberately un-run and takes its own owner word. The 12-month window is uncalibrated (`G-A9`); the `purge_old_provider_calls` symbol is never scheduled/auto-run, so a future slice must decide the operational trigger (and whether the brittle line pin should become a caller-set assertion).
