"""SG-056 provider conformance rail: the SG-027 vision surface, enforced.

Every vision provider implementation in the tree must accept the one surface
the reader calls: `extract_items(image_bytes, prompt, *, estimated_cost=...)`.
This guard exists because the LIVE DEFECT of 2026-09-17 was exactly a signature
drift that no test covered: `FakeProvider.extract_items` and the
`VisionExtractionProvider` protocol kept the SG-025 one-argument shape while the
reader (`reader.py:309`), `ScriptedProvider`, `OpenCodeGoProvider` and every
test double used the three-argument shape. Every default-config (`fake`) import
crashed with `TypeError: FakeProvider.extract_items() takes 2 positional
arguments but 3 were given` while the suite stayed green — the fake was never
exercised through the router.

No network, no key, no DB, no provider call (PG-EV-05). `OpenCodeGoProvider` is
checked at signature level only: no instance is constructed, nothing is sent.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

import pytest

from app.services.providers import opencode_go as go_mod
from app.services.providers.fake import FakeProvider, ScriptedProvider
from app.services.providers.protocols import ProviderResult, VisionExtractionProvider
from app.services.providers.router import ProviderError, ProviderRouter, RouterConfig

VISION_MODES = ("valid", "invalid_json_once", "needs_evidence", "outage_retryable")
SCRIPTED_PAYLOAD = {"items": [], "unknowns": [], "needs_evidence": False}


def _assert_vision_surface(func: Callable[..., Any], label: str) -> None:
    """The exact SG-027 surface: (image_bytes, prompt, *, estimated_cost=0.0)."""
    params = list(inspect.signature(func).parameters.values())
    if params and params[0].name == "self":
        params = params[1:]
    names = [p.name for p in params]
    assert names[:2] == ["image_bytes", "prompt"], f"{label} positional shape drifted: {names}"
    assert all(p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD for p in params[:2]), (
        f"{label} first two parameters must be positional-or-keyword: {names}"
    )
    assert "estimated_cost" in names, f"{label} accepts no estimated_cost: {names}"
    cost = next(p for p in params if p.name == "estimated_cost")
    assert cost.kind is inspect.Parameter.KEYWORD_ONLY, f"{label} estimated_cost must be keyword-only"
    assert cost.default == 0.0, f"{label} estimated_cost default drifted: {cost.default!r}"


def _router(provider: Any) -> ProviderRouter:
    return ProviderRouter(
        config=RouterConfig(
            provider_id=provider.provider_id,
            fallback_id=None,
            json_strict=True,
            cost_budget=10.0,
            retryable_errors=frozenset({"outage"}),
        ),
        registry={provider.provider_id: provider},
    )


def test_protocol_declares_the_3arg_surface() -> None:
    """The protocol is the stale contract this slice fixes; it must carry the surface."""
    _assert_vision_surface(VisionExtractionProvider.extract_items, "VisionExtractionProvider")


@pytest.mark.parametrize("mode", VISION_MODES)
def test_fake_provider_accepts_3arg_surface_through_router(mode: str) -> None:
    """Every fake mode survives the reader's exact call shape, through the router.

    `router.execute` is the real write path (`reader.py:309`); the provider is
    never called directly here, so this is the passthrough under test. A
    one-argument `FakeProvider` fails this with the live TypeError.
    """
    fake = FakeProvider(mode=mode, provider_id=f"fake-{mode}")
    router = _router(fake)

    if mode in ("invalid_json_once", "outage_retryable"):
        with pytest.raises(ProviderError):
            router.execute("extract_items", b"img-bytes", "prompt", estimated_cost=0.0)
        return

    result = router.execute("extract_items", b"img-bytes", "prompt", estimated_cost=0.0)
    assert isinstance(result, ProviderResult)
    if mode == "needs_evidence":
        assert result.normalized_output["needs_evidence"] is True
    else:
        source = result.normalized_output["items"][0]["source"]
        assert source == b"img-bytes", "payload must key off the bytes it is handed"


def test_fake_provider_signature_accepts_keyword_estimated_cost() -> None:
    """Direct surface for a reader-less caller (the router strips the kwarg)."""
    _assert_vision_surface(FakeProvider.extract_items, "FakeProvider")


def test_scripted_provider_accepts_3arg_surface() -> None:
    """The schema-valid double must keep the same surface, called directly."""
    provider = ScriptedProvider(provider_id="scripted-conformance", payload=SCRIPTED_PAYLOAD)
    result = provider.extract_items(b"scripted-bytes", "scripted-prompt", estimated_cost=0.0)
    assert isinstance(result, ProviderResult)
    assert provider.images == [b"scripted-bytes"]
    assert provider.prompts == ["scripted-prompt"]


def test_opencode_go_signature_only_no_network() -> None:
    """Signature level only: no instance constructed, no key, no call, no network."""
    _assert_vision_surface(go_mod.OpenCodeGoProvider.extract_items, "OpenCodeGoProvider")


def test_planning_service_is_a_docstring_mention_not_an_implementation() -> None:
    """`planning/service.py:4` names the operation in prose; it defines nothing."""
    from app.services.planning import service as planning_service

    assert planning_service.PLANNING_OPERATION == "extract_items"
    assert not hasattr(planning_service, "extract_items")
