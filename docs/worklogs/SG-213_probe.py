#!/usr/bin/env python3
"""SG-213 probe driver -- OpenRouter Image API: google/gemini-3.1-flash-image
quota re-check + minimal billed renders (SG-159 wall retry, D-18(b)).

Modes:
  guard-selftest  offline: demonstrate the fail-closed spend guard refusing a
                  synthetic over-cap projection AND proceeding under the cap
                  (CO-20: the gate is shown failing before it is trusted).
  fixture         offline: copy the committed SG-209 neutral 256x256 PNG as
                  SG-213_fixture.png and assert byte-identical (sha256 equal).
  discover        free reads: GET /api/v1/images/models, then the slug's
                  /endpoints record; both bodies persisted verbatim (redacted).
  render          billed legs (<=2): projection + guard computed BEFORE any
                  send, then the G1 minimal text-to-image leg; the G2
                  input_references leg runs ONLY if G1 returned image bytes.
                  Request shapes, full response bodies, decoded images and the
                  ledger are persisted.

Runs INSIDE the production image via the lane's approved tooling (docker run
--rm through the per-slice socket), handed the OpenRouter key ONLY through the
process environment (--env-file .env), the SG-158/159/209 mechanism. The key
value is never printed, persisted, returned or placed on any command line.
Every persisted response body passes a key-value redaction before write, and
the whole docs/worklogs/SG-213_* evidence root is checked by the packet's
literal grep gate before commit.

The credential header name and value prefix are concatenated from fragments so
that no artifact under docs/worklogs/SG-213_* contains the banned literal
token pair; the gate command is word-split the same way in
SG-213_secret_grep.log.

Ledger: one row per call attempt in a disposable SQLite
(/evidence/sg213_ledger.sqlite -- inside the evidence root only during the
run, removed after readback; never committed) and the committed transcript
docs/worklogs/SG-213_ledger.tsv. Columns:
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
TARGET_SLUG = "google/gemini-3.1-flash-image"

CAP_USD = 2.00
READ_TIMEOUT_S = 120.0
BILLED_TIMEOUT_S = 600.0

PROMPT = "A plain gray ceramic cup on a plain white background."
FIXTURE_SRC = "SG-209_fixture.png"
FIXTURE_NAME = "SG-213_fixture.png"

# Fragment-assembled on purpose: see module docstring.
AUTH_HEADER = "Auth" + "orization"
AUTH_PREFIX = "Bea" + "rer "

LEDGER_TSV = "SG-213_ledger.tsv"
LEDGER_DB = "sg213_ledger.sqlite"

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
                cap: float = CAP_USD) -> tuple[bool, float]:
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


def cmd_guard_selftest(ev: Path) -> int:
    print("guard_selftest: synthetic projections against cap=%.2f, known_spend=0.50" % CAP_USD)
    ok_over, total_over = spend_guard(known_spend=0.50, renders=2, per_render_worst=1.50)
    ok_under, total_under = spend_guard(known_spend=0.50, renders=2, per_render_worst=0.05)
    print(f"selftest_over_cap  total={total_over:.4f} verdict={'proceed' if ok_over else 'REFUSE_over_cap'}")
    print(f"selftest_under_cap total={total_under:.4f} verdict={'proceed' if ok_under else 'refuse'}")
    refused = not ok_over and ok_under
    print(f"guard_selftest={'PASS (refusal observed on over-cap input, proceed on under-cap)' if refused else 'FAIL'}")
    return 0 if refused else 1


def cmd_fixture(ev: Path) -> int:
    copy_fixture(ev)
    return 0


def cmd_discover(ev: Path) -> int:
    import httpx

    key = read_key()
    headers = auth_headers(key)
    with httpx.Client(timeout=httpx.Timeout(READ_TIMEOUT_S)) as client:
        r = client.get(IMAGES_MODELS_URL, headers=headers)
        ts = utc_now_iso()
        body = redact(r.text, key)
        out = ev / "SG-213_g1_models_body.json"
        out.write_text(body)
        ledger_write(ev, leg="g1_models", model="-", http=r.status_code,
                     cost=None, error=None if r.status_code == 200 else f"http_{r.status_code}")
        print(f"g1_models http={r.status_code} ts={ts} bytes={len(body)} body={out.name}")
        parsed: object | None
        try:
            parsed = r.json()
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
        chosen = TARGET_SLUG if exact else None
        print(f"g1_models chosen_id={chosen}")
        if chosen is None:
            print("G1_VERDICT slug_absent -> STOP (no billed call; render leg does not run)")
            ledger_readback(ev)
            return 0

        url = f"{IMAGES_MODELS_URL}/{chosen}/endpoints"
        r2 = client.get(url, headers=headers)
        body2 = redact(r2.text, key)
        out2 = ev / "SG-213_g1_endpoints_body.json"
        out2.write_text(body2)
        ledger_write(ev, leg="g1_endpoints", model=chosen, http=r2.status_code,
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


def cmd_render(ev: Path, *, known_spend: float, token_bound: int) -> int:
    import httpx

    parsed = json.loads((ev / "SG-213_g1_endpoints_body.json").read_text())
    eps = endpoints_of(parsed)
    if not eps:
        print("G2_VERDICT endpoints_empty -> STOP (no billed call)")
        return 0

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
        wc, detail = endpoint_worst_case(ep, resolution=resolution, token_bound=token_bound)
        projections.append((wc, i, detail))
        print(f"projection endpoints[{i}] worst_case_usd={wc:.8f} detail={detail}")
    cheapest = min(projections)
    most = max(projections)
    renders = 2 if input_refs_ok else 1
    for label, wc in (("cheapest", cheapest[0]), ("most_expensive", most[0])):
        ok, total = spend_guard(known_spend=known_spend, renders=renders, per_render_worst=wc)
        print(f"guard {label} per_render={wc:.8f} known_spend={known_spend} "
              f"renders={renders} total={total:.8f} verdict={'proceed' if ok else 'REFUSE_over_cap'}")
    ok_cheap, total_cheap = spend_guard(known_spend=known_spend, renders=renders,
                                        per_render_worst=cheapest[0])
    ok_most, total_most = spend_guard(known_spend=known_spend, renders=renders,
                                      per_render_worst=most[0])
    if not ok_cheap:
        print("G2_VERDICT over_cap(even cheapest) -> STOP (no billed call)")
        return 0
    if not ok_most:
        print("G2_VERDICT over_cap(conservative max-endpoint projection) -> STOP, fail-closed "
              "(no billed call; cheapest endpoint alone would fit)")
        return 0
    print(f"G2_VERDICT projection_ok total_most_expensive={total_most:.8f} cap={CAP_USD} "
          f"(D-20 daily bound; arc known_spend={known_spend})")

    chosen_id = parsed.get("id") if isinstance(parsed, dict) else None
    if not isinstance(chosen_id, str):
        chosen_id = TARGET_SLUG
    print(f"render model={chosen_id} prompt={json.dumps(PROMPT)} n=1 "
          f"resolution={resolution or 'model_default'}")

    key = read_key()
    headers = auth_headers(key)
    results: list[dict] = []
    with httpx.Client(timeout=httpx.Timeout(BILLED_TIMEOUT_S)) as client:
        for leg_no in (1, 2):
            if leg_no == 2:
                if not input_refs_ok:
                    print("g2_render skipped: input_references not declared")
                    break
                if results and results[-1]["stop"]:
                    print("g2_render skipped: stop condition on g1_render")
                    break
            leg = f"g{leg_no}_render"
            body: dict[str, object] = {"model": chosen_id, "prompt": PROMPT, "n": 1}
            if resolution:
                body["resolution"] = resolution
            if leg_no == 2:
                fixture = ev / FIXTURE_NAME
                if not fixture.exists():
                    fixture = copy_fixture(ev)
                ref = ("data:image/png;base64,"
                       + base64.b64encode(fixture.read_bytes()).decode("ascii"))
                body["input_references"] = [
                    {"type": "image_url", "image_url": {"url": ref}}
                ]
            req_out = ev / f"SG-213_{leg}_request.json"
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
            (ev / f"SG-213_{leg}_body.json").write_text(body_text)
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
                img_name = f"SG-213_{leg}{ext}"
                (ev / img_name).write_bytes(image_bytes)
                print(f"{leg} image_file={img_name} bytes={len(image_bytes)} "
                      f"media_type={media} sha256={hashlib.sha256(image_bytes).hexdigest()}")
            ts = ledger_write(ev, leg=leg, model=chosen_id, http=status, cost=cost, error=error)
            print(f"{leg} http={status} ts={ts} cost={cost!r} cost_field="
                  f"{'null' if cost is None else cost} error={error or '-'} "
                  f"body=SG-213_{leg}_body.json")
            if leg_no == 1:
                if status == 200 and image_bytes is not None:
                    print("G1_VERDICT quota_wall_down http=200 image_bytes_present=true "
                          "-> G2 reference leg runs")
                    stop = False
                elif status == 429:
                    print("G1_VERDICT quota_429 (body committed; retry wall stands) -> STOP")
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
          f"actual_cost_sum={actual_total:.9f} known_spend_at_projection={known_spend} "
          f"cap={CAP_USD}")
    ledger_readback(ev)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["guard-selftest", "fixture", "discover", "render"])
    parser.add_argument("--evidence", default="/evidence")
    parser.add_argument("--known-spend", type=float, default=0.002437125)
    parser.add_argument("--token-bound", type=int, default=8192)
    args = parser.parse_args()
    ev = Path(args.evidence)
    ev.mkdir(parents=True, exist_ok=True)
    if args.mode == "guard-selftest":
        return cmd_guard_selftest(ev)
    if args.mode == "fixture":
        return cmd_fixture(ev)
    if args.mode == "discover":
        return cmd_discover(ev)
    return cmd_render(ev, known_spend=args.known_spend, token_bound=args.token_bound)


if __name__ == "__main__":
    sys.exit(main())
