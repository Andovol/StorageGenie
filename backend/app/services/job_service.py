from __future__ import annotations

import datetime
import json
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.job import Job, JobStep
from app.services import audit_service

STEP_NAMES = (
    "VALIDATING_INPUT",
    "NORMALIZING",
    "EXTRACTING_DETERMINISTIC_SIGNALS",
    "DEDUPLICATING",
    "AWAITING_REVIEW",
    "COMMITTING",
)
COMPLETED_STEP = "COMPLETED"
PENDING_STEP = "PENDING"
FAILED_STEP = "FAILED"
RETRYING_STEP = "RETRYING"
AWAITING_REVIEW_STATE = "AWAITING_REVIEW"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def _loads(value: str | None) -> object:
    if value is None:
        return None
    return json.loads(value)


def _state_snapshot(job: Job) -> dict[str, str | None]:
    return {"state": job.state, "updated_at": job.updated_at.isoformat() if job.updated_at else None}


def _transition(db: Session, job: Job, state: str) -> None:
    if job.state == state:
        return
    before = _state_snapshot(job)
    job.state = state
    job.updated_at = datetime.datetime.now(datetime.timezone.utc)
    audit_service.record(
        db,
        actor="job-runner",
        action="job.state_transition",
        entity_type="job",
        entity_id=job.id,
        before=before,
        after={"state": state, "updated_at": job.updated_at.isoformat()},
        household_id=job.household_id,
    )


def create_job(
    db: Session,
    household_id: str,
    evidence_ids: Sequence[str],
    config: dict[str, object] | None = None,
    idempotency_key: str | None = None,
) -> Job:
    evidence_refs = list(dict.fromkeys(evidence_ids))
    job = Job(
        job_type="import",
        state="CREATED",
        idempotency_key=idempotency_key,
        config_snapshot=_json({"evidence_ids": evidence_refs, "config": config or {}}),
        household_id=household_id,
    )
    db.add(job)
    db.flush()
    for step_name in STEP_NAMES:
        db.add(
            JobStep(
                job_id=job.id,
                step_name=step_name,
                state=PENDING_STEP,
                attempts=0,
                input_refs=_json({"evidence_ids": evidence_refs}),
            )
        )
    audit_service.record(
        db,
        actor="api",
        action="job.create",
        entity_type="job",
        entity_id=job.id,
        before=None,
        after={"job_type": job.job_type, "state": job.state, "evidence_ids": evidence_refs},
        household_id=household_id,
    )
    db.commit()
    db.refresh(job)
    return job


def execute_step(db: Session, job: Job, step: JobStep) -> dict[str, object]:
    """Execute one deterministic Phase 1 step.

    The signal, deduplication, and catalog commit bodies deliberately remain
    stubs for SG-013/SG-014.  Keeping this function as the seam makes failure
    injection and a future queue worker possible without changing persistence.
    """
    if step.step_name == "VALIDATING_INPUT":
        return {"status": "ok", "step": step.step_name}
    if step.step_name == "AWAITING_REVIEW":
        return {"status": "awaiting_review", "step": step.step_name}
    return {"status": "not_implemented", "step": step.step_name}


def _steps(db: Session, job_id: str) -> list[JobStep]:
    rows = db.query(JobStep).filter(JobStep.job_id == job_id).all()
    order = {name: index for index, name in enumerate(STEP_NAMES)}
    return sorted(rows, key=lambda row: order.get(row.step_name, len(STEP_NAMES)))


def _step_output(step: JobStep) -> dict[str, object] | None:
    value = _loads(step.output_refs)
    return value if isinstance(value, dict) else None


def run_job(db: Session, job: Job) -> Job:
    if job.state in {AWAITING_REVIEW_STATE, "COMPLETED", "CANCELLED", "FAILED"}:
        return job
    if job.state in {"CREATED", RETRYING_STEP}:
        _transition(db, job, "RUNNING")
        db.commit()

    for step in _steps(db, job.id):
        if step.state == COMPLETED_STEP:
            continue
        if step.step_name == "COMMITTING":
            break
        if step.state == AWAITING_REVIEW_STATE:
            _transition(db, job, AWAITING_REVIEW_STATE)
            db.commit()
            return job

        step.state = "RUNNING"
        step.attempts += 1
        step.output_refs = _json({"started_at": _now()})
        db.commit()
        try:
            output = execute_step(db, job, step)
        except Exception as exc:
            db.rollback()
            failed_step = db.query(JobStep).filter_by(id=step.id).one()
            failed_job = db.query(Job).filter_by(id=job.id).one()
            failed_step.state = FAILED_STEP
            failed_step.output_refs = _json({"error": str(exc), "failed_at": _now()})
            _transition(db, failed_job, "FAILED")
            db.commit()
            return failed_job

        step = db.query(JobStep).filter_by(id=step.id).one()
        step.output_refs = _json({**output, "completed_at": _now()})
        if step.step_name == "AWAITING_REVIEW":
            step.state = AWAITING_REVIEW_STATE
            job = db.query(Job).filter_by(id=job.id).one()
            _transition(db, job, AWAITING_REVIEW_STATE)
        else:
            step.state = COMPLETED_STEP
        db.commit()
        if step.step_name == "AWAITING_REVIEW":
            return job

    return db.query(Job).filter_by(id=job.id).one()


def retry_job(db: Session, job: Job) -> Job:
    if job.state != "FAILED":
        return run_job(db, job)
    failed_steps = [step for step in _steps(db, job.id) if step.state == FAILED_STEP]
    if not failed_steps:
        return run_job(db, job)
    _transition(db, job, RETRYING_STEP)
    for step in failed_steps:
        step.state = RETRYING_STEP
        step.output_refs = _json({"retrying_at": _now()})
    db.commit()
    return run_job(db, db.query(Job).filter_by(id=job.id).one())


def serialize_job(db: Session, job: Job) -> dict[str, object]:
    steps = _steps(db, job.id)
    step_items: list[dict[str, object]] = []
    for step in steps:
        output = _step_output(step)
        error = output.get("error") if output else None
        step_items.append(
            {
                "id": step.id,
                "step_name": step.step_name,
                "state": step.state,
                "attempts": step.attempts,
                "input": _loads(step.input_refs),
                "output": output,
                "error": error,
            }
        )
    completed = sum(step.state == COMPLETED_STEP for step in steps)
    failed = sum(step.state == FAILED_STEP for step in steps)
    pending = sum(step.state in {PENDING_STEP, RETRYING_STEP, "RUNNING"} for step in steps)
    errors = [step["error"] for step in step_items if step["error"] is not None]
    return {
        "id": job.id,
        "job_type": job.job_type,
        "state": job.state,
        "household_id": job.household_id,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        "steps": step_items,
        "progress": {
            "completed": completed,
            "total": len(steps),
            "failed": failed,
            "pending": pending,
        },
        "errors": errors,
    }


def list_item(job: Job) -> dict[str, object]:
    return {
        "id": job.id,
        "job_type": job.job_type,
        "state": job.state,
        "household_id": job.household_id,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }
