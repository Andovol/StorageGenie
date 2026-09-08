# SG-020 — Phase 1 exit E2E + runbook + close-out, re-run (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

**Stage:** Phase 1 exit re-run (D11) — SG-018 STOPped correctly on the TIFF detector gap (ISS-3, now closed by SG-019: detector branch at `backend/app/services/evidence_service.py:66-67` returning exactly `image/tiff`, proved by real both-endian `POST /v1/evidence` uploads in `backend/tests/test_evidence_upload.py`, rated 98). This packet re-runs the complete exit scope from the current base. SG-018's BLOCKED report (`docs/worklogs/SG-018_report.md`) is prior art for the probe shape, not a base: re-verify everything below against the tree as built.
**Carries (verify, do not re-derive):** (a) stale `test_candidates.py` migration assertion (explicit-revision pattern per SG-015 precedent) → test-only repair here; grep the suite for remaining head-relative downgrade assumptions and leave none stale. (b) ISS-1 decoder legs stay carried to the manual compose pass — no test here imports pyzbar/pytesseract or depends on real decoders; decoder-kind E2E assertions are present-or-degraded, never decoder-dependent. (c) A "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination (standing SG-014 lever line). (d) Upload-availability premises cite detector code with line numbers, never the config list (standing SG-018 lever line — obeyed: TIFF cites `evidence_service.py:66-67`).

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
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.** (Effort is proven readable from process arguments — do the same.)

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

**DATABASE: none live. Restart: none.** NO migration is authorised in the exit slice — a schema need discovered now is a STOP that becomes its own slice, never a quiet addition. All proof in-process via `TestClient` + temp DBs (`PG-PR-04`). Test rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): finish inside 2100s, report elapsed against it. Coder-side `python`/`pytest` are absent on the host PATH — name `venv/bin/` binaries explicitly.

## Why this exists

Six build slices plus one repair built the machine; the wall-to-wall proof still never ran. The Phase 1 exit condition (blueprint:513) — ingest a mixed folder, resume after failure, request human review including manual expiry entry, no LLM — must be proved with ids chained leg to leg, plus the UV-5 duration, plus a runbook a human can follow, plus an explicit statement of what the NEXT stage owns. Handed route inventory (verify each before chaining): `POST /v1/imports` (evidence_ids + Idempotency-Key) → `POST /v1/imports/{id}/run` → `GET /v1/imports/{id}` (steps/outputs/progress/errors) → `POST /v1/imports/{id}/retry`; `GET /v1/candidates/{id}`; `POST /v1/candidates/{id}/decision` (accept/edit/hold/reject, 409 while tasks open); `GET /v1/review-tasks` + `POST /v1/review-tasks/{id}/resolve`; plugin classify + manual expiry + extensions under `/v1/plugins/expiry-tracker/assets/{id}/...`; `GET /v1/assets?q=` (FTS); `GET /v1/assets/{id}` (assertions/evidence/audit); `GET /v1/export` (manifest). Fixture generators exist in-tree: QR via the `qrcode` dev dependency, EAN bars + text PNG + EXIF JPEG + dHash pairs per `test_signals.py` patterns, real TIFF upload per the SG-019 legs, hand-inserted observations where decoders are unavailable (ISS-1).

## G1 — exit E2E, one fixture, ids chained (`PG-EV-01`, `PG-EV-05`, `PG-EV-09`, `PG-SC-09`)

- New `backend/tests/test_phase1_e2e.py::test_phase1_exit_condition`: temp folder with five generated inputs (EXIF-dated JPEG, QR image, EAN-13 image, plain PNG, TIFF — the TIFF leg uploads through the real `POST /v1/evidence` route per the SG-019 proof, never a direct row) uploaded as evidence, then ONE import job whose every leg asserts against ids created in legs 1–2 (fixed-id replay is vacuous — banned).
- Legs: create→201 with six step rows; run reaches `AWAITING_REVIEW`; observations exist for available extractors (phash/exif rows asserted by row; decoder-kind rows asserted ONLY as service-tolerant — present-or-degraded, never decoder-dependent, ISS-1); near-duplicate pair proposes `similar`; identifier collision opens a review task AND blocks commit (prove the 409); injected step failure → `FAILED` with catalog unchanged → `retry` → resumes to `AWAITING_REVIEW` (failure via the SG-013 monkeypatch pattern or a quarantined-then-fixed input — your call, quote which); manual expiry entry resolves `needs_evidence` → accepted user-sourced assertion; accept commits asset + assertions + evidence links + lifecycle audit atomically; `GET /assets?q=<stem>` finds the committed asset through FTS (identity assertion on the created id); `GET /export` contains both ids (SG-010 discipline).
- UV-5 duration: `job-created → asset-accepted` computed from that fixture's own `audit_event` rows — present, ordered, non-negative; quote the value, single-run honesty (`G-A3`).
- Fail-first quoted, or "already passed, hardened" with the passing run quoted — no third option.

