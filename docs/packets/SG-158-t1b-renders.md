# SG-158 — Scene T1b: 3 controlled renders via OpenRouter (≤$1) + D7 pick

Autonomy: L3 (D-1009-7; spend authority D-1009-4: ≤$1 total, consent-gated). Consumes the triple-confirmed T0-PINNED block (SG-155/156/157). Exits with the D7 model pick on stored-render evidence.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — new Evidence + ledger rows only, grant D-1009-4 + L3 D-1009-7, PG-PR-10). No UPDATE/DELETE of existing rows, ever.
**Restart: none.** No served-code change → no refresh (D145).

## Why this exists

T0 proved the seam and pinned every value this slice needs (all committed, re-verified 3×). CONFIRMED: frozen envelope (`tool_choice: "required"`, `max_tool_calls: 1`, stop schema `{max_cost, step_count_is, ...}`, photo as message image content, server tool text-prompt-only); shortlist prices per image_output unit — `openai/gpt-5-image` 0.00004 · `openai/gpt-5-image-mini` 0.000008 · `openai/gpt-5.4-image-2` 0.00003 · `google/gemini-3.1-flash-image` 0.00006; orchestrator candidates cheapest-first (`inclusionai/ling-3.0-flash-vl`, `qwen/qwen3.7-flash`, `google/gemma-3-12b-it` — pick one and justify, do not inherit blindly). INFERRED: nothing material — prices/paths re-confirm from your own reads before spending.

## G0 — send/store/ledger path + tests

The seam builds requests; add the send path: key at send time only, POST, immediate download of the temporary `imageUrl`, Evidence row (bytes + provenance: provider=`openrouter`, image model, orchestrator, prompt, usage cost, timestamp) + ledger row per billed call INCLUDING billed failures (SG-099 lesson). New tests fail-pre→pass-post both committed (offline shape + refusal paths + billed-failure ledgering; live sends never in tests). Consent predicate: satisfied ONLY by this packet's quoted spend authority (D-1009-4 + L3) — never by flipping `sg_consent`, never assumed.

## G1 — 3 controlled renders, ≤$1 hard

Photos: enumerate food assets with clear labels ON THE TARGET and pick 2 (criterion, not a list — report the enumeration and the pick). Same frozen brief, same first photo: R1 one `openai/gpt-5*` slug, R2 `google/gemini-3.1-flash-image`; R3 confirms the winner on the second photo. Before EACH render assert spend-so-far + this render's worst-case stays ≤$1 or refuse `over_cap` (no second chances — a 4th render is a STOP, PG-IC-08). Persist EACH result as it returns with ids quoted (PG-EV-06 report-and-leave; PG-EV-14). Photo bytes leave for OpenRouter — disclosed, covered by the spend authority, key name-only throughout.

## G2 — D7 pick

Per-render judgment (asset faithfulness vs scene quality, stated per render, no aggregate scores — D30) + the pick with its reason. T0-PINNED stays unchanged unless a live value contradicts it (then both values quoted as drift).

## Constraints

Scope ceiling: G0 code + tests + 3 renders + `docs/worklogs/SG-158_*` files; no migration, no restart, no served-code change. Secrets: key name-only; no secret file copied (CO-100). Spend: ≤$1 TOTAL across the slice (expected ~$0.05 worst-case at listed prices); billed-but-unledgered is a STOP. Publish-before-bound: reports + receipt before half the elapsed budget (standing lever). Expected duration 600s (SG-156/157 actuals 176–355s + renders; lane enforces `RUN_BUDGET_S`). Hang bounds per class: ordinary 120s, suite 600s, one render 300s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; G1's writes are the explicitly authorized Evidence/ledger rows — nothing else writes. Full suite runs (derived-set block not pasted).

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> **No bound reaches the lane's idle kill (`IDLE_KILL_S`, default 900 s):** a run printing nothing for
> that long is killed whole. Run longer work in the background and check it with short calls.
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Acceptance criteria

- A1: G0 tests fail-pre→pass-post both committed; envelope re-asserted offline (PG-EV-04).
- A2: exactly 3 renders, each with Evidence + ledger ids quoted; total spend ≤$1 with per-render accounting; 0 Authorization leaks (name-only key).
- A3: D7 pick with per-render judgments; no invented values (a guard's rejection never satisfied by inventing — G-A9 packet detail).
- A4: SG-158 report + notes-ref receipt read back on remote; publish-before-bound honored with elapsed quoted; production writes = exactly the 3 Evidence + ledger rows (PG-IC-08 both directions).
- A5: suite + ruff + mypy as established; guards invoked: PG-EV-04, PG-EV-06, PG-EV-09, PG-EV-14, PG-SC-03, PG-IC-01, PG-IC-03, PG-IC-07, PG-IC-08, PG-IC-09, PG-PR-10.

## Report

Echo `SG-158` as the first token. Destinations: `docs/worklogs/SG-158_report.md` + fail/pass logs + per-render ledger transcript. Close with FIRST READ / DURING EXECUTION / REMAINING.
