"""SG-132 Jina cost-ledger wiring (offline, $0, no live search).

Scope: the REAL endpoint (`POST /v1/enrich/{asset_id}`) through the REAL router
(`app.main`), the REAL OFF/Jina clients (`app.services.enrich`) and the REAL
production ledger writer (`app.services.enrich.snapshots.record_jina_search_call`)
read back by the REAL month-boxed spend reader
(`app.services.providers.reader._recorded_spend`). Every HTTP leg is a scripted
`httpx.MockTransport` injected through the endpoint's own dependency seams, so no
key crosses a wire and no metered call is made.

What this file proves (`PG-SC-12`: the row crosses the real boundary):
- every Jina search that leaves the machine appends exactly ONE `provider_call`
  row carrying `jina.estimate_jina_search_cost()` ($0.0005 at the vendor floor);
- the row joins through the enrichment job, so `_recorded_spend` moves by that
  figure with NO reader change — BEFORE/AFTER around the real endpoint;
- an OFF hit (no Jina) writes no ledger row and leaves spend 0.0 (`PG-SC-07`);
- a missing-key refusal (nothing sent) records the snapshot but no cost row;
- a degraded HTTP response (a sent attempt) IS charged the floor estimate;
- the household month-boxed recorded spend gates the press: with a cap above the
  one-search floor the first press is allowed and, after the row lands, the next
  press refuses by name — no live-search loop is used to reach the cap;
- `PG-IC-08` blast radius: expected row counts and figures are written here, so a
  measured figure differing in either direction fails the run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.v1.enrich import get_jina_http_client, get_off_http_client
from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.household import Household
from app.models.job import Job
from app.models.provider_call import ProviderCall
from app.services.enrich import jina as jina_mod
from app.services.enrich import snapshots as snap_mod
from app.services.providers import reader as reader_mod

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "enrich"

# PG-IC-08: the expected figures are stop conditions, not comments. One Jina
# request at the vendor floor (10,000 tokens x $0.05/1M) is $0.0005; two presses
# are two rows and $0.001. A measured value differing either way stops the run.
EXPECTED_JINA_COST_USD = 0.0005
EXPECTED_ROWS_ONE_SEARCH = 1
EXPECTED_COST_TWO_SEARCHES = 0.001
EXPECTED_ROWS_TWO_SEARCHES = 2
MONTHLY_TEST_CAP_USD = 0.0007  # > one floor, < two floors: discriminates the row's effect


def _load(name: str) -> Any:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def _scripted(
    payload: Any = None,
    *,
    status: int = 200,
    body_text: str | None = None,
) -> tuple[httpx.Client, list[httpx.Request]]:
    """A mock HTTP driver that records every request it receives (no network)."""
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if body_text is not None:
            return httpx.Response(status, text=body_text, request=request)
        return httpx.Response(status, json=payload, request=request)

    return httpx.Client(transport=httpx.MockTransport(handler)), seen


def _install(off: httpx.Client, jina: httpx.Client) -> None:
    app.dependency_overrides[get_off_http_client] = lambda: off
    app.dependency_overrides[get_jina_http_client] = lambda: jina


@pytest.fixture
def enrich_env(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / 'sg132-endpoint.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG-132 Household")
    session.add(household)
    session.commit()
    asset = Asset(
        household_id=household.id,
        display_name="Jacobs Cronat Gold",
        asset_type="product",
        status="ACTIVE",
    )
    session.add(asset)
    session.commit()
    session.add_all(
        [
            Assertion(
                asset_id=asset.id,
                field_path="brand",
                value_json=json.dumps("Jacobs"),
                source_type="user",
                review_state="accepted",
            ),
            Assertion(
                asset_id=asset.id,
                field_path="identifier",
                value_json=json.dumps("3274080005003"),
                source_type="user",
                review_state="accepted",
            ),
        ]
    )
    session.commit()

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session, household.id, asset.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_off_http_client, None)
        app.dependency_overrides.pop(get_jina_http_client, None)
        session.close()
        engine.dispose()


def _post(asset_id: str, household_id: str) -> Any:
    with TestClient(app) as client:
        return client.post(
            f"/v1/enrich/{asset_id}", params={"household_id": household_id}
        )


# --------------------------------------------------------------------------- #
# G1 — one Jina search appends one cost row; _recorded_spend moves by the figure
# --------------------------------------------------------------------------- #
def test_jina_search_ledgers_estimate_and_moves_month_spend(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", "test-sg132-sentinel")
    off, off_seen = _scripted(_load("off_empty"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    before = reader_mod._recorded_spend(session, household_id)
    assert before == 0.0  # empty-household world: no search yet, spend 0.0

    response = _post(asset_id, household_id)

    assert response.status_code == 200
    body = response.json()
    assert body["fallback_fired"] is True
    assert len(off_seen) == 1 and len(jina_seen) == 1

    rows = session.query(ProviderCall).all()
    assert len(rows) == EXPECTED_ROWS_ONE_SEARCH
    row = rows[0]
    assert row.provider == snap_mod.JINA_LEDGER_PROVIDER == "JinaSearch"
    assert row.model == snap_mod.JINA_LEDGER_MODEL
    assert row.cost == pytest.approx(EXPECTED_JINA_COST_USD)
    assert row.error_state is None
    assert row.job_id is not None
    job = session.query(Job).filter_by(id=row.job_id).one()
    assert job.household_id == household_id
    usage = json.loads(row.usage_json or "{}")
    assert usage["tokens"] == jina_mod.JINA_SEARCH_TOKENS_PER_REQUEST == 10_000

    after = reader_mod._recorded_spend(session, household_id)
    assert after == pytest.approx(EXPECTED_JINA_COST_USD)
    assert after - before == pytest.approx(EXPECTED_JINA_COST_USD)

    # the snapshot writer fired in the same leg (writer + reader in one trace)
    assert len(snap_mod.get_snapshots_by_source(session, "jina")) == 1


# --------------------------------------------------------------------------- #
# PG-SC-07 — OFF hit: no Jina search, no ledger row, spend stays 0.0
# --------------------------------------------------------------------------- #
def test_off_hit_writes_no_ledger_row_and_keeps_spend_zero(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    off, off_seen = _scripted(_load("off_hit"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    response = _post(asset_id, household_id)

    assert response.status_code == 200
    assert response.json()["fallback_fired"] is False
    assert len(off_seen) == 1
    assert jina_seen == []
    assert session.query(ProviderCall).count() == 0
    assert reader_mod._recorded_spend(session, household_id) == 0.0


# --------------------------------------------------------------------------- #
# Design call — a missing key sends nothing, so the snapshot is recorded but the
# cost ledger stays empty (never charge a request that never left the machine).
# --------------------------------------------------------------------------- #
def test_missing_key_records_no_cost_row(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", None)
    monkeypatch.delenv(jina_mod.JINA_API_KEY_ENV, raising=False)
    off, _off_seen = _scripted(_load("off_empty"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    response = _post(asset_id, household_id)

    assert response.status_code == 200
    assert response.json()["fallback_fired"] is True
    assert jina_seen == []  # the key gate refused before any transport call
    jina_rows = snap_mod.get_snapshots_by_source(session, "jina")
    assert len(jina_rows) == 1
    assert (jina_rows[0].no_result_reason or "").startswith("missing_key")
    assert session.query(ProviderCall).count() == 0
    assert reader_mod._recorded_spend(session, household_id) == 0.0


# --------------------------------------------------------------------------- #
# A degraded HTTP response followed a real attempt, so the floor estimate is kept
# --------------------------------------------------------------------------- #
def test_degraded_jina_http_status_still_records_estimate(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", "test-sg132-sentinel")
    off, _off_seen = _scripted(_load("off_empty"))
    jina, jina_seen = _scripted(status=503, body_text="jina unavailable")
    _install(off, jina)

    response = _post(asset_id, household_id)

    assert response.status_code == 200
    assert len(jina_seen) == 1
    rows = session.query(ProviderCall).all()
    assert len(rows) == EXPECTED_ROWS_ONE_SEARCH
    assert rows[0].cost == pytest.approx(EXPECTED_JINA_COST_USD)
    assert "http_status" in (rows[0].error_state or "")
    assert reader_mod._recorded_spend(session, household_id) == pytest.approx(
        EXPECTED_JINA_COST_USD
    )


# --------------------------------------------------------------------------- #
# G2 — the household month-boxed spend gates the press: the first press is under
# the cap, the Jina row lands, the next press refuses by name (no live loop).
# --------------------------------------------------------------------------- #
def test_jina_spend_trips_enrich_monthly_refusal(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", "test-sg132-sentinel")
    monkeypatch.setattr(settings, "sg_monthly_cap", MONTHLY_TEST_CAP_USD)
    off, off_seen = _scripted(_load("off_empty"))
    jina, jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    first = _post(asset_id, household_id)
    assert first.status_code == 200
    assert len(jina_seen) == 1
    assert reader_mod._recorded_spend(session, household_id) == pytest.approx(
        EXPECTED_JINA_COST_USD
    )

    second = _post(asset_id, household_id)

    assert second.status_code == 402
    detail = second.json()["detail"]
    assert detail.startswith("monthly_cap_exceeded")
    assert "0.001000 exceeds" in detail
    assert "0.000500 already recorded" in detail
    # The refusal precedes every client touch and writes nothing.
    assert len(off_seen) == 1
    assert len(jina_seen) == 1
    assert session.query(ProviderCall).count() == EXPECTED_ROWS_ONE_SEARCH


# --------------------------------------------------------------------------- #
# PG-IC-08 blast radius — two searches are exactly two rows and $0.001
# --------------------------------------------------------------------------- #
def test_two_jina_searches_are_two_rows_and_double_spend(enrich_env, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    session, household_id, asset_id = enrich_env
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "jina_api_key", "test-sg132-sentinel")
    off, _off_seen = _scripted(_load("off_empty"))
    jina, _jina_seen = _scripted(_load("jina_hit"))
    _install(off, jina)

    assert _post(asset_id, household_id).status_code == 200
    assert _post(asset_id, household_id).status_code == 200

    assert session.query(ProviderCall).count() == EXPECTED_ROWS_TWO_SEARCHES
    assert reader_mod._recorded_spend(session, household_id) == pytest.approx(
        EXPECTED_COST_TWO_SEARCHES
    )


# --------------------------------------------------------------------------- #
# G1 writer boundary — the production writer's own figure scales with the bound
# --------------------------------------------------------------------------- #
def test_production_writer_prices_the_caller_token_bound(enrich_env) -> None:  # type: ignore[no-untyped-def]
    from app.services.enrich.snapshots import record_jina_search_call

    session, household_id, asset_id = enrich_env
    job = Job(
        household_id=household_id,
        job_type="enrich",
        state="COMPLETED",
        config_snapshot=json.dumps({"asset_id": asset_id}),
    )
    session.add(job)
    session.flush()
    snapshot = jina_mod.JinaSearchSnapshot(
        source_name=jina_mod.SOURCE_NAME,
        request_url="https://s.jina.ai/Jacobs",
        retrieved_at="2026-09-25T00:00:00+00:00",
        status_code=200,
        raw=[],
        raw_text=None,
        results=(),
        no_result_reason=None,
    )
    base = record_jina_search_call(session, job, snapshot, query="Jacobs")
    bigger = record_jina_search_call(
        session, job, snapshot, query="Jacobs", tokens=20_000
    )
    assert base.cost == pytest.approx(EXPECTED_JINA_COST_USD)
    assert bigger.cost == pytest.approx(2 * EXPECTED_JINA_COST_USD)
    assert reader_mod._recorded_spend(session, household_id) == pytest.approx(
        EXPECTED_JINA_COST_USD + 2 * EXPECTED_JINA_COST_USD
    )
