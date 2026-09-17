from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id


class SavedSearch(TimestampMixin, Base):
    """A named, per-household catalog filter set (SG-068, Phase 4).

    ``query_json`` holds EXACTLY the catalog filter surface the list endpoint
    already accepts (``q`` / ``asset_type`` / ``status`` / ``has_evidence``),
    serialized as JSON text. It is not a second query language: applying a
    saved search maps it back onto the same request parameters.
    """

    __tablename__ = "saved_search"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    query_json: Mapped[str] = mapped_column(Text, nullable=False)
