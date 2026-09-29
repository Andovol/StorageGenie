import os
import tempfile
import time
from pathlib import Path

temp_dir = Path(tempfile.mkdtemp(prefix="benchmark-asset-evidence-"))
db_path = temp_dir / "benchmark.db"
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
os.environ["STORAGE_ROOT"] = str(temp_dir / "storage")

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.models import Household  # noqa: E402
from app.models.evidence import Evidence  # noqa: E402
from app.services.asset_service import attach_evidence, create_asset  # noqa: E402


def setup_db():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    household = Household(name="Benchmark Household")
    session.add(household)
    session.commit()
    return session, household.id


def generate_evidence(session, household_id, count):
    evidence_ids = []
    for i in range(count):
        e = Evidence(
            household_id=household_id,
            original_filename=f"file_{i}.jpg",
            media_type="image/jpeg",
            storage_key=f"path_{i}_{time.time()}_{i}.jpg",
            size_bytes=100,
            sha256=f"hash_{time.time()}_{i}_{os.urandom(4).hex()}",
        )
        session.add(e)
        session.flush()
        evidence_ids.append(e.id)
    session.commit()
    return evidence_ids


def run_benchmark():
    session, household_id = setup_db()

    counts = [10, 50, 100, 200]
    print("--- BENCHMARK RESULTS ---")

    # 1. Benchmark create_asset
    print("\n[create_asset]")
    for count in counts:
        evidence_ids = generate_evidence(session, household_id, count)
        payload = {
            "display_name": f"Test Asset {count}",
            "asset_type": "item",
            "evidence_ids": evidence_ids,
        }

        start_time = time.perf_counter()
        create_asset(session, household_id, payload)
        duration_ms = (time.perf_counter() - start_time) * 1000
        print(f"create_asset with {count} evidence items: {duration_ms:.2f} ms")

    # 2. Benchmark attach_evidence
    print("\n[attach_evidence]")
    for count in counts:
        evidence_ids = generate_evidence(session, household_id, count)
        payload = {
            "display_name": f"Test Asset Attach {count}",
            "asset_type": "item",
            "evidence_ids": [],
        }
        asset = create_asset(session, household_id, payload)

        start_time = time.perf_counter()
        attach_evidence(session, asset, evidence_ids)
        duration_ms = (time.perf_counter() - start_time) * 1000
        print(f"attach_evidence with {count} evidence items: {duration_ms:.2f} ms")

    session.close()


if __name__ == "__main__":
    run_benchmark()
