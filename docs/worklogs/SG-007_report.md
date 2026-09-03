SG-007 — Asset CRUD verification and assertion provenance report

BASE REF: automation
BASE resolved: 89dbf72f6d31bfc67e7de21ec1bfa376a84451ef
WORK_HEAD: 625df6ace439f6aec606e07063ca1e267fbd4e61
Work dir: /home/andrei/StorageGenie
Remote: git@github.com:Andovol/StorageGenie.git
Model: unknown (the live process arguments exposed no model id; no provider metadata was available)
Reasoning effort: high (live process argument `-c model_reasoning_effort=high`)
Timeouts: 120s ordinary commands; 600s full suite; 2100s overall. No command was killed for exceeding a timeout.
Database: none; all asset/assertion verification used temporary SQLite and temporary storage under `/tmp/storagegenie-*-tests-*`.
Restart: none.

## Scope and verified differences

The packet’s referenced ARCHITECT.md, PACKET.md, DISPATCH.md, CLOSE.md, LEDGER.md, and PRODUCTION.md files were not present in the repository or the advertised local contract locations. This report therefore follows the supplied SG-007 packet, AGENTS.md, and STATE.md. The packet’s expected asset API path and the actual tree path matched. No application source repair was justified: all exercised asset and assertion behavior passed after test-only corrections.

Changed and committed paths are exactly:

- `backend/tests/test_assets_crud.py`
- `backend/tests/test_assertions.py`
- `docs/worklogs/SG-007.log`
- `docs/worklogs/SG-007_report.md` (this receipt commit)

No migration, evidence-service, export/search/UI, expiry, LLM/OCR, `.env`, secret, restart, production database, or production storage change was made.

## G1 — manual CRUD, idempotency, scoping, and archive

`test_manual_create_idempotency_detail_scoping_and_archive` uses `TestClient` with temporary SQLite/storage fixtures. It creates a manual asset with all writable fields and one valid evidence id, and observed:

- HTTP 201;
- detail evidence containing the linked evidence item;
- exactly one accepted assertion for each supplied writable field (`display_name`, `asset_type`, `status`, `quantity`, `unit`, `condition`);
- exactly one `asset.create` audit row;
- the same `Idempotency-Key` returned the same asset id, while the household had exactly one asset row;
- unknown asset detail returned 404;
- cross-household detail, PATCH, DELETE, and evidence attach each returned 403;
- repeated attach of the already-linked evidence remained successful and produced one linked evidence item;
- archive returned success, detail showed `ARCHIVED`, version changed from 1 to 2, and one `asset.archive` audit row existed.

The create path’s `Asset` model default `version=1` was confirmed by the test. The inspected `(version or 1) + 1` update/archive expressions did not require repair. The idempotency record is committed in a second transaction after asset creation; this remains a single-writer SQLite race window and was reported, not redesigned.

## G2 — cursor pagination and non-vacuous filters

`test_asset_cursor_pagination_and_mixed_filters` creates five assets with `limit=2`, so the pagination leg necessarily exercises three non-empty pages. The union of page ids exactly equals the five created ids, with no duplicate, gap, or empty-page pass. The cursor round trip therefore exercised the `strftime` microsecond workaround end to end.

Each filter fixture contains matching and non-matching rows, and each result was asserted against an exact expected id set:

- `q=Kitchen`: 2 of 5;
- `asset_type=appliance`: 2 of 5;
- `status=ACTIVE`: 3 of 5;
- `has_evidence=true`: 2 of 5;
- `has_evidence=false`: the remaining 3 of 5.

No pagination or filter repair was needed.

## G3 — assertion provenance and post-creation attach

`test_patch_supersedes_assertion_stale_match_and_attaches_evidence` observed a PATCH of `display_name` with `If-Match: 1`, version 1 to 2, the old assertion as `superseded`, and a new accepted assertion carrying the new value. Both assertions were visible in detail, and the corresponding `assertion.upsert` audit row was present.

A stale `If-Match: 1` after version 2 returned 409. A subsequent detail comparison showed unchanged version, display name, assertions, and provenance state. Post-creation evidence attach returned 200; unknown evidence returned 404; cross-household evidence returned 403.

