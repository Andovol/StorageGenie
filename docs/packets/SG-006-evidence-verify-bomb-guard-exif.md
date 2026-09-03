# SG-006 — Evidence verify/repair: SHA-256 service, dynamic bomb guard, EXIF-free derivatives (Codex High)

> Facts below are what I believe from the tree that carries this packet. **They are EXPECTED conditions,
> not established truth. Verify each before building on it; a difference is a finding, not an obstacle.**
> For any number, path or quoted line I hand you: if your figures differ from mine, investigate and
> explain — **do not bend your answer to match mine. Correcting me is worth more than agreeing with me.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: none. Restart: none.** All verification runs against temp SQLite / `TestClient` with an isolated temp storage root. No prod-row writes; no service restart.

## Why this exists

`backend/app/services/evidence_service.py:38-122` already implements the Task 5 core well: SHA-256 computed before expensive work, idempotent return on duplicate, `IntegrityError` race handling, magic-byte detection (`_detect_media_type`), atomic original write (`.tmp` + rename), audit in the same transaction. What is missing per the accepted register (`docs/decisions/2026-09-03-accepted-optimizations.md`): no decompression-bomb guard (`TS-2`), no EXIF/GPS property on derivatives (`TS-3`), and no committed tests (`backend/tests/test_evidence_upload.py` absent — suite covers health only). The thumbnail path also swallows all errors silently (`evidence_service.py:90-91` bare `except: pass`).

Expected conditions (verify, do not trust):
- `store_evidence` signature `(file_bytes, original_filename, media_type, household_id, db, actor="api")`
- `ALLOWED_MEDIA` covers jpeg/png/webp/pdf by magic bytes; `settings.max_upload_bytes` is 20 MB; `settings.thumbnail_sizes` is `[256, 512]`
- `local_store.thumbnail_path(storage_key, size)` derives `*_thumb<size>` siblings; originals stored at `<root>/<household>/<sha[:2]>/<sha><ext>`
- `POST /v1/evidence` exists in `backend/app/api/v1/evidence.py` (verify its reject paths rather than assuming them)
- SG-005 baseline green: `ruff` clean, `pytest` non-vacuous, `busy_timeout=5000`, lockfile present

## G1 — Verify/repair the store path, with committed tests (`BM-3`)

- Add `backend/tests/test_evidence_upload.py`: same bytes twice → same row id/sha/storage_key; different bytes → different rows; audit `evidence.create` row written per store; thumbnail file exists for a generated JPEG (all against temp DB + temp storage root, never prod paths).
- Repair what the tests find (if anything) inside `evidence_service.py` / `local_store.py` only. Log thumbnail failures instead of swallowing them (named logger, warning with sha + size) — silence is not a handling strategy.
- Run the FULL backend suite; exit 5 or a skipped evidence module is a FAIL.

## G2 — Dynamic decompression-bomb guard (`TS-2`, cap policy `m0019`)

- No custom magic pixel number. Keep Pillow's own `MAX_IMAGE_PIXELS` default; escalate its `DecompressionBombWarning` to an error at the service boundary (`warnings.simplefilter('error', …)` scoped to the decode, not process-global); log the rejection with sha + pixel dimensions; reject visibly (`422` with detail naming limit-kind, never silent).
- Add a named, env-overridable setting (e.g. `max_image_pixels`, default unset = Pillow default) so the threshold is dynamic per the owner's cap directive — code never hard-codes a pixel count.
- Test with a small-file/huge-dimension image (e.g. crafted BMP or Pillow-generated): assert visible `422`, no thumbnail, no row, no partial file left behind. The failing run is committed in the log (`PG-EV-09`).

## G3 — EXIF-free derivatives, proved at the byte level (`TS-3`, `PG-EV-05`)

- After `exif_transpose`, derived thumbnails must carry no EXIF/GPS metadata while originals stay byte-identical (immutability preserved — hash the original before and after).
- State the PROPERTY, not the command: acceptance is a byte-level check on written thumbnails (parsed EXIF tags absent, GPS absent), not "called function X". If Pillow's transpose already strips everything, the test documents that observed fact and no code changes — a verified no-op reported as such is a success.

