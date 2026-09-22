"""SG-093: vendored Google Product Taxonomy + pure offline resolver + bucket map.

Every pin here drives the REAL resolver over the REAL vendored file
(``backend/app/data/google_taxonomy/2021-09-21.txt``); nothing is re-implemented
in the test. The module performs no network, no clock and no I/O beyond that one
file, which the source-level pin below asserts.
"""

from __future__ import annotations

from pathlib import Path

from app.services import google_taxonomy
from app.services.google_taxonomy import (
    ACCEPT_MARGIN,
    ACCEPT_SCORE,
    TAXONOMY_VERSION,
    TOP_K,
    bucket_for,
    resolve_google_type,
)

BEER_PATH = "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Beer"


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
