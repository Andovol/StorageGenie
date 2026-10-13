# SG-185 — R4: household-scoped asset idempotency repair (DRAFT, next session)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Report actual resolved commit.
**STATUS: DRAFT prepared 2026-10-13 from SG-181 G1 evidence; scope-approved D4 (R4 + changed-payload replay policy). RE-REVIEW against the tree before dispatch next session.**
**DATABASE: separately isolated disposable test database/storage; production GET observations only.**
**Restart: none. Autonomy: L2.** Owner decision D4 fixes the semantics: replay is household-scoped (same key in another household never returns a foreign row). Changed-payload same-key policy: same-household changed payload returns the ORIGINAL row explicitly (current semantics kept, documented) — do not invent fingerprinting.

## Why this exists

Proven defect F-SG181-1: `POST /v1/assets?household_id=B` with a key first used by A returns 201 with A's asset id and A's household, payload ignored; root `backend/app/api/v1/assets.py:79-87` global `filter_by(key=...)` with no household check (SG-181 G1 real-route two-household proof + fresh-key/no-key/foreign-403 controls; audit SG-181_audit.md). Sibling evidence-key replay (F-SG180-1/2/4) is the same family but a separate surface — out of scope here, named only so its tests are not disturbed.

## G1 — Scope the replay check, keep the current semantics honest

Repair `post_asset` so the replay lookup is household-qualified (key + requesting household); a foreign key behaves as a fresh key for the requester (own row created) or an audited explicit rejection — implement the former (less surprising; matches import replay's household behavior family), and say which in the report. Same-household changed payload keeps returning the original row; document the semantic beside the lookup (comment, not a behavior change). No model/schema change unless the qualified lookup requires a composite index — measure first, prefer the query-only fix.

## G2 — Consistency where the key is read

Inspect every other reader of the asset `IdempotencyKey` table and the `list_assets` filter surface (F-SG181-8 archived-visibility decision D8 applies in SG-188, not here — do not bundle it): if another path returns rows across households by key, report it as a found sibling (do not silently widen scope; fix only `post_asset` unless a sibling is the same two-line shape, then fix and name it). CatalogPage saved-search writer behavior unchanged.

## Constraints and acceptance

- Write ceiling: `backend/app/api/v1/assets.py` (+ migration only if the measured query needs the composite index — justify with a plan-shape measurement, otherwise none), focused tests under `backend/tests/` for this behavior, `docs/worklogs/SG-185*`. No frontend change; no production write; no paid call; no credential/infra change; no restart.
- Disposable `DATABASE_URL`/`STORAGE_ROOT` asserted pre-import; no `.env` handling; scripted-only providers (none expected on this path — a provider call here is a STOP-and-report).
- ALL optional environment/Docker probes excluded; ANY privileged denial STOPS the whole slice.
- Ordinary commands 120s; focused tests 600s; no full suite; no watcher.
- Start/end health GET; contract 0.47.0 echo + source; base/Work-HEAD/settings/lane budget/deadline/elapsed.
- A1: SG-181 G1 two-household replay now returns own rows both ways (B key→B row, A key→A row) with 201s; foreign GET/PATCH still 403.
- A2: FAIL-then-PASS focused tests (pre-change code reproduces 201-foreign; post-change own-row), same-household changed-payload control documents original-row semantics, normal same-key replay still returns the original row.
- A3: no placebo — tests drive `post_asset` through real routes on disposable households, asserting persisted `IdempotencyKey` rows + audit effects, not response shapes alone.
- A4: first token SG-185; `docs/worklogs/SG-185_report.md`; FIRST READ / DURING EXECUTION / REMAINING with dispositions.

Guards: PG-EV-01/02/03/04/05/06/07/09/13; PG-SC-01/02/03/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/07/10.

Receipt: commits `Dispatch-ID: SG-185`; notes `refs/notes/storagegenie-coder-reports` first line `Dispatch-ID: SG-185 | Report: docs/worklogs/SG-185_report.md`, Work-HEAD; push automation/notes with exact remote readback. No retired finalizer. Architect audits/rates before SG-186. No close or deploy in this slice.
