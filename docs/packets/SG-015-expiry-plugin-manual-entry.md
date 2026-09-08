# SG-015 — Expiry Tracker plugin skeleton + test-layer repairs (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

**Stage:** Phase 1 slice 4 of 7 (plan `docs/superpowers/plans/2026-09-08-phase-1-deterministic-import.md`, D9, D10 resume). SG-014 landed (`5d61d43b`, rated 96): candidates commit atomically, review queue is real, `identifier` convention established (`field_path="identifier"`). This slice registers the first plugin and the manual expiry-entry flow. It also carries two bounded TEST-ONLY repairs from the SG-014 audit (G0 below) — product files are untouched for those legs.
**Established premises (verify, do not re-derive):** PDF evidence quarantines at EXTRACTING (SG-013 media gate); ISS-1 decoder legs stay carried to the manual compose pass — no test in this slice imports pyzbar/pytesseract or depends on the real decoders; hand-insert observations (pattern `test_signals.py:210-212`).

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
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.** (SG-014 proved effort IS readable from process arguments — `codex exec ... -c model_reasoning_effort=high` — do the same.)

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

**DATABASE: none live. Restart: none.** At most one Alembic revision, and only if the classification-storage decision (G1) requires a table; exercised `upgrade head` + `downgrade -1` + `upgrade head` against temp SQLite only (`PG-PR-04`: the running service is not touched; all proof in-process via `TestClient` + temp DBs). Test rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): finish inside 2100s, report elapsed against it. Coder-side `python`/`pytest` are absent on the host PATH — name `venv/bin/` binaries explicitly.

## Why this exists

Deterministic import works but the product has no domain: no category, no behavior profile, no expiry state — and no place for manual expiry entry, which is the ONLY Phase 1 path to a resolved expiry date (LLM banned; fabrication forbidden by blueprint §9.3/§15.2). Handed blueprint facts (verify against `inception/generic_asset_catalog_expiry_tracker_blueprint.md:359-407`): plugin = taxonomy + behavior profile per category + extension JSON Schema + prompt fragments (NOT Phase 1) + UI form metadata; categories Food&Beverages (30/7/1-day tiers, build first) and Medicine/pharma (shorter windows, build second); Cosmetics/Household/Documents structures present but inactive (no opened-date mechanic until Phase 3); date-type enum (expiry/best-before/use-by/manufacture+offset/PAO/batch-lot) and unit enum (blueprint §9.2); `needs_evidence` + review task when no date is visible; NO expiry assertion at all for inapplicable categories; plugins cannot redefine core fields (identifier, condition, location, status). Assertion review states include `needs_evidence` (blueprint:211); the current model defaults to `accepted` (`models/assertion.py:19`) — the manual-entry flow must write the states explicitly, never rely on defaults.

## G0 — test-layer repairs from the SG-014 audit (TEST FILES ONLY, `PG-EV-01`)

- **Coupling:** `backend/tests/test_evidence_upload.py:11-28` builds its engine/SessionLocal at import time from the settings singleton, so any alphabetically-earlier test module importing `app.config` first silently re-points its database and storage (audit-established mechanism; 5 in-suite failures at SG-014, 8/8 alone). Repair: construct engine/SessionLocal lazily inside its fixture from explicitly-set environment (order-independent); product files untouched for this leg; the file stays 8/8 alone AND goes green in-suite. If the repair needs any product-file change, STOP that leg instead.
- **Stale migration assertion:** `backend/tests/test_signals.py::test_observation_migration_upgrade_downgrade_upgrade` assumes `downgrade -1` removes `observation` — false since the authorised SG-014 head. Repair test-only: target explicit revisions (or base/head round trip); the assertion must stay green across future heads by construction where possible, or say plainly what future slice must touch it.
- A "pre-existing failure" claim cites the base commit + the base-run command and output, or it is a new finding with a destination — standing line from the SG-014 lever; this slice's report is its first carrier.

## G1 — plugin registry + expiry-tracker 1.0.0 (`PG-SC-02`)

