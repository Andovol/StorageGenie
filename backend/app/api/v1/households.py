from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.household import Household
from app.models.idempotency import IdempotencyKey
from app.schemas.household import HouseholdCreate, HouseholdOut, HouseholdUpdate

router = APIRouter()


@router.get("/households", response_model=list[HouseholdOut])
def list_households(db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    return db.query(Household).order_by(Household.created_at).all()


@router.post("/households", response_model=HouseholdOut, status_code=201)
def create_household(
    payload: HouseholdCreate,
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):  # type: ignore[no-untyped-def]
    if idempotency_key:
        existing = db.query(IdempotencyKey).filter_by(key=idempotency_key).first()
        if existing and existing.response_json:
            import json

            data = json.loads(existing.response_json)
            # Return existing household id
            h = db.query(Household).filter_by(id=data["id"]).first()
            if h:
                return h
    h = Household(name=payload.name)
    db.add(h)
    db.commit()
    db.refresh(h)
    if idempotency_key:
        import json

        ik = IdempotencyKey(key=idempotency_key, response_json=json.dumps({"id": h.id}))
        db.add(ik)
        try:
            db.commit()
        except Exception:
            db.rollback()
    return h


@router.get("/households/{household_id}", response_model=HouseholdOut)
def get_household(household_id: str, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    h = db.query(Household).filter_by(id=household_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Household not found")
    return h


@router.patch("/households/{household_id}", response_model=HouseholdOut)
def patch_household(
    household_id: str, payload: HouseholdUpdate, db: Session = Depends(get_db)  # type: ignore[no-untyped-def]
):  # type: ignore[no-untyped-def]
    h = db.query(Household).filter_by(id=household_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Household not found")
    if payload.name is not None:
        h.name = payload.name
    db.commit()
    db.refresh(h)
    return h
