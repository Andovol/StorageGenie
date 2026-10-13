"""SG-186: evidence serve-time content verification + household-scoped key replay.

G1 (owner D5): ``GET /v1/evidence/{id}/file`` recomputes the stored bytes'
sha256 and refuses with an explicit 500 ``evidence_integrity_error`` when it
differs from the row's sha256 -- the corrupt bytes are never served. A missing
original stays the untouched 404. Rows whose sha256 is a composed artifact
digest by design (SG-080 transcripts) keep the pre-slice serve path: the D5
control is content-anchored only where the row hash IS a content hash.

Sibling (SG-185 I1 -> SG-186): the evidence upload's idempotency replay is
qualified by the requesting household; a foreign key behaves as a fresh key
for the requester, a same-household replay (changed payload included) returns
the ORIGINAL row.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import tempfile
from pathlib import Path

TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-sg186-tests-"))
TEST_STORAGE_ROOT = TEST_ROOT / "storage"
TEST_STORAGE_ROOT.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


def jpeg_bytes(color: str) -> bytes:
    image = Image.new("RGB", (64, 48), color)
    output = io.BytesIO()
    image.save(output, format="JPEG")
    return output.getvalue()


@pytest.fixture
def env(monkeypatch):  # type: ignore[no-untyped-def]
    database_url = f"sqlite:///{TEST_ROOT / 'storagegenie.db'}"
    storage_root = str(TEST_STORAGE_ROOT)
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("STORAGE_ROOT", storage_root)
    monkeypatch.setattr(settings, "storage_root", storage_root)
    test_engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    factory = sessionmaker(bind=test_engine, expire_on_commit=False)

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    session = factory()
    from app.models import Household

    first = Household(name="SG-186 Household A")
    second = Household(name="SG-186 Household B")
    session.add_all([first, second])
    session.commit()
    try:
        yield session, first.id, second.id
    finally:
        session.close()
        app.dependency_overrides.pop(get_db, None)
        test_engine.dispose()


def _upload(client: TestClient, household_id: str, data: bytes, key: str | None = None):
    headers = {"Idempotency-Key": key} if key is not None else None
    return client.post(
        "/v1/evidence",
        params={"household_id": household_id},
        files={"file": ("sg186-fixture.jpg", data, "image/jpeg")},
        headers=headers,
    )


def test_serve_refuses_same_length_mutation_and_keeps_missing_original_404(env) -> None:  # type: ignore[no-untyped-def]
    _, house_a, _ = env
    original = jpeg_bytes("red")
    with TestClient(app) as client:
        uploaded = _upload(client, house_a, original)
        assert uploaded.status_code == 201
        ev = uploaded.json()

        pristine = client.get(f"/v1/evidence/{ev['id']}/file", params={"household_id": house_a})
        assert pristine.status_code == 200
        assert pristine.content == original
        assert hashlib.sha256(pristine.content).hexdigest() == ev["sha256"]

        stored_path = TEST_STORAGE_ROOT / ev["storage_key"]
        mutated = bytearray(stored_path.read_bytes())
        mutated[len(mutated) // 2] ^= 0x01
        stored_path.write_bytes(bytes(mutated))
        assert len(mutated) == ev["size_bytes"]

        refused = client.get(f"/v1/evidence/{ev['id']}/file", params={"household_id": house_a})
        assert refused.status_code == 500
        assert "evidence_integrity_error" in refused.json()["detail"]

        stored_path.unlink()
        missing = client.get(f"/v1/evidence/{ev['id']}/file", params={"household_id": house_a})
        assert missing.status_code == 404
        assert missing.json()["detail"] == "File not found on storage"


def test_serve_refuses_corrupted_row_sha_despite_ok_integrity_check(env) -> None:  # type: ignore[no-untyped-def]
    session, house_a, _ = env
    original = jpeg_bytes("green")
    with TestClient(app) as client:
        uploaded = _upload(client, house_a, original)
        assert uploaded.status_code == 201
        ev = uploaded.json()

    session.execute(
        text("UPDATE evidence SET sha256 = :sha WHERE id = :evidence_id"),
        {"sha": "0" * 64, "evidence_id": ev["id"]},
    )
    session.commit()
    integrity = session.execute(text("PRAGMA integrity_check")).scalar()
    assert integrity == "ok"

    with TestClient(app) as client:
        refused = client.get(f"/v1/evidence/{ev['id']}/file", params={"household_id": house_a})
    assert refused.status_code == 500
    assert "evidence_integrity_error" in refused.json()["detail"]


def test_foreign_household_key_never_returns_foreign_evidence_row(env) -> None:  # type: ignore[no-untyped-def]
    session, house_a, house_b = env
    key = "sg186-shared-evidence-key"
    a_bytes = jpeg_bytes("blue")
    b_bytes = jpeg_bytes("orange")
    a_replay_bytes = jpeg_bytes("purple")
    with TestClient(app) as client:
        first_a = _upload(client, house_a, a_bytes, key=key)
        assert first_a.status_code == 201
        a_id = first_a.json()["id"]

        first_b = _upload(client, house_b, b_bytes, key=key)
        assert first_b.status_code == 201
        b_body = first_b.json()
        assert b_body["id"] != a_id
        assert b_body["sha256"] == hashlib.sha256(b_bytes).hexdigest()

        replay_a = _upload(client, house_a, a_replay_bytes, key=key)
        assert replay_a.status_code == 201
        assert replay_a.json()["id"] == a_id
        assert replay_a.json()["sha256"] == hashlib.sha256(a_bytes).hexdigest()

        assert (
            client.get(f"/v1/evidence/{a_id}/file", params={"household_id": house_b}).status_code
            == 403
        )
        assert (
            client.get(
                f"/v1/evidence/{b_body['id']}/file", params={"household_id": house_a}
            ).status_code
            == 403
        )

    from app.models import Evidence, IdempotencyKey

    assert session.query(Evidence).filter_by(id=a_id).one().household_id == house_a
    assert session.query(Evidence).filter_by(id=b_body["id"]).one().household_id == house_b
    key_rows = session.query(IdempotencyKey).filter_by(key=key).all()
    assert len(key_rows) == 1
    assert json.loads(key_rows[0].response_json)["id"] == a_id


def test_transcript_artifact_digest_rows_keep_serving(env) -> None:  # type: ignore[no-untyped-def]
    session, house_a, _ = env
    from app.services.evidence_service import store_text_evidence

    text_payload = "SG-186 transcript fixture for the artifact-digest exemption"
    row = store_text_evidence(
        session,
        household_id=house_a,
        source_evidence_id="sg186-source-evidence",
        item_index=0,
        text=text_payload,
    )
    session.commit()
    content = text_payload.encode("utf-8")
    assert row.sha256 != hashlib.sha256(content).hexdigest()

    with TestClient(app) as client:
        served = client.get(f"/v1/evidence/{row.id}/file", params={"household_id": house_a})
    assert served.status_code == 200
    assert served.content == content
