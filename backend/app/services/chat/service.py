"""SG-038 chat service: grounded, consent-gated category chat, Stage 0.

The server builds the grounding context from ONE category's catalogue (active
assets plus their classification, expiry/opened assertions and source
attributions) and sends it through the provider seam's text operation as DATA.
The catalogue text is untrusted: `build_user_content` places it inside a
delimited block and the versioned system prompt tells the model to treat that
block as data, never as instructions. Nothing here executes a suggestion or
changes catalogue state.

Consent gates the run before any call or row (`reader.ai_status`); the reader
seam's registry and router are reused unchanged; no key is referenced here.
A `correction` guardrail row is written ONLY by the explicit user action
(`log_correction`), never from model output.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.models.assertion import Assertion
from app.models.asset import UNTITLED_LABEL, Asset
from app.models.guardrail_event import GuardrailEvent
from app.models.provider_call import ProviderCall
from app.models.source_attribution import SourceAttribution
from app.services.providers import reader as reader_mod
from app.services.providers.router import (
    BudgetExceededError,
    ProviderError,
    ProviderRouter,
    RouterConfig,
)

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "providers" / "prompts"
CHAT_PROMPT_FILE = "chat-v1.md"
CHAT_OPERATION = "extract_text"
CLASSIFICATION_FIELD = "plugin:expiry-tracker/classification"
EXPIRY_FIELD = "plugin:expiry-tracker/expiry_date"
OPENED_DATE_FIELD = "opened_date"

DATA_OPEN = "<<<CATALOGUE_DATA>>>"
DATA_CLOSE = "<<<END_CATALOGUE_DATA>>>"

# The user-facing category values this service accepts, mapped to the catalogue
# category slugs. An unsupported value is an enforced 422 at the route.
# Food/medicine are the dedicated category-chat classes; household/documents ride
# the SAME shared generic prompt below (descriptor `chat: "fallback"`, SG-073) —
# no per-category prompt fork. Cosmetics stays gated out here on purpose
# (`chat: "none"`): a dedicated cosmetics agent is a separate decision.
SUPPORTED_CATEGORIES: dict[str, str] = {
    "food": "food_beverages",
    "medicine": "medicine_pharma",
    "household": "household_chemicals",
    "documents": "documents_other",
}

EMPTY_ANSWER = (
    "There is no catalogue data recorded for this category yet, so I cannot "
    "answer from your items."
)


class UnsupportedCategoryError(ValueError):
    """The requested chat category is not in the supported set (enforced 422)."""


def load_chat_prompt() -> tuple[str, str]:
    """Return (prompt_text, template_version) for the versioned chat prompt.

    Same front-matter discipline as the extraction/planning prompts (a
    versioned, read-only file; the runtime never edits it in place).
    """
    text = (PROMPTS_DIR / CHAT_PROMPT_FILE).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"prompt file missing front matter: {CHAT_PROMPT_FILE}")
    header = text.split("---\n", 2)[1]
    version = ""
    for line in header.splitlines():
        if line.startswith("template_version:"):
            version = line.split(":", 1)[1].strip()
    if not version:
        raise ValueError(f"prompt file missing template_version: {CHAT_PROMPT_FILE}")
    return text, version


def resolve_category(category: str) -> str:
    slug = SUPPORTED_CATEGORIES.get(category)
    if slug is None:
        raise UnsupportedCategoryError(f"unknown chat category: {category}")
    return slug


def _active_assertion(db: Session, asset_id: str, field_path: str) -> Assertion | None:
    return (
        db.query(Assertion)
        .filter(
            Assertion.asset_id == asset_id,
            Assertion.field_path == field_path,
            Assertion.review_state.not_in(("superseded", "rejected")),
        )
        .order_by(Assertion.created_at.desc())
        .first()
    )


def _date_assertion_value(db: Session, asset_id: str, field_path: str) -> str | None:
    """The active assertion's JSON value when it is a plain string, else None."""
    assertion = _active_assertion(db, asset_id, field_path)
    if assertion is None:
        return None
    try:
        value = json.loads(assertion.value_json)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, str) else None


