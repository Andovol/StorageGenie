"""provider call ledger (SG-025, blueprint §3.3)

Revision ID: 20260912_sg025_provider_call
Revises: 20260908_sg017_fts
Create Date: 2026-09-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260912_sg025_provider_call"
down_revision: Union[str, None] = "20260908_sg017_fts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "provider_call",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=200), nullable=False),
        sa.Column("prompt_template_version", sa.String(length=100), nullable=False),
        sa.Column("input_hashes", sa.Text(), nullable=True),
        sa.Column("output_payload", sa.Text(), nullable=True),
        sa.Column("cost", sa.Float(), nullable=True),
        sa.Column("usage_json", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("error_state", sa.String(length=200), nullable=True),
        sa.Column("job_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["job.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_provider_call_provider"), "provider_call", ["provider"], unique=False)
    op.create_index(op.f("ix_provider_call_job_id"), "provider_call", ["job_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_provider_call_job_id"), table_name="provider_call")
    op.drop_index(op.f("ix_provider_call_provider"), table_name="provider_call")
    op.drop_table("provider_call")
