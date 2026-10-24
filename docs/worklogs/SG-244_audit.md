# SG-244 audit — one production status transition (`read` → `dismissed`) on the Miso Soup reminder, through the app's own route; rated 96

**Receipt verified:** notes-ref trailer `Dispatch-ID: SG-244 | Report: docs/worklogs/SG-244_report.md | Work-HEAD: e447c8930708bba1f8d1cbb8499e65b5f32c2542` read from the **explicitly fetched mapped ref** (`refs/notes/storagegenie-coder-reports`). Trigger returned `result=done id=SG-244 exit=0`. Work commit `e447c89` + receipt commit `95cd9b7` are on `origin/automation`; the report's last line is `Verification: PASS`.

**Diff verified (base `723d0d0` → `95cd9b7`):** ten files, every one `docs/worklogs/SG-244*` — **zero** product, config, schema, migration, dependency or test bytes. Terminal class **CHANGED**, and it is the *one* write the owner named, on the *one* row they named.

**The write happened, exactly once, and the state before it was captured first.**

- **G1 (read-only, 16:39:33Z–16:40:07Z):** health `200 {"status":"ok","db":"ok","storage":"ok"}`; `GET /v1/reminders` → `unread_count 0`, one item — id `01a16e35-4394-7c11-9798-844754826bcc`, asset `01a0c4aa-…`, `display_name "Miso Soup"`, `as_of_day 2026-10-24`, tier `urgent`, bucket `this-week`, `days_remaining 3`, **`status "read"`**, `updated_at 2026-10-24 15:21:24`. The row's every column was read from the served SQLite file with `sqlite3 -readonly`; `reminder` count 1; alembic head `20261023_sg233_reminder`; all 29 table counts; access-log baseline **0** mutating lines.
- **G2 (one call, 16:40:13Z):** `POST http://127.0.0.1:8003/v1/reminders/01a16e35-…/dismiss?household_id=01a0a029-…` → `200`, body with **`"status":"dismissed"`** and every other field byte-identical. No retry, no second mutating call. The container's own access log shows the mutating delta **0 → 1**, the single line quoted with its timestamp `16:40:13.444250567Z`. The transition is the app's own committed `_transition` (`backend/app/api/v1/reminders.py:93-104`), and `dismissed` is legal from `read` (`reminders.py:24-27`).
- **G3 (read-only, 16:40:19Z–16:40:50Z):** `status "dismissed"`, `unread_count 0`, every identity field identical, `reminder` count 1, **all 29 table counts identical** (`audit_event` 104 → 104), head unchanged, health 200. The before/after table is in `SG-244_identity_diff.log` and the census diff prints `IDENTICAL: all 29 table counts`.

**The two columns are disclosed, not hidden (my packet's wording was wrong).** The authorized route's single UPDATE touches **`status` and `updated_at`** — `TimestampMixin` sets `onupdate=func.now()` (`backend/app/models/base.py:24-25`), so the timestamp necessarily advances in the same statement (`15:21:24` → `16:40:13`). My packet said "one production UPDATE of one column"; that wording was imprecise. The Coder did not bend the measurement to match the wording: it reported the discrepancy as **F1/F2** and passed A3 with the exception stated.

**The decision file's path for this row cannot exist (F3 — my file, not the report).** `docs/decisions/2026-10-24-session-approvals.md` contemplates "if the owner has already clicked Dismiss on the Expiry page". `frontend/src/routes/ExpiryPage.tsx:126` renders only `status === "unread"` rows, so a `read` row has no buttons at all. The API was the only path for this row, and the slice used it. This is the same defect SG-241's audit recorded (D-1024-13 standing rule: never name a UI affordance that does not exist for the row's state).

**The access log was read as a file, not through docker (F5, disclosed).** The packet forbade any docker command; reading the container's JSON log therefore went through the rootless-docker data root (`/proc/1097/root/home/andrei/.local/share/docker/containers/6c648f1c…-json.log`). That is a file read. No docker invocation, no restart, no build, no migration command, no browser, no prompt loop — the packet's constraints were met and the method was stated rather than quietly done.

**Recurrence is by design, and it is the owner's next three days (F4).** `record_due` is keyed on `(asset_id, as_of_day)` (unique constraint `uq_reminder_asset_as_of_day`) and the daily loop runs a pass per live UTC day, so today's dismissal silences **today only**: a fresh **unread** Miso Soup row arrives on the 25th, the 26th and the 27th, and stops once the expiry date `2026-10-27` has passed. The Expiry page's unread block stays empty today and shows the new row tomorrow — that is the working feature, not a defect.

**No flag:** no safety breach (one row updated on the owner's own row, zero rows created or deleted, no secret, no migration, no host change, `$0.000000`, `provider_call` 39 → 39) and no trust breach (the two-column side effect and the file-read method were both reported; the write is evidenced by four independent artifacts — response body, SQL row, `updated_at`, and the access-log line).

**Holistic: 96/100, no flag.** The slice did exactly the one thing the owner authorised, on the row they named, through the app's own route, with the state before and after captured and diffed. It loses points for the wording defects that live in **my** packet and decision file (the "one column" claim and the non-existent UI path). `deduction_attribution`: **packet**.

### Dispositions

| Item | Status |
|---|---|
| The owner-named dismissal (D-1024-11) of the Miso Soup row | **RESOLVED** — `read` → `dismissed` at 16:40:13Z through `POST /v1/reminders/{id}/dismiss`, one call, pre/post state captured and diffed, all 29 counts identical |
| SG-241's rider clause that treated "already `read`" as the end state | **RESOLVED** — the missing write was carried to SG-244 (D-1024-13) and executed |
| The packet's "one column" wording vs the model's `onupdate` | **RESOLVED as recorded** — F1/F2 disclosed; next-packet rule: a packet that authorises a write must name the model's own side effects (`updated_at` on `onupdate`) |
| The decision file's "click Dismiss on the Expiry page" path for a non-unread row | **RESOLVED as recorded** — F3; the API was the only path, and it was used |
| Reminder transitions record **no actor and no audit row** | **OPEN** — backlog W4 (a product change on a declared sensitive surface; needs the owner's scoping word) |
| A fresh unread Miso Soup row on 2026-10-25, -26 and -27 | **OPEN by design** — reported; the daily pass is what creates it |
| The two always-red host signal tests | **OPEN** — the W1 second opinion (SG-242/SG-243) precedes the owner's decision |
| The full `mypy app` reds (41 in 9 untouched files) and the pre-existing eslint error | **OPEN, parked by the owner** — the hygiene slice (W3) |
| SG-244 receipt + rating row | **RESOLVED** — receipt read back from the fetched ref; this row and this audit committed this turn |
