# SG-111 — Lifecycle states: vocabulary + transition enforcement + readers, backfill proven on temp ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D154-approved G-stage slice 2 of 5 (G7 GREEN 98 → G5 → G6 → G3 → G4; L3-build). Blueprint §4.3: `DRAFT → PENDING_REVIEW → ACTIVE → ARCHIVED → DISPOSED + MERGED redirect`. Current tree (verified 2026-09-24, re-verify — every premise below is a hypothesis): `Asset.status` free `String(30)` default `"ACTIVE"` (`models/asset.py:23`, writers `asset_service.py:46` + `candidates.py:818`); the ONLY lifecycle writer is delete→`ARCHIVED` + status assertion + audit (`api/v1/assets.py:383-409`); readers filtering ACTIVE: analytics (`analytics/service.py:188`), chat (`chat/service.py:152`), planning (`planning/service.py:113`), assets list `?status=` (`assets.py:186`); the SG-107 engine has NO status predicate (ISS-2 — archived rows tier today). THIS slice ships the vocabulary + enforced transitions + reader updates + a temp-proven backfill plan. LIVE BACKFILL IS OUT (production write — takes its own owner word; the exact production command is recorded below for that word). NO schema change (values fit `String(30)` — prove by empty diff over `models/`+`alembic/`), NO creation-flow change (see G1), NO merge-map (rides SG-112; MERGED value reserved here), NO frontend. $0 — no metered call exists on any path (a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-24. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-24); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** lifecycle ONLY. One transition module (new file or `asset_service.py` — your call, record why) + API validation hunks + reader hunks + tests + backfill script/plan + `docs/worklogs` — NOTHING else. Exactly ONE recreate. Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05`).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-SC-12` · `PG-DP-02` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

**DATABASE: none live** (backfill proven on a TEMP copy only — the live backfill is a separate owner word; running it here is a STOP). **Restart: ONE backend recreate (D145 standing + D154 L3-build). Deploy: THIS slice.**

## G1 — capture BEFORE + reader inventory (the set is enumerated on target, never handed; PACKET.md §2a)

- BEFORE captures (`PG-EV-08`): image id, `alembic current` (hypothesis single head — VERIFY), 25-table counts (hypothesis 25 — VERIFY), health exact, gate 301/401, live `status` value census (read-only `SELECT status, COUNT(*) GROUP BY status` — hypothesis: only ACTIVE + ARCHIVED).
- Enumerate EVERY read and write of `Asset.status` on target (`grep -rn "\.status" backend/app` + the `status` query params + FTS/saved-search predicates if any reference it): for each hit report keep-as-ACTIVE-only / widen / untouched. My inventory above is the EXPECTATION (analytics, chat, planning, assets list, engine, delete path, creation defaults) — the diff either way is reported (`a list is a fact too`).
- DECIDED by the Architect (not delegated — keeps this slice small): creation paths keep writing `ACTIVE` (no DRAFT-by-default reroute; the import-flow rework is its own future slice if ever wanted); delete keeps meaning ARCHIVED, now validated through the map below.

## G2 — vocabulary + transitions + readers (design calls inside constraints are yours within these pins)

- Vocabulary (EXACT literals, no invention): `DRAFT, PENDING_REVIEW, ACTIVE, ARCHIVED, DISPOSED, MERGED`. Single transition table; legal flow `DRAFT→PENDING_REVIEW→ACTIVE→ARCHIVED→DISPOSED` + `ACTIVE→MERGED` reserved (redirect target rides SG-112 — a MERGED asset with no redirect yet reads as the terminal state, never a dangling pointer, `PG-SC-07`). Illegal transition → 422 with the legal set in the detail (assert the body, not just the code).
- Enforcement points: `PATCH /assets/{id}` status writes + delete path validate through the table (delete ACTIVE→ARCHIVED stays green through the map, not around it). Creation writes bypass validation ONLY for the decided `ACTIVE` default (stated in code, not silent).
- Readers: every ACTIVE-only reader keeps meaning ACTIVE-only through the SHARED predicate (no per-site string literals — grep-gate `"ACTIVE"` outside the vocabulary module after the edit, `PG-SC-05` by rule); the ENGINE gains the status predicate (ISS-2: engine admits ACTIVE assets only — non-ACTIVE assets are excluded from rows AND unresolved, they are lifecycle-terminal, not date-missing; the dashboard needs no change). Any reader my inventory missed follows the same rule or is reported WHY not.
- Tests (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; seen-to-fail in-run, `PG-EV-01`): transition table unit legs (legal chain end to end + every illegal edge 422 incl ARCHIVED→ACTIVE and ACTIVE→DRAFT); API legs through the REAL routes (PATCH status forward/backward, delete→ARCHIVED through the map); reader legs (non-ACTIVE fixtures invisible to engine + assets list; analytics/chat/planning ACTIVE semantics unchanged); backfill dry-run on TEMP (below).
- Backfill (temp-proven, live-OWNED-BY-WORD): script/plan converting any live value outside the vocabulary to the nearest legal state (hypothesis: none exist — only ACTIVE/ARCHIVED live; VERIFY on the census); prove it on a temp copy of the live shape; record the EXACT production command + its before/after census queries for the owner word. The live backfill does NOT run here (`PG-PR-10` — which database and which grant: temp here, live on word).
- Full backend suite green modulo the 2 known decoder env reds (stash-proved on the slice — quote the proof), ruff clean, mypy delta 0, secret gate 0 real over changed files (quote the grep).

## G3 — refresh + verify (D145 owned refresh)

- One backend rebuild + exactly ONE recreate + verify. AFTER proofs quoted raw against G1 BEFORE: image id differs, `alembic current` unchanged (no migration — state the empty diff), counts delta exactly zero (no backfill live, no press), health exact ×6, gate 301/401, PATCH-status illegal edge 422 through the FRESH server (behavioral proof the new code serves).
- Post-restart sweep WAIVED (`PG-DP-02` — restart-gated); substitute: in-process suite pre-restart + post-restart probes as authority. No browser-driven tests on this path — state the derived set and that it differed nowise.
- Actual-versus-budget per leg with units (`PG-PR-06` stated against the build+recreate+verify bound).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-111.log`, `SG-111_report.md`, `SG-111_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + BEFORE/AFTER pairs + the reader inventory with keep/widen/untouched per hit). First token `SG-111`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** transition module + API validation hunks + reader hunks + tests + backfill script/plan + `docs/worklogs` — NOTHING else (`models/` + `alembic/` + `frontend/` empty diff or STOP; no merge-map, no creation-flow change; `docker compose config` FORBIDDEN). Ordered paths committable (re-verify `.gitignore` before commit, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands schema change, merge-map, creation reroute, frontend, second recreate, live backfill, press, or any metered call — no cell collides; stated so the check exists on paper. Reads include pytest/TestClient + host commands + the authorized image build and ONE recreate; pulling/running any OTHER image or launching unnamed runtimes counts as execution — not authorised.
- Privacy: identifiers TEXT only; host `.env` never printed, never read into any artifact (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Transition chain enforced end to end with illegal edges 422 through the real routes; readers (incl engine) admit ACTIVE only via the shared predicate with zero stray literals; backfill proven on temp with the production command recorded for the word; suite/gates green; refresh proved with zero row delta; $0; live backfill NOT run; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): transitions — can an asset reach a state the map forbids? readers — does any path still treat status as free text? backfill — is the production word executable as written?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-111 | Report: docs/worklogs/SG-111_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 600s build+recreate+verify · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
