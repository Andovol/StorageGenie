#!/usr/bin/env python3
"""SG-189 G1 probe — _guard geometry re-derived on the ACTUAL helper (F-SG182-1 repair).

Five scratch-directory geometries are driven through the real
``backend/scripts/backup_restore_drill.py::_guard``, loaded from the path in
``SG189_DRILL`` (default: the repo tree). Post-fix contract: equal /
prod-inside-work / work-inside-prod / missing => rejected with a message naming
that geometry; disjoint => allowed. The drill is NOT executed on the recursive
shape (shape proof only, as in SG-182). Every path lives under a fresh
/tmp/opencode scratch dir with containment-checked cleanup; no production DB,
storage or path is read or written, and the missing-DB case uses a scratch
nonexistent path only.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path
from types import ModuleType

REPO_DRILL = Path("/home/andrei/StorageGenie/backend/scripts/backup_restore_drill.py")
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


def load_drill(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("sg189_backup_restore_drill", path)
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


def guard_case(
    DRILL: ModuleType,
    label: str,
    prod_db: Path,
    prod_storage: Path,
    work: Path,
    expected: str,
    message_fragment: str,
) -> None:
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
        f"work={work.resolve()} storage={prod_storage.resolve()} msg={message!r}",
    )
    if expected == "rejected":
        expect(
            message_fragment in message,
            f"guard[{label}] message names the true geometry",
            f"fragment={message_fragment!r} msg={message!r}",
        )


def main() -> int:
    drill_path = Path(os.environ.get("SG189_DRILL", str(REPO_DRILL)))
    DRILL = load_drill(drill_path)
    print(f"[phase] drill source = {drill_path}", flush=True)
    scratch = Path(tempfile.mkdtemp(prefix="sg189-", dir=SCRATCH_ROOT))
    print(f"[phase] scratch root = {scratch}", flush=True)

    def case_root(name: str) -> Path:
        root = scratch / name
        root.mkdir(parents=True)
        return root

    # equal: work dir IS the production storage
    root = case_root("equal")
    db = root / "db" / "prod.db"
    db.parent.mkdir()
    db.write_bytes(b"x")
    storage = root / "stor"
    storage.mkdir()
    guard_case(DRILL, "equal", db, storage, storage, "rejected", "equals production storage")

    # prod-inside-work: production storage lives inside the work dir
    root = case_root("prod-inside-work")
    db = root / "db" / "prod.db"
    db.parent.mkdir()
    db.write_bytes(b"x")
    work = root / "enclose"
    storage = work / "stor"
    storage.mkdir(parents=True)
    guard_case(
        DRILL, "prod-inside-work", db, storage, work, "rejected", "is inside work-dir"
    )

    # work-inside-prod: the recursive-copy shape F-SG182-1 (drill never executed)
    root = case_root("work-inside-prod")
    db = root / "db" / "prod.db"
    db.parent.mkdir()
    db.write_bytes(b"x")
    storage = root / "stor"
    storage.mkdir()
    work = storage / "work"
    guard_case(
        DRILL, "work-inside-prod", db, storage, work, "rejected", "is inside production storage"
    )
    print(
        "[value] recursive shape (rejected pre-execution, drill intentionally not executed): "
        f"backup destination {(work / 'backup').resolve()} is inside copy source {storage.resolve()}",
        flush=True,
    )

    # disjoint: the documented runbook form (mkdtemp work dir)
    root = case_root("disjoint")
    db = root / "db" / "prod.db"
    db.parent.mkdir()
    db.write_bytes(b"x")
    storage = root / "stor"
    storage.mkdir()
    guard_case(DRILL, "disjoint", db, storage, root / "work", "allowed", "")

    # missing: scratch nonexistent production DB path (never a production path)
    root = case_root("missing")
    storage = root / "stor"
    storage.mkdir()
    guard_case(
        DRILL,
        "missing",
        root / "db" / "absent.db",
        storage,
        root / "work",
        "rejected",
        "production DB not found",
    )

    guarded_cleanup(scratch)
    print(f"[summary] checks={CHECKS} fails={FAILS}", flush=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
