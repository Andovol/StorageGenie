# SG-098 — Enrich endpoint + button trigger wiring (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D131-approved (owner quote "P3 - approved.") Enrich endpoint+trigger slice — first of the three remaining Enrich build slices (synthesis prompt+caller and persistence model+migration ride later slices). SG-081/082 shipped OFF + Jina clients and review mapping as unwired libraries; SG-097 declared the `Settings.jina_api_key` field and documented the seam. THIS slice exposes the manual trigger: a new endpoint serving gated proposals plus the button `onRun` wiring. Carries the F-SG097-2 one-line follow-up (`jina.py:20-24` docstring still claims no settings field — correct it, nothing else in that file). **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** wiring ONLY. No synthesis prompt/caller, no persistence model/migration (prove by diff: `models/` + `alembic/` untouched — snapshots ride the in-memory decision record and the response body, `PG-SC-02` unrecorded this slice, said in as many words), no deploy, no restart, no container action — the running service is untouched (`PG-PR-04`). No live calls of any kind ($0 — scripted transports only; a metered call is a STOP-and-report). Key via settings (SG-097 field), never logged/quoted/committed as a value; `docker compose config` FORBIDDEN (`PG-SC-05` — it prints secrets).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-04` · `PG-EV-05` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03` · `PG-PR-04`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 1200s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none** (gated proposals ride existing candidate storage through the established commit path — no new tables; prove by diff over `models/`+`alembic/`). **Restart: none. Deploy: none. Container actions: none.**

## G1 — endpoint (manual trigger, identifiers only)

- New `backend/app/api/v1/enrich.py`: `POST` trigger for one asset (asset id in path or body — decide and report) reading ONLY its brand+name/barcode TEXT (never photo bytes, never GPS — assert text-only on the real handler, SG-081 precedent extended). Runs the OFF-first→Jina decision through the REAL clients with scripted transports in tests; failures degrade to loud named snapshots with zero sends (SG-081/082 discipline). Consent gate BEFORE any client touch (refuse with a named reason when `sg_consent` is false — prove 0 client invocations on that path); per-press spend cap enforced server-side (mirror of the frontend `enrichCapRefusal`, stated uncalibrated `G-A9`).
- `PG-SC-07`: an asset with NO usable identifiers is refused with a named reason (`missing_identifiers`), never an empty proposal list and never a guessed query. `PG-SC-02`: proposals commit as gated rows through the REAL commit path and read back via `GET /v1/candidates/{id}` (writer + reader both in acceptance); snapshots themselves are UNRECORDED this slice (in-memory decision record + response body).
- Register the router at BOTH sites in `backend/app/main.py` (import line beside `:9-22` + `include_router(..., prefix="/v1")` beside `:56-69` — verified by the Architect 2026-09-23, re-verify; a registration at only one site is the defect, not a pass).

## G2 — button `onRun` wiring (no new UX)

- `frontend/src/routes/AssetDetailPage.tsx:149` renders `<EnrichButton lastSpendUsd={null} />` with NO `onRun` (verified 2026-09-23 — re-verify): pass a handler that POSTs the new endpoint for the shown asset, cap-gated through the existing `enrichCapRefusal` (refusal disables with the named reason, seen-to-fail). `EnrichButton` itself (`:29-57`) is untouched unless the wiring requires it (disclosed). No new review UX anywhere.
- F-SG097-2 one-liner: correct the `jina.py:20-24` docstring's false first clause (settings field now declared) — prose only, zero logic hunks in that file.

## G3 — tests + gates

- Backend (TestClient, new or extended enrich test file — decide and report): trigger commits gated proposals readable via the REAL candidates route; OFF-hit never fires Jina / OFF-miss fires it (order preserved through the endpoint); consent-false → named refusal + 0 invocations; over-cap → named refusal; identifier-less asset → named refusal; key material nowhere (names only). FAIL-then-pass raw BOTH runs committed (`PG-EV-09`).
- Frontend: extend the SG-082 `EnrichButton` suite — click under cap calls `onRun` (prove with the page's wired handler, not a bare callback), above cap refuses without calling.
- `PG-SC-12`: every assertion drives the REAL endpoint/router/commit-path/loader — no re-implemented seam. Full suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0 real; `PG-SC-11` end-relative grep over touched test files committed raw.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-098.log`, `SG-098_report.md`, `SG-098_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate). First token `SG-098`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** new `api/v1/enrich.py` + `main.py` (two registration lines) + `AssetDetailPage.tsx` (wiring only) + `jina.py` docstring prose-only + enrich test file(s) + `docs/worklogs` — NOTHING else. **Suite-green binds on collision** (minimal root-cause repair + disclosure, M45); anything else is a STOP.
- Cross-product (`PG-IC-01`): no criterion demands synthesis, persistence, a live call, deploy, or container act — no cell collides; stated so the check exists on paper. Reads include TestClient + `docker`-free host commands only; pulling/running images or launching unnamed runtimes counts as execution — not authorised.
- Privacy: brand+name TEXT only; key never in any file, log, or assertion (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Endpoint triggers on identifiers TEXT-only; OFF-first order preserved; consent-false and over-cap refuse by name with 0 sends; identifier-less asset refused by name.
- Proposals commit gated through the real path and read back via the real candidates route; snapshots unrecorded (in-memory + body).
- Button calls the endpoint under cap and refuses above it; router registered at both `main.py` sites; docstring corrected.
- Tests fail-pre/post-pass both committed raw; gates green; diff touches no `models/`/`alembic/`; $0; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): G1 — can a manual trigger reach the fetchers and land gated proposals? G2 — does the shipped button drive it within the cap?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-098 | Report: docs/worklogs/SG-098_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 1200s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
