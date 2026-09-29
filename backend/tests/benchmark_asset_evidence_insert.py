import time
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.asset import Asset
from app.models.evidence import Evidence, asset_evidence
from app.models.household import Household
from app.services.candidates import Candidate, _create_asset_for_candidate

def benchmark():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Setup household
    household = Household(id="h1", name="Test Household")
    db.add(household)
    db.commit()

    # Create 100 evidence records
    evidence_ids = []
    for i in range(100):
        e_id = f"ev_{i}"
        evidence_ids.append(e_id)
        db.add(
            Evidence(
                id=e_id,
                household_id="h1",
                sha256=f"sha_{i:064d}",
                media_type="image/jpeg",
                storage_key=f"key_{i}",
                original_filename=f"file_{i}.jpg",
                size_bytes=1000,
            )
        )
    db.commit()

    proposal = {
        "kind": "new_asset",
        "fields": {
            "display_name": {"value": "Test Item", "source_type": "deterministic"},
        },
    }

    # Benchmark creating asset for candidate with 100 evidence links repeated 100 times
    num_iterations = 100
    start_time = time.perf_counter()
    for iteration in range(num_iterations):
        candidate = Candidate(
            job_id=f"job_{iteration}",
            evidence_ids_json=json.dumps(evidence_ids),
            proposed_fields_json=json.dumps(proposal),
            state="accepted",
            household_id="h1",
        )
        db.add(candidate)
        db.flush()
        _create_asset_for_candidate(db, candidate)

    db.commit()
    elapsed = time.perf_counter() - start_time
    print(f"Benchmark completed: {num_iterations} iterations with {len(evidence_ids)} evidence links each in {elapsed:.4f} seconds ({elapsed/num_iterations*1000:.2f} ms/op)")

if __name__ == "__main__":
    benchmark()
