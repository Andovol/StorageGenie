"""enrichment snapshot store (SG-100, Arc A)

Revision ID: 20260923_sg100_enrich_snapshot
Revises: 20260917_sg068_saved_search
Create Date: 2026-09-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260923_sg100_enrich_snapshot"
down_revision: Union[str, None] = "20260917_sg068_saved_search"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    if _has_table("enrich_snapshot"):
        return
    op.create_table(
        "enrich_snapshot",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("request_url", sa.Text(), nullable=False),
        sa.Column("retrieved_at", sa.String(length=64), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("raw_body", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("no_result_reason", sa.Text(), nullable=True),
        sa.Column("version", sa.String(length=64), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_enrich_snapshot_source"), "enrich_snapshot", ["source"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_enrich_snapshot_source"), table_name="enrich_snapshot")
    op.drop_table("enrich_snapshot")
