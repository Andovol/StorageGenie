"""SG-029 G1: SG-029 image-corpus integrity + scorer discrimination (offline).

Every gate is local: no key, no network. The corpus is the committed synthetic
Food/Medicine set under `eval/corpus/sg029/`; its manifest is the count authority
(replacing the SG-026 hardcoded `!= 5`). Images are rendered by the committed
`generate.py` recipe and carry no EXIF/GPS; nothing here reads `/data/storage`.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

from PIL import Image

BACKEND_DIR = Path(__file__).resolve().parent.parent
SG029_DIR = BACKEND_DIR / "eval" / "corpus" / "sg029"
MANIFEST = SG029_DIR / "manifest.json"
RUN_PY = BACKEND_DIR / "eval" / "run.py"

EXPECTATION_CLASSES = frozenset({"exact", "unknown-expected", "needs-evidence"})
CASE_CLASSES = frozenset({"clean", "glare", "clutter", "partial-label", "no-date-visible"})
CATEGORIES = frozenset({"food", "medicine"})


def _load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("sg029_eval_run", RUN_PY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = _load_runner()


def _manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _fixtures() -> list[dict[str, Any]]:
    manifest = _manifest()
    return [
        json.loads((SG029_DIR / name).read_text(encoding="utf-8"))
        for name in manifest["fixtures"]
    ]


def test_manifest_counts_match_committed_fixtures() -> None:
    manifest = _manifest()
    listed = manifest["fixtures"]
    assert manifest["count"] == len(listed)
    on_disk = sorted(p.name for p in SG029_DIR.glob("*.json") if p.name != MANIFEST.name)
    assert on_disk == sorted(listed), "committed fixture files must match the manifest exactly"
    assert manifest["count"] <= 10, "corpus ceiling is 10 fixtures"


def test_every_fixture_has_image_truth_class_and_category() -> None:
    ids: list[str] = []
    for raw in _fixtures():
        for key in ("id", "class", "category", "image", "ground_truth"):
            assert key in raw, f"{raw.get('id')}: missing {key!r}"
        assert raw["class"] in CASE_CLASSES, raw["class"]
        assert raw["category"] in CATEGORIES, raw["category"]
        image = SG029_DIR / str(raw["image"])
        assert image.is_file(), f"missing image {image}"
        ground = raw["ground_truth"]
        for key in ("items", "unknowns", "needs_evidence", "expectation_class"):
            assert key in ground, f"{raw['id']}: ground truth missing {key!r}"
        assert ground["expectation_class"] in EXPECTATION_CLASSES
        ids.append(str(raw["id"]))
    assert len(set(ids)) == len(ids), "fixture ids must be unique"


def test_both_categories_and_all_case_shapes_present() -> None:
    fixtures = _fixtures()
    assert {raw["category"] for raw in fixtures} == {"food", "medicine"}
    assert {raw["class"] for raw in fixtures} == CASE_CLASSES
    assert any(raw["ground_truth"]["expectation_class"] != "exact" for raw in fixtures), (
        "at least one deliberately hard/expected-unknown case is required"
    )


def test_provider_output_cache_parses_strictly() -> None:
    fixtures = _fixtures()
    cached = [raw for raw in fixtures if "provider_output" in raw]
    assert cached, "no committed provider_output cache: the one metered run has not happened"
    for raw in cached:
        parsed = RUNNER.parse_extraction_output(raw["provider_output"])
        assert parsed.items or raw["provider_output"]["items"] == []


def test_images_are_synthetic_pngs_with_no_exif() -> None:
    for raw in _fixtures():
        image = SG029_DIR / str(raw["image"])
        with Image.open(image) as img:
            assert img.format == "PNG", image.name
            assert dict(img.getexif()) == {}, f"{image.name}: EXIF/GPS must not survive"
    assert (SG029_DIR / "generate.py").is_file(), "the committed render recipe must ship"


def test_scorer_discriminates_below_one_for_a_recorded_reason() -> None:
    """A guessed date where the truth is unknown must score below a perfect read.

    A scorer that cannot go below 1.0 measures nothing (SG-026 baseline note) —
    this is the non-vacuous discrimination proof.
    """
    perfect = {
        "provider_output": {
            "items": [
                {
                    "name": "Milk",
                    "expiry_date": "2031-03-15",
                    "date_type": "expiry_date",
                    "confidence": 1.0,
                    "uncertainty_reasons": [],
                }
            ],
            "unknowns": [],
            "needs_evidence": False,
        },
        "ground_truth": {
            "items": [{"name": "Milk", "expiry_date": "2031-03-15"}],
            "unknowns": [],
            "needs_evidence": False,
            "expectation_class": "exact",
        },
    }
    miss = {
        "provider_output": {
            "items": [
                {
                    "name": "Orange juice",
                    "expiry_date": "2031-08-12",
                    "date_type": "best_before",
                    "confidence": 0.9,
                    "uncertainty_reasons": ["glare"],
                }
            ],
            "unknowns": [],
            "needs_evidence": False,
        },
        "ground_truth": {
            "items": [{"name": "Orange juice", "expiry_date": None}],
            "unknowns": ["items.0.expiry_date"],
            "needs_evidence": True,
            "expectation_class": "unknown-expected",
        },
    }
    assert RUNNER.score_fixture(perfect)["overall"] == 1.0
    scored = RUNNER.score_fixture(miss)
    assert scored["overall"] < 1.0
    assert scored["items"] == 0.0, "a guessed date against an unknown-truth must miss"
