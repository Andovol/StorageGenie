"""SG-101 text-path gates: separate text bound + empty-content accounting ($0).

Scope: the metered TEXT turn only (the vision path is deliberately untouched).
What this file proves (`PG-EV-04`/`PG-EV-01`):
- `build_text_payload` carries the new `TEXT_MAX_TOKENS` bound while the vision
  path's `DEFAULT_MAX_TOKENS` stays byte-untouched and its `:135` pin stays green;
- `extract_text`'s post-body empty-content raise carries the received body's
  usage/cost/latency (the SG-062 mechanism) exactly like the no-choices leg, so
  a billed empty-200 (SG-099: reasoning tokens, `content` empty) can be ledgered;
- the vision path's empty-content leg stays usage-free (text path ONLY);
- `synthesize.estimate_text_cost` bounds a text turn at the new constant, so the
  per-call cap the caller compares against is no longer blind (cap binds).

No network, no key: every provider here is a `_post` stub over recorded body
shapes, or a scripted text double. The single live leg is the bounded worklog
call, never this suite.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base
from app.models.provider_call import ProviderCall
from app.services.enrich import synthesize as syn
from app.services.providers import opencode_go as go
from app.services.providers import reader as reader_mod
from app.services.providers.protocols import ProviderResult
from app.services.providers.router import BudgetExceededError, ProviderError

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"

OFF_URL = "https://world.openfoodfacts.org/api/v2/search?x=1"
OFF_AT = "2026-09-22T00:00:00+00:00"
JINA_URL = "https://eu.s.jina.ai/Jacobs+Jacobs+Cronat+Gold"
JINA_AT = "2026-09-22T00:00:00+00:00"

VISION_MAX_TOKENS = 2000
TEXT_BOUND = 8000


def _png_bytes() -> bytes:
    """A tiny real PNG: the vision path redacts (decodes) bytes before sending."""
    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "white").save(buf, format="PNG")
    return buf.getvalue()


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# G1 — separate text bound; vision constant byte-untouched
# --------------------------------------------------------------------------- #
def test_text_payload_carries_new_bound_and_vision_constant_untouched() -> None:
    """The text builder moves to `TEXT_MAX_TOKENS`; the vision constant does not."""
    assert go.DEFAULT_MAX_TOKENS == VISION_MAX_TOKENS, "vision constant byte-untouched"
    assert go.TEXT_MAX_TOKENS == TEXT_BOUND
    assert go.TEXT_MAX_TOKENS != go.DEFAULT_MAX_TOKENS

    text_payload = go.build_text_payload("some-model", "SYSTEM", "USER")
    assert text_payload["max_tokens"] == go.TEXT_MAX_TOKENS
    assert text_payload["max_tokens"] == TEXT_BOUND

    # The vision builder (`extract_items`) keeps the old bound, unchanged.
    vision_payload = go.build_chat_payload("some-model", "SYSTEM", "Zm9v")
    assert vision_payload["max_tokens"] == go.DEFAULT_MAX_TOKENS


# --------------------------------------------------------------------------- #
# G2 — empty-content raise carries the received body's accounting
# --------------------------------------------------------------------------- #
def test_text_extract_empty_content_carries_received_body_accounting() -> None:
    """SG-101: the SG-099 empty-200 leg (reasoning burn) is billed, so account it.

    Shape is the `:333` raise-legs test extended to the content leg: a 200 body
    with non-zero usage and empty `content` must raise carrying `usage`/`cost`/
    `latency_ms` so `reader._write_error_ledger` records what crossed the wire.
    """
    usage = {"prompt_tokens": 1039, "completion_tokens": 2000, "total_tokens": 3039}
    expected_cost = go.compute_cost(usage)

    class _BodyProvider(go.OpenCodeGoProvider):
        def __init__(self, body: dict[str, Any]) -> None:
            super().__init__(session_id="sg101-content-leg")
            self._body = body

        def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
            return self._body

    body = {
        "id": "x",
        "model": "deepseek-v4-flash-vision-exp",
        "choices": [
            {
                "finish_reason": "length",
                "message": {"content": "", "reasoning_content": "We need output JSON only. ..."},
            }
        ],
        "usage": usage,
    }
    provider = _BodyProvider(body)
    with pytest.raises(ProviderError) as caught:
        provider.extract_text("USER", "SYSTEM")
    exc = caught.value
    assert exc.kind == "invalid_json"
    assert exc.usage == usage, "body usage must cross the boundary"
    assert exc.cost == expected_cost, "cost is the file's own compute_cost"
    assert exc.latency_ms is not None and exc.latency_ms >= 0.0


def test_vision_empty_content_leg_stays_usage_free_text_path_only() -> None:
    """The vision path is NOT changed: its empty-content leg stays accounting-free."""
    usage = {"prompt_tokens": 754, "completion_tokens": 341, "total_tokens": 1095}

    class _BodyProvider(go.OpenCodeGoProvider):
        def __init__(self, body: dict[str, Any]) -> None:
            super().__init__(session_id="sg101-vision-content-leg")
            self._body = body

        def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
            return self._body

    provider = _BodyProvider(
        {
            "id": "x",
            "model": "m",
            "usage": usage,
            "choices": [{"message": {"content": "   "}}],
        }
    )
    with pytest.raises(ProviderError) as caught:
        provider.extract_items(_png_bytes(), "prompt")
    exc = caught.value
    assert exc.kind == "invalid_json"
    assert getattr(exc, "usage", None) is None
    assert getattr(exc, "cost", None) is None
    assert getattr(exc, "latency_ms", None) is None


# --------------------------------------------------------------------------- #
# G2 — the estimate covers the new bound; the cap comparison binds
# --------------------------------------------------------------------------- #
def test_text_estimate_covers_new_bound_old_default_understates() -> None:
    """A text-turn estimate at the new bound is strictly above the old default."""
    text = "u" * 1200
    prompt = "s" * 400
    old = syn.estimate_text_cost(text, prompt, max_tokens=go.DEFAULT_MAX_TOKENS)
    new = syn.estimate_text_cost(text, prompt)  # default must be the TEXT bound
    assert new > old, "the old DEFAULT_MAX_TOKENS understates a text-turn worst case"
    delta = (go.TEXT_MAX_TOKENS - go.DEFAULT_MAX_TOKENS) * go.OUTPUT_USD_PER_1M / 1_000_000
    assert new - old == pytest.approx(delta)


class _ScriptedTextProvider:
    """Schema-free scripted text double: records calls, no network."""

    def __init__(self) -> None:
        self.provider_id = "scripted-sg101"
        self.model_id = "scripted-sg101-1"
        self.invocations = 0

    def estimate_cost(self, payload_bytes: bytes, prompt: str) -> float:
        return 0.0

    def extract_text(
        self, text: str, prompt: str = "", *, estimated_cost: float = 0.0
    ) -> ProviderResult:
        self.invocations += 1
        answer = json.dumps(
            {
                "facts": [
                    {
                        "field": "display_name",
                        "value": "Jacobs Cronat Gold instant coffee",
                        "source_url": OFF_URL,
                        "retrieved_at": OFF_AT,
                    }
                ]
            }
        )
        return ProviderResult(
            normalized_output={"text": answer, "model": self.model_id},
            raw_payload={"scripted": True},
            request_id="req-scripted-101",
            usage={"prompt_tokens": 120, "completion_tokens": 40, "total_tokens": 160},
            cost=0.000123,
            model_id=self.model_id,
            latency_ms=4.5,
        )


@pytest.fixture
def sg101_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg101.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_cap_comparison_uses_the_new_text_bound(
    sg101_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A cap between the old and new worst cases refuses before any invocation.

    Under the old default this same cap admitted the call; under the new bound
    the caller's pre-call comparison (`synthesize.py`) refuses — the cap is no
    longer blind to the text-turn output budget.
    """
    provider = _ScriptedTextProvider()
    monkeypatch.setattr(
        reader_mod, "provider_registry", lambda: {provider.provider_id: provider}
    )
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)

    off = _load("off_hit.json")
    jina = _load("jina_hit.json")
    prompt_text, _version = syn.load_synthesis_prompt()
    user_text = syn.build_synthesis_input(
        off,
        jina,
        off_source_url=OFF_URL,
        off_retrieved_at=OFF_AT,
        jina_source_url=JINA_URL,
        jina_retrieved_at=JINA_AT,
        brand="Jacobs",
    )
    old_est = syn.estimate_text_cost(user_text, prompt_text, max_tokens=go.DEFAULT_MAX_TOKENS)
    new_est = syn.estimate_text_cost(user_text, prompt_text)
    assert old_est < new_est
    cap = (old_est + new_est) / 2

    with pytest.raises(BudgetExceededError):
        syn.synthesize(
            sg101_db,
            off,
            jina,
            off_source_url=OFF_URL,
            off_retrieved_at=OFF_AT,
            jina_source_url=JINA_URL,
            jina_retrieved_at=JINA_AT,
            brand="Jacobs",
            provider=provider,
            per_call_cap_usd=cap,
        )
    assert provider.invocations == 0, "cap must refuse before any invocation"
    assert sg101_db.query(ProviderCall).count() == 0
