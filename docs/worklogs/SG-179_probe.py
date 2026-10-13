#!/usr/bin/env python3
"""SG-179 disposable isolated probe (synthetic data ONLY; no production contact).

Exercises REAL routes against a fresh SQLite database and a disposable evidence
root under /tmp. Focus: the recorded import unchecked-branch transition
(REC-ST03/REC-ISS02), the review decision gate on the local SG-175 candidate
source, and expiry manual-entry readback (REC-ST08) with wrong-outcome controls.
Production database and evidence roots are fingerprinted before the first write
and after the last; the probe never opens them.

Run:  cd /home/andrei/StorageGenie/backend && \
      /home/andrei/StorageGenie/backend/venv/bin/python ../docs/worklogs/SG-179_probe.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path("/home/andrei/StorageGenie")
EXPECTED_INTERPRETER = (REPO / "backend" / "venv" / "bin" / "python").resolve()
sys.path.insert(0, str(REPO / "backend"))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Asset, Evidence, Household, ReviewTask  # noqa: E402
from app.plugins.expiry_tracker import EXPIRY_FIELD  # noqa: E402
from app.services import job_service  # noqa: E402

PROD_DB = REPO / "data" / "db" / "storagegenie.db"
PROD_STORES = [REPO / "data" / "storage", REPO / "backend" / "data" / "storage"]

CHECKS_PASSED = 0


class ProbeFailure(Exception):
    pass


def out(tag: str, text: str) -> None:
    print(f"[{tag}] {text}", flush=True)


def check(tag: str, condition: bool, message: str) -> None:
    global CHECKS_PASSED
    if not condition:
        out(tag, f"CHECK_FAILED: {message}")
        raise ProbeFailure(message)
    CHECKS_PASSED += 1


def attempt(fn) -> str | None:  # type: ignore[no-untyped-def]
    try:
        fn()
        return None
    except ProbeFailure as exc:
        out("CTL", f"expected rejection observed: {exc}")
        return str(exc)


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def tree_fingerprint(root: Path) -> str:
    if not root.exists():
        return "absent"
    digest = hashlib.sha256()
    entries = sorted(root.rglob("*"))
    for path in entries:
        rel = str(path.relative_to(root))
        digest.update(rel.encode())
        if path.is_file():
            digest.update(str(path.stat().st_size).encode())
    return f"files={sum(1 for p in entries if p.is_file())} digest={digest.hexdigest()[:16]}"


def short(value: str) -> str:
    return value[-8:]


def main() -> int:
    check("ISO", Path(sys.executable).resolve() == EXPECTED_INTERPRETER,
          f"interpreter {sys.executable!r} != expected {EXPECTED_INTERPRETER!r}")
    out("ISO", f"interpreter={sys.executable}")

    prod_db_before = sha256_file(PROD_DB)
    stores_before = {str(root): tree_fingerprint(root) for root in PROD_STORES}

    tmp = Path(tempfile.mkdtemp(prefix="sg179-probe-"))
    db_path = (tmp / "probe.db").resolve()
    check("ISO", str(tmp).startswith("/tmp/"), f"tmpdir {tmp} not under /tmp")
    check("ISO", db_path != PROD_DB.resolve(), "probe db resolves to the production db")
    check("ISO", not str(db_path).startswith(str(REPO)), f"probe db inside repo: {db_path}")
    settings.storage_root = str(tmp / "storage")
    storage_root = Path(settings.storage_root).resolve()
    check("ISO", str(storage_root).startswith("/tmp/"), f"storage_root {storage_root} not under /tmp")
    storage_root.mkdir(parents=True, exist_ok=True)
    (storage_root / "sg179-probe").mkdir(parents=True, exist_ok=True)
    (storage_root / "sg179-probe" / "source.png").write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\xdac\xfc\xcf\xc0P\x0f\x00\x04\x85\x01\x80\x84\xa9\x8c!\x00\x00\x00\x00IEND\xaeB`\x82')
    settings.sg_provider_id = "fake"
    settings.opencode_api_key = None
    settings.jina_api_key = None
    settings.openrouter_api_key = None
    check("ISO", settings.sg_provider_id == "fake", f"provider {settings.sg_provider_id!r} not forced")
    out("ISO", f"provider_forced=fake keys_nulled=True sg_consent={settings.sg_consent} (no paid provider calls)")
    out("ISO", f"probe_db={db_path} storage_root_override={storage_root}")
    out("ISO", f"prod_db={PROD_DB} hash_before={prod_db_before}")
    for name, fingerprint in stores_before.items():
        out("ISO", f"prod_store={name} before={fingerprint}")

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)  # first write: disposable /tmp sqlite only
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()
    hh = Household(name="SG179 Probe Household")
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

    try:
        ev = Evidence(household_id=hh.id, sha256="c414cd0e204de974f73753c7e28d7638e7b3691bb8b1a2bab6b25bb7fed7ce77", storage_key="sg179-probe/source.png",
                      media_type="image/png", original_filename="source.png", source_kind="upload", size_bytes=1)
        session.add(ev)
        session.commit()

        # ---- T1: unchecked import creates CREATED job; explicit /run is the only starter
        r = client.post("/v1/imports", params={"household_id": hh.id},
                        json={"evidence_ids": [ev.id], "config": {}})
        check("T1", r.status_code == 201, f"POST /v1/imports -> {r.status_code} {r.text[:120]}")
        job_id = r.json()["id"]
        check("T1", r.json()["state"] == "CREATED", f"create response state={r.json()['state']!r}")
        read = client.get(f"/v1/imports/{job_id}", params={"household_id": hh.id})
        check("T1", read.status_code == 200 and read.json()["state"] == "CREATED",
              f"unrun import readback -> {read.status_code} state={read.json().get('state')!r}")
        cands = client.get(f"/v1/jobs/{job_id}/candidates", params={"household_id": hh.id})
        check("T1", cands.status_code == 200 and cands.json()["items"] == [],
              f"unrun import produced candidates {cands.text[:160]}")
        wrong = attempt(lambda: check("T1W", read.json()["state"] == "COMPLETED",
                                      f"WRONG-EXPECTATION CONTROL: unrun import state {read.json()['state']!r} is not COMPLETED"))
        check("T1", wrong is not None and "WRONG-EXPECTATION" in wrong, f"wrong-outcome control not rejected: {wrong!r}")
        out("T1", f"unchecked create -> 201 state=CREATED no candidates; wrong COMPLETED expectation rejected")

        run = client.post(f"/v1/imports/{job_id}/run", params={"household_id": hh.id})
        check("T1", run.status_code == 200, f"explicit /run -> {run.status_code} {run.text[:120]}")
        state_after = run.json()["state"]
        check("T1", state_after != "CREATED", f"explicit /run left state={state_after!r}")
        cands_after = client.get(f"/v1/jobs/{job_id}/candidates", params={"household_id": hh.id}).json()["items"]
        check("T1", len(cands_after) >= 1, f"explicit /run produced no candidates: {cands_after!r}")
        out("T1", f"explicit POST /v1/imports/{{id}}/run -> 200 state={state_after} candidates={len(cands_after)} (runner exists and works)")
        cand_id = cands_after[0]["id"]

        ev_missing = Evidence(household_id=hh.id, sha256="q" * 64, storage_key="sg179-probe/absent.png",
                              media_type="image/png", original_filename="absent.png", source_kind="upload", size_bytes=1)
        session.add(ev_missing)
        session.commit()
        miss = client.post("/v1/imports", params={"household_id": hh.id},
                           json={"evidence_ids": [ev_missing.id], "config": {}})
        miss_run = client.post(f"/v1/imports/{miss.json()['id']}/run", params={"household_id": hh.id})
        check("T1F", miss_run.status_code == 200 and miss_run.json()["state"] == "FAILED",
              f"missing-original run -> {miss_run.status_code} state={miss_run.json().get('state')!r}")
        check("T1F", any("quarantined" in str(e) for e in miss_run.json().get("errors") or []),
              f"missing-original errors={miss_run.json().get('errors')!r}")
        out("T1F", f"missing-original run -> state=FAILED errors={miss_run.json()['errors']} (honest failure state)")

        # ---- T2: local (SG-175 candidate) review gate: live task projection blocks accept
        r = client.get(f"/v1/candidates/{cand_id}", params={"household_id": hh.id})
        check("T2", r.status_code == 200, f"candidate GET -> {r.status_code}")
        check("T2", r.json()["review_task_ids"] == [], f"fresh candidate embedded task ids {r.json()['review_task_ids']!r}")
        task = ReviewTask(task_type="candidate.multi_item", priority="high", subject_ref=cand_id,
                          proposed_change=json.dumps({"candidate_id": cand_id, "item_count": 2}),
                          status="open", household_id=hh.id)
        session.add(task)
        session.commit()
        body = client.get(f"/v1/candidates/{cand_id}", params={"household_id": hh.id}).json()
        check("T2", task.id in body["review_task_ids"],
              f"live open task {short(task.id)} not projected into review_task_ids={body['review_task_ids']!r}")
        blocked = client.post(f"/v1/candidates/{cand_id}/decision", params={"household_id": hh.id},
                              json={"action": "accept", "corrected_fields": {}})
        check("T2", blocked.status_code == 409, f"accept with open task -> {blocked.status_code} {blocked.text[:120]}")
        wrong_accept = attempt(lambda: check("T2W", blocked.status_code == 200,
                                             f"WRONG-EXPECTATION CONTROL: blocked accept returned {blocked.status_code}, not 200"))
        check("T2", wrong_accept is not None and "WRONG-EXPECTATION" in wrong_accept, f"wrong-outcome control not rejected: {wrong_accept!r}")
        resolved = client.post(f"/v1/review-tasks/{task.id}/resolve", params={"household_id": hh.id}, json={})
        check("T2", resolved.status_code == 200 and resolved.json()["status"] == "resolved",
              f"real resolver -> {resolved.status_code}")
        after = client.get(f"/v1/candidates/{cand_id}", params={"household_id": hh.id}).json()
        check("T2", after["review_task_ids"] == [], f"post-resolution ids={after['review_task_ids']!r}")
        ok = client.post(f"/v1/candidates/{cand_id}/decision", params={"household_id": hh.id},
                         json={"action": "accept", "corrected_fields": {}})
        check("T2", ok.status_code == 200 and ok.json()["state"] == "accepted",
              f"accept after resolve -> {ok.status_code} {ok.text[:120]}")
        created_asset_id = ok.json()["asset_id"]
        check("T2", client.get(f"/v1/assets/{created_asset_id}", params={"household_id": hh.id}).status_code == 200,
              "accepted asset not readable")
        out("T2", f"local SG-175 source: live projection blocks accept 409, resolve clears, accept->200 accepted asset readable")

        # ---- T3: expiry manual entry readback on this tree (REC-ST08 data path)
        asset = Asset(household_id=hh.id, display_name="T3 probe expiry", asset_type="product", status="ACTIVE")
        session.add(asset)
        session.commit()
        classified = client.post(f"/v1/plugins/expiry-tracker/assets/{asset.id}/classification",
                                 params={"household_id": hh.id}, json={"category": "food"})
        check("T3", classified.status_code == 200, f"classification -> {classified.status_code} {classified.text[:120]}")
        task_id = classified.json()["review_task"]
        check("T3", isinstance(task_id, str), f"classification opened no manual task: {task_id!r}")
        entry_date = (today + timedelta(days=1)).isoformat()
        expected_value: dict[str, object] = {"expiry_date": entry_date, "date_type": "expiry_date"}
        completion = client.post(f"/v1/plugins/expiry-tracker/assets/{asset.id}/expiry",
                                 params={"household_id": hh.id},
                                 json={"expiry_date": entry_date, "date_type": "expiry_date", "source_evidence_ids": [ev.id]})
        check("T3", completion.status_code == 200, f"manual entry -> {completion.status_code} {completion.text[:120]}")
        check("T3", task_id in completion.json()["resolved_review_task_ids"],
              f"manual entry did not resolve its task: {completion.json()['resolved_review_task_ids']!r}")
        read = client.get(f"/v1/assets/{asset.id}", params={"household_id": hh.id})
        rows = [row for row in read.json()["assertions"]
                if row["field_path"] == EXPIRY_FIELD and row["review_state"] == "accepted"]
        check("T3", len(rows) == 1, f"accepted expiry rows={len(rows)} expected exactly 1")
        check("T3", rows[0]["value"] == expected_value, f"readback {rows[0]['value']!r} != {expected_value!r}")
        check("T3", rows[0]["source_type"] == "user", f"source_type={rows[0]['source_type']!r}")
        wrong_date = (today + timedelta(days=9)).isoformat()
        wrong_rej = attempt(lambda: check("T3W", rows[0]["value"] == {"expiry_date": wrong_date, "date_type": "expiry_date"},
                                          f"WRONG-EXPECTATION CONTROL: stored {rows[0]['value']!r} equals injected wrong date"))
        check("T3", wrong_rej is not None and "WRONG-EXPECTATION" in wrong_rej, f"wrong-value control not rejected: {wrong_rej!r}")
        out("T3", f"manual entry -> 200 task resolved; accepted readback={rows[0]['value']!r} source=user; wrong-date expectation rejected")

        # ---- T4: inherited still-unrepaired paths, measured and labelled
        h_bare = Asset(household_id=hh.id, display_name="T4 probe bare resolve", asset_type="product", status="ACTIVE")
        session.add(h_bare)
        session.commit()
        h_class = client.post(f"/v1/plugins/expiry-tracker/assets/{h_bare.id}/classification",
                              params={"household_id": hh.id}, json={"category": "food"})
        h_task = h_class.json()["review_task"]
        bare = client.post(f"/v1/review-tasks/{h_task}/resolve", params={"household_id": hh.id}, json={})
        check("T4", bare.status_code == 200 and bare.json()["status"] == "resolved", f"bare resolve -> {bare.status_code}")
        h_rows = [row for row in client.get(f"/v1/assets/{h_bare.id}", params={"household_id": hh.id}).json()["assertions"]
                  if row["field_path"] == EXPIRY_FIELD and row["review_state"] == "accepted"]
        check("T4", h_rows == [], f"bare resolve unexpectedly wrote expiry data: {h_rows!r}")
        out("T4", "STILL-UNREPAIRED: bare resolve of expiry.manual_entry -> 200 with zero expiry data")
        i_unclassified = Asset(household_id=hh.id, display_name="T4 probe unclassified", asset_type="product", status="ACTIVE")
        session.add(i_unclassified)
        session.commit()
        status_body = client.get("/v1/plugins/expiry-tracker/status", params={"household_id": hh.id}).json()
        visible = {row["asset_id"] for row in status_body["rows"]} | {row["asset_id"] for row in status_body["unresolved_rows"]}
        check("T4", i_unclassified.id not in visible, "unclassified asset unexpectedly visible")
        out("T4", "STILL-UNREPAIRED: ACTIVE unclassified asset absent from rows and unresolved_rows")

        # ---- isolation post-proof
        prod_db_after = sha256_file(PROD_DB)
        stores_after = {str(root): tree_fingerprint(root) for root in PROD_STORES}
        check("ISO", prod_db_after == prod_db_before, f"prod db hash changed {prod_db_before} -> {prod_db_after}")
        for name, fingerprint in stores_after.items():
            check("ISO", fingerprint == stores_before[name], f"prod store {name} changed: {stores_before[name]} -> {fingerprint}")
        check("ISO", Path(settings.storage_root).resolve() == storage_root, "storage_root override lost")
        out("ISO", f"prod_db hash_after={prod_db_after}")
        out("ISO", "prod_db_untouched=True; prod evidence stores untouched=True; writes confined to override")
    finally:
        app.dependency_overrides.pop(get_db, None)
        client.close()
        session.close()
        engine.dispose()

    out("CHECK", f"checks_passed={CHECKS_PASSED} (every exercised criterion asserted before success)")
    out("RESULT", "PROBE_OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeFailure as exc:
        out("RESULT", f"PROBE_FAILED: {exc}")
        raise SystemExit(1)
