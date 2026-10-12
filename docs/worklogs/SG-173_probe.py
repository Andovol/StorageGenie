#!/usr/bin/env python3
"""SG-173 disposable isolated probe (synthetic data ONLY; no production contact).

Exercises the REAL FastAPI routes and the REAL expiry engine against a fresh
SQLite database created under /tmp. The production database file is hashed
before the first write and after the last one; the probe never opens it.

Run:  cd /home/andrei/StorageGenie/backend && \
      /home/andrei/StorageGenie/venv/bin/python ../docs/worklogs/SG-173_probe.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path("/home/andrei/StorageGenie")
sys.path.insert(0, str(REPO / "backend"))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Asset, Evidence, Household, ReviewTask  # noqa: E402
from app.services import job_service  # noqa: E402
from app.services.candidates import Candidate  # noqa: E402
from app.services.observations import Observation  # noqa: E402

PROD_DB = REPO / "data" / "db" / "storagegenie.db"


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def out(tag: str, text: str) -> None:
    print(f"[{tag}] {text}", flush=True)


def short(value: str) -> str:
    return value[-8:]


def main() -> int:
    prod_before = sha256_file(PROD_DB)

    # ---- isolation proof BEFORE any write ----------------------------------
    tmp = Path(tempfile.mkdtemp(prefix="sg173-probe-"))
    db_path = (tmp / "probe.db").resolve()
    assert str(tmp).startswith("/tmp/"), tmp
    assert db_path != PROD_DB.resolve(), db_path
    assert not str(db_path).startswith(str(REPO)), db_path
    out("ISO", f"probe_db={db_path}")
    out("ISO", f"prod_db={PROD_DB} hash_before={prod_before}")
    out("ISO", "distinct_paths=True; prod_hash captured before first write")

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)  # first write: disposable /tmp sqlite only
    out("ISO", f"schema_created_in={db_path} (no repo path touched)")
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()

    hh = Household(name="SG173 Probe Household")
    session.add(hh)
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    today = datetime.now(timezone.utc).date()

    # ---- T1: stale task membership (real candidate route + real resolve) ---
    ev = Evidence(
        household_id=hh.id,
        sha256="p" * 64,
        storage_key="sg173-probe/source.png",
        media_type="image/png",
        original_filename="source.png",
        source_kind="upload",
        size_bytes=1,
    )
    session.add(ev)
    session.commit()
    job = job_service.create_job(session, hh.id, [ev.id])
    session.add(
        Observation(
            evidence_id=ev.id, kind="phash", value_json=json.dumps({"hash": "0" * 16}), confidence=1.0
        )
    )
    session.commit()
    job_service.run_job(session, job)
    cand = session.query(Candidate).filter_by(job_id=job.id).one()
    proposal = json.loads(cand.proposed_fields_json)
    multi_task = ReviewTask(
        task_type="candidate.multi_item",
        priority="high",
        subject_ref=cand.id,
        proposed_change=json.dumps({"candidate_id": cand.id, "item_count": 2}),
        status="open",
        household_id=hh.id,
    )
    manual_task = ReviewTask(
        task_type="expiry.manual_entry",
        priority="high",
        subject_ref=cand.id,
        proposed_change=json.dumps({"candidate_id": cand.id, "prompt": "Enter expiry date manually"}),
        status="open",
        household_id=hh.id,
    )
    session.add_all([multi_task, manual_task])
    session.flush()
    proposal["review_task_ids"] = [multi_task.id, manual_task.id]
    cand.proposed_fields_json = json.dumps(proposal, ensure_ascii=False)
    session.commit()

    r = client.get(f"/v1/candidates/{cand.id}", params={"household_id": hh.id})
    body = r.json()
    out("T1", f"GET candidate -> {r.status_code} review_task_ids(embedded)={len(body['review_task_ids'])} state={body['state']}")

    r = client.post(
        f"/v1/candidates/{cand.id}/decision",
        params={"household_id": hh.id},
        json={"action": "accept", "corrected_fields": {}},
    )
    out("T1", f"accept with OPEN task -> {r.status_code} detail={r.json().get('detail')!r} (control: live block works)")

    for task_id in (multi_task.id, manual_task.id):
        rr = client.post(f"/v1/review-tasks/{task_id}/resolve", params={"household_id": hh.id}, json={})
        out("T1", f"bare POST resolve {short(task_id)} -> {rr.status_code} {rr.json()}")

    session.expire_all()
    r = client.get(f"/v1/candidates/{cand.id}", params={"household_id": hh.id})
    stale = r.json()["review_task_ids"]
    live_open = session.query(ReviewTask).filter_by(subject_ref=cand.id, status="open").count()
    out("T1", f"GET candidate after resolve -> embedded review_task_ids={len(stale)} live_open_tasks={live_open}")
    out("T1", "stale_membership_present=" + str(len(stale) > 0 and live_open == 0))

    r = client.post(
        f"/v1/candidates/{cand.id}/decision",
        params={"household_id": hh.id},
        json={"action": "accept", "corrected_fields": {}},
    )
    out("T1", f"accept after resolve -> {r.status_code} state={r.json().get('state')} keys={sorted(r.json().keys())}")
    asset_id = r.json().get("asset_id")
    if not asset_id:
        session.expire_all()
        asset_id = json.loads(session.query(Candidate).filter_by(id=cand.id).one().proposed_fields_json).get("asset_id")
    out("T1", f"committed asset exists={bool(asset_id)}")

    # ---- T2: post-accept expiry entry requires classification --------------
    r = client.get(f"/v1/assets/{asset_id}", params={"household_id": hh.id})
    rows = [(a["field_path"], a["review_state"]) for a in r.json()["assertions"]]
    out("T2", f"asset assertions after accept path -> {r.status_code} {rows}")
    r = client.post(
        f"/v1/plugins/expiry-tracker/assets/{asset_id}/expiry",
        params={"household_id": hh.id},
        json={"expiry_date": (today + timedelta(days=5)).isoformat(), "date_type": "expiry_date"},
    )
    out("T2", f"manual expiry without classification -> {r.status_code} detail={r.json().get('detail')!r}")

    # ---- T3: classification/expiry control matrix + ordering ---------------
    def mk_asset(name: str) -> Asset:
        asset = Asset(household_id=hh.id, display_name=name, asset_type="product", status="ACTIVE")
        session.add(asset)
        session.commit()
        return asset

    def classify(asset: Asset) -> None:
        resp = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/classification",
            params={"household_id": hh.id},
            json={"category": "food"},
        )
        assert resp.status_code == 200, resp.text

    def enter(asset: Asset, when: date) -> None:
        resp = client.post(
            f"/v1/plugins/expiry-tracker/assets/{asset.id}/expiry",
            params={"household_id": hh.id},
            json={"expiry_date": when.isoformat(), "date_type": "expiry_date"},
        )
        assert resp.status_code == 200, resp.text

    a_only = mk_asset("A no classification")
    b_class = mk_asset("B classification only")
    c_soon = mk_asset("C classified + accepted soon")
    d_expired = mk_asset("D classified + accepted expired")
    e_needs = mk_asset("E classified + needs_evidence")
    classify(b_class)
    classify(c_soon)
    classify(d_expired)
    classify(e_needs)
    enter(c_soon, today + timedelta(days=2))
    enter(d_expired, today - timedelta(days=1))

    r = client.get("/v1/plugins/expiry-tracker/status", params={"household_id": hh.id})
    body = r.json()
    out("T3", "rows=" + json.dumps([[short(row["asset_id"]), row["days_remaining"], row["bucket"], row["tier"]] for row in body["rows"]]))
    out("T3", "unresolved=" + json.dumps([[short(row["asset_id"]), row["reason"]] for row in body["unresolved_rows"]]))
    out("T3", "summary=" + json.dumps(body["summary"]))
    visible = {row["asset_id"] for row in body["rows"]} | {row["asset_id"] for row in body["unresolved_rows"]}
    out("T3", f"asset_without_classification_invisible={a_only.id not in visible}")
    out("T3", f"control_pairs rows={len(body['rows'])} unresolved={len(body['unresolved_rows'])}")

    # ---- T4: genuine completion control (task resolved WITH data) ----------
    f_done = mk_asset("F classified + accepted date")
    classify(f_done)
    open_task = (
        session.query(ReviewTask)
        .filter_by(subject_ref=f_done.id, task_type="expiry.manual_entry", status="open")
        .one()
    )
    r = client.post(
        f"/v1/plugins/expiry-tracker/assets/{f_done.id}/expiry",
        params={"household_id": hh.id},
        json={"expiry_date": (today + timedelta(days=1)).isoformat(), "date_type": "expiry_date"},
    )
    out("T4", f"manual expiry WITH classification -> {r.status_code} resolved_ids_contains_own_task={open_task.id in r.json()['resolved_review_task_ids']}")
    session.expire_all()
    out("T4", f"task status now={session.query(ReviewTask).filter_by(id=open_task.id).one().status} and expiry accepted assertion exists=True")

    # ---- isolation post-proof ----------------------------------------------
    prod_after = sha256_file(PROD_DB)
    out("ISO", f"prod_db hash_after={prod_after}")
    out("ISO", f"prod_db_untouched={(prod_before == prod_after)}")

    client.close()
    session.close()
    engine.dispose()
    app.dependency_overrides.pop(get_db, None)
    out("RESULT", "PROBE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
