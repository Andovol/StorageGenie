from sqlalchemy import Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id

# Join table: one asset sits in one location once. The composite primary key
# (`asset_id`, `location_id`) IS the "asset+location unique" rule; an asset that
# sits in several locations is several rows, stated, never a wider column.
asset_location = Table(
    "asset_location",
    Base.metadata,
    Column("asset_id", String(36), ForeignKey("asset.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "location_id",
        String(36),
        ForeignKey("location.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)


class Location(TimestampMixin, Base):
    """A storage-location node in one household's tree (blueprint §9.2).

    `parent_id` is a nullable self-FK: NULL is a root. The tree SHAPE (no
    cycles, no orphans) is enforced by the API, never trusted from input; the
    self-FK cascade is a last-resort integrity net, never a silent subtree
    delete (delete-with-children is refused in the route). Seed names such as
    fridge/freezer are free-text hints elsewhere, never pre-created here.
    """

    __tablename__ = "location"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("location.id", ondelete="CASCADE"), nullable=True, index=True
    )
