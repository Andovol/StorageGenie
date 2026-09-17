"""Catalog facet endpoint (SG-064 G1) — counts per dimension, no own filter.

Real HTTP path through `TestClient` on a scratch temp SQLite database. The
discriminator: selecting a value of one dimension must NOT zero the other
values of that same dimension (counts are computed without that dimension's
own filter), which is the opposite of counting WITH all filters applied.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import dialect as postgresql_dialect
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Household
from app.services.asset_service import create_asset
from app.services.evidence_service import store_evidence


def _jpeg_bytes() -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (16, 16), "blue").save(out, format="JPEG")
    return out.getvalue()


@pytest.fixture
def facets_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{tmp_path / 'facets.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))

    def override_get_db():  # type: ignore[no-untyped-def]
        request_session: Session = factory()
        try:
            yield request_session
        finally:
            request_session.close()

    app.dependency_overrides[get_db] = override_get_db
    household = Household(name="Facets Test Household")
    session.add(household)
    session.commit()
    evidence = store_evidence(_jpeg_bytes(), "facets.jpg", "image/jpeg", household.id, session)
    specs = [
        ("Kitchen Blender", "appliance", "ACTIVE", True),
        ("Garden Chair", "furniture", "ACTIVE", False),
        ("Kitchen Table", "furniture", "ARCHIVED", True),
        ("Office Lamp", "appliance", "ARCHIVED", False),
        ("Garage Shelf", "storage", "ACTIVE", False),
    ]
    for name, asset_type, status, has_evidence in specs:
        create_asset(
            session,
            household.id,
            {
                "display_name": name,
                "asset_type": asset_type,
                "status": status,
                "evidence_ids": [evidence.id] if has_evidence else [],
            },
        )
    try:
        yield session, household.id
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _facets(client: TestClient, household_id: str, **filters: object) -> dict:
    response = client.get(
        "/v1/assets/facets", params={"household_id": household_id, **filters}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_facets_counts_each_dimension_without_its_own_filter(facets_fixtures) -> None:  # type: ignore[no-untyped-def]
    _, household_id = facets_fixtures
    with TestClient(app) as client:
        unselected = _facets(client, household_id)
        selected = _facets(client, household_id, asset_type="appliance")

    assert unselected["asset_type"] == {"appliance": 2, "furniture": 2, "storage": 1}
    assert unselected["status"] == {"ACTIVE": 3, "ARCHIVED": 2}
    assert unselected["has_evidence"] == {"with": 2, "without": 3}

    # The discriminator (PG-SC-09): with `asset_type=appliance` the asset_type
    # map is UNCHANGED (not zeroed to only the selected type). Counting WITH all
    # filters would give {"appliance": 2} here.
    assert selected["asset_type"] == {"appliance": 2, "furniture": 2, "storage": 1}
    assert selected["asset_type"] != {"appliance": 2}
    # The OTHER dimensions DO narrow to the selected type.
    assert selected["status"] == {"ACTIVE": 1, "ARCHIVED": 1}
    assert selected["has_evidence"] == {"with": 1, "without": 1}

    for dimension in ("asset_type", "status"):
        keys = list(unselected[dimension])
        assert keys == sorted(keys), f"{dimension} keys must be sorted"
        assert all(isinstance(v, int) for v in unselected[dimension].values())
    assert all(isinstance(v, int) for v in unselected["has_evidence"].values())


def test_facets_q_narrows_the_shared_base(facets_fixtures) -> None:  # type: ignore[no-untyped-def]
    _, household_id = facets_fixtures
    with TestClient(app) as client:
        body = _facets(client, household_id, q="Kitchen")

    assert body["asset_type"] == {"appliance": 1, "furniture": 1}
    assert sum(body["asset_type"].values()) == 2
    assert body["status"] == {"ACTIVE": 1, "ARCHIVED": 1}
    assert body["has_evidence"] == {"with": 2, "without": 0}


def test_facets_empty_household_is_empty_maps_not_error(facets_fixtures) -> None:  # type: ignore[no-untyped-def]
    session, _ = facets_fixtures
    empty = Household(name="Empty Facets Household")
    session.add(empty)
    session.commit()
    with TestClient(app) as client:
        body = _facets(client, empty.id)

    assert body == {"asset_type": {}, "status": {}, "has_evidence": {}}


def test_facets_aggregate_statements_compile_for_postgresql(facets_fixtures) -> None:  # type: ignore[no-untyped-def]
    """PG-SC-12 / dialect: the real facet statements compile under PostgreSQL.

    `test_postgres_dialect.py` only compiles table metadata, so this asserts the
    endpoint's own aggregate SQL (count + group_by and the evidence subquery) is
    dialect-neutral rather than SQLite-specific.
    """
    from app.api.v1.assets import _facet_queries
    from app.models import Asset, asset_evidence

    engine = create_engine("sqlite://")
    db = sessionmaker(bind=engine)()
    try:
        queries = _facet_queries(
            db, "household-x", q=None, asset_type=None, status=None, has_evidence=None
        )
        pg = postgresql_dialect()
        for dimension in ("asset_type", "status"):
            sql = str(queries[dimension].statement.compile(dialect=pg))
            assert "count(" in sql.lower(), dimension
        evidence_sql = str(
            queries["has_evidence"]
            .filter(Asset.id.in_(db.query(asset_evidence.c.asset_id)))
            .statement.compile(dialect=pg)
        )
        assert "asset_evidence" in evidence_sql
        assert "strftime" not in evidence_sql.lower()
    finally:
        db.close()
        engine.dispose()
