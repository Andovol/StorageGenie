"""SG-093: vendored Google Product Taxonomy + pure offline resolver + bucket map.

Every pin here drives the REAL resolver over the REAL vendored file
(``backend/app/data/google_taxonomy/2021-09-21.txt``); nothing is re-implemented
in the test. The module performs no network, no clock and no I/O beyond that one
file, which the source-level pin below asserts.
"""

from __future__ import annotations

import io
import json
import re
from copy import deepcopy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Assertion, Evidence, Household
from app.services import candidates, google_taxonomy, job_service
from app.services.candidates import (
    ALLOWED_CANDIDATE_FIELDS,
    GATED_FIELDS,
    Candidate,
)
from app.services.google_taxonomy import (
    ACCEPT_MARGIN,
    ACCEPT_SCORE,
    TAXONOMY_VERSION,
    TOP_K,
    bucket_for,
    resolve_google_type,
)
from app.services.observations import Observation
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
    """v4 = v3 loader output + spec block + front-matter bump; v3 still on disk."""
    block = _spec_block()
    # SG-095 flipped the live map to v4, so the v3 baseline is loaded by
    # pointing the real loader at the frozen v3 file (never a re-typed copy).
    monkeypatch.setitem(reader.PROMPT_FILES, category, f"extract-{category}-v3.md")
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


