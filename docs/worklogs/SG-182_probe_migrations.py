#!/usr/bin/env python3
"""SG-182 G1 — real alembic upgrade path on a fresh disposable DB + real readers.

Enumerates revision history/heads from backend/alembic/versions, upgrades a
fresh isolated SQLite DB to the single head with ONLY DATABASE_URL/STORAGE_ROOT
env overrides (proving env.py's settings override of alembic.ini line 3), then
reopens the DB, checks alembic_version/integrity/schema against Base.metadata,
runs the runbook seed, and drives the REAL FastAPI app readers via TestClient.
The ini-path DB under backend/data must NOT appear — a discriminating control
that the override was effective. All state under a fresh /tmp/opencode scratch.
"""

from __future__ import annotations

import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path("/home/andrei/StorageGenie")
BACKEND = REPO / "backend"
VENV_PY = BACKEND / "venv" / "bin" / "python"
VERSIONS = BACKEND / "alembic" / "versions"
SCRATCH_ROOT = Path("/tmp/opencode")
INI_PATH_DB = BACKEND / "data" / "db" / "storagegenie.db"

CHECKS = 0
FAILS = 0


def expect(condition: bool, label: str, detail: str = "") -> None:
    global CHECKS, FAILS
    CHECKS += 1
    status = "PASS" if condition else "FAIL"
    if not condition:
        FAILS += 1
    print(f"[{status}] {label} {detail}".rstrip(), flush=True)


def guarded_cleanup(path: Path) -> None:
    resolved = path.resolve()
    root = SCRATCH_ROOT.resolve()
    if resolved == root or root not in resolved.parents:
        raise SystemExit(f"refusing cleanup outside scratch root: {resolved}")
    shutil.rmtree(resolved)
    print(f"[cleanup] removed verified scratch target {resolved}", flush=True)


