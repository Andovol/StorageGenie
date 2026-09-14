# SG-038 report — Category chat (Food, then Medicine), grounded, with the adapter text op: GREEN

**BASE REF:** `automation` → resolved commit `084810b68389c5d309c2aba8d7b84f87aaa7d607` (two fields, as required).
**WORK_HEAD:** the commit carrying this file (hash quoted by the G6 receipt note; note added last, no commit after).
**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`.
**Model/effort per `CO-78` (from process arguments / provider metadata, never an identity line):** process argv
`opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet>"` → effort `medium`; the model flag
is absent from argv (packet: CLI default, omitted per policy). Provider metadata
`providerID=opencode-go modelID=deepseek-v4.1-flash` (`~/.local/share/opencode/log/opencode.log`, read
2026-09-14 10:48 UTC). The adapter's **provider-returned** model in the metered run was
`deepseek-v4-flash-vision-exp`.
**DATABASE:** temp SQLite only (`sqlite:////tmp/opencode/sg038/live.db` for the live leg); the production DB was
never opened for writing. **Restart:** none. **NETWORK:** exactly ONE metered live run (1 provider call, proven
count); all other gates offline with the adapter's `_post` patched to raise.

**Spend:** offline `$0`; live **`$0.0001833`** across **1** call (ceiling `$0.05`) — cumulative live total
**`$0.0009053`** (`$0.000722` carried from SG-037 + `$0.0001833`).

## Verdict

GREEN. The real adapter now implements the text operation the seam always declared: `extract_text(text, prompt,
*, estimated_cost=0.0)` on `OpenCodeGoProvider`, with the same guard set as `extract_items` (pre-call per-job +
monthly refusal, identity headers, HTTP/envelope checks, `guard_usage`, `strip_single_think`/`guard_content`,
usage-derived cost, fully populated `ProviderResult`) and no image/base64/`parse_extraction_output`. A grounded
category chat exists end to end: `POST /v1/chat/{category}` is consent-gated before the provider object is built,
builds its grounding from that category's catalogue (assets + expiry/opened assertions + source attributions),
places the catalogue inside a delimited **DATA** section, calls the seam, writes one `provider_call` ledger row
(`job_id` NULL), and returns the assistant text. `POST /v1/chat/{category}/corrections` is the ONLY write action
(a user-explicit append-only `correction` guardrail row). Food/Medicine are the supported set; anything else is an
enforced `422`. No execution path: catalogue bytes are identical before/after a chat call (test). `extract_items`
and the extraction pipeline are untouched and all existing extraction/provider tests are green. Full backend suite
`2 failed, 160 passed` (the two reds are the base-proved decoder environment legs, re-verified at base); `ruff`
clean; `mypy` 40 errors (delta 0); `npm run build` green; `vitest` 40 passed; secret scan 0; no migration; no
frozen-prompt diff. **One** live call at `$0.0001833`.

## Premise findings (verified in-slice; corrections are findings, not obstacles)

