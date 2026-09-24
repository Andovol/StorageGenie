SG-115 report — Production maintenance: live backfill + batched migrations + activation ($0, ops)
=================================================================================================

Verdict: SHIPPED. The two owner-approved production words were executed exactly as recorded — nothing
else. The SG-111 backfill ran on the live SQLite with a before/after census and changed ZERO rows (the
live catalog needed nothing); the SG-113 + SG-114 migrations applied in one batched `upgrade head`
(`20260923_sg100_enrich_snapshot -> 20260924_sg113_location -> 20260924_sg114_relation`), adding exactly
`{location, asset_location, asset_relation}` with every pre-existing table count identical; both flags
were appended once each; the backend was recreated exactly once and came healthy at 11 s; the dormant
surfaces now answer `200` (`/v1/locations`, `/v1/assets/<id>/relations`) and the asset detail carries
`locations` + `relations`, while the pre-existing catalog list stays `200`. Product diff over
`backend/`+`frontend/`+`alembic/` is EMPTY. $0.000000 — no metered call exists on any path.

Contract echo + source path
---------------------------
Contract 0.33.0 — installed global rules file hashed against the payload, never checkout-vs-stamp (G-L1/M3).
- source: `/home/andrei/storagegenie-contract/VERSION` = `0.33.0`
- source HEAD: `b232b845d74e89cb346c60fa4b9a40ec401c42dd`
- `sha256sum /home/andrei/storagegenie-contract/RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`
- payload `/home/andrei/storagegenie-contract/RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46 RULES.md` -> match.
- recorded `0.33.0` == published `b232b84`. Clean.

Model / effort / spend (CO-78)
-----------------------------
Read from the process arguments, never a system-prompt identity line.
- argv (`/proc/3892551/cmdline`): `opencode run --auto --dir /home/andrei/StorageGenie --variant high`
  (the same argv also carries the full packet prompt text; the run flags are the three shown).
- effort = `high` (from `--variant high`).
- model = `unknown` — `tr '\0' '\n' < /proc/3892551/cmdline | grep -c -- '--model'` = `0` and no provider
  metadata readable; the packet states the CLI default is omitted by policy, and I refuse to guess.
- Spend real $ = `$0.000000` (zero provider calls; no metered call exists on any path).

Refs
----
- Work dir `/home/andrei/StorageGenie`, origin `git@github.com:Andovol/StorageGenie.git`
- BASE_REF = `origin/automation`
- BASE_RESOLVED = `05451c3b364e4f63463959e45b9f5cf0a7bf5896` (== start HEAD; the packet commit)
- WORK_HEAD = `7b4ca92baa435bcb81311ab78e7b621a1a1d5434`

Premise verification — corrections are worth more than agreement
----------------------------------------------------------------
Every G0 hypothesis held; none differed. Quoted raw in `SG-115_verify.log`:
- backend-1 `Up (healthy)`, container `1a0588c7d944…`, RestartCount 0.
- `alembic current` = `20260923_sg100_enrich_snapshot` — VERIFIED (hypothesis exact).
- table set = 25 tables, NO `location`/`asset_location`/`asset_relation` — VERIFIED.
- `SELECT status, COUNT(*) FROM asset GROUP BY status` = `ACTIVE|6` — VERIFIED.
- host `.env` `grep -c '^SG_LOCATIONS_ENABLED='` = `0`; `grep -c '^SG_RELATIONS_ENABLED='` = `0` — VERIFIED
  (counts only; content never printed and never read into any artifact).
- health exact `{"status":"ok","db":"ok","storage":"ok"}`; gate canonical vhost http:80 `301` / https:443
  `401` — VERIFIED (matching SG-110/111/113/114).
- backfill script `/app/scripts/backfill_asset_lifecycle.py` present in the served image with sha256
  `5cda7cc1757d9c80772de58df77ea61047c7c71bafc50404082a8288e607a63c` == the host file — VERIFIED. Both
  migration files (`20260924_sg113_location.py`, `20260924_sg114_relation.py`) present in the image.

