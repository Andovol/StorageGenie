# SG-186 — R6 serve-time verification + evidence replay sibling, complete and honest

Immutable audit: base `91aacb7d44de24b2949ce80eb5c0150a92f71b17` → work `0dd037d832fac64f8cd699a670d7b3df13320ab8` (fix + 4 tests + 6 logs) → evidence `c009213` (probes) → report `7fe71d3`. Forced-command status at end: `result=done id=SG-186 exit=0`; status verb after: `result=reject reason=replay` (correct: receipted). Mapped notes fetch read both dual-annotation notes; settings envelope-sourced (command). Local pulled `--ff-only` to the exact report HEAD. Scope diff: product `backend/app/api/v1/evidence.py` (+56/−1: hash helper, artifact-kind gate, replay qualification, serve-time compare → 500 + warning), new `backend/tests/test_sg186_evidence_serve_integrity.py` (205 lines, 4 tests), 16 worklogs. No migration, no frontend, no config.

Holistic rating: **97/100**, no flag. Contract 0.47.0 echoed with sha match.

## Evidence accepted (re-read in the diff)

- Product hunk is exactly the D5 semantic plus the homed sibling: read-time sha256 over stored bytes vs `Evidence.sha256`, mismatch → explicit 500 (no serve, no fallback); `upload_evidence` replay qualified by household (same two-line shape as SG-185, confirmed on FIRST READ, taken in-slice per the packet conditional).
- Transcript gate verified against the tree, not the report: `store_text_evidence` (`evidence_service.py:250-302`) sets `sha256` to the artifact digest (household+source+index+text) while the file holds verbatim text — comparing would 500 every legitimate transcript read. Exemption is narrow (`frozenset({"transcript"})`), fail-closed for future kinds, pinned by a control green on both trees. Correct design-forced call, disclosed as packet-unnamed.
- Test bodies genuine (read in full): real upload → pristine 200+sha-match → same-length byte flip → 500+error-string → delete → 404; corrupted-row leg with `integrity_check=ok` control; two-household replay leg; transcript control. No placebo.
- FAIL half on isolated base worktree (3F/1P, transcript control green); PASS focused 4/4; authoritative derived set 82/82 (incl. `test_sg080` transcript leg — empirical proof the gate doesn't break transcripts); SG-180 probe rerun: corruption leg DEFECT_OBSERVED→PASS, key-replay flip labelled as intended semantics change; overhead measured per size with hash-floor comparison (≈0.8–1.0 ms/MB, no gate needed, thumbnails untouched). ruff clean; mypy 41 == 41 both sides.
- Residuals reported, not narrowed: thumbnails unverified (no anchor), TOCTOU window (headers kept byte-identical by choice, documented at the site), cross-household sha dedup (schema-level, reported with a passing probe proof). Health-log code slip re-captured and disclosed. Protocol clean: no denial, disposable isolation pre-import, 2 health GETs, 584 s of 2100 s, 0 provider calls.

No deduction: packet premises held; the one packet-unnamed decision (transcript gate) was forced, narrow, fail-closed and pinned; nothing breached, mismatched or looped.

## Dispositions

| Item | Destination |
|---|---|
| Transcript rows unverified (no recomputable anchor) | Parked: needs schema-stored content hash — owner decision if ever wanted (no slice) |
| Thumbnails unverified (derived, no anchor) | Parked with the above |
| TOCTOU verify-then-send window | Documented residual at the site + report; in-memory serve would cost header semantics — no action |
| Cross-household sha dedup (first household's row) | Schema/design decision — own grant if owner wants it |
| mypy 41/9 pre-existing debt | Canonical register; SG-182 mypy owner priority stands |
| Serve | Normal deploy course, not this slice |

Harness context-size reading unavailable; no conclusion made.
