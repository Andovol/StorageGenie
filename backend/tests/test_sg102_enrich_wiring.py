"""SG-102 persisted-snapshot wiring into the Enrich endpoint (offline, $0).

Scope: the REAL endpoint (`POST /v1/enrich/{asset_id}`) driven through the REAL
router (`app.main`), the REAL OFF/Jina clients (`app.services.enrich`) and the
REAL SG-100 writer + loader (`app.services.enrich.snapshots`). Every HTTP leg is
a scripted `httpx.MockTransport` injected through the endpoint's own dependency
seams, so no key crosses a wire and no metered call is made.

What this file proves (`PG-SC-02` closure):
- the endpoint records ONE OFF row always and ONE Jina row iff the fallback
  fired, readable back through the writer's own loader (`get_snapshots_by_source`
  and `get_snapshot`) — writer and reader in one leg;
- the response flips `snapshots_recorded` to True (it was False in SG-098);
- a degraded fetch records its named reason, never dropped (SG-100 rule);
- one fetch = exactly one row per source (no double-write);
- the consent gate still precedes every recording hunk (0 sends, 0 rows).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.v1.enrich import get_jina_http_client, get_off_http_client
from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.enrich_snapshot import EnrichSnapshot
from app.models.household import Household
from app.services.enrich import snapshots as snap_mod

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"

# The exact brand+name TEXT the endpoint searches: `build_jina_query(brand, name)`
# = "Jacobs" + "Jacobs Cronat Gold" (the fixture asset's display_name + brand).
EXPECTED_QUERY = "Jacobs Jacobs Cronat Gold"
EXPECTED_CODE = "3274080005003"


def _load(name: str) -> Any:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def _scripted(
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


def _install(off: httpx.Client, jina: httpx.Client) -> None:
    app.dependency_overrides[get_off_http_client] = lambda: off
    app.dependency_overrides[get_jina_http_client] = lambda: jina


@pytest.fixture
def enrich_env(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg102-endpoint.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG-102 Household")
    session.add(household)
    session.commit()
    asset = Asset(
        household_id=household.id,
        display_name="Jacobs Cronat Gold",
        asset_type="product",
        status="ACTIVE",
    )
    session.add(asset)
    session.commit()
    session.add_all(
        [
            Assertion(
                asset_id=asset.id,
                field_path="brand",
                value_json=json.dumps("Jacobs"),
                source_type="user",
                review_state="accepted",
            ),
            Assertion(
                asset_id=asset.id,
                field_path="identifier",
                value_json=json.dumps(EXPECTED_CODE),
                source_type="user",
                review_state="accepted",
            ),
        ]
    )
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, asset.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_off_http_client, None)
        app.dependency_overrides.pop(get_jina_http_client, None)
        session.close()
        engine.dispose()


def _post(asset_id: str, household_id: str) -> Any:
    with TestClient(app) as client:
        return client.post(
            f"/v1/enrich/{asset_id}", params={"household_id": household_id}
        )


# --------------------------------------------------------------------------- #
# G1 — OFF hit: one OFF row recorded, no Jina row; readable via the loader
# --------------------------------------------------------------------------- #
def test_off_hit_records_one_off_row_and_no_jina_row(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    off, off_seen = _scripted(_load("off_hit"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    response = _post(asset_id, household_id)

    assert response.status_code == 200
    body = response.json()
    # The SG-098 flip: it was False, it is now True (asserted, not assumed).
    assert body["snapshots_recorded"] is True
    assert body["off_accepted"] is True
    assert body["fallback_fired"] is False
    assert len(off_seen) == 1
    assert jina_seen == []

    off_rows = snap_mod.get_snapshots_by_source(session, "off")
    assert snap_mod.get_snapshots_by_source(session, "jina") == []
    assert len(off_rows) == 1
    row = off_rows[0]
    assert row.source == "off"
    assert row.query == EXPECTED_QUERY
    assert row.status_code == 200
    assert row.no_result_reason is None
    assert row.version == snap_mod.SNAPSHOT_SCHEMA_VERSION
    assert json.loads(row.raw_body or "{}")["products"][0]["code"] == EXPECTED_CODE
    # The writer's own by-id loader reads the same row back (reader in one leg).
    assert snap_mod.get_snapshot(session, row.id) is row
    assert session.query(EnrichSnapshot).count() == 1


# --------------------------------------------------------------------------- #
# G1 — OFF miss: exactly one OFF + one Jina row (no double-write)
# --------------------------------------------------------------------------- #
def test_off_miss_records_off_and_jina_rows_once_each(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", "test-sg102-sentinel")
    off, off_seen = _scripted(_load("off_empty"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    response = _post(asset_id, household_id)

    assert response.status_code == 200
    body = response.json()
    assert body["snapshots_recorded"] is True
    assert body["fallback_fired"] is True
    assert len(off_seen) == 1
    assert len(jina_seen) == 1

    off_rows = snap_mod.get_snapshots_by_source(session, "off")
    jina_rows = snap_mod.get_snapshots_by_source(session, "jina")
    assert len(off_rows) == 1
    assert len(jina_rows) == 1
    assert off_rows[0].query == EXPECTED_QUERY
    jrow = jina_rows[0]
    assert jrow.source == "jina"
    assert jrow.query == EXPECTED_QUERY
    assert jrow.status_code == 200
    assert jrow.no_result_reason is None
    assert "mega-image" in (jrow.raw_body or "")
    # One fetch, one write per source: no double-write.
    assert session.query(EnrichSnapshot).count() == 2


# --------------------------------------------------------------------------- #
# G1 — degraded fetch records its named reason (never dropped)
# --------------------------------------------------------------------------- #
def test_degraded_fetch_records_named_reason(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", "test-sg102-sentinel")
    off, _off_seen = _scripted(status=503, body_text="service unavailable")
    jina, _jina_seen = _scripted(status=503, body_text="jina unavailable")
    _install(off, jina)

    response = _post(asset_id, household_id)

    assert response.status_code == 200
    body = response.json()
    assert body["snapshots_recorded"] is True
    assert body["fallback_fired"] is True

    off_rows = snap_mod.get_snapshots_by_source(session, "off")
    jina_rows = snap_mod.get_snapshots_by_source(session, "jina")
    assert len(off_rows) == 1 and len(jina_rows) == 1
    assert "http_status" in (off_rows[0].no_result_reason or "")
    assert off_rows[0].raw_body is None
    assert off_rows[0].raw_text == "service unavailable"
    assert "http_status" in (jina_rows[0].no_result_reason or "")
    assert jina_rows[0].raw_body is None
    assert jina_rows[0].raw_text == "jina unavailable"


# --------------------------------------------------------------------------- #
# G1 — the consent gate still precedes every recording hunk (0 sends, 0 rows)
# --------------------------------------------------------------------------- #
def test_consent_false_refuses_and_records_nothing(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", False)
    off, off_seen = _scripted(_load("off_hit"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    response = _post(asset_id, household_id)

    assert response.status_code == 403
    assert response.json()["detail"].startswith("consent_disabled")
    assert off_seen == []
    assert jina_seen == []
    assert session.query(EnrichSnapshot).count() == 0


# --------------------------------------------------------------------------- #
# G1 — the per-press cap refusal also precedes every recording hunk
# --------------------------------------------------------------------------- #
def test_over_cap_refuses_and_records_nothing(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    off, off_seen = _scripted(_load("off_hit"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/enrich/{asset_id}",
            params={"household_id": household_id, "last_spend_usd": 0.06},
        )

    assert response.status_code == 402
    assert off_seen == []
    assert jina_seen == []
    assert session.query(EnrichSnapshot).count() == 0
