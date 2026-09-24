"""SG-111: the Asset lifecycle vocabulary, transition map and ACTIVE predicate.

One home for the six lifecycle literals (`DRAFT, PENDING_REVIEW, ACTIVE,
ARCHIVED, DISPOSED, MERGED`) and the single transition table, so no reader or
writer carries its own status string (`PG-SC-05` by rule). This module lives on
its own rather than inside `asset_service.py` because the reader services
(analytics, chat, planning, the expiry engine) and the API layer import it:
`asset_service` pulls in the write-side graph (candidates/audit/assertions), and
importing it from a reader would widen that graph for no reason. Here the only
import is the model.

Blueprint §4.3 legal flow: `DRAFT -> PENDING_REVIEW -> ACTIVE -> ARCHIVED ->
DISPOSED`, plus the reserved `ACTIVE -> MERGED` redirect target. A `MERGED`
asset whose redirect has not been written yet (SG-112) reads as the terminal
state, never a dangling pointer (`PG-SC-07`). A same-status request is a no-op,
not a transition: it reaches no new state, so the map has nothing to forbid.
"""

from __future__ import annotations

from sqlalchemy.sql.elements import ColumnElement

from app.models.asset import Asset

DRAFT = "DRAFT"
PENDING_REVIEW = "PENDING_REVIEW"
ACTIVE = "ACTIVE"
ARCHIVED = "ARCHIVED"
DISPOSED = "DISPOSED"
MERGED = "MERGED"

LIFECYCLE_STATUSES: tuple[str, ...] = (
    DRAFT,
    PENDING_REVIEW,
    ACTIVE,
    ARCHIVED,
    DISPOSED,
    MERGED,
)

# The single transition table. Terminal states (`DISPOSED`, `MERGED`) map to an
# empty set; every edge not listed here is illegal.
TRANSITIONS: dict[str, frozenset[str]] = {
    DRAFT: frozenset({PENDING_REVIEW}),
    PENDING_REVIEW: frozenset({ACTIVE}),
    ACTIVE: frozenset({ARCHIVED, MERGED}),
    ARCHIVED: frozenset({DISPOSED}),
    DISPOSED: frozenset(),
    MERGED: frozenset(),
}


class LifecycleTransitionError(ValueError):
    """An illegal Asset lifecycle transition; the API maps it to HTTP 422."""

    def __init__(self, current: str, requested: str) -> None:
        self.current = current
        self.requested = requested
        super().__init__(
            f"illegal status transition {current!r} -> {requested!r}; "
            f"legal from {current!r}: {sorted(allowed_next(current))}"
        )


def allowed_next(current: str) -> frozenset[str]:
    """The legal next statuses from `current` (empty for terminal/unknown)."""
    return TRANSITIONS.get(current, frozenset())


def validate_transition(current: str, requested: str) -> None:
    """Raise `LifecycleTransitionError` unless `current -> requested` is legal.

    A request outside the vocabulary is always illegal. A request equal to the
    current status is a no-op and is permitted (it reaches no new state).
    """
    if requested not in LIFECYCLE_STATUSES:
        raise LifecycleTransitionError(current, requested)
    if requested == current:
        return
    if requested not in TRANSITIONS.get(current, frozenset()):
        raise LifecycleTransitionError(current, requested)


def is_active(asset: Asset) -> bool:
    """The Python-side ACTIVE-only predicate (the shared reader rule)."""
    return asset.status == ACTIVE


def active_clause() -> ColumnElement[bool]:
    """The SQL-side ACTIVE-only predicate (the same shared reader rule)."""
    return Asset.status == ACTIVE
