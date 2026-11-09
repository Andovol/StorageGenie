"""SG-272: gone with a reason, put back, quick quantities, G0b dateless fix.

Every gate runs in-process on a temp SQLite database; no live database read or
write, no key, no network, no spend. Fixtures follow the nearest existing
asset tests (`test_sg271_flow.py::flow_db`).
"""

from __future__ import annotations

import os
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.models import Asset, Assertion, Household, ReviewTask
from app.services import asset_service
from app.services.reminders.service import record_due


@pytest.fixture
def gone_db(tmp_path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg272.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG-272 Household")
    other = Household(name="SG-272 Other Household")
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


def _fresh(session: Session) -> None:
    session.expire_all()


def _create(client: TestClient, household_id: str, **fields: object) -> dict:  # type: ignore[type-arg]
    payload = {"display_name": "Milk", "asset_type": "product", **fields}
    response = client.post("/v1/assets", params={"household_id": household_id}, json=payload)
    assert response.status_code == 201, response.text
    return response.json()  # type: ignore[no-any-return]


def _classify(client: TestClient, asset_id: str, household_id: str, category: str = "food_beverages") -> None:
    response = client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
        params={"household_id": household_id},
        json={"category": category},
    )
    assert response.status_code == 200, response.text


def _enter_expiry(client: TestClient, asset_id: str, household_id: str, expiry: str) -> None:
    response = client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
        params={"household_id": household_id},
        json={"expiry_date": expiry, "date_type": "expiry_date"},
    )
    assert response.status_code == 200, response.text


def _open_task(session: Session, household_id: str, asset_id: str) -> str:
    task = ReviewTask(
        household_id=household_id,
        subject_ref=asset_id,
        task_type="custom.check",
        priority="normal",
        status="open",
    )
    session.add(task)
    session.commit()
    return task.id


def _snapshot(client: TestClient, household_id: str) -> dict:  # type: ignore[type-arg]
    catalog = client.get("/v1/assets", params={"household_id": household_id, "limit": 100}).json()
    gone_view = client.get(
        "/v1/assets", params={"household_id": household_id, "status": "ARCHIVED", "limit": 100}
    ).json()
    expiry = client.get(
        "/v1/plugins/expiry-tracker/status", params={"household_id": household_id}
    ).json()
    reminders = client.get("/v1/reminders", params={"household_id": household_id}).json()
    tasks = client.get("/v1/review-tasks", params={"household_id": household_id}).json()
    summary = client.get("/v1/analytics/summary", params={"household_id": household_id}).json()
    return {
        "catalog": sorted(row["id"] for row in catalog["items"]),
        "gone_view": sorted(row["id"] for row in gone_view["items"]),
        "expiry_rows": sorted(row["asset_id"] for row in expiry["rows"]),
        "unresolved": sorted(row["asset_id"] for row in expiry["unresolved_rows"]),
        "reminders": sorted(row["asset_id"] for row in reminders["items"]),
        "tasks": sorted(row["subject_ref"] for row in tasks["items"] if row["status"] == "open"),
        "summary_active": summary["assets"]["active"],
        "summary_by_status": summary["assets"]["by_status"],
    }


def _live_asset(client: TestClient, session: Session, household_id: str, days: int = 5) -> str:
    asset = _create(client, household_id, quantity=3, unit="pcs")
    asset_id = str(asset["id"])
    _classify(client, asset_id, household_id)
    _enter_expiry(client, asset_id, household_id, (date.today() + timedelta(days=days)).isoformat())
    _open_task(session, household_id, asset_id)
    _fresh(session)
    record_due(session, household_id, date.today())
    return asset_id


# --- the roadmap cycle: snapshot, gone, assert left, put back, assert equal ---


