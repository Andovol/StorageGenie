# SG-103 — Reviewer alternatives: web_alternates as first-class proposal rows ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D139/D141 L3 Arc A slice 5 of 5, LAST build slice (SG-099 live-closed → SG-100 GREEN → SG-101 GREEN → SG-102 GREEN → alternatives; deploy rider parked for its own owner word). SG-082's REMAINING named "surfacing `web_alternates` as first-class review rows"; the helper exists — `apply_web_fields_to_proposal` (`candidates.py:435`, via `merge_web_fields` at `:347`) — but the endpoint never calls it and hardcodes `"web_alternates": []` (`api/v1/enrich.py:173`, re-verified 2026-09-23 — re-verify). Note the trap: merging web fields against the proposal's OWN fields can never conflict (same source both sides), so real alternates need the asset's LABEL-side fields as the `existing` half. THIS slice computes label-side existing from the asset + assertions, merges, and stores + serves the alternates. NO new review UX (Enrich standing rule — existing candidate UI, per-field accept): the frontend does not render alternates today (verified: zero `alternates` hits in `frontend/src` 2026-09-23); UI consumption is named backlog, not this slice. $0 — deterministic logic over fixtures; no live calls (live already proven SG-101/102; a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-23); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** alternates ONLY. No fetcher/synthesis/writer changes (all read-only pattern sources), no model/migration (prove by empty diff over `models/`+`alembic/` — alternates ride the EXISTING candidate row's `proposed_fields_json`), no frontend, no deploy, no restart, no container action. Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05`).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-SC-10` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none** (existing candidate table only; tests on temp DBs; no production writes of any kind). **Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`).

## G1 — label-side existing + merge (the delegated design call)

- Build the label-side `existing` dict from the asset + its assertions (the endpoint already reads brand/identifier TEXT via `read_asset_identifiers` + `display_name` off the asset — verified 2026-09-23, re-verify): map those onto the `LABEL_VISIBLE_FIELDS` vocabulary (`candidates.py:36-49`, verified 2026-09-23 — re-verify the exact set before building). **What this choice turns on** (PACKET.md autonomy — name it): which assertion `field_path`s count as label-visible, and how a display_name/brand/barcode maps onto `merge_web_fields`' field names; a wrong mapping silently empties the alternates (the trap above), so the mapping is asserted by the conflict test, never assumed.
- Merge via the REAL `merge_web_fields(label_existing, web_fields)` — do NOT re-implement the rule and do NOT call `apply_web_fields_to_proposal` blindly (it merges against the proposal's own web fields, which is the empty-alternates trap — verify this claim on target; if it turns out wrong, that is the finding that decides the implementation).
- Store the resulting `alternates` in the proposal's `web_alternates` (replacing the hardcoded `[]`) AND serve them in the endpoint response body. Every alternate carries `field` + `value` + `source_type` + `source_url` + `retrieved_at` (the merge shape `:369-377` — re-verify).
- Brand-absent assets yield NO brand alternate, never a guessed one (`PG-SC-07` — F-SG098-3 lineage, stated).

## G2 — tests + gates ($0, temp DBs only)

- New `backend/tests/test_sg103_web_alternates.py` (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; seen-to-fail in-run, `PG-EV-01`): conflict case (asset WITH brand assertion + web brand → proposal keeps the label value AND one alternate row with the web value + its source triple); no-conflict case (alternates `[]`, fields filled from web); alternate rows round-trip through the REAL `GET /v1/candidates/{id}` route (`PG-SC-02` — writer = endpoint commit, reader = candidates route, both in acceptance); consent-false still refuses with 0 rows (regression leg).
- Full suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0 real.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-103.log`, `SG-103_report.md`, `SG-103_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate). First token `SG-103`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `api/v1/enrich.py` alternates hunks + new test file + `docs/worklogs` (3 files) — NOTHING else (`candidates.py` read-only unless a failing test proves a hunk, M45 terms, disclosed, else STOP). Ordered paths committable (`.gitignore` verified 2026-09-23, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands fetchers, synthesis, writer, migration, frontend, deploy, restart, container acts, or any metered call — no cell collides; stated so the check exists on paper. Reads include TestClient + host commands only; pulling/running images or launching unnamed runtimes counts as execution — not authorised.
- Privacy: identifiers TEXT only; key never in any file, log, or assertion (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; fixture timestamps are sample data; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Conflict yields label value kept + one alternate with the full source triple; no-conflict yields web-filled fields + `[]`; alternates round-trip via the real candidates route; brand-absent yields no brand alternate.
- Tests fail-pre/pass-post both committed raw; gates green; $0; production untouched; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — do label/web conflicts stay BOTH visible with sources instead of collapsing? G2 — is it proven through the real commit path with zero live touch?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-103 | Report: docs/worklogs/SG-103_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
