from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id


class Job(TimestampMixin, Base):
    __tablename__ = "job"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, default="import")
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="CREATED")
    idempotency_key: Mapped[str | None] = mapped_column(String(200), nullable=True, unique=True)
    config_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    household_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=True, index=True
    )


class JobStep(Base):
    __tablename__ = "job_step"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    input_refs: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_refs: Mapped[str | None] = mapped_column(Text, nullable=True)
