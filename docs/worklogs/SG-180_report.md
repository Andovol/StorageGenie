SG-180 model=opencode-go/deepseek-v4.1-flash effort=max (read from own process args, PID 1311012: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max` under `bash /usr/local/lib/dispatch/run-coder SG-180`) cwd=/home/andrei/StorageGenie remote=git@github.com:Andovol/StorageGenie.git
BASE requested=`automation`; BASE resolved=`b02e32205cc56be45ad9f5ab304f11f47a8d7ea9` (clean at start, equals `origin/automation`), `b02e322 Audit SG-183 correction; preserve full scenarios and close mandate; packet SG-180`. WORK_HEAD=`4646ff595b86b6ff4cc90f38e079714bdf3d3552` (G1–G3 probes + captures + tests log + worklog + health log; the report commit and the receipt note follow and are not in this line).
Contract: packet expected 0.46.0; ACTUAL SOURCE **0.47.0** (PB-1 difference). `/home/andrei/storagegenie-contract/VERSION`=`0.47.0`; `CODER.md:3` header `Contract version: 0.47.0`; payload `RULES.sha256`=`49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed`; contract checkout `bdbbaa7 Contract payload 0.47.0` is **untagged**. `bash rules_check.sh` (rc=3): `G-L1 UNCHECKED the cache is not checked out at a contract tag`, `G-L5/L7 UNCHECKED gh-unauthenticated`, `G-L6 BYTES codex=2275 opencode=1933`. There is **no runtime contract echo**: `GET /v1/health` returns only `{"status","db","storage"}`, so "actual echo/source" is the contract files above. `PB-7` is defined at 0.47.0 but the packet did not name it; not bound.
Lane: `RUN_BUDGET_S=2100` read from `/etc/dispatch/storagegenie.conf` (file header: WORLD-READABLE — NO SECRETS, EVER). Dispatch/first-command 14:46:36Z (epoch 1791902796); report-state measurement 15:02:08Z (epoch 1791903728) = **932 s elapsed**, inside the 2100 s bound; no timeout/idle kill. Engine deadline exact kill instant is the runner's record, not readable from the lane. Ordinary commands ≤120 s, isolated tests/probes ≤580 s; longest single command: focused pytest 19.6 s; slowest probe ≈60 s.
HEALTH: unchanged, OK (start 14:46:36Z and end 15:00:49Z both `{"status":"ok","db":"ok","storage":"ok"}`, `SG-180_health.log`). Production read-only GET sessions = health only. No restart, no rebuild, no deploy; container/image identity UNVERIFIED (excluded; no read grant; no docker command was run).

## (a) Issues / deviations / surprises

1. **PB-1 contract correction (above):** installed contract is 0.47.0, not the packet's 0.46.0, and the cache is not at a tag. I read the live `CODER.md` in full and echoed its actual header. No rule conflict surfaced in this slice's scope.
2. **PB-1 environment correction:** the root `venv` lacks `pillow_heif`; the complete audit environment is `/home/andrei/StorageGenie/backend/venv` (Pillow 12.3.0, pillow-heif, pytest 9.1.1). F-SG144-1 venv note stands.
3. **Probe-harness bugs fixed before the committed runs** (verification_attempts, not product evidence): G1 record() kwarg collision; G1 misexpected thumb-404 (thumb artifact is independent of the original — corrected control deletes the thumb artifact); G1 mismatch-bytes ordering (retained as the bypass finding F-4); G2 invalid scripted payloads (low confidence needs `uncertainty_reasons`); G2 reused evidence so dedup made the wrong candidate kind; G3 `redact_image` rejects non-image bytes (probe passed literal bytes); G3 `-v4` suffix check. Only the final clean runs are committed; all three logs end `fail: 0`.
4. **Source map confirmed at the resolved tree:** every module the packet names exists; no `providers/gateway.py` and no `app/jobs/pipeline.py` (packet correct). Real writer/reader paths traced: `evidence_service.store_evidence`/`store_text_evidence`; `api/v1/evidence.py`; `signals.extract_observations`; `job_service.run_job/retry_job`; `api/v1/jobs.py`; `candidates.build/commit`, `dedup.deduplicate_job`; `providers.reader.run_ai_extraction`/`_extract_one`/`_write_ledger`/`_recorded_spend`; `opencode_go.OpenCodeGoProvider`; `enrich.client.fetch_off_search`, `enrich.jina.fetch_jina_search`, `snapshots.*`, `synthesize.build_synthesis_input`.
5. **Isolation established before every synthetic write** (A3): each probe ran with cwd=`/tmp/opencode` (so the repo-root `.env` is never loaded by `pydantic-settings`; never copied), `DATABASE_URL`/`STORAGE_ROOT` set to a fresh `mkdtemp` root before `import app`; each probe asserts and prints `settings.database_url`, `settings.storage_root`, `app.db.engine.url` under that temp root, and all storage artifacts under `TEMP_STORAGE` (G1 `storage_tree` PASS). Real route factories reached: `get_db`→`SessionLocal` (temp URL), `storage_path_for`/`thumbnail_path` (temp root), `provider_registry` (fake/scripted only). Production DB/storage were never opened for write.
6. **Zero live-provider calls (A3):** the real adapter was exercised only through `httpx.MockTransport`; reader flows used `ScriptedProvider` through the defined injection seam; Enrich used the documented `http_client` seam; keys are synthetic literals (`sg180-audit-fake-key-not-a-real-secret`); no env value was printed; `OPENCODE_API_KEY`/`JINA_API_KEY` were explicitly absent so the missing-key paths were real.
7. **Optional probes excluded and not replayed:** no docker command, no `--status` verb, no SSH, no privileged operation; no denial was encountered (no STOP condition; earlier SG-183 breach deliberately not replayed).

### Findings (status / severity judgement / root cause / scenario / repair dependency)

- **F-SG180-1 HIGH — cross-household sha dedup returns a foreign Evidence row.** Writer (`evidence_service.py:175-177`) and route (`api/v1/evidence.py:43-47`) look up `Evidence.sha256` globally (column is globally `unique`). Measured: B uploads A's exact bytes → 201 with **A's evidence id**; B's `GET /v1/evidence/{id}` → 403; B's own distinct bytes → own row (counter-control). Root cause: evidence identity is global, not household-scoped. Scenario CX-01/CX-02/CX-05, SC-02/SC-06. Repair dependency: household-scoped evidence identity or an ownership check + conflict answer; canonical register update is the Architect's.
- **F-SG180-2 HIGH — cross-household `Idempotency-Key` replay.** `api/v1/evidence.py:26-38` replays by key alone; no household check. Measured: A key K with bytes X → id X; B key K with **different** bytes Y → 201 returning **A's id**. Fresh key → own row (counter-control). Scenario CX-01. Same repair family as F-SG180-1 (key namespace/ownership).
- **F-SG180-3 MEDIUM — same-size content corruption is served undetected.** Read path trusts the DB row (`api/v1/evidence.py:101-104`, `local_store.absolute_path`): after flipping one byte in the stored original (same size), `GET /file` → 200 with `sha256=…b605…` ≠ DB `…6682…`; a names/sizes tree fingerprint cannot see this. Working counter-controls: delete original → `/file` 404; delete thumb artifact → 404; missing original in a job → `quarantined: original missing…` FAILED, restore + retry recovers. Scenario CX-05/SC-06. Repair dependency: read-time integrity check or store-side manifest (disposable-storage design decision).
- **F-SG180-4 MEDIUM-LOW — media-type validation bypassed on sha replay.** `store_evidence` runs `_detect_media_type` only for new bytes; the route's sha short-circuit returns 201 for known bytes regardless of the claimed media type (measured: JPEG bytes claimed `image/png` → 201 after the same bytes were stored once; fresh bytes with the wrong claim → 422 `media_type_mismatch`). Scenario SC-02/CX-05. Mitigated by content addressing; fix with F-SG180-1 family.
- **F-SG180-5 MEDIUM-LOW — vision empty-200 writes no accounting.** `guard_content` raises on blank content; `extract_text` attaches received usage/cost (SG-101) but `extract_items` does not (measured: vision empty-200 `cost=None` attached; text empty-200 `cost=4.5e-05`; zero-usage and no-choices paths attach on both). A billed empty vision 200 can land a 0.0 ledger row. Scenario SC-10/CX-04. Repair dependency: mirror SG-101 on `extract_items`.
- **F-SG180-6 MEDIUM — `POST /imports/{id}/run` is synchronous end-to-end.** Measured with a controlled 0.6 s provider latency: response after **0.636 s**, already `AWAITING_REVIEW`; source has no background/queue mechanism (`run_job` loop in-request). Large imports hold the request open (timeouts). Classified as current architecture fact, not a regression; background runner is a scope decision.
- **F-SG180-7 MEDIUM (existing family REC-ISS02/REC-ST03) — CREATED job has no Run control.** Reconfirmed real surface: only `AssetImportModal.tsx:140` calls `/run`; Inbox retry only for `FAILED` (`InboxPage.tsx:37`); `JobCard` select-only; help text (`AssetImportModal.tsx:252`) promises "waits in the Inbox until you run it there". UI/API disconnected transition; repair scope already recorded (no product repair here).
- **F-SG180-8 LOW-MED — cancellation absent by trace, not by one grep.** UI: no cancel/abort for jobs (only modal dismissal); API: `POST /imports/{id}/cancel` → 405 (SPA GET fallback owns the path); service: `CANCELLED` is only a terminal guard (`job_service.py:164`), no writer. Classification: absent capability (intent undocumented); scope decision owed.
- **F-SG180-9 LOW — error/order hygiene on rejection.** Upload against a nonexistent household writes the original file **before** the row flush (FK error) leaving an orphaned file, and the 422 detail carries the raw `IntegrityError` + SQL parameters; a truncated JPEG surfaces raw `Truncated File Read` through the catch-all (`evidence.py:56-58`). Scenario SC-02 negative path; cleanup + error-surface scope.
- **F-SG180-10 LOW — whole body buffered before the size cap.** `evidence.py:41` reads the full upload, then `store_evidence:170-173` enforces 20 MiB (measured 413 for 20 MiB+1). Cap semantics preserved; memory bound is the residual.
- **F-SG180-11 LOW/OBSERVE — same key + changed payload silently returns the original job** (no request fingerprint; `jobs.py:39-44`). Same-household key replay returns the same job (PASS), foreign household 403 (PASS). CX-01.
- **F-SG180-12 OBSERVE (intentional privacy boundary) — EXIF/GPS.** Original retains GPS/orientation and is served to its owning household; thumbnails are re-encoded JPEG with no EXIF; the AI egress is a re-encoded PNG, ledger `input_hashes` is the sha of the **redacted** bytes, original sha unchanged. Boundary is provider egress; no repair.
- **F-SG180-13 ENV — OCR/barcode unavailable on the audit venv.** 2 of 252 focused tests failed deterministically: no `libzbar` (`ldconfig -p` empty) and no `tesseract` binary (`which` empty) while the Python packages import; `signals` degrades loudly (warning, no observations). `Dockerfile:19` installs `tesseract-ocr libzbar0`; deployed container capability **UNVERIFIED** (container excluded). Destination: SG-182.
- **F-SG180-14 OBSERVE — UI/backend input surface mismatch.** Import modal accepts png/jpg/webp only; backend accepts jpeg/png/webp/tiff/heic/heif/pdf; `AssetForm` `accept="image/*,.pdf"` + `capture="environment"`; AssetImportModal/AssetDetail have no camera; no client-side byte-size checks; modal note says DQ9 25 MB vs the enforced 20 MiB. SC-02.
- **Confirmed invariants (no defect):** create-only vs run (8 PENDING steps → 6 COMPLETED/1 AWAITING_REVIEW/1 PENDING); rerun creates no duplicate candidate/observations; duplicate import after first commit → `duplicate_of_asset` → `duplicate_linked`, one asset; controlled step failure → job FAILED with step attempts=1 and prior steps COMPLETED; engine reopen preserves FAILED; retry resumes attempts=2; malformed extraction → 2 committed error ledger rows **retaining the raw payload** (`schema_validation: …`) then retry builds the candidate with provenance; commit failure rolls back (no asset, no link) and retry creates exactly once; missing original quarantines then recovers; multi-item task gates accept (409) and completes after the real resolve route (200); single-repair policy exact (2 supplies, `## Repair`, non-retryable 1 supply); router pre-call budget refusal with zero invocations and retryable-only fallback; consent off → `consent_disabled` zero invocations; missing real adapter key → `provider_not_configured`; monthly cap refuses before any call (0 invocations, 0 ledger rows); durable spend = job-linked + unattributed pool (fail-closed; 0.0 → 0.35 → 0.3505 with a Jina ledger row); OFF/Jina identifiers-only wire shapes, loud degradations, verbatim snapshots, synthesis input source attribution.

## (b) Actions

- Commits (trailer `Dispatch-ID: SG-180`): `4646ff5` (all probes, raw captures, tests log, worklog, health log), then the report commit. Push `automation` + notes read-back named in the receipt lines (published after this report; not claimable here).
- Changed paths (write ceiling respected; `git status` shows nothing outside `docs/worklogs/SG-180*`): `SG-180_probe_g1.py`, `SG-180_probe_g2.py`, `SG-180_probe_g3.py`, `SG-180_g1_run_2026-10-13.log`, `SG-180_g2_run_2026-10-13.log`, `SG-180_g3_run_2026-10-13.log`, `SG-180_tests_run_2026-10-13.log`, `SG-180_health.log`, `SG-180_worklog.log`, this report. No product/config/test/lockfile/schema/migration/dependency file touched; no temporary helper left elsewhere (probes are the committed audit evidence).
- External/production effects: zero network sends (all HTTP through `httpx.MockTransport` or in-process scripted providers), zero paid calls, zero production writes, production GETs = health only, no evidence-store change, no credential/profile access, no restart/rebuild/migration/privilege change, no docker. UNKNOWN: none.
- Verification attempts: probes re-run only after material harness fixes (G1×3, G2×3, G3×3 committed finals); no re-dispatch consumed; test-command count: 4 (3 probes + 1 focused pytest invocation).
- Durations (box clock UTC, `date -u`): first command 14:46:36Z; G1 14:49; G2 14:52; G3 14:57; focused tests 14:59–15:00 (19.6 s); report-state 15:02:08Z = **932 s**; receipt publish is the runner's record. Highest-impact action: the scripted-transport G3 probe + the household-scope matrix in G1, which turned "looks scoped" into measured cross-household replay evidence.

## (c) Verification (raw outputs committed; blocks are observed output)

Isolation (all probes; G1 block):
```
temp_root: /tmp/sg180-g1-…  settings_database_url: sqlite:////tmp/sg180-g1-…/storagegenie.db
settings_storage_root: /tmp/sg180-g1-…/storage  engine_url: sqlite:////tmp/sg180-g1-…/storagegenie.db  cwd: /tmp/opencode
```
G1 (`SG-180_g1_run_2026-10-13.log`, 29 checks: 22 PASS / 0 FAIL / 3 DEFECT_OBSERVED / 4 OBSERVE):
```
upload_jpeg_201 PASS 201 (stored_bytes_identical, size 677); upload_pdf_201 PASS
mismatch_declared_detected_422 PASS 422 media_type_mismatch: claimed 'image/png', detected 'image/jpeg'
unsupported_signature_422 PASS 422; oversize_413 PASS 413 max_upload_bytes … 20971521 > 20971520
truncated_jpeg_422 PASS 422 "Truncated File Read"; image_bomb_422 PASS 422 Pillow max_image_pixels (20000x20000)
mismatch_claim_bypassed_on_known_bytes DEFECT_OBSERVED 201 (sha short-circuit)
cross_household_sha_dedup OBSERVE b_upload_status=201 returned_id=A's id, returned_row_household=A, b_get_status=403
cross_household_key_replay DEFECT_OBSERVED OBSERVE b_returned_a_row=true (B sent DIFFERENT bytes)
same_size_corruption_served DEFECT_OBSERVED 200 served_sha256=b605… db_sha256=6682…
counter_control_missing_thumb_404 PASS; foreign_evidence_read_403 PASS
upload_unknown_household_orphan_file DEFECT_OBSERVED 422 + new file under bogus-household path + raw IntegrityError detail
original_retains_gps_thumbnail_strips OBSERVE gps_tag_present=true orientation=6 thumb_exif_keys=[]
```
G2 (`SG-180_g2_run_2026-10-13.log`, 26 checks: 21 PASS / 0 FAIL / 5 OBSERVE):
```
create_only_created_pending PASS CREATED 8 steps all PENDING attempts=0
run_reaches_awaiting_review PASS progress {"completed":6,"total":8,"failed":0,"pending":1}
rerun_no_duplicate_work PASS candidate_count=1 obs 1→1 all attempts<=1
controlled_failure_state PASS FAILED EXTRACTING=(FAILED,1)
reopen_persists_failed_state PASS FAILED; retry_after_reopen_resumes PASS AWAITING_REVIEW attempts EXTRACTING=2
malformed_extraction_fails_job PASS invocations=2 ledger=[{"error_state":"schema_validation: payload failed schema validation after the single repair","cost":0.0}×2]
retry_with_valid_output_builds_candidate PASS proposal_calls==success_calls extract-food-v4
commit_failure_rolls_back PASS assets 1→1 links=1; commit_retry_creates_once PASS COMPLETED assets=2
missing_original_fails_with_quarantine PASS errors=["quarantined: original missing at storage key …"]
multi_item_task_gates_accept PASS blocked 409 → resolve → 200 COMPLETED
run_blocks_full_pipeline PASS elapsed_s=0.636 invocations=1 state_in_response=AWAITING_REVIEW
duplicate_import_no_second_asset PASS kind=duplicate_of_asset decision=duplicate_linked assets=1
key_replay_changed_payload_ignored OBSERVE returned==original (evidence_ids changed)
cancel_route_absent OBSERVE 405; empty_import_flow OBSERVE candidate "Imported item"
```
G3 (`SG-180_g3_run_2026-10-13.log`, 51 checks: 48 PASS / 0 FAIL / 3 OBSERVE; wire captured through real `OpenCodeGoProvider._post` + MockTransport):
```
wire_request_line PASS POST https://opencode.ai/zen/go/v1/chat/completions
wire_payload_envelope PASS model=deepseek-v4-flash-vision-exp stream=false max_tokens=2000 response_format={"type":"json_object"} content=["text","image_url"]
wire_image_is_redacted_png_upright PASS sent_size=[48,64] sent_exif={} original_sha_unchanged=true
wire_result_and_cost PASS cost=4.5e-05 == compute_cost
validation zero_usage/empty/no_choices/non_json/non_object/http_500/transport all PASS mapped kinds; zero_usage attached_usage={}, no_choices attached usage
empty_200_accounting_vision_vs_text OBSERVE vision_cost_attached=null text_cost_attached=4.5e-05
repair_once_then_valid PASS supplies=2; repair_twice_fails PASS supplies=2; reader_repair_prompt_and_ledger PASS "## Repair"
router_budget_refuses_before_call PASS calls={primary:0,fallback:0}; fallback only on retryable
consent_off_skips_before_provider PASS invocations=0 consent_disabled; provider_not_configured_skips PASS
reader_sends_redacted_png_real_prompt PASS sent_png=true exif={} prompt_is_real=true version=extract-food-v4
ledger_input_hash_is_redacted_sha PASS == sha256(sent); candidate_provenance_threaded PASS; assertion_model_json_has_provider_lineage PASS
monthly_cap_refuses_before_provider PASS invocations=0 ledger_rows=0
durable_spend_reader_sums_job_and_unattributed PASS 0.0 → 0.35 → 0.3505 (jina 0.0005)
off_request_shape/jina_request_identifiers_only/off+jina degradations/snapshot persistence/synthesis attribution PASS
```
Focused tests (`SG-180_tests_run_2026-10-13.log`; derived from the defining modules: evidence_upload, signals, import_jobs, extraction_contract, ai_pipeline, provider_gateway/conformance, opencode_go, privacy_audit, sg080, dedup, sg081/82/98/101/102/103, sg125/132/142, candidates, candidate_read, review_split, sg127): `2 failed, 250 passed in 19.55s`. Both failures are the F-SG180-13 native-tool absence (`test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`, `test_signals.py::test_ocr_has_text_boxes_and_mean_confidence`); root cause measured (`ldconfig -p` no zbar, `which tesseract` empty, packages import). Exclusion: no full suite, no frontend test execution (UI own by SG-179/183), no E2E phases.
Health: `SG-180_health.log` — start/end `{"status":"ok","db":"ok","storage":"ok"}`, unchanged.

## UNCLEAR

- FIRST READ: contract version mismatch (packet 0.46.0 vs source 0.47.0, cache untagged) — used the live contract as authority; no runtime echo exists to cross-check.
- DURING EXECUTION: `run_blocks_full_pipeline` semantics measured only with a controlled 0.6 s scripted latency; the exact engine kill deadline is not readable from inside the lane (budget 2100 s is).
- REMAINING: canonical register update by Architect only; repairs for F-1/2/4 (household-scoped evidence identity + idempotency), F-3 (read-time integrity), F-5 (vision accounting), F-6 (background run decision), F-7 (Inbox run control, existing scope), F-8 (cancel decision), F-9/10 (orphan/error surface) each need their own scope word; SG-182 owns OCR/barcode deployed proof and operations; SG-181 owns SC-12 per-field/enrich domain acceptance; live-provider quality/availability, production evidence-volume bytes, WAL/volume state and container/image identity remain UNVERIFIED.
