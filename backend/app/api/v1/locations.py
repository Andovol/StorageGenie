"""SG-113 location tree API — DORMANT behind `settings.sg_locations_enabled`.

Every route here is gated by the router-level dependency: with the flag OFF
(the default, and the state production ships in until the owner's migrate +
flip + recreate word) each route answers 404, so undeployed schema can never be
exercised. Seed names such as fridge/freezer are never pre-created and never
trusted as the set — creation is explicit rows only.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.asset import Asset
from app.models.household import Household
from app.models.location import Location, asset_location


def _require_locations_enabled() -> None:
    if not settings.sg_locations_enabled:
        raise HTTPException(status_code=404, detail="Not Found")


router = APIRouter(dependencies=[Depends(_require_locations_enabled)])


class LocationCreate(BaseModel):
    name: str
    parent_id: str | None = None

    @field_validator("name")
    @classmethod
    def _name_non_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("name must be a non-empty name")
        if len(stripped) > 200:
            raise ValueError("name must be 200 characters or fewer")
        return stripped


class LocationUpdate(BaseModel):
    name: str | None = None
    parent_id: str | None = None

    @field_validator("name")
    @classmethod
    def _name_non_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("name must be a non-empty name")
        if len(stripped) > 200:
            raise ValueError("name must be 200 characters or fewer")
        return stripped


class AssignLocationRequest(BaseModel):
    location_id: str


def _location_to_dict(location: Location) -> dict[str, object]:
    return {
        "id": location.id,
        "household_id": location.household_id,
        "name": location.name,
        "parent_id": location.parent_id,
        "created_at": location.created_at.isoformat() if location.created_at else None,
        "updated_at": location.updated_at.isoformat() if location.updated_at else None,
    }


def _get_location(db: Session, location_id: str, household_id: str) -> Location:
    location = db.query(Location).filter_by(id=location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    if location.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return location


def _get_asset(db: Session, asset_id: str, household_id: str) -> Asset:
    asset = db.query(Asset).filter_by(id=asset_id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return asset


def _parent_in_household(db: Session, parent_id: str, household_id: str) -> Location:
    parent = db.query(Location).filter_by(id=parent_id).first()
    if parent is None:
        raise HTTPException(status_code=404, detail="Parent location not found")
    if parent.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return parent


def _would_cycle(db: Session, location: Location, new_parent_id: str) -> bool:
    """True when reparenting `location` under `new_parent_id` closes a loop.

    Walks the proposed parent's ancestor chain; the location itself (or any
    descendant, which appears as an ancestor of the proposed parent) means the
    move would create a cycle. A pre-existing loop is also refused defensively.
    """
    cursor: str | None = new_parent_id
    seen: set[str] = set()
    while cursor is not None:
        if cursor == location.id or cursor in seen:
            return True
        seen.add(cursor)
        parent = db.query(Location).filter_by(id=cursor).first()
        if parent is None:
            break
        cursor = parent.parent_id
    return False


@router.get("/locations")
def list_locations(
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """A household with no locations returns an empty list, never an error."""
    rows = (
        db.query(Location)
        .filter(Location.household_id == household_id)
        .order_by(Location.name, Location.id)
        .all()
    )
    return {"items": [_location_to_dict(row) for row in rows]}


@router.post("/locations", status_code=201)
def create_location(
    payload: LocationCreate,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if db.query(Household).filter_by(id=household_id).first() is None:
        raise HTTPException(status_code=404, detail="Household not found")
    if payload.parent_id is not None:
        _parent_in_household(db, payload.parent_id, household_id)
    location = Location(
        household_id=household_id, name=payload.name, parent_id=payload.parent_id
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return _location_to_dict(location)


@router.patch("/locations/{location_id}")
def update_location(
    location_id: str,
    payload: LocationUpdate,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    location = _get_location(db, location_id, household_id)
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=422, detail="No fields to update")
    if "name" in data:
        if data["name"] is None:
            raise HTTPException(status_code=422, detail="name must be a non-empty name")
        location.name = data["name"]
    if "parent_id" in data:
        new_parent_id = data["parent_id"]
        if new_parent_id is not None:
            if new_parent_id == location.id:
                raise HTTPException(
                    status_code=422, detail="a location cannot be its own parent"
                )
            _parent_in_household(db, new_parent_id, household_id)
            if _would_cycle(db, location, new_parent_id):
                raise HTTPException(
                    status_code=422, detail="reparenting would create a cycle"
                )
        location.parent_id = new_parent_id
    db.commit()
    db.refresh(location)
    return _location_to_dict(location)


@router.delete("/locations/{location_id}")
def delete_location(
    location_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Empty-only delete. A location holding assets (409) or children (409) is
    never cascade-emptied silently; reassign or delete the dependants first."""
    location = _get_location(db, location_id, household_id)
    assigned = (
        db.query(asset_location)
        .filter(asset_location.c.location_id == location.id)
        .count()
    )
    if assigned:
        raise HTTPException(status_code=409, detail="Location has assigned assets")
    children = db.query(Location).filter(Location.parent_id == location.id).count()
    if children:
        raise HTTPException(status_code=409, detail="Location has child locations")
    deleted_id = location.id
    db.delete(location)
    db.commit()
    return {"status": "deleted", "id": deleted_id}


@router.post("/assets/{asset_id}/locations")
def assign_asset_location(
    asset_id: str,
    payload: AssignLocationRequest,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Assign an asset to a location; a repeat assign is an idempotent no-op."""
    _get_asset(db, asset_id, household_id)
    _get_location(db, payload.location_id, household_id)
    existing = db.execute(
        asset_location.select().where(
            asset_location.c.asset_id == asset_id,
            asset_location.c.location_id == payload.location_id,
        )
    ).first()
    if existing is None:
        db.execute(
            asset_location.insert().values(asset_id=asset_id, location_id=payload.location_id)
        )
        db.commit()
    return {"status": "assigned", "asset_id": asset_id, "location_id": payload.location_id}


@router.delete("/assets/{asset_id}/locations/{location_id}")
def unassign_asset_location(
    asset_id: str,
    location_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Remove an assignment; a repeat unassign is an idempotent no-op."""
    _get_asset(db, asset_id, household_id)
    _get_location(db, location_id, household_id)
    db.execute(
        asset_location.delete().where(
            asset_location.c.asset_id == asset_id,
            asset_location.c.location_id == location_id,
        )
    )
    db.commit()
    return {"status": "unassigned", "asset_id": asset_id, "location_id": location_id}
