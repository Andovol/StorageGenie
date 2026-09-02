import json

from sqlalchemy.orm import Session

from app.models.assertion import Assertion
from app.services import audit_service


def upsert_assertion(
    db: Session,
    asset_id: str,
    field_path: str,
    value: object,
    household_id: str,
    source_type: str = "user",
    source_evidence_ids: list[str] | None = None,
    confidence: float | None = None,
) -> Assertion:
    prev = (
        db.query(Assertion)
        .filter_by(asset_id=asset_id, field_path=field_path, review_state="accepted")
        .first()
    )
    if prev:
        prev.review_state = "superseded"
    new = Assertion(
        asset_id=asset_id,
        field_path=field_path,
        value_json=json.dumps(value),
        source_type=source_type,
        review_state="accepted",
        confidence=confidence,
        source_evidence_ids=json.dumps(source_evidence_ids) if source_evidence_ids else None,
    )
    db.add(new)
    db.flush()
    audit_service.record(
        db,
        actor="api",
        action="assertion.upsert",
        entity_type="assertion",
        entity_id=new.id,
        before={"field_path": field_path, "previous_review_state": "superseded" if prev else None},
        after={"field_path": field_path, "value": value},
        household_id=household_id,
    )
    return new


def get_assertions_for_asset(db: Session, asset_id: str) -> list[Assertion]:
    return db.query(Assertion).filter_by(asset_id=asset_id).order_by(Assertion.field_path).all()
