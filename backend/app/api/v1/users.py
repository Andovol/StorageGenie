from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.household import Household
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter()


@router.get("/households/{household_id}/users", response_model=list[UserOut])
def list_users(household_id: str, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    h = db.query(Household).filter_by(id=household_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Household not found")
    return db.query(User).filter_by(household_id=household_id).order_by(User.created_at).all()


@router.post("/households/{household_id}/users", response_model=UserOut, status_code=201)
def create_user(household_id: str, payload: UserCreate, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    h = db.query(Household).filter_by(id=household_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Household not found")
    u = User(household_id=household_id, display_name=payload.display_name, email=payload.email)
    db.add(u)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    db.refresh(u)
    return u
