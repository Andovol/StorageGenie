# Accepted optimizations — register and roadmap deltas

**Date:** 2026-09-03 · **Status:** accepted by owner (`m0015`, `m0019`) · **Blueprint:** `inception/generic_asset_catalog_expiry_tracker_blueprint.md` v3, UNCHANGED (this file carries the deltas, not a rewrite)
**Cap policy (`m0019`):** no silent hard caps — every limit is a named, env-overridable setting, logged when it binds, rejected visibly (`413`/`422` with detail). Softens the AGENTS.md 20 MB narrowing: 20 MB stays as configured default with visible `413`.

## Rejected (do not re-propose)

- `UV-3` barcode-before-OCR ordering — owner: plan order stands.
- `UV-6` static dosage guardrails — owner: blueprint §10 rollout stands unchanged.

## Accepted — user value

- `UV-1` **Restore round-trip in Phase 0 exit.** Re-import the export manifest into a scratch DB, compare asset + evidence counts. Lands in Task 15 (`test_phase0_e2e.py` shape). Grounding: owner-accepted backup doctrine; an untested backup is a hope.
- `UV-2` **FTS5 moves to Phase 1 (was Phase 4).** `ILIKE` full-scans won't hold the §2.3 <300 ms target at ~10k assets. Grounding: ADR-008 "deterministic FTS first"; SQLite ships FTS5 in-process (sqlite.org/fts5.html), no new dependency.
- `UV-4` **In-app reminders before push.** Expiry dashboard (§11.2 screen 7) + review queue first; push infra deferred to Phase 3 with its own decision. Grounding: zero new infra, works offline, local-first.
- `UV-5` **Measure time-to-first-asset.** Log `job-created → asset-accepted` duration on the existing `audit_event` timestamps. Grounding: §2.3 90 s target is asserted nowhere-observed today.

## Accepted — build / maintain

- `BM-1` **Pin hard-to-change contracts in Phase 0:** export-manifest schema + version field, assertion `value_json` conventions, `review_state` enum, UUIDv7 IDs. Thresholds/tiers/UI stay loose. Grounding: `G-A9`.
- `BM-2` **Wire the real idempotency table.** `backend/app/models/idempotency.py` exists — use it; Task 7's "in-memory or audit lookup" wording is retired. Grounding: §2.3 100% duplicate prevention; process restarts kill in-memory keys.
- `BM-3` **Test-backfill, don't rebuild.** `backend/app` covers Tasks 2–11 with empty `backend/tests`; slices add tests per task, reporting "already passed, hardened" where true.
- `BM-4` **Postgres-dialect compile check in CI.** Compile Alembic DDL against the Postgres dialect offline — no server. Grounding: keeps ADR-001 migration path honest; SQLAlchemy dialect compilation.
- `BM-5` **Migration discipline:** applied revisions immutable (VPS runs `0201cf10c56c`), one new revision per slice, `seed.py` idempotent.
- `BM-6` **Transactional export.** Manifest inside a single read transaction + DB revision recorded in it — makes "consistent backup" true.
- `BM-7` **`job`/`review_task` stay read-only stubs through Phase 0** (already so in `jobs.py`/`review_tasks.py`). Zero worker infra until Phase 1. Grounding: `G-A7`.
- `BM-8` **Trust-boundary note:** LAN-only, single household, no auth in Phase 0 — so scoping is never misread as security.

## Accepted — tech stack (sources verified 2026-09-03)

- `TS-1` **`PRAGMA busy_timeout`** in the existing `db.py:18-25` listener (FK + WAL already set). Use case: second user saving mid-import gets a wait, not `database is locked`. Source: sqlite.org `PRAGMA busy_timeout` docs — the pragma form of `sqlite3_busy_timeout()` for language bindings.
- `TS-2` **Pillow bomb guard, dynamic form.** Keep Pillow's own `MAX_IMAGE_PIXELS` default; escalate `DecompressionBombWarning` → error, log, visible `422`. No custom magic number. Use case: crafted upload OOMing thumbnailing (§12.1 image-parser attacks). Source: Pillow `Image.open` docs — warning over limit, `DecompressionBombError` over 2×, `warnings.simplefilter('error', …)` escalation.
- `TS-3` **EXIF-free derivatives.** Transpose orientation, save thumbnails without EXIF/GPS; originals byte-identical. Use case: phone GPS leaking via UI/thumbnails. Slice proves the property on our files (`PG-EV-05`).
- `TS-4` **Backend lockfile + pinned base image.** Only `frontend/package-lock.json` exists; `backend/Dockerfile:1,5` installs unpinned deps on unpinned `3.12-slim`. Use case: VPS build drifts from dev silently. Source: uv lockfile + sync model (docs.astral.sh/uv).
- `TS-5` **Fix `lint` script.** `frontend/package.json:10` ends in `|| true` — a gate that cannot fail is decoration. Advisory until tree clean, then drop it. Source: `PG-EV-01`.

## Slice assignment

- **SG-005 (foundation verify/repair):** `TS-1`, `TS-4`, `TS-5`, `BM-3` (Task 1–2 scope), `BM-5` going forward.
- **Evidence/upload slice (Tasks 5/8):** `TS-2`, `TS-3`.
- **Asset/export slices (Tasks 9/11):** `BM-1`, `BM-2`, `BM-6`.
- **Exit slice (Task 15):** `UV-1`, `UV-5`, `BM-8` note.
- **CI (Task 1):** `BM-4`.
- **Phase 1:** `UV-2` (FTS5). **Phase 2/3 boundary:** `UV-4` (push decision).