G0 — capability + census BEFORE (raw in `SG-115_verify.log`)
-----------------------------------------------------------
- image `sha256:b4bec08d9bcb…` created 2026-09-24T11:31:02Z; container `1a0588c7d944…`, RestartCount 0, healthy.
- version_num `20260923_sg100_enrich_snapshot`; `table_count 25`; 25 per-table counts captured.
- status census `ACTIVE|6`; household `01a0a029-1477-7ca0-b200-bce78a96c679`; 6 assets.
- `.env` flag counts `0` / `0`; health exact; gate `301`/`401`.
- product diff over `backend/`+`frontend/`+`alembic/` vs BASE = EMPTY.

G1 — live backfill (D155 word)
------------------------------
EXACT recorded command, re-verified present in the served image first:
```
$ docker exec storagegenie-backend-1 python /app/scripts/backfill_asset_lifecycle.py --db /data/db/storagegenie.db --apply
db=/data/db/storagegenie.db
BEFORE census={'ACTIVE': 6}
planned conversions=[]
no out-of-vocabulary status value exists; nothing to backfill
APPLIED rows_changed=0
AFTER census={'ACTIVE': 6}
backfill exit=0
```
AFTER (read-only): version_num `20260923_sg100_enrich_snapshot`, table_count `25`, `ACTIVE|6`,
asset_total `6`. Census IDENTICAL; zero conversions, so there is no converted row to report an id for.
`PG-PR-10`: database `/data/db/storagegenie.db`, grant D155, stated here.

G2 — batched migrations (D156 word, part 1)
-------------------------------------------
```
$ docker exec storagegenie-backend-1 python -m alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade 20260923_sg100_enrich_snapshot -> 20260924_sg113_location, location tree + asset location assignment (SG-113, G3)
INFO  [alembic.runtime.migration] Running upgrade 20260924_sg113_location -> 20260924_sg114_relation, asset relations: typed links (SG-114, G4)
alembic upgrade exit=0
```
AFTER: `version_num = 20260924_sg114_relation`; `table_count 28`; DELTA vs G0 baseline
`ADDED = ['asset_location', 'asset_relation', 'location']`, `REMOVED = []`, `CHANGED = []`;
`ADDED_EXACT_EXPECTED True`, `OLD_COUNTS_EQUAL True`; status `ACTIVE|6`. Head path is exactly the packet's
expected path and the old counts all equal. Precedence (`PG-IC-03`) not triggered — no failure occurred,
so G3 was reached legitimately. No auto-rollback was run.

G3 — flags + recreate + activation probes (D156 word, part 2)
-------------------------------------------------------------
- pre-append counts `0`/`0`; append-only two lines (`>>`, never rewrite); post-append counts `1`/`1`
  (content never printed).
- exactly ONE recreate: `DOCKER_BUILDKIT=0 docker compose up -d --no-deps backend` — container
  `1a0588c7d944…` -> `c9d780738b68…`, RestartCount 0, healthy at `t=11s` (< 60 s bound). Flags visible in
  the recreated container's env, `count=1` each.
- AFTER proofs quoted raw:
  * health exact ×6 = `{"status":"ok","db":"ok","storage":"ok"}` (all six).
  * gate canonical vhost: http:80 `code=301 redirect=https://storagegenie.dynv6.net/`; https:443 `code=401`.
  * `GET /v1/locations?household_id=01a0a029-…` -> `{"items":[]}` `HTTP 200` (was 404 dormant).
  * `GET /v1/assets/01a0a467-…/relations?household_id=01a0a029-…` -> `{"items":[]}` `HTTP 200` (was 404).
  * asset detail `GET /v1/assets/01a0a467-…?household_id=01a0a029-…` -> `HTTP 200`,
    `has_locations_key True`, `has_relations_key True`.
  * pre-existing route unchanged: `GET /v1/assets -> HTTP 200`.
  * version `20260924_sg114_relation`; 28 tables, ADDED exactly the three, REMOVED/CHANGED none; `ACTIVE|6`.

