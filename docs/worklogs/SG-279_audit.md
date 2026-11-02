# SG-279 audit — widen the candidate state constraint, published by SG-281

**SG-279: 90/100, no flag. SG-281: 97/100, no flag.** The build is sound; the slice ended without publishing it. Read: the diff `16fcae5..e016c02`, the migration, the model hunk, the split and merge test bodies, the rehearsal log, the fail and pass logs, and both reports.

## What holds

- **Scope:** ten files, all inside the ceiling; zero live database, host, container or deploy bytes.
- **Failure half is real:** `SG-279_fail_routes.log:188` and `:508` read `CHECK constraint failed: ck_candidate_state`. Pass log: `2 passed`.
- **Tests are not placebos:** both drive the real route on an Alembic-built file with foreign keys on, close the seed session first, and read back through a new session (`test_sg279_candidate_state.py:198-254`).
- **Rehearsal:** values, indexes, foreign keys, other objects, counts and FTS search unchanged; the deliberate alterations were caught (`SG-279_rehearsal.log:103-104`); both refusals leave everything unchanged (`:108`, `:110`).
- **Schema text diff:** the accepted set, plus quoting the table name and swapping the two foreign key clauses (`:80-94`). Read and accepted as non-semantic.

## Findings

I1. **The slice did not publish its work.** No `git push origin automation` was attempted, and `CO-48`'s *"Confirm the remote head moved"* was not done (`SG-281_report.md`, G2). It published a receipt naming a commit GitHub did not have, and `result=done` showed nothing wrong. **Attribution: mixed.** `PACKET.md` §4 requires the literal branch push in the packet, and the packet omitted it, as did SG-275's, whose Coder pushed anyway. `CODER.md` step 9 still requires it. **Corrected by SG-281.** No flag: nothing false was stated about the push, and the evidence existed on the host, but a slice with no remote work cannot be 95+.

I2. **New, for the rider: the migration does not read the live table.** `copy_from=_candidate_table(OLD_STATES)` rebuilds from a hand-written copy of `20260908_sg014_candidate.py` (`20261102_sg279_candidate_state.py:28-72`). If the live `candidate` differs from that, for example an extra column, the rebuild would silently keep the hand-written shape. The rehearsal cannot see this, because its database came from these same migrations. `UNVERIFIED — my inference that the live table matches:` SG-276 quoted only its CHECK. **Destination: SG-280 compares the live `sqlite_master` text of `candidate` with the expected text before anything changes; any difference stops.**

I3. **Alembic runs non-transactionally here** (`SG-279_rehearsal.log:2`), so an interrupted migration can leave a half-done rebuild. D16's "during it, restore the backup" already covers this. **Destination: SG-280 also treats a leftover `_alembic_tmp_candidate` as that state.**

I4. **Two report inaccuracies, neither material.** It gives elapsed as about 560 s while the engine recorded `elapsed=818s`, a gap the report never explains. It also explains its count as *"777 passed + 5 new + 4 drift from head move"*; 781 + 5 is the plainer reading, and `PACKET.md` forbids carrying a count over. Counted as a report-quality deduction.

I5. **The denied `cat` of the host's `CODER.md` did no harm.** It was a read, and the Coder went on (`SG-281_report.md`, G2 item 1). Its contract echo of `0.56.0` matches SG-281's, whose model line came from the launcher file. `UNVERIFIED — my inference:` the Coder has the contract text in its prompt. **Closed.**

I6. **The engine cannot show this fault.** `--status` read `result=done` with `moved=yes` counting local commits. **Destination: this session's END report to the Launcher desk (issue 62).**

## Below-95 record for SG-279

- **Failure class:** protocol, shared by prompt gap and model execution.
- **Root cause:** the packet's Report section listed only the notes commands, and the Coder followed it instead of `CODER.md` step 9.
- **Exact correction:** SG-281 published both commits unchanged in content.
- **Recurrence guard and lever:** every build and rider packet carries the literal `git push origin automation`, then `git rev-parse HEAD origin/automation` with equal hashes as a criterion. Written into `STATE.md`.
- **Owner impact:** one debug run and one 25 s recovery slice; cost `unavailable`.

## SG-281

Did exactly what was asked in 25 s: right quarantine ref, two clean picks, 4 tests passed, G2 answered from the logs with what it searched. The health probe was skipped because the packet authorised only the test file, so that gap is the packet's. Content checked here: `16fcae5..e016c02` holds SG-279's ten files.
