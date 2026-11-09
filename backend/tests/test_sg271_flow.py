"""SG-271: the AI's proposals carry through review, classification and Expiry.

Every gate runs in-process on a temp SQLite database with the scripted provider
from `test_phase2_e2e.py`; no key, no network, no spend.
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
from app.models import Asset, Assertion, Household, ReviewTask
from app.plugins.expiry_tracker import CLASSIFICATION_FIELD, EXPIRY_FIELD
from app.services import candidates
from tests.test_phase2_e2e import ScriptedPhase2Provider


@pytest.fixture
def flow_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg271.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG-271 Household")
    other = Household(name="SG-271 Other Household")
    session.add_all([household, other])
    session.commit()
    monkeypatch.setattr(settings, "storage_root", str(tmp_path / "storage"))
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    monkeypatch.setattr(settings, "sg_confidence_threshold", 0.9)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")

    from app.services.providers import opencode_go

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        raise AssertionError("network must never be attempted in SG-271")

    monkeypatch.setattr(opencode_go.OpenCodeGoProvider, "_post", _forbidden)

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, other.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _png(color: str) -> bytes:
    image = Image.new("RGB", (48, 48), color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _upload(client: TestClient, household_id: str, name: str, color: str = "green") -> str:
    response = client.post(
        "/v1/evidence",
        params={"household_id": household_id},
        files={"file": (name, _png(color), "image/png")},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


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
    reasons: list[str] | None = None,
    **extra: object,
) -> dict[str, object]:
    item: dict[str, object] = {
        "name": name,
        "expiry_date": expiry,
        "date_type": date_type,
        "lot": lot,
        "confidence": confidence,
        "uncertainty_reasons": reasons or ["faint print"],
    }
    item.update(extra)
    return item


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


def _candidate_id(job: dict[str, object]) -> str:
    steps = job["steps"]
    assert isinstance(steps, list)
    output = next(step for step in steps if step["step_name"] == "DEDUPLICATING")["output"]
    assert isinstance(output, dict)
    return str(output["candidate_id"])


def _fresh(session: Session) -> None:
    session.commit()
    session.expire_all()


def _accept(client: TestClient, household_id: str, candidate_id: str) -> dict[str, object]:
    response = client.post(
        f"/v1/candidates/{candidate_id}/decision",
        params={"household_id": household_id},
        json={"action": "accept"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _create_asset(
    client: TestClient, household_id: str, name: str, evidence_ids: list[str]
) -> str:
    response = client.post(
        "/v1/assets",
        params={"household_id": household_id},
        json={"display_name": name, "evidence_ids": evidence_ids},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def _classify(client: TestClient, asset_id: str, household_id: str, category: str):  # type: ignore[no-untyped-def]
    return client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
        params={"household_id": household_id},
        json={"category": category},
    )


def _open_date_task_count(session: Session, subject_ref: str) -> int:
    _fresh(session)
    return (
        session.query(ReviewTask)
        .filter_by(subject_ref=subject_ref, task_type="expiry.manual_entry", status="open")
        .count()
    )


# G1: a cosmetics candidate with a known expiry but an unknown opened date
# opens NO date task; a food candidate with a missing required date still does.
def test_cosmetics_unknown_opened_date_opens_no_date_task(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    payload = _out(
        [_item("Face Cream", "2029-06-01", "expiry_date", None, 0.9, ["curvature"], opened_date=None)],
        ["items.0.opened_date"],
        True,
    )
    _enable(monkeypatch, ScriptedPhase2Provider([payload]), category="cosmetics")
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg271-cream.png")
        job = _run_import(client, household_id, [evidence_id], "sg271-cream")
        candidate_id = _candidate_id(job)
        read = client.get(f"/v1/candidates/{candidate_id}", params={"household_id": household_id})
        assert read.status_code == 200, read.text
    _fresh(session)
    assert candidates.load_proposal(
        session.query(candidates.Candidate).filter_by(id=candidate_id).one()
    )["needs_evidence"] is True
    assert _open_date_task_count(session, candidate_id) == 0


def test_food_missing_required_date_still_opens_a_date_task(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    payload = _out([_item("Mystery Yogurt", None, None, None, 0.4, ["blur"])], ["items.0.expiry_date"], True)
    _enable(monkeypatch, ScriptedPhase2Provider([payload]))
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg271-yogurt.png")
        job = _run_import(client, household_id, [evidence_id], "sg271-yogurt")
        candidate_id = _candidate_id(job)
    assert _open_date_task_count(session, candidate_id) == 1


def test_split_child_without_a_required_date_unknown_opens_no_task(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    payload = _out(
        [
            _item("Milk", None, None, "L-1", 0.8, ["angle"]),
            _item("Cream", "2029-06-01", "expiry_date", "L-2", 0.9, ["curvature"], opened_date=None),
        ],
        ["items.0.expiry_date", "items.1.opened_date"],
        True,
    )
    _enable(monkeypatch, ScriptedPhase2Provider([payload]))
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg271-split.png")
        job = _run_import(client, household_id, [evidence_id], "sg271-split")
        origin_id = _candidate_id(job)
        split = client.post(
            f"/v1/candidates/{origin_id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 1]},
        )
        assert split.status_code == 200, split.text
        first, second = split.json()["children"]
    assert _open_date_task_count(session, first["id"]) == 1
    assert _open_date_task_count(session, second["id"]) == 0


# G2: a committed candidate's read carries the item id on a fresh session;
# an uncommitted one carries none; another household is refused.
def test_committed_candidate_read_carries_the_item_id(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_id = flow_db
    payload = _out([_item("Whole Milk", "2030-01-15", "expiry_date", "L-77", 0.97, ["faint lot"])])
    _enable(monkeypatch, ScriptedPhase2Provider([payload]))
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg271-committed.png")
        job = _run_import(client, household_id, [evidence_id], "sg271-committed")
        candidate_id = _candidate_id(job)
        accepted = _accept(client, household_id, candidate_id)
        asset_id = str(accepted["asset_id"])
        _fresh(session)

        read = client.get(f"/v1/candidates/{candidate_id}", params={"household_id": household_id})
        assert read.status_code == 200, read.text
        assert read.json()["asset_id"] == asset_id

        listed = client.get(f"/v1/jobs/{job['id']}/candidates", params={"household_id": household_id})
        assert listed.status_code == 200, listed.text
        listed_item = next(item for item in listed.json()["items"] if item["id"] == candidate_id)
        assert listed_item.get("asset_id") == asset_id

        foreign = client.get(f"/v1/candidates/{candidate_id}", params={"household_id": other_id})
        assert foreign.status_code == 403


def test_uncommitted_candidate_read_carries_no_item_id(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    payload = _out([_item("Whole Milk", "2030-01-15", "expiry_date", "L-77", 0.97, ["faint lot"])])
    _enable(monkeypatch, ScriptedPhase2Provider([payload]))
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg271-pending.png")
        job = _run_import(client, household_id, [evidence_id], "sg271-pending")
        candidate_id = _candidate_id(job)
        _fresh(session)
        read = client.get(f"/v1/candidates/{candidate_id}", params={"household_id": household_id})
        assert read.status_code == 200, read.text
        assert read.json()["asset_id"] is None


# G3: the AI's proposed date survives classification with Accept offered, and
# the proposed category reaches the asset unconfirmed.
def test_classify_keeps_the_proposed_date_and_opens_no_task(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    payload = _out(
        [_item("Whole Milk", "2030-01-15", "expiry_date", "L-77", 0.97, ["faint lot"], category_proposed="food_beverages")]
    )
    _enable(monkeypatch, ScriptedPhase2Provider([payload]))
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg271-proposed.png")
        job = _run_import(client, household_id, [evidence_id], "sg271-proposed")
        candidate_id = _candidate_id(job)
        accepted = _accept(client, household_id, candidate_id)
        asset_id = str(accepted["asset_id"])
        _fresh(session)
        before = (
            session.query(Assertion)
            .filter_by(asset_id=asset_id, field_path="expiry_date")
            .one()
        )
        assert before.review_state == "proposed"
        assert json.loads(before.value_json) == "2030-01-15"
        assert session.query(Assertion).filter_by(
            asset_id=asset_id, field_path=CLASSIFICATION_FIELD
        ).count() == 0
        proposed = (
            session.query(Assertion)
            .filter_by(asset_id=asset_id, field_path="category_proposed")
            .one()
        )
        assert proposed.review_state == "proposed"

        classified = _classify(client, asset_id, household_id, "food_beverages")
        assert classified.status_code == 200, classified.text
        body = classified.json()
        assert body["expiry_assertion"]["review_state"] == "proposed"
        assert body["expiry_assertion"]["value"]["expiry_date"] == "2030-01-15"
        assert body["review_task"] is None

        status = client.get(
            "/v1/plugins/expiry-tracker/status", params={"household_id": household_id}
        )
        assert status.status_code == 200, status.text
        unresolved = {row["asset_id"]: row["reason"] for row in status.json()["unresolved_rows"]}
        assert unresolved.get(asset_id) == "proposed"

        entered = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
            params={"household_id": household_id},
            json={"expiry_date": "2030-01-15", "date_type": "expiry_date"},
        )
        assert entered.status_code == 200, entered.text
    _fresh(session)
    kept = (
        session.query(Assertion)
        .filter_by(asset_id=asset_id, field_path=EXPIRY_FIELD, review_state="accepted")
        .one()
    )
    assert json.loads(kept.value_json)["expiry_date"] == "2030-01-15"
    assert _open_date_task_count(session, asset_id) == 0


# G5: a deliberately dateless item leaves Unresolved; a missing date stays.
def test_deliberate_dateless_item_leaves_unresolved_but_missing_stays(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    payload = _out([_item("Whole Milk", "2030-01-15", "expiry_date", "L-77", 0.97, ["faint lot"])])
    _enable(monkeypatch, ScriptedPhase2Provider([payload, payload]))
    with TestClient(app) as client:
        first_evidence = _upload(client, household_id, "sg271-rice.png")
        first_job = _run_import(client, household_id, [first_evidence], "sg271-rice")
        first_asset = str(_accept(client, household_id, _candidate_id(first_job))["asset_id"])
        classified = _classify(client, first_asset, household_id, "non_perishable")
        assert classified.status_code == 200, classified.text

        second_evidence = _upload(client, household_id, "sg271-milk.png", "blue")
        second_asset = _create_asset(client, household_id, "Plain Milk", [second_evidence])
        missing = _classify(client, second_asset, household_id, "food_beverages")
        assert missing.status_code == 200, missing.text

        status = client.get(
            "/v1/plugins/expiry-tracker/status", params={"household_id": household_id}
        )
        assert status.status_code == 200, status.text
        body = status.json()
        unresolved = {row["asset_id"]: row["reason"] for row in body["unresolved_rows"]}
        assert first_asset not in unresolved
        assert unresolved.get(second_asset) == "needs_evidence"
        assert body["summary"]["dateless"] == 1
    assert session.query(Asset).filter_by(household_id=household_id).count() == 2
