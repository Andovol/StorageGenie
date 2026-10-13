# SG-183 — One root-cause correction of SG-179 browser verification

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo actual resolved commit separately.
**DATABASE: production GET observation only; optional synthetic fixtures confined to disposable DB and storage.**
**Restart: none.**
**Autonomy: L2, the ONE correction pass for SG-179, within RECOVERY-D1 approved audit scope.** SG-179_audit.md records 91 FLAG:TRUST(phone-clean-verification); no product/UI repair or acceptance clearance. SG-175's safety hold remains. SG-180–182 are subsequent audits, not part of this correction.

## Why this exists — verified discrepancy, hypotheses about its producer

SG-179's stored phone samples labeled 390x844 contain measure.vw=811–853, nav.clientW=390 and nav.scrollW=811–853, yet overflowX=0. Independent source extraction is `SG-179_architect_geometry.json`: ten phone navigation overflows; ten desktop samples have nav scroll/client widths equal; nine tablet navigation overflows versus the report's eight. contentW is not an authoritative viewport (1100 desktop container). Explain the actual browser/device/layout relationship; do not force a width just to satisfy the old verdict. The previous raw-CDP driver was left only at `/tmp/opencode/sg179/cdp.mjs`; its source was not committed. Reuse it if present, verify its current contents and preserve the corrected executable source under this slice's evidence ceiling.

SG179-F3 inferred WCAG 2.5.8 failure from dimensions alone. Official W3C guidance permits spacing/equivalent/inline/user-agent/essential exceptions; height below 24 is insufficient. Contrast captures omit foreground/background pairs and the algorithm. Blanket transparent text in screenshots also makes public UI labels/contrast unreadable. These are audit defects to correct, not a request to fix the application.

## G1 — Persist and correct the existing measurement path

Reuse the existing browser/capture code and actual loopback-served frontend bytes; record build hashes, current browser executable/version and exact launch flags/transport. No new dependency or service. Do not repeat `/usr/bin/google-chrome`'s known-failing launch or optional Docker listing. Container/image remains UNVERIFIED if no established read grant provides it. Any NEW privileged denial is whole-slice STOP under PB-2, including optional reads; no sudo, alternate identity/mount/socket or security weakening.

Publish the runnable driver and its command with no credentials/customer values. A driver may use ephemeral local GET responses from the actual backend; state clearly that this is served-build rendering with loopback GET fulfillment, not authenticated public-URL proof. Block non-GET before forwarding, record actual methods and reject counters. Verify that this guard rejects a harmless synthetic attempted mutation in an isolated transport control, never by sending one to production. No new auth, credential lookup or browser profile access. Keep 401/public-URL limitation explicit.

At every capture record requested device dimensions, devicePixelRatio, browser layout/visual viewport fields, documentElement/body client/scroll sizes and measured component client/scroll sizes; name the DOM/API source of each. Capture rectangles and visible viewport intersection for the offending Nav/elements. Determine document reflow and component clipping from the relevant real viewport/element relationship, not a denominator that expands with overflowing content. Do not inject layout-fixing CSS, change app styles/meta or crop/stretch evidence to hide overflow. Privacy masking occurs AFTER unmasked geometry/color measurement; record that order.

Compare the same measurement implementation on: the existing known-fitting desktop Nav; a tiny scratch page fitting the viewport; and the same scratch page with deliberate overflow whose mutation is asserted landed. Wrong outcome must fail. Then re-observe all ten original routes at the requested narrow/tablet/desktop dimensions (390x844, 834x1112, 1440x900, exploratory inherited choices, not universal coverage). Account for actual layout expansion rather than claiming viewport equality where it is false. Commit measurements, exact commands and control failures. If the environment cannot render a case, say UNVERIFIED instead of clean.

## G2 — Standards-aware accessibility evidence