def _source_attributions(db: Session, asset_id: str) -> list[dict[str, Any]]:
    rows = (
        db.query(SourceAttribution)
        .filter(SourceAttribution.asset_id == asset_id)
        .order_by(SourceAttribution.retrieved_at.desc())
        .all()
    )
    return [
        {
            "uri": row.uri,
            "field_path": row.field_path,
            "retrieved_at": row.retrieved_at.isoformat() if row.retrieved_at else None,
            "note": row.note,
        }
        for row in rows
    ]


def build_catalog(db: Session, household_id: str, category: str) -> list[dict[str, Any]]:
    """Label data for one category's ACTIVE assets: the ONLY grounding input.

    Returns no secrets: asset label data, the classification/expiry assertions
    that already exist, and any source attributions attached to the asset.
    """
    slug = resolve_category(category)
    assets = (
        db.query(Asset)
        .filter(Asset.household_id == household_id, Asset.status == "ACTIVE")
        .order_by(Asset.display_name)
        .all()
    )
    catalog: list[dict[str, Any]] = []
    for asset in assets:
        classification = _active_assertion(db, asset.id, CLASSIFICATION_FIELD)
        if classification is None:
            continue
        try:
            asset_category = json.loads(classification.value_json).get("category")
        except (json.JSONDecodeError, AttributeError):
            asset_category = None
        if asset_category != slug:
            continue
        expiry_date: str | None = None
        opened_date: str | None = None
        date_type: str | None = None
        expiry_assertion_id: str | None = None
        expiry = _active_assertion(db, asset.id, EXPIRY_FIELD)
        if expiry is not None:
            expiry_assertion_id = expiry.id
            try:
                value = json.loads(expiry.value_json)
            except json.JSONDecodeError:
                value = {}
            if isinstance(value, dict):
                expiry_date = value.get("expiry_date")
                date_type = value.get("date_type")
        opened_date = _date_assertion_value(db, asset.id, OPENED_DATE_FIELD)
        catalog.append(
            {
                "id": asset.id,
                "label": asset.display_name or UNTITLED_LABEL,
                "category": asset_category,
                "expiry_date": expiry_date,
                "opened_date": opened_date,
                "date_type": date_type,
                "status": asset.status,
                "expiry_assertion_id": expiry_assertion_id,
                "source_attributions": _source_attributions(db, asset.id),
            }
        )
    return catalog


def build_user_content(message: str, catalog: list[dict[str, Any]]) -> str:
    """The user turn: the delimited catalogue DATA block, then the question.

    Catalogue text is never instruction content. Everything between the
    delimiters is untrusted data; the system prompt says so and the structural
    test proves a hostile label stays inside this block.
    """
    return (
        f"{DATA_OPEN}\n"
        + json.dumps(catalog, ensure_ascii=False)
        + f"\n{DATA_CLOSE}\n\n"
        + "User question:\n"
        + message
    )


def _estimate(provider: Any, payload_bytes: bytes, prompt: str) -> float:
    estimator = getattr(provider, "estimate_cost", None)
    if callable(estimator):
        return float(estimator(payload_bytes, prompt))
    return 0.0


