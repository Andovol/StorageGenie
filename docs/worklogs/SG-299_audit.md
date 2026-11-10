# SG-299 audit — SG-272 is live; run 1 stopped correctly on my too-narrow file list

**Score 96/100; no flag** (run 2). Model `opencode-go/claude-haiku-5-5`, effort `high`, from the receipt's `Settings:` line. Run 2 report commit `0cfe1b3`, `published_head=yes`. **Elapsed:** run 1 ≈110 s (its stamps); run 2 128 s by its stamps (≈250 s by the trigger file, 20:32:22Z → 20:36:32Z, which includes engine start and publish) against ≈300 s expected. Read: the whole run 2 report, the census after.

## What holds

- **Run 1 stopped in S0 exactly as the packet said**, on files outside my list, and did not widen the list on its own authority. Live app untouched, census identical.
- **Run 2:** one build, one recreate, S1 healthy in ~15 s, no restart; runtime diff = the derived 10 files exactly; served tree equals the worktree for tracked files; G2 strings in the served Python and JS; health ×6 and routes 200; census identical (29 tables, 418 rows); `release-sg299` created, no other tag moved but `latest` (compose build, by design, reported). Phase stamps present.

## Findings

I1. **Packet defect (run 1):** the expected runtime set covered `backend/app` only; the Dockerfile copies all of `backend/`. **Attribution: packet.** Rider packets now derive the set over `backend/` minus `alembic` (`STATE.md`).

I2. **The report says the publish hashes are "quoted below" and does not quote them** (written before the push). The engine's `published_head=yes` and my fetch (`HEAD == origin/automation` at `0cfe1b3`) cover it. Minor, coder.

I3. **Run 1's full-tree hash dumps (≈830 KB) are committed.** Evidence volume; the retry asked for a small diff and got it. No action.

## Model note

Haiku's sixth rotated slice: a literal, correct S0 stop and a clean serve; timings captured once the packet required stamps.

`slowest_waste`: none.
