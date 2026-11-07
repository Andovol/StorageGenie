SG-286 | model opencode-go/claude-haiku-5-5 | effort not stated in the trigger I received (AGENTS.md rotation slot says high; UNVERIFIED) | working dir /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation -> 4b480d6ca6c17fe0d4cfeb95d07e13f9137b909c | WORK_HEAD 4b480d6ca6c17fe0d4cfeb95d07e13f9137b909c

# SG-286 report — recovery image: STOPPED in G2

Outcome: no recovery tag and no image were created. The live app was not touched. G2 stopped on the packet's own rule (anything under `/data` in `docker diff` is a STOP) before any commit.

## G0 — pre-state (changed nothing)

- Socket: `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-286/docker.sock`, `docker version` shows a Server section (Engine 29.9.2, containerd v2.4.2). Scratch was `output/SG-286-scratch/`, removed by exact path at the end.
- Health start: `{"status":"ok","db":"ok","storage":"ok"}`.
- Container `d972bc75` pre-state (expected): id `d972bc752fa038be2552322120af1e0d56a35321cc47d61fc4677b476a91332f`, image `sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22`, `storagegenie-backend`, running, started `2026-11-02T15:52:53.194514305Z`, restart count 0, health `healthy` (FailingStreak 0).
- Mounts: as expected. `/data/db` is a bind (rw); `/data/storage` is a local volume (rw). No other mount.
- Cleanup search (read-only): crontab, `~/.config/systemd/user`, `/etc/systemd/system` timers and services, `Makefile`: no match for `prune`, `rmi` or `image rm`. `scripts/` does not exist. Finding: none. Caveat: `systemctl --user` could not reach a bus, so the user timers were checked through their unit files, not through `list-timers`.
- Contract: recorded `0.58.0` (`AGENTS.md`). The checker `/home/andrei/storagegenie-contract/rules_check.sh` exists, but reading that path is denied by a permission rule. I did not run it and did not route around the denial. Published `contract-v0.58.0` and host contract versions: UNVERIFIED. This is a finding.

## G1 — find the original (changed nothing)

- Store: driver `overlayfs` with `io.containerd.snapshotter.v1`, so the containerd image store is in use.
- `docker image ls -a --digests --no-trunc`: four `storagegenie-backend` tags (`prover`, `latest`, `sg240-proof`, `sg247-verify`), frontend, busybox, node, python, and about 50 untagged ids. None was created between 2026-11-02T15:40Z and 15:56Z. The nearest are `latest` and `prover`, created 2026-11-02 16:27:38Z.
- References tried: container `.Image` (`sha256:96a66241…`) and `96a66241`. Both answered `No such image`, as in SG-280. The in-window list was empty.
- Result: NOT FOUND. Went to G2.

## G2 — commit, STOPPED before step 4

1. `docker diff d972bc75` written to `docs/worklogs/SG-286_diff.log` (paths only): 208 entries (172 `A`, 36 `C`).
2. Classification: 177 entries allowed (`__pycache__` and `*.pyc`, plus the `C` entries of their parent directories). 3 entries not allowed: all kind `A`, all under top-level directory `data` (the `/data` directory and its two subdirectories, the mount destinations from G0). Under the packet, anything under `/data` is a STOP. Stopped. I did not check whether these directories are empty; that would need an export or exec, which the packet does not allow at this step.
3. Tag collision check: `storagegenie-backend:recovery-sg270` is absent, so the create branch would apply. Not reached.
4. Commit: NOT run. No tag, no image created. Time guard not reached (elapsed about 70 s).
5. Second diff: NOT run.

Note: the diff log holds the three `/data` entries by name, because G2 step 1 requires the full path list. They are mount-point directory names, not owner data.

## G3 / G4 / G5 — not reached

No export, no inventory, no comparison, no database copy, no recovery container. No container labelled `sg286-scratch` was created. No store comparison was run. Store type recorded above (containerd snapshotter). The recovery image size is not applicable (no image).

## End state

- Health end: `{"status":"ok","db":"ok","storage":"ok"}`.
- Container `d972bc75` end: same id, same image `sha256:96a66241…`, running, started `2026-11-02T15:52:53.194514305Z`, restart count 0. The end mount list was cut by my own `cut` and not re-quoted in full; the start list above is complete.
- `docker diff d972bc75` still 208 lines, unchanged.
- No stop, pause, restart, recreate or exec on `d972bc75`. No `docker rmi`, prune, tag or compose command. No `.env` opened, no Env printed, no provider call, no spend. The live database was not opened.

## Owner decision needed

The packet rule treats the three `/data` entries as a STOP. Options for the owner (not decided here):
- (a) Accept those three empty mount-point directories as allowed for this commit, after an explicit check that they are empty, and rerun G2 onward.
- (b) Another route, e.g. a read-only export of the running container, which the packet would need to allow.

## Runtime and budget

- Start 2026-11-07T20:51:08Z; last command 20:52:16Z; about 70 s of wall clock. No phase measured over 60 s.
- Budget ceiling `RUN_BUDGET_S` 2100 s; expected full run about 700 s (estimate). The full run was not performed.

## Files

- `docs/worklogs/SG-286_report.md` (this file)
- `docs/worklogs/SG-286_diff.log`

Scratch `output/SG-286-scratch/` removed by exact path.

Verification: STOPPED in G2 — `docker diff` of d972bc75 has 3 entries under /data outside the allowed set; no commit, no recovery tag, G3–G5 not run
