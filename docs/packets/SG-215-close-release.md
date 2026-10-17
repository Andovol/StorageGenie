# SG-215 — close-release: attest the SG-212 delta live, record, tag (D-22 standing close rule)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none (read-only probes: served GETs, health, DB sha/migration-head reads; zero writes). Restart: none** (no build, no recreate — the SG-214 serve stands).
**Autonomy: L3** (approved queue; checkpoints only on `G-K2`/stage end). Authority: standing D-22 close-release rule ("release at every session close"; owner-ordered 2026-10-17). Precedent shape: SG-211 (rated 98, first tag).

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

The session closes with a served-but-untagged delta: SG-214 put the SG-212 width-adaptive rule live; tag `release-2026-10-17` covers only through SG-208. D-22 fires the close-release: attest + record + tag, the same shape as SG-211, before CLOSE_COMPLETE.

## Handed-over facts (expected — re-verify on target, `PB-1`)

- Served state (expected, SG-214 poststate): container `d45005fb`, image `98f8af1f`, index `b52f84ca…`, JS `8bab60ce…` (321010 B), CSS `c3b58cda…`, DB `e6bef157…` 28 tables, alembic `20260924_sg114_relation`. Rule marker `catalog-content-column` 1→0 pre/post in served bytes. Re-derive live, never assume.
- Tag namespace: `release-2026-10-17` exists (SG-211, through SG-208). New tag: **`release-2026-10-17-sg212`** (self-describing, unique — verified absent at authoring; re-check on target, never assume). Record: `docs/releases/2026-10-17-sg212.md`.

## G1 — verify live==tree, then attest + record + tag

- Re-read live (served GETs, `docker inspect` on the lane socket, read-only DB probes): every value must equal the SG-214 poststate. ANY mismatch STOPS the slice (no tag on unverified bytes — `PB-6`).
- Write the release record `docs/releases/2026-10-17-sg212.md`: date, tree HEAD, served shas (container/image/bundle), DB read, what's in (SG-212 rule; SG-213/214 evidence-only), what's not (Option C/D unapproved; AI stages transport-less per SG-209/213; D-23 open), tag name, D-22 authority. No invented scope.
- Create the annotated tag `release-2026-10-17-sg212` on the verified HEAD, push it (`git push origin <tag>`), read back via `ls-remote`. The tag push is the outward-facing act D-22 approves — stated, not silent.

## Constraints

- **Scope ceiling:** record + tag ONLY; evidence ONLY under `docs/worklogs/SG-215_*`. Zero product/config/test bytes; no restart; no secret in any artifact. `PB-3`: a tag on unverified reads is a FAIL.
- Reads: lane GETs + git only, DB mode=ro. Hang bounds: reads 120 s; tag ops 120 s; suite NOT run (zero product bytes; `CO-25` attestation needs no product failure — stated). Expected duration ≈300 s (Architect record, `G-A9` uncalibrated; SG-211 took 174 s same shape).
- Simplicity: verify + record + tag; no new machinery. Excluded (stated): any product change; backfill (this tag covers the live bytes as verified today).

## Acceptance criteria

- **A1:** every live re-read equals its SG-214 record (table of expected vs read, per value); on any delta: STOPPED, no tag, reason named.
- **A2:** release record committed at the path; annotated tag exists locally AND on origin (`ls-remote` read-back); tag points at the verified HEAD.
- **A3:** report `docs/worklogs/SG-215_report.md`; elapsed vs ≈300 s; constraints answered; FIRST/DURING/REMAINING; FIRST token `SG-215`.
- **A4:** notes-ref receipt on `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-215 | Report: docs/worklogs/SG-215_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/05; PG-SC-09; PG-IC-01/07; PG-PR-03. Stop follows `PB-6`.
