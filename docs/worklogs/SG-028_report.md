# SG-028 report — pipeline wiring GREEN: `ANALYZING_WITH_AI` runs for real, offline

**BASE REF:** `automation` → resolved commit `f7de15c38acfbf9d4d6648e9b7d47c8907577ce8` (two fields, as required).
**WORK_HEAD:** the commit carrying this file (hash quoted by the receipt note in G6; note added last, no commit after).
**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`.
**Model/effort per CO-78 (from process arguments / provider metadata, never an identity line):** process argv
`opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet>"` → effort `medium`; the model flag
is absent from argv (packet: CLI default, omitted per policy). Provider metadata line `providerID=opencode-go
modelID=deepseek-v4.1-flash` (session `ses_f68e41ec9ffeLob6Tkr52Wzf6X`, `opencode.log:139244`) → model
`deepseek-v4.1-flash`. No provider was called, so no adapter-target model usage.
**DATABASE:** none — temp SQLite only, zero live rows. **Restart:** none — no service touched, nothing deployed.
**NETWORK:** none — zero provider HTTP attempts (proven in-process). **Spend:** $0.00.

## Verdict

GREEN. Both AI steps exist in blueprint §5.1 order and are wired to the SG-025 router, the SG-026 schemas and the
SG-027 surfaces. Default posture is byte-for-byte Phase-1 on the shipped defaults; the enabled path runs fully
offline on a schema-valid scripted provider with exactly one repair then a FAILED step. Gating, provenance and the
correction chain are proven by negative/positive tests; the carried docstring and config-pollution fixes are done.
Full suite: `2 failed, 98 passed` — the two reds are the base-proved decoder environment legs (no `libzbar`, no
`tesseract`); `ruff` clean; `mypy` unchanged from base (40 errors, none in touched files).

## G0 — baseline and premises (all re-verified in-slice)

- Starting tree clean: `git status --porcelain` (quoted in the verify log) = empty at 19:33Z before any edit.
- **BASE suite** (detached worktree `f7de15c`, from `backend/`, bound 600s → 5.24s): `4 failed, 85 passed`.
  Exactly the packet's premise — 2 config-reload pollution reds (`test_search::test_fts_migration…`,
  `test_signals::test_observation_migration…`) + 2 decoder env legs (`test_signals::test_generated_codes…`,
  `test_signals::test_ocr_has_text_boxes…`, both logged `pyzbar/libzbar is not installed` / `tesseract is not
  installed`). **POST** suite removes the two pollution reds (carried fix); the two decoder legs remain
  environment reds.
- Read + quoted: `job_service.py` (6 `STEP_NAMES`, `execute_step`, `run_job`, AWAITING_REVIEW resume);
  `dedup.py` (candidate creation + the early-return at `:102-104`); `candidates.py` (`:76-91` accepted set +
  hardcoded `source_type="deterministic"`); `api/v1/candidates.py` (decision path); `protocols.py`/`router.py`/
  `fake.py` (non-schema `extract_items`) and `opencode_go.py::extract_items(image_bytes, prompt, *, estimated_cost)`;
  `schemas.py` (`parse_extraction_output`, `extract_with_single_repair`); `config.py` (six SG-027 settings); both
  prompt front-matters (`template_version: extract-{food,medicine}-v1`); `CandidateCard.tsx::fieldInfo` (`:4-14`)
  + `ProvenanceBadge`; `provider_call` model (incl. `job_id`); `signals.py` `_stored_path`/`storage_path`;
  `review_tasks.py` resolve API; `plugins.py::enter_expiry`; `assertion.model_json` (line 21) — **no migration**.
- Premise frame: **confirmed** — the reader (new `providers/reader.py`) supplies BYTES + prompt because the SG-027
  adapter surface is `extract_items(image_bytes, prompt, ...)`, while `protocols.py` keeps the seam-shaped
  `image_ref`; `commit_job_candidate` still commits the first candidate only (`:444`); `CandidateCard.fieldInfo`
  already renders `{value, confidence, source_type}` and `CandidateField` already permits the object; the
  `FakeProvider` raw shape is rejected by `parse_extraction_output` and never reaches candidates as-is.

## G1 — the two steps

- `job_service.STEP_NAMES` is now the 8-name blueprint order; `execute_step` dispatches
  `ANALYZING_WITH_AI → reader.run_ai_extraction` and `BUILDING_CANDIDATES → candidates.build_candidates_step`.
  Resume/retry semantics are untouched: a FAILED AI step is retried by the existing `retry_job`, and the step
  transaction rolls back (no partial candidate/ledger on failure). `# noqa: C901` added to `execute_step`
  (complexity 12>10 from the two new branches) — same convention the repo uses elsewhere.
- **Default OFF:** consent false OR provider id not in the registry → `{"status": "skipped", "reason": ...}` for
  both steps, with **0** `provider_call` rows and **0** AI fields (candidate fields stay Phase-1 flat scalars).
  Proven by `test_default_config_is_phase1_skip` and `test_real_provider_without_consent_skips_and_never_networks`.
