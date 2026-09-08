SG-019 — TIFF signature detection repair

Status: LANDED; receipt note is the final action after the metadata commit.

BASE requested ref: `automation`

BASE resolved: `ef1fa999f754e6d117680168c00ed20b8994cf4b`

WORK_HEAD: to be filled after the implementation/report commit.

Work dir: `/home/andrei/StorageGenie`

Origin: `git@github.com:Andovol/StorageGenie.git`

Coder: `codex`

Model: `unknown` — no model id appeared in readable process arguments; the CLI default model id was omitted by policy.

Reasoning effort: `high` — proven from live process arguments containing `-c model_reasoning_effort=high`.

Autonomy: L3, Phase 1 D11 repair slice.

Elapsed: approximately 15 s of observed command wall time / 2100 s (35 min) overall bound; no command was killed.

Implemented

- Added exactly one detector branch at `backend/app/services/evidence_service.py:66-67` for classic TIFF magic `II*\\0` and `MM\\0*`, returning exactly `image/tiff`.
- Added focused tests at `backend/tests/test_evidence_upload.py:98-168`: six signature legs covering JPEG, PNG, PDF, WebP, little-endian TIFF, and big-endian TIFF; one exact unsupported-signature negative; and a real `POST /v1/evidence` route proof for both classic TIFF byte orders.
- The little-endian fixture is generated with Pillow. The big-endian fixture is a valid classic TIFF constructed in the test because Pillow writes little-endian by default. Both uploaded rows returned 201 and their stored originals decoded through Pillow at 17x11. Thumbnail behavior was untouched; its existing best-effort warning for TIFF remained non-fatal.
- BigTIFF is documented as excluded and was not attempted. The new branch accepts only classic TIFF magic `0x2a`; BigTIFF magic `0x2b` remains unsupported.

Fail-first evidence

Before the code change, the required real TIFF probe produced:

```text
tiff_magic= 49492a00 tiff_size= 701
tiff_upload_status= 422
tiff_upload_body= {'type': 'about:blank', 'title': 'Unprocessable Entity', 'status': 422, 'detail': 'media_type_mismatch: unsupported media signature'}
```

This reproduces SG-018’s baseline defect at the actual upload route, not a config-only inference.

Acceptance evidence

- Focused evidence suite: `timeout 600s bash -lc 'cd backend && venv/bin/python -m pytest -q tests/test_evidence_upload.py'` returned `16 passed, 2 warnings`.
- A pre-commit guard initially used a space-dependent `sed` expression to check the required bare first token and emitted no output; inspection confirmed both records existed, and the corrected explicit first-line/status/diff validation was then run before commit.
- Explicit detector/route listing: `timeout 600s bash -lc 'cd backend && venv/bin/python -m pytest -vv -q tests/test_evidence_upload.py -k "detect_media_type or endpoint_accepts_classic_tiff"` collected 16, selected 8, and returned `8 passed, 8 deselected, 2 warnings`. The output named and executed all six supported-signature parameter cases, the exact unknown-signature negative, and the both-endian route proof. The deselections are the pre-existing non-detector upload tests, not a skipped acceptance leg.
- Configured and detected MIME values match side by side: `backend/app/config.py:16` contains `"image/tiff"`; `backend/app/services/evidence_service.py:67` contains `detected = "image/tiff"`.
- Full backend: `timeout 600s bash -lc 'cd backend && venv/bin/python -m pytest -q'` returned `65 collected, 62 passed, 3 failed`. The three named exceptions were `backend/tests/test_candidates.py::test_candidate_migration_upgrade_downgrade_upgrade` (known stale migration assertion, SG-020 destination), `backend/tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` (ISS-1 decoder), and `backend/tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` (ISS-1 decoder). This is the allowed full-suite outcome; no other test failed.
- Ruff: `timeout 120s bash -lc 'cd backend && venv/bin/ruff check app tests'` returned `All checks passed!`.
- Mypy advisory: `timeout 120s bash -lc 'cd backend && venv/bin/python -m mypy app'` reported `40 errors in 9 files (checked 51 source files)`; this existing advisory was not expanded or repaired outside the ceiling.
- Export head: `tests/test_export.py::test_export_manifest_is_complete_and_downloadable` returned `1 passed, 2 warnings`.
- Scope grep: `git diff --unified=0 -- backend/app/api/v1` emitted no route-decorator change. `git diff --check` was clean. Changed-file inspection found no migration, dependency, env, secret, frontend, provider, or infrastructure path.

Output paths committed by this slice

- `backend/app/services/evidence_service.py`
- `backend/tests/test_evidence_upload.py`
- `docs/worklogs/SG-019.log`
- `docs/worklogs/SG-019_report.md`

The packet itself remains the pre-existing committed input at `docs/packets/SG-019-tiff-detector-repair.md`; it was not modified. No receipt publisher or evidence ref was used. The final notes ref action will carry `Dispatch-ID: SG-019`, the report path above, and the final work-head target; no commit will follow that note.

No criterion passed vacuously: the pre-change probe invoked the real route, the post-change route test uploaded both actual classic TIFF byte orders, Pillow decoded both stored files, every signature parameter invoked `_detect_media_type`, the negative asserted the exact error, and the full suite collected and executed 65 tests.

UNCLEAR — FIRST READ: The packet’s ARCHITECT.md, PACKET.md, DISPATCH.md, and PRODUCTION.md routing files were absent from the checkout; the committed packet plus AGENTS.md and STATE.md were used.
UNCLEAR — DURING EXECUTION: The full backend suite retained the three named failures: the stale candidate migration assertion and the two ISS-1 decoder nodes; mypy retained 40 advisory errors. No privileged workaround was attempted.
UNCLEAR — REMAINING: SG-020 owns the exit re-run and stale migration assertion; the manual compose pass remains the destination for the two decoder nodes. BigTIFF support remains intentionally out of scope.
