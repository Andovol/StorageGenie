"""SG-093: vendored Google Product Taxonomy + pure offline resolver + bucket map.

Every pin here drives the REAL resolver over the REAL vendored file
(``backend/app/data/google_taxonomy/2021-09-21.txt``); nothing is re-implemented
in the test. The module performs no network, no clock and no I/O beyond that one
file, which the source-level pin below asserts.
"""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.services import google_taxonomy
from app.services.google_taxonomy import (
    ACCEPT_MARGIN,
    ACCEPT_SCORE,
    TAXONOMY_VERSION,
    TOP_K,
    bucket_for,
    resolve_google_type,
)
from app.services.providers import reader
from app.services.providers.schemas import ExtractionItem, parse_extraction_output

BEER_PATH = "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Beer"
BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
SPEC_PATH = (
    REPO_ROOT / "docs" / "superpowers" / "specs" / "2026-09-21-google-taxonomy-design.md"
)
V4_FIELD = "google_type_proposed"
V4_CATEGORIES = ("food", "medicine", "cosmetics")


def test_exact_path_resolves_with_id_and_version() -> None:
    r = resolve_google_type(BEER_PATH)
    assert r.status == "resolved"
    assert r.taxonomy_version == "2021-09-21"
    assert r.google_type_id == "414"
    assert r.google_type_path == BEER_PATH
    assert r.score == 1.0


def test_exact_match_is_whitespace_and_case_insensitive() -> None:
    r = resolve_google_type("  food,   BEVERAGES & tobacco > beverages ")
    assert r.status == "resolved"
    assert r.google_type_id == "413"


def test_below_threshold_is_unclear_never_mapped() -> None:
    r = resolve_google_type("vague paraphrase with no close node")
    assert r.status == "unclear"
    assert r.google_type_id is None
    assert r.google_type_path is None


def test_unclear_still_stamps_taxonomy_version() -> None:
    r = resolve_google_type("vague paraphrase with no close node")
    assert r.status == "unclear"
    assert r.taxonomy_version == "2021-09-21"


def test_none_proposal_is_uncategorized() -> None:
    assert resolve_google_type(None).status == "uncategorized"


def test_blank_proposal_is_uncategorized() -> None:
    r = resolve_google_type("   ")
    assert r.status == "uncategorized"
    assert r.google_type_id is None


def test_food_subtree_maps_to_food_bucket() -> None:
    assert bucket_for("414", "Food, Beverages & Tobacco > Beverages") == "food_beverages"


def test_out_of_scope_retains_type_with_non_perishable() -> None:
    assert bucket_for("222", "Electronics") == "non_perishable"


def test_pharma_exception_beats_health_beauty_default() -> None:
    assert (
        bucket_for("518", "Health & Beauty > Health Care > Medicine & Drugs")
        == "medicine_pharma"
    )


def test_health_beauty_default_is_cosmetics() -> None:
    assert (
        bucket_for(None, "Health & Beauty > Personal Care > Cosmetics")
        == "cosmetics_personal_care"
    )


def test_unknown_top_level_is_uncategorized() -> None:
    assert bucket_for(None, "Nonexistent Realm > Widgets") == "uncategorized"


def test_bucket_for_resolves_path_from_id_when_path_absent() -> None:
    assert bucket_for("412", None) == "food_beverages"


def test_bucket_for_nothing_is_uncategorized() -> None:
    assert bucket_for(None, None) == "uncategorized"


def test_accept_thresholds_are_the_designed_constants() -> None:
    assert (ACCEPT_SCORE, ACCEPT_MARGIN, TOP_K) == (0.6, 0.15, 5)
    assert TAXONOMY_VERSION == "2021-09-21"


def test_resolver_source_has_no_network_imports() -> None:
    src = Path(google_taxonomy.__file__).read_text(encoding="utf-8")
    for banned in ("httpx", "urllib", "socket", "requests", "aiohttp"):
        assert banned not in src, banned


