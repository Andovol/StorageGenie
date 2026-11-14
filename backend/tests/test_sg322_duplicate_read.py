"""SG-322 G2: an open or held duplicate reads with no asset_id; a decided one reads its item.

Built on test_sg304_duplicate_pack's _setup. Every read goes through the API the
ReviewPage (GET /v1/candidates/{id}) and the Inbox (GET /v1/jobs/{id}/candidates)
use. Temp SQLite database; no key, no network, no spend.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.test_sg270_flow import flow_db  # noqa: F401  (flow_db is a pytest fixture)
from tests.test_sg304_duplicate_pack import _decide, _setup

SAME_PACK = {"action": "accept"}
ANOTHER_PACK = {"action": "accept", "as_new_pack": True}


def _read(client: TestClient, household_id: str, candidate_id: str) -> dict[str, object]:
    """GET /v1/candidates/{id}: the ReviewPage read."""
    response = client.get(f"/v1/candidates/{candidate_id}", params={"household_id": household_id})
    assert response.status_code == 200, response.text
    return response.json()


def _inbox_item(client: TestClient, household_id: str, job_id: str, candidate_id: str) -> dict[str, object]:
    """GET /v1/jobs/{id}/candidates: the Inbox read, one candidate's row."""
    response = client.get(f"/v1/jobs/{job_id}/candidates", params={"household_id": household_id})
    assert response.status_code == 200, response.text
    rows = [row for row in response.json()["items"] if row["id"] == candidate_id]
    assert len(rows) == 1, response.json()
    return rows[0]


def _duplicate_match_ids(read: dict[str, object]) -> list[str]:
    matches = read["dedup_matches"]
    assert isinstance(matches, list)
    return [str(m["asset_id"]) for m in matches if m.get("type") == "duplicate_of_asset"]


def test_open_duplicate_reads_with_no_asset_id(flow_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    with TestClient(app) as client:
        target_id, candidate_id = _setup(client, session, monkeypatch, household_id, "sg322-open")
        read = _read(client, household_id, candidate_id)

    assert read["state"] == "proposed", read
    assert read["asset_id"] is None, read
    assert _duplicate_match_ids(read) == [target_id], read["dedup_matches"]


def test_held_duplicate_reads_with_no_asset_id(flow_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    with TestClient(app) as client:
        target_id, candidate_id = _setup(client, session, monkeypatch, household_id, "sg322-held")
        held = _decide(client, household_id, candidate_id, {"action": "hold"})
        read = _read(client, household_id, candidate_id)

    assert held["state"] == "held", held
    assert read["state"] == "held", read
    assert read["asset_id"] is None, read
    assert _duplicate_match_ids(read) == [target_id], read["dedup_matches"]


def test_same_pack_reads_the_existing_item(flow_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    with TestClient(app) as client:
        target_id, candidate_id = _setup(client, session, monkeypatch, household_id, "sg322-same")
        decided = _decide(client, household_id, candidate_id, SAME_PACK)
        read = _read(client, household_id, candidate_id)

    assert decided["status"] == "duplicate_linked", decided
    assert read["state"] == "accepted", read
    assert read["asset_id"] == target_id, read


def test_another_pack_reads_the_new_item_not_the_existing_one(flow_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    with TestClient(app) as client:
        target_id, candidate_id = _setup(client, session, monkeypatch, household_id, "sg322-another")
        decided = _decide(client, household_id, candidate_id, ANOTHER_PACK)
        read = _read(client, household_id, candidate_id)

    new_id = str(decided["asset_id"])
    assert decided["status"] == "committed" and decided["created"] is True, decided
    assert new_id != target_id, decided
    assert read["state"] == "accepted", read
    assert read["asset_id"] == new_id, read
    assert read["asset_id"] != target_id, read


@pytest.mark.parametrize("step", ["open", "same", "another"])
def test_inbox_read_agrees_with_the_candidate_read(flow_db, monkeypatch: pytest.MonkeyPatch, step: str) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    with TestClient(app) as client:
        target_id, candidate_id = _setup(client, session, monkeypatch, household_id, f"sg322-inbox-{step}")
        body = {"open": None, "same": SAME_PACK, "another": ANOTHER_PACK}[step]
        decided = _decide(client, household_id, candidate_id, body) if body is not None else None
        read = _read(client, household_id, candidate_id)
        job_id = str(read["job_id"])
        inbox = _inbox_item(client, household_id, job_id, candidate_id)

    expected = {"open": None, "same": target_id, "another": str(decided["asset_id"]) if decided else None}[step]
    assert read["asset_id"] == expected, (step, read)
    assert inbox["asset_id"] == read["asset_id"], (step, inbox, read)
