import os
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    db_status = "error"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        pass
    else:
        db_status = "ok"

    storage_status = "error"
    storage_root = Path(settings.storage_root)
    if storage_root.is_dir() and os.access(storage_root, os.R_OK | os.W_OK | os.X_OK):
        storage_status = "ok"

    overall_status = "ok" if db_status == storage_status == "ok" else "error"
    status_code = 200 if overall_status == "ok" else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": overall_status, "db": db_status, "storage": storage_status},
    )
