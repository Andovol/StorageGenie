# SG-228 — close-release: attest the SG-221/222 drawer surfacing live, record, tag (D-22 standing close rule)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: read-only probes** (served GETs, health, DB sha/migration-head reads; zero writes). **Restart: none** (SG-222's serve stands; no rebuild, no recreate).
**Autonomy: L3** (stage D-31; this is the stage's release gate). Authority: standing D-22 close-release rule ("release at every session close"; owner-ordered 2026-10-17).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

SG-221's drawer surfacing went live under SG-222 (image `d6c6a106`) with no release record or tag covering it (`release-2026-10-17-sg212` predates it). D-22 fires the close-release: attest + record + tag, the SG-211/SG-215 shape, before CLOSE_COMPLETE.

## Handed-over facts (expected — re-verify on target, `PB-1`)

- Served state (expected, SG-222 poststate): container `f419758d`, image `d6c6a106`, JS `43c05c51…` (321283 B), CSS `c3b58cda…` unchanged, DB with `asset_evidence` 17+ rows incl. the 3 pilot links + 4 bulk links, alembic `20260924_sg114_relation`. Re-derive live, never assume.
- Tag namespace: `release-2026-10-17`, `release-2026-10-17-sg212` exist (prior closes). New tag: **`release-2026-10-21`** (self-describing, date-scoped; verify absent on target, never assume). Record: `docs/releases/2026-10-21.md`.
- What's covered: SG-221 drawer surfacing (serializer kind key + Scene tab) served by SG-222; SG-217–SG-220/SG-223/SG-225–SG-226 evidence-only pilot/bulk renders (linked, no deploy needed); SG-224 ledger classification. What's NOT: cutout surfacing (no product change yet), CEAFĂ (parked), PIKOK canonical-photo (pending), bulk cutouts (parked).

## G1 — verify live==tree, then attest + record + tag

- Re-read live (served GETs + `docker inspect` over the lane socket + read-only DB probes): every value must equal the SG-222 poststate, and the tree must hold no unserved product delta beyond it. ANY mismatch STOPS the slice (no tag on unverified bytes — `PB-6`).
- Write the release record `docs/releases/2026-10-21.md`: date, tree HEAD, served shas (container/image/bundle), DB read, what's in (above), what's not (above), tag name, D-22 authority. No invented scope.
- Create the annotated tag `release-2026-10-21` on the verified HEAD, push it (`git push origin <tag>`), read back via `ls-remote`. The tag push is the outward-facing act D-22 approves — stated, not silent.

## Constraints

- **Scope ceiling:** record + tag ONLY; evidence ONLY under `docs/worklogs/SG-228_*`. Zero product/config/test bytes; no restart; no secret in any artifact. `PB-3`: a tag on unverified reads is a FAIL.
- Reads: lane GETs + git only, DB mode=ro. Hang bounds: reads 120 s; tag ops 120 s; suite NOT run (evidence-only delta since SG-221's 298/298 green; `CO-25` attestation needs no product failure — stated). Expected duration ≈300 s (Architect record, `G-A9` uncalibrated; SG-215 took 108 s same shape, SG-211 174 s).
- Simplicity: verify + record + tag; no new machinery. Excluded (stated): any product change; backfill (this tag covers the live bytes as verified today only).

## Acceptance criteria

- **A1:** every live re-read equals its SG-222 record (table of expected vs read, per value); on any delta: STOPPED, no tag, reason named.
- **A2:** release record committed at the path; annotated tag exists locally AND on origin (`ls-remote` read-back); tag points at the verified HEAD.
- **A3:** report `docs/worklogs/SG-228_report.md`; elapsed vs ≈300 s; constraints answered; FIRST/DURING/REMAINING; FIRST token `SG-228`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-228 | Report: docs/worklogs/SG-228_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-228 | Report: docs/worklogs/SG-228_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-228_receipt.log`.

Guards invoked: PG-EV-02/03/05; PG-SC-09; PG-IC-01/07; PG-PR-03. Stop follows `PB-6`.
