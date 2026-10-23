"""SG-233: durable expiry reminders computed by the real urgency engine.

The single production writer is ``record_due``. It reads
``expiry_engine.compute_status`` and stores one unread row per tiered entry
that has no row for the same ``(asset_id, as_of_day)``. The unique constraint
is the structural idempotence guard; a second run for the same day inserts
nothing. Unresolved rows never create a reminder.

"Tiered" means the tier is one of the live category's ``tier_defaults`` keys,
so the row always names the window that fired (for example food ``urgent`` at
seven days). Expired rows (no tier) and the synthesised ``safe`` tier (not a
``tier_defaults`` key) are not warnings and create nothing.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.models.reminder import Reminder
from app.plugins.expiry_tracker import CATEGORIES
from app.services import expiry_engine


def today_utc() -> date:
    """The live UTC calendar day; callers may pass an explicit day instead."""
    return datetime.now(timezone.utc).date()


def window_days_for(tier: str | None, category_slug: str | None) -> int | None:
    """The live tier window that produced ``tier``, or None when untiered."""
    if tier is None or category_slug is None:
        return None
    category = CATEGORIES.get(category_slug)
    if category is None:
        return None
    return category.tier_defaults.get(tier)


def record_due(
    db: Session, household_id: str, as_of_day: date | None = None
) -> list[Reminder]:
    """Insert the missing unread reminders for one household and day.

    Returns only the rows this call created. The caller owns the session; the
    writer commits its inserts so a later run sees them.
    """
    day = as_of_day if as_of_day is not None else today_utc()
    day_key = day.isoformat()
    status = expiry_engine.compute_status(db, household_id, day)
    existing = {
        asset_id
        for (asset_id,) in db.query(Reminder.asset_id)
        .filter(
            Reminder.household_id == household_id,
            Reminder.as_of_day == day_key,
        )
        .all()
    }
    created: list[Reminder] = []
    for row in status["rows"]:
        asset_id = row["asset_id"]
        if asset_id in existing:
            continue
        if window_days_for(row["tier"], row["category"]) is None:
            continue
        created.append(
            Reminder(
                household_id=household_id,
                asset_id=asset_id,
                as_of_day=day_key,
                tier=row["tier"],
                bucket=row["bucket"],
                days_remaining=row["days_remaining"],
                status="unread",
            )
        )
        existing.add(asset_id)
    if created:
        db.add_all(created)
        db.commit()
    return created
