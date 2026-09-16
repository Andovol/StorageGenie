# SG-049 — extraction v2: AI quantity/unit/asset-type through candidates + label fallback + chat pointer

**Dispatch-ID:** SG-049 · **Coder:** opencode · **Effort:** `medium` (read from process args: `/proc/923108: opencode run --auto --dir /home/andrei/StorageGenie --variant medium …`) · **Model:** `unknown` (no model id on argv; the CLI default IS the model and is omitted per policy — never read from an identity line).
**Contract:** 0.27.0 (recorded == published payload == SG-048 receipt echo). **Spend:** **$0.000000** metered — the live leg is unrun (G0 STOP).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`.
**DATABASE:** production SQLite `sqlite:////data/db/storagegenie.db` is for the LIVE LEG ONLY; the live leg is unrun, so the production DB was read once (arithmetic only) and written by nothing. Every test used scratch temp SQLite.

- **BASE REF requested:** `origin/automation`; **resolved commit:** `a969e188124c34d08aaeb3caccc5d2bd92410b32` (`SG-049 packet (S3 extraction v2 AI fields, L3/D74 chain)`).
- **WORK_HEAD:** the commit carrying these three worklogs — stated in the delivery message (it cannot be stated inside a file that is itself part of that commit, same as SG-048/SG-053/SG-054). The receipt note is attached to it LAST; no commit follows.
- **Slice wall-clock:** start `2026-09-16T20:42:24Z`; close `2026-09-16T20:48Z` (~350 s vs 1500 s early-close / 2400 s overall).

## 1. G0 — enablement gate QUOTED FIRST (both outcomes handled)

Read-only, before any provider touch:

```
$ curl -s http://localhost:8003/v1/settings/ai
{"provider_id":"fake","model_id":"deepseek-v4-flash-vision-exp","allowed_model_ids":["deepseek-v4-flash-vision-exp"],"consent":false,"per_job_cap":null,"monthly_cap":null,"prompt_category":"food"}
$ docker exec storagegenie-backend-1 python -c "... existence-only key probe ..."
opencode_api_key_present= True
key_len= 67
consent= False
provider_id= fake
$ docker exec storagegenie-backend-1 python -c "from app.services.providers.reader import ai_status; print(ai_status())"
ai_status= (False, 'consent_disabled')
$ curl -s http://localhost:8003/v1/health
{"status":"ok","db":"ok","storage":"ok"}
```

- (a) `consent=true`? **NO** — `consent=false`.
- (b) provider key exists? **YES** — existence-only boolean (len 67); **zero key bytes printed, logged, quoted, or committed**. `docker compose config` was never run.
- (c) `ai_status()` enabled? **NO** — `(False, 'consent_disabled')`.

**Outcome: STOP-as-SUCCESS.** The enablement pre-step (D73/D62: `.env` key + `SG_CONSENT=true` + restart) is not in place. No provider call was made and no provider call precedes this gate. Offline proofs ship; the live leg (G5) is unrun. **This is the successful outcome for a STOP gate, not a failure.**

Premise correction: the packet's G0 says `GET /settings/ai`; the app mounts routes under the `api_prefix` `/v1` (`config.py:16`), so the live read is `GET /v1/settings/ai`. Both were probed: bare `/settings/ai` returns the SPA HTML (frontend fallback), not JSON.

## 2. Starting tree

```
$ git status --porcelain          # (empty)
$ git branch --show-current       # automation
$ git rev-parse HEAD ; git rev-parse origin/automation
a969e188124c34d08aaeb3caccc5d2bd92410b32
a969e188124c34d08aaeb3caccc5d2bd92410b32
```

Clean and level: no STOP. Backend container healthy on `127.0.0.1:8003->8000`; frontend container exited 5 days ago (the backend serves the built SPA). **Nothing pushed to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.**

## 3. Premises re-verified in-slice (quoted reads, `PG-IC-09`)

