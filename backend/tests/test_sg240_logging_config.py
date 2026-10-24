"""SG-240 G1: the app's logging configuration, asserted in-process.

The container proof (pasted in the slice report) shows VISIBILITY in `docker
logs`; this module asserts the same properties in-process: the daily logger's
effective level is INFO after configuration, and a record it emits reaches the
app's handler exactly once.
"""

from __future__ import annotations

import io
import logging

from app.logging_config import configure_logging

DAILY_LOGGER = "app.services.reminders.daily"


def _app_handlers() -> list[logging.Handler]:
    return [
        handler
        for handler in logging.getLogger().handlers
        if getattr(handler, "_storagegenie_app_handler", False)
    ]


def test_configure_logging_sets_info_and_hands_the_daily_record_to_one_handler() -> None:
    root = logging.getLogger()
    original_level = root.level
    existing = list(root.handlers)
    try:
        configure_logging()
        configure_logging()  # idempotent: a second call must not double the handler

        daily = logging.getLogger(DAILY_LOGGER)
        assert daily.getEffectiveLevel() == logging.INFO

        handlers = _app_handlers()
        assert len(handlers) == 1
        stream = io.StringIO()
        assert isinstance(handlers[0], logging.StreamHandler)
        handlers[0].setStream(stream)

        daily.info(
            "Daily reminder pass completed as_of=2026-01-01 households_visited=0 "
            "reminders_created=0 errors=0"
        )

        output = stream.getvalue()
        assert "Daily reminder pass completed" in output
        assert output.count("Daily reminder pass completed") == 1
        assert DAILY_LOGGER in output
    finally:
        for handler in list(root.handlers):
            if handler not in existing:
                root.removeHandler(handler)
        root.setLevel(original_level)
