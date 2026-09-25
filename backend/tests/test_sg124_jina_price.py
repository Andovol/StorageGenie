"""SG-124 Jina Search price foundation (offline, $0, no served wiring).

Scope: this file exercises the REAL `app.services.enrich.jina` module — the
rate constant, the pure estimator and the module's import surface. It makes no
network call, reads no key and touches no served path (endpoint, snapshot
model/writer, provider_call writer, caps). The vendor figure is proven from the
committed constant, and the estimator is proven by hand-computed arithmetic
(never by its own docstring).

What this file proves:
- the rate constants carry the sourced figure (10,000 tokens/request, $0.05 per
  1M tokens);
- `estimate_jina_search_cost` matches hand-computed USD for the vendor minimum
  and for a larger caller-supplied token bound;
- the estimator refuses a negative token count by name (seen-to-fail), so an
  unset/unknown count can never read as free;
- the estimator is pure source (no clock, no network, no key, no import) and
  the module adds no served-path import.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from app.services.enrich import jina as jina_mod

JINA_SOURCE = Path(jina_mod.__file__)


def test_rate_constants_carry_the_sourced_figure() -> None:
    # Vendor: Search API bills 10,000 tokens/request (starting from); the base
    # top-up pack is 1B tokens for $50.00 USD -> $0.05/1M.
    assert jina_mod.JINA_SEARCH_TOKENS_PER_REQUEST == 10_000
    assert jina_mod.JINA_TOKEN_USD_PER_1M == 0.05


def test_estimator_matches_hand_computed_usd() -> None:
    # Hand-computed: 10,000 tokens x $0.05 / 1,000,000 tokens = $0.0005.
    assert jina_mod.estimate_jina_search_cost() == pytest.approx(0.0005)
    assert jina_mod.estimate_jina_search_cost(10_000) == pytest.approx(0.0005)
    # A larger caller-supplied bound scales linearly: 20,000 -> $0.001.
    assert jina_mod.estimate_jina_search_cost(20_000) == pytest.approx(0.001)
    # Zero tokens cost zero, not an error.
    assert jina_mod.estimate_jina_search_cost(0) == pytest.approx(0.0)


def test_estimator_refuses_negative_tokens_seen_to_fail() -> None:
    with pytest.raises(ValueError) as excinfo:
        jina_mod.estimate_jina_search_cost(-1)
    assert "negative_token_count" in str(excinfo.value)


def test_estimator_is_pure_source_without_served_symbols() -> None:
    source = inspect.getsource(jina_mod.estimate_jina_search_cost)
    for forbidden in ("httpx", "settings", "Session", "ProviderCall", "import "):
        assert forbidden not in source, forbidden
    assert "JINA_SEARCH_TOKENS_PER_REQUEST" in source
    assert "JINA_TOKEN_USD_PER_1M" in source


def test_module_adds_no_served_path_import() -> None:
    tree = ast.parse(JINA_SOURCE.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    served_prefixes = ("app.api", "app.models", "app.services.providers", "app.db")
    offenders = sorted(name for name in imported if name.startswith(served_prefixes))
    assert offenders == []
    app_imports = {name for name in imported if name.startswith("app.")}
    assert app_imports <= {
        "app.config",
        "app.services.enrich",
        "app.services.enrich.client",
    }
