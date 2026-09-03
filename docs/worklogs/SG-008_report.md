SG-008 — export manifest, canonical search tests, and restore round-trip report

BASE REF: automation
BASE resolved: 83ac4340bc90125196084ca6772efa3229ca36b8
WORK_HEAD: dfd6e6e1638d05cc1aa84f08e24dde1a49e2c81b
Implementation commit: 0ffb29ee76a1895211b24fabfcb0dcc1338bdb7d
Worklog commit: 7704f7a66e366b9de080e46ae99a69ec3882e3f3
Work dir: /home/andrei/StorageGenie
Remote: git@github.com:Andovol/StorageGenie.git
Model: unknown (the live process arguments exposed no model id and no provider metadata was available)
Reasoning effort: high (the live process arguments exposed `-c model_reasoning_effort=high`)
Timeouts: 120s ordinary commands; 600s test suite; 2100s overall. No command was killed or hung.
Requested header: `contract_sync=refresh version=0.17.2`
Database/restart: none; all new API verification used fresh temporary SQLite engines, temporary storage roots, and TestClient; no production row, storage, service, or restart operation was used.

## Scope and verified differences

The packet’s expected conditions were checked against the tree. `backend/app/api/v1/exports.py` was 54 lines before repair and lacked `manifest_version`, `db_revision`, an attachment disposition, and an explicit transaction. The four filter branches were present in `backend/app/api/v1/assets.py`; they passed the canonical mixed-fixture tests without source repair. The jobs and review-task list endpoints were empty Phase 0 stubs. The repository has no copies of `ARCHITECT.md`, `PACKET.md`, `DISPATCH.md`, `CLOSE.md`, `LEDGER.md`, or `PRODUCTION.md`, as stated in the packet.

The only application source repair is `backend/app/api/v1/exports.py`:

- `manifest_version` is pinned to string `"1"`.
- `db_revision` is pinned to the verified Alembic head `0201cf10c56c`; `cd backend && timeout 120s /home/andrei/StorageGenie/venv/bin/alembic heads` returned `0201cf10c56c (head)`.
- The response sets `Content-Disposition: attachment; filename="storagegenie-export.json"`.
- All export reads are inside one `with db.begin()` session transaction.

The transaction is an explicit SQLAlchemy session boundary using SQLite’s default deferred transaction/read semantics. The code does not request `BEGIN IMMEDIATE`, writer exclusion, or a stronger isolation guarantee; those are not claimed. The pre-existing per-asset assertion query remains because no acceptance test proved its performance behavior broken, and the scope rule limits repair to behavior proved by the committed tests.

No `backend/app/api/v1/assets.py` filter lines or `backend/app/schemas/common.py` lines were changed. No migration, evidence service, frontend, `.env`, secret, or infrastructure file was changed.

## G1 — export manifest and fail-then-pass evidence

Added `backend/tests/test_export.py`. Its isolated fixture creates a fresh SQLite source database and temporary storage root, seeds two evidence rows with real JPEG bytes, two assets, generated assertions, and audit events, then calls `GET /v1/export?household_id=...` through TestClient. It asserts HTTP 200, exact seeded asset IDs, exact seeded evidence IDs, non-empty SHA-256/storage key/positive size for every manifest item, non-empty assertions and audit events, `manifest_version == "1"`, `db_revision == "0201cf10c56c"`, and an attachment Content-Disposition header.

The required new-test-first run was made before application repair:

```text
timeout 120s /home/andrei/StorageGenie/venv/bin/pytest -q backend/tests/test_export.py backend/tests/test_search.py
F...... .. [100%]
1 failed, 8 passed, 1 warning in 1.06s
FAILED test_export.py::test_export_manifest_is_complete_and_downloadable
KeyError: 'manifest_version'
```

This is a real fail against the unmodified export endpoint. The other eight tests passing at this stage is recorded as already-correct behavior, not as evidence that the missing export contract existed.

The first post-repair run exposed a test-harness issue: `2 failed, 7 passed` in `1.49s`, both failing with SQLAlchemy `InvalidRequestError` because the override reused the seeding session after it had autobegun a transaction. No production request path caused this failure. The test-only correction gives each API request a fresh session from the same isolated engine. The corrected targeted run was `9 passed, 1 warning in 1.05s`, exit 0.

## G2 — canonical search coverage

Added `backend/tests/test_search.py` with five mixed fixtures: Kitchen Blender, Garden Chair, Kitchen Table, Office Lamp, and Garage Shelf. The module asserts exact ID sets for `q=Kitchen`, `asset_type=appliance`, and `status=ACTIVE`, with matching and non-matching rows in each set. It also asserts both `has_evidence=true` and `has_evidence=false` exact, non-empty, disjoint ID sets. This intentionally overlaps SG-007’s filter proof as Task 11’s named canonical artifact. All filters passed against the unmodified source, so the result is “already passed, hardened”; no `assets.py` repair was made.

## G3 — restore, stubs, and idempotency

The restore test parses the export JSON and creates a separately opened `restored.db` SQLite database using the same SQLAlchemy models. It inserts the exported asset and evidence IDs into the sink and verifies source-export counts equal sink counts and exact ID sets equal. The source and sink are different database files and sessions; this is not a same-object or same-connection count comparison. File bytes are intentionally out of scope.