def revision_graph() -> tuple[dict[str, str | None], set[str]]:
    graph: dict[str, str | None] = {}
    for path in sorted(VERSIONS.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        revision = re.search(r'^revision: str = ["\']([^"\']+)["\']', text, re.MULTILINE)
        down = re.search(r'^down_revision: Union\[str, None\] = (?:None|["\']([^"\']+)["\'])',
                         text, re.MULTILINE)
        if revision:
            graph[revision.group(1)] = down.group(1) if (down and down.group(1)) else None
    downs = {value for value in graph.values() if value}
    heads = sorted(set(graph) - downs)
    return graph, set(heads)


def main() -> int:
    scratch = Path(tempfile.mkdtemp(prefix="sg182-mig-", dir=SCRATCH_ROOT))
    print(f"[phase] scratch root = {scratch}", flush=True)
    fresh_db = scratch / "fresh.db"
    storage = scratch / "storage"
    storage.mkdir()

    env = dict(os.environ)
    env["DATABASE_URL"] = f"sqlite:///{fresh_db}"
    env["STORAGE_ROOT"] = str(storage)
    env.pop("OPENCODE_API_KEY", None)
    env.pop("JINA_API_KEY", None)
    env.pop("OPENROUTER_API_KEY", None)
    os.environ.update({"DATABASE_URL": env["DATABASE_URL"], "STORAGE_ROOT": env["STORAGE_ROOT"]})
    os.environ.pop("OPENCODE_API_KEY", None)
    os.environ.pop("JINA_API_KEY", None)
    os.environ.pop("OPENROUTER_API_KEY", None)

    def run(args: list[str], label: str) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [str(VENV_PY), *args], cwd=BACKEND, env=env, capture_output=True, text=True,
            timeout=600,
        )
        print(f"----- {label} (rc={result.returncode}) -----", flush=True)
        print(result.stdout, flush=True)
        if result.stderr:
            print("[stderr]", result.stderr, flush=True)
        return result

    graph, heads = revision_graph()
    expect(len(heads) == 1, "revision graph has exactly one head", f"heads={sorted(heads)} revisions={len(graph)}")
    expected_head = sorted(heads)[0]
    print(f"[value] linear chain length={len(graph)} head={expected_head}", flush=True)

    ini_before = INI_PATH_DB.exists()
    history = run(["-m", "alembic", "history"], "alembic history")
    expect(history.returncode == 0, "alembic history rc=0")
    heads_run = run(["-m", "alembic", "heads"], "alembic heads")
    expect(heads_run.returncode == 0 and expected_head in heads_run.stdout,
           "alembic heads agrees with source-derived head", heads_run.stdout.strip())

    upgrade = run(["-m", "alembic", "upgrade", "head"], "alembic upgrade head (fresh isolated DB)")
    expect(upgrade.returncode == 0, "fresh upgrade to head rc=0")
    expect("Running upgrade" in upgrade.stderr or "Running upgrade" in upgrade.stdout,
           "upgrade executed real revision steps (alembic logs on stderr)")
    rerun = run(["-m", "alembic", "upgrade", "head"], "alembic upgrade head (idempotent rerun)")
    expect(rerun.returncode == 0 and "Running upgrade" not in rerun.stdout
           and "Running upgrade" not in rerun.stderr,
           "second upgrade head is a no-op (already at head; both streams checked)")
    expect(INI_PATH_DB.exists() == ini_before,
           "settings override effective: ini-path DB not created", f"ini_path_db_exists={INI_PATH_DB.exists()}")

    with sqlite3.connect(fresh_db) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        version_rows = connection.execute("SELECT version_num FROM alembic_version").fetchall()
        table_names = sorted(
            row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        )
    expect(integrity == "ok", "upgraded DB integrity_check", integrity)
    expect(version_rows == [(expected_head,)], "DB alembic_version == expected head", str(version_rows))
    print(f"[value] upgraded tables ({len(table_names)}): {table_names}", flush=True)

    sys.path.insert(0, str(BACKEND))
    os.chdir(scratch)  # avoid root .env pickup; env vars already win, this is belt+braces
    from sqlalchemy import create_engine

    from app.config import settings
    from app.db import Base
    import app.models  # noqa: F401  (populate metadata)

    expect(settings.database_url == env["DATABASE_URL"], "settings.database_url == scratch override",
           settings.database_url)

    reference_db = scratch / "reference.db"
    reference_engine = create_engine(f"sqlite:///{reference_db}")
    Base.metadata.create_all(reference_engine)
    metadata_tables = sorted(Base.metadata.tables)
    schema_gaps = []
    with sqlite3.connect(fresh_db) as migrated, sqlite3.connect(reference_db) as reference:
        for table in metadata_tables:
            ref_cols = [row[1] for row in reference.execute(f'PRAGMA table_info("{table}")')]
            mig_cols = [row[1] for row in migrated.execute(f'PRAGMA table_info("{table}")')]
            if not mig_cols:
                schema_gaps.append(f"{table}: missing on migrated")
            elif mig_cols != ref_cols:
                schema_gaps.append(f"{table}: columns differ {mig_cols} != {ref_cols}")
    expect(not schema_gaps, f"all {len(metadata_tables)} metadata tables/columns present after upgrade",
           "; ".join(schema_gaps))
    reference_engine.dispose()

    seed_run = run(["-m", "app.seed"], "runbook seed against migrated scratch DB")
    expect(seed_run.returncode == 0, "app.seed runbook step rc=0")

    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    health = client.get("/v1/health")
    expect(health.status_code == 200 and health.json().get("db") == "ok"
           and health.json().get("storage") == "ok",
           "real app health GET on migrated DB", health.text)
    households = client.get("/v1/households")
    expect(households.status_code == 200 and len(households.json()) >= 1,
           "real reader /v1/households returns seeded household (no rows exposed here)",
           f"status={households.status_code} count={len(households.json())}")
    household_id = households.json()[0]["id"]
    assets = client.get("/v1/assets", params={"household_id": household_id})
    expect(assets.status_code == 200 and assets.json().get("items") == [],
           "real reader /v1/assets on empty migrated catalog (cursor envelope)",
           f"status={assets.status_code} body={assets.text[:200]}")
    settings_ai = client.get("/v1/settings/ai")
    expect(settings_ai.status_code == 200, "real reader /v1/settings/ai on migrated DB",
           f"status={settings_ai.status_code}")
    client.close()

    guarded_cleanup(scratch)
    print(f"[summary] checks={CHECKS} fails={FAILS}", flush=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
