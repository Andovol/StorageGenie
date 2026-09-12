# SG-030 report — Phase 2 exit E2E + runbook + close-out: GREEN

**BASE REF:** `automation` → resolved commit `995e69d9214c5fd08d7f06a2b8f13643db7cfbeb` (two fields, as required).
**WORK_HEAD:** the commit carrying this file (hash quoted by the G6 receipt note; note added last, no commit after).
**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`.
**Model/effort per CO-78 (from process arguments / provider metadata, never an identity line):** process argv
`opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet>"` → effort `medium`; no model flag
is present (packet: CLI default, omitted per policy). Provider metadata
`providerID=opencode-go modelID=deepseek-v4.1-flash` (`~/.local/share/opencode/log/opencode.log`, run `e589127c`).
**DATABASE:** none — temp SQLite only, zero live rows. **Restart:** none. **NETWORK:** none — zero live calls.
**Spend:** `$0.000000` (no metered run; the SG-029 numbers are carried, not re-measured).

## Verdict

GREEN. The Phase 2 exit condition is proved end-to-end **offline** in one fixture shape, the runbook the owner
needs ships, and the two latent money findings close with FAIL-then-PASS raw. ISS-10: the monthly cap now binds
**across jobs** from the durable `provider_call` ledger and refuses **before any call**. ISS-11: a call that
reached the provider and returned a body now leaves a **committed** row carrying the real cost/usage **and**
`error_state`, surviving the step rollback. `backend/tests/test_phase2_e2e.py` (new, 6 tests) proves the six
numbered behaviours on the real HTTP path with zero network attempts. Full suite `2 failed, 114 passed` (the two
reds are the base-proved decoder environment legs); `ruff` clean; `mypy` 40 errors (base-identical, none in
touched files); secret scan 0; no migration; no prompt/corpus/UI change; no ignored file staged.

## G0 — the two latent money findings (offline, FIRST)

### ISS-10 — the monthly cap binds ACROSS jobs

