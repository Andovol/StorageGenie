# SG-293 — Make the live app's recovery image by export and import, prove it, and stop

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte and never stops, pauses, restarts, recreates or `exec`s into the live app.** It writes only `docs/worklogs/SG-293*`, the scratch path, and one new image with one new tag.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: the live app database, read-only, to take one scratch copy.** `sqlite:////data/db/storagegenie.db`, on the host at `data/db/storagegenie.db`. A declared sensitive surface; this packet is the plan the owner approved. **Any result other than the expected one, or any step outside this packet, stops the work and returns it to the owner.**
**Restart: none.**
**Provider: none.** No key is read or printed, no `.env` is opened by you, **no spend**. No container you create gets an `env_file`.

**Authority, verbatim:** owner, 2026-11-07: *"D26 - approved"*. D26 as approved: `docs/decisions/2026-10-30-session-approvals.md` (last entry). Review: `docs/worklogs/SG-291_report.md`, `SG-292_report.md`. Earlier attempts: `SG-286_audit.md`, `SG-290_audit.md`.

**Contract chain:** recorded `0.58.0` (`AGENTS.md`). This lane denies reading the contract folder (SG-286, SG-290); your echo line is the host evidence.

## Why this exists

The live container `d972bc75` runs from image `96a66241`, which no longer exists (SG-286, SG-290 G1). `docker commit` is refused: *"NotFound: content digest sha256:93e35323…: not found"*, twice (`docs/worklogs/SG-290_commit.log`). `docker export` of this container works (`docs/worklogs/SG-280_report.md:45`). A deploy rider must not stop the app until an exact way back exists.

## Secrets and owner data — these bind every goal

- **The live container's environment holds the app's secrets** (`OPENCODE_API_KEY`, `JINA_API_KEY`, `OPENROUTER_API_KEY` and others, `backend/app/config.py:33-46`). Never print it. Never run a bare `docker inspect` of the live container: always `--format` with named fields. Its environment is read only by a script that prints key names and `equal`/`differ`, never a value.
- **The donor image's environment** (`storagegenie-backend:latest`, image configuration, not a container) holds only the base image's and the Dockerfile's `ENV`. You may read it to build the import. **If any of its key names is one of the settings in `backend/app/config.py`, or ends in `_KEY`, `_TOKEN`, `_SECRET` or `PASSWORD`: STOP** without printing its value.
- **The scratch database copy is the owner's data:** counts, hashes and HTTP status codes only.
- **Every container you create or start runs with `--network none`**, label `sg293-scratch`, removed by name.
- If any output you produced contains a secret or owner value, stop, do not commit it, and say so without repeating it.

## G0 — Baseline, changing nothing

- `DOCKER_CONFIG` to a writable directory under `output/SG-293-scratch/`, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-293/docker.sock`, and `docker version` shows a **Server** section. Scratch stays in `output/SG-293-scratch/`, removed by exact path at the end; never touch `output/` itself or `output/dispatch`.
- `curl -s http://127.0.0.1:8003/v1/health` quoted, at start and end.
- **Baseline, against SG-290's record** (`docs/worklogs/SG-290_report.md`): container id `d972bc752fa038be…`, `.Image` `sha256:96a66241…`, running, started `2026-11-02T15:52:53.194514305Z`, restart count 0, mounts `/data/db` (bind) and `/data/storage` (volume) only; `docker diff d972bc75`, sorted, equal to sorted `docs/worklogs/SG-290_diff.log` (208 entries). **Any difference is a STOP; do not refresh the baseline.**
- `df` of the scratch filesystem quoted. **Less than 5 GB free is a STOP** (`UNVERIFIED — my estimate` for three exports and a database copy).
- **`output/` is expected not to be in `.gitignore`.** Stage only by the exact path `docs/worklogs/SG-293*`, never `git add -A` or `git add .`; remove the scratch before your report commit; show `git status --short` clean and `git show --stat HEAD` holding only those paths.

## G1 — Export twice, gate each, compare

1. `docker export -o output/SG-293-scratch/live-1.tar d972bc75`; exit code 0.
2. **Gate, before anything else touches the file:** list its entries under `data/`. Expected exactly `data/`, `data/db/`, `data/storage/`, each a directory. **Any other entry under `data/`, or any entry named `.env` anywhere: delete the file by exact path at once and STOP** (report the count and the directory, never file names under `data/`).
3. The same export and gate as `live-2.tar`.
4. Build an inventory of each with a script committed as `docs/worklogs/SG-293_inventory.py` (it holds no data), run in a one-shot container of `storagegenie-backend:latest` with only the scratch path mounted, `--network none`. Per entry: path, type, mode, uid, gid, size, sha256 for files, link target for symlinks and hard links, and every PAX extended header (`SCHILY.xattr.*`, capabilities) by name and hash. Not modification times. **The script fails on a tar it cannot fully parse, and prints the entry count.**
5. `live-1` and `live-2` inventories must be identical; a difference is drift during capture: STOP. An entry count of zero is a failure (`PB-3`). Report how many entries carry extended headers, including zero.

## G2 — The configuration to import

