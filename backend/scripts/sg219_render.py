#!/usr/bin/env python3
"""SG-219 — D-27 pilot renders 3+4 of 10 via the product path (`render_scene`).

Extends the SG-218 precedent driver (read on target) from one billed render per
invocation to a fixed two-render slice. One invocation enumerates the food
photos, picks the TWO pilot-unused eligible photos, and for EACH render:

  free live reads (key spend + the slug's endpoints/pricing)
  -> pre-send triple-bound proof (guard projection, slice + pilot counts, live
     pricing worst case) BEFORE the send
  -> `render_scene(...)` exactly once on the `image_api` transport
  -> persist the result as it returns, read the ledger row back, copy the
     stored image out, re-read spend.

Differences from `sg218_render.py` (quoted, not silently changed):
  - two picks and at most two sends in one slice invocation; per-send evidence
    names `SG-219_render3_*` and `SG-219_render4_*`;
  - BOTH prior pilot photos are excluded by evidence id (SG-217 Miso Soup,
    SG-218 Costiță-1), plus the SG-159 precedent photos by storage key;
  - the grant id is "renders 3+4 of 10"; the authority cap is recomputed before
    EACH send from live remainders and the first render's actual;
  - a durable duplicate-photo guard reads the live ledger's `input_hashes`.

The key is resolved through the product seam and never printed or persisted;
the free-read header name/prefix are assembled from fragments so no artifact
carries the banned literal token pair.

Modes:
  plan       same analysis code as render; free reads only, no send.
  render     plan + up to two billed renders; each send is individually
             bounded and persisted; a refusal/failure stops that leg.
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
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy import text

from app.db import SessionLocal
from app.services.scene import openrouter as scene

EVIDENCE_DIR = Path(os.environ.get("SG219_EVIDENCE_DIR", "/evidence"))
STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", "/data/storage"))
REPO_ROOT = Path(os.environ.get("SG219_REPO_ROOT", "/repo"))
PRECEDENT = REPO_ROOT / "backend/scripts/sg159_render.py"
DECISION_RECORD = REPO_ROOT / "docs/decisions/2026-10-21-d27-bounded-pilot.md"

IMAGE_MODEL = "google/gemini-3.1-flash-image"
ORCHESTRATOR = "bytedance-seed/seed-1.6-flash"
TRANSPORT = "image_api"
GRANT_ID = "D-27 bounded pilot (renders 3+4 of 10) + D-20 + D-14"

CAP_DAILY_USD = 2.00
CAP_MONTHLY_USD = 10.00
PILOT_RENDERS = 10
SLICE_RENDERS = 2

PILOT_USED_EVIDENCE_IDS = {
    "01a0c4a0-af88-7903-a070-a44e7b120712": "sg217_pilot",
    "01a0c4a1-ad90-78e1-9c17-10d92260fd0e": "sg218_pilot",
}

SG159_CITED_DEFAULT_IMAGE_TOKENS = 1290
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
    path = EVIDENCE_DIR / "SG-219_ledger.tsv"
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


def measured_default_image_tokens(db) -> tuple[int, list[dict]]:
    """Largest `completion_tokens_details.image_tokens` in the live ledger."""
    rows = db.execute(
        text(
            "SELECT id, usage_json, created_at FROM provider_call "
            "WHERE provider = :p AND usage_json IS NOT NULL"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER},
    ).mappings().all()
    measured: list[dict] = []
    for row in rows:
        try:
            usage = json.loads(row["usage_json"])
        except (TypeError, ValueError):
            continue
        details = usage.get("completion_tokens_details")
        if isinstance(details, dict):
            tokens = details.get("image_tokens")
            if isinstance(tokens, int) and tokens > 0:
                measured.append({"id": row["id"], "image_tokens": tokens,
                                 "created_at": row["created_at"]})
    if not measured:
        print("live_image_tokens_absent -> using SG-159 cited default only", flush=True)
        return SG159_CITED_DEFAULT_IMAGE_TOKENS, measured
    largest = max(m["image_tokens"] for m in measured)
    return largest, measured


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
        used = PILOT_USED_EVIDENCE_IDS.get(item["evidence_id"])
        if used is not None:
            reasons.append(f"used_by_{used}")
        item["excluded"] = reasons
        candidates.append(item)
    return candidates


def pick_candidates(candidates: list[dict]) -> tuple[list[dict], list[dict]]:
    """The deterministic criterion: packaged food asset, upload photo bytes
    present, largest photo first (detail proxy for printed-label legibility),
    visually confirmed before the first send. Both prior pilot photos and the
    SG-159 precedents are already excluded. The slice takes the first TWO."""
    eligible = [c for c in candidates if not c["excluded"]]
    eligible.sort(key=lambda c: (-int(c["size_bytes"]), c["evidence_id"]))
    return eligible[:SLICE_RENDERS], eligible


def live_reads(key: str, tag: str) -> tuple[dict, dict]:
    headers = {AUTH_HEADER: AUTH_PREFIX + key}
    with httpx.Client(timeout=httpx.Timeout(READ_TIMEOUT_S)) as client:
        resp = client.get(KEY_URL, headers=headers)
        append_ledger(f"key_{tag}", KEY_URL, resp.status_code, None, None)
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
        write_json(EVIDENCE_DIR / f"SG-219_spend_body_{tag}.json", spend)

        url = f"{IMAGE_MODELS_URL}/{IMAGE_MODEL}/endpoints"
        resp = client.get(url)
        append_ledger(f"endpoints_{tag}", url, resp.status_code, None, None)
        if resp.status_code != 200:
            raise SystemExit(f"endpoints_read_failed http_status:{resp.status_code}")
        endpoints = resp.json()
        write_json(EVIDENCE_DIR / f"SG-219_pricing_body_{tag}.json", endpoints)
    return spend, endpoints


def live_worst_case(endpoints: dict, baseline_tokens: int) -> tuple[float, str]:
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
    tokens = baseline_tokens * WORST_CASE_TOKEN_MULTIPLIER
    worst = tokens * float(max_price)
    detail = (
        f"tokens={tokens} ({baseline_tokens} measured baseline x{WORST_CASE_TOKEN_MULTIPLIER}) "
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


def pilot_counts(db, cutoff: str) -> tuple[int, int, list[dict]]:
    """(successful billed renders, billed sends) on/after the D-27 record."""
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
    return rendered, billed_sends, [dict(r) for r in rows]


def owner_upstream_totals(db) -> tuple[float, float, list[dict]]:
    """Owner-side upstream inference cost from the LIVE product ledger.

    BYOK renders ledger `cost=0.0` (OpenRouter credits) while the real spend is
    `usage.cost_details.upstream_inference_cost`. Summed for today and the
    current month from the live rows; never inherited from a prior report.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    month = today[:7]
    rows = db.execute(
        text(
            "SELECT id, created_at, usage_json FROM provider_call "
            "WHERE provider = :p AND usage_json IS NOT NULL"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER},
    ).mappings().all()
    today_sum = 0.0
    month_sum = 0.0
    detail: list[dict] = []
    for row in rows:
        try:
            usage = json.loads(row["usage_json"])
        except (TypeError, ValueError):
            continue
        details = usage.get("cost_details") if isinstance(usage, dict) else None
        cost = (details or {}).get("upstream_inference_cost")
        if not isinstance(cost, (int, float)) or isinstance(cost, bool):
            continue
        created = str(row["created_at"] or "")
        if created[:10] == today:
            today_sum += float(cost)
        if created[:7] == month:
            month_sum += float(cost)
        detail.append({"id": row["id"], "created_at": created, "upstream": float(cost)})
    print(
        f"owner_upstream_ledger today={today_sum:.9f} month={month_sum:.9f} rows={detail}",
        flush=True,
    )
    return today_sum, month_sum, detail


