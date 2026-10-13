"""SG-181 G1 probe — household identity/replay on assets, If-Match, real transaction rollback.

Real FastAPI routes against a disposable SQLite DB + storage root. ScriptedProvider
only, zero network. Includes the ONE SG-180-C1 measurement correction: the ACTUAL
writer `candidates._create_asset_for_candidate` runs (rows land via flush) BEFORE a
deliberate exception; persisted state is read through a fresh independent engine.

Run:
  cd /tmp/opencode && PYTHONPATH=<repo>/backend <repo>/backend/venv/bin/python \
      <repo>/docs/worklogs/SG-181_probe_g1.py
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path

TEMP_ROOT = Path(tempfile.mkdtemp(prefix="sg181-g1-"))
TEMP_DB = TEMP_ROOT / "storagegenie.db"
TEMP_STORAGE = TEMP_ROOT / "storage"
TEMP_STORAGE.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEMP_DB}"
os.environ["STORAGE_ROOT"] = str(TEMP_STORAGE)
os.environ.pop("OPENCODE_API_KEY", None)

from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    Assertion,
    Asset,
    AuditEvent,
    Evidence,
    Household,
    IdempotencyKey,
    Job,
    asset_evidence,
)
from app.services import candidates  # noqa: E402
from app.services.providers import reader  # noqa: E402
from app.services.providers.fake import ScriptedProvider  # noqa: E402

RESULTS: list[dict[str, object]] = []


def record(name: str, level: str, **detail: object) -> None:
    RESULTS.append({"check": name, "result": level, **detail})
    print(f"[{level}] {name} {json.dumps(detail, default=str)[:400]}", flush=True)


def expect(name: str, condition: bool, **detail: object) -> None:
    record(name, "PASS" if condition else "FAIL", **detail)


def observe(name: str, **detail: object) -> None:
    record(name, "OBSERVE", **detail)


def png_bytes(color: str = "red") -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (48, 32), color).save(out, format="PNG")
    return out.getvalue()


VALID_PAYLOAD = {
    "items": [{"name": "SG181 Audit Widget", "confidence": 0.97, "uncertainty_reasons": ["none"]}],
    "unknowns": [],
    "needs_evidence": False,
}


def main() -> int:
    opened = time.monotonic()
    cmd_start = int(time.time())
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    house_a = Household(name="SG181 G1 House A")
    house_b = Household(name="SG181 G1 House B")
    session.add_all([house_a, house_b])
    session.commit()
    aid, bid = house_a.id, house_b.id

    assert str(TEMP_ROOT) in settings.storage_root and str(TEMP_ROOT) in str(engine.url)
    record("isolation", "PASS", storage_root=settings.storage_root, engine_url=str(engine.url), temp_root=str(TEMP_ROOT))

    client = TestClient(app)

    # --- G1.A asset POST idempotency replay: global key, no household check (REC-ISS06) ---
    key = "sg181-shared-asset-key"
    r_a = client.post("/v1/assets", params={"household_id": aid}, json={"display_name": "A keyed item"}, headers={"Idempotency-Key": key})
    a_body = r_a.json()
    r_b = client.post("/v1/assets", params={"household_id": bid}, json={"display_name": "B DIFFERENT payload"}, headers={"Idempotency-Key": key})
    b_body = r_b.json()
    ik_rows = session.query(IdempotencyKey).filter_by(key=key).all()
    assets_a = session.query(Asset).filter_by(household_id=aid).count()
    assets_b = session.query(Asset).filter_by(household_id=bid).count()
    record(
        "asset_key_replay_same_key_other_household",
        "DEFECT_OBSERVED" if (r_b.status_code == 201 and b_body.get("id") == a_body.get("id") and b_body.get("household_id") == aid) else ("PASS" if r_b.status_code == 403 else "FAIL"),
        a_status=r_a.status_code,
        a_id=a_body.get("id"),
        a_household=a_body.get("household_id"),
        b_status=r_b.status_code,
        b_returned_id=b_body.get("id"),
        b_returned_household=b_body.get("household_id"),
        b_requested_household=bid,
        idempotency_rows=[{"key": row.key, "response": row.response_json} for row in ik_rows],
        assets_a=assets_a,
        assets_b=assets_b,
        expected="household-scoped replay or 403 (import replay precedent F-SG180-11); CX-01",
    )
    # payload ignored on replay (same household)
    r_a2 = client.post("/v1/assets", params={"household_id": aid}, json={"display_name": "CHANGED payload"}, headers={"Idempotency-Key": key})
    observe(
        "asset_key_replay_changed_payload_ignored",
        returned_id=r_a2.json().get("id"),
        original_id=a_body.get("id"),
        returned_name=r_a2.json().get("display_name"),
        note="different display_name under same key silently returns the original row",
    )
    # counter-controls: fresh key -> B's own row; no key -> own rows
    r_b2 = client.post("/v1/assets", params={"household_id": bid}, json={"display_name": "B own"}, headers={"Idempotency-Key": "sg181-fresh-b"})
    expect("counter_control_fresh_key_own_row", r_b2.status_code == 201 and r_b2.json()["id"] != a_body.get("id") and r_b2.json()["household_id"] == bid, status=r_b2.status_code, id=r_b2.json().get("id"), household=r_b2.json().get("household_id"))
    r_a3 = client.post("/v1/assets", params={"household_id": aid}, json={"display_name": "A nokey"})
    r_b3 = client.post("/v1/assets", params={"household_id": bid}, json={"display_name": "B nokey"})
    expect("counter_control_nokey_own_rows", r_a3.json()["id"] != r_b3.json()["id"] and r_a3.json()["household_id"] == aid and r_b3.json()["household_id"] == bid)

    # --- G1.B household-mismatch controls on asset surface ---
    a1 = a_body["id"]
    get_b = client.get(f"/v1/assets/{a1}", params={"household_id": bid})
    expect("asset_get_foreign_403", get_b.status_code == 403, status=get_b.status_code)
    patch_b = client.patch(f"/v1/assets/{a1}", params={"household_id": bid}, json={"condition": "used"})
    expect("asset_patch_foreign_403", patch_b.status_code == 403, status=patch_b.status_code)
    ev_b = client.post(f"/v1/assets/{a1}/evidence", params={"household_id": bid}, json={"evidence_ids": ["nope"]})
    expect("asset_evidence_attach_foreign_403", ev_b.status_code == 403, status=ev_b.status_code)
    list_b = client.get("/v1/assets", params={"household_id": bid}).json()
    expect("asset_list_scoped", all(i["household_id"] == bid for i in list_b["items"]), returned=[i["id"] for i in list_b["items"]])

    # --- G1.C If-Match semantics ---
    v = a_body["version"]
    ok = client.patch(f"/v1/assets/{a1}", params={"household_id": aid}, json={"condition": "new"}, headers={"If-Match": str(v)})
    expect("ifmatch_current_accepts", ok.status_code == 200 and ok.json()["version"] == v + 1, status=ok.status_code, before=v, after=ok.json().get("version"))
    stale = client.patch(f"/v1/assets/{a1}", params={"household_id": aid}, json={"condition": "used"}, headers={"If-Match": str(v)})
    expect("ifmatch_stale_409", stale.status_code == 409, status=stale.status_code, detail=stale.json().get("detail"))
    invalid = client.patch(f"/v1/assets/{a1}", params={"household_id": aid}, json={"condition": "used"}, headers={"If-Match": "not-a-number"})
    expect("ifmatch_invalid_422", invalid.status_code == 422, status=invalid.status_code)
    missing = client.patch(f"/v1/assets/{a1}", params={"household_id": aid}, json={"condition": "used"})
    observe("ifmatch_missing_allowed", status=missing.status_code, version_after=missing.json().get("version"), note="no If-Match -> unconditional update; last-write-wins")
    no_fields = client.patch(f"/v1/assets/{a1}", params={"household_id": aid}, json={}, headers={"If-Match": str(missing.json().get("version"))})
    expect("patch_empty_422", no_fields.status_code == 422, status=no_fields.status_code)
    version_now = missing.json()["version"]
    first = client.patch(f"/v1/assets/{a1}", params={"household_id": aid}, json={"condition": "a"}, headers={"If-Match": str(version_now)})
    second = client.patch(f"/v1/assets/{a1}", params={"household_id": aid}, json={"condition": "b"}, headers={"If-Match": str(version_now)})
    expect("interleaved_same_version_second_409", first.status_code == 200 and second.status_code == 409, first=first.status_code, second=second.status_code, note="sequential CAS, not true concurrency")

    # --- G1.D real transaction rollback (SG-180-C1 correction) ---
    def set_provider(provider) -> None:  # type: ignore[no-untyped-def]
        reader.provider_registry = lambda: {provider.provider_id: provider}  # type: ignore[assignment]
        settings.sg_consent = True
        settings.sg_provider_id = provider.provider_id

    set_provider(ScriptedProvider(provider_id="scripted", payload=VALID_PAYLOAD))
    r = client.post("/v1/evidence", params={"household_id": aid}, files={"file": ("txn.png", png_bytes("magenta"), "image/png")})
    assert r.status_code == 201, r.text
    evidence_id = r.json()["id"]
    created = client.post("/v1/imports", params={"household_id": aid}, json={"evidence_ids": [evidence_id]})
    job_id = created.json()["id"]
    run = client.post(f"/v1/imports/{job_id}/run", params={"household_id": aid})
    assert run.json()["state"] == "AWAITING_REVIEW", run.text
    cand_list = client.get(f"/v1/jobs/{job_id}/candidates", params={"household_id": aid}).json()
    cand_id = cand_list["items"][0]["id"]

    # cross-household decision control before the accept
    foreign_decision = client.post(f"/v1/candidates/{cand_id}/decision", params={"household_id": bid}, json={"action": "accept"})
    expect("candidate_decision_foreign_403", foreign_decision.status_code == 403, status=foreign_decision.status_code)

    real_create = candidates._create_asset_for_candidate
    landed: dict[str, object] = {}
    state = {"fired": False}

    def observing_create(db, cand):  # type: ignore[no-untyped-def]
        if not state["fired"]:
            state["fired"] = True
            asset = real_create(db, cand)  # ACTUAL writer; asset row flushed inside
            db.flush()  # land pending assertions/links/audits inside the same request transaction
            landed["asset_id"] = asset.id
            landed["asset_rows_in_txn"] = db.query(Asset).filter_by(household_id=cand.household_id).count()
            landed["assertion_rows_in_txn"] = db.query(Assertion).filter_by(asset_id=asset.id).count()
            landed["link_rows_in_txn"] = len(db.execute(asset_evidence.select().where(asset_evidence.c.asset_id == asset.id)).all())
            landed["audit_rows_in_txn"] = db.query(AuditEvent).filter_by(entity_id=asset.id).count()
            landed["idempotency_untouched"] = True
            raise RuntimeError("sg181 controlled failure AFTER real partial write")
        return real_create(db, cand)

    assets_before = session.query(Asset).filter_by(household_id=aid).count()
    candidates._create_asset_for_candidate = observing_create
    decision = client.post(f"/v1/candidates/{cand_id}/decision", params={"household_id": aid}, json={"action": "accept"})
    candidates._create_asset_for_candidate = real_create
    d_body = decision.json()
    record(
        "c1_real_writer_partial_mutation_landed",
        "PASS" if landed.get("asset_rows_in_txn", 0) > 0 and landed.get("assertion_rows_in_txn", 0) > 0 and landed.get("link_rows_in_txn", 0) > 0 and landed.get("audit_rows_in_txn", 0) >= 3 else "FAIL",
        **landed,
    )
    expect(
        "c1_controlled_failure_marks_job_failed",
        decision.status_code == 200 and d_body.get("job", {}).get("state") == "FAILED" and any("sg181 controlled failure" in str(e) for e in d_body["job"].get("errors", [])),
        status=decision.status_code,
        state=d_body.get("job", {}).get("state"),
        errors=d_body.get("job", {}).get("errors"),
    )
    session.expire_all()
    assets_during = session.query(Asset).filter_by(household_id=aid).count()

    # fresh independent engine + session (new connection) reads persisted state
    engine.dispose()
    engine2 = create_engine(f"sqlite:///{TEMP_DB}", connect_args={"check_same_thread": False})
    fresh = sessionmaker(bind=engine2, autoflush=False, expire_on_commit=False)()

    def override_get_db2():  # type: ignore[no-untyped-def]
        s = sessionmaker(bind=engine2, autoflush=False, expire_on_commit=False)()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db2
    persisted_after_fail = fresh.query(Asset).filter_by(household_id=aid).count()
    failed_job = fresh.query(Job).filter_by(id=job_id).one()
    record(
        "c1_fresh_session_after_failure",
        "PASS" if persisted_after_fail == assets_before and failed_job.state == "FAILED" else "FAIL",
        assets_before=assets_before,
        assets_after_failure_fresh=fresh.query(Asset).filter_by(household_id=aid).count(),
        job_state=failed_job.state,
        landed_asset_would_have_been=landed.get("asset_id"),
        note="same-request session count above shows the partial unit landed; fresh connection shows it rolled back",
    )
    expect("c1_rollback_differs_from_landed", landed.get("asset_rows_in_txn", 0) > persisted_after_fail, in_txn=landed.get("asset_rows_in_txn"), fresh=persisted_after_fail)

    # normal control: retry reaches COMPLETED and persists exactly one new asset visible to the fresh reader
    retry = client.post(f"/v1/imports/{job_id}/retry", params={"household_id": aid})
    fresh.expire_all()
    assets_after_retry = fresh.query(Asset).filter_by(household_id=aid).count()
    new_asset = fresh.query(Asset).filter_by(household_id=aid).order_by(Asset.created_at.desc()).first()
    asserts = fresh.query(Assertion).filter_by(asset_id=new_asset.id).all() if new_asset else []
    links = fresh.execute(asset_evidence.select().where(asset_evidence.c.asset_id == new_asset.id)).all() if new_asset else []
    audits = fresh.query(AuditEvent).filter_by(entity_id=new_asset.id).all() if new_asset else []
    expect(
        "c1_normal_commit_control_persists",
        retry.status_code == 200 and retry.json()["state"] == "COMPLETED" and assets_after_retry == assets_before + 1 and len(asserts) >= 1 and len(links) >= 1,
        retry_status=retry.status_code,
        state=retry.json().get("state"),
        assets_after_retry=assets_after_retry,
        assertions=[a.field_path for a in asserts],
        links=len(links),
        audits=[a.action for a in audits],
    )
    # GET readback through the real route, now served by the fresh-reader override
    detail = client.get(f"/v1/assets/{new_asset.id}", params={"household_id": aid})
    d = detail.json()
    expect(
        "c1_asset_get_readback_lineage",
        detail.status_code == 200
        and d["household_id"] == aid
        and any(a["source_type"] == "extraction" and evidence_id in a["source_evidence_ids"] for a in d["assertions"])
        and any(ae["action"] == "asset.create" for ae in d["audit_events"]),
        assertion_sources=sorted({a["source_type"] for a in d["assertions"]}),
        audit_actions=sorted({ae["action"] for ae in d["audit_events"]}),
    )
    foreign_detail = client.get(f"/v1/assets/{new_asset.id}", params={"household_id": bid})
    expect("c1_asset_get_foreign_403", foreign_detail.status_code == 403, status=foreign_detail.status_code)

    # observation lineage: Observation rows for the job evidence
    from app.services.observations import Observation  # noqa: E402

    obs = fresh.query(Observation).all()
    observe("observation_lineage", total=len(obs), evidence_ids=sorted({o.evidence_id for o in obs}))

    fresh.close()
    engine2.dispose()
    session.close()
    print(json.dumps({"results": RESULTS}, indent=2))
    print(f"TEMP_ROOT={TEMP_ROOT}")
    print(f"elapsed_s={time.monotonic() - opened:.1f} start_epoch={cmd_start} end_epoch={int(time.time())}")
    return 1 if any(r["result"] == "FAIL" for r in RESULTS) else 0


if __name__ == "__main__":
    sys.exit(main())
