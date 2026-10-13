# SG-187 — R2 journey repair complete; one self-caught report slip, corrected

Immutable audit: base `acdf81f5003c3794da0ca6c4e15a4257d05d7ade` → work `07d4ea8` (8 files: 4 product + 4 test) → evidence `6ebe555` → report `80b94f6` → correction `45d0f2e` (report-only). Forced-command status at end: `result=done id=SG-187 exit=0`; status verb after: `result=reject reason=replay` (correct: receipted). Mapped notes fetch read the receipt; settings envelope-sourced (command). Local pulled `--ff-only` to the exact correction HEAD. Scope diff: backend `evidence.py` (+13: IntegrityError→readable 422, unexpected→clean 500) + `evidence_service.py` (+29: `_remove_written_artifacts` + row-failure cleanup with race-keep) + 2 new backend test files + `AssetImportModal.tsx` (+23/−11: full accepted set, 20 MiB pre-check, honest note) + `InboxPage.tsx` (+5: CREATED Start control) + 3 frontend test files + 22 worklogs/shots. No migration, no cancel writer, no frontend beyond ceiling.

Holistic rating: **96/100**, no flag. Contract 0.47.0 echoed verbatim.

## Evidence accepted (re-read in the diff)

- G1: Start control posts the modal's proven `/run` on CREATED only, honest pending/terminal states; FAILED keeps Retry only. FAIL arm = new frontend test failing on base; backend journey legs green on base too — correctly declared controls (PB-3), not vacuous arms.
- G2: unknown-household FK now readable 422 + zero orphans (SG-180 probe: base DEFECT_OBSERVED raw detail + 3 orphans → candidate clean 422 + []); oversize 413 preserved; full-buffer shape noted-not-redesigned per packet. The 422-raw→500-clean widening for unexpected failures is intentional, reported, with no covered path depending on the old shape.
- G3: note matches enforced reality; both screenshots OPENED BY THE AUDIT at 760px and 390px — wording confirmed, no 25 MB string, no clipping/overflow at either width; owner checklist present.
- FAIL halves genuine both layers (backend 1F/3P raw-detail assertion; frontend 4F/23P); PASS focused 4 + 27; authoritative backend 97 + frontend 41; ruff/tsc/eslint clean; mypy 41 == 41 both sides.
- TWINS: `except→str(e)` enumerated (users.py:29-31 reported out-of-surface); `store_text_evidence` orphan left per its own docstring design (verified in tree).
- Protocol: disposable isolation pre-import, Docker probes excluded, 2 health GETs 200/200, 0 provider calls, no denial. Elapsed 1188 s of 2100 s (57%; over the ~900 s uncalibrated expectation — orientation-heavy 3-goal slice, no bound hit, no loop).

Deduction −4, attribution coder: the first report version carried a forward-written push line (prediction as observation, CO-29/CO-51) — self-caught and corrected in a report-only follow-up commit before audit. The correction is exemplary; the slip itself is the deduction. Elapsed-over-expectation is noted, not deducted (expectation uncalibrated).

## Dispositions

| Item | Destination |
|---|---|
| test import-order fragility (a7) | Reported (CO-16); pre-existing, untouched |
| F-SG180-10 memory shape | Noted per packet, not redesigned |
| No cancel writer / no dishonest cancel text | Per packet scope; closed |
| mypy 41/9 debt | Canonical register |
| Serve | Normal deploy course, not this slice |

Harness context-size reading unavailable; no conclusion made.
