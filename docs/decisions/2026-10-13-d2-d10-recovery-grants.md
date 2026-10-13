# 2026-10-13 — Owner decisions D2–D10 and session directives (quotes verbatim)

Owner approval of the nine recovery decisions (presented m0109, all nine with recommendations):
Owner quote: “All approved.” (2026-10-13, this chat.)

Scope approved: R1 re-scope SG-175 clean (D2); R5 production release after D4–D6 (D3); R4 key-replay repair + replay policy (D4); R6 read-time rehash (D5); R2 capture journey, cancel deferred (D6); cursor 422 (D7); archived exclude-by-default (D8); R8 design after correctness (D9); R7 guard fix (D10). Per-field enrichment + true-concurrency parked (no decision needed).

Session directives (verbatim): “What is next? Do not start any slices yet” → recorded grants in STATE (`97b11bc`), no dispatch. “Prepare in this session the slices that you can already prepare and have the context for, but we will run them in the next session. What makes sense, move it to the next session.” → draft packets SG-184–190 committed (`56185d8`), undispatched; R5 deliberately unprepared (needs live release word at runtime). “Lets close this session and continue in a fresh one.” → this close; standing close-out deploy still conflicts with held SG-175 code (CLOSE_BLOCKED, no waiver).

Earlier D1 adoption approval, owner quote: “D1 - approved.” (this chat.) Executed as `785fe7d` (cache `contract-v0.47.0`, records 0.47.0, checks CLEAN/CURRENT twice).

D11 R1 re-scope direction, owner quote: “D11 - as recommended.” (2026-10-13, this chat.) Adopts Option A: SG-184 becomes a zero-product-change verification + waiver slice proving merged `0b42e7d` cleanly on disposable state (revert-in-`/tmp` fail-pre, HEAD pass-post, probe re-run, served-baseline GETs); no history rewrite, no product edit; serving stays a later rider. Packet correction follows; dispatch still awaits a separate go.

D12 dispatch approval + L3 mode, owner quotes: “We are running in L3 mode.” / “D12 approved.” (2026-10-13, this chat.) Packet autonomy line amended L2→L3 to match. Expected duration ~600 s (uncalibrated; derived from SG-182's 585 s lane actual for the same verification shape per `D369`), lane `RUN_BUDGET_S=2100`. Trigger: `SG-184 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (coder per `D29`, model+effort per `D-1012-15`).

D13 waiver grant, owner quote: “D13 - approved” (2026-10-13, this chat.) The SG-175 `FLAG:SAFETY` hold is WAIVED for serving-rider purposes per the SG-184 audit recommendation (merged bytes re-proved 96, protocol-clean). Serving the merged code rides a later rider; CLOSE_BLOCKED clears on a verified live serve.
