SG-020 — Phase 1 exit E2E + runbook + close-out

Status: LANDED; final receipt note is the last repository action.

BASE requested ref: automation

BASE resolved: 529643d986a4a3d3c8603ab40e713d0d7b346b0a

WORK_HEAD (implementation/report content commit): to be filled after the implementation/report commit.

Work dir: /home/andrei/StorageGenie

Origin: git@github.com:Andovol/StorageGenie.git

Coder: codex

Model: unknown — no model ID appeared in readable process arguments; the CLI default model ID was omitted by policy.

Reasoning effort: high — proven from readable process arguments containing -c model_reasoning_effort=high.

Autonomy: L3, Phase 1 exit re-run under D11.

Elapsed: approximately 30 seconds observed command wall time / 2100 seconds (35 minutes) overall budget; no command was killed.

## Fail-first and findings

At BASE 529643d, after installing the already-declared dev dependency qrcode==8.2 into the ignored local venv, the bounded command
timeout 600s bash -lc 'cd backend && venv/bin/python -m pytest -q'
returned 65 collected, 62 passed, 3 failed. The failures were the stale candidate migration assertion and exactly:
backend/tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier
backend/tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence
The initial environment-only collection result was ModuleNotFoundError: No module named qrcode; no dependency manifest changed.

The stale test failed at test_candidates.py:164 because downgrade -1 removed only the SG-017 FTS revision and left candidate. The test-only repair at backend/tests/test_candidates.py:163-166 explicitly downgrades to 20260908_sg013_observation, proves candidate absent, then upgrades to head and proves it returns.

## G1 — exit E2E

backend/tests/test_phase1_e2e.py::test_phase1_exit_condition uses one temp SQLite database, temp storage, and a non-empty temp mixed-folder containing five imported files: EXIF JPEG, QR PNG, EAN-13 PNG, plain PNG, and classic TIFF. Every imported evidence ID comes from a real POST /v1/evidence response. A separate pre-existing anchor asset/evidence is also uploaded through the route so the single import job can exercise similar and identifier-collision behavior; the job itself contains exactly the five imported IDs. TIFF availability is grounded in backend/app/services/evidence_service.py:66-67, not the config list.

The bounded focused command was timeout 600s bash -lc 'cd backend && venv/bin/python -m pytest -q tests/test_phase1_e2e.py -s'. It returned 1 passed, 2 warnings and printed:
SG-020 E2E job_id=01a080f8-e67e-7f70-bb9f-c4cc733e32aa candidate_id=01a080f8-e6e0-7bb3-8cd8-4895aec5f350 asset_id=01a080f8-e702-7850-b1e8-d77cef78bf30 anchor_asset_id=01a080f8-e63c-7893-8d29-4dc98bccf08e evidence_ids=['01a080f8-e65c-7423-9c7f-b600a7a8b3df', '01a080f8-e666-7d03-89b6-a2534d10d5d3', '01a080f8-e66b-7a40-a27b-320f9ecb57c1', '01a080f8-e670-7651-8c3f-682beda8f6b8', '01a080f8-e674-73f2-a1a9-04198891afe3'] similar_anchor=01a080f8-e63c-7893-8d29-4dc98bccf08e collision_409=409 retry=AWAITING_REVIEW decoder_status={'qr': 'degraded', 'ean': 'present'} uv5_seconds=0.132902

Evidence pointers: create and six-step assertion are test_phase1_e2e.py:161-190; injected NORMALIZING failure, FAILED state, unchanged catalog, and one retry are :196-231; phash/EXIF rows and decoder present-or-degraded handling are :233-257; created candidate read-back, similar anchor, open collision task, and decision 409 are :263-295; accept and detail prove new asset, five evidence links, assertions, and asset.create/asset.accepted/asset.lifecycle.created audit rows at :297-315; classification needs_evidence and manual user-sourced accepted expiry resolve are :317-346; FTS identity and export IDs are :348-359; job.create to asset.accepted ordered non-negative UV-5 computation is :361-379.

The E2E is not vacuous: five upload responses feed the one job, the failure and 409 branches execute, the retry changes durable state, and persisted rows are queried after the transitions. Decoder status is explicitly QR degraded and EAN present; the test imports neither pyzbar nor pytesseract.

## G2 — suite and static gates

The bounded final command timeout 600s bash -lc 'cd backend && venv/bin/python -m pytest -q' returned 66 collected, 64 passed, 2 failed. The only failures were:
backend/tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier
backend/tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence
These are the named ISS-1 decoder legs carried to the manual compose pass. No other red remained.

