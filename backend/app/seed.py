"""Idempotent seed for Phase 0 — household Popescu Household + 2 users."""
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models.household import Household
from app.models.user import User


def seed(db: Session | None = None) -> Household:
    close = False
    if db is None:
        db = SessionLocal()
        close = True
    try:
        h = db.query(Household).filter_by(name=settings.household_default_name).first()
        if h is None:
            h = db.query(Household).first()
        if h is None:
            h = Household(name=settings.household_default_name)
            db.add(h)
            db.commit()
            db.refresh(h)
        # Ensure 2 users
        users = db.query(User).filter_by(household_id=h.id).all()
        if len(users) == 0:
            u1 = User(household_id=h.id, display_name="Andrei", email="andrei@example.com")
            u2 = User(household_id=h.id, display_name="Maria", email="maria@example.com")
            db.add_all([u1, u2])
            db.commit()
        return h
    finally:
        if close:
            db.close()


if __name__ == "__main__":
    h = seed()
    print(f"Seeded household {h.id} name={h.name}")
