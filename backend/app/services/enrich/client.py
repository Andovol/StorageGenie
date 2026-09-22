"""Free, unauthenticated Open Food Facts v2 search client (SG-081).

Scope: OFF ONLY. No key, no auth, no other source. `httpx` is already an
application dependency (`opencode_go.py`, `pyproject.toml`), so no new
dependency is added. The client is SYNC on purpose: this tree's provider seam
is sync (`schemas.py`), and there is no event loop to join.

Every call returns an `OffSearchSnapshot` carrying the request URL, the
retrieval timestamp (live clock) and the verbatim raw body. A provider failure
(HTTP 5xx, transport/timeout, malformed body) NEVER raises into the caller: it
returns the same snapshot type with `no_result_reason` set and the raw error
quoted. No caching and no retry beyond that loud no-result (G-A7).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

OFF_SEARCH_URL = "https://world.openfoodfacts.org/api/v2/search"
OFF_FIELDS = "code,product_name,brands,ingredients_text,nutriments,packaging,countries_tags_en"
OFF_COUNTRY = "romania"
OFF_PAGE = 1
OFF_PAGE_SIZE = 10
OFF_USER_AGENT = (
    "StorageGenie/0.1 (https://github.com/Andovol/StorageGenie; openfoodfacts API client)"
)
SOURCE_NAME = "OpenFoodFacts"
DEFAULT_TIMEOUT_S = 10.0
MAX_QUOTED_BODY_CHARS = 2000


@dataclass(frozen=True)
class OffRequest:
    """The exact request that WOULD be sent to OFF (asserted without network)."""

    method: str
    url: str
    params: dict[str, str]
    headers: dict[str, str]


@dataclass(frozen=True)
class OffSearchSnapshot:
    """A verbatim OFF response with source attribution (URL + timestamp)."""

    source_name: str
    request_url: str
    retrieved_at: str
    status_code: int | None
    raw: dict[str, Any] | None
    raw_text: str | None
    products: tuple[Mapping[str, Any], ...]
    no_result_reason: str | None


def build_off_request(name: str, brand: str) -> OffRequest:
    """The exact v2 search request: brand+name text, Romania scope, 10 fields.

    Parameter order is the research order; the values are the caller's brand and
    name strings and constants only — never an image, a coordinate or key.
    """
    params = {
        "search_terms": name,
        "brands_tags": brand,
        "countries_tags_en": OFF_COUNTRY,
        "page": str(OFF_PAGE),
        "page_size": str(OFF_PAGE_SIZE),
        "fields": OFF_FIELDS,
    }
    headers = {"User-Agent": OFF_USER_AGENT, "Accept": "application/json"}
    return OffRequest(method="GET", url=OFF_SEARCH_URL, params=params, headers=headers)


def _degraded(
    *,
    reason: str,
    request_url: str,
    retrieved_at: str,
    status_code: int | None,
    raw_text: str | None,
) -> OffSearchSnapshot:
    return OffSearchSnapshot(
        source_name=SOURCE_NAME,
        request_url=request_url,
        retrieved_at=retrieved_at,
        status_code=status_code,
        raw=None,
        raw_text=raw_text,
        products=(),
        no_result_reason=reason,
    )


def _interpret(response: httpx.Response, retrieved_at: str) -> OffSearchSnapshot:
    """Turn one HTTP response into a snapshot; degrade loudly, never raise."""
    request_url = str(response.request.url)
    body_text = response.text[:MAX_QUOTED_BODY_CHARS]
    if response.status_code != 200:
        return _degraded(
            reason=(
                f"http_status: OFF returned HTTP {response.status_code}: {body_text!r}"
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
            reason=f"invalid_json: OFF returned a non-JSON body: {exc}",
            request_url=request_url,
            retrieved_at=retrieved_at,
            status_code=response.status_code,
            raw_text=body_text,
        )
    if not isinstance(raw, dict):
        return _degraded(
            reason="malformed_payload: OFF response body is not a JSON object",
            request_url=request_url,
            retrieved_at=retrieved_at,
            status_code=response.status_code,
            raw_text=body_text,
        )
    products = raw.get("products")
    if products is None:
        return _degraded(
            reason="malformed_payload: OFF response has no 'products' key",
            request_url=request_url,
            retrieved_at=retrieved_at,
            status_code=response.status_code,
            raw_text=body_text,
        )
    if not isinstance(products, list) or any(not isinstance(item, dict) for item in products):
        return _degraded(
            reason="malformed_payload: OFF 'products' is not a list of objects",
            request_url=request_url,
            retrieved_at=retrieved_at,
            status_code=response.status_code,
            raw_text=body_text,
        )
    return OffSearchSnapshot(
        source_name=SOURCE_NAME,
        request_url=request_url,
        retrieved_at=retrieved_at,
        status_code=response.status_code,
        raw=raw,
        raw_text=None,
        products=tuple(products),
        no_result_reason=None,
    )


def fetch_off_search(
    name: str,
    brand: str,
    *,
    http_client: httpx.Client | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    now: Callable[[], datetime] | None = None,
) -> OffSearchSnapshot:
    """One sync OFF v2 search, always returned as a snapshot.

    `http_client` is the injection seam for tests; when omitted a 10 s
    `httpx.Client` is built for this one call. `now` is the live clock seam.
    A degraded provider returns a snapshot with `no_result_reason`, never an
    exception and never a silent empty.
    """
    request = build_off_request(name, brand)
    clock = now or (lambda: datetime.now(timezone.utc))
    try:
        if http_client is None:
            with httpx.Client(timeout=httpx.Timeout(timeout_s)) as client:
                response = client.get(
                    request.url, params=request.params, headers=request.headers
                )
        else:
            response = http_client.get(
                request.url, params=request.params, headers=request.headers
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


def snapshot_to_json(snapshot: OffSearchSnapshot) -> str:
    """Serialise a snapshot verbatim (URL + timestamp + raw body) for a fixture
    or a worklog raw."""
    return json.dumps(
        {
            "source_name": snapshot.source_name,
            "request_url": snapshot.request_url,
            "retrieved_at": snapshot.retrieved_at,
            "status_code": snapshot.status_code,
            "no_result_reason": snapshot.no_result_reason,
            "raw": snapshot.raw,
            "raw_text": snapshot.raw_text,
            "products": [dict(product) for product in snapshot.products],
        },
        indent=2,
        ensure_ascii=False,
    )
