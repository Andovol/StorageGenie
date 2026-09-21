"""SG-066 analytics gates: offline, zero network (scripted provider).

TestClient over the real HTTP routes with a temp SQLite database, exactly the
`test_planning.py` shape. The one provider seam
(`app.services.providers.reader.provider_registry`) is monkeypatched with a
scripted analytics provider, so this module makes ZERO network attempts: the
real adapter's `_post` is patched to raise if it is ever reached. The single
authorized metered run lives in the worklog, never in a test.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Asset, GuardrailEvent, Household, Job
from app.models.provider_call import ProviderCall
from app.services.providers import reader as reader_mod
from app.services.providers.protocols import ProviderResult
from app.services.providers.router import ProviderError

CLASSIFICATION_FIELD = "plugin:expiry-tracker/classification"
EXPIRY_FIELD = "plugin:expiry-tracker/expiry_date"
SENTINEL_KEY = "sk-SENTINEL-DO-NOT-WRITE-066"
STAT_SOURCE_TABLES = ("asset", "planning_suggestion", "review_task")


class AnalyticsScriptedProvider:
    """Schema-valid analytics double: records calls, no network, cost 0.0."""

    def __init__(
        self,
        payload: dict[str, Any],
        *,
        provider_id: str = "scripted-analytics",
        model_id: str = "scripted-analytics-1",
        fail_times: int = 0,
        estimate: float = 0.0,
    ) -> None:
        self.provider_id = provider_id
        self.model_id = model_id
        self.payload = payload
        self.fail_times = fail_times
        self.estimate = estimate
        self.invocations = 0
        self.images: list[bytes] = []
        self.prompts: list[str] = []
        self.usage: dict[str, Any] = {
            "prompt_tokens": 13,
            "completion_tokens": 9,
            "total_tokens": 22,
        }
        self.cost: float = 0.0
        self.latency_ms: float = 2.0

    def estimate_cost(self, image_bytes: bytes, prompt: str) -> float:
        return self.estimate

    def extract_items(
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ) -> ProviderResult:
        self.invocations += 1
        self.images.append(image_bytes)
        self.prompts.append(prompt)
        if self.invocations <= self.fail_times:
            exc = ProviderError("invalid_json", f"scripted fail {self.invocations}")
            exc.usage = dict(self.usage)
            exc.cost = self.cost
            exc.latency_ms = self.latency_ms
            raise exc
        return ProviderResult(
            normalized_output=deepcopy(self.payload),
            raw_payload={"scripted": True, "provider_id": self.provider_id},
            request_id="req-scripted-066",
            usage=dict(self.usage),
            cost=self.cost,
            model_id=self.model_id,
            latency_ms=self.latency_ms,
        )


@pytest.fixture
def analytics_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "analytics.db"
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Analytics E2E Household")
    session.add(household)
    session.commit()
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", None)

    from app.services.providers import opencode_go

    network_attempts: list[str] = []

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        network_attempts.append("post")
        raise AssertionError("network must never be attempted in the offline analytics gates")

    monkeypatch.setattr(opencode_go.OpenCodeGoProvider, "_post", _forbidden)

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, network_attempts
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _enable(
    monkeypatch: pytest.MonkeyPatch,
    provider: AnalyticsScriptedProvider,
    *,
    consent: bool = True,
) -> None:
    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", consent)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)


def _seed_asset(
    db: Session,
    household_id: str,
    label: str,
    *,
    category: str | None = None,
    expiry: date | None = None,
    status: str = "ACTIVE",
) -> Asset:
    asset = Asset(household_id=household_id, display_name=label, status=status)
    db.add(asset)
    db.flush()
    if category is not None:
        db.add(
            Assertion(
                asset_id=asset.id,
                field_path=CLASSIFICATION_FIELD,
                value_json=json.dumps({"category": category, "label": label}),
                source_type="user",
                review_state="accepted",
            )
        )
    if expiry is not None:
        db.add(
            Assertion(
                asset_id=asset.id,
                field_path=EXPIRY_FIELD,
                value_json=json.dumps(
                    {"expiry_date": expiry.isoformat(), "date_type": "expiry_date"}
                ),
                source_type="user",
                review_state="accepted",
            )
        )
    db.commit()
    return asset


def _item(sentence: str, *, stat_id: str | None, name: str | None = None) -> dict[str, Any]:
    return {
        "name": sentence,
        "expiry_date": None,
        "opened_date": None,
        "date_type": None,
        "lot": stat_id,
        "confidence": 1.0,
        "uncertainty_reasons": [],
    }


def _payload(*items: dict[str, Any]) -> dict[str, Any]:
    return {"items": list(items), "unknowns": [], "needs_evidence": False}


def _summary(client: TestClient, household_id: str) -> dict[str, Any]:
    response = client.get("/v1/analytics/summary", params={"household_id": household_id})
    assert response.status_code == 200, response.text
    return response.json()


def _insights(client: TestClient, household_id: str) -> Any:
    return client.post("/v1/analytics/insights", params={"household_id": household_id})


def _fingerprint(db: Session) -> tuple[list[Any], list[Any], list[str]]:
    assets = [(a.id, a.status, a.version) for a in db.query(Asset).order_by(Asset.id).all()]
    assertions = [
        (x.id, x.asset_id, x.field_path, x.value_json) for x in db.query(Assertion).order_by(Assertion.id).all()
    ]
    jobs = [row.id for row in db.query(Job).all()]
    return assets, assertions, jobs


def test_summary_stats_have_buckets_and_sources(analytics_fixture) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = analytics_fixture
    today = date.today()
    _seed_asset(session, household_id, "Milk", category="food_beverages", expiry=today - timedelta(days=2))
    _seed_asset(
        session, household_id, "Cream", category="cosmetics_personal_care", expiry=today + timedelta(days=3)
    )
    _seed_asset(
        session, household_id, "Pills", category="medicine_pharma", expiry=today + timedelta(days=20)
    )
    _seed_asset(
        session, household_id, "Rice", category="non_perishable", expiry=today + timedelta(days=120)
    )
    _seed_asset(session, household_id, "Mystery", category=None, expiry=None)
    client = TestClient(app)

    body = _summary(client, household_id)

    assert body["assets"]["total"] == 5
    assert body["assets"]["active"] == 5
    assert body["assets"]["by_status"] == {"ACTIVE": 5}
    assert body["categories"]["counts"]["food_beverages"] == 1
    assert body["categories"]["counts"]["cosmetics_personal_care"] == 1
    assert body["categories"]["counts"]["medicine_pharma"] == 1
    assert body["categories"]["counts"]["non_perishable"] == 1
    assert body["categories"]["uncategorized"] == 1
    assert body["expiry"]["expired"] == 1
    assert body["expiry"]["within_7_days"] == 1
    assert body["expiry"]["within_30_days"] == 1
    assert body["expiry"]["safe"] == 1
    assert body["expiry"]["unknown"] == 1
    assert body["waste"]["expired_untouched"] == 1
    ids = {entry["id"] for entry in body["stats"]}
    assert {"expiry.expired", "waste.expired_untouched", "category.food_beverages"} <= ids
    for entry in body["stats"]:
        assert entry["source"], entry
        assert any(table in entry["source"] for table in STAT_SOURCE_TABLES), entry

    taxonomy = client.get("/v1/taxonomy")
    assert taxonomy.status_code == 200, taxonomy.text
    served_ids = [
        category["id"]
        for plugin in taxonomy.json()["plugins"]
        for category in plugin["categories"]
    ]
    assert [entry["id"] for entry in body["categories"]["taxonomy"]] == served_ids


def test_empty_household_returns_zero_maps(analytics_fixture) -> None:  # type: ignore[no-untyped-def]
    session, _, _ = analytics_fixture
    empty = Household(name="Empty Household")
    session.add(empty)
    session.commit()
    client = TestClient(app)

    body = _summary(client, empty.id)

    assert body["assets"] == {"total": 0, "active": 0, "by_status": {}}
    assert all(count == 0 for count in body["categories"]["counts"].values())
    assert body["categories"]["uncategorized"] == 0
    assert all(count == 0 for count in body["expiry"].values())
    assert body["waste"]["expired_untouched"] == 0
    assert body["adherence"]["suggestions"] == {"pending": 0, "confirmed": 0, "dismissed": 0}
    assert body["expiry"]["unknown"] == 0


def test_unknown_household_is_404(analytics_fixture) -> None:  # type: ignore[no-untyped-def]
    client = TestClient(app)
    missing = client.get("/v1/analytics/summary", params={"household_id": "does-not-exist"})
    assert missing.status_code == 404, missing.text
    missing_post = _insights(client, "does-not-exist")
    assert missing_post.status_code == 404, missing_post.text


def test_household_isolation(analytics_fixture) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = analytics_fixture
    other = Household(name="Other Household")
    session.add(other)
    session.commit()
    _seed_asset(session, household_id, "Only A", category="food_beverages")
    _seed_asset(session, other.id, "B one", category="food_beverages")
    _seed_asset(session, other.id, "B two", category="food_beverages")
    client = TestClient(app)

    body_a = _summary(client, household_id)
    body_b = _summary(client, other.id)

    assert body_a["assets"]["total"] == 1
    assert body_a["categories"]["counts"]["food_beverages"] == 1
    assert body_b["assets"]["total"] == 2
    assert body_b["categories"]["counts"]["food_beverages"] == 2


def test_insights_grounded_run_writes_ledger_only(
    analytics_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network_attempts = analytics_fixture
    _seed_asset(session, household_id, "Milk", category="food_beverages", expiry=date.today() - timedelta(days=1))
    provider = AnalyticsScriptedProvider(
        _payload(
            _item("One active asset is already past its expiry date.", stat_id="waste.expired_untouched"),
            _item("There are 1 active assets recorded in total.", stat_id="assets.active"),
        )
    )
    _enable(monkeypatch, provider)
    client = TestClient(app)
    before = _fingerprint(session)

    response = _insights(client, household_id)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "ok"
    assert body["summary"] == (
        "One active asset is already past its expiry date. "
        "There are 1 active assets recorded in total."
    )
    assert body["cited_stat_ids"] == ["waste.expired_untouched", "assets.active"]
    assert {entry["id"] for entry in body["cited_stats"]} == {
        "waste.expired_untouched",
        "assets.active",
    }
    assert provider.invocations == 1
    assert network_attempts == []

    call = session.query(ProviderCall).one()
    assert call.job_id is None
    assert call.prompt_template_version == "analytics-insights-v1"
    assert call.model == "scripted-analytics-1"
    event = session.query(GuardrailEvent).one()
    assert event.kind == "insight"
    assert json.loads(event.detail_json)["outcome"] == "ok"
    assert _fingerprint(session) == before, "an insights run must not touch catalogue state"


def test_insights_consent_disabled_zero_rows(
    analytics_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network_attempts = analytics_fixture
    _seed_asset(session, household_id, "Milk", category="food_beverages")
    provider = AnalyticsScriptedProvider(_payload(_item("x", stat_id="assets.active")))
    _enable(monkeypatch, provider, consent=False)
    client = TestClient(app)

    response = _insights(client, household_id)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "skipped"
    assert body["reason"] == "consent_disabled"
    assert provider.invocations == 0
    assert network_attempts == []
    assert session.query(ProviderCall).count() == 0
    assert session.query(GuardrailEvent).count() == 0


def test_insights_ungrounded_citation_is_loud_502(
    analytics_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = analytics_fixture
    _seed_asset(session, household_id, "Milk", category="food_beverages")
    provider = AnalyticsScriptedProvider(
        _payload(_item("An invented claim.", stat_id="expiry.bogus"))
    )
    _enable(monkeypatch, provider)
    client = TestClient(app)

    response = _insights(client, household_id)

    assert response.status_code == 502, response.text
    assert "expiry.bogus" in response.json()["detail"]
    assert provider.invocations == 1
    assert session.query(ProviderCall).count() == 1
    event = session.query(GuardrailEvent).one()
    detail = json.loads(event.detail_json)
    assert detail["outcome"] == "ungrounded"
    assert detail["unresolved_stat_ids"] == ["expiry.bogus"]


def test_insights_without_any_citation_is_ungrounded(
    analytics_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = analytics_fixture
    _seed_asset(session, household_id, "Milk", category="food_beverages")
    provider = AnalyticsScriptedProvider(_payload(_item("A number-free blur.", stat_id=None)))
    _enable(monkeypatch, provider)
    client = TestClient(app)

    response = _insights(client, household_id)

    assert response.status_code == 502, response.text
    event = session.query(GuardrailEvent).one()
    assert json.loads(event.detail_json)["resolution"] == "no_citations"


def test_insights_empty_household_calls_nothing(
    analytics_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, _, network_attempts = analytics_fixture
    empty = Household(name="Empty Insights Household")
    session.add(empty)
    session.commit()
    provider = AnalyticsScriptedProvider(_payload(_item("x", stat_id="assets.active")))
    _enable(monkeypatch, provider)
    client = TestClient(app)

    response = _insights(client, empty.id)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "ok"
    assert body["reason"] == "empty_household"
    assert provider.invocations == 0
    assert network_attempts == []
    assert session.query(ProviderCall).count() == 0
    event = session.query(GuardrailEvent).one()
    assert json.loads(event.detail_json)["outcome"] == "empty_household"


def test_insights_budget_refusal_before_any_call(
    analytics_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network_attempts = analytics_fixture
    _seed_asset(session, household_id, "Milk", category="food_beverages")
    provider = AnalyticsScriptedProvider(
        _payload(_item("x", stat_id="assets.active")), estimate=1.0
    )
    _enable(monkeypatch, provider)
    monkeypatch.setattr(settings, "sg_per_job_cap", 0.01)
    client = TestClient(app)

    response = _insights(client, household_id)

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "refused"
    assert provider.invocations == 0
    assert network_attempts == []
    assert session.query(ProviderCall).count() == 0


def test_insights_single_repair_turn_then_success(
    analytics_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = analytics_fixture
    _seed_asset(session, household_id, "Milk", category="food_beverages")
    provider = AnalyticsScriptedProvider(
        _payload(_item("All clear.", stat_id="assets.active")), fail_times=1
    )
    _enable(monkeypatch, provider)
    client = TestClient(app)

    response = _insights(client, household_id)

    assert response.status_code == 200, response.text
    assert provider.invocations == 2
    calls = session.query(ProviderCall).order_by(ProviderCall.created_at).all()
    assert len(calls) == 2
    assert calls[0].error_state is not None
    assert calls[1].error_state is None


def test_insights_prompt_is_versioned_and_carries_stats(
    analytics_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = analytics_fixture
    _seed_asset(session, household_id, "Milk", category="food_beverages")
    provider = AnalyticsScriptedProvider(_payload(_item("x", stat_id="assets.active")))
    _enable(monkeypatch, provider)
    client = TestClient(app)

    from app.services.analytics.service import load_insights_prompt

    text, version = load_insights_prompt()
    assert version == "analytics-insights-v1"
    assert "ExtractionOutput" in text

    _insights(client, household_id)
    prompt = provider.prompts[0]
    assert "analytics-insights-v1" in prompt
    assert "assets.active" in prompt
    assert household_id not in prompt


def test_no_key_material_in_any_written_row(
    analytics_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = analytics_fixture
    _seed_asset(session, household_id, "Milk", category="food_beverages")
    monkeypatch.setattr(settings, "opencode_api_key", SENTINEL_KEY)
    provider = AnalyticsScriptedProvider(_payload(_item("x", stat_id="assets.active")))
    _enable(monkeypatch, provider)
    client = TestClient(app)

    response = _insights(client, household_id)
    assert response.status_code == 200, response.text

    blobs: list[str] = []
    for call in session.query(ProviderCall).all():
        blobs += [call.provider, call.model, call.output_payload or "", call.usage_json or ""]
    for event in session.query(GuardrailEvent).all():
        blobs += [event.kind, event.ref_ids_json, event.detail_json]
    for blob in blobs:
        assert SENTINEL_KEY not in blob
        assert "sk-" not in blob
