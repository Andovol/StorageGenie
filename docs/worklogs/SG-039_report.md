# SG-039 report — Phase 3 exit E2E + runbook + close-out: GREEN

**BASE REF:** `automation` → resolved commit `68f905a03861f699d41600e63b0d239b5386f91e` (two fields, as required).
**WORK_HEAD:** the commit carrying this file (hash quoted by the G6 receipt note; the note is added last, no commit after).
**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`.
**Model/effort per `CO-78` (from process arguments / provider metadata, never an identity line):** process argv
`opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet>"` → effort `medium`; the model flag
is absent from argv (packet: CLI default, omitted per policy). Provider metadata
`providerID=opencode-go modelID=deepseek-v4.1-flash` (`~/.local/share/opencode/log/opencode.log`, read
2026-09-14 11:21 UTC). The adapter's **provider-returned** model in the live leg was
`deepseek-v4-flash-vision-exp`.
**DATABASE:** temp SQLite only — the E2E uses per-test `tmp_path` DBs and the live leg uses its own temp DB; the
production DB was never opened for writing. **Restart:** none. **NETWORK:** exactly ONE metered live run (1 runner
run, 10 provider calls; proven count); all other gates offline with the adapter's `_post` patched to raise.

**Spend:** offline `$0`; live this leg **`$0.003849`** over 10 calls (ceiling `$0.05`); stage metered before this
leg **`$0.0009053`** (SG-037 `$0.000722` + SG-038 `$0.0001833`, matching the committed worklogs) → **Phase 3
metered total `$0.0047543`**; committed durable eval ledger `$0.0023285` (SG-029, Phase 2).

## Verdict