**Defect.** `_monthly_spent` lived on the `OpenCodeGoProvider` instance, and `provider_registry()` rebuilds that
instance at the start of every `run_ai_extraction`, so the counter reset per job and a "monthly" cap could never
see prior spend. (`ProviderRouter.execute` also does not forward `estimated_cost` to the adapter, so the
adapter's own monthly branch was dead on the pipeline path — SG-029 finding 7.)

**Mechanism (decided, not asked).** The reader derives the baseline from the **durable ledger**, not an in-process
singleton: `reader._recorded_spend` sums `provider_call.cost` joined through `job` for the household, and before
the first call of a job the reader compares `already_spent + Σ worst-case estimates` against
`settings.sg_monthly_cap`. Rationale: the ledger is the same committed figure the audit trail already carries, it
survives the per-step provider rebuild and process restarts, and it cannot be reset by constructing a new
adapter. The check runs before any `_extract_one`, so a refusal makes **0 invocations and 0 new ledger rows** and
raises `BudgetExceededError`, which `run_job` records as the step error. The adapter's instance counter is left in
place only as a direct-call guard; it is no longer the binding mechanism. `router.py` and `opencode_go.py` were
**not modified** — the ceiling allowed them but the binding did not need them.

**Proof** `test_monthly_cap_binds_across_jobs_from_durable_ledger` (two sequential offline jobs, cap `1.5`,
per-call estimate `1.0`, recorded cost `0.6`): job 1 reaches `AWAITING_REVIEW` and records `0.6`; job 2 fails its
`ANALYZING_WITH_AI` step with `monthly` in the error, `provider.invocations == 1`, and **0** `provider_call` rows
for job 2. Raw **FAIL** on the base reader (`assert 'AWAITING_REVIEW' == 'FAILED'`) and raw **PASS** after the
fix are in `SG-030_verify.log` §1/§2.

### ISS-11 — a returned body leaves a durable cost/usage record

**Defect.** `_write_ledger` wrote a success-shaped row (`error_state=None`) with `db.flush()` only. When the
returned content then failed strict schema validation on both attempts, `run_job`'s `db.rollback()` erased those
rows entirely, so a billable call could leave no record.

**Mechanism.** `_extract_one` now catches `ExtractionFailedError` and calls `_mark_calls_failed`, which sets
`error_state = "schema_validation: payload failed schema validation after the single repair"` on the returned-body
rows and **commits** them before re-raising. The rows already carry the provider's real `cost`, `usage_json`,
`output_payload` and `latency_ms` from `_write_ledger`. Budget refusals (`BudgetExceededError`) still write no row,
as required.

**Proof** `test_returned_body_failing_schema_is_ledgered_durably`: a provider returns two usage-bearing bodies that
fail validation; the job is `FAILED` and exactly **2 committed** rows exist, each with the returned
`cost == 0.0023`, `total_tokens == 18`, an output payload, and `schema_validation` in `error_state`. Raw **FAIL**
on the base reader (`assert 0 == 2` — rollback erased them) and raw **PASS** after the fix are in
`SG-030_verify.log` §1/§2.

### Default path unchanged

With `sg_per_job_cap = None` and `sg_monthly_cap = None` (F2 shipped defaults) the monthly branch is skipped
entirely, so no behavior changes. The pre-existing pipeline tests
(`test_repair_once_then_success`, `test_provider_error_is_ledgered_and_survives_rollback`,
`test_cap_binds_from_pipeline_zero_calls_zero_rows`, `test_default_config_is_phase1_skip`, all others) stay green
— `SG-030_verify.log` §2 (21 passed) and §4 (full suite).

## G1 — Phase 2 exit E2E (`backend/tests/test_phase2_e2e.py`, new, offline)

`test_phase1_e2e.py` shape: `TestClient` over the real HTTP routes, temp SQLite + temp storage, a schema-valid
scripted provider through the ONE SG-028 seam (`reader.provider_registry`). The fixture patches
`OpenCodeGoProvider._post` to raise, and all six tests assert `network == []` — the real adapter is never reached
(`PG-EV-04` shape is also asserted directly: the exact bytes sent are a redacted PNG with empty EXIF and the
prompt is exactly the versioned file, per category).

1. **AI proposes expiry candidates for Food AND Medicine** —
   `test_ai_proposes_expiry_candidates_for_food_and_medicine`: food `expiry_date=2030-01-15` and medicine
   `expiry_date=2029-11-30`, each a `fields` entry with `source_type=extraction`, provider/model/call id and
   `prompt_template_version` `extract-food-v1` / `extract-medicine-v1`; after accept, every committed gated field
   (`expiry_date`, `lot`) is `proposed`, never `accepted`, and `display_name` is an accepted extraction assertion
   with provenance.
2. **Accept commits atomically** — `test_accept_commit_is_atomic_and_rolls_back_on_forced_failure`: a wrapper
   runs the real `_create_asset_for_candidate` (proving the commit path executed) then raises; the job is
   `FAILED` and there are **0** assets, **0** assertions, and **0** `asset.*` audit rows. Proven by the rollback,
   not prose.
3. **`needs_evidence` works for real** — `test_needs_evidence_manual_entry_never_guesses`: the AI returns no
   expiry (`"expiry_date" not in proposal["fields"]`, `needs_evidence=True`); no expiry assertion exists after
   commit; the plugin classification opens the `expiry.manual_entry` task; entering `2030-05-06` through
   `POST /v1/plugins/expiry-tracker/assets/<id>/expiry` writes an accepted **user** assertion, resolves the task,
   and leaves the prior `needs_evidence` assertion `superseded`. No guessed date is manufactured anywhere.
4. **Corrections are auditable** — `test_correction_supersedes_auditably`: `PATCH /v1/assets/<id>` on the
   AI-sourced `display_name` leaves the original row `superseded` (`Whole Milk`), exactly one new `accepted`
   `user` row (`Whole Milk (corrected)`), and an `assertion.upsert` audit row — never an overwrite.
5. **`provider_call` rows per AI call** — `test_provider_call_rows_per_call_with_scripted_cost`: 2 calls → 2 rows,
   both `job_id`-linked, `error_state is None`, scripted `cost=0.0005`, usage `total_tokens=30`, output payload
   present.
6. **Default-off unchanged** — `test_default_off_is_phase1_equivalent`: with `SG_CONSENT=false` the same HTTP
   flow skips `ANALYZING_WITH_AI` (`reason=consent_disabled`) and `BUILDING_CANDIDATES`, makes **0** provider
   invocations and **0** ledger rows, and the candidate keeps the Phase-1 deterministic `display_name`. This
   extends the existing `test_default_config_is_phase1_skip` coverage to the HTTP path.

**Premise difference (reported, not bent).** The packet's G3 asks FAIL-then-PASS for *every* new test (G0 + G1).
The G1 file is a proof of the already-landed SG-028 flow, so all six tests **pass on the unmodified base tree**
(`SG-030_verify.log` §1 RUN A: `2 failed, 19 passed`). Only the two G0 tests are genuinely fail-then-pass. Rather
than manufacture a pre-fix failure, the G1 tests' sensitivity is proved by source mutations: (A) gated fields
auto-accepted → E2E #1 FAILS; (B) corrections no longer superseded → E2E #4 FAILS; (C) `run_job` rollback removed
→ E2E #2 FAILS (`SG-030_verify.log` §3, all reverted clean). This is called out as a premise difference, not
hidden.

## G2 — runbook + non-goals

- `README.md` gains a **Phase 2 runbook**: OpenCode GO setup and the key into the host `.env` (value never
  printed/logged/committed), the settings table (`SG_PROVIDER_ID`, `SG_MODEL_ID`, `SG_CONFIDENCE_THRESHOLD`,
  `SG_PROMPT_CATEGORY`, both caps, `SG_CONSENT` with cloud OFF by default), the offline and `--live` eval
  commands with the printed `$0.05` ceiling, the F2 budget posture (uncapped now, re-evaluation owed; caps exist
  and can refuse), and the **Phase 3 non-goals** ledger (web enrichment, planning/chat agents, remaining
  categories, prompt tuning, multi-provider).
- `.env.example` gains the two missing NAMES only: `SG_CONFIDENCE_THRESHOLD=`, `SG_PROMPT_CATEGORY=`.

## G3 — proof (`docs/worklogs/SG-030_verify.log`)

- **FAIL-then-PASS raw:** G0 §1 (base reader: `0 == 2`; `AWAITING_REVIEW != FAILED`) → §2 (fixed: `21 passed`).
  G1 base-pass + three mutation failures in §3 (all reverted, empty diff-stat).
- **Suite (bound 600 s):** `2 failed, 114 passed, 10 warnings in 7.40 s`; both reds are the base-proved decoder
  environment legs (`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
  `test_ocr_has_text_boxes_and_mean_confidence`; base run `2 failed, 106 passed` — same tests). No migration tests
  changed.
- **Ruff:** `All checks passed!` **mypy:** `Found 40 errors in 9 files` — identical to base, none in
  `reader.py`/`router.py`/`opencode_go.py`.
- **Read-back (`PG-SC-02`):** `SG_CONFIDENCE_THRESHOLD=0.42 SG_PROMPT_CATEGORY=medicine SG_MONTHLY_CAP=3.5` →
  a fresh `Settings()` reads `0.42 / medicine / 3.5`.
- **Scope:** changed paths are exactly the ceiling files; prompts/corpus/UI/migrations untouched (verify log §5d).
- **Secrets/network:** refined scan `0 matches`; `OPENCODE_API_KEY` `.env` line count `1` (count only, value never
  read); zero network attempts, `$0`.

## G4 — exit verdict against blueprint:522

> "AI proposes candidates including expiry dates for Food/Medicine; corrections are auditable; a working expiry
> tracker is usable end-to-end for the two initial users."

- **(a) AI proposes candidates including expiry dates for Food/Medicine — PROVED.** Food and Medicine scripted
  outputs each produce a candidate whose `expiry_date` field carries per-field provenance; the committed gated
  assertions are `proposed`, not auto-accepted. Evidence: G1 #1, `SG-030_verify.log` §2.
- **(b) corrections are auditable — PROVED.** A post-commit correction supersedes the prior assertion, leaves a
  new accepted user assertion, and records an audit row; the prior value is never overwritten. Evidence: G1 #4.
- **(c) a working expiry tracker is usable end-to-end — PROVED OFFLINE.** Upload → import → AI/`needs_evidence`
  → manual date entry through the existing plugin route → accepted user assertion, task resolved, prior state
  superseded, never a guessed date. Evidence: G1 #3.
- **Zero live calls.** This slice made no provider call: the E2E runs a scripted provider through the injection
  seam, `_post` is patched to raise, and the tests assert an empty network list. Spend `$0`.
- **Measured numbers remain SG-029's, unmodified:** `field_accuracy=0.762` (annotated for the known glare-truth
  artifact), `unknown_rate=2/5=0.400`, `correction_rate=0/4=0.000`, `$0.002328` across 7 calls. Not re-run here.
- **What is NOT yet true for the two initial users (auditable limits):** there is no UI for split/multi-item
  candidates or manual-entry-by-component (the manual-entry path exists as the plugin HTTP route only); the system
  is single-household, LAN-only, and unauthenticated; the monthly cap is uncapped by default (F2) so the refusal
  path is proven but not active in production configuration; the two decoder red nodes (`libzbar`,
  `pytesseract`) remain an environment gap from phase 0/1; corrections are API-only, not surfaced in a review UI.

## G5 — worklogs (unconditional, `CO-57`)

`docs/worklogs/SG-030.log`, `SG-030_report.md`, `SG-030_verify.log` — first token `SG-030`; per-leg elapsed-vs-budget
with units; model/effort from process args + provider metadata; spend `$0`; live-state ledger; three UNCLEAR lines.

## G6 — receipt note (runs after this commit; see delivery message)

Work pushed to `automation`, worktree clean (`CO-55`), no push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
Note added on the work HEAD LAST (120 s bound), first line carrying both `Dispatch-ID:` and `Report:` (`CO-97`),
verified with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>`; executed output quoted in
the delivery message. Existing-note refusal is a STOP. Final line: `note=yes`.

## Findings, disagreements, corrections (including out-of-scope)

1. **G1 is not fail-then-pass on base (packet G3 premise difference).** The six E2E tests prove the pre-existing
   SG-028 flow and pass unchanged on the base tree; only G0 is fix-driven. Answered with three source-mutation
   proofs instead of a fabricated pre-fix failure. Destination: packet-authoring note — proof-of-existing-flow
   files should not be held to FAIL-then-PASS.
2. **The adapter's `_monthly_spent` singleton is now redundant on the pipeline path.** The binding mechanism moved
   to the durable reader check; the instance counter cannot see across jobs and is no longer the authority. Left
   in place for direct-call safety, not edited (scope). Destination: an adapter-touching slice may remove it.
3. **`condition`/`identifier` gating could not be exercised end-to-end.** The extraction schema has no
   `condition` field and `identifier` is populated only from a validated barcode; the E2E images carry none. The
   test asserts the invariant over *present* gated fields (`expiry_date`, `lot`) rather than fabricate
   `condition`/`identifier`. Destination: barcode-bearing fixture if the Architect wants all four fields named.
4. **The packet's singular "create + run an import job" for Food+Medicine was read as one job per image.** A
   single multi-image job maps only `items[0]` onto candidate fields (the rest survive in `ai_items`), so two jobs
   are what actually gives each category per-field expiry provenance. Recorded as a premise difference.
5. **`.env` now has `OPENCODE_API_KEY` configured (count `1`), versus SG-025's `0`.** Information only per
   `CO-44`; the value was never read, printed, or logged. A live key is present on the host for a future metered
   run.
6. **`--live` remains the only spend path and was not run.** The runbook documents it with its printed ceiling;
   the mechanism was exercised offline only. Destination: owner-dispatched metered run if more numbers are wanted.

## UNCLEAR

- **FIRST READ:** whether the packet's FAIL-then-PASS requirement is meant to include a proof-of-existing-flow E2E
  file. Read as: only fix-driven tests can be fail-then-pass; G1's sensitivity is proved by mutation instead
  (Finding 1).
- **DURING EXECUTION:** whether the monthly cap should also be duplicated in `router.py`/`opencode_go.py`. Read as:
  the durable ledger-derived reader check is the single binding mechanism; router/adapter unchanged.
- **REMAINING:** owner/Architect disposition of out-of-scope items — adapter tolerance for the concatenated-JSON
  wrapper, error-cost when the adapter raises before `compute_cost`, and the missing split/manual-by-component UI.

## Acceptance criteria mapping

- Starting tree clean and quoted; BASE resolved and stated (two fields); every premise checked in-slice with
  quoted reads (reader.py, candidates.py, plugin, routes, plan, SG-029 report).
- ISS-10 and ISS-11 each closed with a FAIL-then-PASS test quoted both raw; the default uncapped/no-failure path
  proven unchanged (all pre-existing pipeline tests green).
- E2E proves all six numbered behaviours offline on the HTTP path with zero network attempts; forced-failure
  rollback asserted; `needs_evidence` never guesses; corrections supersede auditably.
- README Phase 2 runbook + Phase 3 non-goals present; `.env.example` names added; no prompt/corpus/migration/UI
  change.
- Exit verdict maps blueprint:522 clause by clause with evidence and limits; zero live calls stated; SG-029
  numbers carried unmodified.
- Suite/ruff/mypy quoted; secret scan 0; MODEL + effort provenance quoted; no vacuous pass (G1 mutation proofs,
  forced-failure rollback, no-op-verify coverage).
