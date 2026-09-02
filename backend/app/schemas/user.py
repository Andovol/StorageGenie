from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    display_name: str
    email: str | None = None


class UserOut(BaseModel):
    id: str
    household_id: str
    display_name: str
    email: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
