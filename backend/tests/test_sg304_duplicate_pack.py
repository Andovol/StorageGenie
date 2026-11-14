"""SG-304 G2: a duplicate photo can become another pack; the other choices change nothing else.

Two same-name packs with distinct dates. Runs in-process on a temp SQLite database
through the SG-270 flow helpers; no key, no network, no spend.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Asset
from app.services.candidates import Candidate
from tests.test_phase2_e2e import ScriptedPhase2Provider
from tests.test_sg270_flow import (  # noqa: F401  (flow_db is a pytest fixture)
    _candidate_id,
    _classify,
    _enable,
    _fresh,
    _item,
    _out,
    _run_import,
    _upload,
    flow_db,
)

SAME_NAME = "Olive Oil"
OLD_DATE = "2030-05-06"  # the existing pack's date
NEW_DATE = "2031-02-03"  # the date the same photo's second pack carries


def _olive_output() -> dict[str, object]:
    return _out([_item(SAME_NAME, NEW_DATE, "expiry_date", "L-9", 0.97, ["faint lot"])])


def _setup(client: TestClient, session, monkeypatch, household_id: str, key: str) -> tuple[str, str]:  # type: ignore[no-untyped-def]
    """An existing 'Olive Oil' pack (qty 2, dated OLD_DATE) and a duplicate candidate of the same photo."""
    evidence_id = _upload(client, household_id, f"sg304-{key}.png")
    created = client.post(
        "/v1/assets",
        params={"household_id": household_id},
        json={"display_name": SAME_NAME, "evidence_ids": [evidence_id], "quantity": 2, "unit": "bottle"},
    )
    assert created.status_code == 201, created.text
    target_id = str(created.json()["id"])
    assert _classify(client, target_id, household_id, "food").status_code == 200
    entered = client.post(
        f"/v1/plugins/expiry-tracker/assets/{target_id}/expiry",
        params={"household_id": household_id},
        json={"expiry_date": OLD_DATE},
    )
    assert entered.status_code == 200, entered.text
    _enable(monkeypatch, ScriptedPhase2Provider([_olive_output()]))
    job = _run_import(client, household_id, [evidence_id], key)
    return target_id, _candidate_id(job)


def _snapshot(client: TestClient, household_id: str, asset_id: str) -> dict[str, object]:
    response = client.get(f"/v1/assets/{asset_id}", params={"household_id": household_id})
    assert response.status_code == 200, response.text
    return response.json()


def _expiry(detail: dict[str, object]) -> str | None:
    """The item's expiry date: an accepted row first, else the proposed one a new pack carries."""
    rows = detail["assertions"]
    assert isinstance(rows, list)
    found: dict[str, str] = {}
    for row in rows:
        if not str(row["field_path"]).endswith("expiry_date"):
            continue
        value = row["value"]
        if isinstance(value, dict):
            value = value.get("expiry_date")
        if value and row["review_state"] in {"accepted", "proposed"}:
            found.setdefault(str(row["review_state"]), str(value))
    return found.get("accepted", found.get("proposed"))


def _decide(client: TestClient, household_id: str, candidate_id: str, body: dict[str, object]) -> dict[str, object]:
    response = client.post(
        f"/v1/candidates/{candidate_id}/decision",
        params={"household_id": household_id},
        json=body,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _asset_count(session, household_id: str) -> int:  # type: ignore[no-untyped-def]
    _fresh(session)
    return session.query(Asset).filter_by(household_id=household_id).count()


def _proposal(session, candidate_id: str) -> dict[str, object]:  # type: ignore[no-untyped-def]
    _fresh(session)
    return json.loads(session.query(Candidate).filter_by(id=candidate_id).one().proposed_fields_json)


def test_another_pack_creates_its_own_item_and_leaves_the_existing_one(flow_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    with TestClient(app) as client:
        target_id, candidate_id = _setup(client, session, monkeypatch, household_id, "sg304-another")
        before = _snapshot(client, household_id, target_id)
        decided = _decide(client, household_id, candidate_id, {"action": "accept", "as_new_pack": True})
        after = _snapshot(client, household_id, target_id)

    assert decided["status"] == "committed" and decided["created"] is True, decided
    new_id = str(decided["asset_id"])
    assert new_id != target_id
    assert after == before, "the existing pack changed"
    assert _expiry(before) == OLD_DATE and before["quantity"] == 2
    with TestClient(app) as client:
        new = _snapshot(client, household_id, new_id)
    assert new["display_name"] == SAME_NAME
    assert _expiry(new) == NEW_DATE
    assert new["quantity"] is None, "quantity was merged from the existing pack"
    assert _asset_count(session, household_id) == 2


@pytest.mark.parametrize("body", [{"action": "accept"}, {"action": "accept", "as_new_pack": False}])
def test_same_pack_links_to_the_existing_item_and_keeps_its_date(flow_db, monkeypatch: pytest.MonkeyPatch, body: dict[str, object]) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    with TestClient(app) as client:
        target_id, candidate_id = _setup(client, session, monkeypatch, household_id, "sg304-same")
        before = _snapshot(client, household_id, target_id)
        decided = _decide(client, household_id, candidate_id, body)
        after = _snapshot(client, household_id, target_id)

    assert decided["status"] == "duplicate_linked", decided
    assert str(decided["asset_id"]) == target_id
    assert decided["created"] is False
    assert after == before
    assert _expiry(after) == OLD_DATE
    assert _asset_count(session, household_id) == 1


@pytest.mark.parametrize("action", ["hold", "reject"])
def test_hold_or_reject_with_the_new_option_changes_nothing(flow_db, monkeypatch: pytest.MonkeyPatch, action: str) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = flow_db
    with TestClient(app) as client:
        target_id, candidate_id = _setup(client, session, monkeypatch, household_id, f"sg304-{action}")
        before = _snapshot(client, household_id, target_id)
        decided = _decide(client, household_id, candidate_id, {"action": action, "as_new_pack": True})
        after = _snapshot(client, household_id, target_id)

    assert decided["state"] == ("held" if action == "hold" else "rejected"), decided
    assert after == before
    assert _asset_count(session, household_id) == 1
    proposal = _proposal(session, candidate_id)
    assert proposal["kind"] == "duplicate_of_asset"
    assert "as_new_pack" not in proposal
