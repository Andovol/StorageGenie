#!/usr/bin/env python3
"""SG-086 backup/restore drill: consistent read-only copy, restore-to-temp proof.

Read-only against production by construction: the live SQLite database is opened
with ``mode=ro`` and copied through SQLite's native backup API (a raw ``cp`` of a
WAL database is not a backup), and the storage directory is only read. The drill
never issues ``UPDATE``/``DELETE``/``INSERT``, never forces a WAL checkpoint and
never restarts a container. Every artifact it writes lands under the work
directory, and a work directory it creates itself is removed when the proof
finishes (hashes/counts stay on stdout, i.e. in the committed verification log).

Restoring production from backup is an incident, never silent cleanup (CO-42).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sqlite3
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

READ_BLOCK_BYTES = 1 << 20

NAMED_ROW_QUERIES: tuple[tuple[str, str], ...] = (
    ("evidence", "SELECT id, household_id, storage_key FROM evidence ORDER BY id LIMIT 3"),
    ("asset", "SELECT id, household_id, display_name FROM asset ORDER BY id LIMIT 3"),
)


def log(message: str) -> None:
    print(message, flush=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(READ_BLOCK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


@contextmanager
def read_only_connection(path: Path) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        yield connection
    finally:
        connection.close()


def table_counts(connection: sqlite3.Connection) -> dict[str, int]:
    names = [
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
    ]
    counts: dict[str, int] = {}
    for name in names:
        row = connection.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()
        counts[name] = int(row[0])
    return counts


def integrity_check(connection: sqlite3.Connection) -> str:
    row = connection.execute("PRAGMA integrity_check").fetchone()
    return str(row[0])


def consistent_backup(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination_connection = sqlite3.connect(destination)
    try:
        with read_only_connection(source) as source_connection:
            source_connection.backup(destination_connection)
    finally:
        destination_connection.close()


def assert_byte_equal(left: Path, right: Path) -> str:
    left_hash = sha256_file(left)
    right_hash = sha256_file(right)
    if left_hash != right_hash:
        raise AssertionError(f"byte inequality: {left}={left_hash} vs {right}={right_hash}")
    return left_hash


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination)


def storage_manifest(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def total_bytes(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def _print_counts(prefix: str, counts: dict[str, int]) -> None:
    for name, count in counts.items():
        log(f"{prefix} {name}\t{count}")


def _guard(prod_db: Path, prod_storage: Path, work_dir: Path) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    work = work_dir.resolve()
    for label, raw in (("production DB", prod_db), ("production storage", prod_storage)):
        resolved = raw.resolve()
        if not resolved.exists():
            raise SystemExit(f"STOP: {label} not found: {resolved}")
        if resolved == work or work in resolved.parents:
            raise SystemExit(f"STOP: work-dir {work} is inside {label} {resolved}")
        if not os.access(resolved, os.R_OK):
            raise SystemExit(f"STOP: {label} not readable: {resolved}")


def _before_phase(prod_db: Path, backup_db: Path) -> dict[str, int]:
    log("[G1.1] BEFORE per-table counts + integrity (read-only, live)")
    with read_only_connection(prod_db) as connection:
        before = table_counts(connection)
        live_integrity = integrity_check(connection)
    _print_counts("  live", before)
    log(f"  live integrity_check={live_integrity}")

    log("[G1.2] consistent copy via SQLite native backup API (read-only source)")
    consistent_backup(prod_db, backup_db)
    with read_only_connection(backup_db) as connection:
        backup_counts = table_counts(connection)
        backup_integrity = integrity_check(connection)
    log(f"  backup sha256={sha256_file(backup_db)} bytes={backup_db.stat().st_size}")
    log(f"  backup integrity_check={backup_integrity}")
    if backup_counts != before:
        raise SystemExit("STOP: backup counts differ from live BEFORE counts")
    return before


def _storage_phase(prod_storage: Path, backup_storage: Path) -> dict[str, str]:
    log("[G1.3] storage recursive copy (read-only source)")
    source_manifest = storage_manifest(prod_storage)
    log(f"  source files={len(source_manifest)} bytes={total_bytes(prod_storage)}")
    copy_tree(prod_storage, backup_storage)
    backup_manifest = storage_manifest(backup_storage)
    if backup_manifest != source_manifest:
        raise SystemExit("STOP: storage backup is not byte-equal to the source")
    log(f"  backup files={len(backup_manifest)} bytes={total_bytes(backup_storage)}")
    for relative, digest in sorted(backup_manifest.items())[:3]:
        log(f"  sample {relative} {digest}")
    return backup_manifest


def _restore_phase(
    backup_dir: Path,
    restore_dir: Path,
    backup_db: Path,
    backup_storage_manifest: dict[str, str],
    before: dict[str, int],
) -> None:
    log("[G2.1] restore into a fresh temp dir (never the live paths)")
    copy_tree(backup_dir, restore_dir)
    restored_db = restore_dir / "storagegenie.db"
    log(f"  backup == restored sha256={assert_byte_equal(backup_db, restored_db)}")
    with read_only_connection(restored_db) as connection:
        restored_integrity = integrity_check(connection)
        restored_counts = table_counts(connection)
        named_rows = [
            (label, connection.execute(query).fetchall()) for label, query in NAMED_ROW_QUERIES
        ]
    log(f"  restored integrity_check={restored_integrity}")
    if restored_counts != before:
        raise SystemExit("STOP: restored counts differ from BEFORE counts")
    for label, rows in named_rows:
        for row in rows:
            log(f"  restored {label}: {row}")
    if storage_manifest(restore_dir / "storage") != backup_storage_manifest:
        raise SystemExit("STOP: restored storage is not byte-equal to the backup")
    log("  storage backup == restored: file hashes identical")


def _corruption_phase(backup_db: Path, restore_dir: Path) -> None:
    log("[G2.2] seen-to-fail: a deliberately corrupted temp copy must fail the equality gate")
    corrupted = restore_dir / "corrupted.db"
    payload = bytearray(backup_db.read_bytes())
    payload[len(payload) // 2] ^= 0xFF
    corrupted.write_bytes(bytes(payload))
    try:
        assert_byte_equal(backup_db, corrupted)
    except AssertionError as error:
        log(f"  equality gate FAILED as expected: {error}")
    else:
        raise SystemExit("STOP: corrupted copy passed the equality gate")
    corrupted.unlink()
    log("  corrupted artifact discarded")


def _after_phase(prod_db: Path, before: dict[str, int]) -> None:
    log("[G1.4] AFTER per-table counts + integrity (read-only, live)")
    with read_only_connection(prod_db) as connection:
        after = table_counts(connection)
        after_integrity = integrity_check(connection)
    _print_counts("  live", after)
    log(f"  live integrity_check={after_integrity}")
    if after != before:
        raise SystemExit("STOP: production logical state moved during the drill")
    log("  production-untouched: BEFORE == AFTER (counts identical)")


def run_drill(prod_db: Path, prod_storage: Path, work_dir: Path, remove_work: bool) -> int:
    _guard(prod_db, prod_storage, work_dir)
    backup_dir = work_dir / "backup"
    restore_dir = work_dir / "restore"
    backup_db = backup_dir / "storagegenie.db"
    log(f"work-dir    = {work_dir}")
    log(f"backup-dir  = {backup_dir}")
    log(f"restore-dir = {restore_dir}")

    before = _before_phase(prod_db, backup_db)
    backup_storage_manifest = _storage_phase(prod_storage, backup_dir / "storage")
    _restore_phase(backup_dir, restore_dir, backup_db, backup_storage_manifest, before)
    _corruption_phase(backup_db, restore_dir)
    _after_phase(prod_db, before)

    if remove_work:
        shutil.rmtree(work_dir)
        log(f"work-dir removed: {work_dir}")
    else:
        log(f"work-dir kept: {work_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prod-db", required=True, type=Path)
    parser.add_argument("--prod-storage", required=True, type=Path)
    parser.add_argument("--work-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    if args.work_dir is None:
        args.work_dir = Path(tempfile.mkdtemp(prefix="sg086-drill-"))
        remove_work = True
    else:
        args.work_dir = args.work_dir.resolve()
        remove_work = False
    return run_drill(args.prod_db, args.prod_storage, args.work_dir, remove_work)


if __name__ == "__main__":
    sys.exit(main())