def test_accept_gate_is_load_bearing(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Non-vacuity: a partial overlap is unclear until the accept gates are removed."""
    proposal = "Alcoholic"
    assert resolve_google_type(proposal).status == "unclear"
    monkeypatch.setattr(google_taxonomy, "ACCEPT_SCORE", 0.0)
    monkeypatch.setattr(google_taxonomy, "ACCEPT_MARGIN", 0.0)
    assert resolve_google_type(proposal).status == "resolved"


def test_pharma_prefix_is_load_bearing(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Non-vacuity: the pharma pin depends on the enumerated prefix row."""
    path = "Health & Beauty > Health Care > Medicine & Drugs"
    assert bucket_for("518", path) == "medicine_pharma"
    monkeypatch.setattr(
        google_taxonomy,
        "_norm_bucket_prefixes",
        lambda: (("health & beauty", "cosmetics_personal_care"),),
    )
    assert bucket_for("518", path) == "cosmetics_personal_care"


# --------------------------------------------------------------------------- #
# SG-094 T2 — `google_type_proposed` schema field (transcribe-only, nullable)
# --------------------------------------------------------------------------- #
def _base_item(**overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "name": "Milk",
        "expiry_date": "2031-03-15",
        "date_type": "best_before",
        "confidence": 1.0,
        "uncertainty_reasons": [],
    }
    item.update(overrides)
    return item


def _base_payload(item: dict[str, object], **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {"items": [item], "unknowns": [], "needs_evidence": False}
    payload.update(overrides)
    return payload


def _spec_block() -> str:
    """The v4 prompt block exactly as the spec (the authority) quotes it."""
    text = SPEC_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"Added block \(packets quote this file, never chat\):\n\n```\n(.*?)\n```",
        text,
        re.DOTALL,
    )
    assert match is not None, "spec S2 v4 prompt block not found"
    return match.group(1)


def test_google_type_proposed_declared_nullable_beside_v3_fields() -> None:
    assert V4_FIELD in ExtractionItem.model_fields
    assert ExtractionItem.model_fields[V4_FIELD].default is None
    parsed = parse_extraction_output(_base_payload(_base_item()))
    assert getattr(parsed.items[0], V4_FIELD) is None


def test_google_type_proposed_parses_verbatim_when_present() -> None:
    path = "Food, Beverages & Tobacco > Beverages"
    parsed = parse_extraction_output(_base_payload(_base_item(**{V4_FIELD: path})))
    assert getattr(parsed.items[0], V4_FIELD) == path


def test_blank_google_type_proposed_is_rejected() -> None:
    with pytest.raises(ValidationError) as exc:
        parse_extraction_output(_base_payload(_base_item(**{V4_FIELD: "  "})))
    assert f"{V4_FIELD} must be non-blank when present" in str(exc.value)


def test_unknowns_entry_for_google_type_proposed_validates_with_null() -> None:
    honest = _base_payload(_base_item(**{V4_FIELD: None}), unknowns=[f"items.0.{V4_FIELD}"])
    parsed = parse_extraction_output(honest)
    assert parsed.unknowns == [f"items.0.{V4_FIELD}"]
    assert getattr(parsed.items[0], V4_FIELD) is None

    fabricated = deepcopy(honest)
    fabricated["items"][0][V4_FIELD] = "Food, Beverages & Tobacco"  # type: ignore[index]
    with pytest.raises(ValidationError):
        parse_extraction_output(fabricated)


# --------------------------------------------------------------------------- #
# SG-094 T2 — frozen v4 prompts load through the REAL loader (PG-SC-12)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("category", V4_CATEGORIES)
def test_v4_prompt_loads_through_real_loader_as_v3_plus_block(
    category: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """v4 = live v3 loader output + spec block + front-matter bump; v3 untouched."""
    block = _spec_block()
    v3_text, v3_version = reader.load_prompt(category)
    assert v3_version == f"extract-{category}-v3"
    assert block not in v3_text
    assert V4_FIELD not in v3_text

    monkeypatch.setitem(reader.PROMPT_FILES, category, f"extract-{category}-v4.md")
    v4_text, v4_version = reader.load_prompt(category)
    assert v4_version == f"extract-{category}-v4"
    assert block in v4_text

    expected = v3_text.replace(
        f"template_version: extract-{category}-v3",
        f"template_version: extract-{category}-v4",
    ).replace("\n## Repair\n", f"\n{block}\n\n## Repair\n", 1)
    assert v4_text == expected
    assert v4_text != v3_text
