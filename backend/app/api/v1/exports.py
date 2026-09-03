import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.assertion import Assertion
from app.models.audit_event import AuditEvent
from app.models.asset import Asset
from app.models.evidence import Evidence
from app.schemas.common import loads_json

router = APIRouter()

MANIFEST_VERSION = "1"
ALEMBIC_HEAD = "0201cf10c56c"


@router.get("/export")
def export_catalog(household_id: str = Query(...), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    with db.begin():
        assets = db.query(Asset).filter_by(household_id=household_id).all()
        evidence = db.query(Evidence).filter_by(household_id=household_id).all()
        assertions = []
        for asset in assets:
            for ass in db.query(Assertion).filter_by(asset_id=asset.id).all():
                assertions.append(
                    {
                        "id": ass.id,
                        "asset_id": ass.asset_id,
                        "field_path": ass.field_path,
                        "value": loads_json(ass.value_json),
                        "review_state": ass.review_state,
                    }
                )
        audits = db.query(AuditEvent).filter_by(household_id=household_id).all()
        body = {
            "household_id": household_id,
            "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "manifest_version": MANIFEST_VERSION,
            "db_revision": ALEMBIC_HEAD,
            "assets": [
                {
                    "id": a.id,
                    "display_name": a.display_name,
                    "asset_type": a.asset_type,
                    "status": a.status,
                    "version": a.version,
                }
                for a in assets
            ],
            "evidence_manifest": [
                {"id": e.id, "sha256": e.sha256, "storage_key": e.storage_key, "size_bytes": e.size_bytes}
                for e in evidence
            ],
            "assertions": assertions,
            "audit_events": [
                {"id": ae.id, "action": ae.action, "entity_id": ae.entity_id} for ae in audits
            ],
        }
    return JSONResponse(
        content=body,
        headers={"Content-Disposition": 'attachment; filename="storagegenie-export.json"'},
    )
