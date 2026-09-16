SG-052 report — production deploy: serve the wardrobe tree live (opencode, medium)

**Status: BLOCKED — STOP at G1 (pre-state DB gate fired). No D69 mutation performed.**

## Header

- **Work dir:** `/home/andrei/StorageGenie` (as on host).
- **Origin remote:** `git@github.com:Andovol/StorageGenie.git`.
- **BASE REF requested:** `origin/automation`; **resolved commit:** `ef5f815fb56f1c9de8b8d800900a8008165f8368`
  (`L3 batch: SG-051 rating 98 + SG-052 deploy packet (D69)`). `HEAD == origin/automation` at start; worktree
  clean (`## automation...origin/automation` only).
- **WORK_HEAD:** the commit carrying these worklogs (stated in the delivery message; it cannot be stated
  inside a file that is itself part of that commit).
- **Model / effort (from process arguments, `CO-78`):** effort = `medium` (`opencode run --auto --dir
  /home/andrei/StorageGenie --variant medium <packet>`, process 741079); **model = `unknown`** — there is no
  `--model` flag in argv and no provider metadata exposed a model id to the process. Not read from any
  identity line.
- **Contract:** 0.27.0 (packet header; `STATE.md:1` `Version: 0.27.0`). The `.rules-cache/` contract checkout
  is absent from this working tree (same condition SG-051 reported), so the `G-L1` fetch/hash check could not
  be run locally; the packet header + `STATE.md:1` are the version evidence.

## What happened

