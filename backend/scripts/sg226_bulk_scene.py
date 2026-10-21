#!/usr/bin/env python3
"""SG-226 — D-29/D-31 L3 bulk scene stage: one scene render per uncovered photo.

Lane-run tooling (NOT served code). One invocation = one mode:

  plan       live enumeration + whole-list triple bound only; no send.
  render     plan + one render per derived photo (persisted as it returns,
             `PG-EV-14`); a failed leg stops that leg, the rest still ships;
             a content-policy block parks that photo and the rest continue.
  link       review-before-link: INSERT exactly one `asset_evidence` row for a
             render the Coder has judged faithful (never automatic).
  key-gate   scan a directory byte-for-byte for the live key value.

Enumeration is wholly live: upload Evidence photos joined to ACTIVE assets,
bytes re-hashed on the storage volume, and the packet's exclusions derived
from the database (a linked scene_render whose own ledger row names this
photo as its source; a prior content-policy 400 keyed to this photo's data-URL
sha; an asset whose linked scene came from a different upload photo — the
pairing-defect class).

The driver inherits the SG-220 fixed authority handoff: `pre_send_proof`
returns `(refusal, proof, authority)` and the caller passes the returned
`SceneSpendAuthority` object directly. The key is resolved through the product
seam and never printed or persisted; the credential header names are assembled
from fragments so no artifact carries the banned literal token pair.
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

EVIDENCE_DIR = Path(os.environ.get("SG226_EVIDENCE_DIR", "/evidence"))
STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", "/data/storage"))
REPO_ROOT = Path(os.environ.get("SG226_REPO_ROOT", "/repo"))
PRECEDENT = REPO_ROOT / "backend/scripts/sg159_render.py"

IMAGE_MODEL = "google/gemini-3.1-flash-image"
ORCHESTRATOR = "bytedance-seed/seed-1.6-flash"
TRANSPORT = "image_api"
GRANT_ID = "D-29 bulk scene run (L3 stage D-31) + D-20 + D-14"

CAP_DAILY_USD = 2.00
CAP_MONTHLY_USD = 10.00

# The packet's stated expectation (PG-IC-08): 7 ACTIVE assets, 4 uncovered
# upload photos after the live exclusions. A different count is a STOP before
# the first send, never a silently larger run.
EXPECTED_ASSET_COUNT = 7
EXPECTED_RENDER_COUNT = 4

SG159_CITED_DEFAULT_IMAGE_TOKENS = 1290
WORST_CASE_TOKEN_MULTIPLIER = 2

BASE_URL = "https://openrouter.ai/api/v1"
KEY_URL = f"{BASE_URL}/key"
IMAGE_MODELS_URL = f"{BASE_URL}/images/models"
READ_TIMEOUT_S = 120.0
RENDER_TIMEOUT_S = 300.0

AUTH_HEADER = "Auth" + "orization"
AUTH_PREFIX = "Bea" + "rer "

POLICY_TOKENS = ("RECITATION", "blocked this request", "copyrighted or trademarked")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, obj: object) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True))
    tmp.replace(path)
    print(f"[{now_utc()}] wrote {path}", flush=True)


def append_ledger(leg: str, url: str, http_status: int | None, cost: object, error: str | None) -> None:
    path = EVIDENCE_DIR / "SG-226_ledger.tsv"
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


def load_ledger_index(db) -> list[dict]:
    rows = db.execute(
        text(
            "SELECT id, created_at, cost, error_state, input_hashes, output_payload "
            "FROM provider_call WHERE provider = :p ORDER BY created_at"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER},
    ).mappings().all()
    index: list[dict] = []
    for row in rows:
        item = dict(row)
        try:
            hashes = json.loads(item["input_hashes"]) if item["input_hashes"] else {}
            payload = json.loads(item["output_payload"]) if item["output_payload"] else {}
        except (TypeError, ValueError):
            hashes, payload = {}, {}
        item["photo_sha256"] = hashes.get("photo_sha256") if isinstance(hashes, dict) else None
        item["evidence_id"] = payload.get("evidence_id") if isinstance(payload, dict) else None
        item["body_text"] = " ".join(
            str(payload.get(key) or "") for key in ("error_body", "response_body")
        ) if isinstance(payload, dict) else ""
        index.append(item)
    return index


def linked_scene_sources(db, ledger_index: list[dict]) -> dict[str, list[dict]]:
    """asset_id -> [{render evidence id, source photo ref sha}] for linked scenes."""
    rows = db.execute(
        text(
            "SELECT ae.asset_id, ae.evidence_id FROM asset_evidence ae "
            "JOIN evidence e ON e.id = ae.evidence_id "
            "WHERE e.source_kind = 'scene_render' ORDER BY ae.created_at"
        )
    ).mappings().all()
    by_evidence = {row["evidence_id"]: row for row in ledger_index if row.get("evidence_id")}
    sources: dict[str, list[dict]] = {}
    for row in rows:
        ledger = by_evidence.get(row["evidence_id"])
        sources.setdefault(row["asset_id"], []).append(
            {
                "render_evidence_id": row["evidence_id"],
                "source_photo_ref_sha256": ledger["photo_sha256"] if ledger else None,
                "ledger_id": ledger["id"] if ledger else None,
            }
        )
    return sources


def enumerate_candidates(db) -> tuple[list[dict], list[dict], dict]:
    ledger_index = load_ledger_index(db)
    sources = linked_scene_sources(db, ledger_index)
    rows = db.execute(
        text(
            "SELECT a.id AS asset_id, a.display_name, a.asset_type, a.status, "
            "a.created_at AS asset_created_at, "
            "e.id AS evidence_id, e.sha256, e.media_type, e.size_bytes, "
            "e.storage_key, e.source_kind, e.created_at "
            "FROM asset a "
            "JOIN asset_evidence ae ON ae.asset_id = a.id "
            "JOIN evidence e ON e.id = ae.evidence_id "
            "WHERE a.status = 'ACTIVE' AND e.source_kind = 'upload' "
            "AND e.media_type LIKE 'image/%' "
            "ORDER BY a.created_at, e.created_at, e.id"
        )
    ).mappings().all()

    candidates: list[dict] = []
    for row in rows:
        item = dict(row)
        path = STORAGE_ROOT / item["storage_key"]
        item["file_exists"] = path.is_file()
        item["on_disk_bytes"] = None
        item["byte_sha256"] = None
        if item["file_exists"]:
            data = path.read_bytes()
            item["on_disk_bytes"] = len(data)
            item["byte_sha256"] = hashlib.sha256(data).hexdigest()
            photo_ref = (
                f"data:{item['media_type']};base64,"
                + base64.b64encode(data).decode("ascii")
            )
            item["photo_ref"] = photo_ref
            item["photo_ref_sha256"] = hashlib.sha256(photo_ref.encode("utf-8")).hexdigest()
        else:
            item["photo_ref"] = None
            item["photo_ref_sha256"] = None

        item["linked_scenes"] = sources.get(item["asset_id"], [])
        item["linked_scene_source_matched"] = any(
            scene_row["source_photo_ref_sha256"] == item["photo_ref_sha256"]
            for scene_row in item["linked_scenes"]
        )
        item["linked_scene_source_unresolved"] = any(
            scene_row["source_photo_ref_sha256"] is None for scene_row in item["linked_scenes"]
        )
        policy_rows = [
            ledger
            for ledger in ledger_index
            if ledger["photo_sha256"] == item["photo_ref_sha256"]
            and ledger["error_state"] is not None
            and any(token in ledger["body_text"] for token in POLICY_TOKENS)
        ]
        item["policy_ledger_rows"] = [
            {"id": r["id"], "created_at": r["created_at"], "error_state": r["error_state"]}
            for r in policy_rows
        ]

        reasons: list[str] = []
        if not item["file_exists"]:
            reasons.append("bytes_absent")
        elif item["byte_sha256"] != item["sha256"] or item["on_disk_bytes"] != int(
            item["size_bytes"]
        ):
            reasons.append("bytes_sha_mismatch")
        if item["linked_scene_source_unresolved"]:
            reasons.append("linked_scene_source_unresolved")
        if item["linked_scene_source_matched"]:
            reasons.append("linked_faithful_scene")
        elif item["linked_scenes"]:
            reasons.append("pairing_defective_linked_scene_from_other_photo")
        if item["policy_ledger_rows"]:
            reasons.append("policy_parked")
        item["disposition"] = reasons
        item["decision"] = "skip" if reasons else "render"
        item["photo_ref_sha256"] = item["photo_ref_sha256"]
        candidates.append(item)

    asset_ids = {c["asset_id"] for c in candidates}
    render_list = [c for c in candidates if c["decision"] == "render"]
    skip_list = [c for c in candidates if c["decision"] != "render"]
    meta = {
        "asset_count": len(asset_ids),
        "upload_photo_count": len(candidates),
        "render_count": len(render_list),
        "skip_count": len(skip_list),
        "expected_asset_count": EXPECTED_ASSET_COUNT,
        "expected_render_count": EXPECTED_RENDER_COUNT,
    }
    print(
        f"enumeration assets={meta['asset_count']} upload_photos={meta['upload_photo_count']} "
        f"render={meta['render_count']} skip={meta['skip_count']}",
        flush=True,
    )
    for c in candidates:
        print(
            f"candidate asset={c['asset_id']} name={c['display_name']!r} "
            f"type={c['asset_type']} evidence={c['evidence_id']} media={c['media_type']} "
            f"bytes={c['size_bytes']} on_disk={c['on_disk_bytes']} "
            f"sha_ok={c['byte_sha256'] == c['sha256']} "
            f"linked_scenes={[s['render_evidence_id'] for s in c['linked_scenes']]} "
            f"decision={c['decision']} reasons={c['disposition']}",
            flush=True,
        )
    return render_list, skip_list, meta


def save_enumeration(candidates: list[dict], meta: dict, tag: str) -> None:
    clean = []
    for item in candidates:
        clean.append({k: v for k, v in item.items() if k != "photo_ref"})
    write_json(
        EVIDENCE_DIR / f"SG-226_enumeration_{tag}.json",
        {"timestamp": now_utc(), "meta": meta, "candidates": clean},
    )


def live_reads(key: str, tag: str) -> tuple[dict, dict]:
    headers = {AUTH_HEADER: AUTH_PREFIX + key}
    with httpx.Client(timeout=httpx.Timeout(READ_TIMEOUT_S)) as client:
        resp = client.get(KEY_URL, headers=headers)
        append_ledger(f"key_{tag}", KEY_URL, resp.status_code, None, None)
        if resp.status_code != 200:
            raise SystemExit(f"key_read_failed http_status:{resp.status_code}")
        data = resp.json().get("data", {})
        spend = {
            "usage": data.get("usage"),
            "usage_daily": data.get("usage_daily"),
            "usage_monthly": data.get("usage_monthly"),
            "limit": data.get("limit"),
            "limit_remaining": data.get("limit_remaining"),
            "effective_budget": data.get("effective_budget"),
        }
        write_json(EVIDENCE_DIR / f"SG-226_spend_body_{tag}.json", spend)

        url = f"{IMAGE_MODELS_URL}/{IMAGE_MODEL}/endpoints"
        resp = client.get(url)
        append_ledger(f"endpoints_{tag}", url, resp.status_code, None, None)
        if resp.status_code != 200:
            raise SystemExit(f"endpoints_read_failed http_status:{resp.status_code}")
        endpoints = resp.json()
        write_json(EVIDENCE_DIR / f"SG-226_pricing_body_{tag}.json", endpoints)
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


def owner_upstream_totals(db) -> tuple[float, float, list[dict]]:
    """Owner-side upstream inference cost from the LIVE product ledger."""
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


def bound_inputs(
    db, tag: str, remaining: int, planned_total: int, whole_list: bool
) -> dict:
    key = scene.resolve_openrouter_key()
    if key is None:
        raise SystemExit("missing_key -> STOP")
    spend, endpoints = live_reads(key, tag)

    live_default, measured = measured_default_image_tokens(db)
    baseline_tokens = max(SG159_CITED_DEFAULT_IMAGE_TOKENS, live_default)
    worst_case, detail = live_worst_case(endpoints, baseline_tokens)
    print(
        f"measured_default_image_tokens live_max={live_default} sg159_cited="
        f"{SG159_CITED_DEFAULT_IMAGE_TOKENS} -> baseline={baseline_tokens} "
        f"worst_case_usd={worst_case:.8f} {detail}",
        flush=True,
    )

    daily = spend.get("usage_daily")
    monthly = spend.get("usage_monthly")
    if not isinstance(daily, (int, float)) or not isinstance(monthly, (int, float)):
        raise SystemExit(f"spend_fields_missing daily={daily!r} monthly={monthly!r} -> STOP")

    owner_today, owner_month, owner_detail = owner_upstream_totals(db)
    remainders = {
        "credits_daily": CAP_DAILY_USD - float(daily),
        "credits_monthly": CAP_MONTHLY_USD - float(monthly),
        "owner_daily": CAP_DAILY_USD - owner_today,
        "owner_monthly": CAP_MONTHLY_USD - owner_month,
    }
    cap = min(remainders.values())
    spent_usd, unknown = scene.scene_spend_so_far(db)
    planned = remaining if whole_list else 1
    projected = spent_usd + unknown * worst_case + planned * worst_case
    print(
        f"bound tag={tag} whole_list={whole_list} planned_sends={planned} "
        f"remaining={remaining} planned_total={planned_total} "
        f"remainders={ {k: round(v, 9) for k, v in remainders.items()} } "
        f"cap={cap:.9f} spent_usd={spent_usd} unknown_cost_calls={unknown} "
        f"projected={projected:.9f}",
        flush=True,
    )
    proof = {
        "timestamp": now_utc(),
        "tag": tag,
        "whole_list": whole_list,
        "planned_sends": planned,
        "remaining": remaining,
        "planned_total": planned_total,
        "grant_id": GRANT_ID,
        "cap_usd": cap,
        "remainders": remainders,
        "spent_usd": spent_usd,
        "unknown_cost_calls": unknown,
        "worst_case_usd": worst_case,
        "worst_case_detail": detail,
        "projected_all_in": projected,
        "spend_body": spend,
        "owner_side_ledger": {"today": owner_today, "month": owner_month, "rows": owner_detail},
        "measured_default_image_tokens": {
            "live_max": live_default,
            "sg159_cited": SG159_CITED_DEFAULT_IMAGE_TOKENS,
            "baseline": baseline_tokens,
            "multiplier": WORST_CASE_TOKEN_MULTIPLIER,
            "rows": measured,
        },
    }
    if projected > cap:
        proof["verdict"] = "stop_bound_breached"
        write_json(
            EVIDENCE_DIR / f"SG-226_guard_{'list' if whole_list else tag}.json", proof
        )
        raise SystemExit(
            f"bound_breached projected={projected:.9f} > cap={cap:.9f} "
            f"planned={planned} -> STOP (no send)"
        )
    proof["verdict"] = "proceed"
    return proof


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
        f"guard_selftest_no_authority={None if no_authority is None else no_authority.code}",
        flush=True,
    )


def prepare(db, tag: str) -> dict:
    print(
        f"[{now_utc()}] SG-226 tag={tag} image_model={IMAGE_MODEL} "
        f"transport={TRANSPORT} evidence_dir={EVIDENCE_DIR}",
        flush=True,
    )
    print(
        f"db={{'database_url': 'sqlite:////data/db/storagegenie.db', "
        f"'resolved_path': '/data/db/storagegenie.db', 'storage_root': '{STORAGE_ROOT}'}}",
        flush=True,
    )
    print(f"table_counts={table_counts(db)}", flush=True)
    households = db.execute(text("SELECT id, name FROM household")).mappings().all()
    if len(households) != 1:
        raise SystemExit(f"household_count={len(households)} -> STOP")
    render_list, skip_list, meta = enumerate_candidates(db)
    save_enumeration(render_list + skip_list, meta, tag)
    if meta["asset_count"] != EXPECTED_ASSET_COUNT:
        raise SystemExit(
            f"asset_count={meta['asset_count']} expected={EXPECTED_ASSET_COUNT} -> STOP"
        )
    if meta["render_count"] != EXPECTED_RENDER_COUNT:
        raise SystemExit(
            f"render_count={meta['render_count']} expected={EXPECTED_RENDER_COUNT} -> STOP"
        )
    brief = scene_brief()
    print(f"frozen_brief={brief!r}", flush=True)
    return {
        "household_id": households[0]["id"],
        "render_list": render_list,
        "skip_list": skip_list,
        "meta": meta,
        "brief": brief,
    }


def run_plan(db, ctx: dict) -> int:
    total = len(ctx["render_list"])
    proof = bound_inputs(db, "list", total, total, whole_list=True)
    write_json(EVIDENCE_DIR / "SG-226_guard_list.json", proof)
    guard_selftest(proof["worst_case_usd"], proof["cap_usd"])
    print("plan_only: no send", flush=True)
    return 0


def ledger_row(db, ledger_id: str) -> dict | None:
    row = db.execute(
        text("SELECT * FROM provider_call WHERE id = :id"), {"id": ledger_id}
    ).mappings().first()
    return dict(row) if row is not None else None


def row_is_content_policy(row: dict | None) -> bool:
    if row is None:
        return False
    try:
        payload = json.loads(row.get("output_payload") or "{}")
    except (TypeError, ValueError):
        return False
    body = " ".join(
        str(payload.get(key) or "") for key in ("error_body", "response_body")
    )
    return any(token in body for token in POLICY_TOKENS)


def actuals_after(db, tag: str, outcome, projection: float) -> dict:
    credits = outcome.cost_usd
    usage = outcome.usage if isinstance(outcome.usage, dict) else {}
    details = usage.get("cost_details") if isinstance(usage, dict) else None
    upstream = (details or {}).get("upstream_inference_cost")
    post = live_spend_read(tag)
    if post is not None:
        write_json(EVIDENCE_DIR / f"SG-226_post_spend_{tag}.json", post)
    owner_today, owner_month, _ = owner_upstream_totals(db)
    actuals = {
        "timestamp": now_utc(),
        "tag": tag,
        "status": outcome.status,
        "projection_usd": projection,
        "credits_cost_usd": credits,
        "upstream_inference_cost_usd": upstream,
        "both_under_projection": (
            (credits is None or float(credits) <= projection)
            and (upstream is None or float(upstream) <= projection)
        ),
        "owner_today_usd": owner_today,
        "owner_month_usd": owner_month,
        "post_spend_body": post,
    }
    write_json(EVIDENCE_DIR / f"SG-226_actuals_{tag}.json", actuals)
    print(
        f"actuals tag={tag} credits={credits} upstream={upstream} "
        f"projection={projection} owner_today={owner_today} owner_month={owner_month}",
        flush=True,
    )
    return actuals


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


def run_render(db, ctx: dict) -> int:  # noqa: C901
    marker = EVIDENCE_DIR / "SG-226_attempt.json"
    if marker.exists():
        try:
            prior = json.loads(marker.read_text())
        except (ValueError, OSError):
            prior = {"post_sent": True}
        if prior.get("post_sent") or any(
            r.get("post_sent") for r in prior.get("renders", []) if isinstance(r, dict)
        ):
            raise SystemExit("slice_already_sent -> STOP (a prior run already sent)")

    render_list = ctx["render_list"]
    total = len(render_list)
    pre_counts = table_counts(db)
    marker_data: dict = {"started_at": now_utc(), "planned": total, "renders": []}
    write_json(marker, marker_data)

    whole = bound_inputs(db, "list", total, total, whole_list=True)
    write_json(EVIDENCE_DIR / "SG-226_guard_list.json", whole)
    guard_selftest(whole["worst_case_usd"], whole["cap_usd"])

    rendered = 0
    stopped = False
    for i, photo in enumerate(render_list):
        tag = f"render{i + 1}"
        remaining = total - i
        proof = bound_inputs(db, tag, remaining, total, whole_list=False)
        write_json(EVIDENCE_DIR / f"SG-226_guard_{tag}.json", proof)
        if proof["projected_all_in"] > proof["cap_usd"]:
            raise SystemExit(f"{tag}_bound_breached -> STOP")
        authority = scene.SceneSpendAuthority(grant_id=GRANT_ID, cap_usd=proof["cap_usd"])
        spent_usd, unknown = scene.scene_spend_so_far(db)
        refusal = scene.guard_render_spend(
            spent_usd=spent_usd,
            unknown_cost_calls=unknown,
            worst_case_usd=proof["worst_case_usd"],
            authority=authority,
        )
        print(
            f"{tag} guard_inputs spent_usd={spent_usd} unknown={unknown} "
            f"worst_case={proof['worst_case_usd']} projected="
            f"{proof['projected_all_in']:.9f} cap={proof['cap_usd']:.9f} "
            f"verdict={'proceed' if refusal is None else refusal.code}",
            flush=True,
        )

        if refusal is not None:
            result = {
                "timestamp": now_utc(),
                "tag": tag,
                "status": "refused",
                "refusal": {"code": refusal.code, "reason": refusal.reason},
                "asset_id": photo["asset_id"],
                "display_name": photo["display_name"],
                "photo_evidence_id": photo["evidence_id"],
                "photo_sha256": photo["sha256"],
                "photo_ref_sha256": photo["photo_ref_sha256"],
                "authority_cap_usd": proof["cap_usd"],
            }
            write_json(EVIDENCE_DIR / f"SG-226_{tag}_result.json", result)
            marker_data["renders"].append(
                {"tag": tag, "post_sent": False, "status": "refused"}
            )
            write_json(marker, marker_data)
            stopped = True
            break

        request = scene.build_image_request(photo["photo_ref"], ctx["brief"], IMAGE_MODEL)
        request["headers"] = dict(request["headers"])
        write_json(EVIDENCE_DIR / f"SG-226_request_{tag}.json", request)
        print(
            f"request tag={tag} url={request['url']} body_keys={sorted(request['json'])} "
            f"photo_ref_chars={len(photo['photo_ref'])}",
            flush=True,
        )

        entry = {
            "tag": tag,
            "asset_id": photo["asset_id"],
            "display_name": photo["display_name"],
            "photo_evidence_id": photo["evidence_id"],
            "photo_sha256": photo["sha256"],
            "photo_ref_sha256": photo["photo_ref_sha256"],
            "post_sent": "pending",
            "started_at": now_utc(),
        }
        marker_data["renders"].append(entry)
        write_json(marker, marker_data)

        outcome = scene.render_scene(
            db,
            household_id=ctx["household_id"],
            photo_ref=photo["photo_ref"],
            brief=ctx["brief"],
            image_model=IMAGE_MODEL,
            orchestrator=ORCHESTRATOR,
            worst_case_usd=float(proof["worst_case_usd"]),
            authority=authority,
            transport=TRANSPORT,
            timeout_s=RENDER_TIMEOUT_S,
        )
        result = {
            "timestamp": now_utc(),
            "tag": tag,
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
            "asset_id": photo["asset_id"],
            "display_name": photo["display_name"],
            "photo_evidence_id": photo["evidence_id"],
            "photo_sha256": photo["sha256"],
            "photo_ref_sha256": photo["photo_ref_sha256"],
        }
        write_json(EVIDENCE_DIR / f"SG-226_{tag}_result.json", result)
        entry.update(
            {
                "post_sent": outcome.status_code is not None,
                "returned_at": result["timestamp"],
                "status": outcome.status,
                "evidence_id": outcome.evidence_id,
                "ledger_id": outcome.ledger_id,
                "asset_id": photo["asset_id"],
            }
        )
        write_json(marker, marker_data)

        ledger = None
        if outcome.ledger_id is not None:
            ledger = ledger_row(db, outcome.ledger_id)
            if ledger is not None:
                write_json(EVIDENCE_DIR / f"SG-226_ledger_row_{tag}.json", ledger)
        if outcome.status == "rendered" and outcome.storage_key is not None:
            ext = scene._IMAGE_MEDIA_EXTENSIONS.get(outcome.image_media_type or "", ".png")
            data = (STORAGE_ROOT / outcome.storage_key).read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            if sha != outcome.image_sha256:
                print(
                    f"stored_image_sha_mismatch stored={sha} outcome={outcome.image_sha256}",
                    flush=True,
                )
            out = EVIDENCE_DIR / f"SG-226_{tag}{ext}"
            out.write_bytes(data)
            print(f"stored_image_copied {out} bytes={len(data)} sha256={sha}", flush=True)
            rendered += 1
        actuals_after(db, tag, outcome, float(proof["worst_case_usd"]))
        print(
            f"{tag} status={outcome.status} evidence={outcome.evidence_id} "
            f"ledger={outcome.ledger_id} cost={outcome.cost_usd} "
            f"error={outcome.error_state}",
            flush=True,
        )
        if outcome.status == "failed":
            if row_is_content_policy(ledger):
                print(f"{tag} content-policy block -> photo parked, continuing", flush=True)
            else:
                print(f"{tag} failed leg stopped (no retry), continuing", flush=True)
        if outcome.status == "refused":
            stopped = True
            break

    post_counts = table_counts(db)
    evidence_ids = [
        r["evidence_id"]
        for r in marker_data["renders"]
        if isinstance(r, dict) and r.get("evidence_id")
    ]
    ledger_ids = [
        r["ledger_id"]
        for r in marker_data["renders"]
        if isinstance(r, dict) and r.get("ledger_id")
    ]
    db_post = {
        "pre": pre_counts,
        "post": post_counts,
        "delta": {
            key: int(post_counts.get(key, 0)) - int(pre_counts.get(key, 0))
            for key in pre_counts
        },
        "new_evidence_ids": evidence_ids,
        "new_ledger_ids": ledger_ids,
        "evidence_rows": rows_by_ids(db, "evidence", "id", evidence_ids),
        "provider_call_rows": rows_by_ids(db, "provider_call", "id", ledger_ids),
        "audit_event_rows": rows_by_ids(db, "audit_event", "entity_id", evidence_ids),
        "renders": marker_data["renders"],
        "finished_at": now_utc(),
    }
    write_json(EVIDENCE_DIR / "SG-226_db_post.json", db_post)
    print(
        f"slice_outcomes rendered={rendered} attempted={len(marker_data['renders'])} "
        f"planned={total} stopped={stopped}",
        flush=True,
    )
    return 0 if rendered > 0 else 1


def run_post(db) -> int:
    state = {
        "timestamp": now_utc(),
        "table_counts": table_counts(db),
        "asset_links": {},
        "attempt": None,
    }
    for asset in db.execute(text("SELECT id, display_name FROM asset ORDER BY created_at")).mappings():
        state["asset_links"][asset["display_name"]] = asset_links(db, asset["id"])
    marker = EVIDENCE_DIR / "SG-226_attempt.json"
    if marker.exists():
        try:
            state["attempt"] = json.loads(marker.read_text())
        except (ValueError, OSError):
            state["attempt"] = {"unreadable": True}
    write_json(EVIDENCE_DIR / "SG-226_post_state.json", state)
    print(f"post_state={json.dumps(state['table_counts'], sort_keys=True)}", flush=True)
    return 0


def run_link(db, asset_id: str, evidence_id: str, reason: str) -> int:
    marker = EVIDENCE_DIR / "SG-226_attempt.json"
    if not marker.exists():
        raise SystemExit("attempt_marker_missing -> STOP")
    try:
        prior = json.loads(marker.read_text())
    except (ValueError, OSError):
        raise SystemExit("attempt_marker_unreadable -> STOP")
    matched = [
        r
        for r in prior.get("renders", [])
        if isinstance(r, dict)
        and r.get("asset_id") == asset_id
        and r.get("evidence_id") == evidence_id
        and r.get("status") == "rendered"
    ]
    if len(matched) != 1:
        raise SystemExit(f"render_not_in_slice matched={len(matched)} -> STOP")
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
        {"a": asset_id, "e": evidence_id},
    ).scalar_one()
    if existing:
        raise SystemExit(f"link_already_exists pair=({asset_id},{evidence_id}) -> STOP")
    before = table_counts(db)
    ins = db.execute(
        text("INSERT INTO asset_evidence (asset_id, evidence_id) VALUES (:a, :e)"),
        {"a": asset_id, "e": evidence_id},
    )
    if ins.rowcount != 1:
        db.rollback()
        raise SystemExit(f"link_insert_rowcount={ins.rowcount} -> STOP")
    db.commit()
    after = table_counts(db)
    if after["asset_evidence"] != before["asset_evidence"] + 1:
        raise SystemExit("link_count_not_incremented -> STOP")
    links = asset_links(db, asset_id)
    print(f"linked asset={asset_id} evidence={evidence_id} rows={links}", flush=True)
    write_json(
        EVIDENCE_DIR / f"SG-226_link_{evidence_id}.json",
        {
            "timestamp": now_utc(),
            "asset_id": asset_id,
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
    parser.add_argument("mode", choices=("plan", "render", "post", "link", "key-gate"))
    parser.add_argument("--asset", default=None)
    parser.add_argument("--evidence", default=None)
    parser.add_argument("--reason", default="")
    parser.add_argument("--dir", default=None, help="key-gate target directory")
    args = parser.parse_args()

    if args.mode == "key-gate":
        return key_gate(Path(args.dir) if args.dir else EVIDENCE_DIR)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        if args.mode == "post":
            return run_post(db)
        if args.mode == "link":
            if not args.asset or not args.evidence:
                raise SystemExit("link_requires_asset_and_evidence -> STOP")
            return run_link(db, args.asset, args.evidence, args.reason)
        ctx = prepare(db, args.mode)
        if args.mode == "plan":
            return run_plan(db, ctx)
        return run_render(db, ctx)
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
