# StorageGenie — Coder ratings

Schema: shared `LEDGER.md` — nine columns, `guards_invoked` + `deduction_attribution` included. Below-95 investigations per shared `RATING_ISSUE.md` sit under their row. No pooled ledger (D30): rows live here, nothing aggregates them.

| slice_id | phase | model | effort | score | flag | lever | guards_invoked | deduction_attribution |
|---|---|---|---|---|---|---|---|---|
| SG-003 | Phase 0 | codex (audit: gpt-5.6-luna) | medium | 82 |  | G5-prefill: every future SG packet orders push-WORK_HEAD-to-evidence-ref + verify equality BEFORE invoking RECEIPT_CMD (verbatim block carried in SG-004) | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-10, PG-EV-06, PG-PR-03, PG-PR-04 | packet |
| SG-004 | Phase 0 | codex (audit: unknown per identity line) | medium | 96 |  |  | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-10, PG-EV-06, PG-PR-03, PG-PR-04 | coder |
| SG-005 | Phase 0 | codex (audit: unknown per identity line) | high | 97 |  |  | PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09 |  |
| SG-006 | Phase 0 | codex (audit: unknown per identity line) | high | 98 |  |  | PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09 |  |
| SG-007 | Phase 0 | codex (audit: unknown per identity line) | high | 98 |  |  | PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09 |  |
| SG-008 | Phase 0 | codex (audit: unknown per identity line) | high | 98 |  |  | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09, PG-EV-10, PG-PR-03, PG-PR-04, PG-IC-01 |  |
| SG-009 | Phase 0 | codex (audit: unknown per identity line) | high | 98 |  |  | PG-EV-01, PG-EV-02, PG-IC-01, PG-IC-09 |  |
| SG-011 | Phase 0 | codex (audit: unknown per identity line) | high | 98 |  |  | PG-EV-01, PG-EV-02, PG-EV-09, PG-SC-02, PG-IC-09 |  |
| SG-010 | Phase 0 | codex (audit: unknown per identity line) | high | 98 |  |  | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09, PG-EV-10, PG-IC-01, PG-IC-09 |  |
| SG-012 | Phase 1 | codex (audit: unknown per identity line) | high | 98 |  |  | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09, PG-PR-03, PG-PR-04, PG-IC-01, PG-SC-02, PG-SC-03 |  |
| SG-013 | Phase 1 | codex (audit: unknown per identity line) | high | 90 |  | Sandbox cannot install apt packages — 2 real-decoder legs carried to manual compose pass, not re-scoped; see investigation below | PG-EV-01, PG-EV-05, PG-EV-06, PG-EV-09, PG-PR-03, PG-PR-04, PG-IC-01, PG-SC-02 | coder-env |
| SG-014 | Phase 1 | codex (effort high verified from process args; model unknown, CLI omits id) | high | 96 |  | Full product proof, genuine tests, exemplary disclosure; test-layer suite-health regression + unverified "pre-existing" label; see lever below | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09, PG-PR-03, PG-PR-04, PG-IC-01, PG-SC-02, PG-SC-03 | coder |
| SG-015 | Phase 1 | codex (effort high verified from process args; model unknown, CLI omits id) | high | 97 |  | Plugin complete + G0 suite repairs verified green; audit-caught observed-date kind-scope flaw (ISS-2) carried to SG-017 | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09, PG-PR-03, PG-PR-04, PG-IC-01, PG-SC-02, PG-SC-05 | coder |
| SG-016 | Phase 1 | codex (effort high verified from process args; model unknown, CLI omits id) | high | 97 |  | Full UI proof with discrimination runs; two minor UX warts queued; ISS-1 destination corrected to manual pass | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09, PG-PR-03, PG-PR-04, PG-IC-01, PG-SC-02, PG-SC-05 | coder |
| SG-017 | Phase 1 | codex (effort high verified from process args; model unknown, CLI omits id) | high | 97 |  | All legs proved + ISS-2 closed with regression tests; new stale migration test disclosed with base evidence, queued to SG-018 | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09, PG-PR-03, PG-PR-04, PG-IC-01, PG-SC-02, PG-SC-05 | coder |
| SG-018 | Phase 1 | codex (effort high verified from process args; model unknown, CLI omits id) | high | 96 |  | Correct STOP on a real product defect (TIFF detector gap), no workaround attempted, clean BLOCKED close-out; see lever below | PG-EV-01, PG-EV-02, PG-EV-05, PG-PR-03, PG-PR-04, PG-IC-01 | coder |
| SG-019 | Phase 1 | codex (effort high verified from process args; model unknown, CLI omits id) | high | 98 |  | Minimal correct repair with byte-level both-endian proof, full signature table pinned, self-corrected guard; ISS-3 closed | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09, PG-PR-03, PG-PR-04, PG-IC-01, PG-SC-05 | coder |
| SG-020 | Phase 1 | codex (effort high verified from process args; model unknown, CLI omits id) | high | 98 |  | Complete wall-to-wall exit proof, chained ids, stale repair done, read-verified runbook, honest door ledger | PG-EV-01, PG-EV-02, PG-EV-05, PG-EV-06, PG-EV-09, PG-PR-03, PG-PR-04, PG-IC-01, PG-SC-02, PG-SC-05, PG-SC-09 | coder |
| SG-021 | manual pass | codex gpt-5.6-luna (effort high, both from process/provider metadata — first known model id) | high | 96 |  | Correct whole-slice STOP: socket denial quoted + foreign-8000 collision forensics, no workaround, clean close-out | PG-EV-01, PG-EV-02, PG-EV-05, PG-PR-03, PG-PR-04, PG-IC-01 | coder |
| SG-021 (re-run, --force) | manual pass | codex (effort high verified from process args; model unknown, CLI omits id) | high | 97 |  | Rootless proved + PID-level occupant forensics (8001 = ShoperOS tenant), correct double-STOP (read-only buildx activity, 8001 foreign), zero scope breach, complete report | PG-EV-01, PG-EV-02, PG-EV-05, PG-PR-03, PG-PR-04, PG-IC-01 | environment |

