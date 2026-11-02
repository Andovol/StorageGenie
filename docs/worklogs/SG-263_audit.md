# SG-263 audit — close-deploy rider for SG-262

**Score 92/100; no flag.** The serve itself is correct. The deduction is a cleanup error outside the rider's ceiling (I1). The diff `ef1eb0e..88a45b7` is `docs/worklogs/SG-263*` only; no product byte.

Cross-checked from the logs: all table counts in `SG-263_prestate.log` and `SG-263_g4_census.log` are the same (a separate diff by this audit; the only differences are rc lines); `SG-263_g2.log` shows `measured_changed_files=2`, `extra_files=0`, `served_tree_vs_worktree_diff_rc=0`, `js pre_vs_post_cmp_rc=1`. The engine's status reads `result=done`, inactive.

## Findings

I1. **The Coder deleted the whole untracked `output/` directory while cleaning its scratch, including the lane's own runtime directory `output/dispatch`.** It recreated the directory and kept the engine's two log files current with a hand-written loop copying from the running writers' file descriptors. It should have stopped and reported rather than improvising inside the engine's directory. Fully disclosed by the Coder (its I6). No product, database or container effect; the status reads inactive, so the loop's unit has ended. `UNVERIFIED — my inference`: anything else under `output/` from earlier runs is gone with it; the lane key opens no shell to check.

No `FLAG:SAFETY`: the deleted data was throwaway lane scratch, not production, and nothing was hidden. No `FLAG:TRUST`: the report is accurate and the evidence is committed.

I2. Cache-satisfied build, proved 100/100 against the worktree rather than assumed. **ACCEPTED.**

I3. The old bundle already held `No date`, so G3's string search in my packet could not fail alone. The Coder caught it and quoted the new ternary and the count moving from 2 to 3. Packet deduction (`PG-EV-05`). **Closed.**

I4. The worktree's `frontend/dist` is a stale local build and is not served. **ACCEPTED**, as in SG-259.

## Below-95 record

- **Failure class:** model execution, with a prompt gap.
- **Root cause:** the packet said "a writable temp directory", while SG-259's audit had already recorded that `/tmp` is denied on this lane. So scratch went beside the engine's directory, in `output/`, and the cleanup was too wide.
- **Exact correction:** no repair needed; the serve is sound and the lane ran to done.
- **Recurrence guard (lever):** every packet needing scratch names it: `output/<ID>-scratch/`, remove exactly that path, never `output/` itself, and damage to `output/dispatch` is a STOP. Rule recorded in `AGENTS.md`.
- **Owner impact:** elapsed about 4 minutes to the report's end against ≈450 s expected; cost unavailable beyond the slice's own $0 of provider spend.
