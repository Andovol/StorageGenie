import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.job import Job
from app.models.review_task import ReviewTask
from app.services import candidates, job_service

router = APIRouter()


class CandidateDecision(BaseModel):
    action: Literal["accept", "edit", "hold", "reject"]
    corrected_fields: dict[str, object] = Field(default_factory=dict)


@router.post("/candidates/{candidate_id}/decision")
def decide_candidate(
    candidate_id: str,
    payload: CandidateDecision,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    candidate = db.query(candidates.Candidate).filter_by(id=candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    if candidate.state == "rejected":
        raise HTTPException(status_code=409, detail="Candidate is rejected")

    if payload.action in {"hold", "reject"}:
        candidate.state = "held" if payload.action == "hold" else "rejected"
        db.commit()
        return {"id": candidate.id, "state": candidate.state, "job_id": candidate.job_id}

    if db.query(ReviewTask).filter_by(subject_ref=candidate.id, household_id=household_id, status="open").count():
        raise HTTPException(status_code=409, detail="Candidate has unresolved review tasks")

    if payload.action == "edit":
        proposal = candidates.load_proposal(candidate)
        fields = proposal.get("fields", {})
        if not isinstance(fields, dict):
            raise HTTPException(status_code=422, detail="Candidate fields are invalid")
        fields.update(payload.corrected_fields)
        proposal["fields"] = fields
        candidate.proposed_fields_json = json.dumps(proposal, ensure_ascii=False)
        candidate.state = "edited"
    else:
        candidate.state = "accepted"

    db.commit()
    job = db.query(Job).filter_by(id=candidate.job_id).first()
    if job is None or job.household_id != household_id:
        raise HTTPException(status_code=404, detail="Candidate job not found")
    review_step = next((step for step in job_service._steps(db, job.id) if step.step_name == "AWAITING_REVIEW"), None)
    if review_step is not None:
        review_step.state = job_service.COMPLETED_STEP
        review_step.output_refs = json.dumps({"status": "decision", "candidate_id": candidate.id})
    job_service._transition(db, job, "RUNNING")
    db.commit()
    result = job_service.run_job(db, db.query(Job).filter_by(id=job.id).one())
    commit_step = next((step for step in job_service._steps(db, job.id) if step.step_name == "COMMITTING"), None)
    output = json.loads(commit_step.output_refs) if commit_step and commit_step.output_refs else {}
    return {"candidate_id": candidate.id, "state": candidate.state, "job": job_service.serialize_job(db, result), **output}


@router.get("/candidates/{candidate_id}")
def get_candidate(
    candidate_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    candidate = db.query(candidates.Candidate).filter_by(id=candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")

    proposal = candidates.load_proposal(candidate)
    evidence_ids = json.loads(candidate.evidence_ids_json)
    if not isinstance(evidence_ids, list):
        raise HTTPException(status_code=500, detail="Candidate evidence is invalid")
    review_task_ids = proposal.get("review_task_ids", [])
    if not isinstance(review_task_ids, list):
        review_task_ids = []
    dedup_matches = proposal.get("dedup_matches", [])
    if not isinstance(dedup_matches, list):
        dedup_matches = []
    fields = proposal.get("fields", {})
    if not isinstance(fields, dict):
        fields = {}
    asset_id = proposal.get("asset_id")
    return {
        "id": candidate.id,
        "state": candidate.state,
        "job_id": candidate.job_id,
        "fields": fields,
        "dedup_matches": dedup_matches,
        "review_task_ids": review_task_ids,
        "evidence_ids": [str(item) for item in evidence_ids],
        "asset_id": asset_id if isinstance(asset_id, str) else None,
    }
