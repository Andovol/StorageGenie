"""SG-099 non-catalogue enrichment synthesis caller (unwired library).

Turns committed OFF JSON + Jina content into attributed proposals by calling the
metered TEXT seam ``OpenCodeGoProvider.extract_text`` DIRECTLY — never through
the catalogue-bound ``chat.service.respond``. Consent (``reader.ai_status``) and
a per-call cap gate the call before any invocation; the provider's own
``ProviderCall`` ledger row is written to the caller-supplied session; the
synthesis is RETURNED, never persisted (``PG-SC-02`` — consumption is a later
slice). No endpoint, no migration, no deploy rides here.

Inputs are the committed SG-081/082 fixtures' shapes (OFF JSON + Jina payload).
The caller assembles ONE user turn carrying each source block with its
attribution slots, loads the frozen ``enrich-synthesis-v1`` prompt, and parses
the model's answer into facts that each cite a source URL + retrieval date. A
brand-absent input can never yield a brand: the caller refuses an invented one.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.models.provider_call import ProviderCall
from app.services.providers import reader as reader_mod
from app.services.providers.opencode_go import (
    INPUT_USD_PER_1M,
    OUTPUT_USD_PER_1M,
    TEXT_MAX_TOKENS,
)
from app.services.providers.router import BudgetExceededError

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "providers" / "prompts"
SYNTHESIS_PROMPT_FILE = "enrich-synthesis-v1.md"

DATA_OPEN = "<<<ENRICH_SOURCE_DATA>>>"
DATA_CLOSE = "<<<END_ENRICH_SOURCE_DATA>>>"

# Mirror of the endpoint's per-press cap (`api/v1/enrich.py`); stated and
# uncalibrated (`G-A9`). The worst-case estimate binds here BEFORE any call.
SYNTHESIS_PER_CALL_CAP_USD = 0.05
BRAND_ABSENT = "ABSENT"

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class SynthesisError(RuntimeError):
    """Base for named synthesis refusals."""


class SynthesisRefusedError(SynthesisError):
    """Consent (or configuration) refused the call before any invocation."""


class SynthesisFormatError(SynthesisError):
    """The provider answer did not carry attributed facts in the frozen shape."""


class SynthesisGroundingError(SynthesisError):
    """The answer carried a fact the input never declared (a guessed brand)."""


@dataclass(frozen=True)
class SynthesisFact:
    field: str
    value: str
    source_url: str
    retrieved_at: str


@dataclass(frozen=True)
class SynthesisSource:
    source_name: str
    source_url: str
    retrieved_at: str


@dataclass(frozen=True)
class SynthesisResult:
    template_version: str
    provider: str
    model: str
    text: str
    facts: tuple[SynthesisFact, ...]
    sources: tuple[SynthesisSource, ...]
    brand: str | None
    provider_call_id: str
    cost: float
    usage: dict[str, Any]
    latency_ms: float


def load_synthesis_prompt() -> tuple[str, str]:
    """Return (prompt_text, template_version) for the frozen synthesis prompt.

    Frozen-file discipline: the file carries ``template_version`` front matter
    and is never edited in place; a version bump is a new file.
    """
    text = (PROMPTS_DIR / SYNTHESIS_PROMPT_FILE).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"prompt file missing front matter: {SYNTHESIS_PROMPT_FILE}")
    header = text.split("---\n", 2)[1]
    version = ""
    for line in header.splitlines():
        if line.startswith("template_version:"):
            version = line.split(":", 1)[1].strip()
    if not version:
        raise ValueError(f"prompt file missing template_version: {SYNTHESIS_PROMPT_FILE}")
    return text, version


def estimate_text_cost(
    text: str, prompt: str, *, max_tokens: int = TEXT_MAX_TOKENS
) -> float:
    """Bounded worst-case USD for ONE text call from the vendor rate table.

    Input tokens are bounded above by one token per source byte (prompt plus
    user text); output is bounded by ``max_tokens``, which defaults to the
    text-turn bound ``TEXT_MAX_TOKENS`` (SG-101) — the same bound
    ``build_text_payload`` sends — so the cap this estimate guards is not blind
    to the text-turn output budget. Deliberately an upper bound, so a cap
    compared against it can never be surprised. No clock, no network.
    """
    input_tokens = len(prompt.encode("utf-8")) + len(text.encode("utf-8"))
    return (input_tokens * INPUT_USD_PER_1M + max_tokens * OUTPUT_USD_PER_1M) / 1_000_000


def _source_block(
    source_name: str, source_url: str, retrieved_at: str, payload: Any
) -> list[str]:
    return [
        f"source_name: {source_name}",
        f"source_url: {source_url}",
        f"retrieved_at: {retrieved_at}",
        "payload:",
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        "",
    ]


def build_synthesis_input(
    off_payload: Any,
    jina_payload: Any,
    *,
    off_source_url: str,
    off_retrieved_at: str,
    jina_source_url: str,
    jina_retrieved_at: str,
    brand: str | None = None,
    off_source_name: str = "OpenFoodFacts",
    jina_source_name: str = "JinaSearch",
) -> str:
    """Assemble the EXACT user turn handed to ``extract_text`` (``PG-EV-04``).

    Fixture-derived source JSON only; the attribution slots (name/url/date) ride
    with each block so every fact the model emits can cite its origin. A
    brand-absent call emits ``brand: ABSENT`` and no brand value.
    """
    lines = [DATA_OPEN]
    lines += _source_block(off_source_name, off_source_url, off_retrieved_at, off_payload)
    lines += _source_block(jina_source_name, jina_source_url, jina_retrieved_at, jina_payload)
    lines.append(f"brand: {brand if brand else BRAND_ABSENT}")
    lines.append(DATA_CLOSE)
    return "\n".join(lines)


def _extract_json(text: str) -> Any:
    if not isinstance(text, str) or not text.strip():
        raise SynthesisFormatError("empty synthesis answer")
    candidates = [text.strip()]
    stripped = _FENCE_RE.sub("", text).strip()
    if stripped and stripped != candidates[0]:
        candidates.append(stripped)
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except ValueError:
            pass
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(candidate[start : end + 1])
            except ValueError:
                pass
    raise SynthesisFormatError("answer is not parseable JSON")


def _require_str(raw: dict[str, Any], key: str, index: int) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SynthesisFormatError(f"fact {index} missing a non-empty `{key}`")
    return value.strip()


def parse_synthesis(text: str, *, brand: str | None = None) -> tuple[SynthesisFact, ...]:
    """Parse the frozen-shape answer into facts, enforcing attribution + grounding.

    Every fact must carry a non-empty ``field``/``value``/``source_url``/
    ``retrieved_at``. When ``brand`` is absent, a ``brand`` fact is refused: the
    input never declared one (``PG-SC-07``).
    """
    payload = _extract_json(text)
    if not isinstance(payload, dict):
        raise SynthesisFormatError("answer is not a JSON object")
    raw_facts = payload.get("facts")
    if not isinstance(raw_facts, list):
        raise SynthesisFormatError("answer has no `facts` list")
    facts: list[SynthesisFact] = []
    for index, raw in enumerate(raw_facts):
        if not isinstance(raw, dict):
            raise SynthesisFormatError(f"fact {index} is not an object")
        facts.append(
            SynthesisFact(
                field=_require_str(raw, "field", index),
                value=_require_str(raw, "value", index),
                source_url=_require_str(raw, "source_url", index),
                retrieved_at=_require_str(raw, "retrieved_at", index),
            )
        )
    if not brand or not str(brand).strip():
        for fact in facts:
            if fact.field.strip().lower() == "brand":
                raise SynthesisGroundingError(
                    "brand_absent: synthesis emitted a brand fact from brand-absent input"
                )
    return tuple(facts)


def synthesize(
    db: Session,
    off_payload: Any,
    jina_payload: Any,
    *,
    off_source_url: str,
    off_retrieved_at: str,
    jina_source_url: str,
    jina_retrieved_at: str,
    brand: str | None = None,
    provider: Any | None = None,
    per_call_cap_usd: float = SYNTHESIS_PER_CALL_CAP_USD,
    estimated_cost: float | None = None,
) -> SynthesisResult:
    """One attributed synthesis over OFF JSON + Jina content, gated and ledgered.

    Consent refuses before any invocation. An over-cap worst-case estimate
    refuses before any invocation. The call goes DIRECTLY to ``extract_text``
    (never the catalogue-bound ``respond``); exactly one ``ProviderCall`` row is
    written to ``db``. The synthesis is returned, never persisted.
    """
    enabled, reason = reader_mod.ai_status()
    if not enabled:
        raise SynthesisRefusedError(reason)

    prompt_text, template_version = load_synthesis_prompt()
    user_text = build_synthesis_input(
        off_payload,
        jina_payload,
        off_source_url=off_source_url,
        off_retrieved_at=off_retrieved_at,
        jina_source_url=jina_source_url,
        jina_retrieved_at=jina_retrieved_at,
        brand=brand,
    )

    if provider is None:
        registry = reader_mod.provider_registry()
        provider = registry[settings.sg_provider_id]
    provider_id = str(getattr(provider, "provider_id", settings.sg_provider_id))

    if estimated_cost is None:
        estimated_cost = estimate_text_cost(user_text, prompt_text)
    if per_call_cap_usd is not None and estimated_cost > per_call_cap_usd:
        raise BudgetExceededError(
            f"estimated cost {estimated_cost:.6f} exceeds per-call cap {per_call_cap_usd}"
        )

    result = provider.extract_text(user_text, prompt_text, estimated_cost=estimated_cost)

    model_id = str(
        getattr(result, "model_id", "") or getattr(provider, "model_id", "") or settings.sg_model_id
    )
    usage = dict(getattr(result, "usage", {}) or {})
    cost = float(getattr(result, "cost", 0.0) or 0.0)
    latency_ms = float(getattr(result, "latency_ms", 0.0) or 0.0)

    row = ProviderCall(
        provider=provider_id,
        model=model_id,
        prompt_template_version=template_version,
        input_hashes=json.dumps(
            {"synthesis_input_sha256": hashlib.sha256(user_text.encode("utf-8")).hexdigest()}
        ),
        output_payload=json.dumps(
            getattr(result, "raw_payload", {}) or {}, ensure_ascii=False, default=str
        ),
        cost=cost,
        usage_json=json.dumps(usage, ensure_ascii=False),
        latency_ms=latency_ms,
        error_state=None,
        job_id=None,
    )
    db.add(row)
    db.commit()

    normalized = getattr(result, "normalized_output", {}) or {}
    raw_text = str(normalized.get("text") or "") if isinstance(normalized, dict) else ""
    facts = parse_synthesis(raw_text, brand=brand)

    return SynthesisResult(
        template_version=template_version,
        provider=provider_id,
        model=model_id,
        text=raw_text,
        facts=facts,
        sources=(
            SynthesisSource("OpenFoodFacts", off_source_url, off_retrieved_at),
            SynthesisSource("JinaSearch", jina_source_url, jina_retrieved_at),
        ),
        brand=brand,
        provider_call_id=str(row.id),
        cost=cost,
        usage=usage,
        latency_ms=latency_ms,
    )
