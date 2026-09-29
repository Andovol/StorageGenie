# Roadmap-finish design — 2026-09-29

Status: design approved in chat 2026-09-29. Next: implementation plan via writing-plans skill.

## Decisions locked (owner words, paraphrased not quoted)

- Scope choice B: small fixes plus decisions first, Context Scene scoped but scheduled after.
- Deferred features stay out: pilot tiers, per-field accept UI, chat persistence, D61 prompts, beauty verdict — each keeps its own future scoping word (`docs/backlog.md:14`).
- Q3 ledger: calibrate later (window stays uncalibrated, no schedule ordered in this plan).
- Q4 autonomy: L3 chain.
- Q5 hue: closes by owner visual verdict on fresh screenshots, no slice.
- Q6 Context Scene: model pick stays parked (D7); this plan ends with a scheduled resume word.
- Approach P1: single L3 chain in dependency order.

## S1 — scope (what finished means)

In: cap-join correction (`F-SG132-5`), F-SG138-1 extraction remainder, frontend-service wording (F-SG140-2 family), runbook-command guard (`F-SG126-3`), offline `--sql` fts limit, host `gh` auth.
Verdicts: hue eyes plus a scheduled Context Scene resume word.
Out: ledger calibration, pilot tiers, per-field UI, chat persistence, D61 prompts, beauty verdict.
Provenance: live items from `STATE.md` RESUME, waiting items from `docs/backlog.md:5-18`, recent ratings SG-133→SG-140b in `docs/ratings.md`.

## S2 — run order and exits

Order: cap-join first (live spend figure reads low: 0.0067 vs 0.0104 true) → extraction remainder with frontend wording (one slice if surfaces allow, else two) → runbook guard → lane items (`--sql`, `gh` auth) → hue verdict on fresh post-deploy screenshots → Context Scene resume scheduled as a named resume word (date named in the implementation plan) → close-out deploy (rebuild + one recreate + verify).
Exits: each slice exits only on green audit + rating + receipt. Any STOP-gate, engine failure needing a probe, or production write outside the slice outline halts the chain and returns with a decision, never a silent skip.
State discipline: `STATE.md` stays the single source of next-slice scope, never duplicated into the backlog (`ARCHITECT.md:34-38`).

## S3 — guards and close-out

Autonomy L3 for the chain, one retry per slice, covering caps (2400s trigger caps; lane `RUN_BUDGET_S=2100`), `opencode`/`high` explicit every trigger with model omitted per standing policy (resolves to `deepseek-v4.1-flash`).
Testing per code slice: committed fail-pre to pass-post, suite + lint + typecheck + secret scan, live health delta where served code changes. Slices own their refresh per D145.
Close-out: live deploy before session close per standing directive; tree clean and pushed; END filed on `Andovol/Launcher#62`; unrated or blocked work stops the deploy rather than shipping silently.
Constraints: `job_spawn`-only triggers; EROFS sandbox (container-exec is the writable path); Jina gate inert until `SG_MONTHLY_CAP` set; `sg026`-freeze stays retired (D18).