- New `backend/app/plugins/` package: `registry.py` (`plugin_id` + semantic version registry; unknown-plugin and version-mismatch are 422s, not silent ignores) + `expiry_tracker.py` (taxonomy, tier defaults per blueprint §9.1, date-type/unit enums per §9.2, extension JSON Schema + validators, UI form metadata as data).
- Classification storage — your design call, recorded with reasons: reuse `assertion` rows with a reserved `field_path` prefix, or one new table (the slice's single migration). Either way the category is READ BACK through a namespaced GET route (`PG-SC-02` trace: write route → GET route → test asserts the round trip).
- Namespaced routes only: `/v1/plugins/expiry-tracker/...` (classify asset, read classification, manual expiry entry, extension-attribute write/validate) — plugin endpoints never override core routes (blueprint:353).
- Active: Food & beverages + Medicine/pharma. Inactive-but-structured: Cosmetics/Household/Documents (a classification attempt against an inactive category is a 422 naming the Phase, not a silent accept).
- Core-field guard: extension attributes attempting `identifier`, `condition`, `location`, or `status` are rejected 422 (prove all four, not one).

## G2 — manual expiry entry, never fabricated (`PG-EV-05`)

- Dateless import (no date-bearing observation — hand-inserted) yields an `expiry_date` assertion in state `needs_evidence` + a review task prompting manual entry; the manual-entry route resolves it to a user-sourced accepted assertion with source_evidence linkage where applicable.
- Property tests: unknown stays unknown until entered (assert the ABSENCE of a resolved expiry before entry — identity, not counts); entering a date for a non-perishable-category asset is rejected (no forced dates, blueprint:396); no code path writes a guessed date — grep-gate date-generating calls (`today`, `now`, `timedelta` in the plugin package) and report the match list with each match justified or removed.
- Date-type and unit enums enforced on write; tier defaults resolve per category (Food 30/7/1, Medicine shorter — quote the resolved values in tests).

## G3 — ADR-005 + ADR-009

- `docs/adr/ADR-005-plugin-contract.md` (registry, isolation, schema validation, what a second plugin must implement) + `docs/adr/ADR-009-expiry-tracker-design.md` (category/behavior-profile design, tiering, manual-entry doctrine, Phase 3 deferrals named). Every claim to file/line (SG-010 discipline).

## G4 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-015.log` and `{{WORKLOG_DIR}}/SG-015_report.md`, first token `SG-015`, every output path named in the report committed, three UNCLEAR lines at the end, elapsed-versus-budget with units. State model/effort provenance from process arguments (SG-014 proved it readable).

## G5 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-015 | Report: docs/worklogs/SG-015_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/plugins/` (new) + `backend/app/api/v1/plugins.py` (new; mount in `main.py`) + `backend/app/api/v1/assets.py` (extension-validation hook lines ONLY — no behavior change to existing routes) + `backend/tests/test_plugin_expiry.py` (new) + TEST-ONLY edits to `backend/tests/test_evidence_upload.py` + `backend/tests/test_signals.py` (G0 legs; product files untouched for these legs) + at most one migration file iff G1 requires a table + `docs/adr/ADR-005-*.md` + `docs/adr/ADR-009-*.md` + `docs/worklogs` files + the G5 note mechanism. No other frontend/backend file, no new runtime dependency, no `.env`/restart/secrets/infra, no AI/LLM/provider code, no prompt fragments, no agents/chat/planning. Anything else is a STOP ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — none requires a second migration, a worker, a frontend change, or a production write. Recorded here once, not per criterion.
- Exclusions by rule: no route decorator outside `/v1/plugins/expiry-tracker/*` is added or modified, except the assets.py validation-hook lines which add no route (`PG-SC-05`); grep-gate the decorators and report the match list.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs (quote file + test counts); every gate names the files it checked and its counts; a gate emitting no output is a FAIL. mypy stays advisory — quote the count, fix nothing outside the ceiling. Decoder-dependent tests FORBIDDEN (ISS-1 — hand-insert observations). Expectation after G0: full suite green except the two named ISS-1 decoder node IDs — any other red is a finding with a destination, never an exclusion by silence.
- Budget: 120s per ordinary command, 600s per suite leg, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`). New constants are named settings, never silent (`m0019`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run. Do not require what the confinement forbids.

## Acceptance criteria

- Registry rejects unknown plugin id and version mismatch as 422; Food/Medicine classify with tier defaults quoted; inactive-category classification 422s naming the Phase.
- Extension schema rejects bad attributes and all four core-field overrides (422 each, quoted).
- Dateless import → `needs_evidence` assertion + review task; manual entry resolves to accepted user-sourced assertion; pre-entry absence proved; non-perishable entry rejected; date-fabrication grep-gate reported with every match justified.
- Classification + expiry round-trip through the namespaced GET routes (read-back, not response-only).
- G0: `test_evidence_upload.py` 8/8 alone and green in-suite; migration assertion green in full suite; full suite otherwise green except the two named ISS-1 decoder nodes (node IDs quoted).
- SG-012…SG-014 suites stay green (no seam regression); one-or-zero migrations with temp-DB round trip quoted; `test_export.py` head test green.
- ADR-005 + ADR-009 committed with traces; worklog + report committed; notes ref carries the `Dispatch-ID: SG-015` + `Report:` note, quoted, dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — from process arguments (proven readable), never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite legs, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
