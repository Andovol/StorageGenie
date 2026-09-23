"""SG-103 reviewer alternatives: `web_alternates` as first-class proposal rows ($0).

Scope: the REAL endpoint (`POST /v1/enrich/{asset_id}`) driven through the REAL
router (`app.main`), the REAL OFF/Jina clients (`app.services.enrich`) and the
REAL candidate reader (`GET /v1/candidates/{id}`). Every HTTP leg is a scripted
`httpx.MockTransport` injected through the endpoint's own dependency seams, so
no key crosses a wire and no metered call is made ($0).

What this file proves:
- a label/web conflict keeps the LABEL value in the proposal AND surfaces the
  WEB value as one alternate row carrying the full source triple
  (`field` + `value` + `source_type` + `source_url` + `retrieved_at`);
- a non-conflicting enrichment fills the proposal from web and yields `[]`;
- the alternates round-trip through the REAL `GET /v1/candidates/{id}` route
  (writer = the endpoint's own commit, reader = the candidates route);
- a brand-absent asset yields NO brand alternate (no web path emits a brand);
- the consent gate still refuses before any candidate row is written.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.v1.enrich import get_jina_http_client, get_off_http_client
from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.household import Household
from app.services.candidates import Candidate

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"

# The exact label value seeded as the asset's own `display_name` assertion.
LABEL_NAME = "Jacobs Cronat Gold"
# The OFF fixture's `product_name`, which conflicts with the label value.
WEB_NAME = "Jacobs Cronat Gold instant coffee"
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
def make_env(tmp_path: Path):  # type: ignore[no-untyped-def]
    """Build one temp-DB asset env per call; tear every override/engine down."""
    created: list[tuple[Session, Engine]] = []

    def _make(
        *,
        name: str,
        display_name: str | None,
        assertions: list[tuple[str, object]],
    ) -> tuple[Session, str, str]:
        engine = create_engine(
            f"sqlite:///{tmp_path / (name + '.db')}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(engine)
        factory = sessionmaker(bind=engine, expire_on_commit=False)
        session: Session = factory()
        household = Household(name=f"{name} household")
        session.add(household)
        session.commit()
        asset = Asset(
            household_id=household.id,
            display_name=display_name,
            asset_type="product",
            status="ACTIVE",
        )
        session.add(asset)
        session.commit()
        for field_path, value in assertions:
            session.add(
                Assertion(
                    asset_id=asset.id,
                    field_path=field_path,
                    value_json=json.dumps(value),
                    source_type="user",
                    review_state="accepted",
                )
            )
        session.commit()

        def override_get_db():  # type: ignore[no-untyped-def]
            request_session: Session = factory()
            try:
                yield request_session
            finally:
                request_session.close()

        app.dependency_overrides[get_db] = override_get_db
        created.append((session, engine))
        return session, household.id, asset.id

    try:
        yield _make
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_off_http_client, None)
        app.dependency_overrides.pop(get_jina_http_client, None)
        for session, engine in created:
            session.close()
            engine.dispose()


def _post(asset_id: str, household_id: str) -> tuple[int, dict[str, Any]]:
    with TestClient(app) as client:
        response = client.post(
            f"/v1/enrich/{asset_id}", params={"household_id": household_id}
        )
        return response.status_code, response.json()


# --------------------------------------------------------------------------- #
# G1/G2 — conflict: label value kept, web value one alternate with its triple
# --------------------------------------------------------------------------- #
def test_conflict_keeps_label_value_and_surfaces_one_alternate(make_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _session, household_id, asset_id = make_env(
        name="sg103-conflict",
        display_name=LABEL_NAME,
        assertions=[("brand", "Jacobs"), ("display_name", LABEL_NAME)],
    )
    monkeypatch.setattr(settings, "sg_consent", True)
    off, _off_seen = _scripted(_load("off_hit"))
    jina, _jina_seen = _scripted(_load("jina_hit"))
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

    # The label value wins the proposal; the web value is NOT collapsed away.
    assert body["fields"]["display_name"]["value"] == LABEL_NAME
    assert body["fields"]["display_name"]["source_type"] == "user"
    # A gap field the label lacks is filled from web (no alternate).
    assert body["fields"]["identifier"]["value"] == EXPECTED_CODE

    alternates = body["web_alternates"]
    assert len(alternates) == 1
    alternate = alternates[0]
    assert alternate["field"] == "display_name"
    assert alternate["value"] == WEB_NAME
    assert alternate["source_type"] == "web:OpenFoodFacts"
    assert isinstance(alternate["source_url"], str)
    assert "openfoodfacts.org" in alternate["source_url"]
    assert isinstance(alternate["retrieved_at"], str) and alternate["retrieved_at"]

    # Round-trip through the REAL candidates route (writer=endpoint, reader=route).
    assert read.status_code == 200
    candidate = read.json()
    assert candidate["fields"]["display_name"]["value"] == LABEL_NAME
    assert candidate["web_alternates"] == alternates


# --------------------------------------------------------------------------- #
# G1/G2 — no conflict: web fills the proposal, alternates stay empty
# --------------------------------------------------------------------------- #
def test_no_conflict_fills_from_web_and_alternates_empty(make_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _session, household_id, asset_id = make_env(
        name="sg103-noconflict",
        display_name=LABEL_NAME,
        assertions=[("brand", "Jacobs"), ("expiry_date", "2030-01-01")],
    )
    monkeypatch.setattr(settings, "sg_consent", True)
    off, _off_seen = _scripted(_load("off_hit"))
    jina, _jina_seen = _scripted(_load("jina_hit"))
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

    assert body["fields"]["display_name"]["source_type"] == "web:OpenFoodFacts"
    assert body["fields"]["identifier"]["value"] == EXPECTED_CODE
    # A label-visible assertion with no web counterpart is retained, not dropped.
    assert body["fields"]["expiry_date"]["value"] == "2030-01-01"
    assert body["web_alternates"] == []
    assert read.status_code == 200
    assert read.json()["web_alternates"] == []


# --------------------------------------------------------------------------- #
# PG-SC-07 — a brand-absent asset yields no brand alternate (never guessed)
# --------------------------------------------------------------------------- #
def test_brand_absent_asset_yields_no_brand_alternate(make_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _session, household_id, asset_id = make_env(
        name="sg103-nobrand",
        display_name=LABEL_NAME,
        assertions=[("display_name", LABEL_NAME)],
    )
    monkeypatch.setattr(settings, "sg_consent", True)
    # No brand assertion lowers the OFF score below the accept bar, so the Jina
    # fallback fires (a key is required); it still yields no brand.
    monkeypatch.setattr(settings, "jina_api_key", "test-sg103-sentinel")
    off, _off_seen = _scripted(_load("off_hit"))
    jina, _jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    _status, body = _post(asset_id, household_id)

    assert body["fallback_fired"] is True
    assert "brand" not in body["fields"]
    assert all(alternate["field"] != "brand" for alternate in body["web_alternates"])
    # The label display_name still conflicts (one alternate), and only that one.
    assert [alternate["field"] for alternate in body["web_alternates"]] == ["display_name"]


# --------------------------------------------------------------------------- #
# Regression — the consent gate still refuses with zero candidate rows
# --------------------------------------------------------------------------- #
def test_consent_false_refuses_with_zero_candidates(make_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = make_env(
        name="sg103-consent",
        display_name=LABEL_NAME,
        assertions=[("brand", "Jacobs"), ("display_name", LABEL_NAME)],
    )
    monkeypatch.setattr(settings, "sg_consent", False)
    off, off_seen = _scripted(_load("off_hit"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    status, body = _post(asset_id, household_id)

    assert status == 403
    assert body["detail"].startswith("consent_disabled")
    assert off_seen == []
    assert jina_seen == []
    assert session.query(Candidate).count() == 0
