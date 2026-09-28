---
status: proposed
applied: NO
from: StorageGenie
raised: 2026-09-28
target: PACKET.md guards (EV family, trigger-loaded)
---

## Proposed rule
A slice landing test-only changes into a tree whose build typechecks must prove the typecheck exit-0 on the merged tree; test-runner green is not build proof.

## Evidence
StorageGenie, 2026-09-28, contract 0.40.0, one incident chain (count: one defect, honest single-instance filing). SG-135 merged 11 audited outside PRs including `WebAlternates.test.tsx` (+93/-0) whose object literals omit required `WebAlternate` fields (`source_type`/`source_url`/`retrieved_at`, `string | null`). Vitest file-green (4/4) and full frontend suite green (243/243) — neither typechecks. SG-137 confirmed the 3× TS2739 as base-resident but out of its ceiling. SG-140 close-out deploy rider then failed `docker compose build backend` at `tsc && vite build` (exit 2, 8s), blocking the session's standing close-out deploy; production stayed healthy on the pre-queue image. SG-141 repaired the 3 literals (explicit `null`) with committed fail-pre/post; SG-140 re-ride served. Cost: one blocked deploy + one extra fix slice + one re-ride (~all $0, time only).

## Generalisation test
1. Different stack? Yes — any typed tree with a test runner that does not typecheck (React+tsc, Python+mypy-gated builds, Go vet-gated CI): test-green decorrelates from build-green the same way.
2. Stated without naming? As above — no host, repo, model, service, database or domain named.
Unsure half, stated plainly: whether the gate belongs on every merge slice or only on slices touching typechecked trees (likely the latter — narrowing candidate for the desk).

## Cost
Lands in PACKET.md guards (EV family): trigger-loaded, read once per packet-writing activity — not always-loaded. Replaces nothing: checked PACKET.md EV guards (suite/gate rules cover test runs and seen-to-fail gates, none names the typecheck on merge); replaces no existing sentence. Where I looked: PACKET.md §§EV/SC/IC/DP + PG index, contract 0.40.0.
