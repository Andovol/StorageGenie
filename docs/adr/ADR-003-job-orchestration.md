# ADR-003: Durable import job orchestration

- Status: accepted for Phase 1 slice 1
- Date: 2026-09-08

## Decision

Import orchestration is a synchronous in-request runner in the modular monolith.
Each import owns six deterministic, ordered steps:
`VALIDATING_INPUT`, `NORMALIZING`, `EXTRACTING_DETERMINISTIC_SIGNALS`,
`DEDUPLICATING`, `AWAITING_REVIEW`, and `COMMITTING`. The step catalog is bound in
`backend/app/services/job_service.py:12-18`.

The database is the durable source of truth for progress. Creation writes one
`Job` and one `JobStep` per catalog entry at
`backend/app/services/job_service.py:63-102`; the API creates these rows at
`backend/app/api/v1/jobs.py:32-75`. Evidence references are carried in the
existing `job.config_snapshot` and `job_step.input_refs` JSON columns. Step
outputs, errors, and transition timestamps are carried in the existing
`job_step.output_refs` JSON column at
`backend/app/services/job_service.py:147-175` and `:178-189`.

The runner commits each durable step boundary. A failed step is recorded as
`FAILED` with its error and `failed_at`, and the job is parked in `FAILED`
(`backend/app/services/job_service.py:151-161`). Retry changes failed steps to
`RETRYING`, preserves completed predecessors, and resumes from the first failed
step (`backend/app/services/job_service.py:178-189`). Re-running an awaiting,
failed, completed, or cancelled job is a no-op unless the retry route explicitly
resets a failed step (`backend/app/services/job_service.py:130-145`).

The runner stops at `AWAITING_REVIEW`; the `COMMITTING` body is intentionally
still pending for SG-014. Therefore this slice creates no catalog rows during an
import run. When catalog commit is implemented, it must execute as one database
transaction at that step boundary, with failure rolling back the asset,
evidence-link, and assertion writes. The current failure test proves that an
injected pre-commit failure leaves those catalog tables unchanged
(`backend/tests/test_import_jobs.py:113-161`).

## Migration verdict

`20260908_sg013_observation` added durable observations; the foundation revision remains sufficient for job orchestration:

| Required durable value | Existing storage |
| --- | --- |
| Job type, household, idempotency, state | `job.job_type`, `job.household_id`, `job.idempotency_key`, `job.state` (`backend/app/models/job.py:8-21`) |
| Job lifecycle timestamps | `job.created_at`, `job.updated_at` from `TimestampMixin` (`backend/app/models/job.py:8-10`, `backend/app/models/base.py:19-25`) |
| Ordered step identity/state/attempts | `job_step.job_id`, `step_name`, `state`, `attempts` (`backend/app/models/job.py:24-39`) |
| Evidence input references | `job.config_snapshot` and `job_step.input_refs` (`backend/app/models/job.py:18-21,35-39`) |
| Outputs, errors, and step timestamps | JSON values in `job_step.output_refs` (`backend/app/services/job_service.py:147-164`) |

`20260908_sg013_observation` is the later revision at this boundary. The existing export regression remains the
mechanism check: `backend/tests/test_export.py:95-117` compares the exported
revision to the independently discovered Alembic head.

## Audit and API boundary

Creation and every job state transition are recorded through
`backend/app/services/audit_service.py:9-31`, called by
`backend/app/services/job_service.py:45-60,90-99`. The four import endpoints
and household checks are in `backend/app/api/v1/jobs.py:32-104`. The existing
cursor query is retained and now serializes its rows at
`backend/app/api/v1/jobs.py:107-136`.

## Future queue path

The `execute_step` seam at `backend/app/services/job_service.py:105-116` is the
future worker boundary. A queue/worker can claim a persisted `PENDING` or
`RETRYING` step and invoke the same step handlers, retaining the database state
machine and idempotency rules. No worker process or queue dependency is added in
this slice; the Phase 1 plan requires evidence before splitting the monolith.

## Consequences

Failures are visible and resumable without infrastructure, and duplicate run or
retry requests do not add step rows or repeat completed steps. The trade-off is
that long-running extraction remains request-bound until a later queue decision;
that limitation is explicit rather than hidden.