GREEN. The Phase 3 exit bar is proved in one offline E2E on the real HTTP path: `backend/tests/test_phase3_e2e.py`
(15 tests, one fixture, temp SQLite/storage, one scripted provider through the ONE `provider_registry` seam, the
real adapter's `_post` patched to raise, `network_attempts == []` asserted). It covers all six G1 groups by VALUE:
the usability block (picker round-trip + `422` + key-exclusion; split full coverage + partial `422`-creates-nothing
+ per-item child fields; manual expiry on a `needs_evidence` asset; correction-chain supersede + audit), planning
(pending suggestion + backing refs + `suggestion` row; confirm/dismiss + illegal `422`; dismiss-with-reason
`correction` row; no execution path), chat (grounded scoped answer; unsupported `422`; cross-category isolation;
user-only correction; model output writes nothing), cosmetics + opened-date (gated persisted `opened_date`; planning
backing ref + chat grounding carry it; a null item stays null), the guardrail log, and the default-off skip shape.
Non-vacuity is proved by **three source-mutation proofs** (split coverage, correction-chain supersession,
guardrail write), each caught and reverted clean, raw in `SG-039_verify.log` §3–§5 — the packet's source-mutation
posture, applied instead of a fabricated pre-fix failure (the flows already shipped). The deferring cosmetics
accuracy leg ran exactly once: **`TOTAL_SPEND=$0.003849` of `$0.05`**, all 10 calls on
`deepseek-v4-flash-vision-exp`, the 3 cosmetics fixtures read item+opened-date correctly (`items=1.00` each). README
carries the appended Phase 3 runbook + non-goals. Full suite `2 failed, 180 passed` (the 2 are the base-proved
decoder environment reds, **re-verified at base `68f905a`**); `ruff` clean; `mypy` 40 errors in 9 files (delta 0);
frontend diff empty; no migration; no frozen-prompt diff; secret scan 0; no ignored file staged.

## Premise findings (verified in-slice; corrections are findings, not obstacles)

1. **`F-SG039-1` — chat cannot carry a Cosmetics asset.** `chat/service.py:53-56` `SUPPORTED_CATEGORIES` is
   `{food, medicine}` only, so `POST /v1/chat/cosmetics` is an enforced `422`. G1 group 4's "the chat/planning
   catalogue carries it" is satisfiable only for **planning** (its `build_catalog` is category-agnostic) and for
   **chat on a Food/Medicine-classified asset**. I proved exactly that instead of pretending a cosmetics chat
   exists: the cosmetics asset's persisted `opened_date` reaches the planning catalog and a planning suggestion's
   backing refs, and the chat grounding carries a persisted `opened_date` for a Food asset (the cosmetics chat
   route is asserted `422`). This matches the approved SG-038 scope (Food, then Medicine).
2. **`F-SG039-2` — there is no durable `provider_call` DB table in this sandbox.** `data/db/storagegenie.db` has no
   `provider_call` table (it is at an early schema), and the SG-037/038 temp DBs under `/tmp/opencode` are gone. The
   only committed, queryable `provider_call` ledger is the SG-029 eval fixture `provider_calls` telemetry; the
   packet's expected `$0.0009053` lives in the committed worklogs, not a table. I read the table I could
   (`sum=$0.0023285`, 7 rows, quoted) and reconciled it with the worklog figures — see G2.
3. **`F-SG039-3` — the full-corpus worst-case bound exceeds the printed ceiling.** Summing `2*estimate` over the 10
   SG-029 fixtures is **`$0.081904 > $0.05`** (`ceiling_check=FAIL`, quoted in the verify log). `eval/run.py` guards
   **per fixture** (`spent_actual + 2*estimate > ceiling` → abort), so the run completed at actual `$0.003849`.
   A "cosmetics-only" reading was not runnable: the runner hardcodes `CORPUS_DIR`/`MANIFEST_PATH` and has no
   category filter, and `check_manifest` requires the on-disk fixture set to equal the listed set.
4. **The runner rewrites fixture caches (M6 gap).** The mandated `eval/run.py --live` writes `provider_output`
   /`provider_calls` back into `backend/eval/corpus/sg029/*.json` — files the scope ceiling does not list. It wrote
   9 files (sg029-03 failed and was not rewritten). **Disposition (in-ceiling):** all 9 were reverted; the leg's
   accuracy evidence lives in this report and `SG-039_verify.log` §7. This preserves the frozen SG-029
   Food/Medicine baseline (committing would have changed reproducible offline scores) and keeps the diff to the
   three ceiling items. `SG-040`/`SG-036` precedent for disclosing a ceiling-side effect.
5. **The runner's error-cost undercount recurs.** `sg029-03-glare-food` failed `invalid_json` on both attempts and
   its two calls are ledgered with `cost=$0.000000` (the SG-029 finding 3 / `ISS-11` pattern: the failure precedes
   a completed 200 body, so usage/cost are absent). No new defect; the same destination (an adapter-touching slice)
   stands.

## G1 — the exit E2E (`backend/tests/test_phase3_e2e.py`, new)

- **One fixture**, exactly the `test_phase2_e2e.py` shape: temp SQLite + temp storage, `Household`, consent OFF /
  `fake` provider defaults, `sg_per_job_cap`/`sg_monthly_cap` `None`, `sg_confidence_threshold` 0.9; the real
  `OpenCodeGoProvider._post` is patched to raise and every test asserts `network_attempts == []`.
- **One scripted provider** implements both seam operations: `extract_items` (vision extraction + planning) and
  `extract_text` (chat), returning schema-valid `ProviderResult`s with a real (scripted) cost.
- **Group 1 — usability:** `test_settings_picker_round_trip_422_and_no_key_bytes` (GET lists
  `["deepseek-v4-flash-vision-exp"]`; PUT selects it and GET reflects it; an out-of-set id is `422`
  `application/problem+json`; the sentinel key is absent from every response byte);
  `test_multi_item_split_full_coverage_and_partial_refused` (partial `[0,1]` → `422` with candidate count
  unchanged and origin still `proposed`; full `[0,1,2]` → 3 children each with their own `display_name`/
  `expiry_date`, and the date-less child has **no** `expiry_date` key — never guessed);
  `test_manual_expiry_entry_on_needs_evidence_resolves_task` (no guessed date before entry; classify →
  `needs_evidence`; hand-entered `2030-05-06` accepted as `source_type="user"`, the manual task resolved, prior
  superseded); `test_correction_chain_supersedes_and_audits` (exactly one `accepted` + one `superseded`, the old
  value retained, `assertion.upsert` audit row, stale `If-Match` → `409`).
- **Group 2 — planning:** run → one `pending` suggestion whose `backing_refs_json` names the asset and its expiry
  assertion, plus one `suggestion` guardrail row whose `ref_ids_json` is the suggestion id; confirm then illegal
  re-confirm `422`; dismiss-with-reason `correction` row with the reason; illegal re-dismiss `422`;
  `test_planning_run_mutates_no_catalogue_state` proves assets/assertions/review-tasks byte-identical before/after
  (no execution path).
- **Group 3 — chat:** grounded answer through `extract_text` for `food`; the grounding contains the food asset and
  **not** the medicine asset; unsupported `snacks` `422` (answer and corrections) with no provider call; a hostile
  model answer writes **zero** guardrail rows; the explicit correction route writes exactly one `correction` row
  with `{message, category, source:"user"}`; assets/assertions unchanged.
- **Group 4 — cosmetics + opened-date:** a Cosmetics extraction carrying `opened_date` reaches a persisted
  `opened_date` assertion after candidate accept with `source_type="extraction"` and `review_state="proposed"`
  (gated), and the planning catalog carries `opened_date` + `opened_assertion_id`; a planning suggestion naming the
  asset carries the opened-date assertion ref; an item without an opened date writes **no** assertion and the
  catalog stays `null`; the chat grounding carries a persisted `opened_date` for a supported category.
- **Group 5 — guardrail log:** `suggestion` and `correction` rows both exist with readable `ref_ids_json` /
  `detail_json`; the planning list route returns the suggestion with its backing refs.
- **Group 6 — default-off unchanged:** with the shipped defaults, planning returns
  `{"status":"skipped","reason":"consent_disabled",...}`, chat returns `{"status":"skipped","reason":"consent_disabled"}`,
  and the import pipeline's skip shape is exactly Phase 1's:
  `ANALYZING_WITH_AI → {"status":"skipped","reason":"consent_disabled"}` and
  `BUILDING_CANDIDATES → {"status":"skipped", ...}` — **0** `provider_call`, `guardrail_event`,
  `planning_suggestion` rows.

**Non-vacuity:** three source-mutation proofs, each applied alone, caught by the named E2E test, then reverted
clean (raw in `SG-039_verify.log` §3–§5): (A) split coverage `!=`→`>` → partial split returned `200` and created
children instead of `422`; (B) `prev.review_state="superseded"`→`"accepted"` → `['accepted','accepted']` instead of
one superseded; (C) suppressed the chat correction write → `{'suggestion'}` instead of `{'suggestion','correction'}`.
`git diff --stat` was empty between/after each revert.

## G2 — the cosmetics accuracy leg (ONE metered run) + stage tally

- **Ceiling printed/checked before the run** (`PG-SC-09`): the cumulative worst-case bound over 10 fixtures is
  `$0.081904` (`ceiling_check=FAIL`); the runner's own per-fixture guard (`SPEND CEILING=$0.05; mode=live
  provider=opencode-go`) governed the run, which finished at **`TOTAL_SPEND=$0.003849 of ceiling $0.05`**.
- **The run** (`SG_CONSENT=true SG_PROVIDER_ID=opencode-go venv/bin/python backend/eval/run.py --live`, from the
  repo root so `.env` supplies the key; the key was never printed): 1 runner run, **10 calls**, all
  `model=deepseek-v4-flash-vision-exp`; per-call model/latency/usage/cost quoted in `SG-039_verify.log` §7. One
  fixture (`sg029-03-glare-food`) failed `invalid_json` on both attempts and is ledgered at `cost=$0.000000`.
- **Cosmetics (the deferred leg):** `sg029-08-clean-cosmetics` **$0.000873**, `sg029-09-no-date-visible-cosmetics`
  **$0.000457**, `sg029-10-partial-label-cosmetics` **$0.000420** (subtotal **$0.001750**). Scores **0.667 each**,
  `needs=1`, `items=1.00` — the model read every name and the printed `opened_date` (`2031-04-10` on the clean
  fixture) correctly; the `0.667` is the strict `unknowns` set-match (the model also flagged `items.0.date_type`),
  the same metric-precision artifact recorded in SG-029 finding 5, **not** an extraction miss.
- **Whole-corpus figures (quoted against the committed ground truth):** `field_accuracy=0.733 over 10 fixtures`,
  `unknown_rate=2/7=0.286`, `correction_rate=0/6=0.000` (`audit_event plugin.assertion.write rows=6`).
- **Stated plainly:** the committed cosmetics `provider_output` caches are **authored offline references**, not
  model reads — their `1.000` scores are corpus-integrity evidence, **not accuracy**. This leg is the cosmetics
  accuracy evidence, and its transcript is committed in `SG-039_verify.log` §7 (the runner's fixture-cache writes
  were reverted per `F-SG039-4`).
- **Stage tally (read from the ledger, not hand-added):** `data/db/storagegenie.db` has no `provider_call` table
  (`ABSENT`); the queryable committed durable ledger (SG-029 eval fixture `provider_calls`) sums to
  **`$0.0023285` over 7 rows**. The packet's reference `$0.0009053` (SG-037 `$0.000722` + SG-038 `$0.0001833`)
  matches the committed worklogs exactly but is not in any table. This leg adds `$0.003849` →
  **Phase 3 metered total `$0.0047543`**; all metered recorded `$0.0070828`.

## G3 — runbook + non-goals (`README.md`, append-only)

Appended `## Phase 3 runbook` (what the stage added: picker, split, manual entry, corrections, planning button,
chat, cosmetics; the settings/consent switches in play — names only, never values; how to run planning and chat;
what stays OFF by default; the F2 uncapped posture with re-evaluation owed) and `### Phase 3 non-goals` (live web
enrichment/search; auto-scheduling; a second provider; streaming/persisted chat history; per-field accept UI beyond
what exists; provider analytics). The Phase 0/1/2 sections are untouched (append only; `git diff` shows only
additions past the Phase 2 closing line).

