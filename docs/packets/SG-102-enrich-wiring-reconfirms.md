# SG-102 — Persisted-snapshot wiring + live re-confirms (EU base, OFF accept) (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D139/D141 L3 Arc A slice 4 of 5 (SG-099 live-closed by SG-101 → SG-100 GREEN → SG-101 GREEN → live re-confirms → reviewer alternatives SG-103). SG-098's endpoint returns `"snapshots_recorded": False` (`api/v1/enrich.py:209`, re-verified 2026-09-23 — re-verify) with the fetch `record` in hand (`.primary` OFF + `.fallback` Jina|None, serializers both sides); SG-100 shipped the append-only writer + table (migration unapplied in production). THIS slice wires recording into the endpoint and re-confirms the live bases. Reviewer alternatives (`web_alternates` first-class rows) ride SG-103, not here. **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-23); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** wiring + re-confirm ONLY. No fetcher changes (OFF/Jina clients read-only), no synthesis changes (proven SG-101, zero new synthesis calls), no model/migration (prove by empty diff over `models/`+`alembic/`), no frontend, no deploy, no restart, no container action. Interim honesty (`PG-PR-05`): the production DB LACKS the `enrich_snapshot` table until a later owner-gated rider applies the migration + deploys — until then the running service is old code and the new wiring is unreachable there; proof is tests + in-process live legs on temp DBs, never the deployed service. Bounded live fetch: OFF ≤2 searches (free) + Jina ≤2 searches (worst-case ≤$0.01 total, uncalibrated `G-A9` — actuals reported); synthesis ZERO calls. Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05`).
**Money posture:** REAL metered spend, Jina ≤2 searches ≤$0.01 worst-case (uncalibrated, actual-vs-budget with units, `PG-PR-06`); OFF free; synthesis $0.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-06` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-10` · `PG-IC-01` · `PG-IC-03` · `PG-IC-04` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-05` · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint, 60s per live call, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none live** (no migration; ALL live legs run in-process on temp DBs per the SG-099/101 precedent; production counts read back identical before/after via read-only queries, `PG-EV-06`). **Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`).

## G0 — consent/key-name gate (read-only, NAMES only)

- `ai_status()` enabled + Jina key NAME present before any metered touch. Closed gate → Jina legs UNEXECUTED with the named reason, OFF legs + wiring still ship (OFF is keyless; stopping the metered part is SUCCESS for the remainder). STOP beats retry itch (`PG-IC-03`) — the one L3 retry covers transients only (zero commits + clean tree + transient signature), never a routed STOP.

## G1 — snapshot recording wired into the endpoint (`PG-SC-02` closure)

- In `trigger_enrich`, after the fetch `record` resolves and BEFORE the candidate commit: `record_off_snapshot(db, record.primary, query=...)` always + `record_jina_snapshot(db, record.fallback, query=...)` when fallback is not None (query = the searched brand+name TEXT the endpoint already holds). `snapshots_recorded` becomes `True` (it is `False` today — the flip is asserted, not assumed). Degraded snapshots record with reason (SG-100 rule, restated). `snapshots.py` stays read-only unless a failing test proves a hunk (M45 terms, disclosed, else STOP).
- The writer + loader are BOTH in acceptance: a test triggers the endpoint (scripted transports) and reads the rows back via `get_snapshots_by_source` — writer and reader in one leg, `PG-SC-02` closed in-slice.

## G2 — live re-confirm legs (in-process, temp DBs, bounded)

- Leg A (OFF, free): one populated search for a real product (brand+name TEXT) through the REAL OFF client. Assert the request shape + classify the outcome: 200-with-products = ACCEPTED (quote count + first code); loud-degraded/503 = reported NOT MET with the named reason (SG-099 honesty precedent — a 503 is a finding, never a pass).
- Leg B (EU base, diagnostic): ONE retrieval attempt at the EU base. Resolves → record the outcome; EU default stands, NO code switch in this slice (global stays diagnostic-only, SG-082 rule). Still NXDOMAIN → EU-stands confirmed with the resolver output quoted. Either outcome is a measurement, reported with the raw line — the criterion asserts the attempt + classification, never a predetermined resolution.
- Leg C (Jina global, metered ≤2): one fallback-shaped search through the REAL Jina client → snapshot recorded to the temp DB via the G1 wiring path ( importer: the same `record_jina_snapshot` the endpoint calls — close the live→persisted loop, don't re-implement it). Quote spend actuals.
- Raw-body recorder from leg 1 (SG-099 lever, now standing). No second attempts beyond the one authorized L3 retry, and only on a transient signature. No synthesis calls (proven SG-101).

## G3 — tests + gates ($0 offline) + G4 worklog/report (`CO-57`)

- Offline tests (scripted transports): endpoint records OFF+Jina rows readable via the loader (`snapshots_recorded: True` in body); degraded fetch records reason; one fetch = exactly one row per source (no double-write); consent-false still refuses with 0 sends (regression leg — the recording hunks must not precede the gate). Fail-then-pass BOTH raw committed (`PG-EV-09`; seen-to-fail in-run, `PG-EV-01`).
- Full suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0 real.
- `{{WORKLOG_DIR}}/SG-102.log`, `SG-102_report.md`, `SG-102_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + live captures). First token `SG-102`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** actuals); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `api/v1/enrich.py` recording hunks + `snapshots.py` ONLY on M45 terms + new test file + `docs/worklogs` (3 files) — NOTHING else. Ordered paths committable (`.gitignore` verified 2026-09-23, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands a migration, fetcher/synthesis changes, frontend, deploy, restart, container acts, or metered calls beyond Jina ≤2 + the authorized retry — no cell collides; stated so the check exists on paper. Reads include TestClient + host commands only; pulling/running images or launching unnamed runtimes counts as execution — not authorised.
- Privacy: identifiers TEXT only (never photos/GPS); key never in any file, log, or assertion (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; fixture timestamps are sample data; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Endpoint records OFF row always + Jina row when fallback present, readable via the loader; `snapshots_recorded: True`; degraded path records reason; one fetch = one row per source; consent gate still precedes everything.
- OFF leg classified (ACCEPTED with count+code, or NOT MET with named reason); EU leg measured with raw line quoted and no code switch; Jina leg recorded through the real writer with spend actuals.
- Tests fail-pre/pass-post both committed raw; gates green; Jina ≤2 searches within $0.01; synthesis $0; production counts identical; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** actuals. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-102 | Report: docs/worklogs/SG-102_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 60s per live call · 1500s early-close · 2100s overall; REAL metered Jina ≤2 searches ≤$0.01 worst-case (uncalibrated) + OFF $0 + synthesis $0; actual-versus-budget per leg with units.
