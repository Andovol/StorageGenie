"""SG-233 in-app reminders: the unread list plus read/dismiss transitions.

Reads are household-scoped and unread-first (most urgent first within each
group). A row may move unread -> read, unread -> dismissed, or read ->
dismissed; every other transition is refused with 422. There is no delivery
channel here: the Expiry page is the sender.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.asset import Asset
from app.models.household import Household
from app.models.reminder import Reminder
from app.services import expiry_engine
from app.services.reminders.service import window_days_for

router = APIRouter()

LEGAL_TRANSITIONS: dict[str, frozenset[str]] = {
    "read": frozenset({"unread"}),
    "dismissed": frozenset({"unread", "read"}),
}


def _asset_names(db: Session, asset_ids: list[str]) -> dict[str, str | None]:
    if not asset_ids:
        return {}
    rows = db.query(Asset.id, Asset.display_name).filter(Asset.id.in_(asset_ids)).all()
    return {asset_id: display_name for asset_id, display_name in rows}


def _serialize(
    db: Session, reminder: Reminder, asset_names: dict[str, str | None] | None = None
) -> dict[str, object]:
    names = asset_names if asset_names is not None else _asset_names(db, [reminder.asset_id])
    category_slug = expiry_engine._accepted_classification_slug(db, reminder.asset_id)
    return {
        "id": reminder.id,
        "household_id": reminder.household_id,
        "asset_id": reminder.asset_id,
        "display_name": names.get(reminder.asset_id),
        "as_of_day": reminder.as_of_day,
        "tier": reminder.tier,
        "window_days": window_days_for(reminder.tier, category_slug),
        "bucket": reminder.bucket,
        "days_remaining": reminder.days_remaining,
        "status": reminder.status,
        "created_at": reminder.created_at.isoformat() if reminder.created_at else None,
        "updated_at": reminder.updated_at.isoformat() if reminder.updated_at else None,
    }


def _owned_reminder(db: Session, reminder_id: str, household_id: str) -> Reminder:
    reminder = db.query(Reminder).filter_by(id=reminder_id).first()
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if reminder.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return reminder


@router.get("/reminders")
def list_reminders(
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Every reminder for one household, unread first then most urgent first."""
    if db.query(Household).filter_by(id=household_id).first() is None:
        raise HTTPException(status_code=404, detail="Household not found")
    rows = (
        db.query(Reminder)
        .filter(Reminder.household_id == household_id)
        .order_by(
            case((Reminder.status == "unread", 0), else_=1),
            Reminder.days_remaining,
            Reminder.asset_id,
        )
        .all()
    )
    names = _asset_names(db, [row.asset_id for row in rows])
    return {
        "household_id": household_id,
        "unread_count": sum(1 for row in rows if row.status == "unread"),
        "items": [_serialize(db, row, names) for row in rows],
    }


def _transition(
    db: Session, reminder_id: str, household_id: str, target: str
) -> dict[str, object]:
    reminder = _owned_reminder(db, reminder_id, household_id)
    if reminder.status not in LEGAL_TRANSITIONS[target]:
        raise HTTPException(
            status_code=422,
            detail=f"cannot mark a {reminder.status} reminder as {target}",
        )
    reminder.status = target
    db.commit()
    return _serialize(db, reminder)


@router.post("/reminders/{reminder_id}/read")
def read_reminder(
    reminder_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return _transition(db, reminder_id, household_id, "read")


@router.post("/reminders/{reminder_id}/dismiss")
def dismiss_reminder(
    reminder_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return _transition(db, reminder_id, household_id, "dismissed")
