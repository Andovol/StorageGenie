# Decisions D-5 · D-6 · D-7 — owner answers, and the L4 window (2026-10-17)

**Owner message, byte-identical (2026-10-17, chat):**

> D5-D7 - as recommended. I want you to continue in L4 auto mode for the next 3 hours.

Issued after the mandatory second-opinion review (`SECOND_OPINION.md`, `D451`; `D-3:17` counter-rule) — Phase A SG-200 (`994345c`) and Phase B SG-201 (`1462392`), ledger `docs/reviews/review-ledger.md`.

## D-5 — APPROVED: A, serve the unserved frontend delta now

- Serve the SG-196 + SG-198 frontend delta (24 files, +622/−170, frontend-only; both slices rated 98/no flag) now, by the proven close-out-deploy rider shape (one rebuild + one recreate + verify; SG-193/SG-197 precedent).
- **Close re-serves only if new product commits land after this serve**; with no new product commits, live==tree at close is verified, not rebuilt. This is the reading applied to the standing 2026-09-28 directive ("Always do a live deploy before session close") — owner may correct it.
- Production authorization basis for the rider: this D-5 approval (same pattern as D-3 ⇒ SG-197). `G-K2` satisfied by the owner's explicit word.
- Second opinion: both reviewers picked B (carry to close); strongest objection — A doubles production cycles against sensitive surfaces for zero repair content (D-3:9 assigned the delta to the close); **rejected** because the close re-serve is conditional here (one cycle in the no-new-commits case) and live==tree directly serves the D-6 work.

## D-6 — APPROVED: P1, build the density proposal

- Build the density proposal (real options + renders) for the owner — the recorded promise (`2026-10-16-density-scope-d4.md:9`; `SG-199_audit.md:22`). Proposal step only; **no density system is implemented before the owner picks an option.**
- Two refinements accepted from Phase B, both binding on the slice:
  1. **Exercise the existing grid/table toggle first** — SG-199 never tested it (`SG-199_report.md:45`, "no control designed, per packet"); its measured behaviour across the routes/states is the proposal's factual base.
  2. **Name the one measured item** — native default button faces render off-token in dark (`SG-199_report.md:14`) — rather than invent requirements the measurement does not support. Options must include leave-it.
- Second opinion: picked P1 (agreed); strongest objection — `G-A7`: the live reason came back empty and a proposal beyond the unmeasured toggle risks "requirements invented"; **accepted** — both refinements folded in.

## D-7 — APPROVED: `default` (rule-resolved reviewer)

- Second-opinion setting becomes **`default`**: the rule resolves the reviewer at dispatch (`openocde`-free wording in `SECOND_OPINION.md:13-17`) — `opencode-go/muse-spark-1.3-contributor effort=xhigh` when the Architect is not Muse 1.3, `opencode-go/deepseek-v4.1-flash effort=max` when it is. **The reviewer is never the Architect's own model** (`D451`).
- Supersedes the explicit value recorded in `docs/decisions/2026-10-15-contract-050-adoption.md:35`; `AGENTS.md` Second opinion row updated in the same step.
- Second opinion: **both** reviewers picked keep-explicit; strongest objection — `default` rests on the Architect's self-classification, and today's resolution would land the reviewer in the Architect's *recorded* family (muse-spark); **kept against them** — this session's engine declares the Architect model `opencode/deepseek-v4.1-flash-free`, so under the real identity `default` resolves *away* from my family while keep-explicit is the one that collides. This is the one disagreement kept, surfaced to the owner (never smoothed).

## Autonomy — L4, three-hour window

- **Level: L4** (`ARCHITECT.md:66`, owner approves a goal). **Goal:** serve the unserved delta (D-5) and deliver the density proposal (D-6), continuing the queued arc for the window.
- **Window: 2026-10-17 14:58 → 17:58** (owner's zone, +03:00; derived from the live clock at the owner's message).
- Binds at every level: `D396` — never launch a slice whose scope rests on an unanswered owner decision; `G-K2` — anything touching the declared sensitive surfaces (evidence store, SQLite DB, dispatch host) still reaches the owner; `D448` — a new outcome starts a new stage; `RULES.md` invariants.
- Per-slice owner gos are ended (`D16`, owner chat); checkpoints only per `D16`.
