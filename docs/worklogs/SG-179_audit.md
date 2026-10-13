# SG-179 — Useful journey evidence; responsive verdict rejected and one correction queued

Immutable base `06ff99824c824257b23ed2aad673845d0b74fa46` → work `631c5e2c51903435a50166224b7828d352d73cd4` → receipt candidate `bed7e218171a194eabf4a254427ed719ae35a243`. Forced-command status returned done/inactive at the 2026-10-13 16:35 Europe/Bucharest check. Mapped notes ref identifies SG-179, report, Work-HEAD and command-selected OpenCode / opencode-go/deepseek-v4.1-flash / max. Checkout fast-forwarded to the receipt candidate. Diff contains only allowed SG-179 evidence paths, no backend/frontend product changes.

Holistic rating **91/100**, Architect judgement, **FLAG:TRUST(phone-clean-verification)**. This is an inaccurate verification claim, not an accusation of intentional deception. The phone-clean verdict is rejected; usable findings are retained separately. One L2 root-cause correction pass is assigned to **SG-183**, before SG-180. No product/UI repair or deployment authorized by this audit.

## Accepted evidence and limitations

- Unchecked import produces CREATED with no candidates through real isolated routes; explicit /run advances it and produces a candidate. Actual Inbox render probe has no Run/Start/Retry for CREATED, while FAILED has an enabled Retry control. Probe body read; independent local re-execution passed one test (`SG-179_architect_probe.log`). The temporary copied test was byte-identical and removed afterwards. This confirms REC-ISS02 without concluding the backend runner is absent.
- Backend captures: 19 targeted tests passed. Frontend combined capture contains 52 passing tests in four unchanged regression files plus one failing transient probe (`screen.unmount` misuse); separate final probe capture passes. The report discloses the correction. Do not call the combined log wholly green. No local backend venv exists; no independent local backend run claimed.
- The Python proof uses a disposable DB/session dependency and temporary evidence root, fake provider and nulled keys before job execution. Real missing-original quarantine, candidate gate, expiry persisted readback and wrong-expectation controls are exercised. Inherited empty-host-directory names/sizes fingerprints do not prove production-volume content conservation; current isolation structure is separate evidence. That limitation remains REC-ISS13 / SG-180.
- Served-bundle identity is observed on the existing loopback service; public URL returned 401. Browser observations used served bytes with GET response fulfillment from loopback; this is not authenticated public-URL browser proof. Image/container identity stays UNVERIFIED; no optional Docker operation was attempted. Parsed stored request methods are GET only; browser driver is not committed, so its filtering/redaction/measurement implementation cannot be independently audited.
- Source/isolated evidence supports the incomplete classification/Resolve/visibility flows, Settings scope gap, file-input disparity and catalog API-failure rendered as No households without an error branch. API-failure evidence is captured in all three unauth samples; it is scoped to the sampled Catalog state, not every route or every possible outage.
- Thirty screenshot paths reconcile to thirty files and thirty distinct SHA256 values. Catalog/tablet and Review/phone masked images were inspected for layout/privacy; remaining images' visual content was not independently inspected. Masking hides all text and blurs photos, so those pixels do not prove readable controls/evidence or the identity of a clipped label. Structural DOM data is the separate channel.

## The failing responsive check

Stored phone samples labeled 390x844 record layout width 811–853; navigation client width is 390 and navigation scroll width is 811–853 (raw per-sample observations). Yet reported document overflow is zero because the denominator follows the expanded layout width. All ten stored phone samples have navigation overflow. Desktop control: all ten samples have navigation scroll width equal to navigation client width. Tablet stored navigation metrics show overflow in nine samples, whereas the report says eight.

The independent extraction is `SG-179_architect_geometry.json`, derived from the committed result objects. It carries the raw navigation fields, not another capture of production. Its comparison checks the same element's scroll/client widths and agrees with the known desktop control. An earlier exploratory comparison to `contentW` was discarded: that field reaches 1100 at desktop and is a content-container width, not necessarily the document viewport. No document-wide defect count is derived from it.

