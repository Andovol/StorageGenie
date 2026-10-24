SG-237 — D2 live reminder proof: report

Dispatch SG-237. Model/effort read from this process's own command line:
`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`
(pid 3268534, `/proc/3268534/cmdline`), so model `opencode-go/deepseek-v4.1-flash`, effort `max` — not from a
system-prompt identity line.

BASE REF requested: `origin/automation`.
BASE REF resolved: `9d340cfabcd17f962f81bb88b397e265cf34be9b` (`git rev-parse origin/automation` at lane
start=1792850173). The worktree at start read the same commit as an observation; this report makes no claim
that any served image or remote HEAD equals that hash.

Version chain: `AGENTS.md` records rule-set `0.52.0`; host copy `/home/andrei/storagegenie-contract/CODER.md`
line 3 reads verbatim `**Contract version: 0.52.0** — **echo this line verbatim in your receipt.** It is the
only proof that you`; SG-235 and SG-236 echoed `0.52.0`. I did not independently fetch a remote “published
payload” (network was loopback plus container-runtime only), so that leg is carried from the predecessor
echoes, not re-observed by me.

Money: zero provider calls. `provider_call` rows created since lane start (2026-10-24 13:56:13): 0; summed
cost 0.0. Spend line: **$0.000000 actual vs $0 bound**. No metered call was made.

## G0 — socket first (before any Docker invocation)

Printed from my own unit's process environment:

```
RUNTIME_DIRECTORY=/run/dispatch-storagegenie-SG-237
RUNTIME_SOCKETS=docker.sock
XDG_RUNTIME_DIR=/run/dispatch-storagegenie-SG-237
srw-rw---T 1 andrei 100987 0 Oct 16 17:19 /run/dispatch-storagegenie-SG-237/docker.sock
lane_socket=unix:///run/dispatch-storagegenie-SG-237/docker.sock
exported DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-237/docker.sock
exported DOCKER_CONFIG=/tmp/opencode/SG-237/docker-config
```

`docker version` then answered with a **Server** section (Engine 29.6.2, API 1.55, containerd 2.2.6, runc
1.3.6, rootlesskit 3.0.2), not a client-only block. No docker invocation of any kind preceded the export.
Transcript: `docs/worklogs/SG-237_g0.log`.

## G1 — pre-state, read-only, before any write

