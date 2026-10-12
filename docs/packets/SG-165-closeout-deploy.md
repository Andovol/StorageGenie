# SG-165 — Close-out deploy rider: serve the Palette pile (rebuild + one recreate + verify)

Autonomy: L2 (standing close-out directive: "Always do a live deploy before session close", owner directive 2026-09-28, G-O4 record — this rider IS that directive for the current work). Production restart + production writes authorized by that directive alone; anything beyond rebuild/recreate/verify is a STOP. `PB-1`–`PB-6` bind (`CODER.md` §14). Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0, `4c23869`); host echo expected 0.46.0 from /home/andrei/storagegenie-contract/VERSION (SG-164 echo) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: live SQLite** (`/data/db/storagegenie.db` — read-only probes; no migration: prove `alembic current` == head `sg114` before touching anything, else STOP).
**Restart: exactly one recreate of the production stack, nothing else.**

## Why this exists

SG-161..164 landed 7 Palette PRs' worth of frontend changes (ExpiryEntryForm guard, import-modal busy state, EvidenceGallery a11y + first test, CandidateCard restyle + tooltip, ChatPage form + theming) that sit on disk unserved — the running service still serves the pre-pile image. THIS slice rebuilds + recreates + verifies, nothing else. NO code changes — any diff outside `docs/worklogs` is a STOP. NO migration (none of SG-160..164 touched `models/`/`alembic/` — prove by empty diff on those paths, else STOP).

## G1 — rebuild the serving image

Rebuild so the bundle includes the landed frontend (the bundle is EXPECTED to differ from the running one — this rider exists because of that). Quote image ID before/after. A rebuild that changes no image ID while the bundle differs on disk is a finding (delivery question per PG-DP-01: ask whether the fixed code is even running before re-reading it).

## G2 — exactly one recreate + verify

Recreate the production stack EXACTLY once (a second recreate is a STOP). Then verify: health probe start+end with delta (`{{HEALTH_CMD}}` pattern — DB+storage proven, deltas quoted), served-bundle check (the merged surfaces present in what is served), request counts both directions with zero unexpected delta (SG-154 precedent: 28 counts delta 0), CORS preflight live. Full end-to-end sweep is WAIVED per PG-DP-02 (restart-gated: externally-driven tests would exercise the previous build) — the substitute coverage is the health/counts/preflight proof above plus the already-green targeted suites; browser-driven hits, if any, are reported and named, never run bare.

## Constraints

Scope ceiling: rebuild + one recreate + verify + `docs/worklogs/SG-165_*`. Permissive-only delivery change (PG-DP-01): add the new bundle, replace nothing else. $0 metered (no provider calls — a metered call is a STOP). Expected duration ~600s (lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, build 600s, one recreate 300s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; the ceiling forbids every product hunk, and no criterion needs one.

## Acceptance criteria

- A1: image rebuilt (IDs quoted) + exactly one recreate + health green with start/end delta + counts delta 0 + preflight live.
- A2: no migration ran and none was pending (alembic current == head quoted); `models/`+`alembic/` diff empty.
- A3: product diff for this slice is EMPTY (worklogs only); any product hunk is a STOP.
- A4: SG-165 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); production writes = exactly the rebuild + one recreate (restart), authorized by the standing close-out directive, with before/after image IDs quoted.

## Report

Echo `SG-165` as the first token. Destinations: `docs/worklogs/SG-165_report.md` + build/verify logs. Close with FIRST READ / DURING EXECUTION / REMAINING.
