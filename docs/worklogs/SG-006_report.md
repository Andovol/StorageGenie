SG-006 — Evidence verification and repair report

BASE REF: automation
BASE resolved: fd2c2f278bb07fb483f4affef8ced0f63d5465dc
WORK_HEAD: 2d70e2872f6174f08e4451bef2df27fc6e9652d1
Work dir: /home/andrei/StorageGenie
Remote: git@github.com:Andovol/StorageGenie.git
Model: unknown (the live Codex process arguments exposed no model id; no provider metadata was available)
Reasoning effort: high (live process argument `-c model_reasoning_effort=high`)
Timeouts: 120s ordinary commands; 600s full suite; 2100s overall. No command exceeded its bound or was killed.

## Scope and observed differences

The packet’s expected `backend/app/services/local_store.py` path differs from the tree: the actual module is `backend/app/storage/local_store.py`. Its `thumbnail_path(storage_key, size)` behavior was verified and reused; it was not modified. The service signature matched the packet. The configured defaults observed were `max_upload_bytes=20971520` and `thumbnail_sizes=[256, 512]`. `POST /v1/evidence` exists at `backend/app/api/v1/evidence.py`.

The pre-repair service had no pixel guard, wrote the original before image decoding, silently swallowed thumbnail failures, accepted claimed MIME fallback values, and the endpoint hard-coded thumbnail sizes. These were repaired only in the evidence service, actual storage helper usage, upload endpoint, config, and tests listed below. No migration, `.env`, restart, auth, export/UI, expiry, LLM/OCR, or secret change was made.

## G1 — store path and committed tests

`backend/tests/test_evidence_upload.py` uses an isolated temporary SQLite database and storage root under `/tmp/storagegenie-evidence-tests-*/` and creates a test household per case. It never uses `/data/db/storagegenie.db`, `/data/storage`, `backend/data/db`, or `backend/data/storage`.

The non-vacuous tests prove:

- repeated identical bytes return the same evidence id, SHA-256, and storage key;
- different bytes create different rows, hashes, and keys;
- exactly one `evidence.create` audit row is present for each newly stored item;
- generated JPEG thumbnail files exist at configured sizes;
- thumbnail failures are warning-logged with SHA and size and leave no temporary thumbnail file.

The written original is atomically stored through `storage_path_for`; thumbnail writes are buffered and atomically renamed. A pre/post SHA-256 comparison proves original bytes are unchanged.

## G2 — dynamic decompression-bomb guard

`backend/app/config.py` adds the named env-overridable `max_image_pixels: int | None = None`. `None` leaves Pillow’s native `Image.MAX_IMAGE_PIXELS` unchanged; a configured value is checked against decoded image dimensions without a hard-coded production pixel number. `DecompressionBombWarning` is escalated to an error inside `warnings.catch_warnings()` only around image decoding. Both configured and native Pillow rejection logs include SHA, dimensions, limit kind, and the configured limit where applicable. The service rejects before creating the storage directory or writing the original.

The first native-Pillow bomb test exposed a real failure: Pillow’s warning text contained only total pixels, so the log emitted `dimensions=unknown`. That run was recorded in `docs/worklogs/SG-006.log` as `G2_failing_run_rc=1`. The repair probes the header under an inner ignore-only warning scope and has a PNG fallback; the corrected logs observed `5000x5000` for `max_image_pixels` and `10000x10000` for `pillow_max_image_pixels`.

The bomb assertions observed HTTP 422 with `decompression_bomb` and `max_image_pixels` in the detail, the SHA/dimensions in the warning log, zero evidence rows, no household/SHA storage directory, and no `*.tmp` file. The focused bomb run was 2 passed, 6 deselected, 1 warning in 0.51s.

## G3 — derivative property and original immutability

The acceptance property is byte-level: each written thumbnail is reopened and its parsed EXIF mapping is empty, the GPS tag is absent, and the parsed GPS IFD is empty. The derivative save passes empty EXIF metadata after orientation normalization. The original JPEG’s SHA-256 before and after storage is identical. This is a property check on written bytes, not a check that a named function was called.

## G4 — upload endpoint reject paths

`TestClient` observed all required paths end to end:

- duplicate JPEG upload: both responses were 201 and returned the same id;
- body above a monkeypatched configured `max_upload_bytes=32`: 413 with detail naming `max_upload_bytes` and `32`;
- JPEG bytes claimed as `image/png`: 422 with `media_type_mismatch` detail.

The endpoint now maps byte-limit errors to 413, validation/signature/bomb errors to 422, and validates configured thumbnail sizes rather than a duplicated literal list. The dead duplicate return block was removed.

## Gates and provenance

The system PATH did not contain `ruff` or `pytest` (both returned 127); the checked-in `/home/andrei/StorageGenie/venv/bin` tools were used for all actual gates. `ruff check app tests` checked the backend app and tests with zero findings and output `All checks passed!`. The full suite command was bounded at 600s and collected 11 tests: `11 passed, 1 warning in 0.59s`, exit 0. The sole warning is an installed FastAPI/Starlette deprecation warning recommending `httpx2`; no evidence test was skipped and no gate exited 5.

The repository outputs are `backend/app/api/v1/evidence.py`, `backend/app/config.py`, `backend/app/services/evidence_service.py`, `backend/tests/test_evidence_upload.py`, `docs/worklogs/SG-006.log`, and this report `docs/worklogs/SG-006_report.md`. The actual helper `backend/app/storage/local_store.py` was checked and unchanged. `git diff --check` passed. The temporary runtime database/storage paths are test fixtures, not repository outputs; no production datastore or storage path was touched.

## G6 — evidence ref and receipt

The candidate to prefill is exactly `WORK_HEAD` above. The first prefill from the pre-merge candidate `6d57bc2d0d2dc249286ee537d09a43da8d4866be` was rejected non-fast-forward because the existing evidence tip was not its ancestor; no force push was used. The content-neutral merge of that evidence history produced `2d70e2872f6174f08e4451bef2df27fc6e9652d1`, which is now the candidate. The mandated command is `git push origin 2d70e2872f6174f08e4451bef2df27fc6e9652d1:refs/heads/storagegenie-evidence` with a 120s bound, followed by fetch and equality verification. The unmodified publisher invocation is `/opt/storagegenie-dispatch/finalize_dispatch_report.sh SG-006 "contract_sync=refresh version=0.17.2" docs/worklogs/SG-006_report.md 2d70e2872f6174f08e4451bef2df27fc6e9652d1`. Its return output, receipt hash, trailer proof, and final clean-tree proof are recorded in the final handoff and execution log.

UNCLEAR — FIRST READ: The repository lacks the referenced ARCHITECT.md, PACKET.md, DISPATCH.md, and PRODUCTION.md files; the supplied packet plus AGENTS.md and STATE.md were available. The packet’s local_store path was corrected to the actual tree path noted above.
UNCLEAR — DURING EXECUTION: System PATH omitted the checked-in Ruff/Pytest executables; the bounded gates were answered successfully through `/home/andrei/StorageGenie/venv/bin`. No privileged operation, SSH check, service restart, or production datastore write was attempted.
UNCLEAR — REMAINING: Publisher/ref receipt completion and final clean-tree state are pending the mandated prefill and unmodified publisher invocation; no other slice work remains.
