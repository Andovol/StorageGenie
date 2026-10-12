# SG-171 — Review gating: visible blocked reason + evidence-thumb fallback

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` named here: derived set = `frontend/src/components/CandidateCard.test.tsx` (run by file; full suite waived with substitute below).

Autonomy: L2 (project standing; 1 retry; D-1012-12, owner quote "D12 - approved" read as D-1012-12 with the legacy collision disclosed in STATE). No spend ($0 — no metered call exists on any path; a metered call is a STOP-and-report). Exits with both defects fixed, unserved. Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0; G-L1 CURRENT 2026-10-12, installed 487841b1) == host 0.46.0 (SG-170 echo from /home/andrei/storagegenie-contract/VERSION) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.** No datastore touch of any kind (a live query is a STOP-and-report).
**Restart: none.** Served code changes but the running service is untouched → no refresh (D145); serving rides a later close-out deploy, never this slice (state this explicitly in the report).

## Why this exists

Owner-verified live (Review workspace screenshots 2026-10-12, two `proposed` candidates): (1) Accept renders dimmed with NO visible reason — the "blocked until open review tasks are resolved" sentence renders ONLY inside the dedup-matches alert (`CandidateCard.tsx:59-65`, gated on `dedup_matches.length > 0`); with no matches the only signal is a hover `title` (`:89`) on a button most users never hover. The block itself (`:47` `review_task_ids.length > 0` → `disabled`, `:93-95`) is correct and stays. (2) The second evidence thumbnail on both candidates is a broken-image icon: `CandidateCard.tsx:82` renders a raw `<img>` per `evidence_ids` with no `onError` fallback, and transcript (non-photo) evidence carries no image bytes, so the thumb 404s. `EvidenceGallery.tsx` fixed this exact shape with a visible focusable "Thumbnail unavailable" block (Palette #44) — mirror that pattern, do not invent a new one (hand-over: file path + pattern quoted above; withholding does not create autonomy). ISS-20 (job-select) is CLOSED — owner confirms selection loads; no repro rides this slice.

## G1 — always-visible blocked reason

When `blocked`, render below the button row (outside any dedup gate): `Acceptance is blocked until the open review task(s) are resolved.` + a react-router `Link` (`text-link focus-ring` precedent) `View them in the Inbox.` → `/inbox?household_id={householdId}`. Unblocked renders nothing new. No other decision logic moves (`busy`/`blocked` predicates byte-identical). Criterion, not a list: a blocked candidate with zero dedup matches shows the reason with no hover and no alert present — assert exactly that.

## G2 — evidence-thumb fallback

Mirror the `EvidenceGallery` "Thumbnail unavailable" treatment onto `CandidateCard`'s evidence `<img>`: on error, swap to the same visible, focusable fallback block (same copy). Photo evidence still renders `<img>` first (no behaviour change on the happy path). Criterion: a candidate with one photo + one imageless evidence id renders one image + one fallback block; zero broken-image icons.

## Constraints

Scope ceiling: `frontend/src/components/CandidateCard.tsx` + `frontend/src/components/CandidateCard.test.tsx` + `docs/worklogs/SG-171_*`; nothing else moves (a second product file is a STOP-and-report). No copy beyond the G1 sentence + the mirrored fallback copy (no new vocabularies). Secrets: none. Spend: $0. Publish-before-bound: report + receipt before 1050s elapsed (half of `RUN_BUDGET_S=2100`). Expected duration ~300s (SG-167 actual ~110s same shape; lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, file runs 600s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; the ceiling's one product file is exactly what every criterion touches. Full suite waived (1-file presentation change; substitute = derived 1-file vitest + `tsc --noEmit` + eslint, all quoted). No served-code proof demanded: the tree is deliberately unserved; the report states it and names the close-out deploy as the vehicle.

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

- A1: blocked candidate with zero dedup matches renders the reason sentence + Inbox link with no hover and no alert; unblocked candidate renders neither (real `CandidateCard` render, PG-SC-12); `busy`/`blocked` predicates unchanged (diff proves).
- A2: photo + imageless evidence renders one `<img>` + one fallback block; all-photo renders zero fallbacks; no-branch image behaviour unchanged (real render with error-event simulation, PG-SC-12).
- A3: derived 1-file vitest green + `tsc --noEmit` + eslint, all quoted; fail-then-pass both runs committed (PG-EV-09).
- A4: SG-171 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); publish-before-bound honored with elapsed quoted; production writes = none (stated, unserved tree stated).
- A5: guards invoked: PG-EV-02, PG-EV-09, PG-SC-12, PG-IC-01, PG-IC-07, PG-IC-09.

## Report

Echo `SG-171` as the first token. Destinations: `docs/worklogs/SG-171_report.md` + fail/pass logs. Close with FIRST READ / DURING EXECUTION / REMAINING.
