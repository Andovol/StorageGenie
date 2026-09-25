# SG-116 — Jina EU reachability probe: is `eu.s.jina.ai` dead or just unreached (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D9-approved read-only probe under D10 L3 (the SG-084/SG-071 verification-first precedent). F-SG104-3: `eu.s.jina.ai` is NXDOMAIN from host AND container while `s.jina.ai` resolves — measured twice (SG-082 report F-SG082-1: `ConnectError: Name or service not known`, EU attempts sent no HTTP request, 1 global diagnostic 200; SG-102 leg B: `getent` exit 2 + `gaierror`, loud transport degradation through the real client; SG-104: host `getent` empty + container `gethostbyname` Errno -2, `s.jina.ai` → `104.26.11.242`). The EU default stands by decision (SG-082: EU data residency, Romania scope; global is a named constant, never silently switched). THIS slice re-measures from today's host and returns a verdict: EU-ALIVE (close F-SG104-3, change nothing) / EU-ALIVE-TRANSPORT (HTTP response without results — host live, status is the finding) / EU-DEAD (recommend a follow-up slice switching the default — NOT implemented here) / INCONCLUSIVE-transient (recommend re-probe). **No code change is made here; no switch, no migration, no container action.** **Authoring date (metadata, never a gate):** 2026-09-25. Transport: the standard job_spawn lane. Contract: recorded `0.36.0` == published (`a9324d5`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** read-only EVERYTHING except `docs/worklogs` — no builds, no container actions, no migrations, no DB writes, no code/test/prompt edits. NETWORK egress allowed ONLY to `eu.s.jina.ai:443`, `s.jina.ai:443`, and DNS — max TWO Jina searches total (one EU through the real client, one global diagnostic iff EU fails), each under the client's own 15s timeout. Secrets: key existence is names-only (`JINA_API_KEY` present/absent — never print, log, quote, or commit a key byte); `docker compose config` output is FORBIDDEN (`PG-SC-05` exclude-by-rule — it prints secrets); no credential file fetched.
**Money posture:** max 2 metered Jina searches; real spend reported to 6 decimals (expected ≈ $0.00–0.05).
**Guards invoked (0.36.0 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-03` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 60s ordinary, 600s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none. Container actions: none** (`docker` CLI queries are allowed read-only; any denial is reported as unanswered, never routed around).

## G1 — premises on the host tree (expectations, verify each)

- Work dir `/home/andrei/StorageGenie`: `git status --porcelain` (quote it — dirt is a finding), `git rev-parse HEAD` vs `origin/automation` (equal expected; a gap is a finding).
- `backend/app/services/enrich/jina.py:42-43` reads `JINA_EU_BASE_URL = "https://eu.s.jina.ai/"` + `JINA_GLOBAL_BASE_URL = "https://s.jina.ai/"` (my 2026-09-25 read; a difference is a finding and re-scopes G3 to the actual constants — do not bend yours to match). Key seam: `config.py:38-40` declares `jina_api_key`, `jina.py:59` names `JINA_API_KEY` env fallback.

## G2 — DNS legs (both bases, raw output committed)

- `getent hosts eu.s.jina.ai` + `getent hosts s.jina.ai` (quote exit code AND output each); plus one resolver cross-check (`python3 -c socket.getaddrinfo` or `nslookup`, quoted). An NXDOMAIN persisting on EU with global resolving reproduces F-SG104-3; EITHER base resolving differently than stated is a finding, not an obstacle.
- Key presence, names-only: is `JINA_API_KEY` present in the backend environment (existence boolean only — test without ever printing the value, e.g. a length/existence check whose output carries no key byte). Absent key is a STOP-as-SUCCESS: commit worklogs + `BLOCKED: no Jina key on host` first line, push, receipt, clean tree — **stopping here is the successful outcome** (`PG-SC-03`). What does NOT count as grounds to stop: slow DNS, one timed-out search (a timeout is a quoted finding of degradation, not a stop), `s.jina.ai` also failing (that widens the verdict to JINA-DOWN, still reported, not stopped).

## G3 — one real EU search through the REAL client, global diagnostic iff EU fails

- Exactly ONE search at the EU base via the real `fetch_jina_search` path (fixed query `Jacobs Cronat Gold`, brand `Jacobs`, category food — the SG-082/SG-104 query shape; `num=5 type=web gl=ro` defaults). Quote the snapshot: status vs transport reason, bytes, elapsed.
- Iff the EU leg degrades on transport, exactly ONE diagnostic search at the global base (same query). Total searches ≤ 2, real spend quoted.
- Verdict line, exactly one: EU-ALIVE (EU search returned HTTP with results — F-SG104-3 closes, recommend nothing) / EU-ALIVE-TRANSPORT (any HTTP response incl 4xx/5xx — DNS and host live; the status itself is the finding, e.g. key rejection, and F-SG104-3 closes as transport-alive) / EU-DEAD (EU NXDOMAIN/transport-dead, global answers — recommend follow-up slice switching the default, with the one-line reason a switch is now evidenced) / INCONCLUSIVE (transients both sides — recommend re-probe, never a switch).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-116.log`, `SG-116_report.md`, `SG-116_verify.log` (raw DNS outputs + raw snapshot bodies, key bytes never). First token `SG-116`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** to 6 decimals); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) for WRITES. READS: work tree, DNS resolver, HTTPS to the two named Jina bases only — all read-only. **Any write outside `docs/worklogs` is a STOP** — code, tests, prompts, compose, `.env`, migrations, STATE/AGENTS.
- Cross-product (`PG-IC-01`): G1–G3 need file reads + DNS + ≤2 HTTPS egress + 3 worklog files; nothing else. No criterion touches containers, the DB, or the running service. The HTTPS egress G3 requires is allowed above with its bound in its own sentence — no blanket network permission exists elsewhere.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): resolve, search, verdict. No switch is implemented here, however small.

## Acceptance criteria

- Tree state quoted (porcelain + HEAD vs origin); `jina.py:42-43` values quoted as found with any difference from §G1 stated.
- Both DNS legs quoted (exit + output + cross-check); key existence boolean without key bytes, or `BLOCKED: no Jina key on host` path taken.
- EU search snapshot quoted (or transport degradation quoted with the exact error); global diagnostic quoted iff run; total searches ≤ 2 stated with real spend.
- Exactly one verdict line (EU-ALIVE / EU-DEAD / INCONCLUSIVE) with the one-line reason; EU-DEAD carries the follow-up outline, implemented nowhere here.
- No writes outside `docs/worklogs`; no vacuous pass (a transport failure evidences the reachability verdict — it never evidences "search works").

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** to 6 decimals.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-116 | Report: docs/worklogs/SG-116_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

60s ordinary · 600s overall; expected ~300s (Architect's record; the lane enforces `RUN_BUDGET_S`); ≤2 metered Jina searches, real spend quoted; actual-versus-budget per leg with units.
