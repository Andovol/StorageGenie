# 2026-10-24 — Session approvals (D-1024-1 … D-1024-12)

Owner instruction, quoted byte-identical (2026-10-24, this chat):

> StorageGenie, continue (paste any time). Run the start command first, then do these in order.
> Approved now:
> - Adopt contract 0.52.0: check out tag contract-v0.52.0, update AGENTS.md:4 and STATE.md:6, re-run the start command, record docs/decisions/2026-10-24-contract-052-adoption.md.
> - Daily reminders: option A, a background task inside the app. It runs once at startup, then every 24 hours (UTC), and calls record_due for every household. Do not backfill missed days. Email stays out (no SMTP).
> - Close PRs #43-#49 with one comment each: "Content landed on automation via SG-161..164 and was served by SG-165; closing as already applied."
> - Close Launcher #89 (D477 is live). Launcher #84 is answered: engine v0.52.0 is live since 2026-10-24 10:24Z. Close it after your next slice shows no false report_unreadable.

## D-1024-1 — Contract 0.52.0 adopted

**Adopt contract 0.52.0.** Full record: `docs/decisions/2026-10-24-contract-052-adoption.md`.

## D-1024-2 — Daily reminders: option A, a background task inside the app

**Do:** a background task inside the app runs **once at startup**, then **every 24 hours (UTC)**, and calls `record_due` for **every household**.

- **No backfill** of missed days. A run computes today only.
- **Email stays out** — no SMTP. The in-app sender from SG-233 is the delivery path.
- Non-negotiable: the caller is inside the app (option A), not a host cron or an external scheduler.

## D-1024-3 — Pull requests #43–#49 closed as already applied

**Close PRs #43, #44, #45, #46, #47, #48, #49** with this one comment each, verbatim:

> Content landed on automation via SG-161..164 and was served by SG-165; closing as already applied.

## D-1024-4 — Launcher #89 closed now; #84 closed on the next clean slice

- **Close Launcher #89** now — D477 is live.
- **Launcher #84 is answered**: engine v0.52.0 is live since 2026-10-24 10:24Z. It closes **after the next slice shows no false `report_unreadable`** — the condition is the gate, not the date.

## D-1024-5 — Context compression is DCP's call, not mine

Owner directive (2026-10-24, this chat), quoted:

> Why did you request compress? I have certain limits set in DCP. you need to let DCP suggest compression.

**Do:** the Architect does **not** initiate a `compress` call on its own initiative in this project. **DCP suggests; the Architect acts on the suggestion.** The generic harness guidance ("use `compress` deliberately") is a default, and this project narrows it: context compression waits for DCP's signal.

