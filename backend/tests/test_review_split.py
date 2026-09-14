"""SG-033 multi-item split: one candidate -> per-item candidates + review action.

Every gate is in-process on a temp SQLite database: no key, no network, zero
spend. The seam under test is `POST /v1/candidates/{id}/split` plus the service
operation it calls. A multi-item candidate is seeded directly (its `ai_items`
list is the SG-028 shape) so the tests prove the split preserves per-item
fields, shared evidence, and origin provenance without depending on a provider.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Evidence, Household
from app.models.review_task import ReviewTask
from app.services import job_service
from app.services.candidates import Candidate


@pytest.fixture
def split_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'split.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Split Household")
    other = Household(name="Other Split Household")
    session.add_all([household, other])
    session.commit()
    monkeypatch.setattr("app.config.settings.storage_root", str(tmp_path / "storage"))

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


def evidence(session: Session, household_id: str, suffix: str) -> Evidence:
    row = Evidence(
        household_id=household_id,
        sha256=(suffix * 64)[:64],
        storage_key=f"split/{suffix}.jpg",
        media_type="image/jpeg",
        original_filename=f"{suffix}.jpg",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(row)
    session.commit()
    return row


def _provenance(
    value: object, *, source_type: str, confidence: float | None, provider: object
) -> dict[str, object]:
    return {
        "value": value,
        "confidence": confidence,
        "source_type": source_type,
        "provider": provider,
        "model": "scripted-model-1" if provider else None,
        "prompt_template_version": "extract-food-v1" if provider else None,
        "provider_call_id": "call-1" if provider else None,
    }


def _proposal(items: list[dict[str, object]], *, unknowns: list[str]) -> dict[str, object]:
    return {
        "kind": "new_asset",
        "asset_id": None,
        "fields": {
            "display_name": _provenance(
                items[0]["name"], source_type="extraction", confidence=0.9, provider="scripted"
            ),
            "asset_type": _provenance(
                "unknown", source_type="deterministic", confidence=None, provider=None
            ),
            "status": _provenance(
                "ACTIVE", source_type="deterministic", confidence=None, provider=None
            ),
            "identifier": _provenance(
                "BARCODE-7", source_type="deterministic", confidence=None, provider=None
            ),
            "expiry_date": _provenance(
                items[0]["expiry_date"], source_type="extraction", confidence=0.9, provider="scripted"
            ),
        },
        "dedup_matches": [],
        "review_task_ids": [],
        "ai_items": items,
        "ai_unknowns": unknowns,
        "needs_evidence": bool(unknowns),
        "ai_provider": "scripted",
        "ai_model": "scripted-model-1",
        "prompt_template_version": "extract-food-v1",
        "provider_call_ids": ["call-1"],
    }


def _seed_candidate(
    session: Session,
    household_id: str,
    evidence_id: str,
    proposal: dict[str, object],
    *,
    multi_item: bool,
) -> tuple[Candidate, list[ReviewTask]]:
    job = job_service.create_job(session, household_id, [evidence_id])
    items = proposal["ai_items"]
    assert isinstance(items, list)
    candidate = Candidate(
        job_id=job.id,
        evidence_ids_json=json.dumps([evidence_id]),
        proposed_fields_json=json.dumps(proposal, ensure_ascii=False),
        state="proposed",
        household_id=household_id,
    )
    session.add(candidate)
    session.flush()
    tasks: list[ReviewTask] = []
    if multi_item and len(items) > 1:
        task = ReviewTask(
            task_type="candidate.multi_item",
            priority="high",
            subject_ref=candidate.id,
            proposed_change=json.dumps({"candidate_id": candidate.id, "item_count": len(items)}),
            status="open",
            household_id=household_id,
        )
        session.add(task)
        session.flush()
        tasks.append(task)
    proposal["review_task_ids"] = [task.id for task in tasks]
    candidate.proposed_fields_json = json.dumps(proposal, ensure_ascii=False)
    session.commit()
    return candidate, tasks


def _two_item_candidate(session: Session, household_id: str, evidence_id: str) -> Candidate:
    proposal = _proposal(
        [
            {
                "name": "Milk",
                "expiry_date": "2030-01-15",
                "date_type": "expiry_date",
                "lot": None,
                "confidence": 0.9,
                "uncertainty_reasons": ["glare"],
            },
            {
                "name": "Yogurt",
                "expiry_date": None,
                "date_type": None,
                "lot": "L-2",
                "confidence": 0.8,
                "uncertainty_reasons": ["angle"],
            },
        ],
        unknowns=["items.1.expiry_date"],
    )
    candidate, _ = _seed_candidate(session, household_id, evidence_id, proposal, multi_item=True)
    return candidate


def test_split_yields_per_item_children_with_shared_evidence_and_provenance(split_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_id = split_db
    incoming = evidence(session, household_id, "a")
    candidate = _two_item_candidate(session, household_id, incoming.id)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/candidates/{candidate.id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 1]},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["state"] == "split"
        assert len(body["children"]) == 2
        child_ids = [child["id"] for child in body["children"]]
        assert len(set(child_ids)) == 2
        assert body["resolved_task_ids"]

        # read-back route named in the packet: children are ordinary candidates
        for child_id in child_ids:
            read_back = client.get(
                f"/v1/candidates/{child_id}", params={"household_id": household_id}
            )
            assert read_back.status_code == 200, read_back.text

        # origin is no longer decidable: a later decision is a conflict
        blocked = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
        assert blocked.status_code in {409, 422}, blocked.text

        # cross-household read is refused
        cross = client.get(
            f"/v1/candidates/{child_ids[0]}", params={"household_id": other_id}
        )
        assert cross.status_code == 403

    session.expire_all()
    origin = session.query(Candidate).filter_by(id=candidate.id).one()
    assert origin.state == "split"
    children = [session.query(Candidate).filter_by(id=child_id).one() for child_id in child_ids]
    assert [child.state for child in children] == ["proposed", "proposed"]
    assert [json.loads(child.evidence_ids_json) for child in children] == [
        [incoming.id],
        [incoming.id],
    ]

    first = json.loads(children[0].proposed_fields_json)
    second = json.loads(children[1].proposed_fields_json)
    assert first["fields"]["display_name"]["value"] == "Milk"  # type: ignore[index]
    assert second["fields"]["display_name"]["value"] == "Yogurt"  # type: ignore[index]
    assert first["fields"]["expiry_date"]["value"] == "2030-01-15"  # type: ignore[index]
    assert "expiry_date" not in second["fields"]  # no guessed value for the unknown expiry
    assert first["fields"]["identifier"]["value"] == "BARCODE-7"  # shared deterministic field kept
    for child_proposal in (first, second):
        assert child_proposal["ai_provider"] == "scripted"
        assert child_proposal["ai_model"] == "scripted-model-1"
        assert child_proposal["prompt_template_version"] == "extract-food-v1"
        assert child_proposal["provider_call_ids"] == ["call-1"]
        assert child_proposal["split_from"] == candidate.id
    assert first["ai_items"][0]["name"] == "Milk"
    assert second["ai_items"][0]["name"] == "Yogurt"
    assert second["ai_unknowns"] == ["items.0.expiry_date"]
    assert second["needs_evidence"] is True

    tasks = session.query(ReviewTask).filter_by(subject_ref=candidate.id).all()
    assert [task.status for task in tasks] == ["resolved"]


def test_split_empty_selection_is_422_and_creates_nothing(split_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = split_db
    incoming = evidence(session, household_id, "b")
    candidate = _two_item_candidate(session, household_id, incoming.id)
    before = session.query(Candidate).count()

    with TestClient(app) as client:
        response = client.post(
            f"/v1/candidates/{candidate.id}/split",
            params={"household_id": household_id},
            json={"item_indexes": []},
        )

    assert response.status_code == 422, response.text
    session.expire_all()
    assert session.query(Candidate).count() == before
    assert session.query(Candidate).filter_by(id=candidate.id).one().state == "proposed"
    assert session.query(ReviewTask).filter_by(status="open").count() == 1


def test_split_single_item_is_422_and_creates_nothing(split_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = split_db
    incoming = evidence(session, household_id, "c")
    candidate = _two_item_candidate(session, household_id, incoming.id)
    before = session.query(Candidate).count()

    with TestClient(app) as client:
        named_one = client.post(
            f"/v1/candidates/{candidate.id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0]},
        )

    assert named_one.status_code == 422, named_one.text
    session.expire_all()
    assert session.query(Candidate).count() == before
    assert session.query(Candidate).filter_by(id=candidate.id).one().state == "proposed"

    # a genuinely single-item candidate cannot be split either
    single_proposal = _proposal(
        [
            {
                "name": "Solo",
                "expiry_date": "2031-02-02",
                "date_type": "expiry_date",
                "lot": None,
                "confidence": 1.0,
                "uncertainty_reasons": [],
            }
        ],
        unknowns=[],
    )
    single, _ = _seed_candidate(
        session, household_id, incoming.id, single_proposal, multi_item=False
    )
    before_single = session.query(Candidate).count()
    with TestClient(app) as client:
        solo = client.post(
            f"/v1/candidates/{single.id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0]},
        )
    assert solo.status_code == 422, solo.text
    session.expire_all()
    assert session.query(Candidate).count() == before_single


def test_split_out_of_range_or_duplicate_indexes_is_422(split_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = split_db
    incoming = evidence(session, household_id, "d")
    candidate = _two_item_candidate(session, household_id, incoming.id)
    before = session.query(Candidate).count()

    with TestClient(app) as client:
        out_of_range = client.post(
            f"/v1/candidates/{candidate.id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 5]},
        )
        duplicate = client.post(
            f"/v1/candidates/{candidate.id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 0, 1]},
        )

    assert out_of_range.status_code == 422, out_of_range.text
    assert duplicate.status_code == 422, duplicate.text
    session.expire_all()
    assert session.query(Candidate).count() == before


def test_split_is_refused_for_unknown_candidate_and_wrong_household(split_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_id = split_db
    incoming = evidence(session, household_id, "e")
    candidate = _two_item_candidate(session, household_id, incoming.id)

    with TestClient(app) as client:
        missing = client.post(
            "/v1/candidates/does-not-exist/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 1]},
        )
        mismatch = client.post(
            f"/v1/candidates/{candidate.id}/split",
            params={"household_id": other_id},
            json={"item_indexes": [0, 1]},
        )

    assert missing.status_code == 404
    assert mismatch.status_code == 403
