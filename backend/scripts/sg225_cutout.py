#!/usr/bin/env python3
"""SG-225 — L3 bulk stage: first cutout probe (Miso, isolation brief, render 5/10).

Modes (one invocation = one step):
  verify    live reads only: photo identity, cutout-unused proof over both sha
            forms, pilot state, spend state; writes the source-photo copy.
  render    verify + the three pre-send bounds + exactly ONE Image API render;
            a refusal/failure writes its bodies and stops (PB-6, no repair).
  link      review-before-link: INSERT one asset_evidence row for a render the
            Coder has opened and judged isolated AND faithful (never automatic).
  key-gate  scan a directory byte-for-byte for the live OpenRouter key value.

Lane-run tooling, not served code. Runs in the production image against the
live SQLite bind and storage volume. One send maximum; no UPDATE/DELETE, no
migration, no restart.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.config import settings
from app.db import SessionLocal
from app.services.scene import openrouter as scene

EVIDENCE_DIR = Path(os.environ.get("SG225_EVIDENCE_DIR", "/evidence"))
STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", "/data/storage"))
REPO_ROOT = Path(os.environ.get("SG225_REPO_ROOT", "/repo"))
PILOT_DECISION = REPO_ROOT / "docs/decisions/2026-10-21-d27-bounded-pilot.md"

IMAGE_MODEL = "google/gemini-3.1-flash-image"
ORCHESTRATOR = "bytedance-seed/seed-1.6-flash"
TRANSPORT = "image_api"
GRANT_ID = "L3 bulk stage (cutout probe, billed 5 of 10) + D-20 + D-14"

CAP_DAILY_USD = 2.00
CAP_MONTHLY_USD = 10.00
PILOT_RENDERS = 10
SLICE_RENDERS = 1
BILLED_BEFORE = 4
RENDER_NUMBER = 5

MISO_ASSET_ID = "01a0c4aa-8b62-7360-b11e-a476ddaea0f6"
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
CUTOUT_BRIEF_SHA256 = hashlib.sha256(MISO_PHOTO["brief"].encode("utf-8")).hexdigest()

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


def append_read_ledger(kind: str, url: str, http_status: int | None) -> None:
    path = EVIDENCE_DIR / "SG-225_reads.tsv"
    new = not path.exists()
    with path.open("a", encoding="utf-8") as fh:
        if new:
            fh.write("timestamp\tkind\turl\thttp_status\n")
        fh.write(f"{now_utc()}\t{kind}\t{url}\t{'' if http_status is None else http_status}\n")


def resolved_database() -> dict:
    url = settings.database_url
    try:
        name = make_url(url).database
    except Exception:
        name = None
    return {
        "database_url": url,
        "resolved_path": str(Path(name).resolve()) if name else None,
        "storage_root": str(STORAGE_ROOT),
    }


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
        raise SystemExit(f"photo_rows={len(rows)} evidence={spec['evidence_id']} -> STOP")
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
        raise SystemExit(f"photo_on_disk_mismatch sha={sha} bytes={len(data)} -> STOP")
    out = EVIDENCE_DIR / f"SG-225_source_{spec['leg']}.png"
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
            "brief_sha256": CUTOUT_BRIEF_SHA256,
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
        f"ref_sha256={pick['photo_ref_sha256']} brief_sha256={CUTOUT_BRIEF_SHA256}",
        flush=True,
    )
    return pick


def cutout_unused(db, photo: dict) -> dict:
    """Zero cutout rows for this photo, over the raw and data-URL sha forms."""
    raw = photo["photo_sha256"]
    ref = photo["photo_ref_sha256"]
    raw_hits = db.execute(
        text("SELECT count(*) FROM provider_call WHERE input_hashes LIKE :p"),
        {"p": f"%{raw}%"},
    ).scalar_one()
    rows = db.execute(
        text(
            "SELECT id, created_at, cost, error_state, input_hashes, output_payload "
            "FROM provider_call WHERE provider = :p AND input_hashes LIKE :ref "
            "ORDER BY created_at, id"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER, "ref": f"%{ref}%"},
    ).mappings().all()
    matched: list[dict] = []
    cutout_rows: list[dict] = []
    for row in rows:
        try:
            hashes = json.loads(row["input_hashes"] or "{}")
            payload = json.loads(row["output_payload"] or "{}")
        except (TypeError, ValueError):
            raise SystemExit(f"ledger_row_unparseable {row['id']} -> STOP")
        prompt = payload.get("prompt")
        entry = {
            "id": row["id"],
            "created_at": row["created_at"],
            "cost": row["cost"],
            "error_state": row["error_state"],
            "photo_sha256": hashes.get("photo_sha256"),
            "brief_sha256": hashes.get("brief_sha256"),
            "prompt": prompt[:200] if isinstance(prompt, str) else None,
        }
        matched.append(entry)
        if entry["brief_sha256"] == CUTOUT_BRIEF_SHA256:
            cutout_rows.append(entry)
    proof = {
        "timestamp": now_utc(),
        "photo_evidence_id": photo["evidence_id"],
        "photo_raw_sha256": raw,
        "photo_ref_sha256": ref,
        "cutout_brief_sha256": CUTOUT_BRIEF_SHA256,
        "raw_sha_rows": int(raw_hits),
        "ref_sha_rows": len(matched),
        "rows": matched,
        "cutout_rows": cutout_rows,
    }
    write_json(EVIDENCE_DIR / "SG-225_cutout_unused.json", proof)
    print(
        f"cutout_unused raw_sha_rows={raw_hits} ref_sha_rows={len(matched)} "
        f"cutout_rows={len(cutout_rows)}",
        flush=True,
    )
    if raw_hits != 0:
        raise SystemExit(f"cutout_raw_sha_hits={raw_hits} expected=0 -> STOP")
    if not matched:
        raise SystemExit("scene_row_for_photo_absent -> STOP")
    if cutout_rows:
        raise SystemExit(f"cutout_rows={len(cutout_rows)} expected=0 -> STOP")
    return proof


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
    if PILOT_DECISION.exists():
        return f"{PILOT_DECISION.name[:10]} 00:00:00"
    print("decision_record_missing -> pilot cutoff 1970 (all history counts)", flush=True)
    return "1970-01-01 00:00:00"


def pilot_counts(db, cutoff: str) -> tuple[int, int, int, list[dict]]:
    rows = db.execute(
        text(
            "SELECT id, cost, error_state, created_at FROM provider_call "
            "WHERE provider = :p AND created_at >= :c ORDER BY created_at, id"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER, "c": cutoff},
    ).mappings().all()
    billed = [r for r in rows if r["cost"] is not None and (r["cost"] > 0 or r["error_state"] is None)]
    rendered = sum(1 for r in rows if r["error_state"] is None)
    non_null = sum(1 for r in rows if r["cost"] is not None)
    return len(billed), rendered, max(rendered, non_null), [dict(r) for r in rows]


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
        append_read_ledger(f"key_{tag}", KEY_URL, resp.status_code)
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
        write_json(EVIDENCE_DIR / f"SG-225_spend_body_{tag}.json", spend)

        url = f"{IMAGE_MODELS_URL}/{IMAGE_MODEL}/endpoints"
        resp = client.get(url)
        append_read_ledger(f"endpoints_{tag}", url, resp.status_code)
        if resp.status_code != 200:
            raise SystemExit(f"endpoints_read_failed http_status:{resp.status_code}")
        endpoints = resp.json()
        write_json(EVIDENCE_DIR / f"SG-225_pricing_body_{tag}.json", endpoints)
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
    db, photo: dict
) -> tuple[object | None, dict, scene.SceneSpendAuthority | None]:
    """The packet's three bounds (a/b/c) re-derived live BEFORE the send."""
    key = scene.resolve_openrouter_key()
    if key is None:
        raise SystemExit("missing_key -> STOP")
    spend, endpoints = live_reads(key, "pre")

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
    billed, rendered, helper_consumed, rows = pilot_counts(db, cutoff)
    print(
        f"pilot_cutoff={cutoff} billed={billed} rendered={rendered} "
        f"helper_consumed={helper_consumed} rows={rows}",
        flush=True,
    )
    if billed != BILLED_BEFORE:
        raise SystemExit(f"pilot_billed_pre={billed} expected={BILLED_BEFORE} -> STOP")

    slice_sends_done = 0
    if slice_sends_done + 1 > SLICE_RENDERS:
        raise SystemExit("slice_bound_breached -> STOP")
    if billed + 1 > PILOT_RENDERS:
        raise SystemExit("pilot_bound_breached -> STOP")

    owner_today, owner_month, owner_detail = owner_upstream_totals(db)
    daily_rem = CAP_DAILY_USD - float(daily)
    monthly_rem = CAP_MONTHLY_USD - float(monthly)
    pilot_rem = (PILOT_RENDERS - billed) * worst_case
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
        "leg": photo["leg"],
        "render_number": RENDER_NUMBER,
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
        "pilot_billed": billed,
        "pilot_rendered": rendered,
        "helper_pilot_consumed": helper_consumed,
        "pilot_rows": rows,
        "photo_evidence_id": photo["evidence_id"],
        "photo_sha256": photo["photo_sha256"],
        "photo_ref_sha256": photo["photo_ref_sha256"],
        "brief": photo["brief"],
        "brief_sha256": photo["brief_sha256"],
    }
    write_json(EVIDENCE_DIR / "SG-225_guard_proof.json", proof)
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
    append_read_ledger(f"post_spend_{tag}", KEY_URL, resp.status_code)
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


