"""Planning agent package (SG-037, Phase 3 Stage 0).

The manual-trigger daily planning pass. It reuses the reader seam
(`ai_status()` consent gate, `provider_registry()` and `ProviderRouter`) and
writes pending suggestions plus guardrail rows. It executes nothing.
"""

from app.services.planning.service import (
    ALLOWED_STATUSES,
    SUGGESTION_KINDS,
    SuggestionHouseholdMismatch,
    SuggestionNotFound,
    SuggestionTransitionError,
    build_catalog,
    confirm_suggestion,
    dismiss_suggestion,
    list_suggestions,
    load_planning_prompt,
    run_planning,
)

__all__ = [
    "ALLOWED_STATUSES",
    "SUGGESTION_KINDS",
    "SuggestionHouseholdMismatch",
    "SuggestionNotFound",
    "SuggestionTransitionError",
    "build_catalog",
    "confirm_suggestion",
    "dismiss_suggestion",
    "list_suggestions",
    "load_planning_prompt",
    "run_planning",
]