def _write_ledger(
    db: Session,
    provider_id: str,
    model_id: str,
    template_version: str,
    content: str,
    result: Any,
) -> ProviderCall:
    row = ProviderCall(
        provider=provider_id,
        model=str(result.model_id or model_id),
        prompt_template_version=template_version,
        input_hashes=json.dumps(
            {"content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}
        ),
        output_payload=json.dumps(result.raw_payload, ensure_ascii=False, default=str),
        cost=result.cost,
        usage_json=json.dumps(result.usage, ensure_ascii=False),
        latency_ms=result.latency_ms,
        error_state=None,
        job_id=None,
    )
    db.add(row)
    db.flush()
    return row


def _write_error_ledger(
    db: Session,
    provider_id: str,
    model_id: str,
    template_version: str,
    content: str,
    kind: str,
    message: str,
    usage: dict[str, Any] | None = None,
    cost: float | None = None,
    latency_ms: float | None = None,
) -> ProviderCall:
    """Persist a failed chat call, recording what the exception CARRIED (SG-062).

    A call that reached the provider and returned a body carries real usage/cost
    on its raised `ProviderError`; those are recorded verbatim. An exception with
    none (`usage`/`cost`/`latency_ms` absent) stays honest `0.0`/`None` — never
    invented. Same split as `reader._write_error_ledger`.
    """
    row = ProviderCall(
        provider=provider_id,
        model=model_id,
        prompt_template_version=template_version,
        input_hashes=json.dumps(
            {"content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}
        ),
        output_payload=None,
        cost=float(cost) if cost is not None else 0.0,
        usage_json=json.dumps(usage, ensure_ascii=False) if usage else None,
        latency_ms=float(latency_ms) if latency_ms is not None else None,
        error_state=f"{kind}: {message}"[:200],
        job_id=None,
    )
    db.add(row)
    db.commit()
    return row


def respond(
    db: Session, household_id: str, category: str, message: str
) -> dict[str, Any]:
    """Answer one grounded question. Consent gates it; nothing is executed.

    No consent -> `status="skipped"` with zero provider calls and zero rows.
    Empty category data -> a valid answer path (`status="ok"`,
    `empty_catalogue=True`, a fixed refusal-to-guess answer) with zero calls.
    """
    resolve_category(category)

    enabled, reason = reader_mod.ai_status()
    if not enabled:
        return {
            "status": "skipped",
            "reason": reason,
            "answer": None,
            "grounded": False,
            "empty_catalogue": False,
            "category": category,
            "catalogue_size": 0,
            "provider_call_id": None,
        }

    catalog = build_catalog(db, household_id, category)
    if not catalog:
        return {
            "status": "ok",
            "reason": "empty_catalogue",
            "answer": EMPTY_ANSWER,
            "grounded": True,
            "empty_catalogue": True,
            "category": category,
            "catalogue_size": 0,
            "provider": None,
            "model": None,
            "provider_call_id": None,
        }

    prompt_text, template_version = load_chat_prompt()
    content = build_user_content(message, catalog)

    registry = reader_mod.provider_registry()
    provider_id = settings.sg_provider_id
    provider = registry[provider_id]
    model_id = str(getattr(provider, "model_id", reader_mod.effective_model_id()))
    config = RouterConfig(
        provider_id=provider_id,
        fallback_id=None,
        json_strict=True,
        cost_budget=settings.sg_per_job_cap if settings.sg_per_job_cap is not None else math.inf,
        retryable_errors=reader_mod.RETRYABLE_ERRORS,
    )
    router = ProviderRouter(config=config, registry=registry)
    estimate = _estimate(provider, content.encode("utf-8"), prompt_text)

    try:
        result = router.execute(
            CHAT_OPERATION, content, prompt_text, estimated_cost=estimate
        )
    except BudgetExceededError as exc:
        return {
            "status": "refused",
            "reason": str(exc),
            "answer": None,
            "grounded": False,
            "empty_catalogue": False,
            "category": category,
            "catalogue_size": len(catalog),
            "provider_call_id": None,
        }
    except ProviderError as exc:
        _write_error_ledger(
            db,
            provider_id,
            model_id,
            template_version,
            content,
            exc.kind,
            str(exc),
            usage=getattr(exc, "usage", None),
            cost=getattr(exc, "cost", None),
            latency_ms=getattr(exc, "latency_ms", None),
        )
        return {
            "status": "error",
            "reason": f"{exc.kind}: {exc}",
            "answer": None,
            "grounded": False,
            "empty_catalogue": False,
            "category": category,
            "catalogue_size": len(catalog),
            "provider_call_id": None,
        }

    row = _write_ledger(db, provider_id, model_id, template_version, content, result)
    db.commit()
    normalized = result.normalized_output or {}
    answer = normalized.get("text") if isinstance(normalized, dict) else None
    return {
        "status": "ok",
        "reason": None,
        "answer": answer,
        "grounded": True,
        "empty_catalogue": False,
        "category": category,
        "catalogue_size": len(catalog),
        "provider": provider_id,
        "model": result.model_id,
        "provider_call_id": row.id,
        "usage": result.usage,
        "cost": result.cost,
        "latency_ms": result.latency_ms,
    }


def log_correction(
    db: Session, household_id: str, category: str, message: str
) -> GuardrailEvent:
    """Write an append-only `correction` event for an explicit user action.

    This is the ONLY chat path that writes a guardrail row, and it is reached
    only from the corrections route: untrusted model output cannot call it.
    """
    resolve_category(category)
    event = GuardrailEvent(
        household_id=household_id,
        kind="correction",
        ref_ids_json=json.dumps([]),
        detail_json=json.dumps(
            {"message": message, "category": category, "source": "user"},
            ensure_ascii=False,
        ),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
