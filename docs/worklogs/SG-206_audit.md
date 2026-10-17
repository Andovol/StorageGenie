# SG-206 audit — serve rider: SG-205 focus-ring fix live, rated 97

Immutable audit: base `ec8be4f` → work `b029593` (7 evidence logs, +313, zero product/config/test bytes) → report `3dd5b7c` → receipt `b1475e5`. Local `--ff-only` to the exact report-chain tip after rebase (`b1475e5` == origin/automation at pull; my two unpublished commits replayed on top, hashes `907dc39`/`a5a1c77`). Trigger exit 0; engine `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-206 | Report: docs/worklogs/SG-206_report.md | Work-HEAD: b029593...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit at the current tip (`c6f5284`, advanced past the transcript's `4d114c2` by runner partial-receipt notes; the Dispatch-ID note resolves). Per `DISPATCH.md` §2: receipt present → NOT failed. **Ninth ISS-4 instance.** No re-trigger; no debug slice.

## Verified (parsed from the committed logs, not the report's §(c))

- **Scope:** `ec8be4f..b029593 --stat` = 7 `docs/worklogs/SG-206_*.log` files ONLY. Zero product bytes — the rider changed the live service, not the tree (CO-48 class 1, stated in the report).
- **A1:** exactly ONE build (exit 0, 15 s, `SG-206_build.log`) + ONE recreate (exit 0, 2 s), lane socket only, zero denials on the lane. New container `f2055f3b` (Created 16:29:13Z, image `fe537fd4` == build manifest sha, RestartCount 0, healthy) replaced `d868f373`. Prestate read first; health 200 start/end + 6 post-recreate GETs all 200.
- **A2 served bytes** (`SG-206_poststate.log`): CSS `c3b58cda…` (4535 B) with BOTH rules on `hsl(var(--link))` IN the served bytes (live GET, `PG-SC-12`); JS `dd4f1bd0…` 325039 B pre==post (`cmp 0`); index.html asset name flipped (`index-DgiNiCw9.js` → `index-Cv0EK3ka.js`, F-SG206-1, bytes identical — mechanism labelled derived, measurement quoted); DB `e6bef157…` identical pre/post/post-tests, 28 tables, alembic head unchanged; `/v1/households` control hash unchanged; SPA routes 200. F-SG206-2 typo confirmed harmless (`e1e5ff63` == SG-202/205 records; target `c3b58cda` confirmed).
- **A2 suite:** `Test Files 16 passed (16) / Tests 191 passed (191)`, rc=0 (`SG-206_tests_frontend.log`). F-SG206-3 (MY packet error — the "SG-202 12-file set incl. four focus-ring tests" line was wrong; only `theme-adoption` of the four was in it): the Coder derived the union on target (`rg -l focus-ring ... *.test.tsx` = the four files) and ran 16 files, delta reported not bent. Packet-side miss, caught by design, +4 files in a 9 s suite — recorded, no separate deduction.
- **A3:** 407 s vs ≈400 s (+7 s, `G-A9` stated); phases all used; no command over 60 s; idle kill never approached.
- **A4:** bound lane notes-ref; push + mapped-fetch read-back; first line exact; Work-HEAD recorded. Retired finalizer not used.
- **Contract:** 0.50.0 echoed with live proof (host `CODER.md:3`, VERSION, bound names; `CODER_PRODUCTION.md` + `lang/python.md` read for the deployed-service slice). Chain equal on the controlled axis.

## The one deduction (coder): deviation #1

Two pre-sequence capability probes the packet never ordered — `sudo -n true` (refused by unit hardening) and bare `docker version` (default-socket permission denied) — against the packet's "zero denials tolerated" line. Mitigating, all true: both were read-only disclosure probes, neither was retried or routed around, every slice operation ran on the mandated lane with zero denials, and the Coder disclosed both verbatim with the stop-path reasoning written out. That is PB-2 working as designed (surface, don't route around), but the probes were still off-plan — one point, attribution `coder`. No safety breach (no privileged action executed; the default socket was never used), no scope breach, verdict unaffected.

## Rating

**Holistic: 97/100, no flag.** Every material requirement complete, authoritative verification + receipt valid, one disclosed off-plan probe deducted. `slowest_waste`: `none` (orientation/evidence legs all used). Guards: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10.

## Dispositions

| Item | Destination |
|---|---|
| SG-205 fix SERVED live (`f2055f3b`/`fe537fd4`/`c3b58cda`) | **live==tree through SG-205** (STATE updated); standing close-deploy directive discharged for this delta |
| Runner `report_unreadable`, **9th instance** | Desk #84 (no re-trigger); transcript notes the replay guard should now read receipt=present |
| F-SG206-1/2/3 | Recorded above; F-SG206-3 is a packet-side miss (mine), no deduction |
| SG-207 (D-12) / SG-208 (D-13) / SG-209 (D-17) | Queue order under L3; SG-207 dispatched this turn after push |
| D-14 owner items (monthly caps; Option C/D; R5 word) | Carried — see the standing outstanding-decisions list in STATE |
| Auth-live / native zoom / touch | Unexercised, stated |

Harness context-size reading unavailable; no conclusion made.