- **Enabled path (offline):** per analyzable evidence — `resolve_original_bytes` (same `storage_path` +
  `Evidence.storage_key` route `signals.py` uses), `redact_image` (the SHARED SG-027 helper; the exact bytes handed
  to the provider are a PNG with `dict(getexif()) == {}`), prompt read from the versioned file (food default;
  `settings.sg_prompt_category` selects `medicine`), call through `ProviderRouter` (budget refusal happens before
  any call; `fallback_id=None`, so fallback semantics are untouched), strict `parse_extraction_output` through
  `extract_with_single_repair` (exactly one repair, then the step FAILS loudly — `test_repair_once_then_success` and
  `test_second_failure_fails_the_step_loudly`), one `provider_call` row per completed call with `job_id`, and the
  aggregated validated extraction persisted on the step output for the next step.
- **Injectability (ONE named seam):** `app.services.providers.reader.provider_registry()` is the single seam; tests
  monkeypatch it. `fake.py` gained a small `ScriptedProvider` (schema-valid caller-supplied payload, records the
  bytes/prompts it was handed, optional `fail_times`) — the packet explicitly allowed a schema-valid mode there.
  The shipped `FakeProvider` remains deliberately non-schema.
- **BUILDING_CANDIDATES:** deterministic fields merged with the first AI item (`display_name`, `expiry_date`, `lot`),
  each as the exact provenance object `{value, confidence, source_type, provider, model, prompt_template_version,
  provider_call_id}` (no parallel structure, no reshaping); the full `ai_items` + `ai_unknowns` + `needs_evidence`
  are preserved on the proposal. `>1` item opens a blocking `candidate.multi_item` task; `needs_evidence` opens the
  same `expiry.manual_entry` task kind the SG-026 bridge uses and derives no date. Resolution rides the existing
  `POST /v1/review-tasks/{id}/resolve`; no split UI and no auto-split (scope decision, reported).
- **Gating (§5.2-7):** `GATED_FIELDS = {identifier, expiry, expiry_date, condition, lot}` are always `proposed`;
  every other field auto-accepts only at/above `settings.sg_confidence_threshold` (default `0.9`, env-overridable,
  marked uncalibrated in the config docstring). Design call: gating is materialized at commit from the
  confidence/source the candidate carries, so the field object keeps exactly the seven keys the packet lists.
- **Dedup reconciliation:** `deduplicate_job` computes matches first and, when `BUILDING_CANDIDATES` already made a
  candidate, reconciles `kind`/`asset_id`/`dedup_matches` into it and appends collision task ids while preserving
  its fields and existing task ids. AI candidates receive matches (`test_ai_candidate_still_receives_dedup_matches`);
  the Phase-1 create path is unchanged. `dedup.py` contains no `merge`/`UPDATE` substring (existing guard test green).

## G2 — provenance, model envelope, corrections

- `_create_asset_for_candidate` unwraps the provenance object (or a plain Phase-1 scalar), derives `source_type`
  (`"extraction"` for AI, `"deterministic"` otherwise), writes `model_json` for extraction assertions
  `{provider, model, prompt_template_version, provider_call_id, evidence_ids, observation_ids}`, and applies the
  gating rule. No migration — `assertion.model_json` already exists.
- **`assertion_service.py` needed no change (finding 3).** `upsert_assertion` already supersedes the prior
  `accepted` assertion, writes a new `accepted` one and records `assertion.upsert`; the tested correction path
  (`PATCH /v1/assets/{id}`) rides it. The candidate-commit path is initial creation (no prior assertion to
  supersede), so there is no bypass to extend. `test_correction_chain_supersedes_and_audits` proves
  `{superseded, accepted}` + the audit row.

## G3 — review workspace: ZERO change

`CandidateCard.fieldInfo` (`:4-14`) already unwraps `{value, confidence, source_type}` and `api/types.ts`
`CandidateField` already permits the object; `ProvenanceBadge` renders states unchanged. No frontend file was
touched; no gap found. (Contract, not redesign.)

## G4 — tests + carried fixes

- NEW `backend/tests/test_ai_pipeline.py` — **11 tests**, all offline/scripted: low-risk auto-accept + model
  envelope; expiry always `proposed` (negative); `needs_evidence` → no date, manual-entry task, unknowns preserved,
  commit yields no expiry assertion; correction chain; default-config skip; multi-item preserved + blocking task →
  resolve → accept → commit; one `provider_call` row per call (all §3.3 fields + `job_id`, redacted PNG + versioned
  prompt asserted pre-"send"); real provider id without consent skips and never networks; one-repair-then-success;
  second-failure FAILED step; AI candidate dedup reconciliation.
- Goldens: the packet named `test_import_jobs.py:95` and `test_phase1_e2e.py:190,226`; the **actual** step-count
  goldens also include `test_import_jobs.py:85,114,167` and `test_phase1_e2e.py:191` (finding 2). All updated
  8-step / `completed:6, total:8` and remain meaningful (the state list now carries 8 entries).
- Carried fixes: `schemas.py` docstring clause corrected to "raises `ExtractionFailedError`, chaining the original
  error as its cause"; `test_opencode_go.py::test_config_readback_new_values` no longer `importlib.reload`s the
  shared `app.config` module — it reads a fresh `Settings()` and asserts the original object identity in `finally`.
  Proof: both previously-polluted migration tests are green in a plain full-suite run from `backend/` (verify log).
