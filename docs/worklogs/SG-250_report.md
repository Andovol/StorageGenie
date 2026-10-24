# SG-250 — Stop predicting costs: remove the estimate and the cap machinery, keep and complete the actual-cost record, log every call's real cost

**Terminal class: CHANGED.** Product and tests changed; no database, migration, provider call, key read, deployment or restart. Target and actual spend: **$0**.

## Identity and base

- **BASE REF:** `origin/automation`
- **BASE COMMIT (resolved):** `da78bae1ad4b156a976a5bba6eac1227203285b3` (`git rev-parse origin/automation`; work-tree HEAD at start was the same commit).
- **WORK HEAD:** the commit carrying this report. Per `CO-55(b)` a report cannot carry the hash of the commit that contains it; the notes receipt records it as `Work-HEAD`.
- **Model / reasoning effort (read from this process's own arguments, `ps -o args= -p 3629969`):** `opencode-go/deepseek-v4.1-flash` / `max` (`--variant max`). Not read from any system-prompt identity label.
- **Lane start (own clock, `run-coder SG-250` process start):** `2026-10-24T18:58:40Z`.
- **Elapsed at report-writing start:** `995 s` of the lane's `1500 s` bound (`19:15:15Z` minus `18:58:40Z`). Report composition runs inside the remainder.
- **Database:** none opened, none written, no migration. **Provider:** none called; no key or `.env` value read.

## Findings first (PB-1 / CO-06 / CO-07)

The packet's list was a hypothesis. The measured set contains more than the named modules:

- **F1 — `_recorded_spend` had a second user.** `backend/app/api/v1/enrich.py::monthly_cap_refusal` called it and `settings.sg_monthly_cap`; the packet said "nothing else uses it". Removing the setting without this would have made the Enrich press raise `AttributeError`. I removed `monthly_cap_refusal` and its one call. The Enrich **per-press** cap (`enrich_cap_refusal`, computed from the previous press's actual recorded cost) is kept.
- **F2 — `services/enrich/synthesize.py` had its own duplicate pre-call cap.** It defined `SYNTHESIS_PER_CALL_CAP_USD`, `estimate_text_cost`, `per_call_cap_usd` and `estimated_cost`, refused before the call, and passed `estimated_cost` into `extract_text`. This is a text-call cost refusal, so A2 required its removal; the parameter also had to go because the adapter/protocol surface lost it. The synthesis consent gate and ledger row are unchanged.
- **F3 — `backend/eval/run.py` imported `estimate_call_cost`.** `tests/test_eval_corpus.py` imports this file, so the full suite failed collection on the removed symbol. The runner's pre-call "projected total" abort was replaced with a stop **after** a fixture records actual spend; no prediction remains.
- **F4 — the privacy audit pins source line numbers.** `tests/test_privacy_audit.py` pins the adapter's send site and redact call sites. The lines moved because the estimate machinery was deleted; only the pins changed: send site `263 -> 256`, redact `310 -> 276`, reader redact `483 -> 423`.
- **F5 — tests that observed the removed reader.** `tests/test_sg142_cap_join.py` existed only to test `_recorded_spend`; it was deleted with the behaviour. `tests/test_sg125_ledger_retention.py` now tests only the retention vehicle; `tests/test_sg132_jina_ledger_wiring.py` reads the provider_call total directly instead of through `_recorded_spend`.
- **F6 — `snapshots.py` docstring** named `_recorded_spend`; documentation only, updated.
- **F7 — no cap write path existed.** `api/v1/settings.py` only exposed the caps on GET; the fields and their population were removed; `AiSettingsUpdate` was and remains model-only.
- **F8 — stale host env cannot break startup.** `config.py:67` keeps `extra: "ignore"`, so a leftover `SG_PER_JOB_CAP`/`SG_MONTHLY_CAP` in the host environment is ignored rather than rejected. Stated, not tested (testing it would read the host environment; the packet forbids that).

## G1 — The prediction is gone

Removed symbols (no replacement):

- `opencode_go.estimate_call_cost`
- `OpenCodeGoProvider.estimate_cost`
- `OpenCodeGoProvider._per_job_cap`, `_monthly_cap`, `_monthly_spent` and both pre-call guard blocks
- `RouterConfig.cost_budget`
- `ProviderRouter.execute(..., estimated_cost=...)` parameter and its pre-call refusal
- `BudgetExceededError` (no caller remains; the scene path does not use it)
- `reader._estimate_call`, `reader._recorded_spend`, the prepared-list estimate tuple, and the monthly-cap block
- `synthesize.estimate_text_cost`, `SYNTHESIS_PER_CALL_CAP_USD`, `per_call_cap_usd`, `estimated_cost`
- `enrich.monthly_cap_refusal`
- `eval.run`'s projected-spend abort

Enumeration on the target — **every module that referenced a removed symbol** (the five named sites plus the findings above):

1. `backend/app/services/providers/reader.py`
2. `backend/app/services/chat/service.py`
3. `backend/app/services/planning/service.py`
4. `backend/app/services/analytics/service.py`
5. `backend/app/services/enrich/synthesize.py`
6. `backend/app/api/v1/enrich.py` (F1)
7. `backend/app/services/enrich/snapshots.py` (F6, doc only)
8. `backend/eval/run.py` (F3)
9. the test modules listed under "Files changed" (F4/F5 included)

The reader's preparation loop no longer computes a per-image estimate; the router call is `router.execute("extract_items", image_bytes, call_prompt)`.

## G2 — The caps are gone

- `config.py`: `sg_per_job_cap` and `sg_monthly_cap` deleted; the class docstring no longer promises them.
- `reader.py`: the month-boxed cap check and `_recorded_spend` deleted; the adapter is constructed with `session_id`, `api_key`, `model_id` only.
- `api/v1/settings.py`: `per_job_cap` and `monthly_cap` removed from `AiSettingsOut` and `_read_safe_settings`.
- `enrich.py`: `monthly_cap_refusal` deleted (F1).
- **Kept untouched:** the consent gate (`reader.ai_status`, `config.sg_consent`), the scene cap (`config.sg_scene_cap` and `services/scene/openrouter.py`), the Enrich per-press cap, the router fallback branch, the local signals path, and `providers/redaction.py`.

## G3 — The ledger keeps the actual cost

The writer is unchanged in substance — it persists the result's post-call `cost` and real `usage` (`reader.py:204-227`):

```python
row = ProviderCall(
    provider=provider_id,
    model=str(result.model_id or settings.sg_model_id),
    prompt_template_version=template_version,
    input_hashes=json.dumps({"image_sha256": hashlib.sha256(image_bytes).hexdigest()}),
    output_payload=json.dumps(result.raw_payload, ensure_ascii=False, default=str),
    cost=result.cost,
    usage_json=json.dumps(result.usage, ensure_ascii=False),
    latency_ms=result.latency_ms,
    error_state=None,
    job_id=job.id,
)
```

The cost is computed **after** the call from the response's real usage (`opencode_go.py:140-151`):

```python
def compute_cost(usage: dict[str, Any]) -> float:
    tokens_in = usage.get("prompt_tokens") or 0
    tokens_out = usage.get("completion_tokens") or 0
    return (tokens_in * INPUT_USD_PER_1M + tokens_out * OUTPUT_USD_PER_1M) / 1_000_000
```

`INPUT_USD_PER_1M` / `OUTPUT_USD_PER_1M` stay (`opencode_go.py:45-46`). The failure path still writes a committed row with whatever cost/usage/latency the error carried (`reader.py:304-335`); a pre-body failure records honest `0.0`/absent.

Proved by `tests/test_ai_pipeline.py::test_ledger_cost_is_post_call_computation_of_real_usage` (fake provider usage `{211,89}`, row `cost == compute_cost(usage)`) and by the existing `::test_failed_body_with_usage_is_ledgered_with_that_usage` (error-carried cost/usage preserved).

## G4 — One INFO line per provider call

`opencode_go._log_call` (`:154-176`) emits exactly one line per call from `app.services.providers.opencode_go`; the root logger is already INFO (SG-240), so it reaches the served container's stderr:

```
provider call: provider=opencode-go model=<id> operation=<extract_items|extract_text> status=<ok|failed> cost=<8dp> input_tokens=<n> output_tokens=<n> latency_ms=<n|unknown>
```

The success path logs `result.cost` / `result.usage`; the `except` path logs `getattr(exc, "cost")` / `getattr(exc, "usage")` with `status=failed`. No prompt, user text, response body, image bytes, base64, key or household item identifier is in the line or its arguments.

Proved by `tests/test_opencode_go.py::test_success_logs_actual_cost_and_token_counts`, `::test_cost_log_carries_no_prompt_image_or_key`, and `::test_failure_logs_the_cost_the_error_carried` (5 passed, log `SG-250_g3_g4.log`).

## G5 — Kept behaviour is still proved

- **Consent denies by default:** `tests/test_ai_pipeline.py::test_default_config_is_phase1_skip`; zero rows, `consent_disabled`.
- **Consent refuses Enrich before any call:** `tests/test_sg080_ingest_pipeline.py::test_consent_gate_refuses_before_any_call`.
- **Scene cap still refuses over its cap:** `tests/test_sg158_scene_render.py::test_over_cap_refuses_before_send`.
- **Router fallback branch:** `tests/test_provider_gateway.py::test_fallback_fires_on_retryable_error_only`.
- **Redaction untouched:** `tests/test_opencode_go.py::test_redaction_gps_stripped_byte_proven`.
- Log: `SG-250_g5_kept.log` (5 passed).

## Acceptance evidence

**A1 — grep zero.** Over all files in `backend/app` and `backend/tests`, for `estimate_call_cost|estimate_cost|_estimate_call|estimated_cost|cost_budget|sg_per_job_cap|sg_monthly_cap|per_job_cap|monthly_cap|BudgetExceededError`: **0 hits**, `grep exit=1` (`SG-250_g1_grep.log`). `BudgetExceededError` is fully removed because no scene caller uses it. The scene cap uses its own names (`sg_scene_cap`, `max_cost`) and was untouched.

**A2 — no cost refusal.** `ProviderRouter.execute(self, operation: str, *args: Any, **kwargs: Any) -> Any`; `RouterConfig` fields are `provider_id`, `fallback_id`, `json_strict`, `retryable_errors` (`SG-250_g2_router.log`). `grep -rn 'budget|Budget' backend/app --include='*.py'` leaves only two comments about reasoning-token budget and Jina's `X-Token-Budget` request header. The chat/planning/analytics `"status": "refused"` branches and the synthesis cap path were removed.

**A3 — actual cost.** Tests named under G3; 5 A3/A4 tests passed.

**A4 — INFO line.** Tests named under G4. A wrong implementation that logged the removed estimate (or omitted tokens) would fail `f"cost={result.cost:.8f}"` and the token assertions; a naive payload log would fail the sentinel checks.

**A5 — kept behaviour.** Five existing tests named under G5, each passed.

**A6 — no schema/migration/dependency change.** `git diff --name-only origin/automation -- backend/alembic backend/requirements.lock backend/app/models/provider_call.py` is empty; `requirements.lock` SHA-256 is `aaecbf51…defda0` in both the work tree and `origin/automation`; alembic has 12 files and one head, `20261023_sg233_reminder`, unchanged; `provider_call` keeps its 11 columns incl. `cost`, `usage_json`, `latency_ms` (`SG-250_g6_a6.log`).

**A7 — suite/lint.** Full backend suite: **742 passed, 2 failed** — exactly the two known environmental reds `tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` (`SG-250_g7_suite.log`). `ruff check app tests eval/run.py` clean; `mypy --follow-imports=silent` clean on the 14 touched product/eval files (`SG-250_g8_lint.log`). Whole-app mypy still reports pre-existing errors in untouched files (`app/models/base.py`, `app/services/audit_service.py`, etc.); none are in a file this slice touched.

**A8 — vacuity.** A1's grep could have printed hits; it printed none and exited 1. A2's signature could have shown a cost argument; it does not. A3 would fail if the row stored a hardcoded or pre-call estimate instead of `compute_cost(usage)`. A4 would fail if the line carried an estimate or omitted the real token counts. A5's tests fail when the gate/branch/helper is removed (they are the same tests that existed before this slice). A6 would list changed files or differing hashes if schema/lock changed. A7 is a real suite run, not a scoped skip.

## What changed for the owner in practice

Before: the app estimated a call's worst-case cost, could refuse the call when the estimate crossed a cap, and only then recorded what was actually spent. After: no cost check can stop a photo or text call; every real provider call writes the same ledger row with the post-call actual cost, and the same actual cost plus input/output token counts and latency appears as one INFO line in the server log. The only cost gates left are non-provider or different-feature gates: the consent switch, the Enrich per-press cap on the previous press's actual cost, and the scene feature's own cap.

## Constraints and guards

- No provider call, no key or `.env` value read, no database opened/written/migrated, no deployment, no restart, no browser. All work was local file edits plus the offline backend suite.
- No prompt, schema, extraction-flow or review-queue change. No new dependency.
- `extra: "ignore"` is retained (F8).
- The only non-packet files touched are F1/F3/F4/F5/F6 dependencies, each reported above.

## Files changed

Product/eval (14): `backend/app/api/v1/enrich.py`, `backend/app/api/v1/settings.py`, `backend/app/config.py`, `backend/app/services/analytics/service.py`, `backend/app/services/chat/service.py`, `backend/app/services/enrich/snapshots.py`, `backend/app/services/enrich/synthesize.py`, `backend/app/services/planning/service.py`, `backend/app/services/providers/fake.py`, `backend/app/services/providers/opencode_go.py`, `backend/app/services/providers/protocols.py`, `backend/app/services/providers/reader.py`, `backend/app/services/providers/router.py`, `backend/eval/run.py`.

Tests (17 changed, 1 deleted): `backend/tests/test_ai_pipeline.py`, `test_analytics.py`, `test_chat.py`, `test_google_taxonomy.py`, `test_opencode_go.py`, `test_phase2_e2e.py`, `test_phase3_e2e.py`, `test_planning.py`, `test_privacy_audit.py`, `test_provider_conformance.py`, `test_provider_gateway.py`, `test_settings.py`, `test_sg080_ingest_pipeline.py`, `test_sg099_synthesis.py`, `test_sg101_text_path.py`, `test_sg125_ledger_retention.py`, `test_sg132_jina_ledger_wiring.py`; `test_sg142_cap_join.py` deleted.

Docs/evidence: `docs/worklogs/SG-250_report.md`, `SG-250.log`, `SG-250_g1_grep.log`, `SG-250_g2_router.log`, `SG-250_g3_g4.log`, `SG-250_g5_kept.log`, `SG-250_g6_a6.log`, `SG-250_g7_suite.log`, `SG-250_g8_lint.log`, `SG-250_g9_identity.log`.

Verification: PASS
