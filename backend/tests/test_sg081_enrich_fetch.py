"""SG-081 OFF v2 fetch client + deterministic scoring (offline, $0).

Scope: OFF ONLY. This is a library SG-082 will call — it wires no pipeline and
creates no datastore field. Every test is offline: the HTTP driver is a scripted
`httpx.MockTransport`, so no key, no network, no metered call.

What this file proves:
- G1: the client speaks the EXACT research request (URL + six params + real UA),
  runs synced 10 s calls, snapshots URL + timestamp + raw body, and degrades to a
  loud no-result (quoted reason) instead of raising into a caller. The query that
  crosses the real driver boundary is asserted (`PG-EV-04` / `PG-SC-12`), and the
  payload is brand+name text only (no image bytes, GPS or key material).
- G2: the scoring formula is exact, the accept rule is `>= 0.6` AND margin
  `>= 0.15`, and there is no nearest-guess accept (ambiguous / below-threshold /
  empty all return an explicit no-confident-match).
"""

from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import pytest

from app.services.enrich import client as off_client
from app.services.enrich import scoring

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"

Q_BRAND = "Jacobs"
Q_NAME = "Jacobs Cronat Gold"

EXPECTED_PARAMS = {
    "search_terms": Q_NAME,
    "brands_tags": Q_BRAND,
    "countries_tags_en": "romania",
    "page": "1",
    "page_size": "10",
    "fields": "code,product_name,brands,ingredients_text,nutriments,packaging,countries_tags_en",
}


def _fixture(name: str) -> dict[str, Any]:
    return dict(_load(f"{name}.json"))


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _scripted_client(
    payload: Any = None,
    *,
    status: int = 200,
    body_text: str | None = None,
    exc: Exception | None = None,
) -> tuple[httpx.Client, list[httpx.Request]]:
    """A mock HTTP driver that records every request it receives."""
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if exc is not None:
            raise exc
        if body_text is not None:
            return httpx.Response(status, text=body_text, request=request)
        return httpx.Response(status, json=payload, request=request)

    return httpx.Client(transport=httpx.MockTransport(handler)), seen


# --------------------------------------------------------------------------- #
# G1 — request shape (PG-EV-04), real UA, 10 s sync timeout
# --------------------------------------------------------------------------- #
def test_request_shape_exact_url_params_and_order() -> None:
    request = off_client.build_off_request(Q_NAME, Q_BRAND)
    assert request.method == "GET"
    assert request.url == "https://world.openfoodfacts.org/api/v2/search"
    assert request.params == EXPECTED_PARAMS
    # Parameter order is the research order, preserved.
    assert list(request.params) == [
        "search_terms",
        "brands_tags",
        "countries_tags_en",
        "page",
        "page_size",
        "fields",
    ]


def test_user_agent_identifies_storagegenie_and_is_placeholder_free() -> None:
    request = off_client.build_off_request(Q_NAME, Q_BRAND)
    ua = request.headers["User-Agent"]
    assert ua == off_client.OFF_USER_AGENT
    assert "StorageGenie" in ua
    lowered = ua.lower()
    for placeholder in ("example", "placeholder", "todo", "changeme", "test@"):
        assert placeholder not in lowered, placeholder


def test_off_call_is_unauthenticated_and_has_no_key_material() -> None:
    request = off_client.build_off_request(Q_NAME, Q_BRAND)
    header_names = {name.lower() for name in request.headers}
    assert "authorization" not in header_names
    assert not any("key" in name or "token" in name for name in header_names)


def test_default_client_builds_a_ten_second_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    assert off_client.DEFAULT_TIMEOUT_S == 10.0
    captured: dict[str, Any] = {}

    class _FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)

        def __enter__(self) -> _FakeClient:
            return self

        def __exit__(self, *_exc: object) -> bool:
            return False

        def get(self, url: str, params: Any = None, headers: Any = None) -> httpx.Response:
            return httpx.Response(
                200, json=_fixture("off_hit"), request=httpx.Request("GET", url, params=params)
            )

    monkeypatch.setattr(off_client.httpx, "Client", _FakeClient)
    off_client.fetch_off_search(Q_NAME, Q_BRAND)
    assert captured["timeout"].connect == 10.0
    assert captured["timeout"].read == 10.0


