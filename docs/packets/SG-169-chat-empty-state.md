# SG-169 — Chat honest empty-state: unclassified count + Inbox link

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` named here: derived set = `backend/tests/test_chat.py` + `frontend/src/routes/ChatPage.test.tsx` (run by file; full suite waived with substitute below).

Autonomy: L2 (project standing; 1 retry; D-1012-9, owner quote "Yes, approved." on the G-C1 restatement). No spend ($0 — the empty path makes zero provider calls today and still will; a metered call on the empty path is a STOP-and-report). Exits with the empty case naming its cause, unserved. Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0; G-L1 CURRENT 2026-10-12, installed 487841b1) == host 0.46.0 (SG-168 echo from /home/andrei/storagegenie-contract/VERSION) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: sqlite live, READ-ONLY this slice** (one filtered count read; no migration, no UPDATE/DELETE/INSERT of any kind — a write is a STOP-and-report).
**Restart: none.** Served code changes but the running service is untouched → no refresh (D145); serving rides a later close-out deploy, never this slice (state this explicitly in the report).

## Why this exists

`/chat` answers "no catalogue data" for a household holding 6 visible items (owner screenshot 2026-10-12). Root cause, verified in-tree: `build_catalog` (`backend/app/services/chat/service.py:144-211`) keeps an asset ONLY on an accepted classification assertion (`plugin:expiry-tracker/classification` → slug); assets without one hit `continue` (`:203-205`). The owner's assets carry no accepted classification (Expiry: Uncategorized 6), so the catalogue is empty and `respond()` returns the fixed `EMPTY_ANSWER` with `empty_catalogue=True` (`service.py:362-375`), rendered by `ChatPage.tsx:54` as "No catalogue data for this category yet." The message is honest but causeless — it never says the items exist yet await classification, nor where to fix it. D-1012-10 (grounding fallback on `asset_type` strings) is REJECTED: extraction labels are unreviewed, the slug is review-accepted — different authorities. This slice names the cause and the remedy, changing no grounding, no prompt, no ledger shape.

## G1 — backend: carry `unclassified_count` on the empty path

In `respond()`'s empty branch ONLY (`service.py:362-375`): add `unclassified_count` = active household assets with NO accepted (non-superseded, non-rejected) classification assertion — the SAME predicate `build_catalog` filters on (`:101-111` + `:164-181` batch pattern; reuse it, do not invent a second definition). `EMPTY_ANSWER` text UNCHANGED. Zero-call property UNCHANGED (a local count read is not a provider call). `catalogue_size: 0` UNCHANGED. Distinguish (PG-SC-07): `unclassified_count > 0` (items exist, none classified) vs `0` (nothing captured at all — or everything classified elsewhere; the notice copy below treats both as the no-action variant). Read-back route `backend/app/api/v1/chat.py:28-38` returns the `respond()` dict unwalled — name it as the surviving route in the report (PG-SC-02: no whitelist, no projection, no serializer tuple stands between the new key and the reader; if one does, that is the finding).

## G2 — frontend: render the cause + the remedy

`frontend/src/api/types.ts`: add optional `unclassified_count?: number` to `ChatResponse` (nothing else in the type moves). `ChatPage.tsx` empty branch ONLY: keep the existing "No catalogue data for this category yet." line, and append iff `(result.unclassified_count ?? 0) > 0`: `No classified items in {CategoryLabel} yet — {N} awaiting classification.` followed by a `Link` (react-router, `text-link focus-ring` precedent) `Review them in the Inbox.` → `/inbox?household_id={effectiveHousehold}`. `{CategoryLabel}` is the visible select label (Food), never the slug. Transcript assistant text stays `EMPTY_ANSWER` (unchanged). No other Chat hunk; no copy beyond these two sentences (no new vocabularies).

## Constraints

Scope ceiling: `backend/app/services/chat/service.py` + `frontend/src/api/types.ts` + `frontend/src/routes/ChatPage.tsx` + the two test files + `docs/worklogs/SG-169_*`; nothing else moves (a fifth product file is a STOP-and-report). Criterion, not a list: the empty branch is the ONLY behaviour that changes — enumerate every other `respond()` return shape ON THE TARGET and prove each byte-identical or ledger-identical (report the enumeration). Secrets: none. Spend: $0. Publish-before-bound: report + receipt before 1050s elapsed (half of `RUN_BUDGET_S=2100`). Expected duration ~300s (SG-167 actual ~110s for 2 files + tests; this is 3 files + tests; lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, suite/file runs 600s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; the ceiling's files are exactly what every criterion touches. Full suite waived (3-file behaviour-preserving change; substitute = derived 2-file runs + `tsc --noEmit` + eslint + ruff/mypy as established, all quoted). No served-code proof demanded: the tree is deliberately unserved; the report states it and names the close-out deploy as the vehicle.

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

- A1: empty branch carries `unclassified_count` computed by the shared predicate (backend test: household with classified + unclassified + other-category assets asserts the exact count; 0-asset household asserts 0; non-empty branches byte-identical); `EMPTY_ANSWER` text unchanged; zero provider calls on the empty path (assert no ledger row).
- A2: real `ChatPage` render with `empty_catalogue + unclassified_count=N>0` shows both sentences + working Inbox link with the household id; with `0`/absent shows the legacy single line (PG-SC-07 both branches, PG-SC-12 consumer's bytes).
- A3: derived set green by file + `tsc --noEmit` + eslint + ruff/mypy as established, all quoted; fail-then-pass both runs committed (PG-EV-09).
- A4: SG-169 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); publish-before-bound honored with elapsed quoted; production writes = none (stated, unserved tree stated).
- A5: guards invoked: PG-EV-02, PG-EV-09, PG-SC-02, PG-SC-07, PG-SC-12, PG-IC-01, PG-IC-07, PG-IC-09.

## Report

Echo `SG-169` as the first token. Destinations: `docs/worklogs/SG-169_report.md` + fail/pass logs. Close with FIRST READ / DURING EXECUTION / REMAINING.
