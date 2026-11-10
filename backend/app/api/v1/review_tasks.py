import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.asset import Asset
from app.models.review_task import ReviewTask
from app.schemas.common import decode_cursor, encode_cursor
from app.services import audit_service, lifecycle
from app.services.candidates import Candidate

router = APIRouter()

# SG-188 (D7): data-required task types cannot be closed by a bare resolve.
# `expiry.manual_entry` is satisfied only by real manual-entry data
# (`store_manual_expiry` writes the accepted expiry assertion, resolves the
# task(s) and answers `resolved_review_task_ids`); a bare `{}` resolve would
# close it while the lived assert stays `{"status": "unknown"}`.
DATA_REQUIRED_TASK_TYPES = frozenset({"expiry.manual_entry"})


def _missing_data_name(task: ReviewTask) -> str:
    """The field the task asks the user to supply, for the refusal message."""
    if task.proposed_change:
        try:
            proposal = json.loads(task.proposed_change)
        except ValueError:
            proposal = None
        if isinstance(proposal, dict):
            field_path = proposal.get("field_path")
            if isinstance(field_path, str) and field_path:
                return field_path.rsplit("/", 1)[-1]
    return "expiry_date"


def _visible_tasks(db: Session, household_id: str):  # type: ignore[no-untyped-def]
    """SG-297 I2/I3: the household's tasks, minus those whose subject asset is not ACTIVE.

    SG-272 G1/G2: a gone item's asset-subject tasks hide until it is put back.
    Rows are never mutated, so hiding and restoring are automatic. The filter
    runs in the query, before pagination, so a page holds its full limit of
    visible tasks, the cursor stays correct, and `total` counts what is listed.
    Candidate subjects are never in the Asset table, so they are unaffected.
    """
    gone_asset_ids = select(Asset.id).where(
        Asset.household_id == household_id,
        ~lifecycle.active_clause(),
    )
    return db.query(ReviewTask).filter(
        ReviewTask.household_id == household_id,
        ReviewTask.subject_ref.notin_(gone_asset_ids),
    )


@router.get("/review-tasks")
def list_review_tasks(
    household_id: str = Query(...),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
):  # type: ignore[no-untyped-def]
    query = _visible_tasks(db, household_id)
    # SG-188 (D7): a cursor that cannot be decoded is a 422, never a silent
    # page-1 repeat (the pre-slice `if decoded:` skipped the filter).
    if cursor is not None:
        decoded = decode_cursor(cursor)
        if decoded is None:
            raise HTTPException(status_code=422, detail="malformed cursor")
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
    # SG-270 G4: resolve each page's subject kind with one batched lookup per
    # subject table, never one query per row.
    # SG-297 I2: gone-asset tasks are excluded in the query (see _visible_tasks),
    # so no page is cut short and `total` excludes them.
    subject_refs = {item.subject_ref for item in items}
    candidate_ids: set[str] = set()
    asset_ids: set[str] = set()
    if subject_refs:
        candidate_ids = {
            str(row[0])
            for row in db.query(Candidate.id)
            .filter(Candidate.id.in_(subject_refs), Candidate.household_id == household_id)
            .all()
        }
        asset_ids = {
            str(row[0])
            for row in db.query(Asset.id)
            .filter(Asset.id.in_(subject_refs), Asset.household_id == household_id)
            .all()
        }
    return {
        "items": [
            {
                "id": item.id,
                "task_type": item.task_type,
                "priority": item.priority,
                "subject_ref": item.subject_ref,
                "subject_kind": (
                    "candidate"
                    if item.subject_ref in candidate_ids
                    else "asset"
                    if item.subject_ref in asset_ids
                    else "unknown"
                ),
                "data_required": item.task_type in DATA_REQUIRED_TASK_TYPES,
                "proposed_change": json.loads(item.proposed_change) if item.proposed_change else None,
                "status": item.status,
                "household_id": item.household_id,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in items
        ],
        "next_cursor": next_cursor,
        "total": _visible_tasks(db, household_id).count(),
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
    # SG-188 (D7): refuse a dataless resolve of a data-required task type; the
    # real manual-entry path is the completion that carries data.
    if task.task_type in DATA_REQUIRED_TASK_TYPES and not payload:
        raise HTTPException(
            status_code=422,
            detail=(
                f"task requires the {_missing_data_name(task)} before it can be "
                "resolved; enter it through the expiry manual-entry path"
            ),
        )
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
