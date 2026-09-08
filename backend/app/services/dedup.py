from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.asset import Asset
from app.models.assertion import Assertion
from app.models.evidence import Evidence, asset_evidence
from app.models.job import Job
from app.models.review_task import ReviewTask
from app.services.candidates import Candidate
from app.services.observations import Observation
from app.services.signals import hamming_distance


def _evidence_ids(job: Job) -> list[str]:
    config = json.loads(job.config_snapshot or "{}")
    value = config.get("evidence_ids", [])
    if not isinstance(value, list):
        raise ValueError("invalid evidence_ids in job config")
    return [str(item) for item in value]


def _observation_value(row: Observation) -> dict[str, object]:
    value = json.loads(row.value_json)
    return value if isinstance(value, dict) else {}


def _existing_asset_for_evidence(db: Session, household_id: str, evidence_id: str) -> Asset | None:
    return (
        db.query(Asset)
        .join(asset_evidence, asset_evidence.c.asset_id == Asset.id)
        .filter(Asset.household_id == household_id, asset_evidence.c.evidence_id == evidence_id)
        .order_by(Asset.id)
        .first()
    )


def _similar_matches(db: Session, household_id: str, evidence_id: str, phash: str) -> list[dict[str, object]]:
    rows = (
        db.query(Observation, Asset)
        .join(asset_evidence, asset_evidence.c.evidence_id == Observation.evidence_id)
        .join(Asset, Asset.id == asset_evidence.c.asset_id)
        .filter(Asset.household_id == household_id, Observation.kind == "phash")
        .all()
    )
    matches: list[dict[str, object]] = []
    for row, asset in rows:
        value = _observation_value(row).get("hash")
        if not isinstance(value, str) or row.evidence_id == evidence_id:
            continue
        distance = hamming_distance(phash, value)
        if distance <= settings.dhash_near_threshold:
            matches.append({"type": "similar", "asset_id": asset.id, "distance": distance})
    return matches


def _identifier_collisions(db: Session, household_id: str, evidence_id: str) -> list[dict[str, object]]:
    rows = db.query(Observation).filter(Observation.evidence_id == evidence_id, Observation.kind == "barcode_qr").all()
    assertions = (
        db.query(Assertion, Asset)
        .join(Asset, Asset.id == Assertion.asset_id)
        .filter(Asset.household_id == household_id, Assertion.field_path == "identifier")
        .all()
    )
    existing: dict[str, str] = {}
    for assertion, asset in assertions:
        try:
            value = json.loads(assertion.value_json)
        except json.JSONDecodeError:
            value = assertion.value_json
        existing[str(value)] = asset.id

    collisions: list[dict[str, object]] = []
    for row in rows:
        value = _observation_value(row)
        if value.get("validated") is not True or not value.get("value"):
            continue
        identifier = str(value["value"])
        if identifier in existing:
            collisions.append(
                {
                    "type": "identifier_collision",
                    "identifier": identifier,
                    "asset_id": existing[identifier],
                    "evidence_id": evidence_id,
                }
            )
    return collisions


def _display_name(evidence: Evidence | None) -> str:
    if evidence is None:
        return "Imported item"
    return Path(evidence.original_filename).stem or evidence.original_filename


def deduplicate_job(db: Session, job: Job) -> dict[str, object]:  # noqa: C901
    existing = db.query(Candidate).filter_by(job_id=job.id).first()
    if existing is not None:
        return {"status": "ok", "step": "DEDUPLICATING", "candidate_id": existing.id, "reused": True}

    evidence_ids = _evidence_ids(job)
    evidence_rows = db.query(Evidence).filter(Evidence.id.in_(evidence_ids)).all() if evidence_ids else []
    by_id = {row.id: row for row in evidence_rows}
    if len(by_id) != len(set(evidence_ids)) or any(row.household_id != job.household_id for row in evidence_rows):
        raise ValueError("job evidence does not belong to its household")

    matches: list[dict[str, object]] = []
    exact_assets: list[str] = []
    collisions: list[dict[str, object]] = []
    identifier: str | None = None
    for evidence_id in evidence_ids:
        exact_asset = _existing_asset_for_evidence(db, job.household_id or "", evidence_id)
        if exact_asset is not None:
            exact_assets.append(exact_asset.id)
            matches.append({"type": "duplicate_of_asset", "asset_id": exact_asset.id, "evidence_id": evidence_id})
            continue
        for observation in db.query(Observation).filter_by(evidence_id=evidence_id, kind="phash").all():
            value = _observation_value(observation).get("hash")
            if isinstance(value, str):
                matches.extend(_similar_matches(db, job.household_id or "", evidence_id, value))
        collisions.extend(_identifier_collisions(db, job.household_id or "", evidence_id))

    for row in db.query(Observation).filter(Observation.evidence_id.in_(evidence_ids), Observation.kind == "barcode_qr").all():
        value = _observation_value(row)
        if value.get("validated") is True and value.get("value"):
            identifier = str(value["value"])
            break

    asset_id: str | None = None
    if exact_assets:
        kind = "duplicate_of_asset"
        asset_id = exact_assets[0]
    elif any(match["type"] == "similar" for match in matches):
        kind = "similar"
        asset_id = str(next(match["asset_id"] for match in matches if match["type"] == "similar"))
    else:
        kind = "new_asset"
        asset_id = None

    fields: dict[str, object] = {
        "display_name": _display_name(evidence_rows[0] if evidence_rows else None),
        "asset_type": "unknown",
        "status": "ACTIVE",
    }
    if identifier is not None:
        fields["identifier"] = identifier
    proposal: dict[str, object] = {
        "kind": kind,
        "asset_id": asset_id,
        "fields": fields,
        "dedup_matches": matches,
        "review_task_ids": [],
    }
    candidate = Candidate(
        job_id=job.id,
        evidence_ids_json=json.dumps(evidence_ids),
        proposed_fields_json=json.dumps(proposal, ensure_ascii=False),
        state="proposed",
        household_id=job.household_id or "",
    )
    db.add(candidate)
    db.flush()
    task_ids: list[str] = []
    for collision in collisions:
        task = ReviewTask(
            task_type="identifier_collision",
            priority="high",
            subject_ref=candidate.id,
            proposed_change=json.dumps({"candidate_id": candidate.id, **collision}),
            status="open",
            household_id=job.household_id,
        )
        db.add(task)
        db.flush()
        task_ids.append(task.id)
    proposal["review_task_ids"] = task_ids
    candidate.proposed_fields_json = json.dumps(proposal, ensure_ascii=False)
    db.flush()
    return {
        "status": "ok",
        "step": "DEDUPLICATING",
        "candidate_id": candidate.id,
        "kind": kind,
        "asset_id": asset_id,
        "review_task_ids": task_ids,
        "dedup_matches": matches,
    }
