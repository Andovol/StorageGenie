"""SG-030 Phase 2 exit E2E: blueprint:522 proved end-to-end, offline.

TestClient over the real HTTP routes with a temp SQLite database and temp
storage, exactly the `test_phase1_e2e.py` shape. Every provider call rides the
ONE SG-028 injection seam (`app.services.providers.reader.provider_registry`)
with a schema-valid scripted provider, so this file makes ZERO network
attempts: the real adapter's `_post` is patched to raise if it is ever reached.

Six behaviours (the packet's G1 numbered list) are proved by six focused tests
sharing one fixture shape.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Asset, AuditEvent, Household, ReviewTask
from app.models.provider_call import ProviderCall
from app.services.candidates import GATED_FIELDS, Candidate
from app.services.providers.protocols import ProviderResult

P2_EXPIRY_FIELD = "plugin:expiry-tracker/expiry_date"


# --------------------------------------------------------------------------- #
# Fixture + helpers
# --------------------------------------------------------------------------- #
@pytest.fixture
def phase2_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "phase2.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Phase 2 E2E Household")
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

    # Zero-network proof: the real adapter must never be reached.
    from app.services.providers import opencode_go

    network_attempts: list[str] = []

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        network_attempts.append("post")
        raise AssertionError("network must never be attempted in the offline E2E")

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


def _png(color: str) -> bytes:
    image = Image.new("RGB", (48, 48), color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _upload(client: TestClient, household_id: str, filename: str, data: bytes) -> dict[str, object]:
    response = client.post(
        "/v1/evidence",
        params={"household_id": household_id},
        files={"file": (filename, data, "image/png")},
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


def _out(items: list[dict[str, object]], unknowns: list[str] | None = None, needs: bool = False) -> dict[str, object]:
    return {"items": items, "unknowns": unknowns or [], "needs_evidence": needs}


def _item(
    name: str,
    expiry: str | None,
    date_type: str | None,
    lot: str | None,
    confidence: float = 0.95,
    reasons: list[str] | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "expiry_date": expiry,
        "date_type": date_type,
        "lot": lot,
        "confidence": confidence,
        "uncertainty_reasons": reasons or ["faint print"],
    }


def _food_output() -> dict[str, object]:
    return _out([_item("Whole Milk", "2030-01-15", "expiry_date", "L-77", 0.97, ["faint lot"])])


def _medicine_output() -> dict[str, object]:
    return _out([_item("Paracetamol", "2029-11-30", "expiry_date", "MED-42", 0.94, ["partial label"])])


def _needs_output() -> dict[str, object]:
    return _out(
        [_item("Mystery Yogurt", None, None, None, 0.4, ["blur"])],
        ["items.0.expiry_date"],
        True,
    )


class ScriptedPhase2Provider:
    """Schema-valid scripted provider with a real (scripted) cost per call."""

    provider_id = "p2-scripted"
    model_id = "p2-scripted-model"

    def __init__(self, payloads: list[dict[str, object]], *, cost: float = 0.0005) -> None:
        self.payloads = list(payloads)
        self.cost = cost
        self.invocations = 0
        self.images: list[bytes] = []
        self.prompts: list[str] = []

    def extract_items(  # type: ignore[no-untyped-def]
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ):
        index = self.invocations
        self.invocations += 1
        self.images.append(image_bytes)
        self.prompts.append(prompt)
        payload = self.payloads[index]
        return ProviderResult(
            normalized_output=payload,
            raw_payload={"scripted": True, "index": index},
            request_id=f"p2-{index}",
            usage={"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
            cost=self.cost,
            model_id=self.model_id,
            latency_ms=1.0,
        )


def _enable(
    monkeypatch: pytest.MonkeyPatch,
    provider: ScriptedPhase2Provider,
    *,
    category: str = "food",
) -> None:
    from app.services.providers import reader as reader_mod

    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", category)
    monkeypatch.setattr(settings, "sg_confidence_threshold", 0.9)


# --------------------------------------------------------------------------- #
# 1. AI proposes candidates with expiry for Food AND Medicine
# --------------------------------------------------------------------------- #
def test_ai_proposes_expiry_candidates_for_food_and_medicine(phase2_fixture, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase2_fixture
    provider = ScriptedPhase2Provider([_food_output(), _medicine_output()])
    with TestClient(app) as client:
        food_evidence = _upload(client, household_id, "phase2-food.png", _png("green"))
        _enable(monkeypatch, provider, category="food")
        food_job = _run_import(client, household_id, [str(food_evidence["id"])], "phase2-food")
        food_candidate = _candidate(session, _candidate_id(food_job))
        food_proposal = json.loads(food_candidate.proposed_fields_json)
        assert food_proposal["ai_items"][0]["name"] == "Whole Milk"  # type: ignore[index]
        food_expiry = food_proposal["fields"]["expiry_date"]  # type: ignore[index]
        assert food_expiry["value"] == "2030-01-15"
        assert food_expiry["source_type"] == "extraction"
        assert food_expiry["provider"] == provider.provider_id
        assert food_expiry["model"] == provider.model_id
        assert food_expiry["prompt_template_version"] == "extract-food-v2"
        assert food_expiry["provider_call_id"]

        # PG-EV-04: the bytes handed to the provider are a redacted PNG and the
        # prompt is exactly the versioned prompt file, per category.
        from app.services.providers import reader as reader_mod

        food_prompt, _ = reader_mod.load_prompt("food")
        assert provider.images[0][:8] == b"\x89PNG\r\n\x1a\n"
        assert dict(Image.open(io.BytesIO(provider.images[0])).getexif()) == {}
        assert provider.prompts[0] == food_prompt

        medicine_evidence = _upload(client, household_id, "phase2-medicine.png", _png("blue"))
        _enable(monkeypatch, provider, category="medicine")
        medicine_job = _run_import(
            client, household_id, [str(medicine_evidence["id"])], "phase2-medicine"
        )
        medicine_prompt, _ = reader_mod.load_prompt("medicine")
        assert provider.prompts[1] == medicine_prompt
        medicine_candidate = _candidate(session, _candidate_id(medicine_job))
        medicine_expiry = json.loads(medicine_candidate.proposed_fields_json)["fields"][  # type: ignore[index]
            "expiry_date"
        ]
        assert medicine_expiry["value"] == "2029-11-30"
        assert medicine_expiry["source_type"] == "extraction"
        assert medicine_expiry["prompt_template_version"] == "extract-medicine-v2"

        food_asset = _accept(client, household_id, food_candidate.id)
        medicine_asset = _accept(client, household_id, medicine_candidate.id)

    assert network == []
    for asset_id, expected_field in ((food_asset, "expiry_date"), (medicine_asset, "expiry_date")):
        rows = session.query(Assertion).filter_by(asset_id=asset_id).all()
        gated = [row for row in rows if row.field_path in GATED_FIELDS]
        assert gated, f"no gated assertions committed for {asset_id}"
        assert all(row.review_state == "proposed" for row in gated), [
            (row.field_path, row.review_state) for row in gated
        ]
        assert any(row.field_path == expected_field and row.review_state == "proposed" for row in rows)
        display = next(row for row in rows if row.field_path == "display_name")
        assert display.source_type == "extraction"
        assert display.model_json is not None
        assert json.loads(display.model_json)["provider"] == provider.provider_id


# --------------------------------------------------------------------------- #
# 2. Accept commits atomically; a forced commit failure rolls everything back
# --------------------------------------------------------------------------- #
def test_accept_commit_is_atomic_and_rolls_back_on_forced_failure(phase2_fixture, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase2_fixture
    provider = ScriptedPhase2Provider([_food_output()])
    with TestClient(app) as client:
        evidence = _upload(client, household_id, "phase2-atomic.png", _png("orange"))
        _enable(monkeypatch, provider, category="food")
        job = _run_import(client, household_id, [str(evidence["id"])], "phase2-atomic")
        candidate_id = _candidate_id(job)
        assert session.query(Asset).filter_by(household_id=household_id).count() == 0

        from app.services import candidates as candidates_mod

        original = candidates_mod._create_asset_for_candidate
        calls = {"n": 0}

        def _explode(db: Session, candidate: Candidate) -> Asset:
            calls["n"] += 1
            original(db, candidate)
            raise RuntimeError("SG-030 forced commit-path failure")

        monkeypatch.setattr(candidates_mod, "_create_asset_for_candidate", _explode)
        response = client.post(
            f"/v1/candidates/{candidate_id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )

    assert response.status_code == 200, response.text
    assert response.json()["job"]["state"] == "FAILED"
    assert calls["n"] == 1, "the commit path must actually have run before failing"
    assert session.query(Asset).filter_by(household_id=household_id).count() == 0
    assert session.query(Assertion).count() == 0
    assert session.query(AuditEvent).filter_by(entity_type="asset").count() == 0
    assert network == []


# --------------------------------------------------------------------------- #
# 3. needs_evidence reaches manual entry; never a guessed date
# --------------------------------------------------------------------------- #
def test_needs_evidence_manual_entry_never_guesses(phase2_fixture, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase2_fixture
    provider = ScriptedPhase2Provider([_needs_output()])
    with TestClient(app) as client:
        evidence = _upload(client, household_id, "phase2-needs.png", _png("purple"))
        _enable(monkeypatch, provider, category="food")
        job = _run_import(client, household_id, [str(evidence["id"])], "phase2-needs")
        candidate_id = _candidate_id(job)
        candidate = _candidate(session, candidate_id)
        proposal = json.loads(candidate.proposed_fields_json)
        assert proposal["needs_evidence"] is True
        assert "expiry_date" not in proposal["fields"]

        # The pipeline opened a candidate-level manual-entry task; resolve it.
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

        # No expiry value exists anywhere yet (the AI did not guess one).
        assert session.query(Assertion).filter_by(asset_id=asset_id, field_path="expiry_date").count() == 0
        assert session.query(Assertion).filter_by(asset_id=asset_id, field_path=P2_EXPIRY_FIELD).count() == 0

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
        assert entered.json()["resolved_review_task_ids"]
        assert manual_task_id in entered.json()["resolved_review_task_ids"]

    assert network == []
    rows = (
        session.query(Assertion)
        .filter_by(asset_id=asset_id, field_path=P2_EXPIRY_FIELD)
        .all()
    )
    states = {row.review_state for row in rows}
    assert "accepted" in states and "superseded" in states, states
    accepted = next(row for row in rows if row.review_state == "accepted")
    assert json.loads(accepted.value_json)["expiry_date"] == "2030-05-06"
    assert all("guessed" not in json.dumps(json.loads(row.value_json)) for row in rows)


# --------------------------------------------------------------------------- #
# 4. Corrections supersede auditably (never an overwrite)
# --------------------------------------------------------------------------- #
def test_correction_supersedes_auditably(phase2_fixture, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase2_fixture
    provider = ScriptedPhase2Provider([_food_output()])
    with TestClient(app) as client:
        evidence = _upload(client, household_id, "phase2-correct.png", _png("teal"))
        _enable(monkeypatch, provider, category="food")
        job = _run_import(client, household_id, [str(evidence["id"])], "phase2-correct")
        asset_id = _accept(client, household_id, _candidate_id(job))
        corrected = client.patch(
            f"/v1/assets/{asset_id}",
            params={"household_id": household_id},
            json={"display_name": "Whole Milk (corrected)"},
        )
        assert corrected.status_code == 200, corrected.text

    assert network == []
    rows = session.query(Assertion).filter_by(asset_id=asset_id, field_path="display_name").all()
    states = [row.review_state for row in rows]
    assert states.count("accepted") == 1 and "superseded" in states, states
    new_accepted = next(row for row in rows if row.review_state == "accepted")
    assert json.loads(new_accepted.value_json) == "Whole Milk (corrected)"
    assert new_accepted.source_type == "user"
    superseded = next(row for row in rows if row.review_state == "superseded")
    assert json.loads(superseded.value_json) == "Whole Milk"
    audit_count = (
        session.query(AuditEvent)
        .filter(AuditEvent.action == "assertion.upsert")
        .filter(AuditEvent.entity_id.in_([row.id for row in rows]))
        .count()
    )
    assert audit_count >= 1


# --------------------------------------------------------------------------- #
# 5. provider_call rows per AI call, job-linked, error_state None
# --------------------------------------------------------------------------- #
def test_provider_call_rows_per_call_with_scripted_cost(phase2_fixture, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase2_fixture
    provider = ScriptedPhase2Provider([_food_output(), _medicine_output()])
    with TestClient(app) as client:
        food_evidence = _upload(client, household_id, "phase2-calls-food.png", _png("green"))
        _enable(monkeypatch, provider, category="food")
        food_job = _run_import(client, household_id, [str(food_evidence["id"])], "phase2-calls-food")

        medicine_evidence = _upload(client, household_id, "phase2-calls-med.png", _png("blue"))
        _enable(monkeypatch, provider, category="medicine")
        medicine_job = _run_import(
            client, household_id, [str(medicine_evidence["id"])], "phase2-calls-med"
        )

    assert network == []
    assert provider.invocations == 2
    rows = session.query(ProviderCall).order_by(ProviderCall.created_at).all()
    assert len(rows) == 2
    linked = {str(food_job["id"]), str(medicine_job["id"])}
    assert {row.job_id for row in rows} == linked
    for row in rows:
        assert row.error_state is None
        assert row.provider == provider.provider_id
        assert row.cost == provider.cost
        assert json.loads(row.usage_json or "{}")["total_tokens"] == 30
        assert row.output_payload is not None


# --------------------------------------------------------------------------- #
# 6. Default-off unchanged: Phase-1-equivalent skip, zero ledger rows
# --------------------------------------------------------------------------- #
def test_default_off_is_phase1_equivalent(phase2_fixture, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, network = phase2_fixture
    provider = ScriptedPhase2Provider([_food_output()])
    from app.services.providers import reader as reader_mod

    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    with TestClient(app) as client:
        evidence = _upload(client, household_id, "phase2-default.png", _png("gray"))
        job = _run_import(client, household_id, [str(evidence["id"])], "phase2-default")
        candidate = _candidate(session, _candidate_id(job))
        proposal = json.loads(candidate.proposed_fields_json)

    assert network == []
    analyzing = _step(job, "ANALYZING_WITH_AI")["output"]
    assert isinstance(analyzing, dict)
    assert analyzing["status"] == "skipped"
    assert analyzing["reason"] == "consent_disabled"
    building = _step(job, "BUILDING_CANDIDATES")["output"]
    assert isinstance(building, dict)
    assert building["status"] == "skipped"
    assert provider.invocations == 0
    assert session.query(ProviderCall).count() == 0
    # Phase-1 deterministic field, no AI provenance.
    assert proposal["fields"]["display_name"] == "phase2-default"
