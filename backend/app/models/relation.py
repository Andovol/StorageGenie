from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, new_id


class AssetRelation(TimestampMixin, Base):
    """A typed, directed link between two assets in one household (SG-114).

    The vocabulary is EXACTLY two types and lives in the API module, never
    here:     ``related_to`` (symmetric intent, stored once directed) and
    ``contains`` (directed, container -> content). Duplicate ownership is NOT a
    relation: a materialized duplicate is redirected through the lifecycle
    `MERGED` status + the `merge.merged_into` assertion (SG-112), never a
    relation type. The composite uniqueness rule
    ``(from_asset_id, to_asset_id, relation_type)`` means the same typed link
    written twice is one row; `household_id` is carried on the row so the
    household scope is readable without joining either asset.
    """

    __tablename__ = "asset_relation"
    __table_args__ = (
        UniqueConstraint(
            "from_asset_id",
            "to_asset_id",
            "relation_type",
            name="uq_asset_relation_from_to_type",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("asset.id", ondelete="CASCADE"), nullable=False, index=True
    )
    to_asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("asset.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
