# D-14 monthly cap — $10/month — 2026-10-17

**Owner message, byte-identical (2026-10-17, chat):**

> Monthly cap 10$

## D-14 — DECIDED (complete): $2.00/day total + $10.00/month total, all live AI spend

- The daily cap ($2.00, D-20 answer) binds first on every slice's worst-case projection, fail-closed. The monthly cap ($10.00) binds across slices within the calendar month — the Architect tracks cumulative measured spend (`usage.cost` per billed leg, arc known spend $0.002437125 to date) and STOPS new billed work for the month when the next slice's projection would breach it.
- No per-render cap stated — the daily bound covers it. No auto-extrapolation was recorded as approval; both numbers are owner-spoken.
- Applies from SG-214 on: any billed leg checks both caps. Unbilled (402/429) responses spend $0 and touch neither cap.

Committed locally; pushes with the SG-214 audit (no push under a live dispatch).
