# SG-326 audit — screenshots of polish A and B (Muse 1.3 Contributor, xhigh)

**Verdict: 95, no flag. Six shots, every DOM proof present; the polish screens hold; the rider (SG-327) may serve them.**

| Check | Evidence | Result |
|---|---|---|
| Dispatch | `result=done id=SG-326 exit=0 published_head=yes`; 605 s by its stamps | ok |
| Scope | `git diff --stat 87ae14e ea8425d`: `docs/worklogs/SG-326_report.md` + `SG-326_shots/` only | ok |
| Shot 02 (opened by me) | table headers *Use by*, two *Olive Oil* rows *3 Feb 2031* / *6 May 2030*, no *Status* / *Dimensions/Specs* | matches report |
| Shot 05 (opened by me) | *Check this item*, *This may already be in your catalog*, three choices, no *Save edits* / *Accept* / *Hold*, labels Name / Kind of item / Status / Use by / Lot, use-by a date field showing *06/18/2032* | matches report |
| No provider | fake provider + `_post` guard raising on any network attempt; 1 scripted invocation, no raise | ok |
| Honesty | corrected its own seed (soup `asset_type`) and re-shot; called a probe's `wraps: true` a padding artifact the image does not show — layout claim checked against the image this time (the SG-321 weakness did not recur) | good |

## Issues

| ID | Issue | Status |
|---|---|---|
| I8 | Review card shows raw values in inputs: *Kind of item* `unknown`, *Status* `ACTIVE` (shot 05) | OPEN — next polish touch, after the trial unless the owner asks sooner |
| I9 | Use-by date field shows the value (`2032-06-18` → *06/18/2032*, browser order, P2 owner-settled) | RESOLVED — the field is not empty |
| I11 | *Confidence: 0.97 · Source: extraction / deterministic* under every field — developer words left by P12(g) (no label existed) | OPEN — same next polish touch |
| I12 | Page title *Review workspace* above *Check this item* — two headings, the first developer-ish | OPEN — same next polish touch |
| I13 | Capture form's formats note still 11 px (shot 04) | OPEN — same next polish touch |
| I14 | Report: font load not proven (`document.fonts`), computed style only | no action — same caveat as SG-321r1 |

Deduction: none material; 95 rather than higher because shot 05's design note calls the white card on paper "intentional" without naming what makes it so.

`slowest_waste`: none.
