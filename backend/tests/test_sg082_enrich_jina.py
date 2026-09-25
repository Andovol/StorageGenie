"""SG-082 Jina fallback client + OFF->Jina order + web review mapping (offline, $0).

Scope: this file wires NO pipeline and writes NO datastore field. Every HTTP
leg is a scripted `httpx.MockTransport`: no real key crosses the wire here. The
live leg is the bounded smoke recorded in the worklog, not this suite.

What this file proves:
- G1: the Jina client speaks the EXACT researched request (global base, urlencoded
  query, repeated `site`, `num`/`type`/`gl`, the four token-budget headers) and
  adds `Authorization` at SEND time only. The request-shape test reads the
  request the real httpx driver received (`PG-EV-04` / `PG-SC-12`); the Bearer
  VALUE is never asserted, stored or logged (`PG-EV-09`). Degradation is a loud
  `no_result_reason`, never an exception and never a silent empty.
- G2: OFF stays first; Jina fires only on OFF miss/degradation or non-food, and
  both snapshots ride the in-memory decision record. OFF decisions and Jina
  results map to `source_type=web:<source>` proposals under the label-wins
  conflict rule; a web field is ALWAYS `review_state="proposed"` even at a
  confidence threshold of 0.0 (`PG-SC-02`: nothing persisted).
"""

from __future__ import annotations

import inspect
import json
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base
from app.models.household import Household
from app.models.assertion import Assertion
from app.models.job import Job
from app.services import candidates
from app.services.candidates import Candidate
from app.services.enrich import client as off_client
from app.services.enrich import jina as jina_mod
from app.services.enrich import scoring

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"

Q_BRAND = "Jacobs"
Q_NAME = "Jacobs Cronat Gold"
EXPECTED_PARAMS = (
    ("site", "mega-image.ro"),
    ("site", "emag.ro"),
    ("site", "farmaciatei.ro"),
    ("num", "5"),
    ("type", "web"),
    ("gl", "ro"),
)


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _fixture(name: str) -> dict[str, Any]:
    return dict(_load(f"{name}.json"))


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
# G1 — request shape (PG-EV-04), EU base, header NAMES only
# --------------------------------------------------------------------------- #
def test_jina_request_shape_exact_url_params_and_header_names() -> None:
    request = jina_mod.build_jina_request(Q_NAME, Q_BRAND)
    assert request.method == "GET"
    assert request.url == "https://s.jina.ai/Jacobs+Jacobs+Cronat+Gold"
    assert request.params == EXPECTED_PARAMS
    assert set(request.headers) == {
        "Accept",
        "X-Token-Budget",
        "X-Timeout",
        "X-Respond-With",
    }
    assert request.headers["Accept"] == "application/json"
    assert request.headers["X-Token-Budget"] == "6000"
    assert request.headers["X-Timeout"] == "15"
    assert request.headers["X-Respond-With"] == "content"
    # The builder carries no key material at all.
    assert "Authorization" not in request.headers


def test_jina_authorize_adds_only_the_authorization_name() -> None:
    request = jina_mod.build_jina_request(Q_NAME, Q_BRAND)
    authorized = jina_mod.authorize(request.headers, "unit-test")
    assert set(authorized) == set(request.headers) | {"Authorization"}
    # The builder input is untouched (no mutation, no key in the shape object).
    assert "Authorization" not in request.headers


def test_jina_default_base_is_global_and_eu_is_named_not_default() -> None:
    assert jina_mod.JINA_EU_BASE_URL == "https://eu.s.jina.ai/"
    assert jina_mod.JINA_GLOBAL_BASE_URL == "https://s.jina.ai/"
    default_url = jina_mod.build_jina_request(Q_NAME, Q_BRAND).url
    assert default_url.startswith(jina_mod.JINA_GLOBAL_BASE_URL)
    assert not default_url.startswith(jina_mod.JINA_EU_BASE_URL)


def test_driver_receives_the_exact_jina_query_and_headers() -> None:
    http_client, seen = _scripted_client(_load("jina_hit.json"))
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test"
    )

    assert len(seen) == 1
    request = seen[0]
    assert request.method == "GET"
    assert str(request.url).startswith("https://s.jina.ai/Jacobs+Jacobs+Cronat+Gold?")
    assert tuple(request.url.params.multi_items()) == EXPECTED_PARAMS
    header_names = {name.lower() for name in request.headers}
    assert {"accept", "x-token-budget", "x-timeout", "x-respond-with", "authorization"} <= header_names
    assert snapshot.request_url == str(request.url)