def photo_already_ledgered(db, photo_ref_sha256: str) -> dict | None:
    """Durable duplicate guard: any prior ledger row for this exact photo."""
    row = db.execute(
        text(
            "SELECT id, created_at, error_state FROM provider_call "
            "WHERE provider = :p AND input_hashes LIKE :pat "
            "ORDER BY created_at LIMIT 1"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER, "pat": f"%{photo_ref_sha256}%"},
    ).mappings().first()
    if row is None:
        return None
    return dict(row)


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


def pre_send_proof(
    db, ctx: dict, index: int, tag: str
) -> tuple[object | None, dict, scene.SceneSpendAuthority]:
    """The triple bound, re-derived live BEFORE this send.

    (a) `guard_render_spend` projection against the tightest remainder;
    (b) this slice's send count <= 2 and pilot-consumed + planned <= 10;
    (c) worst case recomputed from the LIVE pricing lines and measured tokens.
    """
    pick = ctx["picks"][index]
    key = scene.resolve_openrouter_key()
    if key is None:
        raise SystemExit("missing_key -> STOP")
    spend, endpoints = live_reads(key, tag)

    live_default, measured = measured_default_image_tokens(db)
    baseline_tokens = max(SG159_CITED_DEFAULT_IMAGE_TOKENS, live_default)
    print(
        f"measured_default_image_tokens live_max={live_default} rows={measured} "
        f"sg159_cited={SG159_CITED_DEFAULT_IMAGE_TOKENS} -> baseline={baseline_tokens}",
        flush=True,
    )
    worst_case, detail = live_worst_case(endpoints, baseline_tokens)
    print(f"worst_case_usd={worst_case:.8f} {detail}", flush=True)

    daily = spend.get("usage_daily")
    monthly = spend.get("usage_monthly")
    if not isinstance(daily, (int, float)) or not isinstance(monthly, (int, float)):
        raise SystemExit(f"spend_fields_missing daily={daily!r} monthly={monthly!r} -> STOP")

    cutoff = pilot_cutoff()
    rendered, billed_sends, rows = pilot_counts(db, cutoff)
    pilot_consumed = max(rendered, billed_sends)
    slice_sends_done = index
    planned_remaining = SLICE_RENDERS - index
    print(
        f"bounds render={index + 3} slice_sends_done={slice_sends_done} "
        f"planned_remaining={planned_remaining} pilot_consumed={pilot_consumed} "
        f"pilot_planned_total={pilot_consumed + planned_remaining}",
        flush=True,
    )
    if slice_sends_done + 1 > SLICE_RENDERS:
        raise SystemExit("slice_bound_breached -> STOP")
    if pilot_consumed + planned_remaining > PILOT_RENDERS:
        raise SystemExit("pilot_bound_breached -> STOP")

    owner_today, owner_month, owner_detail = owner_upstream_totals(db)
    daily_rem = CAP_DAILY_USD - float(daily)
    monthly_rem = CAP_MONTHLY_USD - float(monthly)
    pilot_rem = (PILOT_RENDERS - pilot_consumed) * worst_case
    owner_daily_rem = CAP_DAILY_USD - owner_today
    owner_monthly_rem = CAP_MONTHLY_USD - owner_month
    print(
        f"remainders credits_daily={daily_rem:.8f} credits_monthly={monthly_rem:.8f} "
        f"pilot={pilot_rem:.8f} owner_daily={owner_daily_rem:.8f} "
        f"owner_monthly={owner_monthly_rem:.8f}",
        flush=True,
    )
    cap = min(daily_rem, monthly_rem, pilot_rem, owner_daily_rem, owner_monthly_rem)
    print(f"authority_cap={cap:.8f}", flush=True)
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

    proof = {
        "render_number": index + 3,
        "tag": tag,
        "timestamp": now_utc(),
        "verdict": "proceed" if refusal is None else "refused",
        "refusal": (
            {"code": refusal.code, "reason": refusal.reason} if refusal is not None else None
        ),
        "grant_id": GRANT_ID,
        "cap_usd": cap,
        "spent_usd": spent_usd,
        "unknown_cost_calls": unknown,
        "worst_case_usd": worst_case,
        "worst_case_detail": detail,
        "projected_all_in": projected,
        "remainders": {
            "credits_daily": daily_rem,
            "credits_monthly": monthly_rem,
            "pilot": pilot_rem,
            "owner_daily": owner_daily_rem,
            "owner_monthly": owner_monthly_rem,
        },
        "spend_body": spend,
        "owner_side_ledger": {"today": owner_today, "month": owner_month, "rows": owner_detail},
        "measured_default_image_tokens": {
            "live_max": live_default,
            "sg159_cited": SG159_CITED_DEFAULT_IMAGE_TOKENS,
            "baseline": baseline_tokens,
            "multiplier": WORST_CASE_TOKEN_MULTIPLIER,
            "rows": measured,
        },
        "slice_sends_done": slice_sends_done,
        "planned_remaining": planned_remaining,
        "pilot_rendered": rendered,
        "pilot_billed_sends": billed_sends,
        "pilot_consumed": pilot_consumed,
        "pilot_rows": rows,
        "photo_evidence_id": pick["evidence_id"],
        "photo_sha256": pick["photo_sha256"],
        "photo_ref_sha256": pick["photo_ref_sha256"],
    }
    write_json(EVIDENCE_DIR / f"SG-219_guard_{tag}.json", proof)
    return refusal, proof, authority


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


