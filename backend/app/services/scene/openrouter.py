"""OpenRouter scene-render client (SG-155, spec §§2–3).

Single integration: one owner-placed `OPENROUTER_API_KEY`, one frozen request
envelope against the OpenAI-compatible
`POST https://openrouter.ai/api/v1/chat/completions`. There is no per-vendor
client — the OpenRouter router is the adapter (spec §2).

Decisions recorded here (reported, not hidden):
- The `Authorization` header is added at SEND time from a key resolved through
  the settings/env seam (the enrich key-seam precedent, SG-097 in
  `services/enrich/`). The key VALUE is never returned by a builder, never
  stored in a request object and never logged.
- `resolve_openrouter_key` reads the declared `settings.openrouter_api_key`
  field first and otherwise the `OPENROUTER_API_KEY` process environment. The
  settings field is the declared carrier; the environment is the explicit
  fallback, never a silent one.
- The envelope is frozen: `tool_choice: "required"` (no model-decides vagueness),
  exactly one `openrouter:image_generation` tool, `max_tool_calls: 1`, and the
  `stop_server_tools_when` condition schema T0-PINNED from the live contract on
  2026-10-09 (`https://openrouter.ai/openapi.json`, openapi 3.1.0). The image
  model is CONFIG, never code (D7 swaps a name, not an architecture).
- The asset photo enters as message image content
  (`{"type": "image_url", "image_url": {"url": ...}}`), never as query text.

T0-PINNED (verbatim, re-stated for T1b, never re-derived):
- `stop_server_tools_when` is an array (`minItems: 1`) of conditions discriminated
  by `type`; any condition firing halts the loop (OR logic) and, when set, it
  OVERRIDES `max_tool_calls`. The five `type`s are `step_count_is`,
  `has_tool_call`, `max_tokens_used`, `max_cost`, `finish_reason_is`.
  - `max_cost`: `{"type": "max_cost", "max_cost_in_dollars": <number>}` required.
  - `step_count_is`: `{"type": "step_count_is", "step_count": <int>}` required.
- The `openrouter:image_generation` server tool "generates images from text
  prompts"; its parameters config is documented as accepting "all image_config
  params ... plus a model field" and does NOT declare a reference-image field.
  Reference images (`input_references`) are documented only on the standalone
  image-generation request, not on the server tool. T0b answer: on this
  chat-completions server-tool path the tool is text-prompt-only; the asset is
  carried by orchestrator vision into the text prompt.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.evidence import Evidence
from app.models.provider_call import ProviderCall
from app.services import audit_service
from app.storage.local_store import storage_path_for

SCENE_ENDPOINT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"

# T0-PINNED condition types (live OpenAPI contract, 2026-10-09).
STOP_CONDITION_TYPES = (
    "step_count_is",
    "has_tool_call",
    "max_tokens_used",
    "max_cost",
    "finish_reason_is",
)

# The orchestrator rewrites the photo + brief into a detailed render prompt
# (subject preserved, shape/label/material pinned; scene, lighting and framing
# variable), then the image tool renders it. The image model is config.
SCENE_SYSTEM_PROMPT = (
    "You are a product-scene director. You receive a photograph of a real "
    "household asset and a short scene brief. Rewrite the brief into one "
    "detailed image-generation prompt that preserves the asset's subject, "
    "shape, label and material exactly, while varying only the surrounding "
    "scene, lighting and framing. Then call the image generation tool once."
)


@dataclass(frozen=True)
class SceneRefusal:
    """A loud, named refusal: never an exception, never a silent empty run."""

    code: str
    reason: str


def resolve_openrouter_key(explicit: str | None = None) -> str | None:
    """Resolve the OpenRouter key through the settings/env seam.

    Explicit wins (test/DI seam), then the declared `openrouter_api_key`
    settings field, then the `OPENROUTER_API_KEY` process environment. Returns
    `None` when no key is present; the caller refuses loudly, never crashes.
    """
    if explicit:
        return explicit
    configured = getattr(settings, "openrouter_api_key", None)
    if isinstance(configured, str) and configured:
        return configured
    from_env = os.environ.get(OPENROUTER_API_KEY_ENV)
    return from_env or None


def _resolve_spend_cap(spend_cap_usd: float | None) -> float | None:
    if spend_cap_usd is not None:
        return spend_cap_usd
    configured = getattr(settings, "sg_scene_cap", None)
    if isinstance(configured, (int, float)):
        return float(configured)
    return None


def build_scene_request(
    photo_ref: str,
    brief: str,
    image_model: str,
    orchestrator: str,
    *,
    spend_cap_usd: float | None = None,
) -> dict[str, object]:
    """Build the exact sendable request; the key is added at SEND time only.

    `photo_ref` is the asset photo as a base64 data URL or HTTP(S) URL; it
    enters as message image content. `spend_cap_usd` overrides the configured
    `sg_scene_cap`. The returned dict carries `method`, `url`, `headers`
    (never `Authorization`) and the `json` body.
    """
    stop_conditions: list[dict[str, object]] = [
        # One render per request: stop the agent loop after a single tool step.
        {"type": "step_count_is", "step_count": 1}
    ]
    cap = _resolve_spend_cap(spend_cap_usd)
    if cap is not None:
        stop_conditions.append({"type": "max_cost", "max_cost_in_dollars": cap})

    body: dict[str, object] = {
        "model": orchestrator,
        "messages": [
            {"role": "system", "content": SCENE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": brief},
                    {"type": "image_url", "image_url": {"url": photo_ref}},
                ],
            },
        ],
        "tools": [
            {
                "type": "openrouter:image_generation",
                "parameters": {"model": image_model},
            }
        ],
        "tool_choice": "required",
        "max_tool_calls": 1,
        "stop_server_tools_when": stop_conditions,
    }
    return {
        "method": "POST",
        "url": SCENE_ENDPOINT_URL,
        "headers": {"Content-Type": "application/json"},
        "json": body,
    }


def missing_key() -> SceneRefusal:
    """Refuse a send when no key is present at any seam layer (`PG-SC-03`)."""
    return SceneRefusal(
        code="missing_key",
        reason=(
            f"missing_key: {OPENROUTER_API_KEY_ENV} is not present in the backend "
            "environment; refusing to send an unauthenticated scene render"
        ),
    )


def refused_consent() -> SceneRefusal:
    """Refuse a send when scene consent is not granted (privacy gate)."""
    return SceneRefusal(
        code="refused_consent",
        reason=(
            "refused_consent: scene rendering is consent-gated; sg_consent is "
            "not granted, so no photo is sent"
        ),
    )


def over_cap(*, cap_usd: float, spent_usd: float) -> SceneRefusal:
    """Refuse a send when the arc spend cap is already reached (never spend)."""
    return SceneRefusal(
        code="over_cap",
        reason=(
            f"over_cap: spent {spent_usd} USD has reached the {cap_usd} USD scene "
            "cap; refusing to spend further"
        ),
    )


# --------------------------------------------------------------------------- #
# SG-158 T1b — the send path: POST, immediate download, Evidence + ledger.
#
# The key enters the headers HERE, in the same function that sends, and nowhere
# else: `build_scene_request` still refuses to carry it. Consent is the explicit
# `SceneSpendAuthority` value the caller passes (the packet's quoted spend
# authority); `settings.sg_consent` is deliberately NOT the predicate — flipping
# it can never authorize a paid render. Every send attempt that leaves the
# machine appends ONE `provider_call` row, including billed failures (SG-099
# lesson: a failed call that cost money must be ledgered, not dropped); a row
# whose response states no cost carries `cost=None`, never a substituted zero.
# --------------------------------------------------------------------------- #

SCENE_LEDGER_PROVIDER = "openrouter"
SCENE_LEDGER_TEMPLATE_VERSION = "scene-render-v1"
SCENE_RENDER_SOURCE_KIND = "scene_render"
SCENE_SEND_TIMEOUT_S = 120.0
SCENE_DOWNLOAD_TIMEOUT_S = 60.0
_IMAGE_MEDIA_EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


@dataclass(frozen=True)
class SceneSpendAuthority:
    """The explicit grant that authorizes ONE paid render arc.

    Constructed by the caller from the owner-approved packet text (grant id +
    cap). Its mere presence is the consent predicate: no settings flag can
    substitute for it.
    """

    grant_id: str
    cap_usd: float


@dataclass(frozen=True)
class SceneRenderOutcome:
    """The result of one `render_scene` call; refusals never raise."""

    status: str  # "rendered" | "refused" | "failed"
    refusal: SceneRefusal | None = None
    status_code: int | None = None
    response_id: str | None = None
    image_url: str | None = None
    image_sha256: str | None = None
    image_media_type: str | None = None
    storage_key: str | None = None
    evidence_id: str | None = None
    ledger_id: str | None = None
    cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    latency_ms: float | None = None
    error_state: str | None = None


def scene_spend_so_far(db: Session) -> tuple[float, int]:
    """Recorded scene spend: (sum of known costs, count of rows with cost NULL)."""
    known = 0.0
    unknown = 0
    for row in db.query(ProviderCall).filter(ProviderCall.provider == SCENE_LEDGER_PROVIDER).all():
        if row.cost is None:
            unknown += 1
        else:
            known += float(row.cost)
    return known, unknown


def guard_render_spend(
    *,
    spent_usd: float,
    unknown_cost_calls: int,
    worst_case_usd: float,
    authority: SceneSpendAuthority | None,
) -> SceneRefusal | None:
    """Refuse before sending when the worst case would cross the cap.

    `None` authority refuses consent (the predicate is the explicit grant, never
    `sg_consent`). A row whose cost is unknown is charged the worst case again
    (fail closed). Returns `None` only when the projection stays within cap.
    """
    if authority is None:
        return refused_consent()
    if not (
        math.isfinite(spent_usd)
        and math.isfinite(worst_case_usd)
        and math.isfinite(authority.cap_usd)
    ):
        return SceneRefusal(
            code="over_cap",
            reason=(
                "over_cap: spend projection is not a finite number "
                f"(spent={spent_usd!r} worst_case={worst_case_usd!r}); refusing to spend"
            ),
        )
    projected = spent_usd + unknown_cost_calls * worst_case_usd + worst_case_usd
    if projected > authority.cap_usd:
        return SceneRefusal(
            code="over_cap",
            reason=(
                f"over_cap: projected worst case {projected} USD (spent {spent_usd} + "
                f"{unknown_cost_calls} unknown-cost call(s) x {worst_case_usd} + this render "
                f"{worst_case_usd}) exceeds cap {authority.cap_usd} USD; refusing to spend"
            ),
        )
    return None


def extract_image_url(response_json: Any) -> str | None:  # noqa: C901
    """First image-looking URL in a chat-completions response, else `None`.

    Tolerant by design (the exact tool-result envelope is only pinned live at
    first render): checks `imageUrl`/`image_url`/`url` keys, dict-valued
    `image_url: {url: ...}`, then walks the whole tree. Only `http(s)://` and
    `data:image/` values qualify.
    """

    def _url(value: Any) -> str | None:
        if isinstance(value, str) and value.startswith(("http://", "https://", "data:image/")):
            return value
        return None

    def _walk(node: Any) -> str | None:  # noqa: C901
        if isinstance(node, dict):
            for key in ("imageUrl", "image_url", "url"):
                if key in node:
                    found = _url(node[key])
                    if found is not None:
                        return found
                    if isinstance(node[key], dict):
                        found = _url(node[key].get("url"))
                        if found is not None:
                            return found
            for value in node.values():
                found = _walk(value)
                if found is not None:
                    return found
        elif isinstance(node, list):
            for value in node:
                found = _walk(value)
                if found is not None:
                    return found
        return None

    return _walk(response_json)


def _sniff_image_media_type(data: bytes, claimed: str | None) -> str | None:
    if data.startswith(b"\x89PNG"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return "image/webp"
    if claimed in _IMAGE_MEDIA_EXTENSIONS:
        return claimed
    return None


def _decode_data_url(data_url: str) -> tuple[bytes, str] | None:
    try:
        header, _, payload = data_url.partition(",")
    except ValueError:
        return None
    if not payload:
        return None
    media_type = header[5:].split(";", 1)[0] if header.startswith("data:") else ""
    try:
        return base64.b64decode(payload), media_type
    except (ValueError, TypeError):
        return None


def _download_image(
    image_url: str,
    *,
    http_client: httpx.Client | None,
    timeout_s: float,
) -> tuple[bytes | None, str | None, str | None]:
    """Immediate download of the temporary render; returns (bytes, media, error)."""
    if image_url.startswith("data:"):
        decoded = _decode_data_url(image_url)
        if decoded is None:
            return None, None, "image_download_failed: undecodable data URL"
        data, claimed = decoded
        media = _sniff_image_media_type(data, claimed or None)
        if media is None:
            return None, None, "image_download_failed: data URL is not a decodable image"
        return data, media, None
    try:
        if http_client is None:
            with httpx.Client(timeout=httpx.Timeout(timeout_s)) as client:
                response = client.get(image_url)
        else:
            response = http_client.get(image_url)
    except httpx.HTTPError as exc:
        return None, None, f"image_download_failed: transport: {type(exc).__name__}"
    if response.status_code != 200:
        return None, None, f"image_download_failed: http_status:{response.status_code}"
    claimed_type: str | None = (
        response.headers.get("Content-Type", "").split(";", 1)[0].strip() or None
    )
    media = _sniff_image_media_type(response.content, claimed_type)
    if media is None:
        return None, None, "image_download_failed: body is not a decodable image"
    return response.content, media, None


def record_scene_call(
    db: Session,
    *,
    image_model: str,
    orchestrator: str,
    brief: str,
    photo_sha256: str,
    status_code: int | None,
    response_id: str | None,
    usage: dict[str, Any] | None,
    cost_usd: float | None,
    latency_ms: float | None,
    error_state: str | None,
    evidence_id: str | None,
    remote_url: str | None,
    error_body: str | None = None,
) -> ProviderCall:
    """Append ONE ledger row for one sent render request; commits immediately."""
    row = ProviderCall(
        provider=SCENE_LEDGER_PROVIDER,
        model=orchestrator,
        prompt_template_version=SCENE_LEDGER_TEMPLATE_VERSION,
        input_hashes=json.dumps(
            {"photo_sha256": photo_sha256, "brief_sha256": hashlib.sha256(brief.encode()).hexdigest()}
        ),
        output_payload=json.dumps(
            {
                "image_model": image_model,
                "orchestrator": orchestrator,
                "prompt": brief,
                "status_code": status_code,
                "response_id": response_id,
                "evidence_id": evidence_id,
                "remote_url": remote_url,
                "error_body": error_body,
            },
            ensure_ascii=False,
        ),
        cost=cost_usd,
        usage_json=json.dumps(usage, ensure_ascii=False) if usage is not None else None,
        latency_ms=latency_ms,
        error_state=error_state[:200] if error_state else None,
        job_id=None,
    )
    db.add(row)
    db.commit()
    return row


def store_scene_render_evidence(
    db: Session,
    *,
    household_id: str,
    image_bytes: bytes,
    media_type: str,
    image_model: str,
    brief: str,
    orchestrator: str,
    response_id: str | None,
    cost_usd: float | None,
    usage: dict[str, Any] | None,
    actor: str = "scene-render",
) -> Evidence:
    """Persist one rendered image as an Evidence row, bytes in the storage root.

    `source_kind="scene_render"`; provenance (provider, image model, orchestrator,
    prompt, usage, cost, response id, timestamp) rides the audit record beside the
    row, since the Evidence table has no provenance columns and no migration is
    in scope. Commits.
    """
    sha = hashlib.sha256(image_bytes).hexdigest()
    existing = db.query(Evidence).filter_by(sha256=sha).first()
    if existing is not None:
        return existing
    ext = _IMAGE_MEDIA_EXTENSIONS.get(media_type, ".png")
    full = storage_path_for(sha, ext, household_id)
    rel = full.relative_to(Path(settings.storage_root)).as_posix()
    full.parent.mkdir(parents=True, exist_ok=True)
    tmp = full.with_suffix(full.suffix + ".tmp")
    try:
        tmp.write_bytes(image_bytes)
        tmp.replace(full)
    finally:
        if tmp.exists():
            tmp.unlink()
    ev = Evidence(
        household_id=household_id,
        sha256=sha,
        media_type=media_type,
        storage_key=rel,
        original_filename=f"scene-render-{image_model.replace('/', '-')}{ext}",
        source_kind=SCENE_RENDER_SOURCE_KIND,
        size_bytes=len(image_bytes),
    )
    db.add(ev)
    db.flush()
    audit_service.record(
        db,
        actor=actor,
        action="evidence.create",
        entity_type="evidence",
        entity_id=ev.id,
        before=None,
        after={
            "sha256": sha,
            "original_filename": ev.original_filename,
            "size_bytes": len(image_bytes),
            "provider": SCENE_LEDGER_PROVIDER,
            "image_model": image_model,
            "orchestrator": orchestrator,
            "prompt": brief,
            "usage": usage,
            "cost_usd": cost_usd,
            "response_id": response_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        household_id=household_id,
    )
    db.commit()
    db.refresh(ev)
    return ev


def render_scene(  # noqa: C901
    db: Session,
    *,
    household_id: str,
    photo_ref: str,
    brief: str,
    image_model: str,
    orchestrator: str,
    worst_case_usd: float,
    authority: SceneSpendAuthority | None,
    key: str | None = None,
    http_client: httpx.Client | None = None,
    timeout_s: float = SCENE_SEND_TIMEOUT_S,
) -> SceneRenderOutcome:
    """One paid render: guard, POST, immediate download, Evidence + ledger row.

    Refusals happen BEFORE any send (`refused_consent`, `missing_key`,
    `over_cap`). Every POST that leaves the machine gets exactly one ledger row
    in a `finally`-equivalent path — including failures — so billed-but-unledgered
    cannot occur. `http_client` is the test seam; the live path builds a fresh
    `httpx.Client`.
    """
    spent_usd, unknown_cost_calls = scene_spend_so_far(db)
    refusal = guard_render_spend(
        spent_usd=spent_usd,
        unknown_cost_calls=unknown_cost_calls,
        worst_case_usd=worst_case_usd,
        authority=authority,
    )
    if refusal is not None:
        return SceneRenderOutcome(status="refused", refusal=refusal)

    resolved_key = resolve_openrouter_key(key)
    if resolved_key is None:
        return SceneRenderOutcome(status="refused", refusal=missing_key())

    request = build_scene_request(
        photo_ref, brief, image_model, orchestrator, spend_cap_usd=worst_case_usd
    )
    send_url = str(request["url"])
    send_body = cast("dict[str, Any]", request["json"])
    headers = dict(cast("dict[str, str]", request["headers"]))
    headers["Authorization"] = f"Bearer {resolved_key}"  # SEND time only

    photo_sha256 = hashlib.sha256(photo_ref.encode("utf-8")).hexdigest()

    status_code: int | None = None
    response_json: dict[str, Any] | None = None
    error_state: str | None = None
    error_body: str | None = None
    usage: dict[str, Any] | None = None
    cost_usd: float | None = None
    response_id: str | None = None
    image_url: str | None = None
    image_media: str | None = None
    evidence: Evidence | None = None
    started = time.monotonic()
    try:
        if http_client is None:
            with httpx.Client(timeout=httpx.Timeout(timeout_s)) as client:
                response = client.post(send_url, json=send_body, headers=headers)
        else:
            response = http_client.post(send_url, json=send_body, headers=headers)
        status_code = response.status_code
        try:
            parsed = response.json()
            response_json = parsed if isinstance(parsed, dict) else {"data": parsed}
        except ValueError:
            error_state = "invalid_json"
            error_body = response.text[:800]
        if status_code != 200:
            raw_body = (
                json.dumps(response_json, ensure_ascii=False)[:800]
                if response_json is not None
                else (error_body or "")
            )
            error_body = raw_body.replace(resolved_key, "[redacted]") if raw_body else None
    except httpx.HTTPError as exc:
        error_state = f"transport: {type(exc).__name__}"

    latency_ms = (time.monotonic() - started) * 1000.0

    if response_json is not None:
        raw_usage = response_json.get("usage")
        if isinstance(raw_usage, dict):
            usage = raw_usage
            raw_cost = raw_usage.get("cost")
            if isinstance(raw_cost, (int, float)) and not isinstance(raw_cost, bool):
                cost_usd = float(raw_cost)
        raw_id = response_json.get("id")
        response_id = raw_id if isinstance(raw_id, str) else None
        image_url = extract_image_url(response_json)

    if status_code == 200 and image_url is not None:
        data, media, download_error = _download_image(
            image_url, http_client=http_client, timeout_s=SCENE_DOWNLOAD_TIMEOUT_S
        )
        if data is not None and media is not None:
            image_media = media
            try:
                evidence = store_scene_render_evidence(
                    db,
                    household_id=household_id,
                    image_bytes=data,
                    media_type=media,
                    image_model=image_model,
                    brief=brief,
                    orchestrator=orchestrator,
                    response_id=response_id,
                    cost_usd=cost_usd,
                    usage=usage,
                )
            except Exception:
                error_state = "evidence_write_failed"
        else:
            error_state = download_error or "image_download_failed"
    elif status_code == 200:
        error_state = error_state or "image_url_missing"
    elif status_code is not None:
        error_state = error_state or f"http_status:{status_code}"

    ledger = record_scene_call(
        db,
        image_model=image_model,
        orchestrator=orchestrator,
        brief=brief,
        photo_sha256=photo_sha256,
        status_code=status_code,
        response_id=response_id,
        usage=usage,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        error_state=error_state,
        evidence_id=evidence.id if evidence is not None else None,
        remote_url=image_url,
        error_body=error_body,
    )
    status = "rendered" if evidence is not None else "failed"
    return SceneRenderOutcome(
        status=status,
        status_code=status_code,
        response_id=response_id,
        image_url=image_url,
        image_sha256=evidence.sha256 if evidence is not None else None,
        image_media_type=image_media,
        storage_key=evidence.storage_key if evidence is not None else None,
        evidence_id=evidence.id if evidence is not None else None,
        ledger_id=ledger.id,
        cost_usd=cost_usd,
        usage=usage,
        latency_ms=latency_ms,
        error_state=error_state,
    )
