"""SG-037 planning agent gates: offline, zero network (scripted provider).

TestClient over the real HTTP routes with a temp SQLite database, exactly the
`test_phase2_e2e.py` shape. Every provider call rides the ONE reader injection
seam (`app.services.providers.reader.provider_registry`) with a scripted
planning provider, so this file makes ZERO network attempts: the real adapter's
`_post` is patched to raise if it is ever reached.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Asset, GuardrailEvent, Household, Job, PlanningSuggestion
from app.models.provider_call import ProviderCall
from app.services.providers import reader as reader_mod
from app.services.providers.protocols import ProviderResult
from app.services.providers.router import ProviderError

CLASSIFICATION_FIELD = "plugin:expiry-tracker/classification"
EXPIRY_FIELD = "plugin:expiry-tracker/expiry_date"
SENTINEL_KEY = "sk-SENTINEL-DO-NOT-WRITE-037"


class PlanningScriptedProvider:
    """Schema-valid planning double: records calls, no network, cost 0.0."""

    def __init__(
        self,
        payload: dict[str, Any],
        *,
        provider_id: str = "scripted-plan",
        model_id: str = "scripted-plan-1",
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

    def estimate_cost(self, image_bytes: bytes, prompt: str) -> float:
        return self.estimate

    def extract_items(
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ) -> ProviderResult:
        self.invocations += 1
        self.images.append(image_bytes)
        self.prompts.append(prompt)
        if self.invocations <= self.fail_times:
            raise ProviderError("invalid_json", f"scripted fail {self.invocations}")
        return ProviderResult(
            normalized_output=deepcopy(self.payload),
            raw_payload={"scripted": True, "provider_id": self.provider_id},
            request_id="req-scripted-037",
            usage={"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
            cost=0.0,
            model_id=self.model_id,
            latency_ms=1.0,
        )


@pytest.fixture
def planning_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "planning.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Planning E2E Household")
    session.add(household)
    session.commit()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", None)

    from app.services.providers import opencode_go

    network_attempts: list[str] = []

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        network_attempts.append("post")
        raise AssertionError("network must never be attempted in the offline planning gates")

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
    provider: PlanningScriptedProvider,
    *,
    consent: bool = True,
) -> None:
    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", consent)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)


def _seed_asset(
    db: Session, household_id: str, label: str, *, expiry: str | None = "2026-09-16"
) -> tuple[Asset, str | None]:
    asset = Asset(household_id=household_id, display_name=label, asset_type="food")
    db.add(asset)
    db.flush()
    db.add(
        Assertion(
            asset_id=asset.id,
            field_path=CLASSIFICATION_FIELD,
            value_json=json.dumps({"category": "food_beverages", "label": label}),
            source_type="user",
            review_state="accepted",
        )
    )
    expiry_assertion_id: str | None = None
    if expiry is not None:
        expiry_assertion = Assertion(
            asset_id=asset.id,
            field_path=EXPIRY_FIELD,
            value_json=json.dumps({"expiry_date": expiry, "date_type": "expiry_date"}),
            source_type="user",
            review_state="accepted",
        )
        db.add(expiry_assertion)
        db.flush()
        expiry_assertion_id = expiry_assertion.id
    db.commit()
    return asset, expiry_assertion_id


def _item(
    asset_id: str,
    *,
    name: str = 'Use "Whole milk" before 2026-09-16',
    kind: str = "use_first",
    expiry: str | None = "2026-09-16",
) -> dict[str, Any]:
    return {
        "name": name,
        "expiry_date": expiry,
        "opened_date": None,
        "date_type": kind,
        "lot": asset_id,
        "confidence": 1.0,
        "uncertainty_reasons": [],
    }


def _payload(*items: dict[str, Any]) -> dict[str, Any]:
    return {"items": list(items), "unknowns": [], "needs_evidence": False}


def _run(client: TestClient, household_id: str) -> dict[str, Any]:
    response = client.post("/v1/planning/run", params={"household_id": household_id})
    assert response.status_code == 200, response.text
    return response.json()


def _fingerprint(db: Session) -> tuple[list[tuple[Any, ...]], list[tuple[Any, ...]], list[Any]]:
    assets = db.query(Asset).order_by(Asset.id).all()
    assertions = db.query(Assertion).order_by(Assertion.id).all()
    jobs = db.query(Job).all()
    return (
        [(a.id, a.display_name, a.status, a.version) for a in assets],
        [
            (x.id, x.asset_id, x.field_path, x.value_json, x.review_state)
            for x in assertions
        ],
        [(j.id, j.state) for j in jobs],
    )


def _written_text(db: Session) -> list[str]:
    blobs: list[str] = []
    for row in db.query(PlanningSuggestion).all():
        blobs += [row.kind, row.title, row.body_json, row.backing_refs_json, row.status]
    for event in db.query(GuardrailEvent).all():
        blobs += [event.kind, event.ref_ids_json, event.detail_json]
    for call in db.query(ProviderCall).all():
        blobs += [
            call.provider,
            call.model,
            call.prompt_template_version,
            call.input_hashes or "",
            call.output_payload or "",
            call.usage_json or "",
            call.error_state or "",
        ]
    return blobs


def test_run_writes_pending_suggestion_backing_refs_and_guardrail(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, network_attempts = planning_fixture
    asset, expiry_assertion_id = _seed_asset(session, household_id, "Whole milk")
    provider = PlanningScriptedProvider(_payload(_item(asset.id)))
    _enable(monkeypatch, provider)
    client = TestClient(app)

    result = _run(client, household_id)

    assert result["status"] == "ok"
    assert result["suggestion_count"] == 1
    assert provider.invocations == 1
    assert network_attempts == []

    suggestion = session.query(PlanningSuggestion).one()
    assert suggestion.status == "pending"
    assert suggestion.kind == "use_first"
    assert suggestion.title == 'Use "Whole milk" before 2026-09-16'
    refs = json.loads(suggestion.backing_refs_json)
    assert {"type": "asset", "id": asset.id, "label": "Whole milk", "category": "food_beverages"} in refs
    assert {"type": "assertion", "id": expiry_assertion_id, "field_path": EXPIRY_FIELD, "value": "2026-09-16"} in refs

    events = session.query(GuardrailEvent).filter_by(kind="suggestion").all()
    assert len(events) == 1
    assert json.loads(events[0].ref_ids_json) == [suggestion.id]
    assert json.loads(events[0].detail_json)["suggestion_count"] == 1

    call = session.query(ProviderCall).one()
    assert call.job_id is None
    assert call.prompt_template_version == "planning-v1"
    assert call.model == "scripted-plan-1"


def test_confirm_and_dismiss_transitions_with_422_on_illegal_moves(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, _ = planning_fixture
    first, _ = _seed_asset(session, household_id, "Milk")
    second, _ = _seed_asset(session, household_id, "Yoghurt")
    provider = PlanningScriptedProvider(
        _payload(_item(first.id, name="Use milk"), _item(second.id, name="Use yoghurt"))
    )
    _enable(monkeypatch, provider)
    client = TestClient(app)
    _run(client, household_id)
    ids = [s.id for s in session.query(PlanningSuggestion).order_by(PlanningSuggestion.id).all()]
    assert len(ids) == 2

    confirmed = client.post(
        f"/v1/planning/suggestions/{ids[0]}/confirm", params={"household_id": household_id}
    )
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["status"] == "confirmed"
    illegal_confirm = client.post(
        f"/v1/planning/suggestions/{ids[0]}/confirm", params={"household_id": household_id}
    )
    assert illegal_confirm.status_code == 422, illegal_confirm.text

    dismissed = client.post(
        f"/v1/planning/suggestions/{ids[1]}/dismiss",
        json={"reason": "already used the milk"},
        params={"household_id": household_id},
    )
    assert dismissed.status_code == 200, dismissed.text
    assert dismissed.json()["status"] == "dismissed"
    corrections = session.query(GuardrailEvent).filter_by(kind="correction").all()
    assert len(corrections) == 1
    assert json.loads(corrections[0].ref_ids_json) == [ids[1]]
    assert json.loads(corrections[0].detail_json)["reason"] == "already used the milk"

    illegal_dismiss = client.post(
        f"/v1/planning/suggestions/{ids[1]}/dismiss", params={"household_id": household_id}
    )
    assert illegal_dismiss.status_code == 422, illegal_dismiss.text


def test_dismiss_without_reason_writes_no_correction_event(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, _ = planning_fixture
    asset, _ = _seed_asset(session, household_id, "Milk")
    provider = PlanningScriptedProvider(_payload(_item(asset.id)))
    _enable(monkeypatch, provider)
    client = TestClient(app)
    _run(client, household_id)
    suggestion = session.query(PlanningSuggestion).one()

    response = client.post(
        f"/v1/planning/suggestions/{suggestion.id}/dismiss",
        params={"household_id": household_id},
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "dismissed"
    assert session.query(GuardrailEvent).filter_by(kind="correction").count() == 0


def test_no_consent_refuses_with_zero_calls_and_zero_rows(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, network_attempts = planning_fixture
    asset, _ = _seed_asset(session, household_id, "Milk")
    provider = PlanningScriptedProvider(_payload(_item(asset.id)))
    _enable(monkeypatch, provider, consent=False)
    client = TestClient(app)

    result = _run(client, household_id)

    assert result["status"] == "skipped"
    assert result["reason"] == "consent_disabled"
    assert provider.invocations == 0
    assert network_attempts == []
    assert session.query(PlanningSuggestion).count() == 0
    assert session.query(GuardrailEvent).count() == 0
    assert session.query(ProviderCall).count() == 0


def test_empty_catalog_yields_empty_list_with_guardrail_note(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, network_attempts = planning_fixture
    provider = PlanningScriptedProvider(_payload())
    _enable(monkeypatch, provider)
    client = TestClient(app)

    result = _run(client, household_id)

    assert result["status"] == "ok"
    assert result["suggestion_count"] == 0
    assert provider.invocations == 0
    assert network_attempts == []
    listed = client.get("/v1/planning/suggestions", params={"household_id": household_id})
    assert listed.status_code == 200, listed.text
    assert listed.json() == {"items": [], "total": 0}
    event = session.query(GuardrailEvent).one()
    assert json.loads(event.detail_json)["outcome"] == "empty_catalog"


def test_catalog_bytes_identical_before_and_after_run(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, _ = planning_fixture
    first, _ = _seed_asset(session, household_id, "Milk")
    _seed_asset(session, household_id, "Rice", expiry=None)
    provider = PlanningScriptedProvider(_payload(_item(first.id)))
    _enable(monkeypatch, provider)
    client = TestClient(app)
    before = _fingerprint(session)

    _run(client, household_id)

    after = _fingerprint(session)
    assert before == after, "a planning run must not execute or mutate anything"
    assert session.query(PlanningSuggestion).count() == 1


def test_no_key_material_in_any_written_row(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, _ = planning_fixture
    asset, _ = _seed_asset(session, household_id, "Milk")
    monkeypatch.setattr(settings, "opencode_api_key", SENTINEL_KEY)
    provider = PlanningScriptedProvider(_payload(_item(asset.id)))
    _enable(monkeypatch, provider)
    client = TestClient(app)

    _run(
        client,
        household_id,
    )

    for blob in _written_text(session):
        assert SENTINEL_KEY not in blob
        assert "sk-" not in blob


def test_list_filter_and_illegal_status_are_enforced(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, _ = planning_fixture
    asset, _ = _seed_asset(session, household_id, "Milk")
    provider = PlanningScriptedProvider(_payload(_item(asset.id)))
    _enable(monkeypatch, provider)
    client = TestClient(app)
    _run(client, household_id)
    suggestion = session.query(PlanningSuggestion).one()
    client.post(
        f"/v1/planning/suggestions/{suggestion.id}/confirm", params={"household_id": household_id}
    )

    pending = client.get("/v1/planning/suggestions", params={"household_id": household_id, "status": "pending"})
    assert pending.status_code == 200, pending.text
    assert pending.json()["total"] == 0
    confirmed = client.get(
        "/v1/planning/suggestions", params={"household_id": household_id, "status": "confirmed"}
    )
    assert confirmed.json()["total"] == 1
    illegal = client.get(
        "/v1/planning/suggestions", params={"household_id": household_id, "status": "deleted"}
    )
    assert illegal.status_code == 422, illegal.text


def test_household_mismatch_and_missing_suggestion(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, _ = planning_fixture
    asset, _ = _seed_asset(session, household_id, "Milk")
    provider = PlanningScriptedProvider(_payload(_item(asset.id)))
    _enable(monkeypatch, provider)
    client = TestClient(app)
    _run(client, household_id)
    suggestion = session.query(PlanningSuggestion).one()

    mismatch = client.post(
        f"/v1/planning/suggestions/{suggestion.id}/confirm", params={"household_id": "somewhere-else"}
    )
    assert mismatch.status_code == 403, mismatch.text
    missing = client.post(
        "/v1/planning/suggestions/does-not-exist/confirm",
        params={"household_id": household_id},
    )
    assert missing.status_code == 404, missing.text


def test_single_repair_turn_then_success(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, _ = planning_fixture
    asset, _ = _seed_asset(session, household_id, "Milk")
    provider = PlanningScriptedProvider(_payload(_item(asset.id)), fail_times=1)
    _enable(monkeypatch, provider)
    client = TestClient(app)

    result = _run(client, household_id)

    assert result["status"] == "ok"
    assert provider.invocations == 2
    assert session.query(PlanningSuggestion).count() == 1
    calls = session.query(ProviderCall).order_by(ProviderCall.created_at).all()
    assert len(calls) == 2
    assert calls[0].error_state is not None
    assert calls[1].error_state is None


def test_budget_refusal_before_any_call(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, network_attempts = planning_fixture
    asset, _ = _seed_asset(session, household_id, "Milk")
    provider = PlanningScriptedProvider(_payload(_item(asset.id)), estimate=1.0)
    _enable(monkeypatch, provider)
    monkeypatch.setattr(settings, "sg_per_job_cap", 0.01)
    client = TestClient(app)

    result = _run(client, household_id)

    assert result["status"] == "refused"
    assert provider.invocations == 0
    assert network_attempts == []
    assert session.query(ProviderCall).count() == 0


def test_prompt_is_versioned_and_carries_catalog_label_data(
    planning_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, household_id, _ = planning_fixture
    asset, _ = _seed_asset(session, household_id, "Whole milk")
    provider = PlanningScriptedProvider(_payload(_item(asset.id)))
    _enable(monkeypatch, provider)
    client = TestClient(app)

    from app.services.planning.service import load_planning_prompt

    text, version = load_planning_prompt()
    assert version == "planning-v1"
    assert "ExtractionOutput" in text

    _run(client, household_id)
    prompt = provider.prompts[0]
    assert "planning-v1" in prompt
    assert "Whole milk" in prompt
    assert household_id not in prompt
