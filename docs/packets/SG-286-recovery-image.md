# SG-286 — Find or make the live app's recovery image, prove it, and stop

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte and never stops, pauses, restarts or recreates the live app.** It writes only `docs/worklogs/SG-286*`, the scratch path, and at most one new image with one new tag.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: the live app database, read-only, to take one scratch copy.** `sqlite:////data/db/storagegenie.db`, on the host at `data/db/storagegenie.db`. A declared sensitive surface; this packet is the plan the owner approved. **Any result other than the expected one, or any step outside this packet, stops the work and returns it to the owner.**
**Restart: none.**
**Provider: none.** No key is read or printed, no `.env` is opened by you, **no spend**. Scratch containers get no `env_file`.

**Authority, verbatim:** owner, 2026-11-07: *"D23 and D24 ok. Lets run in L3 mode."* D23 as approved: `docs/decisions/2026-10-30-session-approvals.md` (last entry). Design review: `docs/worklogs/SG-284_report.md`, `SG-285_report.md`.

**Contract chain:** recorded `0.58.0` (`AGENTS.md`) == published `contract-v0.58.0` == the host's contract. Report it; a different version is a finding.

## Why this exists

Deploy rider SG-280 stopped in S0 because its recovery image no longer answers by its id (`docs/worklogs/SG-280_rehearsal.log:44`: `No such image: sha256:96a66241…`). The live app is healthy on container `d972bc75`, created from that image. A rider must not stop the app until an exact way back exists. **Whether the image object is really gone is not established** (`SG-284_report.md`, G3): the store may be containerd's, where an image can answer to a manifest digest but not to a config id (`SG-280_report.md:44`).

## Secrets and owner data — these bind every goal

- **The container's environment holds the app's secrets.** Never print it. Never run a bare `docker inspect` or `docker image inspect` of the live container or of the recovery image: always pass `--format` with named fields that exclude `Env`. Compare environments **only** as `docker inspect --format '{{json .Config.Env}}' <obj> | sha256sum`, quoting the hash.
- **The scratch database copy is the owner's data:** counts, hashes, schema text and HTTP status codes only. Never a name, id, field value or response body.
- If any output you produced contains a secret or owner value, stop, do not commit it, and say so in the report without repeating it.

## G0 — Socket, pre-state, changing nothing

- `DOCKER_CONFIG` to a writable directory under `output/SG-286-scratch/`, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-286/docker.sock`, and `docker version` shows a **Server** section. Scratch stays in `output/SG-286-scratch/`, removed by exact path at the end; never touch `output/` itself or `output/dispatch`.
- `curl -s http://127.0.0.1:8003/v1/health` quoted, at start and end.
- Expected, hypotheses: container `d972bc752fa0`, `.Image` naming `sha256:96a66241…`, running, healthy, restart count 0, started before 2026-11-02T18:03Z. Quote `docker inspect --format '{{.Id}} {{.Image}} {{.Config.Image}} {{.State.Status}} {{.State.StartedAt}} {{.RestartCount}} {{json .Mounts}}' d972bc75`. **Expected mounts:** `/data/db` (bind) and `/data/storage` (volume). A different container, a restart or another mount is a STOP.
- **`output/` is expected not to be in `.gitignore`.** Stage only by the exact path `docs/worklogs/SG-286*`, never `git add -A` or `git add .`; remove the scratch before your report commit; show `git status --short` clean and `git show --stat HEAD` holding only those paths.
- **Scheduled cleanup, read-only:** quote any `prune`, `rmi` or `image rm` in the user's crontab, user systemd timers, the `Makefile` and `scripts/`. One found is a finding, not a stop.

## G1 — Find the original, changing nothing

Quote `docker info --format '{{.Driver}} {{json .DriverStatus}}'`, whether the containerd image store is in use, and `docker image ls -a --digests --no-trunc` (repository, tag, digest, id, created). Try `docker image inspect --format '{{.Id}} {{json .RepoTags}} {{json .RepoDigests}} {{.Created}} {{.Os}}/{{.Architecture}}'` on: the container's `.Image` value, `96a66241`, and every listed id or digest created between 2026-11-02T15:40Z and 15:56Z (SG-276's serve window, `docs/releases/2026-11-02-sg270.md`).

**Found** means one reference both inspects and lets `docker create --label sg286-scratch <ref> true` succeed (create only, never start; remove that container by name). Then go to G3 with that reference. **Not found** means none does; go to G2.

## G2 — Commit the running container, only if G1 found nothing

1. `docker diff d972bc75`, the full list into `docs/worklogs/SG-286_diff.log` (paths only).
2. **Allowed:** `__pycache__` directories and `*.pyc` files, and the `C` entries for their parent directories. **Anything else — above all `*.db`, `*-wal`, `*-shm`, or anything under `/data` — is a STOP**, with the list quoted.
3. **Tag collision rule, before writing:** if `storagegenie-backend:recovery-sg270` is absent, create it; if it resolves to the object you are about to tag, do nothing; if it resolves elsewhere, STOP.
4. `docker commit --pause=false d972bc75 storagegenie-backend:recovery-sg270`. Record the full id.
5. `docker diff d972bc75` again: the list must equal step 1's. A difference means the container wrote during the commit: STOP.

