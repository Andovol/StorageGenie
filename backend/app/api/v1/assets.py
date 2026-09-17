import json
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import Query as OrmQuery, Session

from app.db import get_db
from app.models.assertion import Assertion
from app.models.audit_event import AuditEvent
from app.models.asset import Asset
from app.models.evidence import Evidence, asset_evidence
from app.models.household import Household
from app.models.saved_search import SavedSearch
from app.schemas.asset import AssetCreate, AssetUpdate
from app.schemas.common import decode_cursor, encode_cursor, loads_json
from app.schemas.saved_search import SAVED_SEARCH_QUERY_MAX_BYTES, SavedSearchCreate
from app.services import audit_service
from app.plugins.registry import iter_plugins
from app.services.asset_service import attach_evidence, create_asset, update_asset
from app.services.fts import ensure_asset_fts, sanitize_fts_query

router = APIRouter()


@router.get("/taxonomy")
def get_taxonomy() -> dict[str, object]:
    """The registered plugins' taxonomy descriptors (SG-065, read-only).

    Reflection over the REAL registry: defining a new domain is a registration,
    not a migration. A plugin registered without a descriptor is skipped; a
    descriptor with an empty category map serves ``categories: []`` (graceful).
    """
    plugins: list[dict[str, object]] = []
    for registered in iter_plugins():
        taxonomy = registered.taxonomy
        if taxonomy is None:
            continue
        plugins.append(
            {
                "plugin_id": taxonomy.plugin_id,
                "version": taxonomy.version,
                "categories": [
                    {
                        "id": category.id,
                        "name": category.name,
                        "active": category.active,
                        "notification": category.behavior.notification,
                        "opened_date_tracking": category.behavior.opened_date_tracking,
                        "chat": category.behavior.chat,
                    }
                    for category in taxonomy.categories
                ],
                "date_types": list(taxonomy.date_types),
                "units": list(taxonomy.units),
            }
        )
    return {"plugins": plugins}


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
    # Evidence: Join Evidence and asset_evidence to fetch linked evidence in a single query
    evs = (
        db.query(Evidence)
        .join(asset_evidence, Evidence.id == asset_evidence.c.evidence_id)
        .filter(asset_evidence.c.asset_id == asset.id)
        .all()
    )
    evidence = [
        {
            "id": e.id,
            "sha256": e.sha256,
            "media_type": e.media_type,
            "storage_key": e.storage_key,
            "original_filename": e.original_filename,
            "size_bytes": e.size_bytes,
        }
        for e in evs
    ]
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


def _apply_asset_filters(
    query: OrmQuery[Asset],
    db: Session,
    *,
    q: str | None,
    asset_type: str | None,
    status: str | None,
    has_evidence: bool | None,
) -> OrmQuery[Asset]:
    """The ONE filter set shared by `list_assets` and `asset_facets`.

    `asset_facets` calls it once per dimension with that dimension's own
    argument set to `None`, so a pill always shows the counts reachable by
    selecting it rather than only-the-selected-zero.
    """
    if q:
        # MATCH is deliberately narrowed before the other filters are applied.
        ensure_asset_fts(db.connection())
        fts_ids = (
            select(text("asset_id"))
            .select_from(text("asset_fts"))
            .where(text("asset_fts MATCH :fts_query"))
            .params(fts_query=sanitize_fts_query(q))
        )
        query = query.filter(Asset.id.in_(fts_ids))
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if status:
        query = query.filter(Asset.status == status)
    if has_evidence is not None:
        if has_evidence:
            query = query.filter(Asset.id.in_(db.query(asset_evidence.c.asset_id)))
        else:
            query = query.filter(~Asset.id.in_(db.query(asset_evidence.c.asset_id)))
    return query


def _facet_queries(
    db: Session,
    household_id: str,
    *,
    q: str | None,
    asset_type: str | None,
    status: str | None,
    has_evidence: bool | None,
) -> dict[str, OrmQuery[Any]]:
    """Build (never execute) the aggregate query for each analyzed dimension.

    Each dimension omits its OWN filter: `asset_type` counts ignore the
    `asset_type` argument, `status` counts ignore `status`, and the
    `has_evidence` base ignores `has_evidence`. Kept separate from execution so
    the SQL compiles under a PostgreSQL dialect in the test (dialect-neutral
    `count(*)` + `group_by` / subquery; no SQLite-only function).
    """
    base: OrmQuery[Any] = db.query(Asset).filter(Asset.household_id == household_id)
    return {
        "asset_type": _apply_asset_filters(
            base, db, q=q, asset_type=None, status=status, has_evidence=has_evidence
        )
        .with_entities(Asset.asset_type, func.count())
        .group_by(Asset.asset_type),
        "status": _apply_asset_filters(
            base, db, q=q, asset_type=asset_type, status=None, has_evidence=has_evidence
        )
        .with_entities(Asset.status, func.count())
        .group_by(Asset.status),
        "has_evidence": _apply_asset_filters(
            base, db, q=q, asset_type=asset_type, status=status, has_evidence=None
        ),
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
    # The outer Asset query keeps the established serializer, ordering, and
    # cursor envelope unchanged. The same filter set backs `asset_facets`.
    query = _apply_asset_filters(
        query,
        db,
        q=q,
        asset_type=asset_type,
        status=status,
        has_evidence=has_evidence,
    )
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
    # SG-064 G3: the catalog card reads the first evidence id to build its
    # thumbnail; the list serializer previously sent no evidence field at all, so
    # that thumbnail (the "evidence badge") could never render from the live API.
    asset_ids = [a.id for a in items]
    evidence_ids_by_asset: dict[str, list[str]] = {}
    if asset_ids:
        for row in db.execute(
            asset_evidence.select().where(asset_evidence.c.asset_id.in_(asset_ids))
        ).fetchall():
            evidence_ids_by_asset.setdefault(row.asset_id, []).append(row.evidence_id)
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
                "evidence_ids": evidence_ids_by_asset.get(a.id, []),
            }
            for a in items
        ],
        "next_cursor": next_cursor,
    }


