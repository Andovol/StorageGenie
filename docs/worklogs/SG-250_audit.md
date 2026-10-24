# SG-250 audit — the cost prediction and the caps are gone; the actual cost is recorded and logged; rated 97

**Receipt verified:** notes-ref trailer `Dispatch-ID: SG-250 | Report: docs/worklogs/SG-250_report.md | Work-HEAD: d0a87c640a82cc1d90a5583e9cb23d96d528a7a4` read from the **explicitly fetched mapped ref** (`refs/notes/storagegenie-coder-reports`, `212d6f3..87f9200`). Trigger returned `result=done id=SG-250 exit=0`. The product commit is `d0a87c6`, plus two docs-only commits (`406aad7`, `9932f85`) on `origin/automation`; the report's last line is `Verification: PASS`.

**Diff verified (base `da78bae` → `9932f85`):** **42 files, +790 / −1361** — 14 product/eval modules, 17 test modules changed and 1 deleted, and 10 evidence files. Every path is inside the packet's criterion ("every module that references a removed symbol") and its named ceiling. **Zero** schema, migration or dependency bytes: `git diff --name-only` over `backend/alembic`, `backend/requirements.lock` and `backend/app/models/provider_call.py` is **empty**, `requirements.lock`'s sha256 is identical in the work tree and on origin, and the alembic head stays `20261023_sg233_reminder` (12 files, one head). **$0**, no provider call, no key or `.env` value read, **no database opened**, no deployment, no restart.

**The owner's decision, executed:** *"D3 - Stop carrying about predicting costs, just log the costs and thats it."* (D-1024-19). The slice removed the prediction, the caps and their refusals; kept the post-call actual cost, the ledger, the consent gate and the scene feature's own cap; and added one INFO line per provider call.

## What the diff proves

- **The prediction is gone** — `estimate_call_cost`, `OpenCodeGoProvider.estimate_cost`, the adapter's `_per_job_cap`/`_monthly_cap`/`_monthly_spent` and both pre-call guard blocks, `RouterConfig.cost_budget`, `ProviderRouter.execute(..., estimated_cost=…)` and its refusal, `BudgetExceededError` (**no caller remained** — the scene path never used it), `reader._estimate_call`, `reader._recorded_spend`, the prepared-list estimate tuple, `synthesize.estimate_text_cost` / `SYNTHESIS_PER_CALL_CAP_USD` / `per_call_cap_usd`, `enrich.monthly_cap_refusal`, and the eval runner's projected-spend abort. A1's grep over `backend/app` and `backend/tests` for all nine symbols returns **0 hits** (`grep exit=1`).
- **The caps are gone** — `sg_per_job_cap` and `sg_monthly_cap` from `config.py` (and the docstring that promised them), the month-boxed check and its ledger reader from `reader.py`, the two fields from `AiSettingsOut` and `_read_safe_settings`, and the cap arguments the registry passed to the adapter.
- **The actual cost is kept and proved** — the ledger row still carries the post-call `cost` and the real `usage` (`reader.py:204-227`), computed after the call from the response's own token counts (`opencode_go.py:140-151`, `compute_cost`), with the rate constants kept (`opencode_go.py:45-46`); the failure path still writes its row with the cost the error carried. Proved by `test_ledger_cost_is_post_call_computation_of_real_usage` (fake usage `{211,89}`, row cost `== compute_cost(usage)`) and the pre-existing `test_failed_body_with_usage_is_ledgered_with_that_usage`.
- **One INFO line per call** — `opencode_go._log_call` emits `provider=… model=… operation=… status=ok|failed cost=<8dp> input_tokens=… output_tokens=… latency_ms=…` from the app's own logger, on the success and the failure path, with **no prompt, response body, image bytes, base64, key or item identifier**. Three tests, including one that asserts the line carries none of those.
- **The kept behaviour is still behaviour** — five pre-existing tests named and passed: consent denies by default, consent refuses Enrich before any call, the scene cap still refuses over its cap, the router's fallback branch still fires on a retryable error only, and the redaction helper is byte-proven untouched.
- **The suite is green except the two known environmental reds** — **742 passed, 2 failed**, the same two (`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`, `test_ocr_has_text_boxes_and_mean_confidence`); `ruff` clean; `mypy --follow-imports=silent` clean on the 14 touched files; the whole-app mypy reds remain in untouched files only.

