"""SG-180 G2 probe — durable jobs, duplicates, failure/retry, rollback, resume.

Real FastAPI routes against a disposable SQLite DB + storage root; a
process-level engine reopen demonstrates durable resume. Provider is a
schema-valid ScriptedProvider injected through the reader's named seam
(`reader.provider_registry`); zero network, zero paid calls.

Run:
  cd /tmp/opencode && PYTHONPATH=<repo>/backend <repo>/backend/venv/bin/python \
      <repo>/docs/worklogs/SG-180_probe_g2.py
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path

TEMP_ROOT = Path(tempfile.mkdtemp(prefix="sg180-g2-"))
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
    Job,
    JobStep,
    ProviderCall,
    ReviewTask,
    asset_evidence,
)
from app.services import candidates, job_service  # noqa: E402
from app.services.observations import Observation  # noqa: E402
from app.services.providers import reader  # noqa: E402
from app.services.providers.fake import ScriptedProvider  # noqa: E402

RESULTS: list[dict[str, object]] = []


def record(name: str, level: str, **detail: object) -> None:
    RESULTS.append({"check": name, "result": level, **detail})


def expect(name: str, condition: bool, **detail: object) -> None:
    record(name, "PASS" if condition else "FAIL", **detail)


def observe(name: str, **detail: object) -> None:
    record(name, "OBSERVE", **detail)


def png_bytes(color="red", size=(48, 32)) -> bytes:
    out = io.BytesIO()
    Image.new("RGB", size, color).save(out, format="PNG")
    return out.getvalue()


VALID_PAYLOAD = {
    "items": [
        {
            "name": "Audit Olive Oil",
            "expiry_date": "2026-12-31",
            "confidence": 0.97,
            "uncertainty_reasons": ["partially obscured"],
            "brand": "AuditBrand",
        }
    ],
    "unknowns": [],
    "needs_evidence": False,
}

TWO_ITEM_PAYLOAD = {
    "items": [
        {"name": "Audit Item One", "confidence": 0.99, "uncertainty_reasons": ["none"]},
        {"name": "Audit Item Two", "confidence": 0.98, "uncertainty_reasons": ["none"]},
    ],
    "unknowns": [],
    "needs_evidence": False,
}


class LatencyProvider(ScriptedProvider):
    def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(**kwargs)
        self.sleep_s = 0.0

    def extract_items(self, image_bytes, prompt, *, estimated_cost=0.0):  # type: ignore[no-untyped-def]
        time.sleep(self.sleep_s)
        return super().extract_items(image_bytes, prompt, estimated_cost=estimated_cost)


def set_provider(provider) -> None:  # type: ignore[no-untyped-def]
    reader.provider_registry = lambda: {provider.provider_id: provider}  # type: ignore[assignment]
    settings.sg_consent = True
    settings.sg_provider_id = provider.provider_id


def main() -> int:
    opened = time.monotonic()
    cmd_start = int(time.time())
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    house = Household(name="SG180 G2 House")
    other = Household(name="SG180 G2 Other")
    session.add_all([house, other])
    session.commit()
    hid, oid = house.id, other.id

    assert str(TEMP_ROOT) in settings.storage_root and str(TEMP_ROOT) in str(engine.url)
    record("isolation", "PASS", storage_root=settings.storage_root, engine_url=str(engine.url))

    client = TestClient(app)
    r = client.post(
        "/v1/evidence",
        params={"household_id": hid},
        files={"file": ("olive.png", png_bytes(), "image/png")},
    )
    assert r.status_code == 201, r.text
    evidence_id = r.json()["id"]

    # --- G2.1 create-only vs run ---
    created = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [evidence_id]})
    job_id = created.json()["id"]
    steps = session.query(JobStep).filter_by(job_id=job_id).all()
    expect(
        "create_only_created_pending",
        created.status_code == 201 and created.json()["state"] == "CREATED" and all(s.state == "PENDING" and s.attempts == 0 for s in steps),
        state=created.json()["state"],
        step_count=len(steps),
        http=created.status_code,
    )
    detail = client.get(f"/v1/imports/{job_id}", params={"household_id": hid}).json()
    expect("created_progress_zero", detail["progress"] == {"completed": 0, "total": 8, "failed": 0, "pending": 8}, progress=detail["progress"])

    run1 = client.post(f"/v1/imports/{job_id}/run", params={"household_id": hid})
    expect(
        "run_reaches_awaiting_review",
        run1.status_code == 200 and run1.json()["state"] == "AWAITING_REVIEW" and run1.json()["progress"]["completed"] == 6,
        state=run1.json()["state"],
        progress=run1.json()["progress"],
    )
    cands = client.get(f"/v1/jobs/{job_id}/candidates", params={"household_id": hid}).json()
    expect("candidate_listed_after_run", cands["total"] == 1, total=cands["total"], kind=cands["items"][0]["fields"].get("display_name") if cands["items"] else None)

    # second run: no duplicate work
    obs_before = session.query(Observation).count()
    run2 = client.post(f"/v1/imports/{job_id}/run", params={"household_id": hid})
    obs_after = session.query(Observation).count()
    cands2 = client.get(f"/v1/jobs/{job_id}/candidates", params={"household_id": hid}).json()
    step_rows = session.query(JobStep).filter_by(job_id=job_id).all()
    attempts = {s.step_name: s.attempts for s in step_rows}
    expect(
        "rerun_no_duplicate_work",
        run2.json()["state"] == "AWAITING_REVIEW" and cands2["total"] == 1 and obs_after == obs_before and all(v <= 1 for v in attempts.values()),
        candidate_count=cands2["total"],
        obs_before=obs_before,
        obs_after=obs_after,
        attempts=attempts,
    )

    # --- G2.2 idempotency: same key same household; foreign household; changed request ---
    k = "sg180-g2-key-1"
    j1 = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [evidence_id]}, headers={"Idempotency-Key": k})
    j1b = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [evidence_id]}, headers={"Idempotency-Key": k})
    j1c = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": []}, headers={"Idempotency-Key": k})
    foreign = client.post("/v1/imports", params={"household_id": oid}, json={"evidence_ids": []}, headers={"Idempotency-Key": k})
    expect("key_replay_same_household_same_job", j1.json()["id"] == j1b.json()["id"], first=j1.json()["id"], second=j1b.json()["id"])
    observe(
        "key_replay_changed_payload_ignored",
        returned_id=j1c.json()["id"],
        original_id=j1.json()["id"],
        note="different evidence_ids under the same key silently return the original job",
    )
    expect("key_replay_foreign_household_403", foreign.status_code == 403, status=foreign.status_code)

    # --- G2.3 duplicate evidence import: second job after first committed -> duplicate_of_asset, no second asset ---
    accept1 = client.post(f"/v1/candidates/{cands['items'][0]['id']}/decision", params={"household_id": hid}, json={"action": "accept"})
    asset_count_1 = session.query(Asset).filter_by(household_id=hid).count()
    expect(
        "accept_commits_asset",
        accept1.status_code == 200 and asset_count_1 == 1 and accept1.json()["job"]["state"] == "COMPLETED",
        status=accept1.status_code,
        state=accept1.json().get("job", {}).get("state"),
        assets=asset_count_1,
    )
    dup = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [evidence_id]})
    dup_run = client.post(f"/v1/imports/{dup.json()['id']}/run", params={"household_id": hid})
    dup_cand = client.get(f"/v1/jobs/{dup.json()['id']}/candidates", params={"household_id": hid}).json()
    dup_proposal = candidates.load_proposal(session.query(candidates.Candidate).filter_by(job_id=dup.json()["id"]).one())
    accept_dup = client.post(f"/v1/candidates/{dup_cand['items'][0]['id']}/decision", params={"household_id": hid}, json={"action": "accept"})
    asset_count_2 = session.query(Asset).filter_by(household_id=hid).count()
    expect(
        "duplicate_import_no_second_asset",
        dup_proposal["kind"] == "duplicate_of_asset"
        and accept_dup.json().get("status") == "duplicate_linked"
        and asset_count_2 == 1
        and dup_run.json()["state"] == "AWAITING_REVIEW",
        kind=dup_proposal["kind"],
        decision=accept_dup.json().get("status"),
        assets=asset_count_2,
    )

    # --- G2.4 empty import edge ---
    empty = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": []})
    empty_run = client.post(f"/v1/imports/{empty.json()['id']}/run", params={"household_id": hid})
    empty_cand = client.get(f"/v1/jobs/{empty.json()['id']}/candidates", params={"household_id": hid}).json()
    observe(
        "empty_import_flow",
        state=empty_run.json()["state"],
        candidate=empty_cand["items"][0]["fields"] if empty_cand["items"] else None,
    )

    # --- G2.5 controlled step failure, durable across engine reopen, retry ---
    original_execute = job_service.execute_step
    fail_state = {"fired": False}

    def flaky_execute(db, job, step):  # type: ignore[no-untyped-def]
        if step.step_name == "EXTRACTING_DETERMINISTIC_SIGNALS" and not fail_state["fired"]:
            fail_state["fired"] = True
            raise RuntimeError("sg180 controlled step failure")
        return original_execute(db, job, step)

    job_service.execute_step = flaky_execute
    r = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [evidence_id]})
    fail_job_id = r.json()["id"]
    failed = client.post(f"/v1/imports/{fail_job_id}/run", params={"household_id": hid})
    failed_steps = {s.step_name: (s.state, s.attempts) for s in session.query(JobStep).filter_by(job_id=fail_job_id).all()}
    session.expire_all()
    expect(
        "controlled_failure_state",
        failed.json()["state"] == "FAILED"
        and failed_steps["EXTRACTING_DETERMINISTIC_SIGNALS"] == ("FAILED", 1)
        and any(s.state == "COMPLETED" for s in session.query(JobStep).filter_by(job_id=fail_job_id).all()),
        state=failed.json()["state"],
        steps=failed_steps,
        errors=failed.json()["errors"],
    )
    job_service.execute_step = original_execute

    # reopen engine on the same durable sqlite file (process-restart analogue)
    engine.dispose()
    engine2 = create_engine(f"sqlite:///{TEMP_DB}", connect_args={"check_same_thread": False})
    Session2 = sessionmaker(bind=engine2, autoflush=False, expire_on_commit=False)

    def override_get_db2():  # type: ignore[no-untyped-def]
        s = Session2()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db2
    s2 = Session2()
    persisted = s2.query(Job).filter_by(id=fail_job_id).one()
    persisted_attempts = {s.step_name: s.attempts for s in s2.query(JobStep).filter_by(job_id=fail_job_id).all()}
    expect("reopen_persists_failed_state", persisted.state == "FAILED", state=persisted.state, attempts=persisted_attempts)

    retried = client.post(f"/v1/imports/{fail_job_id}/retry", params={"household_id": hid})
    retry_attempts = {s.step_name: s.attempts for s in s2.query(JobStep).filter_by(job_id=fail_job_id).all()}
    expect(
        "retry_after_reopen_resumes",
        retried.json()["state"] == "AWAITING_REVIEW" and retry_attempts["EXTRACTING_DETERMINISTIC_SIGNALS"] == 2,
        state=retried.json()["state"],
        attempts=retry_attempts,
    )

    # audit lineage for the failed/retried job
    audits = s2.query(AuditEvent).filter_by(entity_id=fail_job_id).all()
    observe(
        "failed_job_audit_lineage",
        actions=[a.action for a in audits],
        transitions=[a.after_json for a in audits if a.action == "job.state_transition"],
    )

    # --- G2.6 malformed extraction (scripted invalid payload), ledger error rows, retry ---
    r = client.post(
        "/v1/evidence",
        params={"household_id": hid},
        files={"file": ("commit-source.png", png_bytes(color="magenta"), "image/png")},
    )
    commit_evidence = r.json()["id"]
    invalid = LatencyProvider(provider_id="scripted", payload={"items": [{"name": ""}], "unknowns": [], "needs_evidence": False})
    set_provider(invalid)
    r = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [commit_evidence]})
    bad_job = r.json()["id"]
    bad_run = client.post(f"/v1/imports/{bad_job}/run", params={"household_id": hid})
    calls = s2.query(ProviderCall).filter_by(job_id=bad_job).order_by(ProviderCall.created_at, ProviderCall.id).all()
    expect(
        "malformed_extraction_fails_job",
        bad_run.json()["state"] == "FAILED" and invalid.invocations == 2 and len(calls) == 2 and all(c.error_state for c in calls),
        state=bad_run.json()["state"],
        provider_invocations=invalid.invocations,
        ledger_rows=[{"error_state": c.error_state, "cost": c.cost} for c in calls],
    )
    valid = LatencyProvider(provider_id="scripted", payload=VALID_PAYLOAD)
    set_provider(valid)
    bad_retry = client.post(f"/v1/imports/{bad_job}/retry", params={"household_id": hid})
    s2.expire_all()
    good_calls = s2.query(ProviderCall).filter_by(job_id=bad_job).order_by(ProviderCall.created_at, ProviderCall.id).all()
    good_cand = s2.query(candidates.Candidate).filter_by(job_id=bad_job).first()
    proposal = candidates.load_proposal(good_cand)
    success_ids = {c.id for c in good_calls if c.error_state is None}
    expect(
        "retry_with_valid_output_builds_candidate",
        bad_retry.json()["state"] == "AWAITING_REVIEW"
        and len(good_calls) == 3
        and proposal["ai_provider"] == "scripted"
        and proposal["prompt_template_version"].endswith("-v4")
        and bool(set(proposal["provider_call_ids"]) & success_ids),
        state=bad_retry.json()["state"],
        ledger_rows=len(good_calls),
        proposal_calls=proposal["provider_call_ids"],
        success_calls=sorted(success_ids),
        error_rows=[c.error_state for c in good_calls],
    )

    # --- G2.7 commit rollback and re-entry ---
    original_create = candidates._create_asset_for_candidate
    commit_fail = {"fired": False}

    def flaky_create(db, cand):  # type: ignore[no-untyped-def]
        if not commit_fail["fired"]:
            commit_fail["fired"] = True
            raise RuntimeError("sg180 controlled commit failure")
        return original_create(db, cand)

    candidates._create_asset_for_candidate = flaky_create
    assets_before = s2.query(Asset).filter_by(household_id=hid).count()
    decision = client.post(
        f"/v1/candidates/{good_cand.id}/decision", params={"household_id": hid}, json={"action": "accept"}
    )
    s2.expire_all()
    assets_during = s2.query(Asset).filter_by(household_id=hid).count()
    links_during = s2.execute(asset_evidence.select()).all()
    expect(
        "commit_failure_rolls_back",
        decision.json()["job"]["state"] == "FAILED" and assets_during == assets_before and len(links_during) == 1,
        state=decision.json()["job"]["state"],
        assets_before=assets_before,
        assets_during=assets_during,
        asset_evidence_rows=len(links_during),
    )
    candidates._create_asset_for_candidate = original_create
    reentered = client.post(f"/v1/imports/{bad_job}/retry", params={"household_id": hid})
    s2.expire_all()
    assets_after = s2.query(Asset).filter_by(household_id=hid).count()
    asserts = s2.query(Assertion).filter_by(asset_id=s2.query(Asset).filter_by(household_id=hid).order_by(Asset.created_at.desc()).first().id).all()
    expect(
        "commit_retry_creates_once",
        reentered.json()["state"] == "COMPLETED" and assets_after == assets_before + 1,
        state=reentered.json()["state"],
        assets_after=assets_after,
        assertion_fields=sorted(a.field_path for a in asserts),
    )

    # --- G2.8 missing original ---
    r = client.post(
        "/v1/evidence",
        params={"household_id": hid},
        files={"file": ("vanishing.png", png_bytes(color="cyan"), "image/png")},
    )
    missing_id = r.json()["id"]
    stored = TEMP_STORAGE / s2.query(Evidence).filter_by(id=missing_id).one().storage_key
    stored.unlink()
    r = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [missing_id]})
    missing_job = r.json()["id"]
    missing_run = client.post(f"/v1/imports/{missing_job}/run", params={"household_id": hid})
    errs = missing_run.json()["errors"]
    expect(
        "missing_original_fails_with_quarantine",
        missing_run.json()["state"] == "FAILED" and any("original missing" in e for e in errs),
        state=missing_run.json()["state"],
        errors=errs,
    )
    stored.write_bytes(png_bytes(color="cyan"))
    recovered = client.post(f"/v1/imports/{missing_job}/retry", params={"household_id": hid})
    expect("missing_original_restored_retry", recovered.json()["state"] == "AWAITING_REVIEW", state=recovered.json()["state"])

    # --- G2.9 multi-item review gate ---
    two = LatencyProvider(provider_id="scripted", payload=TWO_ITEM_PAYLOAD)
    set_provider(two)
    r = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [evidence_id]})
    multi_job = r.json()["id"]
    client.post(f"/v1/imports/{multi_job}/run", params={"household_id": hid})
    multi_cand = s2.query(candidates.Candidate).filter_by(job_id=multi_job).one()
    tasks = s2.query(ReviewTask).filter_by(subject_ref=multi_cand.id, status="open").all()
    blocked = client.post(f"/v1/candidates/{multi_cand.id}/decision", params={"household_id": hid}, json={"action": "accept"})
    for t in tasks:
        client.post(f"/v1/review-tasks/{t.id}/resolve", params={"household_id": hid}, json={})
    allowed = client.post(f"/v1/candidates/{multi_cand.id}/decision", params={"household_id": hid}, json={"action": "accept"})
    expect(
        "multi_item_task_gates_accept",
        [t.task_type for t in tasks] == ["candidate.multi_item"] and blocked.status_code == 409 and allowed.status_code == 200,
        task_types=[t.task_type for t in tasks],
        blocked_status=blocked.status_code,
        after_resolve=allowed.status_code,
        final_job_state=allowed.json().get("job", {}).get("state"),
    )

    # --- G2.10 blocking /run measurement (controlled latency) ---
    slow = LatencyProvider(provider_id="scripted", payload=VALID_PAYLOAD)
    slow.sleep_s = 0.6
    set_provider(slow)
    r = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [evidence_id]})
    sync_job = r.json()["id"]
    t0 = time.monotonic()
    sync_run = client.post(f"/v1/imports/{sync_job}/run", params={"household_id": hid})
    elapsed = time.monotonic() - t0
    expect(
        "run_blocks_full_pipeline",
        sync_run.status_code == 200 and sync_run.json()["state"] == "AWAITING_REVIEW" and elapsed >= 0.6,
        elapsed_s=round(elapsed, 3),
        provider_invocations=slow.invocations,
        state_in_response=sync_run.json()["state"],
    )

    # --- G2.11 cancellation inventory ---
    cancel = client.post(f"/v1/imports/{sync_job}/cancel", params={"household_id": hid})
    still = client.get(f"/v1/imports/{sync_job}", params={"household_id": hid}).json()
    record(
        "cancel_route_absent",
        "OBSERVE" if cancel.status_code in {404, 405} else "FAIL",
        status=cancel.status_code,
        job_state_after=still["state"],
        note="job state machine names CANCELLED (job_service.py:164) but no writer/route reaches it",
    )
    remaining = session.query(Job).count()
    record(
        "final_counts",
        "OBSERVE",
        jobs=remaining,
        candidates=s2.query(candidates.Candidate).count(),
        assets=s2.query(Asset).count(),
        provider_calls=s2.query(ProviderCall).count(),
    )

    session.close()
    s2.close()
    engine2.dispose()
    print(json.dumps({"results": RESULTS}, indent=2))
    print(f"TEMP_ROOT={TEMP_ROOT}")
    print(f"elapsed_s={time.monotonic() - opened:.1f} start_epoch={cmd_start}")
    return 1 if any(r["result"] == "FAIL" for r in RESULTS) else 0


if __name__ == "__main__":
    sys.exit(main())