- **`providers/schemas.py:30-41`** — `ExtractionItem` carried `name/expiry_date/opened_date/date_type/lot/confidence/uncertainty_reasons`, `extra="forbid"`. **Matches**; new keys were indeed rejected before this slice.
- **`candidates.py:25`** — `GATED_FIELDS = {identifier, expiry, expiry_date, opened_date, condition, lot}`. **Matches.**
- **`candidates.py:75-80`** — `_review_state_for(field_path, confidence)`: gated → `proposed`; else threshold. **Matches.**
- **`candidates.py:234-253`** — the `lot` block is the extraction-provenance template. **Matches.**
- **`candidates.py:346-360`** — `_create_asset_for_candidate` already reads `asset_type` (`:347`), `quantity`/`unit` (`:349-350`) via `_field_parts`. **Matches — no hunk made** (verified, not silently added).
- **`reader.py:51-55`** — `PROMPT_FILES` mapped the three v1 files. **Matches.**
- **`reader.py:97-103`** — `ai_status()` consent → provider-registry → enabled. **Matches.**
- **`settings.py:26`** — `ALLOWED_MODEL_IDS = ("deepseek-v4-flash-vision-exp",)`, vision path only. **Matches.**
- **Three v1 prompts** — `extract-{food,medicine,cosmetics}-v1.md` exist, versioned, no-inference rule. **Match.**
- **`planning/service.py:153`** and **`chat/service.py:179`** — raw `asset.display_name` into `"label"`. **Match.**
- **`ChatPage.tsx` notice block** renders `Chat did not run: consent_disabled` with no pointer. **Matches.**
- **`backend/eval/corpus/sg029/`** — **10** fixtures + `manifest.json` + images. The packet says "9 fixtures" — **correction: 10** (manifest `count: 10`).

## 4. G1 — schema v2 (`providers/schemas.py`)

Added to `ExtractionItem`: `quantity: float | None` (validator rejects non-finite and `< 0`), `unit: str | None` and `asset_type: str | None` (`max_length=50`, non-blank when present). `extra="forbid"` unchanged; the generic `unknowns` machinery (`UNKNOWN_PATH_RE` + `field_name not in ExtractionItem.model_fields`) covers the new paths with **no change**. Contract tests added in `tests/test_extraction_contract.py` (parse each field; every invalid shape fails; unknowns-entry rules hold for the new paths) and exercised again in `tests/test_sg049_v2_extraction.py`.

## 5. G2 — prompts v2 (three NEW files) + `PROMPT_FILES`

- New `extract-food-v2.md`, `extract-medicine-v2.md`, `extract-cosmetics-v2.md`; front matter `template_version: extract-*-v2`; v1 rules plus transcribe-only `quantity` (no arithmetic, no serving-size math), verbatim `unit` (null when absent), printed `asset_type` (null when unclear); illegible/absent → null + `unknowns`; `confidence < 1.0` requires reasons (schema-enforced); JSON-only. Repair sections preserved.
- `reader.py PROMPT_FILES` → v2 filenames. `repair_prompt` unchanged (it names no field; verified).
- **v1 files provably untouched:** `git diff --stat -- extract-food-v1.md extract-medicine-v1.md extract-cosmetics-v1.md` → **empty**.

## 6. G3 — candidate plumbing + label fallback

- `GATED_FIELDS` gains `quantity`, `unit`, `asset_type`. Extraction-sourced values are therefore ALWAYS `review_state="proposed"` (M11 / F4 Stage 0 — human confirms, no threshold auto-accept).
- `build_candidate_from_extraction` maps `item.quantity`/`item.unit`/`item.asset_type` with the full extraction provenance (confidence/provider/model/template/call id) via a small `_extraction_value_field` helper (keeps ruff `C901` green). Double-quote the value: nothing is set when the value is null (never guessed).
- **F-SG048-2:** ONE shared constant `UNTITLED_LABEL = "Untitled"` in `app/models/asset.py`, read at **`planning/service.py:153`** and **`chat/service.py:179`**. Cycle-free because `app/models/asset.py` imports only `app.db` and `app.models.base`; the service layer imports the model, never the reverse. A test asserts **both** call sites fall back (`test_nameless_labels_fall_back_in_both_ai_catalogs`), and the pre-existing SG-048 test was updated from `label is None` to `label == UNTITLED_LABEL`.
- **Enumeration:** production readers of `asset.display_name` on the AI-catalog paths are exactly these two (`planning/service.py build_catalog`, `chat/service.py build_catalog`). No third was found.

## 7. G4 — eval: v2 measured without moving the v1 baseline

**v1 frozen eval path, PRE and POST, byte-identical** (`diff` = "Files are identical"):