## SG-013 investigation (score 90 < 95)

1. **Failure class:** environment.
2. **Root cause:** the dispatch sandbox sets no-new-privileges (`sudo: The "no new privileges" flag is set`, quoted in report); `tesseract-ocr`/`libzbar0` uninstallable, so the generated-QR/EAN-decode and rendered-text-OCR legs fail with `pyzbar/libzbar is not installed` / `tesseract is not installed`. Pure-python controls (check-digit math both polarities, dHash 0/19 vs threshold 10, EXIF gate + GPS exclusion, quarantine + retry, migration round-trip) all green; full suite 32 passed / 2 failed, honestly reported (not class 13 — targeted-green never presented as suite-green; not class 6 — no "pre-existing" claim).
3. **Exact correction:** re-run the 2 red legs where the packages exist — the compose image (`backend/Dockerfile` already carries both apt lines) during the deferred manual compose pass; record green there. No code change unless they fail there too (then a repair slice).
4. **Recurrence guard:** every slice premise now carries its environment capability (sandbox: no apt/sudo/docker; compose image: full) — recorded in the stage plan; decoder legs pre-declared carried in SG-018's amended fixture scope.
5. **Owner impact:** trigger-to-`done` ≈17 min observed via status checks, inside the 2100 s bound; cost unavailable (platform exposes none).
6. **Attribution note:** Coder execution was contract-correct throughout (graceful degradation with warnings, privileged-denial reported as unanswered per packet, ADR-003 staleness reported as a finding instead of silently edited, no scope overreach into DEDUPLICATING/COMMITTING). Deduction is environment, not execution — hence 90, not lower.

## SG-014 lever (score 96, test-layer suite-health regression)

**Mechanism (audit-established, not report-claimed):** `test_evidence_upload.py:11-28` sets `os.environ` then builds its engine/SessionLocal at IMPORT time from the settings singleton. SG-014's new `test_candidates.py`/`test_dedup.py` sort alphabetically earlier and import `app.config` first, so the singleton is constructed before the env vars exist — 5 of that file's tests fail in-suite while passing alone. The log's "pre-existing" label cited no base run (class 6 pattern); at base `0428f9a` the full suite was 32+2 with no coupling failures, so the trigger postdates SG-014's files (the fragility itself is the old file's design). Product code is unaffected.
**Destinations:** (1) order-independent engine construction in `test_evidence_upload.py` + (2) explicit-revision target for the stale SG-013 migration assertion — both test-only, both folded as bounded G0 legs into SG-015's packet. (3) ISS-1 decoder legs stay carried to the manual compose pass.
**Packet lever (Architect's share):** SG-014's packet demanded exclusion-naming but not base proof — every future packet carries the line "a 'pre-existing failure' claim cites the base commit + the base-run command and output, or it is a new finding with a destination." First carried in SG-015.

## SG-018 lever (score 96, correct STOP — Architect's packet share)

**Mechanism:** SG-013 added `image/tiff` to `allowed_mime_types` (`config.py:11`) per the stage plan, but `_detect_media_type` (`evidence_service.py:56-73`, verified by direct read 2026-09-08) never learned TIFF magic bytes (`II*\0`/`MM\0*`) — config advertises what the detector rejects. SG-013's tests inserted evidence rows directly and never exercised the upload route, so the gap survived; the SG-018 packet then asserted TIFF upload availability from the config line alone without reading the detector (PG-IC-09 miss — a premise from my own plan treated as fact).
**Destinations:** SG-019 repair slice (TIFF signature branch + real upload test) → SG-020 exit re-run (fresh packet/base). Standing addition to the packet line: "an upload-availability premise cites the detector code, not the config list."
**Attribution note:** Coder execution was exemplary — bounded probe with quoted 422, correct diagnosis, STOP over workaround, clean BLOCKED close-out with baseline suite state (54+3: 2 ISS-1 + 1 stale) and no product touch. No deduction for the blocker; 96 reflects a perfect stop with no exit proof.

## SG-003 investigation (score 82 < 95)

1. **Failure class:** prompt gap.
2. **Root cause:** packet G5 ordered "publish with RECEIPT_CMD" but never the evidence-prefill push that `finalize_dispatch_report.sh` gates on (`candidate_not_remote`: `origin/storagegenie-evidence` must equal CANDIDATE first). The precondition lived only in the host script, which packet authoring never read (G-A10 miss).
3. **Exact correction:** G5 gains: push `<WORK_HEAD>:refs/heads/storagegenie-evidence`, fetch, verify equality, then invoke RECEIPT_CMD; a post-prefill `candidate_not_remote` is a STOP.
4. **Recurrence guard:** the lever above — pasted into every future SG packet G5.
5. **Owner impact:** run completed inside one 15 min client window (bound, not estimate); cost unavailable (platform exposes none).
6. **Attribution note:** coder execution was contract-correct throughout (CO-54 refusal to hand-move the ref, CO-57 unconditional report, non-vacuous gates, honest BLOCKED first line). No flag: no false completion, no breach.