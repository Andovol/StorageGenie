#!/usr/bin/env python3
"""SG-182 G1 — served bundle/schema/config identification via read-only surfaces.

GET-only against the deployed loopback service (read-only observations) and a
mode=ro sqlite connection to the host-side production DB file for schema
metadata ONLY (alembic_version; no user rows, no writes). Container/image
identity remains UNVERIFIED without Docker (excluded by the packet).
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8003"
PROD_DB = Path("/home/andrei/StorageGenie/data/db/storagegenie.db")
CHECKS = 0
FAILS = 0


def expect(condition: bool, label: str, detail: str = "") -> None:
    global CHECKS, FAILS
    CHECKS += 1
    status = "PASS" if condition else "FAIL"
    if not condition:
        FAILS += 1
    print(f"[{status}] {label} {detail}".rstrip(), flush=True)


def fetch(path: str) -> tuple[int, bytes]:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=15) as response:
        return response.status, response.read()


def main() -> int:
    status, index = fetch("/")
    expect(status == 200, "GET / served", f"status={status} bytes={len(index)}")
    print(f"[value] index.html sha256={hashlib.sha256(index).hexdigest()}", flush=True)
    assets = sorted(set(re.findall(rb'(?:src|href)="(/assets/[^"]+)"', index)))
    expect(len(assets) > 0, "served index references built assets", f"count={len(assets)}")
    for asset in assets:
        asset_status, body = fetch(asset.decode())
        print(f"[value] served asset {asset.decode()} status={asset_status} "
              f"bytes={len(body)} sha256={hashlib.sha256(body).hexdigest()}", flush=True)
        expect(asset_status == 200, f"served asset fetch {asset.decode()}")

    status, ai = fetch("/v1/settings/ai")
    expect(status == 200, "GET /v1/settings/ai effective deployment AI config", f"status={status}")
    print(f"[value] effective AI settings: {json.dumps(json.loads(ai), sort_keys=True)}", flush=True)

    status, health = fetch("/v1/health")
    expect(status == 200, "GET /v1/health", health.decode())

    print(f"[value] production DB file readable: {PROD_DB.exists()}", flush=True)
    connection = sqlite3.connect(f"file:{PROD_DB}?mode=ro", uri=True)
    try:
        version = connection.execute("SELECT version_num FROM alembic_version").fetchall()
        tables = connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
    finally:
        connection.close()
    print(f"[value] served schema: alembic_version={version} table_count={tables}", flush=True)
    expect(len(version) == 1, "production schema identifies exactly one alembic head", str(version))

    print(f"[summary] checks={CHECKS} fails={FAILS}", flush=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