## G4 — proof + hygiene

- **Full suite** from `backend/` (600 s bound): `2 failed, 180 passed, 13 warnings in 12.31s`. The 2 reds are
  `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and
  `::test_ocr_has_text_boxes_and_mean_confidence` — **re-verified at base `68f905a`** in a detached worktree
  (`2 failed in 0.69s`, `libzbar`/`tesseract` absent), not inherited.
- **`ruff check app tests`:** `All checks passed!` (one initial `F401` in the new test — unused `SourceAttribution`
  import — was fixed; no source change).
- **`mypy app`:** `Found 40 errors in 9 files (checked 69 source files)` — base-identical (40/9); the new test is
  not under `app/` and no touched file appears in the output (delta 0).
- **Build/vitest:** frontend diff is **empty** → `npm run build` / `npx vitest run` were **not run** (SG-035/036/040
  precedent). No UI built.
- **Hygiene:** no migration (`git diff` for `backend/alembic`/`backend/app/models` empty; `alembic heads` still
  `20260914_sg035_foundations`); no frozen-prompt diff; `git diff --check` clean; no ignored file staged
  (`git status --porcelain` = `M README.md`, `?? backend/tests/test_phase3_e2e.py`); secret scan 0 real material
  (only the deliberate `sk-SENTINEL-DO-NOT-WRITE-039` fixture and doc references to `OPENCODE_API_KEY`).
- **Eval guard (verify, don't change):** `eval/run.py` `CATEGORIES` = `['cosmetics','food','medicine']`; the frozen
  prompt set is intact and versioned (`extract-food-v1` / `extract-medicine-v1` / `extract-cosmetics-v1` /
  `planning-v1` / `chat-v1`). No change was needed.
- **Health probe — `unanswered`:** `docker compose ps` lists 0 services; ports 8000/8001/8002 answer foreign
  services (`Not Found`), 8003 refuses. No stack runs and starting one is deploying (out of scope per the
  privileged-denial path).

## G5 — worklogs (unconditional, `CO-57`)

`docs/worklogs/SG-039.log`, `SG-039_report.md`, `SG-039_verify.log` — first token `SG-039`; elapsed-versus-budget
per leg with units; model/effort provenance; spend lines; live-state ledger; three UNCLEAR lines; the live
transcript and tally are in the verify log.

## G6 — receipt note on the notes ref (proven shape, unchanged obligation)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
Note added on the work HEAD LAST (120 s bound):

```
git notes --ref=refs/notes/storagegenie-coder-reports add \
  -m "Dispatch-ID: SG-039 | Report: docs/worklogs/SG-039_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`); verified with `show <WORK_HEAD>`; executed output
