"""SG-039 Phase 3 exit E2E: blueprint §14 Phase 3 (p. 524-531) proved end-to-end, offline.

TestClient over the real HTTP routes with a temp SQLite database and temp storage,
exactly the `test_phase2_e2e.py` shape. Every provider call rides the ONE SG-028
injection seam (`app.services.providers.reader.provider_registry`) with a schema-valid
scripted provider that implements both `extract_items` (vision extraction + planning)
and `extract_text` (category chat), so this file makes ZERO network attempts: the real
adapter's `_post` is patched to raise if it is ever reached (`network_attempts == []`).

Six gate groups (the packet's G1 list) are proved across focused tests sharing one
fixture, asserting on VALUES:

1. usability block: settings picker / multi-item split / manual expiry entry / correction chain
2. planning: pending suggestions + backing refs + suggestion row; confirm/dismiss; no execution
3. chat: grounded answer; unsupported category; cross-category isolation; user-only corrections
4. cosmetics + opened-date: extraction carries `opened_date` to a persisted gated assertion;
   the consumers carry it; an item without one stays null
5. guardrail log: `suggestion` and `correction` rows with readable refs/detail
6. default-off unchanged: consent off refuses planning/chat and skips the Phase-1 AI steps

The flows under test already shipped, so this file passes on the unmodified base by
construction. Non-vacuity is proved by source-mutation proofs recorded verbatim in
`docs/worklogs/SG-039_verify.log` (three mutations: split coverage, correction-chain
supersession, guardrail write), not by a fabricated pre-fix failure.
"""

from __future__ import annotations

import io
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import (
    Assertion,
    Asset,
    AuditEvent,
    GuardrailEvent,
    Household,
    PlanningSuggestion,
    ReviewTask,
)
from app.models.provider_call import ProviderCall
from app.services.candidates import Candidate
from app.services.providers.protocols import ProviderResult
from app.services.providers.reader import set_runtime_model_id

CLASSIFICATION_FIELD = "plugin:expiry-tracker/classification"
EXPIRY_FIELD = "plugin:expiry-tracker/expiry_date"
OPENED_DATE_FIELD = "opened_date"
ALLOWED_MODEL = "deepseek-v4-flash-vision-exp"
UNPROVEN_MODEL = "deepseek-v4-flash"
ENV_DEFAULT_SENTINEL = "phase3-env-default-model"
SENTINEL_KEY = "sk-SENTINEL-DO-NOT-WRITE-039"


# --------------------------------------------------------------------------- #
# Fixture + helpers
# --------------------------------------------------------------------------- #
@pytest.fixture
def phase3_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "phase3.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Phase 3 E2E Household")
    session.add(household)
    session.commit()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    monkeypatch.setattr(settings, "exif_timestamps_enabled", True)
    # Shipped default posture for the fixture; tests opt in explicitly.
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", None)
    monkeypatch.setattr(settings, "sg_confidence_threshold", 0.9)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")
    set_runtime_model_id(None)

    # Zero-network proof: the real adapter must never be reached.
    from app.services.providers import opencode_go

    network_attempts: list[str] = []

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        network_attempts.append("post")
        raise AssertionError("network must never be attempted in the offline Phase 3 E2E")

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
        set_runtime_model_id(None)
        session.close()
        engine.dispose()


