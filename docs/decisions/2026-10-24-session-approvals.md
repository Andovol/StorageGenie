# 2026-10-24 — Session approvals (D-1024-1 … D-1024-16)

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

## D-1024-13 — The Miso Soup row: `read` is not `dismissed`, and the missing write is carried to SG-244

Recorded 2026-10-24 after the SG-241 audit (D-1024-11 correction). **The owner does not re-decide this** — they already decided it in D-1024-11 (*"W2 - dismiss."*); this records what actually happened to that decision and where the remainder sits.

**What happened.** The owner answered *"W2 - dismiss"* and the standing close-deploy rider (SG-241) was dispatched to perform it through the app's own route. **The rider issued no write**, because when it started (2026-10-24T16:14:53Z) the row was **already `read`** (`updated_at 2026-10-24 15:21:24Z`, ~13 minutes before that unit began) — and **my own SG-241 packet said *"if the row is already `dismissed` or `read`, make no write and treat the end state as reached"**. That clause was wrong: `read` is **not** the state the owner named; `dismissed` is.

- The rider executed my clause literally, proved that no write happened (zero POST/PUT/PATCH/DELETE lines in the container's access log; `updated_at` identical before and after), and reported the deviation as **I1** instead of dressing `unread_count 0` up as the packet's expected `1`. That is the behaviour the contract wants — the defect was in my packet, not in the execution.
- **Who set it to `read` cannot be established from the system**: `backend/app/api/v1/reminders.py:93-104` writes `status` and commits — **no actor column, no audit row** (backlog **W4**). The timing is consistent with the owner's own click on the Expiry page ~1 minute after my message told them *"you can also click Dismiss yourself right now"* (the Read button precedes Dismiss in the DOM, `frontend/src/routes/ExpiryPage.tsx:200`/`:212`), but **the data cannot confirm the actor** — it is an inference from timing, labelled as such.
- **The practical difference is small but real**: `read` and `dismissed` both hide the row from the Expiry page's unread block (`ExpiryPage.tsx:126` renders unread rows only) and both are superseded by tomorrow's new row (`record_due` is keyed by `(asset_id, as_of_day)`, so the 25th/26th/27th rows arrive either way). What differs is the **state the owner asked for**: `dismissed` is a terminal state in the app's transition table (`LEGAL_TRANSITIONS`), `read` is not.

**Do:** **SG-244** (`docs/packets/SG-244-dismiss-the-miso-soup-row.md`) performs the one remaining authorized write — `POST /v1/reminders/{id}/dismiss` on that row, exactly once, with the pre-state quoted before it and the post-state after, and no other write. It is a **carry of D-1024-11, not a new decision**: the owner already authorised this write and it was not performed because of a clause in my packet.

**Standing rule this session adds:** a rider's end-state branch must name **the transition that reaches the requested state**, and must not treat *"the row is in some other non-unread state"* as the end state. And a rider's closing advice must never name a UI affordance that does not exist for the row's state (SG-241's report told the owner to click Dismiss on the Expiry page — the page renders unread rows only, so that button does not exist for a `read` row).
## D-1024-14 — Report to the owner after each completed slice

Owner, 2026-10-24 (this chat), verbatim: *"I want you to keep me informed after each completed slice."*

**Do:** every slice that reaches a rating sends the owner **one report as soon as it is rated** — what ran, what
landed, the issues table, and the decisions that need them — instead of batching the news until the session
closes.

**Why this is recorded here:** it is a standing directive about how the Architect works with this owner, not a
one-off request for this session's report, so it belongs in the project's record (G-O4) and outlives the
session.

**What it does not change:** the three-section report shape (STATUS · ISSUES & BUGS · DECISIONS FOR YOU); the
rule that a 🟠/🴠 item reaches the owner only with its second-opinion line; the rule that unrated or blocked
work stops the deploy instead of shipping silently; and the rule that a slice the owner is waiting on is
reported by its result, not by a plan.

**One addition the owner asked for in the same breath — status, roadmap progress and what is next.** Each
post-slice report also states the roadmap position (which rows are built, which are partly built, which are
missing) so the owner never has to ask where the work stands.
## D-1024-15 — No local models on the server

Owner, 2026-10-24 (this chat), verbatim: *"We will not have local models on the server."*

