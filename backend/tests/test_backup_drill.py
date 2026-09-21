"""SG-086 G3: backup/restore drill, proven on temporary fixtures only.

Every database and storage artifact here lives under pytest's ``tmp_path``. The
production proof (the live SQLite file and the ``storagegenie_storage_data``
volume) stays in ``docs/worklogs/SG-086_verify.log``; this test re-proves the
same method against fixtures so the drill outlives the slice. The helpers under
test are loaded from ``backend/scripts/backup_restore_drill.py``, the operator
tooling the README runbook invokes.
"""

from __future__ import annotations

import importlib.util
import shutil
import sqlite3
from pathlib import Path
from types import ModuleType

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
DRILL_PATH = BACKEND_DIR / "scripts" / "backup_restore_drill.py"


def _load_drill() -> ModuleType:
    spec = importlib.util.spec_from_file_location("sg086_backup_restore_drill", DRILL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DRILL = _load_drill()


def _write_fixture_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE household (id TEXT PRIMARY KEY, name TEXT NOT NULL)")
        connection.execute(
            "CREATE TABLE asset (id TEXT PRIMARY KEY, household_id TEXT NOT NULL, display_name TEXT)"
        )
        connection.execute("INSERT INTO household VALUES ('h1', 'Popescu Household')")
        for index in range(5):
            connection.execute(
                "INSERT INTO asset VALUES (?, 'h1', ?)", (f"a{index}", f"Asset {index}")
            )
        connection.commit()


def test_consistent_backup_restores_byte_equal_with_matching_state(tmp_path: Path) -> None:
    source = tmp_path / "live" / "storagegenie.db"
    _write_fixture_db(source)
    source_hash_before = DRILL.sha256_file(source)
    with DRILL.read_only_connection(source) as connection:
        before = DRILL.table_counts(connection)
        assert DRILL.integrity_check(connection) == "ok"

    backup = tmp_path / "backup" / "storagegenie.db"
    DRILL.consistent_backup(source, backup)
    restored = tmp_path / "restore" / "storagegenie.db"
    restored.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup, restored)

    assert DRILL.assert_byte_equal(backup, restored) == DRILL.sha256_file(backup)
    with DRILL.read_only_connection(restored) as connection:
        assert DRILL.integrity_check(connection) == "ok"
        assert DRILL.table_counts(connection) == before
        named_rows = connection.execute("SELECT id, display_name FROM asset ORDER BY id").fetchall()

    assert named_rows == [
        ("a0", "Asset 0"),
        ("a1", "Asset 1"),
        ("a2", "Asset 2"),
        ("a3", "Asset 3"),
        ("a4", "Asset 4"),
    ]
    assert DRILL.sha256_file(source) == source_hash_before


def test_storage_copy_is_byte_equal(tmp_path: Path) -> None:
    source = tmp_path / "live-storage"
    (source / "h1" / "ab").mkdir(parents=True)
    (source / "h1" / "ab" / "photo.png").write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    (source / "h1" / "manifest.json").write_text('{"files": 1}', encoding="utf-8")

    backup = tmp_path / "backup-storage"
    DRILL.copy_tree(source, backup)
    restored = tmp_path / "restore-storage"
    DRILL.copy_tree(backup, restored)

    assert DRILL.storage_manifest(source) == DRILL.storage_manifest(backup)
    assert DRILL.storage_manifest(backup) == DRILL.storage_manifest(restored)


def test_byte_equality_gate_rejects_a_corrupted_copy(tmp_path: Path) -> None:
    source = tmp_path / "live" / "storagegenie.db"
    _write_fixture_db(source)
    backup = tmp_path / "backup" / "storagegenie.db"
    DRILL.consistent_backup(source, backup)

    assert DRILL.assert_byte_equal(backup, backup) == DRILL.sha256_file(backup)

    corrupted = tmp_path / "restore" / "corrupted.db"
    corrupted.parent.mkdir(parents=True, exist_ok=True)
    payload = bytearray(backup.read_bytes())
    payload[len(payload) // 2] ^= 0xFF
    corrupted.write_bytes(bytes(payload))

    with pytest.raises(AssertionError):
        DRILL.assert_byte_equal(backup, corrupted)