The broad exception handler in `asset_service.attach_evidence` was inspected. The exercised duplicate-link behavior was already harmless under SQLite, so no repair was made; no test-proven failure justified changing that code within the slice.

## G4 — gates and fail-then-pass evidence

The system PATH did not expose pytest, so the initial command `pytest ...` returned 127 in 0.00s. The checked-in `/home/andrei/StorageGenie/venv/bin` tools were used for actual gates.

The first focused run found only test defects: 2 passed and 1 failed in 0.70s; one assertion selected the old assertion from the update response. A second bounded run found the expected assertion count in the test was 3 while the schema payload also serialized the default ACTIVE status assertion, yielding 2 passed and 1 failed. The tests were corrected; no product source was changed. The initial full run then showed 12 passed and 2 existing evidence-test failures because eager app import from the new modules redirected the singleton settings storage root. The new modules were changed to lazy-load app/database/service imports; this restored test isolation without touching evidence code.

Final gates:

- Command: `timeout 600s ... ./venv/bin/pytest -q backend/tests`; exit 0, elapsed 1.12s; `14 passed, 1 warning in 0.77s`; 14 collected, no skips, no exit-5 vacuity.
- Command: `timeout 120s ... ./venv/bin/ruff check backend/app backend/tests`; exit 0, elapsed 0.01s; output quoted: `All checks passed!`; match count 0.
- Command: `timeout 120s ... ./venv/bin/mypy backend/app backend/tests`; advisory exit 1, elapsed 5.61s; count 1: `backend/app/services/evidence_service.py:95: error: Incompatible types in assignment (expression has type "Image", variable has type "ImageFile") [assignment]`. Mypy was advisory and this pre-existing evidence-path issue was not repaired.

The sole pytest warning is the installed FastAPI/Starlette TestClient deprecation warning recommending `httpx2`; it is not a skipped test or suppressed gate.

## Safety, outputs, and worktree

Every database/storage fixture was under `/tmp`; no production row identifiers exist because no production datastore was opened. No privileged, SSH, Docker, service, or secret operation was attempted. `git diff --check` passed before the work commit. The work commit `c5a2555ee41ac36fadf76a4a0672ba0453c9b2e5` contained the two test modules and log. The content-neutral merge `625df6ace439f6aec606e07063ca1e267fbd4e61` also carried the prior SG-006 report required to reconcile the evidence ref divergence; it did not alter SG-007 product content.

## G6 — evidence ref and receipt

The first mandated prefill of `c5a2555ee41ac36fadf76a4a0672ba0453c9b2e5` returned non-fast-forward in 1.44s; no force push was used. The fetched divergence had merge base `2d70e2872f6174f08e4451bef2df27fc6e9652d1`. A content-neutral merge produced `625df6ace439f6aec606e07063ca1e267fbd4e61`, which was pushed to `automation` in 1.73s.

The required prefill then succeeded in 1.75s:

`PREFILL_CANDIDATE=625df6ace439f6aec606e07063ca1e267fbd4e61`

`PREFILL_REMOTE=625df6ace439f6aec606e07063ca1e267fbd4e61`

Equality passed after a 1.29s fetch. The unmodified publisher command is:

`timeout 120s /opt/storagegenie-dispatch/finalize_dispatch_report.sh SG-007 "contract_sync=refresh version=0.17.2" docs/worklogs/SG-007_report.md 625df6ace439f6aec606e07063ca1e267fbd4e61`

The publisher is expected to commit this report with trailer `Dispatch-ID: SG-007`; the resulting receipt hash, evidence-ref head, notes proof, and clean-tree result are recorded in the final handoff after invocation.

UNCLEAR — FIRST READ: The repository lacks the named ARCHITECT/PACKET/DISPATCH/CLOSE/LEDGER/PRODUCTION contract files; the supplied packet plus AGENTS.md and STATE.md were used. The packet’s cited local_store path was not applicable to this slice.
UNCLEAR — DURING EXECUTION: System PATH omitted pytest/ruff/mypy, so the project venv was required. The first evidence prefill was non-fast-forward and was resolved by a content-neutral merge; no privileged operation, SSH check, restart, or production write was attempted.
UNCLEAR — REMAINING: The unmodified receipt publisher invocation and final evidence-ref trailer proof are the only remaining SG-007 actions; no asset/assertion implementation work remains.
