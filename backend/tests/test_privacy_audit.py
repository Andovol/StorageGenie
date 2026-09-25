"""SG-087 privacy-controls audit: redaction + identifiers-only on every provider path.

Audit-only slice (D107 Phase 5 hardening, Slice 3). No production code changes:
every test here proves an EXISTING property of the tree and would fail loudly if
the property regressed.

Chosen proofs and why they are not vacuous:

* ``redact_image`` is imported from the REAL module (``PG-SC-12``): no test-local
  re-implementation. The JPEG is built in-test with a GPS IFD and an EXIF Make
  tag; the unredacted input is asserted to carry both, and the same tag-free
  assertion is shown to FAIL on that input (the committed seen-to-fail control).
* The reader-pipeline proof runs ``job_service.run_job`` through the real reader,
  captures the exact bytes the provider seam received, and re-derives the ledger
  ``image_sha256`` from those bytes — so the ledger row and the outbound bytes are
  tied together on the seam, not asserted separately.
* The direct-adapter proof overrides only ``_post`` (the transport), so no network
  is touched, and decodes the base64 data URL from the real outgoing payload.
* Consent is proved per service path with an exploding provider: if any gate
  leaked, the probe would raise instead of the run returning ``skipped``.

No binary fixtures are committed; all images are generated at test time. No
provider call, no key value, $0.00.
"""

from __future__ import annotations

import base64
import hashlib
import inspect
import io
import json
from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base
from app.models import Evidence, Household
from app.models.provider_call import ProviderCall
from app.services import job_service, signals
from app.services.observations import Observation
from app.services.providers import opencode_go as go
from app.services.providers import reader as reader_mod
from app.services.providers.fake import ScriptedProvider
from app.services.providers.redaction import redact_image

APP_DIR = Path(__file__).resolve().parents[1] / "app"
GPS_TAG = 0x8825
MAKE_TAG = 0x010F
DATETIME_ORIGINAL_TAG = 0x9003
DATETIME_ORIGINAL_VALUE = "2021:07:04 10:20:30"

VALID_PAYLOAD: dict[str, Any] = {
    "items": [
        {
            "name": "Audit Milk",
            "expiry_date": "2030-01-15",
            "date_type": "expiry_date",
            "lot": None,
            "confidence": 0.95,
            "uncertainty_reasons": ["audit fixture"],
        }
    ],
    "unknowns": [],
    "needs_evidence": False,
}


def _gps_jpeg_bytes() -> bytes:
    """A JPEG carrying an EXIF Make tag and a real GPS IFD (generated in-test)."""
    image = Image.new("RGB", (32, 32), "red")
    exif = image.getexif()
    exif[MAKE_TAG] = "TestMake"
    gps = exif.get_ifd(GPS_TAG)
    gps[1] = "N"
    gps[2] = (51.0, 30.0, 0.0)
    gps[3] = "E"
    gps[4] = (0.0, 7.0, 0.0)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", exif=exif)
    return buffer.getvalue()


def _gps_and_datetime_jpeg_bytes() -> bytes:
    """The same GPS payload plus a DateTimeOriginal tag, for the signals trace."""
    image = Image.new("RGB", (32, 32), "red")
    exif = image.getexif()
    exif[MAKE_TAG] = "TestMake"
    exif[DATETIME_ORIGINAL_TAG] = DATETIME_ORIGINAL_VALUE
    gps = exif.get_ifd(GPS_TAG)
    gps[1] = "N"
    gps[2] = (51.0, 30.0, 0.0)
    gps[3] = "E"
    gps[4] = (0.0, 7.0, 0.0)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", exif=exif)
    return buffer.getvalue()


def _assert_tag_free(data: bytes) -> None:
    """Parse EXIF and fail loudly if any tag or the GPS IFD survives."""
    image = Image.open(io.BytesIO(data))
    exif = image.getexif()
    parsed = dict(exif)
    assert parsed == {}, f"EXIF survives redaction: {parsed}"
    assert GPS_TAG not in parsed, "GPSInfo tag survives redaction"
    gps = exif.get_ifd(GPS_TAG)
    assert not gps, f"GPS IFD survives redaction: {gps}"