- FAIL-then-PASS: PRE (implementation stashed, test present) `11 failed`; POST `11 passed`; both raw runs in
  `SG-028_verify.log` (`PG-EV-01`/`PG-EV-09`). Full suite, `ruff`, `mypy` and config read-back quoted there.

## G5 — worklogs

`docs/worklogs/SG-028.log`, `SG-028_report.md`, `SG-028_verify.log` — first token `SG-028`; per-leg
elapsed-vs-budget with units; model/effort from process arguments; spend line ($0); live-state ledger; three
UNCLEAR lines below.

## G6 — receipt note (G6 runs after this commit; see delivery message)

Push the work to `automation`, worktree clean, no push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note
added on the work HEAD LAST:

```
git notes --ref=refs/notes/storagegenie-coder-reports add \
  -m "Dispatch-ID: SG-028 | Report: docs/worklogs/SG-028_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
```

Verified with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>`; executed output quoted in
the delivery message. Existing-note refusal is a STOP (never force-replace). Final line: `note=yes`.

## Findings, disagreements, corrections (including out-of-scope)

1. **Test-isolation fragility, exposed and fixed (in-slice).** The suite binds `app.config`/`app.db` from whichever
   test module first imports `app` during collection; three modules set `DATABASE_URL`/`STORAGE_ROOT` at import.
   Adding `test_ai_pipeline.py` (alphabetically first) shifted the winner to the default URL and briefly broke
   `test_health` (2) and the `test_assertions`/`test_assets_crud` fixtures (3 setup errors). Fixed by giving the new
   file the repo's own temp-root preamble (same pattern as `test_assertions`/`test_assets_crud`/`test_health`).
   This is a pre-existing ordering hazard, not a slice defect; destination: a future test-infra slice could make
   `app.db` lazy instead.
2. **Packet golden list was incomplete.** `test_import_jobs.py:95` is not the only 6-step assertion in that file
   (`:85`, `:114`, `:167` also), and `test_phase1_e2e.py:191` (`len(...) == 6`) sits beside `:190`. Corrected by
   updating all of them; this is a premise difference, not a scope expansion.
3. **G2: no `assertion_service.py` change was required.** Existing `upsert_assertion` already implements
   supersede + new accepted + audit; verified there is no bypass in the tested correction path. The file is in the
   ceiling but unused this slice.
4. **Gating is materialized at commit, not stored on the field object.** Keeping the field provenance to exactly
   the seven keys the packet lists meant the gating decision is computed at commit from the carried confidence and
   field path (`GATED_FIELDS` + `sg_confidence_threshold`). Behavior is what the acceptance tests check
   (committed assertion `review_state`); the candidate stays inspectable via confidence/source.
5. **`needs_evidence` opens a blocking `expiry.manual_entry` task on the candidate.** With no asset yet, the task's
   `subject_ref` is the candidate id; resolving it via the existing API unblocks commit. This preserves §9.3 (never a
   guessed date) using the same task kind as the SG-026 bridge. Destination: SG-030 may refine the post-commit UX.
6. **`sg_provider_id="fake"` is not a usable enabled path.** The shipped double is deliberately schema-invalid, so
   enabling AI with the default provider fails validation (by design). Tests inject `ScriptedProvider`. Destination:
   README/SG-030 runbook.
7. **`.env.example` not touched.** The two new setting names (`SG_CONFIDENCE_THRESHOLD`, `SG_PROMPT_CATEGORY`) are
   not documented there because the ceiling did not list the file. Destination: the next env-touching slice.

## UNCLEAR

- **FIRST READ:** whether G2 wanted `assertion_service.py` changed for its own sake or only if a bypass existed.
  Read as the latter (existing upsert already supersedes + audits) and reported (finding 3).
- **DURING EXECUTION:** whether the `needs_evidence` manual-entry task should block candidate commit or be
  informational only. Chose blocking via the existing resolve API to keep §9.3 strict; reported (finding 5).
- **REMAINING:** the owner's/Architect's disposition of the two decoder environment reds (unrelated to this slice)
  and of the new `candidate.multi_item` / candidate-subject `expiry.manual_entry` task kinds.

## Acceptance criteria mapping

- Starting tree clean (quoted); all G0 premises re-verified with quoted reads; differences reported (findings 1-7).
- Steps in blueprint order; default-off proved (no call/ledger/AI field); enabled path offline end-to-end with one
  repair max and fail-loud second failure.
- Gating negative tests; provenance envelope (`source_type` derived, `model_json` populated); correction chain
  auditable (superseded + new accepted + audit rows).
- Exactly one `provider_call` per AI call with `job_id`; multi-item preserved + blocking task; `needs_evidence` →
  manual-entry task, no guessed date.
- Goldens updated meaningfully; both carried fixes done with full-suite proof; FAIL-then-PASS both raw; suite/ruff/
  mypy quoted; model+effort provenance quoted; zero network calls proven; no vacuous pass.
