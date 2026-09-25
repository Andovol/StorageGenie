#!/usr/bin/env python3
"""SG-130 backfill: write the missing legacy-PNG ``.jpg`` thumbnails.

SG-129 removed the 14 orphan ``_thumb*.png`` files, which left the 7 PNG
evidences with **no** thumbnail at all: the reader resolves only
``<stem>_thumb<size>.jpg`` (``app/storage/local_store.py:thumbnail_path``,
``app/api/v1/evidence.py:get_thumbnail``), and no ``.jpg`` thumb was ever
written for a PNG source before SG-127 unified the writer. Their thumb routes
therefore 404 (the legacy-PNG gap, F-SG127-2). This script backfills exactly
those artifacts.

It is a thin driver, never a re-implementation (``PG-SC-12``): it decodes each
ORIGINAL through the production ``_decode_image`` and writes each configured
size through the production ``_thumbnail_bytes``, to the production
``thumbnail_path``, with the writer's own atomic write-temp-then-replace
discipline. The artifact the writer leaves is the artifact the reader serves.

Targets are **explicit** ``--storage-key`` values (repeatable), never a glob or
a discovery guess: the caller enumerates the missing set, so an unexpected 15th
artifact cannot be created silently. Idempotency is **skip-existing** by
default -- a re-run with the artifacts present writes nothing; pass
``--overwrite`` to rewrite an existing artifact through the same atomic path.

In the served image the app is importable but this script is not (the running
image predates it), so the live invocation pipes it in over stdin:

    docker exec -i storagegenie-backend-1 python - --storage-key <k1> ... \
        < backend/scripts/backfill_legacy_png_thumbs.py

The live write is owned by the owner's word (D20; ``PG-PR-10``).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from app.config import settings
from app.services.evidence_service import _decode_image, _thumbnail_bytes
from app.storage.local_store import thumbnail_path


def log(message: str) -> None:
    print(message, flush=True)


def backfill_evidence(storage_key: str, *, overwrite: bool = False) -> list[Path]:
    """Write every configured-size thumb for one image original via the writer.

    Returns the artifacts actually written, in size order (empty when every
    artifact already exists and ``overwrite`` is false).
    """
    original = Path(settings.storage_root) / storage_key
    if not original.is_file():
        raise FileNotFoundError(f"original not found: {original}")

    file_bytes = original.read_bytes()
    sha = hashlib.sha256(file_bytes).hexdigest()
    if original.stem != sha:
        log(f"WARN stem does not equal sha256 stem={original.stem} sha={sha}")

    image = _decode_image(file_bytes, sha)
    written: list[Path] = []
    for size in settings.thumbnail_sizes:
        target = thumbnail_path(storage_key, size)
        if target.exists() and not overwrite:
            log(f"SKIP existing (idempotent) size={size} path={target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        try:
            tmp.write_bytes(_thumbnail_bytes(image, "image/png", size))
            tmp.replace(target)
        finally:
            if tmp.exists():
                tmp.unlink()
        body = target.read_bytes()
        log(
            f"WROTE size={size} bytes={len(body)} magic={body[:3].hex()} "
            f"sha256={hashlib.sha256(body).hexdigest()} path={target}"
        )
        written.append(target)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--storage-key",
        action="append",
        default=[],
        required=True,
        dest="storage_keys",
        metavar="KEY",
        help="storage-root-relative path of an image original (repeatable)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="rewrite existing artifacts (default: skip them, idempotent)",
    )
    args = parser.parse_args(argv)

    total = 0
    for key in args.storage_keys:
        log(f"EVIDENCE storage_key={key}")
        written = backfill_evidence(key, overwrite=args.overwrite)
        total += len(written)
        if not written:
            log("  no artifact written for this evidence (already present)")
    log(
        f"BACKFILLED artifacts_written={total} evidences={len(args.storage_keys)} "
        f"sizes={settings.thumbnail_sizes}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
