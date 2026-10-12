# SG-168 — Close-out deploy rider: serve SG-167 theming (rebuild + one recreate + verify)

`PB-1`–`PB-6` bind (`CODER.md` §14).

Autonomy: L2 (project standing; 1 retry; D-1012-7, owner quote "Both approved." for deploy — production restart authorized SOLELY by this word + the standing close-out directive, `AGENTS.md` Close-out row, `G-O4`). **Zero product hunks expected — and zero produced.** Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0; G-L1 CURRENT 2026-10-12, installed 487841b1) == host 0.46.0 (SG-167 echo from /home/andrei/storagegenie-contract/VERSION) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: sqlite live, READ-ONLY this slice** (`/data/db/storagegenie.db` — 28-table counts read before + after; no migration, no UPDATE/DELETE/INSERT of any kind; a write is a STOP-and-report).
**Restart: exactly one recreate** (`docker compose up -d --no-deps backend`, one issuance — a second is a STOP). No served-code change → no refresh beyond the recreate itself.

## Why this exists

SG-167 themed 3 controls (Chat Household select, Resolve, Retry) with tests green, deliberately unserved: the running service (expectation, verify on target: image `0bed0cc4`, the SG-165 generation) still serves the pre-slice bundle. This slice makes the fixed code live: ONE rebuild + exactly ONE recreate + verify. No product, test or config byte is edited: the diff ceiling is `docs/worklogs/SG-168*`.

How the code becomes live (`PG-PR-04`): `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` (one rebuild; the `BUILDX_CONFIG` relocation is the documented EROFS-sandbox workaround, SG-154/SG-165 precedent) + `docker compose up -d --no-deps backend` (exactly one recreate) + verify.

## G1 — rebuild (one) + exactly one recreate

BEFORE (read-only): container id, image id (expect `0bed0cc4`, verify), RestartCount/Created, health ×6 via `{{HEALTH_CMD}}` with bodies quoted, gate http:80/https:443, alembic (expect `20260924_sg114_relation (head)`, verify — no migration runs here), served bundle names + sizes (`index-*.js/css` + `index.html` asset reference), 28-table counts, CORS preflight (OPTIONS only, zero mutating requests). BUILD (exactly one): record new image id (must differ — the frontend bytes moved). RECREATE (exactly one): record container-id change (RestartCount resets, never the proof). AFTER: all of the above re-read.

## G2 — verify live (state change by post-state)

Health ×6 exact, delta 0 vs BEFORE · gate unmoved · alembic head unmoved · counts delta 0 every table · served bundle MOVED (new `index-*.js` hash + `index.html` reference move — the rebuild proof; the SG-167 theming reuses existing Tailwind tokens per F-SG165-2, so a byte-identical CSS bundle is expected and the JS move carries the proof) · served markers in the fresh JS for the shipped surfaces (quote each ×1) · CORS preflight green with ZERO writes · pages `/capture` `/inbox` `/catalog` 200 each through the fresh server. Full end-to-end sweep WAIVED per `PG-DP-02` (restart-gated: externally-driven tests would exercise the previous build); substitute coverage is the health/counts/preflight/bundle proof above plus SG-167's already-green targeted suites; no browser-driven hits.

## Constraints

Scope ceiling: `docs/worklogs/SG-168*` only; `models/`+`alembic/` diff empty (prove it); product diff empty (prove it). Spend: $0 (no metered path). Publish-before-bound: report + receipt before 1050s elapsed (half of `RUN_BUDGET_S=2100`). Expected duration ~300s (SG-165 actual: recon ~110s + build 26s + recreate 2s + verify ~30s; lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, build 600s, verify 120s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans. No migration, no second recreate, no mutating live request.

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

- A1: rebuilt + one recreate + live (image id new on one build, container id new on one recreate, health ×6 delta 0, counts delta 0, preflight green) — quoted both sides.
- A2: no migration (`alembic current` == head both sides; `models/`+`alembic/` diff empty).
- A3: product diff empty (exactly `docs/worklogs/SG-168*` moved).
- A4: report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); publish-before-bound honored with elapsed quoted; production writes = one rebuild + one recreate only, image ids quoted.
- A5: guards invoked: PG-DP-01, PG-DP-02, PG-IC-01, PG-IC-07, PG-PR-04, PG-PR-10.

## Report

Echo `SG-168` as the first token. Destinations: `docs/worklogs/SG-168_report.md` + build/verify logs. Close with FIRST READ / DURING EXECUTION / REMAINING.
