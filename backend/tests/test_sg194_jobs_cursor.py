"""SG-194 (G1): malformed cursor refused on GET /v1/jobs, never a silent page-1 repeat.

The SG-188 cursor shape mirrored onto the third list surface (`list_jobs`):
an undecodable cursor is a 422 `malformed cursor` instead of a silent skip of
the filter. Real routes on disposable state:

- a malformed (and an empty) cursor is refused 422 on GET /v1/jobs;
- an absent cursor still returns page 1 exactly as before (limit rows in
  created_at/id descending order, next_cursor set when more remain);
- a valid cursor walk over 25 tied-timestamp jobs is lossless (3 pages at
  limit=10, no repeats, full db order).
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Household, Job

JOBS = "/v1/jobs"


@pytest.fixture
def sg194_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "sg194.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr("app.config.settings.storage_root", str(storage_root))
    household = Household(name="SG-194 Household")
    session.add(household)
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _post_job(client: TestClient, household_id: str) -> str:
    response = client.post(
        "/v1/imports", params={"household_id": household_id}, json={"evidence_ids": []}
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def _seed_tied_jobs(session: Session, client: TestClient, household_id: str) -> list[str]:
    created_ids = [_post_job(client, household_id) for _ in range(25)]
    tied = datetime(2026, 10, 15, 12, 0, 0)
    session.query(Job).filter(Job.id.in_(created_ids)).update(
        {"created_at": tied}, synchronize_session=False
    )
    session.commit()
    return created_ids


def _db_order(session: Session, household_id: str) -> list[str]:
    return [
        row[0]
        for row in session.execute(
            select(Job.id)
            .where(Job.household_id == household_id)
            .order_by(Job.created_at.desc(), Job.id.desc())
        )
    ]


def test_malformed_cursor_refused_on_jobs_list(sg194_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg194_db
    with TestClient(app) as client:
        _post_job(client, household_id)
        malformed = client.get(
            JOBS, params={"household_id": household_id, "cursor": "%%%not-a-cursor%%%"}
        )
        assert malformed.status_code == 422, malformed.text
        assert malformed.json()["detail"] == "malformed cursor"
        empty = client.get(JOBS, params={"household_id": household_id, "cursor": ""})
        assert empty.status_code == 422, empty.text
        assert empty.json()["detail"] == "malformed cursor"


def test_absent_cursor_is_first_page_unchanged(sg194_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg194_db
    with TestClient(app) as client:
        _seed_tied_jobs(session, client, household_id)
        first = client.get(JOBS, params={"household_id": household_id, "limit": 10})
        assert first.status_code == 200, first.text
        body = first.json()
        assert body["total"] == 25
        assert [item["id"] for item in body["items"]] == _db_order(session, household_id)[:10]
        assert body["next_cursor"] is not None


def test_valid_cursor_walk_is_lossless(sg194_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = sg194_db
    with TestClient(app) as client:
        created_ids = _seed_tied_jobs(session, client, household_id)
        seen: list[str] = []
        cursor: str | None = None
        pages = 0
        while True:
            params: dict[str, object] = {"household_id": household_id, "limit": 10}
            if cursor is not None:
                params["cursor"] = cursor
            page = client.get(JOBS, params=params)
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
        assert seen == _db_order(session, household_id)
