# Second-opinion context pack — the recovery image, after commit failed

**Prepared by:** the Architect, 2026-11-07. **Committed before Phase A runs** (`AGENTS.md`: a 🟡 on the live host goes through the two-phase review).
**Decision (D26):** how to make an exact recovery image now that `docker commit` cannot.
**Why it matters now:** the deploy rider for SG-279's migration needs a way back to the code now live before it may stop the app. Stage C waits on it.

## The problem in plain words

The live container `d972bc75` runs from image `96a66241`, which no longer exists. The first plan was to commit the container to a new image. The daemon refuses: it needs content from the missing image. The container's files can still be exported.

## The evidence, verbatim

**`docs/worklogs/SG-290_commit.log`:**

> `Error response from daemon: NotFound: content digest sha256:93e35323fdb51faac3fc0c915d08e986951c036d9516a2a8fc6456fbd25b3a87: not found` — RC=1, twice, identical.

**`docs/worklogs/SG-290_report.md`, G1:** containerd image store (`overlayfs` with `io.containerd.snapshotter.v1`), Engine 29.9.2, rootless; the original is not findable by any reference; no image created in SG-276's serve window. Tagged backend images: `latest`, `prover` (2026-11-02 16:27:38Z, SG-279's code), `sg240-proof`, `sg247-verify`.

**`docs/worklogs/SG-290_diff.log`:** the container's own changes are 205 bytecode-cache entries and the three empty mount-point directories `/data`, `/data/db`, `/data/storage`.

**`docs/worklogs/SG-280_report.md:45`:** `docker export` of the running container works on this lane, and its served tree differs from `:latest` in exactly `app/app/services/candidates.py` and one new migration file; static assets byte-identical.

**`docs/releases/2026-11-02-sg270.md`:** release tag `release-2026-11-02-sg270`; image *"content proved equal to the worktree; the build was cache-satisfied"*.

**`backend/Dockerfile`:** `FROM node:20-alpine AS frontend-build` (tag, not digest) at line 3; Python base pinned by digest at line 12; `CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]` at line 22.

## Where it lives

| Thing | File |
|---|---|
| Both stopped attempts | `docs/worklogs/SG-286_report.md`, `SG-286_audit.md`, `SG-290_report.md`, `SG-290_commit.log`, `SG-290_audit.md` |
| The approved plan and its proof | `docs/packets/SG-290-recovery-image-rerun.md` (G3, G4) |
| The earlier review | `docs/worklogs/SG-284_report.md`, `SG-285_report.md` |
| Build and run | `backend/Dockerfile`, `docker-compose.yml` |

**Do not read `STATE.md` or `docs/decisions/`; search with file-targeted reads, not repository-wide greps.**

## What binds it

- D23's proof stands: full-filesystem comparison with the running container, configuration compared field by field with the environment by hash only, and a real start on a scratch copy with `--network none`.
- Secrets: never print the environment; the container's environment holds provider keys (`.env`).
- Never stop, pause, restart or `exec` into the live container. No new provider or image spend.

## The options as I see them, without a pick

| Option | What happens |
|---|---|
| **K3 Export and import** | `docker export d972bc75 | docker import` to `storagegenie-backend:recovery-sg270`, with `--change` lines for `CMD`, `WORKDIR`, `EXPOSE` and the image's own `ENV` (the Dockerfile's, not the container's `.env` values), taken from an image built from the same Dockerfile. Same files by construction; one flat layer. |
| **K2 Rebuild from the release tag** | Build `release-2026-11-02-sg270` and tag it. Not the same bytes unless every input is pinned; the Node stage is not. |
| **K7 Accept no exact old image** | The rider's recovery becomes: restore the backup and start `:latest` (SG-279's code) on it at the old schema head. |

**Q1 —** the pick, and the comparison that proves it. **Q2 —** for K3, where should the image's configuration come from, and how is it proved equal without printing secrets? **Q3 —** anything that makes the whole effort unnecessary or unsafe.
