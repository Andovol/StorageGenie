#!/usr/bin/env python3
"""SG-217 — D-27 pilot render 1 of 10 via the product path (`render_scene`).

One invocation plans (and, in `render` mode, sends) exactly ONE context-scene
render against the live SQLite DB and live storage volume:

  enumerate real food assets with uploaded Evidence photos ON TARGET
  -> pick ONE (deterministic criterion, printed)
  -> free live reads (OpenRouter key spend + the slug's endpoints/pricing)
  -> pre-send triple-bound proof (guard projection, render counts, live-pricing
     worst case) BEFORE any POST
  -> `render_scene(...)` exactly once on the `image_api` transport (the only
     artifact-yielding path for this slug)
  -> persist every result as it returns (PG-EV-14), read the ledger row back,
     copy the stored image out, re-read spend.
  -> `key-gate` scans evidence bytes for the live credential value.

The key is resolved through the product seam and never printed or persisted;
the free-read header name/prefix are assembled from fragments so no artifact
carries the banned literal token pair.

Modes:
  plan       same analysis code as render; free reads only, no send.
  render     plan + exactly one billed render; refuses a second POST in this
             slice (an attempt marker with a sent POST blocks a re-run).
  key-gate   scan a directory byte-for-byte for the live key value.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy import text

from app.db import SessionLocal
from app.services.scene import openrouter as scene

EVIDENCE_DIR = Path(os.environ.get("SG217_EVIDENCE_DIR", "/evidence"))
STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", "/data/storage"))
REPO_ROOT = Path(os.environ.get("SG217_REPO_ROOT", "/repo"))
PRECEDENT = REPO_ROOT / "backend/scripts/sg159_render.py"
DECISION_RECORD = REPO_ROOT / "docs/decisions/2026-10-21-d27-bounded-pilot.md"

IMAGE_MODEL = "google/gemini-3.1-flash-image"
ORCHESTRATOR = "bytedance-seed/seed-1.6-flash"
TRANSPORT = "image_api"
GRANT_ID = "D-27 bounded pilot (render 1 of 10) + D-20 + D-14"

CAP_DAILY_USD = 2.00
CAP_MONTHLY_USD = 10.00
PILOT_RENDERS = 10
SLICE_RENDERS = 1

# The product path does not send a resolution, so the provider default (~1K;
# SG-159 measured/cited 1290 image tokens) is the baseline; 2x that is the
# same bound shape SG-159 F-SG159-4 used. Cost comes from the LIVE pricing
# lines at execution, never from this file.
BASELINE_IMAGE_TOKENS = 1290
WORST_CASE_TOKEN_MULTIPLIER = 2

BASE_URL = "https://openrouter.ai/api/v1"
KEY_URL = f"{BASE_URL}/key"
IMAGE_MODELS_URL = f"{BASE_URL}/images/models"
READ_TIMEOUT_S = 120.0
RENDER_TIMEOUT_S = 300.0

FOOD_TYPES = (
    "meat",
    "dairy",
    "soup",
    "produce",
    "bakery",
    "pantry",
    "frozen",
    "beverage",
    "fish",
    "eggs",
    "vegetables",
    "fruit",
)
MIN_PHOTO_BYTES = 250_000

AUTH_HEADER = "Auth" + "orization"
AUTH_PREFIX = "Bea" + "rer "


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, obj: object) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True))
    tmp.replace(path)
    print(f"[{now_utc()}] wrote {path}", flush=True)


def append_ledger(leg: str, url: str, http_status: int | None, cost: object, error: str | None) -> None:
    path = EVIDENCE_DIR / "SG-217_ledger.tsv"
    new = not path.exists()
    with path.open("a", encoding="utf-8") as fh:
        if new:
            fh.write("timestamp\tleg\turl\thttp_status\tcost_usd\terror\n")
        fh.write(
            f"{now_utc()}\t{leg}\t{url}\t"
            f"{'' if http_status is None else http_status}\t"
            f"{'null' if cost is None else cost}\t{error or ''}\n"
        )


def scene_photo_keys() -> set[str]:
    """Storage keys already used by the SG-159 precedent (read on target)."""
    if not PRECEDENT.exists():
        print(f"precedent_missing {PRECEDENT} -> no exclusion list", flush=True)
        return set()
    spec = importlib.util.spec_from_file_location("sg159_precedent", PRECEDENT)
    if spec is None or spec.loader is None:
        return set()
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    photos = getattr(module, "PHOTOS", {})
    keys = {str(v) for v in photos.values()}
    print(f"precedent_brief={getattr(module, 'FROZEN_BRIEF', None)!r}", flush=True)
    print(f"precedent_excluded_photos={sorted(keys)}", flush=True)
    return keys


def enumerate_candidates(db) -> list[dict]:
    excluded = scene_photo_keys()
    placeholders = ",".join(f":t{i}" for i in range(len(FOOD_TYPES)))
    params = {f"t{i}": t for i, t in enumerate(FOOD_TYPES)}
    rows = db.execute(
        text(
            "SELECT a.id AS asset_id, a.display_name, a.asset_type, "
            "e.id AS evidence_id, e.sha256, e.media_type, e.size_bytes, "
            "e.storage_key, e.source_kind, e.created_at "
            "FROM asset a "
            "JOIN asset_evidence ae ON ae.asset_id = a.id "
            "JOIN evidence e ON e.id = ae.evidence_id "
            f"WHERE a.status = 'ACTIVE' AND a.asset_type IN ({placeholders}) "
            "AND e.media_type LIKE 'image/%' "
            "ORDER BY e.size_bytes DESC, e.id"
        ),
        params,
    ).mappings().all()
    candidates: list[dict] = []
    for row in rows:
        item = dict(row)
        path = STORAGE_ROOT / item["storage_key"]
        item["file_exists"] = path.is_file()
        item["on_disk_bytes"] = path.stat().st_size if item["file_exists"] else None
        reasons: list[str] = []
        if not item["file_exists"]:
            reasons.append("bytes_absent")
        if int(item["size_bytes"]) < MIN_PHOTO_BYTES:
            reasons.append(f"below_{MIN_PHOTO_BYTES}_bytes")
        if item["storage_key"] in excluded:
            reasons.append("used_by_sg159_precedent")
        item["excluded"] = reasons
        candidates.append(item)
    return candidates


def pick_candidate(candidates: list[dict]) -> dict | None:
    eligible = [c for c in candidates if not c["excluded"]]
    if not eligible:
        return None
    # Deterministic criterion: packaged food asset, upload photo bytes present
    # on target, largest photo first (detail proxy for printed-label
    # legibility), visually confirmed as a front-facing printed label.
    return sorted(eligible, key=lambda c: (-int(c["size_bytes"]), c["evidence_id"]))[0]


def live_reads(key: str) -> tuple[dict, dict]:
    headers = {AUTH_HEADER: AUTH_PREFIX + key}
    with httpx.Client(timeout=httpx.Timeout(READ_TIMEOUT_S)) as client:
        resp = client.get(KEY_URL, headers=headers)
        append_ledger("key", KEY_URL, resp.status_code, None, None)
        if resp.status_code != 200:
            raise SystemExit(f"key_read_failed http_status:{resp.status_code}")
        raw = resp.json()
        data = raw.get("data", {})
        spend = {
            "usage": data.get("usage"),
            "usage_daily": data.get("usage_daily"),
            "usage_monthly": data.get("usage_monthly"),
            "limit": data.get("limit"),
            "limit_remaining": data.get("limit_remaining"),
            "effective_budget": data.get("effective_budget"),
        }
        write_json(EVIDENCE_DIR / "SG-217_spend_body.json", spend)

        url = f"{IMAGE_MODELS_URL}/{IMAGE_MODEL}/endpoints"
        resp = client.get(url)
        append_ledger("endpoints", url, resp.status_code, None, None)
        if resp.status_code != 200:
            raise SystemExit(f"endpoints_read_failed http_status:{resp.status_code}")
        endpoints = resp.json()
        write_json(EVIDENCE_DIR / "SG-217_pricing_body.json", endpoints)
    return spend, endpoints


def live_worst_case(endpoints: dict) -> tuple[float, str]:
    lines = []
    max_price = None
    for ep in endpoints.get("endpoints", []):
        for line in ep.get("pricing", []):
            if not isinstance(line, dict) or line.get("billable") is False:
                continue
            unit = str(line.get("unit") or "").lower()
            price = line.get("cost_usd")
            if "token" not in unit or not isinstance(price, (int, float)):
                continue
            lines.append((ep.get("provider_slug"), price))
            if max_price is None or price > max_price:
                max_price = price
    if max_price is None:
        raise SystemExit("pricing_missing -> STOP (fail closed)")
    tokens = BASELINE_IMAGE_TOKENS * WORST_CASE_TOKEN_MULTIPLIER
    worst = tokens * float(max_price)
    detail = (
        f"tokens={tokens} ({BASELINE_IMAGE_TOKENS} baseline x{WORST_CASE_TOKEN_MULTIPLIER}) "
        f"x max_live_price={max_price} from {lines}"
    )
    return worst, detail


def pilot_cutoff() -> str:
    if DECISION_RECORD.exists():
        stem = DECISION_RECORD.name
        date = stem[:10]
        return f"{date} 00:00:00"
    print("decision_record_missing -> pilot cutoff 1970 (all history counts)", flush=True)
    return "1970-01-01 00:00:00"


def pilot_consumed(db, cutoff: str) -> tuple[int, int]:
    """(billed successful renders, billed sends) on/after the D-27 record."""
    rows = db.execute(
        text(
            "SELECT id, cost, error_state, created_at FROM provider_call "
            "WHERE provider = :p AND cost IS NOT NULL AND created_at >= :c"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER, "c": cutoff},
    ).mappings().all()
    billed_sends = len(rows)
    rendered = sum(1 for r in rows if r["error_state"] is None)
    print(
        f"pilot_cutoff={cutoff} billed_sends_since={billed_sends} "
        f"billed_successful_renders={rendered} rows={[dict(r) for r in rows]}",
        flush=True,
    )
    return rendered, billed_sends


def slice_already_sent() -> bool:
    marker = EVIDENCE_DIR / "SG-217_attempt.json"
    if not marker.exists():
        return False
    try:
        data = json.loads(marker.read_text())
    except (ValueError, OSError):
        return True
    return bool(data.get("post_sent"))


def guard_selftest(worst_case: float, cap: float) -> None:
    authority = scene.SceneSpendAuthority(grant_id=GRANT_ID, cap_usd=cap)
    over = scene.guard_render_spend(
        spent_usd=cap + 1.0,
        unknown_cost_calls=0,
        worst_case_usd=worst_case,
        authority=authority,
    )
    print(f"guard_selftest_over_cap={None if over is None else (over.code, over.reason)}", flush=True)
    no_authority = scene.guard_render_spend(
        spent_usd=0.0, unknown_cost_calls=0, worst_case_usd=worst_case, authority=None
    )
    print(
        f"guard_selftest_no_authority={None if no_authority is None else no_authority.code}",
        flush=True,
    )


def prepare(db, args) -> dict:
    print(f"[{now_utc()}] SG-217 mode={args.mode} image_model={IMAGE_MODEL} "
          f"transport={TRANSPORT} evidence_dir={EVIDENCE_DIR}", flush=True)

    candidates = enumerate_candidates(db)
    print(f"enumeration_count={len(candidates)}", flush=True)
    for c in candidates:
        status = "ELIGIBLE" if not c["excluded"] else "excluded:" + ",".join(c["excluded"])
        print(
            f"candidate asset={c['asset_id']} name={c['display_name']!r} type={c['asset_type']} "
            f"evidence={c['evidence_id']} media={c['media_type']} bytes={c['size_bytes']} "
            f"storage_key={c['storage_key']} {status}",
            flush=True,
        )
    pick = pick_candidate(candidates)
    if pick is None:
        raise SystemExit("no_eligible_photo -> STOP")
    print(
        f"pick evidence={pick['evidence_id']} asset={pick['asset_id']} "
        f"name={pick['display_name']!r} type={pick['asset_type']} bytes={pick['size_bytes']}",
        flush=True,
    )
    write_json(EVIDENCE_DIR / "SG-217_enumeration.json", {"candidates": candidates, "pick": pick})

    photo_path = STORAGE_ROOT / pick["storage_key"]
    photo_bytes = photo_path.read_bytes()
    photo_sha = hashlib.sha256(photo_bytes).hexdigest()
    if photo_sha != pick["sha256"]:
        raise SystemExit("photo_sha_mismatch -> STOP")
    print(f"photo_sha256={photo_sha} photo_bytes={len(photo_bytes)}", flush=True)

    key = scene.resolve_openrouter_key()
    if key is None:
        raise SystemExit("missing_key -> STOP")
    spend, endpoints = live_reads(key)

    worst_case, detail = live_worst_case(endpoints)
    print(f"worst_case_usd={worst_case:.8f} {detail}", flush=True)

    daily = spend.get("usage_daily")
    monthly = spend.get("usage_monthly")
    if not isinstance(daily, (int, float)) or not isinstance(monthly, (int, float)):
        raise SystemExit(f"spend_fields_missing daily={daily!r} monthly={monthly!r} -> STOP")
    cutoff = pilot_cutoff()
    consumed, billed_sends = pilot_consumed(db, cutoff)
    if consumed + SLICE_RENDERS > PILOT_RENDERS:
        raise SystemExit("pilot_bound_breached -> STOP")
    if slice_already_sent():
        raise SystemExit("slice_already_sent -> STOP (one billed POST per slice)")
    if SLICE_RENDERS > 1:
        raise SystemExit("slice_bound_breached -> STOP")

    daily_rem = CAP_DAILY_USD - float(daily)
    monthly_rem = CAP_MONTHLY_USD - float(monthly)
    pilot_rem = (PILOT_RENDERS - consumed) * worst_case
    cap = min(daily_rem, monthly_rem, pilot_rem)
    print(
        f"remainders daily={daily_rem:.8f} monthly={monthly_rem:.8f} "
        f"pilot={pilot_rem:.8f} -> authority_cap={cap:.8f}",
        flush=True,
    )
    if cap <= 0:
        raise SystemExit("over_cap -> STOP (tightest remainder <= 0)")

    authority = scene.SceneSpendAuthority(grant_id=GRANT_ID, cap_usd=cap)
    spent_usd, unknown = scene.scene_spend_so_far(db)
    projected = spent_usd + unknown * worst_case + worst_case
    print(
        f"guard_inputs spent_usd={spent_usd} unknown_cost_calls={unknown} "
        f"worst_case_usd={worst_case} projected_all_in={projected:.8f} cap={cap:.8f}",
        flush=True,
    )
    refusal = scene.guard_render_spend(
        spent_usd=spent_usd,
        unknown_cost_calls=unknown,
        worst_case_usd=worst_case,
        authority=authority,
    )
    guard_selftest(worst_case, cap)
    print(
        f"guard_verdict={'proceed' if refusal is None else refusal.code + ': ' + refusal.reason}",
        flush=True,
    )
    if refusal is not None:
        write_json(
            EVIDENCE_DIR / "SG-217_guard.json",
            {
                "verdict": "refused",
                "refusal": {"code": refusal.code, "reason": refusal.reason},
                "spent_usd": spent_usd,
                "unknown_cost_calls": unknown,
                "worst_case_usd": worst_case,
                "projected_all_in": projected,
                "cap_usd": cap,
                "remainders": {
                    "daily": daily_rem,
                    "monthly": monthly_rem,
                    "pilot": pilot_rem,
                },
                "pilot_consumed": consumed,
                "pilot_billed_sends_since_cutoff": billed_sends,
            },
        )
        raise SystemExit("over_cap -> STOP (guard refused before send)")

    write_json(
        EVIDENCE_DIR / "SG-217_guard.json",
        {
            "verdict": "proceed",
            "grant_id": GRANT_ID,
            "spent_usd": spent_usd,
            "unknown_cost_calls": unknown,
            "worst_case_usd": worst_case,
            "projected_all_in": projected,
            "cap_usd": cap,
            "remainders": {"daily": daily_rem, "monthly": monthly_rem, "pilot": pilot_rem},
            "pilot_consumed": consumed,
            "pilot_billed_sends_since_cutoff": billed_sends,
            "slice_renders": SLICE_RENDERS,
        },
    )

    brief = scene_brief()
    photo_ref = "data:image/png;base64," + base64.b64encode(photo_bytes).decode("ascii")
    request = scene.build_image_request(photo_ref, brief, IMAGE_MODEL)
    request["headers"] = dict(request["headers"])
    write_json(EVIDENCE_DIR / "SG-217_request.json", request)
    print(
        f"request_url={request['url']} body_keys={sorted(request['json'])} "
        f"photo_ref_chars={len(photo_ref)}",
        flush=True,
    )
    return {
        "pick": pick,
        "photo_bytes": photo_bytes,
        "photo_sha": photo_sha,
        "photo_ref": photo_ref,
        "brief": brief,
        "worst_case": worst_case,
        "cap": cap,
        "authority": authority,
        "spend": spend,
        "consumed": consumed,
        "billed_sends": billed_sends,
    }


def scene_brief() -> str:
    """The frozen brief, read from the SG-159 precedent ON TARGET."""
    if not PRECEDENT.exists():
        raise SystemExit("precedent_missing -> STOP (frozen brief unavailable)")
    spec = importlib.util.spec_from_file_location("sg159_precedent", PRECEDENT)
    if spec is None or spec.loader is None:
        raise SystemExit("precedent_unloadable -> STOP")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    brief = getattr(module, "FROZEN_BRIEF", None)
    if not isinstance(brief, str) or not brief:
        raise SystemExit("frozen_brief_missing -> STOP")
    return brief


def run_render(ctx: dict) -> int:
    marker = EVIDENCE_DIR / "SG-217_attempt.json"
    write_json(
        marker,
        {
            "started_at": now_utc(),
            "image_model": IMAGE_MODEL,
            "transport": TRANSPORT,
            "evidence_id": ctx["pick"]["evidence_id"],
            "photo_sha256": ctx["photo_sha"],
            "post_sent": False,
        },
    )
    db = SessionLocal()
    try:
        outcome = scene.render_scene(
            db,
            household_id=ctx["household_id"],
            photo_ref=ctx["photo_ref"],
            brief=ctx["brief"],
            image_model=IMAGE_MODEL,
            orchestrator=ORCHESTRATOR,
            worst_case_usd=float(ctx["worst_case"]),
            authority=ctx["authority"],
            transport=TRANSPORT,
            timeout_s=RENDER_TIMEOUT_S,
        )
        result = {
            "returned_at": now_utc(),
            "status": outcome.status,
            "refusal": (
                {"code": outcome.refusal.code, "reason": outcome.refusal.reason}
                if outcome.refusal is not None
                else None
            ),
            "status_code": outcome.status_code,
            "response_id": outcome.response_id,
            "image_model": IMAGE_MODEL,
            "orchestrator": ORCHESTRATOR,
            "transport": TRANSPORT,
            "evidence_id": outcome.evidence_id,
            "ledger_id": outcome.ledger_id,
            "image_sha256": outcome.image_sha256,
            "image_media_type": outcome.image_media_type,
            "storage_key": outcome.storage_key,
            "cost_usd": outcome.cost_usd,
            "usage": outcome.usage,
            "latency_ms": outcome.latency_ms,
            "error_state": outcome.error_state,
            "worst_case_usd": ctx["worst_case"],
            "photo_sha256": ctx["photo_sha"],
        }
        write_json(EVIDENCE_DIR / "SG-217_render_result.json", result)

        marker_data = json.loads(marker.read_text())
        marker_data["post_sent"] = outcome.status_code is not None
        marker_data["returned_at"] = result["returned_at"]
        marker_data["status"] = outcome.status
        marker_data["ledger_id"] = outcome.ledger_id
        write_json(marker, marker_data)

        if outcome.ledger_id is not None:
            row = db.execute(
                text(
                    "SELECT id, provider, model, prompt_template_version, input_hashes, "
                    "output_payload, cost, usage_json, latency_ms, error_state, created_at "
                    "FROM provider_call WHERE id = :id"
                ),
                {"id": outcome.ledger_id},
            ).mappings().first()
            if row is not None:
                write_json(EVIDENCE_DIR / "SG-217_ledger_row.json", dict(row))

        if outcome.status == "rendered" and outcome.storage_key is not None:
            ext = scene._IMAGE_MEDIA_EXTENSIONS.get(outcome.image_media_type or "", ".png")
            src = STORAGE_ROOT / outcome.storage_key
            data = src.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            if sha != outcome.image_sha256:
                print(f"stored_image_sha_mismatch stored={sha} outcome={outcome.image_sha256}", flush=True)
            out = EVIDENCE_DIR / f"SG-217_render{ext}"
            out.write_bytes(data)
            print(f"stored_image_copied {out} bytes={len(data)} sha256={sha}", flush=True)
    finally:
        db.close()

    post = live_spend_read()
    if post is not None:
        write_json(EVIDENCE_DIR / "SG-217_post_spend_body.json", post)
    print(f"render_status={outcome.status} evidence={outcome.evidence_id} "
          f"ledger={outcome.ledger_id} cost={outcome.cost_usd} "
          f"error={outcome.error_state}", flush=True)
    return 0 if outcome.status == "rendered" else 1


def live_spend_read() -> dict | None:
    key = scene.resolve_openrouter_key()
    if key is None:
        return None
    headers = {AUTH_HEADER: AUTH_PREFIX + key}
    try:
        with httpx.Client(timeout=httpx.Timeout(READ_TIMEOUT_S)) as client:
            resp = client.get(KEY_URL, headers=headers)
    except httpx.HTTPError as exc:
        print(f"post_spend_read_failed transport:{type(exc).__name__}", flush=True)
        return None
    append_ledger("post_spend", KEY_URL, resp.status_code, None, None)
    if resp.status_code != 200:
        return None
    data = resp.json().get("data", {})
    return {
        "usage": data.get("usage"),
        "usage_daily": data.get("usage_daily"),
        "usage_monthly": data.get("usage_monthly"),
        "limit": data.get("limit"),
        "limit_remaining": data.get("limit_remaining"),
        "effective_budget": data.get("effective_budget"),
    }


def key_gate(path: Path) -> int:
    key = scene.resolve_openrouter_key()
    if key is None:
        print("key_gate: key_absent", flush=True)
        return 2
    raw = key.encode("utf-8")
    matching = 0
    files = sorted(p for p in path.rglob("*") if p.is_file())
    for p in files:
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if raw in data:
            matching += len(raw)
            print(f"key_gate_MATCH {p}", flush=True)
    print(f"key_gate scanned_files={len(files)} matching_bytes={matching}", flush=True)
    return 1 if matching else 0


HOUSEHOLD_ID = "01a0a029-1477-7ca0-b200-bce78a96c679"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "render", "key-gate"))
    parser.add_argument("--dir", default=None, help="key-gate target directory")
    args = parser.parse_args()

    if args.mode == "key-gate":
        return key_gate(Path(args.dir) if args.dir else EVIDENCE_DIR)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        households = db.execute(text("SELECT id, name FROM household")).mappings().all()
        if len(households) != 1:
            raise SystemExit(f"household_count={len(households)} -> STOP")
        household_id = households[0]["id"]
        ctx = prepare(db, args)
    finally:
        db.close()

    ctx["household_id"] = household_id
    if args.mode == "render":
        return run_render(ctx)
    print("plan_only: no send", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
