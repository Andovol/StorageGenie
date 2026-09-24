# SG-110 — HEIC/HEIF ingest: signature branch + decode support + thumbnails, owns its refresh ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D154-approved G-stage slice 1 of 5 (G7 HEIC → G5 → G6 → G3 → G4; L3-build, production touches take individual words — none here). Blueprint §5.2 step 1 names HEIC/HEIF; the tree accepts JPEG/PNG/WebP/TIFF/PDF only. SG-019 is the shape precedent (TIFF branch, same file, same test pattern — read `docs/packets/SG-019-tiff-detector-repair.md`). Current tree (verified 2026-09-24, re-verify — every premise below is a hypothesis): detector `_detect_media_type` (`evidence_service.py:56-75`) has branches for jpeg/png/pdf/webp/tiff and raises `unsupported media signature` otherwise · allowlist `allowed_mime_types` (`config.py:25`: jpeg/png/webp/tiff/pdf, NO heic) · `SUPPORTED_IMAGE_TYPES` (`signals.py:20`, same five) · thumbnails `_thumbnail_bytes` (`evidence_service.py:114-131`) route jpeg→JPEG-with-flatten, png/webp→same-format, and `{"image/png": "PNG", "image/webp": "WEBP"}[media_type]` at `:129` — a new image MIME WITHOUT a thumbnail rule dies in the best-effort handler with NO thumbnail (the trap: upload 201s while cards stay thumbnail-less) · deps `pillow>=10` (pyproject) with NO heif support anywhere in the tree (grep `heif|HEIF` over `backend/` = empty — Pillow cannot decode HEIC natively, so a decoder dependency is REQUIRED, unlike SG-019). THIS slice adds the subtype branch + decode support + thumbnail rule + tests, then refreshes the service (served-code change, D145). NO migration (no model change — prove by empty diff over `models/`+`alembic/`), NO frontend, NO sender, NO other product file. $0 — no metered call exists on any path (a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-24. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-24); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** HEIC/HEIF ONLY. Detector branch + opener registration + dependency declaration + allowlists (config + signals) + thumbnail rule + tests + `docs/worklogs` — NOTHING else. Exactly ONE recreate. Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05`).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-SC-12` · `PG-DP-02` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint, 600s build+recreate+verify, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none live** (tests on temp DBs; post-restart probes read-only — a write of any kind is a STOP). **Restart: ONE backend recreate (D145 standing + D154 L3-build). Deploy: THIS slice.**

## G1 — capture BEFORE (every observable the proof moves; `PG-EV-08`)

- Image id, `alembic current` (hypothesis single head — VERIFY, `PG-IC-09`), 25-table counts (hypothesis 25 — VERIFY), health exact, gate 301/401, HEIC probe: Pillow-generated or crafted `ftypheic` bytes through `POST /v1/evidence` with `image/heic` → quote the refusal (hypothesis 422 `unsupported media signature` — the fail-pre baseline). Quote all raw.

## G2 — HEIC/HEIF detected, decoded, thumbnailed (SG-019 shape; facts handed over)

- Detector branch in `_detect_media_type`: `ftyp` subtypes `heic/heix/hevc/heim/heis/hevm/hevs/mif1/msf1` (verify this list against the decoder's own documentation on target — an invented subtype is the defect class here) mapping to exactly `image/heic` / `image/heif` (which subtype maps to which is a design call inside the constraint "both blueprint names served"; report the table). Configured strings and detected strings quoted side by side (the SG-019 near-miss rule).
- Decode support: declare the decoder dependency where the tree declares deps (verify the install path on target — `requirements.lock` vs pyproject — do not inherit my line) + register its Pillow opener at the module site the decode path loads (verify import-time registration, never per-call). **What this choice turns on:** which module import the decode path always executes — a registration the server never imports is a silent no-op, so the route test below proves it end to end, never by import assertion alone.
- Allowlists: `config.py allowed_mime_types` + `signals.py SUPPORTED_IMAGE_TYPES` gain the SAME two literals (grep-gate both after the edit, `PG-SC-05` by rule — no third literal anywhere).
- Thumbnail rule: HEIC/HEIF MUST produce thumbnails like every image type (the `:129` trap above) — extend the rule (JPEG-flatten shape recommended: RGB convert + JPEG bytes) and PROVE `thumbnail exists` in the route test. A 201 without a thumbnail is a FAIL, not a pass.
- Tests (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; seen-to-fail in-run, `PG-EV-01`): detector unit legs for ALL SEVEN signatures (jpeg/png/pdf/webp/tiff/heic-heif) + negative leg (unknown bytes → exact `unsupported media signature` — the suite pins the complete table so the next MIME cannot repeat SG-018); real route legs: generated HEIC bytes through `POST /v1/evidence` → 201 with decodable dimensions AND thumbnail file present (generate at runtime via the decoder's own encoder; if the encoder is unavailable, STOP with the finding — do NOT commit an opaque binary without provenance, and do NOT fake the bytes). Non-`ftyp` HEIC variants outside the table stay rejected and documented (`PG-SC-07`).
- Full backend suite green modulo the 2 known decoder env reds (stash-proved on the slice — quote the proof), ruff clean, mypy delta 0, secret gate 0 real over changed files (quote the grep).

## G3 — refresh + verify (D145 owned refresh)

- One backend rebuild (new dependency installs here — quote the decoder version resolved) + exactly ONE recreate + verify. AFTER proofs quoted raw against G1 BEFORE: image id differs, `alembic current` unchanged, counts delta exactly zero, health exact ×6, gate 301/401, HEIC upload 201 through the FRESH server (read-only shape proof, temp household — no fixture rows left live).
- Post-restart sweep WAIVED (`PG-DP-02` — restart-gated); substitute: in-process suite pre-restart + post-restart probes as authority. No browser-driven tests on this path — state the derived set and that it differed nowise.
- Actual-versus-budget per leg with units (`PG-PR-06` stated against the build+recreate+verify bound).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-110.log`, `SG-110_report.md`, `SG-110_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + BEFORE/AFTER pairs). First token `SG-110`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `evidence_service.py` (detector + thumbnail rule + opener registration) + `config.py` allowlist + `signals.py` set + dependency declaration + tests + `docs/worklogs` (6 content paths) — NOTHING else (`models/` + `alembic/` + `frontend/` empty diff or STOP; `docker compose config` FORBIDDEN). Ordered paths committable (re-verify `.gitignore` before commit, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands migration, frontend, sender, second recreate, press, or any metered call — no cell collides; stated so the check exists on paper. Reads include pytest/TestClient + host commands + the authorized image build and ONE recreate; pulling/running any OTHER image or launching unnamed runtimes counts as execution — not authorised.
- Privacy: identifiers TEXT only; host `.env` never printed, never read into any artifact (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; fixture bytes generated at execution (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Pre-change HEIC legs fail with the quoted refusal; post-change real HEIC upload → 201 with decodable dimensions AND thumbnail present; all seven signature legs + negative green; configured==detected quoted side by side.
- Suite green modulo the 2 named reds; ruff/mypy/secret gates green with quoted proof; refresh proofs match BEFORE→AFTER with zero row delta; $0; production otherwise untouched; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): detection — does the new branch fire on real HEIC bytes and nothing else? thumbnails — does the new MIME leave the same artifacts every other image leaves? refresh — did the served backend actually change while data stood still?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-110 | Report: docs/worklogs/SG-110_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 600s build+recreate+verify · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