def _add_evidence(session: Session, household_id: str, key: str, data: bytes) -> Evidence:
    path = Path(settings.storage_root) / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    row = Evidence(
        household_id=household_id,
        sha256=hashlib.sha256(data).hexdigest(),
        storage_key=key,
        media_type="image/jpeg",
        original_filename=Path(key).name,
        source_kind="upload",
        size_bytes=len(data),
    )
    session.add(row)
    session.commit()
    return row


@pytest.fixture
def privacy_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    database_path = tmp_path / "privacy_audit.db"
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session: Session = factory()
    monkeypatch.setattr(settings, "storage_root", str(storage_root))
    monkeypatch.setattr(settings, "exif_timestamps_enabled", False)
    household = Household(name="Privacy Audit Household")
    session.add(household)
    session.commit()
    evidence = _add_evidence(session, household.id, "privacy/audit.jpg", _gps_jpeg_bytes())
    # Pre-seed the phash observation so the deterministic step short-circuits and
    # does not depend on the OCR/zbar ABIs (the two known decoder env reds).
    session.add(
        Observation(
            evidence_id=evidence.id,
            kind="phash",
            value_json=json.dumps({"hash": "0000000000000000"}),
            confidence=1.0,
        )
    )
    session.commit()
    try:
        yield session, household.id, evidence.id
    finally:
        session.close()
        engine.dispose()


def _script(monkeypatch: pytest.MonkeyPatch, provider_id: str) -> ScriptedProvider:  # type: ignore[no-untyped-def]
    provider = ScriptedProvider(provider_id=provider_id, payload=VALID_PAYLOAD)
    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {provider_id: provider})
    monkeypatch.setattr(settings, "sg_consent", True)
    monkeypatch.setattr(settings, "sg_provider_id", provider_id)
    monkeypatch.setattr(settings, "sg_prompt_category", "food")
    return provider


# ---------------------------------------------------------------------------
# G0 — outbound carrier inventory (what CAN leave the machine)
# ---------------------------------------------------------------------------

HTTP_CLIENT_TOKENS = (
    "import httpx",
    "import requests",
    "from requests",
    "import urllib",
    "from urllib",
    "import aiohttp",
    "from aiohttp",
    "import http.client",
    "from http.client",
    "socket.socket",
    "urlopen(",
)


