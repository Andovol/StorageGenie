"""deterministic signal observations

Revision ID: 20260908_sg013_observation
Revises: 0201cf10c56c
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260908_sg013_observation"
down_revision: Union[str, None] = "0201cf10c56c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "observation",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("evidence_id", sa.String(length=36), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("value_json", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.CheckConstraint("kind IN ('ocr', 'barcode_qr', 'exif', 'phash')", name="ck_observation_kind"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_observation_evidence_id"), "observation", ["evidence_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_observation_evidence_id"), table_name="observation")
    op.drop_table("observation")
