import hashlib
import json

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.evidence import Evidence
from app.models.idempotency import IdempotencyKey
from app.services.evidence_service import EvidenceValidationError, UploadTooLargeError, store_evidence
from app.storage.local_store import absolute_path, thumbnail_path

router = APIRouter()


@router.post("/evidence", status_code=201)
async def upload_evidence(  # noqa: C901
    file: UploadFile = File(...),  # type: ignore[no-untyped-def]
    household_id: str = Query(...),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):  # type: ignore[no-untyped-def]
    if idempotency_key:
        existing = db.query(IdempotencyKey).filter_by(key=idempotency_key).first()
        if existing and existing.response_json:
            data = json.loads(existing.response_json)
            ev = db.query(Evidence).filter_by(id=data["id"]).first()
            if ev:
                return {
                    "id": ev.id,
                    "sha256": ev.sha256,
                    "storage_key": ev.storage_key,
                    "media_type": ev.media_type,
                    "size_bytes": ev.size_bytes,
                    "original_filename": ev.original_filename,
                }
    if not file.filename:
        raise HTTPException(status_code=422, detail="Filename required")
    data = await file.read()
    # Also check sha-based idempotency before storing to reuse same row
    sha = hashlib.sha256(data).hexdigest()
    pre_existing = db.query(Evidence).filter_by(sha256=sha).first()
    if pre_existing:
        ev = pre_existing
    else:
        try:
            ev = store_evidence(
                data, file.filename, file.content_type or "application/octet-stream", household_id, db
            )
        except UploadTooLargeError as e:
            raise HTTPException(status_code=413, detail=str(e))
        except EvidenceValidationError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            # Could be FK violation for household
            raise HTTPException(status_code=422, detail=str(e))
    if idempotency_key:
        ik = IdempotencyKey(key=idempotency_key, response_json=json.dumps({"id": ev.id}))
        db.add(ik)
        try:
            db.commit()
        except Exception:
            db.rollback()
    return {
        "id": ev.id,
        "sha256": ev.sha256,
        "storage_key": ev.storage_key,
        "media_type": ev.media_type,
        "size_bytes": ev.size_bytes,
        "original_filename": ev.original_filename,
    }


@router.get("/evidence/{evidence_id}")
def get_evidence(evidence_id: str, household_id: str = Query(...), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    ev = db.query(Evidence).filter_by(id=evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    if ev.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return {
        "id": ev.id,
        "household_id": ev.household_id,
        "sha256": ev.sha256,
        "media_type": ev.media_type,
        "storage_key": ev.storage_key,
        "original_filename": ev.original_filename,
        "size_bytes": ev.size_bytes,
    }


@router.get("/evidence/{evidence_id}/file")
def get_evidence_file(evidence_id: str, household_id: str = Query(...), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    ev = db.query(Evidence).filter_by(id=evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    if ev.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    path = absolute_path(ev.storage_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found on storage")
    return FileResponse(path, media_type=ev.media_type, filename=ev.original_filename)


@router.get("/evidence/{evidence_id}/thumb/{size}")
def get_thumbnail(evidence_id: str, size: int, household_id: str = Query(...), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    ev = db.query(Evidence).filter_by(id=evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    if ev.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    # Allow only configured sizes
    if size not in settings.thumbnail_sizes:
        raise HTTPException(status_code=422, detail="Invalid thumbnail size")
    tp = thumbnail_path(ev.storage_key, size)
    if not tp.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(tp, media_type="image/jpeg")
