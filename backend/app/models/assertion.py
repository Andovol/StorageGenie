from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, new_id

if TYPE_CHECKING:
    from app.models.asset import Asset


class Assertion(TimestampMixin, Base):
    __tablename__ = "assertion"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("asset.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_path: Mapped[str] = mapped_column(String(200), nullable=False)
    value_json: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    review_state: Mapped[str] = mapped_column(String(50), nullable=False, default="accepted")
    source_evidence_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="assertions")
