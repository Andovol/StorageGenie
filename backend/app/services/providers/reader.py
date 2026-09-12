"""SG-028 reader bridge: the production bridge between the pipeline and the
SG-025 provider seam.

The Protocol in `protocols.py` describes the seam shape (`image_ref`); the
adapter surface built in SG-027 is `extract_items(image_bytes, prompt, ...)`.
This module is the ONE bridge that supplies BYTES + prompt: it resolves the
immutable original the way `signals.py` does, redacts through the SHARED
`redact_image` (GPS never leaves), calls through the SG-025 router (budget
refusal happens BEFORE any call), validates strictly with exactly one repair
(§5.3), and writes ONE `provider_call` ledger row per completed call.

Tests inject a schema-valid scripted provider through the single named seam
`provider_registry`; production builds it from the named settings. No key is
ever read or logged here — the real adapter owns its own key handling.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.evidence import Evidence
from app.models.job import Job
from app.models.provider_call import ProviderCall
from app.services.providers.fake import FakeProvider
from app.services.providers.opencode_go import OpenCodeGoProvider
from app.services.providers.redaction import redact_image
from app.services.providers.router import (
    ProviderError,
    ProviderRouter,
    RouterConfig,
)
from app.services.providers.schemas import (
    ExtractionOutput,
    extract_with_single_repair,
)
from app.services.signals import SUPPORTED_IMAGE_TYPES
from app.storage.local_store import storage_path

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
PROMPT_FILES = {
    "food": "extract-food-v1.md",
    "medicine": "extract-medicine-v1.md",
}
RETRYABLE_ERRORS = frozenset(
    {"outage", "timeout", "rate_limited", "transport", "http_status", "invalid_json"}
)


def provider_registry() -> dict[str, Any]:
    """Build the id -> provider map from settings.

    Only `fake` is always present; a real adapter is registered only when its
    backend-only key exists. This is the single injection seam for tests.
    """
    registry: dict[str, Any] = {"fake": FakeProvider(mode="valid", provider_id="fake")}
    if settings.opencode_api_key:
        registry["opencode-go"] = OpenCodeGoProvider(
            session_id="storagegenie-sg028",
            api_key=settings.opencode_api_key,
            model_id=settings.sg_model_id,
            per_job_cap=settings.sg_per_job_cap,
            monthly_cap=settings.sg_monthly_cap,
        )
    return registry


def ai_status() -> tuple[bool, str]:
    """Return (enabled, reason). Consent gates every cloud call."""
    if not settings.sg_consent:
        return False, "consent_disabled"
    if settings.sg_provider_id not in provider_registry():
        return False, "provider_not_configured"
    return True, "enabled"


def load_prompt(category: str) -> tuple[str, str]:
    """Return (prompt_text, template_version) for a versioned prompt file."""
    filename = PROMPT_FILES.get(category)
    if filename is None:
        raise ValueError(f"unknown prompt category: {category}")
    text = (PROMPTS_DIR / filename).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"prompt file missing front matter: {filename}")
    header = text.split("---\n", 2)[1]
    version = ""
    for line in header.splitlines():
        if line.startswith("template_version:"):
            version = line.split(":", 1)[1].strip()
    if not version:
        raise ValueError(f"prompt file missing template_version: {filename}")
    return text, version


def _job_evidence_ids(job: Job) -> list[str]:
    config = json.loads(job.config_snapshot or "{}")
    value = config.get("evidence_ids", [])
    if not isinstance(value, list):
        raise ValueError("invalid evidence_ids in job config")
    return [str(item) for item in value]


def analyzable_evidence(db: Session, job: Job) -> list[Evidence]:
    """Job evidence whose original is an image the redactor can decode."""
    evidence_ids = _job_evidence_ids(job)
    rows = db.query(Evidence).filter(Evidence.id.in_(evidence_ids)).all() if evidence_ids else []
    by_id = {row.id: row for row in rows}
    return [
        by_id[evidence_id]
        for evidence_id in evidence_ids
        if evidence_id in by_id and by_id[evidence_id].media_type in SUPPORTED_IMAGE_TYPES
    ]


def resolve_original_bytes(db: Session, evidence_id: str) -> bytes:
    """Read the immutable original exactly the way signals.py locates it."""
    evidence = db.get(Evidence, evidence_id)
    if evidence is None:
        raise ValueError(f"evidence {evidence_id} not found")
    path = storage_path(evidence.storage_key)
    if not path.is_file():
        raise ValueError(f"original missing at storage key {evidence.storage_key}")
    return path.read_bytes()


def _write_ledger(
    db: Session,
    job: Job,
    provider_id: str,
    template_version: str,
    image_bytes: bytes,
    result: Any,
) -> ProviderCall:
    row = ProviderCall(
        provider=provider_id,
        model=str(result.model_id or settings.sg_model_id),
        prompt_template_version=template_version,
        input_hashes=json.dumps({"image_sha256": hashlib.sha256(image_bytes).hexdigest()}),
        output_payload=json.dumps(result.raw_payload, ensure_ascii=False, default=str),
        cost=result.cost,
        usage_json=json.dumps(result.usage, ensure_ascii=False),
        latency_ms=result.latency_ms,
        error_state=None,
        job_id=job.id,
    )
    db.add(row)
    db.flush()
    return row


def _extract_one(
    db: Session,
    job: Job,
    router: ProviderRouter,
    image_bytes: bytes,
    prompt: str,
    provider_id: str,
    template_version: str,
) -> tuple[ExtractionOutput, list[str]]:
    """One evidence, one logical call, at most one repair (§5.3)."""
    call_ids: list[str] = []

    def supply() -> object:
        try:
            result = router.execute("extract_items", image_bytes, prompt)
        except PydanticValidationError as exc:
            raise ProviderError("invalid_json", "adapter schema parse failed") from exc
        row = _write_ledger(db, job, provider_id, template_version, image_bytes, result)
        call_ids.append(row.id)
        return result.normalized_output

    output = extract_with_single_repair(supply)
    return output, call_ids


def _reindex_unknown(entry: str, offset: int) -> str:
    if offset == 0:
        return entry
    prefix, rest = entry.split(".", 1)
    index_text, field = rest.split(".", 1)
    return f"{prefix}.{int(index_text) + offset}.{field}"


def run_ai_extraction(db: Session, job: Job) -> dict[str, object]:
    """ANALYZING_WITH_AI body. Returns the persisted step output."""
    enabled, reason = ai_status()
    if not enabled:
        return {"status": "skipped", "step": "ANALYZING_WITH_AI", "reason": reason}

    category = settings.sg_prompt_category
    prompt, template_version = load_prompt(category)
    registry = provider_registry()
    provider_id = settings.sg_provider_id
    provider = registry[provider_id]
    model_id = str(getattr(provider, "model_id", settings.sg_model_id))

    config = RouterConfig(
        provider_id=provider_id,
        fallback_id=None,
        json_strict=True,
        cost_budget=settings.sg_per_job_cap if settings.sg_per_job_cap is not None else math.inf,
        retryable_errors=RETRYABLE_ERRORS,
    )
    router = ProviderRouter(config=config, registry=registry)

    evidence_rows = analyzable_evidence(db, job)
    if not evidence_rows:
        return {
            "status": "skipped",
            "step": "ANALYZING_WITH_AI",
            "reason": "no_analyzable_image",
        }

    items: list[dict[str, object]] = []
    unknowns: list[str] = []
    call_ids: list[str] = []
    needs_evidence = False
    for evidence in evidence_rows:
        raw = resolve_original_bytes(db, evidence.id)
        redacted = redact_image(raw)
        output, evidence_call_ids = _extract_one(
            db, job, router, redacted, prompt, provider_id, template_version
        )
        offset = len(items)
        items.extend(item.model_dump() for item in output.items)
        unknowns.extend(_reindex_unknown(entry, offset) for entry in output.unknowns)
        needs_evidence = needs_evidence or output.needs_evidence
        call_ids.extend(evidence_call_ids)

    aggregated = ExtractionOutput.model_validate(
        {"items": items, "unknowns": unknowns, "needs_evidence": needs_evidence}
    )
    return {
        "status": "ok",
        "step": "ANALYZING_WITH_AI",
        "provider": provider_id,
        "model": model_id,
        "prompt_template_version": template_version,
        "provider_call_ids": call_ids,
        "extraction": aggregated.model_dump(),
    }
