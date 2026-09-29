"""name-optional capture: asset.display_name becomes nullable (SG-048, S2)

Revision ID: 20260916_sg048_name_optional
Revises: 20260914_sg035_foundations
Create Date: 2026-09-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.services.fts import ddl_statements, drop_statements, install_asset_fts


revision: str = "20260916_sg048_name_optional"
down_revision: Union[str, None] = "20260914_sg035_foundations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _sqlite() -> bool:
    return op.get_bind().dialect.name == "sqlite"


def _offline() -> bool:
    return op.get_context().as_sql


def _exec(statement: str) -> None:
    """Run a raw statement online, render it through Alembic offline.

    In ``--sql`` mode ``op.get_bind()`` is a ``MockConnection`` with no
    ``exec_driver_sql``; ``op.execute`` renders the DDL instead. The online
    branch keeps the exact API the pre-fix code used.
    """
    if _offline():
        op.execute(statement)
    else:
        op.get_bind().exec_driver_sql(statement)


def _asset_table(*, display_name_nullable: bool) -> sa.Table:
    """The ``asset`` table as it exists on disk when this revision runs.

    SQLite batch mode recreates the table, so it needs the full existing
    schema; offline there is no live connection to reflect it from, hence this
    ``copy_from`` object. Mirrors the table created in
    ``0201cf10c56c_001_core_foundation.py`` (no later pre-sg048 revision alters
    ``asset``): columns, the ``household_id`` cascade FK, the primary key, the
    ``(CURRENT_TIMESTAMP)`` server defaults, and ``ix_asset_household_id``
    (recreated by the batch as well).
    """
    table = sa.Table(
        "asset",
        sa.MetaData(),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("household_id", sa.String(length=36), nullable=False),
        sa.Column("display_name", sa.String(length=300), nullable=display_name_nullable),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("condition", sa.String(length=50), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
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
    sa.Index("ix_asset_household_id", table.c.household_id)
    return table


def _drop_fts() -> None:
    """Drop the FTS5 objects before the ``asset`` table is recreated.

    The external-content view ``asset_fts_content`` names ``asset``; SQLite
    validates every view when the batch recreate renames its temp table back,
    so the view must not exist at that moment. Mirrors the sg017 downgrade.
    """
    if not _sqlite():
        return
    for statement in drop_statements():
        _exec(statement)


def _reinstall_fts() -> None:
    """Recreate + rebuild the FTS5 objects after ``asset`` is recreated.

    Recreating the table dropped the triggers and can renumber rowids; the
    rebuild re-reads the (preserved) asset rows. SQLite-only, per ADR-008.
    The rebuild needs live rows, so it stays online-only; offline the objects
    are recreated through rendered DDL.
    """
    if not _sqlite():
        return
    if _offline():
        for statement in ddl_statements():
            op.execute(statement)
        return
    install_asset_fts(op.get_bind(), rebuild=True)


def upgrade() -> None:
    _drop_fts()
    with op.batch_alter_table(
        "asset", copy_from=_asset_table(display_name_nullable=False)
    ) as batch_op:
        batch_op.alter_column(
            "display_name", existing_type=sa.String(length=300), nullable=True
        )
    _reinstall_fts()


def downgrade() -> None:
    if not _offline():
        connection = op.get_bind()
        nameless = connection.execute(
            sa.text("SELECT 1 FROM asset WHERE display_name IS NULL LIMIT 1")
        ).first()
        if nameless is not None:
            raise RuntimeError(
                "cannot restore NOT NULL on asset.display_name: a nameless row exists; "
                "resolve or delete it explicitly -- no silent data drop"
            )
    _drop_fts()
    with op.batch_alter_table(
        "asset", copy_from=_asset_table(display_name_nullable=True)
    ) as batch_op:
        batch_op.alter_column(
            "display_name", existing_type=sa.String(length=300), nullable=False
        )
    _reinstall_fts()
