from datetime import datetime

from pydantic import BaseModel


class AssetCreate(BaseModel):
    display_name: str
    asset_type: str = "unknown"
    status: str = "ACTIVE"
    quantity: float | None = None
    unit: str | None = None
    condition: str | None = None
    evidence_ids: list[str] | None = None


class AssetUpdate(BaseModel):
    display_name: str | None = None
    asset_type: str | None = None
    status: str | None = None
    quantity: float | None = None
    unit: str | None = None
    condition: str | None = None


class AssertionOut(BaseModel):
    id: str
    field_path: str
    value: object
    source_type: str
    confidence: float | None = None
    review_state: str
    source_evidence_ids: object | None = None
    created_at: datetime


class AssetOut(BaseModel):
    id: str
    household_id: str
    display_name: str
    asset_type: str
    status: str
    quantity: float | None = None
    unit: str | None = None
    condition: str | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetDetailOut(AssetOut):
    evidence: list[dict] = []
    assertions: list[AssertionOut] = []
    audit_events: list[dict] = []
