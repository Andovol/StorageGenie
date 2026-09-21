# SG-080 — photo-ingest pipeline on v3: reader flip + transcript evidence + category proposed

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE REF (packet ref `origin/automation`):** `45727cf4244384b33858e6bf23dd6a8468872c12` (start HEAD == `origin/automation`; the packet requested `origin/automation` and it resolved here — two fields, not one)
**WORK_HEAD:** `PENDING` (filled after the work commit; the receipt note rides this hash)
**Contract:** recorded `0.28.2` == published `0.28.2`; source `/home/andrei/storagegenie-contract/VERSION` (contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2`). Note: `.rules-cache/` is absent from this worktree; the source read is the contract repo path.
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`; read from provider metadata `/home/andrei/.local/state/opencode/model.json` `recent[0] = {"providerID":"opencode-go","modelID":"deepseek-v4.1-flash"}` — **not** a system-prompt identity line; argv carries no `--model`) · effort `medium` (process argv `/proc/488842/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-080 …`)
**Spend (real $):** `$0.000919` actual vs a `$0.015` bound (units USD) — ONE metered 200 body ($0.000919) plus one HTTP 503 error leg ($0.0, no body); both ledgered in the temp DB. `$0` outside G5.
**Autonomy:** `L2` slice (1 retry available; not used).
**Containment (`PG-PR-04`/`PG-PR-06`/`PG-PR-10`):** no deploy, no restart, no production touch. The flip takes effect on the next rider deploy (SG-083). The live leg ran against a TEMP SQLite DB (`/tmp/opencode/sg080/live.db`) and TEMP storage; the production DB (`data/db/storagegenie.db`) was never opened.

D101-approved slice 2 of the photo-ingest track (plan `docs/superpowers/plans/2026-09-21-ai-ingestion-enrichment.md` Task 2; spec §2). SG-079 shipped the strict v3 schema + frozen v3 prompts with the live path still on v2. This slice **flips the reader to v3**, **persists transcripts as retrievable evidence**, carries **`category_proposed` as a visible gated proposal**, preserves every other v3 field through `ai_items` (explicitly deferred from accept-writable promotion), keeps split-first + consent + ledger, and ran **exactly one bounded live leg** when G0 came back green.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on tree | Verdict |
|---|---|---|
| `reader.py:50-55` `PROMPT_FILES` maps v2 for all three | `reader.py:51-55` (pre-flip) — exactly v2 | **confirmed** |
| SG-079 v2-pin test is `test_live_prompt_map_still_points_at_v2` | `test_sg079_v3_schema.py:193` — exactly that name | **confirmed** |
| Evidence write path is the `Evidence` constructor via `store_evidence`; no job FK | `evidence_service.py:134-219` + `models/evidence.py` (no `job_id`; job link is `job.config_snapshot["evidence_ids"]`) | **confirmed** |
| `GATED_FIELDS` is what gates candidate fields | `candidates.py:25-39` + `_review_state_for` at `:114-119` | **confirmed** |
| `ai_items` already carries `item.model_dump()` | `candidates.py:315` (pre-change) | **confirmed** |
| BASE `origin/automation` == start HEAD | both `45727cf…` | **confirmed** |
| Contract recorded == published | `0.28.2`; contract HEAD `b495b59` | **confirmed** |

**One premise difference (finding, not obstacle):** the packet's G5 says "≤3 COMMITTED images … worst-case bound $0.015". With the food v3 prompt (5043 bytes) the sum of the adapter's own upper-bound estimates for the 3 smallest committed sg029 PNGs is **$0.012257**, inside the bound. The 3 chosen are `sg029_09_no_date_visible_cosmetics.png`, `sg029_01_clean_food.png`, `sg029_10_partial_label_cosmetics.png`. No bend needed.

## G0 — enablement re-gate: **GREEN** (live leg runs)

Raw in `SG-080_verify.log` §R-G0. Key presence reported as boolean/length only (zero key bytes printed, logged, quoted, or committed); `docker compose config` never run.

- `opencode_api_key_present= True`, `key_len= 67`
- `consent= True`
- `provider_id= opencode-go` — and the SELECTED adapter is real: `registry_ids= ['fake', 'opencode-go']`, `registry_has= True`, `selected_model_id= deepseek-v4-flash-vision-exp`
- `ai_status= (True, 'enabled')`; **route function** = `app.services.providers.router.ProviderRouter.execute` (the call the reader builds at `reader.py:362`)

M32 lineage satisfied: not only `ai_status`-enabled — the metered adapter `opencode-go` is the selected provider id in the registry the call resolves against, and the route function is named.

## G1 — reader flipped to v3 (live behaviour change, fully traced)