Use official W3C sources already in SG-179_audit.md; verify applicability, not a generic size cutoff. Collect rectangles for all adjacent relevant active targets, their actionable area, state and applicable exception evidence. For SC 2.5.8, show a spacing-passing small control and a spacing-failing adjacent-control scratch case using the same evaluator; assert the fixtures' geometry before trusting results. Unmodified native-control or inline exceptions require actual evidence; do not assume them from tag names. Return confirmed failure / meets criterion for sampled controls / UNVERIFIED when exceptions cannot be established. Keep ergonomics judgement separate from conformance. No UI changes.

For reported muted small text, retain computed RGBA foreground/background, ancestor/backdrop/opacity/compositing context, font size/weight, source selector and exact unrounded contrast value. Unknown image/backdrop means UNVERIFIED, not guessed white. Persist calculation code and test known contrast controls before applying it to rendered samples. The same shipped pair must be evaluated in its real context; source token names or masked pixels do not establish runtime contrast. Cover the originally cited Catalog/AssetDetail/Review slots and any directly affected shared controls; do not widen into a whole redesign.

## G3 — Useful sanitized evidence and corrected verdict

Keep public navigation/action/error/empty-state text readable in representative screenshots; mask private product/household values, identifiers and evidence photos locally after collecting metrics. Do not retain raw private screenshots/data in committed artifacts. Preserve slot identity and geometry so an independent reader can see clipped labels, focus and relevant data-state placement. Include narrow/tablet/desktop Nav, Review geometry and contrast representatives; other routes may use structured metrics rather than redundant screenshots. Screenshot record identifies viewport/build/measurement stage and redaction method. Distinguish keyboard focus styling from actual focus visibility within the visual viewport.

Publish a corrected per-route layout table and per-control accessibility disposition, cross-referenced to SG179-F2/F3/F4 and REC-ISS15–17. Do not rewrite SG-179's historical report/logs. No need to repeat the already accepted Python/Inbox regression proofs. State retained findings, retracted claims, new confirmed defects and unresolved questions; every remaining item has a destination in the existing audit chain or consolidated plan.

## Constraints / acceptance / receipt

- Read only this project, its declared contract/runtime paths and this session's scratch. Write ceiling `docs/worklogs/SG-183*` only; temporary helpers removed before publish. No product/config/test/lockfile/schema/migration edits, package upgrade, service rebuild/restart, production write, paid provider request, credential/permission change or another project's path/data. Existing host browser binary execution is allowed; unrelated cache/profile/credential inspection is not.
- Health GET start/end, expected contract 0.46.0 with actual source echo. Current lane bound/actual elapsed from authoritative runner, not a worker-clock approximation. Ordinary commands 120s, browser/control command 600s (uncalibrated inherited bound); visible timeout, no watcher. Publish partial evidence/receipt through PB-6 if constrained; do not retry this correction again without owner disposition.
- A1: persisted runnable driver/measurement schema and raw observations discriminate fitting/overflow controls; current phone/tablet/desktop findings follow actual viewport and element geometry.
- A2: WCAG size/spacing/exception and contrast verdicts have real inputs plus failing/working controls; uncertain cases remain UNVERIFIED. Official criterion source cited.
- A3: privacy-safe visual evidence remains useful for public UI/data-state verification; masking order and real served-build provenance disclosed; no public-URL/container proof inferred.
- A4: first token SG-183, `docs/worklogs/SG-183_report.md`; resolved ref/commit, WORK_HEAD, settings/contract identity, health, runtime, scope and all constraints; FIRST READ / DURING EXECUTION / REMAINING; named committed logs for every claimed run/control/measurement. One honest partial correction is better than false coverage.

Guards: PG-EV-01/02/03/05/06/09/13; PG-SC-01/09/10/12; PG-IC-01/07/09; PG-DP-03; PG-PR-01/03/04/10.

Bound receipt: commit with `Dispatch-ID: SG-183` trailer; note on `refs/notes/storagegenie-coder-reports`, first line `Dispatch-ID: SG-183 | Report: docs/worklogs/SG-183_report.md`, plus Work-HEAD; push automation and notes ref; read back remote note and annotated commit. No legacy finalizer. Architect audits/rates before subsequent stage work.
