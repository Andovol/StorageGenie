"""SG-066 Analytics API: deterministic household stats + manual NL summary.

`GET /v1/analytics/summary` returns computed-from-tables stats only (no
provider, $0). `POST /v1/analytics/insights` runs the Analytics Insight Agent on
a manual trigger, consent-gated BEFORE any call or row; an ungrounded summary
(citing a stat id that was not supplied) is a loud 502, never trimmed silently.
No route executes anything or writes catalogue state.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.household import Household
from app.services.analytics import service

router = APIRouter()


def _require_household(db: Session, household_id: str) -> None:
    if db.query(Household).filter_by(id=household_id).first() is None:
        raise HTTPException(status_code=404, detail="Household not found")


@router.get("/analytics/summary")
def get_analytics_summary(
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _require_household(db, household_id)
    return service.compute_stats(db, household_id)


@router.post("/analytics/insights")
def post_analytics_insights(
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _require_household(db, household_id)
    result = service.run_insights(db, household_id)
    if result["status"] == "ungrounded":
        raise HTTPException(
            status_code=502,
            detail="insight cites unknown stat id(s): "
            + ", ".join(result.get("unresolved_stat_ids") or [])
            + (" (no citations found)" if not result.get("cited_stat_ids") else ""),
        )
    return result
