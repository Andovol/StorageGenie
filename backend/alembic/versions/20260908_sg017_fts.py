"""SQLite FTS5 index for asset catalog search.

Revision ID: 20260908_sg017_fts
Revises: 20260908_sg014_candidate
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op

from app.services.fts import install_asset_fts


revision: str = "20260908_sg017_fts"
down_revision: Union[str, None] = "20260908_sg014_candidate"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    install_asset_fts(op.get_bind(), rebuild=True)


def downgrade() -> None:
    connection = op.get_bind()
    connection.exec_driver_sql("DROP TRIGGER IF EXISTS asset_fts_after_delete")
    connection.exec_driver_sql("DROP TRIGGER IF EXISTS asset_fts_after_update")
    connection.exec_driver_sql("DROP TRIGGER IF EXISTS asset_fts_after_insert")
    connection.exec_driver_sql("DROP TABLE IF EXISTS asset_fts")
    connection.exec_driver_sql("DROP VIEW IF EXISTS asset_fts_content")
