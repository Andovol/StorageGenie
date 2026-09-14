"""Category chat package (SG-038, Phase 3 Stage 0).

A consent-gated, grounded question/answer pass over ONE category's catalogue.
It reuses the reader seam (`ai_status()` consent gate, `provider_registry()` and
`ProviderRouter`) through the adapter's text operation, writes one
`provider_call` ledger row per completed call, and writes a `guardrail_event`
of kind `correction` ONLY when a user explicitly logs one. It executes nothing.
"""

from app.services.chat.service import (
    SUPPORTED_CATEGORIES as SUPPORTED_CATEGORIES,
    UnsupportedCategoryError as UnsupportedCategoryError,
    build_catalog as build_catalog,
    build_user_content as build_user_content,
    load_chat_prompt as load_chat_prompt,
    log_correction as log_correction,
    respond as respond,
)

__all__ = [
    "SUPPORTED_CATEGORIES",
    "UnsupportedCategoryError",
    "build_catalog",
    "build_user_content",
    "load_chat_prompt",
    "log_correction",
    "respond",
]
