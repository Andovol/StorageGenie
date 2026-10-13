#!/usr/bin/env python3
"""SG-182 G1 probe — backup/restore drill on synthetic disposable state.

Runs the REAL module backend/scripts/backup_restore_drill.py (loaded from its
source file) against synthetic nonempty WAL-capable database + evidence bytes,
with source/backup/restore in disjoint disposable directories. Also exercises
the ACTUAL _guard with equal/parent/child/disjoint scratch layouts (packet
hypothesis: work-inside-source is missed while the message claims it).

Every path created here lives under a fresh mkdtemp under /tmp/opencode;
cleanup verifies resolved containment before rmtree. No production path or row
is read or written by this probe.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

REPO = Path("/home/andrei/StorageGenie")
DRILL_PATH = REPO / "backend" / "scripts" / "backup_restore_drill.py"
SCRATCH_ROOT = Path("/tmp/opencode")

CHECKS = 0
FAILS = 0


def expect(condition: bool, label: str, detail: str = "") -> None:
    global CHECKS, FAILS
    CHECKS += 1
    status = "PASS" if condition else "FAIL"
    if not condition:
        FAILS += 1
    print(f"[{status}] {label} {detail}".rstrip(), flush=True)


def load_drill():
    spec = importlib.util.spec_from_file_location("sg182_backup_restore_drill", DRILL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guarded_cleanup(path: Path) -> None:
    resolved = path.resolve()
    root = SCRATCH_ROOT.resolve()
    if resolved == root or root not in resolved.parents:
        raise SystemExit(f"refusing cleanup outside scratch root: {resolved}")
    shutil.rmtree(resolved)
    print(f"[cleanup] removed verified scratch target {resolved}", flush=True)


def guard_case(DRILL, label: str, prod_db: Path, prod_storage: Path, work: Path,
               expected: str) -> None:
    """expected: 'rejected' | 'allowed'. Records actual resolved paths."""
    work.mkdir(parents=True, exist_ok=True)
    outcome = "allowed"
    message = ""
    try:
        DRILL._guard(prod_db, prod_storage, work)
    except SystemExit as exc:  # the guard's own STOP path
        outcome = "rejected"
        message = str(exc)
    expect(
        outcome == expected,
        f"guard[{label}] expected={expected} actual={outcome}",
        f"work={work.resolve()} db={prod_db.resolve()} storage={prod_storage.resolve()} msg={message!r}",
    )
    if label == "work-inside-source":
        # Consequence boundary only — NOT executing the drill on this shape.
        backup_dir = (work / "backup").resolve()
        expect(
            Path(prod_storage).resolve() in backup_dir.parents,
            "guard[work-inside-source] drill storage destination lands INSIDE its own source "
            "(recursive copy shape the guard missed; drill intentionally not executed)",
            f"backup_dir={backup_dir}",
        )


def make_synthetic_prod(root: Path):
    db_path = root / "db" / "storagegenie.db"
    storage = root / "storage"
    (storage / "h1" / "ab").mkdir(parents=True)
    (storage / "h1" / "manifest.json").write_text('{"files": 2}', encoding="utf-8")
    (storage / "h1" / "ab" / "photo.bin").write_bytes(b"\x89PNG\r\n\x1a\nsynthetic-a")
    (storage / "h2" / "deep").mkdir(parents=True)
    (storage / "h2" / "deep" / "note.txt").write_bytes(b"synthetic evidence h2")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA wal_autocheckpoint=0")
    connection.execute("CREATE TABLE household (id TEXT PRIMARY KEY, name TEXT NOT NULL)")
    connection.execute(
        "CREATE TABLE asset (id TEXT PRIMARY KEY, household_id TEXT NOT NULL, display_name TEXT)"
    )
    connection.execute(
        "CREATE TABLE evidence (id TEXT PRIMARY KEY, household_id TEXT NOT NULL, storage_key TEXT)"
    )
    connection.execute("INSERT INTO household VALUES ('h1', 'Synthetic Household')")
    for index in range(5):
        connection.execute("INSERT INTO asset VALUES (?, 'h1', ?)", (f"a{index}", f"Asset {index}"))
    for index in range(3):
        connection.execute(
            "INSERT INTO evidence VALUES (?, 'h1', ?)", (f"e{index}", f"h1/ab/e{index}.bin")
        )
    connection.commit()
    return connection, db_path, storage


def main() -> int:
    raise SystemExit("probe must run as a script, see __main__")


if __name__ == "__main__":
    DRILL = load_drill()
    print(f"[phase] drill source = {DRILL_PATH}", flush=True)
    scratch = Path(tempfile.mkdtemp(prefix="sg182-g1-", dir=SCRATCH_ROOT))
    print(f"[phase] scratch root = {scratch}", flush=True)

    # ---- guard cases on the ACTUAL helper ----
    base = scratch / "guard"
    (base / "db").mkdir(parents=True)
    (base / "db" / "prod.db").write_bytes(b"x")
    (base / "stor").mkdir()
    guard_case(DRILL, "equal", base / "db" / "prod.db", base / "stor", base / "stor", "rejected")

    (base / "enclose" / "db2").mkdir(parents=True)
    (base / "enclose" / "db2" / "prod.db").write_bytes(b"x")
    (base / "enclose" / "stor2").mkdir()
    guard_case(DRILL, "source-inside-work", base / "enclose" / "db2" / "prod.db",
               base / "enclose" / "stor2", base / "enclose", "rejected")

    (base / "db3").mkdir(parents=True)
    (base / "db3" / "prod.db").write_bytes(b"x")
    (base / "stor3").mkdir()
    guard_case(DRILL, "work-inside-source", base / "db3" / "prod.db", base / "stor3",
               base / "stor3" / "work", "allowed")

    (base / "db4").mkdir(parents=True)
    (base / "db4" / "prod.db").write_bytes(b"x")
    (base / "stor4").mkdir()
    guard_case(DRILL, "disjoint", base / "db4" / "prod.db", base / "stor4", base / "work4",
               "allowed")

    (base / "stor5").mkdir()
    guard_case(DRILL, "missing-db", base / "db5" / "missing.db", base / "stor5",
               base / "work5", "rejected")

    # ---- real drill on synthetic WAL-capable prod ----
    prod = scratch / "drill" / "prod"
    writer, prod_db, prod_storage = make_synthetic_prod(prod)
    wal_path = Path(str(prod_db) + "-wal")
    wal_size = wal_path.stat().st_size if wal_path.exists() else -1
    expect(wal_size > 0, "synthetic prod has WAL-resident committed state", f"wal_bytes={wal_size}")
    with DRILL.read_only_connection(prod_db) as connection:
        before = DRILL.table_counts(connection)
        live_integrity = DRILL.integrity_check(connection)
    expect(live_integrity == "ok", "live synthetic integrity_check", live_integrity)
    print(f"[value] live counts ({sum(before.values())} rows total): {before}", flush=True)

    rawcopy = scratch / "drill" / "raw-copy.db"
    shutil.copy2(prod_db, rawcopy)
    raw_note = ""
    try:
        with sqlite3.connect(rawcopy) as raw_conn:
            raw_counts = {
                name: raw_conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
                for name in ("household", "asset", "evidence")
            }
        raw_note = f"raw-cp-of-only-main-file reads counts {raw_counts}"
    except sqlite3.Error as exc:
        raw_note = f"raw-cp-of-only-main-file cannot even read schema: {type(exc).__name__}: {exc}"
    print(f"[value] control (raw single-file copy is not a backup): {raw_note}", flush=True)
    expect(
        "counts {'household': 1, 'asset': 5, 'evidence': 3}" not in raw_note,
        "raw copy control differs from the full backup snapshot (WAL data absent)",
        raw_note,
    )

    work_dir = scratch / "drill" / "work"
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            rc = DRILL.run_drill(prod_db, prod_storage, work_dir, remove_work=False)
    except BaseException as exc:  # noqa: BLE001 — capture the raw failure, not a substitute
        print(buffer.getvalue())
        print(f"[FAIL] drill raised: {type(exc).__name__}: {exc}", flush=True)
        raise
    output = buffer.getvalue()
    print(output, flush=True)
    expect(rc == 0, "full drill exit code", str(rc))
    expect("production-untouched: BEFORE == AFTER (counts identical)" in output,
           "drill reports production-untouched")
    expect("equality gate FAILED as expected" in output,
           "built-in same-length corruption gate observed failing")

    backup_db = work_dir / "backup" / "storagegenie.db"
    restored_db = work_dir / "restore" / "storagegenie.db"
    with DRILL.read_only_connection(backup_db) as connection:
        backup_counts = DRILL.table_counts(connection)
        backup_integrity = DRILL.integrity_check(connection)
        named_rows = connection.execute(
            "SELECT id, household_id, display_name FROM asset ORDER BY id"
        ).fetchall()
    expect(backup_integrity == "ok", "backup integrity_check", backup_integrity)
    expect(backup_counts == before, "backup counts == live BEFORE counts (WAL-resident state captured)",
           json.dumps(backup_counts, sort_keys=True))
    expect(named_rows == [(f"a{i}", "h1", f"Asset {i}") for i in range(5)],
           "backup real row reader returns all synthetic rows", str(named_rows))
    expect(DRILL.sha256_file(backup_db) == DRILL.sha256_file(restored_db),
           "backup == restored byte-equal")

    # ---- missing-file control ----
    missing_outcome = ""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            DRILL.run_drill(scratch / "drill" / "missing.db", prod_storage,
                            scratch / "drill" / "work-missing", remove_work=False)
        missing_outcome = "allowed"
    except SystemExit as exc:
        missing_outcome = f"rejected: {exc}"
    expect(missing_outcome.startswith("rejected") and "not found" in missing_outcome,
           "missing source DB => STOP (differs from normal control)", missing_outcome)

    # ---- same-length corruption controls (independent of drill's built-in) ----
    corrupt_dir = scratch / "corrupt"
    corrupt_dir.mkdir()
    same_len_db = corrupt_dir / "same-len.db"
    payload = bytearray(backup_db.read_bytes())
    payload[len(payload) // 2] ^= 0xFF
    same_len_db.write_bytes(bytes(payload))
    expect(same_len_db.stat().st_size == backup_db.stat().st_size,
           "same-length DB corruption keeps identical size")
    expect(DRILL.sha256_file(same_len_db) != DRILL.sha256_file(backup_db),
           "same-length DB corruption changes sha256 (names/sizes-blind check misses it)")
    try:
        DRILL.assert_byte_equal(backup_db, same_len_db)
        equality_outcome = "no-raise"
    except AssertionError:
        equality_outcome = "AssertionError"
    expect(equality_outcome == "AssertionError", "byte-equality gate rejects same-length DB corruption")
    with sqlite3.connect(same_len_db) as corrupt_conn:
        corrupt_integrity = DRILL.integrity_check(corrupt_conn)
    print(f"[value] integrity_check on same-length corrupted DB = {corrupt_integrity}", flush=True)

    original_file = prod_storage / "h1" / "ab" / "photo.bin"
    corrupt_file = corrupt_dir / "photo-corrupt.bin"
    data = bytearray(original_file.read_bytes())
    data[len(data) // 2] ^= 0xFF
    corrupt_file.write_bytes(bytes(data))
    original_fingerprint = ("h1/ab/photo.bin", original_file.stat().st_size)
    corrupt_fingerprint = ("h1/ab/photo.bin", corrupt_file.stat().st_size)
    expect(original_fingerprint == corrupt_fingerprint,
           "same-length evidence corruption keeps name+size fingerprint identical",
           f"{original_fingerprint}")
    expect(hashlib.sha256(original_file.read_bytes()).hexdigest()
           != hashlib.sha256(corrupt_file.read_bytes()).hexdigest(),
           "same-length evidence corruption changes content hash (names/sizes fingerprint misses it)")

    writer.close()
    guarded_cleanup(scratch)
    print(f"[summary] checks={CHECKS} fails={FAILS}", flush=True)
    sys.exit(1 if FAILS else 0)
