"""SG-026 eval smoke runner (fake only — no key, no network, no SDK).

Reads the committed corpus in eval/corpus/ (PG-EV-07: the smoke input is
pushed from committed fixtures, never authored at runtime), validates each
provider_output under the strict ExtractionOutput schema, scores field
accuracy vs ground truth (including expected-unknown cases), applies the
needs_evidence bridge in a temp-SQLite sandbox, and reads the correction
rate from the audit_event table there.

Scores are BASELINES, not targets — no tuning happens in this slice.
Exits non-zero on corpus-integrity failure only (missing ground truth,
missing expectation class, or a provider_output that fails strict parse).
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.db import Base  # noqa: E402
from app.models import Asset, AuditEvent, Household, ReviewTask  # noqa: E402
from app.plugins import expiry_tracker  # noqa: E402
from app.services.providers.schemas import parse_extraction_output  # noqa: E402

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
EXPECTATION_CLASSES = frozenset({"exact", "unknown-expected", "needs-evidence"})


def check_integrity(raw: dict, path: Path) -> list[str]:
    problems: list[str] = []
    for key in ("id", "class", "provider_output", "ground_truth"):
        if key not in raw:
            problems.append(f"{path.name}: missing key {key!r}")
    ground = raw.get("ground_truth")
    if not isinstance(ground, dict):
        problems.append(f"{path.name}: ground truth missing")
        return problems
    for key in ("items", "unknowns", "needs_evidence", "expectation_class"):
        if key not in ground:
            problems.append(f"{path.name}: ground truth missing {key!r}")
    if ground.get("expectation_class") not in EXPECTATION_CLASSES:
        problems.append(f"{path.name}: expectation class missing or unknown")
    try:
        parse_extraction_output(raw.get("provider_output"))
    except Exception as exc:
        problems.append(f"{path.name}: provider_output fails strict parse: {exc}")
    return problems


def score_fixture(raw: dict) -> dict[str, float]:
    parsed = parse_extraction_output(raw["provider_output"])
    ground = raw["ground_truth"]
    needs_match = 1.0 if parsed.needs_evidence == ground["needs_evidence"] else 0.0
    unknowns_match = 1.0 if set(parsed.unknowns) == set(ground["unknowns"]) else 0.0
    gt_items = ground["items"]
    hits = 0
    for index, gt_item in enumerate(gt_items):
        if index >= len(parsed.items):
            continue
        got = parsed.items[index]
        if got.name == gt_item["name"] and got.expiry_date == gt_item["expiry_date"]:
            hits += 1
    items_match = hits / max(len(gt_items), 1)
    return {
        "needs": needs_match,
        "unknowns": unknowns_match,
        "items": items_match,
        "overall": (needs_match + unknowns_match + items_match) / 3.0,
    }


def run_bridge_sandbox(fixture_rows: list[dict]) -> dict[str, int]:
    tmp = Path(tempfile.mkdtemp(prefix="storagegenie-sg026-eval-"))
    engine = create_engine(f"sqlite:///{tmp / 'eval.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()
    try:
        household = Household(name="SG-026 eval household")
        session.add(household)
        session.commit()
        tasks_created = 0
        for row in fixture_rows:
            parsed = parse_extraction_output(row["provider_output"])
            if not parsed.needs_evidence:
                continue
            asset = Asset(
                household_id=household.id,
                display_name=row["id"],
                asset_type="product",
                status="ACTIVE",
            )
            session.add(asset)
            session.commit()
            _, task = expiry_tracker.apply_extraction_result(session, asset, parsed)
            session.commit()
            if task is not None:
                tasks_created += 1
        total = session.query(ReviewTask).count()
        resolved = session.query(ReviewTask).filter_by(status="resolved").count()
        audit_writes = (
            session.query(AuditEvent).filter_by(action="plugin.assertion.write").count()
        )
        assert total == tasks_created
        return {"tasks_created": total, "tasks_resolved": resolved, "audit_writes": audit_writes}
    finally:
        session.close()
        engine.dispose()


def main() -> int:
    fixtures = sorted(CORPUS_DIR.glob("*.json"))
    problems: list[str] = []
    if len(fixtures) != 5:
        problems.append(f"expected 5 fixtures, found {len(fixtures)}")
    rows: list[dict] = []
    for path in fixtures:
        raw = json.loads(path.read_text(encoding="utf-8"))
        rows.append(raw)
        problems.extend(check_integrity(raw, path))
    if problems:
        print("CORPUS INTEGRITY FAILURE")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    scores: dict[str, dict[str, float]] = {}
    for raw in rows:
        scores[str(raw["id"])] = score_fixture(raw)
        line = scores[str(raw["id"])]
        print(
            f"fixture {raw['id']}: score={line['overall']:.3f} "
            f"needs={line['needs']:.0f} unknowns={line['unknowns']:.0f} items={line['items']:.2f}"
        )
    accuracy = sum(line["overall"] for line in scores.values()) / len(scores)
    unknown_cases = [r for r in rows if r["ground_truth"]["expectation_class"] != "exact"]
    unknown_pass = sum(
        1
        for r in rows
        if r["ground_truth"]["expectation_class"] != "exact"
        and scores[str(r["id"])]["unknowns"] == 1.0
        and scores[str(r["id"])]["needs"] == 1.0
    )
    bridge = run_bridge_sandbox(rows)
    created = bridge["tasks_created"]
    resolved = bridge["tasks_resolved"]
    rate = (resolved / created) if created else 0.0
    print(f"field_accuracy={accuracy:.3f} over {len(scores)} fixtures")
    print(f"expected_unknown_cases={unknown_pass}/{len(unknown_cases)}")
    print(
        f"correction_rate={resolved}/{created}={rate:.3f} "
        f"(audit_event plugin.assertion.write rows={bridge['audit_writes']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