`reader.py:51-55` now maps `food/medicine/cosmetics → extract-<cat>-v3.md` (hunk quoted in the diff). v1/v2 prompt files are byte-untouched: `git diff --stat` over the six `*-v1.md`/`*-v2.md` files is **empty** (raw, §R-G1-PROMPTS).

**FAIL-then-PASS:** the SG-079 freshness pin was updated to the v3 expectation and **failed pre-flip** (`1 failed … AssertionError: assert {'food': 'extract-food-v2.md', …} == {'food': 'extract-food-v3.md', …}`, §R-G1-FAILPRE) and **passed post-flip** (`1 passed`, §R-G1-PASSPOST). It is a freshness pin (`PG-SC-09` inverse), not a regression.

**Full-tree v2-pin enumeration** (criterion: `extract-.*-v2` | `PROMPT_FILES` | `template_version.*v2`; raw list in §R-G1-ENUM). Every live pin was updated to v3:
- `test_sg079_v3_schema.py` — map + runtime version (the pinned test above; also its docstring).
- `test_ai_pipeline.py:207,505,518` — three live pipeline assertions.
- `test_phase2_e2e.py:254,279` — food + medicine provenance versions.
- `test_extraction_contract.py:303` — `load_prompt("cosmetics")` version.
- `test_sg049_v2_extraction.py:137` — the configured-prompt version (test renamed `…_are_v3_…`).

**Intentionally v1/v2-locked (reported, not updated):** `test_sg049_v2_extraction.py:204,213` use an **injected** scripted `"extract-food-v2"` literal and assert the envelope echoes it — that is provenance-plumbing self-consistency, not a read of the live `PROMPT_FILES` map, so it stays v2 by design.

**Ledger row crosses the real boundary (`PG-SC-12`):** the SG-080 e2e test asserts `ProviderCall.prompt_template_version == "extract-food-v3"` on the row written by the real reader (`test_pipeline_ledger_rows_carry_v3_template_version`); the live leg's ledger row also reads `extract-food-v3` (§R-G5).

## G2 — transcript persisted as evidence (never an assertion value)

**Write-path enumeration (measured, not assumed):** `Evidence` rows are created by `store_evidence` (`evidence_service.py:134`) for uploads; there is **no evidence→job FK** — the tree's only job↔evidence link is `job.config_snapshot["evidence_ids"]` (read by `reader._job_evidence_ids`, `candidates._job_evidence_ids`, `dedup._evidence_ids`). Decision (mine, reported): a transcript gets its **own `Evidence` row** (`source_kind="transcript"`, `media_type="text/plain"`) via a new writer `evidence_service.store_text_evidence` (hunk quoted + reason), and is **linked to the same job** by appending its id to the job's `evidence_ids` (source image stays first, so the deterministic display name is unchanged). The row's `sha256` is the **artifact identity** (household + source evidence + item index + text), not a bare content hash: bare content addressing would collide across households on generic label text and violate the global unique `evidence.sha256` constraint. The stored file content is the transcript verbatim.

Evidence (raw in the report tests): `test_transcript_persisted_as_evidence_linked_and_readable` proves the row exists, is `text/plain`, its id is in `job.config_snapshot["evidence_ids"]` after the source image, and its bytes are retrievable through the EXISTING read path `GET /v1/evidence/{id}` + `/v1/evidence/{id}/file`. `test_transcript_never_lands_in_assertion_values` commits the candidate and scans every `Assertion.value_json` on the asset — the transcript text is absent, and no value carries `"transcript"`.

**Finding F-SG080-2 (self-caught by the live leg, fixed):** the first implementation persisted transcripts *inside* the per-image loop. The live leg's image 1 succeeded (creating a transcript row) and image 2 returned HTTP 503; `_write_error_ledger` **commits** on error, which persisted image 1's flush-even-though-the-job-failed transcript row **unlinked**. Fixed by deferring all transcript writes until after every image extracts (so "transcript evidence exists iff the job extracted"), with offline regression `test_partial_job_failure_leaves_no_unlinked_transcript` (2 images, 2nd fails → 0 transcript rows). The live leg was **not** re-run (one bounded live leg).

## G3 — category proposed + v3 fields preserved

