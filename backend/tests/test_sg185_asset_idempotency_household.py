"""SG-185: asset create idempotency replay is household-scoped (D4, F-SG181-1).

Before this slice, ``post_asset`` looked a key up globally: an ``Idempotency-Key``
first used by household A made ``POST /v1/assets?household_id=B`` return 201 with
A's asset id, A's household and A's payload ignored. The replay lookup is now
qualified by the requesting household; a foreign key behaves as a fresh key for
the requester (own row created, key stays registered to its first household).
Semantics kept and documented: a same-household replay -- changed payload
included -- returns the ORIGINAL row.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-sg185-tests-"))
TEST_STORAGE_ROOT = TEST_ROOT / "storage"
TEST_STORAGE_ROOT.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def db():  # type: ignore[no-untyped-def]
    from app.db import Base, SessionLocal, engine
    from app.models import Household

    Base.metadata.create_all(engine)
    session = SessionLocal()
    first = Household(name="SG-185 Household A")
    second = Household(name="SG-185 Household B")
    session.add_all([first, second])
    session.commit()
    try:
        yield session, first.id, second.id
    finally:
        session.close()


def _post_keyed(client: TestClient, household_id: str, key: str, display_name: str):
    return client.post(
        "/v1/assets",
        params={"household_id": household_id},
        headers={"Idempotency-Key": key},
        json={"display_name": display_name},
    )


def test_foreign_household_key_never_returns_foreign_row(db) -> None:  # type: ignore[no-untyped-def]
    from app.main import app
    from app.models import Asset, AuditEvent, IdempotencyKey

    session, house_a, house_b = db
    key = "sg185-shared-replay-key"

    with TestClient(app) as client:
        first_a = _post_keyed(client, house_a, key, "A keyed drill")
        assert first_a.status_code == 201
        a_id = first_a.json()["id"]
        assert first_a.json()["household_id"] == house_a

        # The defect: B replayed A's key and previously received A's row.
        first_b = _post_keyed(client, house_b, key, "B keyed ladder")
        assert first_b.status_code == 201
        b_body = first_b.json()
        assert b_body["id"] != a_id
        assert b_body["household_id"] == house_b
        assert b_body["display_name"] == "B keyed ladder"

        # A's replay of its own key still returns A's ORIGINAL row.
        replay_a = _post_keyed(client, house_a, key, "A changed payload")
        assert replay_a.status_code == 201
        assert replay_a.json()["id"] == a_id
        assert replay_a.json()["display_name"] == "A keyed drill"

        # Household separation holds on the row B now owns, both directions.
        assert (
            client.get(f"/v1/assets/{a_id}", params={"household_id": house_b}).status_code == 403
        )
        assert (
            client.patch(
                f"/v1/assets/{b_body['id']}",
                params={"household_id": house_a},
                json={"condition": "used"},
            ).status_code
            == 403
        )

    # Persisted state: one asset per household; the key row still maps to A's
    # asset (the key is globally unique, so B's registration legitimately
    # rolls back, leaving the key the property of its first household).
    assert session.query(Asset).filter_by(household_id=house_a).count() == 1
    assert session.query(Asset).filter_by(household_id=house_b).count() == 1
    key_rows = session.query(IdempotencyKey).filter_by(key=key).all()
    assert len(key_rows) == 1
    assert json.loads(key_rows[0].response_json)["id"] == a_id
    b_create_audits = (
        session.query(AuditEvent)
        .filter_by(entity_type="asset", entity_id=b_body["id"], action="asset.create")
        .all()
    )
    assert len(b_create_audits) == 1
    assert b_create_audits[0].household_id == house_b


def test_same_household_replay_returns_original_row_ignoring_changed_payload(db) -> None:  # type: ignore[no-untyped-def]
    from app.main import app
    from app.models import Asset

    session, house_a, _ = db
    key = "sg185-same-household-key"

    with TestClient(app) as client:
        first = _post_keyed(client, house_a, key, "Original name")
        assert first.status_code == 201
        original_id = first.json()["id"]

        changed = _post_keyed(client, house_a, key, "Changed name")
        assert changed.status_code == 201
        assert changed.json()["id"] == original_id
        assert changed.json()["display_name"] == "Original name"

        replay = _post_keyed(client, house_a, key, "Original name")
        assert replay.status_code == 201
        assert replay.json()["id"] == original_id

    assert session.query(Asset).filter_by(household_id=house_a).count() == 1
