# SG-186 — R6: evidence-integrity detection repair (DRAFT, next session)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Report actual resolved commit.
**STATUS: RE-REVIEWED vs tree at `5be388f`+ under D16 L3 flow; premises hold (serve path trusts the DB row at `evidence.py:101`, untouched since SG-006; upload replay at `:25-26` is the same two-line shape SG-185 fixed in `assets.py`). Scope-approved D5, sibling homed below.**
**DATABASE: separately isolated disposable test database/storage; production GET observations only.**
**Restart: none. Autonomy: L3** (D16 flow). Owner decision D5 fixes the approach: read-time content-hash verification at serve time (not documented acceptance of silent corruption). Sibling homed (SG-185 I1 → here): `upload_evidence`'s key replay at `evidence.py:25-26` is the same two-line shape SG-185 fixed — qualify it by the requesting household (fresh key for the requester, original row incl. changed payload for the owner) and cover it with the same two-household test shape, all inside this slice's ceiling. If on FIRST READ it is NOT the same shape, do not widen: report it as a found sibling for a follow-up and say which. Its tests ride the same focused files.

## Why this exists

Proven gap: flipping one stored byte (same size) is served 200 with content sha differing from the DB row, while missing originals correctly fail (SG-180 F-SG180-3, real route). SG-182 re-proved at DB level that `PRAGMA integrity_check` returns ok on same-length corruption and names/sizes fingerprints are blind to it — hash comparison is the only detector that works (F-SG182-2, real WAL drill). Expected read path (verify on target): `backend/app/api/v1/evidence.py:101-104` serving via `local_store.absolute_path` trusting the DB row. Measure the per-read cost of a rehash on a fixture population and report it — the decision anticipates a budget question, so the number must exist.

## G1 — Verify content at serve time, fail loud on mismatch

On the evidence file-serve path, recompute the stored bytes' sha256 at read time and compare against the DB row before serving; on mismatch refuse with an explicit integrity error (never serve the corrupt bytes, never silently fall back to them). Missing-original behavior (404/quarantine) stays exactly as-is — prove with the existing counter-controls. FAIL-then-PASS: pre-change code serves the mutated byte (200 + divergent sha); post-change refuses; same-length DB-corruption fixture from SG-182's drill doubles as the discrimination control (integrity_check-ok yet refused).

## G2 — Cost and blast-radius honesty

Report measured per-read overhead (mean over a real-route fixture loop, disposable state) and name every caller of the serve path (trace exact consumers — thumbnail, original, job-pipeline readers) so the overhead applies where measured, nowhere assumed. If a hot path makes per-read rehash measurably painful, gate narrowly (e.g., verify originals, keep derived thumbnails on stored metadata) — but report the gate and its residual risk explicitly rather than silently narrowing scope.

## Constraints and acceptance

- Write ceiling: the evidence serve path + its focused tests, `docs/worklogs/SG-186*`. No schema/migration unless the fix needs a stored-hash column (prefer comparing against the existing row sha; justify any migration with a measurement). No frontend change; no production write; no paid call; no infra change; no restart.
- Disposable `DATABASE_URL`/`STORAGE_ROOT` asserted pre-import; no `.env` handling.
- ALL optional environment/Docker probes excluded; ANY privileged denial STOPS the whole slice.
- Ordinary commands 120s; focused tests 600s; no full suite; no watcher.
- Start/end health GET; contract 0.47.0 echo + source; base/Work-HEAD/settings/lane budget/deadline/elapsed.
- A1: same-byte-mutated fixture refused at serve time with explicit error; missing-original 404/quarantine controls unchanged and green.
- A2: per-read overhead measured and reported; all serve-path callers enumerated with the fix's coverage stated per caller.
- A3: tests drive the real serve route on disposable storage (mutate → refuse; delete → 404; pristine → 200 with matching sha); no placebo.
- A4: first token SG-186; `docs/worklogs/SG-186_report.md`; FIRST READ / DURING EXECUTION / REMAINING with dispositions.

Guards: PG-EV-01/02/03/04/05/06/07/09/13; PG-SC-01/02/03/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/07/10.

Receipt: commits `Dispatch-ID: SG-186`; notes `refs/notes/storagegenie-coder-reports` first line `Dispatch-ID: SG-186 | Report: docs/worklogs/SG-186_report.md`, Work-HEAD; push automation/notes with exact remote readback. No retired finalizer. Architect audits/rates before SG-187. No close or deploy in this slice.
