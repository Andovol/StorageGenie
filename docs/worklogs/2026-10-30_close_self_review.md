# 2026-10-30 — close self-review (D6/D7 phase boundary)

**What I believed that turned out false.**
- The SG-258 packet's G3.3 premise: that the engine already rendered a null accepted expiry as `dateless`. At the base it said `unparseable`; the read path (`backend/app/services/expiry_engine.py`) was therefore in the change, and the packet's scope ceiling missed it. The Coder disclosed the coupled engine + test changes (`CO-09`/`CO-38`); the audit accepted them as a necessary dependent but deducted for the ceiling defect (`docs/worklogs/SG-258_audit.md` finding 1; score 93).
- The `ReviewPage` form: adding optional props made `tsc` pass, but the caller passes no data, so the review-workspace form renders the default `needs_evidence` and an empty date. The SG-258 report's I3 caught the prop, not the caller. The D7 E2 hides the form instead.
- The reverse-move task: `classify_asset`'s move to Non-perishable writes the null accepted expiry but does not resolve the open `expiry.manual_entry` task; the clear and the manual entry both 422 on Non-perishable. The D7 F1-scoped resolves the date-prompt tasks and reports the ids.
- The `accepted`-with-no-date copy: the form shows `accepted` after a clear; the engine says `dateless`. The D7 G2 shows "No date."
- The SG-258 gate reruns: the coupled test and the `ReviewPage` prop caused two avoidable full-gate reruns (~140 s); the `slowest_waste` in the SG-258 rating row.
- The SG-259 evidence scripts: the JS `cmp` lost its `rc` to a `$?` overwrite by two `$(basename)` expansions; the census extraction mis-measured. Corrected and disclosed; the SG-259 rating row's lever.
- The SG-264 Phase A could not resolve the BASE commit (the read-only lane exposes no git) and could not read `STATE.md` (tool policy); it still delivered the four picks from the context pack and the named files. The review's limitation is recorded in its report.

**What the next session must not re-derive from the wrong evidence.**
- The live app is container `10f7fc58` from image `d620e39d`; the SG-258/259 release is `docs/releases/2026-10-30-sg258.md`, tag `release-2026-10-30-sg258`.
- The D7 stage is E2 / F1-scoped / G2 / H1; the three findings are in the SG-258 audit and the SG-264/265 reports; the review ledger has the dispositions.
- The next slice is the D7 work slice + its own rider; the work slice is packet-first, with the same `PG-SC-02`/`PG-IC-09` discipline (the read path and the coupled test are in the ceiling this time).
