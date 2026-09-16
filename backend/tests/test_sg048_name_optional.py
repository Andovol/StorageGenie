from __future__ import annotations

import io
import json
import uuid
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from PIL import Image
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Assertion, Household
from app.schemas.asset import AssetOut
from app.services.asset_service import create_asset
from app.services.evidence_service import store_evidence

HEAD_REVISION = "20260916_sg048_name_optional"
PREVIOUS_REVISION = "20260914_sg035_foundations"


def _alembic_config(url: str) -> Config:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def _display_name_notnull(url: str) -> int:
    engine = create_engine(url)
    with engine.connect() as conn:
        rows = conn.execute(text("PRAGMA table_info(asset)")).fetchall()
    engine.dispose()
    return next(row for row in rows if row[1] == "display_name")[3]


def _fts_trigger_names(url: str) -> set[str]:
    engine = create_engine(url)
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'asset_fts%'")
        ).fetchall()
    engine.dispose()
    return {row[0] for row in rows}


def test_sg048_migration_round_trip_restores_nullability(tmp_path: Path, monkeypatch) -> None:
    url = f"sqlite:///{tmp_path / 'roundtrip.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    config = _alembic_config(url)

    command.upgrade(config, "head")
    assert _display_name_notnull(url) == 0
    assert _fts_trigger_names(url) == {
        "asset_fts_after_insert",
        "asset_fts_after_update",
        "asset_fts_after_delete",
    }

    command.downgrade(config, PREVIOUS_REVISION)
    assert _display_name_notnull(url) == 1

    command.upgrade(config, "head")
    assert _display_name_notnull(url) == 0


def test_sg048_nameless_row_survives_upgrade_and_blocks_downgrade(
    tmp_path: Path, monkeypatch
) -> None:
    url = f"sqlite:///{tmp_path / 'nameless.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    config = _alembic_config(url)
    command.upgrade(config, "head")

    household_id = uuid.uuid4().hex
    asset_id = uuid.uuid4().hex
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO household (id, name) VALUES (:id, 'H')"), {"id": household_id})
        conn.execute(
            text(
                "INSERT INTO asset (id, household_id, display_name, asset_type, status, version) "
                "VALUES (:id, :h, NULL, 'unknown', 'ACTIVE', 1)"
            ),
            {"id": asset_id, "h": household_id},
        )
        assert (
            conn.execute(
                text("SELECT display_name FROM asset WHERE id = :id"), {"id": asset_id}
            ).scalar()
            is None
        )

    with pytest.raises(RuntimeError):
        command.downgrade(config, PREVIOUS_REVISION)

    with engine.connect() as conn:
        assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == HEAD_REVISION
        assert conn.execute(text("SELECT count(*) FROM asset")).scalar() == 1
    engine.dispose()


def _jpeg_bytes() -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (16, 16), "red").save(output, format="JPEG")
    return output.getvalue()


