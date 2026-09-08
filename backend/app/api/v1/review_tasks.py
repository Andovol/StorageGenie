import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.review_task import ReviewTask
from app.schemas.common import decode_cursor, encode_cursor
from app.services import audit_service

router = APIRouter()


@router.get("/review-tasks")
def list_review_tasks(
    household_id: str = Query(...),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
):  # type: ignore[no-untyped-def]
    query = db.query(ReviewTask).filter(ReviewTask.household_id == household_id)
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded:
            ts, oid = decoded
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            created_str = func.strftime("%Y-%m-%d %H:%M:%S", ReviewTask.created_at)
            query = query.filter(or_(created_str < ts_str, and_(created_str == ts_str, ReviewTask.id < oid)))
    query = query.order_by(ReviewTask.created_at.desc(), ReviewTask.id.desc()).limit(limit + 1)
    items = query.all()
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
        last = items[-1]
        next_cursor = encode_cursor(last.created_at, last.id)
    else:
        next_cursor = None
    return {
        "items": [
            {
                "id": item.id,
                "task_type": item.task_type,
                "priority": item.priority,
                "subject_ref": item.subject_ref,
                "proposed_change": json.loads(item.proposed_change) if item.proposed_change else None,
                "status": item.status,
                "household_id": item.household_id,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in items
        ],
        "next_cursor": next_cursor,
        "total": db.query(ReviewTask).filter(ReviewTask.household_id == household_id).count(),
    }


# Alias with underscore for compatibility
@router.get("/review_tasks")
def list_review_tasks_alias(
    household_id: str = Query(...),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
):  # type: ignore[no-untyped-def]
    return list_review_tasks(household_id=household_id, cursor=cursor, limit=limit, db=db)


@router.post("/review-tasks/{task_id}/resolve")
def resolve_review_task(
    task_id: str,
    payload: dict[str, object] | None = None,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    task = db.query(ReviewTask).filter_by(id=task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Review task not found")
    if task.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    if task.status != "resolved":
        before = {"status": task.status}
        task.status = "resolved"
        task.updated_at = datetime.datetime.now(datetime.timezone.utc)
        audit_service.record(
            db,
            actor="api",
            action="review_task.resolve",
            entity_type="review_task",
            entity_id=task.id,
            before=before,
            after={"status": task.status, "resolution": payload or {}},
            household_id=task.household_id,
        )
        db.commit()
    return {"id": task.id, "status": task.status, "subject_ref": task.subject_ref}
