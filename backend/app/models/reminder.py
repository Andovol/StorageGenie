from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id


class Reminder(TimestampMixin, Base):
    """One in-app expiry reminder per asset per compute day (SG-233)."""

    __tablename__ = "reminder"
    __table_args__ = (
        UniqueConstraint("asset_id", "as_of_day", name="uq_reminder_asset_as_of_day"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("household.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("asset.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    as_of_day: Mapped[str] = mapped_column(String(10), nullable=False)
    tier: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bucket: Mapped[str] = mapped_column(String(20), nullable=False)
    days_remaining: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="unread", index=True
    )
