SG-290 | model opencode-go/muse-spark-1.3-contributor effort=xhigh | wdir /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation -> a90102b59affa697c20f58a36342ea400004964e | WORK_HEAD a90102b59affa697c20f58a36342ea400004964e

Model and effort from the rotation slot (STATE.md: SG-290 rerun on Muse 1.3 Contributor, xhigh); the trigger text itself was not visible in this session. BASE commit is `git rev-parse origin/automation` at slice start; HEAD was identical and clean (only untracked `output/` and the new worklog file, both expected). WORK_HEAD is the pre-report tip; this slice changes no product byte, so BASE==HEAD==WORK_HEAD pre-report. The report commit hash never appears in its own report.

Contract chain: recorded `0.58.0` (`AGENTS.md:4`). Published `contract-v0.58.0` and the host's contract versions: UNVERIFIED — this lane denies reading `/home/andrei/storagegenie-contract/*` and I did not run the checker nor route around the denial (same posture as SG-286). This is a finding, not a pass.

# SG-290 report — recovery image: STOPPED in G2, commit refused by the daemon

Outcome: no recovery tag and no recovery image were created. The live app was not touched: same container, same start time, restart count 0, health ok at start, during and end, and the `docker diff` set unchanged at 208 entries. G2 stopped at step 4: `docker commit` failed twice with the same daemon `NotFound` on one content digest (evidence `docs/worklogs/SG-290_commit.log`). Per the packet, any result other than the expected one stops the work.

## G0 — socket, pre-state, changing nothing

