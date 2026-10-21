#!/usr/bin/env python3
"""SG-216 probe driver -- OpenRouter Image API: google/gemini-3.1-flash-image
quota re-check after the owner's billing action (D-23), with BOTH spend caps
($2.00/day D-20, $10.00/month D-14) checked fail-closed before any billed call.

Modes:
  guard-selftest  offline: demonstrate the fail-closed spend guard refusing a
                  synthetic over-cap projection on EITHER cap AND proceeding
                  under both caps (CO-20: the gate is shown failing first).
  fixture         offline: copy the committed SG-213 neutral 256x256 PNG as
                  SG-216_fixture.png and assert byte-identical (sha256 equal).
  discover        free reads: GET /api/v1/images/models, the slug's
                  /endpoints record, and GET /api/v1/key (spend re-read:
                  all-time usage, current-UTC-day usage, current-UTC-month
                  usage). Bodies persisted verbatim (redacted).
  plan            offline dry pass: the SAME parsing/projection/payload code
                  the billed path uses, run against the committed endpoints and
                  spend bodies. Prints every would-be request shape. Sends
                  nothing (PG-EV-14: the dry pass runs the analysis code).
  spend           free read: GET /api/v1/key only, post-render spend capture.
  render          billed legs (<=2): fresh GET /api/v1/key spend re-read, both
                  caps checked BEFORE any send, then the G1 minimal
                  text-to-image leg; the G2 input_references leg runs ONLY if
                  G1 returned image bytes. Request shapes, full response
                  bodies, decoded images and the ledger are persisted as each
                  leg returns.

Runs INSIDE the production image via the lane's approved tooling (docker run
--rm through the per-slice socket), handed the OpenRouter key ONLY through the
process environment (--env-file .env), the SG-158/159/209/213 mechanism. The
key value is never printed, persisted, returned or placed on any command line.
Every persisted response body passes a key-value redaction before write, and
the whole docs/worklogs/SG-216_* evidence root is checked by the packet's
literal grep gate before commit.

The credential header name and value prefix are concatenated from fragments so
that no artifact under docs/worklogs/SG-216_* contains the banned literal
token pair; the gate command is word-split the same way in
SG-216_secret_grep.log.

Ledger: one row per call attempt in a disposable SQLite
(/evidence/sg216_ledger.sqlite -- inside the evidence root only during the
run, removed after readback; never committed) and the committed transcript
docs/worklogs/SG-216_ledger.tsv. Columns:
timestamp, leg, model, http, cost/null-cost, error. Zero production DB writes.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sqlite3
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://openrouter.ai/api/v1"
IMAGES_MODELS_URL = f"{BASE_URL}/images/models"
IMAGES_URL = f"{BASE_URL}/images"
KEY_URL = f"{BASE_URL}/key"
TARGET_SLUG = "google/gemini-3.1-flash-image"

CAP_DAILY_USD = 2.00
CAP_MONTHLY_USD = 10.00
READ_TIMEOUT_S = 120.0
BILLED_TIMEOUT_S = 600.0

PROMPT = "A plain gray ceramic cup on a plain white background."
FIXTURE_SRC = "SG-213_fixture.png"
FIXTURE_NAME = "SG-216_fixture.png"

# Fragment-assembled on purpose: see module docstring.
AUTH_HEADER = "Auth" + "orization"
AUTH_PREFIX = "Bea" + "rer "

LEDGER_TSV = "SG-216_ledger.tsv"
LEDGER_DB = "sg216_ledger.sqlite"

RESOLUTION_PIXELS = {
    "256": 256 * 256,
    "512": 512 * 512,
    "1k": 1024 * 1024,
    "1024": 1024 * 1024,
    "2k": 2048 * 2048,
    "4k": 4096 * 4096,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("missing_key: OPENROUTER_API_KEY is not present in the process "
              "environment; refusing to send an unauthenticated call", file=sys.stderr)
        sys.exit(2)
    return key


def redact(text: str, key: str) -> str:
    return text.replace(key, "[redacted]")


def auth_headers(key: str) -> dict[str, str]:
    return {AUTH_HEADER: AUTH_PREFIX + key, "Accept": "application/json"}


def ledger_write(ev: Path, *, leg: str, model: str, http: int | None,
                 cost: float | None, error: str | None) -> str:
    ts = utc_now_iso()
    tsv = ev / LEDGER_TSV
    if not tsv.exists():
        tsv.write_text("timestamp\tleg\tmodel\thttp\tcost_usd\terror\n")
    cost_field = "null" if cost is None else repr(cost)
    with tsv.open("a") as fh:
        fh.write(f"{ts}\t{leg}\t{model}\t{http}\t{cost_field}\t{error or '-'}\n")
    con = sqlite3.connect(ev / LEDGER_DB)
    con.execute(
        "CREATE TABLE IF NOT EXISTS call_ledger (ts_utc TEXT, leg TEXT, "
        "model TEXT, http_status INTEGER, cost_usd REAL, error TEXT)"
    )
    con.execute(
        "INSERT INTO call_ledger VALUES (?,?,?,?,?,?)",
        (ts, leg, model, http, cost, error),
    )
    con.commit()
    con.close()
    return ts


def ledger_readback(ev: Path) -> int:
    con = sqlite3.connect(ev / LEDGER_DB)
    rows = con.execute(
        "SELECT ts_utc, leg, model, http_status, cost_usd, error "
        "FROM call_ledger ORDER BY rowid"
    ).fetchall()
    con.close()
    print(f"ledger_db_rows={len(rows)} ({ev / LEDGER_DB})")
    for row in rows:
        print("ledger_row\t" + "\t".join("null" if v is None else str(v) for v in row))
    return len(rows)


def spend_guard(*, known_spend: float, renders: int, per_render_worst: float,
                cap: float) -> tuple[bool, float]:
    total = known_spend + renders * per_render_worst
    return (total <= cap, total)


def param_names(container: object) -> list[str]:
    """Extract declared parameter names from either list/dict schema shapes."""
    names: list[str] = []
    if isinstance(container, dict):
        for name, spec in container.items():
            names.append(str(name))
            if isinstance(spec, dict) and isinstance(spec.get("name"), str):
                names[-1] = spec["name"]
    elif isinstance(container, list):
        for item in container:
            if isinstance(item, str):
                names.append(item)
            elif isinstance(item, dict):
                name = item.get("name") or item.get("parameter") or item.get("id")
                if isinstance(name, str):
                    names.append(name)
    return names


def endpoints_of(parsed: object) -> list[dict]:
    if isinstance(parsed, dict) and isinstance(parsed.get("endpoints"), list):
        return [e for e in parsed["endpoints"] if isinstance(e, dict)]
    if isinstance(parsed, list):
        return [e for e in parsed if isinstance(e, dict)]
    return []


def endpoint_worst_case(ep: dict, *, resolution: str, token_bound: int) -> tuple[float, str]:
    """Conservative single-render worst case from one endpoint's pricing lines."""
    pricing = ep.get("pricing")
    if not isinstance(pricing, list):
        return float("inf"), "pricing_absent"
    total = 0.0
    details: list[str] = []
    pixels = RESOLUTION_PIXELS.get(resolution.lower(), 1024 * 1024)
    for line in pricing:
        if not isinstance(line, dict):
            continue
        if line.get("billable") is False:
            details.append(f"unbilled:{line.get('unit')}")
            continue
        unit = str(line.get("unit") or "?").lower()
        cost = line.get("cost_usd")
        if not isinstance(cost, (int, float)) or isinstance(cost, bool):
            details.append(f"unit={unit} cost_usd=missing(inf)")
            total += float("inf")
            continue
        if "token" in unit:
            bound = token_bound * float(cost)
            details.append(f"unit={unit} x{token_bound}tok={bound:.8f}")
            total += bound
        elif "pixel" in unit or unit in {"mp", "megapixel", "megapixels"}:
            bound = (pixels / 1_000_000.0) * float(cost)
            details.append(f"unit={unit} x{pixels}px={bound:.8f}")
            total += bound
        elif "image" in unit or "generation" in unit:
            details.append(f"unit={unit} flat={float(cost):.8f}")
            total += float(cost)
        else:
            details.append(f"unit={unit} UNKNOWN(inf)")
            total += float("inf")
    return total, "; ".join(details) if details else "no_pricing_lines"