- **Launch fields, from the live container:** `docker inspect --format '{{json .Config.Cmd}} {{json .Config.Entrypoint}} {{json .Config.WorkingDir}} {{json .Config.User}} {{json .Config.ExposedPorts}} {{json .Config.Healthcheck}}' d972bc75`. Expected `Cmd` `["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]` (`backend/Dockerfile:22`).
- **Image environment, from the donor:** record `storagegenie-backend:latest`'s full id, `Os/Architecture`, and `json .Config.Env` of the **image**, under the key-name rule above.
- **Per-key check:** for every donor key, the live container's value hashes equal to the donor's. One `differ` is a STOP (key name only).
- **Healthcheck:** if the live container's healthcheck equals the one in `docker-compose.yml`, it stays there and is not imported; say so. If it differs, STOP.

## G3 — Import

- **If `storagegenie-backend:recovery-sg270` already exists: STOP.** Never compare it, reuse it or overwrite it.
- Do not start this step if more than **900 s** have passed since your start; report and stop.
- `docker import` `live-1.tar` with one `--change` per launch field (`CMD`, `ENTRYPOINT` only if non-null, `WORKDIR`, `USER` only if non-empty, `EXPOSE`) and one `ENV` line per donor key, to `storagegenie-backend:recovery-sg270`. Record its full id and `Os/Architecture`; the latter must equal the donor's.

## G4 — Prove it

- Create, never start, a container from the recovery tag (`--network none`, label `sg293-scratch`), `docker export` it to `recovery.tar`, apply G1's gate, inventory it, remove the container.
- **`recovery.tar` and `live-1.tar` inventories must be identical.** Any difference: STOP with the differing paths quoted, classified by you, never excused.
- **The check can fail (`PG-EV-01`):** compare once against a copy of the `live-1` inventory with one file's hash altered, and show it reports exactly that path.
- **Configuration:** the recovery image's `Cmd`, `Entrypoint`, `WorkingDir`, `User`, `ExposedPorts` equal the live container's, field by field; its environment equals the donor's per key, by hash.
- **On any failure in this goal, remove exactly the tag you created in G3** (`docker rmi storagegenie-backend:recovery-sg270`; it is your own new object) and report. Nothing else is removed.

## G5 — It actually starts

Take a scratch copy of the live database with **SQLite's backup API** in a one-shot container with `data/db` mounted **read-only** (as `SG-280_report.md:59`). Start a container **from the recovery tag**, recording the id it resolves to: `--network none`, label `sg293-scratch`, no published port, `DATABASE_URL` at the scratch copy, `STORAGE_ROOT` at an empty scratch folder, no `env_file`, no real storage mount, the image's own user. Its startup may write reminders into the copy; that is expected (`backend/app/server.py:27-34`). From inside it, `GET /v1/health` returns 200 and one read route that reads the database returns 200; name the route, status codes only. A scratch folder the container cannot write is a finding (rootless ownership, `SG-280_report.md:39`); fix it only by `chmod` on your own scratch folder. Stop and remove the container by name. A failure here also removes the tag, as in G4.

## G6 — Record and stop

`docs/worklogs/SG-293_report.md`: the recovery tag, full id and platform; the donor's id; every gate and comparison with its counts; the route used in G5. **Do not deploy, migrate, or remove anything else.**

## Constraints

- **Never stop, pause, restart, recreate or `exec` into `d972bc75`.** Never `docker commit`, `image prune`, `system prune`, `builder prune`, `docker compose up`, `down` or `build`. `docker rmi` only as G4 and G5 say. The only daemon objects you create: the recovery tag and its image, and containers labelled `sg293-scratch`.
- **A denial is a STOP (`PB-2`, `PG-PR-03`).** Rights are not probed on real objects (`PG-PR-01`).
- Scratch removed by exact path before the report commit; a file you cannot remove goes through a throwaway `busybox` container (`--network none`) by exact path.
- Tests: none; nothing in the product changes.

## Hang bounds

`docker version` **120 s**; each export **600 s**; import **600 s**; each one-shot **300 s**; health and routes **120 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. Expected ≈600 s (`UNVERIFIED — my estimate`: SG-290 reached its commit in ≈45 s; three exports and an import added). Runtime against budget in the report (`PG-PR-06`), naming every phase over 60 s.

## Acceptance criteria

- A1 — G0's baseline equal to SG-290's, and free space quoted.
- A2 — both exports gated and inventoried, identical, entry counts non-zero, extended-header count stated.
- A3 — donor id recorded, key-name rule passed, every donor key `equal`, healthcheck disposition stated.
- A4 — the tag created only on the absent branch; its platform equal to the donor's.
- A5 — the comparison seen to fail on the altered copy, then identical on the real pair; configuration equal field by field.
- A6 — health and the named read route 200 from the recovery image, by the id the tag resolved to.
- A7 — no secret, owner value or response body anywhere in git; scratch removed; `git show --stat HEAD` holds only `docs/worklogs/SG-293*`.
- A8 — the last line is `Verification: PASS`, or `Verification: STOPPED in G<n> — <reason>`, or `FAIL`.

## Report

Destination: `docs/worklogs/SG-293_report.md`, evidence beside it (`docs/worklogs/SG-293_*`). The first line states the slice ID, model and effort, working directory, remote, BASE ref and resolved commit, and WORK_HEAD.

**Publish, literally, in this order, after your report commit:**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-293 | Report: docs/worklogs/SG-293_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them in your final message. A refused push is a STOP, quoted verbatim. **Publish even after a stop:** the Architect must be able to read the state you left.
