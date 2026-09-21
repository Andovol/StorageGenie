"""Compile application metadata with PostgreSQL's offline SQLAlchemy dialect.

The SQLite-only FTS5 objects in
``backend/alembic/versions/20260908_sg017_fts.py`` are excluded by rule:
SQLite FTS5 has no PostgreSQL equivalent. ADR-008 records the deliberate
FTS5-first choice and the later PostgreSQL/semantic-search divergence.

The table set is derived from the REAL ``Base.metadata`` the app registers via
its composition root; this test never re-lists table names, so a table-adding
slice cannot trip it.
"""

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects.postgresql import dialect

import app.main  # noqa: F401

from app.db import Base


def test_all_application_tables_compile_for_postgresql() -> None:
    metadata_tables = Base.metadata.tables
    assert metadata_tables, "no tables registered — the app import did not run"
    postgres = dialect()
    ddl = {
        table_name: str(CreateTable(table).compile(dialect=postgres))
        for table_name, table in sorted(metadata_tables.items())
    }
    assert set(ddl) == set(metadata_tables)
    assert all("CREATE TABLE" in statement for statement in ddl.values())