def test_nameless_create_through_full_migration_chain(tmp_path: Path, monkeypatch) -> None:
    """The nameless-create path against the real schema, not a hand-built one.

    Mirrors production: a scratch SQLite upgraded from base through every
    revision, then the API service writes a nameless row (NULL) and a named
    row. No test rows ever touch the production database.
    """
    url = f"sqlite:///{tmp_path / 'fullchain.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    command.upgrade(_alembic_config(url), "head")

    engine = create_engine(url)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    try:
        household = Household(name="Full chain household")
        session.add(household)
        session.commit()

        nameless = create_asset(session, household.id, {"status": "ACTIVE"})
        assert nameless.display_name is None
        assert (
            session.query(Assertion)
            .filter_by(asset_id=nameless.id, field_path="display_name")
            .count()
            == 0
        )

        named = create_asset(session, household.id, {"display_name": "Toothpaste"})
        assert named.display_name == "Toothpaste"
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def asset_db(tmp_path: Path, monkeypatch):  # type: ignore[no-untyped-def]
    from app.db import Base

    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    engine = create_engine(
        f"sqlite:///{tmp_path / 'assets.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="SG-048 Household")
    session.add(household)
    session.commit()
    try:
        yield session, household.id
    finally:
        session.close()
        engine.dispose()


def _evidence(session: Session, household_id: str, filename: str) -> object:
    return store_evidence(_jpeg_bytes(), filename, "image/jpeg", household_id, session)


def test_nameless_with_evidence_uses_photo_stem_deterministic_assertion(asset_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = asset_db
    evidence = _evidence(session, household_id, "before-photo.jpg")

    asset = create_asset(
        session,
        household_id,
        {"display_name": None, "asset_type": "unknown", "evidence_ids": [evidence.id]},
    )

    assert asset.display_name == "before-photo"
    assertion = (
        session.query(Assertion)
        .filter_by(asset_id=asset.id, field_path="display_name")
        .one()
    )
    assert assertion.source_type == "deterministic"
    assert assertion.review_state == "accepted"
    assert json.loads(assertion.value_json) == "before-photo"


def test_nameless_photoless_stores_null_and_writes_no_assertion(asset_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = asset_db

    asset = create_asset(
        session, household_id, {"asset_type": "unknown", "status": "ACTIVE"}
    )

    assert asset.display_name is None
    assert (
        session.query(Assertion)
        .filter_by(asset_id=asset.id, field_path="display_name")
        .count()
        == 0
    )
    # AssetOut carries the NULL through, it does not coerce it to a string.
    assert AssetOut.model_validate(asset).display_name is None


def test_blank_name_is_missing_in_both_branches(asset_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = asset_db
    evidence = _evidence(session, household_id, "pasted-shot.png")

    with_evidence = create_asset(
        session,
        household_id,
        {"display_name": "   ", "evidence_ids": [evidence.id]},
    )
    assert with_evidence.display_name == "pasted-shot"

    without_evidence = create_asset(session, household_id, {"display_name": " \t "})
    assert without_evidence.display_name is None
    assert (
        session.query(Assertion)
        .filter_by(asset_id=without_evidence.id, field_path="display_name")
        .count()
        == 0
    )


def test_supplied_name_is_user_and_unchanged(asset_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = asset_db

    asset = create_asset(session, household_id, {"display_name": "Toothpaste"})

    assert asset.display_name == "Toothpaste"
    assertion = (
        session.query(Assertion)
        .filter_by(asset_id=asset.id, field_path="display_name")
        .one()
    )
    assert assertion.source_type == "user"
    assert assertion.review_state == "accepted"


def test_nameless_asset_neither_errors_nor_corrupts_fts(asset_db) -> None:  # type: ignore[no-untyped-def]
    from app.services.fts import ensure_asset_fts, rebuild_asset_fts

    session, household_id = asset_db
    named = create_asset(session, household_id, {"display_name": "Toothbrush"})
    nameless = create_asset(session, household_id, {"display_name": None})

    engine = session.get_bind()
    with engine.connect() as connection:
        ensure_asset_fts(connection)
        rebuild_asset_fts(connection)

    matched = {
        row[0]
        for row in session.execute(
            text("SELECT asset_id FROM asset_fts WHERE asset_fts MATCH :query"),
            {"query": '"Toothbrush"'},
        ).fetchall()
    }
    assert named.id in matched
    assert nameless.id not in matched


def test_catalog_builders_tolerate_null_name(asset_db) -> None:  # type: ignore[no-untyped-def]
    from app.services.chat.service import CLASSIFICATION_FIELD as CHAT_FIELD
    from app.services.chat.service import build_catalog as build_chat_catalog
    from app.services.planning.service import CLASSIFICATION_FIELD as PLANNING_FIELD
    from app.services.planning.service import build_catalog as build_planning_catalog

    session, household_id = asset_db
    nameless = create_asset(
        session, household_id, {"display_name": None, "status": "ACTIVE"}
    )
    session.add(
        Assertion(
            asset_id=nameless.id,
            field_path=CHAT_FIELD,
            value_json=json.dumps({"category": "food_beverages"}),
            source_type="user",
            review_state="accepted",
        )
    )
    session.add(
        Assertion(
            asset_id=nameless.id,
            field_path=PLANNING_FIELD,
            value_json=json.dumps({"category": "food_beverages"}),
            source_type="user",
            review_state="accepted",
        )
    )
    session.commit()

    planning = build_planning_catalog(session, household_id)
    assert planning and planning[0]["label"] is None

    chat = build_chat_catalog(session, household_id, "food")
    assert chat and chat[0]["label"] is None
