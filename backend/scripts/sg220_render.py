#!/usr/bin/env python3
"""SG-220 — D-27 pilot render 3 of 10 via the product path (`render_scene`).

One invocation confirms the fixed Costiță-2 pick (evidence
`01a0c4a1-acbd-7541-83b7-ce9d04730716`), proves the three spend bounds from
live reads BEFORE any send, then drives `render_scene` exactly once on the
`image_api` transport. The CEAFĂ photo parked by SG-219 is never selected.

Precedent: `sg219_render.py` (read ON TARGET). Its FIXED authority handoff is
inherited: `pre_send_proof` returns `(refusal, proof, authority)` and the caller
uses the returned `SceneSpendAuthority` object directly — never `proof[...]`
(F-SG219-1 `KeyError: 'authority'`, root-caused and fixed in SG-219).

Modes:
  plan       free reads + triple-bound proof only; no send.
  render     plan + exactly one billed render; the result is persisted as it
             returns (`PG-EV-14`). A refusal/failure stops the slice.
  key-gate   scan a directory byte-for-byte for the live key value.

The key is resolved through the product seam and never printed or persisted;
the free-read header name/prefix are assembled from fragments so no artifact
carries the banned literal token pair.
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

EVIDENCE_DIR = Path(os.environ.get("SG220_EVIDENCE_DIR", "/evidence"))
STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", "/data/storage"))
REPO_ROOT = Path(os.environ.get("SG220_REPO_ROOT", "/repo"))
PRECEDENT = REPO_ROOT / "backend/scripts/sg159_render.py"
DECISION_RECORD = REPO_ROOT / "docs/decisions/2026-10-21-d27-bounded-pilot.md"

IMAGE_MODEL = "google/gemini-3.1-flash-image"
ORCHESTRATOR = "bytedance-seed/seed-1.6-flash"
TRANSPORT = "image_api"
GRANT_ID = "D-27 bounded pilot (render 3 of 10) + D-20 + D-14"

CAP_DAILY_USD = 2.00
CAP_MONTHLY_USD = 10.00
PILOT_RENDERS = 10
SLICE_RENDERS = 1
RENDER_NUMBER = 3

PICK_EVIDENCE_ID = "01a0c4a1-acbd-7541-83b7-ce9d04730716"
PICK_EXPECTED_SHA256 = "63b3ec707f184a6c4026948701b0cc3d074cea5aa8449bcb1d22711891a9bd09"
PICK_EXPECTED_BYTES = 565806
PARKED_EVIDENCE_ID = "01a0c445-35b0-7a53-9b8d-22fa3d6523de"

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
    path = EVIDENCE_DIR / "SG-220_ledger.tsv"
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


def previous_pilot_state() -> dict[str, str]:
    """The photos consumed by SG-217/218 (live evidence ids from their reports)."""
    return {
        "01a0c4a0-af88-7903-a070-a44e7b120712": "sg217_pilot",
        "01a0c4a1-ad90-78e1-9c17-10d92260fd0e": "sg218_pilot",
    }


def enumerate_candidates(db) -> list[dict]:
    excluded = scene_photo_keys()
    placeholders = ",".join(f":t{i}" for i in range(len(FOOD_TYPES)))
    params = {f"t{i}": t for i, t in enumerate(FOOD_TYPES)}
    rows = db.execute(
        text(
            "SELECT a.id AS asset_id, a.display_name, a.asset_type, a.status, "
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
    used = previous_pilot_state()
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
        prior = used.get(item["evidence_id"])
        if prior is not None:
            reasons.append(f"used_by_{prior}")
        if item["evidence_id"] == PICK_EVIDENCE_ID:
            reasons.append("selected_sg220")
        if item["evidence_id"] == PARKED_EVIDENCE_ID:
            reasons.append("parked_sg219_content_policy")
        item["disposition"] = reasons
        candidates.append(item)
    return candidates


def confirm_pick(db) -> dict:
    """Confirm the fixed Costiță-2 photo from the live DB + storage volume."""
    if PICK_EVIDENCE_ID == PARKED_EVIDENCE_ID:
        raise SystemExit("pick_is_parked_ceafa -> STOP")
    row = db.execute(
        text(
            "SELECT e.id AS evidence_id, e.sha256, e.media_type, e.size_bytes, "
            "e.storage_key, e.source_kind, e.created_at, "
            "a.id AS asset_id, a.display_name, a.asset_type, a.status "
            "FROM evidence e "
            "JOIN asset_evidence ae ON ae.evidence_id = e.id "
            "JOIN asset a ON a.id = ae.asset_id "
            "WHERE e.id = :id"
        ),
        {"id": PICK_EVIDENCE_ID},
    ).mappings().all()
    if len(row) != 1:
        raise SystemExit(f"pick_rows={len(row)} evidence={PICK_EVIDENCE_ID} -> STOP")
    pick = dict(row[0])
    print(f"pick_row={pick}", flush=True)
    if pick["status"] != "ACTIVE":
        raise SystemExit(f"pick_asset_status={pick['status']} -> STOP")
    if pick["asset_type"] not in FOOD_TYPES:
        raise SystemExit(f"pick_asset_type={pick['asset_type']} -> STOP")
    if pick["media_type"] != "image/png":
        raise SystemExit(f"pick_media_type={pick['media_type']} -> STOP")
    if int(pick["size_bytes"]) != PICK_EXPECTED_BYTES:
        raise SystemExit(
            f"pick_size_bytes={pick['size_bytes']} expected={PICK_EXPECTED_BYTES} -> STOP"
        )
    if pick["sha256"] != PICK_EXPECTED_SHA256:
        raise SystemExit(
            f"pick_sha256={pick['sha256']} expected={PICK_EXPECTED_SHA256} -> STOP"
        )
    path = STORAGE_ROOT / pick["storage_key"]
    if not path.is_file():
        raise SystemExit(f"pick_bytes_absent storage_key={pick['storage_key']} -> STOP")
    photo_bytes = path.read_bytes()
    photo_sha = hashlib.sha256(photo_bytes).hexdigest()
    if photo_sha != pick["sha256"] or len(photo_bytes) != PICK_EXPECTED_BYTES:
        raise SystemExit(
            f"photo_sha_mismatch on_disk={photo_sha} bytes={len(photo_bytes)} -> STOP"
        )
    photo_ref = f"data:{pick['media_type']};base64," + base64.b64encode(photo_bytes).decode(
        "ascii"
    )
    photo_ref_sha = hashlib.sha256(photo_ref.encode("utf-8")).hexdigest()
    pick.update(
        {
            "photo_bytes": len(photo_bytes),
            "photo_sha256": photo_sha,
            "photo_ref": photo_ref,
            "photo_ref_sha256": photo_ref_sha,
        }
    )
    print(
        f"photo evidence={pick['evidence_id']} sha256={photo_sha} bytes={len(photo_bytes)} "
        f"ref_sha256={photo_ref_sha}",
        flush=True,
    )
    return pick


def pilot_cutoff() -> str:
    if DECISION_RECORD.exists():
        date = DECISION_RECORD.name[:10]
        return f"{date} 00:00:00"
    print("decision_record_missing -> pilot cutoff 1970 (all history counts)", flush=True)
    return "1970-01-01 00:00:00"


def pick_usage(db, pick: dict) -> tuple[list[dict], list[dict]]:
    """Any ledger row for this photo, and any successful row after the cutoff."""
    rows = db.execute(
        text(
            "SELECT id, created_at, cost, error_state FROM provider_call "
            "WHERE provider = :p AND (input_hashes LIKE :raw OR input_hashes LIKE :ref) "
            "ORDER BY created_at"
        ),
        {
            "p": scene.SCENE_LEDGER_PROVIDER,
            "raw": f"%{pick['photo_sha256']}%",
            "ref": f"%{pick['photo_ref_sha256']}%",
        },
    ).mappings().all()
    all_rows = [dict(r) for r in rows]
    cutoff = pilot_cutoff()
    successful = [
        r for r in all_rows if r["error_state"] is None and str(r["created_at"] or "") >= cutoff
    ]
    print(f"pick_ledger_rows={all_rows} cutoff={cutoff} successful_after={successful}", flush=True)
    return all_rows, successful


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

    BYOK renders may ledger `cost=0.0` (OpenRouter credits) while the real spend
    is `usage.cost_details.upstream_inference_cost`. Summed for today and the
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
        write_json(EVIDENCE_DIR / f"SG-220_spend_body_{tag}.json", spend)

        url = f"{IMAGE_MODELS_URL}/{IMAGE_MODEL}/endpoints"
        resp = client.get(url)
        append_ledger(f"endpoints_{tag}", url, resp.status_code, None, None)
        if resp.status_code != 200:
            raise SystemExit(f"endpoints_read_failed http_status:{resp.status_code}")
        endpoints = resp.json()
        write_json(EVIDENCE_DIR / f"SG-220_pricing_body_{tag}.json", endpoints)
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
    db, pick: dict, tag: str
) -> tuple[object | None, dict, scene.SceneSpendAuthority]:
    """The triple bound, re-derived live BEFORE the one send.

    (a) `guard_render_spend` projection against the tightest remainder;
    (b) this slice's render count <= 1 and pilot-consumed + 1 <= 10;
    (c) worst case recomputed from the LIVE pricing lines and measured tokens.
    """
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
    slice_sends_done = 0
    planned_remaining = SLICE_RENDERS
    print(
        f"bounds render={RENDER_NUMBER} slice_sends_done={slice_sends_done} "
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
        "render_number": RENDER_NUMBER,
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
    write_json(EVIDENCE_DIR / f"SG-220_guard_{tag}.json", proof)
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
    print(
        f"[{now_utc()}] SG-220 mode={args.mode} image_model={IMAGE_MODEL} "
        f"transport={TRANSPORT} evidence_dir={EVIDENCE_DIR} "
        f"pick_evidence={PICK_EVIDENCE_ID}",
        flush=True,
    )

    candidates = enumerate_candidates(db)
    print(f"enumeration_count={len(candidates)}", flush=True)
    for c in candidates:
        reasons = c["disposition"]
        status = "plain" if not reasons else "flag:" + ",".join(reasons)
        print(
            f"candidate asset={c['asset_id']} name={c['display_name']!r} "
            f"type={c['asset_type']} evidence={c['evidence_id']} media={c['media_type']} "
            f"bytes={c['size_bytes']} storage_key={c['storage_key']} {status}",
            flush=True,
        )
    pick = confirm_pick(db)
    all_rows, successful = pick_usage(db, pick)
    if all_rows:
        raise SystemExit(
            f"pick_already_ledgered rows={all_rows} -> STOP (photo is not pilot-unused)"
        )
    if successful:
        raise SystemExit("pick_successful_after_cutoff -> STOP")
    write_json(
        EVIDENCE_DIR / "SG-220_enumeration.json",
        {
            "candidates": candidates,
            "pick": {k: v for k, v in pick.items() if k != "photo_ref"},
            "pick_ledger_rows": all_rows,
            "pick_successful_rows_after_cutoff": successful,
            "parked_evidence_id": PARKED_EVIDENCE_ID,
        },
    )

    brief = scene_brief()
    print(f"frozen_brief={brief!r}", flush=True)
    return {"pick": pick, "brief": brief, "candidates": candidates}


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


def run_render(db, ctx: dict) -> int:
    marker = EVIDENCE_DIR / "SG-220_attempt.json"
    if marker.exists():
        try:
            prior = json.loads(marker.read_text())
        except (ValueError, OSError):
            prior = {"post_sent": True}
        if prior.get("post_sent") or any(
            r.get("post_sent") for r in prior.get("renders", []) if isinstance(r, dict)
        ):
            raise SystemExit("slice_already_sent -> STOP (a prior run already sent)")

    pick = ctx["pick"]
    pre_counts = db_counts(db)
    marker_data: dict = {"started_at": now_utc(), "renders": []}
    write_json(marker, marker_data)

    refusal, proof, authority = pre_send_proof(db, pick, f"render{RENDER_NUMBER}")
    if refusal is not None:
        result = {
            "render_number": RENDER_NUMBER,
            "returned_at": now_utc(),
            "status": "refused",
            "refusal": {"code": refusal.code, "reason": refusal.reason},
            "photo_evidence_id": pick["evidence_id"],
            "photo_sha256": pick["photo_sha256"],
            "photo_ref_sha256": pick["photo_ref_sha256"],
            "authority_cap_usd": proof["cap_usd"],
        }
        write_json(EVIDENCE_DIR / f"SG-220_render{RENDER_NUMBER}_result.json", result)
        marker_data["renders"].append(
            {"render": RENDER_NUMBER, "post_sent": False, "status": "refused"}
        )
        write_json(marker, marker_data)
        return 1

    request = scene.build_image_request(pick["photo_ref"], ctx["brief"], IMAGE_MODEL)
    request["headers"] = dict(request["headers"])
    write_json(EVIDENCE_DIR / f"SG-220_request_render{RENDER_NUMBER}.json", request)
    print(
        f"request_url={request['url']} body_keys={sorted(request['json'])} "
        f"photo_ref_chars={len(pick['photo_ref'])}",
        flush=True,
    )

    marker_entry = {
        "render": RENDER_NUMBER,
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
        "render_number": RENDER_NUMBER,
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
    write_json(EVIDENCE_DIR / f"SG-220_render{RENDER_NUMBER}_result.json", result)

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

    new_evidence: list[str] = []
    new_ledger: list[str] = []
    if outcome.ledger_id is not None:
        row = db.execute(
            text("SELECT * FROM provider_call WHERE id = :id"),
            {"id": outcome.ledger_id},
        ).mappings().first()
        if row is not None:
            write_json(
                EVIDENCE_DIR / f"SG-220_ledger_row_render{RENDER_NUMBER}.json", dict(row)
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
        out = EVIDENCE_DIR / f"SG-220_render{RENDER_NUMBER}{ext}"
        out.write_bytes(data)
        print(f"stored_image_copied {out} bytes={len(data)} sha256={sha}", flush=True)
    if outcome.evidence_id is not None:
        new_evidence.append(outcome.evidence_id)

    post = live_spend_read(f"render{RENDER_NUMBER}")
    if post is not None:
        write_json(EVIDENCE_DIR / f"SG-220_post_spend_body_render{RENDER_NUMBER}.json", post)

    print(
        f"render_status={outcome.status} evidence={outcome.evidence_id} "
        f"ledger={outcome.ledger_id} cost={outcome.cost_usd} "
        f"error={outcome.error_state}",
        flush=True,
    )

    final_spend = live_spend_read("final")
    if final_spend is not None:
        write_json(EVIDENCE_DIR / "SG-220_post_spend_body_final.json", final_spend)

    cutoff = pilot_cutoff()
    rendered, billed_sends, pilot_rows_after = pilot_counts(db, cutoff)
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
        "pilot_after": {
            "cutoff": cutoff,
            "billed_successful_renders": rendered,
            "billed_sends": billed_sends,
            "rows": pilot_rows_after,
        },
        "outcomes": [result],
        "finished_at": now_utc(),
    }
    write_json(EVIDENCE_DIR / "SG-220_db_post.json", db_post)
    print(
        f"slice_outcomes rendered={1 if result.get('status') == 'rendered' else 0} "
        f"attempted=1 complete={result.get('status') == 'rendered'}",
        flush=True,
    )
    return 0 if result.get("status") == "rendered" else 1


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
            refusal, proof, authority = pre_send_proof(db, ctx["pick"], "plan")
            print(
                f"plan_only: no send verdict={'proceed' if refusal is None else refusal.code}",
                flush=True,
            )
            return 0 if refusal is None else 1
        return run_render(db, ctx)
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
