# SG-059 — hygiene: proper Response mocks + :8000 reference audit (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** L3 stage D80 slice 3 of 4 (SG-057 GO, SG-058 GREEN). Two hygiene items: (1) F-SG049-5 band-aid revert — `frontend/src/api/client.test.ts:80,93` carry `as unknown as Response` double-casts (SG-049's minimal fix for the bot-PR `573ff02` tsc red); replace with properly-typed mocks, no `as unknown` anywhere in the file. (2) F-SG055-1/F-SG056 port audit — `:8000` is a FOREIGN occupant on the host (standing record: SG-053 F-SG053-1, SG-054 F-SG054-2); ours is `127.0.0.1:8003:8000` (`docker-compose.yml:8`). Some `:8000` occurrences are CORRECT (container-internal: healthcheck `docker-compose.yml:21`, compose right side `:8`); some are HOST-STALE (frontend `|| "http://localhost:8000"` fallbacks bind on the host where :8000 is foreign). Audit set (verify each, fix the stale, keep the correct — per-file verdict quoted): `frontend/src/api/client.ts:12`, `frontend/src/components/AssetCard.tsx:7`, `frontend/src/components/catalog/ProductCard.tsx:56`, `frontend/src/components/CandidateCard.tsx:47`, `frontend/src/components/EvidenceGallery.tsx:4`, `frontend/src/types/product.ts:109`, `frontend/src/routes/SettingsPage.tsx:17`, `frontend/vite.config.ts:9`. `AGENTS.md:29` `{{HEALTH_CMD}}` (`curl localhost:8000`) is OFF-LIMITS (rule file — deliver a concrete amendment proposal, DO NOT EDIT). **Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract 0.27.0 (recorded == published payload == SG-058 receipt echo; packet states it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration; no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback + container-runtime only, nothing else.
**Money posture (F2):** spend UNCAPPED-but-ledgered with re-evaluation owed; this slice makes zero provider calls so the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-not-command · `PG-EV-05` property-not-command · `PG-SC-09` name-the-world · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` code-becomes-live · `PG-DP-02` no-sweep-waiver.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build, 900s host build/up. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** All tests use scratch temp SQLite; no live import runs; the production SQLite is touched by nothing.

## Why this exists

The band-aid silences the compiler instead of typing the mock — the next strictness bump breaks it again. The `:8000` fallbacks bind to a foreign occupant on any host without `VITE_API_BASE` set, sending dev-mode API traffic (and the Settings page display) to another project's 404. Neither is live-broken in production (baked `VITE_API_BASE` wins there); both are landmines with the owner's name on them.

## G1 — proper Response mocks (test file only)

- `client.test.ts`: replace both `as unknown as Response` double-casts with properly-typed fetch mocks (a minimal `Partial<Response>`-shaped helper or per-test typed literal — design is yours; no `as unknown` remains in the file, verified by grep). Every assertion the file makes is kept; behaviour under test is unchanged (mock shape only).
- No FAIL-then-PASS leg exists here (nothing fails today — the band-aid is green) — state that honestly instead of manufacturing one; the guards are `tsc` green + the file's tests green + a grep proving zero `as unknown` in the file.

## G2 — :8000 audit (enumerate, classify, fix stale, propose the rule delta)

- Enumerate EVERY `:8000`/`localhost:8000`/`127.0.0.1:8000` occurrence in PRODUCT files (frontend src, compose, Dockerfiles, backend config — criterion, not list; docs/worklogs/history/STATE/ratings are the historical record and stay untouched) and report the diff vs this packet's expectation either way.
- Per occurrence, quote the verdict: IN-CONTAINER-CORRECT (healthcheck, compose right side, vite proxy — each with the reason it resolves inside the container) or HOST-STALE (resolves on the host where :8000 is foreign). Fix the HOST-STALE product occurrences to `:8003` (or the correct host value with quoted reason); keep the correct ones with quoted reason.
- Live probes quoted: `:8003/v1/health` exact JSON + `:8000/v1/health` foreign 404 — the discrimination that makes the classification more than grep.
- Deliverable, NOT an edit: a concrete `AGENTS.md:29` `{{HEALTH_CMD}}` amendment proposal (old line, new line, reason) for the owner — editing a rule file is off-packet-surface and a STOP if attempted silently.
- `PG-SC-09`: name the world where fixing a fallback is wrong (a dev environment where something legitimately serves on host :8000) and why the slice still ships (production bakes `VITE_API_BASE` so fallbacks never bind there; dev without it currently hits foreign — the fix strictly improves; any dev binding :8000 locally is reported as a finding).

## G3 — suite + lint + build + deploy + hygiene

- Backend suite + frontend suite + `ruff`/`eslint` + `tsc && vite build` green; only base-proven pre-existing reds permitted (cite base commit + base-run command and output, or they are new findings with destinations). Gates name files checked with counts+elapsed; silent gates FAIL.
- Deploy (frontend code changed — `PG-PR-04`): rebuild + up, idempotent re-`up -d` (same container, RestartCount=0), health exact, 8003 loopback-only. Property: served frontend bundle hash CHANGED (frontend hunks must reach the served bytes — inverse of SG-058's property). Full sweep WAIVED per `PG-DP-02` (substitute = suite/lint/build + targeted checks, named here).
- Prod DB untouched (no import, no writes — state the construction); no migration; dep list unchanged; secret scan n/a (no secrets touched — state it); no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-059.log`, `{{WORKLOG_DIR}}/SG-059_report.md`, `{{WORKLOG_DIR}}/SG-059_verify.log` (audit table + probes + deploy raw). First token `SG-059`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend line (**real $** $0.000000 actual vs $0 bound); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/api/client.test.ts` (mock hunk) · the eight audit-set files above (per-file verdict; hunks only where HOST-STALE is proven) · `docs/worklogs` (3 files). **Anything else is a STOP** — including `AGENTS.md`, `STATE.md`, `docker-compose.yml` (read-only premise), `backend/` (none), `.env`, and any new dependency.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G-hunks share no condition with any remediation step — stops win (`PG-IC-03`). Reads MAY pull/run the already-built local images only.
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · 900s host build/up · **1500s early-close** · **2400s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): typed mocks, stale fallbacks, one proposal; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified in-slice with quoted reads — in particular the band-aid lines, the eight audit-set lines, compose publish line, healthcheck line.
- `:8000` enumeration with diff vs expectation either way; per-file verdict quoted (correct-kept vs stale-fixed); live probe discrimination quoted (`:8003` JSON vs `:8000` foreign 404).
- `tsc` green with zero `as unknown` in `client.test.ts` (grep quoted); file's tests green with assertions kept.
- Suite + lint + build green (only base-proven reds); deploy targeted checks quoted (same container, RestartCount=0, bundle CHANGED, health exact, loopback-only); AGENTS proposal delivered as text, file untouched (prove with `git diff --stat` showing no AGENTS.md); prod DB untouched; no migration; dep list unchanged; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-059 | Report: docs/worklogs/SG-059_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 900s host build/up · 1500s early-close · 2400s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
