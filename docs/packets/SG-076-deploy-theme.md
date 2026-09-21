# SG-076 — deploy rider: Stone theme live on the public entry (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 14 — the D98-approved deploy rider for SG-075 (audited 98): its work sits at `d209ecc` on `automation`, NO migration ships (frontend-only slice — verified: `git show --stat` touches `frontend/src` + worklogs only; re-verify in-slice), the production SQLite stays at head `20260917_sg068_saved_search`, but the running container still serves the SG-074-era image (bundle `index-3DyyAB0n.js`, 301041 bytes, sha256 `79daad044b3da00c5ce540b6a2ec2dbba97222d40c36450fd48cf885cd8dc378` — quoted from SG-074's measured record) WITHOUT the token migration. This slice rebuilds and brings the new image live with the STANDARD verification set. **Production restart authorized by the owner (D98) — the only authorized production mutation; everything else is read-only.** Recorded facts, verify in-slice (quoted reads):
- Port map: one service, backend loopback `127.0.0.1:8003`; public entry nginx vhost + `auth_basic` at `https://storagegenie.dynv6.net` (cert to 2026-12-14); loopback Host-header form for on-box public checks (F-SG053-2).
- Migrations: DB at `20260917_sg068_saved_search` (head); SG-075 shipped no revision, so **in-container `alembic current` must read that same head BEFORE and AFTER; running any `alembic upgrade` is out of this slice's authority — a mismatch is a STOP and report.** F-SG069-1 precedent stands (stale image may not resolve the head — then the authoritative before-read is the DB's `alembic_version` table directly, read-only).
- Seed household `01a0a029-1477-7ca0-b200-bce78a96c679` (Toothpaste rows) — query parameter only, READ-ONLY. Every regression curl carries the seed `household_id` (F-SG070-1 precision).
- Analytics + taxonomy + saved-searches + facets endpoints are already live — pre-change sanity checks and post-change regression checks, never the discriminator.
- The BUILDX_CONFIG relocation (F-SG067-2, reused every rider since) is available precedent: if `docker compose build` fails on the buildx config dir, relocate `BUILDX_CONFIG` to a writable tmp dir and report it — no privilege probing.
- Baked-UI deploy shape (F-SG069-2): the public bundle is baked into the backend image; the backend rebuild+recreate is the entire deploy; the `frontend` service under profile `dev` stays untouched.
**Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
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

**DATABASE: none** — no migration, no seed, no writes. **Restart: the storagegenie stack only** (one `docker compose up -d` recreate — the authorized D98 production restart).

## G1 — rebuild + bring up (the authorized restart)

- `docker compose build` then `docker compose up -d` (recreate exactly once). Build bound 900s; the BUILDX_CONFIG relocation rule above applies.
- Health `{"status":"ok","db":"ok","storage":"ok"}` — two consecutive 200 reads after up (an instant-read HTTP 000 during settle is disclosed, not hidden — SG-067 precedent); RestartCount before/after quoted (restart loop = STOP); `ss` loopback-only preserved.

## G2 — the new behavior is LIVE (before-leg captured first — `PG-EV-08`/`PG-SC-12`)

- Served bundle: BEFORE quote (expected `index-3DyyAB0n.js`, 301041 B, sha256 `79daad04…` from SG-074's measured record — a different actual is a finding, not an obstacle), then AFTER (expected DIFFERENT hash; the build also emits a new `index-*.css` token stylesheet — quote its name + size).
- **Theme-shipped discriminator (structural — no browser on the box):** the served AFTER bundle contains SG-075's new utilities: grep the served bundle file for `page-header` (count quoted — a utility that exists ONLY post-SG-075; verify the BEFORE bundle lacks it, count 0, so the pair is genuine). BEFORE pair (old bundle): `page-header` count 0 AND a hardcoded Gegenwart probe — grep the old served bundle for `#111827` (App.tsx's old inline ink, count ≥1 expected — proves the old bundle predates the migration). AFTER: `page-header` ≥1 AND `#111827` count 0. All four numbers quoted.
- Analytics summary + taxonomy + saved-searches + facets endpoints still 200 after the rebuild (quoted, each with the seed `household_id`) — regression checks, not the discriminator.
- Gate: unauthenticated `curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/` → 401, before AND after; no credential file fetched.
- `PG-SC-09` named world where green is still wrong: a stale image (old bundle) passing health — the bundle-hash before/after + the `page-header` 0→≥1 pair + the `#111827` ≥1→0 pair are the discriminators; quote the new container/image ids. BEAUTY is explicitly NOT proven here — the owner's eyeball on the public entry is the final authority (D96).

## G2b — what must NOT change

- `alembic current` identical before/after (`20260917_sg068_saved_search` expected — the DB file is mounted; the container code change ships no revision). No upgrade run. No rows created (GET-only traffic + greps; `PG-EV-06` authority NONE — state the construction; quote `provider_call`/`guardrail_event` counts before/after via a read-only query if reachable — they must be unchanged).
- No `UPDATE`/`DELETE` against any existing table.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-076.log`, `SG-076_report.md`, `SG-076_verify.log` (raw curl/health/bundle/alembic/grep outputs). First token `SG-076`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) — NOTHING else in the repository. **Anything else is a STOP** — no code, no `.env`, no compose edits, no migrations, no data.
- Production surface in play: ONE recreate with NO data changes (D98, G-K2 authorized; anything beyond — extra restarts, retagging, credential fetches — STOP and report).
- Cross-product (`PG-IC-01`): no criterion requires repo writes; the verification curls are read-only GETs; the greps read served bundle bytes. Reads MAY pull/run the already-built local images only (the build is the authorized exception).
- Budget (uncalibrated per `G-A9`; SG-074 measured <300s wall): 120s ordinary · 900s build+up · 1800s overall — actual-vs-budget per leg with units.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Pre-bundle quoted; build+up once; two consecutive healthy reads; RestartCount 0→0; loopback preserved.
- Post-bundle hash different (+ new token stylesheet quoted); `page-header` 0-before → ≥1-after; `#111827` ≥1-before → 0-after (all four numbers quoted); analytics/taxonomy/saved-searches/facets still 200; gate 401 both sides.
- `alembic current` identical before/after (quoted, F-SG069-1 substitution if the stale image cannot resolve); `provider_call`/`guardrail_event` counts unchanged; prod DB otherwise untouched; nothing pushed to `storagegenie-evidence`; no vacuous pass; beauty explicitly deferred to the owner.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-076 | Report: docs/worklogs/SG-076_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 900s build+up · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