def verify_live(db) -> dict:
    households = db.execute(text("SELECT id, name FROM household")).mappings().all()
    if len(households) != 1:
        raise SystemExit(f"household_count={len(households)} -> STOP")
    counts = table_counts(db)
    print(f"table_counts={counts}", flush=True)

    photo = confirm_photo(db, MISO_PHOTO)
    unused = cutout_unused(db, photo)

    cutoff = pilot_cutoff()
    billed, rendered, helper_consumed, pilot_rows = pilot_counts(db, cutoff)
    spent_usd, unknown = scene.scene_spend_so_far(db)
    owner_today, owner_month, owner_detail = owner_upstream_totals(db)
    print(
        f"pilot_cutoff={cutoff} billed={billed} rendered={rendered} "
        f"helper_consumed={helper_consumed} rows={pilot_rows}",
        flush=True,
    )
    print(
        f"scene_spend known={spent_usd} unknown={unknown} "
        f"owner_today={owner_today:.9f} owner_month={owner_month:.9f}",
        flush=True,
    )

    report = {
        "timestamp": now_utc(),
        "database": resolved_database(),
        "household": dict(households[0]),
        "table_counts": counts,
        "miso_links": asset_links(db, MISO_ASSET_ID),
        "photo": {k: v for k, v in photo.items() if k != "photo_ref"},
        "cutout_unused": unused,
        "pilot": {
            "cutoff": cutoff,
            "billed": billed,
            "rendered": rendered,
            "helper_consumed": helper_consumed,
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
    write_json(EVIDENCE_DIR / "SG-225_verify.json", report)
    return {"report": report, "photo": photo, "household_id": households[0]["id"]}


def run_render(db) -> int:  # noqa: C901
    marker = EVIDENCE_DIR / "SG-225_attempt.json"
    if marker.exists():
        try:
            prior = json.loads(marker.read_text())
        except (ValueError, OSError):
            prior = {"post_sent": True}
        if prior.get("post_sent"):
            raise SystemExit("slice_already_sent -> STOP (a prior run may already have sent)")

    pre_counts = table_counts(db)
    ctx = verify_live(db)
    refusal, proof, authority = pre_send_proof(db, ctx["photo"])

    if refusal is not None:
        result = {
            "returned_at": now_utc(),
            "status": "refused",
            "refusal": {"code": refusal.code, "reason": refusal.reason},
            "photo_evidence_id": ctx["photo"]["evidence_id"],
            "photo_sha256": ctx["photo"]["photo_sha256"],
            "photo_ref_sha256": ctx["photo"]["photo_ref_sha256"],
            "brief": ctx["photo"]["brief"],
            "authority_cap_usd": proof["cap_usd"],
            "projected_all_in": proof["projected_all_in"],
        }
        write_json(EVIDENCE_DIR / "SG-225_render_result.json", result)
        print(f"render refused {refusal.code}: {refusal.reason}", flush=True)
        write_json(
            EVIDENCE_DIR / "SG-225_db_post.json",
            {
                "timestamp": now_utc(),
                "pre": pre_counts,
                "post": pre_counts,
                "delta": {key: 0 for key in pre_counts},
                "outcome": result,
                "new_evidence_ids": [],
                "new_ledger_ids": [],
            },
        )
        return 1

    photo = ctx["photo"]
    request = scene.build_image_request(photo["photo_ref"], photo["brief"], IMAGE_MODEL)
    request["headers"] = dict(request["headers"])
    write_json(EVIDENCE_DIR / "SG-225_request.json", request)
    print(
        f"request_url={request['url']} body_keys={sorted(request['json'])} "
        f"photo_ref_chars={len(photo['photo_ref'])}",
        flush=True,
    )

    marker_data = {
        "started_at": now_utc(),
        "render_number": RENDER_NUMBER,
        "photo_evidence_id": photo["evidence_id"],
        "photo_sha256": photo["photo_sha256"],
        "photo_ref_sha256": photo["photo_ref_sha256"],
        "brief_sha256": photo["brief_sha256"],
        "post_sent": "pending",
    }
    write_json(marker, marker_data)

    outcome = scene.render_scene(
        db,
        household_id=ctx["household_id"],
        photo_ref=photo["photo_ref"],
        brief=photo["brief"],
        image_model=IMAGE_MODEL,
        orchestrator=ORCHESTRATOR,
        worst_case_usd=float(proof["worst_case_usd"]),
        authority=authority,
        transport=TRANSPORT,
        timeout_s=RENDER_TIMEOUT_S,
    )
    marker_data["post_sent"] = True
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
        "worst_case_usd": proof["worst_case_usd"],
        "authority_cap_usd": proof["cap_usd"],
        "photo_evidence_id": photo["evidence_id"],
        "asset_id": photo["asset_id"],
        "display_name": photo["label"],
        "photo_sha256": photo["photo_sha256"],
        "photo_ref_sha256": photo["photo_ref_sha256"],
        "brief": photo["brief"],
        "brief_sha256": photo["brief_sha256"],
    }
    marker_data.update(
        {
            "returned_at": result["returned_at"],
            "status": outcome.status,
            "evidence_id": outcome.evidence_id,
            "ledger_id": outcome.ledger_id,
        }
    )
    write_json(marker, marker_data)
    write_json(EVIDENCE_DIR / "SG-225_render_result.json", result)

    if outcome.ledger_id is not None:
        row = db.execute(
            text("SELECT * FROM provider_call WHERE id = :id"),
            {"id": outcome.ledger_id},
        ).mappings().first()
        if row is not None:
            write_json(EVIDENCE_DIR / "SG-225_ledger_row.json", dict(row))
    if outcome.status == "rendered" and outcome.storage_key is not None:
        ext = scene._IMAGE_MEDIA_EXTENSIONS.get(outcome.image_media_type or "", ".png")
        data = (STORAGE_ROOT / outcome.storage_key).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        if sha != outcome.image_sha256:
            print(
                f"stored_image_sha_mismatch stored={sha} outcome={outcome.image_sha256}",
                flush=True,
            )
        out = EVIDENCE_DIR / f"SG-225_render_miso{ext}"
        out.write_bytes(data)
        print(f"stored_image_copied {out} bytes={len(data)} sha256={sha}", flush=True)

    post_spend = live_spend_read("post")
    if post_spend is not None:
        write_json(EVIDENCE_DIR / "SG-225_post_spend.json", post_spend)

    post_counts = table_counts(db)
    new_evidence = [outcome.evidence_id] if outcome.evidence_id else []
    new_ledger = [outcome.ledger_id] if outcome.ledger_id else []
    billed_after, rendered_after, helper_after, pilot_rows_after = pilot_counts(
        db, pilot_cutoff()
    )
    db_post = {
        "timestamp": now_utc(),
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
            "billed": billed_after,
            "rendered": rendered_after,
            "helper_consumed": helper_after,
            "rows": pilot_rows_after,
        },
        "miso_links": asset_links(db, MISO_ASSET_ID),
        "outcome": result,
        "finished_at": now_utc(),
    }
    write_json(EVIDENCE_DIR / "SG-225_db_post.json", db_post)
    print(
        f"render status={outcome.status} evidence={outcome.evidence_id} "
        f"ledger={outcome.ledger_id} cost={outcome.cost_usd} "
        f"error={outcome.error_state}",
        flush=True,
    )
    return 0 if outcome.status == "rendered" else 1


