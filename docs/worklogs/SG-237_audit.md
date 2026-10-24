# SG-237 audit — D2 live reminder proof: the chain ran end-to-end in production (one unread reminder exists, engine-shaped, buttons live); A2/A3 failed on the packet's own row model; rated 95

**Receipt verified:** notes-ref trailer `Dispatch-ID: SG-237 | Report: docs/worklogs/SG-237_report.md | Work-HEAD: 8c2b6ed17cf309c36304a634df588253468a4366` read from the **explicitly fetched mapped ref**. Trigger returned `result=done id=SG-237 exit=0`.

**Diff verified (base `9d340cf` → HEAD `09cb913`):** seven paths, every one `docs/worklogs/SG-237*` — **zero** product, config, schema, migration or test bytes.

**The owner's goal was met.** One ACTIVE asset (**Miso Soup**, `01a0c4aa-…a0f6` — a food, chosen from the 7-asset inventory and reported with the reason), one classification (`food_beverages`, HTTP 200) and one expiry date read from the live clock (**2026-10-27**, three days out, HTTP 200) went in through the app's own routes. The engine then shows that asset as `tier urgent / bucket this-week / days_remaining 3`. One container restart (same id, same image, `Cmd app.server:app`, `RestartCount` 0) triggered the **startup pass**, and it created **exactly one** row:

    reminder 01a16e35-4394-7c11-9798-844754826bcc · Miso Soup · as_of_day 2026-10-24
    tier urgent · bucket this-week · days_remaining 3 · status unread · created_at 13:59:06

`GET /v1/reminders?household_id=…` → **200, `unread_count` 1**, the same shape; the served JS still carries `Unread reminders` / `Read reminder` / `Dismiss reminder`. The reminder was left **unread** — no `/read` or `/dismiss` POST was made, so the owner can finish the loop by hand. The bounded observation wait (60 s in 5 s steps) saw `reminder_rows=0` at +0 s and `health=200 reminder_rows=1` at +5 s; observed app-unavailable span **5.95 s**.

**A2 and A3 failed — on numbers the packet supplied, not on the work.** The packet's envelope said *"exactly THREE rows … two assertions + one reminder … no other table is touched"*. The committed routes do more: each `_write_assertion` writes an `audit_event` (`backend/app/plugins/expiry_tracker.py:347-356`), `classify_asset` writes a **second, placeholder** `expiry_date` assertion and opens a review task for a perishable with no observed date (`:423-428`), and `enter_expiry` writes its own audit row. Actual movement: **assertion +3, audit_event +4, review_task +1, reminder +1** — every one of them the routes' own trail for the one asset and one date the owner granted, nothing else touched, nothing deleted. The Coder read the handlers **before** the write, reported the divergence as F1, proceeded under the owner's one-asset/one-date grant, did **not** bend the counts, and ended with `Verification: FAIL — A2/A3 row accounting`. That is the correct behaviour for a false premise in the packet. The packet was also wrong twice more: F3 (a `docker restart` preserves container identity — only `StartedAt` changes) and F2 (the log cannot announce the row: the daily module logs failures only).

**No flag:** no safety breach (three authorised rows and the route's own audit/state trail, one restart of the same image, no build, no recreate, no migration, no deletion, $0, zero provider calls) and no trust breach (every count reported as observed, the failing legs named, the envelope correction escalated to the next packet instead of being worked around).

**Holistic: 95/100, no flag.** The material requirement (the owner's D-1024-7 grant) is **complete** and the end-to-end proof is real; the two FAIL legs are the packet's false numbers, and the Coder's judgement to proceed under the grant rather than stop for a packet-wording defect was right and disclosed. `deduction_attribution`: **packet** — all three false claims (the row model, the "new container identity", the log-announces-the-row) came from the packet, and the Coder's execution was correct throughout. `slowest_waste`: **135 s G1 pre-state** (the code reading and premise checks — the packet handed over the route shapes but not their side effects; the next packet derives a row model by reading the write path).

### Dispositions

| Item | Status |
|---|---|
| F-SG237-1 — the packet's row model was false (3 vs 2 assertions, plus audit_event and review_task) | **RESOLVED by correction, not by code** — the envelope is corrected in the next packet; the rows are the routes' own trail, enumerated in the report |
| F-SG237-2 — the daily pass logs failures only, so the log cannot announce a created row | **FIX QUEUED** — SG-238 adds the success line + a test |
| F-SG237-3 — a `docker restart` preserves container identity (only `StartedAt` changes; `RestartCount` stays 0) | **RESOLVED as recorded** — the packet's wording was wrong; the observation stands |
| F-SG237-4 — Docker's health field read `starting` at the first HTTP-green instant, `healthy` by 14:00:03 | **RESOLVED as recorded** — timing nuance, not a failed health check |
| F-SG237-5 — the local `frontend/dist` bundle differs from the served bundle | **parked** — the served bundle is the one that matters; no file touched |
| Any future production-data write | **RULE** — derive the row model by reading the write path before stating a count (`_write_assertion` → audit_event; `classify_asset` → placeholder assertion + review task; `enter_expiry` → audit row) |
| SG-237 receipt + rating row | **RESOLVED** — published, read back from the fetched ref, row appended this turn |
| The reminder row itself | **OPEN by design** — left unread so the owner clicks Read/Dismiss; SG-238's scope does not touch it |
| Session close | **OPEN** — the owner asked whether a close was requested; the session continues with SG-238 and then roadmap row 11 |
