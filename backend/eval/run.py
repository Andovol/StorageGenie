"""SG-029 eval runner: image corpus scoring + the ONE metered baseline run.

Offline (default): reads the committed SG-029 manifest, validates every fixture
(image + ground truth + expectation class + category), scores the committed
`provider_output` cache with the strict `ExtractionOutput` schema, runs the
needs_evidence bridge in a temp-SQLite sandbox, and prints field accuracy,
unknown rate and correction rate. No key, no network, zero spend.

Live (`--live`): for each fixture, read the committed image, redact through the
SHARED `redact_image`, load the versioned prompt for the fixture category, and
call the ONE adapter through the SG-028 reader path (`reader.run_ai_extraction`,
which already owns the single §5.3 repair and the per-call ledger). The validated
output is cached back into the fixture JSON so scoring stays offline and
reproducible. Every call's provider-returned model id, latency, usage and cost
are printed, and the run aborts before any call that would take the projected
total past `SPEND_CEILING_USD`.

Consent/provider for a live run are set by environment for that one command
(`SG_CONSENT=true`, `SG_PROVIDER_ID=opencode-go`); the key is read from the host
environment by the adapter and never printed here. `PG-EV-07`: the fixtures are
committed inputs, never authored at runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base  # noqa: E402
from app.models import Asset, AuditEvent, Evidence, Household, Job, ReviewTask  # noqa: E402
from app.models.provider_call import ProviderCall  # noqa: E402
from app.plugins import expiry_tracker  # noqa: E402
from app.services.providers import reader  # noqa: E402
from app.services.providers.opencode_go import estimate_call_cost  # noqa: E402
from app.services.providers.schemas import parse_extraction_output  # noqa: E402

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
MANIFEST_PATH = CORPUS_DIR / "sg029" / "manifest.json"
EXPECTATION_CLASSES = frozenset({"exact", "unknown-expected", "needs-evidence"})
CASE_CLASSES = frozenset({"clean", "glare", "clutter", "partial-label", "no-date-visible"})
CATEGORIES = frozenset({"food", "medicine", "cosmetics"})
SPEND_CEILING_USD = 0.05


# --------------------------------------------------------------------------- #
# Manifest + integrity
# --------------------------------------------------------------------------- #
def load_manifest() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a JSON object")
    return manifest


def manifest_fixture_paths(manifest: dict[str, Any]) -> list[Path]:
    base = CORPUS_DIR / str(manifest["base_dir"])
    return [base / str(name) for name in manifest["fixtures"]]


def check_integrity(raw: dict[str, Any], path: Path) -> list[str]:  # noqa: C901 - flat field checks
    problems: list[str] = []
    for key in ("id", "class", "category", "image", "ground_truth"):
        if key not in raw:
            problems.append(f"{path.name}: missing key {key!r}")
    if raw.get("class") not in CASE_CLASSES:
        problems.append(f"{path.name}: class {raw.get('class')!r} not one of {sorted(CASE_CLASSES)}")
    if raw.get("category") not in CATEGORIES:
        problems.append(f"{path.name}: category {raw.get('category')!r} not one of {sorted(CATEGORIES)}")
    image = raw.get("image")
    if isinstance(image, str):
        if not (path.parent / image).is_file():
            problems.append(f"{path.name}: image missing at {image!r}")
    else:
        problems.append(f"{path.name}: image reference missing")
    ground = raw.get("ground_truth")
    if not isinstance(ground, dict):
        problems.append(f"{path.name}: ground truth missing")
        return problems
    for key in ("items", "unknowns", "needs_evidence", "expectation_class"):
        if key not in ground:
            problems.append(f"{path.name}: ground truth missing {key!r}")
    if ground.get("expectation_class") not in EXPECTATION_CLASSES:
        problems.append(f"{path.name}: expectation class missing or unknown")
    if "provider_output" in raw:
        try:
            parse_extraction_output(raw["provider_output"])
        except Exception as exc:  # noqa: BLE001 - reported, never raised
            problems.append(f"{path.name}: provider_output fails strict parse: {exc}")
    return problems


def check_manifest(manifest: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    listed = [str(name) for name in manifest.get("fixtures", [])]
    if manifest.get("count") != len(listed):
        problems.append(
            f"manifest count {manifest.get('count')!r} != listed fixtures {len(listed)}"
        )
    base = CORPUS_DIR / str(manifest["base_dir"])
    ids: list[str] = []
    for name in listed:
        listed_path = base / name
        if not listed_path.is_file():
            problems.append(f"manifest lists a missing fixture: {name}")
            continue
        ids.append(str(json.loads(listed_path.read_text(encoding="utf-8"))["id"]))
    if len(set(ids)) != len(ids):
        problems.append("fixture ids are not unique")
    on_disk = {p.name for p in base.glob("*.json") if p.name != MANIFEST_PATH.name}
    if on_disk != set(listed):
        problems.append(
            f"fixtures on disk {sorted(on_disk)} != manifest {sorted(listed)}"
        )
    return problems


# --------------------------------------------------------------------------- #
# Scoring (reused from SG-026; name match normalized case/whitespace)
# --------------------------------------------------------------------------- #
def _norm_name(value: object) -> str:
    return str(value or "").strip().lower()


def score_fixture(raw: dict[str, Any]) -> dict[str, float]:
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
        date_fields = [field for field in ("expiry_date", "opened_date") if field in gt_item]
        name_matches = _norm_name(got.name) == _norm_name(gt_item["name"])
        dates_match = all(getattr(got, field) == gt_item[field] for field in date_fields)
        if name_matches and dates_match:
            hits += 1
    items_match = hits / max(len(gt_items), 1)
    return {
        "needs": needs_match,
        "unknowns": unknowns_match,
        "items": items_match,
        "overall": (needs_match + unknowns_match + items_match) / 3.0,
    }


def run_bridge_sandbox(fixture_rows: list[dict[str, Any]]) -> dict[str, int]:
    tmp = Path(tempfile.mkdtemp(prefix="storagegenie-sg029-bridge-"))
    engine = create_engine(f"sqlite:///{tmp / 'eval.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()
    try:
        household = Household(name="SG-029 eval household")
        session.add(household)
        session.commit()
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
            expiry_tracker.apply_extraction_result(session, asset, parsed)
            session.commit()
        total = session.query(ReviewTask).count()
        resolved = session.query(ReviewTask).filter_by(status="resolved").count()
        audit_writes = (
            session.query(AuditEvent).filter_by(action="plugin.assertion.write").count()
        )
        return {"tasks_created": total, "tasks_resolved": resolved, "audit_writes": audit_writes}
    finally:
        session.close()
        engine.dispose()


def _report_scores(rows: list[dict[str, Any]]) -> int:
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
    unknown_rate = (unknown_pass / len(unknown_cases)) if unknown_cases else 0.0
    print(f"field_accuracy={accuracy:.3f} over {len(scores)} fixtures")
    print(f"unknown_rate={unknown_pass}/{len(unknown_cases)}={unknown_rate:.3f}")
    print(
        f"correction_rate={resolved}/{created}={rate:.3f} "
        f"(audit_event plugin.assertion.write rows={bridge['audit_writes']})"
    )
    return 0


# --------------------------------------------------------------------------- #
# Offline / integrity modes
# --------------------------------------------------------------------------- #
def _load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def run_offline(paths: list[Path]) -> int:
    rows = _load_rows(paths)
    missing = [row["id"] for row in rows if "provider_output" not in row]
    if missing:
        print(f"OFFLINE SCORING FAILURE: no provider_output cache for {missing}")
        print("Run the metered leg once (`--live`) to populate the cache.")
        return 1
    return _report_scores(rows)


# --------------------------------------------------------------------------- #
# Live (metered) mode
# --------------------------------------------------------------------------- #
def _live_session() -> tuple[Path, Any, Session]:
    root = Path(tempfile.mkdtemp(prefix="storagegenie-sg029-live-"))
    storage = root / "storage"
    storage.mkdir()
    settings.storage_root = str(storage)
    engine = create_engine(
        f"sqlite:///{root / 'eval.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return root, engine, factory()


def _ledger_calls(rows: list[ProviderCall]) -> list[dict[str, Any]]:
    return [
        {
            "provider": row.provider,
            "model": row.model,
            "latency_ms": row.latency_ms,
            "usage": json.loads(row.usage_json) if row.usage_json else None,
            "cost": row.cost,
            "error_state": row.error_state,
        }
        for row in rows
    ]


def _run_live_fixture(
    session: Session, household_id: str, fixture: dict[str, Any], path: Path
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    image_path = path.parent / str(fixture["image"])
    raw = image_path.read_bytes()
    storage_key = f"sg029/{fixture['id']}.png"
    dest = Path(settings.storage_root) / storage_key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    evidence = Evidence(
        household_id=household_id,
        sha256=hashlib.sha256(raw).hexdigest(),
        media_type="image/png",
        storage_key=storage_key,
        original_filename=image_path.name,
        source_kind="upload",
        size_bytes=len(raw),
    )
    session.add(evidence)
    session.commit()
    job = Job(
        job_type="eval",
        state="RUNNING",
        config_snapshot=json.dumps({"evidence_ids": [evidence.id]}),
        household_id=household_id,
    )
    session.add(job)
    session.commit()
    settings.sg_prompt_category = str(fixture["category"])
    try:
        result = reader.run_ai_extraction(session, job)
    except Exception as exc:  # noqa: BLE001 - a failed fixture is a recorded baseline row
        rows = session.query(ProviderCall).filter_by(job_id=job.id).all()
        return None, {
            "error": f"{type(exc).__name__}: {exc}",
            "calls": _ledger_calls(rows),
            "provider_call_ids": [row.id for row in rows],
        }
    call_ids = [str(value) for value in result.get("provider_call_ids", [])]
    rows = session.query(ProviderCall).filter(ProviderCall.id.in_(call_ids)).all() if call_ids else []
    return result["extraction"], {"calls": _ledger_calls(rows), "provider_call_ids": call_ids}


def run_live(paths: list[Path]) -> int:
    if not settings.opencode_api_key:
        print("METERED LEG BLOCKED: OPENCODE_API_KEY is not present in the environment")
        return 3
    settings.sg_consent = True
    settings.sg_provider_id = "opencode-go"
    enabled, reason = reader.ai_status()
    if not enabled:
        print(f"METERED LEG BLOCKED: ai_status={reason}")
        return 3

    root, engine, session = _live_session()
    spent = 0.0
    printed: list[dict[str, Any]] = []
    print(f"SPEND CEILING=${SPEND_CEILING_USD:.2f}; mode=live provider=opencode-go")
    try:
        household = Household(name="SG-029 eval household")
        session.add(household)
        session.commit()
        for path in paths:
            fixture = json.loads(path.read_text(encoding="utf-8"))
            prompt, _version = reader.load_prompt(str(fixture["category"]))
            image_path = path.parent / str(fixture["image"])
            estimate = estimate_call_cost(image_path.read_bytes(), prompt)
            if spent + 2 * estimate > SPEND_CEILING_USD:
                print(
                    f"ABORT: projected total {spent + 2 * estimate:.4f} exceeds "
                    f"ceiling {SPEND_CEILING_USD:.2f} before fixture {fixture['id']}"
                )
                return 2
            extraction, meta = _run_live_fixture(session, household.id, fixture, path)
            per_fixture = 0.0
            for call in meta["calls"]:
                cost = float(call["cost"] or 0.0)
                per_fixture += cost
                print(
                    f"call fixture={fixture['id']} provider={call['provider']} model={call['model']} "
                    f"latency_ms={call['latency_ms']} usage={json.dumps(call['usage'])} "
                    f"cost=${cost:.6f} error_state={call['error_state']}"
                )
            spent += per_fixture
            if extraction is None:
                print(
                    f"fixture {fixture['id']}: FAILED {meta.get('error')}; "
                    f"fixture_spend=${per_fixture:.6f}"
                )
                printed.append({"id": fixture["id"], "calls": meta["calls"], "error": meta.get("error")})
                continue
            fixture["provider_output"] = extraction
            fixture["provider_calls"] = meta["calls"]
            path.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"fixture {fixture['id']}: cached provider_output; fixture_spend=${per_fixture:.6f}")
            printed.append({"id": fixture["id"], "calls": meta["calls"]})
        print(f"TOTAL_SPEND=${spent:.6f} of ceiling ${SPEND_CEILING_USD:.2f}")
    finally:
        session.close()
        engine.dispose()
    rows = _load_rows(paths)
    return _report_scores(rows)


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SG-029 Food/Medicine eval runner")
    parser.add_argument("--live", action="store_true", help="run the ONE metered corpus run")
    parser.add_argument("--check-only", action="store_true", help="integrity checks only")
    args = parser.parse_args(argv)

    manifest = load_manifest()
    paths = manifest_fixture_paths(manifest)
    problems: list[str] = []
    if len(paths) != manifest["count"]:
        problems.append(f"expected {manifest['count']} fixtures, resolved {len(paths)}")
    problems.extend(check_manifest(manifest))
    rows = _load_rows(paths)
    for raw, path in zip(rows, paths, strict=True):
        problems.extend(check_integrity(raw, path))
    if problems:
        print("CORPUS INTEGRITY FAILURE")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    if args.check_only:
        print(f"corpus integrity OK: {len(paths)} fixtures (manifest count {manifest['count']})")
        return 0
    if args.live:
        return run_live(paths)
    return run_offline(paths)


if __name__ == "__main__":
    raise SystemExit(main())