def post_state(db) -> int:
    counts = table_counts(db)
    cutoff = pilot_cutoff()
    billed, rendered, helper_consumed, rows = pilot_counts(db, cutoff)
    spent_usd, unknown = scene.scene_spend_so_far(db)
    owner_today, owner_month, owner_detail = owner_upstream_totals(db)
    result_path = EVIDENCE_DIR / "SG-225_render_result.json"
    result = json.loads(result_path.read_text()) if result_path.exists() else {}
    decision_path = EVIDENCE_DIR / "SG-225_link_decision.json"
    decision = json.loads(decision_path.read_text()) if decision_path.exists() else None
    evidence_id = result.get("evidence_id")
    ledger_id = result.get("ledger_id")
    out = {
        "timestamp": now_utc(),
        "database": resolved_database(),
        "table_counts": counts,
        "pilot_after": {
            "cutoff": cutoff,
            "billed": billed,
            "rendered": rendered,
            "helper_consumed": helper_consumed,
            "rows": rows,
        },
        "spend": {
            "known": spent_usd,
            "unknown_cost_calls": unknown,
            "owner_today": owner_today,
            "owner_month": owner_month,
            "owner_rows": owner_detail,
        },
        "new_evidence_ids": [evidence_id] if evidence_id else [],
        "new_ledger_ids": [ledger_id] if ledger_id else [],
        "evidence_rows": rows_by_ids(db, "evidence", "id", [evidence_id] if evidence_id else []),
        "provider_call_rows": rows_by_ids(
            db, "provider_call", "id", [ledger_id] if ledger_id else []
        ),
        "audit_event_rows": rows_by_ids(
            db, "audit_event", "entity_id", [evidence_id] if evidence_id else []
        ),
        "miso_links": asset_links(db, MISO_ASSET_ID),
        "render_status": result.get("status"),
        "link_decision": decision,
    }
    write_json(EVIDENCE_DIR / "SG-225_post_state.json", out)
    print(
        f"post_state billed={billed} rendered={rendered} known={spent_usd} "
        f"unknown={unknown} owner_today={owner_today:.9f} "
        f"owner_month={owner_month:.9f} miso_links={len(out['miso_links'])} "
        f"render_status={out['render_status']}",
        flush=True,
    )
    return 0 if result.get("status") == "rendered" else 1


