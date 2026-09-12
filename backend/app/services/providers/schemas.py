"""Strict extraction output schemas + single-repair helper (SG-026).

Sync to match SG-025 (protocols/router/fake are sync; no async here).
Pydantic v2, extra="forbid" everywhere: free-form prose is never parsed —
a prose input fails validation (proven in test_extraction_contract.py).

Repair policy (§5.3): exactly ONE retry, then the step fails with
ExtractionFailedError. The helper lives here (not a new extraction.py)
because it is pure validation logic over in-memory payloads: no I/O, no
provider wiring, no reader. The PRODUCTION reader that consumes these
schemas arrives in SG-028.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic import ValidationError as PydanticValidationError

from app.services.providers.router import ProviderError

UNKNOWN_PATH_RE = re.compile(r"^items\.(\d+)\.([A-Za-z_][A-Za-z0-9_]*)$")


class ExtractionItem(BaseModel):
    """One extracted catalog item: per-assertion confidence + uncertainty reasons."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    expiry_date: str | None = None
    date_type: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty_reasons: list[str] = Field(default_factory=list)

    @field_validator("expiry_date")
    @classmethod
    def _date_is_iso(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"expiry_date must be a valid YYYY-MM-DD date: {value!r}") from exc
        if parsed.isoformat() != value:
            raise ValueError(f"expiry_date must use YYYY-MM-DD format: {value!r}")
        return value

    @model_validator(mode="after")
    def _uncertainty_required_below_full_confidence(self) -> ExtractionItem:
        if self.confidence < 1.0 and not self.uncertainty_reasons:
            raise ValueError("uncertainty_reasons required when confidence < 1.0")
        return self


class ExtractionOutput(BaseModel):
    """Strict provider extraction envelope: items + REQUIRED unknowns + needs_evidence."""

    model_config = ConfigDict(extra="forbid")

    items: list[ExtractionItem]
    unknowns: list[str]
    needs_evidence: bool = False

    @model_validator(mode="after")
    def _unknowns_are_absent_fields(self) -> ExtractionOutput:
        if self.needs_evidence and not self.unknowns:
            raise ValueError("needs_evidence=True requires a non-empty unknowns list")
        for entry in self.unknowns:
            match = UNKNOWN_PATH_RE.match(entry)
            if match is None:
                raise ValueError(f"unknowns entry must look like items.<i>.<field>: {entry!r}")
            index = int(match.group(1))
            field_name = match.group(2)
            if index >= len(self.items):
                raise ValueError(f"unknowns entry indexes a missing item: {entry!r}")
            if field_name not in ExtractionItem.model_fields:
                raise ValueError(f"unknowns entry names an unknown field: {entry!r}")
            current = getattr(self.items[index], field_name)
            if current is not None and current != []:
                raise ValueError(f"unknowns entry carries a fabricated value: {entry!r}")
        return self


def parse_extraction_output(raw: Any) -> ExtractionOutput:
    """Strictly parse a raw provider payload.

    Dicts validate directly. Strings must be JSON objects; anything else —
    prose, wrong types, non-object JSON — fails as a pydantic ValidationError
    (unparsable strings are validated against a bogus key so the single
    exception type is preserved and no prose is ever parsed).
    """
    if isinstance(raw, dict):
        data = raw
    elif isinstance(raw, str):
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            decoded = {"prose": raw}
        data = decoded if isinstance(decoded, dict) else {"prose": raw}
    else:
        data = {"prose": raw}
    return ExtractionOutput.model_validate(data)


class ExtractionFailedError(RuntimeError):
    """The extraction step failed: first attempt plus the single repair both failed."""


def extract_with_single_repair(supply: Callable[[], Any]) -> ExtractionOutput:
    """Call `supply()` for a raw payload, validate strictly, retry exactly once.

    A retryable-shaped failure on the FIRST attempt only (ProviderError with
    kind "invalid_json", or a schema ValidationError) triggers one more
    supply() call. Any failure on the second attempt — or a non-retryable
    ProviderError on either attempt — raises ExtractionFailedError (or the
    original non-retryable error) with no further calls.
    """
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            raw = supply()
        except ProviderError as exc:
            if exc.kind != "invalid_json" or attempt == 1:
                raise ExtractionFailedError(
                    f"extraction supply failed (attempt {attempt + 1}/2, kind={exc.kind})"
                ) from exc
            last_error = exc
            continue
        try:
            return parse_extraction_output(raw)
        except PydanticValidationError as exc:
            if attempt == 1:
                raise ExtractionFailedError(
                    "extraction payload invalid after the single repair (attempt 2/2)"
                ) from exc
            last_error = exc
            continue
    raise ExtractionFailedError(f"extraction failed after the single repair: {last_error}") from last_error