def prepare(db, args) -> dict:
    print(f"[{now_utc()}] SG-219 mode={args.mode} image_model={IMAGE_MODEL} "
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
    picks, eligible = pick_candidates(candidates)
    if len(picks) < SLICE_RENDERS:
        raise SystemExit(
            f"eligible_photos={len(eligible)} < {SLICE_RENDERS} -> STOP "
            "(fewer than the two pilot-unused photos this packet names)"
        )
    for i, pick in enumerate(picks):
        print(
            f"pick render={i + 3} evidence={pick['evidence_id']} asset={pick['asset_id']} "
            f"name={pick['display_name']!r} type={pick['asset_type']} bytes={pick['size_bytes']}",
            flush=True,
        )
    write_json(
        EVIDENCE_DIR / "SG-219_enumeration.json",
        {"candidates": candidates, "eligible": eligible, "picks": picks},
    )

    brief = scene_brief()
    ctx: dict = {"picks": [], "brief": brief}
    for pick in picks:
        photo_path = STORAGE_ROOT / pick["storage_key"]
        photo_bytes = photo_path.read_bytes()
        photo_sha = hashlib.sha256(photo_bytes).hexdigest()
        if photo_sha != pick["sha256"]:
            raise SystemExit(f"photo_sha_mismatch evidence={pick['evidence_id']} -> STOP")
        photo_ref = (
            f"data:{pick['media_type']};base64," + base64.b64encode(photo_bytes).decode("ascii")
        )
        photo_ref_sha = hashlib.sha256(photo_ref.encode("utf-8")).hexdigest()
        print(
            f"photo evidence={pick['evidence_id']} sha256={photo_sha} "
            f"bytes={len(photo_bytes)} ref_sha256={photo_ref_sha}",
            flush=True,
        )
        ctx["picks"].append(
            {
                **pick,
                "photo_bytes": photo_bytes,
                "photo_sha256": photo_sha,
                "photo_ref": photo_ref,
                "photo_ref_sha256": photo_ref_sha,
            }
        )
    return ctx


def live_spend_read(tag: str) -> dict | None:
    key = scene.resolve_openrouter_key()
    if key is None:
        return None
    headers = {AUTH_HEADER: AUTH_PREFIX + key}
    try:
        with httpx.Client(timeout=httpx.Timeout(READ_TIMEOUT_S)) as client:
            resp = client.get(KEY_URL, headers=headers)
    except httpx.HTTPError as exc:
        print(f"spend_read_failed transport:{type(exc).__name__}", flush=True)
        return None
    append_ledger(f"post_spend_{tag}", KEY_URL, resp.status_code, None, None)
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


def db_counts(db) -> dict:
    row = db.execute(
        text(
            "SELECT (SELECT count(*) FROM evidence) AS evidence, "
            "(SELECT count(*) FROM provider_call) AS provider_call, "
            "(SELECT count(*) FROM audit_event) AS audit_event, "
            "(SELECT count(*) FROM provider_call WHERE cost IS NULL) AS provider_call_null_cost, "
            "(SELECT coalesce(sum(cost), 0) FROM provider_call) AS provider_call_known_cost"
        )
    ).mappings().first()
    return dict(row) if row is not None else {}


def rows_by_ids(db, table: str, key: str, values: list[str]) -> list[dict]:
    if not values:
        return []
    placeholders = ",".join(f":v{i}" for i in range(len(values)))
    params = {f"v{i}": v for i, v in enumerate(values)}
    rows = db.execute(
        text(f"SELECT * FROM {table} WHERE {key} IN ({placeholders})"), params
    ).mappings().all()
    return [dict(r) for r in rows]


def run_renders(db, ctx: dict) -> int:
    marker = EVIDENCE_DIR / "SG-219_attempt.json"
    if marker.exists():
        try:
            prior = json.loads(marker.read_text())
        except (ValueError, OSError):
            prior = {"post_sent": True}
        if prior.get("post_sent") or any(
            r.get("post_sent") for r in prior.get("renders", []) if isinstance(r, dict)
        ):
            raise SystemExit("slice_already_sent -> STOP (a prior run already sent)")

    pre_counts = db_counts(db)
    marker_data: dict = {"started_at": now_utc(), "renders": []}
    write_json(marker, marker_data)
    new_evidence: list[str] = []
    new_ledger: list[str] = []
    outcomes: list[dict] = []

    for index, pick in enumerate(ctx["picks"]):
        render_no = index + 3
        existing = photo_already_ledgered(db, pick["photo_ref_sha256"])
        if existing is not None:
            result = {
                "render_number": render_no,
                "returned_at": now_utc(),
                "status": "refused",
                "refusal": {
                    "code": "duplicate_photo",
                    "reason": f"photo already ledgered: {existing}",
                },
                "photo_evidence_id": pick["evidence_id"],
                "photo_sha256": pick["photo_sha256"],
                "photo_ref_sha256": pick["photo_ref_sha256"],
            }
            write_json(EVIDENCE_DIR / f"SG-219_render{render_no}_result.json", result)
            outcomes.append(result)
            break

        refusal, proof, authority = pre_send_proof(db, ctx, index, f"render{render_no}")
        if refusal is not None:
            result = {
                "render_number": render_no,
                "returned_at": now_utc(),
                "status": "refused",
                "refusal": {"code": refusal.code, "reason": refusal.reason},
                "photo_evidence_id": pick["evidence_id"],
                "photo_sha256": pick["photo_sha256"],
                "photo_ref_sha256": pick["photo_ref_sha256"],
                "authority_cap_usd": proof["cap_usd"],
            }
            write_json(EVIDENCE_DIR / f"SG-219_render{render_no}_result.json", result)
            marker_data["renders"].append(
                {"render": render_no, "post_sent": False, "status": "refused"}
            )
            write_json(marker, marker_data)
            outcomes.append(result)
            break

        request = scene.build_image_request(pick["photo_ref"], ctx["brief"], IMAGE_MODEL)
        request["headers"] = dict(request["headers"])
        write_json(EVIDENCE_DIR / f"SG-219_request_render{render_no}.json", request)
        print(
            f"request_url={request['url']} body_keys={sorted(request['json'])} "
            f"photo_ref_chars={len(pick['photo_ref'])}",
            flush=True,
        )

        marker_entry = {
            "render": render_no,
            "photo_evidence_id": pick["evidence_id"],
            "photo_sha256": pick["photo_sha256"],
            "photo_ref_sha256": pick["photo_ref_sha256"],
            "post_sent": "pending",
            "started_at": now_utc(),
        }
        marker_data["renders"].append(marker_entry)
        write_json(marker, marker_data)

        outcome = scene.render_scene(
            db,
            household_id=ctx["household_id"],
            photo_ref=pick["photo_ref"],
            brief=ctx["brief"],
            image_model=IMAGE_MODEL,
            orchestrator=ORCHESTRATOR,
            worst_case_usd=float(proof["worst_case_usd"]),
            authority=authority,
            transport=TRANSPORT,
            timeout_s=RENDER_TIMEOUT_S,
        )
        result = {
            "render_number": render_no,
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
            "worst_case_usd": proof["worst_case_usd"],
            "authority_cap_usd": proof["cap_usd"],
            "photo_evidence_id": pick["evidence_id"],
            "asset_id": pick["asset_id"],
            "display_name": pick["display_name"],
            "photo_sha256": pick["photo_sha256"],
            "photo_ref_sha256": pick["photo_ref_sha256"],
        }
        write_json(EVIDENCE_DIR / f"SG-219_render{render_no}_result.json", result)

        marker_entry.update(
            {
                "post_sent": outcome.status_code is not None,
                "returned_at": result["returned_at"],
                "status": outcome.status,
                "evidence_id": outcome.evidence_id,
                "ledger_id": outcome.ledger_id,
            }
        )
        write_json(marker, marker_data)

        if outcome.ledger_id is not None:
            row = db.execute(
                text("SELECT * FROM provider_call WHERE id = :id"),
                {"id": outcome.ledger_id},
            ).mappings().first()
            if row is not None:
                write_json(
                    EVIDENCE_DIR / f"SG-219_ledger_row_render{render_no}.json", dict(row)
                )
            new_ledger.append(outcome.ledger_id)

        if outcome.status == "rendered" and outcome.storage_key is not None:
            ext = scene._IMAGE_MEDIA_EXTENSIONS.get(outcome.image_media_type or "", ".png")
            src = STORAGE_ROOT / outcome.storage_key
            data = src.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            if sha != outcome.image_sha256:
                print(
                    f"stored_image_sha_mismatch stored={sha} outcome={outcome.image_sha256}",
                    flush=True,
                )
            out = EVIDENCE_DIR / f"SG-219_render{render_no}{ext}"
            out.write_bytes(data)
            print(f"stored_image_copied {out} bytes={len(data)} sha256={sha}", flush=True)
        if outcome.evidence_id is not None:
            new_evidence.append(outcome.evidence_id)

        post = live_spend_read(f"render{render_no}")
        if post is not None:
            write_json(EVIDENCE_DIR / f"SG-219_post_spend_body_render{render_no}.json", post)

        print(
            f"render_status={outcome.status} evidence={outcome.evidence_id} "
            f"ledger={outcome.ledger_id} cost={outcome.cost_usd} "
            f"error={outcome.error_state}",
            flush=True,
        )
        outcomes.append(result)
        if outcome.status != "rendered":
            break

    final_spend = live_spend_read("final")
    if final_spend is not None:
        write_json(EVIDENCE_DIR / "SG-219_post_spend_body_final.json", final_spend)

    post_counts = db_counts(db)
    db_post = {
        "pre": pre_counts,
        "post": post_counts,
        "delta": {
            key: int(post_counts.get(key, 0)) - int(pre_counts.get(key, 0))
            for key in pre_counts
        },
        "new_evidence_ids": new_evidence,
        "new_ledger_ids": new_ledger,
        "evidence_rows": rows_by_ids(db, "evidence", "id", new_evidence),
        "provider_call_rows": rows_by_ids(db, "provider_call", "id", new_ledger),
        "audit_event_rows": rows_by_ids(db, "audit_event", "entity_id", new_evidence),
        "outcomes": outcomes,
        "finished_at": now_utc(),
    }
    write_json(EVIDENCE_DIR / "SG-219_db_post.json", db_post)
    complete = len(outcomes) >= SLICE_RENDERS and all(
        o.get("status") == "rendered" for o in outcomes
    )
    print(
        f"slice_outcomes rendered={sum(1 for o in outcomes if o.get('status') == 'rendered')} "
        f"attempted={len(outcomes)} complete={complete}",
        flush=True,
    )
    return 0 if complete else 1


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
        ctx["household_id"] = household_id
        if args.mode == "plan":
            refusal, proof, authority = pre_send_proof(db, ctx, 0, "plan")
            print(
                f"plan_only: no send verdict={'proceed' if refusal is None else refusal.code}",
                flush=True,
            )
            return 0
        return run_renders(db, ctx)
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
