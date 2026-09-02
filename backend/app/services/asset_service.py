import json

from sqlalchemy.orm import Session

from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.evidence import asset_evidence
from app.services import audit_service
from app.services.assertion_service import upsert_assertion


def create_asset(
    db: Session,
    household_id: str,
    payload: dict,
    actor: str = "api",
) -> Asset:
    asset = Asset(
        household_id=household_id,
        display_name=payload["display_name"],
        asset_type=payload.get("asset_type", "unknown"),
        status=payload.get("status", "ACTIVE"),
        quantity=payload.get("quantity"),
        unit=payload.get("unit"),
        condition=payload.get("condition"),
    )
    db.add(asset)
    db.flush()
    # Create assertions for each supplied field
    for field in ("display_name", "asset_type", "quantity", "unit", "condition", "status"):
        if field in payload and payload[field] is not None:
            a = Assertion(
                asset_id=asset.id,
                field_path=field,
                value_json=json.dumps(payload[field]),
                source_type="user",
                review_state="accepted",
            )
            db.add(a)
    # Link evidence
    evidence_ids = payload.get("evidence_ids") or []
    for eid in evidence_ids:
        db.execute(asset_evidence.insert().values(asset_id=asset.id, evidence_id=eid))
    audit_service.record(
        db,
        actor=actor,
        action="asset.create",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after=payload,
        household_id=household_id,
    )
    db.commit()
    db.refresh(asset)
    return asset


def update_asset(
    db: Session,
    asset: Asset,
    payload: dict,
    actor: str = "api",
) -> Asset:
    before = {"display_name": asset.display_name, "version": asset.version}
    # Optimistic concurrency handled at API layer; bump version
    for field in ("display_name", "asset_type", "quantity", "unit", "condition", "status"):
        if field in payload:
            setattr(asset, field, payload[field])
            # Assertion supersession
            upsert_assertion(db, asset.id, field, payload[field], asset.household_id)
    asset.version = (asset.version or 1) + 1
    audit_service.record(
        db,
        actor=actor,
        action="asset.update",
        entity_type="asset",
        entity_id=asset.id,
        before=before,
        after=payload,
        household_id=asset.household_id,
    )
    db.commit()
    db.refresh(asset)
    return asset


def attach_evidence(db: Session, asset: Asset, evidence_ids: list[str], actor: str = "api") -> None:
    for eid in evidence_ids:
        # Use INSERT OR IGNORE to avoid duplicate PK error
        try:
            db.execute(asset_evidence.insert().values(asset_id=asset.id, evidence_id=eid))
        except Exception:
            pass
    audit_service.record(
        db,
        actor=actor,
        action="asset.attach_evidence",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after={"evidence_ids": evidence_ids},
        household_id=asset.household_id,
    )
    db.commit()