def test_jina_query_carries_text_only_no_image_gps_or_key_bytes() -> None:
    http_client, seen = _scripted_client(_load("jina_hit.json"))
    jina_mod.fetch_jina_search(Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test")
    request = seen[0]

    assert request.content == b""  # a GET with no body: no image bytes
    for key, value in request.url.params.multi_items():
        assert isinstance(value, str)
        assert "base64" not in value.lower()
        assert "unit-test" not in value
    for forbidden in ("image", "photo", "lat", "lon", "gps"):
        assert forbidden not in {name.lower() for name in request.url.params.keys()}
        assert forbidden not in {name.lower() for name in request.headers}
    # The key value never appears in the URL.
    assert "unit-test" not in str(request.url)


def test_missing_key_degrades_loudly_with_zero_sends(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JINA_API_KEY", raising=False)
    http_client, seen = _scripted_client(_load("jina_hit.json"))
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key=None
    )
    assert seen == []
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("missing_key:")
    assert snapshot.results == ()


def test_default_client_builds_a_fifteen_second_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    assert jina_mod.DEFAULT_TIMEOUT_S == 15.0
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
                200, json=_load("jina_hit.json"), request=httpx.Request("GET", url, params=params)
            )

    monkeypatch.setattr(jina_mod.httpx, "Client", _FakeClient)
    jina_mod.fetch_jina_search(Q_NAME, Q_BRAND, api_key="unit-test")
    assert captured["timeout"].connect == 15.0
    assert captured["timeout"].read == 15.0


# --------------------------------------------------------------------------- #
# G1 — snapshots + degradation WITHOUT raising
# --------------------------------------------------------------------------- #
def test_snapshot_records_url_timestamp_and_raw_body() -> None:
    payload = _load("jina_hit.json")
    http_client, _seen = _scripted_client(payload)
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test"
    )
    assert snapshot.source_name == "JinaSearch"
    assert snapshot.request_url.startswith("https://s.jina.ai/")
    assert snapshot.status_code == 200
    assert snapshot.raw == payload
    assert snapshot.no_result_reason is None
    assert len(snapshot.results) == 1
    assert snapshot.results[0]["url"] == "https://www.mega-image.ro/p/jacobs-cronat-gold-100g"
    parsed = datetime.fromisoformat(snapshot.retrieved_at)
    assert parsed.tzinfo is not None


def test_snapshot_timestamp_uses_injected_clock() -> None:
    fixed = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    http_client, _seen = _scripted_client(_load("jina_hit.json"))
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test", now=lambda: fixed
    )
    assert snapshot.retrieved_at == fixed.isoformat()


def test_http_5xx_returns_loud_no_result_with_quoted_body() -> None:
    http_client, _seen = _scripted_client(status=503, body_text="upstream unavailable")
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test"
    )
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("http_status: Jina returned HTTP 503")
    assert "upstream unavailable" in snapshot.no_result_reason
    assert snapshot.results == ()
    assert snapshot.raw is None


def test_timeout_returns_loud_no_result() -> None:
    http_client, _seen = _scripted_client(exc=httpx.TimeoutException("simulated timeout"))
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test"
    )
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("transport: TimeoutException")
    assert snapshot.results == ()


def test_malformed_json_returns_loud_no_result() -> None:
    http_client, _seen = _scripted_client(status=200, body_text="<html>not json</html>")
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test"
    )
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("invalid_json:")


def test_wrapped_and_bare_result_shapes_are_both_accepted() -> None:
    wrapped = _scripted_client({"code": 200, "data": _load("jina_hit.json")})[0]
    bare = _scripted_client(_load("jina_hit.json"))[0]
    assert jina_mod.fetch_jina_search("n", "b", http_client=wrapped, api_key="unit-test").results
    assert jina_mod.fetch_jina_search("n", "b", http_client=bare, api_key="unit-test").results


def test_object_without_data_or_results_returns_loud_no_result() -> None:
    http_client, _seen = _scripted_client({"code": 200})
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test"
    )
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("malformed_payload:")