quoted in the delivery message. Final line: `note=yes`.

## Budget — actual vs bound (per leg, units, `PG-PR-06`)

| Leg | Actual | Bound |
|---|---|---|
| Premise probes (reads) | ~180 s wall | 120 s/probe |
| E2E first run + mutation proofs | 2.14 s / 3 mutation runs 0.84+0.76+0.86 s | 600 s suite class |
| Full backend suite | 12.31 s (14.3 s wall) | 600 s |
| Base worktree decoder reds | 0.69 s | 600 s |
| Live ceiling pre-check | <1 s | 120 s |
| Live leg (10 calls) | ~40 s call wall | $0.05 / run |
| `ruff` / `mypy app` | <1 s / few s | 120 s / 300 s |
| Frontend build/vitest | not run — empty diff | 600 s / 600 s (unused) |
| Overall session | ~840 s at log capture | 1800 s early-close / 2400 s overall |

## Live-state ledger

- Live spend this leg: **`$0.003849`** (1 runner run, 10 provider calls, ceiling `$0.05`); stage metered before this
  leg `$0.0009053`; **Phase 3 metered total `$0.0047543`**.
- Offline spend: **`$0`** (all offline gates zero network; adapter `_post` patched to raise, `network_attempts == []`).
- Network attempts: exactly the live leg's **10** calls (proven count; offline tests assert 0).
- Live DB writes: **0** to production — the E2E uses per-test `tmp_path` SQLite; the live leg used its own temp DB
  created by `eval/run.py` (`_live_session`, a `/tmp/…` SQLite); the production path was never opened for writing.
