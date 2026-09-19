from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, new_id

if TYPE_CHECKING:
    from app.models.assertion import Assertion

# SG-049 F-SG048-2: the ONE label a nameless asset shows in the AI catalogue
# grounding built by planning/service.py and chat/service.py. This module is the
# safe home: it imports only `app.db` + `app.models.base`, so importing the
# constant here can never create a cycle with the service layer that imports it.
UNTITLED_LABEL = "Untitled asset"


class Asset(TimestampMixin, Base):
    __tablename__ = "asset"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True
    )
    display_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")
    quantity: Mapped[float | None] = mapped_column(nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    version: Mapped[int] = mapped_column(default=1, nullable=False)

    assertions: Mapped[List["Assertion"]] = relationship(
        "Assertion", back_populates="asset", order_by="Assertion.field_path"
    )
