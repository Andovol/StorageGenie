"""SG-107: the pure expiry urgency engine (Arc B slice 1).

Pure computation over existing rows — no scheduler, no sender, no table, no
model change, and no clock beyond the caller-supplied `as_of`. Two derived
facts per resolved asset:

* a **tier** — the notification window the date falls in, read from the LIVE
  `CATEGORIES[slug].tier_defaults` the plugin already ships. This module holds
  NO hardcoded window numbers, so tier calibration tunes data, never this code.
  The windows are DECLARED UNCALIBRATED (`G-A9`).
* a **bucket** — the fixed blueprint §11.2 urgency bucket (expired / this-week /
  this-month / safe).

Resolved rule (STRICTER than analytics — D143): an asset is tiered/bucketed
ONLY on an `EXPIRY_FIELD` assertion with `review_state == "accepted"` AND a
parseable `YYYY-MM-DD` `expiry_date` string. A `proposed` or `needs_evidence`
date is never tiered; it is reported as an unresolved row. This deliberately
does NOT copy the analytics `not_in(("superseded", "rejected"))` predicate,
which would silently tier a proposed date.

Tier rule: `d < 0` → expired, tier `null`; otherwise the first ascending window
whose `days` satisfies `d <= days` names the tier; beyond the widest window the
tier is `"safe"`; a category with no windows (`non_perishable`) is tier `null`
while its bucket is still computed.

The route-facing summary counts resolved rows only, and `by_tier` uses the key
`"none"` for a null tier so that `sum(by_tier) == sum(by_bucket) == len(rows)`
reconciles exactly.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models.assertion import Assertion
from app.models.asset import Asset
from app.plugins.expiry_tracker import CATEGORIES, CLASSIFICATION_FIELD, EXPIRY_FIELD
from app.services import lifecycle

# The fixed blueprint §11.2 buckets. These are NOT calibration windows: they are
# the dashboard's coarse urgency buckets and carry no per-category numbers.
BUCKETS: tuple[str, ...] = ("expired", "this-week", "this-month", "safe")


def days_remaining(expiry: date, as_of: date) -> int:
    """Calendar-day distance from `as_of` to `expiry` (negative when past)."""
    return (expiry - as_of).days


def tier_for(category_slug: str, d: int) -> str | None:
    """Name the notification tier for `d` days remaining, or None when untiered.

    Reads the live category data; returns None for an expired date (`d < 0`)
    and for a category that declares no windows. Beyond the widest window the
    tier is `"safe"`.
    """
    category = CATEGORIES.get(category_slug)
    if category is None or not category.tier_defaults:
        return None
    if d < 0:
        return None
    for tier, days in sorted(category.tier_defaults.items(), key=lambda item: item[1]):
        if d <= days:
            return tier
    return "safe"


def bucket_for(d: int) -> str:
    """Fixed urgency bucket for `d` days remaining."""
    if d < 0:
        return "expired"
    if d <= 7:
        return "this-week"
    if d <= 30:
        return "this-month"
    return "safe"


def _accepted_classification_slug(db: Session, asset_id: str) -> str | None:
    assertion = (
        db.query(Assertion)
        .filter(
            Assertion.asset_id == asset_id,
            Assertion.field_path == CLASSIFICATION_FIELD,
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
    if not isinstance(value, dict):
        return None
    slug = value.get("category")
    return slug if isinstance(slug, str) and slug else None


def _accepted_expiry(db: Session, asset_id: str) -> Assertion | None:
    return (
        db.query(Assertion)
        .filter(
            Assertion.asset_id == asset_id,
            Assertion.field_path == EXPIRY_FIELD,
            Assertion.review_state == "accepted",
        )
        .order_by(Assertion.created_at.desc())
        .first()
    )


def _latest_active_expiry(db: Session, asset_id: str) -> Assertion | None:
    return (
        db.query(Assertion)
        .filter(
            Assertion.asset_id == asset_id,
            Assertion.field_path == EXPIRY_FIELD,
            Assertion.review_state.not_in(("superseded", "rejected")),
        )
        .order_by(Assertion.created_at.desc())
        .first()
    )


def _parse_expiry_value(value_json: str) -> tuple[date, str | None] | None:
    try:
        value = json.loads(value_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    raw = value.get("expiry_date")
    if not isinstance(raw, str):
        return None
    try:
        expiry = date.fromisoformat(raw)
    except ValueError:
        return None
    if expiry.isoformat() != raw:
        return None
    date_type = value.get("date_type")
    return expiry, (date_type if isinstance(date_type, str) else None)


def _unresolved_reason(db: Session, asset_id: str) -> str:
    latest = _latest_active_expiry(db, asset_id)
    if latest is None:
        return "dateless"
    if latest.review_state == "proposed":
        return "proposed"
    if latest.review_state == "needs_evidence":
        return "needs_evidence"
    return "dateless"


def compute_status(
    db: Session, household_id: str, as_of: date, category: str | None = None
) -> dict[str, Any]:
    """Urgency-sorted expiry status for one household, read-only.

    `category` narrows to a canonical slug; a slug that matches nothing (or is
    unknown) yields an empty 200-shaped result, never a fallback to unfiltered.
    """
    rows: list[dict[str, Any]] = []
    unresolved_rows: list[dict[str, Any]] = []
    # SG-111 ISS-2: the engine admits ACTIVE assets only. A non-ACTIVE asset is
    # lifecycle-terminal, not date-missing, so it is excluded from BOTH the
    # tiered rows and the unresolved rows (the dashboard needs no change).
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
        if category is not None and slug != category:
            continue
        accepted = _accepted_expiry(db, asset.id)
        if accepted is not None:
            parsed = _parse_expiry_value(accepted.value_json)
            if parsed is None:
                unresolved_rows.append({"asset_id": asset.id, "reason": "unparseable"})
                continue
            expiry, date_type = parsed
            d = days_remaining(expiry, as_of)
            rows.append(
                {
                    "asset_id": asset.id,
                    "display_name": asset.display_name,
                    "category": slug,
                    "expiry_date": expiry.isoformat(),
                    "date_type": date_type,
                    "days_remaining": d,
                    "tier": tier_for(slug, d),
                    "bucket": bucket_for(d),
                }
            )
            continue
        unresolved_rows.append(
            {"asset_id": asset.id, "reason": _unresolved_reason(db, asset.id)}
        )

    rows.sort(key=lambda row: (row["days_remaining"], row["asset_id"]))
    unresolved_rows.sort(key=lambda row: row["asset_id"])

    by_bucket: dict[str, int] = {}
    by_tier: dict[str, int] = {}
    for row in rows:
        by_bucket[row["bucket"]] = by_bucket.get(row["bucket"], 0) + 1
        tier_key = row["tier"] or "none"
        by_tier[tier_key] = by_tier.get(tier_key, 0) + 1

    return {
        "household_id": household_id,
        "as_of": as_of.isoformat(),
        "category": category,
        "rows": rows,
        "summary": {
            "by_tier": by_tier,
            "by_bucket": by_bucket,
            "unresolved": len(unresolved_rows),
            "total": len(rows) + len(unresolved_rows),
        },
        "unresolved_rows": unresolved_rows,
    }