def test_non_object_result_entries_return_loud_no_result() -> None:
    http_client, _seen = _scripted_client([1, 2, 3])
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test"
    )
    assert snapshot.no_result_reason is not None
    assert snapshot.no_result_reason.startswith("malformed_payload:")


def test_empty_results_is_a_legit_miss_not_a_degradation() -> None:
    http_client, _seen = _scripted_client(_load("jina_empty.json"))
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test"
    )
    assert snapshot.no_result_reason is None
    assert snapshot.results == ()
    assert snapshot.status_code == 200
    assert snapshot.raw is not None


def test_snapshot_json_helper_is_serialisable_and_attributed() -> None:
    http_client, _seen = _scripted_client(_load("jina_hit.json"))
    snapshot = jina_mod.fetch_jina_search(
        Q_NAME, Q_BRAND, http_client=http_client, api_key="unit-test"
    )
    rendered = jina_mod.snapshot_to_json(snapshot)
    assert "https://s.jina.ai/" in rendered
    assert snapshot.retrieved_at in rendered
    assert '"no_result_reason": null' in rendered


# --------------------------------------------------------------------------- #
# G2 — OFF first; Jina only on miss/degradation/non-food; both snapshots kept
# --------------------------------------------------------------------------- #
def test_off_hit_on_food_never_fires_jina() -> None:
    off_client_http, _ = _scripted_client(_fixture("off_hit"))
    jina_http, jina_seen = _scripted_client(_load("jina_hit.json"))
    record = jina_mod.fetch_with_fallback(
        Q_NAME,
        Q_BRAND,
        category="food",
        http_client=off_client_http,
        jina_http_client=jina_http,
        api_key="unit-test",
    )
    assert record.off_decision.accepted is True
    assert record.fallback_fired is False
    assert record.fallback is None
    assert jina_seen == []  # the fallback client was never reached


def test_off_empty_miss_fires_jina_and_keeps_both_snapshots() -> None:
    off_client_http, _ = _scripted_client(_fixture("off_empty"))
    jina_http, _ = _scripted_client(_load("jina_hit.json"))
    record = jina_mod.fetch_with_fallback(
        Q_NAME,
        Q_BRAND,
        category="food",
        http_client=off_client_http,
        jina_http_client=jina_http,
        api_key="unit-test",
    )
    assert record.off_decision.accepted is False
    assert record.fallback_fired is True
    assert record.fallback_reason == "off_no_confident_match"
    assert record.primary.status_code == 200
    assert record.fallback is not None and record.fallback.results


def test_off_degradation_fires_jina() -> None:
    off_client_http, _ = _scripted_client(status=503, body_text="down")
    jina_http, _ = _scripted_client(_load("jina_hit.json"))
    record = jina_mod.fetch_with_fallback(
        Q_NAME,
        Q_BRAND,
        category="food",
        http_client=off_client_http,
        jina_http_client=jina_http,
        api_key="unit-test",
    )
    assert record.fallback_fired is True
    assert record.fallback_reason is not None and record.fallback_reason.startswith("off_degraded:")


def test_non_food_fires_jina_even_on_an_accepted_off_hit() -> None:
    off_client_http, _ = _scripted_client(_fixture("off_hit"))
    jina_http, jina_seen = _scripted_client(_load("jina_hit.json"))
    record = jina_mod.fetch_with_fallback(
        Q_NAME,
        Q_BRAND,
        category="medicine",
        http_client=off_client_http,
        jina_http_client=jina_http,
        api_key="unit-test",
    )
    assert record.off_decision.accepted is True
    assert record.fallback_fired is True
    assert record.fallback_reason == "non_food"
    assert len(jina_seen) == 1


# --------------------------------------------------------------------------- #
# G2 — mapping OFF decisions + Jina results into existing candidate structures
# --------------------------------------------------------------------------- #
def test_map_off_decision_fields_uses_web_source_and_never_guesses() -> None:
    accepted = scoring.select_candidate(
        _fixture("off_hit")["products"], brand=Q_BRAND, name=Q_NAME
    )
    fields = candidates.map_off_decision_fields(
        accepted, source_url="https://world.openfoodfacts.org/api/v2/search?x=1", retrieved_at="2026-09-22T00:00:00+00:00"
    )
    assert fields["display_name"]["source_type"] == "web:OpenFoodFacts"  # type: ignore[index]
    assert fields["display_name"]["value"] == "Jacobs Cronat Gold instant coffee"  # type: ignore[index]
    assert fields["identifier"]["source_type"] == "web:OpenFoodFacts"  # type: ignore[index]
    assert "category_proposed" not in fields  # no categories supplied -> inert

    ambiguous = scoring.select_candidate(
        _fixture("off_ambiguous")["products"], brand=Q_BRAND, name=Q_NAME
    )
    assert candidates.map_off_decision_fields(
        ambiguous, source_url="u", retrieved_at="t"
    ) == {}


