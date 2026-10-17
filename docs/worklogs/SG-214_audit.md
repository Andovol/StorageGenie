# SG-214 audit — serve rider: SG-212 density rule live, rated 98

Immutable audit: base `916aa53` → work `cfd7fe6` (9 evidence logs, +409, zero product/config/test bytes) → report `6fa3e40` → receipt `6c279d2`. Local `--ff-only` to the exact tip (`6c279d2` == origin/automation at pull); tree clean. Trigger exit 0; engine `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-214 | Report: docs/worklogs/SG-214_report.md | Work-HEAD: cfd7fe6...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit at the fresh fetch. Per `DISPATCH.md` §2: receipt present → NOT failed. **Seventeenth ISS-4 instance.** No re-trigger; no debug slice.

## Verified (parsed from the committed logs, not the report's §(c))

- **Scope:** work commit = 9 `docs/worklogs/SG-214_*` files ONLY (verified via `git show` on the work HEAD, not the range stat — the range includes SG-213's landed files). Zero product bytes (rider only).
- **A1:** exactly ONE build (exit 0, 16 s) + ONE recreate (exit 0, 1 s), lane socket only, zero denials. New container `d45005fb` (Created 19:48:15Z, image `98f8af1f` == manifest sha, RestartCount 0, healthy) replaced `5f82f760`. Health green start/end + 13 GETs all 200.
- **A2 served bytes:** JS `47c65dea`/`index-DbppHp6C.js` → `8bab60ce`/`index-ZkOUf-iS.js`; CSS `c3b58cda` byte-identical (no CSS delta — expected); the rule's read point `catalog-content-column` 0→1 with compiled context on live GETs (identifier markers adjudicated non-discriminating, minification — same shape as SG-210's I2, disclosed); served == in-image `/app/static` bytes `cmp 0` ×3; image Id == manifest == container Image. JS-vs-SG-212-local-dist delta explained (image bakes `VITE_API_BASE=dynv6`, +54 B consistent; candidate explanation labelled, source tree identical). DB `e6bef157` identical ×3, 28 tables, alembic head unchanged. Focused suite `3 passed (3) / 77 passed (77)`, derivation re-derived on target (union L1+L2+L3 with named exclusions, counts 37+23+17 reconciled); full suite not re-run per `D443` on the unchanged tree (stated).
- **Smoke skip (finding 5):** browser run of the served origin skipped with four stated reasons (would XHR the baked dynv6 base — outside lane-only reads; local serve wouldn't exercise the production shape; SG-212's smoke stands on this tree; bytes proof gates). Packet allowed "report either way" — honoured. `docker cp` read disclosed under the packet's byte-proof allowance (same as SG-210). Neither is a breach.
- **A3:** 457 s vs ≈400 s (+57 s, stated `G-A9`); no command over 60 s (longest: 16 s build). **A4:** bound notes-ref, first line exact, Work-HEAD recorded, pushed + read back. **Contract:** 0.50.0 echoed with live proof.
- **F-SG213-1/2 style premise check:** packet premises (served pre, product delta, route, lane, DB) re-verified EXACT, no correction owed.

## Rating

**Holistic: 98/100, no flag.** One build + one recreate + byte-proof with the rule marker live in the bundle, derivation noise recorded as-is (L2 first-attempt, JS-base delta, I2 adjudication all disclosed). `deduction_attribution`: empty (nothing deducted). `slowest_waste`: `none`. Guards: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10.

## Dispositions

| Item | Destination |
|---|---|
| SG-212 product SERVED live (`d45005fb`/`98f8af1f`/`8bab60ce`) | **live==tree through SG-212** (STATE updated); standing directives discharged for this delta |
| Close-release (standing D-22 rule) | DUE AT SESSION CLOSE on the served bytes (`release-2026-10-17` covers through SG-208; the SG-212 delta needs its attestation+tag at close, not now) |
| Runner `report_unreadable`, **17th instance** | Desk #84 (no re-trigger) |
| L3 queue | **EMPTY — stage ends.** All open items need owner decisions (list below). Next slices launch only on answers |

Harness context-size reading unavailable; no conclusion made.
