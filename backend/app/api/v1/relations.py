"""SG-114 asset-relation API — DORMANT behind `settings.sg_relations_enabled`.

Every route here is gated by the router-level dependency: with the flag OFF
(the default, and the state production ships in until the owner's batched
migrate + flip + recreate word) each route answers 404, so the undeployed
schema can never be exercised. The relation vocabulary is EXACTLY two types —
`related_to` and `contains`; a third type is a new decision, never an
invention here. Duplicate ownership is not a relation: SG-112 already redirects
a materialized duplicate through `MERGED` + `merge.merged_into`, so duplicate
ownership is never a relation type on this surface.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.asset import Asset
from app.models.relation import AssetRelation

# The exact relation vocabulary. `related_to` expresses symmetric intent but is
# STORED once as a directed row; `contains` is directed container -> content.
# Membership is the only gate; the API is the enforcement point (never a DB
# CHECK, so the vocabulary can evolve with a decision rather than a migration).
RELATION_TYPES: frozenset[str] = frozenset({"related_to", "contains"})


def _require_relations_enabled() -> None:
    if not settings.sg_relations_enabled:
        raise HTTPException(status_code=404, detail="Not Found")


router = APIRouter(dependencies=[Depends(_require_relations_enabled)])


class RelationCreate(BaseModel):
    to_asset_id: str
    relation_type: str

    @field_validator("relation_type")
    @classmethod
    def _type_in_vocabulary(cls, value: str) -> str:
        if value not in RELATION_TYPES:
            raise ValueError("relation_type must be one of: contains, related_to")
        return value


def _get_asset(db: Session, asset_id: str, household_id: str) -> Asset:
    asset = db.query(Asset).filter_by(id=asset_id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return asset


def _relation_to_dict(row: AssetRelation, perspective_asset_id: str) -> dict[str, object]:
    """The row plus a `direction` labelled from `perspective_asset_id`.

    A link is readable from BOTH ends: the `from` asset sees `outgoing`, the
    `to` asset sees `incoming`. Direction is derived for the read, never stored.
    """
    return {
        "id": row.id,
        "household_id": row.household_id,
        "from_asset_id": row.from_asset_id,
        "to_asset_id": row.to_asset_id,
        "relation_type": row.relation_type,
        "direction": "outgoing" if row.from_asset_id == perspective_asset_id else "incoming",
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def relations_for_asset(
    db: Session, asset_id: str, household_id: str
) -> list[dict[str, object]]:
    """Both directions: outgoing (`from == asset`) and incoming (`to == asset`).

    Shared by the list route and the asset-detail `relations[]` reader
    (`PG-SC-02`), so the two cannot drift.
    """
    rows = (
        db.query(AssetRelation)
        .filter(
            AssetRelation.household_id == household_id,
            or_(
                AssetRelation.from_asset_id == asset_id,
                AssetRelation.to_asset_id == asset_id,
            ),
        )
        .order_by(AssetRelation.created_at, AssetRelation.id)
        .all()
    )
    return [_relation_to_dict(row, asset_id) for row in rows]


@router.get("/assets/{asset_id}/relations")
def list_relations(
    asset_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """An asset with no links returns an empty list, never an error."""
    _get_asset(db, asset_id, household_id)
    return {"items": relations_for_asset(db, asset_id, household_id)}


@router.post("/assets/{asset_id}/relations", status_code=201)
def create_relation(
    asset_id: str,
    payload: RelationCreate,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Create a typed link with `asset_id` as the directed `from` end.

    Both ends must be assets of the SAME household (404 missing / 403 foreign);
    a self-link is refused 422; an out-of-vocabulary type is refused 422 by the
    request model; the same typed link twice is refused 409 (`PG-SC-12`).
    """
    _get_asset(db, asset_id, household_id)
    if payload.to_asset_id == asset_id:
        raise HTTPException(status_code=422, detail="an asset cannot be related to itself")
    _get_asset(db, payload.to_asset_id, household_id)
    existing = (
        db.query(AssetRelation)
        .filter_by(
            from_asset_id=asset_id,
            to_asset_id=payload.to_asset_id,
            relation_type=payload.relation_type,
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="relation already exists")
    row = AssetRelation(
        household_id=household_id,
        from_asset_id=asset_id,
        to_asset_id=payload.to_asset_id,
        relation_type=payload.relation_type,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _relation_to_dict(row, asset_id)


@router.delete("/assets/{asset_id}/relations/{relation_id}")
def delete_relation(
    asset_id: str,
    relation_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Delete a link. A missing link is an idempotent no-op (200), never a 404;
    a link that exists in another household is 403; a link not touching
    `asset_id` is 404 (the nested path is scoped to this asset)."""
    _get_asset(db, asset_id, household_id)
    row = db.query(AssetRelation).filter_by(id=relation_id).first()
    if row is None:
        return {"status": "deleted", "id": relation_id}
    if row.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    if asset_id not in (row.from_asset_id, row.to_asset_id):
        raise HTTPException(status_code=404, detail="Relation not found")
    db.delete(row)
    db.commit()
    return {"status": "deleted", "id": relation_id}