def test_map_jina_result_and_category_activation_rule() -> None:
    result = _load("jina_hit.json")[0]
    fields = candidates.map_jina_result_fields(
        result,
        source_url="https://eu.s.jina.ai/q",
        retrieved_at="2026-09-22T00:00:00+00:00",
        category="food",
    )
    assert fields["display_name"]["source_type"] == "web:JinaSearch"  # type: ignore[index]
    # mega-image.ro -> food_beverages agrees with "food" through category_score.
    assert fields["category_proposed"]["value"] == "food_beverages"  # type: ignore[index]

    disagreeing = candidates.map_jina_result_fields(
        result,
        source_url="https://eu.s.jina.ai/q",
        retrieved_at="t",
        category="medicine",
    )
    assert "category_proposed" not in disagreeing


def test_category_score_is_the_activation_rule() -> None:
    assert scoring.category_score("food", ["food_beverages"]) > 0.0
    assert scoring.category_score("medicine", ["food_beverages"]) == 0.0
    # The OFF path stays byte-identical: the SG-081 request still omits categories.
    request = off_client.build_off_request(Q_NAME, Q_BRAND)
    assert request.params["fields"] == off_client.OFF_FIELDS
    assert "categories_tags_en" not in request.params["fields"]


def test_merge_web_fields_label_wins_but_keeps_the_alternate_visible() -> None:
    photo = {"display_name": {"value": "Photo Name", "source_type": "extraction"}}
    web = {
        "display_name": {
            "value": "Web Name",
            "source_type": "web:JinaSearch",
            "source_url": "https://eu.s.jina.ai/q",
            "retrieved_at": "t",
        },
        "category_proposed": {
            "value": "food_beverages",
            "source_type": "web:JinaSearch",
            "source_url": "https://eu.s.jina.ai/q",
            "retrieved_at": "t",
        },
    }
    merged, alternates = candidates.merge_web_fields(photo, web)
    assert merged["display_name"]["value"] == "Photo Name"  # type: ignore[index]
    assert merged["category_proposed"]["source_type"] == "web:JinaSearch"  # type: ignore[index]
    assert alternates == [
        {
            "field": "display_name",
            "value": "Web Name",
            "source_type": "web:JinaSearch",
            "source_url": "https://eu.s.jina.ai/q",
            "retrieved_at": "t",
        }
    ]


# --------------------------------------------------------------------------- #
# G2 — a web field can never auto-accept, even at a 0.0 confidence threshold
# --------------------------------------------------------------------------- #
@pytest.fixture
def web_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'web.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Web Household")
    session.add(household)
    session.commit()
    try:
        yield session, household.id
    finally:
        session.close()
        engine.dispose()


def test_committed_web_field_is_proposed_never_auto_accepted(
    web_db, monkeypatch: pytest.MonkeyPatch  # type: ignore[no-untyped-def]
) -> None:
    session, household_id = web_db
    monkeypatch.setattr(settings, "sg_confidence_threshold", 0.0)
    job = Job(household_id=household_id, job_type="import", state="COMPLETED", config_snapshot=json.dumps({"evidence_ids": []}))
    session.add(job)
    session.flush()
    proposal = {
        "kind": "new_asset",
        "asset_id": None,
        "fields": {
            "display_name": {"value": "Photo Name", "confidence": 0.99, "source_type": "extraction"},
            "status": {"value": "ACTIVE", "source_type": "deterministic"},
            "category_proposed": {
                "value": "food_beverages",
                "confidence": None,
                "source_type": "web:JinaSearch",
                "source_url": "https://eu.s.jina.ai/q",
                "retrieved_at": "2026-09-22T00:00:00+00:00",
            },
        },
        "dedup_matches": [],
        "review_task_ids": [],
    }
    candidate = Candidate(
        job_id=job.id,
        evidence_ids_json=json.dumps([]),
        proposed_fields_json=json.dumps(proposal),
        state="accepted",
        household_id=household_id,
    )
    session.add(candidate)
    session.flush()
    result = candidates.commit_candidate(session, candidate)
    session.flush()
    assert result["created"] is True

    rows = {
        row.field_path: row
        for row in session.query(Assertion).filter_by(asset_id=result["asset_id"]).all()
    }
    # The web field is a proposal even though the threshold is 0.0.
    assert rows["category_proposed"].review_state == "proposed"
    assert rows["category_proposed"].source_type == "web:JinaSearch"
    assert json.loads(rows["category_proposed"].model_json or "{}")["source_url"] == "https://eu.s.jina.ai/q"
    # A non-gated deterministic field is still accepted at 0.0 (contrast).
    assert rows["status"].review_state == "accepted"