Vacuous-pass disclosure (loudly)
--------------------------------
The two activation `200` bodies are `{"items":[]}` because the live household has zero `location` and
zero `asset_relation` rows. This is NOT a vacuous pass: the SAME two URLs answered `404` with the flag OFF
(proven live by SG-113/114 before this slice) and now answer `200`; and the detail read gained the two
keys only when the flag is ON. The 404->200 transition and the key presence are the assertions; the empty
list is the correct data answer for a household that has not created any location/link. The DELTA block is
also non-vacuous: it compares against the captured G0 baseline, not against itself.

Question each criterion answers (`PG-SC-09`)
--------------------------------------------
- backfill — did the live catalog need anything? No: zero out-of-vocabulary statuses, `rows_changed=0`.
- migration — did the schema land whole with data still? Yes: both revisions applied in order, exactly the
  three tables added, every pre-existing count byte-equal, status census unchanged.
- activation — do the dormant surfaces answer? Yes: the two routes moved 404 -> 200 and the detail read
  carries both new keys; the pre-existing catalog list still 200.

Authorized mutations — exactly five
-----------------------------------
1. backfill `--apply` (G1). 2. `alembic upgrade head` (G2). 3+4. two `.env` appends (G3). 5. one backend
recreate (G3). No sixth mutation occurred. Reads were read-only `docker exec` probes, `curl`, and
`file:…?mode=ro` SQLite. No model/build push, no `docker compose config`, no metered call, no code change.

Issues / disagreements / unanswered
-----------------------------------
- No packet premise was wrong; every G0 hypothesis held exactly.
- Design call reported: for an ops slice with NO product diff, WORK_HEAD is the commit that carries the
  raw evidence worklogs + this report (mirroring SG-113/114's work-commit -> report-commit split); the
  receipt note is anchored on that hash and the final tip is dual-annotated.
- `model` is reported `unknown` (no `--model` in argv, no provider metadata). A refusal to guess, not a
  failure.
- No privileged operation was denied; nothing was left unanswered.

Actual-versus-budget per leg (`PG-PR-06`; units = wall seconds)
--------------------------------------------------------------
- G0 recon + BEFORE capture: ~10 s actual (bound 120 s ordinary).
- G1 live backfill: ~10 s actual (bound 120 s ordinary).
- G2 migrations: ~25 s actual (part of the 600 s migrate+recreate+verify bound).
- G3 flags + ONE recreate + activation probes: ~15 s actual, recreate healthy at t=11 s (same 600 s bound).
- G4 worklog + report + receipt: bounded by 1500 s early-close (process started 11:40:50; G4 began ~11:42:49).
- Overall: well under the 2100 s overall bound.

Receipt (notes ref)
-------------------
Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. Note added on WORK_HEAD
`7b4ca92baa435bcb81311ab78e7b621a1a1d5434`; notes ref `refs/notes/storagegenie-coder-reports` pushed
(`568b8d1..0642505`) and read back from a MAPPED fetch
(`refs/notes/storagegenie-coder-reports-sg115-fetched` at `06425050928da504c4cdb3bfbe1efa9564d2a75f`).
Pasted executed output:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg115-fetched show 7b4ca92baa435bcb81311ab78e7b621a1a1d5434
Dispatch-ID: SG-115 | Report: docs/worklogs/SG-115_report.md | Work-HEAD: 7b4ca92baa435bcb81311ab78e7b621a1a1d5434
```

Full raw transcript (precheck, add, push, mapped fetch, show) is in `SG-115_verify.log` -> `RECEIPT NOTE
VERIFY`. The final tip (this receipt commit) is dual-annotated with the same note (SG-092 inoculation).
final line: `note=yes`.

Three UNCLEAR lines
-------------------
- FIRST READ: whether "activation probes" wanted a non-empty read (a created location/link) rather than the
  empty-list read. I kept the probes strictly read-only because the packet's FIVE authorized mutations do
  not include a live assignment, so any create/assign would have been a sixth mutation (a STOP); the
  404->200 transition is the activation proof.
- DURING EXECUTION: whether appending the two flags should be one mutation or two. I performed a single
  append-only write carrying both lines (the packet counts "two env appends"); no rewrite and no
  `docker compose config` was ever run.
- REMAINING: the model id (CLI default, unreadable from argv/metadata); and whether a future slice should
  add a non-empty activation probe (create a location / link on live) under its own owner word.
