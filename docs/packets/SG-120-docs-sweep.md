# SG-120 — Group C docs sweep: README Phase 4/5, AGENTS pointer, enrich docstring (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D10-chain docs slice (Group C). No served-code behavior changes anywhere in this slice — therefore NO rebuild and NO recreate (stated, not assumed: the only backend touch is a docstring; README/AGENTS never enter the image). Three verified premises (Architect reads 2026-09-25): (1) `AGENTS.md:61` names `(contract \`contract-v0.25.0\`)` while the adopted rule set is `0.36.0` (ISS-5). (2) `backend/app/api/v1/enrich.py:112-114` says "`brand` is NOT in that vocabulary and no web path emits a brand" — false since SG-119 (OFF `brands` maps with provenance); the file is otherwise read-only to others. (3) `README.md` runbooks stop at Phase 3 + Enrich key sections — no Phase 4 (photo-ingest v3 SG-079/080 served by SG-083; 20 MB upload cap; taxonomy/exit proof) and no Phase 5 (eval hardening, backup/restore drill, privacy audit, derived registry, exit). **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.36.0` == published (`a9324d5`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** docs + one docstring ONLY. No builds, no container actions, no migrations, no DB touch, no daemon reads needed (all inputs are the repo). Secrets: README key material stays names-only per the file's existing `Settings (names only...)` discipline; never print, log, quote, or commit a key byte; `docker compose config` FORBIDDEN (`PG-SC-05`). $0 — no metered call on any path (a metered call is a STOP-and-report).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.36.0 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-SC-05` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 60s ordinary, 300s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none (no served-behavior change).**

## G1 — AGENTS pointer ISS-5 (one string, quoted pre/post)

- `AGENTS.md:61` `(contract \`contract-v0.25.0\`)` → the adopted `0.36.0` pointer. Verify what `.rules-cache/` on the host actually holds first (if the dir's state contradicts the pointer, report — do not invent). One line, nothing else in the file.

## G2 — enrich docstring F-SG119-2 (one block, quoted pre/post)

- `enrich.py:112-114` → brand IS in the vocabulary via the OFF path since SG-119 (provenance `web:OpenFoodFacts`); Jina still emits none; the miss population (`PG-SC-07`) still maps to nothing. Code untouched — prove behavior-identical by the enrich test files green (no new tests needed; the imports compile).

## G3 — README Phase 4 + Phase 5 runbooks (factual, bounded)

- Add exactly two sections after the Enrich runbook: Phase 4 (photo-ingest v3: schema/prompts SG-079 → pipeline SG-080 → served SG-083; 20 MB cap with visible 413; taxonomy + plugin-domain exit proof) and Phase 5 (eval hardening; backup/restore drill with temp-only restore; privacy audit; derived registry; exit). Ground every claim in the tree (ratings/docs/code) — a claim you cannot ground is omitted and reported, never written from memory. Key material names-only. No screenshots prose, no marketing.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-120.log`, `SG-120_report.md`, `SG-120_verify.log` (pre/post quotes, absence greps). First token `SG-120`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — `README.md` (2 sections), `AGENTS.md` (1 line), `backend/app/api/v1/enrich.py` (1 docstring block), `docs/worklogs` (3 files). **Anything else written is a STOP** — code, tests, prompts, compose, `.env`, migrations, STATE.
- Cross-product (`PG-IC-01`): G1–G3 need doc edits + quote greps + enrich test files; nothing else. No criterion touches the daemon, the DB, or served code behavior.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): three corrections, no new documentation system.

## Acceptance criteria

- AGENTS string post quoted + old-string absence grep quoted; enrich block post quoted + behavior-identical (enrich tests green); README sections present with every claim grounded (ungrounded claims listed as omitted, not written).
- No file outside the ceiling written (diff proves); $0; no vacuous pass (absence greps scoped tree-wide for the exact old strings, quoted).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-120 | Report: docs/worklogs/SG-120_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

60s ordinary · 300s overall; expected ~300s (Architect's record; the lane enforces `RUN_BUDGET_S`); $0; actual-versus-budget per leg with units.
