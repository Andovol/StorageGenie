"""data foundations: source attribution, planning suggestions, guardrail log (SG-035, Phase 3 S2/S3)

Revision ID: 20260914_sg035_foundations
Revises: 20260912_sg025_provider_call
Create Date: 2026-09-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260914_sg035_foundations"
down_revision: Union[str, None] = "20260912_sg025_provider_call"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "source_attribution",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("assertion_id", sa.String(length=36), nullable=True),
        sa.Column("field_path", sa.String(length=200), nullable=False),
        sa.Column("uri", sa.Text(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["assertion_id"], ["assertion.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_source_attribution_household_id"), "source_attribution", ["household_id"], unique=False
    )
    op.create_index(op.f("ix_source_attribution_asset_id"), "source_attribution", ["asset_id"], unique=False)
    op.create_index(
        op.f("ix_source_attribution_assertion_id"), "source_attribution", ["assertion_id"], unique=False
    )

    op.create_table(
        "planning_suggestion",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
        sa.Column("kind", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("body_json", sa.Text(), nullable=False),
        sa.Column("backing_refs_json", sa.Text(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_planning_suggestion_household_id"),
        "planning_suggestion",
        ["household_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_planning_suggestion_status"), "planning_suggestion", ["status"], unique=False
    )

    op.create_table(
        "guardrail_event",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("ref_ids_json", sa.Text(), nullable=False),
        sa.Column("detail_json", sa.Text(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_guardrail_event_household_id"), "guardrail_event", ["household_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_guardrail_event_household_id"), table_name="guardrail_event")
    op.drop_table("guardrail_event")

    op.drop_index(op.f("ix_planning_suggestion_status"), table_name="planning_suggestion")
    op.drop_index(op.f("ix_planning_suggestion_household_id"), table_name="planning_suggestion")
    op.drop_table("planning_suggestion")

    op.drop_index(op.f("ix_source_attribution_assertion_id"), table_name="source_attribution")
    op.drop_index(op.f("ix_source_attribution_asset_id"), table_name="source_attribution")
    op.drop_index(op.f("ix_source_attribution_household_id"), table_name="source_attribution")
    op.drop_table("source_attribution")
