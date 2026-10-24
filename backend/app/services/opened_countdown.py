"""SG-240: the opened-date countdown over existing rows (roadmap row 11).

Pure computation in the shape of ``expiry_engine``: the caller supplies
``as_of`` (the route defaults it to the live UTC day), this module has no clock
of its own, it writes nothing, it visits ACTIVE assets only, and it reads the
accepted category slug through the engine's own reader. The window is read from
the LIVE ``CATEGORIES`` row, never from a stored snapshot.

D1 (DECLARED UNCALIBRATED): the window is the category's after-opening period.
For ``cosmetics_personal_care`` it is 12 months — the printed
period-after-opening (PAO) open-jar figure under EU Regulation 1223/2009
Art. 19. The printed figure varies per product (the pack may say 6M or 18M), so
the response names the window and its source (``category_default``) and a
per-item override stays parked.

Calendar-month arithmetic, not 30-day blocks: the end date is the opened date
plus the window in months, with the day clamped to the last day of the target
month (31 January + 1 month ends 28/29 February; 29 February + 12 months ends
28 February). ``days_remaining`` is negative once the window has passed.
"""

from __future__ import annotations

import calendar
import json
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models.assertion import Assertion
from app.models.asset import Asset
from app.plugins.expiry_tracker import CATEGORIES, OPENED_DATE_FIELD
from app.services import lifecycle
from app.services.expiry_engine import _accepted_classification_slug

WINDOW_SOURCE_CATEGORY_DEFAULT = "category_default"


def add_months(start: date, months: int) -> date:
    """Add calendar months, clamping the day to the target month's last day."""
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _accepted_opened_date(db: Session, asset_id: str) -> date | None:
    assertion = (
        db.query(Assertion)
        .filter(
            Assertion.asset_id == asset_id,
            Assertion.field_path == OPENED_DATE_FIELD,
            Assertion.review_state == "accepted",
        )
        .order_by(Assertion.created_at.desc())
        .first()
    )
    if assertion is None:
        return None
    try:
        value = json.loads(assertion.value_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def compute_opened_countdown(
    db: Session, household_id: str, as_of: date
) -> dict[str, Any]:
    """One row per ACTIVE asset in an opened-date-tracking category, read-only.

    A row is present even when the asset has no opened date yet (the UI offers
    the form); an asset with no accepted classification, or in a category that
    does not track opened dates, is not a row at all.
    """
    rows: list[dict[str, Any]] = []
    assets = (
        db.query(Asset)
        .filter(Asset.household_id == household_id, lifecycle.active_clause())
        .order_by(Asset.id)
        .all()
    )
    for asset in assets:
        slug = _accepted_classification_slug(db, asset.id)
        if slug is None:
            continue
        category = CATEGORIES.get(slug)
        if category is None or not category.opened_date_tracking:
            continue
        opened = _accepted_opened_date(db, asset.id)
        window_months = category.opened_window_months
        window_end: date | None = None
        days_open: int | None = None
        days_left: int | None = None
        if opened is not None:
            days_open = (as_of - opened).days
            if window_months is not None:
                window_end = add_months(opened, window_months)
                days_left = (window_end - as_of).days
        rows.append(
            {
                "asset_id": asset.id,
                "display_name": asset.display_name,
                "category": slug,
                "opened_date": opened.isoformat() if opened is not None else None,
                "days_open": days_open,
                "window_months": window_months,
                "window_source": WINDOW_SOURCE_CATEGORY_DEFAULT,
                "days_remaining": days_left,
                "window_end": window_end.isoformat() if window_end is not None else None,
            }
        )
    return {"household_id": household_id, "as_of": as_of.isoformat(), "rows": rows}
