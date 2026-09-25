"""Jina Search fallback client (SG-082, D108).

The fallback source for OFF misses/degradation and for non-food input. It is
the SAME package as SG-081's OFF client (no new package) and the SAME snapshot
discipline: every call returns a `JinaSearchSnapshot` carrying the request URL,
the live retrieval timestamp and the verbatim raw body, and every provider
failure degrades to a loud `no_result_reason` — it NEVER raises into a caller.

Decisions recorded here (reported, not hidden):
- DEFAULT base is the GLOBAL endpoint `https://s.jina.ai/` (D11, 2026-09-25).
  The SG-082 EU data-residency posture for the Romania scope is superseded by
  reachability: SG-116 found the EU base `https://eu.s.jina.ai/` NXDOMAIN on the
  host (transport-dead, zero HTTP bytes) while the global base answers HTTP 200,
  so queries go to the global endpoint until the EU base resolves again. No
  geography is claimed for the global endpoint beyond its URL. The EU base stays
  a named non-default constant so the direction can be reversed cleanly.
- The query is brand + name (+ category when supplied) TEXT only: no image, no
  coordinate, no key byte ever enters the query. The `site` filters are the
  three researched Romanian retail domains.
- The `Authorization` header is added at SEND time from a key resolved through
  the settings/env seam. The key VALUE is never returned by a builder, never
  stored in a snapshot and never logged.

`resolve_api_key` reads the declared `settings.jina_api_key` field (SG-097)
first and otherwise the `JINA_API_KEY` process environment. The settings field
is the declared carrier; the environment remains the fallback, never a silent
one.
"""

from __future__ import annotations

import json
import os
import urllib.parse
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import settings
from app.services.enrich import scoring
from app.services.enrich.client import OffSearchSnapshot, fetch_off_search

# D11 (2026-09-25): reachability over EU data residency for the Romania scope.
# SG-116 found the EU base NXDOMAIN on the host while the global base answers
# HTTP 200, so the global endpoint is the default until the EU base resolves
# again. No geography is claimed for the global endpoint beyond its URL; the EU
# constant stays named and non-default (the SG-082 discipline, direction
# reversed).
JINA_EU_BASE_URL = "https://eu.s.jina.ai/"
JINA_GLOBAL_BASE_URL = "https://s.jina.ai/"
SOURCE_NAME = "JinaSearch"
SITE_FILTERS = ("mega-image.ro", "emag.ro", "farmaciatei.ro")
JINA_NUM = "5"
JINA_TYPE = "web"
JINA_GL = "ro"
TOKEN_BUDGET = "6000"
PAGE_TIMEOUT = "15"
RESPOND_WITH = "content"
DEFAULT_TIMEOUT_S = 15.0
MAX_QUOTED_BODY_CHARS = 2000

# The category values that keep OFF first; anything else is "non-food" and
# fires the fallback even when OFF returns a confident match.
FOOD_CATEGORIES = frozenset({"food", "beverage", "beverages", "food_beverages"})

JINA_API_KEY_ENV = "JINA_API_KEY"


@dataclass(frozen=True)
class JinaRequest:
    """The exact request that WOULD be sent (asserted without network).

    `params` is a tuple of pairs, not a dict, because `site` is repeated.
    `headers` never carries `Authorization`: the key is added at send time.
    """

    method: str
    url: str
    params: tuple[tuple[str, str], ...]
    headers: dict[str, str]


@dataclass(frozen=True)
class JinaSearchSnapshot:
    """A verbatim Jina response with source attribution (URL + timestamp)."""

    source_name: str
    request_url: str
    retrieved_at: str
    status_code: int | None
    raw: Any
    raw_text: str | None
    results: tuple[Mapping[str, Any], ...]
    no_result_reason: str | None


def resolve_api_key(explicit: str | None = None) -> str | None:
    """Resolve the Jina key through the settings/env seam.

    Explicit wins (test/DI seam), then a `jina_api_key` settings field when the
    running settings module declares one, then the process environment. Returns
    `None` when no key is present; the caller degrades loudly, never crashes.
    """
    if explicit:
        return explicit
    configured = getattr(settings, "jina_api_key", None)
    if isinstance(configured, str) and configured:
        return configured
    from_env = os.environ.get(JINA_API_KEY_ENV)
    return from_env or None


