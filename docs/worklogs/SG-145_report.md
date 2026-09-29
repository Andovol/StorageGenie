# SG-145 — Probe the two lane limitations (`--sql` fts + host `gh` auth), fix nothing

**Dispatch-ID:** SG-145
**Role:** Coder (never Architect — no dispatch verb run, no unit started or polled for any ID).
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` requested → resolved):** `b157618c0a76f2faae002cb5c3457a0c08fb02ab`
(start HEAD was that same commit — the packet's `BASE REF` is a ref, the resolved commit is stated separately).
**WORK_HEAD:** `bd4f3acff8ae07f8995279714a05db6ca0d81d94`
**Contract:** recorded `0.40.0` == published — source path `/home/andrei/storagegenie-contract/VERSION`
(`0.40.0`); `git -C /home/andrei/storagegenie-contract rev-parse HEAD` = `f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c`
(commit subject `Contract payload 0.40.0`); `RULES.sha256` = `5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`.
**Model / effort (`CO-78`, from process arguments):** model `opencode-go/deepseek-v4.1-flash`, effort `high`
— source `/proc/846513/cmdline` → `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high # SG-145 …`. (No system-prompt identity used.)
**Spend:** **$0.000000 actual USD** — zero metered calls on every path (all probes are local greps, file
reads, one Alembic offline SQL generation that writes no database, and `gh auth status` presence-only).
**Live clock:** `2026-09-29T10:32:26Z` (first capture); probes span ~10:2x–10:33Z.
**Autonomy:** `L3` finish chain (slice 4 of 5); no retry used. **DATABASE none, restart none, deploy none.**

## Verdict: **GREEN** — both limitations established, zero fixes shipped, diff = 3 worklogs

Both item locations are now established with committed probes. **Neither is a "lane" limitation in the
dispatch sense:**
1. `--sql` is **Alembic's offline-SQL flag**, not a lane/wrapper flag. The live defect is in **repo
   migration code** (`fts.py` uses an online-only API under an offline run). A lane change cannot fix it.
2. `gh` on the host is genuinely unauthenticated; repairing it needs an **owner hand** (login/device
   code or token placement), so that leg is returned as a **relay ask**, never performed here.

No product/test/config/auth write occurred; the diff is exactly the three worklogs.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on host 2026-09-29 | Verdict |
|---|---|---|
| `--sql` lives in the lane/wrapper (`.rules-cache/dispatch` has none on the workstation) | `--sql` has **0** matches in `/usr/local/bin/dispatch`, `/opt/storagegenie-dispatch/*.sh`, `/etc/dispatch/*.conf`, and the contract `dispatch/` dir (`run-coder`, `dispatch`, `dispatch@.service`, …). Broad case-insensitive `sql` in the wrapper is also 0. The flag is Alembic's (`alembic/config.py:704`). | **CORRECTED** (F-SG145-2) |
| `.rules-cache/` is the contract cache | `.rules-cache/` **does not exist on the host**; it is gitignored and only on the workstation. The host contract checkout is `/home/andrei/storagegenie-contract` (lane conf `CONTRACT_DIR`). | **finding** (F-SG145-1) |
| offline `--sql` fts limit is a real standing defect | Reproduced read-only: `alembic upgrade head --sql` exits 1 at the FTS revision with `MockConnection … exec_driver_sql`. | **confirmed** |
| host `gh` unauthenticated | `gh auth status` → not logged in, exit 1; no `~/.config/gh`; no token env vars. | **confirmed** |
| contract recorded `0.40.0` == published `f26dbd3` | `VERSION`=0.40.0, HEAD `f26dbd3…`. | **confirmed** |
| `BASE REF origin/automation` | `git rev-parse origin/automation` = `b157618…` = start HEAD. | **confirmed** |

## G0 — located: every `--sql` entry point, with grep scope (`PG-SC-09`)

**The flag is Alembic's offline mode.** The only functional entry point on the target is the Alembic CLI:
`backend/venv/bin/alembic upgrade head --sql` (equivalently `python -m alembic upgrade head --sql`). Its
definition lives in the dependency at `backend/venv/lib/python3.12/site-packages/alembic/config.py:704`.

