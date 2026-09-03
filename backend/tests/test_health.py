import os
import tempfile
from pathlib import Path

TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-health-tests-"))
TEST_STORAGE_ROOT = TEST_ROOT / "storage"
TEST_STORAGE_ROOT.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)

from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402


def test_health_reports_healthy_status() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok", "storage": "ok"}


def test_health_reports_storage_failure(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    missing_storage_root = TEST_ROOT / "missing-storage"
    monkeypatch.setattr(settings, "storage_root", str(missing_storage_root))

    with TestClient(app) as client:
        response = client.get("/v1/health")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "db": "ok", "storage": "error"}


def test_health_reports_database_failure(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    class BrokenSession:
        def execute(self, statement):  # type: ignore[no-untyped-def]
            raise RuntimeError("database probe failed")

        def close(self) -> None:
            pass

    monkeypatch.setattr("app.db.SessionLocal", lambda: BrokenSession())
    monkeypatch.setattr(settings, "storage_root", str(TEST_STORAGE_ROOT))

    with TestClient(app) as client:
        response = client.get("/v1/health")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "db": "error", "storage": "ok"}