def test_cycle_gone_and_back_restores_everything(gone_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = gone_db
    with TestClient(app) as client:
        asset_id = _live_asset(client, session, household_id)
        first = _snapshot(client, household_id)
        assert asset_id in first["catalog"]
        assert asset_id in first["expiry_rows"]
        assert asset_id in first["reminders"]
        assert asset_id in first["tasks"]

        gone = client.post(
            f"/v1/assets/{asset_id}/gone",
            params={"household_id": household_id},
            json={"reason": "used_up"},
        )
        assert gone.status_code == 200, gone.text
        assert gone.json()["status"] == "ARCHIVED"
        assert gone.json()["gone_reason"] == "used_up"

        mid = _snapshot(client, household_id)
        assert asset_id not in mid["catalog"]
        assert asset_id in mid["gone_view"]
        assert asset_id not in mid["expiry_rows"]
        assert asset_id not in mid["unresolved"]
        assert asset_id not in mid["reminders"]
        assert asset_id not in mid["tasks"]

        if os.environ.get("SG272_PLANT_BREAK"):
            # PG-EV-01: a deliberately broken put-back — one reader not
            # restored. The final equality below must FAIL on this run.
            broken = dict(mid)
            broken["expiry_rows"] = sorted([*mid["expiry_rows"], asset_id])
            assert broken == first
            return

        back = client.post(f"/v1/assets/{asset_id}/put-back", params={"household_id": household_id})
        assert back.status_code == 200, back.text
        assert back.json()["status"] == "ACTIVE"
        assert back.json()["gone_reason"] is None

        assert _snapshot(client, household_id) == first


# --- all-or-nothing: a failure injected mid-action writes nothing ---


def test_gone_all_or_nothing_on_injected_failure(gone_db, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = gone_db
    with TestClient(app) as client:
        asset_id = _live_asset(client, session, household_id)
        _fresh(session)
        before_status = session.query(Asset).filter_by(id=asset_id).one().status
        before_version = session.query(Asset).filter_by(id=asset_id).one().version
        before_assertions = session.query(Assertion).filter_by(asset_id=asset_id).count()

        real_upsert = asset_service.upsert_assertion
        calls = {"n": 0}

        def _failing_upsert(db: Session, asset_id_arg: str, field_path: str, value: object, household_id: str, **kwargs: object):  # type: ignore[no-untyped-def]
            calls["n"] += 1
            if field_path == asset_service.GONE_REASON_FIELD:
                raise RuntimeError("injected mid-action failure")
            return real_upsert(db, asset_id_arg, field_path, value, household_id, **kwargs)

        monkeypatch.setattr(asset_service, "upsert_assertion", _failing_upsert)
        with pytest.raises(RuntimeError, match="injected mid-action failure"):
            client.post(
                f"/v1/assets/{asset_id}/gone",
                params={"household_id": household_id},
                json={"reason": "given_away"},
            )
        _fresh(session)
        after = session.query(Asset).filter_by(id=asset_id).one()
        assert after.status == before_status == "ACTIVE"
        assert after.version == before_version
        assert session.query(Assertion).filter_by(asset_id=asset_id).count() == before_assertions
        assert asset_service.get_gone_reason(session, asset_id) is None


# --- reasons, terminals, household ---


def test_three_reasons_store_and_read_back(gone_db) -> None:  # type: ignore[no-untyped-def]
    _, household_id, _ = gone_db
    with TestClient(app) as client:
        for reason in ("used_up", "thrown_away", "given_away"):
            asset = _create(client, household_id)
            asset_id = str(asset["id"])
            gone = client.post(
                f"/v1/assets/{asset_id}/gone",
                params={"household_id": household_id},
                json={"reason": reason},
            )
            assert gone.status_code == 200, gone.text
            assert gone.json()["gone_reason"] == reason
            read = client.get(f"/v1/assets/{asset_id}", params={"household_id": household_id})
            assert read.status_code == 200, read.text
            assert read.json()["gone_reason"] == reason
            gone_view = client.get(
                "/v1/assets",
                params={"household_id": household_id, "status": "ARCHIVED", "limit": 100},
            ).json()
            row = next(item for item in gone_view["items"] if item["id"] == asset_id)
            assert row["gone_reason"] == reason
            back = client.post(
                f"/v1/assets/{asset_id}/put-back", params={"household_id": household_id}
            )
            assert back.status_code == 200, back.text


def test_gone_refusals_terminals_and_household(gone_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, other_id = gone_db
    with TestClient(app) as client:
        asset_id = str(_create(client, household_id)["id"])
        unknown = client.post(
            f"/v1/assets/{asset_id}/gone",
            params={"household_id": household_id},
            json={"reason": "recycled"},
        )
        assert unknown.status_code == 422

        # A repeat with the same reason is a no-op success (double-tap safe).
        assert (
            client.post(
                f"/v1/assets/{asset_id}/gone",
                params={"household_id": household_id},
                json={"reason": "used_up"},
            ).status_code
            == 200
        )
        repeat = client.post(
            f"/v1/assets/{asset_id}/gone",
            params={"household_id": household_id},
            json={"reason": "used_up"},
        )
        assert repeat.status_code == 200
        # A different reason while gone is refused until put back.
        assert (
            client.post(
                f"/v1/assets/{asset_id}/gone",
                params={"household_id": household_id},
                json={"reason": "thrown_away"},
            ).status_code
            == 422
        )
        # Put back from gone works; a repeat on live is a no-op success.
        assert (
            client.post(
                f"/v1/assets/{asset_id}/put-back", params={"household_id": household_id}
            ).status_code
            == 200
        )
        assert (
            client.post(
                f"/v1/assets/{asset_id}/put-back", params={"household_id": household_id}
            ).status_code
            == 200
        )
        # A foreign household's item is untouched by either action.
        assert (
            client.post(
                f"/v1/assets/{asset_id}/gone",
                params={"household_id": other_id},
                json={"reason": "used_up"},
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/v1/assets/{asset_id}/put-back", params={"household_id": other_id}
            ).status_code
            == 403
        )

        # DISPOSED and MERGED stay terminal: put back is refused from both.
        _fresh(session)
        doomed = session.query(Asset).filter_by(id=asset_id).one()
        doomed.status = "DISPOSED"
        session.commit()
        assert (
            client.post(
                f"/v1/assets/{asset_id}/put-back", params={"household_id": household_id}
            ).status_code
            == 422
        )
        _fresh(session)
        doomed = session.query(Asset).filter_by(id=asset_id).one()
        doomed.status = "MERGED"
        session.commit()
        assert (
            client.post(
                f"/v1/assets/{asset_id}/put-back", params={"household_id": household_id}
            ).status_code
            == 422
        )

        # PATCH through the shared table now allows only the same added edge.
        fresh_id = str(_create(client, household_id)["id"])
        assert (
            client.patch(
                f"/v1/assets/{fresh_id}",
                params={"household_id": household_id},
                json={"status": "ARCHIVED"},
            ).status_code
            == 200
        )
        assert (
            client.patch(
                f"/v1/assets/{fresh_id}",
                params={"household_id": household_id},
                json={"status": "ACTIVE"},
            ).status_code
            == 200
        )
        archived_id = str(_create(client, household_id)["id"])
        assert (
            client.patch(
                f"/v1/assets/{archived_id}",
                params={"household_id": household_id},
                json={"status": "DISPOSED"},
            ).status_code
            == 422
        )


# --- quantities: server-side −1, floor at 0, way back up ---


def test_quantity_decrement_floor_and_increment(gone_db) -> None:  # type: ignore[no-untyped-def]
    _, household_id, _ = gone_db
    with TestClient(app) as client:
        asset_id = str(_create(client, household_id, quantity=2, unit="pcs")["id"])
        first = client.post(
            f"/v1/assets/{asset_id}/quantity/decrement",
            params={"household_id": household_id},
        )
        assert first.status_code == 200, first.text
        assert first.json()["quantity"] == 1.0
        second = client.post(
            f"/v1/assets/{asset_id}/quantity/decrement",
            params={"household_id": household_id},
        )
        assert second.status_code == 200, second.text
        assert second.json()["quantity"] == 0.0
        # Below 0 is refused and writes nothing.
        refused = client.post(
            f"/v1/assets/{asset_id}/quantity/decrement",
            params={"household_id": household_id},
        )
        assert refused.status_code == 422
        read = client.get(f"/v1/assets/{asset_id}", params={"household_id": household_id})
        assert read.json()["quantity"] == 0.0
        up = client.post(
            f"/v1/assets/{asset_id}/quantity/increment",
            params={"household_id": household_id},
        )
        assert up.status_code == 200, up.text
        assert up.json()["quantity"] == 1.0
        # A gone item's count is frozen until put back.
        assert (
            client.post(
                f"/v1/assets/{asset_id}/gone",
                params={"household_id": household_id},
                json={"reason": "used_up"},
            ).status_code
            == 200
        )
        assert (
            client.post(
                f"/v1/assets/{asset_id}/quantity/decrement",
                params={"household_id": household_id},
            ).status_code
            == 422
        )


# --- G0b I1: a cleared perishable date lists as No date; Non-perishable counts quietly ---


def test_cleared_perishable_date_lists_as_no_date(gone_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id, _ = gone_db
    with TestClient(app) as client:
        asset = _create(client, household_id, quantity=1)
        asset_id = str(asset["id"])
        _classify(client, asset_id, household_id, "food_beverages")
        _enter_expiry(
            client, asset_id, household_id, (date.today() + timedelta(days=9)).isoformat()
        )
        before = client.get(
            "/v1/plugins/expiry-tracker/status", params={"household_id": household_id}
        ).json()
        assert asset_id in [row["asset_id"] for row in before["rows"]]

        cleared = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry/clear",
            params={"household_id": household_id},
            json={},
        )
        assert cleared.status_code == 200, cleared.text

        after = client.get(
            "/v1/plugins/expiry-tracker/status", params={"household_id": household_id}
        ).json()
        assert asset_id not in [row["asset_id"] for row in after["rows"]]
        unresolved = {row["asset_id"]: row["reason"] for row in after["unresolved_rows"]}
        assert unresolved.get(asset_id) == "dateless"
        assert after["summary"].get("dateless", 0) == 0

        # Classifying Non-perishable counts the same item quietly instead.
        _fresh(session)
        response = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
            params={"household_id": household_id},
            json={"category": "non_perishable"},
        )
        assert response.status_code == 200, response.text
        quiet = client.get(
            "/v1/plugins/expiry-tracker/status", params={"household_id": household_id}
        ).json()
        assert asset_id not in [row["asset_id"] for row in quiet["rows"]]
        assert asset_id not in [row["asset_id"] for row in quiet["unresolved_rows"]]
        assert quiet["summary"].get("dateless", 0) == 1
