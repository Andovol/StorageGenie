# SG-029 report — Food/Medicine eval corpus + first metered baseline: GREEN

**BASE REF:** `automation` → resolved commit `b334a971f12cd0225580a99e2c56fe0841fae39b` (two fields, as required).
**WORK_HEAD:** the commit carrying this file (hash quoted by the receipt note in G6; note added last, no commit after).
**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`.
**Model/effort per CO-78 (from process arguments / provider metadata, never an identity line):** process argv
`opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet>"` → effort `medium`; the model flag
is absent from argv (packet: CLI default, omitted per policy). Provider metadata
`providerID=opencode-go modelID=deepseek-v4.1-flash` (`~/.local/share/opencode/log/opencode.log`, Coder stream
lines). The adapter's **provider-returned** model in the metered run was `deepseek-v4-flash-vision-exp`.
**DATABASE:** none — temp SQLite only, zero live rows (the live `/data/db/storagegenie.db` was never opened).
**Restart:** none. **NETWORK:** only the metered corpus run's provider calls (7 in the successful run; 2 in the
aborted first attempt). No other network attempt.
**Spend:** $0.002328 led across 7 calls (ceiling $0.05); the aborted attempt's 2 calls incurred usage that the G0
error ledger records as `cost=0.0` (finding 3), estimated ≤ $0.0008 — total ≪ ceiling.

## Verdict

GREEN. G0 repairs both money-instrumentation gaps SG-028 left (caps can refuse from the pipeline; failed calls are
ledgered and survive the step rollback), proven FAIL-then-PASS offline. The synthetic Food+Medicine image corpus
ships with a manifest, ground truth, expectation classes and committed `provider_output` caches. One metered run
produced the first measured numbers — `field_accuracy=0.762`, `unknown_rate=2/5=0.400`, `correction_rate=0/4=0.000`
— inside the $0.05 ceiling at $0.002328. **Prompt v1 is FROZEN; no v2 recommended** (the two non-perfect cases are
a too-weak glare rendition and scorer strictness on the `unknowns` set, not prompt defects). Full suite
`2 failed, 106 passed` (the two reds are the base-proved decoder environment legs); `ruff` clean; `mypy` 40 errors
(identical to base, none in touched files); no migration; no prompt file changed; secret scan 0.

## G0 — money-instrumentation repair (offline, FIRST)

- **Caps can now refuse before a call.** `reader._estimate_call` reads the adapter's bounded worst-case estimate
  (`opencode_go.estimate_call_cost`, derived from the vendor rate table: input ≤ one token/source-byte + base64
  body, output ≤ `max_tokens`; no clock, no network) and passes it to `ProviderRouter.execute(estimated_cost=...)`,
  which checks it against `RouterConfig.cost_budget` (from `sg_per_job_cap`) **before** resolving/calling the
  provider. Proof `test_cap_binds_from_pipeline_zero_calls_zero_rows`: with cap `0.01 < estimate 1.0` the step
  FAILS with `estimated cost 1.0 exceeds budget 0.01`, the provider is invoked **0** times, **0** `provider_call`
  rows are written, and there is no network. With caps `None` (F2 default) behavior is unchanged (all other
  pipeline tests green).
- **Failed/errored calls are ledgered and durable.** `reader._write_error_ledger` writes a `provider_call` row with
  `error_state` populated and `db.add` + **`db.commit()`**, so the later `run_job` rollback cannot erase it; a budget
  refusal (`BudgetExceededError`, not a `ProviderError`) writes no row. Proof
  `test_provider_error_is_ledgered_and_survives_rollback`: a scripted provider failing both attempts leaves exactly
  **2** rows with `error_state` containing `invalid_json`, job FAILED, step FAILED persisted. Both proofs FAIL
  pre-fix (raw runs in `SG-029_verify.log` §1) and PASS post-fix (§2); the existing
  `test_repair_once_then_success` expectation moved 1→2 rows because a repaired first attempt is now itself ledgered
  (finding 2). One behavior change beyond the literal G0: the reader's §5.3 retry now carries a real correction turn
  (`reader.repair_prompt`) instead of a blind re-send (finding 1).

## G1 — image corpus (`backend/eval/corpus/sg029/`)

- 7 synthetic fixtures: clean (food, medicine), glare (food), clutter (food), partial-label (food, medicine),
  no-date-visible (medicine) — both categories, all five case shapes, hard/expected-unknown cases present. Each
  carries `id`, `class`, `category`, `image`, `note`, `ground_truth` (`items`/`unknowns`/`needs_evidence`/
  `expectation_class`) and, after the metered run, a committed `provider_output` cache + `provider_calls` telemetry.