```
field_accuracy=0.833 over 10 fixtures
unknown_rate=4/7=0.571
correction_rate=0/6=0.000 (audit_event plugin.assertion.write rows=6)
```

New-field scoring rides **new** scoring-only fixtures under `backend/eval/corpus/sg049/` (manifest + 3 fixtures carrying v2 ground truth and offline-authored `provider_output`; no image, no metered call — G0 STOP). **SG-029 bytes untouched:** the ten `sg029_*.json` + `manifest.json` show zero changes (`git status` clean for that dir). The scorer lives in the new test and is proven non-vacuous (a wrongly transcribed `unit` scores `< 1.0`).

- **`PG-EV-04` (shape-of-unsent):** `test_v2_request_payload_shape_carries_prompt_and_json_object_flag` asserts the real outgoing builder `build_chat_payload(...)` emits `response_format == {"type": "json_object"}`, `stream == False`, the image part, and the exact v2 prompt text. Nothing about the payload is mocked.
- **`PG-SC-09` (name-the-world):** the live leg could parse cleanly yet be *wrong* — e.g. the model transcribes a per-serving amount as the pack `quantity` (arithmetic the prompt forbids but a text model can still slip), or picks an `asset_type` slug that maps to the wrong canonical category downstream. The slice still ships because (i) the new fields are in `GATED_FIELDS`, so every extraction value is committed `review_state="proposed"` and never auto-applies, (ii) `confidence`/`uncertainty_reasons` are mandatory and travel with the value, and (iii) the human review gate this slice relies on is not weakened.

## 8. G5 — live leg: UNRUN (G0 STOP)

Zero images, zero provider calls, zero ledger rows, **real spend $0.000000**. Per-call raw: none exists (correctly — no call). The worst-case bound was not consumed: no call was admitted. Pre-existing live ledger rows: `provider_call` count = **0**.

**`PG-IC-08` blast radius (read-only arithmetic, no write):**

| table | count |
|---|---|
| asset | 1 (`display_name` = `Toothpaste`) |
| candidate | 0 |
| job | 0 |
| evidence | 1 |
| assertion | 3 |
| audit_event | 3 |
| provider_call (ledger) | 0 |

Identical before and after (nothing in this slice writes the production DB).

## 9. G6 — chat pointer (source shipped; container deploy unrun)

`ChatPage.tsx`: the `consent_disabled` notice gains one plain line + link `Enable AI in Settings to use chat` → `/settings`; no other Chat restyle. `ChatPage.test.tsx` asserts the link renders in the disabled state and is absent on the enabled path. **The `PG-PR-04` rebuild/up + served-bundle/gate checks are UNRUN**: the packet scopes the backend restart to the LIVE LEG ("Restart: backend container via compose rebuild+up …" under the DATABASE/LIVE-LEG line), and the live leg is unrun on the G0 STOP. Offline substitute evidence: local `npm run build` produced a changed bundle hash (`index-GQSnPT8t.js` → `index-DgNLBrnK.js`). The served app still runs the old bundle — reported, not hidden.

## 10. FAIL-then-PASS (`PG-EV-09`) and mutations

- **Pre-change failing run (raw in `SG-049_verify.log`):** the new module failed to import (`UNTITLED_LABEL` absent) and 4 targeted tests failed (`test_load_prompt_cosmetics…`, two new v2 contract tests, `test_catalog_builders_tolerate_null_name`), plus the 2 consumer version assertions — total evidence of a genuine red state.
- **Green run:** targeted suite `49 passed`; full backend suite `222 passed, 2 failed` where the 2 are the **pre-existing** `test_signals` failures.
- **Mutations caught singly (4/4):** (A) quantity validator neutralised → 4 failed; (B) `quantity/unit/asset_type` removed from `GATED_FIELDS` → 1 failed; (C) chat label fallback removed → 1 failed; (D) `PROMPT_FILES` reverted to v1 → 1 failed. Raw in `SG-049_verify.log`; worktree restored (25 passed after).

## 11. Gates / hygiene

