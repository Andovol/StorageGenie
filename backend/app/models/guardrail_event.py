from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id


class GuardrailEvent(TimestampMixin, Base):
    """Append-only Stage-1 evidence log (Phase 3 §10); rows are never updated."""

    __tablename__ = "guardrail_event"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    ref_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    detail_json: Mapped[str] = mapped_column(Text, nullable=False)