- Images are deterministic PNG renders from the committed `generate.py` (fixed canvas, fixed dates, seeded clutter),
  **zero EXIF/GPS**, no personal image, no `/data/storage` read; the shared `redact_image` is a second byte-level
  guarantee at call time (`PG-EV-07`).
- `manifest.json` is the count authority. `backend/tests/test_eval_corpus.py` (new, 6 tests) proves: manifest count
  == committed files; every fixture has image+truth+expectation class+category; ids unique; both categories and all
  five shapes present; ≥1 hard case; images are PNG with `getexif() == {}`; every `provider_output` parses strictly;
  and **the scorer discriminates** (a constructed guessed-date-against-unknown case scores `< 1.0`).
- Layout decision (finding 6): the legacy 5 SG-026 provider-output smoke fixtures stay in `corpus/*.json` (the
  untouched `test_extraction_contract.py::test_corpus_integrity` asserts exactly 5); the SG-029 image corpus lives in
  `corpus/sg029/`, and `run.py` reads the manifest instead of the hardcoded `!= 5`.
- Natural discrimination also occurred in the real run: `sg029-03-glare-food` scored 0.000 because the model read a
  date the authored ground truth called unknown.

## G2 — the runner (`backend/eval/run.py`)

- Offline (default): manifest-driven integrity checks, strict-parse scoring of the committed `provider_output`
  cache (reused SG-026 scorer; name comparison normalized case/whitespace), needs_evidence bridge in a temp-SQLite
  sandbox, and field-accuracy / unknown-rate / correction-rate output. Reproduces the metered numbers exactly (§5).
- Live (`--live`): per fixture → read committed image → `reader.load_prompt(category)` (versioned file) →
  `reader.run_ai_extraction` (the ONE SG-028 reader path: shared `redact_image`, router, strict parse with the single
  §5.3 repair, per-call ledger) → cache the validated output into the fixture JSON → score. Category is selected by
  mutating `settings.sg_prompt_category` per fixture (the packet's allowed `category` parameter — reported).
- Every call prints provider-returned model, latency, usage and cost; the ceiling `$0.05` is printed and checked
  before each fixture (`spent + 2*estimate > ceiling` → abort). The run completed with total `$0.002328 / $0.05`.
- Consent/provider came from the environment for the one command (`SG_CONSENT=true`,
  `SG_PROVIDER_ID=opencode-go`); the key came from the host `.env` via the adapter and was never printed. A failed
  fixture is now recorded and the run continues (the first aborted attempt exposed the missing guard).
- `reader.run_ai_extraction` was also smoke-tested offline end-to-end against a scripted provider on a temp corpus
  copy (no committed-file mutation, no network) before the real spend.

## G3 — proof

- Offline: corpus integrity green; discrimination green; offline scoring reproducible from the cache (§5);
  `PG-EV-04` proven by `test_provider_call_ledger_row_per_call_with_job_link` — the exact bytes handed to the
  provider are a redacted PNG (`\x89PNG…`, `dict(getexif()) == {}`) and the prompt is exactly
  `extract-food-v1.md` (`SG-029_verify.log` §8).
- Metered: one successful run, transcript quoted in `baseline_sg029.md` / `SG-029_verify.log` §7 with per-call
  provider-returned model `deepseek-v4-flash-vision-exp`, latency, usage, computed cost, validated-parse result,
  and total vs ceiling. G0 tests green; full suite `2 failed, 106 passed` (base-proved reds red); `ruff` clean;
  `mypy` quoted; secret grep 0 (and all 256 tracked files scanned for the literal key → NONE); no migration; no
  prompt diff; no ignored file staged.

## G4 — baseline report

`backend/eval/baseline_sg029.md` — numbers, per-fixture observed reasons, per-call spend and total, corpus manifest,
and the verdict: **prompt v1 frozen, no v2 recommended**; the two non-perfect cases are corpus-rendition and
scorer-precision follow-ups, not prompt defects.

## G5 — worklogs (unconditional, `CO-57`)

`docs/worklogs/SG-029.log`, `SG-029_report.md`, `SG-029_verify.log` — first token `SG-029`; per-leg elapsed-vs-budget
with units; model/effort from process/provider metadata; spend lines; live-state ledger; three UNCLEAR lines.

## G6 — receipt note (runs after this commit; see delivery message)

Work pushed to `automation`, worktree clean (`CO-55`), no push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
Note added on the work HEAD LAST (120s bound):

```
git notes --ref=refs/notes/storagegenie-coder-reports add \
  -m "Dispatch-ID: SG-029 | Report: docs/worklogs/SG-029_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`); verified with
