from __future__ import annotations

import datetime
import json
from collections.abc import Mapping
from pathlib import Path

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.config import settings
from app.db import Base
from app.models.asset import Asset
from app.models.assertion import Assertion
from app.models.evidence import Evidence, asset_evidence
from app.models.job import Job, JobStep
from app.models.review_task import ReviewTask
from app.models.base import TimestampMixin, new_id
from app.services import audit_service, lifecycle
from app.services.enrich import scoring as enrich_scoring
from app.services.enrich.jina import SOURCE_NAME as JINA_SOURCE_NAME
from app.services.enrich.jina import EnrichDecisionRecord
from app.services.google_taxonomy import RESOLVED, bucket_for, resolve_google_type
from app.services.observations import Observation
from app.services.providers.schemas import ExtractionOutput

# SG-082: web-sourced candidate fields. `source_type` is `web:<source>` per the
# spec §1/§3; web data is ALWAYS a gated proposal, never auto-accepted.
WEB_SOURCE_PREFIX = "web:"
OFF_WEB_SOURCE = f"{WEB_SOURCE_PREFIX}OpenFoodFacts"
JINA_WEB_SOURCE = f"{WEB_SOURCE_PREFIX}{JINA_SOURCE_NAME}"

# Label-visible fields: a label photo (extraction) or deterministic value WINS;
# web fills the gap. When both exist the web value is preserved as a visible
# alternate with its source, never silently dropped (spec §4).
LABEL_VISIBLE_FIELDS = frozenset(
    {
        # SG-119: OFF `brands` joins the label-wins vocabulary so a label brand
        # and a web brand stay BOTH visible (the label wins the proposal, the web
        # value becomes its alternate). Brand-absent assets still gap-fill per the
        # standing rule; see `map_off_decision_fields` for the decision.
        "brand",
        "display_name",
        "asset_type",
        "quantity",
        "unit",
        "condition",
        "identifier",
        "expiry",
        "expiry_date",
        "opened_date",
        "lot",
    }
)

# SG-082 category activation: a Jina result's retailer domain maps to a
# category slug. Reported and uncalibrated (`G-A9`); the agreement rule reuses
# `enrich_scoring.category_score` (exact/contains) against the caller category.
JINA_DOMAIN_CATEGORIES: dict[str, str] = {
    "farmaciatei.ro": "medicine_pharma",
    "mega-image.ro": "food_beverages",
    "emag.ro": "household_chemicals",
}

# SG-028 §5.2-7: safety-critical/serialized fields always route to review,
# whatever the confidence. Every other field auto-accepts at/above the single
# configured threshold (`settings.sg_confidence_threshold`, uncalibrated).
GATED_FIELDS = frozenset(
    {
        "identifier",
        "expiry",
        "expiry_date",
        "opened_date",
        "condition",
        "lot",
        # SG-049 v2: extraction-sourced quantity/unit/asset_type are always
        # human-confirmed (F4 Stage 0), never threshold-auto-accepted.
        "quantity",
        "unit",
        "asset_type",
        # SG-080 G3: the extraction-proposed category is always a proposal,
        # never threshold-auto-accepted at any confidence.
        "category_proposed",
        # SG-095: the resolved Google-taxonomy kind rides beside the category as
        # gated proposals (spec S2/D111); never threshold-auto-accepted.
        "google_type_id",
        "google_type_path",
        "taxonomy_version",
    }
)
ALLOWED_CANDIDATE_FIELDS = frozenset(
    {
        # SG-119: the label-wins brand (and a brand-absent gap-fill) can reach the
        # committed assertion; a web-sourced brand always commits `proposed`.
        "brand",
        "display_name",
        "asset_type",
        "status",
        "quantity",
        "unit",
        "condition",
        "identifier",
        "expiry",
        "expiry_date",
        "opened_date",
        "lot",
        # SG-080 G3: category_proposed is the ONE promoted v3 field, whitelisted
        # so the gated proposal can reach the committed assertion.
        "category_proposed",
        # SG-095: the Google-taxonomy triple, promoted so the gated kind reaches
        # the committed assertion; the triple is stored together, nullable together.
        "google_type_id",
        "google_type_path",
        "taxonomy_version",
    }
)

# SG-095: the version-stamped Google kind triple. When the resolver returns
# `resolved` all three ride together; `unclear`/`uncategorized` produce none
# (the alternatives stay on `google_type_resolution` for the reviewer).
GOOGLE_TYPE_FIELDS = ("google_type_id", "google_type_path", "taxonomy_version")


def _field_parts(raw: object) -> tuple[object, dict[str, object] | None]:
    """Split a candidate field into (value, provenance-envelope or None).

    AI candidate fields carry the provenance object CandidateCard.fieldInfo
    already renders; deterministic Phase-1 fields are plain scalars.
    """
    if isinstance(raw, dict) and "source_type" in raw:
        return raw.get("value"), raw
    return raw, None


def _provenance(
    value: object,
    *,
    source_type: str,
    confidence: float | None = None,
    provider: object = None,
    model: object = None,
    template_version: object = None,
    provider_call_id: object = None,
) -> dict[str, object]:
    return {
        "value": value,
        "confidence": confidence,
        "source_type": source_type,
        "provider": provider,
        "model": model,
        "prompt_template_version": template_version,
        "provider_call_id": provider_call_id,
    }


