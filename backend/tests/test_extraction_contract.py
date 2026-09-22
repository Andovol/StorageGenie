"""Extraction contract tests (SG-026, fake only — no key, no network, no SDK).

Covers: strict schema rejects prose; unknowns honored (absent/empty passes
where evidence is complete, fabricated values fail); repair retried exactly
once then the step fails (fake invalid-JSON-once shape); needs_evidence
output produces the existing manual-entry open task row (not a mock);
corpus integrity (PG-EV-07: input pushed from committed corpus); prompt
files versioned with the provider-neutral no-inference rule.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models import Asset, Household, ReviewTask
from app.plugins.expiry_tracker import EXPIRY_FIELD, apply_extraction_result
from app.services.providers.fake import FakeProvider
from app.services.providers.reader import load_prompt
from app.services.providers.schemas import (
    ExtractionFailedError,
    ExtractionOutput,
    extract_with_single_repair,
    parse_extraction_output,
)

TESTS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TESTS_DIR.parent
CORPUS_DIR = BACKEND_DIR / "eval" / "corpus"
PROMPTS_DIR = BACKEND_DIR / "app" / "services" / "providers" / "prompts"
EXPECTATION_CLASSES = frozenset({"exact", "unknown-expected", "needs-evidence"})


@pytest.fixture
def bridge_db(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(f"sqlite:///{tmp_path / 'bridge.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name="Extraction Bridge Household")
    session.add(household)
    session.commit()
    try:
        yield session, household.id
    finally:
        session.close()
        engine.dispose()


def make_asset(session: Session, household_id: str) -> Asset:
    asset = Asset(household_id=household_id, display_name="Milk carton", asset_type="product", status="ACTIVE")
    session.add(asset)
    session.commit()
    return asset


def test_schema_rejects_prose() -> None:
    with pytest.raises(ValidationError):
        parse_extraction_output("The milk expires sometime next spring, I think.")


def test_unknowns_honored() -> None:
    complete = {
        "items": [
            {
                "name": "Milk",
                "expiry_date": "2030-01-15",
                "date_type": "expiry_date",
                "confidence": 1.0,
                "uncertainty_reasons": [],
            }
        ],
        "unknowns": [],
        "needs_evidence": False,
    }
    assert parse_extraction_output(complete).unknowns == []

    missing_date = {
        "items": [
            {
                "name": "Milk",
                "expiry_date": None,
                "date_type": None,
                "confidence": 0.4,
                "uncertainty_reasons": ["date region blurred by glare"],
            }
        ],
        "unknowns": ["items.0.expiry_date"],
        "needs_evidence": True,
    }
    assert parse_extraction_output(missing_date).needs_evidence is True

    fabricated = {
        "items": [
            {
                "name": "Milk",
                "expiry_date": "2030-01-15",
                "date_type": "expiry_date",
                "confidence": 1.0,
                "uncertainty_reasons": [],
            }
        ],
        "unknowns": ["items.0.expiry_date"],
        "needs_evidence": True,
    }
    with pytest.raises(ValidationError):
        parse_extraction_output(fabricated)


def test_lot_optional_and_fabricated_value_rule() -> None:
    """SG-027 D42(a): `lot` is optional, never required; a value beside an unknowns entry is fabrication."""
    unknown_lot = {
        "items": [
            {
                "name": "Harvest Oats 500g",
                "expiry_date": "2027-03-15",
                "date_type": "best_before",
                "lot": None,
                "confidence": 0.9,
                "uncertainty_reasons": ["torn label: lot region obscured"],
            }
        ],
        "unknowns": ["items.0.lot"],
        "needs_evidence": False,
    }
    out = parse_extraction_output(unknown_lot)
    assert out.items[0].lot is None
    assert out.unknowns == ["items.0.lot"]

    valued = deepcopy(unknown_lot)
    valued["items"][0]["lot"] = "L24-0716"
    valued["unknowns"] = []
    assert parse_extraction_output(valued).items[0].lot == "L24-0716"

    fabricated = deepcopy(unknown_lot)
    fabricated["items"][0]["lot"] = "L24-0716"
    with pytest.raises(ValidationError):
        parse_extraction_output(fabricated)

    non_string = deepcopy(unknown_lot)
    non_string["items"][0]["lot"] = 12345
    non_string["unknowns"] = []
    with pytest.raises(ValidationError):
        parse_extraction_output(non_string)


def test_repair_retried_exactly_once_then_step_fails() -> None:
    fake = FakeProvider(mode="invalid_json_once", provider_id="fake-flaky")

    def supply() -> object:
        result = fake.extract_items(b"img-1", "prompt")
        norm = result.normalized_output
        assert isinstance(norm, dict)
        items = norm.get("items", [])
        assert isinstance(items, list) and items
        first = items[0]
        assert isinstance(first, dict)
        return {
            "items": [
                {
                    "name": str(first.get("name", "fake-item")),
                    "expiry_date": None,
                    "date_type": None,
                    "confidence": 0.4,
                    "uncertainty_reasons": ["fake shape carries no date evidence"],
                }
            ],
            "unknowns": ["items.0.expiry_date"],
            "needs_evidence": bool(norm.get("needs_evidence", False)),
        }

    out = extract_with_single_repair(supply)
    assert isinstance(out, ExtractionOutput)
    assert fake.invocations == 2

    calls = 0

    def always_prose() -> object:
        nonlocal calls
        calls += 1
        return "still just prose, never JSON"

    with pytest.raises(ExtractionFailedError):
        extract_with_single_repair(always_prose)
    assert calls == 2


def test_needs_evidence_produces_manual_entry_task(bridge_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = bridge_db
    asset = make_asset(session, household_id)
    result = ExtractionOutput.model_validate(
        {
            "items": [
                {
                    "name": "Milk",
                    "expiry_date": None,
                    "date_type": None,
                    "confidence": 0.3,
                    "uncertainty_reasons": ["no date visible in frame"],
                }
            ],
            "unknowns": ["items.0.expiry_date"],
            "needs_evidence": True,
        }
    )
    assertion, task = apply_extraction_result(session, asset, result)
    session.commit()

    assert assertion is not None and task is not None
    assert assertion.field_path == EXPIRY_FIELD
    assert assertion.review_state == "needs_evidence"
    assert json.loads(assertion.value_json) == {"status": "unknown"}
    row = session.query(ReviewTask).filter_by(id=task.id).one()
    assert row.task_type == "expiry.manual_entry"
    assert row.status == "open"
    assert row.subject_ref == asset.id


def test_no_bridge_without_needs_evidence(bridge_db) -> None:  # type: ignore[no-untyped-def]
    session, household_id = bridge_db
    asset = make_asset(session, household_id)
    result = parse_extraction_output(
        {
            "items": [
                {
                    "name": "Milk",
                    "expiry_date": "2030-01-15",
                    "date_type": "expiry_date",
                    "confidence": 1.0,
                    "uncertainty_reasons": [],
                }
            ],
            "unknowns": [],
            "needs_evidence": False,
        }
    )
    assertion, task = apply_extraction_result(session, asset, result)
    session.commit()
    assert (assertion, task) == (None, None)
    assert session.query(ReviewTask).filter_by(subject_ref=asset.id).count() == 0


def test_opened_date_honors_iso_discipline() -> None:
    """SG-036: opened_date shares expiry_date's YYYY-MM-DD discipline, not a loose copy."""
    base = {
        "items": [
            {
                "name": "Face cream",
                "expiry_date": None,
                "opened_date": "2031-04-10",
                "date_type": None,
                "confidence": 1.0,
                "uncertainty_reasons": [],
            }
        ],
        "unknowns": [],
        "needs_evidence": False,
    }
    assert parse_extraction_output(base).items[0].opened_date == "2031-04-10"

    for bad in ("2031/04/10", "2031-4-10", "2031-04-10T00:00:00", "not-a-date"):
        broken = deepcopy(base)
        broken["items"][0]["opened_date"] = bad
        with pytest.raises(ValidationError):
            parse_extraction_output(broken)


