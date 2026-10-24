SG-244 — One production status transition: the Miso Soup reminder `read` → `dismissed`, through the app's own route

**Terminal class: CHANGED.** One production row transition was performed through the app's own route; the commit carrying this evidence is docs-only, and no product code changed.

## Identity and base

- **BASE REF:** `origin/automation`
- **BASE COMMIT (resolved):** `723d0d05a41134b98882161d2b9b78a948020aff` (`git rev-parse origin/automation` and `git ls-remote origin refs/heads/automation` agree)
- **WORK HEAD at slice start:** `723d0d05a41134b98882161d2b9b78a948020aff`
- **WORK COMMIT:** the docs-only commit that carries this report. Its hash is recorded by the notes receipt (A6) and is deliberately not self-referenced here (`CO-55(b)`).
- **Model / reasoning effort (read from this process's own arguments, `ps -o args= -p 3445384`):** `opencode-go/deepseek-v4.1-flash` / `max` (`--variant max`). Not read from any system-prompt identity line.
- **Lane start (systemd unit stamp):** `2026-10-24T16:39:08Z`
- **Money:** `$0.000000` actual vs `$0` bound; 0 provider calls; `provider_call` table 39 → 39.

## G1 — Pre-state (read-only, before anything else)

Read at `2026-10-24T16:39:33Z`–`16:40:07Z`, all loopback (`http://127.0.0.1:8003`), SQLite opened with `sqlite3 -readonly` on `./data/db/storagegenie.db`. No docker command ran.

**Health** (`16:39:39Z`, captured in `docs/worklogs/SG-244_g1_api.log`):

```
HTTP/1.1 200 OK
{"status":"ok","db":"ok","storage":"ok"}
```

**`GET /v1/reminders?household_id=01a0a029-1477-7ca0-b200-bce78a96c679`** (`16:39:39Z`, HTTP 200):

```json
{"household_id":"01a0a029-1477-7ca0-b200-bce78a96c679","unread_count":0,"items":[{"id":"01a16e35-4394-7c11-9798-844754826bcc","household_id":"01a0a029-1477-7ca0-b200-bce78a96c679","asset_id":"01a0c4aa-8b62-7360-b11e-a476ddaea0f6","display_name":"Miso Soup","as_of_day":"2026-10-24","tier":"urgent","window_days":7,"bucket":"this-week","days_remaining":3,"status":"read","created_at":"2026-10-24T13:59:06","updated_at":"2026-10-24T15:21:24"}]}
```

**The `reminder` row itself, every column** (`16:39:33Z`, `docs/worklogs/SG-244_g1_sql.log`):

```
id             = 01a16e35-4394-7c11-9798-844754826bcc
household_id   = 01a0a029-1477-7ca0-b200-bce78a96c679
asset_id       = 01a0c4aa-8b62-7360-b11e-a476ddaea0f6
as_of_day      = 2026-10-24
tier           = urgent
bucket         = this-week
days_remaining = 3
status         = read
created_at     = 2026-10-24 13:59:06
updated_at     = 2026-10-24 15:21:24
```

The owning asset row also reads `display_name = Miso Soup` (queried read-only at the same time). The row is present, named Miso Soup, and `read` — so the STOP conditions in the packet do not apply, and `read` → `dismissed` is the authorized legal transition (`backend/app/api/v1/reminders.py:24-27`).

**`reminder` row count:** `1`. **Alembic head:** `20261023_sg233_reminder`.

**Per-table census** (`16:39:40Z`, `docs/worklogs/SG-244_g1_counts.log`):

```
alembic_version 1      assertion 40          asset 7               asset_evidence 20
asset_fts 7            asset_fts_config 1    asset_fts_data 9      asset_fts_docsize 7
asset_fts_idx 7        asset_location 1      asset_relation 1      audit_event 104
candidate 10           enrich_snapshot 4     evidence 27           guardrail_event 2
household 1            idempotency_key 11    job 11                job_step 72
location 1             observation 20        planning_suggestion 0 provider_call 39
reminder 1             review_task 9         saved_search 0        source_attribution 0
user 2
```

**Access-log baseline** (`16:40:07Z`): the backend container's own JSON log contained **0** lines matching `POST|PUT|PATCH|DELETE`. The log was read as a file through the rootless-docker data root; **no docker command was run** (see “How the access log was read” below).

## G2 — The one authorized write

Exactly **one** POST, at `2026-10-24T16:40:13Z`, through the served app (`docs/worklogs/SG-244_g2.log`):

```
POST http://127.0.0.1:8003/v1/reminders/01a16e35-4394-7c11-9798-844754826bcc/dismiss?household_id=01a0a029-1477-7ca0-b200-bce78a96c679

HTTP/1.1 200 OK
content-type: application/json

{"id":"01a16e35-4394-7c11-9798-844754826bcc","household_id":"01a0a029-1477-7ca0-b200-bce78a96c679","asset_id":"01a0c4aa-8b62-7360-b11e-a476ddaea0f6","display_name":"Miso Soup","as_of_day":"2026-10-24","tier":"urgent","window_days":7,"bucket":"this-week","days_remaining":3,"status":"dismissed","created_at":"2026-10-24T13:59:06","updated_at":"2026-10-24T16:40:13"}
```

First attempt returned `200`; no retry and no second mutating call. The access log after the write (`16:40:19Z`, `docs/worklogs/SG-244_g3_counts.log`) contains **exactly one** mutating line — the one above:

```
{"log":"INFO:     172.18.0.1:48604 - \"POST /v1/reminders/01a16e35-4394-7c11-9798-844754826bcc/dismiss?household_id=01a0a029-1477-7ca0-b200-bce78a96c679 HTTP/1.1\" 200 OK\n","stream":"stdout","time":"2026-10-24T16:40:13.444250567Z"}
```

Count 0 before, 1 after; delta exactly the POST. No other row, expiry date, creation, deletion or re-dating occurred. Because the route commits (`_transition`, `backend/app/api/v1/reminders.py:93-104`), the change is durable.

## G3 — Post-state (read-only)

Read at `2026-10-24T16:40:19Z`–`16:40:50Z`.

**`GET /v1/reminders?household_id=…`** (HTTP 200, `docs/worklogs/SG-244_g3.log`):

```json
{"household_id":"01a0a029-1477-7ca0-b200-bce78a96c679","unread_count":0,"items":[{"id":"01a16e35-4394-7c11-9798-844754826bcc","household_id":"01a0a029-1477-7ca0-b200-bce78a96c679","asset_id":"01a0c4aa-8b62-7360-b11e-a476ddaea0f6","display_name":"Miso Soup","as_of_day":"2026-10-24","tier":"urgent","window_days":7,"bucket":"this-week","days_remaining":3,"status":"dismissed","created_at":"2026-10-24T13:59:06","updated_at":"2026-10-24T16:40:13"}]}
```

**The row itself after the write:**

```
id             = 01a16e35-4394-7c11-9798-844754826bcc
household_id   = 01a0a029-1477-7ca0-b200-bce78a96c679
asset_id       = 01a0c4aa-8b62-7360-b11e-a476ddaea0f6
as_of_day      = 2026-10-24
tier           = urgent
bucket         = this-week
days_remaining = 3
status         = dismissed
created_at     = 2026-10-24 13:59:06
updated_at     = 2026-10-24 16:40:13
```

**Before / after, side by side** (`docs/worklogs/SG-244_identity_diff.log`; every listed identity field is `SAME`):

| Field | Pre (16:39:33Z) | Post (16:40:19Z) |
|---|---|---|
| id | `01a16e35-4394-7c11-9798-844754826bcc` | same |
| household_id | `01a0a029-1477-7ca0-b200-bce78a96c679` | same |
| asset_id | `01a0c4aa-8b62-7360-b11e-a476ddaea0f6` | same |
| display_name | `Miso Soup` | same |
| as_of_day | `2026-10-24` | same |
| tier | `urgent` | same |
| window_days | `7` | same |
| bucket | `this-week` | same |
| days_remaining | `3` | same |
| created_at | `2026-10-24T13:59:06` | same |
| **status** | **`read`** | **`dismissed`** |
| **updated_at** | **`2026-10-24T15:21:24`** | **`2026-10-24T16:40:13`** |
| unread_count | `0` | `0` |

**Health** (`16:40:19Z`): `HTTP/1.1 200 OK`, `{"status":"ok","db":"ok","storage":"ok"}`.

**Census:** `reminder` count `1` (unchanged); head `20261023_sg233_reminder` (unchanged); all 29 table counts byte-identical to G1 (`diff` of the two census blocks printed `IDENTICAL: all 29 table counts`, `docs/worklogs/SG-244_identity_diff.log`). In particular `audit_event` 104 → 104: this transition records no audit row, and the `reminder` schema has no actor column (`docs/worklogs/SG-244_g1_sql.log`), exactly as the packet warned. The pre-state quoted in G1 is therefore the only evidence of the row's prior status.

**Recurrence evidence** (`16:40:50Z`, read-only plugin status, `docs/worklogs/SG-244_g3_status.log`): the same asset has `expiry_date 2026-10-27`, `days_remaining 3`.

## A1–A6

**A1 — PASS.** G1 is quoted in full above: id, asset, display name, `as_of_day`, tier, bucket, days, `status=read`, `updated_at=2026-10-24 15:21:24`, row count 1, head `20261023_sg233_reminder`, all 29 table counts, health 200. The row is Miso Soup and was present before the write.

**A2 — PASS.** Exactly one POST to the dismiss route: `200`, body quoted above with `status:"dismissed"`. The access log's POST/PUT/PATCH/DELETE delta is 0 → 1, and the single line is quoted above. No retry, no second call, no other mutation.

**A3 — PASS, with the one disclosed timestamp exception.** Post-state quoted; `status=dismissed`; `unread_count=0`; `asset_id`, `as_of_day`, `tier`, `bucket`, `days_remaining`, `display_name`, `created_at` identical; row count 1; every table count identical; health 200; head unchanged. The single non-identical field besides `status` is `updated_at` (`15:21:24` → `16:40:13`). That is not an extra write: the model sets `onupdate=func.now()` on `updated_at` (`backend/app/models/base.py:24-25`), so the app's own authorized route necessarily advances it in the same single UPDATE. This is finding F1/F2, not a hidden change. If “every other field” is read to demand a frozen `updated_at`, that sub-check would fail — but only because the route the packet authorizes cannot freeze it, and this slice forbids the code change that would.

**A4 — PASS (what the owner sees).** The Expiry page's unread-reminders block stays empty: it was empty before and after (`unread_count` 0 in both API reads; the page filters to `status === "unread"`, `frontend/src/routes/ExpiryPage.tsx:126`), so this row was invisible there in both states. The stored state changed **`read` → `dismissed`**. Recurrence is by design, not a defect: `record_due` keys on `(asset_id, as_of_day)` (`backend/app/services/reminders/service.py:49-60`; unique constraint `uq_reminder_asset_as_of_day`), and the daily loop runs a pass per live UTC day (`backend/app/services/reminders/daily.py:46-105`). A fresh **unread** Miso Soup row will therefore arrive tomorrow (`2026-10-25`), and again on the 26th and 27th; it stops once the expiry date `2026-10-27` has passed (from the 28th), matching D-1024-11. The browser was not used (packet constraint); this line is derived from the live API state and the named frontend filter, not from a screenshot.

**A5 — PASS.** BASE ref `origin/automation` and resolved base commit `723d0d05a41134b98882161d2b9b78a948020aff` are echoed separately above. The work diff is confined to `docs/worklogs/SG-244*` (10 files: this report, the worklog, and eight evidence logs); no product, config, schema, migration, dependency or test file changed. Elapsed per leg vs the lane bound is in the Budget section. The three UNCLEAR lines close the report. The last line is `Verification: PASS`.

**A6 — receipt.** `refs/notes/storagegenie-coder-reports`; first line `Dispatch-ID: SG-244 | Report: docs/worklogs/SG-244_report.md | Work-HEAD: <work commit>`. Published after this report (a report cannot carry the hash of the commit that contains it, `CO-55(b)`); the push and mapped read-back are transcripted in `docs/worklogs/SG-244_receipt.log` and committed docs-only. Bound lane receipt only; the product branch is not moved by the notes publication.

## Premises re-verified (PG-IC-09)

| Packet premise | Measured | Verdict |
|---|---|---|
| Row id/asset/household as stated | exact match | confirmed |
| `display_name` = Miso Soup | API and asset row both Miso Soup | confirmed |
| `as_of_day` 2026-10-24, tier urgent, bucket this-week, days 3 | exact match | confirmed |
| `status` was `read`, `updated_at` 2026-10-24 15:21:24Z | exact match | confirmed |
| `dismissed` is legal from `read` | `LEGAL_TRANSITIONS["dismissed"] = {"unread","read"}` (`reminders.py:24-27`) | confirmed |
| Route is `POST /v1/reminders/{id}/dismiss?household_id=…`, commits | route at `reminders.py:116-122`; `_transition` commits at `:93-104`; live POST 200 | confirmed |
| No actor / no audit row | no actor column in schema; `audit_event` 104 → 104 | confirmed |
| Expiry page renders unread only | `ExpiryPage.tsx:126` filter; `unread_count` 0 | confirmed |
| `record_due` keyed by `(asset_id, as_of_day)` | `service.py:49-60`; unique constraint in schema | confirmed |
| “One column” changes | route writes `status` **and** `updated_at` via `onupdate` | **finding F1** (wording, not an extra write) |

## Findings

- **F1 (packet wording).** The authorized route's single UPDATE touches one row and one statement, but two columns: `status` (the change the owner named) and `updated_at` (`TimestampMixin`, `backend/app/models/base.py:24-25`). The packet's “one production `UPDATE` of one column” is imprecise; no extra statement, row or call exists. I did not bend the measurement.
- **F2 (A3 literal).** Because of F1, `updated_at` moved. Every enumerated identity field is unchanged; the timestamp movement is the route's own bookkeeping and is disclosed rather than suppressed.
- **F3 (decision-file path).** `docs/decisions/2026-10-24-session-approvals.md:106` contemplates “if the owner has already clicked Dismiss on the Expiry page”. For a `read` row that path cannot exist: the page filters unread only (`ExpiryPage.tsx:126`). This slice performed the transition by API, which is the only path for this row.
- **F4 (recurrence).** The dismissal silences today only; a fresh unread row is expected on the 25th, 26th and 27th, stopping after the 27th. This is by design (D-1024-11), not a defect.
- **F5 (access-log access).** Reading the access log without violating “no docker command of any kind” required reading the container's JSON log file through the rootless-docker data root (`/proc/1097/root/home/andrei/.local/share/docker/containers/6c648f1c…/…-json.log`). This is a file read, not a docker invocation; no restart or container operation occurred.

## Vacuity check (PB-3)

- A2 cannot pass vacuously: the same log file recorded my HTTP GETs before and after, the mutating baseline was 0, and the post-write count is 1 with the exact POST line and timestamp. A log that could not show a POST would not have shown this one.
- A3 cannot pass vacuously: the census was run twice on the live file and the two blocks were diffed (`IDENTICAL: all 29 table counts`), and the API pre/post JSON was compared field by field.
- A4's browser clause is **not** a screenshot claim; no browser was used (forbidden). It is explicitly labelled as API + code evidence.
- The write is not inferred from an empty diff: the response body, the SQL row, `updated_at`, and the access-log line all changed together.

## Constraints and guards

- Scope: `docs/worklogs/SG-244*` only; no product, config, schema, migration, dependency or test edit. One production UPDATE of one row through the app's route; no row created or deleted (`reminder` 1 → 1; no INSERT/DELETE evidence in the log). Reads were curl GETs and `sqlite3 -readonly`; the only mutating call was the single G2 POST (`PG-IC-01`).
- No docker invocation, no browser, no prompt/polling loop, no restart, no build, no migration command. `alembic_version` unchanged at `20261023_sg233_reminder`.
- Network: loopback `127.0.0.1:8003` only; no provider call (`$0.000000` actual vs `$0` bound); no secret in any artifact.
- `PG-EV-02` artifact-not-command: every claim above is captured in a committed log or the report.
- `PG-EV-03` stop-not-disclosure: no stop condition occurred; nothing was disclosed instead of blocked.
- `PG-EV-06` rows-your-run-creates: **0 rows created**, 0 deleted, 1 row updated.
- `PG-EV-08` pre-state-before-claim: G1 was captured at 16:39:33Z–16:40:07Z, before the 16:40:13Z write.
- `PG-DP-01` delivered-by-the-path: the write went through the served route, proven by the container's own access-log line.
- `PG-DP-02` no-sweep-waiver: no code changed, so no product test set or full suite was run; the live post-state reads are the verification. This is not a waiver of a test that should have run.
- `PG-PR-03` denied-is-stop: no privileged or denied operation was attempted.
- `PG-PR-04` how-code-becomes-live: no code became live; the already-running app performed the write with its existing bytes. Nothing was built, recreated or restarted.
- `PG-PR-06` runtime-versus-budget: measured below from the lane's own stamp.
- `PG-PR-10` which-database: production SQLite, host `./data/db/storagegenie.db`, bind-mounted to `/data/db/storagegenie.db` (`docker-compose.yml` `DATABASE_URL=sqlite:////data/db/storagegenie.db`). The API row and the read-only file agree, so the file read is the served database. Test DB untouched; no test ran.

## Budget

- **Lane start:** `2026-10-24T16:39:08Z` (unit stamp).
- **Report writing begins:** `2026-10-24T16:41:37Z`.
- **Elapsed:** `149 s` of the `900 s` overall bound (16.6%) and of the lane's `2100 s` (7.1%).
- **Legs (box clock, UTC):** G1 `16:39:33–16:40:07Z` (34 s); G2 `16:40:13Z` (≈1 s, one POST); G3 `16:40:19–16:40:50Z` (31 s incl. the read-only status GET); identity/census diff `16:41:45Z` (<1 s); report composition the remainder.
- **Commands:** every command ran under a stated timeout; the longest observed wall time was ≈11 s (network GETs with a 10 s cap), nowhere near 120 s; none was killed; the 900 s idle kill was never approached.
- **REAL metered spend:** `$0.000000` actual vs `$0` bound; `provider_call` 39 → 39.

## UNCLEAR

UNCLEAR FIRST READ: none. Every packet premise held on first read; the only surprise was the `updated_at` side-effect written into the model (`onupdate=func.now()`), which the packet's “one column” wording did not anticipate.

UNCLEAR DURING EXECUTION: the authorized route updates two columns, not one (F1/F2). I completed the authorized call and report the discrepancy rather than pretending the timestamp stood still; freezing it would require a code change this slice forbids.

UNCLEAR REMAINING: `updated_at` now reads `16:40:13`; the no-actor/audit gap (W4) is unchanged; a fresh unread row for Miso Soup should appear on the 25th, 26th and 27th and stop after the 27th; the decision file's “click Dismiss on the Expiry page” path does not exist for a non-unread row (F3).

Verification: PASS
