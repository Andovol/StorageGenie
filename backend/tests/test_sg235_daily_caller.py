"""SG-235: the in-app daily reminder caller, its lifespan wiring and its gate.

Every database is a scratch SQLite file built by the committed migration; the
production SQLite and the storage folder are never opened. Fixture dates are
computed from the live clock at execution and passed explicitly (`PG-IC-07`).
The production modules are imported inside the tests so the same file collects
against the start-base tree, where they do not exist.
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
import threading
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import get_db
from app.main import app
from app.models import Asset, Household

ROOT = Path(__file__).resolve().parents[2]

ALLOWED_PATHS = {
    "backend/app/services/reminders/daily.py",
    "backend/app/server.py",
    "backend/app/main.py",
    "backend/Dockerfile",
    "backend/tests/test_sg235_daily_caller.py",
    "frontend/src/routes/ExpiryPage.tsx",
    "frontend/src/routes/ExpiryPage.test.tsx",
    "docs/worklogs/SG-235.log",
    "docs/worklogs/SG-235_report.md",
    "docs/worklogs/SG-235_verify.log",
}

REQUIRED_PATHS = {
    "backend/app/services/reminders/daily.py",
    "backend/app/server.py",
    "backend/app/main.py",
    "backend/Dockerfile",
    "backend/tests/test_sg235_daily_caller.py",
    "frontend/src/routes/ExpiryPage.tsx",
    "frontend/src/routes/ExpiryPage.test.tsx",
}


def _alembic_config(url: str) -> Config:
    config = Config(str(ROOT / "backend" / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "backend" / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def _today() -> date:
    return datetime.now(timezone.utc).date()


@pytest.fixture
def daily_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    url = f"sqlite:///{tmp_path / 'sg235.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    command.upgrade(_alembic_config(url), "head")
    engine = create_engine(url, connect_args={"check_same_thread": False})
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    first = Household(name="SG235 First Household")
    second = Household(name="SG235 Second Household")
    session.add_all([first, second])
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield factory, first.id, second.id, session
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _asset(session: Session, household_id: str, name: str = "SG235 Milk") -> Asset:
    asset = Asset(
        household_id=household_id, display_name=name, asset_type="product", status="ACTIVE"
    )
    session.add(asset)
    session.commit()
    return asset


def _classify(client: TestClient, asset_id: str, household_id: str) -> None:
    response = client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/classification",
        params={"household_id": household_id},
        json={"category": "food_beverages"},
    )
    assert response.status_code == 200, response.text


def _enter_expiry(
    client: TestClient, asset_id: str, household_id: str, expiry: date
) -> None:
    response = client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
        params={"household_id": household_id},
        json={"expiry_date": expiry.isoformat(), "date_type": "expiry_date"},
    )
    assert response.status_code == 200, response.text


def _due_asset(
    client: TestClient, session: Session, household_id: str, expiry: date
) -> Asset:
    asset = _asset(session, household_id)
    _classify(client, asset.id, household_id)
    _enter_expiry(client, asset.id, household_id, expiry)
    return asset


def test_sg235_pass_covers_every_household_with_engine_shaped_rows(
    daily_env,  # type: ignore[no-untyped-def]
) -> None:
    from app.services.reminders import daily, service
    from app.models.reminder import Reminder

    factory, first_id, second_id, session = daily_env
    today = _today()
    client = TestClient(app)
    asset = _due_asset(client, session, first_id, today + timedelta(days=3))

    assert daily.record_due is service.record_due

    started = time.perf_counter()
    result = daily.run_daily_pass(factory, as_of_day=today)
    elapsed = time.perf_counter() - started
    print(
        f"sg235_pass_seconds={elapsed:.4f} "
        f"households={result.households_visited} created={result.reminders_created}"
    )

    assert result.as_of_day == today
    assert result.households_visited == 2
    assert result.reminders_created == 1
    assert result.errors == ()

    check = factory()
    try:
        rows = check.query(Reminder).all()
        assert len(rows) == 1
        row = rows[0]
        assert row.household_id == first_id
        assert row.asset_id == asset.id
        assert row.as_of_day == today.isoformat()
        assert row.status == "unread"
        assert check.query(Reminder).filter_by(household_id=second_id).count() == 0
        assert (
            check.query(Reminder)
            .filter_by(as_of_day=(today + timedelta(days=1)).isoformat())
            .count()
            == 0
        )
        stored_shape = (row.tier, row.bucket, row.days_remaining)
    finally:
        check.close()

    engine_status = client.get(
        "/v1/plugins/expiry-tracker/status",
        params={"household_id": first_id, "as_of": today.isoformat()},
    )
    assert engine_status.status_code == 200, engine_status.text
    engine_row = next(
        entry for entry in engine_status.json()["rows"] if entry["asset_id"] == asset.id
    )
    assert (engine_row["tier"], engine_row["bucket"], engine_row["days_remaining"]) == stored_shape

    _enter_expiry(client, asset.id, first_id, today + timedelta(days=20))
    later = today + timedelta(days=4)
    changed = daily.run_daily_pass(factory, as_of_day=later)
    assert changed.households_visited == 2
    assert changed.reminders_created == 1

    check = factory()
    try:
        later_row = (
            check.query(Reminder)
            .filter_by(asset_id=asset.id, as_of_day=later.isoformat())
            .one()
        )
        assert (later_row.tier, later_row.bucket, later_row.days_remaining) == (
            "upcoming",
            "this-month",
            16,
        )
    finally:
        check.close()

    later_status = client.get(
        "/v1/plugins/expiry-tracker/status",
        params={"household_id": first_id, "as_of": later.isoformat()},
    ).json()
    later_engine = next(
        entry for entry in later_status["rows"] if entry["asset_id"] == asset.id
    )
    assert (later_engine["tier"], later_engine["bucket"], later_engine["days_remaining"]) == (
        "upcoming",
        "this-month",
        16,
    )


def test_sg235_second_pass_same_day_creates_nothing(
    daily_env,  # type: ignore[no-untyped-def]
) -> None:
    from app.services.reminders import daily
    from app.models.reminder import Reminder

    factory, first_id, _second_id, session = daily_env
    today = _today()
    client = TestClient(app)
    _due_asset(client, session, first_id, today + timedelta(days=3))

    first = daily.run_daily_pass(factory, as_of_day=today)
    second = daily.run_daily_pass(factory, as_of_day=today)
    assert first.reminders_created == 1
    assert second.households_visited == 2
    assert second.reminders_created == 0

    check = factory()
    try:
        assert check.query(Reminder).count() == 1
    finally:
        check.close()


def test_sg235_loop_does_not_backfill_missed_days(
    daily_env,  # type: ignore[no-untyped-def]
) -> None:
    from app.services.reminders import daily
    from app.models.reminder import Reminder

    factory, first_id, _second_id, session = daily_env
    today = _today()
    client = TestClient(app)
    asset = _due_asset(client, session, first_id, today + timedelta(days=10))

    baseline = daily.run_daily_pass(factory, as_of_day=today)
    assert baseline.reminders_created == 1

    resumed = today + timedelta(days=3)
    clock_calls: list[date] = []

    def clock() -> date:
        clock_calls.append(resumed)
        return resumed

    async def stop_after_one_pass(seconds: float) -> None:
        raise asyncio.CancelledError

    async def drive() -> None:
        await daily.run_daily_forever(
            factory, clock=clock, sleep=stop_after_one_pass
        )

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(drive())

    assert clock_calls == [resumed]
    check = factory()
    try:
        days = {row.as_of_day for row in check.query(Reminder).all()}
        assert days == {today.isoformat(), resumed.isoformat()}
        assert check.query(Reminder).filter_by(asset_id=asset.id).count() == 2
        for missed in (today + timedelta(days=1), today + timedelta(days=2)):
            assert (
                check.query(Reminder).filter_by(as_of_day=missed.isoformat()).count() == 0
            )
    finally:
        check.close()


def test_sg235_loop_cadence_survives_a_failed_pass(
    daily_env,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.reminders import daily

    factory, _first_id, _second_id, _session = daily_env
    assert daily.DAILY_INTERVAL_SECONDS == 86400
    delays: list[float] = []
    attempts: list[date] = []

    def flaky_pass(session_factory, *, as_of_day=None):  # type: ignore[no-untyped-def]
        assert session_factory is factory
        assert as_of_day is not None
        attempts.append(as_of_day)
        if len(attempts) == 1:
            raise RuntimeError("first pass fails")
        return daily.DailyPassResult(
            as_of_day=as_of_day, households_visited=2, reminders_created=0
        )

    async def fake_sleep(seconds: float) -> None:
        delays.append(seconds)
        if len(delays) == 2:
            raise asyncio.CancelledError

    monkeypatch.setattr(daily, "run_daily_pass", flaky_pass)

    async def drive() -> None:
        await daily.run_daily_forever(
            factory, clock=_today, sleep=fake_sleep
        )

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(drive())

    assert delays == [86400.0, 86400.0]
    assert attempts == [_today(), _today()]


def test_sg235_lifespan_starts_loop_once_and_cancels(
    daily_env,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app import server

    _factory, _first_id, _second_id, _session = daily_env
    started = threading.Event()
    cancelled = threading.Event()
    calls: list[object] = []

    async def spy(*args, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(args)
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            raise

    monkeypatch.setattr(server, "run_daily_forever", spy)

    with TestClient(server.app):
        assert started.wait(timeout=5), "lifespan did not start the loop"
        assert len(calls) == 1

    exit_started = time.perf_counter()
    assert cancelled.wait(timeout=server.SHUTDOWN_TIMEOUT_SECONDS)
    shutdown_seconds = time.perf_counter() - exit_started
    print(f"sg235_shutdown_seconds={shutdown_seconds:.4f}")
    assert shutdown_seconds < 2.0
    assert len(calls) == 1


def test_sg235_health_answers_while_a_pass_is_in_flight(
    daily_env,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app import server
    from app.models.reminder import Reminder

    factory, first_id, _second_id, session = daily_env
    today = _today()
    client = TestClient(app)
    _due_asset(client, session, first_id, today + timedelta(days=3))

    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))

    pass_started = threading.Event()
    release = threading.Event()
    pass_done = threading.Event()

    def blocking_factory():  # type: ignore[no-untyped-def]
        pass_started.set()
        release.wait(timeout=10)
        request_session = factory()
        original_close = request_session.close

        def close_with_done() -> None:
            try:
                original_close()
            finally:
                pass_done.set()

        request_session.close = close_with_done  # type: ignore[method-assign]
        return request_session

    monkeypatch.setattr(server, "SessionLocal", blocking_factory)

    with TestClient(server.app) as served:
        assert pass_started.wait(timeout=5), "daily pass never started"
        started = time.perf_counter()
        response = served.get("/v1/health")
        latency = time.perf_counter() - started
        release.set()
        assert pass_done.wait(timeout=5), "daily pass never finished"
        print(f"sg235_health_latency_seconds={latency:.4f}")

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ok"
    assert latency < 2.0

    check = factory()
    try:
        assert check.query(Reminder).filter_by(as_of_day=today.isoformat()).count() == 1
    finally:
        check.close()


def test_sg235_pass_isolates_a_failing_household(
    daily_env,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.reminders import daily, service

    factory, first_id, second_id, session = daily_env
    today = _today()
    client = TestClient(app)
    asset = _due_asset(client, session, second_id, today + timedelta(days=3))

    calls: list[str] = []
    real_record_due = service.record_due

    def flaky_record_due(db, household_id, as_of_day=None):  # type: ignore[no-untyped-def]
        calls.append(household_id)
        if household_id == first_id:
            raise RuntimeError("boom")
        return real_record_due(db, household_id, as_of_day)

    monkeypatch.setattr(daily, "record_due", flaky_record_due)

    result = daily.run_daily_pass(factory, as_of_day=today)
    assert result.households_visited == 2
    assert result.reminders_created == 1
    assert len(result.errors) == 1
    assert result.errors[0].household_id == first_id
    assert "boom" in result.errors[0].error
    assert set(calls) == {first_id, second_id}

    from app.models.reminder import Reminder

    check = factory()
    try:
        rows = check.query(Reminder).all()
        assert len(rows) == 1
        assert rows[0].household_id == second_id
        assert rows[0].asset_id == asset.id
    finally:
        check.close()


def test_sg235_suite_starts_no_pass_and_creates_no_relative_db(
    tmp_path: Path,
) -> None:
    from app.services.reminders import daily

    assert daily.DAILY_INTERVAL_SECONDS == 86400
    assert list(tmp_path.iterdir()) == []
    relative = ROOT / "backend" / "data" / "db" / "storagegenie.db"
    assert not relative.exists()
    assert not (ROOT / "backend" / "data").exists()

    result = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        cwd=str(ROOT / "backend"),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert not relative.exists()
    assert not (ROOT / "backend" / "data").exists()


def test_sg235_diff_touches_only_the_approved_ceiling() -> None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--name-only", "origin/automation...HEAD"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    paths = {line for line in result.stdout.splitlines() if line.strip()}
    for path in paths:
        assert path in ALLOWED_PATHS, path
    assert REQUIRED_PATHS <= paths
    assert not any(path.startswith("backend/alembic/versions/") for path in paths)
    assert "docker-compose.yml" not in paths
    print("sg235_diff_paths=" + ",".join(sorted(paths)))