**Grep scopes quoted (see `SG-145_verify.log` for full output):**

```
$ git grep -l -- "--sql" -- ':!*/venv/*' ':!*/node_modules/*' ':!output/*'
21 lines / 9 files, ALL docs/history: STATE.md, docs/packets/{SG-139…,SG-145…},
docs/ratings.md, docs/superpowers/{plans,specs}/…roadmap-finish…, docs/worklogs/SG-139{,.log,_report.md,_verify.log}
→ ZERO product, script, test, or config file defines or consumes `--sql`.

$ grep -c -- "--sql" /usr/local/bin/dispatch /opt/storagegenie-dispatch/*.sh /etc/dispatch/*.conf \
      /home/andrei/storagegenie-contract/dispatch/*
→ 0 in every file (13 files checked: wrapper, 2 opt scripts, 5 lane confs, 5 contract dispatch files).

$ grep -in "sql" /usr/local/bin/dispatch          # broad, case-insensitive
→ no output (the installed wrapper contains no `sql` substring)
```

The repo's online Alembic invocations deliberately omit the flag: `Makefile:22` and `README.md:33,64` all
read `python -m alembic upgrade head`. **`--sql` is therefore NOT-FOUND in the lane** (scope quoted above),
which is a SUCCESS per `PG-SC-03`; the reachable occurrence is the Alembic CLI itself.

**Finding F-SG145-2 (category correction):** the packet's `{{WORKLOG_DIR}}`-style framing calls this a
"lane limitation". It is not — no lane/wrapper edit can change it. The fix is a **repo code slice**.

## G0 — limited: the fts bound, quoted from the producing code + read-only drive

**Where the bound lives** (read, not guessed — `PACKET.md` §2b):

- `backend/alembic/versions/20260908_sg017_fts.py:22` — `upgrade()` calls
  `install_asset_fts(op.get_bind(), rebuild=True)`.
- `backend/app/services/fts.py:94-106` — `install_asset_fts` type-checks the dialect, then calls
  `_ddl(connection)` at line **104**, then (if `rebuild`) `rebuild_asset_fts` at 106.
- `backend/app/services/fts.py:35` — `_ddl` first statement is `connection.exec_driver_sql(...)`, an
  **online-only** API. In offline (`--sql`) mode `op.get_bind()` is Alembic's `MockConnection`, which has
  no `exec_driver_sql`.
- `backend/alembic/env.py:28-32,47-48` — the offline branch (`context.is_offline_mode()` →
  `run_migrations_offline`) is the path exercised.

**Read-only drive (offline mode emits SQL to stdout; it opens/writes no database):**

```
$ (cd backend && timeout 120 venv/bin/alembic upgrade head --sql) > /tmp/opencode/sg145_alembic_sql.txt 2>&1
EXIT=1 ; LINES=259 ; INFO "Running upgrade" lines=4 ; "-- Running upgrade" comments=4 ; CREATE TABLE=14
...
INFO  … Running upgrade  -> 0201cf10c56c, 001 core foundation
INFO  … Running upgrade 0201cf10c56c -> 20260908_sg013_observation, …
INFO  … Running upgrade 20260908_sg013_observation -> 20260908_sg014_candidate, …
INFO  … Running upgrade 20260908_sg014_candidate -> 20260908_sg017_fts, SQLite FTS5 index for asset catalog search.
...
  File "…/backend/alembic/versions/20260908_sg017_fts.py", line 22, in upgrade
    install_asset_fts(op.get_bind(), rebuild=True)
  File "…/backend/app/services/fts.py", line 104, in install_asset_fts
    _ddl(connection)
  File "…/backend/app/services/fts.py", line 35, in _ddl
    connection.exec_driver_sql(
AttributeError: 'MockConnection' object has no attribute 'exec_driver_sql'
```