`git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>`; executed output quoted in the delivery
message. Existing-note refusal is a STOP. Final line: `note=yes`.

## Findings, disagreements, corrections (including out-of-scope)

1. **Provider output can be two concatenated JSON objects.** The first metered attempt failed on fixture 1: the
   model returned `{"type": "json_object"}{…payload…}` (it repeats the requested `response_format` before the real
   payload). `parse_extraction_output` rejects it (`Extra data`), and the existing "repair" re-sent the identical
   prompt, so both attempts failed identically. The adapter's own parsing is **outside this slice's ceiling**, so the
   in-scope **reader** now sends a genuine §5.3 repair turn (`reader.repair_prompt`, a runtime correction message,
   not a prompt-file edit). The successful run needed no repair (each call validated on attempt 1). Destination: if
   it recurs, an adapter-tolerance/provider-config slice.
2. **An existing test's expected row count changed by mandate.** `test_repair_once_then_success` now expects 2 rows
   (1 error + 1 success) instead of 1, because G0 requires every failed call to be ledgered. This is the packet's
   required behavior, not a workaround.
3. **Error-ledger cost/usage is 0 before a completed 200 body.** The aborted attempt's 2 provider calls incurred
   real token usage, but the adapter raises before `compute_cost` and does not attach usage to the `ProviderError`,
   so the error rows record `cost=0.0`. Fixing it means attaching usage/cost to `ProviderError` in the adapter
   (out of this ceiling). Destination: the next adapter-touching slice.
4. **The glare rendering is too weak.** The model read the rendered date through the semi-transparent glare, so the
   authored `unknown-expected` truth penalises a correct read. Destination: corpus refinement (opaque glare or a
   legible-date truth).
5. **`unknowns` set-equality is strict.** The two partial/no-date fixtures scored 0.667 only because the model also
   flagged `items.0.date_type`; the prompt's own rule 6 ("one entry per unrecoverable field") arguably requires it.
   Destination: metric refinement.
6. **Corpus layout keeps the legacy smoke set intact.** The SG-029 corpus is under `corpus/sg029/` so the
   out-of-ceiling `test_extraction_contract.py::test_corpus_integrity` (`== 5`) stays green unedited; `run.py` uses
   the manifest count. Recorded as a premise difference from a literal "replace".
7. **Adapter-internal cap still receives `estimated_cost=0.0`.** `ProviderRouter.execute` consumes `estimated_cost`
   for its own pre-call check and does not forward it to `extract_items`. The binding refusal G0 requires is the
   router's, which is correct; `router.py` is outside the ceiling, so it was not changed.
8. **`provider_registry()` still builds the adapter with `session_id="storagegenie-sg028"`.** Cosmetic/stale
   provenance, not edited (scope). Destination: the next reader-touching slice.

## UNCLEAR

- **FIRST READ:** whether the aborted first metered attempt plus the successful retry violates "exactly one run".
  Read as one *successful* baseline run with the failure and both transcripts disclosed (2 extra calls, ≈$0.0008);
  reported here rather than hidden.
- **DURING EXECUTION:** whether the `{"type": "json_object"}` wrapper should be fixed in the adapter; read as
  outside the ceiling, so it was handled in the in-scope reader as a real repair turn (finding 1).
- **REMAINING:** the owner's/Architect's disposition of the two base-proved decoder environment reds, and of the
  corpus-rendition / scorer-precision / error-cost follow-ups above.

## Acceptance criteria mapping

- Starting tree quoted clean; BASE resolved and stated (two fields); G0 proofs first, both FAIL before the fix and
  PASS after, both raw runs in the verify log.
- Corpus: both categories, five case shapes, every fixture with image + truth + expectation class + category;
  integrity test green; scorer shown to discriminate; synthetic/no-personal-data proven; manifest count authority.
- Runner: offline reproducible from the cache; metered mode reuses the reader path with the shared redactor and the
  versioned prompt; per-call cost printed; ceiling printed and honored ($0.002328 / $0.05).
- Metered: one successful run; transcript quoted with provider-returned model id, latency, usage, cost; total ≤
  $0.05; FAIL-then-PASS for the new offline tests; suite/ruff/mypy quoted; secret grep 0; no migration; no prompt
  file changed (empty diff); no ignored file staged.
- Baseline report committed; MODEL + effort provenance quoted; no vacuous pass (discrimination shown on a real
  fixture and by a constructed test; the metered run quoted).