- Backend suite: `222 passed, 2 failed` — the 2 are **pre-existing**, not caused here: base commit `a969e188…`, command `./venv/bin/python -m pytest tests/test_signals.py -q`, output `2 failed, 5 passed` (barcode `pyzbar`/OCR `pytesseract` environment). `test_signals.py` is unmodified by this slice (`git diff` empty). **Destination: environment provisioning, not this slice.**
- Frontend suite: `144 passed (21 files)`; `eslint src` green; `tsc && vite build` green.
- Backend lint: `ruff check app tests eval` → **All checks passed!**
- Secret scan: diff + untracked grep for key patterns → **no matches**; worklog files grep-gated before commit → no matches. Zero key bytes anywhere. `docker compose config` never run.
- **No migration** (no `backend/alembic` change — candidate fields are JSON). **No dependency change** (`pyproject.toml` / `requirements.lock` untouched). No ignored file staged. Nothing pushed to `storagegenie-evidence`.

## 12. Budget (actual vs cap, per leg, units)

| Leg | Actual | Cap |
|---|---|---|
| G0 recon + gate proof | ~35 s | 120 s (ordinary) |
| G1–G3 + G6 source edits | ~120 s | 2400 s overall |
| G4 eval pre/post + G2 prompts | ~60 s | 600 s |
| Test authoring + pre-change failing run | ~120 s | 600 s |
| Suite + lint + build (backend + frontend) | ~75 s (pytest 14.06 s, ruff <1 s, vitest 4.05 s, build 1.64 s) | 600 s |
| Mutations (4, singly) | ~25 s | 120 s |
| G5 live metered leg | 0 s ($0.000000) | G5 bound — UNRUN |
| **Overall wall-clock** | **~350 s** | 1500 s early-close / 2400 s overall |

## 13. Receipt note

Work is pushed to `automation` with the worktree clean (`CO-55`). **No** push to `storagegenie-evidence`, **no** `{{RECEIPT_CMD}}`. A note is added on WORK_HEAD under `refs/notes/storagegenie-coder-reports`, pushed, then verified against the explicitly fetched refspec (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`, then `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>`). Per the SG-048/SG-053/SG-054 convention, that `show` output is pasted verbatim **in the delivery message** — it cannot live inside this file, which is itself the noted commit. `note=yes`.

## Findings / deviations

- **F-SG049-1 (over-ceiling test hunk, disclosed):** `PROMPT_FILES → v2` changes the recorded `prompt_template_version`; two out-of-ceiling files asserted the literal v1 string — `tests/test_ai_pipeline.py` (3 assertions) and `tests/test_phase2_e2e.py` (2 assertions). I updated **only those five version literals** so the mandated green suite holds. This exceeds the ceiling's named test files; I judged it covered in spirit by "plumbing test hunks". **Destination:** Architect rating.
- **F-SG049-2 (behavioral consequence):** adding `asset_type` to `GATED_FIELDS` also gates the DETERMINISTIC `asset_type="unknown"` placeholder to `review_state="proposed"`. The default VALUE stays `"unknown"` exactly as the packet requires, but the placeholder now enters human review. No in-scope test breaks (`test_phase2_e2e` asserts every `GATED_FIELDS` row is proposed). **Destination:** confirm intent (likely desirable, but it is a change to the deterministic path).
- **F-SG049-3 (premise):** G0's route is `/v1/settings/ai`, not `/settings/ai`; the sg029 corpus has **10** fixtures, not 9.
- **F-SG049-4 (deploy unrun):** G6's container rebuild/up and served-bundle/gate checks are unrun under the G0 STOP (restart is scoped to the live leg). Reported, not silently skipped.
- **Split inheritance (not in scope):** `_split_child_fields` shares origin fields (including any extraction `quantity`/`unit`/`asset_type` on item 0) to every split child; multi-item splits with per-item counts would need split-side handling. Out of the ceiling; flagged for a future slice.

## UNCLEAR

- **FIRST READ:** whether G0's STOP path expects the *whole* offline slice (G1–G4/G6-source) or only the gate proof. I read "commit offline proofs" as "ship the offline-verifiable slice", so the schema/prompts/plumbing/labels/pointer are implemented and tested; deploy and live leg are not.
- **DURING EXECUTION:** the version-string conflict (F-SG049-1) — I chose the minimal over-ceiling test edits to keep the suite green rather than STOP with the central G2 hunk omitted; a ruling is owed.
- **REMAINING:** whether deterministic `asset_type="unknown"` should be gated to `proposed` (F-SG049-2), and whether per-item `quantity`/`unit` need split-side propagation (F-SG049-4).