**Do:** the live server (`87.106.66.242`) will never run a local model. Roadmap row 14's "local option" therefore
means the **no-model** local path — the deterministic provider double already in the registry
(`backend/app/services/providers/reader.py:96`) and the local OCR / barcode observation path
(`backend/app/services/signals.py:102-109`, `:205-245`) — and **not** a local model server, not an on-demand
model sidecar, and not a model downloaded to the host.

**What this closes.** D-R14-b's **L2 branch is closed by the owner's decision, not deferred**. The review's L2
item — a local model served on the live host, with its host-rule change, its stated memory budget and a
re-measure of the shared 7.7 GiB box — **does not go to the owner at all**, and no slice may plan for it.
The review's **L3 survives** (local as the *fallback destination*, reached on transport/outage classes only),
with its two constraints: a local landing must never present a fabricated reading (`fake` returns `fake-item`,
`fake.py:63`), and `invalid_json` must surface rather than be absorbed by a fixture
(`RETRYABLE_ERRORS`, `providers/reader.py:61-63`).

**Why it is recorded durably (G-O4):** it is a standing product decision, not a question — it removes a branch
that was in front of the owner, and it changes what the row-14 stage may contain.

**What this does not change.** The review rule stands: the decisions that ride on this ruling still need their
second-opinion line before they reach the owner — which is why the owner asked for a second opinion on all of
them, and one runs (SG-248 blind, SG-249 critique) before they come back.

**Scope.** The ruling is about **the live server** — the only server this project runs on. It says nothing about
a developer's own machine, and it does not forbid a local model on a different host if the owner ever wants one.
## D-1024-16 — Model decisions belong to the owner: the Architect recommends, the owner decides

Owner, 2026-10-24 (this chat), verbatim: *"Don't make model decisions without asking me first."*

**Do:** the Architect may **recommend**; the owner **decides**. Anything that chooses an AI model or an AI provider
for the product — the second photo reader's vendor, the vision model id and the model whitelist, whether any path
runs a model at all — is an owner decision, and it reaches the owner as an item **with its second-opinion line**
before anything is built.

**What this changes in practice.**

- The Architect's picks are **recommendations**, and the records must read that way. A pick inside a review packet
  or an architect record is the object the review attacks — never a decision taken, and never written as one.
- **The review protocol is unchanged.** `SECOND_OPINION.md` requires the Architect's pick to be in the repository
  before Phase B — that is what makes the blindness work — so the pick stays, **labelled as a recommendation**.
  The owner asked for a second opinion on these decisions and then to be brought them; the review informs the
  owner's choice, it does not make it.
- **The slice-envelope models are already the owner's standing setting** (`AGENTS.md`: every trigger states
  `model=opencode-go/deepseek-v4.1-flash effort=max`; the second-opinion reviewer is the contract's configured
  `opencode-go/muse-spark-1.3-contributor`, which is never the Architect's own model). So **no new question
  arises** for a dispatch that follows the standing policy; the owner is asked **only if a dispatch would deviate**
  from it.
- The owner's earlier ruling stands and is not re-opened: **no local models on the server** (D-1024-15).

**Where it bites now.** D-R14-a (the second provider) and the vision model id are the owner's; the four row-14
items go to the owner as four separate items after the round-2 review (SG-249), each with its review line.

**Scope note.** The rule is read in the strong sense — it covers **every** model or provider choice for the
product, and it also covers a change to the model that runs a slice. If the owner meant only the product's AI
models, the standing dispatch policy continues unchanged either way.
## D-1024-17 — D1: no fallback yet

Owner, 2026-10-24 (this chat), verbatim: *"D1 - no fallback yet."*

**Do:** roadmap row 14's **fallback is not built now**. No second photo reader, no fallback wiring, no provider or
fallback id in the settings surface, no shared-base extraction (it exists only to serve a second adapter), no
second key, no vendor choice, no vision model id. The router's fallback branch stays exactly as it is — built,
tested, and unreachable in production because no call site sets `fallback_id` — which is precisely "not yet".

**What this defers to `docs/backlog.md` (W6), each with the owner's word as its trigger:** the second photo
reader and its own rate table and estimator; the fallback wiring at the five call sites (four router sites plus
the `services/enrich/synthesize.py:276-285` bypass); the shared base (the measured 119 vendor-neutral lines); the
provider/fallback settings surface; the ledger reader's provider filter; the gateway test's parity with the
production retryable classes; and the vision model id.

**What this does not stop:** the cost-logging work of D-1024-19, and W1 (the two always-red host signal tests) —
the app's existing local signals feature is untouched (D-1024-18).

