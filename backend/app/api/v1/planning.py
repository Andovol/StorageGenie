"""SG-037 planning API: manual trigger + suggestion lifecycle.

`POST /v1/planning/run` runs one consent-gated planning pass and writes pending
suggestions. `GET /v1/planning/suggestions` lists them with an optional status
filter. `confirm`/`dismiss` validate the transition in service code; an illegal
move is an enforced 422. No route executes a suggestion.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.planning_suggestion import PlanningSuggestion
from app.services.planning import service

router = APIRouter()


class DismissPayload(BaseModel):
    reason: str | None = None


def _suggestion_to_dict(suggestion: PlanningSuggestion) -> dict[str, Any]:
    return {
        "id": suggestion.id,
        "household_id": suggestion.household_id,
        "kind": suggestion.kind,
        "title": suggestion.title,
        "body": json.loads(suggestion.body_json) if suggestion.body_json else None,
        "backing_refs": json.loads(suggestion.backing_refs_json)
        if suggestion.backing_refs_json
        else [],
        "status": suggestion.status,
        "created_at": suggestion.created_at.isoformat() if suggestion.created_at else None,
        "updated_at": suggestion.updated_at.isoformat() if suggestion.updated_at else None,
    }


@router.post("/planning/run")
def post_planning_run(
    household_id: str = Query(...),
        db: Session = Depends(get_db),
) -> dict[str, Any]:
    return service.run_planning(db, household_id)


@router.get("/planning/suggestions")
def list_planning_suggestions(
    household_id: str = Query(...),
    status: str | None = Query(default=None),
        db: Session = Depends(get_db),
) -> dict[str, Any]:
    if status is not None and status not in service.ALLOWED_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"unknown suggestion status: {status}",
        )
    suggestions = service.list_suggestions(db, household_id, status)
    return {
        "items": [_suggestion_to_dict(suggestion) for suggestion in suggestions],
        "total": len(suggestions),
    }


@router.post("/planning/suggestions/{suggestion_id}/confirm")
def confirm_planning_suggestion(
    suggestion_id: str,
    household_id: str = Query(...),
        db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        suggestion = service.confirm_suggestion(db, household_id, suggestion_id)
    except service.SuggestionNotFound:
        raise HTTPException(status_code=404, detail="Suggestion not found") from None
    except service.SuggestionHouseholdMismatch:
        raise HTTPException(status_code=403, detail="Household mismatch") from None
    except service.SuggestionTransitionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return _suggestion_to_dict(suggestion)


@router.post("/planning/suggestions/{suggestion_id}/dismiss")
def dismiss_planning_suggestion(
    suggestion_id: str,
    payload: DismissPayload | None = None,
    household_id: str = Query(...),
        db: Session = Depends(get_db),
) -> dict[str, Any]:
    reason = payload.reason if payload is not None else None
    try:
        suggestion = service.dismiss_suggestion(db, household_id, suggestion_id, reason)
    except service.SuggestionNotFound:
        raise HTTPException(status_code=404, detail="Suggestion not found") from None
    except service.SuggestionHouseholdMismatch:
        raise HTTPException(status_code=403, detail="Household mismatch") from None
    except service.SuggestionTransitionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return _suggestion_to_dict(suggestion)
