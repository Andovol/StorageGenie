"""SG-028 pipeline tests: AI steps run for real, offline (scripted provider only).

Every gate here is in-process: no key, no SDK, no network, zero spend. The
schema-valid scripted provider is injected through ONE named seam
(`app.services.providers.reader.provider_registry`), so the pipeline exercises
the same call path the real adapter will ride. Negative tests prove no gated
field is ever silently auto-accepted and that a real provider id without
consent never calls out.
"""

from __future__ import annotations

import io
import json
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# This module sorts first, so it binds app.config/app.db before the other
# env-setting suites unless it declares its own isolated root first (same
# preamble convention as test_assertions/test_assets_crud/test_health).
AI_TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-ai-pipeline-tests-"))
AI_TEST_STORAGE_ROOT = AI_TEST_ROOT / "storage"
AI_TEST_STORAGE_ROOT.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{AI_TEST_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(AI_TEST_STORAGE_ROOT)

from app.config import settings  # noqa: E402
from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Assertion, Asset, AuditEvent, Evidence, Household, Job  # noqa: E402
from app.models.provider_call import ProviderCall  # noqa: E402
from app.models.review_task import ReviewTask  # noqa: E402
from app.services import job_service  # noqa: E402
from app.services.asset_service import create_asset  # noqa: E402
from app.services.candidates import Candidate  # noqa: E402
from app.services.observations import Observation  # noqa: E402
from app.services.providers.protocols import ProviderResult  # noqa: E402


def _gps_jpeg_bytes() -> bytes:
    """A JPEG carrying a fake EXIF/GPS blob (byte-level input for redaction)."""
    img = Image.new("RGB", (32, 32), "red")
    exif = img.getexif()
    exif[0x010F] = "TestMake"
    gps = exif.get_ifd(0x8825)
    gps[1] = "N"
    gps[2] = (51.0, 30.0, 0.0)
    gps[3] = "E"
    gps[4] = (0.0, 7.0, 0.0)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


@pytest.fixture
def ai_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "ai_pipeline.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    household = Household(name="AI Pipeline Household")
    other = Household(name="Other AI Pipeline Household")
    session.add_all([household, other])
    session.commit()
    evidence = Evidence(
        household_id=household.id,
        sha256="a" * 64,
        storage_key="ai/milk.jpg",
        media_type="image/jpeg",
        original_filename="milk.jpg",
        source_kind="upload",
        size_bytes=128,
    )
    session.add(evidence)
    session.commit()
    # Pre-seed the phash observation so the deterministic step short-circuits
    # (returns existing rows) and the fixture does not depend on OCR/zbar ABIs.
    session.add(
        Observation(
            evidence_id=evidence.id,
            kind="phash",
            value_json=json.dumps({"hash": "0000000000000000"}),
            confidence=1.0,
        )
    )
    session.commit()
    path = storage_root / evidence.storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_gps_jpeg_bytes())

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, evidence.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _enable(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    *,
    consent: bool = True,
    provider_id: str = "scripted",
    category: str = "food",
    threshold: float = 0.9,
    fail_times: int = 0,  # type: ignore[no-untyped-def]
):  # type: ignore[no-untyped-def]
    from app.services.providers import reader as reader_mod
    from app.services.providers.fake import ScriptedProvider

    provider = ScriptedProvider(
        provider_id=provider_id,
        payload=payload,
        fail_times=fail_times,
    )
    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", consent)
    monkeypatch.setattr(settings, "sg_provider_id", provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", category)
    monkeypatch.setattr(settings, "sg_confidence_threshold", threshold)
    return provider


def _run(session: Session, household_id: str, evidence_id: str) -> Job:
    job = job_service.create_job(session, household_id, [evidence_id])
    return job_service.run_job(session, job)


def _candidate(session: Session, job_id: str) -> Candidate:
    return session.query(Candidate).filter_by(job_id=job_id).one()


def _proposal(session: Session, job_id: str) -> dict[str, object]:
    return json.loads(_candidate(session, job_id).proposed_fields_json)


def _valid_item(**overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "name": "Milk",
        "expiry_date": "2030-01-15",
        "date_type": "expiry_date",
        "lot": None,
        "confidence": 0.95,
        "uncertainty_reasons": ["faint print"],
    }
    item.update(overrides)
    return item


def _payload(items: list[dict[str, object]], unknowns: list[str] | None = None, needs: bool = False) -> dict[str, object]:
    return {"items": items, "unknowns": unknowns or [], "needs_evidence": needs}


def test_low_risk_auto_accept_at_or_above_threshold(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    _enable(monkeypatch, _payload([_valid_item()]), threshold=0.9)
    job = _run(session, household_id, evidence_id)

    assert [step.step_name for step in job_service._steps(session, job.id)][3:5] == [
        "ANALYZING_WITH_AI",
        "BUILDING_CANDIDATES",
    ]
    candidate = _candidate(session, job.id)
    proposal = _proposal(session, job.id)
    assert proposal["ai_items"][0]["name"] == "Milk"  # type: ignore[index]

    with TestClient(app) as client:
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200, accepted.text
    asset_id = str(accepted.json()["asset_id"])
    display = (
        session.query(Assertion)
        .filter_by(asset_id=asset_id, field_path="display_name", review_state="accepted")
        .one()
    )
    assert display.source_type == "extraction"
    envelope = json.loads(display.model_json or "{}")
    assert envelope["provider"] == "scripted"
    assert envelope["model"] == "scripted-model-1"
    assert envelope["prompt_template_version"] == "extract-food-v2"
    assert envelope["provider_call_id"]
    assert envelope["evidence_ids"] == [evidence_id]


def test_expiry_always_proposed_never_auto_accepted(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    _enable(monkeypatch, _payload([_valid_item(confidence=1.0, uncertainty_reasons=[])]))
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)

    with TestClient(app) as client:
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200, accepted.text
    asset_id = str(accepted.json()["asset_id"])
    expiry = session.query(Assertion).filter_by(asset_id=asset_id, field_path="expiry_date").all()
    assert expiry and all(row.review_state == "proposed" for row in expiry)
    assert not session.query(Assertion).filter_by(
        asset_id=asset_id, field_path="expiry_date", review_state="accepted"
    ).count()


def test_opened_date_persisted_gated_with_value(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """SG-040 G1/G3: an extraction-carried opened date reaches the asset, gated.

    The candidate field must carry the extraction provenance envelope, and the
    committed assertion must carry the exact value, `source_type="extraction"`
    and `review_state="proposed"` (dates are safety-critical, never auto-accepted).
    """
    session, household_id, evidence_id = ai_env
    from app.services.providers import opencode_go

    network_attempts: list[str] = []

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        network_attempts.append("post")
        raise AssertionError("network must never be attempted in the offline opened-date gates")

    monkeypatch.setattr(opencode_go.OpenCodeGoProvider, "_post", _forbidden)
    _enable(monkeypatch, _payload([_valid_item(opened_date="2031-04-10")]))
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)
    proposal = _proposal(session, job.id)

    opened = proposal["fields"]["opened_date"]  # type: ignore[index]
    assert opened["value"] == "2031-04-10"
    assert opened["source_type"] == "extraction"
    assert opened["confidence"] == 0.95
    assert opened["provider_call_id"]
    assert network_attempts == []

    with TestClient(app) as client:
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200, accepted.text
    asset_id = str(accepted.json()["asset_id"])
    rows = (
        session.query(Assertion)
        .filter_by(asset_id=asset_id, field_path="opened_date")
        .all()
    )
    assert rows, "the committed asset must carry an opened_date assertion"
    assert {json.loads(row.value_json) for row in rows} == {"2031-04-10"}
    assert all(row.review_state == "proposed" for row in rows), "dates stay gated"
    assert all(row.source_type == "extraction" for row in rows)
    envelope = json.loads(rows[0].model_json or "{}")
    assert envelope["provider"] == "scripted"
    assert envelope["evidence_ids"] == [evidence_id]


def test_opened_date_none_writes_no_field_and_no_assertion(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """SG-040 G1/G3: a null opened date is absent, never a guessed value."""
    session, household_id, evidence_id = ai_env
    _enable(monkeypatch, _payload([_valid_item(opened_date=None)]))
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)
    proposal = _proposal(session, job.id)
    assert "opened_date" not in proposal["fields"]  # type: ignore[operator]

    with TestClient(app) as client:
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200, accepted.text
    asset_id = str(accepted.json()["asset_id"])
    assert not session.query(Assertion).filter_by(
        asset_id=asset_id, field_path="opened_date"
    ).count()


def test_split_children_keep_their_item_opened_date(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """SG-040 G1/G3 + SG-058 G2: the split replaces per-item fields, never shares the origin's.

    opened_date/expiry_date/lot are item-derived (SG-040); SG-058 extends the same
    rule to quantity/unit/asset_type, with a null item value omitted (never inherited).
    """
    session, household_id, evidence_id = ai_env
    payload = _payload(
        [
            _valid_item(
                name="Milk",
                opened_date="2031-04-10",
                quantity=2.0,
                unit="L",
                asset_type="food",
            ),
            _valid_item(
                name="Yogurt",
                opened_date=None,
                quantity=None,
                unit="cup",
                asset_type="cosmetics",
            ),
        ]
    )
    _enable(monkeypatch, payload)
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/candidates/{candidate.id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 1]},
        )
    assert response.status_code == 200, response.text
    children = response.json()["children"]
    assert len(children) == 2
    first, second = children[0]["fields"], children[1]["fields"]
    assert first["opened_date"]["value"] == "2031-04-10"
    assert first["opened_date"]["source_type"] == "extraction"
    assert "opened_date" not in second, "an item with no opened date adds no field"
    assert second["expiry_date"]["value"] == "2030-01-15"
    # SG-058 G2: per-item quantity/unit/asset_type, null omitted, never the origin's.
    assert first["quantity"]["value"] == 2.0
    assert first["quantity"]["source_type"] == "extraction"
    assert first["unit"]["value"] == "L"
    assert first["asset_type"]["value"] == "food"
    assert "quantity" not in second, "a null item quantity adds no field (never inherited)"
    assert second["unit"]["value"] == "cup"
    assert second["asset_type"]["value"] == "cosmetics"


def test_needs_evidence_opens_manual_entry_and_keeps_unknowns(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    payload = _payload(
        [_valid_item(expiry_date=None, date_type=None, confidence=0.4, uncertainty_reasons=["blur"])],
        unknowns=["items.0.expiry_date"],
        needs=True,
    )
    _enable(monkeypatch, payload)
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)
    proposal = _proposal(session, job.id)

    assert proposal["ai_unknowns"] == ["items.0.expiry_date"]
    assert "expiry_date" not in proposal["fields"]
    task = (
        session.query(ReviewTask)
        .filter_by(subject_ref=candidate.id, task_type="expiry.manual_entry", status="open")
        .one()
    )
    assert task.id in proposal["review_task_ids"]

    with TestClient(app) as client:
        resolved = client.post(
            f"/v1/review-tasks/{task.id}/resolve",
            params={"household_id": household_id},
            json={"resolution": "will enter manually"},
        )
        assert resolved.status_code == 200
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200, accepted.text
    asset_id = str(accepted.json()["asset_id"])
    assert not session.query(Assertion).filter_by(
        asset_id=asset_id, field_path="expiry_date"
    ).count()


def test_correction_chain_supersedes_and_audits(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    _enable(monkeypatch, _payload([_valid_item()]))
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)
    with TestClient(app) as client:
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
        asset_id = str(accepted.json()["asset_id"])
        corrected = client.patch(
            f"/v1/assets/{asset_id}",
            params={"household_id": household_id},
            json={"display_name": "Whole milk"},
        )
    assert corrected.status_code == 200, corrected.text
    rows = (
        session.query(Assertion)
        .filter_by(asset_id=asset_id, field_path="display_name")
        .all()
    )
    assert {row.review_state for row in rows} == {"superseded", "accepted"}
    accepted_row = next(row for row in rows if row.review_state == "accepted")
    assert json.loads(accepted_row.value_json) == "Whole milk"
    assert accepted_row.source_type == "user"
    assert (
        session.query(AuditEvent)
        .filter_by(action="assertion.upsert", entity_type="assertion")
        .filter(AuditEvent.entity_id.in_([row.id for row in rows]))
        .count()
        >= 1
    )


def test_default_config_is_phase1_skip(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    # Shipped defaults: provider "fake", consent False.
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    job = _run(session, household_id, evidence_id)

    steps = {step.step_name: step for step in job_service._steps(session, job.id)}
    analyzing = json.loads(steps["ANALYZING_WITH_AI"].output_refs or "{}")
    building = json.loads(steps["BUILDING_CANDIDATES"].output_refs or "{}")
    assert analyzing["status"] == "skipped"
    assert analyzing["reason"] == "consent_disabled"
    assert building["status"] == "skipped"
    assert session.query(ProviderCall).count() == 0
    proposal = _proposal(session, job.id)
    assert proposal["fields"]["display_name"] == "milk"  # deterministic, Phase-1-shaped


def test_multi_item_preserved_and_blocking_task_resolves_to_commit(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    payload = _payload(
        [
            _valid_item(name="Milk", confidence=0.9, uncertainty_reasons=["glare"]),
            _valid_item(name="Yogurt", confidence=0.8, uncertainty_reasons=["angle"]),
        ]
    )
    _enable(monkeypatch, payload)
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)
    proposal = _proposal(session, job.id)
    assert len(proposal["ai_items"]) == 2  # type: ignore[arg-type]

    task = (
        session.query(ReviewTask)
        .filter_by(subject_ref=candidate.id, task_type="candidate.multi_item", status="open")
        .one()
    )
    with TestClient(app) as client:
        blocked = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
        assert blocked.status_code == 409
        resolved = client.post(
            f"/v1/review-tasks/{task.id}/resolve",
            params={"household_id": household_id},
            json={"resolution": "one product per item"},
        )
        assert resolved.status_code == 200
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["job"]["state"] == "COMPLETED"
    assert session.query(Asset).filter_by(household_id=household_id).count() == 1


def test_provider_call_ledger_row_per_call_with_job_link(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    provider = _enable(monkeypatch, _payload([_valid_item()]))
    job = _run(session, household_id, evidence_id)

    rows = session.query(ProviderCall).filter_by(job_id=job.id).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.provider == "scripted"
    assert row.model == "scripted-model-1"
    assert row.prompt_template_version == "extract-food-v2"
    assert row.input_hashes and json.loads(row.input_hashes)["image_sha256"]
    assert row.output_payload is not None
    assert row.cost == 0.0
    assert row.usage_json and json.loads(row.usage_json)
    assert row.latency_ms is not None
    assert row.error_state is None
    assert provider.invocations == 1
    # PG-EV-04: the bytes handed to the provider are the redacted PNG, no GPS,
    # and the prompt is exactly the versioned prompt file.
    from app.services.providers import reader as reader_mod

    prompt_text, prompt_version = reader_mod.load_prompt("food")
    assert prompt_version == "extract-food-v2"
    assert provider.prompts == [prompt_text]
    assert provider.images[0][:8] == b"\x89PNG\r\n\x1a\n"
    assert dict(Image.open(io.BytesIO(provider.images[0])).getexif()) == {}


def test_real_provider_without_consent_skips_and_never_networks(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    from app.services.providers import opencode_go

    called: list[str] = []

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        called.append("post")
        raise AssertionError("network must never be attempted without consent")

    monkeypatch.setattr(opencode_go.OpenCodeGoProvider, "_post", _forbidden)
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "opencode-go")

    job = _run(session, household_id, evidence_id)
    steps = {step.step_name: step for step in job_service._steps(session, job.id)}
    analyzing = json.loads(steps["ANALYZING_WITH_AI"].output_refs or "{}")
    assert analyzing["status"] == "skipped"
    assert analyzing["reason"] == "consent_disabled"
    assert called == []
    assert session.query(ProviderCall).count() == 0


def test_repair_once_then_success(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    provider = _enable(monkeypatch, _payload([_valid_item()]), fail_times=1)
    job = _run(session, household_id, evidence_id)

    assert job.state == "AWAITING_REVIEW"
    assert provider.invocations == 2
    # SG-029 G0: the failed first attempt is itself ledgered (error_state), so a
    # success after the single repair leaves TWO durable call rows, not one.
    rows = session.query(ProviderCall).filter_by(job_id=job.id).all()
    assert len(rows) == 2
    assert sorted(row.error_state is not None for row in rows) == [False, True]
    # SG-029: the ONE §5.3 repair is a real repair turn, not a blind re-send.
    assert provider.prompts[0] != provider.prompts[1]
    assert "## Repair" in provider.prompts[1]


def test_second_failure_fails_the_step_loudly(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    provider = _enable(monkeypatch, _payload([_valid_item()]), fail_times=2)
    job = _run(session, household_id, evidence_id)

    assert job.state == "FAILED"
    steps = {step.step_name: step for step in job_service._steps(session, job.id)}
    assert steps["ANALYZING_WITH_AI"].state == "FAILED"
    assert steps["BUILDING_CANDIDATES"].state == "PENDING"
    assert provider.invocations == 2
    assert session.query(Candidate).filter_by(job_id=job.id).count() == 0


class _CapProbeProvider:
    """Estimating provider used ONLY to prove a cap binds before any call (SG-029 G0).

    The shipped `ScriptedProvider` reports no estimate, so it cannot exercise the
    pre-call refusal; this probe returns a bounded worst-case estimate and would
    raise loudly if the pipeline invoked it despite the refusal.
    """

    provider_id = "capped"
    model_id = "capped-model"

    def __init__(self) -> None:
        self.invocations = 0

    def estimate_cost(self, image_bytes: bytes, prompt: str) -> float:
        return 1.0

    def extract_items(  # type: ignore[no-untyped-def]
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ):
        self.invocations += 1
        raise AssertionError("provider must not be invoked on budget refusal")


def test_cap_binds_from_pipeline_zero_calls_zero_rows(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """SG-029 G0: a cap below the pipeline's supplied estimate refuses BEFORE a call.

    Pre-fix the pipeline passed no estimate (router default 0.0), so the cap could
    never bind and the provider was invoked. Post-fix: 0 invocations, 0 ledger rows,
    no network, step FAILED with the budget refusal.
    """
    session, household_id, evidence_id = ai_env
    from app.services.providers import reader as reader_mod

    provider = _CapProbeProvider()
    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")
    monkeypatch.setattr(settings, "sg_per_job_cap", 0.01)

    job = _run(session, household_id, evidence_id)

    assert job.state == "FAILED"
    assert provider.invocations == 0
    assert session.query(ProviderCall).count() == 0
    steps = {step.step_name: step for step in job_service._steps(session, job.id)}
    error = json.loads(steps["ANALYZING_WITH_AI"].output_refs or "{}")
    assert "estimated cost 1.0 exceeds" in error["error"]


def test_provider_error_is_ledgered_and_survives_rollback(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """SG-029 G0: every failed provider call leaves a durable `error_state` ledger row.

    Pre-fix a ProviderError raised inside the supply closure wrote no row and the
    `run_job` rollback erased any pending writes. Post-fix each of the two attempts
    (strict parse + single §5.3 repair) leaves exactly one committed error row that
    survives the step rollback.
    """
    session, household_id, evidence_id = ai_env
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    provider = _enable(monkeypatch, _payload([_valid_item()]), fail_times=2)
    job = _run(session, household_id, evidence_id)

    assert job.state == "FAILED"
    assert provider.invocations == 2
    rows = session.query(ProviderCall).filter_by(job_id=job.id).all()
    assert len(rows) == 2
    for row in rows:
        assert row.error_state is not None
        assert "invalid_json" in row.error_state
        assert row.cost == 0.0
    steps = {step.step_name: step for step in job_service._steps(session, job.id)}
    assert steps["ANALYZING_WITH_AI"].state == "FAILED"


def test_ai_candidate_still_receives_dedup_matches(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id = ai_env
    prior_evidence = Evidence(
        household_id=household_id,
        sha256="b" * 64,
        storage_key="ai/prior.jpg",
        media_type="image/jpeg",
        original_filename="prior.jpg",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(prior_evidence)
    session.commit()
    prior = create_asset(
        session, household_id, {"display_name": "Prior milk", "evidence_ids": [prior_evidence.id]}
    )
    session.add(
        Observation(
            evidence_id=prior_evidence.id,
            kind="phash",
            value_json=json.dumps({"hash": "0000000000000000"}),
            confidence=1.0,
        )
    )
    session.commit()

    _enable(monkeypatch, _payload([_valid_item()]))
    job = _run(session, household_id, evidence_id)
    proposal = _proposal(session, job.id)

    similar = [match for match in proposal["dedup_matches"] if match["type"] == "similar"]  # type: ignore[index]
    assert similar and similar[0]["asset_id"] == prior.id
    assert proposal["kind"] == "similar"
    # exactly the BUILDING_CANDIDATES candidate was reconciled, not a second one
    assert session.query(Candidate).filter_by(job_id=job.id).count() == 1
    assert "source_type" in proposal["fields"]["display_name"]  # type: ignore[index]


class _InvalidBodyProvider:
    """A provider whose returned body carries usage/cost but fails the schema (SG-030 ISS-11).

    The call reached the provider and came back with a billable-looking body; the
    reader's strict parse rejects it on both attempts (initial + one repair).
    """

    provider_id = "invalid-body"
    model_id = "invalid-body-model"

    def __init__(self, *, cost: float = 0.0023) -> None:
        self.cost = cost
        self.invocations = 0

    def extract_items(  # type: ignore[no-untyped-def]
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ):
        self.invocations += 1
        return ProviderResult(
            normalized_output={"prose": "this body is not the extraction schema"},
            raw_payload={"provider": self.provider_id, "attempt": self.invocations},
            request_id=f"invalid-body-{self.invocations}",
            usage={"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
            cost=self.cost,
            model_id=self.model_id,
            latency_ms=2.5,
        )


def test_returned_body_failing_schema_is_ledgered_durably(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """SG-030 ISS-11: a returned body keeps its real cost/usage and an error_state.

    Pre-fix the success-shaped rows written for a body that then failed schema
    validation were flushed but erased by the step rollback, and carried no
    error_state. Post-fix each of the two attempts leaves one committed row with
    the returned cost/usage AND `error_state`.
    """
    session, household_id, evidence_id = ai_env
    from app.services.providers import reader as reader_mod

    provider = _InvalidBodyProvider(cost=0.0023)
    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", None)

    job = _run(session, household_id, evidence_id)

    assert job.state == "FAILED"
    assert provider.invocations == 2
    rows = session.query(ProviderCall).filter_by(job_id=job.id).order_by(ProviderCall.created_at).all()
    assert len(rows) == 2
    for row in rows:
        assert row.error_state is not None
        assert "schema_validation" in row.error_state
        assert row.cost == 0.0023
        assert row.output_payload is not None
        assert json.loads(row.usage_json or "{}")["total_tokens"] == 18


class _MonthlyProbeProvider:
    """An estimating provider that records a real cost per call (SG-030 ISS-10)."""

    provider_id = "monthly-probe"
    model_id = "monthly-probe-model"

    def __init__(self, *, estimate: float, cost: float) -> None:
        self.estimate = estimate
        self.cost = cost
        self.invocations = 0

    def estimate_cost(self, image_bytes: bytes, prompt: str) -> float:
        return self.estimate

    def extract_items(  # type: ignore[no-untyped-def]
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ):
        self.invocations += 1
        return ProviderResult(
            normalized_output={
                "items": [
                    {
                        "name": "Monthly Milk",
                        "expiry_date": None,
                        "date_type": None,
                        "lot": None,
                        "confidence": 1.0,
                        "uncertainty_reasons": [],
                    }
                ],
                "unknowns": [],
                "needs_evidence": False,
            },
            raw_payload={"provider": self.provider_id},
            request_id=f"monthly-{self.invocations}",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            cost=self.cost,
            model_id=self.model_id,
            latency_ms=1.0,
        )


def test_monthly_cap_binds_across_jobs_from_durable_ledger(ai_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """SG-030 ISS-10: recorded spend counts toward the next job's pre-call check.

    Pre-fix `_monthly_spent` lived on a provider instance rebuilt per step, so it
    reset and the second job called out again. Post-fix the reader derives the
    baseline from the committed `provider_call` ledger: job 1 succeeds and records
    0.6; job 2 estimates 1.0 against a 1.5 cap and refuses with 0 invocations and
    0 new ledger rows, with the refusal visible in the step error.
    """
    session, household_id, evidence_id = ai_env
    from app.services.providers import reader as reader_mod

    provider = _MonthlyProbeProvider(estimate=1.0, cost=0.6)
    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", 1.5)

    first = _run(session, household_id, evidence_id)
    assert first.state == "AWAITING_REVIEW"
    assert provider.invocations == 1
    first_rows = session.query(ProviderCall).filter_by(job_id=first.id).all()
    assert len(first_rows) == 1
    assert first_rows[0].cost == 0.6

    second = _run(session, household_id, evidence_id)
    assert second.state == "FAILED"
    assert provider.invocations == 1
    assert session.query(ProviderCall).filter_by(job_id=second.id).count() == 0
    steps = {step.step_name: step for step in job_service._steps(session, second.id)}
    error = json.loads(steps["ANALYZING_WITH_AI"].output_refs or "{}")
    assert "monthly" in error["error"]
