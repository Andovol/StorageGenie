# SG-210 audit — serve rider: SG-207+SG-208 product delta live, rated 98

Immutable audit: base `145277d` → work `4952c0a` (8 evidence logs, +531, zero product/config/test bytes) → report `15a9903` → receipt `90779a8`. Local `--ff-only` to the exact tip (`90779a8` == origin/automation at pull); tree clean. Trigger exit 0; engine `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-210 | Report: docs/worklogs/SG-210_report.md | Work-HEAD: 4952c0a...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit at the fresh fetch. Per `DISPATCH.md` §2: receipt present → NOT failed. **Thirteenth ISS-4 instance.** No re-trigger; no debug slice.

## Verified (parsed from the committed logs, not the report's §(c))

- **Scope:** `145277d..4952c0a` = 8 `docs/worklogs/SG-210_*.log` files ONLY. Zero product bytes (rider only).
- **A1:** exactly ONE build (exit 0, 15 s) + ONE recreate (exit 0, 1 s), lane socket only, zero denials. New container `5f82f760` (Created 17:57:53Z, image `38fcae5e` == manifest sha, RestartCount 0, healthy) replaced `f2055f3b`. Health green start/end + 14 post-recreate GETs all 200.
- **A2 served bytes:** JS `dd4f1bd0`/`index-Cv0EK3ka.js` → `47c65dea`/`index-DbppHp6C.js`; CSS `c3b58cda` byte-identical (no CSS in the delta — expected); removals live on served GETs: `raw-json` 1→0, `Raw data` 1→0, `"aria-label":"Household"` 1→0 (Household ×21→×3, all 3 adjudicated non-markup: context error string + kept fallback message); served == in-image `/app/static` bytes `cmp 0` ×3. DB `e6bef157` identical ×3, 28 tables, alembic head unchanged. Focused suite `9 passed (9) / 110 passed (110)` — derivation reported (L1 focus-ring 3 + L2 selector-absence 5 + L3 raw-absence 1), full suite not re-run per `D443` on the unchanged tree (stated).
- **`docker cp` read (finding 6):** the in-image byte extraction the packet's served==build proof requires — classified as a read, no state change, third docker CLI surface disclosed with the strict-reading record. Sound judgment under `PG-SC-12`, not a breach: the packet demanded the comparison and named no other way to obtain the bytes. No deduction. Contrast with SG-206's probes (un-ordered capability checks): this one executes the packet's own proof obligation.
- **Disclosures, all immaterial:** `rawJson` camelCase pre-0 on served bytes (minification artefact, I2 — reconciled, both counts reported); L2 derivation first attempt noise (corrected in place, (a)4); L3 leg added on the SG-207 analogue principle (disclosed, (a)5). Packet premises re-verified EXACT (finding 1).
- **A3:** 510 s vs ≈400 s (+110 s, stated `G-A9`; orientation + derivation, no waste). No command over 60 s. **A4:** bound notes-ref, first line exact, Work-HEAD recorded, pushed + read back. **Contract:** 0.50.0 echoed with live proof.

## Rating

**Holistic: 98/100, no flag.** One build + one recreate + byte-proof, served removals proved present-in-bytes with pre/post discriminating controls, derivation noise recorded as-is. `deduction_attribution`: empty (nothing deducted). `slowest_waste`: `none`. Guards: PG-EV-02/03/08; PG-IC-01/07; PG-DP-01/02; PG-PR-03/04/06/10.

## Dispositions

| Item | Destination |
|---|---|
| SG-207+SG-208 product SERVED live (`5f82f760`/`38fcae5e`) | **live==tree through SG-208** (STATE updated); standing close-deploy directive discharged for this delta |
| Runner `report_unreadable`, **13th instance** | Desk #84 (no re-trigger) |
| L3 queue | **EMPTY — stage ends here.** No approved executable work remains; every open item needs an owner decision (list below). Next slices launch only on owner answers |
| STATE/ratings | Updated this turn (the rider wrote no state file, per its REMAINING) |

Harness context-size reading unavailable; no conclusion made.
