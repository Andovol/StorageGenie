# SG-280 audit — deploy rider stopped in S0: the recovery image is gone

**Score 96/100; no flag. The stop was correct.** The live app was never stopped or migrated, so **no release is recorded**. The diff `b39629e..a8095c7` is `docs/worklogs/SG-280*` only. Read: the report, the rehearsal log, and the diff's file list. The scratch removal and the live counts are the report's claims; this audit cannot read the host. The tree here is clean and `origin/automation` holds the report commit.

## What holds

- **The live database matches the migration's expectation:** 95 objects against 95, zero differences, `candidate` text equal to `SG-279_rehearsal.log:47-60` (report, G2). This settles SG-279 audit I2.
- **The migration works on a copy of the real data:** only `candidate` changed, counts and row hash equal, `split` and `merged` accepted, an invalid state refused (`SG-280_rehearsal.log:21-27`).
- **The backup restores:** hash equal, checks clean (`:40`); a truncated copy is refused (`:48-50`).

## Findings

I1. **My packet deleted the recovery image.** G0 told the Coder to `docker tag` the old image id to a scratch tag and remove that tag. The tag succeeded in G0, showing `96a662414c23`; later in the same run the daemon answers `No such image` (`SG-280_rehearsal.log:44`). `SG-279`'s image proof had already moved `:latest` (the new image's `Created` is `2026-11-02T16:27:38Z`, inside SG-279's run), so `96a66241` probably had no other tag. `UNVERIFIED — my inference, and the Coder's:` removing the only tag removed the image. The alternative, a separate cleanup, would fit the same log, and a search of the `Makefile` for `prune`, `image rm` and `rmi` found none. **Attribution: packet.** I asked for a rights probe on a real object, against `PG-PR-01`'s intent of throwaway objects.

I2. **Live exposure is low but real.** The app is healthy on container `d972bc75`. `UNVERIFIED — my inference:` it keeps running because its own filesystem still exists; a restart of that container is untested without its image. `:latest` holds SG-279's code, which is the same as the live code apart from the new model constraint. So there is no exact way back to the old image until one is made.

I3. **The kill point moved, disclosed.** The packet asked for death right after `DROP TABLE candidate`; the run keys on the rename, and the result is `candidate_missing=False, tmp_present=True` (`:37`). `UNVERIFIED — my inference:` the drop sits in an open transaction that the death rolled back, so a real crash here leaves the old table plus a leftover temporary table. The worst imagined state did not occur, and the restore proof holds either way. The S2 rule on `_alembic_tmp_candidate` is what fires.

I4. **`--user` could not write under the rootless daemon**, disclosed: default-user files are host-owned and removable. The packet's premise was wrong, so the next rider drops it. No deduction.

I5. **Small report gaps:** the model comes from the task text rather than the process arguments, and the "owner must decide" section reads the recovery states oddly. Report-quality deduction only.

## Rating

Stopping is a success, and the Coder also ran the remaining checks and reported honestly. `slowest_waste`: none.

## The new decision, not asked because the owner has asked for a close

**Recorded in `STATE.md` as the first item for the next session.** A stop rule fired on a sensitive surface, so the work returns to the owner (`G-K3`). It is a 🟡 on the live host, so the two-phase review comes first (`AGENTS.md`).

**Recommended:** make the recovery image from the running container (`docker commit --pause=false d972bc75 storagegenie-backend:recovery-sg270`), prove it by comparing its export with the container's, then rerun SG-280 with the real-object tag probe removed and `--user` dropped. **Alternative:** rebuild from tag `release-2026-11-02-sg270`, which is not the same bytes. `UNVERIFIED:` the lane permits `docker commit`; a denial stops.

**Guard:** every future rider tags the image it serves, `storagegenie-backend:release-<slice>`, so a recovery image never hangs on `:latest`.