## G3 — Prove the image equals what the live container runs

Under the scratch path: `docker export d972bc75`, and `docker export` of a container created (never started) from the recovery reference, labelled `sg286-scratch`. Build an inventory of each tar — per entry: path, type, mode, uid, gid, size, sha256 for files, link target for symlinks and hard links — with a script committed as `docs/worklogs/SG-286_inventory.py` (it holds no data). Run it in a one-shot container of `storagegenie-backend:latest` with the scratch path mounted, no `env_file`. Compare.

- **After G2 (commit):** expected **identical**. Any difference: STOP, the differing paths quoted, classified by you, never excused.
- **After G1 (found original):** differences are allowed **only** at paths in `docker diff d972bc75`, quoted in full. Any other difference: STOP.
- **Configuration:** compare `Entrypoint`, `Cmd`, `WorkingDir`, `User`, `ExposedPorts`, `Healthcheck`, `Os/Architecture`, and the environment hash, between the container and the image. Any difference: STOP.
- **The check can fail (`PG-EV-01`):** run the comparison once against a copy of one inventory with one file's hash altered, and show it reports exactly that path.

## G4 — The recovery image actually starts

Take a scratch copy of the live database with **SQLite's backup API** in a one-shot container with `data/db` mounted **read-only** (SG-280 proved this works: `SG-280_report.md:59`). Start a container **from the recovery tag**, recording the id it resolves to: label `sg286-scratch`, no published port, `DATABASE_URL` pointing at the scratch copy, `STORAGE_ROOT` at an empty scratch folder, no `env_file`, no real storage mount, the image's own user. Its startup may write reminders into the scratch copy; that is expected (`backend/app/server.py:27-34`). From inside it, `GET /v1/health` returns 200 and one read route that reads the database returns 200 — name the route; status codes only. Stop and remove it by name.

## G5 — Record and stop

`docs/worklogs/SG-286_report.md` records: the path taken (found or committed); the recovery tag, its full id and platform; the image's size; the store type; the cleanup finding; every comparison result. **Do not deploy, migrate, or remove any tag or image.**

## Constraints

- **Never stop, pause, restart, recreate or `exec` into `d972bc75`.** Never `docker rmi`, `image prune`, `system prune`, `builder prune`, or `docker tag` anything except the one recovery tag. Never `docker compose up`, `down` or `build`. The only daemon objects you create: the recovery tag (and its image in G2), and containers labelled `sg286-scratch`, each removed by name.
- **A denial is a STOP (`PB-2`, `PG-PR-03`).** Rights are not probed on real objects (`PG-PR-01`); a denied `commit` stops with nothing changed.
- **Time guard:** do not start G2 step 4 if more than **900 s** have passed since your start; report and stop.
- Scratch removed by exact path before the report commit; a file you cannot remove goes through a throwaway `busybox` container by exact path.
- Tests: none; nothing in the product changes.

## Hang bounds

`docker version` **120 s**; commit **600 s**; each export **600 s**; each one-shot **300 s**; health and routes **120 s**; ordinary commands **120 s**. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s, read from the lane) is the ceiling. Expected ≈700 s (`UNVERIFIED — my estimate`, from SG-280's ≈461 s to its stop plus two exports). Runtime against budget in the report (`PG-PR-06`), naming every phase over 60 s.

## Acceptance criteria

- A1 — G0's pre-state quoted, mounts as expected, and the cleanup finding stated.
- A2 — G1's store inventory quoted; found or not found, with the reference tried.
- A3 — if G2 ran: both diff lists equal and allowed; the collision rule's branch stated.
- A4 — G3: the comparison seen to fail on the altered copy, then passing on the real pair; the configuration fields equal, the environment by hash only.
- A5 — G4: health and the named read route 200 from the recovery image, by the id the tag resolved to.
- A6 — no secret, owner value or response body anywhere in git; scratch removed; `git show --stat HEAD` holds only `docs/worklogs/SG-286*`.
- A7 — `PB-3`: an empty inventory, an empty diff list or a comparison of zero entries is a failure, not a pass.
- A8 — the last line is `Verification: PASS`, or `Verification: STOPPED in G<n> — <reason>`, or `FAIL`.

## Report

Destination: `docs/worklogs/SG-286_report.md`, evidence beside it (`docs/worklogs/SG-286_*`). The first line states the slice ID, model and effort, working directory, remote, BASE ref and resolved commit, and WORK_HEAD.

**Publish, literally, in this order, after your report commit:**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-286 | Report: docs/worklogs/SG-286_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them in your final message. A refused push is a STOP, quoted verbatim. **Publish even after a stop:** the Architect must be able to read the state you left.