## G2 — stale-test repair + suite green (test-only, `PG-EV-01`)

- Repair the stale `test_candidates.py` migration assertion to the explicit-revision pattern (SG-015 precedent); grep the suite for remaining head-relative downgrade assumptions and leave none stale (quote the grep). Product files untouched for this leg — a product change need is a STOP, not a stretch.
- End state: full backend suite green EXCEPT the two named ISS-1 decoder node IDs (quoted); `ruff` clean quoted; `mypy` advisory count quoted; frontend suites WAIVED with reason (no frontend file in this ceiling; SG-016 proved them green and this slice cannot regress them — name that substitution explicitly per `PG-DP-02`).

## G3 — Phase 1 runbook (SG-010 G3 discipline)

- Extend `README.md` with a Phase 1 section: job create/run/retry via routes (curl shapes matching the actual endpoints), review flow (queue → candidate → decision → resolve), manual expiry entry, FTS rebuild function + when to call it, `make check-postgres-dialect`, data locations (unchanged), trust boundary (unchanged: LAN-only, single household, no auth), and the honest verification map (what the E2E proves, what ISS-1 carries to the manual compose pass, no browser automation).
- Verify by reading: every named command, path, route, and line reference checked against the tree; mismatches fixed, not excused. A runbook line describing absent behavior is a finding, not a line.

## G4 — Phase 2 door ledger (decisions, not code)

- Report section naming what Phase 2 owns on arrival: ADR-004 (provider abstraction), ADR-007 (privacy/external-AI), ADR-010 (guardrail tracking) — explicitly NOT written here; provider keys, costs, and household-data-egress choices as owner decisions (they fire `G-K1`/`G-K2` at every autonomy level and cannot be pre-approved); deferred manual compose pass scope (ISS-1 re-proof + image build + compose-up/UI/restart). No code, no ADR, no provider research in this slice.

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-020.log` and `{{WORKLOG_DIR}}/SG-020_report.md`, first token `SG-020`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget with units. The report carries the exit-condition checklist: each blueprint:513 clause → evidence pointer (test lines + quoted values). State model/effort provenance from process arguments.

## G6 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-020 | Report: docs/worklogs/SG-020_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/tests/test_phase1_e2e.py` (new) + TEST-ONLY repair to `backend/tests/test_candidates.py` (migration assertion only) + `README.md` (Phase 1 section only) + `docs/worklogs` files + the G6 note mechanism. No product file, no migration, no frontend file, no new dependency, no `.env`/restart/secrets/infra, no AI/LLM/provider code, no ADR. Anything else is a STOP ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — the E2E uses only proved routes, the repair touches no product file, the runbook touches no code. Recorded here once, not per criterion.
- Exclusions by rule: no backend or frontend route, component, or migration file is added or modified (`PG-SC-05`); the E2E test file is the single exception. Grep-gate and report.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite (quote file + test counts) with the ONLY permitted reds being the two named ISS-1 decoder nodes; every gate names what it checked; a gate emitting no output is a FAIL. mypy advisory — quote, fix nothing outside the ceiling.
- Budget: 120s per ordinary command, 600s per suite leg, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run. Do not require what the confinement forbids.

## Acceptance criteria

- `test_phase1_exit_condition` chains create→run→review→retry→manual-entry→commit→FTS-find→export on fixture ids, with the 409-block, rollback-safe retry, atomic commit, and UV-5 duration all quoted from that run; decoder-kind assertions tolerant per ISS-1 (present-or-degraded stated per leg).
- Full suite green except the two named ISS-1 nodes (node IDs quoted); no stale downgrade assumption remains (grep quoted); ruff clean; mypy advisory quoted.
- README Phase 1 section read-verified against the tree (every command/path/route checked); verification map states E2E coverage + ISS-1 carry + no-browser-automation honestly.
- Phase 2 door ledger names ADR-004/007/010 as unwritten, provider/money/egress as owner decisions, manual pass scope as pending — no code toward any of them.
- Exit-condition checklist in the report maps each blueprint:513 clause to evidence.
- Worklog + report committed; notes ref carries the `Dispatch-ID: SG-020` + `Report:` note, quoted, dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — from process arguments (proven readable), never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite legs, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