All G1 pre-state probes ran (read-only). The starting tree, stack, listeners, health, served asset hash and
image id are quoted in `SG-052_verify.log`. `alembic current == heads == 20260914_sg035_foundations` (no
pending migration; the packet's "no migration needed" premise is TRUE). The SG-041 seed household is present.

Then the DB read-only probe found **real rows beyond seed**, created 2026-09-15 09:31:08:
`asset=1` (Toothpaste), `evidence=1` (a real Colgate toothpaste photo, `source_kind=upload`), `assertion=3`
(`source_type=user`, `accepted`), `audit_event=3` (`evidence.create`, `asset.create`, `asset.accepted`).

The packet makes this a stop condition in three places (`docs/packets/SG-052-production-deploy.md:35`, `:60`,
`:73`): *"If unexpected real rows beyond seed -> STOP (`PG-IC-08`)"* and *"Unexpected pre-existing real data
-> STOP (`PG-IC-08`, either direction)"*. The literal trigger is met. Per `PG-IC-03` ("stops win, stated not
assumed") I stopped **before** the D69 mutation. `docker compose up --build -d` and the idempotent re-`up`
were NOT run; G3 observables were NOT captured; the external nginx gate was NOT probed. No DB write, no
migrate, no seed, no product-file change.

## Guards invoked — disposition

| Guard | Disposition |
|---|---|
| `PG-EV-01` gate-seen-failing | MET. GATE A (seed-only expectation) FAILs on measured asset rows 1 vs expected 0; GATE B (deliberately wrong asset hash) FAILs as required; raw in `SG-052_verify.log`. |
| `PG-EV-02` artifact-exists | PARTIAL/N-A. The artifact checked (served index bytes, health JSON) is the SERVED response, never an exit code. No post-change artifact exists because no change ran. |
| `PG-EV-05` property-not-command | MET for the probes taken (values quoted: hash `/assets/index-khM4mS2k.js`, health JSON, row counts), not command exits. |
| `PG-EV-08` before-observable | MET. Before-state (tree, stack, listeners, health, asset hash, DB rows, image id) captured and committed in `SG-052_verify.log`. |
| `PG-EV-09` both-runs-committed | PARTIAL. The before-run is committed raw; there is no after-run because the slice stopped. Stated loudly, not claimed as a pass. |
| `PG-SC-10` no-ignored-commit | MET. `git status --porcelain --ignored` shows only pre-existing ignored caches/`.env`; nothing ignored is staged. |
| `PG-IC-01` cross-product | MET. G1 (reads) and G4 (worklogs) only; G2/G3 not entered. No blanket exclusion added. |
| `PG-IC-08` expectation-bounds | **FIRED -> STOP.** Measured rows differ from the packet's seed-only expectation; see F-SG052-1/5. |
| `PG-IC-09` premises-live | MET/RAISED. Migration-need premise re-verified true; the row-count premise was re-verified live and differs (F-SG052-1). |
| `PG-PR-01..PR-10` | `PG-PR-10` (which DB) MET: local SQLite `sqlite:////data/db/storagegenie.db`, read-only probes only. `PG-PR-03` (denied-is-stop): no privileged op was denied; none attempted. `PG-PR-04`/`PG-PR-06`: not exercised (no mutation). |
| `PG-DP-01`/`PG-DP-04` | NOT exercised (no delivery, no second bring-up): the slice stopped before G2. |

## Findings

- **F-SG052-1 (stop trigger).** DB is not seed-only: one real import (asset/evidence/assertions/audit events)
  at 2026-09-15 09:31:08, ~20 h after the SG-041 seed. Undocumented in any worklog (`Toothpaste` /
  `pasta-de-dinti` = 0 hits across `docs/worklogs`); no slice SG-042..SG-051 wrote it.
- **F-SG052-2 (contrary context, surfaced not hidden).** `STATE.md:13`, `:171`, `:173` document the D49/D59
  LIVE USE PASS — public entry LIVE 2026-09-15, owner drove the live app, remaining owner action "import real
  photos". The row shape is exactly what that pass produces. A reading therefore exists that the rows are
  *expected* and the gate should not fire. I did not adopt it: the packet's stated expectation is
  seed-household presence with real rows beyond seed as an explicit stop, and that judgement is the
  Architect's. See F-SG052-5.
- **F-SG052-3 (DB-neutrality).** The D69 mutation is DB-neutral (`backend/Dockerfile` CMD = bare `uvicorn`,
  no entrypoint migrate/seed; `backend/app/main.py` has no lifespan/startup write). The stop is a pure
  expectation-bounds stop, not a data-risk stop.
- **F-SG052-4 (premise verified).** "No slice since SG-041 added a migration" is TRUE.
- **F-SG052-5 (gate ambiguity, requested to be raised loudly).** The packet asks for per-table row counts but
  states no numeric expectation N, then makes "unexpected real rows beyond seed" a stop. On a publicly live
  service the owner was directed to use, *any* real row trips it, so it cannot separate expected owner data
  from rogue data. Recommend stating expected counts explicitly (including expected live-pass rows) or
  dropping the gate.

## Live-state ledger

- **Image id old -> new:** `56968d428c4c` (SG-041 backend, running, created 2026-09-14T13:43:40Z) ->
  **unchanged** (no build executed). Container `62b8cf6b0ce3`, Up 2 days (healthy).
- **DB writes:** **zero** (read-only: `alembic current/heads`, `sqlite3 -readonly`).
- **Live spend:** `$0` metered; AI OFF, no provider calls.
- **Network:** read-only loopback API checks only; no registry pulls (no build); no external calls by the slice.
- **Product diff:** none. **Ignored files staged:** none. **`storagegenie-evidence` push:** none.

## Acceptance criteria — honest status

- Starting tree / BASE == audited tip: **PASS** (`HEAD == origin/automation == ef5f815`, clean).
- No-migration-need proven: **PASS** (`current == head == 20260914_sg035_foundations`, no pending).
- Pre-state health + asset hash + listener state quoted: **PASS**.
- Unexpected pre-existing real data -> STOP: **FIRED** (asset=1 evidence=1 assertion=3 audit_event=3).
- Post-change health/hash/markers/loopback/gate/re-up/memory: **NOT RUN** (stopped before G2).
- Gate-seen-failing: **PASS** (GATE A + GATE B raw).
- No product-file diff / no DB write / no ignored staged / no evidence push: **PASS**.
- **No vacuous pass.** Nothing is claimed as passing that did not actually run; the slice did not pass — it
  stopped. No empty-diff / empty-set / skipped-gate pass is reported.

## Receipt (note on the coder-reports notes ref)

Worklogs committed and pushed to `automation`, worktree clean (`CO-55`). No push to
`storagegenie-evidence`; no `{{RECEIPT_CMD}}` (per this packet's M20-corrected block). The note was added on
WORK_HEAD with the first line carrying both `Dispatch-ID:` and `Report:` (`CO-97`); the notes ref was pushed
explicitly to `origin`; the refspec was fetched explicitly (`<ref>:<ref>`, M21 — a bare fetch never updates a
notes ref); and the executed `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` output is
pasted verbatim in the delivery message (it cannot live inside this file, which is itself part of the commit
the note is attached to — same as SG-047/SG-050). If that `show` output is absent from the delivery, this step
was not executed and must be called out loudly. Final line: `note=yes`.

## (d) UNCLEAR

- **FIRST READ:** whether "unexpected real rows beyond seed" meant *any* row beyond the SG-041 seed, or only
  rows the documented owner live pass would not produce. The packet states no expected count N and no blessed
  row set, so both readings are textually open; I treated the literal trigger as binding (`PG-IC-03`) and
  stopped, rather than silently deciding the Architect's gate for them.
- **DURING EXECUTION:** whether the stop was over-literal given F-SG052-2/3 (the deploy is DB-neutral and the
  rows look like the owner's own live-pass import). I judged that a production stop gate whose literal trigger
  is met must not be overridden by the Coder's inference about intent; the finding is surfaced with full
  context so the Architect can reissue the gate or bless the rows and re-dispatch.
- **REMAINING:** (1) the owner's live-pass data (1 asset + 1 evidence + 3 assertions + 3 audit events) is left
  untouched in the production SQLite; (2) the public site still serves the SG-041 image `/assets/index-khM4mS2k.js`
  — the wardrobe tree is NOT live; (3) the `.rules-cache/` contract checkout is absent from this tree, so the
  `G-L1` version fetch/hash check could not be run locally (packet header + `STATE.md:1` used as evidence).