Served container (lane socket): id `ee4e165af4b62da2f20af53a3ce887ba79fb1da0244417d8648dbcc5d53fd17c`,
name `/storagegenie-backend-1`, created `2026-10-24T11:30:45.946797846Z`, started
`2026-10-24T11:30:46.845151157Z`, image `sha256:2bd3599f2b68980576454f889a7b93db291ec8e0c08f5f7a7afd52b7af93ef5f`
(`storagegenie-backend`), Cmd `["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, restarts 0,
status running, health healthy, ports `127.0.0.1:8003->8000/tcp`. Health body `{"status":"ok","db":"ok","storage":"ok"}`
HTTP 200.

Database: production SQLite at `data/db/storagegenie.db` (bind-mounted at `/data/db`; storage volume
`storagegenie_storage_data` at `/data/storage`), opened read-only with `sqlite3 -readonly`.

| table | before |
|---|---|
| assertion | 37 |
| asset | 7 |
| reminder | 0 |
| household | 1 |
| audit_event | 100 |
| review_task | 8 |
| evidence | 27 |
| asset_evidence | 20 |
| observation | 20 |
| idempotency_key | 11 |

Alembic head `20261023_sg233_reminder`. Household: exactly one,
`01a0a029-1477-7ca0-b200-bce78a96c679` (“Popescu Household”).

ACTIVE asset inventory (all 7, ordered by id):

| id | display_name | asset_type |
|---|---|---|
| 01a0a467-eb0e-7b83-a227-af122dc9268b | Toothpaste | unknown |
| 01a0c446-44c9-7b82-9d1c-2b51fa518191 | CEAFĂ DE PORC | meat |
| 01a0c47f-fbb3-7db1-b6f3-aa52d20aa6a0 | UHT Lapte 3,5% grăsime | dairy |
| 01a0c481-720e-7923-ad6c-bee45caba30f | Milbona Parmigiano Reggiano Italian hard cheese flakes | dairy |
| 01a0c4aa-8b62-7360-b11e-a476ddaea0f6 | Miso Soup | soup |
| 01a0c4ab-3765-7e10-8d0a-705390c6560d | Costiță de porc | meat |
| 01a131ae-7a0c-7363-91c8-cfef6bd1faa3 | TRACHISAN comprimate de supt | medicine |

Expiry-tracker assertions before: none (0 rows with `field_path LIKE 'plugin:expiry-tracker/%'`). Open review
tasks before: none. Engine status before: `rows:[]`, `summary:{"by_tier":{},"by_bucket":{},"unresolved":0,"total":0}`.
Reminders before: `{"unread_count":0,"items":[]}`. Served JS `/assets/index-B0lDq5dE.js` carried
`Unread reminders`, `Read reminder`, `Dismiss reminder` once each before the write.

Routes were read from `backend/app/api/v1/plugins.py:98-126` and `:148-189`: the two shapes and bodies in
packet premise (d) are correct. The handlers have **side effects the packet's row model omits** (see F1): each
`_write_assertion` also inserts an `audit_event` (`backend/app/plugins/expiry_tracker.py:323-357`), and
`classify_asset` writes a second, placeholder `expiry_date` assertion and opens a review task for a perishable
asset with no observed date (`:414-439`).

Transcript: `docs/worklogs/SG-237_prestate.log`.

## G2 — one asset, one classification, one near expiry date, through the app's own routes

Choice: **Miso Soup**, `01a0c4aa-8b62-7360-b11e-a476ddaea0f6`. Its display name unambiguously denotes a food
(Japanese soup; `asset_type=soup`); the remaining names are meat, dairy, medicine or toothpaste. No asset was
chosen by fallback.

Date read from the live clock at execution: `today_utc=2026-10-24`, `expiry_date=2026-10-27` (`date -u +%F`
and `date -u -d '+3 days' +%F`). Not hardcoded.

Classification POST (HTTP 200):

```
POST /v1/plugins/expiry-tracker/assets/01a0c4aa-8b62-7360-b11e-a476ddaea0f6/classification?household_id=01a0a029-1477-7ca0-b200-bce78a96c679
{"category": "food_beverages"}
→ {"plugin_id":"expiry-tracker","version":"1.0.0","classification":{"category":"food_beverages","label":"Food & beverages","profile":{"notification_tier":"upcoming","notification_days":30,"tier_defaults":{"critical":1,"urgent":7,"upcoming":30},"opened_date_tracking":false,"disposal_guidance":true}},"expiry_assertion":{"id":"01a16e35-0c7e-7403-b324-43ac30c478a6","field_path":"plugin:expiry-tracker/expiry_date","value":{"status":"unknown"},"source_type":"deterministic","review_state":"needs_evidence","source_evidence_ids":[]},"review_task":"01a16e35-0c82-7801-8fac-8ea68abee909"}
```

Expiry POST (HTTP 200):

```
POST /v1/plugins/expiry-tracker/assets/01a0c4aa-8b62-7360-b11e-a476ddaea0f6/expiry?household_id=01a0a029-1477-7ca0-b200-bce78a96c679
{"expiry_date": "2026-10-27", "date_type": "expiry_date"}
→ {"asset_id":"01a0c4aa-8b62-7360-b11e-a476ddaea0f6","assertion":{"id":"01a16e35-0c98-7112-9dd5-7c9a4ae027d7","field_path":"plugin:expiry-tracker/expiry_date","value":{"expiry_date":"2026-10-27","date_type":"expiry_date"},"source_type":"user","review_state":"accepted","source_evidence_ids":[]},"resolved_review_task_ids":["01a16e35-0c82-7801-8fac-8ea68abee909"]}
```

Engine after the write (HTTP 200):

```
{"household_id":"01a0a029-1477-7ca0-b200-bce78a96c679","as_of":"2026-10-24","category":null,"rows":[{"asset_id":"01a0c4aa-8b62-7360-b11e-a476ddaea0f6","display_name":"Miso Soup","category":"food_beverages","expiry_date":"2026-10-27","date_type":"expiry_date","days_remaining":3,"tier":"urgent","bucket":"this-week"}],"summary":{"by_tier":{"urgent":1},"by_bucket":{"this-week":1},"unresolved":0,"total":1},"unresolved_rows":[]}
```

Engine quote (not assumption): `FOOD_TIERS` is `{critical:1, urgent:7, upcoming:30}`
(`backend/app/plugins/expiry_tracker.py:95-99`); `tier_for` returns the first ascending window with
`d <= days` and `bucket_for` returns `this-week` for `d <= 7` (`backend/app/services/expiry_engine.py:54-80`).
For `d=3`: tier `urgent`, bucket `this-week`, window 7 — the observed row matches.

`assertion` moved 37 → **40 (+3)**, not +2: classification accepted, `expiry_date {"status":"unknown"}`
deterministic/needs_evidence (superseded by the next call; still a row), and `expiry_date` accepted. Active
expiry-tracker assertions are 2 (classification + accepted expiry). `audit_event` 100 → 104, `review_task`
8 → 9 (the new task was opened then resolved). `reminder` stayed 0. This is the packet's row-model error
(F1), recorded before the write in `docs/worklogs/SG-237_scope.log` and after it in
`docs/worklogs/SG-237_write.log`.

## G3 — one restart, then the startup pass

`docker restart storagegenie-backend-1` was run exactly once through the lane socket at 13:59:04Z; exit 0,
command returned in 1 s. No build, recreate, image change or migration. No second restart.

Bounded wait (stated bound 60 s, 5 s steps): attempt 1 at +0 s, health `000`/reminder 0; attempt 2 at +5 s,
health `200`/reminder 1; loop stopped. Observed app-unavailable span ≈ **5.95 s** (log shutdown
13:59:04.617 → first health 200 13:59:10.563).

Container after: **same container identity** — id `ee4e165af4b6…d17c`, name `/storagegenie-backend-1`,
created `2026-10-24T11:30:45.946797846Z` unchanged; only `StartedAt` changed to
`2026-10-24T13:59:05.238544242Z`. Image and Cmd unchanged. `RestartCount` stayed **0** (manual restart is not
counted). Docker health read `starting` at the 13:59:10 HTTP-green moment and `healthy` by 14:00:03; the HTTP
probe returned `{"status":"ok","db":"ok","storage":"ok"}` throughout the post-start observation.

Log since the restart, verbatim:

```
2026-10-24T13:59:04.617437131Z INFO:     Shutting down
2026-10-24T13:59:04.718060366Z INFO:     Waiting for application shutdown.
2026-10-24T13:59:04.718267775Z INFO:     Application shutdown complete.
2026-10-24T13:59:04.718403770Z INFO:     Finished server process [1]
2026-10-24T13:59:06.863400063Z INFO:     Started server process [1]
2026-10-24T13:59:06.863427244Z INFO:     Waiting for application startup.
2026-10-24T13:59:06.865331827Z INFO:     Application startup complete.
2026-10-24T13:59:06.877810105Z INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2026-10-24T13:59:10.563204557Z INFO:     172.18.0.1:59460 - "GET /v1/health HTTP/1.1" 200 OK
```

Failure scan of the same log (`error|traceback|failed|exception|critical`): `NO_FAILURE_LINES`.
**No line announces the reminder row**: `backend/app/services/reminders/daily.py:63-72` logs failures only, as
SG-236 recorded; a success line is SG-238 scope. The packet's “the reminder row appearing” in the log is
therefore an absence, not a quoted event (F2). The row itself is observed below.

`reminder` table after (exactly one row, created by the startup pass):

```
id=01a16e35-4394-7c11-9798-844754826bcc
household_id=01a0a029-1477-7ca0-b200-bce78a96c679
asset_id=01a0c4aa-8b62-7360-b11e-a476ddaea0f6 (Miso Soup)
as_of_day=2026-10-24   tier=urgent   bucket=this-week   days_remaining=3
status=unread          created_at=2026-10-24 13:59:06
```

`GET /v1/reminders?household_id=…` (HTTP 200):

```
{"household_id":"01a0a029-1477-7ca0-b200-bce78a96c679","unread_count":1,"items":[{"id":"01a16e35-4394-7c11-9798-844754826bcc","household_id":"01a0a029-1477-7ca0-b200-bce78a96c679","asset_id":"01a0c4aa-8b62-7360-b11e-a476ddaea0f6","display_name":"Miso Soup","as_of_day":"2026-10-24","tier":"urgent","window_days":7,"bucket":"this-week","days_remaining":3,"status":"unread","created_at":"2026-10-24T13:59:06","updated_at":"2026-10-24T13:59:06"}]}
```

That is the same shape as the engine row for `as_of=2026-10-24`. The reminder was left **unread**; no
`/read` or `/dismiss` POST was made and no second reminder was created.

Served JS after restart: `/assets/index-B0lDq5dE.js` still carries `Unread reminders` 1, `Read reminder` 1,
`Dismiss reminder` 1.

Counts after, against G1:

| table | before | after | delta |
|---|---|---|---|
| assertion | 37 | 40 | **+3** |
| asset | 7 | 7 | 0 |
| reminder | 0 | 1 | **+1** |
| household | 1 | 1 | 0 |
| audit_event | 100 | 104 | **+4** |
| review_task | 8 | 9 | **+1** |
| evidence | 27 | 27 | 0 |
| asset_evidence | 20 | 20 | 0 |
| observation | 20 | 20 | 0 |
| idempotency_key | 11 | 11 | 0 |

Alembic head unchanged (`20261023_sg233_reminder`). No row was deleted; one assertion moved to `superseded`
and one review task to `resolved` (both rows created by this slice). Transcript:
`docs/worklogs/SG-237_restart.log`.

## Findings

**F1 (material; makes A2/A3 literal counts fail).** The packet's production-write envelope — “exactly THREE
rows … two assertions + one reminder … no other table is touched” — does not match the committed route code.
Each `_write_assertion` inserts one `audit_event` (`expiry_tracker.py:347-356`); `classify_asset` writes a
second `expiry_date` placeholder assertion and opens a review task for a perishable asset without an observed
date (`:423-428`); `enter_expiry` writes its own `expiry.manual_entry` audit row (`plugins.py:174-183`).
Actual movement: **assertion +3, audit_event +4, review_task +1, reminder +1**. I executed the action because
owner grant D-1024-7 authorises “one ACTIVE asset … through the app's own plugin routes” for one near date,
and these rows are that route's own audit/state trail; a literal three-row envelope was impossible without
product-code changes, which this slice forbids. I did not bend the counts to the packet. If the owner or
architect considers the audit/state rows outside the grant, that is a scope correction for the next packet;
the rows are enumerated above.

**F2.** The log cannot show “the reminder row appearing”: the daily caller logs failures only and emits no
success line. The row is proven by the table and the live endpoint, not by the log; SG-238 names the success
line.

**F3.** “New container identity” is not what `docker restart` produces: id, name and created time are
preserved; only `StartedAt` changes, and `RestartCount` remains 0. Reported as observed.

**F4.** Docker's health field briefly read `starting` at the first HTTP-green instant; the HTTP probe was
green at +5 s and the health field read `healthy` by 14:00:03. Timing nuance, not a failed health check.

**F5 (minor, outside slice scope).** The local `frontend/dist/assets/index-BfBGTcVU.js` is not the served
bundle (`/assets/index-B0lDq5dE.js`); the served bundle is the one that matters here, carries all three button
strings, and no product/frontend file was touched.

## Acceptance

**A1 — PASS.** G0 printed the lane socket from my unit environment, exported `DOCKER_HOST`, and proved the
server line before any other docker call. The pre-state inventory, counts, engine and reminder reads were on
record before the write (`SG-237_g0.log`, `SG-237_prestate.log`).

**A2 — FAIL on the stated assertion count.** One asset, one classification and one live-clock date were
written through the app's own routes; both responses were HTTP 200 and are quoted; the engine shows Miso Soup
with tier `urgent`, bucket `this-week`, `days_remaining` 3. But the `assertion` table grew by **3**, not 2
(F1). The two *active* expiry-tracker assertions are the classification and the accepted expiry; the third is
the route's superseded placeholder. The engine-row prerequisite passed (no STOP condition).

**A3 — FAIL on the stated count movement.** Exactly one restart; health green; the log and its absent
success line are quoted; exactly one new `reminder` row, unread, `as_of_day=2026-10-24`, tier/bucket/days
matching the engine; `GET /v1/reminders` gives `unread_count` 1 and the same shape; the served JS carries all
three button strings; the reminder is left unread. But the post-state differs from pre-state in `assertion`
(+3, not +2), **and also** `audit_event` (+4) and `review_task` (+1) (F1), so the “only” clause fails.

**A4 — PASS.** Logs and this report are committed; elapsed per leg is below; constraints are answered;
FIRST/DURING/REMAINING are dispositioned; first token is SG-237; the last line names the failed check.

**A5 — PASS.** After this report's commit, a note is added to `refs/notes/storagegenie-coder-reports` with
first line `Dispatch-ID: SG-237 | Report: docs/worklogs/SG-237_report.md`, the Work-HEAD recorded, the notes
ref pushed and fetched into a mapped local ref, and the read-back pasted into
`docs/worklogs/SG-237_receipt.log` (committed docs-only). The note is placed on the commit that carries this
report; that commit's hash is the Work-HEAD in the receipt.

## Runtime versus budget (PG-PR-06)

Lane stamps come from `systemctl show dispatch-storagegenie@SG-237.service -p ActiveEnterTimestamp`:
`Sat 2026-10-24 13:56:13 UTC` (epoch 1792850173).

| leg | end (UTC) | elapsed from lane start | note |
|---|---|---|---|
| G0 | 13:56:29 | +16 s | socket, export, server version |
| G1 pre-state | 13:58:28 | +135 s | includes code reading and premise checks |
| G2 write | 13:58:52 | +159 s | write call leg itself 10 s |
| G3 restart | 13:59:10 | +177 s | restart command 1 s; health green at +5 s |
| report drafted | 14:00:41 | +268 s | receipt path follows the report commit |

Containment limit: **5.95 s** observed app-unavailable span, unit seconds, source Docker log timestamps
(shutdown 13:59:04.617 → first HTTP 200 13:59:10.563). The wait bound was **60 s in 5 s steps**; it was
satisfied at the second step. Lane budget is **1800 s** (packet); the architect note records
`RUN_BUDGET_S=2100` for the lane. Final work, including commit and receipt, remains far under either bound.

## Constraints answered

- Scope: only `docs/worklogs/SG-237*` was written. No product, config, schema, migration or test edit; zero
  code diff.
- Cross-product (`PG-IC-01`): no remediation step ran; only the already-built image was used; the single
  executed runtime action was the one restart.
- No full suite, no browser sweep (`PG-DP-02`); substitute was the read-only post-restart verification above.
- `PG-IC-07`: the expiry date was computed from the live clock (`date -u`), not fixed; the only fixed dates
  are packet metadata and lane/log stamps. No claim that HEAD equals any hash.
- `PG-IC-08`: the stated 60 s wait bound was honoured; the pass landed inside it.
- `PG-PR-10`: production SQLite, owner grant D-1024-7 (one asset, one date, app routes), with the row-model
  divergence reported as F1.
- Role guard: no dispatch verb, no unit start or poll, no second restart, no interactive command; no command
  was killed. No secret was written to any artifact.

## Vacuity (PB-3)

The chain checks are non-vacuous: a real row moved through accepted data → engine → startup pass → stored
reminder → live endpoint. The JS check read the served bundle over HTTP and matched each string once. The
one check that could not be met is the log line announcing the row: it does not exist in this build, and it is
reported as an absence, not a pass. The row-count checks are real and fail literally. Provider spend was
checked as zero rows since lane start, not assumed.

UNCLEAR
FIRST READ: “exactly three rows / two assertions / no other table” was read as the production-write
envelope. Reading the handlers showed the routes also write audit events, a superseded placeholder assertion
and a review task; I judged the owner's one-asset/one-date grant to cover those automatic route effects and
proceeded, while flagging the envelope as false.
DURING EXECUTION: the classification opened and the expiry resolved a review task; both route responses were
200; the startup pass created exactly one unread reminder at 13:59:06; the log carries no pass success line
by design.
REMAINING: correct the packet's row model (or re-scope the grant explicitly) before the next production-data
write; add the daily-pass success line in SG-238; reconcile the local `frontend/dist` bundle with the served
bundle when the frontend is next built.

Verification: FAIL — A2/A3 row accounting (assertion +3 not +2; audit_event +4; review_task +1; reminder +1 as expected)
