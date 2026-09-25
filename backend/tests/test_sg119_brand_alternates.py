"""SG-119 OFF `brands` into the merge vocabulary + brand alternate ($0).

Scope: the REAL mapper + merge rule (`app.services.candidates`), the REAL
endpoint (`POST /v1/enrich/{asset_id}`) and the REAL candidate reader
(`GET /v1/candidates/{id}`). Every HTTP leg is a scripted `httpx.MockTransport`
injected through the endpoint's own dependency seams, so no key crosses a wire
and no metered call is made.

What this file proves (`PG-SC-07`, `PG-EV-04`):
- `map_off_decision_fields` maps an OFF `brands` value with the same
  `web:OpenFoodFacts` envelope as its sibling fields;
- the two asset populations: a label brand wins and the web brand becomes ONE
  alternate; a brand-absent asset gap-fills (the stated SG-119 decision);
- an OFF-miss / empty `brands` emits NO brand field and NO alternate;
- the brand alternate round-trips through the REAL `GET /v1/candidates/{id}`.
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
from app.services import candidates
from app.services.candidates import Candidate
from app.services.enrich import scoring

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"
OFF_SOURCE_URL = "https://world.openfoodfacts.org/api/v2/search?search_terms=Jacobs"
RETRIEVED_AT = "2026-09-25T00:00:00+00:00"
LABEL_BRAND = "Jacobs"
WEB_BRAND = "Jacobs"


def _load(name: str) -> Any:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def _accepted(product: dict[str, Any]) -> scoring.MatchDecision:
    return scoring.MatchDecision(
        accepted=True,
        best=product,
        best_score=0.9,
        margin=0.3,
        reason=scoring.REASON_ACCEPTED,
    )


# --------------------------------------------------------------------------- #
# G1 — mapper: OFF `brands` -> the sibling `web:OpenFoodFacts` envelope
# --------------------------------------------------------------------------- #
def test_mapper_maps_brands_with_web_provenance() -> None:
    fields = candidates.map_off_decision_fields(
        _accepted({"brands": WEB_BRAND}),
        source_url=OFF_SOURCE_URL,
        retrieved_at=RETRIEVED_AT,
    )

    assert fields["brand"] == {
        "value": WEB_BRAND,
        "confidence": None,
        "source_type": "web:OpenFoodFacts",
        "provider": None,
        "model": None,
        "prompt_template_version": None,
        "provider_call_id": None,
        "source_url": OFF_SOURCE_URL,
        "retrieved_at": RETRIEVED_AT,
    }


def test_mapper_joins_list_brands_verbatim() -> None:
    fields = candidates.map_off_decision_fields(
        _accepted({"brands": ["Jacobs", "Danone"]}),
        source_url=OFF_SOURCE_URL,
        retrieved_at=RETRIEVED_AT,
    )

    assert fields["brand"]["value"] == "Jacobs, Danone"


# --------------------------------------------------------------------------- #
# G1 — miss: absent / empty `brands` emits no field (never an invented brand)
# --------------------------------------------------------------------------- #
def test_mapper_emits_no_brand_when_brands_absent() -> None:
    product = _load("off_absent_brand")["products"][0]
    assert "brands" not in product  # the committed fixture really has none

    fields = candidates.map_off_decision_fields(
        _accepted(product),
        source_url=OFF_SOURCE_URL,
        retrieved_at=RETRIEVED_AT,
    )

    assert "brand" not in fields


def test_mapper_emits_no_brand_when_brands_empty() -> None:
    fields = candidates.map_off_decision_fields(
        _accepted({"brands": ""}),
        source_url=OFF_SOURCE_URL,
        retrieved_at=RETRIEVED_AT,
    )

    assert "brand" not in fields


def test_mapper_non_accepted_maps_nothing() -> None:
    decision = scoring.MatchDecision(
        accepted=False,
        best={"brands": WEB_BRAND},
        best_score=0.3,
        margin=0.0,
        reason=scoring.REASON_BELOW_THRESHOLD,
    )
    assert candidates.map_off_decision_fields(
        decision, source_url=OFF_SOURCE_URL, retrieved_at=RETRIEVED_AT
    ) == {}


# --------------------------------------------------------------------------- #
# G1 — population 1: label brand present -> the web brand is ONE alternate
# --------------------------------------------------------------------------- #
def test_label_brand_present_makes_web_brand_an_alternate() -> None:
    web = candidates.map_off_decision_fields(
        _accepted({"brands": "Jacobs Cronat Gold"}),
        source_url=OFF_SOURCE_URL,
        retrieved_at=RETRIEVED_AT,
    )
    merged, alternates = candidates.merge_web_fields(
        {"brand": {"value": LABEL_BRAND, "source_type": "user"}}, web
    )

    assert merged["brand"]["value"] == LABEL_BRAND  # the label wins the field
    assert alternates == [
        {
            "field": "brand",
            "value": "Jacobs Cronat Gold",
            "source_type": "web:OpenFoodFacts",
            "source_url": OFF_SOURCE_URL,
            "retrieved_at": RETRIEVED_AT,
        }
    ]


# --------------------------------------------------------------------------- #
# G1 — population 2: brand-absent asset -> gap-fill (decision, not a guess)
# --------------------------------------------------------------------------- #
def test_brand_absent_asset_gap_fills_from_web() -> None:
    web = candidates.map_off_decision_fields(
        _accepted({"brands": WEB_BRAND}),
        source_url=OFF_SOURCE_URL,
        retrieved_at=RETRIEVED_AT,
    )
    merged, alternates = candidates.merge_web_fields({}, web)

    assert merged["brand"]["value"] == WEB_BRAND
    assert merged["brand"]["source_type"] == "web:OpenFoodFacts"
    assert alternates == []


# --------------------------------------------------------------------------- #
# G1 — population 3: OFF-miss / empty brands -> no field, gap stays, no alternate
# --------------------------------------------------------------------------- #
def test_off_miss_empty_brands_yields_no_brand_field_or_alternate() -> None:
    product = _load("off_absent_brand")["products"][0]
    web = candidates.map_off_decision_fields(
        _accepted(product),
        source_url=OFF_SOURCE_URL,
        retrieved_at=RETRIEVED_AT,
    )
    merged, alternates = candidates.merge_web_fields(
        {"brand": {"value": LABEL_BRAND, "source_type": "user"}}, web
    )

    assert merged["brand"]["value"] == LABEL_BRAND  # the label row stays alone
    assert [alternate for alternate in alternates if alternate["field"] == "brand"] == []


# --------------------------------------------------------------------------- #
# G1/G2 — endpoint: brand-present asset surfaces the alternate through the route
# --------------------------------------------------------------------------- #
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


def test_endpoint_brand_present_surfaces_and_roundtrips_brand_alternate(
    make_env, monkeypatch  # type: ignore[no-untyped-def]
) -> None:
    _session, household_id, asset_id = make_env(
        name="sg119-brand",
        display_name="Jacobs Cronat Gold",
        assertions=[("brand", LABEL_BRAND), ("display_name", "Jacobs Cronat Gold")],
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

    # The label brand wins the field; the web brand is preserved as an alternate.
    assert body["fields"]["brand"]["value"] == LABEL_BRAND
    assert body["fields"]["brand"]["source_type"] == "user"
    brand_alts = [alt for alt in body["web_alternates"] if alt["field"] == "brand"]
    assert len(brand_alts) == 1
    assert brand_alts[0]["value"] == WEB_BRAND
    assert brand_alts[0]["source_type"] == "web:OpenFoodFacts"
    assert "openfoodfacts.org" in brand_alts[0]["source_url"]

    assert read.status_code == 200
    candidate = read.json()
    assert candidate["fields"]["brand"]["value"] == LABEL_BRAND
    assert candidate["web_alternates"] == body["web_alternates"]


def test_endpoint_off_miss_emits_no_brand_alternate(
    make_env, monkeypatch  # type: ignore[no-untyped-def]
) -> None:
    _session, household_id, asset_id = make_env(
        name="sg119-miss",
        display_name="Jacobs Cronat Gold",
        assertions=[("brand", LABEL_BRAND), ("display_name", "Jacobs Cronat Gold")],
    )
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", "test-sg119-sentinel")
    off, _off_seen = _scripted(_load("off_empty"))
    jina, _jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/enrich/{asset_id}", params={"household_id": household_id}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["off_accepted"] is False
    assert body["fallback_fired"] is True
    # The label brand row is retained; no brand alternate is fabricated.
    assert body["fields"]["brand"]["value"] == LABEL_BRAND
    assert all(alt["field"] != "brand" for alt in body["web_alternates"])


# --------------------------------------------------------------------------- #
# Commit side — a label-wins brand reaches the committed assertion (not a crash)
# --------------------------------------------------------------------------- #
def test_brand_field_commits_through_the_real_commit_path(
    make_env, monkeypatch  # type: ignore[no-untyped-def]
) -> None:
    session, household_id, asset_id = make_env(
        name="sg119-commit",
        display_name="Jacobs Cronat Gold",
        assertions=[("brand", LABEL_BRAND), ("display_name", "Jacobs Cronat Gold")],
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

    candidate = (
        session.query(Candidate).filter_by(id=response.json()["candidate_id"]).one()
    )
    candidate.state = "accepted"
    session.flush()
    result = candidates.commit_candidate(session, candidate)
    session.flush()
    assert result["created"] is True

    brand_rows = (
        session.query(Assertion)
        .filter_by(asset_id=result["asset_id"], field_path="brand")
        .all()
    )
    assert len(brand_rows) == 1
    assert json.loads(brand_rows[0].value_json) == LABEL_BRAND


def test_brand_is_in_both_candidate_vocabularies() -> None:
    """The merge vocabulary and the committable vocabulary move together."""
    assert "brand" in candidates.LABEL_VISIBLE_FIELDS
    assert "brand" in candidates.ALLOWED_CANDIDATE_FIELDS
