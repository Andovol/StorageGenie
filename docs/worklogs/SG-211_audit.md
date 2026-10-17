# SG-211 audit — D-22 release: live==tree attested, `release-2026-10-17` published, rated 98

Immutable audit: base `394e4e7` → work `d1e2225` (release record + 3 evidence logs, +144, zero product/config/test bytes) → report `80fb84e` (+health) → receipt `a21f4d2`. Local `--ff-only` to the exact tip (`a21f4d2` == origin/automation at pull); tree clean. Tag `release-2026-10-17` fetched and inspected locally: annotated, tagger Andrei P, message carries the served shas, object `6fec36d` → commit `394e4e7` (the verified HEAD); `ls-remote` confirms it on origin. Trigger exit 0; engine `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-211 | Report: docs/worklogs/SG-211_report.md | Work-HEAD: d1e2225...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit at the fresh fetch. Per `DISPATCH.md` §2: receipt present → NOT failed. **Fourteenth ISS-4 instance.** No re-trigger; no debug slice.

## Verified (parsed from the committed artifacts, not the report)

- **Live re-read (`SG-211_live.log` + record table):** all 14 values equal SG-210 poststate (container id + created stamp, index/JS/CSS shas + sizes, image id, DB sha + table count + alembic head, health). Zero writes, zero restarts, no build — attestation class.
- **Tag placement (sound):** on `394e4e7` (the verified tree HEAD), not on the record commit — correct, since the record attests that HEAD and no product byte differs between them. Message quotes the served shas + record path + D-22 authority. First tag on record (namespace was empty — verified pre-creation per packet).
- **Scope:** work commit = record + 3 logs ONLY; report + health + receipt follow. **Contract:** 0.50.0 echoed with live proof. **Elapsed:** 174 s vs ≈300 s (under). No command over 60 s. No test run — correct (zero product bytes; `CO-25` attestation needs no product failure).

## Rating

**Holistic: 98/100, no flag.** Attestation complete per value, tag correct and published with read-back, record committed with authority + scope + what's-not-in-it. Nothing deducted. `slowest_waste`: `none`. Guards: PG-EV-02/03/05; PG-SC-09; PG-IC-01/07; PG-PR-03.

## Dispositions

| Item | Destination |
|---|---|
| First release published (`release-2026-10-17` on origin) | D-22 now-step DONE; standing close-release rule owns every future close |
| Runner `report_unreadable`, **14th instance** | Desk #84 (no re-trigger) |
| SG-212 (D-21 values) | **Dispatched this turn after push** (L3 flow) |
| STATE/ratings | Updated this turn |

Harness context-size reading unavailable; no conclusion made.
