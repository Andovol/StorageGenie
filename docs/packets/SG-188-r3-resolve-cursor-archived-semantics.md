# SG-188 — R3 + data semantics: resolve guard, cursor and archived visibility (DRAFT, next session)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Report actual resolved commit.
**STATUS: DRAFT prepared 2026-10-13 from SG-181 observations; scope-approved D6-scope/D7/D8 (bare-Resolve guard + cursor 422 + archived exclude-by-default). SG-176/177/178 grants RETAIN their classification/Resolve/visibility scope — this slice works inside it. RE-REVIEW against the tree before dispatch next session.**
**DATABASE: separately isolated disposable test database/storage; production GET observations only.**
**Restart: none. Autonomy: L2.**

## Why this exists

Three decided semantics from SG-181, all small and all in the task/list/read surfaces (hypotheses with exact expected roots — verify on target): F-SG181-3 bare `POST /v1/review-tasks/{task_id}/resolve` closes a data-required task while data stays `unknown` (root `review_tasks.py:71-97`, no type/data guard); F-SG181-6 malformed cursor silently returns page 1 (root `assets.py:289-292` falsy-cursor filter skip); F-SG181-7/8 archived rows surface in the default list and in expiry `unresolved_rows` (roots: `list_assets` filters-only-when-passed; `expiry_engine.compute_status` active/archived policy). Owner decisions D7/D8 fix the semantics: guard the resolve, 422 the malformed cursor, exclude archived by default.

## G1 — Data-required tasks cannot close without data

`resolve_review_task` refuses a bare `{}` resolve for data-required task types (explicit 422 naming the missing data), while the real manual-entry path still resolves and returns `resolved_review_task_ids` as today. Classification→expiry→task readback fixtures from SG-181 G2 are the control population (food → task; non-perishable → no task). FAIL-then-PASS: pre-change bare Resolve 200-with-unknown-data; post-change 422 + data still unknown; real-entry resolve 200 accepted. SG-176/177/178 classification/repair scope is consumed, not widened.

## G2 — Cursor and archived visibility per the decided semantics

Malformed cursor → explicit 422 (no silent page-1); valid-cursor paging still walks tied-timestamp populations losslessly (SG-181's 25-row/3-page walk is the regression shape). Default `GET /v1/assets` excludes ARCHIVED (explicit `status=ARCHIVED` still lists them); expiry status engine excludes archived/ineligible assets from `unresolved_rows` (archived row no longer counted). Each change ships its negative control (malformed 422 vs valid walk; archived-excluded default vs explicit-filter inclusion).

## Constraints and acceptance

- Write ceiling: `backend/app/api/v1/review_tasks.py`, the assets list/cursor path, `expiry_engine.compute_status` (+ callers if the unresolved contract moves — enumerate them), focused tests, `docs/worklogs/SG-188*`. No schema/migration; no UI behavior change (CatalogPage already sorts loaded pages — wording alignment, if any, is presentation-only per `CO-25`); no production write; no paid call; no infra change; no restart.
- Disposable `DATABASE_URL`/`STORAGE_ROOT` asserted pre-import; scripted-only providers; no `.env` handling.
- ALL optional environment/Docker probes excluded; ANY privileged denial STOPS the whole slice.
- Ordinary commands 120s; focused tests 600s; no full suite; no watcher.
- Start/end health GET; contract 0.47.0 echo + source; base/Work-HEAD/settings/lane budget/deadline/elapsed.
- A1: bare-Resolve 422 with data still unknown; real-entry resolve accepted with `resolved_review_task_ids`.
- A2: malformed cursor 422; valid paging lossless; archived excluded by default, included on explicit filter; unresolved rows drop the archived row.
- A3: tests drive real routes on disposable populations (25-row tied-timestamp walk re-derived, not copied); no placebo.
- A4: first token SG-188; `docs/worklogs/SG-188_report.md`; FIRST READ / DURING EXECUTION / REMAINING with dispositions.

Guards: PG-EV-01/02/03/04/05/06/07/09/13; PG-SC-01/02/03/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/07/10.

Receipt: commits `Dispatch-ID: SG-188`; notes `refs/notes/storagegenie-coder-reports` first line `Dispatch-ID: SG-188 | Report: docs/worklogs/SG-188_report.md`, Work-HEAD; push automation/notes with exact remote readback. No retired finalizer. Architect audits/rates before SG-189. No close or deploy in this slice.
