"""Compile application metadata with PostgreSQL's offline SQLAlchemy dialect.

The SQLite-only FTS5 objects in
``backend/alembic/versions/20260908_sg017_fts.py`` are excluded by rule:
SQLite FTS5 has no PostgreSQL equivalent. ADR-008 records the deliberate
FTS5-first choice and the later PostgreSQL/semantic-search divergence.
"""

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects.postgresql import dialect

from app.db import Base
from app.models import (  # noqa: F401
    Asset,
    Assertion,
    AuditEvent,
    Evidence,
    Household,
    IdempotencyKey,
    Job,
    JobStep,
    ProviderCall,
    ReviewTask,
    User,
    asset_evidence,
)
from app.services.candidates import Candidate  # noqa: F401
from app.services.observations import Observation  # noqa: F401


EXPECTED_TABLES = {
    "asset",
    "asset_evidence",
    "assertion",
    "audit_event",
    "candidate",
    "evidence",
    "household",
    "idempotency_key",
    "job",
    "job_step",
    "observation",
    "provider_call",
    "review_task",
    "user",
}


def test_all_application_tables_compile_for_postgresql() -> None:
    metadata_tables = set(Base.metadata.tables)
    assert metadata_tables == EXPECTED_TABLES
    postgres = dialect()
    ddl = {
        table_name: str(CreateTable(Base.metadata.tables[table_name]).compile(dialect=postgres))
        for table_name in sorted(EXPECTED_TABLES)
    }
    assert set(ddl) == EXPECTED_TABLES
    assert all("CREATE TABLE" in statement for statement in ddl.values())
