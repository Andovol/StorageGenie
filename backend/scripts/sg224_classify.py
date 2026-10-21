#!/usr/bin/env python3
"""SG-224 — D-30: classify the five stale null-cost OpenRouter ledger rows.

Modes:
  run       derive the live null-cost set, prove each row is a $0 error row,
            UPDATE cost NULL -> 0.0 on exactly those five rows (one
            transaction, per-statement changes()=1, ROLLBACK on any mismatch),
            then re-read scene_spend_so_far and re-run the guard projection.
  key-gate  scan SG-224 artifacts + this driver for the live OpenRouter key.

Lane-run tooling, not served code. No sends, no renders, no billed calls,
no INSERT, no DELETE, no migration. The driver runs on the live SQLite bind
named by the project's DATABASE_URL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from app.config import settings
from app.db import SessionLocal
from app.services.scene import openrouter as scene

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = Path(os.environ.get("SG224_EVIDENCE_DIR", REPO_ROOT / "docs/worklogs"))
EXPECTED_DB = (REPO_ROOT / "data/db/storagegenie.db").resolve()
PILOT_DECISION = REPO_ROOT / "docs/decisions/2026-10-21-d27-bounded-pilot.md"
FIRST_SPEND_EVIDENCE = REPO_ROOT / "docs/worklogs/SG-216_g1_key_body.json"
SG219_PRE_SPEND = REPO_ROOT / "docs/worklogs/SG-219_spend_body_render3.json"
SG219_POST_SPEND = REPO_ROOT / "docs/worklogs/SG-219_post_spend_body_render3.json"
SG223_POST_ALL = REPO_ROOT / "docs/worklogs/SG-223_post_spend_final.json"
PRICING_URL = "https://openrouter.ai/api/v1/images/models/google/gemini-3.1-flash-image/endpoints"
IMAGE_TOKENS_BASELINE = 1290
TOKEN_MULTIPLIER = 2
PILOT_RENDERS = 10
CAP_DAILY_USD = 2.00
CAP_MONTHLY_USD = 10.00
GRANT_ID = "D-30 classify (no send) + D-20 + D-14"

EXPECTED_ROWS = (
    ("01a12118-ce4b-79b3-88f8-c289e18d15a2", "http_status:404", 404),
    ("01a12119-de97-7a71-803c-cd17fb237c7c", "http_status:404", 404),
    ("01a13082-aadb-7602-b9dd-f4d48bf9b720", "http_status:429", 429),
    ("01a13084-4367-7ad2-9984-bc7179dfb4f3", "http_status:429", 429),
    ("01a15fe8-aa48-7830-86ec-b3725b611639", "http_status:400", 400),
)
SPEND_FIELDS = (
    "usage",
    "usage_daily",
    "usage_monthly",
    "limit",
    "limit_remaining",
    "effective_budget",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_text(path: Path, value: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(value, encoding="utf-8")
    os.replace(tmp, path)


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, indent=1, sort_keys=True, default=str) + "\n")


def table_counts(db) -> dict[str, int]:
    tables = [
        r[0]
        for r in db.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        )
    ]
    return {t: int(db.execute(text(f'SELECT count(*) FROM "{t}"')).scalar_one()) for t in tables}


def provider_snapshot(db) -> list[dict]:
    rows = db.execute(
        text(
            "SELECT id, provider, model, prompt_template_version, cost, "
            "usage_json, error_state, created_at, updated_at "
            "FROM provider_call ORDER BY id"
        )
    ).mappings()
    return [dict(r) for r in rows]


def snapshot_sha(rows: list[dict]) -> str:
    return hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def git_commit_time(path: Path) -> dict:
    rel = str(path.relative_to(REPO_ROOT))
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%H%x09%cI", "--", rel],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        raise SystemExit(f"git_log_failed path={rel} stderr={proc.stderr.strip()!r} -> STOP")
    commit, stamp = proc.stdout.strip().split("\t", 1)
    return {"path": rel, "commit": commit, "committed_at": stamp}


def keys_named(obj: object, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in ("usage", "cost", "cost_usd", "usage_json"):
                hits.append(f"{path}/{key}")
            hits.extend(keys_named(value, f"{path}/{key}"))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            hits.extend(keys_named(value, f"{path}[{index}]"))
    return hits


def live_guard_projection(
    db, worst: float, cap: float
) -> tuple[tuple[float, int], dict]:
    spent, unknown = scene.scene_spend_so_far(db)
    authority = scene.SceneSpendAuthority(grant_id=GRANT_ID, cap_usd=cap)
    refusal = scene.guard_render_spend(
        spent_usd=spent,
        unknown_cost_calls=unknown,
        worst_case_usd=worst,
        authority=authority,
    )
    proof = {
        "timestamp": now_utc(),
        "spent_usd": spent,
        "unknown_cost_calls": unknown,
        "worst_case_usd": worst,
        "cap_usd": cap,
        "projected_all_in": spent + unknown * worst + worst,
        "verdict": "proceed" if refusal is None else "refused",
        "refusal": (
            None if refusal is None else {"code": refusal.code, "reason": refusal.reason}
        ),
    }
    return (spent, unknown), proof


def derive_null_rows(db) -> list[dict]:
    rows = db.execute(
        text(
            "SELECT id, provider, model, prompt_template_version, input_hashes, "
            "output_payload, cost, usage_json, latency_ms, error_state, "
            "created_at, updated_at FROM provider_call "
            "WHERE provider = :p AND cost IS NULL ORDER BY created_at, id"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER},
    ).mappings()
    return [dict(r) for r in rows]


def prove_rows(db, null_rows: list[dict]) -> dict:  # noqa: C901
    derived = [(str(r["id"]), r["error_state"]) for r in null_rows]
    expected = [(row[0], row[1]) for row in EXPECTED_ROWS]
    if derived != expected:
        raise SystemExit(f"null_set_differs derived={derived} expected={expected} -> STOP")

    other_null = int(
        db.execute(
            text("SELECT count(*) FROM provider_call WHERE cost IS NULL")
        ).scalar_one()
    )
    if other_null != len(EXPECTED_ROWS):
        raise SystemExit(f"null_rows_total={other_null} -> STOP")

    first_spend = git_commit_time(FIRST_SPEND_EVIDENCE)
    sg219_pre = json.loads(SG219_PRE_SPEND.read_text(encoding="utf-8"))
    sg219_post = json.loads(SG219_POST_SPEND.read_text(encoding="utf-8"))
    if SG219_PRE_SPEND.read_bytes() != SG219_POST_SPEND.read_bytes():
        raise SystemExit("sg219_pre_post_spend_bytes_differ -> STOP")
    sg223_post = json.loads(SG223_POST_ALL.read_text(encoding="utf-8"))
    known, unknown = scene.scene_spend_so_far(db)
    if float(sg223_post.get("usage")) != known:
        raise SystemExit(
            f"key_spend_cumulative_differs key={sg223_post.get('usage')} known={known} -> STOP"
        )

    proofs = []
    for row in null_rows:
        body = json.loads(row["output_payload"])
        if row["usage_json"] is not None:
            raise SystemExit(f"usage_object_present id={row['id']} -> STOP")
        if row["cost"] is not None:
            raise SystemExit(f"row_already_billed id={row['id']} -> STOP")
        hits = keys_named(body)
        if hits:
            raise SystemExit(f"usage_or_cost_in_body id={row['id']} hits={hits} -> STOP")
        if int(body.get("status_code")) != int(str(row["error_state"]).split(":")[-1]):
            raise SystemExit(f"status_mismatch id={row['id']} -> STOP")
        if body.get("response_id") is not None:
            raise SystemExit(f"response_id_present id={row['id']} -> STOP")

        if row["id"] in {r[0] for r in EXPECTED_ROWS[:4]}:
            if str(row["created_at"]) >= first_spend["committed_at"]:
                raise SystemExit(f"row_not_predating_spend_log id={row['id']} -> STOP")
            spend_proof = {
                "kind": "predates_spend_logging",
                "first_logged_spend_evidence": first_spend,
                "row_created_at": str(row["created_at"]),
                "statement": (
                    "The call predates spend logging; the row's own body is the "
                    "whole proof."
                ),
            }
        else:
            if str(row["created_at"]) < "2026-10-21 19:20:40":
                raise SystemExit(f"sg219_row_precedes_keys id={row['id']} -> STOP")
            spend_proof = {
                "kind": "pre_post_key_spend_identical",
                "pre": {
                    "path": str(SG219_PRE_SPEND.relative_to(REPO_ROOT)),
                    "fields": {k: sg219_pre.get(k) for k in SPEND_FIELDS},
                    "sha256": hashlib.sha256(SG219_PRE_SPEND.read_bytes()).hexdigest(),
                },
                "post": {
                    "path": str(SG219_POST_SPEND.relative_to(REPO_ROOT)),
                    "fields": {k: sg219_post.get(k) for k in SPEND_FIELDS},
                    "sha256": hashlib.sha256(SG219_POST_SPEND.read_bytes()).hexdigest(),
                },
                "byte_identical": True,
            }

        proofs.append(
            {
                "id": row["id"],
                "error_state": row["error_state"],
                "status_code": int(body.get("status_code")),
                "created_at": str(row["created_at"]),
                "provider": row["provider"],
                "model": row["model"],
                "cost_pre": row["cost"],
                "usage_json": row["usage_json"],
                "body_usage_or_cost_keys": hits,
                "error_quoted": body.get("error_body") or body.get("response_body"),
                "error_absent_note": (
                    "No error_body was stored for this 404 row; the stored payload "
                    "carries status_code=404 and response_id=null, and error_state "
                    "is http_status:404."
                    if body.get("error_body") is None
                    and body.get("response_body") is None
                    else None
                ),
                "spend_proof": spend_proof,
            }
        )
    return {
        "derived_null_set": [
            {"id": r["id"], "error_state": r["error_state"], "created_at": str(r["created_at"])}
            for r in null_rows
        ],
        "expected_set": [
            {"id": i, "error_state": e, "status_code": s} for i, e, s in EXPECTED_ROWS
        ],
        "null_rows_all_providers": other_null,
        "known_usd_pre": known,
        "unknown_cost_calls_pre": unknown,
        "cumulative_key_spend_crosscheck": {
            "source": str(SG223_POST_ALL.relative_to(REPO_ROOT)),
            "usage": sg223_post.get("usage"),
            "equals_known_sum": True,
            "note": (
                "Read after all five null rows existed (SG-223 final spend body, "
                "2026-10-21T20:12:44Z); it equals the sum of known costs exactly."
            ),
        },
        "rows": proofs,
    }


def fetch_pricing() -> tuple[dict, dict]:
    request = urllib.request.Request(PRICING_URL, method="GET")
    with urllib.request.urlopen(request, timeout=60) as response:
        status = response.status
        raw = response.read()
    if status != 200:
        raise SystemExit(f"pricing_read_failed http_status:{status} -> STOP")
    body = json.loads(raw)
    write_text(EVIDENCE_DIR / "SG-224_pricing_body.json", raw.decode("utf-8"))

    lines = []
    max_price = None
    for endpoint in body.get("endpoints", []):
        for line in endpoint.get("pricing", []):
            if not isinstance(line, dict) or line.get("billable") is False:
                continue
            if "token" not in str(line.get("unit") or "").lower():
                continue
            price = line.get("cost_usd")
            if not isinstance(price, (int, float)):
                continue
            lines.append({"provider_slug": endpoint.get("provider_slug"), "cost_usd": price})
            if max_price is None or price > max_price:
                max_price = price
    if max_price is None:
        raise SystemExit("pricing_missing -> STOP (fail closed)")
    tokens = IMAGE_TOKENS_BASELINE * TOKEN_MULTIPLIER
    worst = tokens * float(max_price)
    detail = {
        "timestamp": now_utc(),
        "url": PRICING_URL,
        "http_status": status,
        "pricing_lines": lines,
        "max_live_price": max_price,
        "baseline_tokens": IMAGE_TOKENS_BASELINE,
        "multiplier": TOKEN_MULTIPLIER,
        "tokens": tokens,
        "worst_case_usd": worst,
        "source": "live pricing body committed as SG-224_pricing_body.json",
    }
    return body, detail


def owner_upstream_totals(db) -> tuple[float, float, list[dict]]:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    month = today[:7]
    rows = db.execute(
        text(
            "SELECT id, created_at, usage_json FROM provider_call "
            "WHERE provider = :p AND usage_json IS NOT NULL"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER},
    ).mappings()
    today_sum = 0.0
    month_sum = 0.0
    detail = []
    for row in rows:
        usage = json.loads(row["usage_json"])
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


def pilot_state(db, worst: float) -> dict:
    cutoff = f"{PILOT_DECISION.name[:10]} 00:00:00"
    rows = db.execute(
        text(
            "SELECT id, cost, error_state, created_at FROM provider_call "
            "WHERE provider = :p AND cost IS NOT NULL AND created_at >= :c "
            "ORDER BY created_at, id"
        ),
        {"p": scene.SCENE_LEDGER_PROVIDER, "c": cutoff},
    ).mappings()
    picked = [dict(r) for r in rows]
    rendered = sum(1 for r in picked if r["error_state"] is None)
    non_null = len(picked)
    helper_consumed = max(rendered, non_null)
    return {
        "decision_record": str(PILOT_DECISION.relative_to(REPO_ROOT)),
        "cutoff": cutoff,
        "rows_with_non_null_cost": picked,
        "rendered_rows": rendered,
        "non_null_cost_rows": non_null,
        "helper_pilot_consumed": helper_consumed,
        "helper_pilot_cap_usd": (PILOT_RENDERS - helper_consumed) * worst,
        "d27_billed_renders_consumed": rendered,
        "d27_pilot_remainder_cap_usd": (PILOT_RENDERS - rendered) * worst,
        "note": (
            "After classification the SG-219 400 row carries cost=0.0 and is "
            "therefore counted by the repo's non-null-cost proxy as a billed row; "
            "it was unbilled (HTTP 400, no usage). D-27 consumption remains the "
            "four rendered rows, so the packet's pilot-remainder cap uses 10-4."
        ),
    }


def update_rows(db, proofs: list[dict]) -> dict:
    started = now_utc()
    statements = []
    try:
        for proof in proofs:
            result = db.execute(
                text(
                    "UPDATE provider_call SET cost = 0.0 "
                    "WHERE id = :id AND provider = 'openrouter' "
                    "AND cost IS NULL AND error_state = :err"
                ),
                {"id": proof["id"], "err": proof["error_state"]},
            )
            changes = int(db.execute(text("SELECT changes()")).scalar_one())
            rowcount = int(result.rowcount)
            print(
                f"[{now_utc()}] update id={proof['id']} changes={changes} "
                f"rowcount={rowcount}",
                flush=True,
            )
            statements.append(
                {
                    "id": proof["id"],
                    "error_state": proof["error_state"],
                    "changes": changes,
                    "rowcount": rowcount,
                    "pre_cost": proof["cost_pre"],
                    "sql": (
                        "UPDATE provider_call SET cost = 0.0 WHERE id = :id "
                        "AND provider = 'openrouter' AND cost IS NULL "
                        "AND error_state = :err"
                    ),
                }
            )
            if changes != 1 or rowcount != 1:
                db.rollback()
                print(f"[{now_utc()}] ROLLBACK changes={changes} rowcount={rowcount}", flush=True)
                return {
                    "transaction_started": started,
                    "transaction_finished": now_utc(),
                    "committed": False,
                    "rolled_back": True,
                    "statements": statements,
                    "stop": f"statement_affected_{changes}_{rowcount}",
                }
        remaining = int(
            db.execute(
                text(
                    "SELECT count(*) FROM provider_call WHERE provider = 'openrouter' "
                    "AND cost IS NULL"
                )
            ).scalar_one()
        )
        if remaining != 0:
            db.rollback()
            print(f"[{now_utc()}] ROLLBACK lingering_null={remaining}", flush=True)
            return {
                "transaction_started": started,
                "transaction_finished": now_utc(),
                "committed": False,
                "rolled_back": True,
                "statements": statements,
                "stop": f"lingering_null_rows_{remaining}",
            }
        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"[{now_utc()}] ROLLBACK exception={type(exc).__name__}", flush=True)
        return {
            "transaction_started": started,
            "transaction_finished": now_utc(),
            "committed": False,
            "rolled_back": True,
            "statements": statements,
            "stop": f"exception_{type(exc).__name__}",
        }
    finished = now_utc()
    print(f"[{now_utc()}] COMMIT statements={len(statements)}", flush=True)
    return {
        "transaction_started": started,
        "transaction_finished": finished,
        "committed": True,
        "rolled_back": False,
        "statements": statements,
        "discipline": (
            "One SessionLocal (autocommit=False, the app's own convention): the "
            "five UPDATEs share one transaction and one commit; any changes()!=1 "
            "or a lingering null row rolls the whole transaction back."
        ),
    }


def key_gate() -> int:
    key = scene.resolve_openrouter_key()
    if not key:
        print("key_gate missing_key -> cannot scan", flush=True)
        return 2
    raw_key = key.encode("utf-8")
    targets = sorted(EVIDENCE_DIR.glob("SG-224_*")) + [Path(__file__).resolve()]
    scanned = 0
    matching = 0
    for path in targets:
        if not path.is_file() or path.name.endswith(".tmp"):
            continue
        data = path.read_bytes()
        scanned += 1
        if raw_key in data:
            matching += len(raw_key)
            print(f"key_gate_MATCH {path}", flush=True)
    print(f"key_gate scanned_files={scanned} matching_bytes={matching}", flush=True)
    return 1 if matching else 0


def finalize_post(  # noqa: C901
    db,
    *,
    counts_pre: dict,
    snapshot_pre: list[dict] | None,
    spend_pre: tuple[float, int],
    pre_rows: list[dict],
    pricing: dict,
    cap: float,
    pilot_pre: dict | None,
    wall_pre: dict,
) -> None:
    counts_post = table_counts(db)
    if counts_pre != counts_post:
        raise SystemExit(f"table_counts_changed pre={counts_pre} post={counts_post} -> STOP")
    snapshot_post = provider_snapshot(db)
    pre_sha = (
        snapshot_sha(snapshot_pre)
        if snapshot_pre is not None
        else json.loads((EVIDENCE_DIR / "SG-224_pre_state.json").read_text())[
            "provider_call_snapshot_sha256"
        ]
    )
    if snapshot_pre is not None and snapshot_sha(snapshot_pre) != pre_sha:
        raise SystemExit("pre_snapshot_sha_mismatch -> STOP")
    target_ids = {row[0] for row in EXPECTED_ROWS}
    reverted = [
        dict(row, cost=None) if row["id"] in target_ids else row for row in snapshot_post
    ]
    if snapshot_sha(reverted) != pre_sha:
        raise SystemExit("revert_five_costs_does_not_reproduce_pre_snapshot -> STOP")
    spend_post = scene.scene_spend_so_far(db)
    if spend_post[1] != 0:
        raise SystemExit(f"unknown_after={spend_post[1]} -> STOP")
    if abs(spend_post[0] - spend_pre[0]) > 1e-12:
        raise SystemExit(f"known_changed pre={spend_pre[0]} post={spend_post[0]} -> STOP")

    pre_map = {row["id"]: row for row in pre_rows}
    current = [
        dict(r)
        for r in db.execute(
            text(
                "SELECT id, provider, model, prompt_template_version, input_hashes, "
                "output_payload, cost, usage_json, latency_ms, error_state, job_id, "
                "created_at, updated_at FROM provider_call WHERE id IN ("
                + ",".join(f"'{row[0]}'" for row in EXPECTED_ROWS)
                + ") ORDER BY created_at, id"
            )
        ).mappings()
    ]
    if {r["id"] for r in current} != target_ids or len(current) != len(EXPECTED_ROWS):
        raise SystemExit(f"classified_row_set={[r['id'] for r in current]} -> STOP")
    changed = []
    for row in current:
        pre = pre_map[row["id"]]
        if row["cost"] != 0.0 or pre["cost"] is not None:
            raise SystemExit(f"cost_not_null_to_zero id={row['id']} -> STOP")
        for field in (
            "provider",
            "model",
            "prompt_template_version",
            "input_hashes",
            "output_payload",
            "usage_json",
            "latency_ms",
            "error_state",
            "created_at",
            "updated_at",
        ):
            if row[field] != pre[field]:
                raise SystemExit(f"non_cost_field_changed id={row['id']} field={field} -> STOP")
        changed.append(
            {
                "id": row["id"],
                "pre_cost": pre["cost"],
                "post_cost": row["cost"],
                "error_state": row["error_state"],
                "updated_at": str(row["updated_at"]),
                "other_fields_unchanged": True,
            }
        )

    pricing_proof = pricing
    pilot_post = pilot_state(db, pricing_proof["worst_case_usd"])
    _, guard_post = live_guard_projection(db, pricing_proof["worst_case_usd"], cap)
    over = scene.guard_render_spend(
        spent_usd=cap + 1.0,
        unknown_cost_calls=0,
        worst_case_usd=pricing_proof["worst_case_usd"],
        authority=scene.SceneSpendAuthority(grant_id=GRANT_ID, cap_usd=cap),
    )
    no_authority = scene.guard_render_spend(
        spent_usd=0.0,
        unknown_cost_calls=0,
        worst_case_usd=pricing_proof["worst_case_usd"],
        authority=None,
    )
    if guard_post["verdict"] != "proceed":
        raise SystemExit(f"guard_post={guard_post} -> STOP")
    if over is None or over.code != "over_cap":
        raise SystemExit(f"guard_selftest_over={over} -> STOP")
    if no_authority is None or no_authority.code != "refused_consent":
        raise SystemExit(f"guard_selftest_no_authority={no_authority} -> STOP")
    owner_today, owner_month, owner_detail = owner_upstream_totals(db)
    if owner_today > CAP_DAILY_USD:
        raise SystemExit(f"owner_daily_cap_crossed today={owner_today} -> STOP")
    if owner_month > CAP_MONTHLY_USD:
        raise SystemExit(f"owner_monthly_cap_crossed month={owner_month} -> STOP")
    print(
        f"[{now_utc()}] guard_post spent={guard_post['spent_usd']} "
        f"unknown={guard_post['unknown_cost_calls']} projected="
        f"{guard_post['projected_all_in']:.9f} cap={guard_post['cap_usd']:.8f} "
        f"verdict={guard_post['verdict']}",
        flush=True,
    )
    print(f"[{now_utc()}] guard_selftest_over_cap={(over.code, over.reason)}", flush=True)
    print(f"[{now_utc()}] guard_selftest_no_authority={no_authority.code}", flush=True)
    print(
        f"[{now_utc()}] owner_side today={owner_today:.9f} month={owner_month:.9f} "
        f"caps={CAP_DAILY_USD:.2f}/{CAP_MONTHLY_USD:.2f}",
        flush=True,
    )

    pre_pilot = pilot_pre or {
        "reconstructed": True,
        "d27_billed_renders_consumed": pilot_post["rendered_rows"],
        "d27_pilot_remainder_cap_usd": cap,
        "note": (
            "Pre-update pilot state reconstructed from post rows: the SG-219 400 "
            "row carried cost NULL and was not counted by the non-null proxy; "
            "the four rendered rows remain."
        ),
    }
    write_json(
        EVIDENCE_DIR / "SG-224_guard_proof.json",
        {
            "pre_wall": wall_pre,
            "post": guard_post,
            "pilot_cap_pre": pre_pilot,
            "pilot_post_classification": pilot_post,
            "synthetic_over_cap": {"code": over.code, "reason": over.reason},
            "synthetic_no_authority": {"code": no_authority.code},
        },
    )
    write_json(
        EVIDENCE_DIR / "SG-224_post_state.json",
        {
            "timestamp": now_utc(),
            "database_url": settings.database_url,
            "resolved_store": str(Path(settings.database_url.replace("sqlite:///", "")).resolve()),
            "table_counts": counts_post,
            "table_counts_unchanged": True,
            "provider_call_snapshot_sha256_pre": pre_sha,
            "provider_call_snapshot_sha256_post": snapshot_sha(snapshot_post),
            "revert_five_costs_equals_pre_snapshot": True,
            "scene_spend_so_far": {
                "known_usd": spend_post[0],
                "known_unchanged": abs(spend_post[0] - spend_pre[0]) <= 1e-12,
                "unknown_cost_calls": spend_post[1],
            },
            "classified_rows": current,
            "changed_rows": changed,
            "other_rows_changed": 0,
            "owner_side": {
                "today_usd": owner_today,
                "month_usd": owner_month,
                "daily_cap_usd": CAP_DAILY_USD,
                "monthly_cap_usd": CAP_MONTHLY_USD,
                "slice_actual_usd": 0.0,
                "rows": owner_detail,
            },
        },
    )
    print(
        f"[{now_utc()}] post_counts provider_call={counts_post['provider_call']} "
        f"scene_spend_post={spend_post}",
        flush=True,
    )


def main() -> int:  # noqa: C901
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "post", "key-gate"))
    args = parser.parse_args()
    if args.mode == "key-gate":
        return key_gate()

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    resolved = Path(settings.database_url.replace("sqlite:///", "")).resolve()
    print(
        f"[{now_utc()}] SG-224 mode={args.mode} database_url={settings.database_url} "
        f"resolved={resolved} expected={EXPECTED_DB}",
        flush=True,
    )
    if resolved != EXPECTED_DB or not resolved.is_file():
        raise SystemExit(f"store_mismatch resolved={resolved} -> STOP")

    db = SessionLocal()
    try:
        if args.mode == "post":
            pre_state = json.loads((EVIDENCE_DIR / "SG-224_pre_state.json").read_text())
            wall_pre = json.loads((EVIDENCE_DIR / "SG-224_guard_pre.json").read_text())
            pricing = json.loads((EVIDENCE_DIR / "SG-224_pricing_proof.json").read_text())
            pre_rows = json.loads((EVIDENCE_DIR / "SG-224_null_rows_pre.json").read_text())
            finalize_post(
                db,
                counts_pre=pre_state["table_counts"],
                snapshot_pre=None,
                spend_pre=(
                    pre_state["scene_spend_so_far"]["known_usd"],
                    pre_state["scene_spend_so_far"]["unknown_cost_calls"],
                ),
                pre_rows=pre_rows,
                pricing=pricing,
                cap=wall_pre["cap_usd"],
                pilot_pre=None,
                wall_pre=wall_pre,
            )
            return 0
        counts_pre = table_counts(db)
        snapshot_pre = provider_snapshot(db)
        spend_pre = scene.scene_spend_so_far(db)
        print(f"[{now_utc()}] scene_spend_pre={spend_pre}", flush=True)
        write_json(
            EVIDENCE_DIR / "SG-224_pre_state.json",
            {
                "timestamp": now_utc(),
                "database_url": settings.database_url,
                "resolved_store": str(resolved),
                "table_counts": counts_pre,
                "provider_call_snapshot_sha256": snapshot_sha(snapshot_pre),
                "scene_spend_so_far": {
                    "known_usd": spend_pre[0],
                    "unknown_cost_calls": spend_pre[1],
                },
            },
        )

        null_rows = derive_null_rows(db)
        print(f"[{now_utc()}] null_cost_rows={len(null_rows)}", flush=True)
        proof = prove_rows(db, null_rows)
        write_json(EVIDENCE_DIR / "SG-224_null_rows_pre.json", null_rows)
        write_json(EVIDENCE_DIR / "SG-224_proof.json", proof)
        for row in proof["rows"]:
            print(
                f"[{now_utc()}] proved id={row['id']} error={row['error_state']} "
                f"spend_proof={row['spend_proof']['kind']}",
                flush=True,
            )

        pricing_body, pricing = fetch_pricing()
        write_json(EVIDENCE_DIR / "SG-224_pricing_proof.json", pricing)
        print(
            f"[{now_utc()}] worst_case_usd={pricing['worst_case_usd']:.8f} "
            f"max_price={pricing['max_live_price']} tokens={pricing['tokens']}",
            flush=True,
        )

        pilot_pre = pilot_state(db, pricing["worst_case_usd"])
        cap = pilot_pre["d27_pilot_remainder_cap_usd"]
        _, wall_pre = live_guard_projection(db, pricing["worst_case_usd"], cap)
        write_json(EVIDENCE_DIR / "SG-224_guard_pre.json", wall_pre)
        print(
            f"[{now_utc()}] guard_pre spent={wall_pre['spent_usd']} "
            f"unknown={wall_pre['unknown_cost_calls']} projected="
            f"{wall_pre['projected_all_in']:.9f} cap={wall_pre['cap_usd']:.8f} "
            f"verdict={wall_pre['verdict']}",
            flush=True,
        )

        write_log = update_rows(db, proof["rows"])
        write_json(EVIDENCE_DIR / "SG-224_write_log.json", write_log)
        if not write_log["committed"]:
            raise SystemExit(f"write_failed {write_log['stop']} -> STOP")

        finalize_post(
            db,
            counts_pre=counts_pre,
            snapshot_pre=snapshot_pre,
            spend_pre=spend_pre,
            pre_rows=null_rows,
            pricing=pricing,
            cap=cap,
            pilot_pre=pilot_pre,
            wall_pre=wall_pre,
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
