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

import pytest
from PIL import Image

BACKEND_DIR = Path(__file__).resolve().parent.parent
SG029_DIR = BACKEND_DIR / "eval" / "corpus" / "sg029"
MANIFEST = SG029_DIR / "manifest.json"
RUN_PY = BACKEND_DIR / "eval" / "run.py"
EVAL_DIR = BACKEND_DIR / "eval"
CORPUS_ROOT = EVAL_DIR / "corpus"

EXPECTATION_CLASSES = frozenset({"exact", "unknown-expected", "needs-evidence"})
CASE_CLASSES = frozenset({"clean", "glare", "clutter", "partial-label", "no-date-visible"})
CATEGORIES = frozenset({"food", "medicine", "cosmetics"})


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


def test_categories_and_all_case_shapes_present() -> None:
    fixtures = _fixtures()
    assert {raw["category"] for raw in fixtures} == {"food", "medicine", "cosmetics"}
    assert {raw["class"] for raw in fixtures} == CASE_CLASSES
    assert any(raw["ground_truth"]["expectation_class"] != "exact" for raw in fixtures), (
        "at least one deliberately hard/expected-unknown case is required"
    )


def test_cosmetics_fixtures_carry_opened_date_truth() -> None:
    """SG-036: the third category is covered clean/no-date/partial, opened_date first-class."""
    fixtures = [raw for raw in _fixtures() if raw["category"] == "cosmetics"]
    assert {raw["class"] for raw in fixtures} == {"clean", "no-date-visible", "partial-label"}
    for raw in fixtures:
        item = raw["ground_truth"]["items"][0]
        assert "opened_date" in item, f"{raw['id']}: ground truth must carry opened_date"
        assert raw["provider_output"]["items"][0]["opened_date"] == item["opened_date"]
    clean = next(raw for raw in fixtures if raw["class"] == "clean")
    assert clean["ground_truth"]["items"][0]["opened_date"] == "2031-04-10"


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


# --------------------------------------------------------------------------- #
# SG-085: manifest selector + frozen baselines (offline, $0, no scoring hunks)
# --------------------------------------------------------------------------- #
SELECTED_CORPORA = ("sg029", "sg049", "sg079")


def _baseline_payload(corpus: str) -> dict[str, Any]:
    path = EVAL_DIR / f"baseline_{corpus}_frozen.md"
    text = path.read_text(encoding="utf-8")
    assert text.count("```json") == 1, f"{path.name}: expected exactly one ```json block"
    block = text.split("```json", 1)[1].split("```", 1)[0]
    return json.loads(block)


def _score_corpus(corpus: str) -> dict[str, Any]:
    base = CORPUS_ROOT / corpus
    manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    paths = [base / name for name in manifest["fixtures"]]
    rows = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    scores = {str(raw["id"]): RUNNER.score_fixture(raw) for raw in rows}
    field_accuracy = round(sum(line["overall"] for line in scores.values()) / len(scores), 3)
    unknown_cases = [raw for raw in rows if raw["ground_truth"]["expectation_class"] != "exact"]
    unknown_pass = sum(
        1
        for raw in rows
        if raw["ground_truth"]["expectation_class"] != "exact"
        and scores[str(raw["id"])]["unknowns"] == 1.0
        and scores[str(raw["id"])]["needs"] == 1.0
    )
    bridge = RUNNER.run_bridge_sandbox(rows)
    created = bridge["tasks_created"]
    resolved = bridge["tasks_resolved"]
    return {
        "corpus": corpus,
        "fixtures": [
            {
                "id": str(raw["id"]),
                "overall": scores[str(raw["id"])]["overall"],
                "needs": scores[str(raw["id"])]["needs"],
                "unknowns": scores[str(raw["id"])]["unknowns"],
                "items": scores[str(raw["id"])]["items"],
            }
            for raw in rows
        ],
        "field_accuracy": field_accuracy,
        "unknown_pass": unknown_pass,
        "unknown_cases": len(unknown_cases),
        "unknown_rate": round((unknown_pass / len(unknown_cases)) if unknown_cases else 0.0, 3),
        "correction_resolved": resolved,
        "correction_created": created,
        "correction_rate": round((resolved / created) if created else 0.0, 3),
        "audit_writes": bridge["audit_writes"],
    }


def test_selector_lists_every_manifest_corpus_and_defaults_to_sg029() -> None:
    known = RUNNER.available_corpora()
    for corpus in SELECTED_CORPORA:
        assert corpus in known, f"{corpus} must be selectable (its manifest exists)"
    assert RUNNER.DEFAULT_CORPUS == "sg029"
    assert RUNNER.load_manifest()["corpus"] == "sg029", "no-flag default must address sg029"
    assert RUNNER.load_manifest()["base_dir"] == "sg029"
    assert "sg026" not in known, "no manifest -> not selectable (stated, not silent)"


def test_selector_rejects_unknown_corpus_loudly(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        RUNNER.main(["--corpus", "sg999-does-not-exist", "--check-only"])
    assert excinfo.value.code != 0
    captured = capsys.readouterr()
    assert "invalid choice" in captured.err, "an unknown corpus must be refused with usage"
    assert "sg999-does-not-exist" in captured.err


def test_default_invocation_scores_sg029_like_the_frozen_baseline(
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = _baseline_payload("sg029")
    result = RUNNER.main([])
    out = capsys.readouterr().out
    assert result == 0
    assert (
        f"field_accuracy={expected['field_accuracy']:.3f} over {len(expected['fixtures'])} fixtures"
        in out
    ), "the no-flag default must still score sg029"
    assert _score_corpus("sg029")["fixtures"] == expected["fixtures"]


@pytest.mark.parametrize("corpus", SELECTED_CORPORA)
def test_frozen_baseline_reproduces_every_selected_corpus(corpus: str) -> None:
    expected = _baseline_payload(corpus)
    assert _score_corpus(corpus) == expected, f"{corpus}: frozen baseline drift"
