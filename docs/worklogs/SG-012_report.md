SG-012 — job engine core report

Status: complete

Ref and provenance
- BASE_REF_REQUESTED: `automation`.
- BASE_RESOLVED_COMMIT: `86e8860f4d614f06f530e1ab4d1fbc02bcb2c611`.
- WORK_HEAD: recorded by the final receipt note on the final evidence commit.
- Origin: `git@github.com:Andovol/StorageGenie.git`.
- Work dir: `/home/andrei/StorageGenie`.
- Coder: `codex`; reasoning effort: `high` from the committed dispatch parameter. Model ID: `unknown` because it was not present in process arguments or provider metadata.
- Overall bound: `2100s`; measured named command subtotal under `5s`; no command was killed.

Acceptance evidence

1. Lifecycle and durable steps — `backend/tests/test_import_jobs.py:68-110` creates an import with one evidence reference, asserts HTTP 201 and six persisted `job_step` rows through the database session, runs it, and reads the resulting state and attempts through both the detail response and persisted rows. The final state is `AWAITING_REVIEW`; four steps are `COMPLETED`, the review step is `AWAITING_REVIEW`, and `COMMITTING` is `PENDING`. Stub output and `completed_at` are asserted from `job_step.output_refs`, not only from the response.

2. Failure, resume, and catalog safety — `backend/tests/test_import_jobs.py:113-161` injects a real exception at `NORMALIZING`, observes `FAILED` and the persisted error text, then calls retry and reaches `AWAITING_REVIEW`. It asserts six total step rows, zero assets, and zero assertions, with job audit rows present. The current slice stops before catalog commit, so evidence rows supplied before job creation remain fixture input; no asset/assertion/catalog row is created by the failed job. Double retry and double run are exercised and do not add rows.

3. Idempotency and household boundary — `backend/tests/test_import_jobs.py:164-204` replays the same `Idempotency-Key` and proves one `Job` row plus the same ID. It exercises cross-household detail, run, retry, and evidence-backed create paths and requires `[403, 403, 403, 403]`. The implementation uses the real `idempotency_key` table and `IdempotencyKey.response_json` at `backend/app/api/v1/jobs.py:39-75`.

4. Audit — `backend/app/services/job_service.py:45-60` records every state transition and `:90-99` records creation through the existing `audit_service.record` interface (`backend/app/services/audit_service.py:9-31`). The failure test checks at least three job lifecycle audit rows.

5. Migration verdict — `no-migration-needed`. Column mapping is documented in `docs/adr/ADR-003-job-orchestration.md` under Migration verdict: job state/type/household/idempotency; job timestamps from `TimestampMixin`; ordered step identity/state/attempts; evidence inputs in `config_snapshot`/`input_refs`; and outputs/errors/timestamps in `output_refs`. No Alembic revision was added. `backend/tests/test_export.py:95-117` remained green and independently checked the current head.

6. Jobs read-back — `backend/app/api/v1/jobs.py:107-136` retains the existing cursor query and now serializes real items and total. The new list assertion is `backend/tests/test_import_jobs.py:99-101`. The old SG-008 empty-list assertion remains only for an empty database in `backend/tests/test_export.py:173-183`; it was not altered because the packet’s explicit scope ceiling permits extending that file only for the migration-head leg. A non-empty list gate therefore proves the old stub cannot satisfy the new behavior.

7. Fail-first and gates — The pre-change test run was real: `3 failed, 1 warning in 0.97s`, with `POST /v1/imports` returning 404. Post-change targeted import/export tests reported `8 passed, 1 warning in 1.15s`; the full backend suite reported `27 passed, 1 warning in 1.79s`; `ruff check backend` reported `All checks passed!`; `git diff --check` was clean. Advisory `mypy app` reported 40 errors in 9 files and was not used as a gate. No gate passed vacuously: the new file has three tests, the full suite has 27 passing tests, and no tests were skipped.

8. Route and scope gate — Changed route decorators are exactly the six listed in `docs/worklogs/SG-012.log`; no route outside `/v1/imports*` and the existing `/v1/jobs*` surface was created or modified. Changed output paths are:
   - `backend/app/services/job_service.py`
   - `backend/app/api/v1/jobs.py`
   - `backend/tests/test_import_jobs.py`
   - `docs/adr/ADR-003-job-orchestration.md`
   - `docs/worklogs/SG-012.log`
   - `docs/worklogs/SG-012_report.md`

No migration file, frontend, runtime dependency, `.env`, secret, restart, service, live database, Docker, host, or privileged operation was touched. The `/review_tasks` underscore alias was left unchanged.

9. Receipt handoff — The final work commit is pushed to `automation`; the notes ref `refs/notes/storagegenie-coder-reports` carries the note whose first line contains `Dispatch-ID: SG-012` and `Report: docs/worklogs/SG-012_report.md`. The local note and remote read-back are quoted after the final commit in the handoff record. No commit follows the note.

UNCLEAR: FIRST READ — The stated base resolved to `86e8860`; the cited governance path `docs/ARCHITECT.md` was absent. The existing schema was verified sufficient, so the migration verdict is `no-migration-needed`.
UNCLEAR: DURING EXECUTION — The packet’s prior 43 mypy advisory count differed from the measured final 40 after three in-scope jobs annotations were tightened; the remaining 40 are advisory/out of scope. The known Starlette warning remained.
UNCLEAR: REMAINING — Step bodies for deterministic signal extraction, deduplication, and catalog commit remain stubs for SG-013/SG-014; the synchronous request-bound runner has not been promoted to a worker; Docker/restart/live-service verification remains out of scope.
