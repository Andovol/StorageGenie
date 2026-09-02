from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    storage_status = "ok"
    try:
        Path(settings.storage_root).mkdir(parents=True, exist_ok=True)
    except Exception:
        storage_status = "error"
    return {"status": "ok", "db": db_status, "storage": storage_status}
