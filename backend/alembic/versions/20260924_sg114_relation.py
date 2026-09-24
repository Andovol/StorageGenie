"""asset relations: typed links (SG-114, G4)

Revision ID: 20260924_sg114_relation
Revises: 20260924_sg113_location
Create Date: 2026-09-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260924_sg114_relation"
down_revision: Union[str, None] = "20260924_sg113_location"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    if _has_table("asset_relation"):
        return
    op.create_table(
        "asset_relation",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
        sa.Column("from_asset_id", sa.String(length=36), nullable=False),
        sa.Column("to_asset_id", sa.String(length=36), nullable=False),
        sa.Column("relation_type", sa.String(length=50), nullable=False),
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
        sa.ForeignKeyConstraint(["from_asset_id"], ["asset.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_asset_id"], ["asset.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "from_asset_id",
            "to_asset_id",
            "relation_type",
            name="uq_asset_relation_from_to_type",
        ),
    )
    op.create_index(
        op.f("ix_asset_relation_household_id"), "asset_relation", ["household_id"], unique=False
    )
    op.create_index(
        op.f("ix_asset_relation_from_asset_id"), "asset_relation", ["from_asset_id"], unique=False
    )
    op.create_index(
        op.f("ix_asset_relation_to_asset_id"), "asset_relation", ["to_asset_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_asset_relation_to_asset_id"), table_name="asset_relation")
    op.drop_index(op.f("ix_asset_relation_from_asset_id"), table_name="asset_relation")
    op.drop_index(op.f("ix_asset_relation_household_id"), table_name="asset_relation")
    op.drop_table("asset_relation")
