# SG-107 — Expiry urgency engine: pure tier+bucket compute + read route, owns its refresh ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D143 L3 Arc B slice 1 of 3 (engine → dashboard → calibration; one retry/slice; checkpoint where a result changes the next packet; riders + production writes still need individual words). D147: expiry-stream only — cosmetics tiers from `expiry_date` like every category, `opened_date` ships as its own follow-up slice (window undefined, no PAO duration stored anywhere). D148: approach P1 — standalone pure engine + plugin-namespaced route, analytics untouched. D3: design S1–S7 APPROVED as a whole; standalone spec doc skipped per the owner approaches→design→packet sequence (D138 precedent). THIS slice builds the engine + serves it + refreshes the service (first slice owning its refresh under D145). NO sender, NO scheduler, NO opened-date stream, NO analytics changes, NO migration, NO frontend. $0 — pure compute over existing rows; no live metered call exists on any path (a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-24. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-24); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** engine + route + refresh ONLY. New pure module + one `plugins.py` route hunk + one test file + `docs/worklogs` (4 content paths) — NOTHING else (`models/` + `alembic/` + `frontend/` prove empty diff or STOP; analytics byte-untouched). Exactly ONE recreate, no migration vehicle (no model change — if `alembic current` shows any head you did not expect, STOP, do not upgrade). Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05` — it prints secrets; no compose-config read is needed for this slice).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-07` · `PG-SC-09` · `PG-SC-12` · `PG-DP-02` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

**DATABASE: none live** (tests on temp DBs; post-restart probes are read-only GETs — a write of any kind is a STOP). **Restart: ONE backend recreate (D145 standing + D143 L3). Deploy: THIS slice (backend-only; frontend bundle expected byte-identical AFTER — a difference is a STOP-and-report finding).**

## G1 — capture BEFORE (every observable the proof moves; `PG-EV-08`)

- Image id, served frontend bundle name+size+sha256, `alembic current` (hypothesis: single head, SG-106 lineage `sg100` — VERIFY, never inherit, `PG-IC-09`), table counts, `GET /v1/health` exact body, gate (http 301 / https 401 without login). Quote all raw.

## G2 — pure engine + read route (the approved S1–S4; facts handed over, no rediscovery)

- New module (suggested `backend/app/services/expiry_engine.py` — location is yours): `days_remaining(expiry, as_of)`, generic `tier_for(category_slug, d)` reading the LIVE `CATEGORIES[slug].tier_defaults` (values verified 2026-09-24 at `expiry_tracker.py:95-122`: food 1/7/1-critical/urgent/upcoming 1/7/30 · medicine 1/3/14 · cosmetics 7/30/90 · household upcoming-only 30 · documents upcoming 30 + long_lead 60 · non-perishable `{}` — **windows are DECLARED UNCALIBRATED (`G-A9`)**, the engine takes NO hardcoded numbers so calibration tunes data, never this code), fixed `bucket_for(d)` (`<0` expired · `≤7` this-week · `≤30` this-month · else safe), `compute_status(db, household_id, as_of, category=None)`.
- **Resolved rule (STRICTER than analytics — D143, do not copy `analytics/service.py:_active_assertion`):** an asset is tiered/bucketed ONLY on an `EXPIRY_FIELD` (`plugin:expiry-tracker/expiry_date`) assertion with `review_state == "accepted"` AND a parseable `expiry_date` string (shape `{"expiry_date": "YYYY-MM-DD", "date_type": ...}`, writer `store_manual_expiry` at `expiry_tracker.py:498-509` — re-verify). Classification (`plugin:expiry-tracker/classification`, shape `{"category": slug, ...}`, writer `classify_asset` at `:414-419` — re-verify) gives the category. Tier rule: `d<0` → expired (tier `null`); else first ascending window with `d ≤ days` names the tier; beyond max → `safe`; category with `{}` windows (non-perishable) → tier `null`, bucket still computed. **What this choice turns on:** which rows count as accepted (review_state equality, not the analytics not-in predicate) — a wrong predicate silently tiers proposed dates, so the discrimination test asserts it, never assumes it.
- Route `GET /v1/plugins/expiry-tracker/status` on the existing mount (`plugins.py:20` prefix `/plugins/expiry-tracker` + `main.py:68` `prefix="/v1"` — re-verify both lines before building): query `household_id` (required) + `category` (optional slug) + `as_of` (optional `YYYY-MM-DD`, default today UTC); unparseable `as_of` → 422 (plugin `_error` style); unknown household → 404, never 500. Response: `as_of` + urgency-sorted rows (expired first, then `days_remaining` asc) `{asset_id, display_name, category, expiry_date, date_type, days_remaining, tier, bucket}` + `summary {by_tier, by_bucket, unresolved, total}` + `unresolved_rows {asset_id, reason}` where reason ∈ `proposed | needs_evidence | unparseable | dateless`.
- **Empty-set semantics (`PG-SC-07`):** category filter matching nothing and empty household both return 200 with empty rows + zeroed summary — never 404, never a silent fallback to unfiltered.

