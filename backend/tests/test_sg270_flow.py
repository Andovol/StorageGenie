"""SG-270: imported items stay reachable, acceptable and finishable.

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
from app.models import Asset, Assertion, AuditEvent, Evidence, Household, JobStep, ReviewTask
from app.plugins.expiry_tracker import CLASSIFICATION_FIELD, EXPIRY_FIELD
from app.services import candidates, job_service
from app.services.candidates import Candidate, CandidateBlockedError
from app.services.observations import Observation
from tests.test_phase2_e2e import ScriptedPhase2Provider


@pytest.fixture
def flow_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg270.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG-270 Household")
    other = Household(name="SG-270 Other Household")
    session.add_all([household, other])
    session.commit()
    monkeypatch.setattr(settings, "storage_root", str(tmp_path / "storage"))
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    monkeypatch.setattr(settings, "sg_confidence_threshold", 0.9)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")

    from app.services.providers import opencode_go

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        raise AssertionError("network must never be attempted in SG-270")

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


def _upload(client: TestClient, household_id: str, name: str) -> str:
    response = client.post(
        "/v1/evidence",
        params={"household_id": household_id},
        files={"file": (name, _png("green"), "image/png")},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def _enable(monkeypatch: pytest.MonkeyPatch, provider: ScriptedPhase2Provider) -> None:
    from app.services.providers import reader as reader_mod

    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")


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
) -> dict[str, object]:
    return {
        "name": name,
        "expiry_date": expiry,
        "date_type": date_type,
        "lot": lot,
        "confidence": confidence,
        "uncertainty_reasons": reasons or ["faint print"],
    }


def _needs_output() -> dict[str, object]:
    return _out(
        [_item("Mystery Yogurt", None, None, None, 0.4, ["blur"])],
        ["items.0.expiry_date"],
        True,
    )


def _dated_output() -> dict[str, object]:
    return _out([_item("Whole Milk", "2030-01-15", "expiry_date", "L-77", 0.97, ["faint lot"])])


def _two_item_output() -> dict[str, object]:
    return _out(
        [
            _item("Milk", "2030-01-15", "expiry_date", "L-1", 1.0),
            _item("Yogurt", None, None, "L-2", 0.8, ["angle"]),
        ],
        ["items.1.expiry_date"],
        True,
    )


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


def _fresh(session: Session) -> None:
    # End the test session's read transaction and drop cached rows so later
    # request commits are visible despite expire_on_commit=False.
    session.commit()
    session.expire_all()


def _candidate(session: Session, candidate_id: str) -> Candidate:
    _fresh(session)
    return session.query(Candidate).filter_by(id=candidate_id).one()


def _date_task(session: Session, subject_ref: str) -> ReviewTask:
    _fresh(session)
    return (
        session.query(ReviewTask)
        .filter_by(subject_ref=subject_ref, task_type="expiry.manual_entry", status="open")
        .one()
    )


def _accept(client: TestClient, household_id: str, candidate_id: str) -> dict[str, object]:
    response = client.post(
        f"/v1/candidates/{candidate_id}/decision",
        params={"household_id": household_id},
        json={"action": "accept"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _edit(
    client: TestClient,
    household_id: str,
    candidate_id: str,
    corrected_fields: dict[str, object],
) -> dict[str, object]:
    response = client.post(
        f"/v1/candidates/{candidate_id}/decision",
        params={"household_id": household_id},
        json={"action": "edit", "corrected_fields": corrected_fields},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _drop_committed_assets(session: Session, job_id: str) -> None:
    """Leave a real commit's row as SG-270's base left it: no map, commit output intact."""
    _fresh(session)
    step = session.query(JobStep).filter_by(job_id=job_id, step_name="AWAITING_REVIEW").one()
    output = json.loads(step.output_refs or "{}")
    assert isinstance(output, dict)
    assert "committed_assets" in output
    output.pop("committed_assets")
    step.output_refs = json.dumps(output)
    session.commit()


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


def test_date_only_candidate_journey_moves_task_and_reaches_the_expiry_page(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_needs_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg270-needs.png")
        job = _run_import(client, household_id, [evidence_id], "sg270-needs")
        candidate_id = _candidate_id(job)
        candidate_read = client.get(
            f"/v1/candidates/{candidate_id}", params={"household_id": household_id}
        )
        assert candidate_read.status_code == 200
        body = candidate_read.json()
        assert len(body["review_task_ids"]) == 1
        assert body["blocking_review_task_ids"] == []

        listed = client.get(
            f"/v1/jobs/{job['id']}/candidates", params={"household_id": household_id}
        )
        assert listed.status_code == 200, listed.text
        listed_item = next(item for item in listed.json()["items"] if item["id"] == candidate_id)
        assert listed_item["state"] == "proposed"
        assert listed_item["fields"]["display_name"]["value"] == "Mystery Yogurt"

        before_tasks = client.get(
            "/v1/review-tasks", params={"household_id": household_id}
        ).json()["items"]
        date_task = next(item for item in before_tasks if item["task_type"] == "expiry.manual_entry")
        assert date_task["subject_kind"] == "candidate"
        assert date_task["data_required"] is True
        task_id = date_task["id"]

        accepted = _accept(client, household_id, candidate_id)
        asset_id = str(accepted["asset_id"])
        assert accepted["job"]["state"] == "COMPLETED"

        _fresh(session)
        assert (
            session.query(Assertion)
            .filter_by(asset_id=asset_id, field_path=EXPIRY_FIELD)
            .count()
            == 0
        )
        moved = session.query(ReviewTask).filter_by(id=task_id).one()
        assert moved.subject_ref == asset_id
        assert json.loads(moved.proposed_change or "{}") == {"field_path": EXPIRY_FIELD, "prompt": "Enter expiry date manually"}
        assert moved.status == "open"
        move_audit = (
            session.query(AuditEvent)
            .filter_by(action="review_task.move", entity_id=task_id)
            .one()
        )
        assert json.loads(move_audit.after_json or "{}")["subject_ref"] == asset_id

        after_read = client.get(
            f"/v1/candidates/{candidate_id}", params={"household_id": household_id}
        ).json()
        assert after_read["review_task_ids"] == []
        assert after_read["blocking_review_task_ids"] == []
        after_tasks = client.get(
            "/v1/review-tasks", params={"household_id": household_id}
        ).json()["items"]
        moved_row = next(item for item in after_tasks if item["id"] == task_id)
        assert moved_row["subject_kind"] == "asset"
        assert moved_row["data_required"] is True

        classified = _classify(client, asset_id, household_id, "food")
        assert classified.status_code == 200, classified.text
        assert classified.json()["review_task"] == task_id

        entered = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
            params={"household_id": household_id},
            json={"expiry_date": "2030-05-06", "date_type": "best_before"},
        )
        assert entered.status_code == 200, entered.text
        assert task_id in entered.json()["resolved_review_task_ids"]

        status = client.get(
            "/v1/plugins/expiry-tracker/status", params={"household_id": household_id}
        )
        assert status.status_code == 200, status.text
        assert asset_id in {row["asset_id"] for row in status.json()["rows"]}

    _fresh(session)
    assert session.query(ReviewTask).filter_by(id=task_id).one().status == "resolved"
    assert provider.invocations == 1


def test_date_only_candidate_can_be_edited(flow_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_needs_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg270-edit.png")
        job = _run_import(client, household_id, [evidence_id], "sg270-edit")
        candidate_id = _candidate_id(job)
        edited = client.post(
            f"/v1/candidates/{candidate_id}/decision",
            params={"household_id": household_id},
            json={"action": "edit", "corrected_fields": {"display_name": "Edited Yogurt"}},
        )
    assert edited.status_code == 200, edited.text
    asset_id = str(edited.json()["asset_id"])
    task = _date_task(session, asset_id)
    assert task.status == "open"
    assert (
        session.query(Asset).filter_by(id=asset_id, household_id=household_id).count() == 1
    )


def test_shelf_stable_classification_resolves_the_moved_date_task(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_needs_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg270-shelf.png")
        job = _run_import(client, household_id, [evidence_id], "sg270-shelf")
        accepted = _accept(client, household_id, _candidate_id(job))
        asset_id = str(accepted["asset_id"])
        task_id = _date_task(session, asset_id).id
        classified = _classify(client, asset_id, household_id, "non-perishable")
    assert classified.status_code == 200, classified.text
    assert task_id in classified.json()["resolved_review_task_ids"]
    _fresh(session)
    assert session.query(ReviewTask).filter_by(id=task_id).one().status == "resolved"


def test_commit_failure_leaves_neither_asset_nor_moved_task(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_needs_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg270-fail.png")
        job = _run_import(client, household_id, [evidence_id], "sg270-fail")
        candidate_id = _candidate_id(job)
        task_id = _date_task(session, candidate_id).id
        original = candidates._create_asset_for_candidate

        def fail_after_asset(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
            original(*args, **kwargs)
            raise RuntimeError("forced mid-commit failure")

        monkeypatch.setattr(candidates, "_create_asset_for_candidate", fail_after_asset)
        failed = client.post(
            f"/v1/candidates/{candidate_id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert failed.status_code == 200
    assert failed.json()["job"]["state"] == "FAILED"
    _fresh(session)
    assert session.query(Asset).filter_by(household_id=household_id).count() == 0
    task = session.query(ReviewTask).filter_by(id=task_id).one()
    assert task.subject_ref == candidate_id
    assert task.status == "open"
    assert session.query(AuditEvent).filter_by(action="review_task.move").count() == 0


def test_hold_keeps_the_task_and_reject_closes_it_without_a_date(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_needs_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg270-reject.png")
        job = _run_import(client, household_id, [evidence_id], "sg270-reject")
        candidate_id = _candidate_id(job)
        task_id = _date_task(session, candidate_id).id
        held = client.post(
            f"/v1/candidates/{candidate_id}/decision",
            params={"household_id": household_id},
            json={"action": "hold"},
        )
        assert held.status_code == 200 and held.json()["state"] == "held"
        _fresh(session)
        assert session.query(ReviewTask).filter_by(id=task_id).one().status == "open"
        rejected = client.post(
            f"/v1/candidates/{candidate_id}/decision",
            params={"household_id": household_id},
            json={"action": "reject"},
        )
    assert rejected.status_code == 200 and rejected.json()["state"] == "rejected"
    _fresh(session)
    task = session.query(ReviewTask).filter_by(id=task_id).one()
    assert task.status == "resolved"
    rows = (
        session.query(AuditEvent)
        .filter_by(action="review_task.resolve", entity_id=task_id)
        .all()
    )
    assert len(rows) == 1
    resolution = json.loads(rows[0].after_json or "{}")["resolution"]
    assert resolution == {"candidate_rejected": candidate_id}


@pytest.mark.parametrize("mode", ["date", "clear"])
def test_duplicate_target_with_accepted_date_or_clear_closes_the_task(
    flow_db, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_needs_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, f"sg270-dup-{mode}.png")
        target_id = _create_asset(client, household_id, "Existing target", [evidence_id])
        assert _classify(client, target_id, household_id, "food").status_code == 200
        if mode == "date":
            entered = client.post(
                f"/v1/plugins/expiry-tracker/assets/{target_id}/expiry",
                params={"household_id": household_id},
                json={"expiry_date": "2030-05-06"},
            )
            assert entered.status_code == 200, entered.text
        else:
            cleared = client.post(
                f"/v1/plugins/expiry-tracker/assets/{target_id}/expiry/clear",
                params={"household_id": household_id},
                json={},
            )
            assert cleared.status_code == 200, cleared.text

        job = _run_import(client, household_id, [evidence_id], f"sg270-dup-{mode}")
        candidate_id = _candidate_id(job)
        task_id = _date_task(session, candidate_id).id
        accepted = _accept(client, household_id, candidate_id)

    assert accepted["status"] == "duplicate_linked"
    assert str(accepted["asset_id"]) == target_id
    assert accepted["job"]["state"] == "COMPLETED"
    _fresh(session)
    task = session.query(ReviewTask).filter_by(id=task_id).one()
    assert task.status == "resolved"
    rows = (
        session.query(AuditEvent)
        .filter_by(action="review_task.resolve", entity_id=task_id)
        .all()
    )
    assert json.loads(rows[0].after_json or "{}")["resolution"]["duplicate_of_asset"] == target_id
    assert session.query(Asset).filter_by(household_id=household_id).count() == 1


def test_duplicate_target_with_an_open_date_task_joins_it_once(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_needs_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg270-dup-open.png")
        target_id = _create_asset(client, household_id, "Dateless target", [evidence_id])
        assert _classify(client, target_id, household_id, "food").status_code == 200
        target_task = _date_task(session, target_id)
        job = _run_import(client, household_id, [evidence_id], "sg270-dup-open")
        candidate_id = _candidate_id(job)
        candidate_task_id = _date_task(session, candidate_id).id
        accepted = _accept(client, household_id, candidate_id)

    assert accepted["status"] == "duplicate_linked"
    _fresh(session)
    open_target_tasks = (
        session.query(ReviewTask)
        .filter_by(subject_ref=target_id, task_type="expiry.manual_entry", status="open")
        .all()
    )
    assert [task.id for task in open_target_tasks] == [target_task.id]
    candidate_task = session.query(ReviewTask).filter_by(id=candidate_task_id).one()
    assert candidate_task.status == "resolved"
    rows = (
        session.query(AuditEvent)
        .filter_by(action="review_task.resolve", entity_id=candidate_task_id)
        .all()
    )
    resolution = json.loads(rows[0].after_json or "{}")["resolution"]
    assert resolution["existing_review_task_id"] == target_task.id


def test_duplicate_target_in_another_household_is_refused(flow_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_id = flow_db
    other_asset = Asset(household_id=other_id, display_name="Other home item", asset_type="product")
    session.add(other_asset)
    session.flush()
    job = job_service.create_job(session, household_id, [])
    candidate = Candidate(
        job_id=job.id,
        evidence_ids_json="[]",
        proposed_fields_json=json.dumps(
            {"kind": "duplicate_of_asset", "asset_id": other_asset.id, "fields": {}}
        ),
        state="accepted",
        household_id=household_id,
    )
    session.add(candidate)
    session.flush()
    task = ReviewTask(
        task_type="expiry.manual_entry",
        priority="high",
        subject_ref=candidate.id,
        proposed_change=json.dumps({"field_path": EXPIRY_FIELD, "prompt": "Enter expiry date manually"}),
        status="open",
        household_id=household_id,
    )
    session.add(task)
    session.commit()
    with pytest.raises(CandidateBlockedError, match="not in this household"):
        candidates.commit_candidate(session, candidate)
    session.rollback()
    assert session.query(ReviewTask).filter_by(id=task.id).one().subject_ref == candidate.id


def test_split_children_commit_their_own_assets_and_the_same_child_twice_is_idempotent(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_two_item_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg270-split.png")
        job = _run_import(client, household_id, [evidence_id], "sg270-split")
        origin_id = _candidate_id(job)
        blocked = client.post(
            f"/v1/candidates/{origin_id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
        assert blocked.status_code == 409
        split = client.post(
            f"/v1/candidates/{origin_id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 1]},
        )
        assert split.status_code == 200, split.text
        children = split.json()["children"]
        assert len(children) == 2
        first, second = children
        first_asset = str(_accept(client, household_id, first["id"])["asset_id"])
        second_response = _accept(client, household_id, second["id"])
        second_asset = str(second_response["asset_id"])
        repeat = _accept(client, household_id, first["id"])

    assert first_asset != second_asset
    assert repeat["asset_id"] == first_asset
    assert repeat["created"] is False
    _fresh(session)
    assert session.query(Asset).filter_by(household_id=household_id).count() == 2
    second_task = _date_task(session, second_asset)
    assert second_task.status == "open"
    assert session.query(ReviewTask).filter_by(
        subject_ref=origin_id, task_type="expiry.manual_entry", status="open"
    ).count() == 0


def test_pre_sg270_repeat_accept_returns_the_existing_item(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_dated_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg275-old-accept.png")
        job = _run_import(client, household_id, [evidence_id], "sg275-old-accept")
        candidate_id = _candidate_id(job)
        first = _accept(client, household_id, candidate_id)
        assert first["created"] is True
        asset_id = str(first["asset_id"])
        _drop_committed_assets(session, str(job["id"]))
        repeat = _accept(client, household_id, candidate_id)

    assert repeat["asset_id"] == asset_id
    assert repeat["created"] is False
    assert repeat["job"]["state"] == "COMPLETED"
    _fresh(session)
    assert session.query(Asset).filter_by(household_id=household_id).count() == 1


def test_pre_sg270_repeat_edit_returns_the_existing_item(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_dated_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg275-old-edit.png")
        job = _run_import(client, household_id, [evidence_id], "sg275-old-edit")
        candidate_id = _candidate_id(job)
        first = _accept(client, household_id, candidate_id)
        assert first["created"] is True
        asset_id = str(first["asset_id"])
        _drop_committed_assets(session, str(job["id"]))
        edited = _edit(
            client, household_id, candidate_id, {"display_name": "Renamed older row"}
        )

    assert edited["asset_id"] == asset_id
    assert edited["created"] is False
    _fresh(session)
    assert session.query(Asset).filter_by(household_id=household_id).count() == 1


def test_failed_commit_retried_creates_exactly_one_item(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_dated_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg275-retry.png")
        job = _run_import(client, household_id, [evidence_id], "sg275-retry")
        candidate_id = _candidate_id(job)
        original = candidates._create_asset_for_candidate

        def fail_after_asset(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
            original(*args, **kwargs)
            raise RuntimeError("forced mid-commit failure")

        monkeypatch.setattr(candidates, "_create_asset_for_candidate", fail_after_asset)
        failed = _accept(client, household_id, candidate_id)
        assert failed["job"]["state"] == "FAILED"
        _fresh(session)
        assert session.query(Asset).filter_by(household_id=household_id).count() == 0
        commit_step = (
            session.query(JobStep)
            .filter_by(job_id=str(job["id"]), step_name="COMMITTING")
            .one()
        )
        failed_output = json.loads(commit_step.output_refs or "{}")
        assert "asset_id" not in failed_output

        monkeypatch.setattr(candidates, "_create_asset_for_candidate", original)
        retried = client.post(
            f"/v1/imports/{job['id']}/retry", params={"household_id": household_id}
        )
        assert retried.status_code == 200, retried.text
        assert retried.json()["state"] == "COMPLETED"

    _fresh(session)
    assert session.query(Asset).filter_by(household_id=household_id).count() == 1


def test_new_row_repeat_accept_stays_one_item(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_dated_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg275-new-row.png")
        job = _run_import(client, household_id, [evidence_id], "sg275-new-row")
        candidate_id = _candidate_id(job)
        first = _accept(client, household_id, candidate_id)
        repeat = _accept(client, household_id, candidate_id)

    assert first["created"] is True
    assert repeat["asset_id"] == first["asset_id"]
    assert repeat["created"] is False
    _fresh(session)
    assert session.query(Asset).filter_by(household_id=household_id).count() == 1


def test_ai_read_dated_item_opens_no_review_task(
    flow_db, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    provider = ScriptedPhase2Provider([_dated_output()])
    _enable(monkeypatch, provider)
    with TestClient(app) as client:
        evidence_id = _upload(client, household_id, "sg270-dated.png")
        job = _run_import(client, household_id, [evidence_id], "sg270-dated")
        candidate_id = _candidate_id(job)
        read = client.get(
            f"/v1/candidates/{candidate_id}", params={"household_id": household_id}
        )
    assert read.status_code == 200
    assert read.json()["review_task_ids"] == []
    _fresh(session)
    assert (
        session.query(ReviewTask).filter_by(subject_ref=candidate_id).count() == 0
    )


def test_food_then_non_perishable_resolves_the_real_task(flow_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    with TestClient(app) as client:
        created = client.post(
            "/v1/assets",
            params={"household_id": household_id},
            json={"display_name": "Canned beans"},
        )
        assert created.status_code == 201
        asset_id = str(created.json()["id"])
        food = _classify(client, asset_id, household_id, "food")
        assert food.status_code == 200, food.text
        task_id = food.json()["review_task"]
        assert task_id
        moved = _classify(client, asset_id, household_id, "non-perishable")
    assert moved.status_code == 200, moved.text
    assert task_id in moved.json()["resolved_review_task_ids"]
    _fresh(session)
    task = session.query(ReviewTask).filter_by(id=task_id).one()
    assert task.status == "resolved"
    assert session.query(Assertion).filter_by(
        asset_id=asset_id, field_path=CLASSIFICATION_FIELD, review_state="accepted"
    ).count() == 1


def test_non_perishable_resolves_a_split_origin_orphan_with_audit(flow_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    evidence = Evidence(
        household_id=household_id,
        sha256="z" * 64,
        storage_key="sg270/orphan.png",
        media_type="image/png",
        original_filename="orphan.png",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(evidence)
    session.commit()
    with TestClient(app) as client:
        asset_id = _create_asset(client, household_id, "Split child", [evidence.id])
        job = job_service.create_job(session, household_id, [evidence.id])
        origin = Candidate(
            job_id=job.id,
            evidence_ids_json=json.dumps([evidence.id]),
            proposed_fields_json=json.dumps({"kind": "new_asset", "fields": {}}),
            state="split",
            household_id=household_id,
        )
        session.add(origin)
        session.flush()
        orphan = ReviewTask(
            task_type="expiry.manual_entry",
            priority="high",
            subject_ref=origin.id,
            proposed_change=json.dumps({"field_path": EXPIRY_FIELD, "prompt": "Enter expiry date manually"}),
            status="open",
            household_id=household_id,
        )
        session.add(orphan)
        session.commit()
        moved = _classify(client, asset_id, household_id, "non-perishable")

    assert moved.status_code == 200, moved.text
    assert orphan.id in moved.json()["resolved_review_task_ids"]
    _fresh(session)
    assert session.query(ReviewTask).filter_by(id=orphan.id).one().status == "resolved"
    rows = (
        session.query(AuditEvent)
        .filter_by(action="review_task.resolve", entity_id=orphan.id)
        .all()
    )
    assert len(rows) == 1
    resolution = json.loads(rows[0].after_json or "{}")["resolution"]
    assert resolution["manual_entry_orphan"] is True
    assert resolution["asset_id"] == asset_id
    assert session.query(Observation).count() == 0