## G4 — Upload endpoint reject paths, verified not assumed

- Exercise `POST /v1/evidence` end to end via `TestClient`: duplicate upload returns the same id; oversize body gets a visible reject naming the configured limit; claimed-vs-signature MIME mismatch gets a visible `422`.
- Repair mismatches inside `backend/app/api/v1/evidence.py` only. No new endpoints, no auth changes.

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-006.log` and `{{WORKLOG_DIR}}/SG-006_report.md`, first token `SG-006`, every output path named in the report committed, three UNCLEAR lines at the end. Failing runs (G2 bomb test, any G1/G4 repair) committed in the log, not only quoted in prose.

## G6 — Prefill the evidence ref, then auto-publish

- After WORK_HEAD is pushed to `automation`: `git push origin <WORK_HEAD>:refs/heads/storagegenie-evidence` (120s bound), then `git fetch origin refs/heads/storagegenie-evidence` and verify `git rev-parse origin/storagegenie-evidence` equals WORK_HEAD — quote both hashes. The publisher gates on this equality (`candidate_not_remote`); the prefill is what establishes it. If the push is non-fast-forward, merge content-neutrally and push the merge — never force-push (`CO-54`, as SG-005 demonstrated).
- Only then invoke `{{RECEIPT_CMD}}` with (`SG-006`, header `contract_sync=refresh version=0.17.2`, report path, WORK_HEAD), unmodified. A repair need is a finding, never a local patch to the wrapper.
- A `candidate_not_remote` from the unmodified publisher AFTER the verified prefill is a STOP — commit `BLOCKED`, push, report. Never hand-move the ref by other means and never force-push outside the publisher (`CO-54`).
- Verify the artifact, not the command: the evidence ref carries a commit with the `Dispatch-ID: SG-006` trailer — quote its hash. A zero-exit publish with no such commit is a FAIL.

## Constraints

- Scope ceiling: evidence service + derivatives + upload endpoint only — no asset/export/UI behaviour change, no expiry/LLM/OCR, no migrations, no `.env`/restart/secrets. Writes permitted: `backend/tests/test_evidence_upload.py`, repairs inside the three evidence files named above, one config setting, `docs/worklogs` files, and the G6 prefill/publish mechanism. Anything else is a STOP, not a stretch goal ("STOP and report" is not satisfiable by disclosure — disclosing an out-of-scope change does not authorize it).
- Cross-product (`PG-IC-01`): the G2 setting alters a limit, not product behaviour; G3 may alter derivative bytes but never originals (hash-proved); no acceptance criterion requires anything the ceiling forbids.
- No datastore writes outside temp space; accidental prod rows reported with identifiers and left in place (`PG-EV-06`).
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs; every gate names the files it checked and its match counts; a gate emitting no output is a FAIL, not a pass.
- Budget: 120s per ordinary command, 600s for the suite, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run — host paths and the prefill/publish return codes are the verification. Do not require what the confinement forbids.

## Acceptance criteria

- Duplicate bytes → same id/sha/storage_key; audit row per store; JPEG thumbnail file exists — all on temp paths, prod paths untouched (stated with the paths).
- Crafted huge-dimension image → visible `422` naming the limit-kind, logged with sha + dimensions, no row, no partial file; threshold is a named setting, no magic number in code.
- Written thumbnails byte-proved EXIF/GPS-free; originals hash-identical before and after.
- Upload endpoint: duplicate same-id, oversize visible reject, MIME-mismatch `422` — all observed via `TestClient`, not read from code.
- `ruff` clean with output quoted; full suite non-vacuous.
- `docs/worklogs/SG-006.log` and `docs/worklogs/SG-006_report.md` committed; every output path in the report committed.
- `storagegenie-evidence` carries the `Dispatch-ID: SG-006` receipt commit; hash quoted; prefill equality quoted before publish.
- No criterion passed vacuously — an empty test, an empty log, or a skipped leg is declared loudly, never a pass.

## Report

- Work dir `/home/andrei/StorageGenie`, remote `git@github.com:Andovol/StorageGenie.git`, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite, 2100s overall (`TIMEOUT_S=2100` in wrapper).