Full output sha256 `827323e3df69b7122a889fae36f8d3310162c668dab0aff4252ef7b8aba9d686`. **What the limit does
today: 3 of the 11 revisions emit (core, sg013, sg014); the run aborts entering the 4th (FTS), so the FTS
DDL (view + `CREATE VIRTUAL TABLE … USING fts5` + 3 sync triggers) and all 7 later revisions (sg025, sg035,
sg048, sg068, sg100, sg113, sg114) are never emitted.** Offline SQL generation is unusable end-to-end.

**Finding F-SG145-3 (premise delta vs SG-139):** `SG-139_report.md:123-125` says the run prints "8
`Running upgrade` blocks". Measured here: **4** INFO `Running upgrade` lines. Since the run aborts *inside*
the 4th revision, the reported 8 is not reproducible (investigated, not bent — the SG-139 number is a
miscount, zero harm either way).

**Secondary query-side bound (the "rows returned vs rows matched" surface).** There is **no bound in the
FTS layer**: the `MATCH` subquery at `backend/app/api/v1/assets.py:209-215` carries no `LIMIT`. The only
cap is the API page limit at `assets.py:274` (`limit: int = Query(default=20, ge=1, le=100)`), applied as
`.limit(limit + 1)` at `:299`, truncated to `limit` at `:303`, with `has_more = len(items) > limit` at
`:301`. Read-only observation on the live DB (`?mode=ro`, no writes): `asset`=6 rows, `asset_fts`=6 rows;
`MATCH '"de"'`=2, `'"porc"'`=2, `'"Lapte"'`=1. So "matched" is the true FTS hit set and "returned" is the
page cap; this is ordinary pagination, **not** a defect.

## G1 — authed: host `gh` state, exact signature + relay ask (`PG-SC-03`, `CO-100`)

Exact read-only signature (presence-only; no token file exists to print):

```
$ timeout 120 gh auth status
You are not logged into any GitHub hosts. To log in, run: gh auth login
gh_auth_status_exit=1

$ command -v gh ; gh --version
/usr/bin/gh
gh version 2.96.0 (2026-07-02)
$ ls -la ~/.config/gh/
ls: cannot access '/home/andrei/.config/gh/': No such file or directory
$ GH_TOKEN / GITHUB_TOKEN
GH_TOKEN=unset
GITHUB_TOKEN=unset
```

**Verdict: genuinely unauthenticated** — no host config, no token env var, no active account. This leg is
**UNANSWERED by design** (repairing it is an owner hand); the precise relay ask is in RECOMMENDED-NEXT. No
auth flow was performed (that would be a STOP). Nothing credential-shaped was read or printed.

## G2 — worklog and report (`CO-57`)

Written: `docs/worklogs/SG-145.log`, `SG-145_report.md`, `SG-145_verify.log` (probes, grep scopes,
producing-code reads, diff-ceiling). **Diff ceiling — exactly the 3 worklogs, nothing else:**

```
$ git diff --name-only origin/automation..bd4f3acff8ae07f8995279714a05db6ca0d81d94
docs/worklogs/SG-145.log
docs/worklogs/SG-145_report.md
docs/worklogs/SG-145_verify.log
```

## Findings (all reported, none fixed — ceiling)

- **F-SG145-1** — `.rules-cache/` is a workstation-only, gitignored path; the host contract checkout is
  `/home/andrei/storagegenie-contract`. The Architect's `.rules-cache/dispatch` grep scope does not exist
  here. Location difference, not a defect.
- **F-SG145-2** — `--sql` is Alembic's offline flag, not a lane flag; the fix is repo code, not lane config.
- **F-SG145-3** — SG-139's "8 `Running upgrade` blocks" is not reproducible; measured 4.
- **F-SG145-4** — no FTS-layer bound exists; the only cap is the API page limit (code quoted). Not a defect.
- **F-SG145-5** — host `gh` unauthenticated with no config/token; needs owner relay.

## Receipt

- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
  `{{RECEIPT_CMD}}`.
- Note added on WORK_HEAD `bd4f3ac`, then `refs/notes/storagegenie-coder-reports` pushed and verified from a
  **mapped** fetch (`refs/notes/sg145-fetched`); executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-145 | Report: docs/worklogs/SG-145_report.md | Work-HEAD: bd4f3acff8ae07f8995279714a05db6ca0d81d94" bd4f3acff8ae07f8995279714a05db6ca0d81d94   # add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports            # e5c0e00..f8a4ede push_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg145-fetched   # fetch_exit=0
