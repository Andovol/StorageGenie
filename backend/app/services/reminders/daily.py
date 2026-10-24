"""SG-235: the in-app daily caller for expiry reminders.

One pass visits every household and writes through the single production
writer ``app.services.reminders.service.record_due`` for the current UTC day.
The loop runs a pass immediately and then once every ``DAILY_INTERVAL_SECONDS``.
Missed days are never walked: each pass computes its day from the live clock.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from sqlalchemy.orm import Session

from app.models.household import Household
from app.services.reminders.service import record_due, today_utc

logger = logging.getLogger(__name__)

DAILY_INTERVAL_SECONDS = 86400.0


class SessionFactory(Protocol):
    def __call__(self) -> Session: ...


@dataclass(frozen=True)
class HouseholdPassError:
    household_id: str
    error: str


@dataclass(frozen=True)
class DailyPassResult:
    as_of_day: date
    households_visited: int
    reminders_created: int
    errors: tuple[HouseholdPassError, ...] = ()


def run_daily_pass(
    session_factory: SessionFactory, *, as_of_day: date | None = None
) -> DailyPassResult:
    """Run one pass over every household for one day and close its session."""
    day = as_of_day if as_of_day is not None else today_utc()
    visited = 0
    created = 0
    errors: list[HouseholdPassError] = []
    session = session_factory()
    try:
        household_ids = [
            household_id
            for (household_id,) in session.query(Household.id).order_by(Household.id).all()
        ]
        for household_id in household_ids:
            visited += 1
            try:
                created += len(record_due(session, household_id, day))
            except Exception as exc:
                session.rollback()
                message = f"{type(exc).__name__}: {exc}"
                errors.append(HouseholdPassError(household_id=household_id, error=message))
                logger.exception(
                    "Daily reminder pass failed for household %s on %s",
                    household_id,
                    day.isoformat(),
                )
    finally:
        session.close()
    return DailyPassResult(
        as_of_day=day,
        households_visited=visited,
        reminders_created=created,
        errors=tuple(errors),
    )


async def run_daily_forever(
    session_factory: SessionFactory,
    *,
    interval_seconds: float = DAILY_INTERVAL_SECONDS,
    clock: Callable[[], date] | None = None,
    sleep: Callable[[float], Awaitable[None]] | None = None,
) -> None:
    """Run one pass at once, then once per interval until cancelled."""
    day_clock = clock if clock is not None else today_utc
    sleep_fn = sleep if sleep is not None else asyncio.sleep
    while True:
        day = day_clock()
        try:
            await asyncio.to_thread(run_daily_pass, session_factory, as_of_day=day)
        except Exception:
            logger.exception("Daily reminder loop pass failed on %s", day.isoformat())
        await sleep_fn(interval_seconds)
