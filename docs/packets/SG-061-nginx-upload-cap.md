# SG-061 — read-only host check: nginx upload cap on the public entry (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 1 (stage approved 2026-09-17 minus the second-provider slice — one provider only, owner word). Purpose: measure whether the nginx vhost serving the public entry sets `client_max_body_size`, closing an open question (ISS-1). Expected facts, all re-verified in-slice: (a) `VPS.md` F3, measured 2026-09-17 by Launcher — nginx 1.24.0, `sites-available`/`sites-enabled` layout, **no host-wide `client_max_body_size`: the 1 MB default applies to every site that does not set its own**; (b) the public entry is `https://storagegenie.dynv6.net` (nginx vhost + `auth_basic` gate, proxying the app at `127.0.0.1:8003` — the live port map from the latest deploy reports); (c) the app accepts up to a 20 MB upload (expected at `backend/app/config.py:11` — hypothesis, verify in-tree); (d) a 25M ask was posted on the exposure request (`#34` comment 5695532154, 2026-09-16) — the desk may have applied it on-box since, so **the on-box measurement is the authority, not the comment thread**. **Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published payload (tag `contract-v0.28.2`, `b495b59`, verified at adoption D82); **your contract copy may still echo `0.27.0` (host-side install arc pending, F-SG056-3) — echo verbatim whatever your copy says and report WHICH version string and source path you read; a difference is a finding, not an obstacle.**
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration; no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); **READ-ONLY on the host** (details in Constraints); no product code changes anywhere; NETWORK: loopback + container-runtime only, nothing else.
**Money posture:** this slice makes zero provider calls; the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-02` artifact-not-command · `PG-EV-05` property-not-command · `PG-EV-06` rows-your-run-creates · `PG-SC-03` unread-precondition-is-a-goal · `PG-SC-09` name-the-world · `PG-SC-12` proof-runs-on-the-real-thing · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-01` non-mutating-enumeration · `PG-PR-03` denied-is-stop · `PG-EV-03` stop-not-disclosure.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 900s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** The production SQLite is touched by nothing. **Restart: none.** No service, container or nginx operation of any kind.

## Why this exists

The app accepts 20 MB uploads; nginx rejects bodies over 1 MB unless the site sets its own `client_max_body_size` (VPS.md F3, measured 2026-09-17 — no host-wide override). A 25M ask was filed with the desk on 2026-09-16 but never verified on-box. If the cap is still missing, every photo upload over 1 MB dies at the gate with 413 before the app ever sees it — the owner's live use would hit this immediately and confusingly. One read-only measurement settles it.

## G1 — identify the vhost (read-only)

- List `/etc/nginx/sites-available/` and `/etc/nginx/sites-enabled/` (read-only), grep them for `storagegenie.dynv6.net` (`server_name`) and `127.0.0.1:8003` (`proxy_pass`). Quote the hits with file:line.
- Name the ONE site file that serves the hostname, and confirm the `sites-enabled` link exists (name the link you checked). **PG-SC-09, named world:** a server block could set the cap while the request actually hits a DIFFERENT block (server_name collision, default server, missing enabled link) — your identification must rule that out, or say it cannot and what you would need (that unanswered step is then reported as such, not guessed).
- **What does NOT count as grounds to stop:** no matching file, an unexpected shape (e.g. certbot-mangled config), or an `auth_basic` reference — each is a FINDING reported as success. STOP only for the privilege denial or an impossible step, per the stop path.

## G2 — read the effective upload cap (read-only)

- If the vhost (or an included snippet it names — follow include directives one level) sets `client_max_body_size`: quote the line with file:line.
- If absent everywhere relevant: the answer is **"absent → 1 MB default applies"** (VPS.md F3) — and the absence claim cites the exact grep over the site file + includes that produced it. **An absence claim without its grep is a FAIL, not a pass** (M22 standing rule).
- State the effective cap as one number with its unit.

## G3 — verdict against the app (in-tree verify, still read-only on the host)

- Verify the app's accepted upload size in-tree (expected `backend/app/config.py:11` = 20 MB): quote the actual line and path you read. If it differs from the expectation, that is a finding — do not bend it.
- State the verdict in one line: measured cap vs app cap — **which upload body sizes the public entry ACCEPTS, and which die at the nginx gate (413) before the app sees them.** Name your check's subject explicitly (`PG-SC-12`): this runs against the real nginx config on the box, not a template or a local stand-in.
- Suggested cap design belongs to the desk request already filed — do NOT propose or apply one; this slice measures and reports only.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-061.log`, `{{WORKLOG_DIR}}/SG-061_report.md`, `{{WORKLOG_DIR}}/SG-061_verify.log` (raw quoted reads). First token `SG-061`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend line (**real $** $0.000000 actual vs $0 bound); contract version echo + the source path you read it from; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` (3 files) — and NOTHING else in the repository. **Anything else is a STOP** — no product code, no `AGENTS.md`, no `.env`, no compose files, no docs edits.
- **READ-ONLY ON THE HOST (`PG-PR-01`):** every host command must be a form that changes nothing if it succeeds — read/ls/grep/cat-class only. No `sudo`, no nginx `-t`/reload/restart, no service or container operations, no file writes, no config edits, no requests that could create rows (an accepted upload = production rows with no authority to create them — `PG-EV-06`). State the command classes you ran in the report; silence is not compliance.
- Secret gate: never run `docker compose config` (its output prints host `.env` secrets — SG-041 advisory); never quote credential/key files or htpasswd contents; paste config structure lines (server_name/proxy_pass/listen/include/client_max_body_size) only.
- Cross-product (`PG-IC-01`): no blanket exclusion issued; no acceptance criterion requires a forbidden action (nothing here requires privilege or a write). Reads do NOT include running containers — none are expected; if you believe one is needed, STOP and report instead.
- Budget (uncalibrated per `G-A9`; this lane's read-only box checks measured ~28–140 s previously): 120s per command · 900s overall — actual-versus-budget per leg with units.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified in-slice with quoted reads (vhost shape, app cap line, `VPS.md` F3 facts).
- Vhost file named with quoted grep evidence; effective cap stated as a number (set-line quoted, or absence-grep quoted + "1 MB default applies"); verdict vs the app's cap stated in one sentence.
- Non-mutating command classes stated; repo diff = worklogs only; no migration; no deploy; prod DB untouched (state the construction); nothing pushed to `storagegenie-evidence`; no vacuous pass.
- If the desk ask was already applied (cap >= 20 MB): say so plainly — that is the green answer, not a stop.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-061 | Report: docs/worklogs/SG-061_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s per command · 900s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
