# D-23 — DECIDED: billing fixed, run one Google re-probe — 2026-10-21

**Owner message, byte-identical (2026-10-21, chat):**

> D1 - billing is fixed for Google models, do a test.

(Read as the answer to the standing D-1/D-23 choice from the 2026-10-17 close: billing action done, test authorised. "D1" is the turn-local label for that choice; the durable ID stays D-23 per `G-P4` — no ID is reused.)

## D-23 — DECIDED: test the Google leg once, capped

- Billing-side premise (expected, re-verify in-slice per `PB-1`): the owner reports the Google prepay wall cleared. The slice measures whether `google/gemini-3.1-flash-image` now returns 200 with image bytes — it does not assume the fix.
- Test shape: SG-213 rerun, minimal: discovery re-measure (free reads) + ONE minimal billed text-to-image; only on 200+bytes, ONE `input_references` fixture render. Any 402/429/quota or artifact-less 200 STOPS with bodies committed. Exactly the planned POSTs, zero otherwise.
- Spend authority: D-20 ($2.00/day total) + D-14 ($10.00/month total) both bind, fail-closed. Worst-case projection computed BEFORE any billed call from live pricing lines × planned renders + known spend; breach on either cap STOPS before any POST. Unbilled (402/429) responses spend $0 against neither cap.
- Slice: **SG-216** under project **L2** (one retry, root-cause only). Coder/model/effort ride the dispatch envelope, never the packet (D302).
