SG-014 | Deduplication, candidates, review decisions, lifecycle events

BASE ref requested: automation
BASE resolved: 0428f9ac7025d8721346d1068b87f088735a38ba
WORK_HEAD: pending until the final commit is created
Work dir: /home/andrei/StorageGenie
Origin: git@github.com:Andovol/StorageGenie.git
Coder: codex
Model: unknown (the CLI process omitted the model id and uses its default)
Reasoning effort: high (verified from process arguments: `codex exec --sandbox danger-full-access -c model_reasoning_effort=high -C /home/andrei/StorageGenie`)
Autonomy: L3, Phase 1 slice 3 of 7
Elapsed: within the 2100 s overall bound; final process elapsed is recorded at close-out.

Implemented

- `backend/app/services/dedup.py` consumes hand-inserted or SG-013 observations. Exact asset-linked evidence proposes the existing asset id; dHash distance uses `settings.dhash_near_threshold` and remains advisory; validated barcode collisions create blocking review tasks. The module has no UPDATE or merge path.
- `backend/app/services/candidates.py` owns the single Candidate model/service used by the one authorized migration. Accepted/edit candidates create deterministic assertions, source-evidence links, and `asset.lifecycle.created` in one transaction. Identifier and expiry assertions are `proposed`; machine-safe fields are `accepted`.
- `backend/app/services/job_service.py` now executes DEDUPLICATING and COMMITTING. A failed COMMITTING transaction rolls back asset, assertion, evidence-link, and audit rows; the accepted candidate/job remains retryable and retry completes it.
- `backend/app/api/v1/review_tasks.py` returns real cursor-envelope items, keeps `/review_tasks`, and resolves tasks with an audit row.
- `backend/app/api/v1/candidates.py` provides accept/edit/hold/reject with household checks and unresolved-task blocking.
- `backend/app/api/v1/assets.py` provides the single lifecycle event route; events are `asset.lifecycle.<type>` audit rows visible through asset detail.
- `backend/alembic/versions/20260908_sg014_candidate.py` is the only new migration. Temp SQLite proof passed upgrade head, downgrade -1, upgrade head.
- `docs/adr/ADR-006-duplicate-policy.md` records exact/perceptual/identifier/semantic policy, merge-never behavior, and `identifier` convention with file/line traces. ADR-003 lines 41 and 51 now name `20260908_sg013_observation`.

Acceptance evidence

- Exact duplicate: test asserts the candidate proposal’s `asset_id` equals the existing asset and the household asset count remains one.
- Near/far: test asserts a threshold-distance `similar` proposal, accepts it independently into a second asset, and asserts no similar match for the far hash.
- Identifier collision: test asserts a real task through both review routes, proves accept returns 409 while open, resolves it, proves the audit row, and then commits.
- Atomic commit: test proves database rows for asset, assertions, `asset_evidence`, and lifecycle audit. A forced exception after asset construction leaves all four row categories empty; `/retry` completes the job.
- Household boundaries: candidate decision, review resolution, and lifecycle event cross-household calls return 403.
- Non-vacuous queue gate: the permitted old empty-list assertion was weakened to an empty-envelope shape assertion in `backend/tests/test_export.py`; the new non-empty task listing is asserted in `backend/tests/test_dedup.py`.

Verification

- SG-014 tests: 7 passed, 5 warnings, under the 600 s bound.
- Eligible backend suite: 30 passed, 3 explicitly deselected, 5 warnings, under the 600 s bound. It included SG-012 job tests, export tests, and non-decoder SG-013 tests.
- `backend/tests/test_evidence_upload.py`: 8 passed independently under 600 s. The unfiltered suite still exposes five global settings/storage-root coupling failures; this slice did not alter that out-of-ceiling test.
- Ruff: clean under 120 s. `git diff --check`: clean.
- Mypy: advisory only, 40 errors in 9 files; no SG-014 service error remained.
- Full unfiltered backend result: 33 passed, 8 failed. The two decoder node ids and one stale SG-013 migration node are named in `docs/worklogs/SG-014.log`; no failure was treated as a pass.

Output paths: `backend/app/services/dedup.py`, `backend/app/services/candidates.py`, `backend/app/services/job_service.py`, `backend/app/api/v1/candidates.py`, `backend/app/api/v1/review_tasks.py`, `backend/app/api/v1/assets.py`, `backend/app/main.py`, `backend/alembic/versions/20260908_sg014_candidate.py`, `backend/tests/test_dedup.py`, `backend/tests/test_candidates.py`, `backend/tests/test_export.py`, `docs/adr/ADR-006-duplicate-policy.md`, `docs/adr/ADR-003-job-orchestration.md`, `docs/worklogs/SG-014.log`, and `docs/worklogs/SG-014_report.md`.

UNCLEAR — FIRST READ: The repository uses `backend/alembic`; the packet’s `backend/migrations` wording was not tree-accurate.
UNCLEAR — DURING EXECUTION: Sandbox decoder absence and full-suite settings coupling were observed and reported; neither was routed around.
UNCLEAR — REMAINING: The out-of-ceiling SG-013 migration test still assumes its old head, and decoder legs remain for manual compose verification.
