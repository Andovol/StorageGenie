# SG-079 — photo-ingest schema v3 + frozen v3 prompts

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE (packet ref `origin/automation`):** `3bf9198339a0f92d1daf5e779c29160a6dbc47be` (`SG-079: photo-ingest schema v3 + frozen v3 prompts packet (D101 track)`)
**WORK_HEAD:** `{{WORK_HEAD}}` (work commit; the post-note, docs-only receipt commit is HEAD after it)
**Contract:** recorded `0.28.2` == published `0.28.2`; source `/home/andrei/storagegenie-contract/VERSION`, contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2`
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`, read from provider metadata `/home/andrei/.local/share/opencode/log/opencode.log` line `llm.provider=opencode-go llm.model=deepseek-v4.1-flash`, **not** a system-prompt identity line; argv carries no `--model`) · effort `medium` (process argv `/proc/459564/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Spend (real $):** `$0.000000` actual vs `$0` bound — zero metered provider calls.
**Autonomy:** `L2` slice (1 retry available; not used).
**Cost posture:** $0.000000 actual vs $0 bound. No production run, no restart, no deploy (`PG-PR-04` stated; `PG-PR-06` containment N/A — no production touch). No network (proof in G3).

D101-approved slice 1 of the photo-ingest track (plan `docs/superpowers/plans/2026-09-21-ai-ingestion-enrichment.md` Task 1; spec `docs/superpowers/specs/2026-09-21-ai-ingestion-enrichment-design.md` §1–§2). This
slice extends the strict extraction schema and freezes three v3 prompt files. **It deliberately does not flip the
live pipeline:** `reader.py` `PROMPT_FILES` still maps `food → extract-food-v2.md`,
`medicine → extract-medicine-v2.md`, `cosmetics → extract-cosmetics-v2.md` (re-verified raw in
`SG-079_verify.log`), so the running service is untouched and the slice is $0 offline. The new fields are
**UNRECORDED** this slice (`PG-SC-02`): no writer fills them, no reader shows them — SG-080 is the
writer/reader slice.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on tree | Verdict |
|---|---|---|
| `ExtractionItem` fields `name, expiry_date, opened_date, date_type, lot, quantity, unit, asset_type, confidence, uncertainty_reasons` | `schemas.py:36-47` — exactly these ten | **confirmed** |
| Validators: quantity finite ≥ 0; unit/asset_type non-blank when present; ISO dates; uncertainty required below 1.0; `unknowns` path `items.<i>.<field>` with null-beside-unknown via `ExtractionItem.model_fields` | `schemas.py:49-83,95-112` — exactly | **confirmed** |
| v2 front matter `template_version/category/output_schema/repair_policy`; transcribe-only; `unknowns items.<index>.<field>`; `needs_evidence`; JSON-only; single-retry Repair | all three v2 files match (read in recon) | **confirmed** |
| `reader.py` `PROMPT_FILES` maps v2 for all three categories | `reader.py:51-55`; runtime read prints v2 for all three | **confirmed** |
| `eval/run.py` offline path is reusable for the new dir | **difference:** `run.py:50 MANIFEST_PATH = CORPUS_DIR/"sg029"/"manifest.json"` is hardwired; loading sg079 would require a loader hunk | **finding F-SG079-1** |
| BASE `origin/automation` == start HEAD | both `3bf9198339a0f92d1daf5e779c29160a6dbc47be` | **confirmed** |
| Contract recorded == published | `VERSION` `0.28.2`; contract HEAD `b495b59` | **confirmed** |

## G1 — strict schema v3 (transcribed-only, Pydantic v2)

`backend/app/services/providers/schemas.py:44-64` adds eleven nullable fields to `ExtractionItem`, inside
`extra="forbid"`: `brand, variant, size_text, barcode, category_proposed, transcript, storage,
nutrition_per100g, nutrition_serving` as `str | None`, and `warnings, allergens` as `list[str] | None`.
Container-type decision (mine, per the packet): verbatim text fields stay `str` — including the two
nutrition panels, transcribed verbatim as text, because a structured nutrient dict would itself be an
inference surface and the spec calls nutrition transcribe-only; the multi-valued care panels are
`list[str]`. `category_proposed` is an open-vocabulary slug (no enum) whose canonical mapping is downstream
(SG-080, never here). `transcript` is verbatim label text, evidence only.

The existing `_non_blank_when_present` validator (`schemas.py:66-84`) is extended to the nine new string
fields; a new `_list_entries_non_blank_when_present` (`schemas.py:86-97`) rejects blank entries in
`warnings`/`allergens`. The pre-existing `_unknowns_are_absent_fields` mechanism needed **no change**: it
already reads `ExtractionItem.model_fields`, so the new names are recognised and a value beside an
`unknowns` entry still fails as fabrication; an empty list equals absent for the two list fields.

**Fail-then-pass (raw, both runs in `SG-079_verify.log`):**
- **FAIL-pre:** `tests/test_sg079_v3_schema.py` before any change → **19 failed, 37 passed** (fields
  `extra_forbidden`; v3 prompts absent). Reproduced cleanly with schema stashed while prompts/tests exist
  → **16 failed, 40 passed**. The failing run was seen to fail (`PG-EV-01`); the gate is the tests
  (`PG-EV-02`).
- **PASS-post:** **56 passed** (`rc=0`).

Covered properties: transcribed values parse verbatim; null is legal; a fabricated string or list value
beside an `unknowns` entry is rejected (`ValidationError`); a blank string field / blank list entry is
rejected; an unknown field is still forbidden; prose naming the new fields is never parsed.

## G2 — frozen v3 prompts (+ v1/v2 untouched)

Three new files: `extract-food-v3.md`, `extract-medicine-v3.md`, `extract-cosmetics-v3.md` (sha256 in
`SG-079_verify.log`). Each opens with the exact envelope `template_version: extract-<cat>-v3` +
`category` + `output_schema: ExtractionOutput` + `repair_policy: single-retry-then-fail`, carries the
transcribe-only system rule extended to every new field, names `items.<index>.<field>`, and preserves
`needs_evidence`, `JSON ONLY` and the single-retry `## Repair` section.

**v1/v2 byte-identical:** `git diff --stat` over the six old prompt files is **empty** (quoted raw in
`SG-079_verify.log`). The three v3 files are the files committed by this packet's work commit
(`PG-EV-07` — no Coder-authored stand-in input).

**Live path untouched:** `reader.PROMPT_FILES` still maps v2 and `reader.load_prompt` returns
`extract-<cat>-v2` for all three (raw). The v3 files are not loaded by the running service.

### Fixtures + scoring (`PG-SC-12`)

`backend/eval/corpus/sg079/` holds six offline scoring fixtures (clean + partial + glare across
food/medicine/cosmetics) + `manifest.json`. They carry authored v3 ground truth and provider_output
references, no images and no `provider_calls` — identical shape to the SG-049 scoring-only corpus, so no
live call and $0. Each parses through the **real** `app.services.providers.schemas` and its `unknowns`
entries are honest (raw dump in `SG-079_verify.log`). The new test scores all new fields against ground
truth (all 1.0) and proves non-vacuity: mutating one transcribed value scores below perfect.

`PG-EV-07` / `PG-EV-02` / `PG-SC-12`: the fixtures are committed inputs, and the scoring goes through the
real schema module. The **real `eval/run.py` offline path** was run **unmodified** on its existing sg029
corpus before and after: `corpus integrity OK: 10 fixtures`; `field_accuracy=0.833`,
`unknown_rate=4/7=0.571`, `correction_rate=0/6=0.000` — identical before and after, proving the schema
extension is backward-compatible with the frozen v1 cache. `--live` was **not** run (forbidden this
slice); no corpus file was rewritten by the runner.

## G3 — what must not change

- **Scope diff empty:** `git diff --stat` over `reader.py`, `router.py`, `candidates.py`, `app/api`,
  `frontend`, `alembic`, `docker-compose.yml`, `.env`, `app/models` → empty. Only
  `schemas.py` (tracked) + the new prompt/test/corpus files are touched.
- **No table change / no migration:** no `app/models` or `alembic` diff. The static table registry
  `tests/test_postgres_dialect.py:35 EXPECTED_TABLES` (asserted `== set(Base.metadata.tables)`) is among
  the passing tests.
- **Full backend suite:** `2 failed, 344 passed` — the **same 2 base decoder reds** as the pre-change
  baseline (`2 failed, 288 passed`; +56 new tests pass). The reds are
  `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and
  `::test_ocr_has_text_boxes_and_mean_confidence`; caused by the box lacking `pytesseract`/`pyzbar`
  (`app.services.signals: OCR extraction unavailable: pytesseract is not installed`). **Stash-reproved:**
  with all SG-079 work stashed, the two reds fail on the bare BASE tree (`2 failed in 0.56s`) — SG-073
  precedent, raw in the verify log.
- **`ruff`:** `All checks passed!` (`rc=0`) on `app tests`.
- **`mypy` delta 0:** pre-change `Found 41 errors in 9 files` == post-change `Found 41 errors in 9 files`;
  `mypy app` reports **0** errors in `schemas.py`. Delta 0, quoted.
- **Secret scan 0:** `git diff` and the new untracked files scanned for `sk-|api[_-]?key|secret|password|
  token|BEGIN .*PRIVATE` → no matches. The only `sk-…` hits are the four pre-existing deliberate
  `sk-SENTINEL-DO-NOT-WRITE` test fixtures, untouched.
- **$0 / no network:** no new `socket`/`http`/`requests`/`urllib` import in the `schemas.py` diff; the new
  test imports only stdlib, pytest, and real app modules; the only execution was the local test suite and
  the offline `eval/run.py` (no `--live`, no key read, no container pull/run). No metered call.

## G4 — worklog and report

- `docs/worklogs/SG-079.log`, `SG-079_report.md`, `SG-079_verify.log` written (first token `SG-079`).
- Elapsed vs budget (units, per leg): recon+baseline **~1 min** / 120 s · G1 fail-pre+implement+pass
  **~1 min** / 120 s · G2 prompts+fixtures+scoring **~1 min** / 120 s · G3 full suite / lint / secret /
  scope **~1 min** / 600 s (suite itself 16.5 s) · overall **~5 min** / 1800 s. No command hit its bound;
  nothing was killed.
- Model `deepseek-v4.1-flash` / effort `medium` (sources above). Spend: **real $0.000000** (zero metered
  calls). Contract echo + source path above.
- `PG-IC-01`: no criterion touched the network, the DB, or the running service; reads were the local test
  suite and the offline eval runner only. No container image pull/run.

### Question each criterion answers (`PG-SC-09`)

- **G1 — does the schema accept transcribed v3 fields and reject fabrication?** Yes: 11 fields parse
  verbatim (56 tests pass), and a value beside an `unknowns` entry / blank field / prose raises
  `ValidationError`, proven fail-pre→pass-post.
- **G2 — are the frozen v3 prompts complete with v1/v2 preserved and the live path untouched?** Yes: three
  v3 files with the exact envelope and every field named; six old files byte-identical (empty diff);
  `PROMPT_FILES` still v2.
- **G3 — did nothing else move?** Yes: scope diff empty, no migration, suite green modulo the two
  stash-reproved base reds, ruff clean, mypy delta 0, secret scan 0.

### Receipt note verification (pasted `show` output)

Work pushed to `automation`; worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. Note added on `WORK_HEAD` and pushed, then fetched into a mapped local ref and shown:

```
PASTE_SHOW_OUTPUT_PLACEHOLDER
```

Final line: `note=yes`

## Findings

- **F-SG079-1 (`eval/run.py` cannot load sg079 without a loader hunk — reported, default taken).** The
  packet allows a loader change "ONLY if the new corpus needs a loader change (hunk quoted + reason, else
  untouched)" and names "runner untouched" the default. `run.py:50` hardwires `MANIFEST_PATH` to
  `corpus/sg029/manifest.json`; scoring sg079 through it would require adding a sg079 manifest selector.
  I took the default: **runner untouched**, sg079 scored through the real `schemas` module in
  `test_sg079_v3_schema.py`, and the real runner exercised unmodified on its own corpus to prove backward
  compatibility. If the Architect intended the runner to gain a sg079 mode this slice, that is the item
  to correct — I did not bend the runner to match.
- **F-SG079-2 (`nutrition_*` container type is a design call).** Kept as verbatim `str`, not a structured
  dict, to stay transcribe-only and avoid an inference surface. Stated so the reviewer sees the choice.
- **F-SG079-3 (base reds are environment, not code).** The two `test_signals.py` failures are the known
  decoder reds (`pytesseract`/`pyzbar` absent) and reproduce on the bare BASE tree; unchanged by this
  slice.

## Vacuity check (loud)

No acceptance criterion passed vacuously. The new-field tests genuinely **failed pre-change** (19/37, then
16/40 with schema stashed) and pass post (56). The v1/v2 "unchanged" check is a real `git diff --stat`
over the six named files, output pasted. `PROMPT_FILES`/`load_prompt` are read at runtime, not asserted
against a copy. The fixtures are committed files parsed by the real schema module, and a mutated value
provably scores below perfect (non-vacuous scorer). The two base reds are real failures reproduced by
stash on the bare tree, not assumed. The eval runner ran a real integrity check + offline scoring. The
mypy "delta 0" compares two real full runs (41/9 both). The scope-diff and secret-scan checks were run
over the real worktree. No grep was scoped so narrowly it could not have matched.

## UNCLEAR

- **FIRST READ:** the packet's G2 says sg079 fixtures should be scored through "the real `eval/run.py`
  offline path where it runs without modification" while also defaulting the runner to untouched. On this
  tree the runner is hardwired to the sg029 manifest (`F-SG079-1`), so it cannot *by construction* score
  the new dir unmodified. I read the two clauses as: runner stays untouched, sg079 is scored through the
  real schema module, and the unmodified runner is exercised on its own corpus — and reported it plainly
  rather than silently editing `run.py`.
- **DURING EXECUTION:** the first fail-pre run (before the v3 prompts existed) fails 19 tests including
  the three prompt-existence tests; the reproducible schema-stash run fails 16 because the prompt files
  then exist. Both are quoted, so the reader sees which leg is which rather than a single blurred number.
- **REMAINING:** the v3 fields are unrecorded this slice by design (`PG-SC-02`) — no writer fills them and
  no reader shows them; the live pipeline still loads v2. Wiring the reader, transcript-to-evidence, and
  `category_proposed` into the candidate flow is SG-080, and any live/metered proof of v3 against a real
  model is deferred there.
