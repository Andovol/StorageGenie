"""SQLite FTS5 support for the asset catalog.

The FTS table uses an external-content projection because ``asset.id`` is a
text primary key while SQLite's external-content row mapping is integer-based.
The projection exposes the asset rowid and the three indexed-table columns
without adding a second source of asset data.
"""

from __future__ import annotations

import re

from sqlalchemy import Connection, text


FTS_TABLE = "asset_fts"


def sanitize_fts_query(value: str) -> str:
    """Quote every whitespace-delimited input token as an FTS5 literal.

    FTS5 has no bind parameter for MATCH syntax itself. Quoting each token and
    doubling embedded quotes makes operators, wildcards, and quote fragments
    ordinary input while retaining implicit AND semantics for multi-token
    searches.
    """

    parts = [part for part in value.split() if re.search(r"\w", part, re.UNICODE)]
    if not parts:
        return '""'
    return " ".join('"' + part.replace('"', '""') + '"' for part in parts)


def ddl_statements() -> tuple[str, ...]:
    """Return the FTS DDL statements in creation order.

    Exposed separately from :func:`_ddl` so the Alembic revision can render the
    same statements through ``op.execute`` in offline (``--sql``) mode, where
    ``op.get_bind()`` is a ``MockConnection`` without ``exec_driver_sql``. The
    online path keeps emitting the identical strings through
    ``exec_driver_sql``.
    """

    return (
        """
        CREATE VIEW IF NOT EXISTS asset_fts_content AS
        SELECT rowid AS rowid, id AS asset_id, display_name, household_id
        FROM asset
        """,
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts USING fts5(
            asset_id UNINDEXED,
            display_name,
            household_id,
            content='asset_fts_content',
            content_rowid='rowid'
        )
        """,
        """
        CREATE TRIGGER IF NOT EXISTS asset_fts_after_insert
        AFTER INSERT ON asset
        BEGIN
            INSERT INTO asset_fts(rowid, asset_id, display_name, household_id)
            VALUES (new.rowid, new.id, new.display_name, new.household_id);
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS asset_fts_after_update
        AFTER UPDATE OF id, display_name, household_id ON asset
        BEGIN
            INSERT INTO asset_fts(asset_fts, rowid, asset_id, display_name, household_id)
            VALUES ('delete', old.rowid, old.id, old.display_name, old.household_id);
            INSERT INTO asset_fts(rowid, asset_id, display_name, household_id)
            VALUES (new.rowid, new.id, new.display_name, new.household_id);
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS asset_fts_after_delete
        AFTER DELETE ON asset
        BEGIN
            INSERT INTO asset_fts(asset_fts, rowid, asset_id, display_name, household_id)
            VALUES ('delete', old.rowid, old.id, old.display_name, old.household_id);
        END
        """,
    )


def drop_statements() -> tuple[str, ...]:
    """Return the FTS teardown statements in dependency order.

    Exposed for the same reason as :func:`ddl_statements`: a revision can
    render the drops through ``op.execute`` in offline (``--sql``) mode, where
    ``op.get_bind()`` has no ``exec_driver_sql``. Triggers go before the table;
    the external-content view names ``asset`` and must be dropped before any
    batch recreate of that table.
    """

    return (
        "DROP TRIGGER IF EXISTS asset_fts_after_delete",
        "DROP TRIGGER IF EXISTS asset_fts_after_update",
        "DROP TRIGGER IF EXISTS asset_fts_after_insert",
        "DROP TABLE IF EXISTS asset_fts",
        "DROP VIEW IF EXISTS asset_fts_content",
    )


def _ddl(connection: Connection) -> None:
    for statement in ddl_statements():
        connection.exec_driver_sql(statement)


def rebuild_asset_fts(connection: Connection) -> None:
    """Rebuild the asset FTS index from its external content source."""

    connection.execute(text("INSERT INTO asset_fts(asset_fts) VALUES ('delete-all')"))
    connection.execute(text("INSERT INTO asset_fts(asset_fts) VALUES ('rebuild')"))


def install_asset_fts(connection: Connection, *, rebuild: bool = False) -> None:
    """Create the SQLite FTS objects and optionally backfill them.

    The route uses this only for legacy/test SQLite databases created through
    ``Base.metadata.create_all``; deployed databases receive the same objects
    through the Alembic revision.
    """

    if connection.dialect.name != "sqlite":
        raise RuntimeError("asset FTS5 is a SQLite-only index")
    _ddl(connection)
    if rebuild:
        rebuild_asset_fts(connection)


def ensure_asset_fts(connection: Connection) -> None:
    """Bootstrap FTS objects for an un-migrated local SQLite test database."""

    exists = connection.execute(
        text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'asset_fts'")
    ).first()
    if exists is None:
        install_asset_fts(connection, rebuild=True)
        connection.commit()