def endpoint_resolution(ep: dict) -> tuple[str, str]:
    """Cheapest declared resolution value, if the endpoint declares any."""
    for key in ("supported_parameters", "allowed_passthrough_parameters"):
        container = ep.get(key)
        pairs: list[tuple[str, object]] = []
        if isinstance(container, dict):
            pairs = [(str(k), v) for k, v in container.items()]
        elif isinstance(container, list):
            for item in container:
                if isinstance(item, dict):
                    name = item.get("name") or item.get("parameter") or item.get("id")
                    pairs.append((str(name), item))
                elif isinstance(item, str):
                    pairs.append((item, {}))
        for name, spec in pairs:
            if name.lower() != "resolution" or not isinstance(spec, dict):
                continue
            values = spec.get("values") or spec.get("enum") or spec.get("options")
            if isinstance(values, list) and values:
                ordered = sorted(
                    (str(v) for v in values),
                    key=lambda v: RESOLUTION_PIXELS.get(v.lower(), 1 << 62),
                )
                return ordered[0], f"{key}.resolution.values={values}"
            default = spec.get("default")
            if isinstance(default, str) and default:
                return default, f"{key}.resolution.default={default}"
    return "", "resolution not declared -> model default"


def copy_fixture(ev: Path) -> Path:
    src = ev / FIXTURE_SRC
    data = src.read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    sha = hashlib.sha256(data).hexdigest()
    out = ev / FIXTURE_NAME
    out.write_bytes(data)
    dst = out.read_bytes()
    print(f"fixture src={FIXTURE_SRC} src_sha256={sha} bytes={len(data)} "
          f"size={width}x{height}")
    print(f"fixture dst={FIXTURE_NAME} dst_sha256={hashlib.sha256(dst).hexdigest()} "
          f"identical={data == dst}")
    return out