**Why:** the owner holds the DCP limits for this workspace, and a self-initiated compression can cut material the owner wanted kept (and, in this session, fired without the owner's limits being consulted).

**Note on this session:** one self-initiated compression already ran (block `b1`, covering the closed steps 1–3: contract adoption, release record, PR closes). Its content was preserved in the summary and the underlying facts are durable in git (`f9f63b3`, `67f1aa4`) and in `docs/decisions/2026-10-24-contract-052-adoption.md`. Nothing else was compressed, and no further compression happens in this session unless DCP suggests it.

## D-1024-6 — D1 approved: the two always-red suite tests must stop masking signal

Owner, 2026-10-24 (this chat), verbatim: *"Okay with D1 and D2"*.

**Do:** make the two red tests (`backend/tests/test_signals.py` — generated-code validation and OCR text boxes) stop masking signal in every later suite run.

- **Cheapest mechanism first:** the project's own image already installs both libraries (`backend/Dockerfile`: `apt-get install tesseract-ocr libzbar0`), so the fix is to run those tests **inside the image** and record the result — **no host change needed**.
- The host package install the owner authorised is the **fallback**, used only if the image route fails.

## D-1024-7 — D2 approved: accept one near expiry date so the daily reminder path is proven end-to-end

Owner, 2026-10-24 (this chat), verbatim: *"Okay with D1 and D2"*.

**Do:** accept one classification plus one near expiry date (≈3 days out) for one ACTIVE asset of the live household `01a0a029-…c679`, through the app's own plugin routes; let the daily pass run; observe the reminder row it creates.

- **This is a production data write on the owner's own data — authorised by the owner on 2026-10-24 (this section).**
- The reminder is left **unread**, so the owner can click Read/Dismiss on the Expiry page and finish the loop by hand.
- The slice reports which asset it touched and the expiry date it set.

## The close reading (owner query, 2026-10-24)

Owner, verbatim: *"But I did not ask for a close, did I?"*

- The Architect read the owner's step 6 — *"Close out: deploy, record the release, then close the session."* — as a close order; it is the authorisation the SG-236 rider packet cites for the deploy.
- The close-out obligations were discharged and are durable: the deploy, `docs/releases/2026-10-24.md` + tag `release-2026-10-24`, the END report on Launcher issue 62, the state file and the starter. **Nothing needs undoing.**
- If the owner meant "close out the work and keep going in this chat", the filed END report covers the deploy+release batch and the **next** close files a fresh one. The session continues with the approved D1/D2 work and then roadmap row 11.

## Standing order for this session (owner, quoted)

> Steps:
> 1. Adopt 0.52.0 as above.
> 2. Repair the release record: write docs/releases/2026-10-23.md and tag release-2026-10-23 on the bytes serving now (SG-233/234).
> 3. Close the PRs and #89 as above.
> 4. Write SG-235: (a) the daily caller as above, with tests that prove it fails before and passes after; (b) Read and Dismiss buttons on frontend/src/routes/ExpiryPage.tsx, using the endpoints and client wrappers SG-233 already shipped. The packet asks the Coder to end its report with "Verification: PASS" or "Verification: FAIL — <check>" (CO-104; the runner now refuses a restart without PASS). Dispatch at L2 with model=opencode-go/deepseek-v4.1-flash effort=max, then audit and rate it.
> 5. Fix STATE.md: the RESUME line no longer says "closing now", and the startup record names #84 and #89.
> 6. Close out: deploy, record the release, then close the session.

> After row 9 is done, the next work is roadmap row 11 (opened-date countdown for cosmetics). Keep everything else parked.

Read as: **row 9 closes with SG-235; roadmap row 11 (opened-date countdown for cosmetics) is the next work after that; every other roadmap row stays parked.** The close at step 6 is a live deploy plus a release record, then the session ends.

## D-1024-10 — W1 goes to a second opinion before it comes back to the owner

Owner, 2026-10-24 (this chat), verbatim: *"W1 - give me the 2nd opinion before bringing such decisions."*

**Do:** W1 (the two host test libraries) is **not** put to the owner again until the two-phase second opinion (`SECOND_OPINION.md`, `D451`) has run — Phase A blind, then Phase B critique carrying the Architect's pick verbatim.

- The decision item carries one line: *Second opinion (model): picked X; strongest objection Y; accepted / rejected because Z.* **A 🟠/🔴 item without that line and its review ID is malformed.**
- **Standing rule for this project:** every 🟠 or 🔴 decision item goes through the second opinion **before** the owner sees it, and so does a 🟡 item whose subject is the live host, the dispatch key, the app database, or the owner's own data. Never for 🔵.
- **Reviewer for this project:** `coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh`, dispatched with `agent=plan` — the contract's default resolved: the Architect runs on `opencode-go/minimax-m3.1-flash`, so the reviewer must not be that model, and the slice builder (`opencode-go/deepseek-v4.1-flash`) must not be the reviewer either.
- The context pack is `docs/reviews/2026-10-24-second-opinion-w1-host-test-libraries-context.md`; the review IDs are **SG-242** (Phase A) and **SG-243** (Phase B), each with a row in `docs/reviews/review-ledger.md`.

## D-1024-11 — W2: dismiss the Miso Soup reminder

Owner, 2026-10-24 (this chat), verbatim: *"W2 - dismiss."*

**Do:** the unread reminder row for Miso Soup is **dismissed**, through the app's own route (`POST /v1/reminders/{id}/dismiss`) — never by editing the database.

- **Authorised by the owner on 2026-10-24** — their own data, their own product.
- The standing close-deploy rider (the next slice) performs it, records the pre-state and the result, and reports it. If the owner has already clicked Dismiss on the Expiry page, the desired end state is reached and the rider reports "already dismissed" — **that is a pass, not a failure**.
- **A dismissal silences today only** (`record_due` skips an item that already has a row for the same day): a new unread row arrives on the 25th, the 26th and the 27th, and stops on the 28th when the date has passed. The owner took that trade knowingly — the date was a stand-in set by SG-237 (≈3 days out, D-1024-7), not a reading of the pack.
- **No other production row is touched.**

## D-1024-12 — Priority: the remaining missing photo AI features

Owner, 2026-10-24 (this chat), verbatim: *"I want to prioritize the remaining missing photo AI features going forward."*

**Do:** the next stage after roadmap row 11 and its close-deploy rider is the **remaining missing photo AI work** — roadmap row 14, "Second AI provider and local option with fallback and spending limits", whose missing part is the **second photo reader not wired** into the router (`backend/app/services/providers/`), alongside the scene-only web reader (`backend/app/services/scene/`) and the spending limits as they stand.

- The roadmap's own build order already read *"rows 9, 11, 14, 15, 16, then 8 on a schedule"* — this directive confirms and sharpens it: **rows 15 (category editor), 16 (restore from backup) and 8 (use-up suggestions on a schedule) stay parked behind row 14.**
- Row 14 touches **metered provider calls**: its packet states the spend bound, and any real spend authority is a separate owner decision — and a 🟠/🔴 item, so it gets a second opinion before it reaches the owner (D-1024-10).
