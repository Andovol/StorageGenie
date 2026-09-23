"""SG-098 manual Enrich trigger endpoint (offline, $0).

Scope: the REAL endpoint (`POST /v1/enrich/{asset_id}`) driven through the REAL
router (`app.main`), the REAL OFF/Jina clients (`app.services.enrich`) and the
REAL candidate reader (`GET /v1/candidates/{id}`). Every HTTP leg is a scripted
`httpx.MockTransport` injected through the endpoint's own dependency seams, so
no key crosses a wire and no metered call is made.

What this file proves (`PG-SC-12`: no re-implemented seam):
- consent gates BEFORE any client touch (named refusal, 0 invocations);
- the per-press cap is enforced server-side as the mirror of the frontend
  `enrichCapRefusal` (named refusal, 0 invocations);
- an asset with no usable identifier TEXT is refused by name;
- OFF runs first and Jina fires only on an OFF miss (order preserved);
- the identifier query is TEXT only (no image bytes, no GPS, no key value);
- the proposals persist as a gated candidate row readable via the REAL
  candidates route, and web fields commit as `review_state="proposed"` through
  the REAL commit path; the snapshots themselves are UNRECORDED (`PG-SC-02`).
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

from app.api.v1.enrich import (
    ENRICH_PER_PRESS_CAP_USD,
    enrich_cap_refusal,
    get_jina_http_client,
    get_off_http_client,
)
from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.household import Household
from app.services import candidates
from app.services.candidates import Candidate

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"
KEY_SENTINEL = "test-sg098-sentinel"
EXPECTED_CAP_MESSAGE = (
    "per_press_cap_exceeded: last press cost $0.060000 exceeds cap $0.05"
)


def _load(name: str) -> Any:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def _scripted(
    payload: Any = None,
    *,
    status: int = 200,
    body_text: str | None = None,
    tag: str | None = None,
    order: list[str] | None = None,
) -> tuple[httpx.Client, list[httpx.Request]]:
    """A mock HTTP driver that records every request and its call order."""
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if order is not None and tag is not None:
            order.append(tag)
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
        f"sqlite:///{tmp_path / 'enrich-endpoint.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Enrich Household")
    other = Household(name="Other Enrich Household")
    session.add_all([household, other])
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
                value_json=json.dumps("3274080005003"),
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
        yield session, household.id, other.id, asset.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_off_http_client, None)
        app.dependency_overrides.pop(get_jina_http_client, None)
        session.close()
        engine.dispose()


# --------------------------------------------------------------------------- #
# Cap helper mirrors the frontend exactly (`G-A9`, stated and uncalibrated)
# --------------------------------------------------------------------------- #
def test_cap_refusal_mirrors_the_frontend_message() -> None:
    assert ENRICH_PER_PRESS_CAP_USD == 0.05
    assert enrich_cap_refusal(0.01) is None
    assert enrich_cap_refusal(0.06) == EXPECTED_CAP_MESSAGE
    assert enrich_cap_refusal(float("inf")) is not None
    assert enrich_cap_refusal(float("inf")).startswith("per_press_cap_unknown")  # type: ignore[union-attr]


# --------------------------------------------------------------------------- #
# Router registration — BOTH main.py sites (import + include) and the live route
# --------------------------------------------------------------------------- #
def test_router_registered_at_both_main_sites_and_served() -> None:
    paths = set(app.openapi()["paths"])
    assert "/v1/enrich/{asset_id}" in paths
    source = (Path(__file__).resolve().parents[1] / "app" / "main.py").read_text(
        encoding="utf-8"
    )
    assert "from app.api.v1.enrich import router as enrich_router" in source
    assert 'app.include_router(enrich_router, prefix="/v1")' in source


# --------------------------------------------------------------------------- #
# G1 — OFF hit: Jina never fires; gated proposal reads back via the real route
# --------------------------------------------------------------------------- #
def test_off_hit_never_fires_jina_and_candidate_reads_back(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _other_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    order: list[str] = []
    off, off_seen = _scripted(_load("off_hit"), tag="off", order=order)
    jina, jina_seen = _scripted(_load("jina_hit"), tag="jina", order=order)
    _install(off, jina)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/enrich/{asset_id}", params={"household_id": household_id}
        )
        assert response.status_code == 200
        body = response.json()
        read = client.get(
            f"/v1/candidates/{body['candidate_id']}",
            params={"household_id": household_id},
        )

    assert body["off_accepted"] is True
    assert body["fallback_fired"] is False
    assert body["fallback_reason"] is None
    assert body["snapshots_recorded"] is False
    assert order == ["off"]
    assert len(off_seen) == 1
    assert jina_seen == []

    assert read.status_code == 200
    candidate = read.json()
    assert candidate["state"] == "proposed"
    assert candidate["fields"]["display_name"]["source_type"] == "web:OpenFoodFacts"
    assert candidate["fields"]["identifier"]["value"] == "3274080005003"
    # Snapshots are UNRECORDED (`PG-SC-02`): no raw provider body on the row.
    # The snapshot rides the RESPONSE body but is UNRECORDED on the row
    # (`PG-SC-02`): the contrast is the non-vacuous proof.
    assert body["primary"]["raw"] is not None
    stored = session.query(Candidate).filter_by(id=body["candidate_id"]).one()
    assert '"raw"' not in stored.proposed_fields_json
    assert '"primary"' not in stored.proposed_fields_json
    assert '"fallback"' not in stored.proposed_fields_json


# --------------------------------------------------------------------------- #
# G1 — OFF miss: Jina fires, OFF strictly first
# --------------------------------------------------------------------------- #
def test_off_miss_fires_jina_and_order_is_off_then_jina(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _session, household_id, _other_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", KEY_SENTINEL)
    order: list[str] = []
    off, off_seen = _scripted(_load("off_empty"), tag="off", order=order)
    jina, jina_seen = _scripted(_load("jina_hit"), tag="jina", order=order)
    _install(off, jina)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/enrich/{asset_id}", params={"household_id": household_id}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["off_accepted"] is False
    assert body["fallback_fired"] is True
    assert body["fallback_reason"] == "off_no_confident_match"
    assert order == ["off", "jina"]
    assert len(off_seen) == 1
    assert len(jina_seen) == 1
    assert body["fields"]["display_name"]["source_type"] == "web:JinaSearch"
    assert body["web_sources"][0]["source"] == "web:JinaSearch"


# --------------------------------------------------------------------------- #
# G1 — consent gates BEFORE any client touch
# --------------------------------------------------------------------------- #
def test_consent_false_refuses_by_name_with_zero_invocations(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _session, household_id, _other_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", False)
    off, off_seen = _scripted(_load("off_hit"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/enrich/{asset_id}", params={"household_id": household_id}
        )

    assert response.status_code == 403
    assert response.json()["detail"].startswith("consent_disabled")
    assert off_seen == []
    assert jina_seen == []


# --------------------------------------------------------------------------- #
# G1 — server-side per-press cap refuses by name with zero invocations
# --------------------------------------------------------------------------- #
def test_over_cap_refuses_by_name_with_zero_invocations(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _session, household_id, _other_id, asset_id = enrich_env
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
    assert response.json()["detail"] == EXPECTED_CAP_MESSAGE
    assert off_seen == []
    assert jina_seen == []


# --------------------------------------------------------------------------- #
# PG-SC-07 — no usable identifier TEXT: named refusal, never a guessed query
# --------------------------------------------------------------------------- #
def test_identifier_less_asset_is_refused_by_name(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _other_id, _asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    bare = Asset(
        household_id=household_id, display_name=None, asset_type="unknown", status="ACTIVE"
    )
    session.add(bare)
    session.commit()
    off, off_seen = _scripted(_load("off_hit"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/enrich/{bare.id}", params={"household_id": household_id}
        )

    assert response.status_code == 422
    assert response.json()["detail"].startswith("missing_identifiers")
    assert off_seen == []
    assert jina_seen == []


# --------------------------------------------------------------------------- #
# G1 — TEXT only: no image bytes, no GPS, no key value anywhere
# --------------------------------------------------------------------------- #
def test_identifier_query_is_text_only_and_key_value_never_leaves(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _other_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", KEY_SENTINEL)
    order: list[str] = []
    off, off_seen = _scripted(_load("off_empty"), tag="off", order=order)
    jina, jina_seen = _scripted(_load("jina_hit"), tag="jina", order=order)
    _install(off, jina)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/enrich/{asset_id}", params={"household_id": household_id}
        )

    assert response.status_code == 200
    body = response.json()
    off_request = off_seen[0]
    assert off_request.content == b""
    assert dict(off_request.url.params)["brands_tags"] == "Jacobs"
    assert dict(off_request.url.params)["search_terms"] == "Jacobs Cronat Gold"
    for name in off_request.url.params.keys():
        assert name.lower() not in {"image", "photo", "lat", "lon", "gps", "key", "token"}

    jina_request = jina_seen[0]
    assert jina_request.content == b""
    assert KEY_SENTINEL not in str(jina_request.url)
    for _name, value in jina_request.url.params.multi_items():
        assert KEY_SENTINEL not in value
    # The Bearer header NAME is added at send time; its VALUE is never asserted.
    assert "authorization" in {name.lower() for name in jina_request.headers}
    assert KEY_SENTINEL not in json.dumps(body)
    stored = session.query(Candidate).filter_by(id=body["candidate_id"]).one()
    assert KEY_SENTINEL not in stored.proposed_fields_json


# --------------------------------------------------------------------------- #
# PG-SC-02 — the endpoint's own proposal commits gated via the REAL commit path
# --------------------------------------------------------------------------- #
def test_endpoint_proposal_commits_gated_via_real_commit_path(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _other_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_confidence_threshold", 0.0)
    off, _off_seen = _scripted(_load("off_hit"))
    jina, _jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/enrich/{asset_id}", params={"household_id": household_id}
        )

    assert response.status_code == 200
    candidate = (
        session.query(Candidate).filter_by(id=response.json()["candidate_id"]).one()
    )
    candidate.state = "accepted"
    session.flush()
    result = candidates.commit_candidate(session, candidate)
    session.flush()
    assert result["created"] is True

    rows = {
        row.field_path: row
        for row in session.query(Assertion).filter_by(asset_id=result["asset_id"]).all()
    }
    # A web field is a proposal even at a 0.0 confidence threshold.
    assert rows["display_name"].review_state == "proposed"
    assert rows["display_name"].source_type == "web:OpenFoodFacts"
    assert rows["identifier"].review_state == "proposed"
