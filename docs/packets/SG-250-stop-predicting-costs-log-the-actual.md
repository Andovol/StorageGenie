# SG-250 — Stop predicting costs: remove the estimate and the cap machinery, keep and complete the actual-cost record, log every call's real cost

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.** No database is opened, written or migrated by this slice. The ledger table and its columns stay exactly as they are.
**Restart: none.** This slice changes code only; the close-deploy rider that serves it is a separate slice.
**Provider: none.** No provider is called, no key is read, no spend occurs. Target: **$0**.

## Why this exists

The owner decided, 2026-10-24, verbatim: ***"D3 - Stop carrying about predicting costs, just log the costs and thats it."*** (D-1024-19). Two related decisions frame it: *"D1 - no fallback yet"* (D-1024-17) and *"D2 - No built in or local reader, only cloud"* (D-1024-18).

The app today estimates what a call **will** cost, refuses the call if the estimate crosses a cap, and only then learns what the call actually cost. Both caps have been **off** (`None`) since the owner's own *"no caps at first"* (2026-09-11, F2), so the estimate machinery bound **nothing** — it was machinery without a job. The owner's instruction is to delete it and keep the truthful part: **what each call actually cost**, recorded and logged.

**What must not change:** what the app reads, what it proposes, what it stores, and the two gates that are not about cost — the **consent gate** (the owner's switch for AI use) and the **scene feature's own cap** (a different feature's limit, enforced against actual reported cost).

## G1 — Remove the prediction

Delete, with no replacement:

- the pre-call estimate — `backend/app/services/providers/opencode_go.py:151-164` (`estimate_call_cost`) and `:244-250` (`estimate_cost`);
- the router's cost budget and its pre-call refusal — `backend/app/services/providers/router.py:35` (`RouterConfig.cost_budget`), `:52-74` (`execute(..., estimated_cost=…)` and the refusal at `:71-74`);
- the reader's estimate plumbing — `backend/app/services/providers/reader.py:233-242` (`_estimate_call`) and the estimate carried in the prepared list at `:480-484`;
- the `estimated_cost` parameter of the provider protocol — `backend/app/services/providers/protocols.py:28-37`;
- the adapter's duplicate budget guards — `backend/app/services/providers/opencode_go.py:298-309` and `:361-372`.

**State the criterion, then enumerate the set on the target** (a list handed over is a fact to be verified, not a fact): *every module that references a removed symbol* — the router's call sites construct `RouterConfig` with a budget, so each of them changes mechanically (`providers/reader.py`, `services/chat/service.py`, `services/planning/service.py`, `services/analytics/service.py`, and `services/enrich/synthesize.py` if it passes the removed parameter). **Enumerate the set and report it** — a module you find beyond the named ones is a finding, not an obstacle.

## G2 — Remove the caps

- the settings — `backend/app/config.py:48-49` (`sg_per_job_cap`, `sg_monthly_cap`) and the docstring's promise of them (`config.py:6-12`);
- the monthly cap check and the ledger reader that fed it — `backend/app/services/providers/reader.py:486-497` and `_recorded_spend` at `:293-306` (nothing else uses it; if you find a second user, report it);
- the caps in the settings surface — `backend/app/api/v1/settings.py:29-36` (`AiSettingsOut.per_job_cap`, `.monthly_cap`) and any write path for them;
- the cap arguments the adapter's constructor takes and the registry passes — `backend/app/services/providers/reader.py:97-105`.

**Keep** the **consent gate** (`providers/reader.py:108-114`, `config.py:50`) and the **scene feature's own cap** (`config.py:45-47`, `services/scene/openrouter.py:288-296`) untouched.

## G3 — Keep and complete the actual-cost record

The `provider_call` ledger row must carry what the call **actually** cost — not an estimate:

- the actual cost comes from the response's **real** usage, computed after the call (`providers/opencode_go.py:139-148`, `compute_cost`), and the actual token counts (`usage`);
- the row is still written on the failure paths too, with the cost the error carried (`providers/reader.py:359-390`, the error ledger);
- the rate constants `INPUT_USD_PER_1M` / `OUTPUT_USD_PER_1M` (`providers/opencode_go.py:44-45`) **stay** — they price what actually happened, not what was predicted.

**Verify, do not assume:** quote the writer (`providers/reader.py:208-230`) and the cost computation, and state in the report that the recorded cost is the post-call computation of the response's real usage.

## G4 — Log every call's real cost

**One INFO line per provider call**, from the app's own logger, carrying: the provider id, the model id, the operation, the **actual** cost, the input and output token counts, and the latency. No prompt text, no response body, no image bytes, no key, no identifier of the household's items.

The app's logging configuration (SG-240) already puts the root logger at INFO with one stderr handler, so the line appears in the served container's own log — that is where the cost becomes visible without a query. Keep the line on the **failure** path too, with the cost the error carried and `status=failed`.

## G5 — What stays, untouched

- the router's **fallback branch** and the retryable set (`providers/router.py:79-81`, `providers/reader.py:61-63`) — the owner deferred the fallback (D-1024-17); the branch stays built, tested and unreachable in production;
- the **consent gate** and the **scene cap**;
- the app's local signals path (`backend/app/services/signals.py`) and the redaction helper (`providers/redaction.py`) — no local reader is added and none is removed (D-1024-18 concerns what we build, not the existing feature; the owner may revisit that);
- every schema, table and column; no migration; no new dependency.

## Scope ceiling

- **Product:** `backend/app/services/providers/` (the router, the reader, the opencode-go adapter, the protocols, the fake double if its signature changes), `backend/app/config.py`, `backend/app/api/v1/settings.py`, and the **five provider call sites** named in G1 — each changed mechanically only (the removed argument).
- **Tests:** every module that references a removed symbol. **Criterion, not a list:** enumerate the set on the target, report it, and update each — the fake adapters' `estimated_cost` signatures, the `monkeypatch.setattr(settings, "sg_per_job_cap", …)` / `"sg_monthly_cap"` lines, and the tests that assert a cost refusal (those behaviours are gone — the tests go with them).
- **Docs:** `docs/worklogs/SG-250*` only.
- **Nothing else.** No blueprint, roadmap, backlog or decision-file edit — those are the Architect's, and they are already committed.

## Acceptance criteria

- **A1** — the prediction and the caps are **gone**, proved by a grep over `backend/app` and `backend/tests` for `estimate_call_cost`, `estimate_cost`, `_estimate_call`, `estimated_cost`, `cost_budget`, `sg_per_job_cap`, `sg_monthly_cap`, `per_job_cap`, `monthly_cap` — every remaining hit is listed in the report with its reason (the scene path's cap and its own constants are allowed to remain; `BudgetExceededError` remains only if the scene path still uses it). The report **enumerates every file changed and every symbol removed**.
- **A2** — **no call is refused for cost**: no code path raises a budget error for a photo or text call, and the router's `execute` no longer takes a cost argument.
- **A3** — the ledger keeps the **actual** cost: a test shows a fake provider reporting real usage produces a `provider_call` row whose `cost` equals the post-call computation of that usage and whose `usage` carries the real token counts; and the error path still writes its row with the cost the error carried.
- **A4** — one INFO line per provider call with the actual cost and the token counts: a test captures it and asserts the actual cost and the counts; a second asserts the line carries **no** prompt text, no image bytes and no key.
- **A5** — the kept behaviour is still behaviour: the consent gate still denies by default, the scene cap still refuses over its cap, the router's fallback branch still passes the gateway test, and the redaction helper is untouched — each proved by the existing test, named.
- **A6** — **no schema change, no migration, no new dependency**: the alembic head is unchanged, the `provider_call` table's columns are unchanged, and `requirements.lock` is byte-identical.
- **A7** — the whole backend suite is green except the **two known environmental reds** (`backend/tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `::test_ocr_has_text_boxes_and_mean_confidence`), whose count and names are stated in the report; `ruff` and `mypy` are clean on the touched files; the report states the full-suite counts.
- **A8** — `PB-3` vacuity: each acceptance check must be one that **could** fail. For A3 and A4, say what a wrong implementation would look like and what the test would show instead (for A4: a line carrying an **estimated** cost must fail the assertion, since the estimate is what was removed).
- **A9** — the report's last line is `Verification: PASS` or the honest failure reason.

## Constraints and guards

- No provider call, no key read, no `.env` value read, no database opened, no migration, no deployment, no restart, no browser. `extra: "ignore"` in `backend/app/config.py:67` means a stale `SG_PER_JOB_CAP` in the host's environment cannot break startup — state that in the report rather than testing it.
- The slice changes **what the app spends and records**, not what it reads: no change to the prompts, the schema, the extraction flow or the review queue.
- The report must state **what changed for the owner in practice**: before, an estimate could stop a call; after, no cost check stops a call, and the real cost of each call appears in the server log and in the ledger.

## Budget

The lane's own `RUN_BUDGET_S` is the ceiling; **publish before the bound** at 1500 s. Expected ≈1000 s, derived from SG-240's actual elapsed time (1504 s for a build, a full suite and a census) — this slice touches fewer files and runs one suite.

## Report

Destination: `{{WORKLOG_DIR}}/SG-250_report.md`, with the evidence logs beside it; the receipt to the notes ref `refs/notes/storagegenie-coder-reports` with the first line `Dispatch-ID: SG-250 | Report: docs/worklogs/SG-250_report.md | Work-HEAD: <work commit>` (fetch the ref explicitly: `git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`). The report states the base ref and the resolved base commit as two fields, the model and effort read from the process arguments (never a system-prompt label), the elapsed time measured from the lane's own clock, and the files changed.
