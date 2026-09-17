# SG-067 — deploy rider: SG-064's catalog facets + evidence_ids live on the public entry (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 4 — the D84-approved deploy rider for SG-064 (`98` at audit). SG-064's work sits at `4060bb0`(+ receipt docs) on `automation`, audited green, NOT deployed: the production service still runs the `index-nugWvqun.js`/v2-prompts image (`fe509cf0`) from 2026-09-17's SG-049 run-2. This slice rebuilds and brings the new image live with the STANDARD verification set. **Production restart authorized by the owner (D84, 2026-09-17) — the only authorized production mutation; everything else is read-only.** Re-verify in-slice, quote reads:
- Port map: one service, backend bound `127.0.0.1:8003` (loopback-only; public entry = nginx vhost + `auth_basic` at `https://storagegenie.dynv6.net`, cert valid to 2026-12-14).
- Migration heads: expected NONE added by SG-064 (`alembic/` clean — verify in-tree; head expected `20260916_sg048_name_optional`); **if the tree unexpectedly gains a head, STOP and report — running a migration is out of this slice's authority.**
- Seed household `01a0a029-1477-7ca0-b200-bce78a96c679` exists with assets (at least the `unknown`-type Toothpaste rows) — only used as a query parameter, READ-ONLY.
- On-box public-hostname checks use the loopback Host-header form (F-SG053-2 standing line): `curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/...`.
**Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + name the source path (SG-062 precedent: `/home/andrei/storagegenie-contract/VERSION`).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration (unless explicitly covered below — it is NOT); no seed; no data writes; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback + container runtime only.
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` gates-seen-failing · `PG-EV-02` artifact-not-command · `PG-EV-05` property-not-command · `PG-EV-06` rows-your-run-creates (as authority: NONE authorized) · `PG-SC-09` name-the-world · `PG-SC-12` proof-on-the-real-thing · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` live-proof-scoped (this slice IS the live proof) · `PG-PR-06` runtime-vs-budget.

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

**DATABASE: none** — no migration, no seed, no writes; `Restart: the storagegenie stack only` (`docker compose up -d` recreate) — the authorized production restart (D84).

## G1 — rebuild + bring up (the authorized restart)

- `docker compose build` then `docker compose up -d` (recreate). Cap the build at its 900s bound; a fixture-rewriting or source-mutation command MUST be reverted (there is none expected).
- Health: `{"status":"ok","db":"ok","storage":"ok"}` at `127.0.0.1:8003/v1/health` — TWO consecutive reads after up (immediately and after settling), RestartCount observed via compose/docker inspect of the backend container (quote before/after — a restart LOOP is a STOP).
- `ss` (or compose) confirms loopback-only binding preserved.

## G2 — the new behavior is LIVE (each failure leg captured before, the result after — `PG-EV-08`/`PG-SC-12`)

- Served bundle: `GET /` HTML references a hashed asset name; **quote the pre-change hash from the CURRENT served bytes FIRST** (expected `index-nugWvqun.js`), then the post-change hash (expected DIFFERENT — a new `index-<hash>.js`).
- Facets endpoint live: `curl 127.0.0.1:8003/v1/assets/facets?household_id=<seed>` → 200, shape `{"asset_type":{...},"status":{...},"has_evidence":{"with":N,"without":M}}` (or empty maps — seed may carry few rows); quote the actual counts.
- `evidence_ids` live: one shape assertion that a `GET /v1/assets?<seed>` row carries `evidence_ids` (quote it).
- Public entry through the LOCAL gate (loopback Host-header form): unauthenticated `/` → 401 (nginx `auth_basic`); the gate check is status-code-only (401 without credentials); do NOT fetch or quote credential files.
- `PG-SC-09` named world where a green here is still wrong: a stale image serving the OLD bundle would pass "health ok" — your bundle-hash before/after is the discriminator; also state which container/image id now serves.

## G2b — what must NOT change

- No migration ran (quote the `alembic` head check: `revision id` equal to the pre-change head); no new rows created by this slice (its own calls are GETs only — `PG-EV-06` authority line); no data touched.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-067.log`, `SG-067_report.md`, `SG-067_verify.log` (raw curl/health/bundle outputs). First token `SG-067`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** NO repository product file edits AT ALL — `docs/worklogs` (3 files) only. **Anything else is a STOP** — no code, no `.env`, no compose files, no migrations, no data.
- Production surface in play: ONE `docker compose up -d` recreate with NO data changes (D84, G-K2 authorized; if any other production effect becomes necessary — extra restarts, image retagging beyond the default — STOP and report instead).
- Cross-product (`PG-IC-01`): no criterion requires code writes; nothing else forbids the verification curls (read-only GETs to the app's own API).
- Budget (uncalibrated per `G-A9`; prior deploy slices SG-041/052/053 ran within ~1800s): 120s ordinary · 900s build+up · 1800s overall — actual-vs-budget per leg with units.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS files and packet dirs: untouched (state pushes buffer locally until the wake).

## Acceptance criteria

- Pre-change bundle hash quoted (`index-nugWvqun.js` expected; a different actual is a finding, not an obstacle); build+up completed once (recreate, not a loop — RestartCount quoted); health ok three-times (quoting a consecutive-healthy proof for the entry point per `PG-DP-04`: two consecutive health reads after up).
- Post-change bundle hash different (new asset served for `/`); facets endpoint 200 with the real shape (counts quoted); a list row carries `evidence_ids`; gate 401 unauthenticated; loopback-only binding preserved.
- No migration (head quoted, unchanged); no rows created (the slice's own traffic is read-only GETs — state the construction); prod DB otherwise untouched; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash (docs-only diff). Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-067 | Report: docs/worklogs/SG-067_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 900s build+up · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