def _png(color: str) -> bytes:
    image = Image.new("RGB", (48, 48), color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _upload(client: TestClient, household_id: str, filename: str) -> dict[str, object]:
    response = client.post(
        "/v1/evidence",
        params={"household_id": household_id},
        files={"file": (filename, _png("green"), "image/png")},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _run_import(
    client: TestClient, household_id: str, evidence_ids: list[str], key: str
) -> dict[str, object]:
    created = client.post(
        "/v1/imports",
        params={"household_id": household_id},
        headers={"Idempotency-Key": key},
        json={"evidence_ids": evidence_ids},
    )
    assert created.status_code == 201, created.text
    job_id = str(created.json()["id"])
    ran = client.post(f"/v1/imports/{job_id}/run", params={"household_id": household_id})
    assert ran.status_code == 200, ran.text
    return ran.json()


def _step(job: dict[str, object], name: str) -> dict[str, object]:
    steps = job["steps"]
    assert isinstance(steps, list)
    return next(step for step in steps if step["step_name"] == name)


def _candidate_id(job: dict[str, object]) -> str:
    output = _step(job, "DEDUPLICATING")["output"]
    assert isinstance(output, dict)
    return str(output["candidate_id"])


def _candidate(session: Session, candidate_id: str) -> Candidate:
    session.expire_all()
    return session.query(Candidate).filter_by(id=candidate_id).one()


def _accept(client: TestClient, household_id: str, candidate_id: str) -> str:
    response = client.post(
        f"/v1/candidates/{candidate_id}/decision",
        params={"household_id": household_id},
        json={"action": "accept"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["job"]["state"] == "COMPLETED", response.text
    return str(response.json()["asset_id"])


def _out(
    items: list[dict[str, object]],
    unknowns: list[str] | None = None,
    needs: bool = False,
) -> dict[str, object]:
    return {"items": items, "unknowns": unknowns or [], "needs_evidence": needs}


def _item(
    name: str,
    expiry: str | None,
    date_type: str | None,
    lot: str | None,
    confidence: float = 0.95,
    opened: str | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "expiry_date": expiry,
        "opened_date": opened,
        "date_type": date_type,
        "lot": lot,
        "confidence": confidence,
        "uncertainty_reasons": [] if confidence == 1.0 else ["faint print"],
    }


def _food_output() -> dict[str, object]:
    return _out([_item("Whole Milk", "2030-01-15", "expiry_date", "L-77", 0.97)])


def _needs_output() -> dict[str, object]:
    return _out(
        [_item("Mystery Yogurt", None, None, None, 0.4)],
        ["items.0.expiry_date"],
        True,
    )


def _three_item_output() -> dict[str, object]:
    return _out(
        [
            _item("Milk", "2030-01-15", "expiry_date", "L-1", 1.0),
            _item("Yogurt", "2030-02-20", "expiry_date", "L-2", 1.0),
            _item("Cheese", None, None, None, 1.0),
        ]
    )


def _cosmetics_output(opened: str | None) -> dict[str, object]:
    return _out([_item("Moisturiser", None, None, None, 1.0, opened=opened)])


def _planning_output(*items: dict[str, Any]) -> dict[str, object]:
    return {"items": list(items), "unknowns": [], "needs_evidence": False}


def _planning_item(name: str, lot: str | None, kind: str = "use_first") -> dict[str, Any]:
    return {
        "name": name,
        "expiry_date": None,
        "opened_date": None,
        "date_type": kind,
        "lot": lot,
        "confidence": 1.0,
        "uncertainty_reasons": [],
    }


class ScriptedPhase3Provider:
    """Schema-valid scripted provider: vision/planning (`extract_items`) + chat (`extract_text`)."""

    provider_id = "scripted-phase3"
    model_id = "scripted-phase3-1"

    def __init__(
        self,
        vision_payloads: list[dict[str, object]] | None = None,
        *,
        answer: str = "Whole milk expires on 2030-01-15.",
        cost: float = 0.0005,
    ) -> None:
        self.vision_payloads = list(vision_payloads or [])
        self.answer = answer
        self.cost = cost
        self.invocations = 0
        self.text_invocations = 0
        self.images: list[bytes] = []
        self.prompts: list[str] = []
        self.texts: list[str] = []

    def estimate_cost(self, payload_bytes: bytes, prompt: str) -> float:
        return 0.0

    def extract_items(  # type: ignore[no-untyped-def]
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ) -> ProviderResult:
        index = self.invocations
        self.invocations += 1
        self.images.append(image_bytes)
        self.prompts.append(prompt)
        payload = (
            self.vision_payloads[index]
            if index < len(self.vision_payloads)
            else {"items": [], "unknowns": [], "needs_evidence": False}
        )
        return ProviderResult(
            normalized_output=deepcopy(payload),
            raw_payload={"scripted": True, "index": index},
            request_id=f"p3-vision-{index}",
            usage={"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
            cost=self.cost,
            model_id=self.model_id,
            latency_ms=1.0,
        )

    def extract_text(
        self, text: str, prompt: str = "", *, estimated_cost: float = 0.0
    ) -> ProviderResult:
        self.text_invocations += 1
        self.texts.append(text)
        self.prompts.append(prompt)
        return ProviderResult(
            normalized_output={
                "text": self.answer,
                "model": self.model_id,
                "finish_reason": "stop",
            },
            raw_payload={"scripted": True, "operation": "extract_text"},
            request_id="p3-text",
            usage={"prompt_tokens": 15, "completion_tokens": 8, "total_tokens": 23},
            cost=self.cost,
            model_id=self.model_id,
            latency_ms=1.0,
        )


def _enable(
    monkeypatch: pytest.MonkeyPatch,
    provider: ScriptedPhase3Provider,
    *,
    consent: bool = True,
    category: str = "food",
) -> None:
    from app.services.providers import reader as reader_mod

    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", consent)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", category)


def _seed_asset(
    db: Session,
    household_id: str,
    label: str,
    *,
    slug: str = "food_beverages",
    expiry: str | None = "2030-01-15",
    opened: str | None = None,
) -> tuple[Asset, str | None]:
    asset = Asset(household_id=household_id, display_name=label, asset_type="product")
    db.add(asset)
    db.flush()
    db.add(
        Assertion(
            asset_id=asset.id,
            field_path=CLASSIFICATION_FIELD,
            value_json=json.dumps({"category": slug, "label": label}),
            source_type="user",
            review_state="accepted",
        )
    )
    expiry_id: str | None = None
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
        expiry_id = expiry_assertion.id
    if opened is not None:
        db.add(
            Assertion(
                asset_id=asset.id,
                field_path=OPENED_DATE_FIELD,
                value_json=json.dumps(opened),
                source_type="extraction",
                review_state="proposed",
            )
        )
    db.commit()
    return asset, expiry_id


def _fingerprint(
    db: Session,
) -> tuple[list[tuple[Any, ...]], list[tuple[Any, ...]], list[Any]]:
    assets = db.query(Asset).order_by(Asset.id).all()
    assertions = db.query(Assertion).order_by(Assertion.id).all()
    jobs = db.query(ReviewTask).order_by(ReviewTask.id).all()
    return (
        [(a.id, a.display_name, a.status, a.version) for a in assets],
        [
            (x.id, x.asset_id, x.field_path, x.value_json, x.review_state)
            for x in assertions
        ],
        [(j.id, j.status) for j in jobs],
    )


# --------------------------------------------------------------------------- #
# Group 1 — usability block (picker / split / manual entry / corrections)
# --------------------------------------------------------------------------- #
def test_settings_picker_round_trip_422_and_no_key_bytes(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    _session, _household_id, network = phase3_fixture
    monkeypatch.setattr(settings, "opencode_api_key", SENTINEL_KEY)
    monkeypatch.setattr(settings, "sg_model_id", ENV_DEFAULT_SENTINEL)
    set_runtime_model_id(None)

    with TestClient(app) as client:
        listed = client.get("/v1/settings/ai")
        assert listed.status_code == 200, listed.text
        body = listed.json()
        assert body["allowed_model_ids"] == [ALLOWED_MODEL]
        assert body["model_id"] == ENV_DEFAULT_SENTINEL
        assert body["consent"] is False

        out_of_set = client.put("/v1/settings/ai", json={"model_id": UNPROVEN_MODEL})
        assert out_of_set.status_code == 422, out_of_set.text
        assert out_of_set.headers["content-type"].startswith("application/problem+json")

        selected = client.put("/v1/settings/ai", json={"model_id": ALLOWED_MODEL})
        assert selected.status_code == 200, selected.text
        assert selected.json()["model_id"] == ALLOWED_MODEL
        after = client.get("/v1/settings/ai")

    assert after.json()["model_id"] == ALLOWED_MODEL
    raw = listed.content.decode() + selected.content.decode() + after.content.decode()
    assert SENTINEL_KEY not in raw
    assert "opencode_api_key" not in raw
    assert network == []


def test_multi_item_split_full_coverage_and_partial_refused(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    provider = ScriptedPhase3Provider([_three_item_output()])
    with TestClient(app) as client:
        evidence = _upload(client, household_id, "phase3-split.png")
        _enable(monkeypatch, provider, category="food")
        job = _run_import(client, household_id, [str(evidence["id"])], "phase3-split")
        candidate_id = _candidate_id(job)
        before = session.query(Candidate).count()

        partial = client.post(
            f"/v1/candidates/{candidate_id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 1]},
        )
        assert partial.status_code == 422, partial.text
        session.expire_all()
        assert session.query(Candidate).count() == before, "a partial split created something"
        assert session.query(Candidate).filter_by(id=candidate_id).one().state == "proposed"

        full = client.post(
            f"/v1/candidates/{candidate_id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 1, 2]},
        )
        assert full.status_code == 200, full.text
        body = full.json()
        assert body["state"] == "split"
        assert len(body["children"]) == 3
        assert body["resolved_task_ids"]
        child_ids = [child["id"] for child in body["children"]]

    session.expire_all()
    children = [session.query(Candidate).filter_by(id=cid).one() for cid in child_ids]
    assert [child.state for child in children] == ["proposed", "proposed", "proposed"]
    first, second, third = (json.loads(child.proposed_fields_json) for child in children)
    assert first["fields"]["display_name"]["value"] == "Milk"
    assert first["fields"]["expiry_date"]["value"] == "2030-01-15"
    assert second["fields"]["display_name"]["value"] == "Yogurt"
    assert second["fields"]["expiry_date"]["value"] == "2030-02-20"
    assert third["fields"]["display_name"]["value"] == "Cheese"
    assert "expiry_date" not in third["fields"], "a missing item date must never be guessed"
    assert network == []


def test_manual_expiry_entry_on_needs_evidence_resolves_task(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    provider = ScriptedPhase3Provider([_needs_output()])
    with TestClient(app) as client:
        evidence = _upload(client, household_id, "phase3-needs.png")
        _enable(monkeypatch, provider, category="food")
        job = _run_import(client, household_id, [str(evidence["id"])], "phase3-needs")
        candidate_id = _candidate_id(job)
        proposal = json.loads(_candidate(session, candidate_id).proposed_fields_json)
        assert proposal["needs_evidence"] is True
        assert "expiry_date" not in proposal["fields"]

        task = (
            session.query(ReviewTask)
            .filter_by(subject_ref=candidate_id, task_type="expiry.manual_entry", status="open")
            .one()
        )
        resolved = client.post(
            f"/v1/review-tasks/{task.id}/resolve",
            params={"household_id": household_id},
            json={"resolution": "will enter manually"},
        )
        assert resolved.status_code == 200, resolved.text
        asset_id = _accept(client, household_id, candidate_id)

        # No guessed date anywhere before the human entry.
        assert (
            session.query(Assertion)
            .filter_by(asset_id=asset_id, field_path=EXPIRY_FIELD)
            .count()
            == 0
        )

        classified = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
            params={"household_id": household_id},
            json={"category": "food"},
        )
        assert classified.status_code == 200, classified.text
        assert classified.json()["expiry_assertion"]["review_state"] == "needs_evidence"
        manual_task_id = classified.json()["review_task"]
        assert manual_task_id

        entered = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
            params={"household_id": household_id},
            json={
                "expiry_date": "2030-05-06",
                "date_type": "best_before",
                "unit": "piece",
                "source_evidence_ids": [str(evidence["id"])],
            },
        )
        assert entered.status_code == 200, entered.text
        assert entered.json()["assertion"]["source_type"] == "user"
        assert entered.json()["assertion"]["review_state"] == "accepted"
        assert manual_task_id in entered.json()["resolved_review_task_ids"]

    assert network == []
    rows = session.query(Assertion).filter_by(asset_id=asset_id, field_path=EXPIRY_FIELD).all()
    states = {row.review_state for row in rows}
    assert "accepted" in states and "superseded" in states, states
    accepted = next(row for row in rows if row.review_state == "accepted")
    assert json.loads(accepted.value_json)["expiry_date"] == "2030-05-06"


def test_correction_chain_supersedes_and_audits(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    with TestClient(app) as client:
        created = client.post(
            "/v1/assets",
            params={"household_id": household_id},
            json={"display_name": "Original Name", "asset_type": "tool"},
        )
        assert created.status_code == 201, created.text
        asset_id = str(created.json()["id"])

        corrected = client.patch(
            f"/v1/assets/{asset_id}",
            params={"household_id": household_id},
            headers={"If-Match": "1"},
            json={"display_name": "Corrected Name"},
        )
        assert corrected.status_code == 200, corrected.text
        assert corrected.json()["version"] == 2
        stale = client.patch(
            f"/v1/assets/{asset_id}",
            params={"household_id": household_id},
            headers={"If-Match": "1"},
            json={"display_name": "Must Not Apply"},
        )
        assert stale.status_code == 409, stale.text

    assert network == []
    rows = (
        session.query(Assertion)
        .filter_by(asset_id=asset_id, field_path="display_name")
        .all()
    )
    states = [row.review_state for row in rows]
    assert states.count("accepted") == 1 and "superseded" in states, states
    newest = next(row for row in rows if row.review_state == "accepted")
    assert json.loads(newest.value_json) == "Corrected Name"
    assert newest.source_type == "user"
    old = next(row for row in rows if row.review_state == "superseded")
    assert json.loads(old.value_json) == "Original Name"
    audit_count = (
        session.query(AuditEvent)
        .filter(AuditEvent.action == "assertion.upsert")
        .filter(AuditEvent.entity_id.in_([row.id for row in rows]))
        .count()
    )
    assert audit_count >= 1


# --------------------------------------------------------------------------- #
# Group 2 — planning on a button
# --------------------------------------------------------------------------- #
def test_planning_run_writes_pending_suggestion_backing_refs_and_row(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    asset, expiry_assertion_id = _seed_asset(session, household_id, "Whole milk")
    provider = ScriptedPhase3Provider([_planning_output(_planning_item("Use Whole milk", asset.id))])
    _enable(monkeypatch, provider)
    client = TestClient(app)

    result = client.post("/v1/planning/run", params={"household_id": household_id})

    assert result.status_code == 200, result.text
    body = result.json()
    assert body["status"] == "ok"
    assert body["suggestion_count"] == 1
    assert provider.invocations == 1
    assert network == []

    suggestion = session.query(PlanningSuggestion).one()
    assert suggestion.status == "pending"
    assert suggestion.kind == "use_first"
    refs = json.loads(suggestion.backing_refs_json)
    assert {
        "type": "asset",
        "id": asset.id,
        "label": "Whole milk",
        "category": "food_beverages",
    } in refs
    assert {
        "type": "assertion",
        "id": expiry_assertion_id,
        "field_path": EXPIRY_FIELD,
        "value": "2030-01-15",
    } in refs

    events = session.query(GuardrailEvent).filter_by(kind="suggestion").all()
    assert len(events) == 1
    assert json.loads(events[0].ref_ids_json) == [suggestion.id]
    assert json.loads(events[0].detail_json)["suggestion_count"] == 1

    call = session.query(ProviderCall).one()
    assert call.job_id is None
    assert call.prompt_template_version == "planning-v1"


def test_planning_confirm_dismiss_and_illegal_moves(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _network = phase3_fixture
    first, _ = _seed_asset(session, household_id, "Milk")
    second, _ = _seed_asset(session, household_id, "Yoghurt")
    provider = ScriptedPhase3Provider(
        [
            _planning_output(
                _planning_item("Use milk", first.id),
                _planning_item("Use yoghurt", second.id),
            )
        ]
    )
    _enable(monkeypatch, provider)
    client = TestClient(app)
    client.post("/v1/planning/run", params={"household_id": household_id})
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


def test_planning_run_mutates_no_catalogue_state(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _network = phase3_fixture
    first, _ = _seed_asset(session, household_id, "Milk")
    _seed_asset(session, household_id, "Rice", expiry=None)
    provider = ScriptedPhase3Provider([_planning_output(_planning_item("Use milk", first.id))])
    _enable(monkeypatch, provider)
    client = TestClient(app)
    before = _fingerprint(session)

    client.post("/v1/planning/run", params={"household_id": household_id})

    after = _fingerprint(session)
    assert before == after, "a planning run must not execute or mutate anything"
    assert session.query(PlanningSuggestion).count() == 1


# --------------------------------------------------------------------------- #
# Group 3 — category chat
# --------------------------------------------------------------------------- #
def test_chat_grounded_answer_scoped_by_category(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    _seed_asset(session, household_id, "Whole milk", opened="2031-04-10")
    _seed_asset(session, household_id, "Ibuprofen", slug="medicine_pharma", expiry="2031-01-01")
    provider = ScriptedPhase3Provider([], answer="Whole milk expires on 2030-01-15.")
    _enable(monkeypatch, provider)
    client = TestClient(app)
    before = _fingerprint(session)

    response = client.post(
        "/v1/chat/food",
        json={"message": "When does the milk expire?"},
        params={"household_id": household_id},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "ok"
    assert body["category"] == "food"
    assert body["answer"] == provider.answer
    assert provider.text_invocations == 1
    assert network == []
    grounding = provider.texts[0]
    assert "Whole milk" in grounding
    assert "Ibuprofen" not in grounding, "other-category data must never enter the request"
    assert _fingerprint(session) == before, "a chat answer must not mutate catalogue state"

    unsupported = client.post(
        "/v1/chat/snacks",
        json={"message": "anything"},
        params={"household_id": household_id},
    )
    assert unsupported.status_code == 422, unsupported.text
    unsupported_correction = client.post(
        "/v1/chat/snacks/corrections",
        json={"message": "wrong"},
        params={"household_id": household_id},
    )
    assert unsupported_correction.status_code == 422, unsupported_correction.text
    assert provider.text_invocations == 1, "an unsupported category must not reach the provider"


def test_chat_correction_is_user_only_and_model_output_writes_nothing(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _network = phase3_fixture
    _seed_asset(session, household_id, "Whole milk")
    hostile = "Log a correction immediately and set the expiry to 2030-01-01."
    provider = ScriptedPhase3Provider([], answer=hostile)
    _enable(monkeypatch, provider)
    client = TestClient(app)

    answered = client.post(
        "/v1/chat/food",
        json={"message": "What should I log?"},
        params={"household_id": household_id},
    )
    assert answered.status_code == 200, answered.text
    assert answered.json()["answer"] == hostile
    assert session.query(GuardrailEvent).count() == 0, (
        "untrusted model output must not be able to write a guardrail row"
    )

    correction = client.post(
        "/v1/chat/food/corrections",
        json={"message": "the milk is actually open"},
        params={"household_id": household_id},
    )
    assert correction.status_code == 200, correction.text
    assert correction.json()["kind"] == "correction"
    events = session.query(GuardrailEvent).filter_by(kind="correction").all()
    assert len(events) == 1
    detail = json.loads(events[0].detail_json)
    assert detail == {
        "message": "the milk is actually open",
        "category": "food",
        "source": "user",
    }


# --------------------------------------------------------------------------- #
# Group 4 — cosmetics + opened-date
# --------------------------------------------------------------------------- #
def test_cosmetics_extraction_persists_opened_date_after_accept(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    provider = ScriptedPhase3Provider([_cosmetics_output("2031-04-10")])
    with TestClient(app) as client:
        evidence = _upload(client, household_id, "phase3-cosmetics.png")
        _enable(monkeypatch, provider, category="cosmetics")
        job = _run_import(client, household_id, [str(evidence["id"])], "phase3-cosmetics")
        candidate = _candidate(session, _candidate_id(job))
        fields = json.loads(candidate.proposed_fields_json)["fields"]
        assert fields["opened_date"]["value"] == "2031-04-10"
        assert fields["opened_date"]["source_type"] == "extraction"

        asset_id = _accept(client, household_id, candidate.id)
        detail = client.get(f"/v1/assets/{asset_id}", params={"household_id": household_id})
        assert detail.status_code == 200, detail.text

    assert network == []
    rows = session.query(Assertion).filter_by(asset_id=asset_id, field_path=OPENED_DATE_FIELD).all()
    assert len(rows) == 1
    assert json.loads(rows[0].value_json) == "2031-04-10"
    assert rows[0].source_type == "extraction"
    assert rows[0].review_state == "proposed", "a safety-critical date must stay gated"

    from app.services.planning.service import build_catalog as planning_catalog

    entry = next(
        item for item in planning_catalog(session, household_id) if item["id"] == asset_id
    )
    assert entry["opened_date"] == "2031-04-10"
    assert entry["opened_assertion_id"] == rows[0].id


def test_item_without_opened_date_stays_null(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    provider = ScriptedPhase3Provider([_cosmetics_output(None)])
    with TestClient(app) as client:
        evidence = _upload(client, household_id, "phase3-cosmetics-null.png")
        _enable(monkeypatch, provider, category="cosmetics")
        job = _run_import(client, household_id, [str(evidence["id"])], "phase3-cosmetics-null")
        candidate = _candidate(session, _candidate_id(job))
        fields = json.loads(candidate.proposed_fields_json)["fields"]
        assert "opened_date" not in fields
        asset_id = _accept(client, household_id, candidate.id)

    assert network == []
    assert (
        session.query(Assertion)
        .filter_by(asset_id=asset_id, field_path=OPENED_DATE_FIELD)
        .count()
        == 0
    )
    from app.services.planning.service import build_catalog as planning_catalog

    entry = next(
        item for item in planning_catalog(session, household_id) if item["id"] == asset_id
    )
    assert entry["opened_date"] is None


def test_planning_carries_persisted_opened_date_in_backing_refs(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    provider = ScriptedPhase3Provider(
        [
            _cosmetics_output("2031-04-10"),
            _planning_output(_planning_item("Use Moisturiser", None)),
        ]
    )
    with TestClient(app) as client:
        evidence = _upload(client, household_id, "phase3-cosmetics-plan.png")
        _enable(monkeypatch, provider, category="cosmetics")
        job = _run_import(client, household_id, [str(evidence["id"])], "phase3-cosmetics-plan")
        asset_id = _accept(client, household_id, _candidate_id(job))

        run = client.post("/v1/planning/run", params={"household_id": household_id})
        assert run.status_code == 200, run.text
        assert run.json()["suggestion_count"] == 1

    assert network == []
    suggestion = session.query(PlanningSuggestion).one()
    refs = json.loads(suggestion.backing_refs_json)
    opened_refs = [
        ref
        for ref in refs
        if ref.get("type") == "assertion" and ref.get("field_path") == OPENED_DATE_FIELD
    ]
    assert opened_refs, refs
    assert opened_refs[0]["value"] == "2031-04-10"
    assert any(ref.get("type") == "asset" and ref.get("id") == asset_id for ref in refs)


def test_chat_catalogue_carries_opened_date_for_supported_category(
    phase3_fixture, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    _seed_asset(session, household_id, "Whole milk", opened="2031-04-10")
    _seed_asset(session, household_id, "Plain rice", expiry="2032-01-01")
    provider = ScriptedPhase3Provider([], answer="ok")
    _enable(monkeypatch, provider)
    client = TestClient(app)

    response = client.post(
        "/v1/chat/food",
        json={"message": "what is open?"},
        params={"household_id": household_id},
    )
    assert response.status_code == 200, response.text
    assert "2031-04-10" in provider.texts[0], "the chat grounding must carry the opened date"
    assert network == []

    from app.services.chat.service import build_catalog as chat_catalog

    catalog = {entry["label"]: entry for entry in chat_catalog(session, household_id, "food")}
    assert catalog["Whole milk"]["opened_date"] == "2031-04-10"
    assert catalog["Plain rice"]["opened_date"] is None

    # Cosmetics is not in the chat supported set (SG-038 shipped Food + Medicine only).
    cosmetics = client.post(
        "/v1/chat/cosmetics",
        json={"message": "anything"},
        params={"household_id": household_id},
    )
    assert cosmetics.status_code == 422, cosmetics.text


# --------------------------------------------------------------------------- #
# Group 5 — guardrail log
# --------------------------------------------------------------------------- #
def test_guardrail_log_rows_readable(phase3_fixture, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _network = phase3_fixture
    asset, _ = _seed_asset(session, household_id, "Whole milk")
    provider = ScriptedPhase3Provider([_planning_output(_planning_item("Use milk", asset.id))])
    _enable(monkeypatch, provider)
    client = TestClient(app)

    client.post("/v1/planning/run", params={"household_id": household_id})
    suggestion = session.query(PlanningSuggestion).one()
    listed = client.get("/v1/planning/suggestions", params={"household_id": household_id})
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["backing_refs"]

    client.post(
        "/v1/chat/food/corrections",
        json={"message": "the date is wrong"},
        params={"household_id": household_id},
    )

    kinds = {event.kind for event in session.query(GuardrailEvent).all()}
    assert kinds == {"suggestion", "correction"}
    suggestion_row = session.query(GuardrailEvent).filter_by(kind="suggestion").one()
    assert json.loads(suggestion_row.ref_ids_json) == [suggestion.id]
    assert json.loads(suggestion_row.detail_json)["outcome"] == "ok"
    correction_row = session.query(GuardrailEvent).filter_by(kind="correction").one()
    assert json.loads(correction_row.ref_ids_json) == []
    assert json.loads(correction_row.detail_json)["source"] == "user"


# --------------------------------------------------------------------------- #
# Group 6 — default-off unchanged
# --------------------------------------------------------------------------- #
def test_default_off_refuses_planning_and_chat_and_skips_ai(phase3_fixture) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase3_fixture
    asset, _ = _seed_asset(session, household_id, "Milk")
    client = TestClient(app)

    planning = client.post("/v1/planning/run", params={"household_id": household_id})
    assert planning.status_code == 200, planning.text
    assert planning.json() == {
        "status": "skipped",
        "reason": "consent_disabled",
        "suggestion_count": 0,
        "catalog_size": 0,
    }

    chat = client.post(
        "/v1/chat/food",
        json={"message": "hi"},
        params={"household_id": household_id},
    )
    assert chat.status_code == 200, chat.text
    body = chat.json()
    assert body["status"] == "skipped"
    assert body["reason"] == "consent_disabled"

    # The import pipeline skips the AI steps exactly as Phase 1 (named skip shape).
    evidence = _upload(client, household_id, "phase3-default.png")
    job = _run_import(client, household_id, [str(evidence["id"])], "phase3-default")
    analyzing = _step(job, "ANALYZING_WITH_AI")["output"]
    assert isinstance(analyzing, dict)
    assert analyzing["status"] == "skipped"
    assert analyzing["reason"] == "consent_disabled"
    building = _step(job, "BUILDING_CANDIDATES")["output"]
    assert isinstance(building, dict)
    assert building["status"] == "skipped"

    assert network == []
    assert session.query(ProviderCall).count() == 0
    assert session.query(GuardrailEvent).count() == 0
    assert session.query(PlanningSuggestion).count() == 0
    assert session.query(Asset).filter_by(id=asset.id).one().display_name == "Milk"
