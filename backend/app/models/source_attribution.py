import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id


class SourceAttribution(TimestampMixin, Base):
    """Where an external source lookup attaches to a catalog field (Phase 3 S2)."""

    __tablename__ = "source_attribution"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("asset.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assertion_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("assertion.id", ondelete="SET NULL"), nullable=True, index=True
    )
    field_path: Mapped[str] = mapped_column(String(200), nullable=False)
    uri: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
