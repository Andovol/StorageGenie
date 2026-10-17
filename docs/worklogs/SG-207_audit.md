# SG-207 audit — D-12: Raw Data panel removed, drawer intact, rated 98

Immutable audit: base `145d297` → work `476bd42` (2 product files, +5/−37) → evidence `da22a23` (13 files) → scope `8b99866` → report `4e79dd5` → receipt `478c77a`. Local `--ff-only` to the exact tip (`478c77a` == origin/automation at pull); tree clean. Trigger exit 0; engine `report_unreadable ... reason=report_missing`; status verb `inactive reason=report_missing`. Against that: the Coder's receipt note `Dispatch-ID: SG-207 | Report: docs/worklogs/SG-207_report.md | Work-HEAD: 8b99866...` IS on the remote — mapped-fetch read-back `show_exit=0` verified by this audit at the fresh fetch. Per `DISPATCH.md` §2: receipt present → NOT failed. **Tenth ISS-4 instance.** No re-trigger; no debug slice.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **Product diff** (`145d297..8b99866 -- frontend/`): ONLY `ItemInspectorDrawer.tsx` (−25: section, `rawOpen` state, `rawJson` memo, Chevron imports) and `drawer.test.tsx` (raw test → absence test: toggle absent, `/^raw-/` testid family absent, no `<pre>`). `useMemo` still consumed 3× elsewhere (`:87-88,:94`) — no dead import. Exactly the authorised removal.
- **FAIL-then-PASS (both committed, `SG-207_verify.log`):** RUN 1 pre-change targeted run green (1 passed/16 skipped — the deleted test clicking the role matcher; the rc=127 `npx` miss executed nothing and was re-run, both lines kept); RUN 2 full suite `30 passed (30) / 298 passed (298)`, rc=0, replacement absence test green. `PG-EV-09` holds.
- **Grep gates (`SG-207_scope.txt`, committed):** `rawJson|raw-json|Raw data` → rc=1 EMPTY tree-wide; production-files `raw data` → rc=1 EMPTY; the single remaining token is the mandated negative matcher `drawer.test.tsx:198` — finding #2's PB-6 design call (literal-in-test vs empty-tree tension) is sound, disclosed, and keeps both literal greps green. Non-vacuous: the pre-change green click proves the matcher discriminates.
- **Served smoke:** candidate served on loopback, drawer opened on the real page; all gates true (drawer present, 0 raw nodes, 0 pre nodes, 0 raw buttons, sections intact, 5 inputs, 2 AI buttons, text tail ends at the AI notice). Served-byte check: base bundle carries `Raw data`×1 + `raw-json`×1, candidate 0× all three with `Generate Context Scene`×1 control present. Screenshot opened by this audit (D425): drawer end shows AI actions + honest note, nothing after; sections/inputs/tabs intact; masking holds (no legible PII); no clipping/overlap/data anomaly. Light theme only — acceptable (removal is theme-independent; both themes share the section).
- **Scope:** `145d297..da22a23` = 15 files (2 product + 13 evidence); outside-pattern grep rc=1 EMPTY. Health identical start/end. Contract 0.50.0 echoed with live proof.
- **Elapsed:** 842 s vs ≈450 s (+392 s, stated `G-A9`). Cause: two smoke self-corrections (~320 s: wrong `/catalog` route assumption ×2 attempts, no-op scroll ×1) + recon. Root: the PACKET never named the Catalog route — `App.tsx:188-199` puts it at `/`, and no `/catalog` route exists. Packet-side premise gap (mine), recovered in-slice with the full diagnostic trail committed (attempts 1-4). Consequence: SG-208's packet amended this turn to pin the route. One point of signal, no deduction beyond the packet attribution below.

## Rating

**Holistic: 98/100, no flag.** Removal exact, absence proved three ways (suite + greps + served smoke with screenshot), disclosure exemplary (rc=127, all attempts, design call all on the record). `deduction_attribution`: packet (route premise gap; recovered in-slice at the cost of the overage). `slowest_waste`: `none` (every phase's output used — including the diagnostic attempts). Guards: PG-EV-02/03/05/09; PG-SC-05/09/12; PG-IC-01/07/08/09; PG-PR-01/03.

## Dispositions

| Item | Destination |
|---|---|
| D-12 removal complete in tree | Serve rider after SG-208 (production still serves the pre-change bundle — REMAINING, standing directive owns it) |
| SG-208 packet route gap | **Amended this turn** (`Catalog route is /` + SG-207 finding reference) |
| Runner `report_unreadable`, **10th instance** | Desk #84 (no re-trigger) |
| SG-208 (D-13) | **Dispatched this turn after push** (L3 flow) |
| SG-209 (D-17) | Queued after SG-208; D-14(c-monthly) still owed by owner |
| Auth-live / native input / backend | Untouched, stated |

Harness context-size reading unavailable; no conclusion made.
