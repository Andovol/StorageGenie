import json

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.assertion import Assertion
from app.models.audit_event import AuditEvent
from app.models.asset import Asset
from app.models.evidence import Evidence, asset_evidence
from app.schemas.asset import AssetCreate, AssetUpdate
from app.schemas.common import decode_cursor, encode_cursor, loads_json
from app.services.asset_service import attach_evidence, create_asset, update_asset

router = APIRouter()


@router.post("/assets", status_code=201)
def post_asset(
    payload: AssetCreate,
    household_id: str = Query(...),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):  # type: ignore[no-untyped-def]
    # Idempotency: if key exists, return existing asset with same display_name+household?
    # Simplified: check IdempotencyKey table for response id
    if idempotency_key:
        from app.models.idempotency import IdempotencyKey

        existing = db.query(IdempotencyKey).filter_by(key=idempotency_key).first()
        if existing and existing.response_json:
            data = json.loads(existing.response_json)
            a = db.query(Asset).filter_by(id=data["id"]).first()
            if a:
                return _asset_to_dict(a, db)
    a = create_asset(db, household_id, payload.model_dump())
    if idempotency_key:
        from app.models.idempotency import IdempotencyKey

        ik = IdempotencyKey(key=idempotency_key, response_json=json.dumps({"id": a.id}))
        db.add(ik)
        try:
            db.commit()
        except Exception:
            db.rollback()
    return _asset_to_dict(a, db)


def _asset_to_dict(asset: Asset, db: Session) -> dict:  # type: ignore[no-untyped-def]
    # Evidence
    rows = db.execute(
        asset_evidence.select().where(asset_evidence.c.asset_id == asset.id)
    ).fetchall()
    evidence_ids = [r.evidence_id for r in rows]
    evidence = []
    if evidence_ids:
        evs = db.query(Evidence).filter(Evidence.id.in_(evidence_ids)).all()
        for e in evs:
            evidence.append(
                {
                    "id": e.id,
                    "sha256": e.sha256,
                    "media_type": e.media_type,
                    "storage_key": e.storage_key,
                    "original_filename": e.original_filename,
                    "size_bytes": e.size_bytes,
                }
            )
    # Assertions
    assertions = []
    for ass in db.query(Assertion).filter_by(asset_id=asset.id).order_by(Assertion.field_path).all():
        assertions.append(
            {
                "id": ass.id,
                "field_path": ass.field_path,
                "value": loads_json(ass.value_json),
                "source_type": ass.source_type,
                "confidence": ass.confidence,
                "review_state": ass.review_state,
                "source_evidence_ids": loads_json(ass.source_evidence_ids),
                "created_at": ass.created_at.isoformat() if ass.created_at else None,
            }
        )
    audits = []
    for ae in (
        db.query(AuditEvent).filter_by(entity_type="asset", entity_id=asset.id).order_by(AuditEvent.timestamp).all()
    ):
        audits.append(
            {
                "id": ae.id,
                "actor": ae.actor,
                "action": ae.action,
                "before": loads_json(ae.before_json),
                "after": loads_json(ae.after_json),
                "timestamp": ae.timestamp.isoformat() if ae.timestamp else None,
            }
        )
    return {
        "id": asset.id,
        "household_id": asset.household_id,
        "display_name": asset.display_name,
        "asset_type": asset.asset_type,
        "status": asset.status,
        "quantity": asset.quantity,
        "unit": asset.unit,
        "condition": asset.condition,
        "version": asset.version,
        "created_at": asset.created_at.isoformat() if asset.created_at else None,
        "updated_at": asset.updated_at.isoformat() if asset.updated_at else None,
        "evidence": evidence,
        "assertions": assertions,
        "audit_events": audits,
    }


