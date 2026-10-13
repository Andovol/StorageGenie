"""SG-180 G3 probe — real provider client/builders, privacy, accounting, Enrich.

Uses the REAL OpenCodeGoProvider / router / reader / schemas / enrich clients.
HTTP is intercepted ONLY via httpx.MockTransport (scripted transport, no
network, fake keys). Reader flows run on a disposable SQLite DB + storage.

Run:
  cd /tmp/opencode && PYTHONPATH=<repo>/backend <repo>/backend/venv/bin/python \
      <repo>/docs/worklogs/SG-180_probe_g3.py
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

TEMP_ROOT = Path(tempfile.mkdtemp(prefix="sg180-g3-"))
TEMP_DB = TEMP_ROOT / "storagegenie.db"
TEMP_STORAGE = TEMP_ROOT / "storage"
TEMP_STORAGE.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEMP_DB}"
os.environ["STORAGE_ROOT"] = str(TEMP_STORAGE)
os.environ.pop("OPENCODE_API_KEY", None)
os.environ.pop("JINA_API_KEY", None)

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Household, Job, ProviderCall  # noqa: E402
from app.services import candidates, job_service  # noqa: E402
from app.services.enrich.client import build_off_request, fetch_off_search  # noqa: E402
from app.services.enrich.jina import (  # noqa: E402
    authorize,
    build_jina_request,
    estimate_jina_search_cost,
    fetch_jina_search,
    resolve_api_key,
)
from app.services.enrich.snapshots import (  # noqa: E402
    get_snapshot,
    record_jina_snapshot,
    record_jina_search_call,
    record_off_snapshot,
)
from app.services.enrich.synthesize import build_synthesis_input  # noqa: E402
from app.services.providers import reader  # noqa: E402
from app.services.providers.fake import ScriptedProvider  # noqa: E402
from app.services.providers.opencode_go import (  # noqa: E402
    OpenCodeGoProvider,
    build_chat_payload,
    build_identity_headers,
    build_text_payload,
    compute_cost,
    response_format_for,
)
from app.services.providers.router import (  # noqa: E402
    BudgetExceededError,
    ProviderError,
    ProviderNotFoundError,
    ProviderRouter,
    RouterConfig,
)
from app.services.providers.schemas import (  # noqa: E402
    ExtractionFailedError,
    extract_with_single_repair,
)

RESULTS: list[dict[str, object]] = []
FAKE_KEY = "sg180-audit-fake-key-not-a-real-secret"

VALID_ITEMS = {
    "items": [
        {
            "name": "Audit Beans",
            "expiry_date": "2027-01-31",
            "confidence": 0.98,
            "uncertainty_reasons": ["printed date small"],
            "brand": "AuditBrand",
        }
    ],
    "unknowns": [],
    "needs_evidence": False,
}


def record(name: str, level: str, **detail: object) -> None:
    RESULTS.append({"check": name, "result": level, **detail})


def expect(name: str, condition: bool, **detail: object) -> None:
    record(name, "PASS" if condition else "FAIL", **detail)


def observe(name: str, **detail: object) -> None:
    record(name, "OBSERVE", **detail)


def jpeg_bytes(color="red", with_gps=False) -> bytes:
    image = Image.new("RGB", (64, 48), color)
    out = io.BytesIO()
    if with_gps:
        exif = Image.Exif()
        exif[0x0112] = 6
        exif[0x8825] = {1: "N", 2: (40.0, 1.0, 0.0), 3: "E", 4: (26.0, 2.0, 0.0)}
        image.save(out, format="JPEG", exif=exif.tobytes())
    else:
        image.save(out, format="JPEG")
    return out.getvalue()


CAPTURED: list[dict[str, object]] = []


def _handler(request: httpx.Request) -> httpx.Response:
    CAPTURED.append(
        {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "content": request.content,
        }
    )
    script = SCRIPTED_RESPONSES.pop(0)
    if callable(script):
        return script(request)
    status, body = script
    return httpx.Response(status, json=body, request=request)


SCRIPTED_RESPONSES: list[object] = []


@contextmanager
def scripted_http(responses: list[object]):  # type: ignore[no-untyped-def]
    global SCRIPTED_RESPONSES
    SCRIPTED_RESPONSES = list(responses)
    real_client = httpx.Client

    def factory(*args, **kwargs):  # type: ignore[no-untyped-def]
        kwargs.pop("timeout", None)
        return real_client(transport=httpx.MockTransport(_handler), timeout=5.0)

    httpx.Client = factory  # type: ignore[assignment]
    CAPTURED.clear()
    try:
        yield CAPTURED
    finally:
        httpx.Client = real_client  # type: ignore[assignment]


def ok_body(content: str = json.dumps(VALID_ITEMS)) -> tuple[int, dict]:
    return (
        200,
        {
            "id": "req-abc",
            "model": "deepseek-v4-flash-vision-exp",
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
        },
    )


def make_provider(**kwargs) -> OpenCodeGoProvider:  # type: ignore[no-untyped-def]
    return OpenCodeGoProvider(session_id="sg180-session", api_key=FAKE_KEY, model_id="deepseek-v4-flash-vision-exp", **kwargs)


# ---------------------------------------------------------------- Part A
def part_a() -> None:
    IMG = jpeg_bytes(color="blue")
    provider = make_provider()
    gps = jpeg_bytes(with_gps=True)
    orig_sha = hashlib.sha256(gps).hexdigest()
    prompt = "AUDIT-PROMPT: return JSON"
    with scripted_http([ok_body()]) as captured:
        result = provider.extract_items(gps, prompt)
        req = captured[0]
    body = json.loads(bytes(req["content"]).decode("utf-8"))
    headers = {k.lower(): v for k, v in req["headers"].items()}
    expect(
        "wire_request_line",
        req["method"] == "POST" and req["url"] == "https://opencode.ai/zen/go/v1/chat/completions",
        method=req["method"],
        url=req["url"],
    )
    expect(
        "wire_identity_headers",
        headers.get("content-type") == "application/json"
        and headers.get("user-agent") == "StorageGenie/0.1 (opencode-go vision adapter)"
        and headers.get("x-opencode-session") == "sg180-session"
        and headers.get("authorization") == f"Bearer {FAKE_KEY}",
        headers={k: v for k, v in headers.items() if k in ("content-type", "user-agent", "x-opencode-session", "authorization")},
    )
    expect(
        "wire_payload_envelope",
        body["model"] == "deepseek-v4-flash-vision-exp"
        and body["stream"] is False
        and body["max_tokens"] == 2000
        and body["response_format"] == {"type": "json_object"}
        and [part["type"] for part in body["messages"][0]["content"]] == ["text", "image_url"]
        and body["messages"][0]["content"][0]["text"] == prompt,
        envelope={k: body[k] for k in ("model", "stream", "max_tokens", "response_format")},
        content_types=[p["type"] for p in body["messages"][0]["content"]],
    )
    data_url = body["messages"][0]["content"][1]["image_url"]["url"]
    sent = __import__("base64").b64decode(data_url.split(",", 1)[1])
    sent_img = Image.open(io.BytesIO(sent))
    sent_exif = dict(sent_img.getexif())
    expect(
        "wire_image_is_redacted_png_upright",
        data_url.startswith("data:image/png;base64,")
        and sent.startswith(b"\x89PNG")
        and sent_exif == {}
        and sent_img.size == (48, 64)
        and hashlib.sha256(gps).hexdigest() == orig_sha,
        sent_size=sent_img.size,
        sent_exif=sent_exif,
        original_sha_unchanged=hashlib.sha256(gps).hexdigest() == orig_sha,
    )
    expect(
        "wire_result_and_cost",
        result.normalized_output["items"][0]["name"] == "Audit Beans"
        and result.model_id == "deepseek-v4-flash-vision-exp"
        and result.usage["total_tokens"] == 150
        and abs(result.cost - compute_cost(result.usage)) < 1e-12
        and result.request_id == "req-abc"
        and result.latency_ms >= 0,
        cost=result.cost,
        expected=compute_cost({"prompt_tokens": 100, "completion_tokens": 50}),
    )
    observe(
        "text_payload_shape",
        payload=build_text_payload("m", "SYS", "USER"),
        note="text turn: system+user plain text, max_tokens 8000, no response_format",
    )

    # validation paths
    cases = [
        ("zero_usage", [(200, {"usage": {}, "choices": [{"message": {"content": "{}"}}]})], "invalid_json", True),
        ("empty_content", [ok_body("")], "invalid_json", False),
        ("no_choices", [(200, {"usage": {"total_tokens": 3}, "choices": []})], "invalid_json", True),
        ("non_json_200", [(200, None)], "invalid_json", False),
        ("non_object_200", [(200, [1, 2, 3])], "invalid_json", False),
        ("http_500", [(500, {"error": "server exploded: audit-body"})], "http_status", False),
    ]
    for name, responses, kind, attach in cases:
        parsed = []
        for r in responses:
            if r[1] is None:
                parsed.append(lambda request: httpx.Response(200, content=b"not-json", headers={"content-type": "application/json"}, request=request))
            else:
                parsed.append(r)
        p = make_provider()
        with scripted_http(parsed):
            try:
                p.extract_items(IMG, "p")
                got = None
            except ProviderError as exc:
                got = exc
            except Exception as exc:  # noqa: BLE001
                got = exc
        ok = isinstance(got, ProviderError) and got.kind == kind
        detail = {"kind": getattr(got, "kind", type(got).__name__), "message": str(got)[:120], "attached_usage": getattr(got, "usage", "MISSING") if got else None}
        expect(f"validation_{name}", ok, **detail)
        if attach and isinstance(got, ProviderError):
            expect(f"validation_{name}_accounting_attached", getattr(got, "cost", None) is not None, cost=getattr(got, "cost", None))

    # vision empty-200 vs text empty-200 accounting attachment (SG-101 scope)
    p = make_provider()
    with scripted_http([ok_body("")]):
        try:
            p.extract_items(IMG, "p")
            vision_exc = None
        except ProviderError as exc:
            vision_exc = exc
    p = make_provider()
    with scripted_http([ok_body("")]):
        try:
            p.extract_text("t", "p")
            text_exc = None
        except ProviderError as exc:
            text_exc = exc
    observe(
        "empty_200_accounting_vision_vs_text",
        vision_kind=getattr(vision_exc, "kind", None),
        vision_cost_attached=getattr(vision_exc, "cost", None),
        text_kind=getattr(text_exc, "kind", None),
        text_cost_attached=getattr(text_exc, "cost", None),
        note="extract_text attaches body accounting (SG-101); extract_items does not",
    )

    # transport failure
    def boom(request):  # type: ignore[no-untyped-def]
        raise httpx.ConnectError("audit connect failure", request=request)

    p = make_provider()
    with scripted_http([boom]):
        try:
            p.extract_items(IMG, "p")
            got = None
        except ProviderError as exc:
            got = exc
    expect("validation_transport", got is not None and got.kind == "transport", kind=getattr(got, "kind", None), message=str(got)[:80])

    # think handling
    p = make_provider()
    with scripted_http([ok_body("<think>hidden reasoning</think>\n" + json.dumps(VALID_ITEMS))]):
        res = p.extract_items(IMG, "p")
    expect("think_single_stripped", res.normalized_output["items"][0]["name"] == "Audit Beans")
    p = make_provider()
    with scripted_http([ok_body("<think>a</think>{}<think>b</think>")]):
        try:
            p.extract_items(IMG, "p")
            got = None
        except ProviderError as exc:
            got = exc
    expect("think_double_rejected", got is not None and got.kind == "invalid_json", message=str(got)[:80])

    # key-reading path by name (no value printed)
    no_key = OpenCodeGoProvider(session_id="s", api_key=None)
    try:
        no_key._resolve_api_key()
        missing = None
    except ProviderError as exc:
        missing = exc
    expect(
        "open_code_key_path_missing_key",
        missing is not None and missing.kind == "missing_key" and "OPENCODE_API_KEY" in str(missing),
        kind=getattr(missing, "kind", None),
    )
    expect("jina_key_seam_absent_returns_none", resolve_api_key(None) is None)
    expect(
        "identity_builder_never_carries_key",
        "authorization" not in {k.lower() for k in build_identity_headers("s")} and set(build_identity_headers("s")) == {"Content-Type", "User-Agent", "x-opencode-session"},
        headers=build_identity_headers("s"),
    )
    expect(
        "response_format_by_model",
        response_format_for("deepseek-v4-flash-vision-exp") == {"type": "json_object"}
        and response_format_for("muse-spark") == {"type": "json_schema"},
    )


# ---------------------------------------------------------------- Part B
def part_b(db) -> None:  # type: ignore[no-untyped-def]
    supplies = {"n": 0}

    def flaky() -> object:
        supplies["n"] += 1
        return {"prose": "no"} if supplies["n"] == 1 else dict(VALID_ITEMS)

    out = extract_with_single_repair(flaky)
    expect("repair_once_then_valid", supplies["n"] == 2 and out.items[0].name == "Audit Beans", supplies=supplies["n"])

    always = {"n": 0}

    def always_bad() -> object:
        always["n"] += 1
        return {"prose": "no"}

    try:
        extract_with_single_repair(always_bad)
        failed = None
    except ExtractionFailedError as exc:
        failed = exc
    expect("repair_twice_fails", failed is not None and always["n"] == 2, supplies=always["n"], error=str(failed)[:100])

    # reader._extract_one: repair prompt and ledger rows
    house = Household(name="SG180 G3 House")
    db.add(house)
    db.commit()
    job = job_service.create_job(db, house.id, [])
    db.commit()
    provider = ScriptedProvider(provider_id="scripted", payload=dict(VALID_ITEMS), fail_times=1)
    registry = {"scripted": provider}
    cfg = RouterConfig(
        provider_id="scripted", fallback_id=None, json_strict=True, cost_budget=float("inf"), retryable_errors=reader.RETRYABLE_ERRORS
    )
    router = ProviderRouter(cfg, registry)
    prompt_text, version = reader.load_prompt("food")
    output, call_ids = reader._extract_one(db, job, router, b"pngbytes", prompt_text, "scripted", provider.model_id, version, 0.0)
    rows = db.query(ProviderCall).filter_by(job_id=job.id).order_by(ProviderCall.created_at).all()
    expect(
        "reader_repair_prompt_and_ledger",
        provider.invocations == 2
        and provider.prompts[0] == prompt_text
        and provider.prompts[1].startswith(prompt_text)
        and "## Repair" in provider.prompts[1]
        and len(rows) == 2
        and rows[0].error_state is not None
        and rows[1].error_state is None
        and rows[1].prompt_template_version == version,
        invocations=provider.invocations,
        repair_appended=provider.prompts[1].startswith(prompt_text) and "## Repair" in provider.prompts[1],
        ledger=[{"error": r.error_state, "version": r.prompt_template_version} for r in rows],
    )
    db.rollback()

    # always-failing provider: 2 committed error rows for THIS step, no success row
    error_rows_before = db.query(ProviderCall).filter_by(job_id=job.id).filter(ProviderCall.error_state.is_not(None)).count()
    provider2 = ScriptedProvider(provider_id="scripted", payload=dict(VALID_ITEMS), fail_times=99)
    router2 = ProviderRouter(cfg, {"scripted": provider2})
    try:
        reader._extract_one(db, job, router2, b"pngbytes", prompt_text, "scripted", provider2.model_id, version, 0.0)
        failed2 = None
    except ExtractionFailedError as exc:
        failed2 = exc
    db.rollback()
    error_rows_after = db.query(ProviderCall).filter_by(job_id=job.id).filter(ProviderCall.error_state.is_not(None)).count()
    expect(
        "reader_failure_twice_two_error_rows",
        failed2 is not None and provider2.invocations == 2 and error_rows_after - error_rows_before == 2,
        invocations=provider2.invocations,
        error_rows_delta=error_rows_after - error_rows_before,
    )
    # non-retryable: one supply only
    provider3 = ScriptedProvider(provider_id="scripted", payload=dict(VALID_ITEMS))
    original = provider3.extract_items

    def outage(image, prompt, *, estimated_cost=0.0):  # type: ignore[no-untyped-def]
        provider3.invocations += 1
        raise ProviderError("outage", "audit outage")

    provider3.extract_items = outage  # type: ignore[method-assign]
    try:
        reader._extract_one(db, job, ProviderRouter(cfg, {"scripted": provider3}), b"b", prompt_text, "scripted", "m", version, 0.0)
        failed3 = None
    except ExtractionFailedError as exc:
        failed3 = exc
    db.rollback()
    expect("reader_non_retryable_one_supply", failed3 is not None and provider3.invocations == 1, invocations=provider3.invocations)

    # router budget / fallback
    calls = {"primary": 0, "fallback": 0}

    class P:
        def extract_items(self, *a, **k):  # type: ignore[no-untyped-def]
            calls["primary"] += 1
            raise ProviderError("outage", "primary outage")

    class F:
        def extract_items(self, *a, **k):  # type: ignore[no-untyped-def]
            calls["fallback"] += 1
            return "fallback-result"

    rcfg = RouterConfig(provider_id="p", fallback_id="f", json_strict=True, cost_budget=1.0, retryable_errors=reader.RETRYABLE_ERRORS)
    r = ProviderRouter(rcfg, {"p": P(), "f": F()})
    result = r.execute("extract_items", b"b", "p", estimated_cost=0.5)
    expect("router_fallback_on_retryable", result == "fallback-result" and calls == {"primary": 1, "fallback": 1}, calls=dict(calls))
    calls.update(primary=0, fallback=0)
    try:
        r.execute("extract_items", b"b", "p", estimated_cost=2.0)
        budget_error = None
    except BudgetExceededError as exc:
        budget_error = exc
    expect("router_budget_refuses_before_call", budget_error is not None and calls == {"primary": 0, "fallback": 0}, calls=dict(calls))

    class PN:
        def extract_items(self, *a, **k):  # type: ignore[no-untyped-def]
            raise ProviderError("schema", "non-retryable")

    r2 = ProviderRouter(rcfg, {"p": PN(), "f": F()})
    calls.update(primary=0, fallback=0)
    try:
        r2.execute("extract_items", b"b", "p")
        kind_error = None
    except ProviderError as exc:
        kind_error = exc
    expect("router_no_fallback_on_non_retryable", kind_error is not None and kind_error.kind == "schema" and calls["fallback"] == 0, calls=dict(calls))
    try:
        r2.resolve("missing")
        nf = None
    except ProviderNotFoundError as exc:
        nf = exc
    expect("router_unknown_provider", nf is not None)


# ---------------------------------------------------------------- Part D
def part_d(db, client: TestClient) -> None:  # type: ignore[no-untyped-def]
    house = Household(name="SG180 G3 Reader House")
    db.add(house)
    db.commit()
    hid = house.id

    def upload(name="sauce.png"):  # type: ignore[no-untyped-def]
        color = "#%06x" % (abs(hash(name)) % 0xFFFFFF)
        r = client.post("/v1/evidence", params={"household_id": hid}, files={"file": (name, jpeg_bytes(color=color), "image/jpeg")})
        assert r.status_code == 201, r.text
        return r.json()["id"]

    def set_provider(provider, consent=True, provider_id=None):  # type: ignore[no-untyped-def]
        reader.provider_registry = lambda: {provider.provider_id: provider}  # type: ignore[assignment]
        settings.sg_consent = consent
        settings.sg_provider_id = provider_id or provider.provider_id

    # D1 consent off
    scripted = ScriptedProvider(provider_id="scripted", payload=dict(VALID_ITEMS))
    set_provider(scripted, consent=False)
    ev1 = upload("consent-off.png")
    j = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [ev1]}).json()["id"]
    run = client.post(f"/v1/imports/{j}/run", params={"household_id": hid}).json()
    ai_step = next(s for s in run["steps"] if s["step_name"] == "ANALYZING_WITH_AI")
    expect(
        "consent_off_skips_before_provider",
        ai_step["output"]["status"] == "skipped" and ai_step["output"]["reason"] == "consent_disabled" and scripted.invocations == 0,
        output=ai_step["output"],
        invocations=scripted.invocations,
    )

    # D2 provider not configured
    settings.sg_consent = True
    settings.sg_provider_id = "opencode-go"
    ev2 = upload("provider-missing.png")
    j2 = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [ev2]}).json()["id"]
    run2 = client.post(f"/v1/imports/{j2}/run", params={"household_id": hid}).json()
    ai2 = next(s for s in run2["steps"] if s["step_name"] == "ANALYZING_WITH_AI")
    expect("provider_not_configured_skips", ai2["output"]["status"] == "skipped" and ai2["output"]["reason"] == "provider_not_configured", output=ai2["output"])

    # D3 enabled: redacted bytes, real prompt, ledger, provenance
    original = jpeg_bytes(color="red", with_gps=True)
    r = client.post("/v1/evidence", params={"household_id": hid}, files={"file": ("gps-source.jpg", original, "image/jpeg")})
    ev3 = r.json()["id"]
    scripted3 = ScriptedProvider(provider_id="scripted", payload=dict(VALID_ITEMS))
    set_provider(scripted3)
    j3 = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [ev3]}).json()["id"]
    run3 = client.post(f"/v1/imports/{j3}/run", params={"household_id": hid}).json()
    prompt_text, version = reader.load_prompt("food")
    sent = scripted3.images[0]
    sent_img = Image.open(io.BytesIO(sent))
    ledger = db.query(ProviderCall).filter_by(job_id=j3).one()
    cand3 = db.query(candidates.Candidate).filter_by(job_id=j3).one()
    proposal = candidates.load_proposal(cand3)
    expect(
        "reader_sends_redacted_png_real_prompt",
        run3["state"] == "AWAITING_REVIEW"
        and scripted3.invocations == 1
        and sent.startswith(b"\x89PNG")
        and dict(sent_img.getexif()) == {}
        and sent_img.size == (48, 64)
        and sent != original
        and scripted3.prompts[0] == prompt_text
        and version.endswith("-v4"),
        sent_png=sent.startswith(b"\x89PNG"),
        sent_size=sent_img.size,
        exif=dict(sent_img.getexif()),
        prompt_is_real=scripted3.prompts[0] == prompt_text,
        version=version,
    )
    expect(
        "ledger_input_hash_is_redacted_sha",
        json.loads(ledger.input_hashes)["image_sha256"] == hashlib.sha256(sent).hexdigest()
        and json.loads(ledger.output_payload)["scripted"] is True
        and ledger.cost == 0.0
        and ledger.prompt_template_version == version,
        input_hashes=json.loads(ledger.input_hashes),
        expected_sha=hashlib.sha256(sent).hexdigest(),
    )
    expect(
        "candidate_provenance_threaded",
        proposal["ai_provider"] == "scripted"
        and proposal["prompt_template_version"] == version
        and proposal["provider_call_ids"] == [ledger.id]
        and proposal["fields"]["display_name"]["provider_call_id"] == ledger.id,
        provenance={k: proposal.get(k) for k in ("ai_provider", "ai_model", "prompt_template_version", "provider_call_ids")},
        field_provenance=proposal["fields"]["display_name"],
    )
    # accept and read assertion provenance
    decision = client.post(
        f"/v1/candidates/{cand3.id}/decision",
        params={"household_id": hid},
        json={"action": "accept"},
    )
    from app.models import Assertion, Asset  # noqa: E402

    asset = db.query(Asset).filter_by(household_id=hid).order_by(Asset.created_at.desc()).first()
    model_jsons = [json.loads(a.model_json) for a in db.query(Assertion).filter_by(asset_id=asset.id) if a.model_json]
    expect(
        "assertion_model_json_has_provider_lineage",
        decision.status_code == 200
        and any(m.get("provider") == "scripted" and m.get("prompt_template_version") == version and m.get("provider_call_id") == ledger.id for m in model_jsons),
        status=decision.status_code,
        model_json_samples=model_jsons[:2],
    )

    # D4 monthly cap refusal before any call + durable spend reader
    class EstimatingProvider(ScriptedProvider):
        def estimate_cost(self, image_bytes: bytes, prompt: str) -> float:
            return 1.0

    ev4 = upload("cap-source.png")
    cap_provider = EstimatingProvider(provider_id="scripted", payload=dict(VALID_ITEMS))
    set_provider(cap_provider)
    settings.sg_monthly_cap = 0.5
    j4 = client.post("/v1/imports", params={"household_id": hid}, json={"evidence_ids": [ev4]}).json()["id"]
    run4 = client.post(f"/v1/imports/{j4}/run", params={"household_id": hid}).json()
    rows4 = db.query(ProviderCall).filter_by(job_id=j4).count()
    expect(
        "monthly_cap_refuses_before_provider",
        run4["state"] == "FAILED"
        and cap_provider.invocations == 0
        and rows4 == 0
        and any("monthly" in e for e in run4["errors"]),
        state=run4["state"],
        invocations=cap_provider.invocations,
        ledger_rows=rows4,
        errors=run4["errors"],
    )
    settings.sg_monthly_cap = None

    spend_before = reader._recorded_spend(db, hid)
    job5 = job_service.create_job(db, hid, [])
    db.commit()
    db.add(ProviderCall(provider="p", model="m", prompt_template_version="v", cost=0.25, job_id=job5.id))
    db.add(ProviderCall(provider="p", model="m", prompt_template_version="v", cost=0.10, job_id=None))
    db.commit()
    spend_after = reader._recorded_spend(db, hid)
    jina_row = record_jina_search_call(
        db,
        job5,
        fetch_jina_search("beans", "AuditBrand", http_client=httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json={"data": []}, request=req))), api_key=FAKE_KEY),
        query="AuditBrand beans",
    )
    spend_with_jina = reader._recorded_spend(db, hid)
    expect(
        "durable_spend_reader_sums_job_and_unattributed",
        abs(spend_after - spend_before - 0.35) < 1e-9 and abs(spend_with_jina - spend_after - estimate_jina_search_cost()) < 1e-9,
        before=spend_before,
        after=spend_after,
        with_jina=spend_with_jina,
        jina_cost=jina_row.cost,
    )
    observe(
        "unattributed_pool_counts_against_every_household",
        note="provider_call rows with job_id NULL are summed into every household's monthly spend (reader.py:286-306)",
        spend=spend_with_jina,
    )


# ---------------------------------------------------------------- Part E
def part_e(db) -> None:  # type: ignore[no-untyped-def]
    off_req = build_off_request("Sauce", "AuditBrand")
    expect(
        "off_request_shape",
        off_req.method == "GET"
        and off_req.url == "https://world.openfoodfacts.org/api/v2/search"
        and off_req.params
        == {
            "search_terms": "Sauce",
            "brands_tags": "AuditBrand",
            "countries_tags_en": "romania",
            "page": "1",
            "page_size": "10",
            "fields": "code,product_name,brands,ingredients_text,nutriments,packaging,countries_tags_en",
        }
        and off_req.headers["Accept"] == "application/json"
        and "StorageGenie" in off_req.headers["User-Agent"],
        params=off_req.params,
    )
    seen = []

    def off_handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"products": [{"code": "123", "product_name": "Sauce"}]}, request=request)

    snap_ok = fetch_off_search("Sauce", "AuditBrand", http_client=httpx.Client(transport=httpx.MockTransport(off_handler)))
    expect(
        "off_success_snapshot",
        snap_ok.no_result_reason is None and len(snap_ok.products) == 1 and snap_ok.status_code == 200
        and snap_ok.request_url.startswith("https://world.openfoodfacts.org/api/v2/search"),
        status=snap_ok.status_code,
        products=len(snap_ok.products),
        request_url=snap_ok.request_url,
    )
    snap_mal = fetch_off_search("Sauce", "AuditBrand", http_client=httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json={"count": 0}, request=req))))
    snap_500 = fetch_off_search("Sauce", "AuditBrand", http_client=httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(500, text="off down", request=req))))
    def off_boom(req):  # type: ignore[no-untyped-def]
        raise httpx.ConnectTimeout("off timeout", request=req)
    snap_transport = fetch_off_search("Sauce", "AuditBrand", http_client=httpx.Client(transport=httpx.MockTransport(off_boom)))
    expect(
        "off_degradations_loud",
        snap_mal.no_result_reason is not None and "products" in snap_mal.no_result_reason
        and snap_500.no_result_reason is not None and snap_500.no_result_reason.startswith("http_status")
        and snap_transport.no_result_reason is not None and snap_transport.no_result_reason.startswith("transport"),
        malformed=snap_mal.no_result_reason,
        http500=snap_500.no_result_reason,
        transport=snap_transport.no_result_reason,
    )
    row = record_off_snapshot(db, snap_ok, query="AuditBrand Sauce")
    readback = get_snapshot(db, row.id)
    expect(
        "off_snapshot_persisted_verbatim",
        readback is not None and json.loads(readback.raw_body)["products"][0]["code"] == "123" and readback.version,
        raw_body=readback.raw_body,
        version=readback.version,
    )

    jina_req = build_jina_request("Sauce", "AuditBrand")
    expect(
        "jina_request_identifiers_only",
        jina_req.method == "GET"
        and jina_req.url == "https://s.jina.ai/AuditBrand+Sauce"
        and jina_req.params
        == (("site", "mega-image.ro"), ("site", "emag.ro"), ("site", "farmaciatei.ro"), ("num", "5"), ("type", "web"), ("gl", "ro"))
        and "Authorization" not in jina_req.headers
        and jina_req.headers["X-Respond-With"] == "content",
        url=jina_req.url,
        params=jina_req.params,
        headers=jina_req.headers,
    )
    authorized = authorize(jina_req.headers, FAKE_KEY)
    expect("jina_bearer_added_at_send", authorized["Authorization"] == f"Bearer {FAKE_KEY}")
    jseen = []

    def jina_handler(request: httpx.Request) -> httpx.Response:
        jseen.append(request)
        return httpx.Response(200, json={"data": [{"title": "Sauce", "url": "https://emag.ro/p/1"}]}, request=request)

    jclient = httpx.Client(transport=httpx.MockTransport(jina_handler))
    jsnap = fetch_jina_search("Sauce", "AuditBrand", http_client=jclient, api_key=FAKE_KEY)
    jreq = jseen[0]
    expect(
        "jina_wire_shape_and_snapshot",
        jsnap.no_result_reason is None
        and len(jsnap.results) == 1
        and jreq.headers["authorization"] == f"Bearer {FAKE_KEY}"
        and jreq.url.params.get_list("site") == ["mega-image.ro", "emag.ro", "farmaciatei.ro"]
        and "AuditBrand" in str(jreq.url),
        status=jsnap.status_code,
        sites=jreq.url.params.get_list("site"),
        results=len(jsnap.results),
    )
    jmal = fetch_jina_search(
        "Sauce", "AuditBrand", api_key=FAKE_KEY, http_client=httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json={"nope": 1}, request=req)))
    )
    jempty = fetch_jina_search(
        "Sauce", "AuditBrand", api_key=FAKE_KEY, http_client=httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json=[], request=req)))
    )
    jnokey = fetch_jina_search("Sauce", "AuditBrand", api_key=None)
    expect(
        "jina_degradations",
        jmal.no_result_reason is not None and jmal.no_result_reason.startswith("malformed_payload")
        and jempty.no_result_reason is None and jempty.results == ()
        and jnokey.no_result_reason is not None and jnokey.no_result_reason.startswith("missing_key"),
        malformed=jmal.no_result_reason,
        empty_is_success=jempty.no_result_reason is None,
        missing_key=jnokey.no_result_reason[:60],
    )
    jrow = record_jina_snapshot(db, jsnap, query="AuditBrand Sauce")
    expect("jina_snapshot_persisted", get_snapshot(db, jrow.id) is not None)

    synthesis_input = build_synthesis_input(
        {"product_name": "Sauce"},
        {"data": [{"title": "Sauce"}]},
        off_source_url=snap_ok.request_url,
        off_retrieved_at=snap_ok.retrieved_at,
        jina_source_url=jsnap.request_url,
        jina_retrieved_at=jsnap.retrieved_at,
        brand="AuditBrand",
    )
    expect(
        "synthesis_input_carries_source_attribution",
        "source_name: OpenFoodFacts" in synthesis_input
        and "source_name: JinaSearch" in synthesis_input
        and "source_url: https://world.openfoodfacts.org" in synthesis_input
        and snap_ok.retrieved_at in synthesis_input
        and "brand: AuditBrand" in synthesis_input,
        head=synthesis_input[:200],
    )


def main() -> int:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    assert str(TEMP_ROOT) in settings.storage_root and str(TEMP_ROOT) in str(engine.url)
    record("isolation", "PASS", storage_root=settings.storage_root, engine_url=str(engine.url))
    client = TestClient(app)
    part_a()
    part_b(db)
    part_d(db, client)
    part_e(db)
    db.close()
    print(json.dumps({"results": RESULTS, "captured_wire_requests": len(CAPTURED)}, indent=2))
    print(f"TEMP_ROOT={TEMP_ROOT}")
    return 1 if any(r["result"] == "FAIL" for r in RESULTS) else 0


if __name__ == "__main__":
    sys.exit(main())