- **Gating lives in `GATED_FIELDS`** (`candidates.py:25`), consumed by `_review_state_for` → `review_state="proposed"`. Extended in place (hunk quoted): `"category_proposed"` added. Also added to `ALLOWED_CANDIDATE_FIELDS` (the whitelist `_create_asset_for_candidate` enforces), because a gated candidate field that reaches commit must pass the whitelist. `category_proposed` is populated from the item (per-item) and added to `_split_child_fields`' item-derived set.
- **Visible read path (named):** `GET /v1/candidates/{candidate_id}` (`api/v1/candidates.py:120`) returns `proposal["fields"]`; the e2e test reads `fields.category_proposed.value == "dairy"` through the real route. So it is **not** `ai_items`-only.
- **Gated at any confidence:** `test_category_proposed_visible_gated_and_never_auto_accepted` runs with `sg_confidence_threshold=0.0` and confidence 1.0, accepts the candidate, and asserts the committed `category_proposed` assertion is `review_state="proposed"` with `source_type="extraction"`. It never auto-accepts.
- **Other v3 fields preserved byte-equal / deferred:** `test_other_v3_fields_preserved_byte_equal_in_ai_items_and_deferred` drives the REAL `build_candidate_from_extraction` on a v3-shaped `ExtractionOutput` and asserts `brand, variant, size_text, barcode, storage, warnings, allergens, nutrition_per100g, nutrition_serving` (and `transcript`) cross into `ai_items[0]` equal, AND that none is in `ALLOWED_CANDIDATE_FIELDS` nor in `fields`. Accept-writable promotion is **explicitly deferred** (not silent) — these ride `ai_items` only; a later slice (Enrich/review-mapping track, Task 4) promotes them.

## G4 — split-first + end-to-end on scripted v3 ($0)

- **Split-first:** `test_multi_item_v3_splits_first_with_per_item_quantity` runs a 2-item v3 payload through `run_job`, sees the `candidate.multi_item` task, splits via `POST /v1/candidates/{id}/split`, and asserts per-item `quantity` (2.0 vs omitted-null), per-item `category_proposed` ("dairy" vs omitted), and `unit` per item — SG-049/SG-058 lineage verified, not assumed.
- **End-to-end through the REAL `run_ai_extraction`:** extraction → transcript evidence → candidate → gated review; consent gate and monthly-ledger refusal both exercised **before any call** (`test_consent_gate_refuses_before_any_call`: 0 invocations / 0 ledger rows; `test_monthly_ledger_refuses_before_any_call`: prior $0.6 ledger spend + $1.0 estimate vs $1.5 cap → FAILED step, 0 invocations).
- **Request shape (`PG-EV-04`):** `test_v3_request_wire_shape_carries_prompt_and_json_object_flag` asserts the exact v3 prompt text in the `build_chat_payload` content, `response_format={"type":"json_object"}`, and `test_pipeline_ledger_rows_carry_v3_template_version` asserts the seam received the v3 prompt and a redacted PNG (`\x89PNG…`, empty EXIF).
- **Null-heavy v3** covered (`test_null_heavy_v3_items_are_handled`): all v3 fields null → no transcript row, no `category_proposed` field, job green.
- **Suite / lint / type / secrets:** full backend suite **2 failed, 356 passed** — the **same 2 base decoder reds** as the clean-BASE baseline (2 failed, 344 passed); ruff `All checks passed!`; mypy **41 errors in 9 files** == baseline (delta 0); secret scan 0. Raw in `SG-080_verify.log`.
- **Non-vacuity:** with only the three source files stashed, the new test file fails **6 of 11** (the G1–G3 feature tests), proving the tests exercise the new code (raw §R-G4-VACUITY). `job_service.py` needed NO change and is untouched; `router/schemas/prompts-content/models/alembic/compose/.env/eval/run.py` untouched (`eval/run.py` carries the F-SG079-1 default).

## G5 — exactly one bounded live leg (G0 green)

≤3 committed images (`backend/eval/corpus/sg029/images/*.png`, `PG-EV-07`) through the real pipeline on a TEMP DB with the real metered `opencode-go` adapter. **Worst-case bound `$0.015`; adapter-estimate sum `$0.012257` for the 3 chosen images** (`PG-IC-04` multiply-out on the worst case). Actual metered **`$0.000919`** (USD; one 200 body; ratio 0.0613 of bound).

- Image 1 (`sg029_09_no_date_visible_cosmetics.png`) returned a billable 200: `cost=0.000919`, `usage.total_tokens=2710`, `template_version=extract-food-v3` — **v3 survives one real metered call, within bound**.
- Image 2's call returned **HTTP 503** (`"http_status: provider returned HTTP 503: ''"`, cost 0.0, no usage) → the single-repair path raised `ExtractionFailedError`, step `ANALYZING_WITH_AI FAILED`, job `FAILED`. This is a **provider-side FINDING, not a slice failure** (G4 green), quoted raw in §R-G5. No third image was attempted (the job aborted).
- Rows created (job/evidence/provider_call), **reported and LEFT in the temp DB** (`PG-EV-06`, authority NONE): job `01a0c467-84ff-74e1-9c57-5a6a8c2f0588`; evidence `01a0c467-84c3-…`, `01a0c467-84e0-…`, `01a0c467-84fc-…` (uploads) and `01a0c467-9d20-…` (the pre-fix orphan transcript, see F-SG080-2); provider_call `01a0c467-9d1e-…` (200, $0.000919) and `01a0c467-ab52-…` (503, $0.0). No candidate row (aborted before BUILDING_CANDIDATES). Production never touched (`PG-PR-10`).