def test_unknowns_may_name_opened_date() -> None:
    """The unknowns validator reads model_fields, so opened_date flows without a new path."""
    unknown = {
        "items": [
            {
                "name": "Shampoo",
                "expiry_date": None,
                "opened_date": None,
                "date_type": None,
                "confidence": 0.5,
                "uncertainty_reasons": ["opened date not legible"],
            }
        ],
        "unknowns": ["items.0.opened_date"],
        "needs_evidence": True,
    }
    out = parse_extraction_output(unknown)
    assert out.unknowns == ["items.0.opened_date"]
    assert out.items[0].opened_date is None

    fabricated = deepcopy(unknown)
    fabricated["items"][0]["opened_date"] = "2031-04-10"
    with pytest.raises(ValidationError):
        parse_extraction_output(fabricated)


def test_load_prompt_cosmetics_versioned_and_unknown_category_raises() -> None:
    text, version = load_prompt("cosmetics")
    assert version == "extract-cosmetics-v4"
    assert "never infer beyond visible evidence" in text
    assert "opened_date" in text
    with pytest.raises(ValueError):
        load_prompt("does-not-exist")


def test_v2_new_fields_parse_and_invalid_shapes_fail() -> None:
    """SG-049 G1: quantity/unit/asset_type parse; every invalid shape fails."""
    base = {
        "items": [
            {
                "name": "Milk",
                "quantity": 2,
                "unit": "bottles",
                "asset_type": "beverage",
                "confidence": 1.0,
                "uncertainty_reasons": [],
            }
        ],
        "unknowns": [],
        "needs_evidence": False,
    }
    out = parse_extraction_output(base)
    assert out.items[0].quantity == 2.0
    assert out.items[0].unit == "bottles"
    assert out.items[0].asset_type == "beverage"

    for bad in (
        {"quantity": -1},
        {"quantity": float("nan")},
        {"quantity": float("inf")},
        {"quantity": "two"},
        {"unit": ""},
        {"unit": "   "},
        {"unit": "u" * 51},
        {"asset_type": ""},
        {"asset_type": ["beverage"]},
        {"asset_type": "a" * 51},
    ):
        broken = deepcopy(base)
        broken["items"][0].update(bad)
        with pytest.raises(ValidationError):
            parse_extraction_output(broken)


