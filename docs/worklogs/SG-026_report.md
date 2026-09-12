# SG-026 report — prompts, schemas, fallback, eval scaffolding (fake only)

**Dispatch-ID:** SG-026 · coder `opencode` · effort `medium` (both from packet head;
effort corroborated by parent argv `--variant medium`) · **MODEL `unknown`**
(no model flag or ID anywhere in process arguments or model-bearing env —
only `OPENCODE`/`OPENCODE_PID` presence markers; CLI default per policy, never guessed).
Work dir `/home/andrei/StorageGenie` · BASE ref `automation` = start HEAD
`bd2c112beafdb5f50b6c727c0e661f704b4ecd4b` · WORK_HEAD = (filled at commit time).

## Verdict: SHIP — all acceptance criteria met, no STOP fired

## 1. Starting tree + live SG-025 surface

`git status --porcelain` at start: EMPTY (clean). SG-025 surface confirmed live:
`backend/app/services/providers/protocols.py` (sync `ProviderResult` + 4 Protocols),
`router.py` (`ProviderRouter` + `RouterConfig`), `fake.py` (4-shape `FakeProvider`),
migration `20260912_sg025_provider_call.py`. `downgrade` grep: 5 version files + 3
head-relative migration tests — no new migration this slice, nothing to update; no
`-1` unwind touched `sg025`. `.env` present (203B, presence only). Q2 count `0`
(zero `OPENCODE_API_KEY=` lines; information only, never a gate, no secret literal
anywhere — grep-gated per PG-SC-05).

## 2. G1 baseline (bound 600s, actual 5.08s)

`venv/bin/python -m pytest -q`: **2 failed, 69 passed**. The 2 reds are the known
decoder env-reds (`test_generated_codes_are_validated...`, `test_ocr_has_text_boxes...`
— native barcode/QR + OCR decodes empty in sandbox), cited with base-run command +
output, not relitigated. Premises verified live (PG-IC-09): `backend/eval/` absent,
`prompts/` absent, `schemas.py` absent; manual-entry flow at
`expiry_tracker.py:350-364` (classify writes `needs_evidence` + `_manual_task`),
resolved at `:389-413`; `review_task.py` + `audit_service.record` confirmed.
Packet line numbers drifted slightly (:351-357 → :350-364, :382-410 → :389-413) —
same shapes, drift noted, no finding. No disagreement with any premise.

## 3. G2 — versioned prompts + strict schemas

- **Format decision: Markdown + YAML front-matter** — human-reviewable, version in
  filename AND front-matter, stdlib-parseable, zero new dependencies.
- `prompts/extract-food-v1.md` + `prompts/extract-medicine-v1.md`: system
  instruction carries the provider-neutral rule `never infer beyond visible evidence`.
- `providers/schemas.py` (Pydantic v2, sync, `extra="forbid"`): items array,
  `unknowns` array REQUIRED, per-assertion confidence + uncertainty reasons
  (required when confidence < 1.0); prose input fails validation (quoted §5:
  `ValidationError` on `"The milk expires sometime next spring, I think."`).
- Repair: `extract_with_single_repair` — exactly ONE retry, then
  `ExtractionFailedError`. **No `extraction.py`: quoted reason** — the helper is pure
  validation logic over in-memory payloads with no I/O, provider wiring, or reader;
  a second module adds import surface with no caller. SG-028 owns the reader.

## 4. G3 — bridge + eval

- Bridge: `apply_extraction_result` in `expiry_tracker.py` — the ONLY tracked-file
  touch (+29 lines, capped diff, no step/job/api changes). `needs_evidence` output
  writes the SAME assertion kind (`EXPIRY_FIELD`, `{"status": "unknown"}`,
  `needs_evidence`) and opens the SAME `expiry.manual_entry` task via `_manual_task`
  — no new task type, no pipeline edit. `source_type="extraction"` (not classify's
  `"deterministic"`) — honest provenance, stated loudly. `False` maps to `(None,None)`.
- `backend/eval/corpus/`: 5 smoke fixtures, fabricated JSON only, each with ground
  truth incl. `needs_evidence` + `expectation_class`. `run.py` scores field accuracy
  incl. expected-unknown cases, reads correction rate from `audit_event`, exits
  non-zero on integrity failure. **Baseline: `field_accuracy=0.833`,
  `expected_unknown_cases=3/4`, `correction_rate=0/3=0.000`** (audit writes=3),
  exit 0 in ~1s (bound 600s), committed to `backend/eval/baseline_sg026.md`. The
  clutter fixture carries an INTENTIONAL provider miss (score 0.167) proving the
  scorer discriminates — the 0.833 is measured, not vacuous. No tuning performed.

## 5. G4 — contract tests (bound 600s suite, actual ~6s)

`backend/tests/test_extraction_contract.py` (7 tests): prose rejected; unknowns
honored (complete+empty passes, null+listed passes, fabricated fails); repair via
the fake's invalid-once shape (**invocations == 2**, second valid) + persistent-prose
`ExtractionFailedError` with `supply_calls == 2` (exactly-once proven both ways);
bridge asserts the OPEN task row (not a mock) + a no-bridge negative; corpus
integrity; prompt versioning. **PRE FAIL** (collection `ImportError:
apply_extraction_result`, exit 2) **+ POST 7 passed** — both raw runs committed in
`SG-026_verify.log` (PG-EV-01/09). Full suite: 2 failed (base-proved reds), 76 passed
(+7 exactly the new file). `ruff check .`: **All checks passed**. `mypy app`:
40 errors in 9 files, **0 in touched files** (destinations in verify log §6; matches
the standing 40-in-9 advisory). PG-SC-05 grep over all slice files: zero SDK/key/
network matches. PG-SC-10: no new path ignored. PG-SC-02: fields read back by the
tests + scorer; PRODUCTION reader arrives SG-028 — stated explicitly.

## 6. Guards, budget, scope

Guards exercised: PG-EV-01/02/04/07/09, PG-SC-02/05/10, PG-IC-01/03/07/09, PG-PR-03/04/06/10 —
no guard fired except as designed (EV-01 FAIL anchor). Elapsed vs budget: probes ~10s/120s;
baseline suite 5.08s/600s; POST <1s; full suite ~6s/600s; eval ~1s/600s; ruff+mypy <120s;
session total ~4min at log write vs 2400s overall. Scope ceiling honored: `prompts/` new +
`schemas.py` + bridge inside `expiry_tracker.py` ONLY + `backend/eval/*` + 1 test file +
`docs/worklogs` (3 files) — `git status` shows exactly that plus nothing else.
DATABASE none (temp SQLite, zero live rows); restart none; no privileged ops attempted.

## 7. Issues / disagreements (incl. out-of-scope)

1. Prompt-phrase iteration (mine, root-caused in-slice): the no-inference sentence
   twice failed its own test — first split by `**bold**` markers, then by a line
   break. Fixed by placing the contiguous phrase on one line; POST green. No packet
   impact. 2. mypy pre-change run omitted (suite was the base proof); count/files
   match the standing advisory exactly and touched files read 0 — destination list
   committed. 3. Out-of-scope observation: `mypy app` file list shows 9 files but the
   naive `uniq` undercounts names with digits — cosmetic, noted for future quoters.

UNCLEAR — FIRST READ: none (packet premises all verified live).
UNCLEAR — DURING EXECUTION: none (two prompt-phrasing misses were root-caused, not unclear).
UNCLEAR — REMAINING: none. SG-027 (vision-spike-first, needs Q2 key) is next per D35/D36.