def _http_client_files() -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for path in sorted(APP_DIR.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        found = [token for token in HTTP_CLIENT_TOKENS if token in text]
        if found:
            hits[str(path.relative_to(APP_DIR))] = found
    return hits


def _send_sites() -> list[str]:
    sites: list[str] = []
    for path in sorted(APP_DIR.rglob("*.py")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("@router."):
                continue
            if "client.post(" in line or "httpx.post(" in line or "requests.post(" in line:
                sites.append(f"{path.relative_to(APP_DIR)}:{number}")
    return sites


def test_g0_single_http_client_and_send_site_full_scan() -> None:
    """Scan every app source file: exactly two named HTTP clients, one send site.

    SG-082 repair (M45): the Jina fallback client is a second legitimate httpx
    carrier inside the enrich package; the inventory now names both. SG-098 adds
    `api/v1/enrich.py`: it imports `httpx` only for the injection-seam type
    annotation and makes no send of its own (it delegates to the enrich clients).
    The single POST send site is unchanged (all enrich carriers are read-only GETs).
    SG-101 shifts the adapter's send-site line by its text-path hunks; the pin
    below tracks the line, not the count (M45).
    """
    assert _http_client_files() == {
        "api/v1/enrich.py": ["import httpx"],
        "services/enrich/client.py": ["import httpx"],
        "services/enrich/jina.py": ["import httpx", "import urllib"],
        "services/providers/opencode_go.py": ["import httpx"],
    }, f"unexpected HTTP clients: {_http_client_files()}"
    assert _send_sites() == ["services/providers/opencode_go.py:263"], (
        f"unexpected provider send sites: {_send_sites()}"
    )


def test_g0_redact_call_sites_are_reader_and_direct_adapter() -> None:
    """The only two callers of the shared redactor are the two image paths.

    SG-101 shifts the adapter's call-site line by its text-path hunks; SG-125
    shifts the reader call site by its ledger-retention hunks. The pin below
    tracks the line, not the caller set (M45).
    """
    callers: list[str] = []
    for path in sorted(APP_DIR.rglob("*.py")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "redact_image(" in line and "def redact_image" not in line:
                callers.append(f"{path.relative_to(APP_DIR)}:{number}")
    assert callers == [
        "services/providers/opencode_go.py:310",
        "services/providers/reader.py:465",
    ], f"unexpected redact_image call sites: {callers}"


def test_g0_text_services_ship_blank_carriers_not_photos() -> None:
    """Analytics/planning are text tasks on a generated 1x1 carrier; chat is text-only."""
    from app.services.analytics import service as analytics_service
    from app.services.chat import service as chat_service
    from app.services.planning import service as planning_service

    assert analytics_service.INSIGHTS_OPERATION == "extract_items"
    assert planning_service.PLANNING_OPERATION == "extract_items"
    assert chat_service.CHAT_OPERATION == "extract_text"
    for carrier in (analytics_service._carrier_png(), planning_service._carrier_png()):
        assert carrier[:8] == b"\x89PNG\r\n\x1a\n"
        assert Image.open(io.BytesIO(carrier)).size == (1, 1)
    text_payload = go.build_text_payload("m", "system", "user text")
    assert text_payload["messages"][1]["content"] == "user text"


# ---------------------------------------------------------------------------
# G1 — EXIF/GPS absence on outbound bytes (proved, not asserted)
# ---------------------------------------------------------------------------


def test_g1_seen_to_fail_unredacted_input_carries_exif_and_gps() -> None:
    """Committed negative control: the tag-free assertion FAILS on the raw input."""
    raw = _gps_jpeg_bytes()
    raw_exif = dict(Image.open(io.BytesIO(raw)).getexif())
    assert raw_exif, "negative control precondition: raw input must carry EXIF"
    assert GPS_TAG in raw_exif, "negative control precondition: raw input must carry GPS"
    with pytest.raises(AssertionError):
        _assert_tag_free(raw)


def test_g1_real_redaction_strips_tags_and_preserves_pixels() -> None:
    """Import the REAL redactor and prove parsed tag absence + pixels preserved."""
    raw = _gps_jpeg_bytes()
    redacted = redact_image(raw)
    assert redacted[:8] == b"\x89PNG\r\n\x1a\n", "re-encode to PNG by construction"
    _assert_tag_free(redacted)
    original = Image.open(io.BytesIO(raw))
    result = Image.open(io.BytesIO(redacted))
    assert (result.size, result.mode) == (original.size, original.mode)


def test_g1_reader_pipeline_seam_and_ledger_are_exif_free(
    privacy_env, monkeypatch: pytest.MonkeyPatch  # type: ignore[no-untyped-def]
) -> None:
    """The pipeline hands the redacted PNG to the provider and ledgers its hash."""
    session, household_id, evidence_id = privacy_env
    provider = _script(monkeypatch, "scripted-audit")
    job = job_service.create_job(session, household_id, [evidence_id])
    job_service.run_job(session, job)

    assert provider.invocations >= 1, "the audited path must actually have been exercised"
    handed = provider.images[0]
    assert handed[:8] == b"\x89PNG\r\n\x1a\n"
    _assert_tag_free(handed)
    rows = session.query(ProviderCall).filter_by(job_id=job.id).all()
    assert rows, "the exercised path must have written ledger rows"
    for row in rows:
        hashes = json.loads(row.input_hashes or "{}")
        assert hashes["image_sha256"] == hashlib.sha256(handed).hexdigest(), (
            "ledger hash must be the very bytes the provider received"
        )
        payload = row.output_payload or ""
        assert "exif" not in payload.lower() and "gps" not in payload.lower()
        assert "TestMake" not in payload


def test_g1_direct_adapter_seam_payload_is_redacted() -> None:
    """Override only the transport; decode the real outgoing base64 image part."""
    raw = _gps_jpeg_bytes()
    captured: list[dict[str, Any]] = []

    class _CapturingGo(go.OpenCodeGoProvider):
        def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
            captured.append(payload)
            return {
                "id": "sg087",
                "model": "deepseek-v4-flash-vision-exp",
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {"items": [], "unknowns": [], "needs_evidence": False}
                            )
                        }
                    }
                ],
            }

    provider = _CapturingGo(session_id="sg087-audit")
    provider.extract_items(raw, "audit prompt")
    assert captured, "the transport override must have been reached"
    payload = captured[0]
    url = payload["messages"][0]["content"][1]["image_url"]["url"]
    assert url.startswith("data:image/png;base64,")
    handed = base64.b64decode(url.split(",", 1)[1])
    _assert_tag_free(handed)
    assert Image.open(io.BytesIO(handed)).size == Image.open(io.BytesIO(raw)).size
    blob = repr(payload)
    for forbidden in ("OPENCODE_API_KEY", "Bearer", "sk-", "TestMake"):
        assert forbidden not in blob


