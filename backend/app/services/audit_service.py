import datetime
import json

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def record(
    db: Session,
    *,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str,
    before: dict | None,
    after: dict | None,
    household_id: str | None,
) -> AuditEvent:
    ev = AuditEvent(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_json=json.dumps(before) if before is not None else None,
        after_json=json.dumps(after) if after is not None else None,
        household_id=household_id,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(ev)
    return ev
