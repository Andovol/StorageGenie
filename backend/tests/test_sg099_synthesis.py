"""SG-099 enrichment synthesis prompt + non-catalogue caller (offline, $0).

Scope: this file drives the REAL frozen prompt and the REAL caller
(`app.services.enrich.synthesize`) through the ONE reader injection seam
(`app.services.providers.reader.provider_registry`) with a scripted text
provider, so no key crosses a wire and no metered call is made. The single live
leg is the bounded smoke recorded in the worklog, not this suite.

What this file proves (`PG-SC-12`: no re-implemented stand-in):
- the frozen prompt loads by version from its file, and the file on disk is the
  loader's source;
- consent-off refuses by name with ZERO invocations (`reader.ai_status`);
- an over-cap estimate refuses BEFORE any call;
- the EXACT user turn + system prompt that cross into `extract_text` are the
  ones the real builder/prompt produce (`PG-EV-04`), carrying fixture-derived
  OFF+Jina text and their attribution slots;
- every returned fact carries source URL + retrieval date, and a fact missing
  attribution is refused (seen-to-fail);
- a brand-absent input never yields a brand, and an invented brand is refused
  (seen-to-fail, `PG-SC-07`);
- the caller reaches `extract_text` directly, never the catalogue-bound
  `chat.service.respond`, and writes exactly one `ProviderCall` ledger row.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base
from app.models.provider_call import ProviderCall
from app.services.enrich import synthesize as syn
from app.services.providers import reader as reader_mod
from app.services.providers.protocols import ProviderResult
from app.services.providers.router import BudgetExceededError

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"

OFF_URL = "https://world.openfoodfacts.org/api/v2/search?x=1"
OFF_AT = "2026-09-22T00:00:00+00:00"
JINA_URL = "https://eu.s.jina.ai/Jacobs+Jacobs+Cronat+Gold"
JINA_AT = "2026-09-22T00:00:00+00:00"


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _brand_absent_off() -> dict[str, Any]:
    """Derive a brand-absent OFF input from the committed hit fixture.

    No committed fixture is brand-absent, so the input is the committed
    `off_hit.json` with the `brands` key removed (a deterministic transform,
    never a hand-authored blob — `PG-EV-07`). Reported in the worklog.
    """
    payload = _load("off_hit.json")
    for product in payload.get("products", []):
        product.pop("brands", None)
    return payload


def _answer(*, brand: str | None = "Jacobs", missing: str | None = None) -> str:
    """A provider answer in the frozen shape; `missing` drops one attribution key."""
    facts = [
        {
            "field": "display_name",
            "value": "Jacobs Cronat Gold instant coffee",
            "source_url": OFF_URL,
            "retrieved_at": OFF_AT,
        },
        {
            "field": "ingredients",
            "value": "Coffee",
            "source_url": OFF_URL,
            "retrieved_at": OFF_AT,
        },
        {
            "field": "packaging",
            "value": "Jar",
            "source_url": JINA_URL,
            "retrieved_at": JINA_AT,
        },
    ]
    if brand is not None:
        facts.insert(
            1,
            {
                "field": "brand",
                "value": brand,
                "source_url": OFF_URL,
                "retrieved_at": OFF_AT,
            },
        )
    if missing is not None:
        facts[0].pop(missing, None)
    return json.dumps({"facts": facts})


class ScriptedSynthesisProvider:
    """Schema-free scripted text double: records calls, no network."""

    def __init__(
        self,
        answer: str,
        *,
        provider_id: str = "scripted-synthesis",
        model_id: str = "scripted-synthesis-1",
        estimate: float = 0.0,
    ) -> None:
        self.provider_id = provider_id
        self.model_id = model_id
        self.answer = answer
        self.estimate = estimate
        self.invocations = 0
        self.texts: list[str] = []
        self.prompts: list[str] = []
        self.estimated_costs: list[float] = []

    def estimate_cost(self, payload_bytes: bytes, prompt: str) -> float:
        return self.estimate

    def extract_text(
        self, text: str, prompt: str = "", *, estimated_cost: float = 0.0
    ) -> ProviderResult:
        self.invocations += 1
        self.texts.append(text)
        self.prompts.append(prompt)
        self.estimated_costs.append(estimated_cost)
        return ProviderResult(
            normalized_output={"text": self.answer, "model": self.model_id},
            raw_payload={"scripted": True, "provider_id": self.provider_id},
            request_id="req-scripted-099",
            usage={"prompt_tokens": 120, "completion_tokens": 40, "total_tokens": 160},
            cost=0.000123,
            model_id=self.model_id,
            latency_ms=4.5,
        )


@pytest.fixture
def syn_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg099.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _enable(
    monkeypatch: pytest.MonkeyPatch,
    provider: ScriptedSynthesisProvider,
    *,
    consent: bool = True,
) -> None:
    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider.provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", consent)
    monkeypatch.setattr(settings, "sg_provider_id", provider.provider_id)


def _call(db: Session, provider: ScriptedSynthesisProvider, **overrides: Any) -> syn.SynthesisResult:
    kwargs: dict[str, Any] = {
        "off_source_url": OFF_URL,
        "off_retrieved_at": OFF_AT,
        "jina_source_url": JINA_URL,
        "jina_retrieved_at": JINA_AT,
        "brand": "Jacobs",
        "provider": provider,
    }
    kwargs.update(overrides)
    return syn.synthesize(db, _load("off_hit.json"), _load("jina_hit.json"), **kwargs)


# --------------------------------------------------------------------------- #
# G1 — frozen prompt (loads by version; the file IS the source)
# --------------------------------------------------------------------------- #
def test_frozen_prompt_loads_by_version() -> None:
    prompt_text, version = syn.load_synthesis_prompt()
    assert version == "enrich-synthesis-v1"
    assert prompt_text.startswith("---\n")
    assert "template_version: enrich-synthesis-v1" in prompt_text


def test_frozen_prompt_is_the_file_on_disk() -> None:
    prompt_text, _version = syn.load_synthesis_prompt()
    on_disk = (syn.PROMPTS_DIR / syn.SYNTHESIS_PROMPT_FILE).read_text(encoding="utf-8")
    assert prompt_text == on_disk


def test_frozen_prompt_carries_the_grounding_rules() -> None:
    prompt_text, _version = syn.load_synthesis_prompt()
    lowered = prompt_text.lower()
    assert "source_url" in prompt_text and "retrieved_at" in prompt_text
    assert "brand: absent" in lowered or "no brand" in lowered
    assert "label-wins-visible" in lowered
    assert "never infer" in lowered or "nothing is inferred" in lowered


# --------------------------------------------------------------------------- #
# G2 — consent + cap refusals, seen-to-fail with zero invocations
# --------------------------------------------------------------------------- #
def test_consent_off_refuses_by_name_with_zero_invocations(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer())
    _enable(monkeypatch, provider, consent=False)
    with pytest.raises(syn.SynthesisRefusedError) as excinfo:
        _call(syn_db, provider)
    assert "consent_disabled" in str(excinfo.value)
    assert provider.invocations == 0
    assert syn_db.query(ProviderCall).count() == 0


def test_over_cap_estimate_refuses_before_any_call(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer())
    _enable(monkeypatch, provider)
    with pytest.raises(BudgetExceededError) as excinfo:
        _call(syn_db, provider, per_call_cap_usd=0.0000001)
    assert "per-call cap" in str(excinfo.value)
    assert provider.invocations == 0
    assert syn_db.query(ProviderCall).count() == 0


# --------------------------------------------------------------------------- #
# G3 — the exact cross-boundary payload (PG-EV-04 / PG-SC-12)
# --------------------------------------------------------------------------- #
def test_request_shape_is_exactly_what_crosses_into_extract_text(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer())
    _enable(monkeypatch, provider)
    _call(syn_db, provider)

    assert provider.invocations == 1
    expected_text = syn.build_synthesis_input(
        _load("off_hit.json"),
        _load("jina_hit.json"),
        off_source_url=OFF_URL,
        off_retrieved_at=OFF_AT,
        jina_source_url=JINA_URL,
        jina_retrieved_at=JINA_AT,
        brand="Jacobs",
    )
    prompt_text, _version = syn.load_synthesis_prompt()
    assert provider.texts[0] == expected_text
    assert provider.prompts[0] == prompt_text

    # Fixture-derived source material is present, not a re-typed copy.
    for needle in (
        "Jacobs Cronat Gold instant coffee",
        "Coffee",
        "3274080005003",
        "mega-image.ro",
        "Cafea macinata",
    ):
        assert needle in provider.texts[0], needle
    # Attribution slots ride with the payload.
    for needle in (OFF_URL, OFF_AT, JINA_URL, JINA_AT):
        assert needle in provider.texts[0], needle
    # Text only: no image part, no key material, no Authorization.
    blob = provider.texts[0] + provider.prompts[0]
    assert "base64" not in blob and "image_url" not in blob
    assert "Authorization" not in blob and "sk-" not in blob
    assert "OPENCODE_API_KEY" not in blob


def test_estimated_cost_is_bounded_and_under_the_cap(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer())
    _enable(monkeypatch, provider)
    _call(syn_db, provider)
    estimate = provider.estimated_costs[0]
    assert 0.0 < estimate <= syn.SYNTHESIS_PER_CALL_CAP_USD


# --------------------------------------------------------------------------- #
# G3 — attribution per fact; missing attribution seen-to-fail
# --------------------------------------------------------------------------- #
def test_output_attribution_present_per_fact(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer())
    _enable(monkeypatch, provider)
    result = _call(syn_db, provider)

    assert result.facts, "synthesis must return at least one attributed fact"
    for fact in result.facts:
        assert fact.value
        assert fact.source_url in {OFF_URL, JINA_URL}
        assert fact.retrieved_at in {OFF_AT, JINA_AT}
    assert {(s.source_url, s.retrieved_at) for s in result.sources} == {
        (OFF_URL, OFF_AT),
        (JINA_URL, JINA_AT),
    }
    assert result.template_version == "enrich-synthesis-v1"


def test_fact_missing_attribution_seen_to_fail(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer(missing="retrieved_at"))
    _enable(monkeypatch, provider)
    with pytest.raises(syn.SynthesisFormatError):
        _call(syn_db, provider)


def test_non_json_answer_seen_to_fail(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider("I can only answer from the catalogue data.")
    _enable(monkeypatch, provider)
    with pytest.raises(syn.SynthesisFormatError):
        _call(syn_db, provider)


def test_parse_synthesis_requires_every_attribution_field() -> None:
    good = json.loads(_answer())
    assert len(syn.parse_synthesis(json.dumps(good), brand="Jacobs")) == 4
    for missing in ("field", "value", "source_url", "retrieved_at"):
        broken = json.loads(_answer())
        broken["facts"][0].pop(missing)
        with pytest.raises(syn.SynthesisFormatError):
            syn.parse_synthesis(json.dumps(broken), brand="Jacobs")


# --------------------------------------------------------------------------- #
# G3 — brand absent is never guessed (PG-SC-07), seen-to-fail
# --------------------------------------------------------------------------- #
def test_brand_absent_input_never_yields_a_brand(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer(brand=None))
    _enable(monkeypatch, provider)
    result = _call(
        syn_db,
        provider,
        brand=None,
    )
    # Rebuild with the derived brand-absent OFF payload to prove the input path.
    off_payload = _brand_absent_off()
    assembled = syn.build_synthesis_input(
        off_payload,
        _load("jina_hit.json"),
        off_source_url=OFF_URL,
        off_retrieved_at=OFF_AT,
        jina_source_url=JINA_URL,
        jina_retrieved_at=JINA_AT,
        brand=None,
    )
    assert "brand: ABSENT" in assembled
    assert '"brands"' not in assembled
    assert result.brand is None
    assert all(fact.field.lower() != "brand" for fact in result.facts)


def test_brand_absent_input_drives_the_real_caller(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer(brand=None))
    _enable(monkeypatch, provider)
    result = syn.synthesize(
        syn_db,
        _brand_absent_off(),
        _load("jina_hit.json"),
        off_source_url=OFF_URL,
        off_retrieved_at=OFF_AT,
        jina_source_url=JINA_URL,
        jina_retrieved_at=JINA_AT,
        brand=None,
        provider=provider,
    )
    assert '"brands"' not in provider.texts[0]
    assert result.brand is None
    assert all(fact.field.lower() != "brand" for fact in result.facts)


def test_invented_brand_seen_to_fail(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer(brand="GuessedBrand"))
    _enable(monkeypatch, provider)
    with pytest.raises(syn.SynthesisGroundingError):
        _call(syn_db, provider, brand=None)


# --------------------------------------------------------------------------- #
# G3 — direct seam + ledger row; no catalogue, no persistence
# --------------------------------------------------------------------------- #
def test_caller_reaches_extract_text_not_the_catalogue_respond() -> None:
    source = inspect.getsource(syn)
    assert "build_catalog" not in source
    assert "app.services.chat" not in source
    assert not hasattr(syn, "respond")


def test_one_ledger_row_written_to_the_caller_session(
    syn_db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = ScriptedSynthesisProvider(_answer())
    _enable(monkeypatch, provider)
    result = _call(syn_db, provider)

    rows = syn_db.query(ProviderCall).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.provider == provider.provider_id
    assert row.model == provider.model_id
    assert row.prompt_template_version == "enrich-synthesis-v1"
    assert row.cost == pytest.approx(0.000123)
    assert json.loads(row.usage_json or "{}")["total_tokens"] == 160
    assert row.job_id is None
    assert result.provider_call_id == row.id
    assert result.cost == pytest.approx(0.000123)
    assert result.model == provider.model_id
    # The synthesis is returned, never persisted: only the call ledger row exists.
    assert syn_db.query(ProviderCall).count() == 1
