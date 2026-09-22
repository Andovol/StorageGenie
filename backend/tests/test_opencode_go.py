"""Offline gates for the OpenCode GO adapter (SG-027, G3).

NEVER live: every gate runs against recorded vendor-shaped fixtures or pure
local helpers. The single metered live proof is the G0 spike transcript, not
these tests. PG-EV-04: the outgoing payload SHAPE is asserted pre-send
(endpoint, fields, no key material) without sending.
"""

from __future__ import annotations

import io

import pytest
from PIL import Image


def _png_bytes() -> bytes:
    """A tiny real PNG: the adapter redacts (decodes) the bytes before sending."""
    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "white").save(buf, format="PNG")
    return buf.getvalue()


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


def test_guard_stray_think_raises_and_single_block_strips_charcode_built():
    """SG-064 G0 pin (mangler-immune): the unbalanced-guard restores its angle token.

    The payload is CONSTRUCTED from character codes — never a typed escape — so
    this test cannot be silently disabled by the same editing channel that
    corrupted `strip_single_think` in SG-062. A stray unclosed think tag must hit
    the `unbalanced` guard and raise; a balanced single block must strip once.
    """
    from app.services.providers import opencode_go as go
    from app.services.providers.router import ProviderError

    lt = chr(60)  # less-than
    gt = chr(62)  # greater-than
    open_tag = lt + "think" + gt
    close_tag = lt + "/think" + gt

    balanced = open_tag + "hmm" + close_tag + '{"items": []}'
    assert go.strip_single_think(balanced) == '{"items": []}'

    stray = "prefix text " + open_tag + " stray unclosed content"
    with pytest.raises(ProviderError) as caught:
        go.strip_single_think(stray)
    assert "unbalanced" in str(caught.value)

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


def test_raise_legs_carry_a_received_bodys_usage_and_cost():
    """SG-062 G2: the post-usage raise leg attaches the body's usage/cost/latency.

    `provider 200 with no choices` is the ONE leg in `extract_items` that raises
    AFTER `guard_usage` parsed a real usage — the leg the SG-039 `glare` run hit
    (both attempts recorded `$0.000000`). The exception must carry the FIELDS THE
    READER READS — `exc.usage`, `exc.cost`, `exc.latency_ms` (PG-SC-12), so
    `reader._write_error_ledger` records them with no reader hunk.
    """
    from app.services.providers import opencode_go as go
    from app.services.providers.router import ProviderError

    usage = {"prompt_tokens": 754, "completion_tokens": 341, "total_tokens": 1095}
    expected_cost = go.compute_cost(usage)

    class _BodyProvider(go.OpenCodeGoProvider):
        def __init__(self, body: object) -> None:
            super().__init__(session_id="sg062-raise-legs")
            self._body = body

        def _post(self, payload: dict) -> object:  # type: ignore[override]
            return self._body

    for name, body in {
        "no_choices": {"id": "x", "model": "m", "usage": usage, "choices": []},
        "non_list_choices": {"id": "x", "model": "m", "usage": usage, "choices": "nope"},
    }.items():
        provider = _BodyProvider(body)
        with pytest.raises(ProviderError) as caught:
            provider.extract_items(_png_bytes(), "prompt")
        exc = caught.value
        assert exc.kind == "invalid_json", name
        assert exc.usage == usage, f"{name}: body usage must cross the boundary"
        assert exc.cost == expected_cost, f"{name}: cost is the file's own compute_cost"
        assert exc.latency_ms is not None and exc.latency_ms >= 0.0, name


def test_content_guard_leg_stays_usage_free():
    """SG-062 not-a-defect: the empty-200 leg raises before usage crosses.

    `guard_content` is a content-shape guard reached after `guard_usage`, but it
    is a module-level helper taking only the content; the body's usage is not
    threaded to it and the reader records honest absent fields. This pin fixes
    that current behavior so a later change is deliberate.
    """
    from app.services.providers import opencode_go as go
    from app.services.providers.router import ProviderError

    usage = {"prompt_tokens": 754, "completion_tokens": 341, "total_tokens": 1095}

    class _BodyProvider(go.OpenCodeGoProvider):
        def __init__(self, body: object) -> None:
            super().__init__(session_id="sg062-content-legs")
            self._body = body

        def _post(self, payload: dict) -> object:  # type: ignore[override]
            return self._body

    provider = _BodyProvider(
        {
            "id": "x",
            "model": "m",
            "usage": usage,
            "choices": [{"message": {"content": "   "}}],
        }
    )
    with pytest.raises(ProviderError) as caught:
        provider.extract_items(_png_bytes(), "prompt")
    exc = caught.value
    assert exc.kind == "invalid_json"
    assert getattr(exc, "usage", None) is None
    assert getattr(exc, "cost", None) is None
    assert getattr(exc, "latency_ms", None) is None


