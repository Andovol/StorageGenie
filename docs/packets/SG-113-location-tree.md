# SG-113 — Location tree: tables + migration (temp-only) + API + asset-detail UI, dormant behind a flag ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D154-approved G-stage slice 4 of 5 (G7 GREEN 98 → G5 GREEN 98 → G6 GREEN 98 → G3 → G4; L3-build). Blueprint gaps G3: `location` + `asset_location` entities, §9.2 storage locations, "locations" on asset detail (§4.2, §11.1). Current tree (verified 2026-09-24, re-verify — every premise below is a hypothesis): NO location model/table/route anywhere (gaps review 2026-09-23; `relation|location` over `models/` empty); the closest existing vocabulary is the extension-enum `storage_location` (`expiry_tracker.py` EXTENSION_SCHEMA: fridge/freezer/pantry/bathroom_cabinet/medicine_cabinet/garage_utility/custom) — free-text hints, NOT entities, never trusted as the set; migration chain head is `20260923_sg100_enrich_snapshot` (9 files in `backend/alembic/versions/`, SG-100 pattern: model + migration file, temp-only, no restart); asset detail page reads assertions + offers `ExpiryEntryForm` (`AssetDetailPage.tsx`, tested with mocked api). THIS slice builds the tree + serves it dormant + shows it. PRODUCTION MIGRATION IS OUT (takes its own owner word — batched with SG-114's; the exact command is recorded below). NO sender, NO other model change, NO catalog-wide filter changes. $0 — no metered call exists on any path (a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-24. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-24); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** locations ONLY. Model files + `models/__init__` export + ONE migration + location API + asset-detail UI hunks + tests + `docs/worklogs` — NOTHING else. Exactly ONE recreate. Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05`).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-SC-11` · `PG-SC-12` · `PG-DP-02` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-05` · `PG-PR-06` · `PG-PR-10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint (backend) / 600s suite+lint (frontend), 600s build+recreate+verify, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none live** (ONE new migration file; applied to temp DBs in tests only — production migration rides a later owner-gated word, batched with SG-114. No `UPDATE/DELETE/INSERT` against production in any form; temp rows reported and removed, `PG-EV-06`, `PG-PR-10`). **Restart: ONE backend recreate (D145 standing + D154 L3-build — serves DORMANT code, see G2). Deploy: THIS slice.**

## G1 — models + migration (temp-only; SG-100 pattern)

- `location` (`id String(36) PK new_id`, `household_id` FK+cascade+index, `name` non-empty ≤200, `parent_id` self-FK nullable for the tree) + `asset_location` (`asset_id` FK+cascade, `location_id` FK+cascade, composite uniqueness asset+location — one asset sits in one location once; multi-location is separate rows, stated). TimestampMixin + Base on the provider_call pattern; export in `models/__init__.py` (name + `__all__`).
- ONE migration chaining from the CURRENT head (read `backend/alembic/versions/` in-slice, do NOT inherit my listing): upgrade creates both tables, downgrade drops both, head-relative — grep every end-relative assertion over the touched files and list the hits in-slice (`PG-SC-11`).
- Cycle guard lives in G2 (a parent chain is data, not schema).

## G2 — API + dormancy gate (the interim IS production, `PG-PR-05`)

- Routes (namespaced with the household scoping + 404/403 shapes the tree already uses — verify on target): create/list/rename/delete location (delete WITH assignments is 409 — a location holding assets is never cascade-emptied silently; empty-only delete or explicit reassignment first, decided and tested); assign/unassign asset↔location (both exist, same household, idempotent re-assign is a no-op); asset detail read includes `locations[]`.
- Cycle guard: a parent must exist in the same household and must not be the location itself nor any of its descendants (walk ancestors; refusal 422). Seed names (§9.2 fridge/freezer/…) are NOT pre-created and NEVER trusted as input — creation is explicit rows only (the enum stays a hint, never the set).
- DORMANCY (`PG-PR-05` — the migration is deferred, so the code must be inert until it lands): ALL new routes sit behind a settings flag defaulting OFF (name it, e.g. `sg_locations_enabled`); flag-off answers 404; the UI section hides when the flag reads off. The flag flips ONLY with the production migration word (record the exact word-shape: migrate + flip + recreate). Until then production serves dormant code with zero behavior change — prove it (flag-off probe through the fresh server).
- `PG-SC-02` whole: writer = assign/create routes, reader = asset-detail `locations[]` + the UI section — both in acceptance below; the migration file itself is read back by upgrade→downgrade→upgrade on temp.

