"""SG-136: assertions are batch-loaded; the per-asset SELECT is gone.

The serialization seam is ``app.api.v1.assets._asset_to_dict``. Pre-slice it
issued one ``SELECT ... FROM assertion WHERE asset_id = ?`` per asset; a
K-asset serialization therefore cost K assertion SELECTs (the N+1). This module
pins the shipped shape: one batched ``SELECT ... WHERE asset_id IN (...)`` for
any number of assets (constant in K), byte-identical output per asset, and a
zero-asset world that issues no assertion SELECT at all.

``backend/tests/fixtures/sg136_asset_dict_baseline.json`` is the fail-pre
capture: the exact ``_asset_to_dict`` output per asset, recorded from the
pre-slice code on a deterministic temp database (see the SG-136 worklog).
"""

from __future__ import annotations

import datetime
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Iterator

import pytest

TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-sg136-tests-"))
TEST_STORAGE_ROOT = TEST_ROOT / "storage"
TEST_STORAGE_ROOT.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import event  # noqa: E402
from sqlalchemy.orm import selectinload  # noqa: E402

from app.models import Asset, Assertion, Household  # noqa: E402

HOUSEHOLD_ID = "hh-1"
EMPTY_HOUSEHOLD_ID = "sg136-empty-hh"
_T0 = datetime.datetime(2026, 1, 1, 0, 0, 0)
FIXTURE = Path(__file__).parent / "fixtures" / "sg136_asset_dict_baseline.json"
_ASSERTION_SELECT = re.compile(r"\bfrom\s+assertion\b", re.IGNORECASE)