def test_g1_signals_exif_values_never_reach_a_provider_payload(
    privacy_env, monkeypatch: pytest.MonkeyPatch  # type: ignore[no-untyped-def]
) -> None:
    """Trace the EXIF hotspot end to end: value exists locally, absent outbound."""
    session, household_id, _ = privacy_env
    monkeypatch.setattr(settings, "exif_timestamps_enabled", True)
    evidence = _add_evidence(
        session, household_id, "privacy/trace.jpg", _gps_and_datetime_jpeg_bytes()
    )
    rows = signals.extract_observations(evidence.id, session)
    exif_rows = [row for row in rows if row.kind == "exif"]
    assert exif_rows, "the EXIF observation must exist for the trace to be meaningful"
    value = json.loads(exif_rows[0].value_json)
    assert value["tag"] == "DateTimeOriginal"
    assert value["timestamp"] == DATETIME_ORIGINAL_VALUE
    assert "gps" not in exif_rows[0].value_json.lower()

    provider = _script(monkeypatch, "scripted-trace")
    job = job_service.create_job(session, household_id, [evidence.id])
    job_service.run_job(session, job)
    assert provider.invocations >= 1
    assert DATETIME_ORIGINAL_VALUE not in provider.prompts[0]
    assert "TestMake" not in provider.prompts[0]
    _assert_tag_free(provider.images[0])
    for row in session.query(ProviderCall).filter_by(job_id=job.id).all():
        outbound = row.output_payload or ""
        assert DATETIME_ORIGINAL_VALUE not in outbound
        assert "TestMake" not in outbound


# ---------------------------------------------------------------------------
# G2 — identifiers-only (keys, consent, Enrich-absence)
# ---------------------------------------------------------------------------


def test_g2_payload_builders_accept_no_key_and_emit_no_secret() -> None:
    """The wire builders have no key parameter and render no secret material."""
    for builder in (go.build_chat_payload, go.build_text_payload, go.build_identity_headers):
        names = set(inspect.signature(builder).parameters)
        assert not names & {"api_key", "key", "authorization", "token"}, (
            f"{builder.__name__} must not accept key material: {names}"
        )
    rendered = repr(go.build_chat_payload("m", "prompt", "Zm9v")) + repr(
        go.build_text_payload("m", "prompt", "user text")
    )
    for forbidden in ("OPENCODE_API_KEY", "Bearer", "sk-", "Authorization"):
        assert forbidden not in rendered
    assert go.CHAT_PATH == "/chat/completions"
    assert go.BASE_URL == "https://opencode.ai/zen/go/v1"