@router.get("/assets/facets")
def asset_facets(
    household_id: str = Query(...),
    q: str | None = Query(default=None),
    asset_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    has_evidence: bool | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict[str, dict[str, int]]:
    """Catalog facet counts per analyzed dimension (Phase 4 "advanced filters").

    Declared before `/assets/{asset_id}` so the literal path is not captured as
    an asset id. Same base filters as `list_assets`; each dimension's counts
    omit that dimension's own filter. Keys are sorted; counts are integers.
    """
    queries = _facet_queries(
        db, household_id, q=q, asset_type=asset_type, status=status, has_evidence=has_evidence
    )
    asset_type_counts = {str(key): int(count) for key, count in queries["asset_type"].all()}
    status_counts = {str(key): int(count) for key, count in queries["status"].all()}
    # Zero-population (PG-SC-07): an empty base yields empty maps, not an error.
    # `has_evidence` carries its fixed `with`/`without` keys only when at least
    # one row is reachable (otherwise there is no polarity to report).
    has_evidence_counts: dict[str, int] = {}
    if status_counts:
        evidence_base = queries["has_evidence"]
        with_evidence = evidence_base.filter(
            Asset.id.in_(db.query(asset_evidence.c.asset_id))
        ).count()
        without_evidence = evidence_base.filter(
            ~Asset.id.in_(db.query(asset_evidence.c.asset_id))
        ).count()
        has_evidence_counts = {
            "with": int(with_evidence),
            "without": int(without_evidence),
        }
    return {
        "asset_type": dict(sorted(asset_type_counts.items())),
        "status": dict(sorted(status_counts.items())),
        "has_evidence": has_evidence_counts,
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


@router.post("/assets/{asset_id}/events", status_code=201)
def post_asset_event(
    asset_id: str,
    payload: dict[str, object],
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    asset = db.query(Asset).filter_by(id=asset_id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    event_type = payload.get("type") or payload.get("event_type")
    if not isinstance(event_type, str) or not event_type or "." in event_type or " " in event_type:
        raise HTTPException(status_code=422, detail="event type must be a non-empty name")
    audit_service.record(
        db,
        actor="api",
        action=f"asset.lifecycle.{event_type}",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after=payload,
        household_id=asset.household_id,
    )
    db.commit()
    return {"asset_id": asset.id, "action": f"asset.lifecycle.{event_type}"}


def _saved_search_to_dict(row: SavedSearch) -> dict[str, Any]:
    """Read a saved search back as the exact filter dict the list endpoint takes."""
    return {
        "id": row.id,
        "household_id": row.household_id,
        "name": row.name,
        "query": loads_json(row.query_json) or {},
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.post("/saved-searches", status_code=201)
def create_saved_search(
    payload: SavedSearchCreate,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Persist a named filter set for one household (SG-068 G1).

    The query is serialized with its ``None`` fields dropped, so a saved row
    reads back as exactly the parameters the catalog would have sent. Unknown
    keys, wrong value types, an oversize name and an oversize query are all
    visible 422s (PG-SC-05 / PG-SC-06); a duplicate name is a 409.
    """
    if db.query(Household).filter_by(id=household_id).first() is None:
        raise HTTPException(status_code=404, detail="Household not found")
    serialized = json.dumps(
        payload.query.model_dump(exclude_none=True), sort_keys=True, ensure_ascii=False
    )
    if len(serialized.encode("utf-8")) > SAVED_SEARCH_QUERY_MAX_BYTES:
        raise HTTPException(
            status_code=422,
            detail=f"query exceeds the {SAVED_SEARCH_QUERY_MAX_BYTES} byte saved-search cap",
        )
    duplicate = (
        db.query(SavedSearch)
        .filter(SavedSearch.household_id == household_id)
        .filter(func.lower(SavedSearch.name) == payload.name.lower())
        .first()
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=409,
            detail="A saved search with that name already exists for this household",
        )
    row = SavedSearch(household_id=household_id, name=payload.name, query_json=serialized)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _saved_search_to_dict(row)


@router.get("/saved-searches")
def list_saved_searches(
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Newest first; a household with none returns an empty list, never an error."""
    rows = (
        db.query(SavedSearch)
        .filter(SavedSearch.household_id == household_id)
        .order_by(SavedSearch.created_at.desc(), SavedSearch.id.desc())
        .all()
    )
    return {"items": [_saved_search_to_dict(row) for row in rows]}


@router.delete("/saved-searches/{saved_search_id}")
def delete_saved_search(
    saved_search_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = db.query(SavedSearch).filter_by(id=saved_search_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Saved search not found")
    if row.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    db.delete(row)
    db.commit()
    return {"status": "deleted", "id": saved_search_id}
