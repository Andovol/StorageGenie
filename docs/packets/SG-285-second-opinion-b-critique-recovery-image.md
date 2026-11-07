# SG-285 — Second opinion Phase B (critique): the missing recovery image

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one. This lane's snapshot has no `.git`: state `unknown` once and carry on.
**DATABASE: none.**
**Restart: none.**

## Why this exists

Phase A is done (`docs/worklogs/SG-284_report.md`). This is **Phase B — the critique.** Attack the picks below. They are the Architect's **recommendations, not decisions**; the owner decides them as D23.

## The picks, verbatim

> **R1 (Q1), recommended: find first, then commit.**
> - **Find:** read-only, inspect `d972bc75`'s image field, `docker image ls --digests -a`, `docker image inspect` of every candidate reference, and the daemon's store mode (`docker info`). If the original object still answers by any reference, tag it `storagegenie-backend:recovery-sg270` and prove it as below. No new object.
> - **Otherwise K1:** run `docker diff d972bc75` first. If every changed path is transient (bytecode caches, logs) and none is database-like (`*.db`, `*-wal`, `*-shm`, anything under `/data`), run `docker commit --pause=false d972bc75 storagegenie-backend:recovery-sg270`. Any other path: STOP and report the list. `--pause=false` because the database and storage are mounts that commit does not capture, so pausing would freeze the live app for no consistency gain.
> - **Proof, whichever path:** a full-filesystem comparison between `docker export d972bc75` and the export of a never-started container created from the recovery tag: per path, type, mode, owner, symlink target and sha256. Expected: identical, since a commit carries the container's own writable layer. Any difference stops. Effective configuration compared field by field (Entrypoint, Cmd, WorkingDir, User, Env with values compared by hash only, Healthcheck, platform). Then **start** the recovery image on a scratch restored copy of the database, no published port, scratch storage, and from inside it `GET /v1/health` and one read route return 200.
>
> **R2 (Q2), recommended: its own slice, SG-286.** It finds or makes the image, proves it, reports and stops. The rider reruns after it as SG-287, from `docs/packets/SG-280-deploy-rider-candidate-state-migration.md`, with: the real-object tag probe removed; `--user` dropped; G0 checks that `recovery-sg270` resolves to the id SG-286 recorded; G3 step 4 actually starts the old app and reads health and one route (Phase A found `SG-280_rehearse.py:272-285` only creates a container); step 2's damage assertion strengthened to show the state it claims.
>
> **R3 (Q3), recommended: two tags per rider, never removed by a rider.** Before any build, a rider tags the image it is about to replace `storagegenie-backend:recovery-<slice>` and verifies it resolves to the recorded id; after a good deploy it tags what it serves `storagegenie-backend:release-<slice>`. No rider removes, moves or prunes either. Rights are never probed on a real object (`PG-PR-01`). Old tags are retired only by an owner-approved cleanup. Cost: disk for retained layers, about one inspect per rider.

## G1 — Read

`AGENTS.md`'s top section, `docs/reviews/2026-11-07-recovery-image-context.md`, `docs/worklogs/SG-284_report.md`, and the files they name. **List every file read beyond those.**

## G2 — Per pick R1 to R3

- the strongest case against it, with evidence (`file:line`, a quote, a measurement);
- a premise of it that is unverified;
- the observation that would settle any disagreement.

An objection without evidence is labelled `opinion`. Where your Phase A pick differed, say whether the Architect's reasoning changes it. Check especially: whether `--pause=false` is safe given what `docker diff` would show; whether a commit's export can be identical to the container's on a rootless containerd store; whether R2's extra slice earns its cost against folding R1 into the rider's G0; and whether R3 needs anything R1's proof does not already give.

## G3 — Report

Your final message **is** the report (read back with `SG-285 --status`; the Architect copies it unedited to `docs/worklogs/SG-285_report.md`). **Keep the whole report under 120 lines.** The most serious objection first. Shape: `SG-285` as the first token; the contract-version line (`PB-4`); the extra-files list; R1–R3; a closing line of what you read.

## Constraints

Read-only; reads confined to the repository at BASE; no host commands, Docker, credentials, browser, network or database. Hang bound: file reads 120 s each. A denial is a STOP (`PB-2`).

## Acceptance criteria

Each of R1–R3 answered; each objection evidenced or labelled `opinion`; extra-files list complete; report under 120 lines. `PB-3` vacuity: "no objection" needs one sentence on what was checked.

## Report

Destination: final message (engine-published). Identity line and stop path are `PB-4`/`PB-6`. State that you wrote nothing.
