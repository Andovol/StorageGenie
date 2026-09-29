"""SG-148: `alembic upgrade head --sql` renders the whole chain offline.

The four post-FTS idempotency guards (`sg068`, `sg100`, `sg113`, `sg114`) skip
their `sa.inspect(...).has_table(...)` check when `op.get_context().as_sql`, so
offline SQL generation no longer aborts on `MockConnection`. This test drives
the real CLI and asserts the full emitted SQL, not just an early prefix.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]

POST_FTS_MARKERS = (
    "20260912_sg025_provider_call",
    "20260914_sg035_foundations",
    "20260916_sg048_name_optional",
    "20260917_sg068_saved_search",
    "20260923_sg100_enrich_snapshot",
    "20260924_sg113_location",
    "20260924_sg114_relation",
)

FTS_TRIGGERS = (
    "asset_fts_after_insert",
    "asset_fts_after_update",
    "asset_fts_after_delete",
)

FTS_TABLE_DDL = "CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts"


def _run_offline_sql() -> str:
    alembic = Path(sys.executable).parent / "alembic"
    completed = subprocess.run(
        [str(alembic), "upgrade", "head", "--sql"],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        timeout=300,
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 0, output
    return output


def test_upgrade_head_sql_renders_full_chain() -> None:
    output = _run_offline_sql()

    assert FTS_TABLE_DDL in output
    for trigger in FTS_TRIGGERS:
        assert f"CREATE TRIGGER IF NOT EXISTS {trigger}" in output

    running = [
        line.strip()
        for line in output.splitlines()
        if line.strip().startswith("-- Running upgrade")
    ]
    for revision in POST_FTS_MARKERS:
        assert any(line.endswith(f"-> {revision}") for line in running), revision
    assert any(
        line.endswith("-> 20260924_sg114_relation") for line in running
    ), "chain did not reach the head revision"
