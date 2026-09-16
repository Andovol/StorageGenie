"""name-optional capture: asset.display_name becomes nullable (SG-048, S2)

Revision ID: 20260916_sg048_name_optional
Revises: 20260914_sg035_foundations
Create Date: 2026-09-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.services.fts import install_asset_fts


revision: str = "20260916_sg048_name_optional"
down_revision: Union[str, None] = "20260914_sg035_foundations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _sqlite() -> bool:
    return op.get_bind().dialect.name == "sqlite"


def _drop_fts() -> None:
    """Drop the FTS5 objects before the ``asset`` table is recreated.

    The external-content view ``asset_fts_content`` names ``asset``; SQLite
    validates every view when the batch recreate renames its temp table back,
    so the view must not exist at that moment. Mirrors the sg017 downgrade.
    """
    if not _sqlite():
        return
    connection = op.get_bind()
    connection.exec_driver_sql("DROP TRIGGER IF EXISTS asset_fts_after_delete")
    connection.exec_driver_sql("DROP TRIGGER IF EXISTS asset_fts_after_update")
    connection.exec_driver_sql("DROP TRIGGER IF EXISTS asset_fts_after_insert")
    connection.exec_driver_sql("DROP TABLE IF EXISTS asset_fts")
    connection.exec_driver_sql("DROP VIEW IF EXISTS asset_fts_content")


def _reinstall_fts() -> None:
    """Recreate + rebuild the FTS5 objects after ``asset`` is recreated.

    Recreating the table dropped the triggers and can renumber rowids; the
    rebuild re-reads the (preserved) asset rows. SQLite-only, per ADR-008.
    """
    if _sqlite():
        install_asset_fts(op.get_bind(), rebuild=True)


def upgrade() -> None:
    _drop_fts()
    with op.batch_alter_table("asset") as batch_op:
        batch_op.alter_column(
            "display_name", existing_type=sa.String(length=300), nullable=True
        )
    _reinstall_fts()


def downgrade() -> None:
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
    with op.batch_alter_table("asset") as batch_op:
        batch_op.alter_column(
            "display_name", existing_type=sa.String(length=300), nullable=False
        )
    _reinstall_fts()
