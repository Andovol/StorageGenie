# 2026-10-13 — Owner decisions D2–D10 and session directives (quotes verbatim)

Owner approval of the nine recovery decisions (presented m0109, all nine with recommendations):
Owner quote: “All approved.” (2026-10-13, this chat.)

Scope approved: R1 re-scope SG-175 clean (D2); R5 production release after D4–D6 (D3); R4 key-replay repair + replay policy (D4); R6 read-time rehash (D5); R2 capture journey, cancel deferred (D6); cursor 422 (D7); archived exclude-by-default (D8); R8 design after correctness (D9); R7 guard fix (D10). Per-field enrichment + true-concurrency parked (no decision needed).

Session directives (verbatim): “What is next? Do not start any slices yet” → recorded grants in STATE (`97b11bc`), no dispatch. “Prepare in this session the slices that you can already prepare and have the context for, but we will run them in the next session. What makes sense, move it to the next session.” → draft packets SG-184–190 committed (`56185d8`), undispatched; R5 deliberately unprepared (needs live release word at runtime). “Lets close this session and continue in a fresh one.” → this close; standing close-out deploy still conflicts with held SG-175 code (CLOSE_BLOCKED, no waiver).

Earlier D1 adoption approval, owner quote: “D1 - approved.” (this chat.) Executed as `785fe7d` (cache `contract-v0.47.0`, records 0.47.0, checks CLEAN/CURRENT twice).

D11 R1 re-scope direction, owner quote: “D11 - as recommended.” (2026-10-13, this chat.) Adopts Option A: SG-184 becomes a zero-product-change verification + waiver slice proving merged `0b42e7d` cleanly on disposable state (revert-in-`/tmp` fail-pre, HEAD pass-post, probe re-run, served-baseline GETs); no history rewrite, no product edit; serving stays a later rider. Packet correction follows; dispatch still awaits a separate go.

D12 dispatch approval + L3 mode, owner quotes: “We are running in L3 mode.” / “D12 approved.” (2026-10-13, this chat.) Packet autonomy line amended L2→L3 to match. Expected duration ~600 s (uncalibrated; derived from SG-182's 585 s lane actual for the same verification shape per `D369`), lane `RUN_BUDGET_S=2100`. Trigger: `SG-184 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (coder per `D29`, model+effort per `D-1012-15`).

D13 waiver grant, owner quote: “D13 - approved” (2026-10-13, this chat.) The SG-175 `FLAG:SAFETY` hold is WAIVED for serving-rider purposes per the SG-184 audit recommendation (merged bytes re-proved 96, protocol-clean). Serving the merged code rides a later rider; CLOSE_BLOCKED clears on a verified live serve.

D14 serving-rider dispatch approval, owner quote: “Yes, approved” (2026-10-13, this chat; D14 proposed as SG-191 dispatch-go.) Trigger: `SG-191 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (coder per `D29`, model+effort per `D-1012-15`), autonomy L3. Expected ~600 s (uncalibrated; SG-184 ran 360 s, plus one rebuild + one recreate within their 600 s bound).

D15 corrected-rider dispatch approval, owner quote: “D15 - approved.” (2026-10-13, this chat.) Trigger: `SG-192 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (coder per `D29`, model+effort per `D-1012-15`), autonomy L3. Expected ~600 s (uncalibrated; SG-191 ran 540 s stopped before build, plus one rebuild + one recreate within their 600 s bound). Owner question same turn: why per-slice approval under L3 — answered in chat (G-K2 production/sensitive-surface writes always checkpoint; L2-era per-slice-go rule kept without re-examination); D16 proposed: L3 flow checkpoints only on G-K2 surfaces, assumption-changing results, or stage end.

D16 L3 flow rule, owner quote: “D16 - ok” (2026-10-13, this chat.) Per-slice gos end; recovery slices flow with audit + rate after each. Checkpoints only on (a) G-K2 surfaces — production writes, sensitive surfaces, irreversible/outward-facing acts; (b) results changing the next packet's assumptions; (c) grant-needing verdicts. SG-185 first under this rule.

SG-185 dispatched under D16 (no per-slice go; disposable DB + read-only GETs, no G-K2 surface). Re-reviewed vs `328851e`: global `filter_by(key=…)` holds at `assets.py:82`, untouched since SG-136. Expected ~600 s (uncalibrated; single-endpoint repair + focused tests). Done `5be388f`, rated 97 no flag (audit SG-185_audit.md).

SG-186 dispatched under D16 (same class: disposable + read-only GETs, no restart, no prod write). Re-reviewed vs `5be388f`: serve-path gap holds at `evidence.py:101` (untouched since SG-006); upload-replay sibling homed with same-shape conditional (SG-185 I1 → here). Expected ~600 s (uncalibrated; rehash repair + overhead loop + conditional sibling).
