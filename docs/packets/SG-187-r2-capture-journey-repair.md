# SG-187 — R2: capture/import journey repair (DRAFT, next session)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Report actual resolved commit.
**STATUS: DRAFT prepared 2026-10-13 from SG-179/180 journey evidence; scope-approved D6 (R2; cancellation stays deferred-not-absent). RE-REVIEW against the tree — especially the UI files — before dispatch next session.**
**DATABASE: separately isolated disposable test database/storage; production GET observations only.**
**Restart: none. Autonomy: L2.** Cancellation (F-SG180-8) is explicitly OUT: no cancel writer is built; the slice only proves no cancel path is falsely advertised. If a cancel affordance is found in UI text, it is corrected to honest wording (presentation fix), not wired to a new backend writer.

## Why this exists

Approved-but-broken journey SC-02/03: CREATED jobs strand in the Inbox with no Run/Start control while the import modal's help promises "waits in the Inbox until you run it there" (SG-179 real-route + render proof; F-SG180-7). Rejection hygiene: nonexistent-household upload orphans the stored original before the FK failure and leaks raw SQL/parse wording to the client (F-SG180-9). Surface mismatch: import modal accepts png/jpg/webp only while the backend accepts more, with no client-side size check and a stale 25 MB note vs enforced 20 MiB (F-SG180-14). Expected surfaces (re-verify before changing): `frontend/src/routes/AssetImportModal.tsx` (≈:140 run call, ≈:252 help text), `frontend/src/routes/InboxPage.tsx` (≈:37 FAILED-only retry), `JobCard` select-only, `backend/app/api/v1/evidence.py` upload path (`:26-58` key replay + validation order, `:41` full-buffer read, `:56-58` catch-all), `backend/app/api/v1/jobs.py:39-44` replay.

## G1 — CREATED jobs gain an explicit Start where the promise points

Wire the Inbox CREATED-job Start to the real `/run` (the modal's existing call is the proven pattern) with honest pending/running/failed states; failed jobs retry honestly (no fake success). worked-then-verified through real routes on disposable state: CREATED → Start → AWAITING_REVIEW/COMPLETED transitions; controls: FAILED retry path unchanged in behavior, foreign-household 403s intact.

## G2 — Rejections clean up and speak plainly

Upload against a failing household/validation path must not leave orphaned stored bytes (clean up on row failure) and must return readable client errors without raw SQL/parse internals. Oversize keeps the explicit 413 (cap semantics preserved — the full-buffer memory shape F-SG180-10 is noted, not redesigned here). FAIL-then-PASS with the SG-180 probes as the failing baseline (orphan present + raw detail pre-change; no orphan + clean detail post-change).

## G3 — Import surface tells the truth

Modal accepted-formats/size note matches backend reality (accepted set + 20 MiB cap stated; client-side pre-check where cheap, server remains authoritative). Presentation acceptance for wording changes per `CO-25` (screenshots + owner checklist; Architect opens every image independently).

## Constraints and acceptance

- Write ceiling: the Inbox/modal/JobCard surfaces above, the evidence upload + jobs replay paths, focused tests for each, `docs/worklogs/SG-187*`. No schema/migration; no new cancel writer; no provider change; no production write; no paid call; no infra change; no restart.
- Disposable `DATABASE_URL`/`STORAGE_ROOT` asserted pre-import; scripted/fake providers only; no `.env` handling.
- ALL optional environment/Docker probes excluded; ANY privileged denial STOPS the whole slice.
- Ordinary commands 120s; focused tests/browser runs 600s; no full suite; no watcher.
- Start/end health GET; contract 0.47.0 echo + source; base/Work-HEAD/settings/lane budget/deadline/elapsed.
- A1: CREATED→Start→terminal transitions real-route proven with foreign-403 + retry-honesty controls.
- A2: failing-upload fixtures leave no orphan bytes and return non-raw errors; 413 preserved.
- A3: modal wording matches enforced reality; screenshot evidence for presentation hunks.
- A4: first token SG-187; `docs/worklogs/SG-187_report.md`; FIRST READ / DURING EXECUTION / REMAINING with dispositions.

Guards: PG-EV-01/02/03/04/05/06/07/09/13; PG-SC-01/02/03/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/07/10.

Receipt: commits `Dispatch-ID: SG-187`; notes `refs/notes/storagegenie-coder-reports` first line `Dispatch-ID: SG-187 | Report: docs/worklogs/SG-187_report.md`, Work-HEAD; push automation/notes with exact remote readback. No retired finalizer. Architect audits/rates before SG-188. No close or deploy in this slice.
