import base64
import json
from datetime import datetime

from pydantic import BaseModel


class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str


def encode_cursor(created_at: datetime, id: str) -> str:
    # Spec: base64(last_id:created_at)  -> id first, colon separator
    raw = f"{id}:{created_at.isoformat()}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, str] | None:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        # Support both ':' (spec) and '|' (legacy) and handle id:ts or ts|id order
        if ":" in raw:
            oid, ts_str = raw.split(":", 1)
            ts = datetime.fromisoformat(ts_str)
            return ts, oid
        if "|" in raw:
            # legacy ts|id
            ts_str, oid = raw.split("|", 1)
            ts = datetime.fromisoformat(ts_str)
            return ts, oid
        return None
    except Exception:
        return None


def dumps_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def loads_json(value: str | None) -> object:
    if value is None:
        return None
    try:
        return json.loads(value)
    except Exception:
        return value
