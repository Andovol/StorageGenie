# SG-292 — Second opinion Phase B (critique): the recovery image, after commit failed

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one. This lane's snapshot has no `.git`: state `unknown` once and carry on.
**DATABASE: none.**
**Restart: none.**

## Why this exists

Phase A is done (`docs/worklogs/SG-291_report.md`). This is **Phase B — the critique.** Attack the pick below. It is the Architect's **recommendation, not a decision**; the owner decides it as D26.

## The pick, verbatim

> **R1, recommended: K3, export and import, as its own slice, proved before it is kept.**
> 1. **Baseline first:** re-quote the container's identity, start time, restart count, mounts and `docker diff` set; a change from `SG-290_report.md` is a STOP.
> 2. **Export to a scratch file, inspect, then import.** `docker export d972bc75` to a file under the scratch path. List its `data/` entries before anything else: exactly three empty directories, or STOP and delete the file at once. Export a second time and compare inventories; a difference is a STOP (drift during capture).
> 3. **Configuration from two sources, never from the `.env` values.** Non-secret launch fields (`Cmd`, `Entrypoint`, `WorkingDir`, `User`, `ExposedPorts`) from the live container's own configuration, by named `--format` fields. Image environment from `storagegenie-backend:latest`'s **image** configuration, which holds only the Dockerfile's `ENV`: the build inputs are unchanged since the release tag (`git diff --stat release-2026-11-02-sg270 HEAD -- backend/Dockerfile backend/requirements.lock backend/pyproject.toml frontend/package.json frontend/package-lock.json docker-compose.yml` is empty). The healthcheck stays where it lives today, in `docker-compose.yml`, not in the image.
> 4. `docker import` the file with those `--change` lines to `storagegenie-backend:recovery-sg270`, under the collision rule (absent → create, same → no-op, different → STOP).
> 5. **Proof:** full inventory comparison (path, type, mode, uid, gid, size, sha256, link target, and any extended attributes the tar carries) between the export and the export of a never-started container from the imported image; the negative control; launch fields equal field by field; **environment proved per key:** for every key in the image's `ENV`, the value's hash equals the live container's value hash for that key; and a **never-started** container created from the recovery image with the same `env_file` and `environment` the compose file gives must have a sorted-environment hash equal to the live container's. Nothing printed but hashes, key names and counts.
> 6. **Real start** on a scratch database copy, `--network none`, no `env_file`: health and one read route 200.
> - Runs as the next rotation slot (Haiku 5.5 `high`). K2 and K7 are rejected for the reasons Phase A gives.

## G1 — Read

`AGENTS.md`'s top section, `docs/reviews/2026-11-07-recovery-image-route-context.md`, `docs/worklogs/SG-291_report.md`, `docs/packets/SG-290-recovery-image-rerun.md`, and the files they name. **Do not read `STATE.md` or `docs/decisions/`; file-targeted reads only.** List every file read beyond those.

## G2 — Per step of R1

- the strongest case against it, with evidence (`file:line`, a quote, a measurement);
- a premise of it that is unverified;
- the observation that would settle any disagreement.

An objection without evidence is labelled `opinion`. Check especially: whether step 5's created-not-started container with the real `env_file` can leak a secret into the Coder's context; whether `:latest`'s image `ENV` can differ from the lost image's; and whether import drops anything the running app needs.

## G3 — Report

Your final message **is** the report (read back with `SG-292 --status`; the Architect copies it unedited to `docs/worklogs/SG-292_report.md`). **Keep the whole report under 100 lines.** The most serious objection first. Shape: `SG-292` as the first token; the contract-version line (`PB-4`); the extra-files list; the steps of R1; a closing line of what you read.

## Constraints

Read-only; reads confined to the repository at BASE; no host commands, Docker, credentials, browser, network or database. Hang bound: file reads 120 s each. A denial is a STOP (`PB-2`).

## Acceptance criteria

Each step of R1 answered; each objection evidenced or labelled `opinion`; extra-files list complete; report under 100 lines. `PB-3` vacuity: "no objection" needs one sentence on what was checked.

## Report

Destination: final message (engine-published). Identity line and stop path are `PB-4`/`PB-6`. State that you wrote nothing.
