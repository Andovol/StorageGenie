"""SG-188 (D7/D8): resolve guard, cursor refusal, archived visibility.

Real routes on disposable state:

- G1: a bare `{}` resolve of an `expiry.manual_entry` task is refused (422
  naming the missing data) while the real manual-entry path still resolves it
  and answers `resolved_review_task_ids`. Classification -> expiry -> task
  readback re-derives the SG-181 G2 control population (food -> task;
  non-perishable -> no task).
- G2: a malformed cursor is refused (422) on both list surfaces while a valid
  cursor walk over 25 tied-timestamp rows is lossless; the default asset list
  excludes ARCHIVED (explicit `status=ARCHIVED` still lists them); the expiry
  status engine reports no archived row in rows or unresolved_rows.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Asset, Household, ReviewTask

EXP = "/v1/plugins/expiry-tracker"


@pytest.fixture
def sg188_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "sg188.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr("app.config.settings.storage_root", str(storage_root))
    household = Household(name="SG-188 Household")
    other = Household(name="SG-188 Other Household")
    session.add_all([household, other])
    session.commit()

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


def _post_asset(client: TestClient, household_id: str, name: str) -> str:
    response = client.post(
        "/v1/assets", params={"household_id": household_id}, json={"display_name": name}
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def test_bare_resolve_refused_for_data_required_task_and_real_entry_resolves(sg188_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_household_id = sg188_db
    with TestClient(app) as client:
        food_asset = _post_asset(client, household_id, "Food jar")
        classified = client.post(
            f"{EXP}/assets/{food_asset}/classification",
            params={"household_id": household_id},
            json={"category": "food"},
        )
        assert classified.status_code == 200, classified.text
        assert classified.json()["expiry_assertion"]["value"] == {"status": "unknown"}
        assert classified.json()["expiry_assertion"]["review_state"] == "needs_evidence"
        task_id = classified.json()["review_task"]
        assert task_id

        foreign = client.post(
            f"/v1/review-tasks/{task_id}/resolve",
            params={"household_id": other_household_id},
            json={},
        )
        assert foreign.status_code == 403, foreign.text

        bare = client.post(
            f"/v1/review-tasks/{task_id}/resolve",
            params={"household_id": household_id},
            json={},
        )
        assert bare.status_code == 422, bare.text
        assert "expiry_date" in bare.json()["detail"]
        bodyless = client.post(
            f"/v1/review-tasks/{task_id}/resolve", params={"household_id": household_id}
        )
        assert bodyless.status_code == 422, bodyless.text

        tasks = client.get(
            "/v1/review-tasks", params={"household_id": household_id, "limit": 100}
        ).json()
        mine = next(item for item in tasks["items"] if item["id"] == task_id)
        assert mine["status"] == "open"
        detail = client.get(
            f"/v1/assets/{food_asset}", params={"household_id": household_id}
        ).json()
        expiry = [a for a in detail["assertions"] if a["field_path"].endswith("expiry_date")]
        assert len(expiry) == 1
        assert expiry[0]["value"] == {"status": "unknown"}
        assert expiry[0]["review_state"] == "needs_evidence"

        entered = client.post(
            f"{EXP}/assets/{food_asset}/expiry",
            params={"household_id": household_id},
            json={"expiry_date": "2030-05-06"},
        )
        assert entered.status_code == 200, entered.text
        assert task_id in entered.json()["resolved_review_task_ids"]
        after = client.get(
            f"/v1/assets/{food_asset}", params={"household_id": household_id}
        ).json()
        accepted = [
            a
            for a in after["assertions"]
            if a["field_path"].endswith("expiry_date") and a["review_state"] == "accepted"
        ]
        assert len(accepted) == 1
        assert accepted[0]["value"]["expiry_date"] == "2030-05-06"


def test_controls_non_perishable_needs_no_task_and_non_data_task_resolves_bare(sg188_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = sg188_db
    with TestClient(app) as client:
        non_perishable = _post_asset(client, household_id, "Plain glass jar")
        classified = client.post(
            f"{EXP}/assets/{non_perishable}/classification",
            params={"household_id": household_id},
            json={"category": "non_perishable"},
        )
        assert classified.status_code == 200, classified.text
        assert classified.json()["expiry_assertion"] is None
        assert classified.json()["review_task"] is None

        collision = ReviewTask(
            task_type="identifier_collision",
            priority="high",
            subject_ref="sg188-candidate",
            proposed_change=json.dumps({"candidate_id": "sg188-candidate"}),
            status="open",
            household_id=household_id,
        )
        session.add(collision)
        session.commit()
        resolved = client.post(
            f"/v1/review-tasks/{collision.id}/resolve",
            params={"household_id": household_id},
            json={},
        )
        assert resolved.status_code == 200, resolved.text
        assert resolved.json()["status"] == "resolved"


def test_malformed_cursor_refused_and_valid_25_row_walk_is_lossless(sg188_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = sg188_db
    with TestClient(app) as client:
        created_ids = [_post_asset(client, household_id, f"Tied row {index:02d}") for index in range(25)]
        tied = datetime(2026, 10, 13, 12, 0, 0)
        session.query(Asset).filter(Asset.id.in_(created_ids)).update(
            {"created_at": tied}, synchronize_session=False
        )
        session.commit()

        malformed = client.get(
            "/v1/assets",
            params={"household_id": household_id, "cursor": "%%%not-a-cursor%%%"},
        )
        assert malformed.status_code == 422, malformed.text
        empty = client.get(
            "/v1/assets", params={"household_id": household_id, "cursor": ""}
        )
        assert empty.status_code == 422, empty.text
        tasks_malformed = client.get(
            "/v1/review-tasks",
            params={"household_id": household_id, "cursor": "%%%not-a-cursor%%%"},
        )
        assert tasks_malformed.status_code == 422, tasks_malformed.text

        seen: list[str] = []
        cursor: str | None = None
        pages = 0
        while True:
            params: dict[str, object] = {"household_id": household_id, "limit": 10}
            if cursor is not None:
                params["cursor"] = cursor
            page = client.get("/v1/assets", params=params)
            assert page.status_code == 200, page.text
            body = page.json()
            seen.extend(item["id"] for item in body["items"])
            pages += 1
            cursor = body["next_cursor"]
            if cursor is None:
                break
            assert pages < 5

        assert pages == 3
        assert len(seen) == 25
        assert len(set(seen)) == 25
        assert set(seen) == set(created_ids)
        db_order = [
            row[0]
            for row in session.execute(
                select(Asset.id)
                .where(Asset.household_id == household_id)
                .order_by(Asset.created_at.desc(), Asset.id.desc())
            )
        ]
        assert seen == db_order


def test_default_asset_list_excludes_archived_and_explicit_filter_includes(sg188_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = sg188_db
    with TestClient(app) as client:
        active_one = _post_asset(client, household_id, "Active one")
        active_two = _post_asset(client, household_id, "Active two")
        archived = _post_asset(client, household_id, "Archived one")
        gone = client.delete(
            f"/v1/assets/{archived}", params={"household_id": household_id}
        )
        assert gone.status_code == 200, gone.text

        default = client.get(
            "/v1/assets", params={"household_id": household_id, "limit": 100}
        )
        assert default.status_code == 200, default.text
        default_ids = {item["id"] for item in default.json()["items"]}
        assert archived not in default_ids
        assert default_ids == {active_one, active_two}

        explicit = client.get(
            "/v1/assets",
            params={"household_id": household_id, "status": "ARCHIVED", "limit": 100},
        )
        assert explicit.status_code == 200, explicit.text
        assert {item["id"] for item in explicit.json()["items"]} == {archived}

        active_only = client.get(
            "/v1/assets",
            params={"household_id": household_id, "status": "ACTIVE", "limit": 100},
        )
        assert {item["id"] for item in active_only.json()["items"]} == {active_one, active_two}


def test_expiry_status_reports_archived_nowhere(sg188_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = sg188_db
    with TestClient(app) as client:
        active = _post_asset(client, household_id, "Dated active")
        classified = client.post(
            f"{EXP}/assets/{active}/classification",
            params={"household_id": household_id},
            json={"category": "food"},
        )
        assert classified.status_code == 200, classified.text
        entered = client.post(
            f"{EXP}/assets/{active}/expiry",
            params={"household_id": household_id},
            json={"expiry_date": "2030-05-06"},
        )
        assert entered.status_code == 200, entered.text

        archived = _post_asset(client, household_id, "Dateless archived")
        archived_classified = client.post(
            f"{EXP}/assets/{archived}/classification",
            params={"household_id": household_id},
            json={"category": "food"},
        )
        assert archived_classified.status_code == 200, archived_classified.text
        assert archived_classified.json()["expiry_assertion"]["review_state"] == "needs_evidence"
        gone = client.delete(
            f"/v1/assets/{archived}", params={"household_id": household_id}
        )
        assert gone.status_code == 200, gone.text

        status = client.get(
            f"{EXP}/status", params={"household_id": household_id, "as_of": "2026-10-13"}
        )
        assert status.status_code == 200, status.text
        body = status.json()
        row_ids = {row["asset_id"] for row in body["rows"]}
        unresolved_ids = {row["asset_id"] for row in body["unresolved_rows"]}
        assert row_ids == {active}
        assert archived not in row_ids
        assert archived not in unresolved_ids
        assert unresolved_ids == set()
        assert body["summary"]["total"] == 1
