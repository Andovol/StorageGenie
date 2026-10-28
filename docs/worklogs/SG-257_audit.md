# SG-257 audit — 98 (SG-256's row-11 polish is live; the served bytes are exactly its delta)

**Verdict:** 98, no flag, nothing deducted. **Deduction attribution: empty.** One image build, one recreate, the served-byte proof, the changed bundle, the unchanged 29-table census and green health — all evidenced. The release record and tag are the Architect's next step.

## What was read

The rider report, every SG-257 log, the receipt on the notes ref, and the pre/post state and census. The scope diff `09d5289..0ddf94a` is twelve `docs/worklogs/SG-257*` files; **no product, config, schema, migration, dependency or test byte.**

## What landed

| Item | Evidence | Verdict |
|---|---|---|
| Socket first | `SG-257_g0.log`: the default path was tried and denied (recorded, not routed around); `DOCKER_CONFIG` + `DOCKER_HOST` then Server 29.9.2 / API 1.56, rc 0 | PASS |
| One build, one recreate | `SG-257_build.log` rc 0 (3 s, fully cache-satisfied; the image content predates the lane because SG-256's gate built it); `SG-257_deploy.log` rc 0 (1 s): `a831fbd0` → `40bee778`, image `e8c73735` → `b2c42abd`, same `Cmd`, RestartCount 0, running/healthy | PASS |
| No migration | `SG-257_prestate.log` / `SG-257_g4_census.log`: head `20261023_sg233_reminder` before and after | PASS |
| Served bytes are SG-256's | `SG-257_g2.log`: pre-serve image → worktree runtime diff is **exactly** `api/v1/plugins.py` + `plugins/expiry_tracker.py`; set comparison extra=0, missing=0; served tree equals worktree 100/100, rc 0 | PASS |
| Frontend bundle changed | `SG-257_g2.log`: JS `index-CWp6nYu6.js` `fe7dff6e…` 326217 B → `index-BRl7CaJb.js` `457010d8…` 327119 B (cmp rc 1); `index.html` changed because it references the new hashed JS; CSS byte-identical | PASS |
| The new behaviour is served | `SG-257_g3_served.log`, from the served image/bundle: route at line 242, call at 253; `clear_opened_date` at 531 and `_write_assertion(..., None, ...)` at 552-553; JS `/opened/clear` hit 1 and `Clear opened date` hit 1 | PASS |
| Census unchanged | `SG-257_g4_census.log`: 29 tables, 31 lines, `diff` rc 0; `provider_call=39`, `reminder=4` both sides; the production sqlite main file unchanged (765952 B) | PASS |
| Live app answers | `SG-257_g5_live.log`: health start, six post, six end and the final GET all 200 with the same body; `/`, `/expiry`, `/inbox`, `/planning` all 200; startup log clean (no traceback, no configuration error) | PASS |
| Honest limit | the live clear/edit write was **not** exercised (it would write the owner's data); the served code and bundle are the proof | PASS |
| Receipt | notes ref `refs/notes/storagegenie-coder-reports`, `Dispatch-ID: SG-257`, `Work-HEAD: d06e230`, settings line, contract echo `0.53.0` | PASS |

## Issues and dispositions

| ID | Issue | Status |
|---|---|---|
| I1 | The default docker path is denied; `DOCKER_CONFIG` + an explicit `DOCKER_HOST` are required. | NOT A DEFECT — environment, disclosed; the root-owned `~/.docker` is an engine-arc item |
| I2 | The image `b2c42abd` was created at 21:13:11 during SG-256's gate, so the rider's build was fully cache-satisfied. The rider proved the built image's runtime tree equals the worktree (100/100) and the running container's tree; `Created` is not the freshness proof, the tree is. | NOT A DEFECT — correctly reasoned and evidenced |
| I3 | `index.html` changed as well as the JS, because Vite content-hashes the JS filename it references; the packet allowed the index to be identical but did not require it. The CSS is byte-identical. | NOT A DEFECT — allowed and disclosed |
| I4 | The packet said "visible `Clear opened date` label"; in the bundle it is the accessible label (`aria-label`), with visible text `Clear`. The control is present and correctly named; the component tests address the accessible name. | NOT A DEFECT — packet wording, resolved |
| I5 | `reminder=4` (SG-251 recorded 1); the count moved over the intervening days, not during the rider. The pre/post census is identical and the DB main file is unchanged. | NOT A DEFECT — live data observation |
| I6 | The error scan's only hit is the daily pass's `errors=0`; the log has no traceback or configuration error. | NOT A DEFECT — same false positive as SG-251 I8 |
| I7 | The build exported a manifest-list digest; the container's `.Image` and the inspected image id are the same digest. | NOT A DEFECT |

Every `UNCLEAR` line is dispositioned above: `FIRST READ` the label wording (I4); `DURING EXECUTION` the cache-satisfied image's provenance (I2); `REMAINING` the root-owned `~/.docker`; no open product item.

## Rating row inputs

`guards_invoked`: PG-EV-01, PG-EV-02, PG-EV-03, PG-EV-05, PG-EV-07, PG-EV-08, PG-EV-10, PG-IC-01, PG-IC-07, PG-SC-12, PG-DP-01, PG-DP-04, PG-PR-01, PG-PR-02, PG-PR-03, PG-PR-04, PG-PR-06.
`remaining`: (1) the household-and-document half of roadmap row 11 remains and needs the owner's word; (2) W3, W4, W5 and row 14's deferred work need the owner's word; (3) the root-owned `~/.docker` remains an engine-arc item, so `DOCKER_CONFIG`/`DOCKER_HOST` stay required; no open product item for this slice.
`slowest_waste`: none — the session-start 110 s and the 95 s report composition were both used; no named phase's output went unused.
`escape`: empty.
