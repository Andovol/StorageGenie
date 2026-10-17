# SG-210 — serve rider: live-deploy the SG-207 + SG-208 product delta (D-5 re-serve due)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none (SQLite read-only verification — sha pre/post/recreate/tests byte-identical, no writes). Restart: ONE `docker compose build backend` + ONE `docker compose up -d --no-deps backend` on the lane socket** (`DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-210/docker.sock`; default socket never touched).
**Autonomy: L3** (approved queue; checkpoints only on `G-K2`/assumption-change/stage end). Authority: standing 2026-09-28 close-deploy directive + D-5 conditional (re-serve due — SG-208 rated 98 with SG-207 unserved). Precedent shape: SG-206 (rated 97), SG-202, SG-193.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

SG-207 (raw-panel removal, 2 files) and SG-208 (selector removal, 19 files) are rated and committed but NOT live: production still serves the SG-206 bundle. D-5 fires: serve now.

## Handed-over facts (expected — re-verify on target, `PB-1`)

- Product delta since the SG-206 serve (`b029593`): SG-207 (`ItemInspectorDrawer.tsx`, `drawer.test.tsx`) + SG-208 (19 files under `frontend/src/`, incl. 2 deletions) ONLY — expected; re-derive the product-surface diff, never assume.
- SG-207 acceptance evidence (expected): greps empty, suite 30/298, smoke screenshot. SG-208 evidence (expected): fail-half 10 red + pass-half 29/293, greps empty (rail justified), smoke `/` + `/inbox` + 2 screenshots. This rider does NOT re-prove behaviour — it proves the SERVED bytes are the audited bytes.
- Catalog route is `/` (there is NO `/catalog` route — SG-207 finding #3). Lane `RUN_BUDGET_S=2100` (read `/etc/dispatch/storagegenie.conf` read-only at execution).

## G1 — rebuild + recreate + prove the served bytes

- FIRST READ the prestate (container id/image/bundle shas, health, DB sha, alembic head, product delta vs served), then exactly ONE build + ONE recreate (named units, lane socket only), then the poststate. Zero denials tolerated; any denial STOPS per `PB-2`.
- Prove: health green start/end + N post-recreate GETs all 200; served index/CSS/JS shas == the candidate build (cross-check image sha vs build manifest as SG-206 did); BOTH removals present IN the served bytes — no `raw-json`/`rawJson` literal AND no `aria-label="Household"` markup in the served bundle (grep the served bytes, `PG-SC-12`); DB sha byte-identical pre/post/post-tests, 28 tables, alembic head unchanged; no migration, no slice-caused row change.
- Focused suite for the touched surface ONCE (derive the consumer set on target as SG-206 did — union of focus-ring-asserting + selector-absence-asserting files; report the derivation, never bend to a list). Full suite NOT re-run (SG-207 298 + SG-208 293 green on this exact tree hours earlier — stated, not skipped silently; `D443`).

## Constraints

- **Scope ceiling:** zero product/config/test/lockfile/schema/migration bytes (rider only); evidence ONLY under `docs/worklogs/SG-210_*`. Reads: lane only, DB mode=ro read-probes only. No secret in any log. `PB-3`: an empty poststate (no container id, no bundle sha) is a FAIL.
- **Out of scope (stated):** Option C/D; AI stages (no transport on record — SG-209 STOP stands); server-side single-household enforcement (decision open); auth-live; native zoom/touch.
- Hang bounds: build 600 s; recreate 120 s; GETs 120 s; suite per its bound; idle kill 900 s never approached. Simplicity: one rebuild + one recreate + proof. Expected duration ≈400 s (Architect record, `G-A9` uncalibrated; derived from SG-206's 407 s same shape — NOT a slice budget; the lane enforces `RUN_BUDGET_S`).
- `PG-PR-03/04/06/10`: privileged ops ONLY the two named issuances; runtime + cost delta stated with sources; how the code becomes live = this rider's rebuild + recreate.

## Acceptance criteria

- **A1:** exactly ONE build + ONE recreate, both exit 0, lane socket only, zero denials; new container healthy, RestartCount 0.
- **A2:** served bundle == candidate build bytes; both removals IN the served bytes (served-grep proof); health green start/end; DB sha identical ×3; focused suite green with counts + derivation.
- **A3:** report `docs/worklogs/SG-210_report.md`; elapsed vs ≈400 s; constraints answered; FIRST/DURING/REMAINING; FIRST token `SG-210`.
- **A4:** notes-ref receipt on `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-210 | Report: docs/worklogs/SG-210_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`.
