"""SG-079 schema v3 contract + frozen v3 prompt + fixture scoring (offline only).

Proves the properties this slice adds, measured with the real `schemas` module
and the committed corpus files (no key, no network, no metered call — $0):

- G1: the eleven new transcribed-only fields parse when transcribed, are legal
  when null (with an `unknowns` entry), reject a fabricated value beside an
  `unknowns` entry, reject blank string fields / blank list entries, and still
  never parse prose.
- G2: the three frozen v3 prompt files exist with the exact envelope front
  matter and name every new field; the live `PROMPT_FILES` map still points at
  v2 (the running pipeline is untouched); v1/v2 files remain on disk. The
  sgo79 fixtures score through the real schema module and a wrong transcription
  scores below perfect (non-vacuous).
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.services.providers import reader
from app.services.providers.schemas import ExtractionItem, parse_extraction_output

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BACKEND_DIR / "app" / "services" / "providers" / "prompts"
SG079_DIR = BACKEND_DIR / "eval" / "corpus" / "sg079"

CATEGORIES = ("food", "medicine", "cosmetics")
NEW_STRING_FIELDS = (
    "brand",
    "variant",
    "size_text",
    "barcode",
    "category_proposed",
    "transcript",
    "storage",
    "nutrition_per100g",
    "nutrition_serving",
)
NEW_LIST_FIELDS = ("warnings", "allergens")
NEW_FIELDS = NEW_STRING_FIELDS + NEW_LIST_FIELDS
V1_PROMPTS = ("extract-food-v1.md", "extract-medicine-v1.md", "extract-cosmetics-v1.md")


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


def _transcribed_item() -> dict[str, object]:
    return _valid_item(
        brand="DairyGold",
        variant="Semi-skimmed",
        size_text="1 L",
        barcode="5012345678900",
        category_proposed="dairy",
        transcript="DairyGold Semi-skimmed Milk 1 L Best before 2031-03-15",
        storage="Keep refrigerated below 5 C",
        warnings=["Not suitable for freezing"],
        allergens=["milk"],
        nutrition_per100g="Energy 250 kJ / 60 kcal; Fat 3.2 g; Protein 3.4 g",
        nutrition_serving="Per 250 ml: Energy 150 kcal",
    )


# --------------------------------------------------------------------------- #
# G1 — schema v3
# --------------------------------------------------------------------------- #
def test_v3_schema_declares_all_new_fields() -> None:
    assert set(NEW_FIELDS).issubset(set(ExtractionItem.model_fields))


def test_v3_transcribed_fields_parse_verbatim() -> None:
    item = _transcribed_item()
    parsed = parse_extraction_output(_payload(item))
    got = parsed.items[0]
    for field in NEW_STRING_FIELDS:
        assert getattr(got, field) == item[field], field
    assert got.warnings == ["Not suitable for freezing"]
    assert got.allergens == ["milk"]


def test_v3_null_new_fields_are_legal() -> None:
    nulls = {field: None for field in NEW_FIELDS}
    parsed = parse_extraction_output(_payload(_valid_item(**nulls)))
    for field in NEW_FIELDS:
        assert getattr(parsed.items[0], field) is None, field


@pytest.mark.parametrize("field", NEW_STRING_FIELDS)
@pytest.mark.parametrize("bad", ["", "   ", "\t"])
def test_v3_blank_string_fields_rejected(field: str, bad: str) -> None:
    with pytest.raises(ValidationError):
        parse_extraction_output(_payload(_valid_item(**{field: bad})))


@pytest.mark.parametrize("field", NEW_LIST_FIELDS)
@pytest.mark.parametrize("bad", [[""], ["   "], "milk"])
def test_v3_bad_list_fields_rejected(field: str, bad: object) -> None:
    with pytest.raises(ValidationError):
        parse_extraction_output(_payload(_valid_item(**{field: bad})))


@pytest.mark.parametrize("field", NEW_STRING_FIELDS)
def test_v3_unknowns_rule_rejects_fabricated_string_field(field: str) -> None:
    honest = _payload(_valid_item(**{field: None}))
    honest["unknowns"] = [f"items.0.{field}"]
    parsed = parse_extraction_output(honest)
    assert getattr(parsed.items[0], field) is None

    fabricated = deepcopy(honest)
    fabricated["items"][0][field] = "guessed"  # type: ignore[index]
    with pytest.raises(ValidationError):
        parse_extraction_output(fabricated)


@pytest.mark.parametrize("field", NEW_LIST_FIELDS)
def test_v3_unknowns_rule_rejects_fabricated_list_field(field: str) -> None:
    honest = _payload(_valid_item(**{field: None}))
    honest["unknowns"] = [f"items.0.{field}"]
    assert parse_extraction_output(honest).items[0] is not None

    empty_beside_unknown = deepcopy(honest)
    empty_beside_unknown["items"][0][field] = []  # type: ignore[index]
    parse_extraction_output(empty_beside_unknown)  # [] == absent, legal

    fabricated = deepcopy(honest)
    fabricated["items"][0][field] = ["guessed"]  # type: ignore[index]
    with pytest.raises(ValidationError):
        parse_extraction_output(fabricated)


def test_v3_prose_is_never_parsed_even_naming_new_fields() -> None:
    prose = "brand: DairyGold; allergens: milk; transcript: hello world"
    with pytest.raises(ValidationError):
        parse_extraction_output(prose)


def test_v3_unknown_field_still_forbidden() -> None:
    with pytest.raises(ValidationError):
        parse_extraction_output(_payload(_valid_item(made_up_field="x")))


# --------------------------------------------------------------------------- #
# G2 — frozen v3 prompts + live path untouched
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("category", CATEGORIES)
def test_v3_prompt_file_frozen_with_exact_front_matter(category: str) -> None:
    path = PROMPTS_DIR / f"extract-{category}-v3.md"
    assert path.is_file(), f"missing v3 prompt: {path.name}"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), "front matter must open the file"
    header = text.split("---\n", 2)[1]
    assert f"template_version: extract-{category}-v3" in header
    assert "output_schema: ExtractionOutput" in header
    assert "repair_policy: single-retry-then-fail" in header
    assert "category:" in header
    for field in NEW_FIELDS:
        assert field in text, f"{category} v3 prompt never names {field}"
    assert "items.<index>.<field>" in text
    assert "needs_evidence" in text
    assert "JSON ONLY" in text
    assert "## Repair" in text


def test_v1_and_v2_prompt_files_still_ship() -> None:
    for category in CATEGORIES:
        for version in ("v1", "v2"):
            assert (PROMPTS_DIR / f"extract-{category}-{version}.md").is_file()


def test_live_prompt_map_still_points_at_v2() -> None:
    assert reader.PROMPT_FILES == {
        "food": "extract-food-v2.md",
        "medicine": "extract-medicine-v2.md",
        "cosmetics": "extract-cosmetics-v2.md",
    }
    for category in CATEGORIES:
        _text, version = reader.load_prompt(category)
        assert version == f"extract-{category}-v2"


# --------------------------------------------------------------------------- #
# G2 — fixture scoring through the real schema module
# --------------------------------------------------------------------------- #
def _sg079_fixtures() -> list[dict[str, object]]:
    manifest = json.loads((SG079_DIR / "manifest.json").read_text(encoding="utf-8"))
    return [
        json.loads((SG079_DIR / name).read_text(encoding="utf-8"))
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


def test_sg079_fixtures_score_and_unknowns_are_honest() -> None:
    fixtures = _sg079_fixtures()
    assert len(fixtures) == 6, "expected six sg079 fixtures"
    for raw in fixtures:
        parsed = parse_extraction_output(raw["provider_output"])
        for entry in parsed.unknowns:
            _, index_text, field = entry.split(".")
            assert getattr(parsed.items[int(index_text)], field) is None, entry
        assert _score_new_fields(raw) == 1.0, raw["id"]

    accuracy = sum(_score_new_fields(raw) for raw in fixtures) / len(fixtures)
    assert accuracy == 1.0


def test_sg079_fixture_miss_scores_below_perfect() -> None:
    miss = deepcopy(_sg079_fixtures()[0])
    miss["provider_output"]["items"][0]["brand"] = "wrong-brand"  # type: ignore[index]
    assert _score_new_fields(miss) < 1.0