1. **`F-SG038-1` — `protocols.py`'s `OcrProvider.extract_text` is not the chat signature (design call).** The
   packet's `protocols.py:34-37` premise is correct: `OcrProvider.extract_text(image_ref)` is declared, the fake
   implemented it, and the real adapter did not. But that protocol is an image-OCR capability; the chat op takes
   `(text, prompt)`. The router dispatches by name via `getattr` (`router.py:52-72`) and never type-checks the
   Protocol, so no protocol change is required for the seam to work. Per the packet ("only if the declared
   `extract_text` signature must be clarified … no new protocol, no new vocabulary"), I **left `protocols.py`
   unchanged** rather than overload the OCR protocol with chat semantics. Recorded, not silently bent.
2. **The packet's implicit category mapping is confirmed by the tree.** `food`→`food_beverages`,
   `medicine`→`medicine_pharma` (`backend/app/plugins/expiry_tracker.py:111-152`); the chat service enforces only
   those two user-facing values and scopes grounding by the mapped slug.
3. **`opened_date` still is not persisted** (SG-037 `F-SG037-3`, `SG-040` ordered after this slice). The chat
   grounding reads `opened_date` from the expiry assertion's `value_json` when present and otherwise reports
   `null`; nothing here relies on it being populated. Consistent with the ordering note.
4. **No check constraints / no migration** — `alembic heads` unchanged at `20260914_sg035_foundations`.

## G1 — the adapter text operation (`backend/app/services/providers/opencode_go.py`)

- `build_text_payload(model, prompt, text)` sits beside `build_chat_payload`: `messages` = one `system` (the
  versioned prompt) + one `user` (the delimited data + question), plain-text content, `stream: False`,
  `max_tokens` sized as before, **no `response_format`** (the answer is free text) and **no image part**. `PG-EV-04`
  test `test_text_payload_shape_no_image_no_key` asserts roles, per-message content, model, absence of
  `image_url`/`base64`, and absence of key material.
- `extract_text(text, prompt, *, estimated_cost=0.0)` mirrors `extract_items`'s guards exactly. It adds no new
  machinery: it calls the existing `_post`, `guard_usage`, `strip_single_think`, `guard_content`, `compute_cost`.
  The decided `normalized_output` shape is `{"text": <content>, "model": <response model>,
  "finish_reason": <choice finish_reason>}`; `model_id`/`latency_ms`/`usage`/`cost`/`raw_payload` are populated
  as before.
- `fake.py`'s `extract_text` now takes `(text, prompt="", *, estimated_cost=0.0)` and returns the scripted
  `{"text": "fake-text", "source": text}`, so the existing router tests that call `extract_text("img-1")` still
  pass unchanged.
- **Regression rail:** full suite green (`2 failed, 160 passed`), including `test_extraction_contract.py`,
  `test_ai_pipeline.py`, `test_opencode_go.py`, `test_provider_gateway.py`; no `extract_items` behaviour changed.

## G2 — chat service + routes (`backend/app/services/chat/`, `backend/app/api/v1/chat.py`)

- Consent first: `reader_mod.ai_status()` returns `(False, "consent_disabled")` and `POST /v1/chat/food` returns
  `{"status":"skipped","reason":"consent_disabled"}` with **0 provider calls and 0 rows** (test
  `test_no_consent_refuses_zero_calls_and_zero_rows`). No provider object is built on the disabled path.
- Grounding: `build_catalog(db, household_id, category)` reads ACTIVE assets whose active classification
  assertion carries the mapped slug, plus the expiry assertion (`expiry_date`, `opened_date`, `date_type`) and any
  `source_attribution` rows. `build_user_content` puts that JSON between `<<<CATALOGUE_DATA>>>` /
  `<<<END_CATALOGUE_DATA>>>` and appends the user question. The versioned system prompt (`chat-v1.md`) states the
  block is untrusted DATA, never instruction content.
- **Cross-category refusal:** the supported set is enforced via `resolve_category` → 422; and the grounding is
  category-scoped, proven by `test_chat_grounded_answer...` (a seeded `medicine_pharma` asset never appears in a
  `food` request's user content). Smallest case: `POST /v1/chat/snacks` → `422` with 0 calls and 0 rows.
- **Empty category data:** a valid path, not an error — `{"status":"ok","empty_catalogue":true,
  "catalogue_size":0,"answer":<fixed no-data sentence>}` with **0 provider calls** (`PG-SC-07`; test
  `test_empty_catalogue_is_a_valid_path`).
- **Corrections:** `POST /v1/chat/{category}/corrections` writes one append-only `guardrail_event`
  (`kind="correction"`, detail carries `message` + `category` + `source="user"`). `test_model_output_cannot_trigger_a_write`
  feeds a scripted answer that *says* to log a correction and asserts zero guardrail rows: the write is reachable
  only from the explicit user route.
- **Injection posture:** `test_injection_string_stays_inside_the_data_section` seeds a hostile asset label, asserts
  it lands strictly between the data delimiters, and asserts it never reaches the system instruction.
- **No execution path:** `test_chat_grounded_answer...` fingerprints assets+assertions before/after and asserts
  equality.
- **Secrets:** prompt sees label data only; a sentinel-key test asserts no written row carries key material.
- **Budget:** an over-cap estimate returns `{"status":"refused"}` with 0 calls/rows (test
  `test_budget_refusal_before_any_call`).

## G3 — chat screen (`frontend/src/routes/ChatPage.tsx`, `frontend/src/components/ChatTranscript.tsx`)

- React-query screen registered in `App.tsx` (nav + `/chat` route, in the ceiling this time per M10): household
  select, Food/Medicine category select, in-state transcript, question input + Send, and a separate correction
  input + **Log correction**. Skips/failures surface in a `role="alert"` with the reason. No schedule, no
  auto-send, no streaming.
- Tests beside both files: send → reply rendered; category selection drives the request; correction action posts
  (`PG-SC-02` forward trace: screen → `logChatCorrection` → backend route → guardrail row asserted in
  `test_correction_is_user_initiated_and_writes_one_event`); a skipped call surfaces `consent_disabled`; an
  unsupported-category error surfaces.

## G4 — proof

- **FAIL-then-PASS (raw in `SG-038_verify.log`):** backend new file `11 failed` at base `084810b` (routes/service/
  adapter op absent) → `11 passed` post-change; frontend `2 test files failed` (screen/component absent) →
  `7 passed` post-change. Both raw runs are committed with this report (`PG-EV-01`, `PG-EV-09`).
- **Offline gates (zero network):** 11 backend tests green with `opencode_go.OpenCodeGoProvider._post` patched to
  raise (`network_attempts` asserted `[]`); 7 frontend tests green (`vitest` 40 passed overall).
- **Full suite:** `2 failed, 160 passed, 13 warnings in 10.24s`. The two reds are
  `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and
  `test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` — the base-proved decoder environment legs
  (`pyzbar`/`libzbar` and `pytesseract`/`tesseract` absent in this sandbox), **re-verified at base** (`2 failed in
  0.64s`, same warnings), not inherited.
- **`ruff`:** `All checks passed!` **`mypy app`:** `Found 40 errors in 9 files` — identical count and file set to
  base `084810b` (`40 errors in 9 files`, checked 66 vs 69 source files); no touched file
  (`chat/`, `api/v1/chat.py`, `opencode_go.py`, `fake.py`) appears in the output.
- **Build:** `npm run build` green (`tsc && vite build`, 97 modules, `built in 881ms`).
- **Hygiene:** secret scan 0 in new/changed source (the only matches are the pre-existing key-resolver lines in
  `opencode_go.py:207-214`, which the text op does not touch); `alembic heads` unchanged; no `extract-*-v1.md` or
  `planning-v1.md` diff; no ignored file staged.
- **Health probe — `unanswered`:** `docker compose ps` lists `0 services`; port 8000 answers a foreign service
  (`Not Found`). No stack is running and starting one is deploying (out of scope per the packet's
  privileged-denial path).
- **No vacuous pass:** the secret-scan test asserts the provider-call and correction rows exist before scanning
  (it failed at base for exactly that reason), the cross-category test seeds a real other-category asset, and the
  payload test asserts positive shape as well as absent image/key material.

## G4-live — the ONE metered leg (temp SQLite; last)

- Ceiling printed and checked BEFORE the run: `CEILING=$0.05000 worst_case_estimate(1 call)=$0.001525` →
  `ceiling_check=PASS`.
- Exactly **one** call: provider-returned model `deepseek-v4-flash-vision-exp`, latency `2114.39ms`,
  usage `{"prompt_tokens":594,"completion_tokens":157,"total_tokens":751,"completion_tokens_details":{"reasoning_tokens":33}}`,
  cost **`$0.0001833`**; `TOTAL=$0.000183 / CEILING=$0.05000` → `ceiling_total_check=PASS`.
- Ledger row exists: `provider_call_rows=1` (`job_id` NULL, `prompt_template_version=chat-v1`),
  `run_status=ok category=food catalogue_size=1`, `answer_len=432`. Key never printed; no second run.

## G5 — worklogs (unconditional, `CO-57`)

`docs/worklogs/SG-038.log`, `SG-038_report.md`, `SG-038_verify.log` — first token `SG-038`; elapsed-versus-budget
per leg with units; model/effort provenance; spend lines; live-state ledger; three UNCLEAR lines.

## G6 — receipt note on the notes ref (proven shape, unchanged obligation)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
Note added on the work HEAD LAST (120s bound):

```
git notes --ref=refs/notes/storagegenie-coder-reports add \
  -m "Dispatch-ID: SG-038 | Report: docs/worklogs/SG-038_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`); verified with `show <WORK_HEAD>`; executed output
quoted in the delivery message. Final line: `note=yes`.

## Budget — actual vs bound (per leg, units)

| Leg | Actual | Bound |
|---|---|---|
| Premise probes (all reads) | ~60 s wall | 120 s/probe |
| Backend new-file pre/post | 1.06 s / 1.08 s | 600 s suite class |
| Full backend suite | 10.24 s | 600 s |
| Frontend pre/post | 0.49 s / 0.72 s | 600 s vitest |
| Full vitest | 2.32 s | 600 s |
| `npm run build` | 881 ms (97 modules) | 600 s |
| Live leg | 2.1 s call, 1 call | $0.05 single live run |
| Overall session | 361 s at log capture | 2400 s overall / 1800 s early-close |

## Live-state ledger

- Live spend total: **`$0.0009053`** (`$0.000722` prior + `$0.0001833` this slice; quoted above).
- Offline spend: **`$0`** (all offline gates zero network; adapter `_post` patched to raise, `network_attempts == []`).
- Network attempts: exactly the live leg's **1** provider call (proven count; offline tests assert 0).
- Live DB writes: **0** to production — the live leg ran against
  `database=sqlite:////tmp/opencode/sg038/live.db` (asserted temp and quoted in the live output); the production DB
  path was never opened.

## Findings, disagreements, corrections (including out-of-scope)

1. **`F-SG038-1` (see above)** — no `protocols.py` change: the declared `OcrProvider.extract_text` is an OCR
   capability, not the chat signature, and the router never type-checks the Protocol. Overloading it would add
   vocabulary the packet forbids. Reported so the Architect can rule.
2. **`opened_date` grounding is best-effort until `SG-040`** — the chat catalog exposes it from the expiry
   assertion when present, else `null`. No chat behaviour depends on it.
3. **`finish_reason` in `normalized_output` is a design call** — the packet left the normalized text shape to be
   decided and reported. It carries `text`, `model`, `finish_reason`; the service consumes only `text`.
4. **Health probe stays `unanswered`** — no stack is running in this sandbox; starting one is deploying. Compose
   `0 services` and the port-8000 foreign-service response are the evidence.

## UNCLEAR

- **FIRST READ:** whether the Architect expected `protocols.py`'s `OcrProvider.extract_text` to be re-signatured
  for the chat op (`F-SG038-1`), or whether "no new protocol, no new vocabulary" means the Protocol stays as the
  OCR declaration and the real adapter's concrete signature is authoritative.
- **DURING EXECUTION:** whether the empty-catalogue path should still invoke the model (I return a fixed,
  deterministic no-data answer with 0 calls, which keeps the path $0 and injection-free), and whether an answer
  turn should also write a guardrail event (I write only the `provider_call` ledger row for answers; the
  `correction` event is the sole guardrail row, user-initiated).
- **REMAINING:** the disposition of the 2 base-proved decoder environment reds; whether `opened_date` (SG-040)
  should change the chat grounding once persisted; and whether chat answers should ever be persisted as history
  (out of scope here — the transcript is component state only).
