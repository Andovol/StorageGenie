"""Saved-search schemas (SG-068).

The accepted ``query`` keys are EXACTLY the filter surface ``GET /v1/assets``
already sends — ``q`` (FTS MATCH), ``asset_type``, ``status``,
``has_evidence``. ``extra="forbid"`` makes an unknown key a visible 422 naming
it (PG-SC-05), never a silent drop. The caps below are named settings with a
visible rejection (PG-SC-06 / G-A8), not silent truncation.
"""

from datetime import datetime

from pydantic import BaseModel, Field

SAVED_SEARCH_NAME_MAX_LENGTH = 80
SAVED_SEARCH_QUERY_MAX_BYTES = 2048
SAVED_SEARCH_QUERY_KEYS = ("q", "asset_type", "status", "has_evidence")


class SavedSearchQuery(BaseModel):
    model_config = {"extra": "forbid"}

    q: str | None = None
    asset_type: str | None = None
    status: str | None = None
    has_evidence: bool | None = None


class SavedSearchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=SAVED_SEARCH_NAME_MAX_LENGTH)
    query: SavedSearchQuery


class SavedSearchOut(BaseModel):
    id: str
    household_id: str
    name: str
    query: SavedSearchQuery
    created_at: datetime | None = None
