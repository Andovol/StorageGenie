# SG-159 — Scene T1b re-dispatch, Google-only: R2-fix + Google-vs-Muse contest + narrowed D7

Autonomy: L3 (D-1009-7; spend authority D-1009-4: ≤$1 total, consent-gated; scope authority D-1009-10, owner quote "Use Google and Muse Image only"). Consumes T0-PINNED (SG-155/156/157) + SG-158 (G0 send path shipped, R1 impossible under account policy, R2 imageless-200). Exits with the narrowed D7 pick on stored-render evidence. Contract: recorded 0.44.1 == published payload (tag contract-v0.44.1); host echo expected 0.44.1 from /home/andrei/storagegenie-contract/VERSION (SG-158 precedent) — echo verbatim + source path. Known delta 0.44.2..0.46.0 exists; adoption is DEFERRED to chain close — do not trip on it. Authoring date (metadata, never a gate): 2026-10-12.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — new Evidence + ledger rows only, grants D-1009-4 + L3 D-1009-7 + D-1009-10, PG-PR-10). No UPDATE/DELETE of existing rows, ever.
**Restart: none.** No served-code change → no refresh (D145).

## Why this exists

SG-158 left two answered questions and one code gap. ANSWERED: the account's allowed-providers permits `meta` and `google-ai-studio` (live 404 body, SG-158 report F-SG158-1) — so both contest models below are routable with NO account change, and openai legs are OUT (owner-named scope, not a workaround). GAP (F-SG158-3): R2's live 200 billed $0.000758925 with server-tool calls executed but no image URL extracted and no 2xx body persisted. CONFIRMED carried forward: frozen envelope (`tool_choice: "required"`, `max_tool_calls: 1`, stop schema, photo as message image content, server tool text-prompt-only); orchestrator expectation `bytedance-seed/seed-1.6-flash` (SG-158 justified: Seed permitted, cheapest routable — re-verify, do not inherit blindly). INFERRED prices (re-verify via the free endpoints API before spending; correcting me beats agreeing): `google/gemini-3.1-flash-image` 0.00006/image_output (T0-PINNED) · `meta/muse-image` $0.01/image (OpenRouter list 2026-08-26; Meta agentic image model, text-to-image + reference-image edit). SG-158's open REMAINING items are answered here: allowed-providers → D-1009-10 above; 2xx persistence / Image API → G0-fix below.

## G0-fix — 2xx-body persistence + extractor hardening + tests

Persist EVERY live response body (2xx as well as errors) at return with ids quoted (PG-EV-06 report-and-leave; PG-EV-14), harden `extract_image_url` against the shape SG-158's 200 actually returned, and decide server-tool vs dedicated Image API (`POST /api/v1/images`, `b64_json`, `input_references`) inside these constraints — decide and report, do not ask. New tests fail-pre→pass-post BOTH committed (offline shape + 2xx persistence + billed-failure ledgering; live sends never in tests). Consent predicate: satisfied ONLY by this packet's quoted spend authority (D-1009-4 + L3 + D-1009-10) — never by flipping `sg_consent`, never assumed.

## G1 — 3 controlled renders, ≤$1 hard

Photos: enumerate food assets with clear labels ON THE TARGET and pick 2 (criterion, not a list — report the enumeration and the pick). Expectation (verify on target, report difference either way): reuse SG-158's two photos (photo 1 = SG-158 R2's photo, read from its logs). Same frozen brief throughout: R2a `google/gemini-3.1-flash-image` on photo 1, R2b `meta/muse-image` on photo 1; R3 confirms the winner on photo 2. Before EACH billed send: free endpoints-API routability check against the account allowed-providers + spend-so-far + this render's worst-case stays ≤$1, or refuse `over_cap` (no second chances — a 4th billed send is a STOP, PG-IC-08). Precedence (PG-IC-03): an owner-named image model proving unroutable is BLOCKED for that leg — ship the rest, never substitute another image slug. Orchestrator: expectation above, re-verified free before spending; if unroutable, pick the cheapest routable candidate that accepts image input and supports tools + `tool_choice: "required"` from a permitted provider, and justify (SG-158 F-SG158-2 precedent). Persist EACH result as it returns. Photo bytes leave for OpenRouter — disclosed, covered by the spend authority, key name-only throughout.

## G2 — narrowed D7 pick

Per-render judgment (asset faithfulness vs scene quality, stated per render, no aggregate scores — D30) + the pick with its reason, Google vs Muse only. T0-PINNED stays unchanged unless a live value contradicts it (then both values quoted as drift).

## Constraints

Scope ceiling: G0-fix code + tests + 3 renders + `docs/worklogs/SG-159_*` files; no migration, no restart, no served-code change. Secrets: key name-only; no secret file copied (CO-100). Spend: ≤$1 TOTAL across the slice (worst-case per render 0.30, sequential sums 0+0.30, 0+0.30, 0+0.30 ≤ 1.0 — both legs' list prices sit far inside); billed-but-unledgered is a STOP. Publish-before-bound: reports + receipt before 1050s elapsed (half of `RUN_BUDGET_S=2100`, standing lever). Expected duration ~900s (SG-158 actual 940s to work commit; lane enforces `RUN_BUDGET_S`). Hang bounds per class: ordinary 120s, suite 600s, one render 300s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; G1's writes are the explicitly authorized Evidence/ledger rows — nothing else writes. Full suite runs (derived-set block not pasted).

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

- A1: G0-fix tests fail-pre→pass-post both committed; envelope re-asserted offline (PG-EV-04); 2xx-body persistence proven against real SQLite rows, not a stand-in (PG-SC-12).
- A2: at most 3 billed renders, each with Evidence + ledger ids quoted; total spend ≤$1 with per-render accounting; 0 Authorization leaks (name-only key).
- A3: narrowed D7 (Google vs Muse) with per-render judgments; no invented values (a guard's rejection never satisfied by inventing — G-A9 packet detail).
- A4: SG-159 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch per SG-158 precedent); publish-before-bound honored with elapsed quoted; production writes = exactly the new Evidence + ledger rows, counted both directions (PG-IC-08).
- A5: suite + ruff + mypy as established (SG-158 snapshot: 2 test_signals env reds, 676 passed; mypy 41/9 none in scene); guards invoked: PG-EV-02, PG-EV-04, PG-EV-06, PG-EV-09, PG-EV-14, PG-SC-03, PG-IC-01, PG-IC-03, PG-IC-07, PG-IC-08, PG-IC-09, PG-PR-10.

## Report

Echo `SG-159` as the first token. Destinations: `docs/worklogs/SG-159_report.md` + fail/pass logs + per-render ledger transcript. Close with FIRST READ / DURING EXECUTION / REMAINING.
