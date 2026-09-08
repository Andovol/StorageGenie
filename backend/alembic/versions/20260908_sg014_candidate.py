"""deduplication candidates

Revision ID: 20260908_sg014_candidate
Revises: 20260908_sg013_observation
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260908_sg014_candidate"
down_revision: Union[str, None] = "20260908_sg013_observation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "candidate",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_ids_json", sa.Text(), nullable=False),
        sa.Column("proposed_fields_json", sa.Text(), nullable=False),
        sa.Column("state", sa.String(length=30), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.CheckConstraint("state IN ('proposed', 'accepted', 'edited', 'held', 'rejected')", name="ck_candidate_state"),
        sa.ForeignKeyConstraint(["job_id"], ["job.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["household_id"], ["household.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_candidate_job_id"), "candidate", ["job_id"], unique=False)
    op.create_index(op.f("ix_candidate_household_id"), "candidate", ["household_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_candidate_household_id"), table_name="candidate")
    op.drop_index(op.f("ix_candidate_job_id"), table_name="candidate")
    op.drop_table("candidate")
