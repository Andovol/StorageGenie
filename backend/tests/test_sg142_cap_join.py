"""SG-142 cap-join: `None`-job ledger rows must count toward month spend.

Scope: this file exercises the REAL `app.services.providers.reader` module on a
fresh temp SQLite database. It makes no network call, reads no key and touches
no live database: the production DB is never opened. What it proves:

- the SG-142 decided semantics: `_recorded_spend` counts `job_id IS NULL`
  `provider_call` rows (chat/planning/analytics/synthesize writers) as a
  SHARED UNATTRIBUTED POOL boxed to the current calendar month, added to the
  household's job-joined rows — the rows carry no household and are never
  attributed to one by guessing;
- the G0 fail-pre seed: one joined row (0.006700) + one `None`-job row
  (0.003700) reads 0.010400 after the fix and 0.006700 on the unmodified BASE
  reader (the red is quoted in `docs/worklogs/SG-142_verify.log`);
- the no-change case (`PG-IC-08`): a month with zero `None`-job rows reads
  byte-identical to the old join-only semantics;
- month boxing applies to the pool exactly as it does to joined rows;
- the disclosed blast radius: because the pool is unattributed, every
  household reading that month carries it (this is the decided semantics, not
  an accident — see the SG-142 report).
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

# Bind an isolated root before importing app modules (same preamble convention
# as test_sg125_ledger_retention). Nothing here uses the global engine.
SG142_TEST_ROOT = Path(tempfile.mkdtemp(prefix="storagegenie-sg142-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{SG142_TEST_ROOT / 'capjoin.db'}"
os.environ.setdefault("STORAGE_ROOT", str(SG142_TEST_ROOT / "storage"))

from app.db import Base  # noqa: E402
from app.models.household import Household  # noqa: E402
from app.models.job import Job  # noqa: E402
from app.models.provider_call import ProviderCall  # noqa: E402
from app.services.providers import reader as reader_mod  # noqa: E402

# PG-IC-08: the expected figures are stop conditions, not comments. The G0 seed
# is one joined row and one `None`-job row; the corrected reader must read their
# sum, not the joined-only figure the unmodified BASE reader returns.
JOINED_COST = 0.006700
NULL_JOB_COST = 0.003700
DECIDED_TOTAL = 0.010400


@pytest.fixture
def ledger(tmp_path: Path) -> Iterator[Session]:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg142.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _household(session: Session, name: str = "Cap-Join Household") -> str:
    row = Household(name=name)
    session.add(row)
    session.flush()
    return row.id


def _job(session: Session, household_id: str) -> Job:
    row = Job(job_type="enrich", state="COMPLETED", household_id=household_id)
    session.add(row)
    session.flush()
    return row


def _now_utc_naive() -> datetime.datetime:
    """The live clock as naive UTC, the shape `provider_call.created_at` is stored in."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def _joined_call(
    session: Session, job: Job, *, cost: float, created_at: datetime.datetime
) -> ProviderCall:
    row = ProviderCall(
        provider="scripted-joined",
        model="scripted-model-1",
        prompt_template_version="extract-food-v4",
        cost=cost,
        job_id=job.id,
        created_at=created_at,
    )
    session.add(row)
    session.flush()
    return row


def _none_job_call(
    session: Session, *, cost: float, created_at: datetime.datetime
) -> ProviderCall:
    """A ledger row exactly as the chat/planning/analytics/synthesize writers leave it."""
    row = ProviderCall(
        provider="scripted-unattributed",
        model="scripted-model-1",
        prompt_template_version="chat-v1",
        cost=cost,
        job_id=None,
        created_at=created_at,
    )
    session.add(row)
    session.flush()
    return row


def _joined_only_spend(session: Session, household_id: str) -> float:
    """The OLD semantics: month-boxed, but inner-joined through Job only."""
    total = (
        session.query(func.coalesce(func.sum(ProviderCall.cost), 0.0))
        .join(Job, ProviderCall.job_id == Job.id)
        .filter(Job.household_id == household_id)
        .filter(ProviderCall.created_at >= reader_mod._current_month_start_utc())
        .scalar()
    )
    return float(total or 0.0)


def test_null_job_rows_count_toward_the_month(ledger: Session) -> None:
    """G0 seed: the joined row AND the `None`-job row both count (fail-pre red)."""
    household_id = _household(ledger)
    job = _job(ledger, household_id)
    now = _now_utc_naive()
    _joined_call(ledger, job, cost=JOINED_COST, created_at=now)
    _none_job_call(ledger, cost=NULL_JOB_COST, created_at=now)
    ledger.commit()

    # The unmodified BASE reader returns only the joined figure; quoted so the
    # fail-pre/fail-post delta is visible in one run.
    assert _joined_only_spend(ledger, household_id) == pytest.approx(JOINED_COST)
    assert reader_mod._recorded_spend(ledger, household_id) == pytest.approx(DECIDED_TOTAL)


def test_no_change_when_month_has_no_null_job_rows(ledger: Session) -> None:
    """PG-IC-08 no-change case: a `None`-job-free month is byte-identical."""
    household_id = _household(ledger)
    job = _job(ledger, household_id)
    now = _now_utc_naive()
    _joined_call(ledger, job, cost=1.25, created_at=now)
    _joined_call(ledger, job, cost=2.75, created_at=now)
    ledger.commit()

    expected = _joined_only_spend(ledger, household_id)
    assert expected == pytest.approx(4.0)
    assert reader_mod._recorded_spend(ledger, household_id) == pytest.approx(expected)


def test_null_job_pool_is_boxed_to_the_current_month(ledger: Session) -> None:
    """The pool is month-boxed: a last-month `None`-job row never enters."""
    household_id = _household(ledger)
    job = _job(ledger, household_id)
    now = _now_utc_naive()
    last_month = now - datetime.timedelta(days=40)  # >31 days back => never this month
    _joined_call(ledger, job, cost=0.5, created_at=now)
    _none_job_call(ledger, cost=99.0, created_at=last_month)
    _none_job_call(ledger, cost=0.25, created_at=now)
    ledger.commit()

    assert reader_mod._recorded_spend(ledger, household_id) == pytest.approx(0.75)


def test_unattributed_pool_is_shared_across_households(ledger: Session) -> None:
    """Disclosed blast radius: the pool is unattributed, so every household reads it.

    The `None`-job writers store no household (`provider_call` has only
    `job_id`), and SG-142 never attributes such a row by guessing, so the pooled
    figure is fail-closed: it counts against each household reading that month.
    """
    household_a = _household(ledger, "Household A")
    household_b = _household(ledger, "Household B")
    job_a = _job(ledger, household_a)
    now = _now_utc_naive()
    _joined_call(ledger, job_a, cost=0.5, created_at=now)
    _none_job_call(ledger, cost=NULL_JOB_COST, created_at=now)
    ledger.commit()

    assert reader_mod._recorded_spend(ledger, household_a) == pytest.approx(
        0.5 + NULL_JOB_COST
    )
    # B owns no rows, yet the same unattributed month pool is visible to it.
    assert reader_mod._recorded_spend(ledger, household_b) == pytest.approx(NULL_JOB_COST)
