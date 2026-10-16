# SG-195 — Route error branches: failed queries render an alert, never eternal loading (Catalog, Inbox, Analytics, Planning, Capture)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none.** No backend touch; frontend tests mock queries; no live interaction (jsdom only — health probes not applicable, stated not silent).
**Restart: none.**
**Autonomy: L3.** Stage: owner's 2026-10-15 starter arc under D16 (SG-190 REMAINING candidate 1 of 4). Dispatch settings ride the trigger, never this packet.

Authoring date (metadata, never a gate): 2026-10-15.

## Why this exists

SG-190 REMAINING (SG-190_report.md:68-72): five routes render loading/empty text on query failure with no error branch. Verified by the Architect 2026-10-15 by tree grep — no `isError` on CatalogPage / InboxPage / AnalyticsPage / PlanningPage / CapturePage — re-verify on target FIRST READ. Sibling precedent EXISTS (`role="alert"` at SettingsPage:36, ReviewPage:56, ExpiryPage:163) — mirror that shape; do not invent a new alert idiom. EXPECTED set: Catalog assets list, Inbox jobs/tasks/detail, Analytics summary, Planning household/suggestions, Capture household — enumerate the queries on target; a route already branched is reported-not-rebuilt; a route outside this set needing one is reported-not-widened. No `slowest_waste` removal beyond the one below (SG-194 named `5s precommit-focused`).

Expected recorded/published/host contract 0.50.0. Echo version/source and report differences.

## G1 — Error conditionals + FAIL-then-PASS per route

Per route in the EXPECTED set: render `{query.isError && <div role="alert">…}` naming the failed query. Retry affordance ONLY where the route already has a refetch pattern — never invent refetch plumbing; text-only otherwise; decide per route and report the choice. Tests (new focused module or modules — Coder decides, reports why): mocked query-error → the alert renders naming that query; loading/success/empty paths unchanged. `D443`: the new rows' FAIL half runs on the base with BOTH runs in the committed log (`PG-EV-09`); the FULL frontend suite runs once on the candidate (SG-190 precedent: the whole frontend suite is the authoritative set); an old row failing on the candidate is run alone on the base; no count carried from an earlier slice. Backend suite untouched/unrun (no backend in ceiling — stated). Every new gate is seen to fail on the base (`PG-EV-01`).

## Constraints

Scope ceiling: the five route files above + ONE shared error-text helper ONLY if the same text emerges on ≥3 routes (fewer → per-route text, duplication reported, no premature component) + test modules + `docs/worklogs/SG-195*` only (`PG-IC-01`: criteria require nothing these exclusions forbid — suite runs are executions, not edits). No backend, no router/nav/state changes (nav household context is a LATER candidate, not this slice), no new routes or data fetching, no screenshots/driver (jsdom only). Ordinary commands bounded 120 s; visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo, no alternate identity/mount, no host config change. No secret in logs (none needed).
Waste removal (`D434`/`D436`, SG-194 `slowest_waste`): NO pre-commit focused pass — the post-commit run gates acceptance. Runtime-vs-lane budget seconds + source (no app spend exists on this path; platform spend stated-not-substituted).

## Acceptance and report

- A1: per-route alert on mocked query error + unchanged loading/success/empty paths (FAIL half on base + PASS on candidate, both committed).
- A2: diff within ceiling; route census reported (EXPECTED 5 branched; already-branched reported-not-rebuilt; out-of-set reported-not-widened); full frontend suite green once on candidate (or old-row base reruns per `D443`).
- A3: logs + report `docs/worklogs/SG-195_report.md`; elapsed per leg vs ~600 s expectation (uncalibrated, vitest-only basis, no driver/screenshots); constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-195.
- A4: notes-ref receipt `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-195 | Report: docs/worklogs/SG-195_report.md`, Work-HEAD, read-back verified, pushes complete. Bound lane receipt.

Guards invoked: PG-EV-01/02/03/09; PG-IC-01/07/09; PG-PR-03/06. Stop per `PB-6`.
