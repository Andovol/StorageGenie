# SG-205 — D-8 Option B: fix dark .focus-ring contrast at theme/tokens.css:173, re-verify every focus surface both themes

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none. Restart: none** (lane-local serve for measurement only; prod serve is a follow-up rider, not this slice).
**Autonomy: L2.** Basis: owner D-8 approval 2026-10-17 (`docs/decisions/2026-10-17-density-pick-and-close.md` — Option B adopted, C/D not approved). One retry max; a retry fixes the root cause only.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

D-8 adopted **Option B** (`docs/proposals/2026-10-17-density-proposal.md` option 2): the dark-theme keyboard focus ring sits at **1.7559:1** vs its surrounding toolbar (light: **9.8813**), below the 3:1 non-text contrast floor. Shared `.focus-ring` rule, app-wide, not density-specific. The SG-204 simulation (injected `html.dark .focus-ring:focus-visible { outline-color: hsl(var(--link)); }` on the real page) measured **7.4784** vs toolbar, 4.2589 worst case vs the focused button's own face, light unchanged at 9.8813. **Option C** (native default-button faces off-token in dark) is NOT approved — observe-only if encountered. **Option D** (width-adaptive default) needs an owner requirement — out of scope entirely.

## Handed-over facts (expected — re-verify on target, `PB-1`; correct this packet openly on any mismatch)

- Defect rule (expected): `frontend/src/theme/tokens.css:173` `.focus-ring:focus-visible { outline: 2px solid hsl(var(--primary)); }` (NOT `styles/` — `F-SG204-1`; packet path verified against the tree at authoring). Dark `--primary` is `2 41% 30.6%` (tokens.css `:44`), dark `--link` is `2 41% 72%` (`:47`).
- Sibling rule in the same file (expected): `.file-pick:focus-within` at tokens.css `:288-291` also outlines in `hsl(var(--primary))`. Enumerate on target whether further `--primary` outline usages exist.
- Measured control (expected): `frontend/src/components/shell/CatalogToolbar.tsx:5` (`Density` type), `:13-15` labels, `:44-45` props, `:63` `THEMED_CONTROL_CLASS`, `:168` control group; default `useState<Density>("grid")` at `frontend/src/routes/CatalogPage.tsx:40`; grid breakpoints `frontend/src/components/catalog/ProductGrid.tsx:15-18` (2/3/4/5 at 768/1024/1536), table branch `:331`.
- Prior artifacts: `docs/worklogs/SG-203_measure.json` (focus probes `phases.density.focusProbes`), `docs/worklogs/SG-204_measure.json` (`renders[option 2].ringBefore/ringAfter`), driver pattern: served lane build + raw CDP, read-only GETs fulfilled from loopback, fresh temp profile, masking after measurement. Lane `RUN_BUDGET_S=2100` (read `/etc/dispatch/storagegenie.conf` read-only at execution; never assume the number).

## G1 — fix the dark focus-ring contrast

