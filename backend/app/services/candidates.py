from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.config import settings
from app.db import Base
from app.models.asset import Asset
from app.models.assertion import Assertion
from app.models.evidence import Evidence, asset_evidence
from app.models.job import Job, JobStep
from app.models.review_task import ReviewTask
from app.models.base import TimestampMixin, new_id
from app.services import audit_service
from app.services.observations import Observation
from app.services.providers.schemas import ExtractionOutput

# SG-028 §5.2-7: safety-critical/serialized fields always route to review,
# whatever the confidence. Every other field auto-accepts at/above the single
# configured threshold (`settings.sg_confidence_threshold`, uncalibrated).
GATED_FIELDS = frozenset({"identifier", "expiry", "expiry_date", "condition", "lot"})
ALLOWED_CANDIDATE_FIELDS = frozenset(
    {
        "display_name",
        "asset_type",
        "status",
        "quantity",
        "unit",
        "condition",
        "identifier",
        "expiry",
        "expiry_date",
        "lot",
    }
)


def _field_parts(raw: object) -> tuple[object, dict[str, object] | None]:
    """Split a candidate field into (value, provenance-envelope or None).

    AI candidate fields carry the provenance object CandidateCard.fieldInfo
    already renders; deterministic Phase-1 fields are plain scalars.
    """
    if isinstance(raw, dict) and "source_type" in raw:
        return raw.get("value"), raw
    return raw, None


def _provenance(
    value: object,
    *,
    source_type: str,
    confidence: float | None = None,
    provider: object = None,
    model: object = None,
    template_version: object = None,
    provider_call_id: object = None,
) -> dict[str, object]:
    return {
        "value": value,
        "confidence": confidence,
        "source_type": source_type,
        "provider": provider,
        "model": model,
        "prompt_template_version": template_version,
        "provider_call_id": provider_call_id,
    }


def _review_state_for(field_path: str, confidence: float | None) -> str:
    if field_path in GATED_FIELDS:
        return "proposed"
    if confidence is not None and confidence < settings.sg_confidence_threshold:
        return "proposed"
    return "accepted"


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


def _job_evidence_ids(db: Session, job_id: str) -> list[str]:
    job = db.query(Job).filter_by(id=job_id).first()
    if job is None:
        return []
    config = json.loads(job.config_snapshot or "{}")
    value = config.get("evidence_ids", [])
    if not isinstance(value, list):
        raise ValueError("invalid evidence_ids in job config")
    return [str(item) for item in value]


def _observation_ids(db: Session, job_id: str) -> list[str]:
    step = (
        db.query(JobStep)
        .filter_by(job_id=job_id, step_name="EXTRACTING_DETERMINISTIC_SIGNALS")
        .first()
    )
    if step is None or not step.output_refs:
        return []
    output = json.loads(step.output_refs)
    value = output.get("observation_ids", []) if isinstance(output, dict) else []
    return [str(item) for item in value] if isinstance(value, list) else []


def _step_output(db: Session, job_id: str, step_name: str) -> dict[str, object] | None:
    step = db.query(JobStep).filter_by(job_id=job_id, step_name=step_name).first()
    if step is None or not step.output_refs:
        return None
    value = json.loads(step.output_refs)
    return value if isinstance(value, dict) else None


def _deterministic_display_name(db: Session, evidence_ids: list[str]) -> str:
    if not evidence_ids:
        return "Imported item"
    evidence = db.get(Evidence, evidence_ids[0])
    if evidence is None:
        return "Imported item"
    return Path(evidence.original_filename).stem or evidence.original_filename


def _barcode_identifier(db: Session, evidence_ids: list[str]) -> str | None:
    if not evidence_ids:
        return None
    rows = (
        db.query(Observation)
        .filter(Observation.evidence_id.in_(evidence_ids), Observation.kind == "barcode_qr")
        .all()
    )
    for row in rows:
        value = json.loads(row.value_json)
        if isinstance(value, dict) and value.get("validated") is True and value.get("value"):
            return str(value["value"])
    return None


