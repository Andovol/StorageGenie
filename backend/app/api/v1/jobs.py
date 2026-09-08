import json

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.evidence import Evidence
from app.models.idempotency import IdempotencyKey
from app.models.job import Job
from app.schemas.common import decode_cursor, encode_cursor
from app.services import job_service

router = APIRouter()


class ImportCreate(BaseModel):
    evidence_ids: list[str] = Field(default_factory=list)
    config: dict[str, object] = Field(default_factory=dict)


def _owned_job(db: Session, job_id: str, household_id: str) -> Job:
    job = db.query(Job).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return job


@router.post("/imports", status_code=201)
def create_import(  # noqa: C901
    payload: ImportCreate,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    if idempotency_key:
        existing_job = db.query(Job).filter_by(idempotency_key=idempotency_key).first()
        if existing_job:
            if existing_job.household_id != household_id:
                raise HTTPException(status_code=403, detail="Household mismatch")
            return job_service.serialize_job(db, existing_job)
        existing_key = db.query(IdempotencyKey).filter_by(key=idempotency_key).first()
        if existing_key:
            raise HTTPException(status_code=409, detail="Idempotency key already used")

    evidence_ids = list(dict.fromkeys(payload.evidence_ids))
    if evidence_ids:
        evidence = db.query(Evidence).filter(Evidence.id.in_(evidence_ids)).all()
        found = {item.id: item for item in evidence}
        if len(found) != len(evidence_ids):
            raise HTTPException(status_code=404, detail="Evidence not found")
        if any(item.household_id != household_id for item in evidence):
            raise HTTPException(status_code=403, detail="Household mismatch")

    job = job_service.create_job(
        db,
        household_id,
        evidence_ids,
        config=payload.config,
        idempotency_key=idempotency_key,
    )
    if idempotency_key:
        db.add(IdempotencyKey(key=idempotency_key, response_json=json.dumps({"id": job.id})))
        try:
            db.commit()
        except Exception:
            db.rollback()
            existing_job = db.query(Job).filter_by(idempotency_key=idempotency_key).first()
            if existing_job:
                return job_service.serialize_job(db, existing_job)
            raise
    return job_service.serialize_job(db, job)


@router.post("/imports/{job_id}/run")
def run_import(
    job_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    job = _owned_job(db, job_id, household_id)
    return job_service.serialize_job(db, job_service.run_job(db, job))


@router.post("/imports/{job_id}/retry")
def retry_import(
    job_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    job = _owned_job(db, job_id, household_id)
    return job_service.serialize_job(db, job_service.retry_job(db, job))


@router.get("/imports/{job_id}")
def get_import(
    job_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return job_service.serialize_job(db, _owned_job(db, job_id, household_id))


@router.get("/jobs")
def list_jobs(
    household_id: str = Query(...),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    query = db.query(Job).filter(Job.household_id == household_id)
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded:
            ts, oid = decoded
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            created_str = func.strftime("%Y-%m-%d %H:%M:%S", Job.created_at)
            query = query.filter(or_(created_str < ts_str, and_(created_str == ts_str, Job.id < oid)))
    query = query.order_by(Job.created_at.desc(), Job.id.desc()).limit(limit + 1)
    items = query.all()
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
        last = items[-1]
        next_cursor = encode_cursor(last.created_at, last.id)
    else:
        next_cursor = None
    total = db.query(Job).filter(Job.household_id == household_id).count()
    return {
        "items": [job_service.list_item(item) for item in items],
        "next_cursor": next_cursor,
        "total": total,
    }


@router.get("/jobs/{job_id}")
def get_job(
    job_id: str, household_id: str = Query(...), db: Session = Depends(get_db)
) -> dict[str, object]:
    from fastapi import HTTPException

    j = db.query(Job).filter_by(id=job_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Job not found")
    if j.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return {"id": j.id, "job_type": j.job_type, "state": j.state, "household_id": j.household_id}
