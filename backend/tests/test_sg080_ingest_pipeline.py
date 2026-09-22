"""SG-080 photo-ingest pipeline on the live prompts (offline, scripted provider — $0).

Proves the properties this slice adds, measured through the REAL pipeline and
the ONE named injection seam (`app.services.providers.reader.provider_registry`),
with a scripted schema-valid provider and the committed v4 prompts (SG-095
flipped the reader from v3). No key, no SDK, no network, no metered call:

- G1: the live reader loads v4 for all three categories at runtime; the ledger
  row written across the real boundary carries the v4 template version.
- G2: every verbatim `transcript` is persisted as its own `Evidence` row, linked
  to the job's `evidence_ids`, readable through the existing evidence API, and
  NEVER present in any assertion `value_json`.
- G3: `category_proposed` is a visible, gated proposal (never auto-accepted at
  any confidence); every other v3 field crosses byte-equal into `ai_items` and
  is explicitly deferred from accept-writable promotion.
- G4: split-first on multi-item output with per-item quantity; consent gate
  and monthly-ledger refusal both fire BEFORE any provider call; the outgoing
  request shape (v4 prompt + redacted PNG bytes) is asserted, not mocked away.
"""

from __future__ import annotations

import io
import json
from copy import deepcopy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Evidence, Household, Job
from app.models.provider_call import ProviderCall
from app.models.review_task import ReviewTask
from app.services import job_service
from app.services.candidates import (
    ALLOWED_CANDIDATE_FIELDS,
    GATED_FIELDS,
    Candidate,
    build_candidate_from_extraction,
)
from app.services.observations import Observation
from app.services.providers import reader
from app.services.providers.protocols import ProviderResult
from app.services.providers.router import ProviderError
from app.services.providers.schemas import parse_extraction_output

