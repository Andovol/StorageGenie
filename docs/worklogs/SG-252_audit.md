# SG-252 audit — 92 (BLOCKED by the lane Docker runtime; the code is complete, the image half unexecuted)

**Verdict:** 92, no flag. Terminal class 3 (blocked before publication of the image half). **Deduction attribution: mixed** — environment for the lane's containerd shim failure, packet for the wrong base count. The host half and the image's file identity are proven; the image proof's PASS, the gate's PASS and the whole-suite trial did not run.

## What was read

The full diff `bdb5733..2d351a1` (three product files, +50/−8), the report, every SG-252 evidence log, the receipt note, and the pre-existing SG-238/SG-250 evidence the report cites. The base count was cross-checked against `docs/worklogs/SG-250_g7_suite.log:114`.

## What landed

| Item | Evidence | Verdict |
|---|---|---|
| One marker, registered, selecting exactly the two library-dependent tests | `SG-252_a1_marker_lint.log` (2/8 collected) | PASS |
| Exact capability guards; skip on a host, **fail** under `SG_IMAGE_PROOF=1` | `SG-252_g1_host_guard_fail.log` (2 failed: zbar; tesseract+font); `SG-252_g1_host_skip.log` (2 skipped) | PASS |
| Pure-Python EAN coverage split out and green on the host | `SG-252_g5_new_test.log` (1 passed); `SG-252_g5_host_suite.log` (743 passed, 2 deselected, 0 failed) | PASS |
| `make backend-test` = host suite, then the image proof as the gating second line | the Makefile diff; `SG-252_g3_gate_fail_combined.log` shows the host suite green then the image run failing the target | PASS (structure) |
| Prover image built from the worktree, dedicated tag, files byte-equal | `SG-252_a4_image_files.log`: image Id `87fc25d9…`, both sha256 pairs equal, `cmp` rc=0 | PASS |
| Image proof PASS, gate PASS, whole-suite trial, mount trial | none | **FAIL — blocked** |
| Scope | `SG-252_a7_scope_work.log`: only the three product files + SG-252 evidence; no app/Dockerfile/compose/lockfile/migration/database/host/provider change | PASS |
| Receipt | notes ref `refs/notes/storagegenie-coder-reports`, `Dispatch-ID: SG-252`, `Report:`, `Work-HEAD: 2d351a1`, contract echo 0.53.0, `Verification: FAIL` with the reason | PASS |

## Issues and dispositions

| ID | Issue | Status |
|---|---|---|
| I1 | **The lane Docker runtime cannot start any container.** `docker run` on busybox, the prover image, `--runtime runc` and `--platform linux/amd64` all return rc=125: `failed to start shim: io.containerd.runc.v2: bootstrap parameters do not match command-line arguments … if you upgraded containerd, you may need to restart the daemon`. The build works; the running app is healthy (health 200). A daemon restart is outside the packet and is a host action. | **NEEDS DECISION** — owner; second opinion running |
| I2 | Packet defect: the base count was written as “2 failed / 740 passed”; SG-250's own log says **2 failed / 742 passed**. The Coder corrected it and did not force 741. | RESOLVED — recorded; packet attribution |
| I3 | The Makefile takes `PROVER_IMAGE` for the run image only; the build always tags the prover. The wrong-image control therefore failed for I1's runtime reason, not for the wrong image. The Coder disclosed it. | OPEN — folded into SG-253 (re-run the control on a healthy runtime) |
| I4 | The host `make backend-test` needs the backend venv on `PATH`; the Coder supplied it (`I7`). The pre-existing target had the same `python` assumption. | NOT A DEFECT — no regression |
| I5 | The local contract clone on the server has no `contract-v0.53.0` tag (tags stop at 0.33.0); the version chain itself is 0.53.0 on all four links. | NOTED — host-side clone fact, not project work |
| I6 | A and D: the trial could not start, so A is not established; D remains the implemented route, with its image half unproven. | OPEN — SG-253 |

Every `UNCLEAR` line is dispositioned above: `FIRST READ` none; `DURING EXECUTION` the daemon mismatch (I1) and the `PROVER_IMAGE` reading (I3); `REMAINING` the image proof, gate PASS and trials (I1 → SG-253) and the contract tag gap (I5, noted).

## Below-95 investigation (`RATING_ISSUE.md`)

- **Failure class:** environment (primary); packet (secondary).
- **Root cause:** the host's containerd runtime was upgraded under a daemon that was not restarted, so every new task fails at shim bootstrap. The packet's base count was copied from an older report instead of the latest suite log.
- **Exact correction:** restart the project's Docker/containerd runtime under owner approval, then run SG-253 to execute the image proof, the gate PASS twice, the wrong-image control and the whole-suite/mount trial. Read the base count from `SG-250_g7_suite.log` (2 failed / 742 passed).
- **Recurrence guard (one lever):** **every packet that depends on the lane's Docker runtime opens its Docker goal with a trivial `docker run --rm busybox true` and stops as BLOCKED if it fails — before any build, proof or trial claim.** This would have cost one second and turned I1 into the first line of the report instead of the last goal.
- **Owner impact:** elapsed 468 s of the ≈500 s expectation; spend $0. No host package, database, container or provider action.

## Rating row inputs

`guards_invoked`: PG-EV-01, PG-EV-02, PG-EV-03, PG-EV-05, PG-EV-09, PG-IC-01, PG-IC-07, PG-IC-08, PG-IC-09, PG-SC-10, PG-SC-12, PG-DP-04, PG-PR-03, PG-PR-04, PG-PR-06.
`remaining`: (1) the image proof + gate PASS + A-vs-D trial → **SG-253**, after the owner's restart decision; (2) the wrong-image control → SG-253; (3) the base-count correction → recorded, no code; (4) the server contract clone's tag gap → noted, host-side; (5) the whole-suite A-vs-D verdict → SG-253.
`slowest_waste`: none — the 67.67 s host suite and 42 s build outputs were both used by this audit.
`escape`: empty.
