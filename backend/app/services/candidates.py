from __future__ import annotations

import json

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.db import Base
from app.models.asset import Asset
from app.models.assertion import Assertion
from app.models.evidence import Evidence, asset_evidence
from app.models.job import Job
from app.models.review_task import ReviewTask
from app.models.base import TimestampMixin, new_id
from app.services import audit_service


class Candidate(TimestampMixin, Base):
    __tablename__ = "candidate"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_fields_json: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(String(30), nullable=False, default="proposed")
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True
    )


class CandidateBlockedError(RuntimeError):
    pass


def load_proposal(candidate: Candidate) -> dict[str, object]:
    value = json.loads(candidate.proposed_fields_json)
    if not isinstance(value, dict):
        raise ValueError("candidate proposal must be an object")
    return value


def _asset_fields(proposal: dict[str, object]) -> dict[str, object]:
    fields = proposal.get("fields", {})
    if not isinstance(fields, dict):
        raise ValueError("candidate fields must be an object")
    return dict(fields)


def _create_asset_for_candidate(db: Session, candidate: Candidate) -> Asset:
    proposal = load_proposal(candidate)
    fields = _asset_fields(proposal)
    evidence_ids = json.loads(candidate.evidence_ids_json)
    if not isinstance(evidence_ids, list):
        raise ValueError("candidate evidence_ids must be a list")
    evidence_ids = [str(item) for item in evidence_ids]
    evidence_rows = db.query(Evidence).filter(Evidence.id.in_(evidence_ids)).all() if evidence_ids else []
    if len(evidence_rows) != len(set(evidence_ids)) or any(
        row.household_id != candidate.household_id for row in evidence_rows
    ):
        raise ValueError("candidate evidence does not belong to its household")

    asset = Asset(
        household_id=candidate.household_id,
        display_name=str(fields.get("display_name") or "Imported item"),
        asset_type=str(fields.get("asset_type") or "unknown"),
        status=str(fields.get("status") or "ACTIVE"),
        quantity=fields.get("quantity"),
        unit=fields.get("unit"),
        condition=fields.get("condition"),
    )
    db.add(asset)
    db.flush()

    accepted_fields = {"display_name", "asset_type", "status", "quantity", "unit", "condition"}
    for field_path, value in fields.items():
        if value is None:
            continue
        if field_path not in accepted_fields and field_path not in {"identifier", "expiry", "expiry_date"}:
            raise ValueError(f"unsupported candidate field: {field_path}")
        db.add(
            Assertion(
                asset_id=asset.id,
                field_path=field_path,
                value_json=json.dumps(value, ensure_ascii=False),
                source_type="deterministic",
                review_state="proposed" if field_path in {"identifier", "expiry", "expiry_date"} else "accepted",
                source_evidence_ids=json.dumps(evidence_ids),
            )
        )

    for evidence_id in evidence_ids:
        db.execute(asset_evidence.insert().values(asset_id=asset.id, evidence_id=evidence_id))

    audit_service.record(
        db,
        actor="import-runner",
        action="asset.create",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after={"candidate_id": candidate.id, "fields": fields},
        household_id=candidate.household_id,
    )
    audit_service.record(
        db,
        actor="import-runner",
        action="asset.accepted",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after={"review_state": "accepted", "candidate_id": candidate.id},
        household_id=candidate.household_id,
    )
    audit_service.record(
        db,
        actor="import-runner",
        action="asset.lifecycle.created",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after={"event_type": "created", "source": "deterministic", "candidate_id": candidate.id},
        household_id=candidate.household_id,
    )
    return asset


def commit_candidate(db: Session, candidate: Candidate) -> dict[str, object]:
    if candidate.state not in {"accepted", "edited"}:
        raise CandidateBlockedError(f"candidate state {candidate.state} is not committable")
    open_tasks = (
        db.query(ReviewTask)
        .filter(
            ReviewTask.subject_ref == candidate.id,
            ReviewTask.household_id == candidate.household_id,
            ReviewTask.status == "open",
        )
        .all()
    )
    if open_tasks:
        raise CandidateBlockedError("candidate has unresolved review tasks")

    proposal = load_proposal(candidate)
    if proposal.get("kind") == "duplicate_of_asset":
        asset_id = proposal.get("asset_id")
        if not isinstance(asset_id, str):
            raise ValueError("duplicate proposal is missing asset_id")
        return {"status": "duplicate_linked", "asset_id": asset_id, "created": False}

    asset = _create_asset_for_candidate(db, candidate)
    db.flush()
    return {"status": "committed", "asset_id": asset.id, "created": True}


def commit_job_candidate(db: Session, job: Job) -> dict[str, object]:
    candidate = db.query(Candidate).filter_by(job_id=job.id).order_by(Candidate.created_at).first()
    if candidate is None:
        raise ValueError("job has no candidate")
    result = commit_candidate(db, candidate)
    return {"status": "ok", "step": "COMMITTING", "candidate_id": candidate.id, **result}
