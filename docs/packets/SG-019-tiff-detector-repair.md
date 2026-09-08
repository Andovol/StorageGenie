# SG-019 — TIFF signature detection repair (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

**Stage:** Phase 1 repair slice (D11) — closes ISS-3 so the exit re-run (SG-020) can prove the five-input fixture. SG-018 STOPped correctly on the quoted 422: `allowed_mime_types` advertises `image/tiff` but `_detect_media_type` (`backend/app/services/evidence_service.py:56-73`, verified by direct read) has no TIFF branch. This slice adds exactly that branch. Nothing else.
**Standing lines (SG-014/SG-018 levers, first carriers noted):** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; an upload-availability premise cites the detector code, never the config list — this packet obeys both by construction (the detector hunk IS the slice).

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

**DATABASE: none live. Restart: none.** NO migration. All proof in-process via `TestClient` + temp DBs (`PG-PR-04`). Test rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): finish inside 2100s, report elapsed against it. Coder-side `python`/`pytest` are absent on the host PATH — name `venv/bin/` binaries explicitly.

## Why this exists

The five-input exit fixture needs a real TIFF through `POST /v1/evidence`, which 422s today. The detector checks four signatures (JPEG `ffd8ff`, PNG `89PNG`, PDF `%PDF`, WEBP `RIFF....WEBP`) and raises `media_type_mismatch: unsupported media signature` for anything else. Classic TIFF magic is `II*\0` (little-endian) and `MM\0*` (big-endian); BigTIFF variants are explicitly out of scope (rejected as before, documented). Pillow decodes classic TIFF natively, so no other pipeline change is needed — verify that by decoding the fixture in the test rather than assuming it.

## G1 — TIFF detected, uploaded, decoded (`PG-EV-01`, `PG-EV-05`, `PG-EV-09`)

- Add the TIFF branch to `_detect_media_type` returning exactly `image/tiff` (the configured string — quote both lines to prove they match; a near-miss string is the defect class here).
- Real route proof: Pillow-generated classic TIFF bytes (both endiannesses — Pillow writes one by default; craft or convert for the other) through `POST /v1/evidence` with `image/tiff` → 201, then decoded dimensions readable (Pillow path, not filename inference).
- Detector unit legs for ALL FIVE supported signatures (JPEG/PNG/PDF/WebP/TIFF) plus one negative (unknown bytes → the exact `unsupported media signature` error): the suite must pin the complete signature table so the next added MIME cannot repeat this class.
- Fail-first with both runs in the committed log: pre-change the TIFF legs fail with the quoted 422 (reproduce SG-018's probe first — it is the baseline, not Bedrock).

## G2 — No collateral (`PG-EV-01`)

- Full backend suite green except the two named ISS-1 decoder nodes and the one known stale `test_candidates.py` migration assertion (all three quoted with node IDs — SG-020 owns that repair, not this slice); `ruff` clean quoted; `mypy` advisory count quoted. `test_export.py` head test green (no migration here, but the discipline is free).

## G3 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-019.log` and `{{WORKLOG_DIR}}/SG-019_report.md`, first token `SG-019`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget with units. State model/effort provenance from process arguments.

## G4 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-019 | Report: docs/worklogs/SG-019_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/services/evidence_service.py` (detector branch ONLY — upload/decode/thumbnail logic untouched) + TIFF legs appended to `backend/tests/test_evidence_upload.py` (upload route) and the detector unit legs in the same file or a focused new module (your call, record why) + `docs/worklogs` files + the G4 note mechanism. No migration, no other product file, no new dependency, no `.env`/restart/secrets/infra, no AI/LLM/provider code. Anything else is a STOP ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling. Recorded here once, not per criterion.
- Exclusions by rule: no route decorator is added or modified (`PG-SC-05`); grep-gate and report. No new MIME string is introduced anywhere (the configured `image/tiff` is the only literal).
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite (quote file + test counts); every gate names what it checked; a gate emitting no output is a FAIL. mypy advisory — quote, fix nothing outside the ceiling. Decoder-dependent tests FORBIDDEN (ISS-1 — node IDs quoted if excluded).
- Budget: 120s per ordinary command, 600s per suite leg, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run. Do not require what the confinement forbids.

## Acceptance criteria

- Pre-change TIFF legs fail with the SG-018 422 quoted; post-change real TIFF upload (both endiannesses) → 201 with decodable dimensions; all five signature unit legs + negative leg green.
- Configured `image/tiff` and detected `image/tiff` quoted side by side from the tree (the match IS the property).
- Full suite green except the three named nodes (2 ISS-1 + 1 stale, IDs quoted); ruff clean; mypy advisory quoted; export head test green.
- BigTIFF correctly rejected (documented, not attempted).
- Worklog + report committed; notes ref carries the `Dispatch-ID: SG-019` + `Report:` note, quoted, dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — from process arguments (proven readable), never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite legs, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
