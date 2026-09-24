#!/usr/bin/env python3
"""SG-111 Asset lifecycle backfill: convert out-of-vocabulary ``status`` values.

Reads the six-value lifecycle vocabulary from the single source
(``app.services.lifecycle``) rather than re-typing it. **Dry-run by default**:
with no ``--apply`` it prints the BEFORE census, the planned conversions and the
projected AFTER census, and writes nothing.

The **live** backfill is owned by the owner's word (``PG-PR-10``); this slice
proves the script on a temp copy only. The exact production command, for that
word, is printed by ``--print-production-command`` and also in the report:

    docker exec storagegenie-backend-1 python /app/scripts/backfill_asset_lifecycle.py \
        --db /data/db/storagegenie.db --apply

Nearest-legal mapping: an exact vocabulary value is kept; a case/whitespace
variant is canonicalised; any other value maps to ``ARCHIVED`` -- conservative,
because an unrecognised status must never be promoted to a live (``ACTIVE``)
one.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from app.services.lifecycle import ARCHIVED, LIFECYCLE_STATUSES

VOCABULARY: frozenset[str] = frozenset(LIFECYCLE_STATUSES)

PRODUCTION_COMMAND = (
    "docker exec storagegenie-backend-1 python /app/scripts/backfill_asset_lifecycle.py "
    "--db /data/db/storagegenie.db --apply"
)


def log(message: str) -> None:
    print(message, flush=True)


def census(connection: sqlite3.Connection) -> dict[str, int]:
    """``{status: count}`` for every distinct stored value, ordered."""
    rows = connection.execute(
        "SELECT status, COUNT(*) FROM asset GROUP BY status ORDER BY status"
    ).fetchall()
    return {str(value): int(count) for value, count in rows}


def canonical_status(value: str) -> str:
    """The nearest legal lifecycle state for a stored ``value``."""
    if value in VOCABULARY:
        return value
    if isinstance(value, str) and value.strip().upper() in VOCABULARY:
        return value.strip().upper()
    return ARCHIVED


def plan(connection: sqlite3.Connection) -> list[tuple[str, str, int]]:
    """``[(stored_value, target_value, row_count), ...]`` for values to convert."""
    changes: list[tuple[str, str, int]] = []
    for value, count in census(connection).items():
        target = canonical_status(value)
        if target != value:
            changes.append((value, target, count))
    return changes


def projected_census(connection: sqlite3.Connection) -> dict[str, int]:
    """The census that ``--apply`` would leave behind, without writing."""
    projected: dict[str, int] = {}
    for value, count in census(connection).items():
        target = canonical_status(value)
        projected[target] = projected.get(target, 0) + count
    return dict(sorted(projected.items()))


def apply_changes(connection: sqlite3.Connection) -> int:
    """Write the planned conversions; return the number of rows changed."""
    changed = 0
    for value, target, count in plan(connection):
        connection.execute("UPDATE asset SET status = ? WHERE status = ?", (target, value))
        changed += count
    connection.commit()
    return changed


def run(db_path: Path, apply: bool) -> int:
    if not db_path.exists():
        log(f"STOP: database not found: {db_path}")
        return 2
    connection = sqlite3.connect(db_path)
    try:
        log(f"db={db_path}")
        before = census(connection)
        log(f"BEFORE census={before}")
        changes = plan(connection)
        log(f"planned conversions={changes}")
        if not changes:
            log("no out-of-vocabulary status value exists; nothing to backfill")
        if apply:
            changed = apply_changes(connection)
            log(f"APPLIED rows_changed={changed}")
            log(f"AFTER census={census(connection)}")
        else:
            log(f"DRY-RUN projected AFTER census={projected_census(connection)}")
            log("dry-run: nothing written (pass --apply to write)")
        log(f"production command (owner word required): {PRODUCTION_COMMAND}")
        return 0
    finally:
        connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--apply", action="store_true", help="write the conversions")
    parser.add_argument(
        "--print-production-command",
        action="store_true",
        help="print the owner-word production command and exit",
    )
    args = parser.parse_args(argv)
    if args.print_production_command:
        log(PRODUCTION_COMMAND)
        return 0
    return run(args.db, args.apply)


if __name__ == "__main__":
    sys.exit(main())
