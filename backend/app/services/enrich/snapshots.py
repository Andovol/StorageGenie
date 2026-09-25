"""SG-100 append-only enrichment snapshot writer, extended by SG-132.

One row per source fetch, stored verbatim. There is NO update path anywhere in
this module: a correction is a NEW row. A degraded snapshot (``no_result_reason``
set) is recorded loudly with its named reason and raw text, never dropped.

The endpoint does not read this table until the live re-confirms slice
(``PG-SC-02``): this module is the library only. The snapshot value objects do
not carry the query text, so the writer takes ``query`` as an explicit keyword
argument (brand+name TEXT only — never a photo, a coordinate or a key).

SG-132 adds the Jina Search COST ledger beside the snapshot: every Jina request
that actually left the machine appends ONE ``provider_call`` row carrying the
``jina.estimate_jina_search_cost`` figure, joined through the enrichment job so
the month-boxed spend reader (``providers.reader._recorded_spend``) counts it
with no reader change. The writer is the production seam the wire path calls; a
test that inserts the row itself would prove only that the table accepts it.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.enrich_snapshot import EnrichSnapshot
from app.models.job import Job
from app.models.provider_call import ProviderCall
from app.services.enrich import jina as jina_mod
from app.services.enrich.client import OffSearchSnapshot
from app.services.enrich.jina import JinaSearchSnapshot

SOURCE_OFF = "off"
SOURCE_JINA = "jina"
SNAPSHOT_SCHEMA_VERSION = "enrich-snapshot-v1"

# The ledger identity of a Jina Search request. `provider` mirrors the source
# attribution the snapshot carries ("JinaSearch"); Search has no model, so the
# model slot names the endpoint's product rather than inventing a model id, and
# the template slot names the request builder.
JINA_LEDGER_PROVIDER = jina_mod.SOURCE_NAME
JINA_LEDGER_MODEL = "jina-search"
JINA_LEDGER_TEMPLATE_VERSION = "jina-search-v1"


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


def record_jina_search_call(
    db: Session,
    job: Job,
    snapshot: JinaSearchSnapshot,
    *,
    query: str,
    tokens: int = jina_mod.JINA_SEARCH_TOKENS_PER_REQUEST,
) -> ProviderCall:
    """Append ONE ``provider_call`` ledger row for one Jina Search request.

    Cost is the estimator's bounded USD figure for ``tokens`` (default the
    vendor floor) — never a measured cost, which the keyless client cannot
    observe. The row joins through ``job`` so ``provider_call -> job ->
    household_id`` carries it into the month-boxed spend reader with no reader
    change. It commits immediately: the request has already been paid for even
    if a later step in the press fails.
    """
    text = query.strip()
    if not text:
        raise ValueError("query must be non-empty brand+name text")
    reason = snapshot.no_result_reason
    row = ProviderCall(
        provider=JINA_LEDGER_PROVIDER,
        model=JINA_LEDGER_MODEL,
        prompt_template_version=JINA_LEDGER_TEMPLATE_VERSION,
        input_hashes=json.dumps(
            {"query_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
        ),
        output_payload=json.dumps(
            {
                "request_url": snapshot.request_url,
                "status_code": snapshot.status_code,
                "no_result_reason": reason,
                "result_count": len(snapshot.results),
            },
            ensure_ascii=False,
        ),
        cost=jina_mod.estimate_jina_search_cost(tokens),
        usage_json=json.dumps({"requests": 1, "tokens": tokens}, ensure_ascii=False),
        latency_ms=None,
        error_state=reason[:200] if reason else None,
        job_id=job.id,
    )
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
