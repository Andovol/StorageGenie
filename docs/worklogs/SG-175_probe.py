#!/usr/bin/env python3
"""SG-175 disposable isolated probe (synthetic data ONLY; no production contact).

Exercises the REAL FastAPI routes (candidate GET/decision, the real task
resolver, expiry classification/completion, asset GET) against a fresh SQLite
database and a disposable evidence root under /tmp. The production database
file and the production evidence roots are fingerprinted before the first
write and after the last; the probe never opens them.

Every exercised criterion runs through `check()` and prints its measured
values; the success footer is unreachable once a check fails.

Run:  cd /home/andrei/StorageGenie/backend && \
      /home/andrei/StorageGenie/backend/venv/bin/python ../docs/worklogs/SG-175_probe.py

Run from `backend/` so the process never reads the repo-root `.env` (pydantic
`env_file` is CWD-relative); the provider is additionally forced to the
deterministic fake in-process before any job step runs.
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
from app.services.candidates import Candidate  # noqa: E402
from app.services.observations import Observation  # noqa: E402

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
    check(
        "ISO",
        Path(sys.executable).resolve() == EXPECTED_INTERPRETER,
        f"interpreter {sys.executable!r} != expected {str(EXPECTED_INTERPRETER)!r}",
    )
    check(
        "ISO",
        Path(sys.prefix) == REPO / "backend" / "venv",
        f"sys.prefix {sys.prefix!r} is not the backend venv",
    )
    out("ISO", f"interpreter={sys.executable} prefix={sys.prefix} (verified against backend/venv)")

    prod_db_before = sha256_file(PROD_DB)
    stores_before = {str(root): tree_fingerprint(root) for root in PROD_STORES}

    tmp = Path(tempfile.mkdtemp(prefix="sg175-probe-"))
    db_path = (tmp / "probe.db").resolve()
    check("ISO", str(tmp).startswith("/tmp/"), f"tmpdir {tmp} not under /tmp")
    check("ISO", db_path != PROD_DB.resolve(), "probe db resolves to the production db")
    check("ISO", not str(db_path).startswith(str(REPO)), f"probe db inside repo: {db_path}")
    settings.storage_root = str(tmp / "storage")
    storage_root = Path(settings.storage_root).resolve()
    check("ISO", str(storage_root).startswith("/tmp/"), f"storage_root {storage_root} not under /tmp")
    storage_root.mkdir(parents=True, exist_ok=True)
    settings.sg_provider_id = "fake"
    settings.opencode_api_key = None
    settings.jina_api_key = None
    settings.openrouter_api_key = None
    check("ISO", settings.sg_provider_id == "fake", f"provider {settings.sg_provider_id!r} not forced")
    out(
        "ISO",
        f"provider_forced=fake keys_nulled=True sg_consent={settings.sg_consent} (no paid provider calls)",
    )
    out("ISO", f"probe_db={db_path}")
    out("ISO", f"storage_root_override={storage_root} (evidence writes isolated before first write)")
    out("ISO", f"prod_db={PROD_DB} hash_before={prod_db_before}")
    for name, fingerprint in stores_before.items():
        out("ISO", f"prod_store={name} before={fingerprint}")

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)  # first write: disposable /tmp sqlite only
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()

    hh = Household(name="SG175 Probe Household")
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
        # ---- T1: repaired blocked state (real GET/decision/resolve) ---------
        ev = Evidence(
            household_id=hh.id,
            sha256="p" * 64,
            storage_key="sg175-probe/source.png",
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
        embedded = [
            ReviewTask(
                task_type="candidate.multi_item",
                priority="high",
                subject_ref=cand.id,
                proposed_change=json.dumps({"candidate_id": cand.id, "item_count": 2}),
                status="open",
                household_id=hh.id,
            ),
            ReviewTask(
                task_type="expiry.manual_entry",
                priority="high",
                subject_ref=cand.id,
                proposed_change=json.dumps({"candidate_id": cand.id, "prompt": "Enter expiry date manually"}),
                status="open",
                household_id=hh.id,
            ),
        ]
        omitted = ReviewTask(
            task_type="identifier_collision",
            priority="high",
            subject_ref=cand.id,
            proposed_change=json.dumps({"candidate_id": cand.id}),
            status="open",
            household_id=hh.id,
        )
        session.add_all([*embedded, omitted])
        session.flush()
        proposal["review_task_ids"] = [task.id for task in embedded]
        cand.proposed_fields_json = json.dumps(proposal, ensure_ascii=False)
        session.commit()
        live_open_ids = {task.id for task in [*embedded, omitted]}

        r = client.get(f"/v1/candidates/{cand.id}", params={"household_id": hh.id})
        body = r.json()
        check("T1", r.status_code == 200, f"GET candidate status={r.status_code}")
        check(
            "T1",
            set(body["review_task_ids"]) == live_open_ids,
            f"review_task_ids={body['review_task_ids']} != live open {sorted(live_open_ids)}",
        )
        check(
            "T1",
            omitted.id in body["review_task_ids"],
            "live task absent from the proposal snapshot is not projected",
        )
        out(
            "T1",
            f"GET candidate -> {r.status_code} live_ids={len(body['review_task_ids'])} "
            f"includes_omitted={omitted.id in body['review_task_ids']} state={body['state']}",
        )

        r = client.post(
            f"/v1/candidates/{cand.id}/decision",
            params={"household_id": hh.id},
            json={"action": "accept", "corrected_fields": {}},
        )
        check("T1", r.status_code == 409, f"accept with live open tasks status={r.status_code}")
        out("T1", f"accept with live open tasks -> {r.status_code} detail={r.json().get('detail')!r} (control)")

        for task in [*embedded, omitted]:
            rr = client.post(
                f"/v1/review-tasks/{task.id}/resolve", params={"household_id": hh.id}, json={}
            )
            check("T1", rr.status_code == 200 and rr.json()["status"] == "resolved", f"resolve {short(task.id)} -> {rr.status_code}")
        out("T1", f"real resolver resolved all {len(live_open_ids)} live tasks")

        r = client.get(f"/v1/candidates/{cand.id}", params={"household_id": hh.id})
        check(
            "T1",
            r.json()["review_task_ids"] == [],
            f"post-resolution review_task_ids={r.json()['review_task_ids']} not empty",
        )
        session.expire_all()
        live_open = session.query(ReviewTask).filter_by(subject_ref=cand.id, status="open").count()
        check("T1", live_open == 0, f"live open task rows={live_open}")
        out("T1", f"GET candidate after resolution -> review_task_ids={r.json()['review_task_ids']} live_open_tasks={live_open}")

        r = client.post(
            f"/v1/candidates/{cand.id}/decision",
            params={"household_id": hh.id},
            json={"action": "accept", "corrected_fields": {}},
        )
        check("T1", r.status_code == 200 and r.json()["state"] == "accepted", f"accept after resolution -> {r.status_code}")
        asset_id = r.json()["asset_id"]
        asset_read = client.get(f"/v1/assets/{asset_id}", params={"household_id": hh.id})
        check("T1", asset_read.status_code == 200, f"committed asset GET -> {asset_read.status_code}")
        out("T1", f"accept after resolution -> 200 state=accepted asset_exists=True (repaired blocked state)")

        # ---- T2: measured expiry completion readback ------------------------
        def mk_asset(name: str) -> Asset:
            asset = Asset(household_id=hh.id, display_name=name, asset_type="product", status="ACTIVE")
            session.add(asset)
            session.commit()
            return asset

        def classify(asset: Asset) -> dict[str, object]:
            resp = client.post(
                f"/v1/plugins/expiry-tracker/assets/{asset.id}/classification",
                params={"household_id": hh.id},
                json={"category": "food"},
            )
            check("T2", resp.status_code == 200, f"classification {short(asset.id)} -> {resp.status_code} {resp.text[:120]}")
            return resp.json()

        def read_accepted_expiry(asset_id: str, expected: dict[str, object]) -> dict[str, object]:
            resp = client.get(f"/v1/assets/{asset_id}", params={"household_id": hh.id})
            check("T2", resp.status_code == 200, f"asset GET {short(asset_id)} -> {resp.status_code}")
            rows = [
                row
                for row in resp.json()["assertions"]
                if row["field_path"] == EXPIRY_FIELD and row["review_state"] == "accepted"
            ]
            check("T2", len(rows) == 1, f"accepted EXPIRY_FIELD count={len(rows)} expected exactly 1")
            observed = rows[0]
            check(
                "T2",
                observed["value"] == expected,
                f"value mismatch expected {expected!r} observed {observed['value']!r}",
            )
            check("T2", observed["source_type"] == "user", f"source_type={observed['source_type']!r}")
            return observed

        f_done = mk_asset("F probe classified + accepted date")
        classified = classify(f_done)
        task_id = classified["review_task"]
        check("T2", isinstance(task_id, str), f"classification did not open a manual task: {task_id!r}")
        check(
            "T2",
            classified["expiry_assertion"]["review_state"] == "needs_evidence",
            f"pre-entry expiry review_state={classified['expiry_assertion']['review_state']!r}",
        )
        pre_rows = [
            row
            for row in client.get(f"/v1/assets/{f_done.id}", params={"household_id": hh.id}).json()["assertions"]
            if row["field_path"] == EXPIRY_FIELD and row["review_state"] == "accepted"
        ]
        check("T2", pre_rows == [], f"accepted EXPIRY_FIELD before entry count={len(pre_rows)}")
        entry_date = (today + timedelta(days=1)).isoformat()
        expected_value: dict[str, object] = {"expiry_date": entry_date, "date_type": "expiry_date"}
        completion = client.post(
            f"/v1/plugins/expiry-tracker/assets/{f_done.id}/expiry",
            params={"household_id": hh.id},
            json={"expiry_date": entry_date, "date_type": "expiry_date", "source_evidence_ids": [ev.id]},
        )
        check("T2", completion.status_code == 200, f"completion POST -> {completion.status_code} {completion.text[:120]}")
        completion_body = completion.json()
        check(
            "T2",
            task_id in completion_body["resolved_review_task_ids"],
            f"intended task {short(str(task_id))} absent from {completion_body['resolved_review_task_ids']}",
        )
        check(
            "T2",
            completion_body["assertion"]["value"] == expected_value,
            f"completion assertion value={completion_body['assertion']['value']!r}",
        )
        check(
            "T2",
            completion_body["assertion"]["source_evidence_ids"] == [ev.id],
            f"completion provenance={completion_body['assertion']['source_evidence_ids']!r}",
        )
        observed = read_accepted_expiry(f_done.id, expected_value)
        session.expire_all()
        resolved_row = session.query(ReviewTask).filter_by(id=task_id).one()
        db_accepted = session.query(Asset).filter_by(id=f_done.id).one()
        check("T2", resolved_row.status == "resolved", f"task row status={resolved_row.status!r}")
        out(
            "T2",
            f"completion POST -> 200 resolved_contains_own_task=True; GET readback value={observed['value']!r} "
            f"source_type={observed['source_type']!r} source_evidence_ids={observed['source_evidence_ids']!r} "
            f"task_row={resolved_row.status}",
        )
        check("T2", db_accepted.status == "ACTIVE", f"asset row status={db_accepted.status!r}")

        # ---- T3: controls reject wrong/missing expectations ------------------
        g_control = mk_asset("G probe control missing accepted")
        classify(g_control)
        missing_rejection = attempt(
            lambda: read_accepted_expiry(g_control.id, expected_value)
        )
        check(
            "T3",
            missing_rejection is not None and "count=0" in missing_rejection,
            f"missing-assertion control not rejected for the intended property: {missing_rejection!r}",
        )
        g_rows = [
            row
            for row in client.get(f"/v1/assets/{g_control.id}", params={"household_id": hh.id}).json()["assertions"]
            if row["field_path"] == EXPIRY_FIELD
        ]
        check(
            "T3",
            [(row["review_state"], row["value"]) for row in g_rows] == [("needs_evidence", {"status": "unknown"})],
            f"control data did not land: {[(row['review_state'], row['value']) for row in g_rows]!r}",
        )
        wrong_date = (today + timedelta(days=9)).isoformat()
        wrong_rejection = attempt(
            lambda: read_accepted_expiry(
                f_done.id, {"expiry_date": wrong_date, "date_type": "expiry_date"}
            )
        )
        check(
            "T3",
            wrong_rejection is not None and "mismatch" in wrong_rejection,
            f"wrong-value control not rejected for the intended property: {wrong_rejection!r}",
        )
        check(
            "T3",
            wrong_date != entry_date,
            "control landed wrong: injected expectation equals the stored value",
        )
        read_accepted_expiry(f_done.id, expected_value)
        out(
            "T3",
            f"missing-assertion rejection={missing_rejection!r}; wrong-value rejection={wrong_rejection!r}; "
            "same reader accepts the true value; controls landed in disposable data",
        )

        # ---- T4: still-unrepaired behaviour, measured and labelled ----------
        h_bare = mk_asset("H probe bare resolve")
        h_classified = classify(h_bare)
        h_task = h_classified["review_task"]
        bare = client.post(
            f"/v1/review-tasks/{h_task}/resolve", params={"household_id": hh.id}, json={}
        )
        check("T4", bare.status_code == 200 and bare.json()["status"] == "resolved", f"bare resolve -> {bare.status_code}")
        session.expire_all()
        h_expiry_rows = [
            row
            for row in client.get(f"/v1/assets/{h_bare.id}", params={"household_id": hh.id}).json()["assertions"]
            if row["field_path"] == EXPIRY_FIELD and row["review_state"] == "accepted"
        ]
        check("T4", h_expiry_rows == [], f"bare resolve unexpectedly wrote expiry data: {h_expiry_rows!r}")
        out("T4", "STILL-UNREPAIRED (SG-177): bare resolve of expiry.manual_entry returns 200 with zero expiry data")

        i_unclassified = mk_asset("I probe unclassified")
        status_body = client.get(
            "/v1/plugins/expiry-tracker/status", params={"household_id": hh.id}
        ).json()
        visible = {row["asset_id"] for row in status_body["rows"]} | {
            row["asset_id"] for row in status_body["unresolved_rows"]
        }
        check("T4", i_unclassified.id not in visible, "unclassified asset unexpectedly visible")
        out("T4", "STILL-UNREPAIRED (SG-178): ACTIVE unclassified asset absent from rows and unresolved_rows")

        # ---- isolation post-proof -------------------------------------------
        prod_db_after = sha256_file(PROD_DB)
        stores_after = {str(root): tree_fingerprint(root) for root in PROD_STORES}
        check("ISO", prod_db_after == prod_db_before, f"prod db hash changed {prod_db_before} -> {prod_db_after}")
        for name, fingerprint in stores_after.items():
            check("ISO", fingerprint == stores_before[name], f"prod store {name} changed: {stores_before[name]} -> {fingerprint}")
        check("ISO", Path(settings.storage_root).resolve() == storage_root, "storage_root override lost")
        out("ISO", f"prod_db hash_after={prod_db_after}")
        out("ISO", "prod_db_untouched=True; prod evidence stores untouched=True; evidence writes confined to override")
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