class StatementCounter:
    """A real statement seam: counts SQL emitted on the live engine (`PG-SC-12`)."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.statements: list[str] = []

    def __enter__(self) -> StatementCounter:
        event.listen(self.engine, "before_cursor_execute", self._record)
        return self

    def __exit__(self, *exc: object) -> None:
        event.remove(self.engine, "before_cursor_execute", self._record)

    def _record(
        self,
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        self.statements.append(statement)

    @property
    def assertion_selects(self) -> list[str]:
        return [
            s
            for s in self.statements
            if s.lstrip().upper().startswith("SELECT") and _ASSERTION_SELECT.search(s)
        ]


def _reset_rows() -> None:
    from app.db import Base, SessionLocal, engine

    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        session.query(Assertion).filter(Assertion.asset_id.like("ast-%")).delete(
            synchronize_session=False
        )
        session.query(Asset).filter(Asset.household_id == HOUSEHOLD_ID).delete(
            synchronize_session=False
        )
        session.query(Household).filter(Household.id == HOUSEHOLD_ID).delete(
            synchronize_session=False
        )
        session.commit()
    finally:
        session.close()


def _seed(k: int) -> None:
    """Deterministic K-asset world matching the committed baseline fixture.

    Each asset carries four assertions across three field paths, including a
    ``condition`` tie (superseded + accepted) so ordering is exercised, not
    just the happy path.
    """
    from app.db import SessionLocal

    _reset_rows()
    session = SessionLocal()
    try:
        session.add(Household(id=HOUSEHOLD_ID, name="SG-136 Household"))
        session.flush()
        for i in range(k):
            session.add(
                Asset(
                    id=f"ast-{i}",
                    household_id=HOUSEHOLD_ID,
                    display_name=f"Name {i}",
                    asset_type="tool",
                    status="ACTIVE",
                    quantity=i,
                    unit="pieces",
                    condition="good",
                    version=1,
                    created_at=_T0 + datetime.timedelta(seconds=i),
                    updated_at=_T0 + datetime.timedelta(seconds=i),
                )
            )
        session.flush()
        for i in range(k):
            for j, (field_path, value, review_state) in enumerate(
                [
                    ("asset_type", "tool", "accepted"),
                    ("condition", "old", "superseded"),
                    ("condition", "good", "accepted"),
                    ("display_name", f"Name {i}", "accepted"),
                ]
            ):
                session.add(
                    Assertion(
                        id=f"as-{i}-{j}",
                        asset_id=f"ast-{i}",
                        field_path=field_path,
                        value_json=json.dumps(value),
                        source_type="user",
                        review_state=review_state,
                        created_at=_T0 + datetime.timedelta(seconds=i * 10 + j),
                    )
                )
        session.commit()
    finally:
        session.close()


@pytest.fixture(autouse=True)
def _cleanup_sg136_rows() -> Iterator[None]:
    yield
    _reset_rows()


def test_assertion_select_count_constant_in_k() -> None:
    """The batched shape costs ONE assertion SELECT whether K is 3 or 6."""
    from app.api.v1.assets import _asset_to_dict
    from app.db import SessionLocal, engine

    for k in (3, 6):
        _seed(k)
        session = SessionLocal()
        try:
            with StatementCounter(engine) as counter:
                assets = (
                    session.query(Asset)
                    .filter(Asset.household_id == HOUSEHOLD_ID)
                    .order_by(Asset.id)
                    .options(selectinload(Asset.assertions))
                    .all()
                )
                assert len(assets) == k
                outputs = [_asset_to_dict(asset, session) for asset in assets]
            assert len(outputs) == k
            assert len(counter.assertion_selects) == 1, (
                f"k={k} issued {len(counter.assertion_selects)} assertion SELECTs"
            )
        finally:
            session.close()


def test_lazy_per_asset_access_is_the_n_plus_one() -> None:
    """Without the batch option the same serialization is K selects (the N+1)."""
    from app.api.v1.assets import _asset_to_dict
    from app.db import SessionLocal, engine

    k = 6
    _seed(k)
    session = SessionLocal()
    try:
        with StatementCounter(engine) as counter:
            assets = (
                session.query(Asset)
                .filter(Asset.household_id == HOUSEHOLD_ID)
                .order_by(Asset.id)
                .all()
            )
            outputs = [_asset_to_dict(asset, session) for asset in assets]
        assert len(outputs) == k
        assert len(counter.assertion_selects) == k, (
            "expected the lazy relationship to issue one assertion SELECT per "
            f"asset, saw {len(counter.assertion_selects)}"
        )
    finally:
        session.close()


def test_output_is_byte_identical_to_prechange_baseline() -> None:
    """Per-asset output equals the fail-pre capture, direct and over HTTP."""
    from app.api.v1.assets import _asset_to_dict
    from app.db import SessionLocal
    from app.main import app

    baseline: dict[str, dict[str, Any]] = json.loads(FIXTURE.read_text())
    _seed(3)
    session = SessionLocal()
    try:
        assets = (
            session.query(Asset)
            .filter(Asset.household_id == HOUSEHOLD_ID)
            .order_by(Asset.id)
            .options(selectinload(Asset.assertions))
            .all()
        )
        assert {a.id for a in assets} == set(baseline)
        for asset in assets:
            assert _asset_to_dict(asset, session) == baseline[asset.id]

        with TestClient(app) as client:
            for asset in assets:
                response = client.get(
                    f"/v1/assets/{asset.id}", params={"household_id": HOUSEHOLD_ID}
                )
                assert response.status_code == 200
                assert response.json() == baseline[asset.id], (
                    f"HTTP detail diverged from baseline for {asset.id}"
                )
    finally:
        session.close()


def test_empty_asset_world_issues_no_assertion_select() -> None:
    """Zero assets in scope: the batch option emits no assertion SELECT (`PG-SC-07`)."""
    from app.api.v1.assets import _asset_to_dict
    from app.db import SessionLocal, engine

    _seed(3)
    session = SessionLocal()
    try:
        with StatementCounter(engine) as counter:
            assets = (
                session.query(Asset)
                .filter(Asset.household_id == EMPTY_HOUSEHOLD_ID)
                .options(selectinload(Asset.assertions))
                .all()
            )
            outputs = [_asset_to_dict(asset, session) for asset in assets]
        assert outputs == []
        assert counter.assertion_selects == []
    finally:
        session.close()
