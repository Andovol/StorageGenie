# SG-199 — Measure touch/zoom/dark on the new nav shell (read-only; feeds the density proposal)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none. Restart: none.**
**Autonomy: L3.** D16 stage flow + owner D-4 approval 2026-10-16 (measure-first; recorded `docs/decisions/2026-10-16-density-scope-d4.md`). Same class as SG-183/SG-190: lane browser harness, read-only GETs, committed evidence only. Dispatch settings ride the trigger, never this packet. No product repair is implemented here.

Authoring date (metadata, never a gate): 2026-10-16.

## Why this exists

SG-190 REMAINING left zoom/touch/dark-theme/authenticated-live coverage unmeasured (SG-183's recorded limits); SG-196 put a new selector, badge and alerts into the nav that no axis has ever rendered. D-4 ordered facts before the density control. Proven lane capabilities (re-verify on target, do not trust): host Playwright-cache `chrome-headless-shell` + raw CDP over the DevTools websocket, dependency-free (SG-183); served-build rendering with loopback GET fulfillment (86 GETs precedent — the public API answers 401 without credentials, so fulfillment stands in for the authenticated origin and is disclosed as such); committed drivers `docs/worklogs/SG-183_driver.mjs` + `SG-190_driver.mjs`.
Dark mechanism on this tree (verified by the Architect 2026-10-16): `sg-theme` localStorage (`ThemeProvider.tsx:20`, `light|dark|system`), `.dark` class on `<html>`, `.dark` token block in `tokens.css` (link-token AA checks already in `theme.test.tsx`).

## G1 — Touch emulation (mobile + touch)

Render the 6 sampled routes (Catalog, Inbox, Planning, Analytics, Capture, asset detail — SG-183's sampled set) under touch emulation (`mobile:true`, touch points enabled). Measure per route: document overflow (SG-183 denominator shape), nav selector/badge/alert operability by touch (tap, no hover dependence), smallest interactive target sizes in the nav shell with spacing/exception semantics stated (acceptance source, not a conformance claim: WCAG target-size-minimum). Committed screenshots per route; every image opened by the Coder (`D425` — the audit opens every one too).

## G2 — Zoom reflow

200% browser zoom on the same 6 routes: overflow counts + which shell elements (nav menu, selector, badge, cards, tables) break the reflow first. Same denominator reporting as G1. Density inputs: card/table density at 100% vs 200% recorded as numbers + shots (feeds the later density proposal; no control designed here).

## G3 — Dark theme

Seed `sg-theme=dark` pre-load (fresh temp profile, same privacy masking as SG-183/190 AFTER measurement). Same 6 routes: committed screenshots + sampled contrast numbers on the new surfaces (nav selector, badge, household alert, role=alert branches) with opaque pairs and exception semantics stated (SG-190 A1 shape). Muted/link tokens already unit-covered; this measures the served render, not the tokens.

## Constraints

Scope ceiling: `docs/worklogs/SG-199*` ONLY (driver, controls, measure JSON, shots, report). No product/config/test/lockfile/schema/migration change; `git status` clean apart from the named evidence commits. Reads: lane CDP only; API GETs fulfilled from loopback `127.0.0.1:8003` (zero credential/cookie forwarding, `Access-Control-Allow-Origin` injected by the driver only); zero non-GET forwarded; no production or evidence-store writes; fresh temp browser profile; no restart; DB/storage untouched (health unchanged, start+end). Fulfillment fidelity (`PG-EV-04` price): every fulfilled response byte-compared against the direct loopback GET; any mismatch is STOP, not a footnote. Controls phase first (harness self-checks, SG-183 `controls.json` precedent; failed controls are failed prove executions per `CO-35`). Masking AFTER measurement, layout-safe. Auth-live and container/image identity are EXCLUDED (no credentials requested, no host grant — blocked items, stated not silent). Ordinary reads 120 s; browser/control runs 600 s; visible timeout finding; never approach idle kill 900 s. No interactive prompt or polling loop. No sudo, no alternate identity/mount, no host config change. No secret in any log or artifact. `PB-2`: ANY privileged denial STOPS the whole slice. Full suite untouched/unrun (no product in scope — stated, not silent). No waste cut owed (`slowest_waste = none`, SG-198).

## Acceptance and report

- A1: per-route overflow counts on all three axes with denominators; touch target sizes with exception semantics; zoom breakage ordered by element; dark contrast pairs with exceptions — every number committed in one measure JSON with its DOM/API sources named (SG-183 schema precedent).
- A2: committed screenshots per route per axis, every one opened by the Coder and dispositioned for UI + layout + data issues together (a written screenshot audit alone is not evidence).
- A3: command + evidence logs, report `docs/worklogs/SG-199_report.md`; elapsed per leg vs ~1200 s uncalibrated expectation (SG-190 shape, stated per `G-A9`); constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token SG-199. Density-relevant observations (card/table density at 100/200/light/dark) recorded as a named section for the proposal slice.
- A4: notes-ref receipt + mapped read-back, `Work-HEAD` recorded, pushes complete; bound lane receipt, never the retired finalizer.

Guards invoked: PG-EV-01/02/03/04/05/07/09/13; PG-SC-01/02/03/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/07/10. Stop follows `PB-6`.
