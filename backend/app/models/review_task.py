from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id


class ReviewTask(TimestampMixin, Base):
    __tablename__ = "review_task"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, default="review")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    subject_ref: Mapped[str] = mapped_column(String(36), nullable=False)
    proposed_change: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")
    household_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=True, index=True
    )