def test_pre_body_legs_do_not_invent_usage_or_cost():
    """SG-062: a leg that raised before any completed 200 body stays honestly empty."""
    from app.services.providers import opencode_go as go
    from app.services.providers.router import ProviderError

    class _NonJsonProvider(go.OpenCodeGoProvider):
        def _post(self, payload: dict) -> dict:  # type: ignore[override]
            raise ProviderError("invalid_json", "provider 200 with a non-JSON body")

    provider = _NonJsonProvider(session_id="sg062-pre-body")
    with pytest.raises(ProviderError) as caught:
        provider.extract_items(_png_bytes(), "prompt")
    exc = caught.value
    assert exc.kind == "invalid_json"
    assert getattr(exc, "usage", None) is None
    assert getattr(exc, "cost", None) is None

    bare = go.OpenCodeGoProvider(session_id="sg062-pre-body", api_key="")
    import os

    original = os.environ.pop("OPENCODE_API_KEY", None)
    try:
        with pytest.raises(ProviderError) as caught:
            bare.extract_items(_png_bytes(), "prompt")
    finally:
        if original is not None:
            os.environ["OPENCODE_API_KEY"] = original
    assert caught.value.kind == "missing_key"
    assert getattr(caught.value, "usage", None) is None
    assert getattr(caught.value, "cost", None) is None


def test_transport_and_http_status_legs_carry_no_usage():
    """SG-062: transport and non-200 legs have no body of their own to account for."""
    import httpx

    from app.services.providers import opencode_go as go
    from app.services.providers.router import ProviderError

    class _TransportProvider(go.OpenCodeGoProvider):
        def _post(self, payload: dict) -> dict:  # type: ignore[override]
            raise ProviderError("transport", "provider transport failure: ConnectError")

    with pytest.raises(ProviderError) as caught:
        _TransportProvider(session_id="sg062-transport").extract_items(_png_bytes(), "p")
    assert getattr(caught.value, "usage", None) is None

    def _handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="upstream exploded")

    class _PatchedClient(httpx.Client):
        def __init__(self, **kwargs: object) -> None:
            kwargs["transport"] = httpx.MockTransport(_handler)
            super().__init__(**kwargs)  # type: ignore[arg-type]

    import app.services.providers.opencode_go as go_mod

    real_client = httpx.Client
    go_mod.httpx.Client = _PatchedClient  # type: ignore[assignment,misc]
    try:
        with pytest.raises(ProviderError) as caught:
            go.OpenCodeGoProvider(session_id="sg062-http", api_key="k").extract_items(
                _png_bytes(), "p"
            )
    finally:
        go_mod.httpx.Client = real_client  # type: ignore[assignment,misc]
    assert caught.value.kind == "http_status"
    assert getattr(caught.value, "usage", None) is None


def test_extract_text_raise_legs_carry_a_received_bodys_usage_and_cost():
    """SG-062: the text op shares the shape; its post-body legs attach usage too."""
    from app.services.providers import opencode_go as go
    from app.services.providers.router import ProviderError

    usage = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    expected_cost = go.compute_cost(usage)

    class _BodyProvider(go.OpenCodeGoProvider):
        def __init__(self, body: dict) -> None:
            super().__init__(session_id="sg062-text-legs")
            self._body = body

        def _post(self, payload: dict) -> dict:  # type: ignore[override]
            return self._body

    no_choices = _BodyProvider({"id": "x", "model": "m", "usage": usage, "choices": []})
    with pytest.raises(ProviderError) as caught:
        no_choices.extract_text("USER", "SYSTEM")
    assert caught.value.usage == usage
    assert caught.value.cost == expected_cost
    assert caught.value.latency_ms is not None


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