# --------------------------------------------------------------------------- #
# G1 — the exact query crosses the real driver boundary (PG-EV-04 / PG-SC-12)
# --------------------------------------------------------------------------- #
def test_driver_receives_the_exact_query_text() -> None:
    http_client, seen = _scripted_client(_fixture("off_hit"))
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)

    assert len(seen) == 1
    request = seen[0]
    assert request.method == "GET"
    assert str(request.url).startswith("https://world.openfoodfacts.org/api/v2/search?")
    assert dict(request.url.params) == EXPECTED_PARAMS
    assert snapshot.request_url == str(request.url)


def test_snapshot_records_url_timestamp_and_raw_body() -> None:
    payload = _fixture("off_hit")
    http_client, _seen = _scripted_client(payload)
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)

    assert snapshot.source_name == "OpenFoodFacts"
    assert snapshot.request_url.startswith("https://world.openfoodfacts.org/api/v2/search?")
    assert snapshot.status_code == 200
    assert snapshot.raw == payload
    assert snapshot.no_result_reason is None
    assert len(snapshot.products) == 1
    assert snapshot.products[0]["code"] == "3274080005003"
    parsed = datetime.fromisoformat(snapshot.retrieved_at)
    assert parsed.tzinfo is not None


def test_snapshot_timestamp_uses_injected_clock() -> None:
    fixed = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    http_client, _seen = _scripted_client(_fixture("off_hit"))
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client, now=lambda: fixed)
    assert snapshot.retrieved_at == fixed.isoformat()


# --------------------------------------------------------------------------- #
# G1 — privacy: brand+name TEXT only, no photo / GPS / key leaves the machine
# --------------------------------------------------------------------------- #
def test_off_query_carries_text_only_no_image_gps_or_key() -> None:
    http_client, seen = _scripted_client(_fixture("off_hit"))
    off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)
    request = seen[0]

    assert request.content == b""  # a GET with no body: no image bytes
    assert dict(request.url.params) == EXPECTED_PARAMS
    for key, value in request.url.params.items():
        assert isinstance(value, str)
        assert "base64" not in value.lower()
    for forbidden in ("image", "photo", "lat", "lon", "gps", "key", "token"):
        assert forbidden not in {name.lower() for name in request.url.params}
        assert forbidden not in {name.lower() for name in request.headers}


# --------------------------------------------------------------------------- #
# G1 — degradation WITHOUT raising: loud no-result with the quoted reason
# --------------------------------------------------------------------------- #
def test_http_5xx_returns_loud_no_result_with_quoted_body() -> None:
    http_client, _seen = _scripted_client(status=503, body_text="Page temporarily unavailable")
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("http_status: OFF returned HTTP 503")
    assert "Page temporarily unavailable" in snapshot.no_result_reason
    assert snapshot.products == ()
    assert snapshot.raw is None
    assert snapshot.raw_text == "Page temporarily unavailable"


def test_timeout_returns_loud_no_result() -> None:
    http_client, _seen = _scripted_client(exc=httpx.TimeoutException("simulated timeout"))
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("transport: TimeoutException")
    assert snapshot.products == ()


def test_malformed_json_returns_loud_no_result() -> None:
    http_client, _seen = _scripted_client(status=200, body_text="<html>not json</html>")
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("invalid_json:")
    assert snapshot.raw is None
    assert snapshot.raw_text == "<html>not json</html>"


def test_non_object_body_returns_loud_no_result() -> None:
    http_client, _seen = _scripted_client([1, 2, 3])
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("malformed_payload:")


def test_missing_products_key_returns_loud_no_result() -> None:
    http_client, _seen = _scripted_client({"count": 0})
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)
    assert snapshot.no_result_reason is not None
    assert "products" in snapshot.no_result_reason


def test_empty_products_is_a_legit_miss_not_a_degradation() -> None:
    http_client, _seen = _scripted_client(_fixture("off_empty"))
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)
    assert snapshot.no_result_reason is None
    assert snapshot.products == ()
    assert snapshot.status_code == 200
    assert snapshot.raw is not None


def test_snapshot_json_helper_is_serialisable_and_attributed() -> None:
    http_client, _seen = _scripted_client(_fixture("off_hit"))
    snapshot = off_client.fetch_off_search(Q_NAME, Q_BRAND, http_client=http_client)
    rendered = off_client.snapshot_to_json(snapshot)
    assert "world.openfoodfacts.org" in rendered
    assert snapshot.retrieved_at in rendered
    assert '"no_result_reason": null' in rendered


# --------------------------------------------------------------------------- #
# G2 — deterministic scoring, exact formula
# --------------------------------------------------------------------------- #
def test_scoring_module_is_pure_and_offline() -> None:
    source = inspect.getsource(scoring)
    assert "httpx" not in source
    assert "openfoodfacts" not in source
    assert not hasattr(scoring, "httpx")