def build_candidate_from_extraction(
    db: Session,
    job: Job,
    extraction: ExtractionOutput,
    analyzing: dict[str, object],
) -> Candidate:
    """Form the candidate from deterministic signals + validated AI output.

    Fields carry the per-field provenance object CandidateCard.fieldInfo already
    renders; the full AI item list and unknowns are preserved on the proposal
    so nothing the provider returned is dropped.
    """
    evidence_ids = _job_evidence_ids(db, job.id)
    provider = analyzing.get("provider")
    model = analyzing.get("model")
    version = analyzing.get("prompt_template_version")
    raw_calls = analyzing.get("provider_call_ids", [])
    call_ids = [str(item) for item in raw_calls] if isinstance(raw_calls, list) else []
    primary_call = call_ids[0] if call_ids else None

    fields: dict[str, object] = {
        "display_name": _provenance(
            _deterministic_display_name(db, evidence_ids), source_type="deterministic"
        ),
        "asset_type": _provenance("unknown", source_type="deterministic"),
        "status": _provenance("ACTIVE", source_type="deterministic"),
    }
    identifier = _barcode_identifier(db, evidence_ids)
    if identifier is not None:
        fields["identifier"] = _provenance(identifier, source_type="deterministic")
    if extraction.items:
        item = extraction.items[0]
        fields["display_name"] = _provenance(
            item.name,
            source_type="extraction",
            confidence=item.confidence,
            provider=provider,
            model=model,
            template_version=version,
            provider_call_id=primary_call,
        )
        if item.expiry_date is not None:
            fields["expiry_date"] = _provenance(
                item.expiry_date,
                source_type="extraction",
                confidence=item.confidence,
                provider=provider,
                model=model,
                template_version=version,
                provider_call_id=primary_call,
            )
        if item.lot is not None:
            fields["lot"] = _provenance(
                item.lot,
                source_type="extraction",
                confidence=item.confidence,
                provider=provider,
                model=model,
                template_version=version,
                provider_call_id=primary_call,
            )

    proposal: dict[str, object] = {
        "kind": "new_asset",
        "asset_id": None,
        "fields": fields,
        "dedup_matches": [],
        "review_task_ids": [],
        "ai_items": [item.model_dump() for item in extraction.items],
        "ai_unknowns": list(extraction.unknowns),
        "needs_evidence": extraction.needs_evidence,
        "ai_provider": provider,
        "ai_model": model,
        "prompt_template_version": version,
        "provider_call_ids": call_ids,
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
    if len(extraction.items) > 1:
        task = ReviewTask(
            task_type="candidate.multi_item",
            priority="high",
            subject_ref=candidate.id,
            proposed_change=json.dumps(
                {"candidate_id": candidate.id, "item_count": len(extraction.items)}
            ),
            status="open",
            household_id=job.household_id,
        )
        db.add(task)
        db.flush()
        task_ids.append(task.id)
    if extraction.needs_evidence:
        task = ReviewTask(
            task_type="expiry.manual_entry",
            priority="high",
            subject_ref=candidate.id,
            proposed_change=json.dumps(
                {"candidate_id": candidate.id, "prompt": "Enter expiry date manually"}
            ),
            status="open",
            household_id=job.household_id,
        )
        db.add(task)
        db.flush()
        task_ids.append(task.id)
    proposal["review_task_ids"] = task_ids
    candidate.proposed_fields_json = json.dumps(proposal, ensure_ascii=False)
    db.flush()
    return candidate


def build_candidates_step(db: Session, job: Job) -> dict[str, object]:
    analyzing = _step_output(db, job.id, "ANALYZING_WITH_AI")
    if not analyzing or analyzing.get("status") != "ok":
        reason = str(analyzing.get("reason", "no_ai_output")) if analyzing else "no_ai_output"
        return {"status": "skipped", "step": "BUILDING_CANDIDATES", "reason": reason}
    raw_extraction = analyzing.get("extraction")
    if not isinstance(raw_extraction, dict):
        raise ValueError("AI step output is missing the validated extraction")
    extraction = ExtractionOutput.model_validate(raw_extraction)
    candidate = build_candidate_from_extraction(db, job, extraction, analyzing)
    return {
        "status": "ok",
        "step": "BUILDING_CANDIDATES",
        "candidate_id": candidate.id,
        "item_count": len(extraction.items),
        "review_task_ids": load_proposal(candidate).get("review_task_ids", []),
    }


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

    display, _ = _field_parts(fields.get("display_name"))
    asset_type, _ = _field_parts(fields.get("asset_type"))
    status, _ = _field_parts(fields.get("status"))
    quantity, _ = _field_parts(fields.get("quantity"))
    unit, _ = _field_parts(fields.get("unit"))
    condition, _ = _field_parts(fields.get("condition"))
    asset = Asset(
        household_id=candidate.household_id,
        display_name=str(display or "Imported item"),
        asset_type=str(asset_type or "unknown"),
        status=str(status or "ACTIVE"),
        quantity=quantity,
        unit=unit,
        condition=condition,
    )
    db.add(asset)
    db.flush()

    observation_ids = _observation_ids(db, candidate.job_id)
    for field_path, raw in fields.items():
        value, provenance = _field_parts(raw)
        if value is None:
            continue
        if field_path not in ALLOWED_CANDIDATE_FIELDS:
            raise ValueError(f"unsupported candidate field: {field_path}")
        confidence: float | None = None
        source_type = "deterministic"
        model_json: str | None = None
        if provenance is not None:
            raw_confidence = provenance.get("confidence")
            confidence = float(raw_confidence) if isinstance(raw_confidence, (int, float)) else None
            if provenance.get("source_type") == "extraction":
                source_type = "extraction"
                model_json = json.dumps(
                    {
                        "provider": provenance.get("provider"),
                        "model": provenance.get("model"),
                        "prompt_template_version": provenance.get("prompt_template_version"),
                        "provider_call_id": provenance.get("provider_call_id"),
                        "evidence_ids": evidence_ids,
                        "observation_ids": observation_ids,
                    },
                    ensure_ascii=False,
                )
        db.add(
            Assertion(
                asset_id=asset.id,
                field_path=field_path,
                value_json=json.dumps(value, ensure_ascii=False),
                source_type=source_type,
                confidence=confidence,
                review_state=_review_state_for(field_path, confidence if source_type == "extraction" else None),
                source_evidence_ids=json.dumps(evidence_ids),
                model_json=model_json,
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
