"""SG-112 candidate merge + asset MERGED redirect: one survivor, terminal losers.

Every gate is in-process on a temp SQLite database: no key, no network, zero
spend. The seams under test are `POST /v1/candidates/merge` (the review action),
the decision guard it feeds, and `POST /v1/assets/{id}/merge` (the redirect
writer SG-111 reserved `ACTIVE -> MERGED` for). Candidates are seeded directly so
the tests prove the union/terminal/redirect behaviour without a provider.

The blocking-task oracle is typed here, never imported: a merge RESOLVES the
duplicate-identifier collision task and is BLOCKED by every other open task type
(an unrelated pending decision must not be silently dropped).
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
from app.models import Asset, Evidence, Household
from app.models.audit_event import AuditEvent
from app.models.review_task import ReviewTask
from app.services import job_service
from app.services.candidates import Candidate

# Independent oracle: the terminal loser state name.
MERGED_STATE = "merged"

# Independent oracle: the one task type a merge resolves; every other blocks.
RESOLVED_TASK_TYPES = {"identifier_collision"}
BLOCKING_TASK_TYPES = ("candidate.multi_item", "expiry.manual_entry")


@pytest.fixture
def merge_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'merge.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Merge Household")
    other = Household(name="Other Merge Household")
    session.add_all([household, other])
    session.commit()
    monkeypatch_set = pytest.MonkeyPatch()
    monkeypatch_set.setattr("app.config.settings.storage_root", str(tmp_path / "storage"))

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
        monkeypatch_set.undo()


def evidence(session: Session, household_id: str, suffix: str) -> Evidence:
    row = Evidence(
        household_id=household_id,
        sha256=(suffix * 64)[:64],
        storage_key=f"merge/{suffix}.jpg",
        media_type="image/jpeg",
        original_filename=f"{suffix}.jpg",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(row)
    session.commit()
    return row


def _proposal(name: str) -> dict[str, object]:
    return {
        "kind": "new_asset",
        "asset_id": None,
        "fields": {"display_name": {"value": name, "source_type": "deterministic"}},
        "dedup_matches": [],
        "review_task_ids": [],
    }


def _seed_candidate(
    session: Session,
    household_id: str,
    evidence_id: str,
    name: str,
    *,
    state: str = "proposed",
) -> Candidate:
    job = job_service.create_job(session, household_id, [evidence_id])
    candidate = Candidate(
        job_id=job.id,
        evidence_ids_json=json.dumps([evidence_id]),
        proposed_fields_json=json.dumps(_proposal(name), ensure_ascii=False),
        state=state,
        household_id=household_id,
    )
    session.add(candidate)
    session.commit()
    return candidate


def _seed_task(
    session: Session, household_id: str, candidate_id: str, task_type: str
) -> ReviewTask:
    task = ReviewTask(
        task_type=task_type,
        priority="high",
        subject_ref=candidate_id,
        proposed_change=json.dumps({"candidate_id": candidate_id}),
        status="open",
        household_id=household_id,
    )
    session.add(task)
    session.commit()
    return task


def make_asset(session: Session, household_id: str, status: str, name: str = "Item") -> Asset:
    asset = Asset(household_id=household_id, display_name=name, asset_type="product", status=status)
    session.add(asset)
    session.commit()
    return asset


def _counts(session: Session) -> tuple[int, int, int]:
    return (
        session.query(Candidate).count(),
        session.query(ReviewTask).count(),
        session.query(AuditEvent).count(),
    )


# --- candidate merge: the happy path -------------------------------------------


def test_merge_unions_evidence_and_terminates_losers(merge_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = merge_db
    winner = _seed_candidate(session, household_id, evidence(session, household_id, "a").id, "W")
    loser_one = _seed_candidate(
        session, household_id, evidence(session, household_id, "b").id, "L1"
    )
    loser_two = _seed_candidate(
        session, household_id, evidence(session, household_id, "c").id, "L2"
    )
    winner_evidence = json.loads(winner.evidence_ids_json)
    loser_one_evidence = json.loads(loser_one.evidence_ids_json)
    loser_two_evidence = json.loads(loser_two.evidence_ids_json)

    with TestClient(app) as client:
        response = client.post(
            "/v1/candidates/merge",
            params={"household_id": household_id},
            json={"winner_id": winner.id, "loser_ids": [loser_one.id, loser_two.id]},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["winner_id"] == winner.id
        assert body["state"] == "proposed"  # merge never auto-accepts
        assert set(body["merged_loser_ids"]) == {loser_one.id, loser_two.id}
        assert set(body["evidence_ids"]) == {
            *winner_evidence,
            *loser_one_evidence,
            *loser_two_evidence,
        }

        # read-back via the candidates route names the redirect (PG-SC-02)
        winner_read = client.get(
            f"/v1/candidates/{winner.id}", params={"household_id": household_id}
        ).json()
        assert winner_read["state"] == "proposed"
        assert set(winner_read["evidence_ids"]) == set(body["evidence_ids"])
        for loser in (loser_one, loser_two):
            read_back = client.get(
                f"/v1/candidates/{loser.id}", params={"household_id": household_id}
            ).json()
            assert read_back["state"] == "merged"
            assert read_back["merged_into"] == winner.id

    session.expire_all()
    stored_winner = session.query(Candidate).filter_by(id=winner.id).one()
    assert stored_winner.state == "proposed"
    assert len(json.loads(stored_winner.evidence_ids_json)) == 3
    for loser in (loser_one, loser_two):
        stored = session.query(Candidate).filter_by(id=loser.id).one()
        assert stored.state == MERGED_STATE
        assert json.loads(stored.proposed_fields_json)["merged_into"] == winner.id

    merge_audits = session.query(AuditEvent).filter_by(action="candidate.merge").all()
    assert len(merge_audits) == 1
    after = json.loads(merge_audits[0].after_json)
    assert after["merged_into"] == winner.id
    assert set(after["loser_ids"]) == {loser_one.id, loser_two.id}


def test_merge_resolves_duplicate_tasks_with_audit_rows(merge_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = merge_db
    winner = _seed_candidate(session, household_id, evidence(session, household_id, "d").id, "W")
    loser = _seed_candidate(session, household_id, evidence(session, household_id, "e").id, "L")
    collision = _seed_task(session, household_id, loser.id, next(iter(RESOLVED_TASK_TYPES)))

    with TestClient(app) as client:
        response = client.post(
            "/v1/candidates/merge",
            params={"household_id": household_id},
            json={"winner_id": winner.id, "loser_ids": [loser.id]},
        )
        assert response.status_code == 200, response.text
        assert response.json()["resolved_task_ids"] == [collision.id]

    session.expire_all()
    assert session.query(ReviewTask).filter_by(id=collision.id).one().status == "resolved"
    resolves = session.query(AuditEvent).filter_by(action="review_task.resolve").all()
    assert len(resolves) == 1
    assert json.loads(resolves[0].after_json)["resolution"] == {"merge": winner.id}


# --- candidate merge: every illegal shape writes nothing ------------------------


def test_merge_refuses_illegal_shapes_and_writes_nothing(merge_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_id = merge_db
    winner = _seed_candidate(session, household_id, evidence(session, household_id, "f").id, "W")
    proposed = _seed_candidate(session, household_id, evidence(session, household_id, "g").id, "P")
    decided = _seed_candidate(
        session, household_id, evidence(session, household_id, "h").id, "D", state="accepted"
    )
    foreign = _seed_candidate(session, other_id, evidence(session, other_id, "i").id, "F")
    blocked = _seed_candidate(session, household_id, evidence(session, household_id, "j").id, "B")
    _seed_task(session, household_id, blocked.id, BLOCKING_TASK_TYPES[0])

    cases = [
        ({"winner_id": winner.id, "loser_ids": [decided.id]}, 409),  # decided loser
        ({"winner_id": winner.id, "loser_ids": [foreign.id]}, 403),  # cross-household loser
        ({"winner_id": winner.id, "loser_ids": [winner.id]}, 422),  # winner == loser
        ({"winner_id": winner.id, "loser_ids": []}, 422),  # empty losers
        ({"winner_id": winner.id, "loser_ids": [blocked.id]}, 409),  # loser with open task
        ({"winner_id": "missing-winner", "loser_ids": [proposed.id]}, 404),
        ({"winner_id": decided.id, "loser_ids": [proposed.id]}, 409),  # decided winner
    ]

    with TestClient(app) as client:
        for payload, expected in cases:
            before = _counts(session)
            response = client.post(
                "/v1/candidates/merge",
                params={"household_id": household_id},
                json=payload,
            )
            assert response.status_code == expected, (payload, response.text)
            session.expire_all()
            assert _counts(session) == before, payload
            assert session.query(Candidate).filter_by(id=winner.id).one().state == "proposed"
            assert session.query(Candidate).filter_by(id=proposed.id).one().state == "proposed"
            assert session.query(ReviewTask).filter_by(status="open").count() == 1

        # winner belongs to another household -> 403
        session.expire_all()
        before = _counts(session)
        mismatch = client.post(
            "/v1/candidates/merge",
            params={"household_id": other_id},
            json={"winner_id": winner.id, "loser_ids": [foreign.id]},
        )
        assert mismatch.status_code == 403
        session.expire_all()
        assert _counts(session) == before


def test_merged_loser_redecision_is_409(merge_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = merge_db
    winner = _seed_candidate(session, household_id, evidence(session, household_id, "k").id, "W")
    loser = _seed_candidate(session, household_id, evidence(session, household_id, "l").id, "L")

    with TestClient(app) as client:
        merged = client.post(
            "/v1/candidates/merge",
            params={"household_id": household_id},
            json={"winner_id": winner.id, "loser_ids": [loser.id]},
        )
        assert merged.status_code == 200, merged.text
        again = client.post(
            f"/v1/candidates/{loser.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
        assert again.status_code == 409, again.text
        assert "merged" in again.json()["detail"]

    session.expire_all()
    assert session.query(Candidate).filter_by(id=loser.id).one().state == "merged"


# --- asset MERGED redirect writer ----------------------------------------------


def test_asset_merge_redirect_round_trips_read_path(merge_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = merge_db
    winner = make_asset(session, household_id, "ACTIVE", "Winner")
    duplicate = make_asset(session, household_id, "ACTIVE", "Duplicate")

    with TestClient(app) as client:
        response = client.post(
            f"/v1/assets/{duplicate.id}/merge",
            params={"household_id": household_id},
            json={"merged_into": winner.id},
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "MERGED"

        read_back = client.get(
            f"/v1/assets/{duplicate.id}", params={"household_id": household_id}
        ).json()
        winner_read = client.get(
            f"/v1/assets/{winner.id}", params={"household_id": household_id}
        ).json()

    assert read_back["status"] == "MERGED"
    assert winner_read["status"] == "ACTIVE"
    redirect = [
        a
        for a in read_back["assertions"]
        if a["field_path"] == "merge.merged_into" and a["review_state"] == "accepted"
    ]
    assert len(redirect) == 1
    assert redirect[0]["value"] == {"merged_into": winner.id}

    session.expire_all()
    assert session.query(Asset).filter_by(id=duplicate.id).one().status == "MERGED"
    assert session.query(AuditEvent).filter_by(action="asset.merge").count() == 1


def test_merged_asset_without_redirect_reads_terminal(merge_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = merge_db
    merged_asset = make_asset(session, household_id, "MERGED", "Terminal")

    with TestClient(app) as client:
        read_back = client.get(
            f"/v1/assets/{merged_asset.id}", params={"household_id": household_id}
        )
    assert read_back.status_code == 200, read_back.text
    body = read_back.json()
    assert body["status"] == "MERGED"  # terminal, never dangling
    assert [a for a in body["assertions"] if a["field_path"] == "merge.merged_into"] == []


def test_asset_merge_refusals_write_nothing(merge_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_id = merge_db
    winner = make_asset(session, household_id, "ACTIVE", "Winner")
    duplicate = make_asset(session, household_id, "ACTIVE", "Duplicate")
    draft = make_asset(session, household_id, "DRAFT", "Draft")
    foreign = make_asset(session, other_id, "ACTIVE", "Foreign")
    already = make_asset(session, household_id, "MERGED", "Already")

    cases = [
        (duplicate.id, winner.id, 200),  # legal control
    ]
    with TestClient(app) as client:
        # legal control first (proves the route works, then the refusals)
        assert client.post(
            f"/v1/assets/{cases[0][0]}/merge",
            params={"household_id": household_id},
            json={"merged_into": cases[0][1]},
        ).status_code == 200

        before_assets = session.query(Asset).count()
        before_audits = session.query(AuditEvent).filter_by(action="asset.merge").count()

        self_merge = client.post(
            f"/v1/assets/{winner.id}/merge",
            params={"household_id": household_id},
            json={"merged_into": winner.id},
        )
        missing = client.post(
            f"/v1/assets/{winner.id}/merge",
            params={"household_id": household_id},
            json={"merged_into": "no-such-asset"},
        )
        cross = client.post(
            f"/v1/assets/{winner.id}/merge",
            params={"household_id": household_id},
            json={"merged_into": foreign.id},
        )
        illegal = client.post(
            f"/v1/assets/{draft.id}/merge",
            params={"household_id": household_id},
            json={"merged_into": winner.id},
        )
        rem = client.post(
            f"/v1/assets/{already.id}/merge",
            params={"household_id": household_id},
            json={"merged_into": winner.id},
        )
        asset_mismatch = client.post(
            f"/v1/assets/{winner.id}/merge",
            params={"household_id": other_id},
            json={"merged_into": winner.id},
        )

    assert self_merge.status_code == 422, self_merge.text
    assert missing.status_code == 404, missing.text
    assert cross.status_code == 403, cross.text
    assert illegal.status_code == 422, illegal.text
    assert "illegal status transition" in illegal.json()["detail"]
    assert rem.status_code == 409, rem.text
    assert asset_mismatch.status_code == 403, asset_mismatch.text

    session.expire_all()
    assert session.query(Asset).count() == before_assets
    assert (
        session.query(AuditEvent).filter_by(action="asset.merge").count() == before_audits
    )
    assert session.query(Asset).filter_by(id=winner.id).one().status == "ACTIVE"
    assert session.query(Asset).filter_by(id=draft.id).one().status == "DRAFT"
    assert session.query(Asset).filter_by(id=already.id).one().status == "MERGED"
