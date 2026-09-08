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


def _ddl(connection: Connection) -> None:
    connection.exec_driver_sql(
        """
        CREATE VIEW IF NOT EXISTS asset_fts_content AS
        SELECT rowid AS rowid, id AS asset_id, display_name, household_id
        FROM asset
        """
    )
    connection.exec_driver_sql(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts USING fts5(
            asset_id UNINDEXED,
            display_name,
            household_id,
            content='asset_fts_content',
            content_rowid='rowid'
        )
        """
    )
    connection.exec_driver_sql(
        """
        CREATE TRIGGER IF NOT EXISTS asset_fts_after_insert
        AFTER INSERT ON asset
        BEGIN
            INSERT INTO asset_fts(rowid, asset_id, display_name, household_id)
            VALUES (new.rowid, new.id, new.display_name, new.household_id);
        END
        """
    )
    connection.exec_driver_sql(
        """
        CREATE TRIGGER IF NOT EXISTS asset_fts_after_update
        AFTER UPDATE OF id, display_name, household_id ON asset
        BEGIN
            INSERT INTO asset_fts(asset_fts, rowid, asset_id, display_name, household_id)
            VALUES ('delete', old.rowid, old.id, old.display_name, old.household_id);
            INSERT INTO asset_fts(rowid, asset_id, display_name, household_id)
            VALUES (new.rowid, new.id, new.display_name, new.household_id);
        END
        """
    )
    connection.exec_driver_sql(
        """
        CREATE TRIGGER IF NOT EXISTS asset_fts_after_delete
        AFTER DELETE ON asset
        BEGIN
            INSERT INTO asset_fts(asset_fts, rowid, asset_id, display_name, household_id)
            VALUES ('delete', old.rowid, old.id, old.display_name, old.household_id);
        END
        """
    )


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
