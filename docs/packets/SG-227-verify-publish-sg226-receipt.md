# SG-227 — recovery: verify pushed SG-226 work vs its report, publish the SG-226 receipt note + transcript

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: read-only** (`GET /v1/health`, served-asset GETs, DB sha/migration-head reads, ledger row re-reads; ZERO writes of any kind — this slice proves, never amends). **Restart: none.**
**Autonomy: L3** (stage D-31; checkpoint met — see Why). Authority: this packet (Architect-authorized recovery of SG-226's unpublished receipt; G-K1: narrow, non-destructive, fully documented) + standing receipt protocol.

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

SG-226 did all its work and was killed 1s over budget after its report commit, before publishing the receipt (`result=partial killed=term pushed=3 wip=none`; lane partial note on record; NO Dispatch-ID note). The work is on the branch, verified by audit. This slice has the Coder re-verify the pushed work against the report and then publish what the killed unit could not: the notes-ref note + read-back transcript. Checkpoint status: this IS the stage checkpoint — a killed unit with a missing receipt changes the next packet's assumptions (replay guard answers absent until this lands).

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Pushed SG-226 delta: `daf5e9c` (G1) + `f20867f` (G2) + `cb9734a` (G3 + report). Report commit (Work-HEAD candidate): resolve LIVE as the tip-most commit containing `docs/worklogs/SG-226_report.md` (method, not a hash — never inherit one); expectation: `cb9734a`. If live resolution differs, STOP (do not publish a note on a guessed commit).
- Expected content (verify, report difference either way): 4 Evidence + 4 ledger + 4 audit + 4 link rows with the report's ids; live asset routes returning the 4 renders; secrets gates EMPTY on re-run.

## G1 — verify the pushed work (no writes)

- Re-derive live: the 4 Evidence/ledger/audit/link rows exist with the report's ids; each linked asset's route returns its render (`source_kind=scene_render`); table counts match the report's post-state; secret gates re-run EMPTY over `docs/worklogs/SG-226_*` + `backend/scripts/sg226_bulk_scene.py`. Any mismatch STOPS the slice (no note on unverified bytes).
- Health: ONE `GET /v1/health` start+end (delta none expected; no restart, no served-code change anywhere in this slice).

## G2 — publish the SG-226 receipt (the killed unit's exact commands)

- On the verified Work-HEAD, run EXACTLY (report commit first — this slice wrote no report of its own into that commit; CO-55(b) timing is already broken by the kill, disclosed):
  - `git log --format=%H -n 1 HEAD` (record; this slice's own HEAD, not the note target)
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-226 | Report: docs/worklogs/SG-226_report.md" <verified-work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation` (no-op expected — nothing to push; proves it)
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-226_receipt.log` (late-receipt transcript, labeled with the reason in its first lines).
- Never the retired finalizer. A `notes add` refusal (note exists?) STOPS — read what is there and report; do not force, do not overwrite.

## Constraints

- **Money:** $0 — zero sends, zero renders, zero billed calls (reads + git only). Stated.
- **Scope ceiling:** evidence ONLY `docs/worklogs/SG-227_*` (+ the late `docs/worklogs/SG-226_receipt.log` transcript commit — explicitly authorized here, the recovery's whole point). Zero product/test/DB bytes; no migration; no restart; no secret in any artifact.
- **Production writes:** NONE — not one row. The notes-ref push is not a product write (audit trail on the report ref, per protocol). Any other write is a STOP.
- `PG-EV-02`: the verification reads the live DB/route/volume, never the report's word. `PG-EV-09`: verification outputs + transcript committed raw. `PB-2`: any denial STOPS the whole slice. Consent predicate: this packet's quoted authority ONLY.
- Hang bounds: reads 120 s; git ops 120 s; idle kill never approached. Expected duration ≈300 s (Architect record, `G-A9` uncalibrated).
- Simplicity: verify + note + transcript; no new machinery. Excluded (stated): any SG-226 rework (verify-only); CEAFĂ; cutout; bulk; Generate-button wiring.

## Acceptance criteria

- **A1:** live re-verification matches the SG-226 report per row and per route (or STOPPED with the difference quoted); the verified Work-HEAD equals the live-resolved report commit.
- **A2:** notes-ref note with the EXACT first line `Dispatch-ID: SG-226 | Report: docs/worklogs/SG-226_report.md` on the verified Work-HEAD, pushed + read back; late transcript committed at `docs/worklogs/SG-226_receipt.log` with the kill reason in its first lines.
- **A3:** report `docs/worklogs/SG-227_report.md`; elapsed vs ≈300 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-227`.
- **A4:** SG-227's own receipt: FIRST line exactly `Dispatch-ID: SG-227 | Report: docs/worklogs/SG-227_report.md` + `Work-HEAD` recorded, pushed + read back; own transcript at `docs/worklogs/SG-227_receipt.log`. Never the retired finalizer. Same exact command shape as A2.

Guards invoked: PG-EV-02/03/05/09; PG-SC-03/09; PG-IC-01/07/08/09; PG-PR-01/03. Stop follows `PB-6`.
