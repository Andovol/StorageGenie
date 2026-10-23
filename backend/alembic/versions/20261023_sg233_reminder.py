"""expiry reminders: durable per-asset daily rows (SG-233, G1)

Revision ID: 20261023_sg233_reminder
Revises: 20260924_sg114_relation
Create Date: 2026-10-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261023_sg233_reminder"
down_revision: Union[str, None] = "20260924_sg114_relation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    if not op.get_context().as_sql and _has_table("reminder"):
        return
    op.create_table(
        "reminder",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("as_of_day", sa.String(length=10), nullable=False),
        sa.Column("tier", sa.String(length=50), nullable=True),
        sa.Column("bucket", sa.String(length=20), nullable=False),
        sa.Column("days_remaining", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
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
        sa.ForeignKeyConstraint(["asset_id"], ["asset.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_id", "as_of_day", name="uq_reminder_asset_as_of_day"),
    )
    op.create_index(
        op.f("ix_reminder_household_id"), "reminder", ["household_id"], unique=False
    )
    op.create_index(op.f("ix_reminder_asset_id"), "reminder", ["asset_id"], unique=False)
    op.create_index(op.f("ix_reminder_status"), "reminder", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reminder_status"), table_name="reminder")
    op.drop_index(op.f("ix_reminder_asset_id"), table_name="reminder")
    op.drop_index(op.f("ix_reminder_household_id"), table_name="reminder")
    op.drop_table("reminder")
