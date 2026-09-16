"""SG-049 extraction v2 contract + plumbing + label-pointer tests (offline only).

Covers the properties this slice adds, measured with the fake/scripted seams and
the committed corpus only (no key, no network, no metered call — G0 found
`SG_CONSENT=false`, so the live leg is unrun under the STOP-as-SUCCESS path):

- G1: `quantity`/`unit`/`asset_type` parse; each invalid shape fails; the
  generic `unknowns` rule holds for the new field paths.
- G2: the three configured prompts are v2 and ask for the new fields; the
  outgoing payload shape carries the json_object response-format flag
  (`PG-EV-04`, shape-of-unsent).
- G3: extraction-sourced new fields are ALWAYS `review_state="proposed"`
  (M11/F4 Stage 0), the committed asset carries the values, and a nameless
  asset labels as `Untitled` in BOTH AI catalog builders (F-SG048-2).
- G4: v2 ground truth is scored from authored v2 fixtures, never from the
  frozen SG-029 v1 cache; the scorer discriminates.
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
from app.models import Assertion, Household
from app.models.asset import UNTITLED_LABEL
from app.models.job import Job
from app.services.candidates import (
    GATED_FIELDS,
    build_candidate_from_extraction,
    commit_candidate,
)
from app.services.chat.service import CLASSIFICATION_FIELD as CHAT_FIELD
from app.services.chat.service import build_catalog as build_chat_catalog
from app.services.planning.service import CLASSIFICATION_FIELD as PLANNING_FIELD
from app.services.planning.service import build_catalog as build_planning_catalog
from app.services.providers import reader
from app.services.providers.opencode_go import build_chat_payload
from app.services.providers.schemas import parse_extraction_output

BACKEND_DIR = Path(__file__).resolve().parent.parent
V2_DIR = BACKEND_DIR / "eval" / "corpus" / "sg049"
V1_PROMPTS = ("extract-food-v1.md", "extract-medicine-v1.md", "extract-cosmetics-v1.md")
NEW_FIELDS = ("quantity", "unit", "asset_type")


def _valid_item(**overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "name": "Milk",
        "expiry_date": "2031-03-15",
        "date_type": "best_before",
        "quantity": 2,
        "unit": "bottles",
        "asset_type": "beverage",
        "confidence": 1.0,
        "uncertainty_reasons": [],
    }
    item.update(overrides)
    return item


def _payload(item: dict[str, object], **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {"items": [item], "unknowns": [], "needs_evidence": False}
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# G1 — schema v2
# --------------------------------------------------------------------------- #
def test_v2_fields_parse() -> None:
    parsed = parse_extraction_output(_payload(_valid_item()))
    item = parsed.items[0]
    assert item.quantity == 2.0
    assert item.unit == "bottles"
    assert item.asset_type == "beverage"


@pytest.mark.parametrize("bad", [-1, -0.5, float("nan"), float("inf"), "two"])
def test_v2_invalid_quantity_rejected(bad: object) -> None:
    with pytest.raises(ValidationError):
        parse_extraction_output(_payload(_valid_item(quantity=bad)))


@pytest.mark.parametrize(
    "field,bad",
    [
        ("unit", ""),
        ("unit", "   "),
        ("unit", 5),
        ("unit", "x" * 51),
        ("asset_type", ""),
        ("asset_type", "\t"),
        ("asset_type", ["beverage"]),
        ("asset_type", "y" * 51),
    ],
)
def test_v2_blank_or_oversized_text_fields_rejected(field: str, bad: object) -> None:
    with pytest.raises(ValidationError):
        parse_extraction_output(_payload(_valid_item(**{field: bad})))


def test_v2_null_new_fields_are_legal() -> None:
    parsed = parse_extraction_output(
        _payload(_valid_item(quantity=None, unit=None, asset_type=None))
    )
    assert parsed.items[0].quantity is None
    assert parsed.items[0].unit is None
    assert parsed.items[0].asset_type is None


def test_v2_unknowns_rule_holds_for_new_field_paths() -> None:
    honest = _payload(_valid_item(quantity=None, unit=None, asset_type=None))
    honest["unknowns"] = ["items.0.quantity", "items.0.unit", "items.0.asset_type"]
    out = parse_extraction_output(honest)
    assert out.items[0].quantity is None
    assert set(out.unknowns) == {"items.0.quantity", "items.0.unit", "items.0.asset_type"}

    fabricated = deepcopy(honest)
    fabricated["items"][0]["quantity"] = 3  # type: ignore[index]
    with pytest.raises(ValidationError):
        parse_extraction_output(fabricated)


# --------------------------------------------------------------------------- #
# G2 — prompts v2 + outgoing shape (PG-EV-04)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("category", ["food", "medicine", "cosmetics"])
def test_configured_prompts_are_v2_and_ask_for_new_fields(category: str) -> None:
    text, version = reader.load_prompt(category)
    assert version == f"extract-{category}-v2"
    for field in NEW_FIELDS:
        assert field in text, f"{category} v2 prompt never names {field}"
    assert "never infer beyond visible evidence" in text


def test_v1_prompt_files_still_ship() -> None:
    prompts_dir = BACKEND_DIR / "app" / "services" / "providers" / "prompts"
    for name in V1_PROMPTS:
        assert (prompts_dir / name).is_file(), f"frozen v1 prompt missing: {name}"


def test_v2_request_payload_shape_carries_prompt_and_json_object_flag() -> None:
    """PG-EV-04: the outgoing wire shape is asserted, not mocked away."""
    prompt, _ = reader.load_prompt("food")
    for field in NEW_FIELDS:
        assert field in prompt
    payload = build_chat_payload("deepseek-v4-flash-vision-exp", prompt, "AAAA")
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["stream"] is False
    content = payload["messages"][0]["content"]
    assert any(part.get("text") == prompt for part in content)


# --------------------------------------------------------------------------- #
# Shared scratch DB helpers
# --------------------------------------------------------------------------- #
def _scratch_db(tmp_path: Path, name: str):  # type: ignore[no-untyped-def]
    engine = create_engine(
        f"sqlite:///{tmp_path / name}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session: Session = factory()
    household = Household(name=f"SG-049 {name}")
    session.add(household)
    session.commit()
    return session, household.id


def _job(session: Session, household_id: str) -> Job:
    job = Job(
        job_type="import",
        state="RUNNING",
        config_snapshot=json.dumps({"evidence_ids": []}),
        household_id=household_id,
    )
    session.add(job)
    session.commit()
    return job


# --------------------------------------------------------------------------- #
# G3 — candidate plumbing
# --------------------------------------------------------------------------- #
def test_extraction_new_fields_always_proposed_and_committed(tmp_path: Path) -> None:
    session, household_id = _scratch_db(tmp_path, "plumbing.db")
    try:
        job = _job(session, household_id)
        extraction = parse_extraction_output(_payload(_valid_item()))
        candidate = build_candidate_from_extraction(
            session,
            job,
            extraction,
            {
                "provider": "scripted",
                "model": "scripted-model-1",
                "prompt_template_version": "extract-food-v2",
                "provider_call_ids": ["call-1"],
            },
        )
        proposal = json.loads(candidate.proposed_fields_json)
        for field in NEW_FIELDS:
            envelope = proposal["fields"][field]
            assert envelope["source_type"] == "extraction"
            assert envelope["provider_call_id"] == "call-1"
            assert envelope["prompt_template_version"] == "extract-food-v2"
        assert proposal["fields"]["quantity"]["value"] == 2.0
        assert proposal["fields"]["unit"]["value"] == "bottles"
        assert proposal["fields"]["asset_type"]["value"] == "beverage"
        for field in NEW_FIELDS:
            assert field in GATED_FIELDS, f"{field} must be gated"

        candidate.state = "accepted"
        result = commit_candidate(session, candidate)
        session.commit()
        asset_id = str(result["asset_id"])

        by_field = {
            row.field_path: row
            for row in session.query(Assertion).filter_by(asset_id=asset_id)
        }
        for field in NEW_FIELDS:
            assert by_field[field].review_state == "proposed", field
            assert by_field[field].source_type == "extraction", field

        from app.models import Asset

        asset = session.get(Asset, asset_id)
        assert asset is not None
        assert asset.quantity == 2.0
        assert asset.unit == "bottles"
        assert asset.asset_type == "beverage"
    finally:
        session.close()


def test_deterministic_asset_type_default_value_unchanged(tmp_path: Path) -> None:
    """G3: the deterministic `asset_type="unknown"` default itself stays as-is."""
    session, household_id = _scratch_db(tmp_path, "default.db")
    try:
        job = _job(session, household_id)
        extraction = parse_extraction_output(
            _payload(_valid_item(asset_type=None, quantity=None, unit=None))
        )
        candidate = build_candidate_from_extraction(
            session, job, extraction, {"provider": None, "model": None}
        )
        proposal = json.loads(candidate.proposed_fields_json)
        assert proposal["fields"]["asset_type"]["value"] == "unknown"
        assert proposal["fields"]["asset_type"]["source_type"] == "deterministic"
    finally:
        session.close()


def test_nameless_labels_fall_back_in_both_ai_catalogs(tmp_path: Path) -> None:
    """F-SG048-2: the shared constant is read by BOTH catalog builders."""
    session, household_id = _scratch_db(tmp_path, "labels.db")
    try:
        from app.models import Asset

        asset = Asset(
            household_id=household_id,
            display_name=None,
            asset_type="unknown",
            status="ACTIVE",
        )
        session.add(asset)
        session.flush()
        for field_path in (CHAT_FIELD, PLANNING_FIELD):
            session.add(
                Assertion(
                    asset_id=asset.id,
                    field_path=field_path,
                    value_json=json.dumps({"category": "food_beverages"}),
                    source_type="user",
                    review_state="accepted",
                )
            )
        session.commit()

        planning = build_planning_catalog(session, household_id)
        planning_entry = next(item for item in planning if item["id"] == asset.id)
        assert planning_entry["label"] == UNTITLED_LABEL

        chat = build_chat_catalog(session, household_id, "food")
        chat_entry = next(item for item in chat if item["id"] == asset.id)
        assert chat_entry["label"] == UNTITLED_LABEL
        assert UNTITLED_LABEL == "Untitled"
    finally:
        session.close()


# --------------------------------------------------------------------------- #
# G4 — v2 scoring from authored v2 fixtures (never the SG-029 v1 cache)
# --------------------------------------------------------------------------- #
def _v2_fixtures() -> list[dict[str, object]]:
    manifest = json.loads((V2_DIR / "manifest.json").read_text(encoding="utf-8"))
    return [
        json.loads((V2_DIR / name).read_text(encoding="utf-8"))
        for name in manifest["fixtures"]
    ]


def _score_new_fields(raw: dict[str, object]) -> float:
    parsed = parse_extraction_output(raw["provider_output"])
    ground = raw["ground_truth"]
    gt_items = ground["items"]  # type: ignore[index]
    hits = 0
    total = 0
    for index, gt_item in enumerate(gt_items):
        for field in NEW_FIELDS:
            total += 1
            if index < len(parsed.items) and getattr(parsed.items[index], field) == gt_item.get(field):
                hits += 1
    return hits / total if total else 0.0


def test_v2_fixtures_score_and_unknowns_are_honest() -> None:
    fixtures = _v2_fixtures()
    assert fixtures, "no v2 scoring fixtures"
    for raw in fixtures:
        parsed = parse_extraction_output(raw["provider_output"])
        for entry in parsed.unknowns:
            _, index_text, field = entry.split(".")
            assert getattr(parsed.items[int(index_text)], field) is None, entry
        assert _score_new_fields(raw) == 1.0, raw["id"]

    accuracy = sum(_score_new_fields(raw) for raw in fixtures) / len(fixtures)
    assert accuracy == 1.0

    # Non-vacuous: a wrongly transcribed field must score below perfect. (The
    # partial fixture is intentionally not mutated: giving it a quantity while
    # its `unknowns` entry stands is invalid by contract, not a scoring miss.)
    miss = deepcopy(fixtures[0])
    miss["provider_output"]["items"][0]["unit"] = "litres"  # type: ignore[index]
    assert _score_new_fields(miss) < 1.0