def build_jina_query(brand: str, name: str, category: str | None = None) -> str:
    """Brand + name (+ category) TEXT only; no identifier beyond the words."""
    parts = [part for part in (brand, name, category) if part]
    return " ".join(parts)


def build_jina_request(
    name: str,
    brand: str,
    *,
    category: str | None = None,
    base_url: str = JINA_GLOBAL_BASE_URL,
) -> JinaRequest:
    """The exact search request: global base (D11), urlencoded query, repeated site."""
    query = build_jina_query(brand, name, category)
    encoded = urllib.parse.quote_plus(query)
    params: tuple[tuple[str, str], ...] = tuple(
        [("site", site) for site in SITE_FILTERS]
        + [("num", JINA_NUM), ("type", JINA_TYPE), ("gl", JINA_GL)]
    )
    headers = {
        "Accept": "application/json",
        "X-Token-Budget": TOKEN_BUDGET,
        "X-Timeout": PAGE_TIMEOUT,
        "X-Respond-With": RESPOND_WITH,
    }
    return JinaRequest(
        method="GET", url=f"{base_url}{encoded}", params=params, headers=headers
    )


def authorize(headers: Mapping[str, str], api_key: str) -> dict[str, str]:
    """Add the Bearer header at send time; the value is never returned elsewhere."""
    merged = dict(headers)
    merged["Authorization"] = f"Bearer {api_key}"
    return merged


def _degraded(
    *,
    reason: str,
    request_url: str,
    retrieved_at: str,
    status_code: int | None,
    raw_text: str | None,
) -> JinaSearchSnapshot:
    return JinaSearchSnapshot(
        source_name=SOURCE_NAME,
        request_url=request_url,
        retrieved_at=retrieved_at,
        status_code=status_code,
        raw=None,
        raw_text=raw_text,
        results=(),
        no_result_reason=reason,
    )


def _extract_results(raw: Any) -> tuple[list[Any], str | None]:
    """Return (results, reason). Supports the bare list and `data`/`results`."""
    if isinstance(raw, list):
        return raw, None
    if isinstance(raw, dict):
        for key in ("data", "results"):
            value = raw.get(key)
            if isinstance(value, list):
                return value, None
        return [], "malformed_payload: Jina response has no 'data'/'results' list"
    return [], "malformed_payload: Jina response body is not a JSON list or object"


def _interpret(response: httpx.Response, retrieved_at: str) -> JinaSearchSnapshot:
    """Turn one HTTP response into a snapshot; degrade loudly, never raise."""
    request_url = str(response.request.url)
    body_text = response.text[:MAX_QUOTED_BODY_CHARS]
    if response.status_code != 200:
        return _degraded(
            reason=(
                f"http_status: Jina returned HTTP {response.status_code}: {body_text!r}"
            ),
            request_url=request_url,
            retrieved_at=retrieved_at,
            status_code=response.status_code,
            raw_text=body_text,
        )
    try:
        raw: Any = response.json()
    except ValueError as exc:
        return _degraded(
            reason=f"invalid_json: Jina returned a non-JSON body: {exc}",
            request_url=request_url,
            retrieved_at=retrieved_at,
            status_code=response.status_code,
            raw_text=body_text,
        )
    items, reason = _extract_results(raw)
    if reason is not None:
        return _degraded(
            reason=reason,
            request_url=request_url,
            retrieved_at=retrieved_at,
            status_code=response.status_code,
            raw_text=body_text,
        )
    if any(not isinstance(item, dict) for item in items):
        return _degraded(
            reason="malformed_payload: Jina results are not a list of objects",
            request_url=request_url,
            retrieved_at=retrieved_at,
            status_code=response.status_code,
            raw_text=body_text,
        )
    return JinaSearchSnapshot(
        source_name=SOURCE_NAME,
        request_url=request_url,
        retrieved_at=retrieved_at,
        status_code=response.status_code,
        raw=raw,
        raw_text=None,
        results=tuple(items),
        no_result_reason=None,
    )