$ git notes --ref=refs/notes/sg145-fetched show bd4f3acff8ae07f8995279714a05db6ca0d81d94
Dispatch-ID: SG-145 | Report: docs/worklogs/SG-145_report.md | Work-HEAD: bd4f3acff8ae07f8995279714a05db6ca0d81d94
show_exit=0
```

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| G0 greps + code reads | ordinary | 120 s | < 1 s |
| G0 read-only `--sql` drive | ordinary | 120 s | < 2 s |
| G0 read-only fts/SQLite reads | ordinary | 120 s | < 1 s |
| G1 `gh auth status` | ordinary | 120 s | < 1 s |
| G2 worklogs + commit + push | ordinary | 120 s | < 2 s |
| G2 notes add + push + mapped fetch + show | ordinary / notes-push | 120 s / 300 s | < 5 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | **~4 min wall** |

Actual-versus-budget per goal: G0 well under its 120 s classes (greps near-instant, one 259-line offline
generation); G1 trivial; G2 trivial; overall well under the 2400 s cap. **Real metered spend $0.000000 USD,
zero metered calls.**

## UNCLEAR

- **FIRST READ:** the packet framed both items as "lane limitations" with `--sql` possibly living in
  `.rules-cache/dispatch`. First contact showed the opposite: `--sql` is Alembic's flag (no lane/wrapper
  occurrence at all) and `.rules-cache/` does not exist on the host. The genuine limit is repo migration
  code calling an online-only API under an offline run — confirmed by executing it.
- **DURING EXECUTION:** the offline drive dies *inside* revision 4 of 11, so only 3 revisions ever emit —
  the FTS revision and everything after it are absent. SG-139's "8 upgrades" claim did not reproduce
  (measured 4); I reported my number rather than bending to it.
- **REMAINING:** (a) the offline-`--sql` FTS defect needs a repo code slice (shape below); (b) host `gh`
  auth needs an owner relay; (c) neither was fixed here by design — a fix is a STOP under this ceiling.

## RECOMMENDED-NEXT

### R1 — offline `--sql` FTS fix (repo slice, size **S**) — proposed SG-146

- **Shape:** make the FTS revision offline-safe. In `backend/app/services/fts.py` / the FTS migration,
  emit the DDL through Alembic's `op.execute(...)` (or `op.get_bind().execute(text(...))` where the mock
  supports it) so the view + `CREATE VIRTUAL TABLE … USING fts5` + 3 triggers render in **both** online and
  offline modes; gate the `rebuild=True` backfill behind an online-only check (e.g.
  `op.get_context().as_sql` / `context.is_offline_mode()`), because the FTS rebuild needs live rows and
  cannot run offline. Keep the online path byte-equivalent (deployable databases unchanged).
- **Acceptance:** an affected-tests fixture (`CO-101`) asserting `alembic upgrade head --sql` **exits 0**
  and its stdout contains the FTS DDL (`CREATE VIRTUAL TABLE asset_fts`, the 3 `asset_fts_after_*`
  triggers) **and** the post-FTS revision markers (non-vacuity: the 7 later revisions must appear, not just
  an empty/early prefix). No DB opened, no migration applied, no deploy.
- **Size/units:** S — one migration file (+ optional small `fts.py` helper split) and one offline-SQL test;
  offline tooling only, unserved, no rider.

### R2 — host `gh` authentication (owner relay, **no slice**)

- **Ask:** on host `87.106.66.242:2222` as user `andrei`, run one of:
  - interactive `gh auth login` (needs a device-code / browser hand at the host console), or
  - token placement without echoing it: `gh auth login --with-token < <token-file>` (owner-side only).
- **Minimum scope:** `repo` (+ `read:org` if org queries are needed; add `workflow` only if Actions need it).
- **Proof to hand back:** `gh auth status` prints a `Logged in to github.com account …` line, exit 0.
- This is a desk/lane boundary relay, not a product slice — no packet should carry a credential.

**note=yes**