- Key: read from the host `.env` by the adapter only; **never printed/logged** (no key material in any output).
- Services deployed/restarted: **0**. Frozen-prompt byte changes: **0**. Committed eval fixture cache changes: **0**
  (reverted).

## Findings, disagreements, corrections (including out-of-scope)

1. **`F-SG039-1` (cosmetics has no chat).** `POST /v1/chat/cosmetics` is `422`; the packet's "chat/planning
   catalogue carries it" is only true for planning, and for chat on a Food/Medicine asset. Proved honestly.
2. **`F-SG039-2` (no durable `provider_call` table).** The packet's ledger premise is not reproducible in this
   sandbox; the tally is reported from the committed fixture ledger + the committed worklog figures.
3. **`F-SG039-3` (full-corpus worst-case > ceiling).** The cumulative bound is `$0.081904`; the run stayed under
   on actual ($0.003849) thanks to the runner's per-fixture guard. A cosmetics-only run is not expressible without
   changing `eval/run.py` or the manifest.
4. **`F-SG039-4` (runner writes outside the ceiling, M6).** `--live` rewrites `backend/eval/corpus/sg029/*.json`;
   reverted, evidence carried in the worklog. Ceiling preserved.
5. **Out-of-scope observation — field_path namespacing inconsistency** (carried from SG-040): candidate-derived
   `expiry_date`/`opened_date` are bare while the plugin stores
   `plugin:expiry-tracker/expiry_date`. Consumers already handle both read sites; a future consistency slice may
   unify them.

