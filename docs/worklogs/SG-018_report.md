SG-018 — BLOCKED close-out

Status: BLOCKED — the Phase 1 exit slice cannot satisfy G1 within its stated
scope ceiling.

BASE requested ref: `automation`

BASE resolved: `9c1a3233ceb4403a6355f8664ef8fe0145f7f9f2`

WORK_HEAD: to be filled after the blocked close-out commit.

Work dir: `/home/andrei/StorageGenie`

Origin: `git@github.com:Andovol/StorageGenie.git`

Coder: `codex`

Model: `unknown` — no model id appeared in readable process arguments; the CLI
used its default model and the model id was omitted by policy.

Reasoning effort: `high` — proven from the live process arguments containing
`-c model_reasoning_effort=high`.

Autonomy: L3, Phase 1 slice 7 of 7.

Elapsed: approximately 10 s of observed command wall time / 2100 s (35 min)
overall bound; no command was killed and no command lacked observable progress.

## Blocking evidence

The required fixture includes five generated inputs: EXIF JPEG, QR image,
EAN-13 image, plain PNG, and TIFF. The actual upload route is
`backend/app/api/v1/evidence.py:18-74`, and its detector is
`backend/app/services/evidence_service.py::_detect_media_type`. A bounded
probe generated a real TIFF with Pillow and called `POST /v1/evidence` using
`image/tiff`. It returned:

```text
tiff_upload_status= 422
tiff_upload_body= {'type': 'about:blank', 'title': 'Unprocessable Entity', 'status': 422, 'detail': 'media_type_mismatch: unsupported media signature'}
```

The configuration advertises TIFF at `backend/app/config.py:11`, and signal
extraction advertises TIFF at `backend/app/services/signals.py:18`, but the
upload detector accepts only JPEG, PNG, PDF, and WebP signatures. This is a
product mismatch before the import route is reached.

The packet ceiling permits only `backend/tests/test_phase1_e2e.py`, a
migration-assertion-only repair in `backend/tests/test_candidates.py`, the
Phase 1 section of `README.md`, and worklog files. It expressly forbids a
product-file change. A direct evidence row, a monkeypatch, or a PNG renamed to
`.tiff` would not prove the required upload and would violate the packet's
non-vacuity rule. Therefore this is a STOP, not a test workaround.

## Baseline proof before the STOP

Command, with the packet's 600-second suite bound:

```text
timeout 600s bash -lc 'cd backend && venv/bin/python -m pytest -q'
```

Observed output: `54 passed, 3 failed`.

The failures were:

- `backend/tests/test_candidates.py::test_candidate_migration_upgrade_downgrade_upgrade` — its `downgrade -1` leaves the SG-014 candidate table because SG-017 is the current head.
- `backend/tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` — carried ISS-1 decoder failure.
- `backend/tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` — carried ISS-1 decoder failure.

The baseline command was non-vacuous: 57 tests were collected and the three
named nodes executed.

## Acceptance status

G1 is BLOCKED by the real TIFF upload mismatch. The chained E2E test was not
created, so no create/run/review/retry/manual-entry/commit/FTS/export or UV-5
claim is made. No criterion is represented as passing through an empty diff,
skipped gate, or fixed-id replay.

G2 is unanswered after the STOP. The baseline records the stale candidate
migration assertion and the two named ISS-1 failures. Ruff, mypy, the final
suite count after repair, and the downgrade grep were not claimed.

G3 is unanswered. `README.md` was not changed because the exit runbook cannot
truthfully document a passing Phase 1 exit while its required fixture cannot be
uploaded.

G4 is unanswered. No Phase 2 ADR, provider, cost, egress, or manual-compose
decision was written or pre-approved.

G5 is partially satisfied by this worklog and report. Both output paths are
committed by this blocked close-out. The report carries the required model and
effort provenance and ends with the three UNCLEAR lines.

G6 is satisfied only for this blocked close-out after the commit is pushed: the
notes-ref receipt will be attached last, with no commit after it, and verified
locally and from the remote notes ref. The final dispatch artifact must report
`note=yes`.

## Scope and side effects

No migration, live database write, restart, docker/sudo operation, secret,
frontend file, product file, dependency, or infrastructure change was made.
The worktree will be clean after the receipt note operation.

## Phase 1 / blueprint:513 exit checklist

The required blueprint clauses are not claimed as proved because the fixture
cannot enter the route chain:

- mixed-folder ingest: BLOCKED at real TIFF upload;
- resume after failure: unanswered in the blocked run;
- human review including manual expiry entry: unanswered in the blocked run;
- no LLM: no LLM/provider code was touched, but this alone is not an exit
  proof;
- UV-5 `job-created → asset-accepted`: not computed because no exit fixture ran.

## Required follow-up

Authorize a separate product slice to add TIFF signature detection in
`backend/app/services/evidence_service.py`, with its own test and scope. Then
resume SG-018 from a fresh packet/base and execute the complete exit proof.

UNCLEAR — FIRST READ: The packet expected TIFF upload to be available, but the
actual detector did not implement the configured TIFF MIME type.
UNCLEAR — DURING EXECUTION: G1 is unanswered; the mandated ceiling prevents
repairing the product mismatch, so the stale-test repair and remaining gates
were not claimed.
UNCLEAR — REMAINING: Add TIFF signature support in a separately authorized
product slice, then resume SG-018 from a fresh packet/base and re-run all exit
proof, suite, runbook, and Phase 2 ledger gates.
