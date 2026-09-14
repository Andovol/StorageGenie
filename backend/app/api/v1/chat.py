"""SG-038 chat API: grounded category Q&A plus an explicit correction log.

`POST /v1/chat/{category}` answers one question grounded in that category's
catalogue. `POST /v1/chat/{category}/corrections` is the ONLY write action: an
explicit, user-initiated `correction` guardrail row. The supported category set
is enforced server-side (an unsupported value is an enforced 422); no route
executes anything or changes catalogue state.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.chat import service

router = APIRouter()


class ChatMessagePayload(BaseModel):
    message: str


@router.post("/chat/{category}")
def post_chat(
    category: str,
    payload: ChatMessagePayload,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return service.respond(db, household_id, category, payload.message)
    except service.UnsupportedCategoryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None


@router.post("/chat/{category}/corrections")
def post_chat_correction(
    category: str,
    payload: ChatMessagePayload,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        event = service.log_correction(db, household_id, category, payload.message)
    except service.UnsupportedCategoryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return {
        "id": event.id,
        "kind": event.kind,
        "category": category,
        "message": payload.message,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }
