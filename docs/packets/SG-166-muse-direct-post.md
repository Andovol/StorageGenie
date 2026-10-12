# SG-166 — Scene Muse-only probe: direct Image-API POST + narrowed D7

`PB-1`–`PB-6` bind (`CODER.md` §14).

Autonomy: L3 (D-1009-7; spend authority D-1009-4: ≤$1 total, consent-gated; scope authority D-1012-3, owner quote "Google not working, lets skip it" + owner Approved m0034 for this probe ≤$0.05). Consumes T0-PINNED (SG-155/156/157) + SG-158 (G0 send path, R1 impossible) + SG-159 (R2 root cause PROVEN, Google 429, Muse chat imageless + endpoints empty, D7 unanswered). Answers SG-159 REMAINING (2) Muse transport via the direct POST the docs name and SG-159 never sent; (1) Google quota retired by D-1012-3, not re-probed; (3) pillow_heif carried (suite runs in the production image until fixed); (4) half-bound carried below. Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0; G-L1 CURRENT verified session-start: adopted=0.46.0 shared=0.46.0, installed 487841b1); host echo expected 0.46.0 from /home/andrei/storagegenie-contract/VERSION (SG-165 precedent) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — at most 1 Evidence + ledger rows from the single billed render, grants D-1009-4 + L3 D-1009-7 + D-1012-3 + m0034, PG-PR-10). No UPDATE/DELETE of existing rows, ever.
**Restart: none.** No served-code change → no refresh (D145).

## Why this exists

SG-159 proved the chat server-tool path never delivers an image artifact (persisted 200 body: text only, `image_tokens 0` — no extractor could conjure it) and measured Muse Image-API `endpoints []` on 2026-10-12, so it never sent the direct POST. Owner-supplied docs (`/docs/guides/overview/multimodal/image-generation`, fetched 2026-10-12) name exactly that transport: `POST /api/v1/images` `{model, prompt, input_references[]}` → `data[].b64_json` + `usage.cost`, all-or-nothing billing, reference images as URLs or base64 data URLs. INFERRED (re-verify free before spending; correcting me beats agreeing): `meta/muse-image` $0.01/image, provider `meta` permitted under the account allowed-providers (SG-158 F-SG158-1 — re-read live, do not inherit). This probe sends the one direct POST SG-159 never sent and exits with the Muse-only D7 answered or honestly still blocked.

## G0 — free discovery, $0

Read `GET /api/v1/images/models` + `.../models/meta/muse-image/endpoints` live (free, no consent needed). Quote both. Allowed-providers re-read free. STOP-success case (PG-SC-03): endpoints still empty AND no servable Muse image slug under a permitted provider → STOP as SUCCESS with D7 still blocked, G1 never starts, nothing spent. What does NOT count as grounds to stop: a transient 5xx on discovery (retry once under hang bound, then report). Photo bytes do not leave in G0.

## G1 — one direct render, ≤$0.05 hard

Photos: enumerate food assets with clear labels ON THE TARGET and pick 1 (criterion, not a list — report the enumeration and the pick). Expectation (verify on target, report difference either way): reuse SG-159's photo 1 (read its logs for the exact Evidence id). Frozen brief: same scene brief SG-158/159 used (quote it; if unrecoverable from their logs, freeze one sentence and say so). Exactly ONE `POST /api/v1/images` `{model: meta/muse-image, prompt: frozen brief, input_references: [the picked photo as URL or base64 data URL — decide and report]}`. Before the billed send: spend-so-far + this render's worst-case 0.05 stays ≤$1.00 total authority, or refuse `over_cap`. Precedence (PG-IC-03): unroutable/absent Muse endpoint is BLOCKED — ship G0, never substitute another image slug. A 2nd billed send is a STOP (PG-IC-08). Persist the result AS IT RETURNS (PG-EV-14: Evidence bytes + ledger row immediately, dry pass runs the analysis code first). Photo bytes leave for OpenRouter — disclosed, covered by the spend authority, key name-only throughout. Consent predicate: satisfied ONLY by this packet's quoted spend authority (D-1009-4 + L3 + D-1012-3 + m0034) — never by flipping `sg_consent`, never assumed.

## G2 — Muse-only D7

Per-render judgment (asset faithfulness vs scene quality, stated, no aggregate scores — D30) + the pick or the honest BLOCKED verdict with the quoted body (404/429/endpoints-empty). T0-PINNED stays unchanged unless a live value contradicts it (then both values quoted as drift). No invented values (a guard's rejection never satisfied by inventing — G-A9 packet detail).

## Constraints

Scope ceiling: G0 discovery + 1 render + offline payload-shape test + `docs/worklogs/SG-166_*` files; no migration, no restart, no served-code change. Secrets: key name-only; no secret file copied (CO-100). Spend: ≤$1.00 TOTAL authority, this probe ≤$0.05 (worst-case 0.05, sums 0+0.05 ≤ 1.0 — list price $0.01 sits far inside); billed-but-unledgered is a STOP. Publish-before-bound: report + receipt before 1050s elapsed (half of `RUN_BUDGET_S=2100`, standing lever). Expected duration ~600s (SG-158 actual 940s for code + 3 renders; this is no code + 1 render; lane enforces `RUN_BUDGET_S`). Hang bounds per class: ordinary 120s, one render 300s, suite 600s if code touched — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; G1's writes are the explicitly authorized Evidence/ledger rows — nothing else writes. Full suite runs only if product code changes (none expected); otherwise waived with the live discovery + render quotes as substitute (PG-DP-02 shape). Offline shape test (PG-EV-04): one mocked test asserting the exact direct-POST payload shape (model/prompt/input_references keys) — fail-pre→pass-post, both runs committed, no network/credentials/money.

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

- A1: G0 discovery quoted (models + Muse endpoints + allowed-providers re-read); STOP-success path honored if still empty (PG-SC-03).
- A2: at most 1 billed render with Evidence + ledger ids quoted, persisted as returned (PG-EV-14); spend accounting actual-vs-budget with arc total; 0 Authorization leaks (name-only key); 2nd billed send never starts (PG-IC-08: expected 1 Evidence + matched ledger rows, stop + report on difference either direction).
- A3: payload-shape test fail-pre→pass-post both committed (PG-EV-04); no live sends in tests.
- A4: Muse-only D7 answered or BLOCKED with quoted body; per-render judgment, no invented values.
- A5: SG-166 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch per SG-158 precedent); publish-before-bound honored with elapsed quoted; production writes = exactly the new Evidence + ledger rows, counted both directions.
- A6: guards invoked: PG-EV-02, PG-EV-04, PG-EV-06, PG-EV-09, PG-EV-14, PG-SC-03, PG-IC-01, PG-IC-03, PG-IC-07, PG-IC-08, PG-IC-09, PG-PR-10.

## Report

Echo `SG-166` as the first token. Destinations: `docs/worklogs/SG-166_report.md` + fail/pass logs + discovery + render transcript. Close with FIRST READ / DURING EXECUTION / REMAINING.