## The findings (eight, all disclosed, one of them a near-miss the packet did not see)

- **F1 — `_recorded_spend` had a second user.** `backend/app/api/v1/enrich.py::monthly_cap_refusal` called it and `settings.sg_monthly_cap`; the packet said "nothing else uses it". Removing the setting without this would have left the Enrich press raising `AttributeError` at runtime. The slice removed the refusal and its call, and **kept** the Enrich per-press cap (computed from the previous press's actual recorded cost — an actual-cost limit, not a prediction).
- **F2 — `services/enrich/synthesize.py` carried its own duplicate pre-call cap** (`SYNTHESIS_PER_CALL_CAP_USD`, `estimate_text_cost`, `per_call_cap_usd`) and passed `estimated_cost` into `extract_text` — a text-call cost refusal, so A2 required its removal; the synthesis consent gate and its ledger row are unchanged.
- **F3 — `backend/eval/run.py` imported `estimate_call_cost`**, so the full suite failed collection on the removed symbol. Its pre-call "projected total" abort became a stop **after** a fixture records actual spend.
- **F4 — the privacy audit pins source line numbers**; the send site moved `263 → 256`, the adapter's redact site `310 → 276`, the reader's `483 → 423`. Only the pins changed.
- **F5/F6** — a test module that existed only to test `_recorded_spend` was deleted with the behaviour; another now reads the ledger total directly; one docstring named the removed function.
- **F7** — there was never a cap **write** path; the caps were exposed on GET only. **F8** — `extra: "ignore"` (`config.py:67`) means a leftover `SG_PER_JOB_CAP` in the host's environment cannot break startup; stated, not tested (testing it would read the host environment).

**No flag:** no safety breach (no provider call, no key read, no database opened, no migration, no schema change, no deployment, no restart, $0) and no trust breach (eight findings, two of them against the packet's own premise, none hidden; the enumeration criterion was honoured and the extra set reported).

**Holistic: 97/100, no flag.** The slice did exactly the owner's instruction, kept every cost gate that is not about cost, proved the removed machinery is gone by grep and by signature, and proved the surviving behaviour by the tests that already existed. `deduction_attribution`: **packet** — the packet's touch-list named five modules where the real set was nine; the *criterion* ("every module that references a removed symbol") caught the difference, which is the mitigation working, but the ceiling was wider than the packet said.

### One thing the owner should know (recorded, not a defect)

**The cost line is emitted by the `opencode-go` adapter**, so a run with **no** provider key — which uses the `fake` double — logs no cost line. The live app's provider registry decides whether the line ever appears: if the host holds an `OPENCODE_API_KEY`, every real photo read logs its cost; if not, the photo path is the double and nothing is logged. The rider will report which providers the **served** registry holds (ids only, never a key value), so this is answered by measurement, not by assumption.

### Dispositions

| Item | Status |
|---|---|
| The owner's D-1024-19 — stop predicting costs, log the actual cost | **RESOLVED** — the prediction, the caps and their refusals are gone; the actual cost is recorded and logged; nothing else changed |
| D-1024-17 (no fallback yet) and D-1024-18 (cloud only) | **RESOLVED as scoped** — the router's fallback branch and the local signals path are untouched; the deferred work sits in `docs/backlog.md` (W6, W7) |
| The consent gate and the scene feature's cap | **RESOLVED** — kept and proved by their pre-existing tests |
| The near-miss F1 (`enrich.monthly_cap_refusal` would have raised `AttributeError`) | **RESOLVED** — found, fixed and reported before the slice ended |
| The cost line's reach (adapter-local, so a keyless run logs nothing) | **OPEN** — answered by the rider's registry read; if the owner wants a line for every provider, a later slice moves the log to the reader |
| The contract version the lane ran under | **OPEN** — the receipt echoes **0.53.0** while the project records 0.52.0: the shared contract moved mid-session (see the close report and the adoption decision) |
| SG-250 receipt + rating row | **RESOLVED** — receipt read back from the fetched ref; this row and this audit committed this turn |