def _extraction_value_field(
    fields: dict[str, object],
    name: str,
    value: object,
    *,
    item: object,
    provider: object,
    model: object,
    template_version: object,
    provider_call_id: object,
) -> None:
    """Add an extraction-sourced field unless its value is absent (never guessed)."""
    if value is None:
        return
    fields[name] = _provenance(
        value,
        source_type="extraction",
        confidence=item.confidence,  # type: ignore[attr-defined]
        provider=provider,
        model=model,
        template_version=template_version,
        provider_call_id=provider_call_id,
    )


def _review_state_for(field_path: str, confidence: float | None) -> str:
    if field_path in GATED_FIELDS:
        return "proposed"
    if confidence is not None and confidence < settings.sg_confidence_threshold:
        return "proposed"
    return "accepted"


# --------------------------------------------------------------------------- #
# SG-095 — Google-taxonomy resolution (one item's free-text path -> triple)
# --------------------------------------------------------------------------- #
def _google_type_resolution(item: object) -> dict[str, object]:
    """Resolve one item's proposal into the version-stamped Google kind (SG-095).

    A pure resolver call (offline, deterministic, no threshold of its own). When
    the status is `resolved` the triple is stored together; `unclear` keeps the
    resolver's top-k `alternatives` for the reviewer and maps none of them. The
    `bucket` is the map's SUGGESTION only -- the six expiry buckets remain the
    behaviour authority (D111).
    """
    resolution = resolve_google_type(getattr(item, "google_type_proposed", None))
    return {
        "status": resolution.status,
        "google_type_id": resolution.google_type_id,
        "google_type_path": resolution.google_type_path,
        "taxonomy_version": resolution.taxonomy_version,
        "score": resolution.score,
        "margin": resolution.margin,
        "alternatives": [list(pair) for pair in resolution.alternatives],
        "bucket": bucket_for(resolution.google_type_id, resolution.google_type_path),
    }


def _apply_google_type_fields(
    fields: dict[str, object],
    item: object,
    *,
    provider: object,
    model: object,
    template_version: object,
    provider_call_id: object,
) -> dict[str, object]:
    """Add the resolved triple to `fields` (all three, or none) and return the resolution."""
    resolution = _google_type_resolution(item)
    if resolution["status"] == RESOLVED:
        for field_name in GOOGLE_TYPE_FIELDS:
            _extraction_value_field(
                fields,
                field_name,
                resolution[field_name],
                item=item,
                provider=provider,
                model=model,
                template_version=template_version,
                provider_call_id=provider_call_id,
            )
    return resolution


def _ai_items_with_resolution(extraction: ExtractionOutput) -> list[dict[str, object]]:
    """Each item's own dump plus its resolution, so a split child keeps its own triple."""
    items: list[dict[str, object]] = []
    for extracted in extraction.items:
        dumped = extracted.model_dump()
        dumped["google_type_resolution"] = _google_type_resolution(extracted)
        items.append(dumped)
    return items


# --------------------------------------------------------------------------- #
# SG-082 — web-source mapping (OFF decision + Jina results -> candidate fields)
# --------------------------------------------------------------------------- #
def _web_provenance(
    value: object,
    *,
    source_type: str,
    source_url: str,
    retrieved_at: str,
) -> dict[str, object]:
    """A web-sourced field envelope: value + `web:<source>` + URL + retrieval date."""
    provenance = _provenance(value, source_type=source_type)
    provenance["source_url"] = source_url
    provenance["retrieved_at"] = retrieved_at
    return provenance


def jina_result_category(result: Mapping[str, object]) -> str | None:
    """The category slug a Jina result's retailer domain supplies, else None."""
    url = str(result.get("url") or "")
    for domain, category in JINA_DOMAIN_CATEGORIES.items():
        if domain in url:
            return category
    return None


def map_off_decision_fields(
    decision: enrich_scoring.MatchDecision,
    *,
    source_url: str,
    retrieved_at: str,
    category: str | None = None,
) -> dict[str, object]:
    """Map an accepted OFF `MatchDecision` into existing candidate fields.

    Only safe identity fields are mapped (`display_name`, accepted exact
    `identifier`, the product `brands`, an agreeing `category_proposed`); every
    value is `web:OpenFoodFacts` with its URL + retrieval date. A non-accepted
    decision maps to nothing (no nearest guess).

    SG-119 brand decision (stated): `brands` is mapped ONLY when the payload
    carries it. An OFF-miss/empty `brands` emits nothing, so the gap stays and no
    brand alternate is fabricated. A brand-absent ASSET is indistinguishable at
    this mapper (it never reads asset state) and gap-fills under `merge_web_fields`;
    `synthesize.py`'s `brand_absent` refusal governs LLM-emitted facts with no
    payload grounding (`parse_synthesis`), and it is not on this deterministic
    mapping path — the OFF snapshot IS the grounding here, so gap-fill wins.
    """
    if not decision.accepted or decision.best is None:
        return {}
    product = decision.best
    fields: dict[str, object] = {}
    name = product.get("product_name")
    if isinstance(name, str) and name:
        fields["display_name"] = _web_provenance(
            name,
            source_type=OFF_WEB_SOURCE,
            source_url=source_url,
            retrieved_at=retrieved_at,
        )
    code = product.get("code")
    if isinstance(code, str) and code:
        fields["identifier"] = _web_provenance(
            code,
            source_type=OFF_WEB_SOURCE,
            source_url=source_url,
            retrieved_at=retrieved_at,
        )
    # SG-119: the OFF payload's `brands` (a string, or a list whose items are
    # joined verbatim) rides the same `web:OpenFoodFacts` envelope. Absent/empty
    # brands emit NO field — never an invented or substituted value.
    brands = product.get("brands")
    brand_value: str | None = None
    if isinstance(brands, str) and brands:
        brand_value = brands
    elif isinstance(brands, (list, tuple)):
        parts = [item for item in brands if isinstance(item, str) and item]
        if parts:
            brand_value = ", ".join(parts)
    if brand_value is not None:
        fields["brand"] = _web_provenance(
            brand_value,
            source_type=OFF_WEB_SOURCE,
            source_url=source_url,
            retrieved_at=retrieved_at,
        )
    if category and enrich_scoring.category_score(
        category, product.get("categories_tags_en")
    ) > 0:
        fields["category_proposed"] = _web_provenance(
            category,
            source_type=OFF_WEB_SOURCE,
            source_url=source_url,
            retrieved_at=retrieved_at,
        )
    return fields


