"""location tree + asset location assignment (SG-113, G3)

Revision ID: 20260924_sg113_location
Revises: 20260923_sg100_enrich_snapshot
Create Date: 2026-09-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260924_sg113_location"
down_revision: Union[str, None] = "20260923_sg100_enrich_snapshot"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    if _has_table("location"):
        return
    op.create_table(
        "location",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("parent_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["household_id"], ["household.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["location.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_location_household_id"), "location", ["household_id"], unique=False
    )
    op.create_index(op.f("ix_location_parent_id"), "location", ["parent_id"], unique=False)
    op.create_table(
        "asset_location",
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("location_id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["asset_id"], ["asset.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("asset_id", "location_id"),
    )
    op.create_index(
        op.f("ix_asset_location_location_id"),
        "asset_location",
        ["location_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_asset_location_location_id"), table_name="asset_location")
    op.drop_table("asset_location")
    op.drop_index(op.f("ix_location_parent_id"), table_name="location")
    op.drop_index(op.f("ix_location_household_id"), table_name="location")
    op.drop_table("location")