# --------------------------------------------------------------------------- #
# SG-097 — the settings-field seam: explicit > Settings.jina_api_key > environment
# --------------------------------------------------------------------------- #
def test_settings_field_beats_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Both the field and the env var are set: the declared field wins."""
    monkeypatch.setenv(jina_mod.JINA_API_KEY_ENV, "test-env-key")
    monkeypatch.setattr(settings, "jina_api_key", "test-field-key")
    assert jina_mod.resolve_api_key() == "test-field-key"


def test_explicit_argument_beats_the_settings_field(monkeypatch: pytest.MonkeyPatch) -> None:
    """The explicit argument (test/DI seam) wins over the declared field."""
    monkeypatch.setenv(jina_mod.JINA_API_KEY_ENV, "test-env-key")
    monkeypatch.setattr(settings, "jina_api_key", "test-field-key")
    assert jina_mod.resolve_api_key("test-explicit-key") == "test-explicit-key"


def test_absent_field_falls_through_to_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """The field is declared but unset: resolution falls through to the env var."""
    monkeypatch.setattr(settings, "jina_api_key", None)
    monkeypatch.setenv(jina_mod.JINA_API_KEY_ENV, "test-env-key")
    assert jina_mod.resolve_api_key() == "test-env-key"


def test_no_field_no_env_resolves_to_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """No key at any layer resolves to None (the caller then degrades loudly)."""
    monkeypatch.setattr(settings, "jina_api_key", None)
    monkeypatch.delenv(jina_mod.JINA_API_KEY_ENV, raising=False)
    assert jina_mod.resolve_api_key() is None


WORKED_EXAMPLE = (
    Path(__file__).resolve().parents[2] / "docs" / "enrich-jina-request-example.md"
)


def test_worked_example_artifact_matches_the_real_driver() -> None:
    """SG-097: the committed worked example IS the request the REAL driver builds.

    The expected URL/params are derived from the real module constants
    (`PG-SC-12`), never a re-typed copy; the artifact is names-only (the key is
    added at send time and never appears in the example).
    """
    example = jina_mod.build_jina_request("Jacobs Cronat Gold", "Jacobs")
    expected_params = tuple(
        [("site", site) for site in jina_mod.SITE_FILTERS]
        + [
            ("num", jina_mod.JINA_NUM),
            ("type", jina_mod.JINA_TYPE),
            ("gl", jina_mod.JINA_GL),
        ]
    )
    assert example.params == expected_params
    assert example.url == f"{jina_mod.JINA_GLOBAL_BASE_URL}Jacobs+Jacobs+Cronat+Gold"
    full_request = example.url + "?" + urllib.parse.urlencode(example.params)
    artifact = WORKED_EXAMPLE.read_text(encoding="utf-8")
    assert full_request in artifact
    assert set(example.headers) == {
        "Accept",
        "X-Token-Budget",
        "X-Timeout",
        "X-Respond-With",
    }
    assert "Authorization" not in example.headers


# --------------------------------------------------------------------------- #
# Purity guards
# --------------------------------------------------------------------------- #
def test_jina_module_declares_no_dispatch_or_pipeline_symbols() -> None:
    source = inspect.getsource(jina_mod)
    for forbidden in ("WEB_" + "DETECTION", "visi" + "on"):
        assert forbidden not in source