def test_brand_score_exact_contains_similar_and_miss() -> None:
    assert scoring.brand_score("Jacobs", "Jacobs") == 1.0
    assert scoring.brand_score("jacobs", "Jacobs Cronat") == 1.0
    assert scoring.brand_score("Jacobs", "Jakobs") == 0.5
    assert scoring.brand_score("Jacobs", "Nescafe") == 0.0
    assert scoring.brand_score("", "Jacobs") == 0.0


def test_name_score_is_token_jaccard() -> None:
    assert scoring.name_score("Gold Coffee", "Gold") == 0.5
    assert scoring.name_score("Jacobs Cronat Gold", "Jacobs Cronat Gold") == 1.0
    assert scoring.name_score("Jacobs Cronat Gold", "") == 0.0
    assert scoring.name_score("", "Gold") == 0.0


def test_country_score_romania_bonus() -> None:
    assert scoring.country_score(["en:romania", "en:germany"]) == 0.5
    assert scoring.country_score(["Romania"]) == 0.5
    assert scoring.country_score(["en:france"]) == 0.0
    assert scoring.country_score(None) == 0.0


def test_score_formula_on_committed_hit_fixture() -> None:
    product = _fixture("off_hit")["products"][0]
    # brand 1.0, name 3/5, country 0.5 -> 0.4 + 0.4*0.6 + 0.2*0.5 = 0.74
    assert scoring.score_candidate(product, brand=Q_BRAND, name=Q_NAME) == pytest.approx(0.74)


def test_score_formula_below_threshold_fixture() -> None:
    product = _fixture("off_below_threshold")["products"][0]
    # brand 0.0, name 1/4, country 0.5 -> 0 + 0.1 + 0.1 = 0.2
    assert scoring.score_candidate(product, brand=Q_BRAND, name=Q_NAME) == pytest.approx(0.2)


def test_rank_candidates_is_deterministic() -> None:
    products = _fixture("off_ambiguous")["products"]
    ranked = scoring.rank_candidates(products, brand=Q_BRAND, name=Q_NAME)
    assert [candidate.product["code"] for candidate in ranked] == [
        "1000000000001",
        "1000000000002",
    ]
    assert ranked[0].score > ranked[1].score


# --------------------------------------------------------------------------- #
# G2 — accept rule: >= 0.6 AND margin >= 0.15, no nearest-guess
# --------------------------------------------------------------------------- #
def _candidate(score: float) -> scoring.ScoredCandidate:
    return scoring.ScoredCandidate(product={"code": "x"}, score=score)


def test_accept_threshold_boundary_both_sides() -> None:
    assert scoring.decide([_candidate(0.6)]).accepted is True
    assert scoring.decide([_candidate(0.5999999999999999)]).accepted is False
    assert scoring.decide([_candidate(0.5999999999999999)]).reason == "below_threshold"


def test_accept_margin_boundary_both_sides() -> None:
    accepted = scoring.decide([_candidate(0.9), _candidate(0.75)])
    assert accepted.accepted is True
    assert accepted.margin == pytest.approx(0.15)

    rejected = scoring.decide([_candidate(0.9), _candidate(0.7500000001)])
    assert rejected.accepted is False
    assert rejected.reason == "ambiguous_margin"
    assert rejected.best is None


def test_select_candidate_no_nearest_guess_on_all_three_shapes() -> None:
    accepted = scoring.select_candidate(
        _fixture("off_hit")["products"], brand=Q_BRAND, name=Q_NAME
    )
    assert accepted.accepted is True
    assert accepted.best is not None
    assert accepted.best["code"] == "3274080005003"
    assert accepted.reason == "accepted"

    ambiguous = scoring.select_candidate(
        _fixture("off_ambiguous")["products"], brand=Q_BRAND, name=Q_NAME
    )
    assert ambiguous.accepted is False
    assert ambiguous.best is None
    assert ambiguous.reason == "ambiguous_margin"

    below = scoring.select_candidate(
        _fixture("off_below_threshold")["products"], brand=Q_BRAND, name=Q_NAME
    )
    assert below.accepted is False
    assert below.best is None
    assert below.reason == "below_threshold"

    empty = scoring.select_candidate([], brand=Q_BRAND, name=Q_NAME)
    assert empty.accepted is False
    assert empty.reason == "no_candidates"
