"""SG-240: the app's own logging configuration, applied at startup.

uvicorn applies its own ``LOGGING_CONFIG`` before the lifespan runs. That config
defines only the ``uvicorn``, ``uvicorn.error`` and ``uvicorn.access`` loggers
and no root entry, and ``dictConfig`` clears existing root handlers, so a
``basicConfig`` executed at import time is undone. Configuring from the lifespan
therefore survives uvicorn's configuration instead of racing it.

The properties this module owns (G1): the root logger is INFO, exactly one
handler is attached (no duplicate lines), and that handler writes to stderr,
which is the stream ``docker logs`` reads.
"""

from __future__ import annotations

import logging

LOG_FORMAT = "%(levelname)s:     %(name)s - %(message)s"
_HANDLER_MARKER = "_storagegenie_app_handler"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Set the root level and attach the app's one handler, idempotently."""
    root = logging.getLogger()
    root.setLevel(level)
    for handler in root.handlers:
        if getattr(handler, _HANDLER_MARKER, False):
            handler.setLevel(level)
            return root
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    setattr(handler, _HANDLER_MARKER, True)
    root.addHandler(handler)
    return root
