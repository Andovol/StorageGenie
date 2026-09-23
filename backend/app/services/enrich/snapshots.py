"""SG-100 append-only enrichment snapshot writer (unwired library).

One row per source fetch, stored verbatim. There is NO update path anywhere in
this module: a correction is a NEW row. A degraded snapshot (``no_result_reason``
set) is recorded loudly with its named reason and raw text, never dropped.

The endpoint does not read this table until the live re-confirms slice
(``PG-SC-02``): this module is the library only. The snapshot value objects do
not carry the query text, so the writer takes ``query`` as an explicit keyword
argument (brand+name TEXT only — never a photo, a coordinate or a key).
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.enrich_snapshot import EnrichSnapshot
from app.services.enrich.client import OffSearchSnapshot
from app.services.enrich.jina import JinaSearchSnapshot

SOURCE_OFF = "off"
SOURCE_JINA = "jina"
SNAPSHOT_SCHEMA_VERSION = "enrich-snapshot-v1"


def serialize_raw_body(raw: Any) -> str | None:
    """Canonical, lossless JSON for a snapshot's raw body; ``None`` stays ``None``.

    The snapshot carries the parsed body, not the original byte stream, so
    "verbatim" here means the raw object round-trips exactly — it is never
    filtered, truncated or reshaped.
    """
    if raw is None:
        return None
    return json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _new_row(
    snapshot: OffSearchSnapshot | JinaSearchSnapshot, *, source: str, query: str
) -> EnrichSnapshot:
    text = query.strip()
    if not text:
        raise ValueError("query must be non-empty brand+name text")
    return EnrichSnapshot(
        source=source,
        query=text,
        request_url=snapshot.request_url,
        retrieved_at=snapshot.retrieved_at,
        status_code=snapshot.status_code,
        raw_body=serialize_raw_body(snapshot.raw),
        raw_text=snapshot.raw_text,
        no_result_reason=snapshot.no_result_reason,
        version=SNAPSHOT_SCHEMA_VERSION,
    )


def record_off_snapshot(
    db: Session, snapshot: OffSearchSnapshot, *, query: str
) -> EnrichSnapshot:
    """Append ONE row for an OFF fetch; always inserts, never updates."""
    row = _new_row(snapshot, source=SOURCE_OFF, query=query)
    db.add(row)
    db.commit()
    return row


def record_jina_snapshot(
    db: Session, snapshot: JinaSearchSnapshot, *, query: str
) -> EnrichSnapshot:
    """Append ONE row for a Jina fetch; always inserts, never updates."""
    row = _new_row(snapshot, source=SOURCE_JINA, query=query)
    db.add(row)
    db.commit()
    return row


def get_snapshot(db: Session, snapshot_id: str) -> EnrichSnapshot | None:
    """Read one row back by id (the writer's own loader)."""
    return db.get(EnrichSnapshot, snapshot_id)


def get_snapshots_by_source(db: Session, source: str) -> list[EnrichSnapshot]:
    """Read every row for a source, oldest first (append-only history)."""
    return list(
        db.query(EnrichSnapshot)
        .filter(EnrichSnapshot.source == source)
        .order_by(EnrichSnapshot.created_at, EnrichSnapshot.id)
        .all()
    )
