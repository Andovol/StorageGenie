# SG-070 — deploy rider: taxonomy endpoint + inspector swap live on the public entry (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 8 — the D88-approved deploy rider for SG-065 (audited 98): its work sits at `3f2fd6b` on `automation` (plus docs-only `1cea56e`, rating `63e0f75`, close `9baba79`), the production SQLite is at head `20260917_sg068_saved_search` — SG-065 added NO migration (verified: `backend/alembic/versions/` holds no file newer than `20260917_sg068_saved_search.py`), but the running container still serves the SG-069-era image (bundle `index-CVg0y-4w.js`, 296747 bytes, sha256 `fcafabbfef694bdc8488156484ca1ac0e8dba16d51f1338cc1f0d02de07ab179` — quoted from SG-069's measured record) WITHOUT `GET /v1/taxonomy` and WITHOUT the inspector dropdown swap. The two Bolt bot merges (`df184e5`, `c849088`) landed BEFORE SG-065's rebase, so the rebuild carries them — no in-slice merge action. This slice rebuilds and brings the new image live with the STANDARD verification set. **Production restart authorized by the owner (D88) — the only authorized production mutation; everything else is read-only.** Recorded facts, verify in-slice (quoted reads):
- Port map: one service, backend loopback `127.0.0.1:8003`; public entry nginx vhost + `auth_basic` at `https://storagegenie.dynv6.net` (cert to 2026-12-14); loopback Host-header form for on-box public checks (F-SG053-2).
- Migrations: the DB is at `20260917_sg068_saved_search` (head); SG-065 shipped no revision, so **in-container `alembic current` must read that same head BEFORE and AFTER; running any `alembic upgrade` is out of this slice's authority — a mismatch is a STOP and report.** F-SG069-1 precedent stands: if the pre-deploy image cannot resolve the head, the authoritative before-read is the DB's `alembic_version` table directly (read-only), and the invariant (head unchanged, no upgrade) is proven both sides — accepted, not a STOP.
- Seed household `01a0a029-1477-7ca0-b200-bce78a96c679` (Toothpaste rows) — query parameter only, READ-ONLY.
- Saved-searches + facets endpoints are already live (SG-067/SG-069) — they are pre-change sanity checks and post-change regression checks, not the discriminator.
- The BUILDX_CONFIG relocation from SG-067 (F-SG067-2, reused SG-069) is available precedent: the coder confinement still lacks a writable `~/.docker`; if `docker compose build` fails on the buildx config dir, relocate `BUILDX_CONFIG` to a writable tmp dir (the accepted ruling) and report it — no privilege probing.
- Baked-UI deploy shape (F-SG069-2): the public bundle is baked into the backend image by `backend/Dockerfile`'s multi-stage `frontend-build` stage → `backend/static`; the backend rebuild+recreate is the entire deploy; the `frontend` service under profile `dev` stays untouched.
**Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); host link from SG-069's receipt echo (`0.28.2` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration; no seed; no data writes; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback + container runtime only.
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

**DATABASE: none** — no migration, no seed, no writes. **Restart: the storagegenie stack only** (one `docker compose up -d` recreate — the authorized D88 production restart).

## G1 — rebuild + bring up (the authorized restart)

- `docker compose build` then `docker compose up -d` (recreate exactly once). Build bound 900s; the BUILDX_CONFIG relocation rule above applies.
- Health `{"status":"ok","db":"ok","storage":"ok"}` — two consecutive 200 reads after up (an instant-read HTTP 000 during settle is disclosed, not hidden — SG-067 precedent); RestartCount before/after quoted (restart loop = STOP); `ss` loopback-only preserved.

## G2 — the new behavior is LIVE (before-leg captured first — `PG-EV-08`/`PG-SC-12`)

- Served bundle: BEFORE quote (expected `index-CVg0y-4w.js`, 296747 B, sha256 `fcafabbf…` from SG-069's measured record — a different actual is a finding, not an obstacle), then AFTER (expected DIFFERENT hash).
- **Taxonomy endpoint discriminator:** BEFORE `GET /v1/taxonomy` → 404 (route absent in the old image — quote it; note it may fall through to another route, quote what answers); AFTER → 200 with the registered-descriptor shape (quote the body: at least the `expiry-tracker` plugin entry with its category list carrying per-category `opened_date_tracking` and `chat` mode — read-only GET; `PG-EV-06` authority line: NONE).
- Saved-searches endpoint still 200 after the rebuild (quoted) — regression check, not the discriminator.
- Facets endpoint still live after the rebuild (200, quoted) — regression check, not the discriminator.
- Gate: unauthenticated `curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/` → 401, before AND after; no credential file fetched.
- `PG-SC-09` named world where green is still wrong: a stale image (old bundle) passing health — the bundle-hash before/after + the 404→200 endpoint pair are the discriminators; quote the new container/image ids.

## G2b — what must NOT change

- `alembic current` identical before/after (`20260917_sg068_saved_search` expected — the DB file is mounted; the container code change ships no revision). No upgrade run. No rows created (GET-only traffic; `PG-EV-06` authority NONE — state the construction; quote row counts via a read-only query if reachable, else the GET-only construction is the observable).
- No `UPDATE`/`DELETE` against any existing table; no test residue in production (no POST/PUT/PATCH/DELETE issued at all).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-070.log`, `SG-070_report.md`, `SG-070_verify.log` (raw curl/health/bundle/alembic outputs). First token `SG-070`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) — NOTHING else in the repository. **Anything else is a STOP** — no code, no `.env`, no compose edits, no migrations, no data.
- Production surface in play: ONE recreate with NO data changes (D88, G-K2 authorized; anything beyond — extra restarts, retagging, credential fetches — STOP and report).
- Cross-product (`PG-IC-01`): no criterion requires repo writes; the verification curls are read-only GETs. Reads MAY pull/run the already-built local images only (the build is the authorized exception).
- Budget (uncalibrated per `G-A9`; SG-069 measured ~90s wall): 120s ordinary · 900s build+up · 1800s overall — actual-vs-budget per leg with units.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Pre-bundle quoted; build+up once; two consecutive healthy reads; RestartCount 0→0; loopback preserved.
- Post-bundle hash different; taxonomy 404-before → 200-after (descriptor body quoted); saved-searches still 200; facets still 200; gate 401 both sides.
- `alembic current` identical before/after (quoted, F-SG069-1 substitution if the stale image cannot resolve); no rows created (GET-only construction stated); prod DB otherwise untouched; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-070 | Report: docs/worklogs/SG-070_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 900s build+up · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
