"""SQLite FTS5 index for asset catalog search.

Revision ID: 20260908_sg017_fts
Revises: 20260908_sg014_candidate
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op

from app.services.fts import ddl_statements, drop_statements, install_asset_fts


revision: str = "20260908_sg017_fts"
down_revision: Union[str, None] = "20260908_sg014_candidate"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().as_sql:
        # Offline (``--sql``) mode binds a MockConnection that has no
        # ``exec_driver_sql``; render the DDL through Alembic instead. The
        # rebuild needs live rows and stays online-only.
        for statement in ddl_statements():
            op.execute(statement)
        return
    install_asset_fts(op.get_bind(), rebuild=True)


def downgrade() -> None:
    if op.get_context().as_sql:
        # Offline (``--sql``) mode: render the drops through Alembic (the
        # MockConnection has no ``exec_driver_sql``), mirroring upgrade().
        for statement in drop_statements():
            op.execute(statement)
        return
    connection = op.get_bind()
    for statement in drop_statements():
        connection.exec_driver_sql(statement)
