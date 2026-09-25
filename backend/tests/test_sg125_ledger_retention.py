"""SG-125 ledger retention: month-boxed spend + purge vehicle (temp-DB only, $0).

Scope: this file exercises the REAL `app.services.providers.reader` module on a
fresh temp SQLite database. It makes no network call, reads no key and touches
no live database: the production DB is never opened. What it proves:

- `_recorded_spend` (NEW) sums the current calendar month only; the OLD behavior
  (lifetime sum) is computed beside it as `_lifetime_spend`, so the fail-then-pass
  delta is visible in one run;
- an empty household spends `0.0` and purges nothing (the empty world is named);
- `purge_old_provider_calls` deletes only `provider_call` rows older than the
  retention cutoff, returns their ids, and leaves `guardrail_event`/`audit_event`
  untouched (proved by before/after SELECTs, not by the vehicle's own return);
- re-running the month math on the purged DB is unchanged (the purge cannot move
  the monthly figure once the query is month-boxed).
"""

from __future__ import annotations

import datetime
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

# Bind an isolated root before importing app modules (same preamble convention as
# test_ai_pipeline / test_sg124). Nothing here uses the global engine.
SG125_TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-sg125-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{SG125_TEST_ROOT / 'retention.db'}"
os.environ.setdefault("STORAGE_ROOT", str(SG125_TEST_ROOT / "storage"))

from app.db import Base  # noqa: E402
from app.models.audit_event import AuditEvent  # noqa: E402
from app.models.guardrail_event import GuardrailEvent  # noqa: E402
from app.models.household import Household  # noqa: E402
from app.models.job import Job  # noqa: E402
from app.models.provider_call import ProviderCall  # noqa: E402
from app.services.providers import reader as reader_mod  # noqa: E402


@pytest.fixture
def ledger(tmp_path: Path) -> Iterator[Session]:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg125.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _household(session: Session, name: str = "Retention Household") -> str:
    row = Household(name=name)
    session.add(row)
    session.flush()
    return row.id


def _job(session: Session, household_id: str) -> Job:
    row = Job(job_type="import", state="SUCCEEDED", household_id=household_id)
    session.add(row)
    session.flush()
    return row


def _call(
    session: Session, job: Job, *, cost: float, created_at: datetime.datetime
) -> ProviderCall:
    row = ProviderCall(
        provider="scripted",
        model="scripted-model-1",
        prompt_template_version="extract-food-v4",
        cost=cost,
        job_id=job.id,
        created_at=created_at,
    )
    session.add(row)
    session.flush()
    return row


def _lifetime_spend(session: Session, household_id: str) -> float:
    """The OLD (pre-SG-125) semantics: every committed provider_call row, no month filter."""
    total = (
        session.query(func.coalesce(func.sum(ProviderCall.cost), 0.0))
        .join(Job, ProviderCall.job_id == Job.id)
        .filter(Job.household_id == household_id)
        .scalar()
    )
    return float(total or 0.0)


def _now_utc_naive() -> datetime.datetime:
    """The live clock as naive UTC, the shape `provider_call.created_at` is stored in."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def test_retention_constant_is_twelve_months() -> None:
    # UNCALIBRATED (G-A9): a year of audit trail on local disk; never auto-run.
    assert reader_mod.LEDGER_RETENTION_MONTHS == 12


def test_recorded_spend_boxes_to_current_month(ledger: Session) -> None:
    """OLD returns the lifetime total; NEW returns this-month-only (both quoted)."""
    household_id = _household(ledger)
    job = _job(ledger, household_id)

    now = _now_utc_naive()
    last_month = now - datetime.timedelta(days=40)  # >31 days back => never this month

    _call(ledger, job, cost=5.0, created_at=last_month)
    _call(ledger, job, cost=2.0, created_at=now)
    _call(ledger, job, cost=3.0, created_at=now)

    # A different household's rows must never enter this household's figure.
    other_household_id = _household(ledger, "Other Household")
    other_job = _job(ledger, other_household_id)
    _call(ledger, other_job, cost=100.0, created_at=now)
    ledger.commit()

    assert _lifetime_spend(ledger, household_id) == pytest.approx(10.0)
    assert reader_mod._recorded_spend(ledger, household_id) == pytest.approx(5.0)
    assert reader_mod._recorded_spend(ledger, other_household_id) == pytest.approx(100.0)


def test_empty_household_spends_zero_and_purges_nothing(ledger: Session) -> None:
    household_id = _household(ledger, "Empty Household")
    ledger.commit()

    assert reader_mod._recorded_spend(ledger, household_id) == pytest.approx(0.0)
    assert reader_mod.purge_old_provider_calls(ledger) == []
    assert ledger.query(ProviderCall).count() == 0


def test_purge_vehicle_deletes_only_old_rows_and_spares_non_spend_tables(
    ledger: Session,
) -> None:
    household_id = _household(ledger)
    job = _job(ledger, household_id)

    now = _now_utc_naive()
    old_marker = now - datetime.timedelta(days=400)  # ~13 months old
    recent_marker = now

    old_ids = {
        _call(ledger, job, cost=1.0, created_at=old_marker).id for _ in range(3)
    }
    recent_ids = {
        _call(ledger, job, cost=1.0, created_at=recent_marker).id for _ in range(2)
    }
    ledger.add(
        GuardrailEvent(
            household_id=household_id, kind="spend", ref_ids_json="[]", detail_json="{}"
        )
    )
    ledger.add(
        AuditEvent(
            actor="system",
            action="test",
            entity_type="job",
            entity_id=job.id,
            household_id=household_id,
        )
    )
    ledger.commit()

    lifetime_before = _lifetime_spend(ledger, household_id)
    month_before = reader_mod._recorded_spend(ledger, household_id)
    calls_before = ledger.query(ProviderCall).count()
    guardrail_before = ledger.query(GuardrailEvent).count()
    audit_before = ledger.query(AuditEvent).count()
    assert calls_before == 5
    assert lifetime_before == pytest.approx(5.0)
    assert month_before == pytest.approx(2.0)
    assert guardrail_before == 1 and audit_before == 1

    deleted = reader_mod.purge_old_provider_calls(ledger)

    assert set(deleted) == old_ids
    calls_after = ledger.query(ProviderCall).count()
    assert calls_after == 2
    assert {row.id for row in ledger.query(ProviderCall).all()} == recent_ids
    assert ledger.query(GuardrailEvent).count() == guardrail_before
    assert ledger.query(AuditEvent).count() == audit_before
    # The old rows are gone from the durable total; the monthly figure never moved.
    assert _lifetime_spend(ledger, household_id) == pytest.approx(2.0)
    assert reader_mod._recorded_spend(ledger, household_id) == pytest.approx(month_before)


def test_purge_keeps_rows_inside_the_retention_window(ledger: Session) -> None:
    """A ~11-month row is kept; a ~13-month row is deleted (strictly-older predicate)."""
    household_id = _household(ledger)
    job = _job(ledger, household_id)
    now = _now_utc_naive()
    outside = _call(ledger, job, cost=1.0, created_at=now - datetime.timedelta(days=400))
    inside = _call(ledger, job, cost=1.0, created_at=now - datetime.timedelta(days=350))
    ledger.commit()

    assert reader_mod.purge_old_provider_calls(ledger) == [outside.id]
    assert {row.id for row in ledger.query(ProviderCall).all()} == {inside.id}