@router.get("/assets")
def list_assets(
    household_id: str = Query(...),
    q: str | None = Query(default=None),
    asset_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    has_evidence: bool | None = Query(default=None),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
):  # type: ignore[no-untyped-def]
    query = db.query(Asset).filter(Asset.household_id == household_id)
    if q:
        query = query.filter(Asset.display_name.ilike(f"%{q}%"))
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if status:
        query = query.filter(Asset.status == status)
    if has_evidence is not None:
        if has_evidence:
            query = query.filter(Asset.id.in_(db.query(asset_evidence.c.asset_id)))
        else:
            query = query.filter(~Asset.id.in_(db.query(asset_evidence.c.asset_id)))
    # Cursor pagination: (created_at, id) descending — use strftime to handle microsecond mismatch (stored without micros)
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded:
            ts, oid = decoded
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            # Compare via strftime to avoid ".000000" mismatch between bound param and CURRENT_TIMESTAMP text
            created_str = func.strftime("%Y-%m-%d %H:%M:%S", Asset.created_at)
            query = query.filter(
                or_(created_str < ts_str, and_(created_str == ts_str, Asset.id < oid))
            )
    query = query.order_by(Asset.created_at.desc(), Asset.id.desc()).limit(limit + 1)
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
                "id": a.id,
                "household_id": a.household_id,
                "display_name": a.display_name,
                "asset_type": a.asset_type,
                "status": a.status,
                "quantity": a.quantity,
                "unit": a.unit,
                "condition": a.condition,
                "version": a.version,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in items
        ],
        "next_cursor": next_cursor,
    }


@router.get("/assets/{asset_id}")
def get_asset(asset_id: str, household_id: str = Query(...), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    a = db.query(Asset).filter_by(id=asset_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Asset not found")
    if a.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return _asset_to_dict(a, db)


@router.patch("/assets/{asset_id}")
def patch_asset(
    asset_id: str,
    payload: AssetUpdate,
    household_id: str = Query(...),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
    if_match: str | None = Header(default=None, alias="If-Match"),
):  # type: ignore[no-untyped-def]
    a = db.query(Asset).filter_by(id=asset_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Asset not found")
    if a.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    if if_match is not None:
        try:
            expected = int(if_match)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid If-Match header")
        if a.version != expected:
            raise HTTPException(status_code=409, detail=f"Version mismatch: expected {expected}, got {a.version}")
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=422, detail="No fields to update")
    a = update_asset(db, a, data)
    return _asset_to_dict(a, db)


@router.delete("/assets/{asset_id}")
def delete_asset(asset_id: str, household_id: str = Query(...), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    a = db.query(Asset).filter_by(id=asset_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Asset not found")
    if a.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    a.status = "ARCHIVED"
    # Assertion for status
    from app.services.assertion_service import upsert_assertion

    upsert_assertion(db, a.id, "status", "ARCHIVED", household_id=a.household_id)
    a.version = (a.version or 1) + 1
    from app.services import audit_service

    audit_service.record(
        db,
        actor="api",
        action="asset.archive",
        entity_type="asset",
        entity_id=a.id,
        before=None,
        after={"status": "ARCHIVED"},
        household_id=a.household_id,
    )
    db.commit()
    return {"status": "archived", "id": a.id}


@router.post("/assets/{asset_id}/evidence")
def post_asset_evidence(
    asset_id: str,
    payload: dict,
    household_id: str = Query(...),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
):  # type: ignore[no-untyped-def]
    a = db.query(Asset).filter_by(id=asset_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Asset not found")
    if a.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    evidence_ids = payload.get("evidence_ids") or []
    if not evidence_ids:
        raise HTTPException(status_code=422, detail="evidence_ids required")
    # Validate evidence belongs to household
    for eid in evidence_ids:
        ev = db.query(Evidence).filter_by(id=eid).first()
        if not ev:
            raise HTTPException(status_code=404, detail=f"Evidence {eid} not found")
        if ev.household_id != household_id:
            raise HTTPException(status_code=403, detail="Evidence household mismatch")
    attach_evidence(db, a, evidence_ids)
    return _asset_to_dict(a, db)