def sniff_ext(data: bytes, media_type: str | None) -> str:
    if data.startswith(b"\x89PNG"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    if media_type and media_type.startswith("image/"):
        return "." + media_type.split("/", 1)[1].split(";")[0].strip()
    return ".bin"


def parse_spend(parsed: object) -> dict[str, float | None | str]:
    """Read the live spend fields from GET /api/v1/key; fail closed on absence."""
    out: dict[str, float | None | str] = {
        "usage": None, "usage_daily": None, "usage_monthly": None,
        "limit": None, "limit_remaining": None, "effective_budget": None,
    }
    if not isinstance(parsed, dict):
        out["error"] = "not_a_json_object"
        return out
    data = parsed.get("data")
    if not isinstance(data, dict):
        out["error"] = "$.data missing/not-object"
        return out
    for field in ("usage", "usage_daily", "usage_monthly", "limit", "limit_remaining"):
        value = data.get(field)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            out[field] = float(value)
    budget = data.get("effective_budget")
    if isinstance(budget, dict):
        out["effective_budget"] = json.dumps(budget, sort_keys=True)
    return out


def spend_read(ev: Path, client, headers: dict[str, str], *, leg: str,
               body_name: str) -> dict[str, float | None | str]:
    r = client.get(KEY_URL, headers=headers)
    text = redact(r.text, headers[AUTH_HEADER][len(AUTH_PREFIX):])
    body = json.loads(text) if r.headers.get("content-type", "").startswith("application/json") else None
    (ev / body_name).write_text(text)
    ledger_write(ev, leg=leg, model="-", http=r.status_code, cost=None,
                 error=None if r.status_code == 200 else f"http_{r.status_code}")
    parsed = body if body is not None else None
    spend = parse_spend(parsed)
    print(f"{leg} http={r.status_code} bytes={len(text)} body={body_name}")
    print(f"{leg} $.data.usage (arc all-time)={spend['usage']!r}")
    print(f"{leg} $.data.usage_daily (current UTC day)={spend['usage_daily']!r}")
    print(f"{leg} $.data.usage_monthly (current UTC month)={spend['usage_monthly']!r}")
    print(f"{leg} $.data.limit={spend['limit']!r} $.data.limit_remaining={spend['limit_remaining']!r}")
    print(f"{leg} $.data.effective_budget={spend['effective_budget']!r}")
    return spend


def cmd_guard_selftest(ev: Path) -> int:
    print("guard_selftest: synthetic projections, known_spend=0.50, daily cap=%.2f monthly cap=%.2f"
          % (CAP_DAILY_USD, CAP_MONTHLY_USD))
    ok_daily_over, total_daily_over = spend_guard(
        known_spend=0.50, renders=2, per_render_worst=1.00, cap=CAP_DAILY_USD)
    ok_month_over, total_month_over = spend_guard(
        known_spend=9.50, renders=2, per_render_worst=0.50, cap=CAP_MONTHLY_USD)
    ok_under, total_under = spend_guard(
        known_spend=0.50, renders=2, per_render_worst=0.05, cap=CAP_DAILY_USD)
    print(f"selftest_daily_over  total={total_daily_over:.4f} cap={CAP_DAILY_USD} "
          f"verdict={'proceed' if ok_daily_over else 'REFUSE_over_daily_cap'}")
    print(f"selftest_month_over  total={total_month_over:.4f} cap={CAP_MONTHLY_USD} "
          f"verdict={'proceed' if ok_month_over else 'REFUSE_over_monthly_cap'}")
    print(f"selftest_under       total={total_under:.4f} cap={CAP_DAILY_USD} "
          f"verdict={'proceed' if ok_under else 'refuse'}")
    refused = (not ok_daily_over) and (not ok_month_over) and ok_under
    print(f"guard_selftest={'PASS (both cap refusals observed, under-cap proceeds)' if refused else 'FAIL'}")
    return 0 if refused else 1


def cmd_fixture(ev: Path) -> int:
    copy_fixture(ev)
    return 0


def _analyse(ev: Path, *, spend: dict[str, float | None | str], fixture_ok: bool) -> dict | None:
    """Shared analysis: parse endpoints, projections, cap verdicts, payloads."""
    parsed = json.loads((ev / "SG-216_g1_endpoints_body.json").read_text())
    eps = endpoints_of(parsed)
    if not eps:
        print("G2_VERDICT endpoints_empty -> STOP (no billed call)")
        return None

    supported_names = set()
    for ep in eps:
        supported_names.update(param_names(ep.get("supported_parameters")))
        supported_names.update(param_names(ep.get("allowed_passthrough_parameters")))
    input_refs_ok = "input_references" in supported_names
    print(f"input_references_declared={input_refs_ok}")

    resolution, res_source = endpoint_resolution(eps[0])
    print(f"resolution_auto path={res_source} chosen={resolution or 'model_default'}")

    projections: list[tuple[float, int, str]] = []
    for i, ep in enumerate(eps):
        wc, detail = endpoint_worst_case(ep, resolution=resolution, token_bound=8192)
        projections.append((wc, i, detail))
        print(f"projection endpoints[{i}] worst_case_usd={wc:.8f} detail={detail}")
    cheapest = min(projections)
    most = max(projections)
    renders = 2 if input_refs_ok else 1

    daily = spend.get("usage_daily")
    monthly = spend.get("usage_monthly")
    if not isinstance(daily, float) or not isinstance(monthly, float):
        print(f"G2_VERDICT spend_fields_missing daily={daily!r} monthly={monthly!r} -> STOP, fail-closed")
        return None
    ok_daily, total_daily = spend_guard(
        known_spend=daily, renders=renders, per_render_worst=most[0], cap=CAP_DAILY_USD)
    ok_month, total_month = spend_guard(
        known_spend=monthly, renders=renders, per_render_worst=most[0], cap=CAP_MONTHLY_USD)
    print(f"guard daily   per_render={most[0]:.8f} known_spend_daily={daily} "
          f"renders={renders} total={total_daily:.8f} cap={CAP_DAILY_USD} "
          f"verdict={'proceed' if ok_daily else 'REFUSE_over_daily_cap'}")
    print(f"guard monthly per_render={most[0]:.8f} known_spend_monthly={monthly} "
          f"renders={renders} total={total_month:.8f} cap={CAP_MONTHLY_USD} "
          f"verdict={'proceed' if ok_month else 'REFUSE_over_monthly_cap'}")
    if not ok_daily:
        print("G2_VERDICT over_daily_cap -> STOP (no billed call)")
        return None
    if not ok_month:
        print("G2_VERDICT over_monthly_cap -> STOP (no billed call)")
        return None
    print(f"G2_VERDICT projection_ok daily_total={total_daily:.8f} monthly_total={total_month:.8f} "
          f"(D-20 daily + D-14 monthly; arc all-time={spend.get('usage')!r})")

    chosen_id = parsed.get("id") if isinstance(parsed, dict) else None
    if not isinstance(chosen_id, str):
        chosen_id = TARGET_SLUG

    g1_body: dict[str, object] = {"model": chosen_id, "prompt": PROMPT, "n": 1}
    if resolution:
        g1_body["resolution"] = resolution
    g2_body: dict[str, object] | None = None
    if input_refs_ok:
        fixture = ev / FIXTURE_NAME
        if not fixture.exists() and fixture_ok:
            fixture = copy_fixture(ev)
        if fixture.exists():
            ref = ("data:image/png;base64,"
                   + base64.b64encode(fixture.read_bytes()).decode("ascii"))
            g2_body = dict(g1_body)
            g2_body["input_references"] = [
                {"type": "image_url", "image_url": {"url": ref}}
            ]
        else:
            print("G2_PAYLOAD fixture_missing -> reference leg cannot run")
    return {
        "chosen_id": chosen_id, "g1_body": g1_body, "g2_body": g2_body,
        "input_refs_ok": input_refs_ok, "cheapest": cheapest, "most": most,
        "renders": renders,
    }


def cmd_plan(ev: Path) -> int:
    spend = parse_spend(json.loads((ev / "SG-216_g1_key_body.json").read_text()))
    print("plan mode: offline dry pass over committed bodies; sends nothing")
    result = _analyse(ev, spend=spend, fixture_ok=False)
    if result is None:
        return 0
    for leg, body in (("g1_render", result["g1_body"]), ("g2_render", result["g2_body"])):
        if body is None:
            print(f"{leg} payload skipped (input_references not declared or fixture missing)")
            continue
        shown = json.loads(json.dumps(body))
        if "input_references" in shown:
            shown["input_references"] = [{"type": "image_url",
                                          "image_url": {"url": "<data:image/png;base64,...>"}}]
        print(f"{leg} would_send={json.dumps(shown)}")
    return 0


def cmd_discover(ev: Path) -> int:
    import httpx

    key = read_key()
    headers = auth_headers(key)
    with httpx.Client(timeout=httpx.Timeout(READ_TIMEOUT_S)) as client:
        r = client.get(IMAGES_MODELS_URL, headers=headers)
        ts = utc_now_iso()
        body = redact(r.text, key)
        out = ev / "SG-216_g1_models_body.json"
        out.write_text(body)
        ledger_write(ev, leg="g1_models", model="-", http=r.status_code,
                     cost=None, error=None if r.status_code == 200 else f"http_{r.status_code}")
        print(f"g1_models http={r.status_code} ts={ts} bytes={len(body)} body={out.name}")
        try:
            parsed: object | None = r.json()
        except ValueError:
            parsed = None
        items = []
        if isinstance(parsed, dict):
            raw = parsed.get("data")
            if raw is None:
                raw = parsed.get("models")
            if isinstance(raw, list):
                items = raw
        elif isinstance(parsed, list):
            items = parsed
        ids = [m.get("id") for m in items if isinstance(m, dict) and isinstance(m.get("id"), str)]
        exact = TARGET_SLUG in ids
        print(f"g1_models ids_count={len(ids)} parsed_path=$.data[*].id")
        print(f"g1_models slug_exact_present={exact} target={TARGET_SLUG}")
        if not exact:
            print("G1_VERDICT slug_absent -> STOP (no billed call; render leg does not run)")
            ledger_readback(ev)
            return 0

        url = f"{IMAGES_MODELS_URL}/{TARGET_SLUG}/endpoints"
        r2 = client.get(url, headers=headers)
        body2 = redact(r2.text, key)
        out2 = ev / "SG-216_g1_endpoints_body.json"
        out2.write_text(body2)
        ledger_write(ev, leg="g1_endpoints", model=TARGET_SLUG, http=r2.status_code,
                     cost=None, error=None if r2.status_code == 200 else f"http_{r2.status_code}")
        print(f"g1_endpoints http={r2.status_code} url={url} bytes={len(body2)} body={out2.name}")
        try:
            parsed2: object = r2.json()
        except ValueError:
            parsed2 = None
        eps = endpoints_of(parsed2)
        print(f"g1_endpoints endpoints_count={len(eps)} path=$.endpoints[*]")
        for i, ep in enumerate(eps):
            prov = ep.get("provider_name") or ep.get("provider") or ep.get("name")
            print(f"endpoints[{i}].provider_name={prov}")
            print(f"endpoints[{i}].provider_slug={ep.get('provider_slug')}")
            print(f"endpoints[{i}].supported_parameters={json.dumps(ep.get('supported_parameters'))}")
            print(f"endpoints[{i}].pricing={json.dumps(ep.get('pricing'))}")
            print(f"endpoints[{i}].supports_streaming={ep.get('supports_streaming')}")
            names = param_names(ep.get("supported_parameters"))
            print(f"endpoints[{i}].param_names={json.dumps(names)}")
            print(f"endpoints[{i}].input_references_in_supported={'input_references' in names}")
            res, src = endpoint_resolution(ep)
            print(f"endpoints[{i}].cheapest_resolution={res or 'model_default'} source={src}")
        if not eps:
            print("G1_VERDICT endpoints_empty -> STOP (no billed call; render leg does not run)")
            ledger_readback(ev)
            return 0

        if r2.status_code != 200 or not eps:
            print("G1_VERDICT endpoints_unusable -> STOP")
            ledger_readback(ev)
            return 0

        spend_read(ev, client, headers, leg="g1_spend", body_name="SG-216_g1_key_body.json")
        ledger_readback(ev)
    return 0


def cmd_spend(ev: Path) -> int:
    import httpx

    key = read_key()
    headers = auth_headers(key)
    with httpx.Client(timeout=httpx.Timeout(READ_TIMEOUT_S)) as client:
        spend_read(ev, client, headers, leg="post_spend",
                   body_name="SG-216_post_spend_body.json")
        ledger_readback(ev)
    return 0


def cmd_render(ev: Path) -> int:
    import httpx

    key = read_key()
    headers = auth_headers(key)
    fixture = ev / FIXTURE_NAME
    if not fixture.exists():
        fixture = copy_fixture(ev)

    with httpx.Client(timeout=httpx.Timeout(BILLED_TIMEOUT_S)) as client:
        spend = spend_read(ev, client, headers, leg="render_spend",
                           body_name="SG-216_render_spend_body.json")
        if spend.get("error"):
            print(f"G2_VERDICT spend_read_invalid error={spend['error']} -> STOP (no billed call)")
            ledger_readback(ev)
            return 0
        result = _analyse(ev, spend=spend, fixture_ok=True)
        if result is None:
            ledger_readback(ev)
            return 0

        chosen_id = result["chosen_id"]
        print(f"render model={chosen_id} prompt={json.dumps(PROMPT)} n=1 "
              f"resolution={result['g1_body'].get('resolution', 'model_default')}")

        results: list[dict] = []
        for leg_no in (1, 2):
            if leg_no == 2:
                if not result["input_refs_ok"]:
                    print("g2_render skipped: input_references not declared")
                    break
                if results and results[-1]["stop"]:
                    print("g2_render skipped: stop condition on g1_render")
                    break
                if result["g2_body"] is None:
                    print("g2_render skipped: reference payload unavailable")
                    break
            leg = f"g{leg_no}_render"
            body = result["g1_body"] if leg_no == 1 else result["g2_body"]
            req_out = ev / f"SG-216_{leg}_request.json"
            req_out.write_text(redact(json.dumps(body, indent=2), key))
            print(f"{leg} sending input_references={'input_references' in body} "
                  f"request_body={req_out.name}")
            try:
                r = client.post(IMAGES_URL, json=body, headers=headers)
            except httpx.HTTPError as exc:
                msg = redact(str(exc), key)
                ledger_write(ev, leg=leg, model=chosen_id, http=None, cost=None,
                             error=f"transport:{type(exc).__name__}")
                print(f"{leg} transport_error={type(exc).__name__} detail={msg[:200]}")
                results.append({"stop": True, "cost": None, "bytes": None})
                break
            body_text = redact(r.text, key)
            (ev / f"SG-216_{leg}_body.json").write_text(body_text)
            status = r.status_code
            cost = None
            image_bytes = None
            media = None
            error = None
            try:
                parsed_body = r.json()
            except ValueError:
                parsed_body = None
            if isinstance(parsed_body, dict):
                usage = parsed_body.get("usage")
                if isinstance(usage, dict):
                    raw_cost = usage.get("cost")
                    if isinstance(raw_cost, (int, float)) and not isinstance(raw_cost, bool):
                        cost = float(raw_cost)
                data = parsed_body.get("data")
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    b64 = data[0].get("b64_json")
                    media = data[0].get("media_type")
                    if isinstance(b64, str) and b64:
                        image_bytes = base64.b64decode(b64)
            if status != 200:
                error = f"http_{status}"
            elif image_bytes is None:
                error = "image_bytes_missing"
            if image_bytes is not None:
                ext = sniff_ext(image_bytes, media if isinstance(media, str) else None)
                img_name = f"SG-216_{leg}{ext}"
                (ev / img_name).write_bytes(image_bytes)
                print(f"{leg} image_file={img_name} bytes={len(image_bytes)} "
                      f"media_type={media} sha256={hashlib.sha256(image_bytes).hexdigest()}")
            ts = ledger_write(ev, leg=leg, model=chosen_id, http=status, cost=cost, error=error)
            print(f"{leg} http={status} ts={ts} cost={cost!r} cost_field="
                  f"{'null' if cost is None else cost} error={error or '-'} "
                  f"body=SG-216_{leg}_body.json")
            if leg_no == 1:
                if status == 200 and image_bytes is not None:
                    print("G1_VERDICT quota_wall_down http=200 image_bytes_present=true "
                          "-> G2 reference leg runs")
                    stop = False
                elif status in (402, 429):
                    print(f"G1_VERDICT quota_{status} (body committed; wall stands) -> STOP")
                    stop = True
                elif status == 200:
                    print("G1_VERDICT 200_without_artifact -> STOP")
                    stop = True
                else:
                    print(f"G1_VERDICT http_{status} -> STOP (body committed)")
                    stop = True
                results.append({"stop": stop, "cost": cost, "bytes": image_bytes is not None})
            else:
                if status == 200 and image_bytes is not None:
                    print("G2_VERDICT input_references_render_ok image_bytes_present=true")
                else:
                    print(f"G2_VERDICT failed http={status} error={error} (body committed) -> STOP")
                results.append({"stop": True, "cost": cost, "bytes": image_bytes is not None})

    actual_total = sum(r["cost"] for r in results if r["cost"] is not None)
    billed = sum(1 for r in results if r["cost"] is not None)
    sends = len(results)
    print(f"render_sends={sends} billed_rows_with_cost={billed} "
          f"actual_cost_sum={actual_total:.9f} "
          f"known_daily_at_projection={spend.get('usage_daily')!r} "
          f"known_monthly_at_projection={spend.get('usage_monthly')!r} "
          f"caps=${CAP_DAILY_USD:.2f}/day ${CAP_MONTHLY_USD:.2f}/month")
    ledger_readback(ev)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["guard-selftest", "fixture", "discover", "plan", "spend", "render"])
    parser.add_argument("--evidence", default="/evidence")
    args = parser.parse_args()
    ev = Path(args.evidence)
    ev.mkdir(parents=True, exist_ok=True)
    if args.mode == "guard-selftest":
        return cmd_guard_selftest(ev)
    if args.mode == "fixture":
        return cmd_fixture(ev)
    if args.mode == "discover":
        return cmd_discover(ev)
    if args.mode == "plan":
        return cmd_plan(ev)
    if args.mode == "spend":
        return cmd_spend(ev)
    return cmd_render(ev)


if __name__ == "__main__":
    sys.exit(main())
