# SG-013 — Deterministic signal extraction: OCR, barcode/QR, EXIF, pHash (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

**Stage:** Phase 1 slice 2 of 7 (plan `docs/superpowers/plans/2026-09-08-phase-1-deterministic-import.md`, D9). SG-012 landed (`f0709f7`, rated 98): the `execute_step` seam (`backend/app/services/job_service.py:105-116`) returns `not_implemented` for `EXTRACTING_DETERMINISTIC_SIGNALS` — this slice fills that body and no other stub (`DEDUPLICATING`/`COMMITTING` stay stubbed for SG-014; touching them is a STOP, not a stretch goal).

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
> to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: none live. Restart: none.** One Alembic revision is authorised (the `observation` table below); it is exercised `upgrade head` + `downgrade -1` + `upgrade head` against temp SQLite only (`PG-PR-04`: the running service is not touched; all proof in-process via `TestClient` + temp DBs). Test rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): finish inside 2100s, report elapsed against it. Coder-side `python`/`pytest` are absent on the host PATH — name `venv/bin/` binaries explicitly.

## Why this exists

The import runner persists steps but extracts nothing. Evidence upload already proves bytes are safe (SHA-256, signature/MIME validation, bomb guard, EXIF-free derivatives — SG-006, re-proved SG-011), but no OCR text, barcode/QR value, EXIF timestamp, or perceptual hash is ever read. This slice adds the four deterministic extractors behind the blueprint §5.3 quality gates and stores their outputs as `observation` rows the SG-014 dedup slice will consume. Dependency choice is fixed by the stage plan (simplicity, `G-A7`): `pyzbar` (+ apt `libzbar0`), `pytesseract` (+ apt `tesseract-ocr` with `eng` data only), Pillow EXIF (already a dependency), hand-rolled dHash on Pillow (no new dep). If a fixed system package is uninstallable in this environment, that leg is a STOP with the package-manager output quoted — never a source build, never a vendored binary.

## G1 — extractors + observations + one migration (`PG-EV-01`, `PG-EV-05`, `PG-EV-09`, `PG-SC-02`)

- New `backend/app/services/signals.py` (module split is your call; the seam it feeds is `execute_step`): `extract_observations(evidence_id) -> list[Observation]` reading the stored original through the existing storage layer (never a re-upload, never a mutated original — SG-006 immutability holds).
- Exactly one migration: `observation` (`evidence_id` FK → `evidence.id`, `kind` in {ocr, barcode_qr, exif, phash}, `value_json`, `confidence` nullable, created-at). No other schema change; a second table is a STOP.
- `EXTRACTING_DETERMINISTIC_SIGNALS` step body becomes real: runs the extractors over the job's evidence ids, writes observations, records observation ids + counts in `output_refs`. Read-back trace (`PG-SC-02`): observation rows are read back through the step `output_refs` ids plus a service-level getter covered by tests; the HTTP route that serves them arrives in SG-014/SG-016 — state this boundary in the report so the field is never orphaned.
- §5.3 gates as behavior: check-digit/syntax-validated codes only (EAN-13/UPC-A check digit verified, QR syntax-checked; failures → low-confidence `barcode_qr` observation, never an identifier); OCR stores text + boxes + mean confidence; EXIF timestamps stored only when the new `exif_timestamps_enabled` setting allows, GPS-derived fields never (default off, `m0019` named-setting discipline); dHash hex stored per image; corrupted/unsupported input quarantines the step (`FAILED` with reason, job resumable) rather than crashing.
- Fail-first with both runs in the committed log: new tests fail pre-change (no module, no table, stub output), pass post-change. Control (`PG-EV-01`): feed a deliberately bad-checksum barcode and a corrupted image and quote the quarantine/low-confidence path firing.

## G2 — dependency, lockfile, image discipline (TS-4)

