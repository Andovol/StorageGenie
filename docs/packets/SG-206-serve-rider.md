# SG-206 — serve rider: live-deploy the SG-205 dark focus-ring fix (D-5 re-serve due)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none (SQLite read-only verification — sha pre/post/recreate/tests byte-identical, no writes). Restart: ONE `docker compose build backend` + ONE `docker compose up -d --no-deps backend` on the lane socket** (`DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-206/docker.sock`; default socket never touched).
**Autonomy: L2.** Authority: standing 2026-09-28 close-deploy directive (every product delta ships before close) + D-5 conditional (re-serve due when new product commits land — SG-205's `tokens.css` change is exactly that). One retry max, root-cause only. Precedent shape: SG-202 (rated 97), SG-197, SG-193.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

SG-205 (rated 98) changed product bytes (`frontend/src/theme/tokens.css` ONLY: two outline declarations `--primary` → `--link`) that are not yet live: `live==tree` held through the SG-202 serve, and the SG-205 work commits are the first product delta since. D-5 fires: serve now or the close ships silently stale.

## Handed-over facts (expected — re-verify on target, `PB-1`)

- Product delta since the SG-202 serve: SG-205's tokens.css change ONLY (expected `git log` product-surface check; docs-only otherwise). Served bundle must flip CSS `e1e5f63…` → `c3b58cda…` (expected shas from SG-205 evidence; re-derive, never assume); JS bundle expected byte-identical (`626d1038` — SG-205 finding).
- SG-205 acceptance evidence (expected): dark ring `7.4784`/`4.2589` ≥3:1, light `9.8813`/`9.4611` unchanged, suite 30 files/298 pass. This rider does NOT re-prove contrast — it proves the SERVED bytes are the audited bytes.
- Lane: `RUN_BUDGET_S=2100` (read `/etc/dispatch/storagegenie.conf` read-only at execution).

## G1 — rebuild + recreate + prove the served bytes

- FIRST READ the prestate (container id/image/bundle shas, health, DB sha, alembic head, markers expected absent-or-prior), then exactly ONE build + ONE recreate (named units above, lane socket only), then the poststate. Zero denials tolerated; any denial STOPS per `PB-2`.
- Prove: health green start/end + N post-recreate GETs all 200; served index/CSS shas == the candidate build (cross-check image sha vs build manifest as SG-202 did); SG-205 ring tint present in the SERVED CSS bytes (grep the served bundle for the `.focus-ring` rule — `PG-SC-12`: the proof runs against the real thing, not the build log); DB sha byte-identical pre/post/post-tests, 28 tables, alembic head unchanged; no migration, no slice-caused row change.

## G2 — focused tests + report

- Focused suite for the touched surface (expected: the SG-202 set — 12 files incl. the four focus-ring-asserting test files `CandidateCard`/`EvidenceGallery`/`HouseholdSelector`/`theme-adoption`; Coder confirms the set covers the changed file's consumers and reports any delta). Full suite NOT re-run (SG-205 ran it green on this exact tree 399 s earlier — stated, not skipped silently; `D443`).
- Report `docs/worklogs/SG-206_report.md`: FIRST READ / DURING EXECUTION / REMAINING; elapsed vs ≈400 s (Architect record, `G-A9` uncalibrated; derived from SG-202's 379 s same shape); constraints answered; FIRST token `SG-206`.

## Constraints

- **Scope ceiling:** zero product/config/test/lockfile/schema/migration bytes (rider only); evidence ONLY under `docs/worklogs/SG-206_*`. Reads: lane only; no production or evidence-store writes (DB read-probes only); no secret in any log. `PB-3`: an empty poststate (no container id, no bundle sha) is a FAIL.
- **Out of scope (stated):** Option C/D; Q1/Q3 slices (SG-207/208 drafted, undispatched); auth-live; native zoom/touch.
- Hang bounds: build 600 s; recreate 120 s; GETs 120 s; suite per its own bound; idle kill 900 s never approached. Simplicity: one rebuild + one recreate + proof, no new machinery.
- `PG-PR-03/04/06/10`: privileged ops ONLY the two named issuances; state runtime + cost delta (expected: ~15 s build + ~1 s recreate per SG-202 — measure, never assume); how the code becomes live = this rider's rebuild; interim = the SG-202 bytes until recreate.

## Acceptance criteria

- **A1:** exactly ONE build + ONE recreate, both exit 0, lane socket only, zero denials; new container healthy, RestartCount 0.
- **A2:** served CSS == candidate `c3b58cda…` with the `.focus-ring{...hsl(var(--link))...}` rule IN the served bytes; JS bundle unchanged; health green start/end; DB sha identical ×3; focused suite green with counts.
- **A3:** report + elapsed vs ≈400 s + constraints answered + FIRST/DURING/REMAINING; FIRST token `SG-206`.
- **A4:** notes-ref receipt on `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-206 | Report: docs/worklogs/SG-206_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10. Stop follows `PB-6`.