CATEGORIES = ("food", "medicine", "cosmetics")
OTHER_V3_FIELDS = (
    "brand",
    "variant",
    "size_text",
    "barcode",
    "storage",
    "warnings",
    "allergens",
    "nutrition_per100g",
    "nutrition_serving",
)


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (24, 24), "white").save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def sg080_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "sg080.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", None)
    monkeypatch.setattr(settings, "sg_confidence_threshold", 0.9)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")

    # Zero-network proof: the real adapter must never be reached offline.
    from app.services.providers import opencode_go

    network_attempts: list[str] = []

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        network_attempts.append("post")
        raise AssertionError("network must never be attempted in the offline SG-080 tests")

    monkeypatch.setattr(opencode_go.OpenCodeGoProvider, "_post", _forbidden)

    household = Household(name="SG-080 Household")
    session.add(household)
    session.commit()
    png = _png_bytes()
    evidence = Evidence(
        household_id=household.id,
        sha256="e" * 64,
        storage_key="sg080/source.png",
        media_type="image/png",
        original_filename="source.png",
        source_kind="upload",
        size_bytes=len(png),
    )
    session.add(evidence)
    session.commit()
    path = storage_root / evidence.storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)
    session.add(
        Observation(
            evidence_id=evidence.id,
            kind="phash",
            value_json=json.dumps({"hash": "0" * 16}),
            confidence=1.0,
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
    try:
        yield session, household.id, evidence.id, network_attempts
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _enable(  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    *,
    consent: bool = True,
    provider_id: str = "scripted",
    category: str = "food",
    threshold: float = 0.9,
):
    from app.services.providers.fake import ScriptedProvider

    provider = ScriptedProvider(provider_id=provider_id, payload=payload)
    monkeypatch.setattr(reader, "provider_registry", lambda: {provider_id: provider})
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


def _v3_item(**overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "name": "Milk",
        "expiry_date": "2031-03-15",
        "date_type": "best_before",
        "lot": None,
        "quantity": 2.0,
        "unit": "bottles",
        "asset_type": "beverage",
        "confidence": 1.0,
        "uncertainty_reasons": [],
    }
    item.update(overrides)
    return item


def _payload(items: list[dict[str, object]], **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {"items": items, "unknowns": [], "needs_evidence": False}
    payload.update(overrides)
    return payload


TRANSCRIPT = "DairyGold Semi-skimmed Milk 1 L Best before 2031-03-15"


# --------------------------------------------------------------------------- #
# G1 — live reader loads v3
# --------------------------------------------------------------------------- #
def test_reader_loads_v4_for_all_categories_at_runtime() -> None:
    assert reader.PROMPT_FILES == {
        "food": "extract-food-v4.md",
        "medicine": "extract-medicine-v4.md",
        "cosmetics": "extract-cosmetics-v4.md",
    }
    for category in CATEGORIES:
        text, version = reader.load_prompt(category)
        assert version == f"extract-{category}-v4"
        # The loaded text is the REAL v4 content, not a copy: it names the new
        # evidence-only transcript and the proposed category.
        assert "transcript" in text, category
        assert "category_proposed" in text, category


def test_pipeline_ledger_rows_carry_v4_template_version(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, network = sg080_env
    provider = _enable(monkeypatch, _payload([_v3_item(transcript=TRANSCRIPT)]))
    job = _run(session, household_id, evidence_id)

    assert job.state == "AWAITING_REVIEW"
    rows = session.query(ProviderCall).filter_by(job_id=job.id).all()
    assert len(rows) == 1
    assert rows[0].prompt_template_version == "extract-food-v4"
    # PG-EV-04: the exact bytes + prompt handed to the seam, not a mock.
    prompt_text, prompt_version = reader.load_prompt("food")
    assert prompt_version == "extract-food-v4"
    assert provider.prompts == [prompt_text]
    assert provider.images[0][:8] == b"\x89PNG\r\n\x1a\n"
    assert dict(Image.open(io.BytesIO(provider.images[0])).getexif()) == {}
    assert network == []


# --------------------------------------------------------------------------- #
# G2 — transcript as evidence, never an asserted fact
# --------------------------------------------------------------------------- #
def test_transcript_persisted_as_evidence_linked_and_readable(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, _network = sg080_env
    _enable(monkeypatch, _payload([_v3_item(transcript=TRANSCRIPT)]))
    job = _run(session, household_id, evidence_id)

    rows = session.query(Evidence).filter_by(household_id=household_id, source_kind="transcript").all()
    assert len(rows) == 1
    transcript_evidence = rows[0]
    assert transcript_evidence.media_type == "text/plain"
    assert transcript_evidence.size_bytes == len(TRANSCRIPT.encode("utf-8"))
    # Linked to the same job, source image still first.
    config = json.loads(job.config_snapshot or "{}")
    assert config["evidence_ids"][0] == evidence_id
    assert transcript_evidence.id in config["evidence_ids"]

    # Readable through the EXISTING evidence read path.
    with TestClient(app) as client:
        meta = client.get(
            f"/v1/evidence/{transcript_evidence.id}", params={"household_id": household_id}
        )
        file_response = client.get(
            f"/v1/evidence/{transcript_evidence.id}/file",
            params={"household_id": household_id},
        )
    assert meta.status_code == 200, meta.text
    assert meta.json()["media_type"] == "text/plain"
    assert file_response.status_code == 200, file_response.text
    assert file_response.content.decode("utf-8") == TRANSCRIPT


def test_transcript_never_lands_in_assertion_values(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, _network = sg080_env
    _enable(monkeypatch, _payload([_v3_item(transcript=TRANSCRIPT)]))
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

    assertions = session.query(Assertion).filter_by(asset_id=asset_id).all()
    assert assertions
    for row in assertions:
        assert TRANSCRIPT not in (row.value_json or ""), row.field_path
        assert "transcript" not in (row.value_json or ""), row.field_path


# --------------------------------------------------------------------------- #
# G3 — category proposed + v3 fields preserved
# --------------------------------------------------------------------------- #
def test_category_proposed_visible_gated_and_never_auto_accepted(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, _network = sg080_env
    # Threshold 0.0: even a perfect-confidence category must stay proposed.
    _enable(
        monkeypatch,
        _payload([_v3_item(category_proposed="dairy")]),
        threshold=0.0,
    )
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)
    proposal = _proposal(session, job.id)

    assert "category_proposed" in GATED_FIELDS
    envelope = proposal["fields"]["category_proposed"]  # type: ignore[index]
    assert envelope["value"] == "dairy"
    assert envelope["source_type"] == "extraction"
    assert envelope["confidence"] == 1.0

    # Visible on the existing candidate read route.
    with TestClient(app) as client:
        body = client.get(
            f"/v1/candidates/{candidate.id}", params={"household_id": household_id}
        )
        assert body.status_code == 200, body.text
        assert body.json()["fields"]["category_proposed"]["value"] == "dairy"
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200, accepted.text
    asset_id = str(accepted.json()["asset_id"])

    rows = (
        session.query(Assertion)
        .filter_by(asset_id=asset_id, field_path="category_proposed")
        .all()
    )
    assert rows, "the committed asset must carry the proposed category"
    assert all(row.review_state == "proposed" for row in rows), "never auto-accepted"
    assert all(row.source_type == "extraction" for row in rows)


def test_other_v3_fields_preserved_byte_equal_in_ai_items_and_deferred(sg080_env) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _evidence_id, _network = sg080_env
    job = Job(
        job_type="import",
        state="RUNNING",
        config_snapshot=json.dumps({"evidence_ids": []}),
        household_id=household_id,
    )
    session.add(job)
    session.commit()

    item = _v3_item(
        brand="DairyGold",
        variant="Semi-skimmed",
        size_text="1 L",
        barcode="5012345678900",
        transcript=TRANSCRIPT,
        storage="Keep refrigerated below 5 C",
        warnings=["Not suitable for freezing"],
        allergens=["milk"],
        nutrition_per100g="Energy 250 kJ / 60 kcal; Fat 3.2 g",
        nutrition_serving="Per 250 ml: Energy 150 kcal",
    )
    extraction = parse_extraction_output(_payload([item]))
    candidate = build_candidate_from_extraction(
        session,
        job,
        extraction,
        {
            "provider": "scripted",
            "model": "scripted-model-1",
            "prompt_template_version": "extract-food-v3",
            "provider_call_ids": ["call-v3"],
        },
    )
    proposal = json.loads(candidate.proposed_fields_json)
    ai_item = proposal["ai_items"][0]
    for field in OTHER_V3_FIELDS + ("transcript",):
        assert ai_item[field] == item[field], field

    # Accept-writable promotion is explicitly deferred: none of these fields is
    # in the candidate whitelist, and none rides `fields`.
    for field in OTHER_V3_FIELDS + ("transcript",):
        assert field not in ALLOWED_CANDIDATE_FIELDS, field
        assert field not in proposal["fields"], field


def test_null_heavy_v3_items_are_handled(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, _network = sg080_env
    nulls = {field: None for field in OTHER_V3_FIELDS + ("transcript", "category_proposed")}
    _enable(monkeypatch, _payload([_v3_item(**nulls)]))
    job = _run(session, household_id, evidence_id)

    assert job.state == "AWAITING_REVIEW"
    proposal = _proposal(session, job.id)
    ai_item = proposal["ai_items"][0]
    for field in OTHER_V3_FIELDS + ("transcript", "category_proposed"):
        assert ai_item[field] is None, field
    assert "category_proposed" not in proposal["fields"]
    assert session.query(Evidence).filter_by(source_kind="transcript").count() == 0


# --------------------------------------------------------------------------- #
# G4 — split-first, refusal paths, request shape
# --------------------------------------------------------------------------- #
def test_multi_item_v3_splits_first_with_per_item_quantity(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, _network = sg080_env
    payload = _payload(
        [
            _v3_item(name="Milk", quantity=2.0, unit="L", category_proposed="dairy"),
            _v3_item(
                name="Yogurt",
                quantity=None,
                unit="cup",
                category_proposed=None,
                expiry_date=None,
                date_type=None,
            ),
        ]
    )
    _enable(monkeypatch, payload)
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)
    assert len(_proposal(session, job.id)["ai_items"]) == 2  # type: ignore[arg-type]

    task = (
        session.query(ReviewTask)
        .filter_by(subject_ref=candidate.id, task_type="candidate.multi_item", status="open")
        .one()
    )
    assert task.id in _proposal(session, job.id)["review_task_ids"]  # type: ignore[operator]

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
    # SG-049/SG-058 lineage: per-item quantity, null omitted, never inherited.
    assert first["quantity"]["value"] == 2.0
    assert first["quantity"]["source_type"] == "extraction"
    assert first["category_proposed"]["value"] == "dairy"
    assert "quantity" not in second, "a null item quantity adds no field"
    assert "category_proposed" not in second, "a null category adds no field"
    assert second["unit"]["value"] == "cup"


def test_consent_gate_refuses_before_any_call(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, _network = sg080_env
    provider = _enable(monkeypatch, _payload([_v3_item(transcript=TRANSCRIPT)]), consent=False)
    job = _run(session, household_id, evidence_id)

    steps = {step.step_name: step for step in job_service._steps(session, job.id)}
    analyzing = json.loads(steps["ANALYZING_WITH_AI"].output_refs or "{}")
    assert analyzing["status"] == "skipped"
    assert analyzing["reason"] == "consent_disabled"
    assert provider.invocations == 0
    assert session.query(ProviderCall).count() == 0
    assert session.query(Evidence).filter_by(source_kind="transcript").count() == 0


class _RefusingProvider:
    """Estimating provider that would raise loudly if invoked (pre-call refusal proof)."""

    provider_id = "capped-v3"
    model_id = "capped-v3-model"

    def __init__(self) -> None:
        self.invocations = 0

    def estimate_cost(self, image_bytes: bytes, prompt: str) -> float:
        return 1.0

    def extract_items(  # type: ignore[no-untyped-def]
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ):
        self.invocations += 1
        raise AssertionError("provider must not be invoked on monthly-ledger refusal")


class _OneCallThenFailProvider:
    """Succeeds on the first image, then fails (a provider-side leg)."""

    provider_id = "one-then-fail"
    model_id = "one-then-fail-model"

    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.invocations = 0

    def extract_items(  # type: ignore[no-untyped-def]
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ):
        self.invocations += 1
        if self.invocations >= 2:
            raise ProviderError("http_status", "provider returned HTTP 503: ''")
        return ProviderResult(
            normalized_output=deepcopy(self.payload),
            raw_payload={"scripted": True},
            request_id="one-then-fail-1",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            cost=0.0,
            model_id=self.model_id,
            latency_ms=1.0,
        )


def test_partial_job_failure_leaves_no_unlinked_transcript(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """A mid-job failure must not leave an unlinked transcript evidence row."""
    session, household_id, evidence_id, _network = sg080_env
    storage_root = Path(settings.storage_root)
    second = Evidence(
        household_id=household_id,
        sha256="f" * 64,
        storage_key="sg080/second.png",
        media_type="image/png",
        original_filename="second.png",
        source_kind="upload",
        size_bytes=len(_png_bytes()),
    )
    session.add(second)
    session.commit()
    path = storage_root / second.storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_png_bytes())
    session.add(
        Observation(
            evidence_id=second.id,
            kind="phash",
            value_json=json.dumps({"hash": "1" * 16}),
            confidence=1.0,
        )
    )
    session.commit()

    provider = _OneCallThenFailProvider(_payload([_v3_item(transcript=TRANSCRIPT)]))
    monkeypatch.setattr(reader, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")

    job = job_service.create_job(session, household_id, [evidence_id, second.id])
    job = job_service.run_job(session, job)

    assert job.state == "FAILED"
    assert provider.invocations == 2
    assert session.query(Evidence).filter_by(source_kind="transcript").count() == 0


def test_monthly_ledger_refuses_before_any_call(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, _network = sg080_env
    prior_job = Job(
        job_type="import",
        state="COMPLETED",
        config_snapshot=json.dumps({"evidence_ids": []}),
        household_id=household_id,
    )
    session.add(prior_job)
    session.flush()
    session.add(
        ProviderCall(
            provider="scripted",
            model="scripted-model-1",
            prompt_template_version="extract-food-v3",
            cost=0.6,
            job_id=prior_job.id,
        )
    )
    session.commit()

    provider = _RefusingProvider()
    monkeypatch.setattr(reader, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")
    monkeypatch.setattr(settings, "sg_monthly_cap", 1.5)

    job = _run(session, household_id, evidence_id)

    assert job.state == "FAILED"
    assert provider.invocations == 0
    assert session.query(ProviderCall).filter_by(job_id=job.id).count() == 0
    steps = {step.step_name: step for step in job_service._steps(session, job.id)}
    error = json.loads(steps["ANALYZING_WITH_AI"].output_refs or "{}")
    assert "monthly" in error["error"]


def test_v4_request_wire_shape_carries_prompt_and_json_object_flag(sg080_env, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """PG-EV-04: the shape of what would have been sent, not the mock."""
    from app.services.providers.opencode_go import build_chat_payload

    session, household_id, evidence_id, _network = sg080_env
    _enable(monkeypatch, _payload([_v3_item(transcript=TRANSCRIPT)]))
    _run(session, household_id, evidence_id)

    prompt, version = reader.load_prompt("food")
    assert version == "extract-food-v4"
    wire = build_chat_payload("deepseek-v4-flash-vision-exp", prompt, "AAAA")
    assert wire["response_format"] == {"type": "json_object"}
    assert wire["stream"] is False
    texts = [
        part.get("text") for part in wire["messages"][0]["content"] if part.get("type") == "text"
    ]
    assert prompt in texts
    assert "transcript" in prompt and "category_proposed" in prompt
