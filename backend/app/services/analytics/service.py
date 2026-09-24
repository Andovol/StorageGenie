"""SG-066 analytics service: deterministic stats + a grounded NL summary.

Two operations, no scheduler and no new table:

* `compute_stats` is pure computation over existing tables. Every number it
  returns carries a `source` string naming the table and the query shape it was
  read through (`PG-SC-02`). Category ids come from the SAME plugin registry the
  serving route (`GET /v1/taxonomy`) reflects, never a hardcoded list.
* `run_insights` is the manual-trigger Analytics Insight Agent (blueprint §9.4).
  It mirrors the SG-037 planning agent shape: consent gates the run BEFORE any
  call or row (`reader.ai_status`), the reader seam's ONE vision operation
  `extract_items(image_bytes, prompt)` is reused with a frozen versioned prompt,
  and a run writes only `provider_call` + `guardrail_event` rows. Nothing here
  executes anything or touches catalogue state.

Grounding: the G1 stats are supplied to the prompt as a flat `stats` list of
`{id, label, value, source}` rows. The model must return one `ExtractionOutput`
item per summary sentence, each carrying the exact stat id it is grounded in as
`item.lot`. A response with no citations, or one citing an id that is not in the
supplied stats, is a loud failure (`InsightsUngroundedError` at the HTTP layer);
it is never trimmed silently.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from PIL import Image
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.guardrail_event import GuardrailEvent
from app.models.household import Household
from app.models.planning_suggestion import PlanningSuggestion
from app.models.provider_call import ProviderCall
from app.models.review_task import ReviewTask
from app.plugins.registry import iter_plugins
from app.services.providers import reader as reader_mod
from app.services.providers.router import (
    BudgetExceededError,
    ProviderError,
    ProviderRouter,
    RouterConfig,
)
from app.services.providers.schemas import ExtractionItem, ExtractionOutput

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "providers" / "prompts"
INSIGHTS_PROMPT_FILE = "analytics-insights-v1.md"
INSIGHTS_OPERATION = "extract_items"
CLASSIFICATION_FIELD = "plugin:expiry-tracker/classification"
EXPIRY_FIELD = "plugin:expiry-tracker/expiry_date"

# Blueprint §11.2 screen 7 describes the expiry dashboard as an urgency-sorted
# view (expired / this week / this month / safe). No such dashboard exists in the
# tree yet (SG-016 deferred it), so these are the bucket semantics this service
# fixes: strict `< as_of` is expired, `<= as_of + 7d` is the week, `<= as_of +
# 30d` is the month, the rest safe, and an active asset without a parseable
# active expiry date is `unknown`.
EXPIRY_BUCKETS: tuple[str, ...] = (
    "expired",
    "within_7_days",
    "within_30_days",
    "safe",
    "unknown",
)


class InsightsUngroundedError(ValueError):
    """The summary cited a stat id that was not supplied (enforced 502)."""

    def __init__(self, unresolved: list[str]) -> None:
        self.unresolved = unresolved
        super().__init__(f"insight cites unknown stat id(s): {', '.join(unresolved)}")


def taxonomy_categories() -> list[dict[str, str]]:
    """The served taxonomy's categories, read from the REAL plugin registry.

    `GET /v1/taxonomy` reflects `iter_plugins()`; this reads the same source, so
    the analytics category list can never drift from the served descriptor.
    """
    categories: dict[str, str] = {}
    for registered in iter_plugins():
        taxonomy = registered.taxonomy
        if taxonomy is None:
            continue
        for category in taxonomy.categories:
            categories.setdefault(category.id, category.name)
    return [{"id": cid, "name": name} for cid, name in categories.items()]


def _classification_slug_from_assertion(assertion: Assertion | None) -> str | None:
    if assertion is None:
        return None
    try:
        value = json.loads(assertion.value_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    slug = value.get("category")
    return slug if isinstance(slug, str) and slug else None


def _active_expiry_date_from_assertion(assertion: Assertion | None) -> date | None:
    if assertion is None:
        return None
    try:
        value = json.loads(assertion.value_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    raw = value.get("expiry_date")
    if not isinstance(raw, str):
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _bucket_for(expiry: date, as_of: date) -> str:
    if expiry < as_of:
        return "expired"
    if expiry <= as_of + timedelta(days=7):
        return "within_7_days"
    if expiry <= as_of + timedelta(days=30):
        return "within_30_days"
    return "safe"


def _aggregate_assets(
    db: Session, active: list[Asset], taxonomy_ids: list[str], as_of: date
) -> tuple[dict[str, int], int, dict[str, int], int]:
    """Bucket the ACTIVE assets by served category and expiry urgency.

    Performance optimization: Batch load active assertions for all active assets
    in a single database query to prevent N+1 queries during statistics computation.
    """
    category_counts = {category_id: 0 for category_id in taxonomy_ids}
    uncategorized = 0
    expiry = {bucket: 0 for bucket in EXPIRY_BUCKETS}
    expired_untouched = 0

    active_asset_ids = [asset.id for asset in active]
    # Map (asset_id, field_path) -> latest active Assertion
    active_assertions: dict[tuple[str, str], Assertion] = {}
    if active_asset_ids:
        rows = (
            db.query(Assertion)
            .filter(
                Assertion.asset_id.in_(active_asset_ids),
                Assertion.field_path.in_((CLASSIFICATION_FIELD, EXPIRY_FIELD)),
                Assertion.review_state.not_in(("superseded", "rejected")),
            )
            .order_by(Assertion.created_at.asc())
            .all()
        )
        for row in rows:
            active_assertions[(row.asset_id, row.field_path)] = row

    for asset in active:
        class_assertion = active_assertions.get((asset.id, CLASSIFICATION_FIELD))
        slug = _classification_slug_from_assertion(class_assertion)
        if slug is not None and slug in category_counts:
            category_counts[slug] += 1
        else:
            uncategorized += 1

        exp_assertion = active_assertions.get((asset.id, EXPIRY_FIELD))
        expiry_date = _active_expiry_date_from_assertion(exp_assertion)
        if expiry_date is None:
            expiry["unknown"] += 1
            continue
        bucket = _bucket_for(expiry_date, as_of)
        expiry[bucket] += 1
        if bucket == "expired":
            expired_untouched += 1
    return category_counts, uncategorized, expiry, expired_untouched


def compute_stats(db: Session, household_id: str, as_of: date | None = None) -> dict[str, Any]:
    """Deterministic household stats; zero-maps for an empty household (200)."""
    as_of = as_of or datetime.now(timezone.utc).date()
    assets = db.query(Asset).filter(Asset.household_id == household_id).all()
    active = [asset for asset in assets if asset.status == "ACTIVE"]
    by_status = dict(sorted(Counter(asset.status for asset in assets).items()))

    taxonomy = taxonomy_categories()
    category_counts, uncategorized, expiry, expired_untouched = _aggregate_assets(
        db, active, [entry["id"] for entry in taxonomy], as_of
    )

    suggestions = {"pending": 0, "confirmed": 0, "dismissed": 0}
    for status, count in (
        db.query(PlanningSuggestion.status, func.count())
        .filter(PlanningSuggestion.household_id == household_id)
        .group_by(PlanningSuggestion.status)
        .all()
    ):
        suggestions[str(status)] = int(count)
    review_tasks = {"open": 0, "resolved": 0}
    for status, count in (
        db.query(ReviewTask.status, func.count())
        .filter(ReviewTask.household_id == household_id)
        .group_by(ReviewTask.status)
        .all()
    ):
        review_tasks[str(status)] = int(count)

    stats: list[dict[str, Any]] = []

    def add(stat_id: str, label: str, value: Any, source: str) -> None:
        stats.append({"id": stat_id, "label": label, "value": value, "source": source})

    add("assets.total", "Total assets", len(assets), "asset: count(*) WHERE household_id = :h")
    add(
        "assets.active",
        "Active assets",
        len(active),
        "asset: count(*) WHERE household_id = :h AND status = 'ACTIVE'",
    )
    add(
        "assets.by_status",
        "Assets by status",
        by_status,
        "asset: group by status WHERE household_id = :h",
    )
    for entry in taxonomy:
        add(
            f"category.{entry['id']}",
            f"Active assets in {entry['name']}",
            category_counts[entry["id"]],
            "asset JOIN active assertion field_path = "
            f"'{CLASSIFICATION_FIELD}' WHERE value_json.category = '{entry['id']}' "
            "AND asset.status = 'ACTIVE'",
        )
    add(
        "category.uncategorized",
        "Active assets with no served category",
        uncategorized,
        "ACTIVE asset with no active classification assertion carrying a served category id",
    )
    expiry_labels = {
        "expired": "Expired",
        "within_7_days": "Expiring within 7 days",
        "within_30_days": "Expiring within 30 days",
        "safe": "Safe (beyond 30 days)",
        "unknown": "No active expiry date",
    }
    for bucket in EXPIRY_BUCKETS:
        add(
            f"expiry.{bucket}",
            expiry_labels[bucket],
            expiry[bucket],
            "ACTIVE asset JOIN active assertion field_path = "
            f"'{EXPIRY_FIELD}' WHERE expiry_date {_bucket_predicate(bucket)}",
        )
    add(
        "waste.expired_untouched",
        "Expired assets still active",
        expired_untouched,
        "ACTIVE asset whose active expiry_date < as_of",
    )
    for status in ("pending", "confirmed", "dismissed"):
        add(
            f"adherence.suggestions.{status}",
            f"Planning suggestions {status}",
            suggestions[status],
            f"planning_suggestion: count(*) WHERE household_id = :h AND status = '{status}'",
        )
    for status in ("open", "resolved"):
        add(
            f"adherence.review_tasks.{status}",
            f"Review tasks {status}",
            review_tasks[status],
            f"review_task: count(*) WHERE household_id = :h AND status = '{status}'",
        )
    return {
        "household_id": household_id,
        "as_of_date": as_of.isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets": {"total": len(assets), "active": len(active), "by_status": by_status},
        "categories": {
            "taxonomy": taxonomy,
            "counts": category_counts,
            "uncategorized": uncategorized,
        },
        "expiry": expiry,
        "waste": {"expired_untouched": expired_untouched},
        "adherence": {"suggestions": suggestions, "review_tasks": review_tasks},
        "stats": stats,
    }


def _bucket_predicate(bucket: str) -> str:
    if bucket == "expired":
        return "< as_of"
    if bucket == "within_7_days":
        return "BETWEEN as_of AND as_of + 7d"
    if bucket == "within_30_days":
        return "BETWEEN as_of + 7d AND as_of + 30d"
    if bucket == "safe":
        return "> as_of + 30d"
    return "is null or unparseable"


def load_insights_prompt() -> tuple[str, str]:
    """Return (prompt_text, template_version) for the frozen insights prompt."""
    text = (PROMPTS_DIR / INSIGHTS_PROMPT_FILE).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"prompt file missing front matter: {INSIGHTS_PROMPT_FILE}")
    header = text.split("---\n", 2)[1]
    version = ""
    for line in header.splitlines():
        if line.startswith("template_version:"):
            version = line.split(":", 1)[1].strip()
    if not version:
        raise ValueError(f"prompt file missing template_version: {INSIGHTS_PROMPT_FILE}")
    return text, version


def _carrier_png() -> bytes:
    """A 1x1 white PNG: the shared vision surface requires image bytes.

    As in the SG-037 planning agent, the analytics task is entirely in the prompt
    text; the carrier carries no data and is redacted by the adapter exactly like
    a real upload.
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
    db: Session, provider_id: str, model_id: str, version: str, prompt: str, result: Any
) -> ProviderCall:
    row = ProviderCall(
        provider=provider_id,
        model=str(result.model_id or model_id),
        prompt_template_version=version,
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
    db: Session,
    provider_id: str,
    model_id: str,
    version: str,
    prompt: str,
    kind: str,
    message: str,
    usage: dict[str, Any] | None = None,
    cost: float | None = None,
    latency_ms: float | None = None,
) -> ProviderCall:
    """Persist a failed insights call, recording what the exception CARRIED.

    Same split as planning/chat: a post-body failure carries real usage/cost on
    the raised `ProviderError` and it is recorded verbatim; a bare failure stays
    honest `0.0`/`None`. Nothing is invented.
    """
    row = ProviderCall(
        provider=provider_id,
        model=model_id,
        prompt_template_version=version,
        input_hashes=json.dumps({"prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest()}),
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


def _run_provider(
    db: Session,
    provider: Any,
    provider_id: str,
    model_id: str,
    version: str,
    router: ProviderRouter,
    carrier: bytes,
    prompt: str,
) -> tuple[ExtractionOutput | None, list[str], str | None, Any]:
    """One logical call with at most one repair turn (§5.3 shape)."""
    estimate = _estimate(provider, carrier, prompt)
    call_ids: list[str] = []
    last_error: str | None = None
    last_result: Any = None
    for attempt in (1, 2):
        call_prompt = prompt if attempt == 1 else _repair_prompt(prompt)
        try:
            result = router.execute(
                INSIGHTS_OPERATION, carrier, call_prompt, estimated_cost=estimate
            )
        except BudgetExceededError:
            raise
        except ProviderError as exc:
            row = _write_error_ledger(
                db,
                provider_id,
                model_id,
                version,
                call_prompt,
                exc.kind,
                str(exc),
                usage=getattr(exc, "usage", None),
                cost=getattr(exc, "cost", None),
                latency_ms=getattr(exc, "latency_ms", None),
            )
            call_ids.append(row.id)
            last_error = f"{exc.kind}: {exc}"
            continue
        except PydanticValidationError as exc:
            row = _write_error_ledger(
                db, provider_id, model_id, version, call_prompt, "invalid_json", str(exc)
            )
            call_ids.append(row.id)
            last_error = f"invalid_json: {exc}"
            continue
        try:
            output = ExtractionOutput.model_validate(result.normalized_output)
        except PydanticValidationError as exc:
            row = _write_error_ledger(
                db, provider_id, model_id, version, call_prompt, "invalid_json", str(exc)
            )
            call_ids.append(row.id)
            last_error = f"invalid_json: {exc}"
            continue
        row = _write_ledger(db, provider_id, model_id, version, call_prompt, result)
        call_ids.append(row.id)
        return output, call_ids, None, result
    return None, call_ids, last_error, last_result


def _resolve_citations(
    items: list[ExtractionItem], stats: list[dict[str, Any]]
) -> tuple[list[str], list[str]]:
    """Split cited stat ids into (resolved, unresolved), preserving order."""
    supplied = {entry["id"] for entry in stats}
    cited: list[str] = []
    for item in items:
        if item.lot and item.lot not in cited:
            cited.append(item.lot)
    unresolved = [stat_id for stat_id in cited if stat_id not in supplied]
    return cited, unresolved


def run_insights(db: Session, household_id: str) -> dict[str, Any]:
    """Run one manual Analytics Insight pass. Consent gates it; nothing executes."""
    if db.query(Household).filter_by(id=household_id).first() is None:
        raise LookupError(household_id)

    enabled, reason = reader_mod.ai_status()
    if not enabled:
        return {
            "status": "skipped",
            "reason": reason,
            "summary": None,
            "sentences": [],
            "cited_stat_ids": [],
            "provider_call_ids": [],
        }

    stats = compute_stats(db, household_id)
    if stats["assets"]["total"] == 0:
        event = GuardrailEvent(
            household_id=household_id,
            kind="insight",
            ref_ids_json=json.dumps([]),
            detail_json=json.dumps({"outcome": "empty_household", "sentence_count": 0}),
        )
        db.add(event)
        db.commit()
        return {
            "status": "ok",
            "reason": "empty_household",
            "summary": None,
            "sentences": [],
            "cited_stat_ids": [],
            "provider": None,
            "model": None,
            "provider_call_ids": [],
            "guardrail_event_id": event.id,
        }

    prompt_text, version = load_insights_prompt()
    base_prompt = prompt_text + "\n\n## Stats\n" + json.dumps(stats["stats"], ensure_ascii=False)

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
        output, call_ids, error, result = _run_provider(
            db, provider, provider_id, model_id, version, router, carrier, base_prompt
        )
    except BudgetExceededError as exc:
        return {
            "status": "refused",
            "reason": str(exc),
            "summary": None,
            "sentences": [],
            "cited_stat_ids": [],
            "provider_call_ids": [],
        }

    if output is None:
        db.commit()
        return {
            "status": "error",
            "reason": error or "provider_failed",
            "summary": None,
            "sentences": [],
            "cited_stat_ids": [],
            "provider": provider_id,
            "model": model_id,
            "provider_call_ids": call_ids,
        }

    sentences = [item.name for item in output.items]
    cited, unresolved = _resolve_citations(output.items, stats["stats"])
    if not sentences or not cited or unresolved:
        resolution = "unresolved_citations" if unresolved else "no_citations"
        unresolved_ids = unresolved or []
        event = GuardrailEvent(
            household_id=household_id,
            kind="insight",
            ref_ids_json=json.dumps([]),
            detail_json=json.dumps(
                {
                    "outcome": "ungrounded",
                    "resolution": resolution,
                    "unresolved_stat_ids": unresolved_ids,
                    "cited_stat_ids": cited,
                    "provider": provider_id,
                    "model": model_id,
                    "prompt_template_version": version,
                }
            ),
        )
        db.add(event)
        db.commit()
        return {
            "status": "ungrounded",
            "reason": f"insight rejected: {resolution}",
            "summary": None,
            "sentences": sentences,
            "cited_stat_ids": cited,
            "unresolved_stat_ids": unresolved_ids,
            "provider": provider_id,
            "model": model_id,
            "provider_call_ids": call_ids,
            "guardrail_event_id": event.id,
        }

    cited_set = set(cited)
    cited_stats = [
        {"id": entry["id"], "label": entry["label"], "value": entry["value"]}
        for entry in stats["stats"]
        if entry["id"] in cited_set
    ]
    summary = " ".join(sentences)
    event = GuardrailEvent(
        household_id=household_id,
        kind="insight",
        ref_ids_json=json.dumps([]),
        detail_json=json.dumps(
            {
                "outcome": "ok",
                "sentence_count": len(sentences),
                "cited_stat_ids": cited,
                "provider": provider_id,
                "model": model_id,
                "prompt_template_version": version,
                "stat_count": len(stats["stats"]),
            }
        ),
    )
    db.add(event)
    db.commit()
    return {
        "status": "ok",
        "reason": None,
        "summary": summary,
        "sentences": sentences,
        "cited_stat_ids": cited,
        "cited_stats": cited_stats,
        "provider": provider_id,
        "model": model_id,
        "provider_call_ids": call_ids,
        "guardrail_event_id": event.id,
        "usage": result.usage if result is not None else {},
        "cost": result.cost if result is not None else 0.0,
        "latency_ms": result.latency_ms if result is not None else 0.0,
    }
