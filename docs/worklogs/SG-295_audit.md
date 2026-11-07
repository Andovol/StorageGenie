# SG-295 audit — the candidate-state migration is live

**Score 97/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high`, from the receipt's `Settings:` line. Diff `f9bfb30..fbc9736` is `docs/worklogs/SG-295_*` only; receipt on the notes ref, `published_head=yes`. Read: report, rehearsal log, receipt, the diff's file list. Host-side claims are the report's.

## What holds

- **Rehearsal on real data, app running** (`SG-295_rehearsal.log`): upgrade changes only `candidate`, counts and row hash equal, `split` and `merged` accepted and an invalid state refused; the interrupted run left `_alembic_tmp_candidate` beside `candidate` with the old revision and rc 99 (the S2 state, named exactly); the restore matched by hash; **the recovery image actually served** health and `/v1/households` (200, 200) on the restored file — the proof SG-280 could not give; the truncated copy was refused.
- **Live, in order:** S1 stop, no restart over 15 s; backup `data/db/SG-295-backup-20261107T214652Z.db` (sha256 `3aa4e1f5…`, retained) restored and proved; S2 one migration, rc 0, about 2 s; after it only `candidate` changed, its text equals SG-279's, 29 counts and the candidate row hash equal, no temporary table; S3 new container `e2a10bde…` on image `6b86f5e0…`, healthy.
- **Downtime 77.9 s** stop to healthy, 15 s of it the packet's own no-restart wait.
- **The app answers:** health six times, `/`, `/expiry`, `/inbox`, `/planning` 200; startup log clean, daily pass `reminders_created=0`; census unchanged.
- **Tags:** `release-sg295` created on the new image; `recovery-sg270` still present. Nothing removed.

## Findings

I1. **Two read-only verifications failed on WAL files in read-only mounts** and were repeated on byte-identical copies, both disclosed with hashes. Correct handling; the packet did not anticipate it. **Attribution: packet**, small.

I2. **Why `candidate` was still present after the kill was not investigated.** Same as SG-280 I3; the drop is inside a transaction the kill rolls back. The restore proof holds either way.

I3. **Rollback now means `recovery-sg270`,** the pre-SG-279 code, with the retained backup. Recorded in the release.

## Model note

Third Haiku slice, first with a live write: **kept the state machine exactly, disclosed two failed read attempts and why, ran far under the expected time.** Same habit as before: the identity line says the effort is unknown to it, which is right.

## Rating

`slowest_waste`: 15 s no-restart wait (kept: it is the S1 proof). Next: SG-271 on Muse (rotation).
