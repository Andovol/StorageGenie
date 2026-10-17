# SG-214 — serve rider: live-deploy the SG-212 width-adaptive density delta (D-5 re-serve due)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none (SQLite read-only verification — sha pre/post/recreate/tests byte-identical, no writes). Restart: ONE `docker compose build backend` + ONE `docker compose up -d --no-deps backend` on the lane socket** (`DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-214/docker.sock`; default socket never touched).
**Autonomy: L3** (approved queue; checkpoints only on `G-K2`/assumption-change/stage end). Authority: standing 2026-09-28 close-deploy directive + D-5 conditional (re-serve due — SG-212 rated 98 with SG-212 unserved). Precedent shape: SG-210 (rated 98), SG-206, SG-202.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

SG-212 (content-fit density default, CatalogPage + catalog.test) is rated and committed but NOT live: production still serves the SG-208 bundle (SG-210). D-5 fires: serve now.

## Handed-over facts (expected — re-verify on target, `PB-1`)

- Product delta since the SG-210 serve (`4952c0a`): SG-212 ONLY (`frontend/src/routes/CatalogPage.tsx`, `frontend/src/components/catalog/catalog.test.tsx`) — re-derive the product-surface diff, never assume.
- SG-212 acceptance evidence (expected): failpre 4 red + passpost 4 green, suite 29/297, tsc clean; served smoke wide1440 TABLE (content 1052, maxScrollLeft 0) + touch390 GRID (342, docOverflowX 0) + toggle both ways; 4 screenshots. This rider does NOT re-prove behaviour — it proves the SERVED bytes are the audited bytes.
- Catalog route is `/` (no `/catalog` route — SG-207 finding #3). Lane `RUN_BUDGET_S=2100` (read `/etc/dispatch/storagegenie.conf` read-only at execution).

## G1 — rebuild + recreate + prove the served bytes

- FIRST READ the prestate (container id/image/bundle shas, health, DB sha, alembic head, product delta vs served), then exactly ONE build + ONE recreate (named units, lane socket only), then the poststate. Zero denials tolerated; any denial STOPS per `PB-6`'s stop path via `PB-2`.
- Prove: health green start/end + N post-recreate GETs all 200; served index/JS/CSS shas == the candidate build (cross-check image sha vs build manifest as SG-206/210 did); the SG-212 rule IN the served bytes (`CATALOG_TABLE_FIT_MIN_PX` / `resolveInitialDensity` / `data-testid="catalog-content-column"` greps on the served bundle — `PG-SC-12`); served Catalog opens per the rule (lane smoke: wide smoke optional — the served-bytes proof is the gate; a one-shot wide/grid open is cheap confirmation, report either way); DB sha byte-identical pre/post/post-tests, 28 tables, alembic head unchanged; no migration, no slice-caused row change.
- Focused suite for the touched surface ONCE (derive the consumer set on target as SG-206/210 did — catalog density-init rows + absence rows; report the derivation, never bend to a list). Full suite NOT re-run (SG-212 ran 29/297 green on this exact tree hours earlier — stated, not skipped silently; `D443`).

## Constraints

- **Scope ceiling:** zero product/config/test/lockfile/schema/migration bytes (rider only); evidence ONLY under `docs/worklogs/SG-214_*`. Reads: lane only, DB mode=ro read-probes only. A `docker cp`-class read of the running container fs is permitted ONLY as the byte-proof read with the same disclosure SG-210 carried (no state change, no third build/recreate). No secret in any log or artifact. `PB-3`: an empty poststate (no container id, no bundle sha) is a FAIL.
- **Out of scope (stated):** Option C/D; AI stages (D-18(b) wall stands — SG-213 STOP; D-23 with the owner); server single-household enforcement (D-19 leave); auth-live; native zoom/touch.
- Hang bounds: build 600 s; recreate 120 s; GETs 120 s; suite per its bound; idle kill 900 s never approached. Expected duration ≈400 s (Architect record, `G-A9` uncalibrated; derived from SG-210's 510 s and SG-206's 407 s same shape — NOT a slice budget; the lane enforces `RUN_BUDGET_S`).
- `PG-PR-03/04/06/10`: privileged ops ONLY the two named issuances (+ the disclosed byte-proof read); runtime + cost delta stated with sources; how the code becomes live = this rider's rebuild + recreate.

## Acceptance criteria

- **A1:** exactly ONE build + ONE recreate, both exit 0, lane socket only, zero denials; new container healthy, RestartCount 0.
- **A2:** served bundle == candidate build bytes (cmp against the in-image bytes); the SG-212 rule markers IN the served bundle; health green start/end; DB sha identical ×3; focused suite green with counts + derivation.
- **A3:** report `docs/worklogs/SG-214_report.md`; elapsed vs ≈400 s; constraints answered; FIRST/DURING/REMAINING; FIRST token `SG-214`.
- **A4:** notes-ref receipt on `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-214 | Report: docs/worklogs/SG-214_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`.
