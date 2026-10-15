# SG-194 — jobs.py cursor twin: malformed cursor is a 422, never a silent page-1 repeat

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none** (disposable test DBs only; production datastore never opened — start/end health GETs only per `CO-92`, delta reported).
**Restart: none.**
**Autonomy: L3.** Stage: owner's 2026-10-15 starter arc (deploy + micro-slice + candidates) under D16. Dispatch settings ride the trigger, never this packet.

Authoring date (metadata, never a gate): 2026-10-15.

## Why this exists

SG-188 fixed the falsy-cursor skip on two list surfaces (`assets.py:301-304`, `review_tasks.py:47-50`: `if cursor is not None` + `if decoded is None: raise 422 "malformed cursor"`) and reported the third twin outside its ceiling: `backend/app/api/v1/jobs.py:115-121` still runs `if cursor:` + `if decoded:` — a truthy-but-undecodable cursor skips the filter and silently repeats page 1. Verified by the Architect 2026-10-15 at HEAD `706b9b6` — re-verify on target FIRST READ; if the construct is already gone, STOP and report, do not manufacture a change. EXPECTED minimal repair: the SG-188 shape mirrored, no new behavior beyond the 422. No `slowest_waste` named yet (SG-193 rated pre-`D436`) — nothing to remove this packet.

Expected recorded/published/host contract 0.50.0 (`D-2` adoption this session). Echo version/source and report differences.

## G1 — Repair the twin + FAIL-then-PASS

Mirror the SG-188 cursor shape into `list_jobs` (`backend/app/api/v1/jobs.py:115-121` EXPECTED): undecodable cursor → 422 `malformed cursor`; valid cursor pages as before; absent cursor unchanged. One focused test module (EXPECTED new `backend/tests/test_sg194_jobs_cursor.py` reusing the disposable-DB fixture pattern; extending `test_sg188_semantics.py` acceptable only with a stated reason): malformed cursor → 422 on `GET /v1/jobs`, valid cursor still pages, absent cursor unchanged. `D443`: the new rows' FAIL half runs on the base with BOTH runs in the committed log (`PG-EV-09`); the FULL backend suite runs once on the candidate; an old row failing on the candidate is run alone on the base; no count carried from an earlier slice. Frontend untouched and unrun (no frontend in ceiling — stated, not silent).

## Constraints

Scope ceiling: `backend/app/api/v1/jobs.py` (G1 hunk only) + one test module (+ `test_sg188_semantics.py` only if extended with reason) + `docs/worklogs/SG-194*` only (`PG-IC-01`: no criterion requires what these exclusions forbid — suite runs and health GETs are reads/executions, not edits). No other route, service, schema, migration, config or frontend file. Production datastore never opened. Ordinary commands bounded 120 s; visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo, no alternate identity/mount, no host config change. No secret in logs (none needed). `PG-EV-06`: rows exist in disposable DBs only, never a live datastore. Twin census (`CO-17`): grep the exact construct class backend-wide, count and classify — EXPECTED 1 live site (this one) + 2 already-fixed; any further twin reported, not widened.
Full suite per `D443` as above. Runtime-vs-lane budget seconds + source (no app spend exists on this path; platform spend stated-not-substituted).

## Acceptance and report

- A1: malformed cursor → 422 `malformed cursor` on `GET /v1/jobs`; valid/absent cursor behavior unchanged (FAIL half on base + PASS on candidate, both runs committed).
- A2: diff is the G1 hunk + one test module only; twin census reported (EXPECTED 1 + 2 fixed, zero new); full backend suite green once on candidate.
- A3: logs + report `docs/worklogs/SG-194_report.md`; elapsed per leg vs ~300 s expectation (uncalibrated, same-class SG-189 basis); constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-194.
- A4: notes-ref receipt `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-194 | Report: docs/worklogs/SG-194_report.md`, Work-HEAD, read-back verified, pushes complete. Bound lane receipt.

Guards invoked: PG-EV-02/03/09; PG-IC-01/07/09; PG-DP-02; PG-PR-03/06. Stop per `PB-6`.