Repository-wide downgrade output was:
backend/tests/test_candidates.py:163 command.downgrade(config, "20260908_sg013_observation")
backend/tests/test_signals.py:229 command.downgrade(config, "20260908_sg013_observation")
backend/tests/test_search.py:247 command.downgrade(config, "-1")
The first two are explicit. The remaining -1 is intentional in the FTS-only migration test: it removes the latest SG-017 FTS objects and upgrades head again. It is not the stale candidate assumption; changing it exceeds the packet's candidate-only repair ceiling.

Ruff command bound 120s: timeout 120s bash -lc 'cd backend && venv/bin/ruff check app tests' returned All checks passed!
Mypy command bound 120s: timeout 120s bash -lc 'cd backend && venv/bin/python -m mypy app' returned 40 errors in 9 files (checked 51 source files). Mypy remains advisory and no out-of-ceiling product fix was attempted.
make check-postgres-dialect ran from the root under a 120s bound and returned 1 passed; target source is Makefile:18-19.
Frontend suites are WAIVED: SG-016 proved them green, this slice has no frontend-file ceiling, and no frontend file changed.

## G3 — runbook verification

README.md:93-180 is the Phase 1-only addition. Route checks match the tree: evidence upload backend/app/api/v1/evidence.py:18; import create/run/retry/detail jobs.py:32,78,88,98; candidate decision/read candidates.py:21,72; review queue/resolve review_tasks.py:16,71; plugin classify/manual expiry/extensions plugins.py:62,112,156,179; asset search/detail assets.py:119,192; export exports.py:32. The README curl shapes include household_id, JSON or multipart bodies, and Idempotency-Key.

The FTS reference backend/app/services/fts.py:87-91 matches rebuild_asset_fts and its direct cd backend; venv/bin/python maintenance shape. The data-location references match docker-compose.yml:8-14,43 and backend/app/config.py:4-6. The trust boundary remains LAN-only, single household, and no auth. The verification map states E2E coverage, service-tolerant decoder assertions, ISS-1 manual compose carry, and no browser automation honestly.

## G4 — Phase 2 door ledger

ADR-004 provider abstraction, ADR-007 privacy/external-AI, and ADR-010 guardrail tracking are explicitly unwritten here; the tree inventory contains ADR-001/002/003/005/006/008/009 only. Phase 2 owns provider keys, costs, and household-data-egress decisions; each fires G-K1/G-K2 at every autonomy level and cannot be pre-approved. The deferred manual compose pass owns ISS-1 re-proof in an image with libzbar and tesseract, image build, compose-up, UI verification, and restart verification. No code, ADR, provider research, compose operation, restart, or AI/LLM work was added.

## G5/G6 — artifacts and receipt

Committed output paths are backend/tests/test_phase1_e2e.py, backend/tests/test_candidates.py (one migration assertion only), README.md (Phase 1 section only), docs/worklogs/SG-020.log, and docs/worklogs/SG-020_report.md. The packet docs/packets/SG-020-phase1-exit-rerun.md was not modified. No legacy receipt publisher and no storagegenie-evidence push are used; automation is the only code ref.

The final metadata commit is the receipt target. The notes ref refs/notes/storagegenie-coder-reports will carry a first line containing both Dispatch-ID: SG-020 and Report: docs/worklogs/SG-020_report.md, with no commit after the note. The remote notes ref will be fetched and quoted; completion requires the dispatch result to report note=yes.

No criterion passed vacuously: the fixture is non-empty, all branches invoke real routes, the full suite collected 66 tests, the downgrade grep was broad, Ruff emitted a positive result, and mypy emitted its advisory count.

UNCLEAR — FIRST READ: The packet's referenced ARCHITECT.md, PACKET.md, DISPATCH.md, PRODUCTION.md, CLOSE.md, LEDGER.md, and RATIONALE.md files were absent from the checkout; the committed packet plus AGENTS.md and STATE.md were used.
UNCLEAR — DURING EXECUTION: The two named ISS-1 decoder nodes remained red because the confined venv lacks usable libzbar and tesseract; the full backend gate otherwise returned 64 passed, and mypy retained 40 advisory errors. No privileged workaround was attempted.
UNCLEAR — REMAINING: The manual compose pass owns ISS-1 decoder re-proof plus image/compose/UI/restart verification; Phase 2 owns ADR-004/007/010 and provider, cost, and household-egress decisions. The intentional FTS test -1 downgrade remains outside this slice's permitted repair.
