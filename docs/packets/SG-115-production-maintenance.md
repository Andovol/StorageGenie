# SG-115 — Production maintenance: live backfill + batched G3+G4 migrations + activation ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D155+D156-approved production words (owner quote "D8 and D9 approved", 2026-09-24): (1) run the SG-111 backfill against the live SQLite with before/after census; (2) apply the SG-113 + SG-114 migrations, flip `SG_LOCATIONS_ENABLED` + `SG_RELATIONS_ENABLED`, one recreate, activation probes. THIS slice executes exactly those recorded commands — nothing else. It is an ops slice: no product code changes (prove by empty diff over `backend/`+`frontend/`+`alembic/` — any product hunk is a STOP), no tests (nothing to fail-then-pass — the proof is before==after measurements, stated), no migration FILE changes. $0 — no metered call exists on any path (a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-24. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-24); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** the two words ONLY, in order G1 backfill → G2 migrations → G3 flags+recreate+probes. Exactly ONE recreate (G3). The host `.env` is NEVER printed and NEVER read into any artifact — presence checks are `grep -c` counts only (`PG-SC-05`). Key NAMES only; `docker compose config` FORBIDDEN.
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` · `PG-PR-03` · `PG-PR-06` · `PG-PR-10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s migrate+recreate+verify, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: LIVE — the two approved words ONLY** (`PG-PR-10`: this packet cites D155 for the backfill and D156 for the migrations; no other live write exists). **Restart: exactly ONE backend recreate (G3, D156). Deploy: no code change (dormant code already served).**

## G0 — capability + census BEFORE (nothing moves until this is quoted; `PG-PR-01` with non-mutating forms)

- Enumerate with read-only forms: `docker ps` (backend-1 healthy?), `alembic current` (hypothesis `20260923_sg100_enrich_snapshot` — VERIFY), table set (hypothesis 25, no location/asset_location/asset_relation — VERIFY), `SELECT status, COUNT(*) FROM asset GROUP BY status` (hypothesis `ACTIVE|6` — VERIFY), `grep -c SG_LOCATIONS_ENABLED/SG_RELATIONS_ENABLED` on host `.env` (hypothesis 0 — counts only, never content), health exact, gate 301/401. Quote all raw. Any hypothesis miss is a finding that gates what follows (e.g. flags already present → do NOT duplicate-append; unexpected rows → STOP).

## G1 — live backfill (D155 word)

- Run EXACTLY (SG-111 recorded command — re-verify the script path exists in the served image first; if absent, STOP, do not improvise):
  `docker exec storagegenie-backend-1 python /app/scripts/backfill_asset_lifecycle.py --db /data/db/storagegenie.db --apply`
- Before AND after: the read-only status census above. Expected: identical (`ACTIVE|6`, zero conversions — the dry-run already proved this on temp). ANY converted row is reported with its id and before/after (not hidden, not reverted — the Architect decides). `PG-PR-10`: database `/data/db/storagegenie.db`, grant D155, stated here.

## G2 — batched migrations (D156 word, part 1)

- `docker exec storagegenie-backend-1 python -m alembic upgrade head` — expected head path `..._sg100_enrich_snapshot → 20260924_sg113_location → 20260924_sg114_relation` (VERIFY each step in output; a different head is a STOP). After: `version_num == 20260924_sg114_relation`; table set = before + exactly `{location, asset_location, asset_relation}`; every pre-existing table count IDENTICAL to G0 (any other delta is a STOP-and-report). `PG-PR-10`: same database, grant D156.
- Precedence (`PG-IC-03`): on ANY failure here, STOP wins over continuing to G3 — a half-migrated backend with flipped flags is the outcome this ordering exists to prevent. No auto-rollback (downgrades drop tables; the Architect decides on the report).

## G3 — flags + recreate + activation probes (D156 word, part 2)

- Append `SG_LOCATIONS_ENABLED=true` and `SG_RELATIONS_ENABLED=true` to the host backend `.env` (verify counts 0 first; append-only, never rewrite; verify counts 1 after; content never quoted). Then exactly ONE `docker compose up -d --no-deps backend`; healthy within 60s (else STOP).
- AFTER proofs quoted raw: health exact ×6; gate 301/401; `GET /v1/locations?household_id=<live-id>` 200 (not 404); `GET /v1/assets/<live-asset>/relations?household_id=<live-id>` 200 (not 404); asset detail carries `locations` + `relations` keys; pre-existing routes byte-identical in behavior (catalog-list 200); 25+3-table counts with ONLY the three new tables added and all old counts equal.
- Actual-versus-budget per leg with units (`PG-PR-06` stated against the migrate+recreate+verify bound).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-115.log`, `SG-115_report.md`, `SG-115_verify.log` (raw outputs + every census + every command). First token `SG-115`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines. NO product diff to prove — the proof is before==after measurements with the three expected deltas (backfill zero, +3 tables, 404→200); a fourth delta of any kind is a STOP-and-report finding, never a silent accept.

## Constraints

- **Scope ceiling:** `docs/worklogs` ONLY committed (no product file touched — empty product diff or STOP; `docker compose config` FORBIDDEN). Ordered paths committable (re-verify `.gitignore` before commit, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands code change, tests, second recreate, press, sender, or any metered call — no cell collides; stated so the check exists on paper. Reads/executions: host `docker exec` read-only probes + the FIVE authorized mutating steps (backfill apply, alembic upgrade, two env appends, one recreate); any sixth mutation is a STOP.
- Privacy: `.env` counts only, never content; identifiers TEXT only (`PG-SC-05` by rule).
- No fixed dates except this header's authoring-date metadata; live clock at execution (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Backfill census identical with the command quoted; migration head path exact with +3 tables and all old counts equal; flags flipped once each with counts; one recreate healthy; activation 200s with detail keys present; $0; exactly the authorized mutations, nothing else; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): backfill — did the live catalog need anything? migration — did the schema land whole with data still? activation — do the dormant surfaces answer?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-115 | Report: docs/worklogs/SG-115_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s migrate+recreate+verify · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