## UNCLEAR

- **FIRST READ:** whether G1 group 4's "the chat/planning catalogue carries it" intended a Cosmetics chat that does
  not exist (`F-SG039-1`), or whether "chat" was shorthand and Food/Medicine grounding plus planning is the
  accepted proof. I proved the latter and asserted the `422`.
- **DURING EXECUTION:** whether the mandated `--live` should have been scoped to the 3 cosmetics fixtures only.
  The runner has no category filter and its cumulative worst-case bound exceeds the printed ceiling
  (`F-SG039-3`); I ran the literal command, watched the actual stay under `$0.05`, and reverted the cache writes
  (`F-SG039-4`).
- **REMAINING:** the disposition of the 2 base-proved decoder environment reds; whether the committed cosmetics
  caches should be replaced with the live reads in a dedicated corpus-refresh slice; and whether `opened_date`
  needs a per-field accept UI beyond the gated `proposed` state.

## Acceptance criteria mapping

- Starting tree quoted clean; every premise verified with quoted reads (incl. three premise findings). **Met.**
- The E2E proves each exit-bar item on the real HTTP path with zero network, by VALUE; default-off unchanged; three
  source mutations caught and reverted clean, raw committed. **Met.**
- The cosmetics live leg ran exactly once under the printed ceiling with per-call figures and accuracy quoted; the
  stage tally is read from the queryable ledger and quoted. **Met.**
- README carries the Phase 3 runbook + non-goals, append-only. **Met.**
- Suite green modulo the 2 base-proved decoder reds (re-verified at base); `ruff` clean; touched files add zero
  mypy errors; secret scan 0; no migration; no frozen-prompt diff; MODEL+effort provenance quoted; no vacuous
  pass (mutation proofs). **Met.**

## Stage exit material (blueprint §14 Phase 3, `blueprint:531`)

| Exit-bar item | Evidence that proves it | Limit for the verdict |
|---|---|---|
| Daily planning suggestions functional | `test_planning_run_writes_pending_suggestion_backing_refs_and_row`, `..._confirm_dismiss_and_illegal_moves`, `..._run_mutates_no_catalogue_state` | Suggestions are model-chosen `kind`; confirm/dismiss only, no execution. |
| Category chat functional | `test_chat_grounded_answer_scoped_by_category`, `..._correction_is_user_only_and_model_output_writes_nothing` | Food + Medicine only; Cosmetics has no chat route (`F-SG039-1`). |
| Guardrail rollout tracking (§10) active | `test_guardrail_log_rows_readable` (`suggestion` + `correction` rows with refs/detail); planning + chat correction rows in groups 2–3 | Append-only rows exist and are readable; no analytics. |
| Usability block shippable on screen | Group 1 tests (picker / split / manual entry / correction chain) via the shipped endpoints | The screens themselves were built+unit-tested in SG-031/033/034; this E2E re-proves the behaviour on the HTTP path, not the pixels. |
| Cosmetics tracked with opened-date | `test_cosmetics_extraction_persists_opened_date_after_accept`, `..._item_without_opened_date_stays_null`, `..._planning_carries_persisted_opened_date_in_backing_refs`, `..._chat_catalogue_carries_opened_date_for_supported_category`; live cosmetics leg (3 fixtures, `items=1.00`, `$0.001750`) | Accuracy is a 3-fixture synthetic sample scored with a strict-`unknowns` metric (0.667 each; items 1.00). |
