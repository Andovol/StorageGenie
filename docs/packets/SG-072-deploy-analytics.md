# SG-072 — deploy rider: analytics routes + screen live on the public entry (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 10 — the D93-approved deploy rider for SG-066 (audited 98): its work sits at `0c9fc1b` on `automation`, NO migration ships (stateless — verified: no new file under `backend/alembic/versions/` beyond `20260917_sg068_saved_search.py`; re-verify in-slice), the production SQLite stays at head `20260917_sg068_saved_search`, but the running container still serves the SG-070-era image (bundle `index-CZqbqy4J.js`, 296980 bytes, sha256 `5bf83861197eb73b1b54c94bc12e7215fa734a77329329a6d480a53051cf1598` — quoted from SG-070's measured record) WITHOUT the analytics routes/screen. This slice rebuilds and brings the new image live with the STANDARD verification set. **Production restart authorized by the owner (D93) — the only authorized production mutation; everything else is read-only.** Recorded facts, verify in-slice (quoted reads):
- Port map: one service, backend loopback `127.0.0.1:8003`; public entry nginx vhost + `auth_basic` at `https://storagegenie.dynv6.net` (cert to 2026-12-14); loopback Host-header form for on-box public checks (F-SG053-2).
- Migrations: DB at `20260917_sg068_saved_search` (head); SG-066 shipped no revision, so **in-container `alembic current` must read that same head BEFORE and AFTER; running any `alembic upgrade` is out of this slice's authority — a mismatch is a STOP and report.** F-SG069-1 precedent stands (stale image may not resolve the head — then the authoritative before-read is the DB's `alembic_version` table directly, read-only).
- Seed household `01a0a029-1477-7ca0-b200-bce78a96c679` (Toothpaste rows) — query parameter only, READ-ONLY. Bare `GET /v1/analytics/summary` (no `household_id`) is `422` — the required-param precision from F-SG070-1 is built into every criterion below, not re-discovered.
- Taxonomy + saved-searches + facets endpoints are already live — pre-change sanity checks and post-change regression checks, never the discriminator.
- The BUILDX_CONFIG relocation (F-SG067-2, reused SG-069/070) is available precedent: if `docker compose build` fails on the buildx config dir, relocate `BUILDX_CONFIG` to a writable tmp dir and report it — no privilege probing.
- Baked-UI deploy shape (F-SG069-2): the public bundle is baked into the backend image; the backend rebuild+recreate is the entire deploy; the `frontend` service under profile `dev` stays untouched.
**Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); host link from SG-071's echo (`0.28.2` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration; no seed; no data writes; no provider calls ($0 — a metered call is a STOP-and-report; this expressly includes the insights POST — see G2); NETWORK: loopback + container runtime only.
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-06` (authority: NONE) · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (this slice IS the live proof) · `PG-PR-06`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 900s build+up, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none** — no migration, no seed, no writes. **Restart: the storagegenie stack only** (one `docker compose up -d` recreate — the authorized D93 production restart).

## G1 — rebuild + bring up (the authorized restart)

- `docker compose build` then `docker compose up -d` (recreate exactly once). Build bound 900s; the BUILDX_CONFIG relocation rule above applies.
- Health `{"status":"ok","db":"ok","storage":"ok"}` — two consecutive 200 reads after up (an instant-read HTTP 000 during settle is disclosed, not hidden — SG-067 precedent); RestartCount before/after quoted (restart loop = STOP); `ss` loopback-only preserved.

## G2 — the new behavior is LIVE (before-leg captured first — `PG-EV-08`/`PG-SC-12`)

- Served bundle: BEFORE quote (expected `index-CZqbqy4J.js`, 296980 B, sha256 `5bf83861…` from SG-070's measured record — a different actual is a finding, not an obstacle), then AFTER (expected DIFFERENT hash).
- **Analytics endpoint discriminator (GET-only — the POST stays untouched):** BEFORE `GET /v1/analytics/summary?household_id=<seed>` → 404 (route absent in the old image — quote it; note it may fall through to another route, quote what answers); AFTER → 200 with the stats shape (quote the body: totals + category counts + expiry buckets + adherence signals). **`POST /v1/analytics/insights` is NEVER called in this slice** — it runs the metered provider and is out of the $0 authority; the POST's liveness is proven structurally instead: the served bundle contains the insights client call (grep the bundle for `analytics/insights`, count quoted — SG-070 `v1/taxonomy` precedent) AND the backend image contains the route (grep the built tree for the route decorator, quoted). A metered call is a STOP-and-report.
- Taxonomy + saved-searches + facets endpoints still 200 after the rebuild (quoted, each with the seed `household_id`) — regression checks, not the discriminator.
- Gate: unauthenticated `curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/` → 401, before AND after; no credential file fetched.
- `PG-SC-09` named world where green is still wrong: a stale image (old bundle) passing health — the bundle-hash before/after + the 404→200 GET pair + the two structural greps are the discriminators; quote the new container/image ids.

## G2b — what must NOT change

- `alembic current` identical before/after (`20260917_sg068_saved_search` expected — the DB file is mounted; the container code change ships no revision). No upgrade run. No rows created (GET-only traffic + greps; `PG-EV-06` authority NONE — state the construction; quote `provider_call`/`guardrail_event` counts before/after via a read-only query if reachable — they must be unchanged).
- No `UPDATE`/`DELETE` against any existing table.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-072.log`, `SG-072_report.md`, `SG-072_verify.log` (raw curl/health/bundle/alembic/grep outputs). First token `SG-072`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) — NOTHING else in the repository. **Anything else is a STOP** — no code, no `.env`, no compose edits, no migrations, no data.
- Production surface in play: ONE recreate with NO data changes (D93, G-K2 authorized; anything beyond — extra restarts, retagging, credential fetches, any POST to the insights route — STOP and report).
- Cross-product (`PG-IC-01`): no criterion requires repo writes; the verification curls are read-only GETs; the greps read the served bundle and the built tree. Reads MAY pull/run the already-built local images only (the build is the authorized exception).
- Budget (uncalibrated per `G-A9`; SG-070 measured 158s wall): 120s ordinary · 900s build+up · 1800s overall — actual-vs-budget per leg with units.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Pre-bundle quoted; build+up once; two consecutive healthy reads; RestartCount 0→0; loopback preserved.
- Post-bundle hash different; analytics summary 404-before → 200-after (stats body quoted, seed `household_id` in the URL); insights POST never called ($0 held); bundle grep hits `analytics/insights`; built-tree route grep hits; taxonomy/saved-searches/facets still 200; gate 401 both sides.
- `alembic current` identical before/after (quoted, F-SG069-1 substitution if the stale image cannot resolve); `provider_call`/`guardrail_event` counts unchanged; prod DB otherwise untouched; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-072 | Report: docs/worklogs/SG-072_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 900s build+up · 1800s overall; REAL metered $0.000000 (zero calls — the insights POST is never called); actual-versus-budget per leg with units.
