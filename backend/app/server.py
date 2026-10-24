"""SG-235: served entrypoint — the app plus its daily reminder lifespan.

``uvicorn app.server:app`` serves the same FastAPI object as ``app.main`` so
every route, middleware and static response is unchanged. The lifespan starts
exactly one daily reminder loop and cancels it on shutdown with a bounded wait.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.db import SessionLocal
from app.main import app
from app.services.reminders.daily import run_daily_forever

logger = logging.getLogger(__name__)

SHUTDOWN_TIMEOUT_SECONDS = 5.0


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(run_daily_forever(SessionLocal))
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError, asyncio.TimeoutError):
            await asyncio.wait_for(task, timeout=SHUTDOWN_TIMEOUT_SECONDS)


app.router.lifespan_context = lifespan