- `backend/pyproject.toml` gains exactly `pyzbar` + `pytesseract` (test-only fixture generators, if any, go in `dev` — and only if committed-binary fixtures cannot cover the case; justify each); `backend/requirements.lock` regenerated with pinned versions quoted in the report (mechanism is your call; pins are the property).
- `backend/Dockerfile` gains exactly the two apt packages (`tesseract-ocr` + `libzbar0`, `--no-install-recommends` retained). `docker build` is NOT runnable here (no privilege — report as unanswered per the block above, not routed around); verification is the Dockerfile diff plus package-name provenance quoted from the local apt cache where available. The deferred compose build (manual pass) is where the image proves itself — record that handoff, do not claim it.
- `allowed_mime_types` gains `image/tiff` as a named config change; HEIC stays out (recorded deferral — attempting it is out of scope).

## G3 — fixtures that cannot lie

- Fixtures are machine-generated at test time (Pillow-rendered text PNG, Pillow-written EXIF JPEG, generated QR/EAN-13) or committed binaries with SHA-256 quoted in the log — your call per fixture, byte-stability is the property either way. All fixture *outputs* go to temp paths. A test that decodes a value the test itself hardcoded into the generator input still proves the round trip honestly; a test that asserts on a committed binary proves the decoder — say which each test is.

## G4 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-013.log` and `{{WORKLOG_DIR}}/SG-013_report.md`, first token `SG-013`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget with units.

## G5 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-013 | Report: docs/worklogs/SG-013_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/services/signals.py` (+ `observations.py` only if the split earns it) + `backend/app/services/job_service.py` (EXTRACTING step body only — DEDUPLICATING/COMMITTING bodies untouched) + `backend/app/config.py` (named settings only) + `backend/tests/test_signals.py` (new; may extend `test_import_jobs.py` only for the step-body leg) + one migration file + `backend/pyproject.toml` + `backend/requirements.lock` + `backend/Dockerfile` (apt lines only) + `docs/worklogs` files + the G5 note mechanism. No frontend, no new routes, no `.env`/restart/secrets/infra, no AI/LLM/provider code. Anything else is a STOP ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — none requires a second migration, a new route, a worker, or a production write. Recorded here once, not per criterion.
- Exclusions by rule: no route decorator outside the existing `/v1/imports*` + `/v1/jobs*` surface is added or modified (`PG-SC-05`); grep-gate the decorators and report the match list. No new `source_type` value beyond what the assertion model already carries — observations are not assertions; minting assertion semantics here belongs to SG-014.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo`, `docker`, or `apt` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs (quote file + test counts); every gate names the files it checked and its counts; a gate emitting no output is a FAIL. mypy stays advisory — quote the count, fix nothing outside the ceiling.
- Budget: 120s per ordinary command, 600s per suite leg (apt/pip legs may approach this — report actuals), 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run. Do not require what the confinement forbids.

## Acceptance criteria

- Generated QR + EAN-13 images decode to their exact values with confidence recorded; bad-checksum barcode yields a low-confidence observation and no identifier anywhere (quote the control run).
- Rendered-text PNG OCR returns the string with mean confidence; EXIF-dated JPEG yields a timestamp observation with the gate on and none with it off; GPS-derived fields never stored in either mode.
- dHash equal for identical bytes, near for a resized copy (distance quoted against the named threshold), far for a different image.
- Corrupted/unsupported input quarantines: step `FAILED` with reason quoted, job resumable via the SG-012 retry path (prove one retry-after-quarantine with a fixed input).
- `EXTRACTING_DETERMINISTIC_SIGNALS` output_refs carry observation ids + counts; service getter returns the rows; SG-012 suite still green (no seam regression).
- One migration with temp-DB upgrade/downgrade quoted; `test_export.py` head test still green; lockfile pins quoted; Dockerfile diff minimal with install-time provenance or an honest unanswered leg.
- ADR-003 needs no amendment, or the amendment is a finding with the exact lines named (not a silent edit).
- Worklog + report committed; notes ref carries the `Dispatch-ID: SG-013` + `Report:` note, quoted, dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite legs, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