def map_jina_result_fields(
    result: Mapping[str, object],
    *,
    source_url: str,
    retrieved_at: str,
    category: str | None = None,
) -> dict[str, object]:
    """Map one Jina web result into existing candidate fields.

    `title` becomes a proposed `display_name`; a retailer-derived category
    becomes `category_proposed` only when it agrees with the caller's category
    through `category_score` (the activation this slice adds).
    """
    fields: dict[str, object] = {}
    title = result.get("title")
    if isinstance(title, str) and title:
        fields["display_name"] = _web_provenance(
            title,
            source_type=JINA_WEB_SOURCE,
            source_url=source_url,
            retrieved_at=retrieved_at,
        )
    derived = jina_result_category(result)
    if derived and category and enrich_scoring.category_score(category, [derived]) > 0:
        fields["category_proposed"] = _web_provenance(
            derived,
            source_type=JINA_WEB_SOURCE,
            source_url=source_url,
            retrieved_at=retrieved_at,
        )
    return fields


def merge_web_fields(
    existing_fields: dict[str, object], web_fields: dict[str, object]
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Merge web fields into existing fields under the label-wins conflict rule.

    A label-visible field that already has a non-null value keeps it; the web
    value is returned as an alternate with its source (both visible). Every
    other web field fills the gap. Returns `(merged_fields, web_alternates)`.
    """
    merged = dict(existing_fields)
    alternates: list[dict[str, object]] = []
    for field_name, raw in web_fields.items():
        existing_value: object = None
        if field_name in merged:
            existing_value, _ = _field_parts(merged[field_name])
        if (
            field_name in merged
            and field_name in LABEL_VISIBLE_FIELDS
            and existing_value is not None
        ):
            web_value, provenance = _field_parts(raw)
            provenance = provenance or {}
            alternates.append(
                {
                    "field": field_name,
                    "value": web_value,
                    "source_type": provenance.get("source_type"),
                    "source_url": provenance.get("source_url"),
                    "retrieved_at": provenance.get("retrieved_at"),
                }
            )
            continue
        merged[field_name] = raw
    return merged, alternates


def build_enrich_fields(
    record: EnrichDecisionRecord, *, category: str | None = None
) -> dict[str, object]:
    """The web-sourced field set + source list for one decision record.

    OFF first; Jina's top result fills only fields OFF did not provide. Both
    snapshots' sources are listed with URL + retrieval date. Nothing is
    persisted (`PG-SC-02`).
    """
    fields: dict[str, object] = {}
    sources: list[dict[str, object]] = []
    if record.off_decision.accepted:
        fields.update(
            map_off_decision_fields(
                record.off_decision,
                source_url=record.primary.request_url,
                retrieved_at=record.primary.retrieved_at,
                category=category,
            )
        )
        sources.append(
            {
                "source": OFF_WEB_SOURCE,
                "url": record.primary.request_url,
                "retrieved_at": record.primary.retrieved_at,
            }
        )
    fallback = record.fallback
    if fallback is not None and fallback.results:
        jina_fields: dict[str, object] = {}
        for result in fallback.results[:1]:
            jina_fields.update(
                map_jina_result_fields(
                    result,
                    source_url=fallback.request_url,
                    retrieved_at=fallback.retrieved_at,
                    category=category,
                )
            )
        for field_name, raw in jina_fields.items():
            if field_name not in fields:
                fields[field_name] = raw
        sources.append(
            {
                "source": JINA_WEB_SOURCE,
                "url": fallback.request_url,
                "retrieved_at": fallback.retrieved_at,
            }
        )
    return {"fields": fields, "sources": sources}


def apply_web_fields_to_proposal(
    proposal: dict[str, object], record: EnrichDecisionRecord, *, category: str | None = None
) -> dict[str, object]:
    """Merge web fields into a candidate proposal's `fields` (in-memory only).

    The web alternates are attached under `web_alternates` so a label-wins
    conflict keeps BOTH values visible with sources. The proposal stays
    JSON-serialisable; no datastore field is written.
    """
    web = build_enrich_fields(record, category=category)
    web_fields = web["fields"]
    if not isinstance(web_fields, dict):
        return proposal
    existing = _asset_fields(proposal)
    merged, alternates = merge_web_fields(existing, web_fields)
    updated = dict(proposal)
    updated["fields"] = merged
    updated["web_alternates"] = alternates
    updated["web_sources"] = web["sources"]
    return updated


class Candidate(TimestampMixin, Base):
    __tablename__ = "candidate"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_fields_json: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(String(30), nullable=False, default="proposed")
    household_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("household.id", ondelete="CASCADE"), nullable=False, index=True
    )


class CandidateBlockedError(RuntimeError):
    pass


class CandidateSplitError(RuntimeError):
    """A split request the operation refuses; `status_code` is the HTTP mapping."""

    def __init__(self, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.status_code = status_code


class CandidateMergeError(RuntimeError):
    """A merge request the operation refuses; `status_code` is the HTTP mapping."""

    def __init__(self, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.status_code = status_code


SPLIT_ORIGIN_STATE = "split"
MERGED_STATE = "merged"

# SG-112: the review-task types a merge RESOLVES on a losing candidate. Every
# other open task type blocks a merge so an unrelated pending decision is never
# silently dropped; the duplicate-identifier collision task IS the duplicate
# question a merge answers, so it resolves with an audit row (the split
# precedent's `candidate.multi_item` shape, `candidates.py:1096`).
MERGE_RESOLVED_TASK_TYPES: tuple[str, ...] = ("identifier_collision",)


def load_proposal(candidate: Candidate) -> dict[str, object]:
    value = json.loads(candidate.proposed_fields_json)
    if not isinstance(value, dict):
        raise ValueError("candidate proposal must be an object")
    return value


def _asset_fields(proposal: dict[str, object]) -> dict[str, object]:
    fields = proposal.get("fields", {})
    if not isinstance(fields, dict):
        raise ValueError("candidate fields must be an object")
    return dict(fields)


def _job_evidence_ids(db: Session, job_id: str) -> list[str]:
    job = db.query(Job).filter_by(id=job_id).first()
    if job is None:
        return []
    config = json.loads(job.config_snapshot or "{}")
    value = config.get("evidence_ids", [])
    if not isinstance(value, list):
        raise ValueError("invalid evidence_ids in job config")
    return [str(item) for item in value]


def _observation_ids(db: Session, job_id: str) -> list[str]:
    step = (
        db.query(JobStep)
        .filter_by(job_id=job_id, step_name="EXTRACTING_DETERMINISTIC_SIGNALS")
        .first()
    )
    if step is None or not step.output_refs:
        return []
    output = json.loads(step.output_refs)
    value = output.get("observation_ids", []) if isinstance(output, dict) else []
    return [str(item) for item in value] if isinstance(value, list) else []


def _step_output(db: Session, job_id: str, step_name: str) -> dict[str, object] | None:
    step = db.query(JobStep).filter_by(job_id=job_id, step_name=step_name).first()
    if step is None or not step.output_refs:
        return None
    value = json.loads(step.output_refs)
    return value if isinstance(value, dict) else None


def _deterministic_display_name(db: Session, evidence_ids: list[str]) -> str:
    if not evidence_ids:
        return "Imported item"
    evidence = db.get(Evidence, evidence_ids[0])
    if evidence is None:
        return "Imported item"
    return Path(evidence.original_filename).stem or evidence.original_filename


def _barcode_identifier(db: Session, evidence_ids: list[str]) -> str | None:
    if not evidence_ids:
        return None
    rows = (
        db.query(Observation)
        .filter(Observation.evidence_id.in_(evidence_ids), Observation.kind == "barcode_qr")
        .all()
    )
    for row in rows:
        value = json.loads(row.value_json)
        if isinstance(value, dict) and value.get("validated") is True and value.get("value"):
            return str(value["value"])
    return None


def build_candidate_from_extraction(
    db: Session,
    job: Job,
    extraction: ExtractionOutput,
    analyzing: dict[str, object],
) -> Candidate:
    """Form the candidate from deterministic signals + validated AI output.

    Fields carry the per-field provenance object CandidateCard.fieldInfo already
    renders; the full AI item list and unknowns are preserved on the proposal
    so nothing the provider returned is dropped.
    """
    evidence_ids = _job_evidence_ids(db, job.id)
    provider = analyzing.get("provider")
    model = analyzing.get("model")
    version = analyzing.get("prompt_template_version")
    raw_calls = analyzing.get("provider_call_ids", [])
    call_ids = [str(item) for item in raw_calls] if isinstance(raw_calls, list) else []
    primary_call = call_ids[0] if call_ids else None

    fields: dict[str, object] = {
        "display_name": _provenance(
            _deterministic_display_name(db, evidence_ids), source_type="deterministic"
        ),
        "asset_type": _provenance("unknown", source_type="deterministic"),
        "status": _provenance(lifecycle.ACTIVE, source_type="deterministic"),
    }
    identifier = _barcode_identifier(db, evidence_ids)
    if identifier is not None:
        fields["identifier"] = _provenance(identifier, source_type="deterministic")
    primary_resolution: dict[str, object] | None = None
    if extraction.items:
        item = extraction.items[0]
        fields["display_name"] = _provenance(
            item.name,
            source_type="extraction",
            confidence=item.confidence,
            provider=provider,
            model=model,
            template_version=version,
            provider_call_id=primary_call,
        )
        if item.expiry_date is not None:
            fields["expiry_date"] = _provenance(
                item.expiry_date,
                source_type="extraction",
                confidence=item.confidence,
                provider=provider,
                model=model,
                template_version=version,
                provider_call_id=primary_call,
            )
        if item.opened_date is not None:
            fields["opened_date"] = _provenance(
                item.opened_date,
                source_type="extraction",
                confidence=item.confidence,
                provider=provider,
                model=model,
                template_version=version,
                provider_call_id=primary_call,
            )
        if item.lot is not None:
            fields["lot"] = _provenance(
                item.lot,
                source_type="extraction",
                confidence=item.confidence,
                provider=provider,
                model=model,
                template_version=version,
                provider_call_id=primary_call,
            )
        for field_name, value in (
            ("quantity", item.quantity),
            ("unit", item.unit),
            ("asset_type", item.asset_type),
            # SG-080 G3: category_proposed rides the candidate as a gated
            # proposal (always review_state="proposed" at commit).
            ("category_proposed", item.category_proposed),
        ):
            _extraction_value_field(
                fields,
                field_name,
                value,
                item=item,
                provider=provider,
                model=model,
                template_version=version,
                provider_call_id=primary_call,
            )
        # SG-095: the primary item's Google path resolves to the version-stamped
        # triple, which rides as gated fields (all three, or none at all).
        primary_resolution = _apply_google_type_fields(
            fields,
            item,
            provider=provider,
            model=model,
            template_version=version,
            provider_call_id=primary_call,
        )

    # SG-095: every item's own resolution travels with it, so a split child can
    # promote its own triple without inheriting the primary's.
    ai_items = _ai_items_with_resolution(extraction)

    proposal: dict[str, object] = {
        "kind": "new_asset",
        "asset_id": None,
        "fields": fields,
        "dedup_matches": [],
        "review_task_ids": [],
        "google_type_resolution": primary_resolution,
        "ai_items": ai_items,
        "ai_unknowns": list(extraction.unknowns),
        "needs_evidence": extraction.needs_evidence,
        "ai_provider": provider,
        "ai_model": model,
        "prompt_template_version": version,
        "provider_call_ids": call_ids,
    }
    candidate = Candidate(
        job_id=job.id,
        evidence_ids_json=json.dumps(evidence_ids),
        proposed_fields_json=json.dumps(proposal, ensure_ascii=False),
        state="proposed",
        household_id=job.household_id or "",
    )
    db.add(candidate)
    db.flush()

    task_ids: list[str] = []
    if len(extraction.items) > 1:
        task = ReviewTask(
            task_type="candidate.multi_item",
            priority="high",
            subject_ref=candidate.id,
            proposed_change=json.dumps(
                {"candidate_id": candidate.id, "item_count": len(extraction.items)}
            ),
            status="open",
            household_id=job.household_id,
        )
        db.add(task)
        db.flush()
        task_ids.append(task.id)
    if extraction.needs_evidence:
        task = ReviewTask(
            task_type="expiry.manual_entry",
            priority="high",
            subject_ref=candidate.id,
            proposed_change=json.dumps(
                {"candidate_id": candidate.id, "prompt": "Enter expiry date manually"}
            ),
            status="open",
            household_id=job.household_id,
        )
        db.add(task)
        db.flush()
        task_ids.append(task.id)
    proposal["review_task_ids"] = task_ids
    candidate.proposed_fields_json = json.dumps(proposal, ensure_ascii=False)
    db.flush()
    return candidate


def build_candidates_step(db: Session, job: Job) -> dict[str, object]:
    analyzing = _step_output(db, job.id, "ANALYZING_WITH_AI")
    if not analyzing or analyzing.get("status") != "ok":
        reason = str(analyzing.get("reason", "no_ai_output")) if analyzing else "no_ai_output"
        return {"status": "skipped", "step": "BUILDING_CANDIDATES", "reason": reason}
    raw_extraction = analyzing.get("extraction")
    if not isinstance(raw_extraction, dict):
        raise ValueError("AI step output is missing the validated extraction")
    extraction = ExtractionOutput.model_validate(raw_extraction)
    candidate = build_candidate_from_extraction(db, job, extraction, analyzing)
    return {
        "status": "ok",
        "step": "BUILDING_CANDIDATES",
        "candidate_id": candidate.id,
        "item_count": len(extraction.items),
        "review_task_ids": load_proposal(candidate).get("review_task_ids", []),
    }


def _assertion_source(
    field_path: str,
    provenance: dict[str, object] | None,
    *,
    evidence_ids: list[str],
    observation_ids: list[str],
) -> tuple[str, float | None, str | None, str]:
    """Resolve `(source_type, confidence, model_json, review_state)` for a field.

    SG-082 adds the `web:<source>` branch: web data is ALWAYS a proposal at
    every confidence (no threshold can promote it); attribution rides
    `model_json`. Extraction keeps its SG-028 behaviour; deterministic fields
    keep the plain-threshold rule.
    """
    confidence: float | None = None
    source_type = "deterministic"
    model_json: str | None = None
    if provenance is not None:
        raw_confidence = provenance.get("confidence")
        confidence = float(raw_confidence) if isinstance(raw_confidence, (int, float)) else None
        raw_source = provenance.get("source_type")
        if raw_source == "extraction":
            source_type = "extraction"
            model_json = json.dumps(
                {
                    "provider": provenance.get("provider"),
                    "model": provenance.get("model"),
                    "prompt_template_version": provenance.get("prompt_template_version"),
                    "provider_call_id": provenance.get("provider_call_id"),
                    "evidence_ids": evidence_ids,
                    "observation_ids": observation_ids,
                },
                ensure_ascii=False,
            )
        elif isinstance(raw_source, str) and raw_source.startswith(WEB_SOURCE_PREFIX):
            source_type = raw_source
            confidence = None
            model_json = json.dumps(
                {
                    "web_source": raw_source,
                    "source_url": provenance.get("source_url"),
                    "retrieved_at": provenance.get("retrieved_at"),
                },
                ensure_ascii=False,
            )
    if source_type.startswith(WEB_SOURCE_PREFIX):
        review_state = "proposed"
    else:
        review_state = _review_state_for(
            field_path, confidence if source_type == "extraction" else None
        )
    return source_type, confidence, model_json, review_state


def _create_asset_for_candidate(db: Session, candidate: Candidate) -> Asset:
    proposal = load_proposal(candidate)
    fields = _asset_fields(proposal)
    evidence_ids = json.loads(candidate.evidence_ids_json)
    if not isinstance(evidence_ids, list):
        raise ValueError("candidate evidence_ids must be a list")
    evidence_ids = [str(item) for item in evidence_ids]
    evidence_rows = db.query(Evidence).filter(Evidence.id.in_(evidence_ids)).all() if evidence_ids else []
    if len(evidence_rows) != len(set(evidence_ids)) or any(
        row.household_id != candidate.household_id for row in evidence_rows
    ):
        raise ValueError("candidate evidence does not belong to its household")

    display, _ = _field_parts(fields.get("display_name"))
    asset_type, _ = _field_parts(fields.get("asset_type"))
    status, _ = _field_parts(fields.get("status"))
    quantity, _ = _field_parts(fields.get("quantity"))
    unit, _ = _field_parts(fields.get("unit"))
    condition, _ = _field_parts(fields.get("condition"))
    asset = Asset(
        household_id=candidate.household_id,
        display_name=str(display or "Imported item"),
        asset_type=str(asset_type or "unknown"),
        status=str(status or lifecycle.ACTIVE),
        quantity=quantity,
        unit=unit,
        condition=condition,
    )
    db.add(asset)
    db.flush()

    observation_ids = _observation_ids(db, candidate.job_id)
    for field_path, raw in fields.items():
        value, provenance = _field_parts(raw)
        if value is None:
            continue
        if field_path not in ALLOWED_CANDIDATE_FIELDS:
            raise ValueError(f"unsupported candidate field: {field_path}")
        source_type, confidence, model_json, review_state = _assertion_source(
            field_path,
            provenance,
            evidence_ids=evidence_ids,
            observation_ids=observation_ids,
        )
        db.add(
            Assertion(
                asset_id=asset.id,
                field_path=field_path,
                value_json=json.dumps(value, ensure_ascii=False),
                source_type=source_type,
                confidence=confidence,
                review_state=review_state,
                source_evidence_ids=json.dumps(evidence_ids),
                model_json=model_json,
            )
        )

    for evidence_id in evidence_ids:
        db.execute(asset_evidence.insert().values(asset_id=asset.id, evidence_id=evidence_id))

    audit_service.record(
        db,
        actor="import-runner",
        action="asset.create",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after={"candidate_id": candidate.id, "fields": fields},
        household_id=candidate.household_id,
    )
    audit_service.record(
        db,
        actor="import-runner",
        action="asset.accepted",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after={"review_state": "accepted", "candidate_id": candidate.id},
        household_id=candidate.household_id,
    )
    audit_service.record(
        db,
        actor="import-runner",
        action="asset.lifecycle.created",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after={"event_type": "created", "source": "deterministic", "candidate_id": candidate.id},
        household_id=candidate.household_id,
    )
    return asset


def commit_candidate(db: Session, candidate: Candidate) -> dict[str, object]:
    if candidate.state not in {"accepted", "edited"}:
        raise CandidateBlockedError(f"candidate state {candidate.state} is not committable")
    open_tasks = (
        db.query(ReviewTask)
        .filter(
            ReviewTask.subject_ref == candidate.id,
            ReviewTask.household_id == candidate.household_id,
            ReviewTask.status == "open",
        )
        .all()
    )
    if open_tasks:
        raise CandidateBlockedError("candidate has unresolved review tasks")

    proposal = load_proposal(candidate)
    if proposal.get("kind") == "duplicate_of_asset":
        asset_id = proposal.get("asset_id")
        if not isinstance(asset_id, str):
            raise ValueError("duplicate proposal is missing asset_id")
        return {"status": "duplicate_linked", "asset_id": asset_id, "created": False}

    asset = _create_asset_for_candidate(db, candidate)
    db.flush()
    return {"status": "committed", "asset_id": asset.id, "created": True}


def commit_job_candidate(db: Session, job: Job) -> dict[str, object]:
    candidate = db.query(Candidate).filter_by(job_id=job.id).order_by(Candidate.created_at).first()
    if candidate is None:
        raise ValueError("job has no candidate")
    result = commit_candidate(db, candidate)
    return {"status": "ok", "step": "COMMITTING", "candidate_id": candidate.id, **result}


def _split_child_fields(
    origin_fields: dict[str, object],
    item: dict[str, object],
    *,
    provider: object,
    model: object,
    version: object,
    provider_call_id: object,
) -> dict[str, object]:
    """Build one child's fields from the origin fields + ITS extraction item.

    Item-derived fields (`display_name`, `expiry_date`, `opened_date`, `lot`,
    `quantity`, `unit`, `asset_type`) are replaced by this item's values; every
    other origin field (status, barcode identifier) is shared unchanged. A field
    with no item value is omitted, never guessed and never inherited.
    """
    name = item.get("name")
    if not isinstance(name, str) or not name:
        raise CandidateSplitError("candidate item is missing a name")
    raw_confidence = item.get("confidence")
    confidence = raw_confidence if isinstance(raw_confidence, (int, float)) else None
    item_derived = {
        "display_name",
        "expiry_date",
        "opened_date",
        "lot",
        "quantity",
        "unit",
        "asset_type",
        "category_proposed",
        "google_type_id",
        "google_type_path",
        "taxonomy_version",
    }
    fields: dict[str, object] = {
        key: raw for key, raw in origin_fields.items() if key not in item_derived
    }
    fields["display_name"] = _provenance(
        name,
        source_type="extraction",
        confidence=confidence,
        provider=provider,
        model=model,
        template_version=version,
        provider_call_id=provider_call_id,
    )
    for field_name in (
        "expiry_date",
        "opened_date",
        "lot",
        "quantity",
        "unit",
        "asset_type",
        "category_proposed",
    ):
        value = item.get(field_name)
        if value is not None:
            fields[field_name] = _provenance(
                value,
                source_type="extraction",
                confidence=confidence,
                provider=provider,
                model=model,
                template_version=version,
                provider_call_id=provider_call_id,
            )
    # SG-095: promote THIS item's own resolved Google triple, never the origin's.
    resolution = item.get("google_type_resolution")
    if isinstance(resolution, dict) and resolution.get("status") == RESOLVED:
        for field_name in GOOGLE_TYPE_FIELDS:
            value = resolution.get(field_name)
            if value is not None:
                fields[field_name] = _provenance(
                    value,
                    source_type="extraction",
                    confidence=confidence,
                    provider=provider,
                    model=model,
                    template_version=version,
                    provider_call_id=provider_call_id,
                )
    return fields


def split_candidate(
    db: Session, candidate: Candidate, item_indexes: list[int]
) -> tuple[list[Candidate], list[str]]:
    """Split a multi-item candidate into one `proposed` child per named item.

    The request must name every item index exactly once (>= 2 items): a partial
    or single selection is refused before anything is written so no item is
    silently dropped. Children share the origin evidence and provider
    provenance; the origin leaves the decidable set and its `candidate.multi_item`
    task(s) resolve. The caller commits.
    """
    if candidate.state != "proposed":
        raise CandidateSplitError(
            f"candidate state {candidate.state} is not splittable", status_code=409
        )
    proposal = load_proposal(candidate)
    items = proposal.get("ai_items")
    if not isinstance(items, list) or len(items) < 2:
        raise CandidateSplitError("candidate has no multi-item list to split", status_code=422)
    if not isinstance(item_indexes, list) or any(
        isinstance(index, bool) or not isinstance(index, int) for index in item_indexes
    ):
        raise CandidateSplitError("item_indexes must be a list of integers", status_code=422)
    if len(item_indexes) < 2:
        raise CandidateSplitError("split requires at least two item indexes", status_code=422)
    if len(set(item_indexes)) != len(item_indexes):
        raise CandidateSplitError("item_indexes must be unique", status_code=422)
    if set(item_indexes) != set(range(len(items))):
        raise CandidateSplitError(
            "item_indexes must name every item exactly once", status_code=422
        )

    origin_fields = _asset_fields(proposal)
    provider = proposal.get("ai_provider")
    model = proposal.get("ai_model")
    version = proposal.get("prompt_template_version")
    raw_calls = proposal.get("provider_call_ids", [])
    call_ids = [str(item) for item in raw_calls] if isinstance(raw_calls, list) else []
    primary_call = call_ids[0] if call_ids else None
    raw_unknowns = proposal.get("ai_unknowns", [])
    unknowns = [str(entry) for entry in raw_unknowns] if isinstance(raw_unknowns, list) else []

    children: list[Candidate] = []
    for index in item_indexes:
        item = items[index]
        if not isinstance(item, dict):
            raise CandidateSplitError("candidate item is invalid", status_code=422)
        prefix = f"items.{index}."
        child_unknowns = [
            f"items.0.{entry[len(prefix):]}"
            for entry in unknowns
            if entry.startswith(prefix)
        ]
        child_proposal: dict[str, object] = {
            "kind": "new_asset",
            "asset_id": None,
            "fields": _split_child_fields(
                origin_fields,
                item,
                provider=provider,
                model=model,
                version=version,
                provider_call_id=primary_call,
            ),
            "dedup_matches": [],
            "review_task_ids": [],
            "ai_items": [item],
            "ai_unknowns": child_unknowns,
            "needs_evidence": bool(child_unknowns),
            "ai_provider": provider,
            "ai_model": model,
            "prompt_template_version": version,
            "provider_call_ids": call_ids,
            "split_from": candidate.id,
            "split_item_index": index,
        }
        child = Candidate(
            job_id=candidate.job_id,
            evidence_ids_json=candidate.evidence_ids_json,
            proposed_fields_json=json.dumps(child_proposal, ensure_ascii=False),
            state="proposed",
            household_id=candidate.household_id,
        )
        db.add(child)
        children.append(child)
    db.flush()

    candidate.state = SPLIT_ORIGIN_STATE
    resolved_task_ids: list[str] = []
    open_tasks = (
        db.query(ReviewTask)
        .filter_by(
            subject_ref=candidate.id,
            household_id=candidate.household_id,
            task_type="candidate.multi_item",
            status="open",
        )
        .all()
    )
    for task in open_tasks:
        before = {"status": task.status}
        task.status = "resolved"
        task.updated_at = datetime.datetime.now(datetime.timezone.utc)
        audit_service.record(
            db,
            actor="api",
            action="review_task.resolve",
            entity_type="review_task",
            entity_id=task.id,
            before=before,
            after={"status": task.status, "resolution": {"split": candidate.id}},
            household_id=task.household_id,
        )
        resolved_task_ids.append(task.id)

    audit_service.record(
        db,
        actor="api",
        action="candidate.split",
        entity_type="candidate",
        entity_id=candidate.id,
        before={"state": "proposed", "item_count": len(items)},
        after={
            "state": candidate.state,
            "child_ids": [child.id for child in children],
            "item_indexes": list(item_indexes),
        },
        household_id=candidate.household_id,
    )
    db.flush()
    return children, resolved_task_ids


def merge_candidates(  # noqa: C901
    db: Session,
    winner_id: str,
    loser_ids: list[str],
    household_id: str,
) -> tuple[Candidate, list[Candidate], list[str]]:
    """Merge one `proposed` survivor with one-or-more `proposed` duplicates.

    Validate-first-then-write (the `split_candidate` shape): every participant is
    checked before anything changes, so a refused merge writes NOTHING. The
    winner KEEPS its fields and stays `proposed` -- a merge never auto-accepts,
    the review still decides. The winner's evidence becomes the exact union of
    every participant's evidence; each loser ends terminal (`merged`) carrying
    `merged_into`, and its open duplicate task(s) resolve with audit rows. The
    request's explicit ids are the merge set; the candidate proposals'
    `dedup_matches` are evidence for the reviewer, never trusted as the set. The
    caller commits, the route rolls back on error.
    """
    winner = db.query(Candidate).filter_by(id=winner_id).first()
    if winner is None:
        raise CandidateMergeError("Winner candidate not found", status_code=404)
    if winner.household_id != household_id:
        raise CandidateMergeError("Household mismatch", status_code=403)
    if not isinstance(loser_ids, list) or any(
        not isinstance(item, str) for item in loser_ids
    ):
        raise CandidateMergeError("loser_ids must be a list of candidate ids", status_code=422)
    if not loser_ids:
        raise CandidateMergeError("merge requires at least one loser", status_code=422)
    if len(set(loser_ids)) != len(loser_ids):
        raise CandidateMergeError("loser_ids must be unique", status_code=422)
    if winner.id in loser_ids:
        raise CandidateMergeError("the winner cannot also be a loser", status_code=422)
    if winner.state != "proposed":
        raise CandidateMergeError(
            f"winner state {winner.state} is not mergeable", status_code=409
        )

    losers: list[Candidate] = []
    for loser_id in loser_ids:
        loser = db.query(Candidate).filter_by(id=loser_id).first()
        if loser is None:
            raise CandidateMergeError(f"Loser candidate {loser_id} not found", status_code=404)
        if loser.household_id != household_id:
            raise CandidateMergeError("Household mismatch", status_code=403)
        if loser.state != "proposed":
            raise CandidateMergeError(
                f"loser state {loser.state} is not mergeable", status_code=409
            )
        blocking = (
            db.query(ReviewTask)
            .filter(
                ReviewTask.subject_ref == loser.id,
                ReviewTask.household_id == household_id,
                ReviewTask.status == "open",
                ReviewTask.task_type.notin_(list(MERGE_RESOLVED_TASK_TYPES)),
            )
            .count()
        )
        if blocking:
            raise CandidateMergeError("loser has unresolved review tasks", status_code=409)
        losers.append(loser)

    # Every participant validated; only now does anything change.
    raw_winner_evidence = json.loads(winner.evidence_ids_json)
    if not isinstance(raw_winner_evidence, list):
        raise CandidateMergeError("winner evidence is invalid", status_code=500)
    winner_evidence = [str(item) for item in raw_winner_evidence]
    union = list(winner_evidence)
    for loser in losers:
        raw_loser_evidence = json.loads(loser.evidence_ids_json)
        if not isinstance(raw_loser_evidence, list):
            raise CandidateMergeError("loser evidence is invalid", status_code=500)
        for item in raw_loser_evidence:
            evidence_id = str(item)
            if evidence_id not in union:
                union.append(evidence_id)

    # Invariant: the survivor stays `proposed` after a merge -- merge never
    # auto-accepts; the review still decides (asserted in the tests).
    winner.evidence_ids_json = json.dumps(union, ensure_ascii=False)

    resolved_task_ids: list[str] = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for loser in losers:
        proposal = load_proposal(loser)
        proposal["merged_into"] = winner.id
        loser.proposed_fields_json = json.dumps(proposal, ensure_ascii=False)
        loser.state = MERGED_STATE

    open_tasks = (
        db.query(ReviewTask)
        .filter(
            ReviewTask.subject_ref.in_([loser.id for loser in losers]),
            ReviewTask.household_id == household_id,
            ReviewTask.task_type.in_(list(MERGE_RESOLVED_TASK_TYPES)),
            ReviewTask.status == "open",
        )
        .all()
    )
    for task in open_tasks:
        before = {"status": task.status}
        task.status = "resolved"
        task.updated_at = now
        audit_service.record(
            db,
            actor="api",
            action="review_task.resolve",
            entity_type="review_task",
            entity_id=task.id,
            before=before,
            after={"status": task.status, "resolution": {"merge": winner.id}},
            household_id=task.household_id,
        )
        resolved_task_ids.append(task.id)

    audit_service.record(
        db,
        actor="api",
        action="candidate.merge",
        entity_type="candidate",
        entity_id=winner.id,
        before={
            "state": "proposed",
            "evidence_ids": winner_evidence,
            "loser_ids": loser_ids,
        },
        after={
            "state": winner.state,
            "evidence_ids": union,
            "loser_ids": [loser.id for loser in losers],
            "merged_into": winner.id,
            "resolved_task_ids": resolved_task_ids,
        },
        household_id=household_id,
    )
    db.flush()
    return winner, losers, resolved_task_ids
