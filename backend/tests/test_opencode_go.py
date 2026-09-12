"""Offline gates for the OpenCode GO adapter (SG-027, G3).

NEVER live: every gate runs against recorded vendor-shaped fixtures or pure
local helpers. The single metered live proof is the G0 spike transcript, not
these tests. PG-EV-04: the outgoing payload SHAPE is asserted pre-send
(endpoint, fields, no key material) without sending.
"""

from __future__ import annotations

import io

from PIL import Image


def _gps_jpeg_bytes() -> bytes:
    """Build a JPEG carrying a fake EXIF/GPS blob (byte-level input)."""
    img = Image.new("RGB", (32, 32), "red")
    buf = io.BytesIO()
    exif = img.getexif()
    exif[0x010F] = "TestMake"  # Make
    gps = exif.get_ifd(0x8825)  # GPSInfo IFD (Pillow 12 API; a bare int pointer cannot serialize)
    gps[1] = "N"
    gps[2] = (51.0, 30.0, 0.0)
    gps[3] = "E"
    gps[4] = (0.0, 7.0, 0.0)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


def test_identity_headers_stable_and_no_pintel_prefix():
    from app.services.providers import opencode_go as go

    h1 = go.build_identity_headers("storagegenie-sg027-run1")
    h2 = go.build_identity_headers("storagegenie-sg027-run1")
    assert h1 == h2, "session headers must be stable for one conversation value"
    names = {k.lower() for k in h1}
    assert "user-agent" in names and "x-opencode-session" in names
    assert "storagegenie-sg027-run1" in h1["x-opencode-session"]
    for v in h1.values():
        assert "pintel" not in v.lower(), "never another project's prefix"
    assert "pintel" not in go.USER_AGENT.lower()


def test_response_format_map_deepseek_kin_json_object():
    from app.services.providers import opencode_go as go

    fmt = go.response_format_for("deepseek-v4-flash-vision-exp")
    assert fmt == {"type": "json_object"}
    other = go.response_format_for("some-other-model")
    assert other["type"] == "json_schema"


def test_guard_empty_200_rejected():
    from app.services.providers import opencode_go as go
    from app.services.providers.router import ProviderError

    for bad in ("", "   ", None):
        try:
            go.guard_content(bad)  # type: ignore[arg-type]
        except ProviderError as exc:
            assert exc.kind == "invalid_json"
        else:
            raise AssertionError(f"empty content not rejected: {bad!r}")


def test_guard_zero_usage_rejected():
    from app.services.providers import opencode_go as go
    from app.services.providers.router import ProviderError

    for usage in ({}, {"prompt_tokens": 0, "completion_tokens": 0}, {"total_tokens": 0}):
        try:
            go.guard_usage(usage)
        except ProviderError as exc:
            assert exc.kind == "invalid_json"
        else:
            raise AssertionError(f"zero usage not rejected: {usage!r}")
    go.guard_usage({"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15})


def test_guard_think_strip_once_then_loud_fail():
    from app.services.providers import opencode_go as go
    from app.services.providers.router import ProviderError

    clean = go.strip_single_think("<think>hmm</think>{\"items\": []}")
    assert clean == '{"items": []}'
    try:
        go.strip_single_think("<think>a</think><think>b</think>{\"items\": []}")
    except ProviderError as exc:
        assert exc.kind == "invalid_json"
    else:
        raise AssertionError("double-<think> must fail loudly, not strip twice")
    assert go.strip_single_think('{"items": []}') == '{"items": []}'


def test_guard_max_tokens_sized_past_truncation():
    from app.services.providers import opencode_go as go

    assert go.DEFAULT_MAX_TOKENS >= 1500, "max_tokens must size past truncation"
    payload = go.build_chat_payload("deepseek-v4-flash-vision-exp", "prompt", "Zm9v")
    assert payload["max_tokens"] >= 1500


def test_redaction_gps_stripped_byte_proven():
    from app.services.providers import opencode_go as go

    raw = _gps_jpeg_bytes()
    assert len(raw) > 0
    stripped = go.redact_image(raw)
    assert stripped[:8] == b"\x89PNG\r\n\x1a\n", "re-encoded stripped by construction"
    reparsed = Image.open(io.BytesIO(stripped))
    assert reparsed.getexif() is not None
    assert dict(reparsed.getexif()) == {}, "no EXIF/GPS survives on the exact bytes sent"


def test_budget_refusal_zero_calls():
    from app.services.providers import opencode_go as go
    from app.services.providers.router import BudgetExceededError

    calls: list[str] = []

    class _Probe(go.OpenCodeGoProvider):
        def _post(self, payload: dict) -> dict:  # type: ignore[override]
            calls.append("called")
            raise AssertionError("must not be called")

    probe = _Probe(session_id="storagegenie-sg027-run1", per_job_cap=0.001)
    try:
        probe.extract_items(b"fake-bytes", "prompt", estimated_cost=1.0)
    except BudgetExceededError:
        pass
    else:
        raise AssertionError("tiny cap must refuse before any call")
    assert calls == [], "zero provider calls on budget refusal"


def test_outgoing_payload_shape_no_key_material():
    from app.services.providers import opencode_go as go

    payload = go.build_chat_payload("deepseek-v4-flash-vision-exp", "food prompt", "Zm9v")
    assert payload["model"] == "deepseek-v4-flash-vision-exp"
    assert payload["stream"] is False
    assert payload["response_format"] == {"type": "json_object"}
    assert isinstance(payload["messages"], list) and payload["messages"]
    blob = repr(payload)
    assert "OPENCODE_API_KEY" not in blob and "sk-" not in blob
    assert payload["messages"][0]["content"][1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert go.CHAT_PATH == "/chat/completions"
    assert go.BASE_URL == "https://opencode.ai/zen/go/v1"


def test_config_readback_new_values():
    import os

    from app import config as cfgmod

    original = cfgmod.settings
    os.environ["SG_PROVIDER_ID"] = "opencode-go"
    os.environ["SG_PER_JOB_CAP"] = "0.5"
    os.environ["SG_MONTHLY_CAP"] = "5.0"
    os.environ["SG_CONSENT"] = "true"
    try:
        # SG-028 carried fix: read the environment through a fresh Settings()
        # instead of importlib.reload(cfgmod). Reloading rebound the shared
        # app.config.settings object, which leaked this test env into the
        # later migration tests (test_search / test_signals).
        s = cfgmod.Settings()
        assert s.sg_provider_id == "opencode-go"
        assert s.sg_per_job_cap == 0.5
        assert s.sg_monthly_cap == 5.0
        assert s.sg_consent is True
        assert hasattr(s, "opencode_api_key")
    finally:
        for k in ("SG_PROVIDER_ID", "SG_PER_JOB_CAP", "SG_MONTHLY_CAP", "SG_CONSENT"):
            os.environ.pop(k, None)
        assert cfgmod.settings is original
