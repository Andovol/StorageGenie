# SG-114 — Asset relations: typed links + temp-only migration + dormant API + detail UI ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D154-approved G-stage slice 5 of 5, LAST build slice (G7 GREEN 98 → G5 GREEN 98 → G6 GREEN 98 → G3 GREEN 98 → G4; L3-build). Blueprint gaps G4: `asset_relation` entity, "relationships" on asset detail (§4.2, §11.1). Current tree (verified 2026-09-24, re-verify — every premise below is a hypothesis): NO relation model/table/route anywhere (gaps review 2026-09-23; SG-113 proved the grep discipline for absence claims — quote yours); SG-113 shipped the locations pattern to mirror (dormant flag `sg_locations_enabled`, temp-only migration `20260924_sg113_location` chaining sg100, asset-detail conditional read, UI hides when dormant); merge/duplicate links already exist as `merged_into` (candidate proposal + `merge.merged_into` assertion — relations MUST NOT duplicate them: no `duplicate_of` type here, stated). THIS slice adds typed asset links + serves them dormant + shows them. PRODUCTION MIGRATION IS OUT (takes the owner word — batched with SG-113's; both word-shapes recorded below). NO other model change, NO catalog filter changes, NO sender. $0 — no metered call exists on any path (a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-24. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-24); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** relations ONLY. Model file + export hunk + ONE migration + relations API + asset-detail UI hunks + tests + `docs/worklogs` — NOTHING else. Exactly ONE recreate. Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05`).
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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint per side, 600s build+recreate+verify, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none live** (ONE new migration file; applied to temp DBs in tests only — production migration rides the batched G3+G4 owner word. No `UPDATE/DELETE/INSERT` against production in any form; temp rows reported and removed, `PG-EV-06`, `PG-PR-10`). **Restart: ONE backend recreate (D145 standing + D154 L3-build — serves DORMANT code, see G2). Deploy: THIS slice.**

## G1 — model + migration (temp-only; SG-100/SG-113 pattern)

- `asset_relation` (`id` String(36) PK new_id, `household_id` FK+cascade+index, `from_asset_id` FK asset CASCADE + index, `to_asset_id` FK asset CASCADE + index, `relation_type` non-empty ≤50, composite uniqueness (from,to,type) — the same typed link twice is one row; timestamps). NO `duplicate_of` type anywhere (merge owns duplicates — grep-gate it, `PG-SC-05` by rule).
- Relation vocabulary (EXACT set, no invention — the packet fixes it): `related_to` (symmetric intent, stored once directed) + `contains` (directed, container→content). A third type is a STOP-and-report (new vocabulary is a new decision, not a design call).
- ONE migration chaining from the CURRENT head (read `backend/alembic/versions/` in-slice — hypothesis: `20260924_sg113_location`, do NOT inherit): upgrade creates the table, downgrade drops it, head-relative (`PG-SC-11` — list the end-relative hits in-slice).

## G2 — API + dormancy gate (SG-113 pattern; the interim IS production, `PG-PR-05`)

- Routes (household scoping + 404/403 shapes the tree uses — verify on target): create/delete relation + list-for-asset (BOTH directions: outgoing `from==asset` and incoming `to==asset`, labelled by direction — a link readable from one end only is half a feature); create validates both assets exist in the same household (404/403), type in vocabulary (422), no self-link (422), no duplicate (409 exact); delete of a missing link is an idempotent no-op (200).
- DORMANCY: separate settings flag defaulting OFF (name it, e.g. `sg_relations_enabled` — separate from the locations flag so each migration word flips only its own surface); flag-off answers 404 on every new route; asset-detail read adds `relations[]` ONLY when ON (OFF response byte-identical); UI section hides when dormant.
- `PG-SC-02` whole: writer = relation routes, reader = asset-detail `relations[]` + UI section — both in acceptance; migration read back by upgrade→downgrade→upgrade on temp.

## G3 — tests + gates ($0, temp DBs only)

- Backend `test_sg114_relations.py` (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; seen-to-fail in-run, `PG-EV-01`): migration cycle on temp; vocabulary pin (exactly the two types — a third literal anywhere is a FAIL); create/read-both-directions/delete incl idempotent re-delete; self-link/dup-link/cross-household/illegal-type refusals with NOTHING written (before==after counts, `PG-EV-02`); flag-off 404s; no-`duplicate_of` grep-gate.
- Frontend detail-page relations section (mocked-api pattern): lists both directions, creates, deletes, hides when dormant; empty state for an unlinked asset (`PG-SC-07` — empty renders the state, never an error).
- Full backend suite green modulo the 2 known decoder env reds (stash-proved on the slice — quote the proof) + full frontend suite green (`tsc` + `vite build` + `eslint` + `vitest` — quote counts, never inherit); ruff clean, mypy delta 0, secret gate 0 real over changed files (quote the grep).

## G4 — refresh + verify (dormant code live, zero behavior change)

- One full rebuild + exactly ONE recreate + verify. AFTER proofs quoted raw against G1 BEFORE (capture image id, bundle name+sha, alembic head, counts, health, gate before starting): image id differs, bundle name differs (EXPECTED, frontend changed), `alembic current` UNCHANGED (migration NOT applied — state it), counts delta exactly zero, health exact ×6, gate 301/401, flag-off probes 404 through the fresh server, pre-existing routes byte-identical in behavior (spot-probe catalog-list 200).
- Post-restart sweep WAIVED (`PG-DP-02` — restart-gated); substitute: in-process suites pre-restart + post-restart probes as authority. State the derived set and how it differed.
- Actual-versus-budget per leg with units (`PG-PR-06` stated against the build+recreate+verify bound).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-114.log`, `SG-114_report.md`, `SG-114_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + BEFORE/AFTER pairs). First token `SG-114`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines. ALSO record the batched G3+G4 production migration+activation word-shape (exact commands for BOTH migrations + both flags + one recreate, with before/after census queries).

## Constraints

- **Scope ceiling:** model file + export hunk + ONE migration + relations API + asset-detail UI hunks + tests + `docs/worklogs` — NOTHING else (no second migration, no third relation type, no lifecycle/merge/location hunks; `docker compose config` FORBIDDEN). Ordered paths committable (re-verify `.gitignore` before commit, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands production migration, second recreate, live links, press, sender, or any metered call — no cell collides; stated so the check exists on paper. Reads include pytest/vitest/TestClient + host commands + the authorized image build and ONE recreate; pulling/running any OTHER image or launching unnamed runtimes counts as execution — not authorised.
- Privacy: relation rows carry ids only; host `.env` never printed, never read into any artifact (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; fixture names are sample data (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Migration chains from the live head and cycles on temp; exactly two relation types creatable/readable-both-directions/deletable with refusals writing nothing; flag-off 404s + hidden UI; asset detail serves + shows `relations[]` when on; suites green; refresh serves dormant code with zero row delta and zero behavior change; $0; production migration NOT run (batched word-shape recorded); no vacuous pass.
- Question each criterion answers (`PG-SC-09`): schema — do links hold both directions without orphans? dormancy — can the undeployed schema's code serve safely? UI — does the detail page show truth and hide cleanly?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-114 | Report: docs/worklogs/SG-114_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint per side · 600s build+recreate+verify · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
