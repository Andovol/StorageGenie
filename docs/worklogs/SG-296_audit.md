# SG-296 audit — SG-271 is live

**Score 96/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high`, from the receipt's `Settings:` line. Two runs: run 1 stopped correctly in S0 on a packet defect; run 2 served. Diff `d205f9a..97701ab` is `docs/worklogs/SG-296_*` only; receipt on the notes ref, `published_head=yes`; `HEAD` = `origin/automation` = `97701ab` (checked here after pull). Read: report (both runs), evidence file, receipt, the diff's file list. Host-side claims are the report's.

## What holds

- **Pre-state matched** (container `e2a10bde`, image `6b86f5e0`, head `20261102_sg279_candidate_state`); rollback override written and resolved to `release-sg295` before any change.
- **Runtime diff exactly SG-271's five app files plus the eval baseline**; served tree equals the worktree; JS changed, CSS identical.
- **No migration**, head unchanged; one build, one recreate, healthy in ~12 s, restart count 0; no rollback needed.
- **The new behaviour is in the served artifact**, read from the container's own files: `requires_date_task`, `committed_asset_id`, `dateless_count`, and the five UI strings in the served bundle.
- **App answers:** health six times, four shell routes 200, expiry status 200 with `summary.dateless`; startup clean; census 29 tables / 418 rows, no table moved.
- **Tags:** `release-sg296` created; `release-sg295`, `recovery-sg270` untouched.

## Findings

I1. **Run 1 stopped on my packet.** It demanded a read of the contract folder, which this lane denies — known since SG-295 (`STATE.md` Owed) and stated in SG-295's packet; I copied SG-279's older wording. Haiku stopped in S0 exactly as `PB-2` requires. **Attribution: packet.** Guard: a packet's contract line is taken from the last rider packet, not an older build packet (`PG-IC-09`).

I2. **The contract version line was not echoed** — the report says recorded `0.58.0` and that the folder was not opened, while the retry packet asked it to echo its own contract's version line. Small. **Attribution: coder.** No action; the host contract version stays owed with the lane's missing files (`STATE.md`).

I3. **`latest` moved** with the compose build, as every build does. Disclosed. No action.

I4. **One bash call refused with no reason**; the Coder did not retry the probe and re-ran only cleanup. Correct.

## Model note

Fourth Haiku slice: **stopped at the first sign on a denial, then served cleanly in ~150 s**, under the 450 s estimate. Same report gap as before: effort not stated.

## Rating

`slowest_waste`: none. Next: SG-272 on Muse, fix-first I1 and I2 from SG-271's audit.
