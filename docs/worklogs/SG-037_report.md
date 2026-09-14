# SG-037 report — Daily Planning Agent on a button, Stage 0: GREEN

**BASE REF:** `automation` → resolved commit `c251463cd418beb97b29fada27d0318c5a8a43df` (two fields, as required).
**WORK_HEAD:** the commit carrying this file (hash quoted by the G5 receipt note; note added last, no commit after).
**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`.
**Model/effort per `CO-78` (from process arguments / provider metadata, never an identity line):** process argv
`opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet>"` → effort `medium`; the model flag
is absent from argv (packet: CLI default, omitted per policy). Provider metadata
`providerID=opencode-go modelID=deepseek-v4.1-flash` (`~/.local/share/opencode/log/opencode.log`, read
2026-09-14 10:39 UTC). The adapter's **provider-returned** model in the metered run was
`deepseek-v4-flash-vision-exp`.
**DATABASE:** temp SQLite only (`sqlite:////tmp/opencode/sg037/live.db` for the live leg); the production DB was
never opened for writing. **Restart:** none. **NETWORK:** exactly ONE metered live run (1 provider call, proven
count); all other gates offline with the adapter's `_post` patched to raise.

**Spend:** offline `$0`; live **`$0.000722`** across **1** call (ceiling `$0.05`) — total `$0.000722 / $0.05`.

## Verdict

GREEN. The manual-trigger planning pass exists end to end: `POST /v1/planning/run` reads the catalogue, is gated
by the reader seam's `ai_status()` before any call, writes `pending` suggestions with `backing_refs_json` and one
`suggestion` guardrail event, and confirm/dismiss validate the transition in service code (illegal → `422`); a
dismissal with a reason writes an append-only `correction` event. The planning screen lists suggestions with a
status filter, shows each suggestion's backing evidence, and runs/confirms/dismisses on demand. No execution path
exists: catalogue bytes are identical before/after a run (test). Full backend suite `2 failed, 149 passed` (the two
reds are the base-proved decoder environment legs); `ruff` clean; `mypy` 40 errors (delta 0); `npm run build` green;
`vitest` 33 passed; secret scan 0; no migration; no frozen-prompt diff. **One** live call at `$0.000722`.

## Premise findings (verified in-slice; corrections are findings, not obstacles)

