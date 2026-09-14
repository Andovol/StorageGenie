"""SG-037 planning service: manual-trigger daily planning, Stage 0.

Design note (premise correction F-SG037-1). The provider seam exposes exactly
one real operation, `extract_items(image_bytes, prompt)`, and the SG-027
adapter validates its response against the frozen `ExtractionOutput` schema.
The packet's scope ceiling forbids extending the seam (`protocols.py`,
`router.py`, `opencode_go.py`) and forbids touching the reader, so this service
reuses that one operation: the planning prompt asks the model for the same
strict envelope, and each returned `item` is mapped to one `PlanningSuggestion`.
The catalogue facts (labels, dates, ids) are supplied to the prompt and used to
resolve `backing_refs_json`; the model supplies priority, kind and rationale.
A 1x1 carrier image is sent only because the adapter's surface requires image
bytes — the entire planning task is in the prompt text.

Consent gates the run before any call or row (`reader.ai_status`); the reader
seam's registry and router are reused unchanged; no key is referenced here.
Nothing in this module executes a suggestion: a run writes only
`planning_suggestion`, `guardrail_event` and `provider_call` rows.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.guardrail_event import GuardrailEvent
from app.models.planning_suggestion import PlanningSuggestion
from app.models.provider_call import ProviderCall
from app.services.providers import reader as reader_mod
from app.services.providers.router import (
    BudgetExceededError,
    ProviderError,
    ProviderRouter,
    RouterConfig,
)
from app.services.providers.schemas import ExtractionItem, ExtractionOutput

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "providers" / "prompts"
PLANNING_PROMPT_FILE = "planning-v1.md"
PLANNING_OPERATION = "extract_items"
CLASSIFICATION_FIELD = "plugin:expiry-tracker/classification"
EXPIRY_FIELD = "plugin:expiry-tracker/expiry_date"
OPENED_DATE_FIELD = "opened_date"

ALLOWED_STATUSES: tuple[str, ...] = ("pending", "confirmed", "dismissed")
SUGGESTION_KINDS: tuple[str, ...] = ("use_first", "restock", "days_math")
DEFAULT_KIND = "general"


class SuggestionNotFound(LookupError):
    """No suggestion with that id exists."""


class SuggestionHouseholdMismatch(PermissionError):
    """The suggestion belongs to a different household."""


class SuggestionTransitionError(ValueError):
    """An illegal status transition was attempted (enforced as 422)."""


def load_planning_prompt() -> tuple[str, str]:
    """Return (prompt_text, template_version) for the frozen planning prompt.

    Same front-matter discipline as the extraction prompts (a versioned,
    read-only file; the runtime never edits it in place).
    """
    text = (PROMPTS_DIR / PLANNING_PROMPT_FILE).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"prompt file missing front matter: {PLANNING_PROMPT_FILE}")
    header = text.split("---\n", 2)[1]
    version = ""
    for line in header.splitlines():
        if line.startswith("template_version:"):
            version = line.split(":", 1)[1].strip()
    if not version:
        raise ValueError(f"prompt file missing template_version: {PLANNING_PROMPT_FILE}")
    return text, version


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


def build_catalog(db: Session, household_id: str) -> list[dict[str, Any]]:
    """Label data for every ACTIVE asset: the ONLY input the prompt builder sees.

    Reads the existing asset + assertion tables as-is; returns no ids beyond the
    asset/assertion ids the suggestion must name, and no secrets.
    """
    assets = (
        db.query(Asset)
        .filter(Asset.household_id == household_id, Asset.status == "ACTIVE")
        .order_by(Asset.display_name)
        .all()
    )
    catalog: list[dict[str, Any]] = []
    for asset in assets:
        category: str | None = None
        classification = _active_assertion(db, asset.id, CLASSIFICATION_FIELD)
        if classification is not None:
            try:
                category = json.loads(classification.value_json).get("category")
            except (json.JSONDecodeError, AttributeError):
                category = None
        expiry_date: str | None = None
        opened_date: str | None = None
        date_type: str | None = None
        expiry_assertion_id: str | None = None
        opened_assertion_id: str | None = None
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
        opened = _active_assertion(db, asset.id, OPENED_DATE_FIELD)
        if opened is not None:
            opened_assertion_id = opened.id
            try:
                opened_value = json.loads(opened.value_json)
            except json.JSONDecodeError:
                opened_value = None
            if isinstance(opened_value, str):
                opened_date = opened_value
        catalog.append(
            {
                "id": asset.id,
                "label": asset.display_name,
                "category": category,
                "expiry_date": expiry_date,
                "opened_date": opened_date,
                "date_type": date_type,
                "status": asset.status,
                "expiry_assertion_id": expiry_assertion_id,
                "opened_assertion_id": opened_assertion_id,
            }
        )
    return catalog


def _carrier_png() -> bytes:
    """A 1x1 white PNG: the adapter's surface requires image bytes.

    The planning task is entirely in the prompt; the carrier carries no data and
    is redacted by the adapter exactly like a real upload.
    """
    buffer = io.BytesIO()
    Image.new("RGB", (1, 1), (255, 255, 255)).save(buffer, format="PNG")
    return buffer.getvalue()


def _estimate(provider: Any, carrier: bytes, prompt: str) -> float:
    estimator = getattr(provider, "estimate_cost", None)
    if callable(estimator):
        return float(estimator(carrier, prompt))
    return 0.0


def _repair_prompt(prompt: str) -> str:
    return (
        prompt
        + "\n\n## Repair\n"
        + "Your previous response was rejected. Return ONE JSON object with keys "
        + "`items`, `unknowns`, `needs_evidence` and nothing else. Do NOT prepend a "
        + '`{"type": "json_object"}` wrapper, a code fence, or any prose.'
    )


def _write_ledger(
    db: Session,
    provider_id: str,
    model_id: str,
    prompt: str,
    result: Any,
) -> ProviderCall:
    row = ProviderCall(
        provider=provider_id,
        model=str(result.model_id or model_id),
        prompt_template_version="planning-v1",
        input_hashes=json.dumps({"prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest()}),
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
    db: Session, provider_id: str, model_id: str, prompt: str, kind: str, message: str
) -> ProviderCall:
    row = ProviderCall(
        provider=provider_id,
        model=model_id,
        prompt_template_version="planning-v1",
        input_hashes=json.dumps({"prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest()}),
        output_payload=None,
        cost=0.0,
        usage_json=None,
        latency_ms=None,
        error_state=f"{kind}: {message}"[:200],
        job_id=None,
    )
    db.add(row)
    db.commit()
    return row


def _run_provider(
    db: Session,
    provider: Any,
    provider_id: str,
    model_id: str,
    router: ProviderRouter,
    carrier: bytes,
    prompt: str,
) -> tuple[ExtractionOutput | None, list[str], str | None]:
    """One logical planning call with at most one repair turn (§5.3 shape).

    Every failed attempt leaves a committed `error_state` ledger row; a budget
    refusal raises before any provider call and therefore writes no row.
    """
    estimate = _estimate(provider, carrier, prompt)
    call_ids: list[str] = []
    last_error: str | None = None
    for attempt in (1, 2):
        call_prompt = prompt if attempt == 1 else _repair_prompt(prompt)
        try:
            result = router.execute(
                PLANNING_OPERATION, carrier, call_prompt, estimated_cost=estimate
            )
        except BudgetExceededError:
            raise
        except ProviderError as exc:
            row = _write_error_ledger(db, provider_id, model_id, call_prompt, exc.kind, str(exc))
            call_ids.append(row.id)
            last_error = f"{exc.kind}: {exc}"
            continue
        except PydanticValidationError as exc:
            row = _write_error_ledger(db, provider_id, model_id, call_prompt, "invalid_json", str(exc))
            call_ids.append(row.id)
            last_error = f"invalid_json: {exc}"
            continue
        try:
            output = ExtractionOutput.model_validate(result.normalized_output)
        except PydanticValidationError as exc:
            row = _write_error_ledger(db, provider_id, model_id, call_prompt, "invalid_json", str(exc))
            call_ids.append(row.id)
            last_error = f"invalid_json: {exc}"
            continue
        row = _write_ledger(db, provider_id, model_id, call_prompt, result)
        call_ids.append(row.id)
        return output, call_ids, None
    return None, call_ids, last_error


def _backing_refs(item: ExtractionItem, index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    entry: dict[str, Any] | None = index.get(item.lot) if item.lot else None
    if entry is None:
        lowered = (item.name or "").lower()
        for candidate in index.values():
            label = str(candidate.get("label") or "")
            if label and label.lower() in lowered:
                entry = candidate
                break
    if entry is None:
        return [{"type": "label", "value": item.lot or item.name}]
    refs: list[dict[str, Any]] = [
        {
            "type": "asset",
            "id": entry["id"],
            "label": entry["label"],
            "category": entry["category"],
        }
    ]
    if entry.get("expiry_assertion_id"):
        refs.append(
            {
                "type": "assertion",
                "id": entry["expiry_assertion_id"],
                "field_path": EXPIRY_FIELD,
                "value": entry.get("expiry_date"),
            }
        )
    if entry.get("opened_assertion_id"):
        refs.append(
            {
                "type": "assertion",
                "id": entry["opened_assertion_id"],
                "field_path": OPENED_DATE_FIELD,
                "value": entry.get("opened_date"),
            }
        )
    return refs


def _write_suggestions(
    db: Session, household_id: str, items: list[ExtractionItem], catalog: list[dict[str, Any]]
) -> list[PlanningSuggestion]:
    index = {str(entry["id"]): entry for entry in catalog}
    suggestions: list[PlanningSuggestion] = []
    for item in items:
        kind = item.date_type if item.date_type in SUGGESTION_KINDS else DEFAULT_KIND
        body = {
            "rationale": item.uncertainty_reasons,
            "expiry_date": item.expiry_date,
            "opened_date": item.opened_date,
            "confidence": item.confidence,
            "asset_ref": item.lot,
        }
        suggestion = PlanningSuggestion(
            household_id=household_id,
            kind=kind,
            title=item.name[:300],
            body_json=json.dumps(body, ensure_ascii=False),
            backing_refs_json=json.dumps(_backing_refs(item, index), ensure_ascii=False),
        )
        db.add(suggestion)
        suggestions.append(suggestion)
    db.flush()
    return suggestions


def run_planning(db: Session, household_id: str) -> dict[str, Any]:
    """Run one manual planning pass. Consent gates it; nothing is executed."""
    enabled, reason = reader_mod.ai_status()
    if not enabled:
        return {
            "status": "skipped",
            "reason": reason,
            "suggestion_count": 0,
            "catalog_size": 0,
        }

    catalog = build_catalog(db, household_id)
    if not catalog:
        event = GuardrailEvent(
            household_id=household_id,
            kind="suggestion",
            ref_ids_json=json.dumps([]),
            detail_json=json.dumps({"outcome": "empty_catalog", "suggestion_count": 0}),
        )
        db.add(event)
        db.commit()
        return {
            "status": "ok",
            "suggestion_count": 0,
            "catalog_size": 0,
            "provider": None,
            "model": None,
            "guardrail_event_id": event.id,
            "provider_call_ids": [],
        }

    prompt_text, _version = load_planning_prompt()
    base_prompt = prompt_text + "\n\n## Catalog\n" + json.dumps(catalog, ensure_ascii=False)

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
    carrier = _carrier_png()

    try:
        output, call_ids, error = _run_provider(
            db, provider, provider_id, model_id, router, carrier, base_prompt
        )
    except BudgetExceededError as exc:
        return {
            "status": "refused",
            "reason": str(exc),
            "suggestion_count": 0,
            "catalog_size": len(catalog),
        }

    if output is None:
        db.commit()
        return {
            "status": "error",
            "reason": error or "provider_failed",
            "suggestion_count": 0,
            "catalog_size": len(catalog),
            "provider": provider_id,
            "model": model_id,
            "provider_call_ids": call_ids,
        }

    suggestions = _write_suggestions(db, household_id, output.items, catalog)
    event = GuardrailEvent(
        household_id=household_id,
        kind="suggestion",
        ref_ids_json=json.dumps([suggestion.id for suggestion in suggestions]),
        detail_json=json.dumps(
            {
                "outcome": "ok",
                "suggestion_count": len(suggestions),
                "provider": provider_id,
                "model": model_id,
                "prompt_template_version": "planning-v1",
                "catalog_size": len(catalog),
            }
        ),
    )
    db.add(event)
    db.commit()
    return {
        "status": "ok",
        "suggestion_count": len(suggestions),
        "catalog_size": len(catalog),
        "provider": provider_id,
        "model": model_id,
        "guardrail_event_id": event.id,
        "provider_call_ids": call_ids,
    }


def list_suggestions(
    db: Session, household_id: str, status: str | None = None
) -> list[PlanningSuggestion]:
    query = db.query(PlanningSuggestion).filter(PlanningSuggestion.household_id == household_id)
    if status is not None:
        query = query.filter(PlanningSuggestion.status == status)
    return query.order_by(PlanningSuggestion.created_at.desc(), PlanningSuggestion.id.desc()).all()


def _get_suggestion(db: Session, household_id: str, suggestion_id: str) -> PlanningSuggestion:
    suggestion = db.get(PlanningSuggestion, suggestion_id)
    if suggestion is None:
        raise SuggestionNotFound(suggestion_id)
    if suggestion.household_id != household_id:
        raise SuggestionHouseholdMismatch(suggestion_id)
    return suggestion


def confirm_suggestion(
    db: Session, household_id: str, suggestion_id: str
) -> PlanningSuggestion:
    """pending -> confirmed; any other source status is an illegal transition."""
    suggestion = _get_suggestion(db, household_id, suggestion_id)
    if suggestion.status != "pending":
        raise SuggestionTransitionError(
            f"cannot confirm a suggestion in status {suggestion.status!r}"
        )
    suggestion.status = "confirmed"
    db.commit()
    db.refresh(suggestion)
    return suggestion


def dismiss_suggestion(
    db: Session, household_id: str, suggestion_id: str, reason: str | None = None
) -> PlanningSuggestion:
    """pending -> dismissed; a reason writes an append-only correction event."""
    suggestion = _get_suggestion(db, household_id, suggestion_id)
    if suggestion.status != "pending":
        raise SuggestionTransitionError(
            f"cannot dismiss a suggestion in status {suggestion.status!r}"
        )
    suggestion.status = "dismissed"
    if reason:
        db.add(
            GuardrailEvent(
                household_id=household_id,
                kind="correction",
                ref_ids_json=json.dumps([suggestion.id]),
                detail_json=json.dumps(
                    {
                        "reason": reason,
                        "from_status": "pending",
                        "to_status": "dismissed",
                    }
                ),
            )
        )
    db.commit()
    db.refresh(suggestion)
    return suggestion
