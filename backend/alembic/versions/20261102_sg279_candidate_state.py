"""widen candidate state constraint for split and merge (SG-279)

Revision ID: 20261102_sg279_candidate_state
Revises: 20261023_sg233_reminder
Create Date: 2026-11-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261102_sg279_candidate_state"
down_revision: Union[str, None] = "20261023_sg233_reminder"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OLD_STATES = "state IN ('proposed', 'accepted', 'edited', 'held', 'rejected')"
NEW_STATES = "state IN ('proposed', 'accepted', 'edited', 'held', 'rejected', 'split', 'merged')"


def _offline() -> bool:
    return op.get_context().as_sql


def _candidate_table(check_sql: str) -> sa.Table:
    """The ``candidate`` table as it exists on disk when this revision runs.

    SQLite batch mode recreates the table, so it needs the full existing
    schema; offline there is no live connection to reflect it from, hence this
    ``copy_from`` object. Mirrors the table created in
    ``20260908_sg014_candidate.py:21-34`` (no later revision alters
    ``candidate``): columns, the two outgoing CASCADE FKs, the primary key, the
    two ``(CURRENT_TIMESTAMP)`` server defaults, and the two indexes (recreated
    by the batch as well).
    """
    table = sa.Table(
        "candidate",
        sa.MetaData(),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_ids_json", sa.Text(), nullable=False),
        sa.Column("proposed_fields_json", sa.Text(), nullable=False),
        sa.Column("state", sa.String(length=30), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
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
        sa.CheckConstraint(check_sql, name="ck_candidate_state"),
        sa.ForeignKeyConstraint(["job_id"], ["job.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["household_id"], ["household.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    sa.Index("ix_candidate_job_id", table.c.job_id)
    sa.Index("ix_candidate_household_id", table.c.household_id)
    return table


def upgrade() -> None:
    with op.batch_alter_table(
        "candidate", copy_from=_candidate_table(OLD_STATES), recreate="always"
    ) as batch_op:
        batch_op.drop_constraint("ck_candidate_state", type_="check")
        batch_op.create_check_constraint("ck_candidate_state", NEW_STATES)


def downgrade() -> None:
    if not _offline():
        connection = op.get_bind()
        blocking = connection.execute(
            sa.text("SELECT id, state FROM candidate WHERE state IN ('split', 'merged') LIMIT 1")
        ).first()
        if blocking is not None:
            raise RuntimeError(
                "cannot restore five-state ck_candidate_state: candidate "
                f"{blocking[0]} is in state {blocking[1]!r}; "
                "resolve or delete it explicitly -- no silent data drop"
            )
    with op.batch_alter_table(
        "candidate", copy_from=_candidate_table(NEW_STATES), recreate="always"
    ) as batch_op:
        batch_op.drop_constraint("ck_candidate_state", type_="check")
        batch_op.create_check_constraint("ck_candidate_state", OLD_STATES)
