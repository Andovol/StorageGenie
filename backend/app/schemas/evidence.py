from datetime import datetime

from pydantic import BaseModel


class EvidenceOut(BaseModel):
    id: str
    household_id: str
    sha256: str
    media_type: str
    storage_key: str
    original_filename: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}
