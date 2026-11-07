# Second-opinion context pack — the missing recovery image

**Prepared by:** the Architect, 2026-11-07. **Committed before Phase A runs** (`SECOND_OPINION.md`; `AGENTS.md`: a 🟡 item on the live host goes through the two-phase review).
**Decision:** how to get back an exact way to return to the live app's current code before the next deploy rider stops it.
**Why it matters now:** stage C needs SG-279's migration live before SG-271 can build on split and merge. The rider that deploys it, SG-280, stopped before touching the live app because its recovery image no longer exists.

## The problem in plain words

A deploy rider stops the live app, migrates its database, and starts the new image. If anything goes wrong, its recovery path starts **the old image** on a restored copy of the database. The old image, `96a66241`, is still what the running container `d972bc75` was created from, but the daemon now answers `No such image` for it. So there is no exact way back until one is made. The live app is healthy and untouched.

## The evidence, verbatim

**`docs/worklogs/SG-280_rehearsal.log:42-47`:**

> `+ docker create --label sg280-scratch --name sg280-old-read ... sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22 python -c print('old-image-present')`
> `Error response from daemon: No such image: sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22`
> `SG280-G3-STEP4-OLD-IMAGE-MISSING STOP in S0`

**`docs/worklogs/SG-280_report.md:38`** (the probe the packet ordered):

> `docker tag <old-id> sg280-scratch-probe-tag` succeeded (showing `96a662414c23`) and `docker rmi` removed that tag.

**`docs/worklogs/SG-280_report.md:14`** (the Coder's inference, labelled so):

> My inference (UNVERIFIED): the G0 `docker tag <old-id> scratch-tag` + `docker rmi scratch-tag` combined with the G1 `docker compose build` retagging `:latest` left the old id untagged, and the object was then garbage-collected despite the running container.

**`docs/worklogs/SG-280_report.md:44`** — the new image is a manifest list, which suggests the containerd image store, where ids and digests behave differently from the classic store:

> New image: `storagegenie-backend:latest` = `sha256:e3e74a61…` (manifest list), image config `sha256:bd046bff…` (`:prover` tag, same Created 2026-11-02T16:27:38Z …)

**`docs/worklogs/SG-280_report.md:45`** — exporting the running container works on this lane:

> Runtime diff over the served Python tree via `docker export` of the running (old) container vs `docker create`+`export` of the new image: `app/app/` changed exactly `app/app/services/candidates.py`; `app/alembic/` adds exactly `app/alembic/versions/20261102_sg279_candidate_state.py`. … JS/CSS byte-identical as required.

**`docs/releases/2026-11-02-sg270.md`**, the release that made `96a66241`: tag `release-2026-11-02-sg270`; image `sha256:96a66241…` *"(content proved equal to the worktree; the build was cache-satisfied)"*.

**Not established by anyone:** that the image object is really deleted rather than unreachable by that id; and what happens if container `d972bc75` restarts (both app services restart on their own unless stopped, `AGENTS.md`).

## Where it lives

| Thing | File |
|---|---|
| The stopped rider: packet, report, log, rehearsal script | `docs/packets/SG-280-deploy-rider-candidate-state-migration.md`, `docs/worklogs/SG-280_report.md`, `SG-280_rehearsal.log`, `SG-280_rehearse.py` |
| The release the live app runs | `docs/releases/2026-11-02-sg270.md`; the git tag `release-2026-11-02-sg270` |
| How the image is built and run | `backend/Dockerfile`, `docker-compose.yml`, `Makefile`, `backend/requirements.lock` |
| What changes between the live code and SG-279 | `backend/app/services/candidates.py`, `backend/alembic/versions/20261102_sg279_candidate_state.py` |
| Whether the app migrates on start | `backend/app/server.py` and what it imports |

**Do not read `STATE.md`, `docs/decisions/` or `docs/worklogs/SG-280_audit.md`.** They carry the Architect's view; leaving them out keeps this pass blind.

## What binds it

- **Decided, not reopened:** SG-279's migration ships through a rider with the owner's recovery states S0–S4 and the isolated restore rehearsal (D16, D20; in the SG-280 packet).
- **Sensitive surfaces:** the live host, the app database, the stored files (`AGENTS.md`). A stop rule that fires on one returns the work to the owner.
- **Lane facts:** rootless Docker daemon; `/tmp` is denied, scratch lives under `output/<ID>-scratch/` (`AGENTS.md`); the dispatch key runs only the dispatch command.
- **No new provider or image spend in stage C.**
- `PG-PR-01` (shared contract): rights are probed only on throwaway objects.

## The options as I see them, without a pick

**Q1 — how to make the recovery image.**

| Option | What happens |
|---|---|
| **K1 Commit the running container** | `docker commit` of `d972bc75` to a new tag. Same files as the running container, including anything it wrote at run time; same config (`Cmd`, `Env`). Proved by comparing its export with the container's export. |
| **K2 Rebuild from the release tag** | Build `release-2026-11-02-sg270` and tag the result. Clean of run-time writes, but not the same bytes unless every input is pinned. Proved the same way against the running container's served tree. |
| **K3 Export and import** | `docker export d972bc75 | docker import` to a tag. Same files; the config (`Cmd`, `Env`, workdir) must be supplied by hand. |
| **K4 No old image** | Recovery becomes: restore the backup file and run the **new** image at the old schema head, relying on the code differing only in `candidates.py` and one migration file. |

**Q2 — where it is made.** Inside the rerun rider's first goal, or as its own small slice before the rider, with its own report?

**Q3 — the guard for the future.** What stops a recovery image depending on a tag something else can move or remove? Name the smallest rule and what it costs.

## What would make the whole approach wrong

Name it if the image is not actually gone (for example, still present in the store under another digest, so a `docker image ls --digests -a` or an inspect of `d972bc75`'s image field would find it), if `docker commit` or `export` is unsafe on a running SQLite-backed container whose database lives in a bind mount, or if a restart of `d972bc75` before the rider would already fail.