def fetch_jina_search(
    name: str,
    brand: str,
    *,
    category: str | None = None,
    http_client: httpx.Client | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    now: Callable[[], datetime] | None = None,
    api_key: str | None = None,
    base_url: str = JINA_GLOBAL_BASE_URL,
) -> JinaSearchSnapshot:
    """One sync Jina search, always returned as a snapshot.

    `http_client` is the injection seam for tests; when omitted a 15 s
    `httpx.Client` is built for this one call. `now` is the live clock seam.
    A missing key, a transport/timeout, a non-200 or a malformed body returns a
    snapshot with `no_result_reason` — never an exception, never a silent empty.
    """
    request = build_jina_request(name, brand, category=category, base_url=base_url)
    clock = now or (lambda: datetime.now(timezone.utc))
    retrieved_at = clock().isoformat()
    key = resolve_api_key(api_key)
    if key is None:
        return _degraded(
            reason=(
                f"missing_key: {JINA_API_KEY_ENV} is not present in the backend "
                "environment; refusing to send an unauthenticated search"
            ),
            request_url=request.url,
            retrieved_at=retrieved_at,
            status_code=None,
            raw_text=None,
        )
    headers = authorize(request.headers, key)
    try:
        if http_client is None:
            with httpx.Client(timeout=httpx.Timeout(timeout_s)) as client:
                response = client.get(
                    request.url, params=list(request.params), headers=headers
                )
        else:
            response = http_client.get(
                request.url, params=list(request.params), headers=headers
            )
    except httpx.HTTPError as exc:
        return _degraded(
            reason=f"transport: {type(exc).__name__}: {exc}",
            request_url=request.url,
            retrieved_at=clock().isoformat(),
            status_code=None,
            raw_text=None,
        )
    return _interpret(response, clock().isoformat())


@dataclass(frozen=True)
class EnrichDecisionRecord:
    """The in-memory decision record: BOTH sources' snapshots side by side.

    JSON-serialisable (no datastore field, no model, no migration, `PG-SC-02`).
    `off_decision` is SG-081's `MatchDecision`; `fallback` is present iff the
    fallback fired. The record is a value object returned to the caller; this
    slice persists nothing.
    """

    primary: OffSearchSnapshot
    off_decision: scoring.MatchDecision
    fallback: JinaSearchSnapshot | None
    fallback_fired: bool
    fallback_reason: str | None


def should_use_jina(
    *,
    off_reason: str | None,
    off_accepted: bool,
    category: str | None,
) -> tuple[bool, str | None]:
    """OFF stays first; Jina fires only on a miss/degradation or non-food.

    Returns (fire, named reason). An accepted OFF hit on a food (or unknown)
    category never fires the fallback.
    """
    if category is not None and category not in FOOD_CATEGORIES:
        return True, "non_food"
    if off_reason is not None:
        return True, f"off_degraded: {off_reason}"
    if not off_accepted:
        return True, "off_no_confident_match"
    return False, None


def fetch_with_fallback(
    name: str,
    brand: str,
    *,
    category: str | None = None,
    http_client: httpx.Client | None = None,
    jina_http_client: httpx.Client | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    now: Callable[[], datetime] | None = None,
    api_key: str | None = None,
) -> EnrichDecisionRecord:
    """Run OFF first, then Jina iff `should_use_jina`. Both snapshots returned."""
    off_snapshot = fetch_off_search(name, brand, http_client=http_client, now=now)
    off_decision = scoring.select_candidate(
        off_snapshot.products, brand=brand, name=name, category=category
    )
    fire, reason = should_use_jina(
        off_reason=off_snapshot.no_result_reason,
        off_accepted=off_decision.accepted,
        category=category,
    )
    fallback = None
    if fire:
        fallback = fetch_jina_search(
            name,
            brand,
            category=category,
            http_client=jina_http_client,
            timeout_s=timeout_s,
            now=now,
            api_key=api_key,
        )
    return EnrichDecisionRecord(
        primary=off_snapshot,
        off_decision=off_decision,
        fallback=fallback,
        fallback_fired=fire,
        fallback_reason=reason,
    )


def snapshot_to_json(snapshot: JinaSearchSnapshot) -> str:
    """Serialise a snapshot verbatim (URL + timestamp + raw body)."""
    return json.dumps(
        {
            "source_name": snapshot.source_name,
            "request_url": snapshot.request_url,
            "retrieved_at": snapshot.retrieved_at,
            "status_code": snapshot.status_code,
            "no_result_reason": snapshot.no_result_reason,
            "raw": snapshot.raw,
            "raw_text": snapshot.raw_text,
            "results": [dict(result) for result in snapshot.results],
        },
        indent=2,
        ensure_ascii=False,
    )