def test_v2_unknowns_entry_rules_hold_for_new_paths() -> None:
    honest = {
        "items": [
            {
                "name": "Tablets",
                "quantity": None,
                "unit": None,
                "asset_type": None,
                "confidence": 0.6,
                "uncertainty_reasons": ["torn label"],
            }
        ],
        "unknowns": ["items.0.quantity", "items.0.unit", "items.0.asset_type"],
        "needs_evidence": False,
    }
    assert set(parse_extraction_output(honest).unknowns) == {
        "items.0.quantity",
        "items.0.unit",
        "items.0.asset_type",
    }

    fabricated = deepcopy(honest)
    fabricated["items"][0]["unit"] = "tablets"
    with pytest.raises(ValidationError):
        parse_extraction_output(fabricated)


def test_corpus_integrity() -> None:
    fixtures = sorted(CORPUS_DIR.glob("*.json"))
    assert len(fixtures) == 5
    for path in fixtures:
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(raw.get("ground_truth"), dict), f"{path.name}: ground truth missing"
        assert raw["ground_truth"].get("expectation_class") in EXPECTATION_CLASSES, (
            f"{path.name}: expectation class missing"
        )
        parse_extraction_output(raw["provider_output"])


def test_prompt_files_versioned() -> None:
    for name in ("extract-food-v1", "extract-medicine-v1", "extract-cosmetics-v1"):
        path = PROMPTS_DIR / f"{name}.md"
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        front_matter = text.split("---\n", 2)[1]
        assert f"template_version: {name}" in front_matter
        assert "never infer beyond visible evidence" in text
