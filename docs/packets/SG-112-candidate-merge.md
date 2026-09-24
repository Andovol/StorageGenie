# SG-112 — Candidate merge: duplicate review rows merge into one survivor, losers terminal ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D154-approved G-stage slice 3 of 5 (G7 GREEN 98 → G5 GREEN 98 → G6 → G3 → G4; L3-build). Blueprint journey A decision list: accept, edit, split, merge, hold, reject — merge is the missing review action (gaps G6). Current tree (verified 2026-09-24, re-verify — every premise below is a hypothesis): decision actions `accept/edit/hold/reject` + separate `split` (`api/v1/candidates.py:16-22,25-117`); candidate states observed: `proposed/edited/accepted/held/rejected/split` (`candidates.py:484`, `:681`, `:1087`, `:1094`, `api/v1/candidates.py:37-58`); the decision guard refuses `{"rejected", "split"}` (`:37`); split precedent `split_candidate` (`candidates.py:1007-1111`): validates-first-then-writes, children share origin evidence + provenance, origin leaves the decidable set, caller commits, route rolls back on error (`api/v1/candidates.py:104-111`); proposals already carry `dedup_matches` (read path `:139-141`); SG-111 reserved `ACTIVE→MERGED` in the lifecycle table with redirect-by-SG-112. THIS slice adds the merge review action + the asset MERGED redirect writer. NO schema change (candidate state strings + assertion rows — prove by empty diff over `models/`+`alembic/`), NO frontend, NO sender. $0 — no metered call exists on any path (a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-24. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-24); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** merge ONLY. `merge_candidates` service + `POST /candidates/merge` route + redirect writer + tests + `docs/worklogs` — NOTHING else. Exactly ONE recreate. Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05`).
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

**DATABASE: none live** (tests on temp DBs; post-restart probes read-only — a write of any kind is a STOP). **Restart: ONE backend recreate (D145 standing + D154 L3-build). Deploy: THIS slice.**

## G1 — capture BEFORE (every observable the proof moves; `PG-EV-08`)

- Image id, `alembic current` (hypothesis single head — VERIFY), 25-table counts (hypothesis 25 — VERIFY), health exact, gate 301/401, merge-absence proof: decision Literal has no merge + no `merge` route/def in candidates paths (quote the grep — the fail-pre baseline for the new action). Quote all raw.

## G2 — merge review action + MERGED redirect (split precedent is the shape; facts handed over)

- `POST /v1/candidates/merge` with `{winner_id, loser_ids[]}` (household scoping + 404/403 exactly like the split route, `:99-103` — re-verify): validate FIRST (all exist, same household, all `proposed`, winner not among losers, ≥1 loser, losers carry no open review tasks — enumerate the task types that must be clear on target, `PG-EV-08`; anything written before a refusal is the defect), then write: winner KEEPS its fields and stays `proposed` (merge never auto-accepts — the review still decides; state this invariant in code), winner's `evidence_ids` becomes the UNION (dedupe exact), each loser → state `"merged"` with `merged_into: <winner_id>` recorded in its proposal (read-back via `GET /v1/candidates/{id}`, `PG-SC-02`: writer = merge route, reader = candidates route), open duplicate tasks on losers resolved with audit rows (split precedent `:1096-1111` — re-verify the audit shape).
- The decision guard (`api/v1/candidates.py:37`) MUST learn `"merged"` (a merged loser re-decided is 409 — the exact site the split slice had to touch; missing it re-opens decided rows, and a test proves it).
- Asset MERGED redirect (makes SG-111's reserved value meaningful with NO new table): writer takes a materialized duplicate asset → validates `ACTIVE→MERGED` through the lifecycle table → writes status + a redirect assertion (`field_path` naming is yours inside the `merge.*` namespace, reported; value carries `merged_into`) + audit row; read-back names the winner (assert through the existing asset read path, `PG-SC-02`). A MERGED asset with no redirect yet reads terminal, never dangling (`PG-SC-07` — run the no-redirect case in test).
- **What this choice turns on:** which rows count as "the duplicate set" (candidate proposal `dedup_matches` vs explicit ids in the request) — the request's explicit ids win (a list is a fact too: the Coder does NOT trust a handed list, it validates each id on target); `dedup_matches` is evidence for the reviewer, never the merge set.
- Tests (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; seen-to-fail in-run, `PG-EV-01`): merge two proposed duplicates → winner proposed + union evidence + losers merged with `merged_into` readable back; illegals (decided loser, cross-household, winner==loser, empty losers, loser with open tasks) each refused with NOTHING written (prove by before==after counts, `PG-EV-02`); decided-merged-loser re-decision 409; asset MERGED + redirect round-trip incl no-redirect terminal read.
- Full backend suite green modulo the 2 known decoder env reds (stash-proved on the slice — quote the proof), ruff clean, mypy delta 0, secret gate 0 real over changed files (quote the grep).

## G3 — refresh + verify (D145 owned refresh)

- One backend rebuild + exactly ONE recreate + verify. AFTER proofs quoted raw against G1 BEFORE: image id differs, `alembic current` unchanged (no migration — state the empty diff), counts delta exactly zero (no merge executed live, no press), health exact ×6, gate 301/401, merge route present in the fresh image (grep the served code) + one illegal-merge refusal through the FRESH server on a temp DB (behavioral proof, no live write).
- Post-restart sweep WAIVED (`PG-DP-02` — restart-gated); substitute: in-process suite pre-restart + post-restart probes as authority. No browser-driven tests on this path — state the derived set and that it differed nowise.
- Actual-versus-budget per leg with units (`PG-PR-06` stated against the build+recreate+verify bound).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-112.log`, `SG-112_report.md`, `SG-112_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + BEFORE/AFTER pairs). First token `SG-112`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** merge service + merge route + decision-guard hunk + redirect writer + tests + `docs/worklogs` — NOTHING else (`models/` + `alembic/` + `frontend/` empty diff or STOP; no merge-map table, no auto-accept, no creation-flow change; `docker compose config` FORBIDDEN). Ordered paths committable (re-verify `.gitignore` before commit, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands schema change, merge-map table, auto-accept, frontend, second recreate, live merge, press, or any metered call — no cell collides; stated so the check exists on paper. Reads include pytest/TestClient + host commands + the authorized image build and ONE recreate; pulling/running any OTHER image or launching unnamed runtimes counts as execution — not authorised.
- Privacy: identifiers TEXT only; host `.env` never printed, never read into any artifact (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Duplicate merge leaves one proposed survivor with union evidence and terminal losers carrying `merged_into`, readable back; every illegal shape refused with zero writes; merged losers undecidable; asset MERGED + redirect round-trips; suite/gates green; refresh proved with zero row delta; $0; no live merge; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): merge — does the survivor hold everything while losers stay terminal? refusal — can a bad merge write anything? redirect — does MERGED point somewhere?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-112 | Report: docs/worklogs/SG-112_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 600s build+recreate+verify · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