## G6 — worklog and report

- `docs/worklogs/SG-080.log`, `SG-080_report.md`, `SG-080_verify.log` written (first token `SG-080`; raw outputs + BOTH fail-then-pass runs).
- Elapsed vs budget (per leg, units): recon+baseline ~3 min / 600 s · G1 ~2 min / 120 s · G2/G3 ~4 min / 120 s · G4 suite/lint ~1 min / 600 s (suite 18 s) · G5 ~1 min / 600 s · overall under 1800 s. No command hit its bound; nothing was killed.
- Spend: **real `$0.000919`** vs `$0.015` bound; `$0` outside G5. Contract echo + source path above.
- `PG-IC-01`: no criterion touched production, the running service, or the network beyond the one G5 leg; tests are local suite only; no container pull/run.

### Question each criterion answers (`PG-SC-09`)

- **G1 — does the live path load v3 with v1/v2 preserved?** Yes: runtime `load_prompt` returns `extract-<cat>-v3` for all three (not a copy), ledger rows carry v3, v1/v2 files byte-identical.
- **G2 — is the transcript evidence (and only evidence)?** Yes: it is a retrievable `text/plain` evidence row linked to the job, and absent from every assertion `value_json`.
- **G3 — is the category a visible, gated proposal with everything else preserved?** Yes: visible through `GET /v1/candidates/{id}.fields.category_proposed`, gated at threshold 0.0, while every other v3 field stays byte-equal in `ai_items` and un-promoted.
- **G4 — does the wired pipeline refuse-before-call and never auto-accept?** Yes: consent and monthly-ledger both refuse with zero invocations; gated fields never auto-accept; request shape asserted.
- **G5 — does v3 survive one real metered call within bound?** Yes: one real 200 with `extract-food-v3`, `$0.000919` ≤ `$0.015`; the second call's HTTP 503 is the provider-side finding.

## Findings

- **F-SG080-1 (G5 provider-side 503).** The real adapter returned HTTP 503 on the second image; quoted raw. Per packet this is a finding, not a slice failure (G4 green). Cost still bounded and reported.
- **F-SG080-2 (unlinked transcript on partial failure — self-caught, fixed).** Detail in G2. The live leg exposed it; the fix is offline and regression-tested; the live leg was not re-run.
- **F-SG080-3 (`category_proposed` promoted to a gated candidate field).** The packet offered "visible now" or "`ai_items`-only, stated". I chose visible+gated (and whitelisted), because the acceptance text requires a named visible read path and the spec §2 calls category "a proposed field". Consequence stated: it becomes a gated assertion at commit (never auto-accepted). If the Architect intended it to ride `ai_items` only this slice, that is the item to correct.
- **F-SG080-4 (`store_text_evidence` sha is an artifact identity).** Reported in G2; a bare content hash is impossible under the global unique `evidence.sha256` without cross-household collisions on generic text.
- **F-SG080-5 (no schema/migration needed).** Transcript evidence reuses the existing `evidence` table and `source_kind`; `PG-SC-11` stated — no migration.

## Vacuity check (loud)

No acceptance criterion passed vacuously. The G1–G3 feature tests genuinely fail with the source stashed (6/11, raw); the freshness pin failed pre-flip and passed post; the reader is read at runtime, not asserted against a copy; the v1/v2 "unchanged" check is a real empty `git diff --stat` over six named files; the transcript negative scans every assertion on a committed asset; the request-shape test reads the real `build_chat_payload`; the G5 leg used committed corpus images and the real adapter (no stand-in). The 2 suite reds reproduce on the clean BASE tree (baseline run before any edit). No grep was scoped so narrowly it could not have matched.

## Receipt note

`RECEIPT_PENDING`

## UNCLEAR

- **FIRST READ:** the packet's G3 gives two acceptable outcomes for `category_proposed` (visible on a read path, OR stated as `ai_items`-only), while the Acceptance line requires "visible on a named read path". I read the stronger one as intended and promoted it to a visible gated candidate field (F-SG080-3), reporting the consequence rather than silently choosing the weaker.
- **DURING EXECUTION:** the live leg is what proved F-SG080-2 (an unlinked transcript row after a partial failure, persisted by the error-ledger commit). I fixed it offline and did not re-run the metered leg (one bounded leg per packet), so the quoted live rows include the pre-fix orphan by design; the fix is covered by an offline regression test.
- **REMAINING:** the v3 enrichment fields (brand/variant/size/barcode/storage/warnings/allergens/nutrition) are preserved in `ai_items` but not promoted to accept-writable fields this slice (explicitly deferred; Task 4/Enrich track). The live flip takes effect only on the next rider deploy (SG-083); the running service still serves the pre-slice v2 build until then.
