"""SG-186 G2 probe: per-read cost of serve-time rehash on a fixture population.

Disposable DATABASE_URL/STORAGE_ROOT are asserted before the app import; the
probe drives the REAL GET /v1/evidence/{id}/file route through TestClient on
disposable state (no production, no network, no provider). Run from the
candidate tree and from a base worktree at the packet's BASE commit; the
candidate-minus-base delta is the measured per-read verification overhead.

Run (candidate):
  cd backend && PYTHONPATH=. venv/bin/python ../docs/worklogs/SG-186_probe_overhead.py
Run (base worktree):
  cd /tmp/opencode/sg186-base/backend && PYTHONPATH=. \
      /home/andrei/StorageGenie/backend/venv/bin/python \
      /home/andrei/StorageGenie/docs/worklogs/SG-186_probe_overhead.py
"""

from __future__ import annotations

import hashlib
import os
import statistics
import tempfile
import time
from pathlib import Path

TEMP_ROOT = Path(tempfile.mkdtemp(prefix="sg186-overhead-"))
os.environ["DATABASE_URL"] = f"sqlite:///{TEMP_ROOT / 'storagegenie.db'}"
os.environ["STORAGE_ROOT"] = str(TEMP_ROOT / "storage")
assert "sg186-overhead-" in os.environ["DATABASE_URL"], "database url not disposable"
assert "sg186-overhead-" in os.environ["STORAGE_ROOT"], "storage root not disposable"

from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Household  # noqa: E402

POPULATION = [
    (256 * 1024, 40),
    (2 * 1024 * 1024, 30),
    (8 * 1024 * 1024, 20),
    (20 * 1024 * 1024, 12),
]


def pdf_of_size(size: int) -> bytes:
    prefix = b"%PDF-1.4\n"
    suffix = b"\n%%EOF\n"
    return prefix + b"0" * (size - len(prefix) - len(suffix)) + suffix


def hash_file_ms(path: Path) -> float:
    started = time.perf_counter()
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    digest.hexdigest()
    return (time.perf_counter() - started) * 1000


def main() -> None:
    assert str(TEMP_ROOT) in settings.database_url, "settings db not disposable"
    assert str(TEMP_ROOT) in settings.storage_root, "settings storage not disposable"
    Base.metadata.create_all(engine)
    session = SessionLocal()
    household = Household(name="SG-186 overhead probe")
    session.add(household)
    session.commit()
    client = TestClient(app)
    print(f"probe_db={settings.database_url}")
    print(f"probe_storage={settings.storage_root}")
    print(f"population={POPULATION}")
    for size, rounds in POPULATION:
        data = pdf_of_size(size)
        uploaded = client.post(
            "/v1/evidence",
            params={"household_id": household.id},
            files={"file": (f"sg186-overhead-{size}.pdf", data, "application/pdf")},
        )
        assert uploaded.status_code == 201, uploaded.text
        evidence = uploaded.json()
        url = f"/v1/evidence/{evidence['id']}/file"
        stored = Path(settings.storage_root) / evidence["storage_key"]
        warm = client.get(url, params={"household_id": household.id})
        assert warm.status_code == 200, warm.text
        hash_ms = statistics.mean(hash_file_ms(stored) for _ in range(5))
        samples = []
        for _ in range(rounds):
            started = time.perf_counter()
            served = client.get(url, params={"household_id": household.id})
            samples.append((time.perf_counter() - started) * 1000)
            assert served.status_code == 200, served.text
        print(
            f"size_bytes={size} rounds={rounds} mean_ms={statistics.mean(samples):.3f} "
            f"median_ms={statistics.median(samples):.3f} min_ms={min(samples):.3f} "
            f"hash_only_mean_ms={hash_ms:.3f}"
        )
    session.close()


if __name__ == "__main__":
    main()