## G3 — tests + gates ($0, temp DBs only)

- New `backend/tests/test_sg107_expiry_engine.py` (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; seen-to-fail in-run, `PG-EV-01`): boundary table per category through the REAL `CATEGORIES` (at minimum `d` −1/0/1/3/7/14/30/60/90/91 — the DEFAULT must fire on a reachable input, `PG-SC-12`, not only planted windows); discrimination (accepted tiers, proposed-with-near-date stays `unresolved`); household isolation (other-household rows invisible); `as_of` determinism (same fixture, two clocks, exact expected shift); no-write proof (table counts before==after the compute + route legs, `PG-EV-02`); route leg through the REAL TestClient GET asserting row shape + summary reconciliation (rows sum to summary — `PG-SC-02` read route: writer = existing manual-entry path, reader = this route).
- Full backend suite green modulo the 2 known decoder env reds (stash-proved on the slice — quote the count, never inherit it), ruff clean, mypy delta 0, secret gate 0 real.
- Full-suite sweep WAIVED post-restart only (`PG-DP-02` — restart-gated; externally-driven tests would exercise the previous build); substitute: the in-process suite above (runs pre-restart against the new code) + the post-restart run as authority (G4 probes). No browser-driven tests exist on this path — state the derived set and that it differed nowise.

## G4 — refresh + verify (D145 owned refresh; production restart inside D143 L3 bounds)

- One backend rebuild + exactly ONE recreate + verify. AFTER proofs quoted raw against the G1 BEFORE: image id differs, bundle name+size+sha256 byte-identical, `alembic current` unchanged, counts delta exactly zero (no press, no writes — any new row is a STOP-and-report), health exact ×6, gate 301/401, `GET /v1/plugins/expiry-tracker/status` 200 read-only through the fresh server (shape only, no fixture data created live).
- Actual-versus-budget per leg with units (`PG-PR-06` stated against the build+recreate+verify bound).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-107.log`, `SG-107_report.md`, `SG-107_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + BEFORE/AFTER pairs). First token `SG-107`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** new engine module + `plugins.py` route hunk + new test file + `docs/worklogs` (4 content paths) + the refresh — NOTHING else (no sender/scheduler/opened-date/analytics/migration/frontend; `docker compose config` FORBIDDEN). Ordered paths committable (re-verify `.gitignore` before commit, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands a sender, scheduler, opened-date stream, analytics hunk, migration, frontend change, second recreate, press, or any metered call — no cell collides; stated so the check exists on paper. Reads include TestClient + host commands + the authorized image build and ONE recreate; pulling/running any OTHER image or launching unnamed runtimes counts as execution — not authorised.
- Privacy: identifiers TEXT only; host `.env` never printed, never read into any artifact (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; fixture dates are sample data computed relative to the live clock at execution (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Boundary table tiers exactly per the generic rule on every category (including documents long_lead at 31–60d and safe beyond, household upcoming-only, non-perishable tier-null); proposed-near-date unresolved; households isolated; `as_of` shifts exact; compute+route write nothing.
- Route 200s with the exact row/summary/unresolved shape; summary reconciles rows; empty sets 200 zeroed; refresh proofs match BEFORE→AFTER with zero row delta; $0; production otherwise untouched; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): tier table — does the generic rule reproduce every category window without hardcoded numbers? discrimination — can a proposed date ever tier? refresh — did the served code actually change while data stood still?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-107 | Report: docs/worklogs/SG-107_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 600s build+recreate+verify · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
