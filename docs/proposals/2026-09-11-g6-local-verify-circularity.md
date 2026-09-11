# Proposal: G6 cannot ask the report to quote a note that does not exist yet

**Date:** 2026-09-11 · **Status:** proposed (project-local record; relay to the shared queue at a safe
multi-repo boundary, never mid-slice) · **Evidence:** SG-022 (97), SG-023 (97), SG-024 (98) — three
consecutive slices, three independent Coder instances, same shape.

## The defect

`PACKET.md` G6 orders the Coder to "verify locally with `git notes ... show <WORK_HEAD>` and quote the
note" inside the committed report. But the note attaches to the work HEAD, and the report is committed
INSIDE the work HEAD — the quoted object cannot exist before the quoting document is sealed. What three
slices shipped instead: a restatement of the command shape (`SG-022`), placeholders (`SG-023`), an
assertion of verification without the paste (`SG-024`). All three receipts were independently valid on the
remote ref; all three reports carry the same cosmetic gap. A guard that cannot be satisfied as written is
noise (`G-A7`) — and it spends audit attention on every slice while proving nothing.

## Options (desk decides)

1. **Move the quote to the dispatch result line.** The runner already reads the remote note back — require
   the result line (not the report) to carry the note's first line verbatim. Report keeps the command it
   ran; the result line carries the evidence.
2. **Two-commit work shape.** Commit work, attach note, commit an addendum quoting it. Costs a second
   commit per slice and complicates HEAD attestation — not recommended, recorded for completeness.
3. **Accept remote validity as the verify.** Architect's `show` against the fetched ref IS the check; the
   report's obligation shrinks to naming the note's expected first line. Cheapest, weakest per-slice paper
   trail.

**Recommendation:** option 1 — the evidence already flows through that channel; only the requirement text moves.
