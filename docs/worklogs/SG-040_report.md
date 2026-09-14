# SG-040 report — Persist `opened_date` end to end (extraction → candidate → assertion → consumers): GREEN

**BASE REF:** `automation` → resolved commit `e5494a1afd3c28313c6118a23189b40fc7345532` (two fields, as required).
**WORK_HEAD:** the commit carrying this report (hash quoted by the G5 receipt note; note added last, no commit after).
**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`.
**Model/effort per `CO-78` (from process arguments / provider metadata, never an identity line):** process argv
`opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet>"` → effort `medium`; no model flag
on argv (packet: CLI default, omitted per policy). Provider metadata
`providerID=opencode-go modelID=deepseek-v4.1-flash` (`~/.local/share/opencode/log/opencode.log`, read
2026-09-14T10:59Z).
**DATABASE:** none — temp SQLite per test (`pytest` `tmp_path`); the production DB was never opened. **Restart:**
none. **NETWORK:** none — all proof in-process on the scripted provider; the real adapter's `_post` is never
reached (and is patched to raise in the new pipeline test). **Spend: `$0`** (no live call in this slice).

## Verdict

GREEN. `opened_date` now travels the whole chain. `build_candidate_from_extraction` maps a non-null
`item.opened_date` into `fields["opened_date"]` with the exact `expiry_date` provenance envelope, and the field is
both allowed (`ALLOWED_CANDIDATE_FIELDS`) and gated (`GATED_FIELDS`), so candidate accept commits an
`opened_date` assertion carrying the value, `source_type="extraction"` and `review_state="proposed"`. The
split-child rebuild replaces `opened_date` per item exactly like `expiry_date`/`lot`, and drops it when the item's
is null. Chat grounding (`build_catalog`) and the planning catalog now read the asset's ACTIVE `opened_date`
assertion directly (field_path `opened_date`); the planning catalog also exposes `opened_assertion_id` and
`_backing_refs` appends the opened-date assertion ref. Assets without an opened-date assertion stay `null` exactly
as before (proven by test, not prose). Full backend suite `2 failed, 165 passed` (the 2 reds are the base-proved
decoder environment legs, re-verified at base: `2 failed, 160 passed`); `ruff` clean; `mypy` 40 errors in 9 files
(delta 0; no touched file in the list); no migration; no frozen-prompt diff; secret scan 0; no ignored file staged;
empty frontend diff (no build/vitest leg). Five new tests: raw `4 failed, 1 passed` at base → `5 passed`
post-change, both runs committed in `SG-040_verify.log`.

## Premise findings (verified in-slice; corrections are findings, not obstacles)

1. **All six packet premises confirmed by direct read.**
   - `ExtractionItem.opened_date` exists: `backend/app/services/providers/schemas.py:37`.
   - `build_candidate_from_extraction` mapped only `display_name`/`expiry_date`/`lot`:
     `backend/app/services/candidates.py:212-242` (pre-change line range).
   - `opened_date` was absent from `GATED_FIELDS` (`candidates.py:25`) and `ALLOWED_CANDIDATE_FIELDS`
     (`candidates.py:26-39`), so a hand-written field would be refused at `candidates.py:358-359` (commit) —
     pre-change line numbers.
   - Split rebuild replaced only `{display_name, expiry_date, lot}`: `candidates.py:487` (pre-change).
   - Chat read `opened_date` from the plugin expiry assertion's `value_json`: `chat/service.py:161` (pre-change
     152-162) — a field the plugin never writes (see finding 2).
   - Planning hardcoded `"opened_date": None`: `planning/service.py:144` (pre-change).
2. **The chat "persisted" read was dead in production until now.** The plugin's `EXPIRY_FIELD` value is either
   `{"expiry_date", "date_type"}` (`expiry_tracker.py:407-415`) or `{"status": "unknown"}` (`:402-404`); it never
   writes an `opened_date` key. So `value.get("opened_date")` was always `None`. This is why the packet's exit bar
   was unmet despite the chat code "reading" it.
3. **No test pins the field-list content (`PG-SC-05`).** `ALLOWED_CANDIDATE_FIELDS` is referenced only inside
   `candidates.py` itself. `GATED_FIELDS` is imported only by `tests/test_phase2_e2e.py:30` and used as a dynamic
   membership test at `:287` (`row.field_path in GATED_FIELDS`); no literal set is asserted. So extending both
   frozensets is safe and the existing gate stays meaningful.
4. **Generic rendering claim verified — no UI built.** `AssetDetailPage.tsx:151-164` maps **all** assertions
   (`a.field_path`, `a.value`, `a.source_type`, `a.review_state`, `a.confidence`) with no name filter; the only
   name-based lookup is `expiryAssertion` at `:58`, used solely to decide when to render the manual-expiry form,
   not the assertions table. `CandidateCard.tsx:4-14` (`fieldInfo`) and `:67-74` iterate `Object.entries(candidate.fields)`
   generically. Neither screen needs a change and no frontend file changed (empty diff).
