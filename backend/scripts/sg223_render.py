#!/usr/bin/env python3
"""SG-223 — D-28: unlink the wrong Costiță render + two billed renders.

Modes (one invocation = one step):
  verify    live reads only: link pair, counts, source photos, pilot state.
  unlink    verify + DELETE exactly one `asset_evidence` row (SG-218 wrong link).
  render    Costiță-1 re-render (frozen scene brief) then Miso cutout probe;
            a refusal/failure stops that leg and ships what rendered (PB-6).
  link      review-before-link: INSERT one `asset_evidence` row for a faithful
            render (never called automatically; the Coder reviews first).
  key-gate  scan a directory byte-for-byte for the live key value.

The driver is lane-run tooling, not served code. It runs inside the production
image against the live SQLite bind and storage volume. No UPDATE; the only
DELETE is the one named pair (count-checked both directions before writing).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy import text

from app.db import SessionLocal
from app.services.scene import openrouter as scene

EVIDENCE_DIR = Path(os.environ.get("SG223_EVIDENCE_DIR", "/evidence"))
STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", "/data/storage"))
REPO_ROOT = Path(os.environ.get("SG223_REPO_ROOT", "/repo"))
PRECEDENT = REPO_ROOT / "backend/scripts/sg159_render.py"
DECISION_RECORD = REPO_ROOT / "docs/decisions/2026-10-21-d27-bounded-pilot.md"

IMAGE_MODEL = "google/gemini-3.1-flash-image"
ORCHESTRATOR = "bytedance-seed/seed-1.6-flash"
TRANSPORT = "image_api"
GRANT_ID = "D-28 (renders 4+5 of 10) + D-20 + D-14"

CAP_DAILY_USD = 2.00
CAP_MONTHLY_USD = 10.00
PILOT_RENDERS = 10
SLICE_RENDERS = 2
FIRST_RENDER_NUMBER = 4

COSTITA_ASSET_ID = "01a0c4ab-3765-7e10-8d0a-705390c6560d"
MISO_ASSET_ID = "01a0c4aa-8b62-7360-b11e-a476ddaea0f6"
WRONG_RENDER_EVIDENCE_ID = "01a15fdc-f5b6-7f31-9008-2f8d89be8813"
SG220_RENDER_EVIDENCE_ID = "01a15ff5-11e3-7243-99a6-9eeb9bbe1e09"
EXPECTED_LINKS_BEFORE = 17
EXPECTED_LINKS_AFTER_UNLINK = 16

COSTITA_PHOTO = {
    "leg": "costita",
    "label": "Costiță-1",
    "evidence_id": "01a0c4a1-ad90-78e1-9c17-10d92260fd0e",
    "asset_id": COSTITA_ASSET_ID,
    "sha256": "f9d71a40b1c5ac455fe568576c77b042abc4755c65dce99a9dfcb25f64a8f367",
    "size_bytes": 1259505,
    "media_type": "image/png",
    "brief": None,  # frozen scene brief, read from the precedent on target
}
MISO_PHOTO = {
    "leg": "miso",
    "label": "Miso Soup cutout",
    "evidence_id": "01a0c4a0-af88-7903-a070-a44e7b120712",
    "asset_id": MISO_ASSET_ID,
    "sha256": "71901cac327fdd76926e36aa2a7889b2b17fb4e2619ca92d97f86d53aac0de63",
    "size_bytes": 1280694,
    "media_type": "image/png",
    "brief": (
        "Isolate this packaged product on a plain seamless white background, "
        "front-facing, even studio lighting; the full package with its label and "
        "printed text exactly as photographed; no props, no scene, no shadow, no hands."
    ),
}
PACKET_FROZEN_BRIEF = (
    "Restage this packaged product on a clean kitchen counter in warm natural "
    "daylight; keep the package, its label and its printed text exactly as photographed."
)

SG159_CITED_DEFAULT_IMAGE_TOKENS = 1290
WORST_CASE_TOKEN_MULTIPLIER = 2

BASE_URL = "https://openrouter.ai/api/v1"
KEY_URL = f"{BASE_URL}/key"
IMAGE_MODELS_URL = f"{BASE_URL}/images/models"
READ_TIMEOUT_S = 120.0
RENDER_TIMEOUT_S = 300.0

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
    path = EVIDENCE_DIR / "SG-223_ledger.tsv"
    new = not path.exists()
    with path.open("a", encoding="utf-8") as fh:
        if new:
            fh.write("timestamp\tleg\turl\thttp_status\tcost_usd\terror\n")
        fh.write(
            f"{now_utc()}\t{leg}\t{url}\t"
            f"{'' if http_status is None else http_status}\t"
            f"{'null' if cost is None else cost}\t{error or ''}\n"
        )


def table_counts(db) -> dict:
    row = db.execute(
        text(
            "SELECT (SELECT count(*) FROM evidence) AS evidence, "
            "(SELECT count(*) FROM provider_call) AS provider_call, "
            "(SELECT count(*) FROM audit_event) AS audit_event, "
            "(SELECT count(*) FROM asset_evidence) AS asset_evidence, "
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


def asset_links(db, asset_id: str) -> list[dict]:
    rows = db.execute(
        text(
            "SELECT ae.asset_id, ae.evidence_id, e.source_kind, e.sha256, "
            "e.media_type, e.size_bytes, e.original_filename "
            "FROM asset_evidence ae JOIN evidence e ON e.id = ae.evidence_id "
            "WHERE ae.asset_id = :a ORDER BY ae.created_at, ae.evidence_id"
        ),
        {"a": asset_id},
    ).mappings().all()
    return [dict(r) for r in rows]


def link_counts(db) -> dict:
    total = db.execute(text("SELECT count(*) FROM asset_evidence")).scalar_one()
    wrong_pair = db.execute(
        text(
            "SELECT count(*) FROM asset_evidence "
            "WHERE asset_id = :a AND evidence_id = :e"
        ),
        {"a": COSTITA_ASSET_ID, "e": WRONG_RENDER_EVIDENCE_ID},
    ).scalar_one()
    wrong_any = db.execute(
        text("SELECT count(*) FROM asset_evidence WHERE evidence_id = :e"),
        {"e": WRONG_RENDER_EVIDENCE_ID},
    ).scalar_one()
    sg220_any = db.execute(
        text("SELECT count(*) FROM asset_evidence WHERE evidence_id = :e"),
        {"e": SG220_RENDER_EVIDENCE_ID},
    ).scalar_one()
    return {
        "total": int(total),
        "wrong_pair_rows": int(wrong_pair),
        "wrong_render_link_rows": int(wrong_any),
        "sg220_render_link_rows": int(sg220_any),
    }


def scene_brief() -> str:
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
    if brief.strip() != PACKET_FROZEN_BRIEF.strip():
        raise SystemExit(
            f"frozen_brief_differs_from_packet on_target={brief!r} -> STOP"
        )
    return brief


def confirm_photo(db, spec: dict) -> dict:
    rows = db.execute(
        text(
            "SELECT e.id AS evidence_id, e.sha256, e.media_type, e.size_bytes, "
            "e.storage_key, e.source_kind, e.created_at, "
            "a.id AS asset_id, a.display_name, a.asset_type, a.status "
            "FROM evidence e "
            "JOIN asset_evidence ae ON ae.evidence_id = e.id "
            "JOIN asset a ON a.id = ae.asset_id "
            "WHERE e.id = :id"
        ),
        {"id": spec["evidence_id"]},
    ).mappings().all()
    if len(rows) != 1:
        raise SystemExit(
            f"photo_rows={len(rows)} evidence={spec['evidence_id']} -> STOP"
        )
    pick = dict(rows[0])
    if pick["asset_id"] != spec["asset_id"] or pick["asset_type"] not in ("meat", "soup"):
        raise SystemExit(f"photo_asset_mismatch {pick} -> STOP")
    if pick["status"] != "ACTIVE":
        raise SystemExit(f"photo_asset_status={pick['status']} -> STOP")
    if pick["media_type"] != spec["media_type"]:
        raise SystemExit(f"photo_media_type={pick['media_type']} -> STOP")
    if int(pick["size_bytes"]) != spec["size_bytes"] or pick["sha256"] != spec["sha256"]:
        raise SystemExit(
            f"photo_identity_mismatch size={pick['size_bytes']} sha={pick['sha256']} -> STOP"
        )
    path = STORAGE_ROOT / pick["storage_key"]
    if not path.is_file():
        raise SystemExit(f"photo_bytes_absent {pick['storage_key']} -> STOP")
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != spec["sha256"] or len(data) != spec["size_bytes"]:
        raise SystemExit(
            f"photo_on_disk_mismatch sha={sha} bytes={len(data)} -> STOP"
        )
    out = EVIDENCE_DIR / f"SG-223_source_{spec['leg']}.png"
    out.write_bytes(data)
    photo_ref = "data:%s;base64,%s" % (
        pick["media_type"],
        base64.b64encode(data).decode("ascii"),
    )
    pick.update(
        {
            "leg": spec["leg"],
            "label": spec["label"],
            "brief": spec["brief"],
            "photo_bytes": len(data),
            "photo_sha256": sha,
            "photo_ref": photo_ref,
            "photo_ref_sha256": hashlib.sha256(photo_ref.encode("utf-8")).hexdigest(),
            "source_copy": str(out),
        }
    )
    print(
        f"photo leg={spec['leg']} evidence={pick['evidence_id']} "
        f"asset={pick['asset_id']} sha256={sha} bytes={len(data)} "
        f"ref_sha256={pick['photo_ref_sha256']}",
        flush=True,
    )
    return pick


def measured_default_image_tokens(db) -> tuple[int, list[dict]]:
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
                measured.append(
                    {"id": row["id"], "image_tokens": tokens, "created_at": row["created_at"]}
                )
    if not measured:
        print("live_image_tokens_absent -> using SG-159 cited default only", flush=True)
        return SG159_CITED_DEFAULT_IMAGE_TOKENS, measured
    return max(m["image_tokens"] for m in measured), measured


def pilot_cutoff() -> str:
    if DECISION_RECORD.exists():
        return f"{DECISION_RECORD.name[:10]} 00:00:00"
    print("decision_record_missing -> pilot cutoff 1970 (all history counts)", flush=True)
    return "1970-01-01 00:00:00"


def pilot_counts(db, cutoff: str) -> tuple[int, int, list[dict]]:
    rows = db.execute(
        text(
            "SELECT id, cost, error_state, created_at FROM provider_call "
            "WHERE provider = :p AND cost IS NOT NULL AND created_at >= :c"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER, "c": cutoff},
    ).mappings().all()
    billed_sends = len(rows)
    rendered = sum(1 for r in rows if r["error_state"] is None)
    return rendered, billed_sends, [dict(r) for r in rows]


def owner_upstream_totals(db) -> tuple[float, float, list[dict]]:
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
        write_json(EVIDENCE_DIR / f"SG-223_spend_body_{tag}.json", spend)

        url = f"{IMAGE_MODELS_URL}/{IMAGE_MODEL}/endpoints"
        resp = client.get(url)
        append_ledger(f"endpoints_{tag}", url, resp.status_code, None, None)
        if resp.status_code != 200:
            raise SystemExit(f"endpoints_read_failed http_status:{resp.status_code}")
        endpoints = resp.json()
        write_json(EVIDENCE_DIR / f"SG-223_pricing_body_{tag}.json", endpoints)
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
        f"tokens={tokens} ({baseline_tokens} measured baseline x"
        f"{WORST_CASE_TOKEN_MULTIPLIER}) x max_live_price={max_price} from {lines}"
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
    print(
        f"guard_selftest_over_cap={None if over is None else (over.code, over.reason)}",
        flush=True,
    )
    no_authority = scene.guard_render_spend(
        spent_usd=0.0, unknown_cost_calls=0, worst_case_usd=worst_case, authority=None
    )
    print(
        f"guard_selftest_no_authority="
        f"{None if no_authority is None else no_authority.code}",
        flush=True,
    )


def pre_send_proof(
    db, leg: dict, index: int, tag: str
) -> tuple[object | None, dict, scene.SceneSpendAuthority | None]:
    """Triple bound re-derived live BEFORE this send (a/b/c in the packet)."""
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
    render_number = FIRST_RENDER_NUMBER + index
    print(
        f"bounds leg={leg['leg']} render={render_number} "
        f"slice_sends_done={slice_sends_done} planned_remaining={planned_remaining} "
        f"pilot_consumed={pilot_consumed} "
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

    spent_usd, unknown = scene.scene_spend_so_far(db)
    projected = spent_usd + unknown * worst_case + worst_case
    print(
        f"guard_inputs spent_usd={spent_usd} unknown_cost_calls={unknown} "
        f"worst_case_usd={worst_case} projected_all_in={projected:.8f} cap={cap:.8f}",
        flush=True,
    )
    if cap <= 0:
        refusal: object = scene.SceneRefusal(
            code="over_cap", reason="over_cap: tightest remainder <= 0"
        )
        authority = None
    else:
        authority = scene.SceneSpendAuthority(grant_id=GRANT_ID, cap_usd=cap)
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
        "leg": leg["leg"],
        "render_number": render_number,
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
        "photo_evidence_id": leg["evidence_id"],
        "photo_sha256": leg["photo_sha256"],
        "photo_ref_sha256": leg["photo_ref_sha256"],
        "brief": leg["brief"],
    }
    write_json(EVIDENCE_DIR / f"SG-223_guard_{leg['leg']}.json", proof)
    return refusal, proof, authority


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


def verify_live(db, expect_total: int | None) -> dict:
    households = db.execute(text("SELECT id, name FROM household")).mappings().all()
    if len(households) != 1:
        raise SystemExit(f"household_count={len(households)} -> STOP")
    counts = table_counts(db)
    links = link_counts(db)
    print(f"table_counts={counts}", flush=True)
    print(f"link_counts={links}", flush=True)
    if expect_total is not None and links["total"] != expect_total:
        raise SystemExit(
            f"asset_evidence_count={links['total']} expected={expect_total} -> STOP"
        )

    costita_photo = confirm_photo(db, COSTITA_PHOTO)
    miso_photo = confirm_photo(db, MISO_PHOTO)
    brief = scene_brief()
    costita_photo["brief"] = brief
    print(f"frozen_brief={brief!r}", flush=True)
    print(f"cutout_brief={MISO_PHOTO['brief']!r}", flush=True)

    cutoff = pilot_cutoff()
    rendered, billed_sends, pilot_rows = pilot_counts(db, cutoff)
    spent_usd, unknown = scene.scene_spend_so_far(db)
    owner_today, owner_month, owner_detail = owner_upstream_totals(db)
    print(
        f"pilot_cutoff={cutoff} rendered={rendered} billed_sends={billed_sends} "
        f"rows={pilot_rows}",
        flush=True,
    )
    print(
        f"scene_spend known={spent_usd} unknown={unknown} "
        f"owner_today={owner_today:.9f} owner_month={owner_month:.9f}",
        flush=True,
    )

    report = {
        "timestamp": now_utc(),
        "household": dict(households[0]),
        "table_counts": counts,
        "link_counts": links,
        "costita_links": asset_links(db, COSTITA_ASSET_ID),
        "miso_links": asset_links(db, MISO_ASSET_ID),
        "photos": {
            "costita": {k: v for k, v in costita_photo.items() if k != "photo_ref"},
            "miso": {k: v for k, v in miso_photo.items() if k != "photo_ref"},
        },
        "frozen_brief": brief,
        "cutout_brief": MISO_PHOTO["brief"],
        "pilot": {
            "cutoff": cutoff,
            "rendered": rendered,
            "billed_sends": billed_sends,
            "rows": pilot_rows,
        },
        "spend": {
            "known": spent_usd,
            "unknown_cost_calls": unknown,
            "owner_today": owner_today,
            "owner_month": owner_month,
            "owner_rows": owner_detail,
        },
        "scene_module": {
            "file": str(getattr(scene, "__file__", None)),
            "sha256": (
                hashlib.sha256(Path(scene.__file__).read_bytes()).hexdigest()
                if getattr(scene, "__file__", None)
                else None
            ),
        },
    }
    write_json(EVIDENCE_DIR / "SG-223_verify.json", report)
    return {"report": report, "photos": {"costita": costita_photo, "miso": miso_photo}}


def unlink_wrong_render(db) -> int:
    verify_live(db, EXPECTED_LINKS_BEFORE)
    links = link_counts(db)
    if links["wrong_pair_rows"] != 1 or links["wrong_render_link_rows"] != 1:
        raise SystemExit(
            f"wrong_link_shape pair={links['wrong_pair_rows']} "
            f"any={links['wrong_render_link_rows']} -> STOP"
        )
    before = table_counts(db)
    before_links = asset_links(db, COSTITA_ASSET_ID)
    result = db.execute(
        text(
            "DELETE FROM asset_evidence WHERE asset_id = :asset AND evidence_id = :evidence"
        ),
        {"asset": COSTITA_ASSET_ID, "evidence": WRONG_RENDER_EVIDENCE_ID},
    )
    deleted = result.rowcount
    if deleted != 1:
        db.rollback()
        raise SystemExit(f"delete_rowcount={deleted} -> STOP (rolled back)")
    db.commit()
    after = table_counts(db)
    after_links = link_counts(db)
    after_asset_links = asset_links(db, COSTITA_ASSET_ID)
    print(f"delete_rowcount={deleted} before={before} after={after}", flush=True)
    print(f"link_counts_after={after_links}", flush=True)
    if after["asset_evidence"] != EXPECTED_LINKS_AFTER_UNLINK:
        raise SystemExit(
            f"asset_evidence_after={after['asset_evidence']} "
            f"expected={EXPECTED_LINKS_AFTER_UNLINK} -> STOP"
        )
    if after_links["wrong_pair_rows"] != 0 or after_links["wrong_render_link_rows"] != 0:
        raise SystemExit("wrong_link_still_present -> STOP")
    write_json(
        EVIDENCE_DIR / "SG-223_unlink.json",
        {
            "timestamp": now_utc(),
            "deleted_pair": {
                "asset_id": COSTITA_ASSET_ID,
                "evidence_id": WRONG_RENDER_EVIDENCE_ID,
            },
            "delete_rowcount": deleted,
            "before_table_counts": before,
            "after_table_counts": after,
            "before_costita_links": before_links,
            "after_costita_links": after_asset_links,
            "after_link_counts": after_links,
        },
    )
    return 0


def run_render(db, ctx: dict) -> int:  # noqa: C901
    marker = EVIDENCE_DIR / "SG-223_attempt.json"
    if marker.exists():
        try:
            prior = json.loads(marker.read_text())
        except (ValueError, OSError):
            prior = {"post_sent": True}
        if prior.get("post_sent") or any(
            r.get("post_sent") for r in prior.get("renders", []) if isinstance(r, dict)
        ):
            raise SystemExit("slice_already_sent -> STOP (a prior run already sent)")

    links = link_counts(db)
    if links["total"] != EXPECTED_LINKS_AFTER_UNLINK or links["wrong_pair_rows"] != 0:
        raise SystemExit(
            f"unlink_state_not_verified links={links} -> STOP "
            "(renders never run against an unverified link state)"
        )

    pre_counts = table_counts(db)
    marker_data: dict = {"started_at": now_utc(), "renders": []}
    write_json(marker, marker_data)
    outcomes: list[dict] = []

    for index, leg in enumerate((ctx["photos"]["costita"], ctx["photos"]["miso"])):
        if outcomes and outcomes[-1]["status"] != "rendered":
            print("prior_leg_not_rendered -> second leg not attempted", flush=True)
            break
        tag = leg["leg"]
        refusal, proof, authority = pre_send_proof(db, leg, index, tag)
        render_number = proof["render_number"]
        if refusal is not None:
            result = {
                "leg": tag,
                "render_number": render_number,
                "returned_at": now_utc(),
                "status": "refused",
                "refusal": {"code": refusal.code, "reason": refusal.reason},
                "photo_evidence_id": leg["evidence_id"],
                "photo_sha256": leg["photo_sha256"],
                "photo_ref_sha256": leg["photo_ref_sha256"],
                "authority_cap_usd": proof["cap_usd"],
                "projected_all_in": proof["projected_all_in"],
            }
            write_json(EVIDENCE_DIR / f"SG-223_render_{tag}_result.json", result)
            marker_data["renders"].append(
                {"leg": tag, "post_sent": False, "status": "refused"}
            )
            write_json(marker, marker_data)
            outcomes.append(result)
            print(f"leg={tag} refused {refusal.code}: {refusal.reason}", flush=True)
            break

        request = scene.build_image_request(leg["photo_ref"], leg["brief"], IMAGE_MODEL)
        request["headers"] = dict(request["headers"])
        write_json(EVIDENCE_DIR / f"SG-223_request_{tag}.json", request)
        print(
            f"leg={tag} request_url={request['url']} body_keys={sorted(request['json'])} "
            f"photo_ref_chars={len(leg['photo_ref'])}",
            flush=True,
        )

        marker_entry = {
            "leg": tag,
            "render_number": render_number,
            "photo_evidence_id": leg["evidence_id"],
            "photo_sha256": leg["photo_sha256"],
            "photo_ref_sha256": leg["photo_ref_sha256"],
            "post_sent": "pending",
            "started_at": now_utc(),
        }
        marker_data["renders"].append(marker_entry)
        write_json(marker, marker_data)

        outcome = scene.render_scene(
            db,
            household_id=ctx["household_id"],
            photo_ref=leg["photo_ref"],
            brief=leg["brief"],
            image_model=IMAGE_MODEL,
            orchestrator=ORCHESTRATOR,
            worst_case_usd=float(proof["worst_case_usd"]),
            authority=authority,
            transport=TRANSPORT,
            timeout_s=RENDER_TIMEOUT_S,
        )
        result = {
            "leg": tag,
            "render_number": render_number,
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
            "photo_evidence_id": leg["evidence_id"],
            "asset_id": leg["asset_id"],
            "display_name": leg["label"],
            "photo_sha256": leg["photo_sha256"],
            "photo_ref_sha256": leg["photo_ref_sha256"],
            "brief": leg["brief"],
        }
        write_json(EVIDENCE_DIR / f"SG-223_render_{tag}_result.json", result)
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
                    EVIDENCE_DIR / f"SG-223_ledger_row_{tag}.json", dict(row)
                )
        if outcome.status == "rendered" and outcome.storage_key is not None:
            ext = scene._IMAGE_MEDIA_EXTENSIONS.get(outcome.image_media_type or "", ".png")
            data = (STORAGE_ROOT / outcome.storage_key).read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            if sha != outcome.image_sha256:
                print(
                    f"stored_image_sha_mismatch stored={sha} outcome={outcome.image_sha256}",
                    flush=True,
                )
            out = EVIDENCE_DIR / f"SG-223_render_{tag}{ext}"
            out.write_bytes(data)
            print(f"stored_image_copied {out} bytes={len(data)} sha256={sha}", flush=True)
        post = live_spend_read(tag)
        if post is not None:
            write_json(EVIDENCE_DIR / f"SG-223_post_spend_{tag}.json", post)
        print(
            f"leg={tag} status={outcome.status} evidence={outcome.evidence_id} "
            f"ledger={outcome.ledger_id} cost={outcome.cost_usd} "
            f"error={outcome.error_state}",
            flush=True,
        )
        outcomes.append(result)
        if outcome.status != "rendered":
            break

    final_spend = live_spend_read("final")
    if final_spend is not None:
        write_json(EVIDENCE_DIR / "SG-223_post_spend_final.json", final_spend)
    rendered, billed_sends, pilot_rows_after = pilot_counts(db, pilot_cutoff())
    post_counts = table_counts(db)
    new_evidence = [r["evidence_id"] for r in outcomes if r.get("evidence_id")]
    new_ledger = [r["ledger_id"] for r in outcomes if r.get("ledger_id")]
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
            "cutoff": pilot_cutoff(),
            "billed_successful_renders": rendered,
            "billed_sends": billed_sends,
            "rows": pilot_rows_after,
        },
        "costita_links": asset_links(db, COSTITA_ASSET_ID),
        "miso_links": asset_links(db, MISO_ASSET_ID),
        "outcomes": outcomes,
        "finished_at": now_utc(),
    }
    write_json(EVIDENCE_DIR / "SG-223_db_post.json", db_post)
    print(
        f"slice_outcomes rendered={sum(1 for r in outcomes if r['status'] == 'rendered')} "
        f"attempted={len(outcomes)}",
        flush=True,
    )
    return 0 if len(outcomes) == SLICE_RENDERS and all(
        r["status"] == "rendered" for r in outcomes
    ) else 1


def link_render(db, leg_name: str, reason: str) -> int:
    leg = {"costita": COSTITA_PHOTO, "miso": MISO_PHOTO}[leg_name]
    result_path = EVIDENCE_DIR / f"SG-223_render_{leg_name}_result.json"
    if not result_path.exists():
        raise SystemExit(f"render_result_missing {result_path} -> STOP")
    result = json.loads(result_path.read_text())
    if result.get("status") != "rendered" or not result.get("evidence_id"):
        raise SystemExit(f"render_not_rendered status={result.get('status')} -> STOP")
    evidence_id = result["evidence_id"]
    if evidence_id not in (result.get("evidence_id"),):
        raise SystemExit("evidence_id_mismatch -> STOP")
    row = db.execute(
        text("SELECT id, source_kind, media_type, sha256 FROM evidence WHERE id = :id"),
        {"id": evidence_id},
    ).mappings().first()
    if row is None:
        raise SystemExit(f"evidence_row_missing {evidence_id} -> STOP")
    if row["source_kind"] != "scene_render":
        raise SystemExit(f"evidence_source_kind={row['source_kind']} -> STOP")
    if row["media_type"] not in ("image/jpeg", "image/png", "image/webp"):
        raise SystemExit(f"evidence_media_type={row['media_type']} -> STOP")
    existing = db.execute(
        text(
            "SELECT count(*) FROM asset_evidence WHERE asset_id = :a AND evidence_id = :e"
        ),
        {"a": leg["asset_id"], "e": evidence_id},
    ).scalar_one()
    if existing:
        raise SystemExit(f"link_already_exists pair=({leg['asset_id']},{evidence_id}) -> STOP")
    before = table_counts(db)
    ins = db.execute(
        text("INSERT INTO asset_evidence (asset_id, evidence_id) VALUES (:a, :e)"),
        {"a": leg["asset_id"], "e": evidence_id},
    )
    if ins.rowcount != 1:
        db.rollback()
        raise SystemExit(f"link_insert_rowcount={ins.rowcount} -> STOP")
    db.commit()
    after = table_counts(db)
    if after["asset_evidence"] != before["asset_evidence"] + 1:
        raise SystemExit("link_count_not_incremented -> STOP")
    links = asset_links(db, leg["asset_id"])
    print(f"linked asset={leg['asset_id']} evidence={evidence_id} rows={links}", flush=True)
    write_json(
        EVIDENCE_DIR / f"SG-223_link_{leg_name}.json",
        {
            "timestamp": now_utc(),
            "asset_id": leg["asset_id"],
            "evidence_id": evidence_id,
            "reason": reason,
            "before_table_counts": before,
            "after_table_counts": after,
            "asset_links": links,
        },
    )
    return 0


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
    parser.add_argument(
        "mode", choices=("verify", "unlink", "render", "link", "key-gate")
    )
    parser.add_argument("--leg", choices=("costita", "miso"), default=None)
    parser.add_argument("--reason", default="")
    parser.add_argument("--dir", default=None, help="key-gate target directory")
    args = parser.parse_args()

    if args.mode == "key-gate":
        return key_gate(Path(args.dir) if args.dir else EVIDENCE_DIR)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        print(
            f"[{now_utc()}] SG-223 mode={args.mode} image_model={IMAGE_MODEL} "
            f"transport={TRANSPORT} evidence_dir={EVIDENCE_DIR}",
            flush=True,
        )
        if args.mode == "verify":
            verify_live(db, None)
            return 0
        if args.mode == "unlink":
            return unlink_wrong_render(db)
        if args.mode == "link":
            if args.leg is None:
                raise SystemExit("link requires --leg")
            return link_render(db, args.leg, args.reason)
        households = db.execute(text("SELECT id, name FROM household")).mappings().all()
        if len(households) != 1:
            raise SystemExit(f"household_count={len(households)} -> STOP")
        ctx = verify_live(db, EXPECTED_LINKS_AFTER_UNLINK)
        ctx["household_id"] = households[0]["id"]
        return run_render(db, ctx)
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