## G3 — tests + gates ($0, temp DBs only)

- Backend `test_sg113_locations.py` (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; seen-to-fail in-run, `PG-EV-01`): migration upgrade→downgrade→upgrade on temp (SG-035/SG-100 precedent — locate by grep, name it); tree create/child/reparent; cycle + self-parent 422; delete-with-assignments 409 vs empty delete 200; assign/unassign incl idempotent re-assign; cross-household 403s; flag-off 404s on every new route; asset-detail `locations[]` round-trip through the REAL route.
- Frontend AssetDetailPage locations section (mocked-api pattern): lists assigned, assigns from select, unassigns, hides entirely when the backend reports disabled; create-inline tested if shipped.
- Full backend suite green modulo the 2 known decoder env reds (stash-proved on the slice — quote the proof) + full frontend suite green (`tsc` + `vite build` + `eslint` + `vitest` — quote counts, never inherit); ruff clean, mypy delta 0, secret gate 0 real over changed files (quote the grep).
- `PG-SC-07`: the smallest population reaching "no locations" (empty household / unassigned asset) renders the empty state, never an error and never a fallback list.

## G4 — refresh + verify (dormant code live, zero behavior change)

- One full rebuild + exactly ONE recreate + verify. AFTER proofs quoted raw against G1 BEFORE (capture image id, bundle name+sha, alembic head, counts, health, gate before starting): image id differs, bundle carries the new page code (name differs — EXPECTED, frontend changed), `alembic current` UNCHANGED (migration NOT applied — state it), counts delta exactly zero, health exact ×6, gate 301/401, flag-off probes 404 through the fresh server (dormancy proven live), pre-existing routes byte-identical in behavior (spot-probe catalog-list 200).
- Post-restart sweep WAIVED (`PG-DP-02` — restart-gated); substitute: in-process suites pre-restart + post-restart probes as authority. State the derived set and how it differed.
- Actual-versus-budget per leg with units (`PG-PR-06` stated against the build+recreate+verify bound).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-113.log`, `SG-113_report.md`, `SG-113_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + BEFORE/AFTER pairs). First token `SG-113`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines. ALSO record the production migration+activation word-shape (exact commands + before/after census queries) for the batched G3+G4 word.

## Constraints

- **Scope ceiling:** model files + export hunk + ONE migration + location API + asset-detail UI hunks + tests + `docs/worklogs` — NOTHING else (no other model, no second migration, no catalog filter changes, no merge/lifecycle hunks; `docker compose config` FORBIDDEN). Ordered paths committable (re-verify `.gitignore` before commit, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands production migration, second recreate, live assignment, press, sender, or any metered call — no cell collides; stated so the check exists on paper. Reads include pytest/vitest/TestClient + host commands + the authorized image build and ONE recreate; pulling/running any OTHER image or launching unnamed runtimes counts as execution — not authorised.
- Privacy: location names are user TEXT; host `.env` never printed, never read into any artifact (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; fixture names are sample data (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Migration chains from the live head and cycles on temp; tree/cycle/delete/assign semantics proven through the real routes with flag-off 404s; asset detail serves + shows `locations[]`; UI hides when disabled; suites green; refresh serves dormant code with zero row delta and zero behavior change; $0; production migration NOT run (word-shape recorded); no vacuous pass.
- Question each criterion answers (`PG-SC-09`): schema — does the tree hold without orphans or cycles? dormancy — can the undeployed schema's code serve safely? UI — does the detail page show truth and hide cleanly?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-113 | Report: docs/worklogs/SG-113_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint per side · 600s build+recreate+verify · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