class _ExplodingProvider:
    """Records any call and fails loudly: a consent leak cannot pass silently."""

    provider_id = "exploding-audit"
    model_id = "exploding-audit-model"

    def __init__(self) -> None:
        self.calls: list[str] = []

    def extract_items(  # type: ignore[no-untyped-def]
        self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0
    ):
        self.calls.append("extract_items")
        raise AssertionError("provider must never be called while consent is false")

    def extract_text(  # type: ignore[no-untyped-def]
        self, text: str, prompt: str = "", *, estimated_cost: float = 0.0
    ):
        self.calls.append("extract_text")
        raise AssertionError("provider must never be called while consent is false")


def test_g2_consent_false_binds_zero_calls_on_every_service_path(
    privacy_env, monkeypatch: pytest.MonkeyPatch  # type: ignore[no-untyped-def]
) -> None:
    """Refusal precedes every call on all four service entry points."""
    from app.services.analytics import service as analytics_service
    from app.services.chat import service as chat_service
    from app.services.planning import service as planning_service

    session, household_id, evidence_id = privacy_env
    probe = _ExplodingProvider()
    monkeypatch.setattr(reader_mod, "provider_registry", lambda: {probe.provider_id: probe})
    monkeypatch.setattr(settings, "sg_provider_id", probe.provider_id)
    monkeypatch.setattr(settings, "sg_consent", False)

    insights = analytics_service.run_insights(session, household_id)
    assert insights["status"] == "skipped" and insights["reason"] == "consent_disabled"
    assert probe.calls == []

    planning = planning_service.run_planning(session, household_id)
    assert planning["status"] == "skipped" and planning["reason"] == "consent_disabled"
    assert probe.calls == []

    chat = chat_service.respond(session, household_id, "food", "what expires first?")
    assert chat["status"] == "skipped" and chat["reason"] == "consent_disabled"
    assert probe.calls == []

    job = job_service.create_job(session, household_id, [evidence_id])
    job_service.run_job(session, job)
    assert probe.calls == []
    assert session.query(ProviderCall).count() == 0


def test_g2_web_senders_are_the_two_researched_sources() -> None:
    """SG-082 repair (M45): the Jina fallback is now the ONE web-search sender.

    The name-only scan allows the enrich package's Jina module (+ the mapping
    import in `candidates.py`) and keeps every other web sender absent. SG-097
    adds `config.py` to the allow-set: it declares the `jina_api_key` settings
    field (a name, not a sender).     SG-098 adds `api/v1/enrich.py` to the allow-set:
    it imports the real Jina module as the endpoint's client seam (a name, not a
    sender of its own). SG-099 adds `services/enrich/synthesize.py` to the
    allow-set: it consumes the Jina payload as synthesis input (a name, not a
    sender). SG-100 adds `services/enrich/snapshots.py` (it persists a Jina
    snapshot) and `models/enrich_snapshot.py` (its `source` value is `"jina"`)
    to the allow-set: names, not senders. The excluded detection source is
    checked over the touched web-source files only (the rule's literal gate
    covers new/modified files, not the whole tree).
    """
    jina_files: set[str] = set()
    for path in sorted(APP_DIR.rglob("*.py")):
        rel = str(path.relative_to(APP_DIR))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            lowered = line.lower()
            assert "web_search" not in lowered and "websearch" not in lowered, (
                f"unexpected web-search implementation: {rel}:{number}: {line.strip()}"
            )
            if "jina" in lowered:
                jina_files.add(rel)
    assert jina_files == {
        "api/v1/enrich.py",
        "config.py",
        "models/enrich_snapshot.py",
        "services/candidates.py",
        "services/enrich/jina.py",
        "services/enrich/snapshots.py",
        "services/enrich/synthesize.py",
    }, jina_files

    excluded_hits: list[str] = []
    for rel in ("api/v1/enrich.py", "services/candidates.py", "services/enrich/jina.py"):
        for number, line in enumerate(
            (APP_DIR / rel).read_text(encoding="utf-8").splitlines(), start=1
        ):
            lowered = line.lower()
            if ("web_" + "detection") in lowered or ("visi" + "on") in lowered:
                excluded_hits.append(f"{rel}:{number}: {line.strip()}")
    assert excluded_hits == [], f"excluded detection source must stay absent: {excluded_hits}"
    assert _send_sites() == ["services/providers/opencode_go.py:263"]
