SG-013 — Deterministic signal extraction

## Identity and provenance

- Requested ref: `automation`
- BASE resolved at packet start: `c48b00dfd4bb7d639fb235629539e597262d1f07`
- WORK_HEAD: final work commit carrying this report; exact hash is quoted in the `refs/notes/storagegenie-coder-reports` receipt attached after push.
- Model: `unknown` (no model/provider metadata in process arguments)
- Reasoning effort: `unknown` (no effort argument/provider metadata exposed)
- Budget: 2100 s / 35 min. Measured bounded tool wall time was approximately 15 s; no timeout kill occurred.

## Delivered

`backend/app/services/signals.py` reads the stored original through the existing storage layer and stages OCR, barcode/QR, EXIF timestamp, and dHash observations. Barcode values are persisted only after QR syntax or EAN-13/UPC-A check-digit validation. Invalid codes produce low-confidence validation-failure observations with no candidate value or identifier. OCR stores text, boxes, and mean confidence. EXIF timestamps are gated by `exif_timestamps_enabled` (default false); GPS is never copied. Corrupt or unsupported originals raise a quarantine error.

`EXTRACTING_DETERMINISTIC_SIGNALS` is the only job body filled. Its `output_refs` contain observation IDs and per-kind counts. `get_observations` provides the service-level read-back covered by tests. No observation HTTP route is added; that boundary is SG-014/SG-016.

The schema change is exactly one table/revision: `observation`, with the evidence FK, constrained kind set, JSON value, nullable confidence, and created-at. Temp SQLite migration proof passed `upgrade head`, `downgrade -1`, `upgrade head`.

Dependencies are pinned in `backend/requirements.lock`: `pyzbar==0.1.9`, `pytesseract==0.3.13`, and dev-only fixture generator `qrcode==8.2`. `backend/Dockerfile` adds exactly `tesseract-ocr` and `libzbar0`. `allowed_mime_types` includes named `image/tiff`; HEIC remains deferred and upload validator code was not broadened beyond the scope ceiling.

## Verification

Fail-first was real: before implementation, focused test collection failed with `ImportError: cannot import name 'signals' from 'app.services'`. Post-change, the non-binary signal/migration subset passed 5/5, SG-012 import-job tests passed 3/3, and `test_export.py` passed 5/5.

The full backend collection is 34 tests. The full run is 32 passed and 2 failed, both non-vacuous dependency legs: generated real QR/EAN decoding and rendered-text OCR. The failures report the actual runtime messages `pyzbar/libzbar is not installed` and `tesseract is not installed or it's not in your PATH`; they were not skipped or counted as passes.

The deterministic controls that could execute passed: invalid EAN candidate `5901234123450` is check-invalid and is not persisted as an identifier; valid EAN `5901234123457` is check-valid in the fallback control; dHash resize distance is 0, different-image distance is 19, against named threshold 10; EXIF gate/GPS exclusion; corrupted input quarantine plus retry to `AWAITING_REVIEW`; output refs/getter; and migration round-trip. Ruff is clean. Mypy remains advisory at 41 pre-existing errors after SG-013’s own errors were corrected.

The host package install was attempted once under the required bound and denied exactly: `sudo: The "no new privileges" flag is set, which prevents sudo from running as root.` The local apt cache has `tesseract-ocr 5.3.4-1build5` provenance (SHA256 `2dfac382d77215aee0c3de4a2a2205505d5f2195e72e79b54ad32154fc08da77`) but no `libzbar0` record. Docker build was not run; Dockerfile diff is the image evidence and compose/image proof is deferred manual work.

The route-decorator gate found only the unchanged existing list: assets `19,117,180,190,217,246`; evidence `18,76,94,107`; jobs `32,78,88,98,107,139`; households `12,17,49,57`; users `12,20`; export `32`; health `15`; review tasks `12,40`. No API file changed.

ADR-003 was not silently edited. Its lines 41 and 51 still say `no-migration-needed`; this is a finding because SG-013 adds the authorised observation migration. The amendment belongs outside this slice ceiling.

## Output paths

- `backend/app/services/signals.py`
- `backend/app/services/observations.py`
- `backend/app/services/job_service.py`
- `backend/app/config.py`
- `backend/alembic/versions/20260908_sg013_observation.py`
- `backend/tests/test_signals.py`
- `backend/tests/test_import_jobs.py`
- `backend/pyproject.toml`
- `backend/requirements.lock`
- `backend/Dockerfile`
- `docs/worklogs/SG-013.log`
- `docs/worklogs/SG-013_report.md`

No production write, restart, secret, SSH, or privileged workaround was performed. All fixture outputs and test databases are temporary. No acceptance criterion was reported as passing vacuously.

FIRST READ: BASE automation resolved to c48b00dfd4bb7d639fb235629539e597262d1f07; actual migration head and existing SG-012 seam were inspected before edits.
DURING EXECUTION: required host OCR/barcode system packages were absent; sudo was denied by no-new-privileges, so those real decoder legs are unanswered rather than hidden.
REMAINING: attach/read back the pushed notes receipt and verify dispatch result `note=yes`; perform Docker/compose manual image proof later.
