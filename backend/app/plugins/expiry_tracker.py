"""The deterministic Expiry Tracker 1.0.0 domain contract.

This module contains data and validation only. In particular, it never derives a
date from the clock or from a shelf-life guess. A resolved expiry date is a
manual user assertion; an observed date can remain proposed pending review.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.assertion import Assertion
from app.models.evidence import asset_evidence
from app.models.review_task import ReviewTask
from app.services import audit_service
from app.services.observations import Observation
from app.services.providers.schemas import ExtractionOutput

PLUGIN_ID = "expiry-tracker"
PLUGIN_VERSION = "1.0.0"
FIELD_PREFIX = "plugin:expiry-tracker/"
CLASSIFICATION_FIELD = f"{FIELD_PREFIX}classification"
EXPIRY_FIELD = f"{FIELD_PREFIX}expiry_date"
EXTENSION_PREFIX = f"{FIELD_PREFIX}extension/"


class DateType(StrEnum):
    EXPIRY_DATE = "expiry_date"
    BEST_BEFORE = "best_before"
    USE_BY = "use_by"
    MANUFACTURE_DATE = "manufacture_date"
    PERIOD_AFTER_OPENING = "period_after_opening"
    BATCH_LOT_CODE = "batch_lot_code"


class Unit(StrEnum):
    PIECE = "piece"
    UNIT = "unit"
    ML = "ml"
    L = "l"
    G = "g"
    KG = "kg"
    DOSE = "dose"
    TABLET = "tablet"
    APPLICATION = "application"


class NotificationTier(StrEnum):
    CRITICAL = "critical"
    URGENT = "urgent"
    UPCOMING = "upcoming"
    LONG_LEAD = "long_lead"


@dataclass(frozen=True)
class Category:
    slug: str
    label: str
    active: bool
    has_expiry: bool
    tier_defaults: dict[str, int]
    default_tier: str
    phase: str | None = None

    def profile(self, tier: str | None = None) -> dict[str, Any]:
        if not self.tier_defaults:
            return {
                "notification_tier": None,
                "notification_days": None,
                "tier_defaults": {},
                "opened_date_tracking": False,
                "disposal_guidance": False,
            }
        selected = tier or self.default_tier
        if selected not in self.tier_defaults:
            raise ValueError(f"Unknown notification tier: {selected}")
        return {
            "notification_tier": selected,
            "notification_days": self.tier_defaults[selected],
            "tier_defaults": dict(self.tier_defaults),
            "opened_date_tracking": False,
            "disposal_guidance": self.slug in {"food_beverages", "medicine_pharma"},
        }


FOOD_TIERS = {
    NotificationTier.CRITICAL.value: 1,
    NotificationTier.URGENT.value: 7,
    NotificationTier.UPCOMING.value: 30,
}
MEDICINE_TIERS = {
    NotificationTier.CRITICAL.value: 1,
    NotificationTier.URGENT.value: 3,
    NotificationTier.UPCOMING.value: 14,
}

CATEGORIES: dict[str, Category] = {
    "food_beverages": Category(
        "food_beverages", "Food & beverages", True, True, FOOD_TIERS, NotificationTier.UPCOMING.value
    ),
    "medicine_pharma": Category(
        "medicine_pharma", "Medicine/pharma", True, True, MEDICINE_TIERS, NotificationTier.UPCOMING.value
    ),
    "cosmetics_personal_care": Category(
        "cosmetics_personal_care", "Cosmetics/personal care", False, True, {}, "", "Phase 3"
    ),
    "household_chemicals": Category(
        "household_chemicals", "Household chemicals", False, True, {}, "", "Phase 3"
    ),
    "documents_other": Category(
        "documents_other", "Documents/other", False, False, {}, "", "Phase 3"
    ),
    "non_perishable": Category("non_perishable", "Non-perishable", True, False, {}, ""),
}

_CATEGORY_ALIASES = {
    "food": "food_beverages",
    "food and beverages": "food_beverages",
    "food & beverages": "food_beverages",
    "food-beverages": "food_beverages",
    "medicine": "medicine_pharma",
    "medicine/pharma": "medicine_pharma",
    "pharma": "medicine_pharma",
    "cosmetics": "cosmetics_personal_care",
    "cosmetics/personal care": "cosmetics_personal_care",
    "household": "household_chemicals",
    "household chemicals": "household_chemicals",
    "documents": "documents_other",
    "documents/other": "documents_other",
    "non-perishable": "non_perishable",
    "nonperishable": "non_perishable",
}

EXTENSION_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "storage_location": {"type": "string", "enum": ["fridge", "freezer", "pantry", "bathroom_cabinet", "medicine_cabinet", "garage_utility", "custom"]},
        "notification_tier": {"type": "string", "enum": [tier.value for tier in NotificationTier]},
        "unit": {"type": "string", "enum": [unit.value for unit in Unit]},
        "quantity": {"type": "number"},
        "batch_lot_code": {"type": "string", "minLength": 1},
    },
}

_DATE_ALIASES = {
    "expiry": DateType.EXPIRY_DATE.value,
    "best-before": DateType.BEST_BEFORE.value,
    "use-by": DateType.USE_BY.value,
    "manufacture": DateType.MANUFACTURE_DATE.value,
    "pao": DateType.PERIOD_AFTER_OPENING.value,
    "batch-lot": DateType.BATCH_LOT_CODE.value,
}


class ExpiryValidationError(ValueError):
    pass


def canonical_category(value: object) -> Category:
    if not isinstance(value, str):
        raise ExpiryValidationError("category must be a string")
    key = value.strip().lower().replace("_", " ")
    slug = _CATEGORY_ALIASES.get(key, value.strip().lower())
    category = CATEGORIES.get(slug)
    if category is None:
        raise ExpiryValidationError(f"Unknown expiry-tracker category: {value}")
    if not category.active:
        raise ExpiryValidationError(
            f"Category {category.label} is inactive until {category.phase}"
        )
    return category


def canonical_date_type(value: object) -> str:
    if not isinstance(value, str):
        raise ExpiryValidationError("date_type must be one of the expiry-tracker date types")
    normalized = _DATE_ALIASES.get(value.strip().lower(), value.strip().lower())
    if normalized not in {item.value for item in DateType}:
        raise ExpiryValidationError(f"Invalid date_type: {value}")
    return normalized


def canonical_unit(value: object) -> str:
    if not isinstance(value, str) or value.strip().lower() not in {item.value for item in Unit}:
        raise ExpiryValidationError(f"Invalid unit: {value}")
    return value.strip().lower()


def validate_extension_attributes(attributes: object) -> dict[str, object]:
    if not isinstance(attributes, dict):
        raise ExpiryValidationError("extension attributes must be an object")
    core_fields = {"identifier", "condition", "location", "status"}
    for key in attributes:
        if key in core_fields:
            raise ExpiryValidationError(f"Extension cannot override core field: {key}")
        if key not in EXTENSION_SCHEMA["properties"]:
            raise ExpiryValidationError(f"Unsupported extension attribute: {key}")
    result: dict[str, object] = {}
    for key, value in attributes.items():
        schema = EXTENSION_SCHEMA["properties"][key]
        if schema["type"] == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))):
            raise ExpiryValidationError(f"Extension attribute {key} must be a number")
        if schema["type"] == "string" and not isinstance(value, str):
            raise ExpiryValidationError(f"Extension attribute {key} must be a string")
        if "enum" in schema and value not in schema["enum"]:
            raise ExpiryValidationError(f"Invalid {key}: {value}")
        if schema.get("minLength") and isinstance(value, str) and not value:
            raise ExpiryValidationError(f"Extension attribute {key} must not be empty")
        result[key] = value
    return result


def parse_manual_entry(payload: dict[str, object]) -> dict[str, object]:
    raw_value = payload.get("expiry_date", payload.get("date"))
    if not isinstance(raw_value, str):
        raise ExpiryValidationError("expiry_date is required as YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ExpiryValidationError("expiry_date must be a valid YYYY-MM-DD date") from exc
    if parsed.isoformat() != raw_value:
        raise ExpiryValidationError("expiry_date must use YYYY-MM-DD format")
    result: dict[str, object] = {
        "expiry_date": raw_value,
        "date_type": canonical_date_type(payload.get("date_type", DateType.EXPIRY_DATE.value)),
    }
    if "unit" in payload:
        result["unit"] = canonical_unit(payload["unit"])
    return result


_DATE_PATTERN = re.compile(r"\b(20\d{2})[-/:](\d{1,2})[-/:](\d{1,2})\b")


def _observed_date(db: Session, asset: Asset) -> tuple[str, list[str]] | None:
    links = db.execute(asset_evidence.select().where(asset_evidence.c.asset_id == asset.id)).fetchall()
    evidence_ids = [row.evidence_id for row in links]
    if not evidence_ids:
        return None
    rows = (
        db.query(Observation)
        .filter(
            Observation.evidence_id.in_(evidence_ids),
            Observation.kind.in_(("ocr", "barcode_qr")),
        )
        .all()
    )
    for row in rows:
        try:
            value = json.loads(row.value_json)
        except json.JSONDecodeError:
            continue
        text = json.dumps(value, ensure_ascii=False)
        match = _DATE_PATTERN.search(text)
        if match:
            candidate = "-".join(match.groups())
            try:
                if date.fromisoformat(candidate):
                    return candidate, [row.evidence_id]
            except ValueError:
                continue
    return None


def _active_assertion(db: Session, asset_id: str, field_path: str) -> Assertion | None:
    return (
        db.query(Assertion)
        .filter(
            Assertion.asset_id == asset_id,
            Assertion.field_path == field_path,
            Assertion.review_state.not_in(("superseded", "rejected")),
        )
        .order_by(Assertion.created_at.desc())
        .first()
    )


def _write_assertion(
    db: Session,
    asset: Asset,
    field_path: str,
    value: object,
    source_type: str,
    review_state: str,
    evidence_ids: list[str] | None,
) -> Assertion:
    previous = _active_assertion(db, asset.id, field_path)
    if previous is not None:
        if previous.review_state == review_state and json.loads(previous.value_json) == value:
            return previous
        previous.review_state = "superseded"
    assertion = Assertion(
        asset_id=asset.id,
        field_path=field_path,
        value_json=json.dumps(value, ensure_ascii=False),
        source_type=source_type,
        review_state=review_state,
        source_evidence_ids=json.dumps(evidence_ids) if evidence_ids else None,
    )
    db.add(assertion)
    db.flush()
    audit_service.record(
        db,
        actor="expiry-tracker",
        action="plugin.assertion.write",
        entity_type="assertion",
        entity_id=assertion.id,
        before={"field_path": field_path, "review_state": previous.review_state if previous else None},
        after={"field_path": field_path, "review_state": review_state, "value": value},
        household_id=asset.household_id,
    )
    return assertion


def _manual_task(db: Session, asset: Asset) -> ReviewTask:
    task = (
        db.query(ReviewTask)
        .filter_by(
            subject_ref=asset.id,
            household_id=asset.household_id,
            task_type="expiry.manual_entry",
            status="open",
        )
        .first()
    )
    if task is not None:
        return task
    task = ReviewTask(
        task_type="expiry.manual_entry",
        priority="high",
        subject_ref=asset.id,
        proposed_change=json.dumps({"field_path": EXPIRY_FIELD, "prompt": "Enter expiry date manually"}),
        status="open",
        household_id=asset.household_id,
    )
    db.add(task)
    db.flush()
    return task


def apply_extraction_result(
    db: Session, asset: Asset, result: ExtractionOutput
) -> tuple[Assertion | None, ReviewTask | None]:
    """Map a validated extraction output onto the EXISTING manual-entry path.

    Callable mapping only — not a job step, no pipeline changes (SG-028 owns
    wiring). When the output carries needs_evidence, this writes the SAME
    assertion kind classify_asset writes for a dateless asset (EXPIRY_FIELD,
    {"status": "unknown"}, review_state "needs_evidence") and opens the SAME
    "expiry.manual_entry" task via _manual_task — no new task type.
    source_type is "extraction" (not classify's "deterministic") so provenance
    stays honest. Outputs without needs_evidence map to (None, None): nothing
    written, no task opened.
    """
    if not result.needs_evidence:
        return None, None
    assertion = _write_assertion(
        db,
        asset,
        EXPIRY_FIELD,
        {"status": "unknown"},
        "extraction",
        "needs_evidence",
        None,
    )
    return assertion, _manual_task(db, asset)


def classify_asset(db: Session, asset: Asset, category: Category, tier: str | None) -> dict[str, object]:
    if tier is not None and tier not in category.tier_defaults:
        raise ExpiryValidationError(f"Invalid notification_tier: {tier}")
    profile = category.profile(tier)
    classification = {"category": category.slug, "label": category.label, "profile": profile}
    _write_assertion(db, asset, CLASSIFICATION_FIELD, classification, "user", "accepted", None)
    expiry_assertion: Assertion | None = None
    task: ReviewTask | None = None
    observed = _observed_date(db, asset) if category.has_expiry else None
    if category.has_expiry:
        if observed is None:
            expiry_assertion = _write_assertion(
                db, asset, EXPIRY_FIELD, {"status": "unknown"}, "deterministic", "needs_evidence", None
            )
            task = _manual_task(db, asset)
        else:
            expiry_assertion = _write_assertion(
                db,
                asset,
                EXPIRY_FIELD,
                {"expiry_date": observed[0], "date_type": DateType.EXPIRY_DATE.value},
                "deterministic",
                "proposed",
                observed[1],
            )
    return {"classification": classification, "expiry_assertion": expiry_assertion, "review_task": task}


def get_classification(db: Session, asset_id: str) -> Assertion | None:
    return _active_assertion(db, asset_id, CLASSIFICATION_FIELD)


def store_extensions(db: Session, asset: Asset, attributes: dict[str, object]) -> list[Assertion]:
    rows = []
    for key, value in attributes.items():
        rows.append(_write_assertion(db, asset, f"{EXTENSION_PREFIX}{key}", value, "user", "accepted", None))
    return rows


def store_manual_expiry(
    db: Session, asset: Asset, entry: dict[str, object], evidence_ids: list[str] | None
) -> tuple[Assertion, list[ReviewTask]]:
    classification = get_classification(db, asset.id)
    if classification is None:
        raise ExpiryValidationError("Asset must be classified before manual expiry entry")
    category = json.loads(classification.value_json)["category"]
    if not CATEGORIES[category].has_expiry:
        raise ExpiryValidationError("Manual expiry entry is not applicable to non-perishable assets")
    assertion = _write_assertion(
        db, asset, EXPIRY_FIELD, entry, "user", "accepted", evidence_ids
    )
    tasks = (
        db.query(ReviewTask)
        .filter_by(
            subject_ref=asset.id,
            household_id=asset.household_id,
            task_type="expiry.manual_entry",
            status="open",
        )
        .all()
    )
    for task in tasks:
        task.status = "resolved"
    return assertion, tasks
