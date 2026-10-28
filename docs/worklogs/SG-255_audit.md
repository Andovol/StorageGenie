# SG-255 audit — 97 (W1's image half proven on the repaired lane runtime; A rejected, D stands)

**Verdict:** 97, no flag. **Deduction attribution: packet** — one packet-internal inconsistency (`A9` vs `G5`/`A7`) that the Coder flagged and resolved correctly; nothing deducted from the Coder's execution. **W1 is complete:** the two library-dependent tests now live in the prover image, the host suite is green without them, and `make backend-test` gates the whole route.

## What was read

The full diff `e739c20..43a95d7` (11 evidence files, +2512), the report, every SG-255 log, the receipt note on the notes ref, and the base count in `docs/worklogs/SG-250_g7_suite.log:114`. The receipt was read from `refs/notes/storagegenie-coder-reports` at `43a95d7` and carries `Dispatch-ID: SG-255`, `Work-HEAD: 2e2fef9`, the contract echo `0.53.0`, and the settings line.

## What landed

| Item | Evidence | Verdict |
|---|---|---|
| Docker runtime healthy before any claim | `SG-255_g0_docker_preflight.log`: Server 29.9.2 / API 1.56, busybox `rc=0` in 0.665 s, socket at the expected lane path, health 200 start and end | PASS |
| Host guard FAIL under `SG_IMAGE_PROOF=1` | `SG-255_g1_guard_fail_host.log`: `2 failed, 6 deselected in 1.33s`, messages naming zbar and tesseract+font | PASS |
| Image proof PASS | `SG-255_g2_image_proof.log`: `2 passed, 6 deselected in 3.22s`, rc 0 — no skip token | PASS |
| Prover image is the worktree | `SG-255_g2_image_identity.log`: both sha256 pairs equal, `cmp=identical`; build fully cache-satisfied (8 s); `Created` unchanged from 2026-10-26 | PASS |
| Gate PASS twice in a row | `SG-255_g3_gate_pass_1.log` / `_2.log`: rc 0 both; host `743 passed, 2 deselected, 0 failed` (64.34 s / 61.08 s), image proof `2 passed` both | PASS |
| Wrong-image control fails for the image's own reason | `SG-255_g4_wrong_image_proof.log` / `_gate.log`: rc 2 both; `exec: "python": executable file not found in $PATH`, make `Error 127` — not rc 125 and not the SG-252 bootstrap-shim error | PASS |
| Whole-suite image trial measured | `SG-255_g5_whole_suite_image.log`: rc 1, 72.56 s, `10 failed, 722 passed, 13 errors`; failures enumerated; root cause visible in the traceback (`/backend/alembic` does not exist in the image) | PASS |
| Worktree mount variant | `SG-255_g5_mount_variant.log`: rc 0, `2 passed`, in-container `/app/tests/test_signals.py` sha256 equals the worktree | PASS |
| A vs D | D stands: the whole suite reds and would need repo-root artifacts the image does not carry; the SG-243 rule's green + comparable-duration + no-extra-mounts conditions are not met | PASS |
| Scope | diff is only `docs/worklogs/SG-255*`; no Makefile, app, Dockerfile, compose, lockfile, dependency, migration, database, host package, sudo, service, provider or running-container change | PASS |
| Receipt | notes ref `refs/notes/storagegenie-coder-reports`, `Dispatch-ID: SG-255`, `Report:`, `Work-HEAD: 2e2fef9`, contract echo 0.53.0, `Verification: PASS`, settings line | PASS |

## Issues and dispositions

| ID | Issue | Status |
|---|---|---|
| I1 | **Packet defect (mine): `A9` said `the whole-suite trial red` must not be observed, while `G5`/`A7` select D precisely when it reds.** The Coder flagged the contradiction (`I5`) and read `A9` as the vacuity guard for the PASS claims, which is the only coherent reading. No Coder deduction; the packet's wording is the fault. | RESOLVED — recorded; packet attribution |
| I2 | The image Id (manifest-list digest) changes on each cache-satisfied build re-export while the config digest and layers stay fixed; `Created` is unchanged. Freshness is proved by both file sha256 pairs and `cmp`, not by the digest or timestamp. | NOT A DEFECT — disclosed and correctly reasoned |
| I3 | `0 skipped` is an absence, not a printed token: pytest prints `2 passed, 6 deselected` when nothing skips. The host guard log proves both marked tests ran and failed rather than skipped. | NOT A DEFECT |
| I4 | The whole-suite red's root cause is the image layout (tests derive `parents[2]` from `/app/tests` and expect `/backend/alembic`); the Coder inferred it from tracebacks rather than a further run. The trial's job is the measurement, and it is recorded; A is rejected on that measurement. | NOT A DEFECT — the finding A's rejection rests on |
| I5 | `DOCKER_CONFIG` was set before the first call and `DOCKER_HOST` explicitly to the lane socket; the socket path matched. CLI/environment state only. | NOT A DEFECT — disclosed |
| I6 | No app deploy owed: no product byte changed, so the standing "deploy every app-changing slice" rule does not fire. Health 200 before and after; the running container was never recreated. | CLOSED — no deploy |

Every `UNCLEAR` line is dispositioned above: `FIRST READ` the base and candidate counts matched the packet; `DURING EXECUTION` the digest churn (I2), the image-layout cause (I4), the `A9`/`G5` tension (I1); `REMAINING` A rejected, D stands; the root-owned `~/.docker` remains an engine-arc item, so `DOCKER_CONFIG` stays required.

## Below-95 investigation (`RATING_ISSUE.md`)

Not loaded: score 97, no flag. The one deduction attribution is the packet's `A9` wording; the Coder's execution was complete, honest and evidenced.

## Rating row inputs

`guards_invoked`: PG-EV-01, PG-EV-02, PG-EV-03, PG-EV-05, PG-EV-09, PG-IC-01, PG-IC-07, PG-IC-08, PG-IC-09, PG-SC-10, PG-SC-12, PG-DP-04, PG-PR-03, PG-PR-04, PG-PR-06.
`remaining`: (1) A rejected, D stands — no further slice; (2) the root-owned `~/.docker` is still pending in the engine arc, so `DOCKER_CONFIG` remains required — host-side note; (3) the whole-suite image layout (`/backend` vs `/app`) is the recorded cause of the trial red — no slice, A is rejected; (4) W1-IMG closes in the backlog.
`slowest_waste`: none — every long phase (three host suites, the whole-suite trial) was used by this audit.
`escape`: empty.