The parameterized stub test invokes both `GET /v1/jobs` and `GET /v1/review-tasks`, asserting HTTP 200, `items` and `next_cursor` keys, empty `items`, and `next_cursor is None`. Empty Phase 0 items are asserted only as envelope shape.

The idempotency test posts an asset with `Idempotency-Key`, queries the isolated `idempotency_key` table, parses `response_json`, and verifies the stored ID equals the created asset ID. A second post with the same key returns the same ID and leaves one asset row. The existing second-transaction race window remains: asset creation commits before the idempotency row commit. The `IdempotencyKey` model still has no TTL column. Both are findings only; no redesign or migration was authorized.

## G4 — gates

The baseline full command was bounded at 600s and returned `14 passed, 1 warning in 0.85s`, exit 0. The final commands checked these paths:

```text
timeout 600s /home/andrei/StorageGenie/venv/bin/pytest -q backend/tests/test_export.py backend/tests/test_search.py
9 passed, 1 warning in 1.05s; exit 0

timeout 600s /home/andrei/StorageGenie/venv/bin/pytest -q backend/tests
23 passed, 1 warning in 1.42s; exit 0

timeout 120s /home/andrei/StorageGenie/venv/bin/ruff check backend/app backend/tests
All checks passed!
elapsed_s=0.00 exit=0; violations=0

timeout 120s /home/andrei/StorageGenie/venv/bin/mypy backend/app backend/tests
backend/app/services/evidence_service.py:95: error: Incompatible types in assignment (expression has type "Image", variable has type "ImageFile") [assignment]
Found 1 error in 1 file (checked 46 source files)
elapsed_s=0.22 exit=1; advisory error lines=1; not gated
```

The full suite was non-vacuous: 23 tests were collected and passed, and exit 5 would have been a failure. The one installed FastAPI/Starlette TestClient deprecation warning recommends httpx2; no test was skipped. The mypy error is the pre-existing `evidence_service.py:95` advisory and is outside this slice.

## G5 — outputs, vacuity, and safety

The committed SG-008 outputs are:

- `backend/app/api/v1/exports.py`
- `backend/tests/test_export.py`
- `backend/tests/test_search.py`
- `docs/worklogs/SG-008.log`
- `docs/worklogs/SG-008_report.md` (this report, committed by the receipt commit)

The tests invoke every required endpoint. Export fixtures are non-empty; every manifest set is compared with seeded IDs; search fixtures contain both positive and negative rows; both evidence polarities are checked; the restore sink is separately created; and the stubs’ empty items are not treated as content proof. `git diff --check` passed. Temporary databases and storage roots were under pytest temp paths only. No sudo, docker, SSH, production DB/storage, restart, or secret operation was attempted.

The content-neutral non-fast-forward merge required by G6 imported only the already committed `docs/worklogs/SG-007_report.md` from the evidence history. It did not alter SG-008 source or tests.

## G6 — prefill and publisher artifact

The implementation/worklog candidate was pushed to `origin/automation`, then the existing evidence tip `d43f4c12f17cb3d0deddb627d7fd7757ccc0940d` was found not to be an ancestor. No force push was used. Merging that evidence tip content-neutrally produced the candidate below; the merge added only the prior SG-007 report.

```text
WORK_HEAD=dfd6e6e1638d05cc1aa84f08e24dde1a49e2c81b
git push origin dfd6e6e1638d05cc1aa84f08e24dde1a49e2c81b:refs/heads/storagegenie-evidence -> exit 0
git fetch origin refs/heads/storagegenie-evidence -> exit 0
git rev-parse origin/storagegenie-evidence -> dfd6e6e1638d05cc1aa84f08e24dde1a49e2c81b
prefill equality: verified; candidate == fetched evidence ref
```

The unmodified publisher invocation is:

```text
/opt/storagegenie-dispatch/finalize_dispatch_report.sh SG-008 "contract_sync=refresh version=0.17.2" docs/worklogs/SG-008_report.md dfd6e6e1638d05cc1aa84f08e24dde1a49e2c81b
```

The publisher creates the receipt commit with the `Dispatch-ID: SG-008` trailer and this report as its sole diff. Its return code, receipt hash, trailer, evidence-ref tip, notes proof, and final clean-tree proof are supplied in the final handoff because the receipt hash is created after this report is committed. A zero-exit publisher without that trailer would be treated as a failure.

UNCLEAR — FIRST READ: The repository has no copies of ARCHITECT.md, PACKET.md, DISPATCH.md, CLOSE.md, LEDGER.md, or PRODUCTION.md; the supplied SG-008 packet, AGENTS.md, and STATE.md were the available contract context.
UNCLEAR — DURING EXECUTION: The existing evidence ref was non-fast-forward relative to the candidate, so a content-neutral merge was required; the known mypy advisory and TestClient deprecation warning remain, with no privileged or dependency-install route attempted.
UNCLEAR — REMAINING: Publisher return code, receipt hash/trailer proof, final evidence-ref tip, and final clean-tree proof are pending the unmodified publisher invocation and are reported in the final handoff.