# --------------------------------------------------------------------------- #
# SG-095 T3 — reader flip, gated triple, unclear alternatives (offline, $0)
# --------------------------------------------------------------------------- #
COSMETICS_PATH = "Health & Beauty > Personal Care > Cosmetics"


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (24, 24), "white").save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def sg095_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "sg095.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    monkeypatch.setattr(settings, "sg_consent", False)
    monkeypatch.setattr(settings, "sg_provider_id", "fake")
    monkeypatch.setattr(settings, "sg_per_job_cap", None)
    monkeypatch.setattr(settings, "sg_monthly_cap", None)
    monkeypatch.setattr(settings, "sg_confidence_threshold", 0.9)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")

    from app.services.providers import opencode_go

    network_attempts: list[str] = []

    def _forbidden(self: object, payload: dict[str, object]) -> dict[str, object]:
        network_attempts.append("post")
        raise AssertionError("network must never be attempted in the offline SG-095 tests")

    monkeypatch.setattr(opencode_go.OpenCodeGoProvider, "_post", _forbidden)

    household = Household(name="SG-095 Household")
    session.add(household)
    session.commit()
    png = _png_bytes()
    evidence = Evidence(
        household_id=household.id,
        sha256="f" * 64,
        storage_key="sg095/source.png",
        media_type="image/png",
        original_filename="source.png",
        source_kind="upload",
        size_bytes=len(png),
    )
    session.add(evidence)
    session.commit()
    path = storage_root / evidence.storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)
    session.add(
        Observation(
            evidence_id=evidence.id,
            kind="phash",
            value_json=json.dumps({"hash": "0" * 16}),
            confidence=1.0,
        )
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
        yield session, household.id, evidence.id, network_attempts
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        engine.dispose()


def _enable(  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    *,
    provider_id: str = "scripted",
    category: str = "food",
    threshold: float = 0.9,
):
    from app.services.providers.fake import ScriptedProvider

    provider = ScriptedProvider(provider_id=provider_id, payload=payload)
    monkeypatch.setattr(reader, "provider_registry", lambda: {provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", category)
    monkeypatch.setattr(settings, "sg_confidence_threshold", threshold)
    return provider


def _item(**overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "name": "Milk",
        "expiry_date": "2031-03-15",
        "date_type": "best_before",
        "confidence": 1.0,
        "uncertainty_reasons": [],
    }
    item.update(overrides)
    return item


def _payload(items: list[dict[str, object]], **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {"items": items, "unknowns": [], "needs_evidence": False}
    payload.update(overrides)
    return payload


def _run(session: Session, household_id: str, evidence_id: str):  # type: ignore[no-untyped-def]
    job = job_service.create_job(session, household_id, [evidence_id])
    return job_service.run_job(session, job)


def _candidate(session: Session, job_id: str) -> Candidate:
    return session.query(Candidate).filter_by(job_id=job_id).one()


def _proposal(session: Session, job_id: str) -> dict[str, object]:
    return json.loads(_candidate(session, job_id).proposed_fields_json)


def test_live_reader_serves_v4_for_all_categories_at_runtime() -> None:
    """SG-095 G1: the live reader is on v4 for all three categories (PG-SC-12)."""
    assert reader.PROMPT_FILES == {
        "food": "extract-food-v4.md",
        "medicine": "extract-medicine-v4.md",
        "cosmetics": "extract-cosmetics-v4.md",
    }
    for category in V4_CATEGORIES:
        text, version = reader.load_prompt(category)
        assert version == f"extract-{category}-v4"
        assert V4_FIELD in text, category


def test_resolved_item_carries_triple_gated_through_route_and_commit(
    sg095_env, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, network = sg095_env
    _enable(monkeypatch, _payload([_item(**{V4_FIELD: BEER_PATH})]), threshold=0.0)
    job = _run(session, household_id, evidence_id)
    assert job.state == "AWAITING_REVIEW"
    candidate = _candidate(session, job.id)
    proposal = _proposal(session, job.id)

    for field_name in candidates.GOOGLE_TYPE_FIELDS:
        assert field_name in GATED_FIELDS, field_name
        assert field_name in ALLOWED_CANDIDATE_FIELDS, field_name
        envelope = proposal["fields"][field_name]  # type: ignore[index]
        assert envelope["source_type"] == "extraction"
    assert proposal["fields"]["google_type_id"]["value"] == "414"  # type: ignore[index]
    assert proposal["fields"]["google_type_path"]["value"] == BEER_PATH  # type: ignore[index]
    assert proposal["fields"]["taxonomy_version"]["value"] == TAXONOMY_VERSION  # type: ignore[index]

    # Per-item resolution: the primary item's own resolution is on the ai_item too.
    assert proposal["ai_items"][0]["google_type_resolution"]["google_type_id"] == "414"  # type: ignore[index]

    with TestClient(app) as client:
        body = client.get(
            f"/v1/candidates/{candidate.id}", params={"household_id": household_id}
        )
        assert body.status_code == 200, body.text
        fields = body.json()["fields"]
        assert fields["google_type_id"]["value"] == "414"
        assert fields["google_type_path"]["value"] == BEER_PATH
        assert fields["taxonomy_version"]["value"] == TAXONOMY_VERSION
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200, accepted.text
    asset_id = str(accepted.json()["asset_id"])

    rows = {
        row.field_path: row
        for row in session.query(Assertion).filter_by(asset_id=asset_id).all()
    }
    for field_name in candidates.GOOGLE_TYPE_FIELDS:
        assert rows[field_name].review_state == "proposed", "never auto-accepted"
    # Contrast: a non-gated deterministic field DOES accept at the same 0.0 threshold.
    assert rows["status"].review_state == "accepted"
    assert rows["status"].source_type == "deterministic"
    assert network == []


def test_unclear_item_surfaces_alternatives_and_maps_nothing(
    sg095_env, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, _network = sg095_env
    _enable(monkeypatch, _payload([_item(**{V4_FIELD: "Alcoholic"})]), threshold=0.0)
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)
    proposal = _proposal(session, job.id)

    resolution = proposal["google_type_resolution"]
    assert isinstance(resolution, dict)
    assert resolution["status"] == "unclear"
    assert resolution["google_type_id"] is None
    assert resolution["google_type_path"] is None
    assert resolution["taxonomy_version"] == TAXONOMY_VERSION
    alternatives = resolution["alternatives"]
    assert alternatives, "top-k alternatives must be surfaced to the reviewer"
    assert all(isinstance(pair, list) and len(pair) == 2 for pair in alternatives)

    # Nothing auto-maps: no triple field at all on an unclear item.
    for field_name in candidates.GOOGLE_TYPE_FIELDS:
        assert field_name not in proposal["fields"]

    with TestClient(app) as client:
        accepted = client.post(
            f"/v1/candidates/{candidate.id}/decision",
            params={"household_id": household_id},
            json={"action": "accept"},
        )
    assert accepted.status_code == 200, accepted.text
    asset_id = str(accepted.json()["asset_id"])
    google_rows = (
        session.query(Assertion)
        .filter(
            Assertion.asset_id == asset_id,
            Assertion.field_path.in_(candidates.GOOGLE_TYPE_FIELDS),
        )
        .all()
    )
    assert google_rows == []


def test_multi_item_split_promotes_each_items_own_triple(
    sg095_env, monkeypatch: pytest.MonkeyPatch
) -> None:  # type: ignore[no-untyped-def]
    session, household_id, evidence_id, _network = sg095_env
    payload = _payload(
        [
            _item(name="Milk", **{V4_FIELD: BEER_PATH}),
            _item(name="Cream", **{V4_FIELD: COSMETICS_PATH}),
        ]
    )
    _enable(monkeypatch, payload)
    job = _run(session, household_id, evidence_id)
    candidate = _candidate(session, job.id)
    proposal = _proposal(session, job.id)
    assert proposal["ai_items"][0]["google_type_resolution"]["google_type_id"] == "414"  # type: ignore[index]
    assert proposal["ai_items"][1]["google_type_resolution"]["google_type_id"] == "473"  # type: ignore[index]

    with TestClient(app) as client:
        response = client.post(
            f"/v1/candidates/{candidate.id}/split",
            params={"household_id": household_id},
            json={"item_indexes": [0, 1]},
        )
    assert response.status_code == 200, response.text
    children = response.json()["children"]
    by_index = {child["split_item_index"]: child for child in children}
    assert by_index[0]["fields"]["google_type_id"]["value"] == "414"
    assert by_index[1]["fields"]["google_type_id"]["value"] == "473"
    assert by_index[0]["fields"]["google_type_path"]["value"] == BEER_PATH
    assert by_index[1]["fields"]["google_type_path"]["value"] == COSMETICS_PATH