def link_render(db, reason: str) -> int:
    if not reason.strip():
        raise SystemExit("link requires a non-empty --reason -> STOP")
    result_path = EVIDENCE_DIR / "SG-225_render_result.json"
    if not result_path.exists():
        raise SystemExit(f"render_result_missing {result_path} -> STOP")
    result = json.loads(result_path.read_text())
    if result.get("status") != "rendered" or not result.get("evidence_id"):
        raise SystemExit(f"render_not_rendered status={result.get('status')} -> STOP")
    evidence_id = result["evidence_id"]
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
        {"a": MISO_ASSET_ID, "e": evidence_id},
    ).scalar_one()
    if existing:
        raise SystemExit(f"link_already_exists pair=({MISO_ASSET_ID},{evidence_id}) -> STOP")
    before = table_counts(db)
    ins = db.execute(
        text("INSERT INTO asset_evidence (asset_id, evidence_id) VALUES (:a, :e)"),
        {"a": MISO_ASSET_ID, "e": evidence_id},
    )
    if ins.rowcount != 1:
        db.rollback()
        raise SystemExit(f"link_insert_rowcount={ins.rowcount} -> STOP")
    db.commit()
    after = table_counts(db)
    if after["asset_evidence"] != before["asset_evidence"] + 1:
        raise SystemExit("link_count_not_incremented -> STOP")
    links = asset_links(db, MISO_ASSET_ID)
    print(f"linked asset={MISO_ASSET_ID} evidence={evidence_id} rows={links}", flush=True)
    write_json(
        EVIDENCE_DIR / "SG-225_link.json",
        {
            "timestamp": now_utc(),
            "asset_id": MISO_ASSET_ID,
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
    parser.add_argument("mode", choices=("verify", "render", "post", "link", "key-gate"))
    parser.add_argument("--reason", default="")
    parser.add_argument("--dir", default=None, help="key-gate target directory")
    args = parser.parse_args()

    if args.mode == "key-gate":
        return key_gate(Path(args.dir) if args.dir else EVIDENCE_DIR)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        print(
            f"[{now_utc()}] SG-225 mode={args.mode} image_model={IMAGE_MODEL} "
            f"transport={TRANSPORT} evidence_dir={EVIDENCE_DIR} db={resolved_database()}",
            flush=True,
        )
        if args.mode == "verify":
            verify_live(db)
            return 0
        if args.mode == "post":
            return post_state(db)
        if args.mode == "link":
            return link_render(db, args.reason)
        return run_render(db)
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