Root cause: the capture labels requested device dimensions while its overflow check uses a layout width that can expand with content; viewport, visual viewport, document client width and component width are not interchangeable. Missing persisted browser driver prevents independent inspection of this derivation. Reporting phone-clean from these measurements fails G-A4/G-T6 and the packet's real-viewport requirement.

## Accessibility claim correction

SG179-F3 labels all targets below 24x24 as WCAG 2.2 SC 2.5.8 failures. The standard includes spacing, equivalent-control, inline, user-agent-control and essential exceptions. Size-only data does not establish failure; stored target records lack adjacent-target rectangles. Keep small-control dimensions as ergonomic observations; withdraw the categorical conformance verdict until exceptions are assessed.

Official source: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html . Contrast source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html . Stored contrast samples report 4.4 for small text but omit actual foreground/background pairs and the measurement code. Runtime contrast failure remains a finding to verify, not an accepted general conformance verdict. Masked screenshot text cannot independently verify contrast. SG-183 must retain the actual pairs, compositing context and the standards-aware computation/controls.

## Dispositions

| ID | Finding or report entry | Status / destination |
|---|---|---|
| REC-ISS02 / SG179-F1 | CREATED import has no UI Run action; real runner exists | OPEN, confirmed; consolidated repair plan after audit, no implementation now |
| REC-ISS15 | False phone-clean verdict and mismatched viewport measures | FIX QUEUED, SG-183 one L2 root-cause correction |
| REC-ISS16 | Size-only WCAG verdict omitted exceptions; contrast algorithm/pairs absent | FIX QUEUED, SG-183 |
| REC-ISS17 | Browser driver/provenance absent; all-text masking limits UI/data inspection | FIX QUEUED, SG-183; readable public UI with private values masked after measurement |
| REC-ISS03 / SG179-F8 | Settings UI partial; export API-only | OPEN scope gap; consolidated recovery proposal |
| REC-ISS18 / SG179-F9 | Catalog API failure renders empty household state without error | OPEN, sampled failure state confirmed; consolidated recovery proposal |
| FIRST READ | Public URL and container identity limitations; backend build identity | OPEN / UNVERIFIED, SG-182; public-URL proof remains owed, no auth/privilege changes |
| DURING EXECUTION | Missing-original fixture, transient screen.unmount misuse | RESOLVED final route/probe controls; code/console captures distinguish the paths |
| REMAINING REC-ST02 per-file error/retry matrix | Not fully exercised | OPEN, SG-180 |
| REMAINING REC-ST05/07/09 | Multi-page/saved search, effective location/relation flags, task-link destinations | OPEN, SG-181 |
| REMAINING REC-ST10/11/12 | Agent/enrich generation flows | OPEN, zero-paid scripted-provider contract proofs in SG-180/181; no live spend grant |
| REMAINING container/build identity + benchmark/clock/test trust | Not proven by bundle/pid proxy | OPEN, SG-182 |

## Below-95 investigation and recurrence lever

Failure class: model execution / verification methodology. Exact correction: SG-183 repairs only the browser audit measurement/provenance, retains failing cases and assesses WCAG exceptions. One lever: persist the actual browser driver and one metric schema distinguishing requested device width, layout/visual viewport and each measured element's dimensions; exercise it against a known-fitting desktop case and a deliberately overflowing scratch control. Cost: a bounded audit artifact and correction run; replaces the unreproducible /tmp driver and ambiguous overflow verdict, not product behavior.

Owner impact: report claims 1437 seconds from first health to report write; that is not an independently measured whole engine runtime. Exact Coder/Codex platform cost unavailable. No production mutation/deploy accepted or performed by Architect. Context-size reading unavailable. The earlier status-only stop was an Architect execution mistake; approval already covered this audit. Continue the authorized stage after the one corrective checkpoint, without requesting the same authorization again.
