from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.job import Job
from app.schemas.common import decode_cursor, encode_cursor

router = APIRouter()


@router.get("/jobs")
def list_jobs(
    household_id: str = Query(...),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
):  # type: ignore[no-untyped-def]
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
    return {"items": [], "next_cursor": next_cursor, "total": 0}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, household_id: str = Query(...), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    from fastapi import HTTPException

    j = db.query(Job).filter_by(id=job_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Job not found")
    if j.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return {"id": j.id, "job_type": j.job_type, "state": j.state, "household_id": j.household_id}