1. **`F-SG037-1` — the seam has no text operation (load-bearing).** The only real provider operation is the
   SG-027 vision surface `extract_items(image_bytes, prompt)` (`opencode_go.py:216-258`), and it parses its
   response through the strict `ExtractionOutput` schema (`schemas.py:93-111`). There is no chat/text op
   (`protocols.py` declares `extract_items`/`extract_text`/`embed`/`search_and_summarize`, but the real adapter
   implements only `extract_items`; `extract_text` exists only on the fake). The packet's own ceiling forbids
   touching `reader.py`, `router.py`, `protocols.py`, `opencode_go.py`. **In-scope resolution (design call, per the
   packet's design-autonomy line):** the planning prompt asks the model for the same strict `ExtractionOutput`
   envelope and the service maps each returned `item` to one `PlanningSuggestion` (`lot`→asset id, `name`→title,
   `date_type`→kind, `uncertainty_reasons`→rationale); a 1×1 white PNG is sent only because the adapter's surface
   requires image bytes. Offline and live therefore share one parsing path. This is documented in
   `service.py`'s module docstring; it is not a second provider or new machinery.
2. **`F-SG037-3` — `opened_date` is not persisted.** SG-036 added `opened_date` to `ExtractionItem` and the
   cosmetics profile, but grep shows it is never written to an assertion; the catalogue therefore reports
   `opened_date: None` for every asset. The "already-opened" planning input is not yet available at the catalogue
   layer. Destination: a later slice that persists opened-date assertions; nothing here assumes it.
3. **`F-SG037-2` — the ceiling omits `frontend/src/App.tsx` (M6).** The packet's M6 line says a requirement whose
   file the ceiling does not enable is a STOP. G2's "new planning route" cannot be reachable without registering
   the route and nav link in `App.tsx` (the codebase registers every route there). I treated the 5-line
   registration as glue analogous to `main.py`'s "registration only" and included it, reporting the deviation here
   rather than stopping the whole slice on a one-file omission. If the Architect rules this out of scope, the
   screen file and tests still stand; only reachability is affected.
4. **`F-SG037-4` — no CHECK constraints, per the packet's own decision.** `planning_suggestion.status` and
   `guardrail_event.kind` are enforced in service code; illegal confirm/dismiss is an enforced `422`. No migration
   was written (`alembic heads` unchanged: `20260914_sg035_foundations`).

## G1 — planning service + routes (`backend/app/services/planning/`, `backend/app/api/v1/planning.py`)

- `POST /v1/planning/run` (manual trigger), `GET /v1/planning/suggestions` (+`status` filter),
  `POST /v1/planning/suggestions/{id}/confirm`, `POST .../dismiss` — registered beside the v1 routers in `main.py`.
- Consent first: `reader_mod.ai_status()` returns `(False, "consent_disabled")` and the route returns
  `{"status":"skipped","reason":"consent_disabled"}` with **0 provider calls and 0 rows** (test
  `test_no_consent_refuses_with_zero_calls_and_zero_rows`). The gate is the reader's own; no provider object is
  built for a disabled provider.
- Empty catalogue: a valid outcome — `{"status":"ok","suggestion_count":0}`, an empty list, and a `suggestion`
  guardrail row whose detail records `outcome="empty_catalog"`; **0 provider calls** (`PG-SC-07`).
- One call per run with at most ONE repair turn (§5.3 shape); every failed attempt leaves a committed
  `error_state` `provider_call` row; budget refusal raises before the call and writes no row.
- `backing_refs_json` names the label data it is grounded in: asset `{type,id,label,category}` plus the
  expiry assertion `{type,id,field_path,value}`.
- `dismiss` with a reason writes a `correction` guardrail event (`from_status`/`to_status`/`reason`);
  dismissal without a reason writes none (both tested).
- No execution path: `test_catalog_bytes_identical_before_and_after_run` fingerprints assets, assertions and
  jobs before/after and asserts equality.
- Secrets: the prompt builder sees label data only; `service.py` names no key identifier; a sentinel-key test
  asserts no written row contains key material (`PG-SC-05`).

## G2 — planning screen (`frontend/src/routes/PlanningPage.tsx`, `frontend/src/components/PlanningSuggestionCard.tsx`)

- React-query screen: household select, **Run planning**, a status filter (all/pending/confirmed/dismissed), and a
  suggestion list that shows the rationale and the backing evidence per suggestion. Confirm/dismiss render only for
  `pending`. No auto-refresh, no schedule UI.
- Tests beside both files: run → pending appears; confirm/dismiss round-trip with the loaded id; a refused
  (skipped) run surfaces the reason; the status filter refetches with the chosen status; the card renders backing
  refs and hides its actions when not pending (`PG-SC-02` forward trace).

## G3 — proof

- **FAIL-then-PASS (raw in `SG-037_verify.log`):** backend new file `12 failed` at base `c251463` (implementation
  absent) → `12 passed` post-change; frontend new tests `2 files failed` (screen/component absent) → `6 passed`
  post-change. Both raw runs are committed with this report (`PG-EV-01`, `PG-EV-09`).
- **Offline gates (zero network):** 12 backend tests green with `opencode_go.OpenCodeGoProvider._post` patched to
  raise (`network_attempts` asserted `[]`); 6 frontend tests green (`vitest` 33 passed overall).
- **Full suite:** `2 failed, 149 passed, 14 warnings in 10.15s`. The two reds are
  `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and
  `test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` — the base-proved decoder environment legs
  (`pyzbar`/`libzbar` and `pytesseract`/`tesseract` absent in this sandbox), re-verified rather than inherited
  (both fail on an empty decode/OCR result, not on new code).
- **`ruff`:** `All checks passed!` **`mypy app`:** `Found 40 errors in 9 files` — identical count to the base
  (SG-029/030/036 quote 40); no new error in any touched file.
- **Build:** `npm run build` green (`tsc && vite build`, 95 modules, `built in 876ms`).
- **Hygiene:** secret scan 0; no `api_key`/`OPENCODE_API_KEY`/`Bearer`/`token` identifier in the new
  service/route/prompt (only the word "secrets" in docstrings); `alembic heads` unchanged; no
  `extract-*-v1.md` diff; no ignored file staged.
- **Health probe — `unanswered`:** `docker compose ps` lists no services (empty table); no StorageGenie listener;
  ports 8000/8001/8002 answer foreign services (`Not Found`/`{"detail":"Not Found"}`) and 8003 refuses. No stack is
  running and starting one is deploying (out of scope per the packet's privileged-denial path).

## G3-live — the ONE metered leg (temp SQLite; last)

- Ceiling printed and checked BEFORE the run: `CEILING=$0.05000 worst_case_estimate(2 calls)=$0.003309` →
  `ceiling_check=PASS`.
- Exactly **one** call: provider-returned model `deepseek-v4-flash-vision-exp`, latency `5224.48ms`,
  usage `{"prompt_tokens":1142,"completion_tokens":918,"total_tokens":2060,"completion_tokens_details":{"reasoning_tokens":474}}`,
  cost **`$0.000722`**; `TOTAL=$0.000722 / CEILING=$0.05000` → `ceiling_total_check=PASS`.
- Ledger row exists: `provider_call_rows=1` (`job_id` NULL, `prompt_template_version=planning-v1`).
- Outcome: `run_status=ok suggestion_count=3`, `guardrail_rows=1`, all three suggestions `pending` with backing
  refs naming their asset + expiry assertion. Key never printed; no second run.

## G4 — worklogs (unconditional, `CO-57`)

`docs/worklogs/SG-037.log`, `SG-037_report.md`, `SG-037_verify.log` — first token `SG-037`; elapsed-versus-budget
per leg with units; model/effort provenance; spend lines; live-state ledger; three UNCLEAR lines.

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
Note added on the work HEAD LAST (120s bound):

```
git notes --ref=refs/notes/storagegenie-coder-reports add \
  -m "Dispatch-ID: SG-037 | Report: docs/worklogs/SG-037_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`); verified with `show <WORK_HEAD>`; executed output
quoted in the delivery message. Final line: `note=yes`.

## Budget — actual vs bound (per leg, units)

| Leg | Actual | Bound |
|---|---|---|
| Premise probes (all reads) | ~45 s wall | 120 s/probe |
| Backend new-file pre/post | 1.33 s / 1.49 s | 600 s suite class |
| Full backend suite | 10.15 s | 600 s |
| Frontend pre/post | 0.51 s / 0.88 s | 600 s vitest |
| Full vitest | 2.15 s | 600 s |
| `npm run build` | 876 ms vite (+ tsc) | 600 s |
| Live leg | 5 s wall, 1 call | $0.05 single live run |
| Overall session | 474 s at log capture | 2400 s overall / 1800 s early-close |

## Live-state ledger

- Live spend total: **`$0.000722`** (one call; quoted above).
- Offline spend: **`$0`** (all offline gates zero network; adapter `_post` patched to raise, `network_attempts == []`).
- Network attempts: exactly the live leg's **1** provider call (proven count; offline tests assert 0).
- Live DB writes: **0** to production — the live leg ran against
  `database=sqlite:////tmp/opencode/sg037/live.db` (quoted in the live output); the production DB path was never
  opened.

## Findings, disagreements, corrections (including out-of-scope)

1. **`F-SG037-1` (see above)** — the packet's "calls through the reader seam" is satisfiable only by reusing the
   vision operation and its strict envelope, because the seam has no text op and the ceiling forbids extending it.
   Flagged loudly; the resolution is in-scope and documented.
2. **`F-SG037-2` (see above)** — ceiling omitted `App.tsx`; minimal registration included and reported.
3. **`F-SG037-3` (see above)** — `opened_date` is not persisted; the "already-opened" input is currently always
   null. Destination: a later assertion-persistence slice.
4. **Live-leg per-call parsing risk.** The adapter parses the response against `ExtractionOutput`; a malformed
   live response would fail validation *after* the network call and the adapter would not attach usage/cost to the
   error, so an errored live call would read `cost=0.0` (the SG-029 finding 3 pattern). The single live run
   validated on the first attempt, so no such row exists here. Destination: the adapter-touching slice already
   named in SG-029 finding 3.
5. **The suggestion "kind" vocabulary is model-chosen.** `date_type` is mapped to `use_first`/`restock`/`days_math`
   and anything else falls back to `general`; the service does not constrain the model's kind beyond that. This is
   deliberate under Stage 0 (no hardcoded rules) and worth an Architect ruling on whether kinds should be a closed
   set later.

## UNCLEAR

- **FIRST READ:** whether reusing `extract_items` with a 1×1 carrier and the `ExtractionOutput` envelope is the
  intended reading of "calls through the reader seam" (finding `F-SG037-1`), or whether the Architect expected a
  text operation that the ceiling forbids adding.
- **DURING EXECUTION:** whether the 5-line `App.tsx` route/nav registration violates the scope ceiling (finding
  `F-SG037-2`). Read as required glue and reported rather than STOPping the slice on a one-file omission.
- **REMAINING:** the disposition of the 2 base-proved decoder environment reds; how opened-date should reach the
  planning catalogue once persisted (`F-SG037-3`); and whether suggestion `kind` should be a closed set.
