"""Config-driven provider routing (ADR-004).

Routing is configuration, never quality-ranked: the configured provider id
is used, and the fallback id fires on retryable errors ONLY. A per-job cost
budget refuses BEFORE any provider call. No real SDK, key, or network here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ProviderError(Exception):
    """Provider failure carrying a machine-readable error kind."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind


class ProviderNotFoundError(LookupError):
    """Raised when a configured provider id has no registered implementation."""


class BudgetExceededError(RuntimeError):
    """Raised when estimated cost exceeds the per-job budget (pre-call)."""


@dataclass(frozen=True)
class RouterConfig:
    provider_id: str
    fallback_id: str | None
    json_strict: bool
    cost_budget: float
    retryable_errors: frozenset[str]


class ProviderRouter:
    """Dispatch operations to the configured provider with fallback."""

    def __init__(self, config: RouterConfig, registry: dict[str, Any]) -> None:
        self.config = config
        self.registry = registry

    def resolve(self, provider_id: str) -> Any:
        try:
            return self.registry[provider_id]
        except KeyError as exc:
            raise ProviderNotFoundError(f"unknown provider: {provider_id}") from exc

    def execute(self, operation: str, *args: Any, estimated_cost: float = 0.0, **kwargs: Any) -> Any:
        """Run `operation` on the configured provider.

        Budget is enforced BEFORE any call: exceeding it raises
        BudgetExceededError with zero provider invocations. On ProviderError
        whose kind is in the retryable set (and a fallback is configured),
        the fallback provider is tried once. Non-retryable errors surface
        with no fallback.
        """
        if estimated_cost > self.config.cost_budget:
            raise BudgetExceededError(
                f"estimated cost {estimated_cost} exceeds budget {self.config.cost_budget}"
            )
        primary = self.resolve(self.config.provider_id)
        try:
            return getattr(primary, operation)(*args, **kwargs)
        except ProviderError as exc:
            if self.config.fallback_id is not None and exc.kind in self.config.retryable_errors:
                fallback = self.resolve(self.config.fallback_id)
                return getattr(fallback, operation)(*args, **kwargs)
            raise
