# 2026-10-24 — The row-11 stage, and the standing dispatch rules (D-1024-8, D-1024-9)

Owner instruction, quoted byte-identical (2026-10-24, this chat):

> Next action (my recommendation): write and dispatch the roadmap row-11 slice — opened-date countdown for cosmetics — carrying the logging configuration with it (the app logs nothing at INFO, so the daily pass is invisible in the server log; prove it in a container, not only in caplog), then row 11's close-deploy rider, which is where the pass line first appears live.

> First things to put to the owner, whole and with no action taken yet: W1 — whether to authorise an install path that can sudo for the two host test libraries (libzbar0, tesseract; the lane's sudo is denied and nothing on the host was changed; the image route make backend-test-image already proves those two reds environmental); W2 — Miso Soup's expiry date is 2026-10-27 on their own data, dismiss or move it. Then the parked mypy reds (app/models/base.py, app/services/audit_service.py).

> Working rules the owner set for this repo: dispatch at L3 with model=opencode-go/deepseek-v4.1-flash effort=max; the Coder's report ends with a Verification: line; every app-changing slice is deployed as its own slice right after it is rated; every close = live deploy + release record + END report on Launcher #62; keep everything else parked.

## D-1024-8 — Stage: roadmap row 11 and its close-deploy rider, at L3

**Do:** roadmap row 11 (opened-date countdown for cosmetics) and the close-deploy rider that serves it are one approved stage.

- **Autonomy: L3.** Inside the stage the Architect packets, dispatches, audits and rates each slice without asking. A stage boundary is a new approval.
- **Envelope on every trigger:** `coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max`. Settings ride the trigger, never the packet.
- **The rider is a slice of its own**, dispatched after the work slice is rated: it builds the image, recreates the container, and is the first place the daily pass's success line appears in the **production** log.
- `AGENTS.md` now records L3 in the configuration table (it said L2 — the owner's chat instruction outranks the file, and the file now matches).

**SG-240's packet:** `docs/packets/SG-240-opened-countdown-and-logging.md`.

**The design calls SG-240 makes** (recorded so the next session does not re-derive them):

- The countdown's end is the category's after-opening window: `cosmetics_personal_care` declares **12 months**, **DECLARED UNCALIBRATED** at the site, sourced to the EU period-after-opening (PAO) symbol (Regulation 1223/2009 Art. 19) whose printed figure varies per product. The response names the window and its source, so the number is visible and correctable. **A per-item PAO override is parked.**
- Storage is one accepted assertion: `field_path = "opened_date"`, `value_json` a bare JSON string — the shape the planning and chat services already read.
- The read endpoint returns one row per ACTIVE asset in an opened-date-tracking category, **including rows with no opened date yet**, so the UI can offer the form.

## D-1024-9 — Standing rules for this repo

Recorded in `AGENTS.md` (configuration table) as well, so they bind a cold session:

- **Dispatch at L3** with `model=opencode-go/deepseek-v4.1-flash effort=max` on every trigger.
- **The Coder's report ends with a `Verification:` line** (`CO-104`).
- **Every app-changing slice is deployed as its own slice, right after it is rated** — the deploy is not folded into the work slice and not deferred to the close.
- **Every close = live deploy + release record + END report on Launcher issue 62.**
- **Everything else stays parked** — the roadmap rows other than 11, the email path (parked on SMTP credentials, D-1024-2), and the three pre-existing mypy reds in `app/models/base.py` and `app/services/audit_service.py`.

## W1 and W2 — waiting decisions, nothing acted on

Both are now rows in `docs/backlog.md` with their triggers. **No action was taken on either** (nothing installed on the host, no production row written, no reminder dismissed).

- **W1 — the two host test libraries.** The lane's `sudo -n` is denied, so the host suite keeps two environmental reds (`backend/tests/test_signals.py`, the generated-code and OCR tests) on every run; SG-238 proved both green inside the project's own image, and `make backend-test-image` is the repeatable route. The owner's word decides between an authorised install path and keeping the image route.
- **W2 — the Miso Soup reminder row** (expiry 2026-10-27, tier urgent, bucket this-week, unread). `record_due` skips an item that already has a row **for the same day**, so dismissing silences today only; a new unread row arrives on each following day until the date passes. The owner chooses: dismiss, move the date, or leave it standing.

**Neither blocks the row-11 stage:** SG-240's host suite quotes the same two reds as environmental (as SG-235–SG-239 each did), and SG-240 touches no production row.
