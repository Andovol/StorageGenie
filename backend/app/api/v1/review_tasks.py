from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.review_task import ReviewTask
from app.schemas.common import decode_cursor, encode_cursor

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
    return {"items": [], "next_cursor": next_cursor, "total": 0}


# Alias with underscore for compatibility
@router.get("/review_tasks")
def list_review_tasks_alias(
    household_id: str = Query(...),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
):  # type: ignore[no-untyped-def]
    return list_review_tasks(household_id=household_id, cursor=cursor, limit=limit, db=db)