- Give `.focus-ring:focus-visible` a dark-adapted outline tint that clears **≥3:1 against EVERY surrounding it renders against**, following the existing token pattern (candidate: the dark `--link` tint, per the measured simulation — the Coder decides the exact shape and reports why; what the choice turns on: the ring must clear the floor on toolbar, card, muted and button-face surroundings in dark while the light ring stays ≥3:1 and visually unchanged).
- Light theme: **no regression** — the light ring stays ≥3:1 (expected 9.8813; measure, don't assume).
- Same-file sibling rule: any OTHER focus-indicator rule **in `frontend/src/theme/tokens.css`** (expected: `.file-pick:focus-within`) that measures **below 3:1 in dark** is fixed in the same one-line override pattern in this slice; each such fix named in the report. Anything outside that file measuring below floor is a reported REMAINING finding for the next slice — NOT fixed here (Option C stays untouched: no native-button faces change).

## G2 — enumerate every focus-indicator usage on target

- A handed list is a fact too: do NOT work from one. State the criterion (every rule that paints a keyboard-focus outline plus every `focus-ring` class use on a focusable), enumerate the set on the target (grep the tree + the served bundle), and report the difference against the expectation (28 files carry `focus-ring`; `.file-pick` sibling) in EITHER direction — an under- or over-count STOPS and is reported before writing (`PG-IC-08`).
- Measure the ring contrast on every DISTINCT background context the enumeration finds (toolbar, card, muted, button faces, inputs), BOTH themes. All ≥3:1. Worst case per context reported with numbers.

## G3 — prove it on the real page, base vs candidate

- Drive the REAL Catalog on the lane harness (served build + raw CDP; the SG-203/SG-204 driver shape, reused by COPY under `docs/worklogs/SG-205_*`, never an edit of committed artifacts). BEFORE at the base (pre-change file served identically) then AFTER on the candidate; BOTH runs committed to `docs/worklogs/SG-205_measure.json`, the failing BEFORE gate output committed, never prose-only (`PG-EV-09`).
- Contrast computation gate seen to fail (`PG-EV-01`): feed it one deliberately wrong input (e.g. the 1.7559 dark reading against a ≥3:1 gate; a planted wrong expectation) and show it failing in the same run.
- Full frontend suite ONCE on the candidate (`vitest run` — expected `frontend/package.json:9`); on the base, nothing (no new unit-test rows; the probe is the FAIL-then-PASS). Health `{{HEALTH_CMD}}` start+end with delta (expected both `{"status":"ok","db":"ok","storage":"ok"}`; any other value STOPS per `PB-6`).

## Constraints

- **Scope ceiling (rule, grep-gated — `PG-SC-05`):** product bytes ONLY in `frontend/src/theme/tokens.css`; evidence ONLY under `docs/worklogs/SG-205_*` (driver copy, measure JSON, logs, shots). No backend/Python, no config/test/lockfile/schema/migration change. Prove the ceiling with a diff file-list + a grep over the diff for any path outside the two allowed roots — the gate checks the artifact, never the exit code (`PG-EV-02`).
- **Cross-product (`PG-IC-01`):** no blanket exclusion collides with G1–G3 — each criterion names the file it must touch transiently (lane build serves the tree; the driver reads the served bundle) and no constraint forbids it. Reads: lane CDP only; loopback GETs; zero credential/cookie forwarding; driver-injected ACAO only; zero non-GET forwarded; no production/evidence-store writes; fresh temp profile; DB/storage untouched (health identical, no restart).
- **Out of scope (stated, not silent):** Option C native-button faces (observe + report numbers only); Option D (no requirement on record — do not invent one); auth-live + live-container rendering (no grant); native zoom / physical touch (emulations only, stated).
- No interactive prompt or polling loop; no sudo; no alternate identity/mount; no host config change; no secret in any log or artifact. `PB-2`: ANY privileged denial STOPS the whole slice. `PB-3`: an empty measure (zero contexts, zero samples) is a FAIL, never a pass. State the PROPERTY (`PG-EV-05`): "the dark ring reads ≥3:1 against `<context>`", never only the command that read it.
- Hang bounds: ordinary reads 120 s; browser/measurement runs 600 s; lane build 600 s; state any visible timeout finding; never approach idle kill 900 s. Simplicity (`G-A7`): a token tint + measurement; no new machinery. No waste cut owed — SG-204's audit named `slowest_waste = none`.
- Expected duration ≈ 750 s (Architect record, `G-A9` uncalibrated; derived from lane precedent SG-203 731 s / SG-204 688 s for the same served-build + CDP-measure shape — NOT a slice budget; the lane enforces `RUN_BUDGET_S`).

## Acceptance criteria

- **A1:** `frontend/src/theme/tokens.css` is the only product file changed; the dark `.focus-ring` reads **≥3:1 on every measured surrounding** (numbers per context, both themes); the light ring is unchanged and ≥3:1; BEFORE (base, <3:1 dark) and AFTER (candidate, ≥3:1) both committed to `SG-205_measure.json`; the must-fail arm transcript committed.
- **A2:** the enumeration (criterion + found set + delta vs 28-file expectation either way) is in the report; every distinct background context measured both themes, worst cases named; any sub-floor non-`.focus-ring` surface outside tokens.css is a REMAINING finding, not a silent pass.
- **A3:** command + evidence logs committed; full frontend suite green once on the candidate quoted with counts; health start+end with delta; report `docs/worklogs/SG-205_report.md`; elapsed vs the ≈750 s expectation stated; all constraints answered on explicit lines; FIRST READ / DURING EXECUTION / REMAINING dispositioned. First report token `SG-205`.
- **A4:** notes-ref receipt on `refs/notes/storagegenie-coder-reports` published and mapped-fetch/read-back verified, first line `Dispatch-ID: SG-205 | Report: docs/worklogs/SG-205_report.md`, Work-HEAD recorded, branch/report push complete. Use the bound lane receipt, never the retired finalizer.

Guards invoked: PG-EV-01/02/03/05/08/09; PG-SC-05/09/12; PG-IC-01/07/08/09; PG-PR-03/04. Stop follows `PB-6`.
