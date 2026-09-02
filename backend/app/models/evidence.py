from sqlalchemy import Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id

# Join table: many-to-many asset ↔ evidence (one photo can back multiple assets after split/merge)
asset_evidence = Table(
    "asset_evidence",
    Base.metadata,
    Column("asset_id", String(36), ForeignKey("asset.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", String(36), ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)


class Evidence(TimestampMixin, Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    media_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    source_kind: Mapped[str] = mapped_column(String(50), nullable=False, default="upload")
    size_bytes: Mapped[int] = mapped_column(nullable=False)
