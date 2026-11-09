import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.job import Job, JobStep
from app.models.review_task import ReviewTask
from app.services import audit_service, candidates, job_service

router = APIRouter()


class CandidateDecision(BaseModel):
    action: Literal["accept", "edit", "hold", "reject"]
    corrected_fields: dict[str, object] = Field(default_factory=dict)


class CandidateSplitRequest(BaseModel):
    item_indexes: list[int] = Field(default_factory=list)


class CandidateMergeRequest(BaseModel):
    winner_id: str
    loser_ids: list[str] = Field(default_factory=list)


def _close_rejected_candidate_tasks(
    db: Session, candidate: candidates.Candidate, household_id: str
) -> None:
    """Close the candidate's open tasks, naming the rejection and never a date."""
    open_tasks = (
        db.query(ReviewTask)
        .filter_by(subject_ref=candidate.id, household_id=household_id, status="open")
        .all()
    )
    for task in open_tasks:
        before = {"status": task.status}
        task.status = "resolved"
        audit_service.record(
            db,
            actor="api",
            action="review_task.resolve",
            entity_type="review_task",
            entity_id=task.id,
            before=before,
            after={
                "status": task.status,
                "resolution": {"candidate_rejected": candidate.id},
            },
            household_id=task.household_id,
        )


def _created_asset_from_commit_step(
    commit_step: JobStep | None, candidate_id: str
) -> str | None:
    """The asset id a pre-SG-270 commit wrote into its step output, if any."""
    if commit_step is None or not commit_step.output_refs:
        return None
    try:
        output = json.loads(commit_step.output_refs)
    except ValueError:
        return None
    if not isinstance(output, dict):
        return None
    asset_id = output.get("asset_id")
    if (
        output.get("candidate_id") == candidate_id
        and output.get("created") is True
        and isinstance(asset_id, str)
    ):
        return asset_id
    return None


def _prepare_commit_steps(
    db: Session, job: Job, candidate: candidates.Candidate
) -> None:
    """Record the decided candidate and give the commit step a fresh pass."""
    review_step = next(
        (step for step in job_service._steps(db, job.id) if step.step_name == "AWAITING_REVIEW"),
        None,
    )
    commit_step = next(
        (step for step in job_service._steps(db, job.id) if step.step_name == "COMMITTING"),
        None,
    )
    if review_step is not None:
        previous_output: dict[str, object] = {}
        if review_step.output_refs:
            try:
                loaded = json.loads(review_step.output_refs)
            except ValueError:
                loaded = None
            if isinstance(loaded, dict):
                previous_output = loaded
        review_output: dict[str, object] = {"status": "decision", "candidate_id": candidate.id}
        committed_assets = previous_output.get("committed_assets")
        if not isinstance(committed_assets, dict):
            committed_assets = {}
        # SG-275: a commit made before the map existed left its asset only in the
        # commit step's own output. Record that created asset before the reset
        # below, so a repeat decision on the older row returns it, not a second.
        prior_asset_id = _created_asset_from_commit_step(commit_step, candidate.id)
        if prior_asset_id is not None:
            committed_assets[candidate.id] = prior_asset_id
        if committed_assets:
            review_output["committed_assets"] = committed_assets
        review_step.state = job_service.COMPLETED_STEP
        review_step.output_refs = json.dumps(review_output)
    # SG-270 G2: every accepted candidate (including a second split child) gets
    # its own commit pass; a repeat decision on the same candidate is idempotent
    # through the review step's committed_assets map.
    if commit_step is not None:
        commit_step.state = job_service.PENDING_STEP
        commit_step.output_refs = None


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
    if candidate.state in {"rejected", "split", "merged"}:
        raise HTTPException(status_code=409, detail=f"Candidate is {candidate.state}")

    if payload.action in {"hold", "reject"}:
        candidate.state = "held" if payload.action == "hold" else "rejected"
        if payload.action == "reject":
            _close_rejected_candidate_tasks(db, candidate, household_id)
        db.commit()
        return {"id": candidate.id, "state": candidate.state, "job_id": candidate.job_id}

    if candidates.blocking_review_task_ids(db, candidate):
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
    _prepare_commit_steps(db, job, candidate)
    job_service._transition(db, job, "RUNNING")
    db.commit()
    result = job_service.run_job(db, db.query(Job).filter_by(id=job.id).one())
    commit_step = next((step for step in job_service._steps(db, job.id) if step.step_name == "COMMITTING"), None)
    output = json.loads(commit_step.output_refs) if commit_step and commit_step.output_refs else {}
    return {"candidate_id": candidate.id, "state": candidate.state, "job": job_service.serialize_job(db, result), **output}


def _serialize_split_child(child: candidates.Candidate) -> dict[str, object]:
    proposal = candidates.load_proposal(child)
    fields = proposal.get("fields", {})
    evidence_ids = json.loads(child.evidence_ids_json)
    return {
        "id": child.id,
        "state": child.state,
        "job_id": child.job_id,
        "fields": fields if isinstance(fields, dict) else {},
        "evidence_ids": (
            [str(item) for item in evidence_ids] if isinstance(evidence_ids, list) else []
        ),
        "split_item_index": proposal.get("split_item_index"),
    }


@router.post("/candidates/{candidate_id}/split")
def split_candidate(
    candidate_id: str,
    payload: CandidateSplitRequest,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    candidate = db.query(candidates.Candidate).filter_by(id=candidate_id).first()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    try:
        children, resolved_task_ids = candidates.split_candidate(
            db, candidate, payload.item_indexes
        )
    except candidates.CandidateSplitError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    db.commit()
    return {
        "candidate_id": candidate.id,
        "state": candidate.state,
        "resolved_task_ids": resolved_task_ids,
        "children": [_serialize_split_child(child) for child in children],
    }


@router.post("/candidates/merge")
def merge_candidates(
    payload: CandidateMergeRequest,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    try:
        winner, losers, resolved_task_ids = candidates.merge_candidates(
            db, payload.winner_id, payload.loser_ids, household_id
        )
    except candidates.CandidateMergeError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    db.commit()
    return {
        "winner_id": winner.id,
        "state": winner.state,
        "evidence_ids": [str(item) for item in json.loads(winner.evidence_ids_json)],
        "merged_loser_ids": [loser.id for loser in losers],
        "resolved_task_ids": resolved_task_ids,
    }


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
    review_task_ids = candidates.open_review_task_ids(db, candidate)
    blocking_review_task_ids = candidates.blocking_review_task_ids(db, candidate)
    dedup_matches = proposal.get("dedup_matches", [])
    if not isinstance(dedup_matches, list):
        dedup_matches = []
    fields = proposal.get("fields", {})
    if not isinstance(fields, dict):
        fields = {}
    web_alternates = proposal.get("web_alternates", [])
    if not isinstance(web_alternates, list):
        web_alternates = []
    # SG-271 G2: a candidate that already led to an item says so on first load
    # and on reload — derived from the commit rows, never stored.
    asset_id = candidates.committed_asset_id(db, candidate)
    merged_into = proposal.get("merged_into")
    return {
        "id": candidate.id,
        "state": candidate.state,
        "job_id": candidate.job_id,
        "fields": fields,
        "dedup_matches": dedup_matches,
        "review_task_ids": review_task_ids,
        "blocking_review_task_ids": blocking_review_task_ids,
        "evidence_ids": [str(item) for item in evidence_ids],
        "asset_id": asset_id if isinstance(asset_id, str) else None,
        "web_alternates": web_alternates,
        "merged_into": merged_into if isinstance(merged_into, str) else None,
    }