5. **The 2 decoder env reds are a base-proved premise, re-verified, not inherited.** At base `e5494a1` the full
   suite is `2 failed, 160 passed`: `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`
   and `test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` (missing `libzbar`/`tesseract` in this
   sandbox). Post-change the same two fail: `2 failed, 165 passed` (the +5 are the new tests).

## G1 — persist (`backend/app/services/candidates.py`)

- `GATED_FIELDS` now `{"identifier", "expiry", "expiry_date", "opened_date", "condition", "lot"}`; **gating
  rationale (packet-mandated, recorded):** dates are safety-critical per §5.2-7 and the design requires the same
  unknown-is-valid discipline as expiry dates — an opened date must be human-confirmed, never silently
  auto-accepted. `ALLOWED_CANDIDATE_FIELDS` gains `"opened_date"`.
- `build_candidate_from_extraction` maps `item.opened_date` **only when not `None`**, with the identical
  `_provenance(...)` envelope used one block above for `expiry_date` (`candidates.py:234-245`).
- `_split_child_fields` now excludes `"opened_date"` from the copied origin fields (so the origin's first-item
  value cannot leak into every child) and rebuilds it from **that** item, exactly like `expiry_date`/`lot`
  (`candidates.py:498` key set; `:520-531` mapping).
- **Fifth touchpoint check (M6):** none. The ceiling files were sufficient: the field vocabulary is bare
  `opened_date` (like every other candidate field), so no schema, model, plugin, or migration change is needed.
  `extract_items` and the provider seam are untouched.

## G2 — consumers read the persisted value (`PG-IC-01`)

- **Decision — field_path `opened_date`, direct active-assertion read.** The candidate commit writes
  `Assertion(field_path="opened_date", value_json=<json string>)`; both consumers read that assertion via their
  existing `_active_assertion(db, asset.id, "opened_date")` helper. `OPENED_DATE_FIELD = "opened_date"` is a new
  module constant in each service.
- `chat/service.py`: the dead `opened_date = value.get("opened_date")` inside the expiry block is removed; the
  value now comes from `_date_assertion_value(db, asset.id, OPENED_DATE_FIELD)` (a small helper returning the
  active assertion's string value, added to keep `build_catalog` under ruff's `C901` complexity bound). The
  `expiry_date`/`date_type`/`expiry_assertion_id` behaviour is byte-identical.
- `planning/service.py`: the hardcoded `"opened_date": None` is replaced with the same read; the catalog entry
  gains `opened_assertion_id`. **Decision — `_backing_refs` opted IN:** when the matched catalog entry has an
  opened assertion, an `{"type": "assertion", "field_path": "opened_date", ...}` ref is appended, mirroring the
  expiry assertion ref so a suggestion that names the asset cites the opened date too.
- **Backward compatibility (proven, not prose):** `test_catalog_carries_persisted_opened_date_and_null_without`
  (chat) and `test_catalog_carries_persisted_opened_date_and_backing_ref` (planning) seed one asset **with** an
  `opened_date` assertion and one **without**; the without-asset returns `opened_date is None` and its
  `expiry_date` is unchanged. Nothing is inferred from the expiry row.

## G3 — proof

- **FAIL-then-PASS raw (committed in `SG-040_verify.log`, both runs on the same tree; source stashed only for
  run 1, `PG-EV-01`/`PG-EV-09`):**
  - RUN 1 at base (source `candidates.py`/`chat/service.py`/`planning/service.py` stashed; new tests present):
    `4 failed, 1 passed in 1.07s` — the 4 are the opened-date tests; the 1 pass is the **null-date foil**
    (below).
  - RUN 2 post-change: `5 passed in 1.02s`.
- **Evidence set:**
  1. `test_opened_date_persisted_gated_with_value` — candidate `fields["opened_date"].value == "2031-04-10"`,
     `source_type == "extraction"`, confidence/prompt_call present; after candidate accept the asset carries an
     `opened_date` assertion whose decoded **value is exactly `"2031-04-10"`**, `review_state == "proposed"`
     (gated), `source_type == "extraction"`, `model_json` provider `scripted`, `evidence_ids` correct. A
     module-local `_post` guard proves `network_attempts == []`.
  2. `test_opened_date_none_writes_no_field_and_no_assertion` — `"opened_date" not in fields` and zero
     `opened_date` assertions after accept. **Called out loudly: this test PASSES at base too** (base also writes
     nothing). It is a non-regression foil, not part of the fail-then-pass set; it exists to make a future
     "guess a date" regression fail.
  3. `test_split_children_keep_their_item_opened_date` — child 0 keeps `"2031-04-10"` (with extraction
     provenance), child 1 (item `opened_date=None`) has no `opened_date` key; mirrors the existing split
     assertions and also re-asserts the shared `expiry_date`.
  4. `test_catalog_carries_persisted_opened_date_and_null_without` (chat) and
     `test_catalog_carries_persisted_opened_date_and_backing_ref` (planning) — persisted date surfaces for the
     asset that has it, `None` for the one that does not, and the planning `_backing_refs` carries the opened
     assertion ref.
- **Full backend suite (`backend/`, 600 s bound):** base `2 failed, 160 passed` (10.39 s); post
  `2 failed, 165 passed` (10.91 s). Same 2 `test_signals.py` decoder reds, no new red.