- Socket: `DOCKER_CONFIG=output/SG-290-scratch/docker-config`, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-290/docker.sock`; `docker version` shows Client 29.9.2 plus a Server section (Engine 29.9.2, containerd v2.4.2, runc 1.5.2, rootless). Scratch stayed in `output/SG-290-scratch/`, removed by exact path at the end; `output/` itself and `output/dispatch` never touched.
- Health start: `{"status":"ok","db":"ok","storage":"ok"}`.
- Container `d972bc75` pre-state, as expected: id `d972bc752fa038be2552322120af1e0d56a35321cc47d61fc4677b476a91332f`, `.Image` `sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22`, `.Config.Image` `storagegenie-backend`, `running`, started `2026-11-02T15:52:53.194514305Z` (before 2026-11-02T18:03Z), restart count 0, health `healthy` (FailingStreak 0).
- Mounts, as expected: `/data/db` is a bind (`/home/andrei/StorageGenie/data/db`, rw); `/data/storage` is a local volume (`storagegenie_storage_data`, rw). No other mount.
- `output/` is not in `.gitignore` (no `^output` match). Staging was by exact path `docs/worklogs/SG-290*` only.
- Cleanup search, read-only, in-scope locations only: user crontab unreadable (`crontab -l` answers `Permission denied` — disclosed, not routed around); user systemd unit dir absent (`~/.config/systemd/user/` does not exist); `Makefile`: no match for `prune`, `rmi` or `image rm`; `scripts/` does not exist. Finding: none in scope. (Out of scope, for honesty: system timers checked, no match; unrelated `dispatch-*` unit backups under `/etc/systemd/system/` match `rmi` only as a substring and own no schedule — not a finding.)

## G1 — find the original, changing nothing

- Store: driver `overlayfs` with `io.containerd.snapshotter.v1` — the containerd image store is in use.
- `docker image ls -a --digests --no-trunc`: 62 ids. Tagged: `storagegenie-backend` `latest`, `prover` (both Created 2026-11-02 16:27:38Z), `sg240-proof`, `sg247-verify` (both 2026-10-24 15:40:06Z), plus frontend, busybox, node, python. No id or digest was created between 2026-11-02T15:40Z and 15:56Z (SG-276's serve window); confirmed with `CreatedAt` on the full `ls -a` list — the in-window set is empty.
- References tried with `--format` (never bare): the container's `.Image` (`sha256:96a66241…`) answers `No such image`; `96a66241` answers `No such image` (resolved as `96a66241:latest`, also absent). Nothing further to try — the window list is empty.
- Result: NOT FOUND. Went to G2. No container was created (create-only probe needs a reference; there was none).

## G2 — diff allowed, collision branch chosen, commit refused: STOP

1. `docker diff d972bc75` written to `docs/worklogs/SG-290_diff.log` (paths only): 208 entries (172 `A`, 36 `C`).
2. Classification under the rerun rule: all 208 allowed — 169 `A` entries are `__pycache__`/`*.pyc`, 36 `C` entries are their parent directories, and exactly 3 `A` entries are the mount destinations quoted in G0 (`A /data`, `A /data/db`, `A /data/storage`). No `*.db`, `*-wal`, `*-shm`, and no other entry under `/data`. Entries outside `/app`, `/usr`, `/root`, `/tmp`: 3, all top-level `data` (the three mount dirs) — reported as a count, not by name, beyond the three the packet names. A different count than SG-286's 208 was not observed.
3. Tag collision rule: `storagegenie-backend:recovery-sg270` is absent (`No such image`), so the create branch applies. Not reached for writing — the commit failed first.
4. Commit: `docker commit --pause=false d972bc75 storagegenie-backend:recovery-sg270` failed with `Error response from daemon: NotFound: content digest sha256:93e35323fdb51faac3fc0c915d08e986951c036d9516a2a8fc6456fbd25b3a87: not found`, RC=1 (plus the `--pause` deprecation notice; the flag was used exactly as the packet orders). Retried once with the identical literal command (the builder's one retry): identical failure, identical digest. Full text in `docs/worklogs/SG-290_commit.log`.
5. Second diff: the packet orders it after a commit. No commit happened, so I verified instead that nothing changed: `docker diff` still 208 entries and set-equal to step 1's list (sorted comparison equal; raw order differs between invocations — the daemon returns the list unsorted). The tag is still absent, the image count is still 62, no `sg290-scratch` container exists, and health still answers ok.
6. Time guard: step 4 first started ~45 s after slice start, far under the 900 s ceiling.

Inference (UNVERIFIED): the daemon cannot assemble the new image because content it needs — plausibly a blob of the long-gone parent `sha256:96a66241…` — is absent from the store. `docker commit` on a container whose parent image was garbage-collected fails deterministically (same digest twice), so this route is exhausted, not transient. No other route is in the packet.

## G3 / G4 — not reached

No recovery reference exists, so no export, no inventory script, no comparison, no negative control, no database copy, no recovery container. No container labelled `sg290-scratch` was ever created. Store type recorded above (containerd snapshotter); recovery image size and platform are not applicable (no image). Configuration comparison not applicable (no image).

## End state

- Health end: `{"status":"ok","db":"ok","storage":"ok"}`.
- Container `d972bc75` end: same id, same image `sha256:96a66241…`, running, started `2026-11-02T15:52:53.194514305Z`, restart count 0, same two mounts. No stop, pause, restart, recreate or exec on it. No `docker rmi`, prune, tag (except the attempted recovery tag, which was never written) or compose command. No `.env` opened, no Env printed, no provider call, no spend. The live database was never opened.
- Scratch `output/SG-290-scratch/` removed by exact path before the report commit.

## Runtime and budget

- Start 2026-11-07T20:55:19Z; engine work done ~20:57Z (~100 s of wall clock). No phase measured over 60 s (version, inspect, image list, diffs, two commit attempts, health — each seconds).
- Budget ceiling `RUN_BUDGET_S` 2100 s; expected full run ~700 s. The full run was not performed; spend is a small fraction of the ceiling.

## Files

- `docs/worklogs/SG-290_report.md` (this file)
- `docs/worklogs/SG-290_diff.log` (208 paths, step 1's list)
- `docs/worklogs/SG-290_commit.log` (both failed attempts quoted)

## Acceptance criteria

- A1 — G0 pre-state quoted, mounts as expected, cleanup finding stated: yes.
- A2 — G1 store inventory quoted; not found, with the references tried: yes.
- A3 — G2 ran: both diff lists set-equal and allowed (raw order noted as unstable); collision branch stated (absent → create, never written): yes.
- A4 — G3: not run — no recovery image exists to compare, and the packet allows comparison only against the recovery reference. Stated, not passed off.
- A5 — G4: not run — same reason. Stated.
- A6 — no secret, owner value or response body in git (paths, digests, counts, status codes only); scratch removed; `git show --stat HEAD` holds only `docs/worklogs/SG-290*`: yes (shown at publish).
- A7 — `PB-3`: no empty inventory/diff/zero-entry pass claimed — the diff holds 208 real entries and the STOP rests on the daemon's refusal, not on vacuous evidence: yes.
- A8 — last line below.

## What the owner must decide

The commit route is exhausted on this daemon: the running container's parent image is gone (G1) and the daemon cannot commit the container without that content (G2, same missing digest twice). Options belong to the owner — e.g. rebuild the image from the release commit and tag it as the new recovery baseline after review, or seed the store so `commit` can resolve its parent. I took neither; the app keeps running on the live container, untouched.

Verification: STOPPED in G2 — `docker commit` of d972bc75 to storagegenie-backend:recovery-sg270 refused twice by the daemon (NotFound content digest), no tag or image created, G3–G5 not run
