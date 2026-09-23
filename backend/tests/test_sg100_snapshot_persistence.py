"""SG-100 enrichment snapshot persistence (offline, $0).

Scope: the new append-only ``enrich_snapshot`` table + migration + writer + the
committed brand-absent fixture. The REAL SG-081/082 fetchers run over scripted
``httpx.MockTransport`` transports, so no network and no metered call exists on
any path. The endpoint is NOT touched: it still reads memory (``PG-SC-02``), and
the migration is exercised on temp SQLite databases only.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect as sa_inspect
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base
from app.models.enrich_snapshot import EnrichSnapshot
from app.services.enrich import client as off_client
from app.services.enrich import jina as jina_mod
from app.services.enrich import snapshots as snap_mod

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"

HEAD_REVISION = "20260923_sg100_enrich_snapshot"
PREVIOUS_REVISION = "20260917_sg068_saved_search"

Q_NAME = "Jacobs Cronat Gold instant coffee"
Q_BRAND = "Jacobs"
QUERY = f"{Q_BRAND} {Q_NAME}"
SENTINEL_KEY = "test-key-not-real"


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _scripted_client(
    payload: Any = None,
    *,
    status: int = 200,
    body_text: str | None = None,
) -> tuple[httpx.Client, list[httpx.Request]]:
    """A mock HTTP driver that records every request it receives (no network)."""
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if body_text is not None:
            return httpx.Response(status, text=body_text, request=request)
        return httpx.Response(status, json=payload, request=request)

    return httpx.Client(transport=httpx.MockTransport(handler)), seen


def _alembic_config(url: str) -> Config:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[1] / "alembic")
    )
    config.set_main_option("sqlalchemy.url", url)
    return config


def _off_snapshot(
    *, payload: Any = None, status: int = 200, body_text: str | None = None
) -> off_client.OffSearchSnapshot:
    client, _seen = _scripted_client(
        _load("off_hit.json") if payload is None else payload,
        status=status,
        body_text=body_text,
    )
    return off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=client)


def _jina_snapshot(
    *, payload: Any = None, status: int = 200, body_text: str | None = None
) -> jina_mod.JinaSearchSnapshot:
    client, _seen = _scripted_client(
        _load("jina_hit.json") if payload is None else payload,
        status=status,
        body_text=body_text,
    )
    return jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=client, api_key=SENTINEL_KEY
    )


@pytest.fixture
def snapshot_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg100.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


# --------------------------------------------------------------------------- #
# G1 — migration chains from the live head; upgrade/downgrade/upgrade on temp DB
# --------------------------------------------------------------------------- #
def test_sg100_migration_upgrade_downgrade_upgrade(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{tmp_path / 'sg100_migration.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    config = _alembic_config(url)

    command.upgrade(config, "head")
    inspector = sa_inspect(create_engine(url))
    assert "enrich_snapshot" in inspector.get_table_names()
    assert {ix["name"] for ix in inspector.get_indexes("enrich_snapshot")} >= {
        "ix_enrich_snapshot_source"
    }

    command.downgrade(config, PREVIOUS_REVISION)
    assert "enrich_snapshot" not in set(sa_inspect(create_engine(url)).get_table_names())

    command.upgrade(config, "head")
    assert "enrich_snapshot" in set(sa_inspect(create_engine(url)).get_table_names())


def test_table_is_visible_through_derived_metadata() -> None:
    """The suite sees the new table via metadata, not a static table list."""
    assert "enrich_snapshot" in Base.metadata.tables
    assert Base.metadata.tables["enrich_snapshot"] is EnrichSnapshot.__table__


# --------------------------------------------------------------------------- #
# G2 — writer round-trip per source; verbatim body byte-equal to the input
# --------------------------------------------------------------------------- #
def test_off_round_trip_stores_verbatim_body(snapshot_db: Session) -> None:
    snapshot = _off_snapshot()
    assert snapshot.no_result_reason is None
    row = snap_mod.record_off_snapshot(snapshot_db, snapshot, query=QUERY)

    assert row.id
    assert row.source == "off"
    assert row.query == QUERY
    assert row.request_url == snapshot.request_url
    assert row.retrieved_at == snapshot.retrieved_at
    assert row.status_code == 200
    assert row.no_result_reason is None
    assert row.raw_text is None
    assert row.version == snap_mod.SNAPSHOT_SCHEMA_VERSION
    assert json.loads(row.raw_body or "null") == snapshot.raw
    assert row.raw_body == json.dumps(
        snapshot.raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    assert json.loads(row.raw_body or "{}")["products"][0]["code"] == "3274080005003"


def test_jina_round_trip_stores_verbatim_body(snapshot_db: Session) -> None:
    snapshot = _jina_snapshot()
    assert snapshot.no_result_reason is None
    row = snap_mod.record_jina_snapshot(snapshot_db, snapshot, query=QUERY)

    assert row.source == "jina"
    assert row.query == QUERY
    assert row.status_code == 200
    assert json.loads(row.raw_body or "null") == snapshot.raw
    assert row.raw_body == json.dumps(
        snapshot.raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    assert (
        json.loads(row.raw_body or "[]")[0]["url"]
        == "https://www.mega-image.ro/p/jacobs-cronat-gold-100g"
    )
    # The key is added at send time and never stored anywhere in the row.
    blob = " ".join(
        filter(None, [row.raw_body, row.raw_text, row.request_url, row.query])
    )
    assert SENTINEL_KEY not in blob
    assert "Authorization" not in blob


def test_verbatim_equality_is_not_vacuous(snapshot_db: Session) -> None:
    """A deliberately-reshaped body must NOT compare equal to the stored one."""
    snapshot = _off_snapshot()
    row = snap_mod.record_off_snapshot(snapshot_db, snapshot, query=QUERY)
    tampered = dict(snapshot.raw or {})
    tampered["count"] = 999
    expected_tampered = json.dumps(
        tampered, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    assert row.raw_body != expected_tampered
    assert row.raw_body == json.dumps(
        snapshot.raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


# --------------------------------------------------------------------------- #
# G2 — degraded snapshots recorded loudly; append-only; no update path
# --------------------------------------------------------------------------- #
def test_degraded_off_snapshot_recorded_with_reason(snapshot_db: Session) -> None:
    snapshot = _off_snapshot(status=503, body_text="service unavailable")
    assert snapshot.no_result_reason is not None
    row = snap_mod.record_off_snapshot(snapshot_db, snapshot, query=QUERY)

    assert row.no_result_reason == snapshot.no_result_reason
    assert "http_status" in (row.no_result_reason or "")
    assert row.raw_body is None
    assert row.raw_text == "service unavailable"
    assert snapshot_db.query(EnrichSnapshot).count() == 1


def test_degraded_jina_snapshot_recorded_with_reason(
    snapshot_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("JINA_API_KEY", raising=False)
    monkeypatch.setattr(settings, "jina_api_key", None, raising=False)
    client, _seen = _scripted_client(_load("jina_hit.json"))
    snapshot = jina_mod.fetch_jina_search(Q_NAME, Q_BRAND, http_client=client)
    assert snapshot.no_result_reason is not None
    row = snap_mod.record_jina_snapshot(snapshot_db, snapshot, query=QUERY)

    assert "missing_key" in (row.no_result_reason or "")
    assert row.raw_body is None
    assert snapshot_db.query(EnrichSnapshot).count() == 1


def test_second_write_appends_a_second_row(snapshot_db: Session) -> None:
    row1 = snap_mod.record_off_snapshot(snapshot_db, _off_snapshot(), query=QUERY)
    row2 = snap_mod.record_off_snapshot(snapshot_db, _off_snapshot(), query=QUERY)

    assert row1.id != row2.id
    rows = (
        snapshot_db.query(EnrichSnapshot).filter_by(source="off", query=QUERY).all()
    )
    assert len(rows) == 2
    assert {r.id for r in rows} == {row1.id, row2.id}


def test_module_has_no_update_or_overwrite_function() -> None:
    callables = {
        name
        for name, obj in vars(snap_mod).items()
        if not name.startswith("__") and callable(obj)
    }
    forbidden = ("update", "overwrite", "upsert", "replace", "merge", "delete")
    assert not {n for n in callables if any(t in n.lower() for t in forbidden)}
    source = inspect.getsource(snap_mod)
    for token in (".merge(", ".update(", ".delete(", "session.merge"):
        assert token not in source


def test_empty_query_is_refused(snapshot_db: Session) -> None:
    with pytest.raises(ValueError):
        snap_mod.record_off_snapshot(snapshot_db, _off_snapshot(), query="   ")
    assert snapshot_db.query(EnrichSnapshot).count() == 0


# --------------------------------------------------------------------------- #
# G2 — the writer's own loaders read back by id/source
# --------------------------------------------------------------------------- #
def test_loaders_read_back_by_id_and_source(snapshot_db: Session) -> None:
    off_row = snap_mod.record_off_snapshot(snapshot_db, _off_snapshot(), query=QUERY)
    jina_row = snap_mod.record_jina_snapshot(snapshot_db, _jina_snapshot(), query=QUERY)

    loaded = snap_mod.get_snapshot(snapshot_db, off_row.id)
    assert loaded is not None and loaded.id == off_row.id
    assert snap_mod.get_snapshot(snapshot_db, "does-not-exist") is None
    assert {r.id for r in snap_mod.get_snapshots_by_source(snapshot_db, "off")} == {
        off_row.id
    }
    assert {r.id for r in snap_mod.get_snapshots_by_source(snapshot_db, "jina")} == {
        jina_row.id
    }


# --------------------------------------------------------------------------- #
# G3 — committed brand-absent fixture (F-SG099-2), absence + parity pinned
# --------------------------------------------------------------------------- #
def test_brand_absent_fixture_committed_absent_and_parity_pinned() -> None:
    path = FIXTURES / "off_absent_brand.json"
    assert path.exists()
    absent = _load("off_absent_brand.json")
    hit = _load("off_hit.json")

    assert all("brands" not in product for product in absent["products"])
    # Parity otherwise: removing `brands` from the committed hit yields exactly
    # the committed absent fixture (a deterministic transform, not a new blob).
    derived = json.loads(json.dumps(hit))
    for product in derived["products"]:
        product.pop("brands", None)
    assert absent == derived