- **`ruff`:** `All checks passed!` (after factoring the chat helper; see finding F-SG040-2).
- **`mypy app`:** `Found 40 errors in 9 files (checked 69 source files)` — identical to base (40/9). A grep of
  the output for `candidates.py`, `chat/service.py`, `planning/service.py` returns **NONE** (touched files add
  zero errors).
- **Build/vitest:** frontend diff is **empty** → per the packet (and SG-035/036 precedent) `npm run build` and
  `npx vitest run` were not run. No UI built.
- **Hygiene:** no migration (`git diff --stat -- backend/alembic` empty; `alembic heads` unchanged at
  `20260914_sg035_foundations`); no frozen-prompt diff (`backend/app/services/providers/prompts` diff empty); no
  ignored file staged (`git status --porcelain` shows only the 6 intended modified tracked files, no `??`); secret
  scan of the changed files shows only pre-existing test sentinels (`sk-SENTINEL-DO-NOT-WRITE-037/038`) and
  docstrings saying "no secrets" — **0 real secret material**.
- **Health probe per the standing line — `unanswered`:** `docker compose ps` lists 0 services; port 8000 answers
  a foreign service (`Not Found`). No stack runs; starting one is deploying (out of scope per the
  privileged-denial path).

## Findings, disagreements, corrections (including out-of-scope)

1. **`F-SG040-1` — the G3 wording "an accepted (user-confirmed) `opened_date` assertion" conflicts with the
   packet's own gating instruction.** A field in `GATED_FIELDS` is committed `review_state="proposed"` on
   candidate accept, never `"accepted"`; the existing `test_expiry_always_proposed_never_auto_accepted`
   (`test_ai_pipeline.py:211-229`) proves this for the sibling date field. I gated `opened_date` as instructed
   and asserted the exact **value** plus `review_state="proposed"`. If the Architect instead wants an *accepted*
   assertion after candidate accept, that would require removing `opened_date` from `GATED_FIELDS`, which
   contradicts G1's explicit gating rationale. Reported for a ruling; I did not bend either requirement.
2. **`F-SG040-2` (self-correction) — ruff `C901`.** The first chat implementation inlined the opened read and
   pushed `build_catalog` to complexity 11 (>10). I extracted `_date_assertion_value`; ruff is clean. No
   behaviour change.
3. **Out-of-scope observation — the expiry/opened assertion field_paths differ in namespacing.**
   `expiry_date` is stored as `plugin:expiry-tracker/expiry_date` for the plugin path but as bare `expiry_date`
   for candidate-derived assertions (`_create_asset_for_candidate`); `opened_date` is bare. Consumers already
   handle expiry with two different read sites, so this slice follows the bare candidate-field convention. Not a
   defect here, but worth a future consistency note.
4. **`_backing_refs` addition is a judgement call**, as the packet marked it optional: opted IN for parity.

## Budget — actual vs bound (per leg, units, `PG-PR-06`)

| Leg | Actual | Bound |
|---|---|---|
| Premise probes (reads) | ~120 s wall | 120 s/probe |
| BASE full suite | 10.39 s (real 12.0 s) | 600 s |
| FAIL run (base source) | 1.07 s | 600 s |
| PASS run | 1.02 s | 600 s |
| POST full suite | 10.91 s (real 12.6 s) | 600 s |
| `ruff` (base/post) | <1 s each | — |
| `mypy app` (base/post) | few s each | — |
| Frontend build/vitest | not run — empty diff | 600 s / 600 s (unused) |
| Overall session | ~260 s at log capture | 1800 s early-close / 2400 s overall |

## Live-state ledger

- Live spend: **`$0`** — zero provider calls in this slice.
- Network attempts: **0** — scripted in-process provider only; the new pipeline test patches the real adapter's
  `_post` to raise and asserts `network_attempts == []`; existing offline suites pass.
- Live DB writes: **0** to production — all tests use temp SQLite under `tmp_path`.
- No key read; no service started; nothing deployed.

## UNCLEAR

- **FIRST READ:** whether the G3 criterion "an accepted (user-confirmed) `opened_date` assertion" meant the
  candidate-level accept (after which a gated field is `proposed`) or a later per-field acceptance UI action that
  this slice's ceiling does not build (`F-SG040-1`). I implemented the packet's explicit gating instruction.
- **DURING EXECUTION:** whether chat grounding should preserve the old "opened embedded in the expiry assertion
  value" fallback. Since the plugin never writes that shape, I switched to the dedicated assertion directly; if a
  third-party writer ever embeds it, no value would surface. The packet left the mechanism to me.
- **REMAINING:** the 2 base-proved `test_signals.py` decoder environment reds (libzbar/tesseract absent) and
  whether a future slice adds a UI path to *accept* a proposed `opened_date` (today it stays `proposed`).

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
Note added on the work HEAD LAST (120 s bound):

```
git notes --ref=refs/notes/storagegenie-coder-reports add \
  -m "Dispatch-ID: SG-040 | Report: docs/worklogs/SG-040_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`); verified with `show <WORK_HEAD>`; executed output
quoted in the delivery message. Final line: `note=yes`.