## D-1024-18 — D2: cloud only — no built-in reader, no local reader

Owner, 2026-10-24 (this chat), verbatim: *"D2 - No built in or local reader, only cloud."*

**Do:** roadmap row 14's **"local option" is not built**. No local provider, no local fallback destination, and no
local reader added to the product. Together with D-1024-15 (**no local models on the server**), the path that
*proposes items* is **cloud only**.

**Scope, stated plainly, because it matters.** This decision is about **what we build**. The app's **existing**
local signals feature — roadmap row 3, "read labels automatically": the barcode and OCR observations read from
the stored photo in `backend/app/services/signals.py` — is **not removed by it**, because that path reads two
things a cloud model cannot: the photo's own **date** (EXIF) and, just as important, it is where the image's
**GPS is stripped** (`backend/app/services/providers/redaction.py:16-21`; the signal path reads the stored file).
A privacy property that depends on the image never carrying location data off the machine does not belong to a
model. **If the owner means the existing reader also goes, say so** — that is a separate, larger product change
and it would also dissolve W1.

**Consequences:** the blueprint's local-fallback language is **amended** to the no-model, no-local reading
(`inception/generic_asset_catalog_expiry_tracker_blueprint.md:318`, `:533-539`); row 14's "local" half is closed;
`fallback_id` may never resolve to a local provider.

## D-1024-19 — D3: stop predicting costs, log the actual costs

Owner, 2026-10-24 (this chat), verbatim: *"D3 - Stop carrying about predicting costs, just log the costs and thats
it."*

**Do:** the app stops **predicting** what a call will cost and stops **refusing a call on a prediction**. It
records and logs what each call **actually** cost.

**Removed**

- the pre-call cost estimate — `providers/opencode_go.py:151-164` (`estimate_call_cost`), `:244-250`
  (`estimate_cost`);
- the router's cost budget and its pre-call refusal — `providers/router.py:35` (`cost_budget`), `:52-74`
  (`execute(..., estimated_cost=…)`, the refusal at `:71-74`);
- the reader's estimate plumbing — `providers/reader.py:233-242` (`_estimate_call`), `:480-484`;
- the monthly cap and the ledger reader that fed it — `providers/reader.py:293-306` (`_recorded_spend`),
  `:486-497`;
- the per-job cap and the adapter's duplicate budget guards — `providers/opencode_go.py:298-309`, `:361-372`;
- the `estimated_cost` parameter of the provider protocol — `providers/protocols.py:28-37`;
- the two cap settings — `backend/app/config.py:48-49` (`sg_per_job_cap`, `sg_monthly_cap`) and their place in
  the settings surface — `backend/app/api/v1/settings.py:29-36`.

**Kept**

- the **consent gate** — `providers/reader.py:108-114`, `config.py:50`: that is the owner's switch for AI use,
  not a cost prediction;
- the **actual** post-call cost — computed from the response's real token usage
  (`providers/opencode_go.py:139-148`, `compute_cost`) and recorded in the `provider_call` ledger
  (`providers/reader.py:208-230`);
- the **scene** feature's own cap — `config.py:45-47`, `services/scene/openrouter.py:288-296`: a different
  feature's limit, enforced against **actual** reported cost, not a prediction, and therefore outside this
  decision.

**Added** — one INFO line per provider call carrying the **actual** cost and the token counts, so the cost is
visible in the server log without a query.

**No schema change, no migration** — the ledger table and its columns stay as they are.

**Why this is a simplification rather than a loss:** both caps have been `None` — off — since the owner's own
"no caps at first" (2026-09-11, F2), so the machinery bound nothing; what the app keeps is a truthful record of
what each call cost, and the budget conversation moves to the owner, where it belongs.

**What it does not touch:** the fallback work (deferred, D-1024-17), the local reader (D-1024-18), and the
app's local signals feature.

## The three answers together — what roadmap row 14 now is

Row 14's original scope ("Second AI provider and local option with fallback and spending limits") reduces to
**one small slice**: stop predicting costs, keep and complete the actual-cost record, and log it. The second
provider, the fallback and the local option are **deferred by the owner** (D-1024-17, D-1024-18), and the
blueprint is amended to say so. The **next slice is therefore a slimming slice, not a building slice** — and the
money the review spent on caps and estimates bought exactly this: a smaller row.

**W1 is untouched by all three answers** — the two always-red host signal tests belong to the app's existing
local signals feature (roadmap row 3), which D-1024-18 does not remove. W1 stays open as it was.
