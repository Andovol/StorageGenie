# SG-232 audit — close-deploy retry SERVED (G0 fix worked, one rebuild + one recreate, bundle identical); rated 98

**Receipt verified:** notes-ref trailer `Dispatch-ID: SG-232 | Report: docs/worklogs/SG-232_report.md` present on remote (fetch `c6ef7f5..8276c3a`); Work-HEAD `965b84f` + mapped read-back transcript committed. **Diff verified:** new commits `965b84f` (8 × `SG-232_*` logs + report, 647 +) + `8ea1705` (receipt transcript) — docs/worklogs only, zero product/config/schema/test bytes. Served-identity churn (f419758d→1e859548, d6c6a106→793c89ce) corroborates the serve independently of the report.

- **G0 root-cause fix verified:** socket printed from unit env, exported, server line answered at 13:41:18Z before any other docker call — the SG-231 failure mode is gone.
- **F-SG232-1 (client-side obstruction, handled):** first build CLI failed on root-owned HOME (`mkdir ~/.docker`); no daemon contact (image ID unchanged proves it). Per-command `/tmp` client config, one daemon build rc=0 19 s. Both counts stated (2 CLI attempts, 1 daemon issuance); no endpoint change, no sudo. Judgement disclosed, not smoothed.
- **F-SG232-2 (expected mechanism):** WAL checkpoint on clean stop; 28 tables + head + all counts identical — logical DB unchanged. Correctly disclosed at file-sha level instead of claiming "unchanged" flatly.
- **A1/A2/A3/A4 all MET with evidence:** new identity + start time, health 6/6, bundle `cmp` identical with byte-identical-build reason (frontend layers CACHED, runtime diff 0), premises (a)(b) verified on target, first token SG-232, receipt published + read back.
- **No flag:** no safety breach, no trust breach (substitute verification named with log paths; void nothing).

**Holistic: 98/100, no flag.** Complete serve with the failure mode from SG-231 demonstrably fixed and every judgement disclosed. `deduction_attribution`: empty (nothing deducted). `slowest_waste`: none — G0 output (the fix proof), pre-state, build, verification all used. 274 s of 2100 vs ~400 s expectation (bracketed actuals).

## Dispositions

| Item | Status |
|---|---|
| F-SG232-1 HOME-permission obstruction | **RESOLVED** in-slice (/tmp client config, disclosed, no repeat) |
| F-SG232-2 WAL checkpoint / CORS preflight / `/catalog` premise | **RESOLVED** as recorded premises — informational, no action |
| SG-232 receipt + rating row | **RESOLVED** — published, read back, row appended this turn |
| Standing close-deploy | **RESOLVED** — PROVEN SERVED (container `1e859548`, image `793c89ce`) |
| Close-release tag | **OPEN** — needs owner word: no product delta since `release-2026-10-21`, recommend no new tag |
| Session close | **OPEN** — needs owner close order (`CLOSE.md`: never unprompted) |
