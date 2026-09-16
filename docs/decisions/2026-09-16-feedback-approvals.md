# Decisions 2026-09-16 — live-UI feedback approvals (D71–D73)

Owner quote (m0015): "D1, D2, D3 - approved" — approves the three numbered items in the
2026-09-16 feedback triage message (m0014), namely:

- D71 (from triage D1): SG-054 UI-polish slice APPROVED — remove white legacy nav, fallback icon
  for photo-less items, table/pill overflow fix, "Total: 1 items" grammar. L2, opencode/medium,
  one retry. Touches no DB/host/secret.
- D72 (from triage D2): S2/SG-048 fire SEQUENCED — fires after SG-054 lands (live SQLite migration,
  G-K3 surface; per-slice word requirement from D60 satisfied by this approval, ordering constraint kept).
- D73 (from triage D3 = D62): S3/SG-049 consent + provider key APPROVED — owner places the key into
  host backend `.env` (Q2, never in chat); slice fires after SG-048 lands.

Order: SG-054 → SG-048 → SG-049 → SG-055+ (remaining routes to tokens).
Triage note: `docs/feedback/2026-09-16-live-UI-feedback.md`.
Rule-set: 0.27.0. Coder: opencode (D29). Autonomy SG-054: L2.
