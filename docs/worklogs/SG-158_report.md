SG-158 — Scene T1b: controlled renders via OpenRouter (≤$1) + D7 pick

**VERDICT: BLOCKED (partial ship, per packet's impossible-constraint rule): R1 — the
required `openai/gpt-5*` image slug — is UNROUTABLE under the owner account's
allowed-providers setting; G0 send path shipped and live-proven; D7 pick is
UNANSWERED (answering it would be inventing); total spend $0.000758925 ≤ $1;
production writes = 3 `provider_call` rows + 0 Evidence rows.**

Dispatch: SG-158 · Coder `opencode` · Model `opencode-go/deepseek-v4.1-flash` ·
Effort `max` (read first-hand from process arguments, never a system-prompt identity:
`/proc/1680653/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant max …`; engine
`bash /usr/local/lib/dispatch/run-coder SG-158`, pid 1680547).
Work dir / remote: `/home/andrei/StorageGenie` · `git@github.com:Andovol/StorageGenie.git`.
BASE ref requested `automation` → resolved `b118649` (tip at slice start; worktree clean).
WORK_HEAD: `04d26a7ffb9a4c7fbae82c0f303f6f50dac46505` (`04d26a7`) — the work
commit carrying the send path, the tests, the driver, all logs and this report;
the receipt note names it back and is read back from the remote below.
Contract echo: `0.44.1` (AGENTS.md recorded == `/home/andrei/storagegenie-contract/VERSION`);
`rules_check.sh` still exits 3 `G-L1 UNCHECKED` on this host (F-SG157-2 stands, re-measured).
Type: G0 send-path code+tests + G1 live renders. No migration, no restart, no
served-code change → no refresh (D145).

---

## (a) Issues / deviations / surprises

- **F-SG158-1 (BLOCKING, the reason for BLOCKED) — the account's allowed-providers
  setting rejects OpenAI.** R1's first live attempt returned HTTP 404 with the
  verbatim body: *"No allowed providers are available for the selected model.
  Providers serving inclusionai/ling-3.0-flash-vl-20260910: novita, deepinfra, but
  your account's allowed-providers setting permits only: xai, meta, seed, baidu,
  nvidia, xiaomi, minimax, stealth, deepseek, moonshotai, open-inference,
  google-ai-studio."* (`docs/worklogs/SG-158_render_R1.log`; ledger
  `01a12119-de97-7a71-803c-cd17fb237c7c`). The endpoints API re-confirms each
  `openai/gpt-5*` image model is served ONLY by OpenAI (blocked) and
  `google/gemini-3.1-flash-image` by "Google AI Studio" (permitted) + "Google"
  (blocked). **R1's constraint is impossible without an owner account change** —
  and an account policy is owner privilege: not routed around, reported. Per the
  packet, impossible constraint = STOP/BLOCKED.
- **F-SG158-2 (drift vs T0-PINNED) — ALL THREE T0 orchestrator candidates are
  unroutable**: `inclusionai/ling-3.0-flash-vl` (Novita/DeepInfra),
  `qwen/qwen3.7-flash` (Alibaba), `google/gemma-3-12b-it` (NextBit/DeepInfra) —
  none of those providers is in the account list. T0-pinned VALUES (prices/schema)
  are unchanged and MATCH my 2026-10-09 re-read; what the account contradicts is
  the *routability* premise. Substitute chosen by my own read under the packet's
  "pick one and justify, do not inherit blindly": `bytedance-seed/seed-1.6-flash`
  (provider Seed, permitted; vision+tools+tool_choice; $0.000000075/$0.0000003 —
  cheapest routable candidate; it was rank 7 on the SG-155/SG-157 list).
- **F-SG158-3 — R2's live 200 carried NO image URL.** The server-tool path with
  Seed executed (`server_tool_use_details.tool_calls_executed=2`,
  `image_tokens=0`) and billed **$0.000758925**, but the response contained no
  `imageUrl`/`image_url`/`data:image/` value my (tolerant, recursive) extractor
  could find → `image_url_missing`, no Evidence row. Raw-body persistence for
  2xx bodies was a gap in my first G0 draft; error bodies are now captured
  (`error_body`) and tested, 2xx bodies are not (a re-send to capture one would
  be a 4th billed render — refused). The dedicated Image API (`POST /api/v1/images`,
  `b64_json`, `input_references`) is documented as the alternative path; changing
  the frozen envelope was NOT this slice's grant.
- **Attempt accounting (packet's "no second chances / 4th render is STOP"):
  exactly 3 sends left the machine** — R1×2 (both policy 404, `cost=None`,
  $0.00) + R2×1 (billed, no image). No 4th send was made; R3 was NOT run because
  with no contest there is no winner to confirm and no pick to carry.
- **Publish-before-bound HONORED, narrowly:** reports commit pushed at
  14:44:00Z = elapsed 940s and the receipt note read back at 14:44:12Z = elapsed
  952s, both inside the 1050s half-bound (`RUN_BUDGET_S=2100`, lane start
  14:28:20Z). The live-policy investigation consumed most of the margin.
- **Coupled-test update, named:** `tests/test_privacy_audit.py` (SG-087's sender
  inventory) pinned "one send site"; SG-158's owner-approved sender adds one
  httpx carrier and two `client.post` lines. The two pins were extended and the
  docstring names **SG-158** as the approving slice (CO-38). No other test changed.
- No Authorization leakage: 0 `Bearer`/`Authorization` strings in any committed
  log; the key is resolved at send time and never returned, stored or logged
  (asserted by tests). No secret file copied (CO-100; the live container was
  handed `.env` via `--env-file`, values never echoed).
- `PG-EV-09` note: the 2 new reds the suite showed first (privacy audit) were
  fixed in-slice by the pin update above; the 2 standing `test_signals` reds are
  the known environment class (pyzbar/libzbar + tesseract absent), same as base.

## (b) Actions

Changed paths (work commit W): `backend/app/services/scene/openrouter.py` (send
path: `SceneSpendAuthority`, `guard_render_spend`, `extract_image_url`,
`download`, `record_scene_call`, `store_scene_render_evidence`, `render_scene`);
`backend/tests/test_sg158_scene_render.py` (new, 15 tests);
`backend/scripts/sg158_render.py` (new, one-render-per-invocation driver);
`backend/tests/test_privacy_audit.py` (2 pins + docstring);
`docs/worklogs/SG-158_failpre.log`, `SG-158_passpost.log`, `SG-158_verify.log`,
`SG-158_render_R1.log`, `SG-158_render_R2.log`, `SG-158.log`, this report.
Commits/push/receipt: see Receipt section (WORK_HEAD + note read back on the
remote). External effects: 3 OpenRouter POSTs (2×HTTP 404 policy, 1×HTTP 200
billed) from the production image via `docker run --rm` (repo mounted read-only,
live `/data/db` + `storagegenie_storage_data` mounted; no served container
touched, no restart/build). Production writes: exactly **3 `provider_call`
rows, 0 `evidence` rows, 0 other rows** — read back below. Provider-call count:
3 sends, 1 billed. Retries: 0 (one R1 diagnostic re-send, disclosed). Test
commands: 6. Health section: not applicable (no served-code change, no restart);
the live container's own `/v1/health` was not probed (out of scope; the runner
owns it). Durations (UTC clock): lane start 14:28:20Z; G0 write+tests
14:29–14:36; R1/R2 live legs 14:37–14:40; suite+logs+report 14:40–14:44; work
commit 14:44:00Z (elapsed 940s); receipt note on remote 14:44:12Z (elapsed
952s). Only command > 60s: none (full suite 32.2s; slowest render 15.9s).

## (c) Verification

**A1 — fail-pre → pass-post, both committed** (`CO-20(c)` isolated base worktree
`/tmp/opencode/sg158-base` at `b118649`, candidate test copied in; then candidate):

    SG-158_failpre.log  (base b118649 + candidate test):
    E   AttributeError: module 'app.services.scene.openrouter' has no attribute 'SceneSpendAuthority'
    Error during collection — 1 error in 0.34s
    SG-158_passpost.log (candidate W):
    27 passed in 0.44s    (15 new + 12 SG-155 envelope re-assertions, offline, $0)

**A5 — suite / ruff / mypy as established** (`SG-158_verify.log`, verbatim tail):

    ruff: All checks passed!  (ruff_exit=0)
    mypy: Found 41 errors in 9 files (checked 92 source files)  — none in app/services/scene (touched-file clean; same 41/9 debt snapshot as SG-157)
    suite: 2 failed, 676 passed  (the 2 are test_signals environment reds, same class as base; +15 new tests passed)

**A2 — renders, per-render accounting, ≤$1, 0 leaks.** Live reads (read-only SQL
against `/data/db/storagegenie.db`; ledger ids quoted; `SG-158_render_R*.log`):

    R1a 2026-10-09 14:37:16  ledger 01a12118-ce4b-79b3-88f8-c289e18d15a2  model inclusionai/ling-3.0-flash-vl  404  cost=null
    R1b 2026-10-09 14:38:25  ledger 01a12119-de97-7a71-803c-cd17fb237c7c  model inclusionai/ling-3.0-flash-vl  404  cost=null (body: account allowed-providers)
    R2  2026-10-09 14:39:55  ledger 01a1211b-3ae2-7ec2-aa57-4e1a8219c8f8  model bytedance-seed/seed-1.6-flash  200  cost=0.000758925 error=image_url_missing
    Evidence rows (source_kind='scene_render'): 0   (evidence total unchanged 13)
    TOTAL SPEND: $0.000758925 ≤ $1.00 cap; worst-case guards: 0.30 per render, sequential (0+0.30, 0+0.30, 0+0.30 ≤ 1.0)
    Authorization leaks: 0 (grep 'Bearer|Authorization' over both render logs = 0; code adds it at send time only; test-asserted)

**A3 — D7 pick: UNANSWERED, deliberately.** No per-render judgment table is
possible for R1 (never rendered) and R2 produced no stored image. **No pick is
invented** (G-A9). Report-only recommendation (not a pick): under the current
account policy the only routable image family is Google AI Studio-served
(`google/gemini-3.1-flash-image` / `-flash-lite-image` / `nano-banana-2.1`); the
owner can widen allowed providers (add `openai`, `google`) or accept a
Google-only D7. T0-PINNED values unchanged; the drift is routability (F-SG158-2).

**A4 — production writes exactly as measured, both directions (PG-IC-08).**
`provider_call` where provider='openrouter': 3 rows (above). No other table
written; no UPDATE/DELETE anywhere; no file written into the storage volume
(0 Evidence rows). Report + receipt: see Receipt section (remote read-back).

**Guards invoked:** `PG-EV-04` (all tests offline, scripted transports; live
legs are the 3 authorized sends only) · `PG-EV-06` (each result persisted at
return; ids quoted) · `PG-EV-09` (coupled privacy pins updated in-slice and
named; no weakening) · `PG-EV-14` (report-and-leave; nothing updated/deleted) ·
`PG-SC-03` (missing key refuses loudly before send; tested) · `PG-IC-01` (no
blanket bans; only named writes) · `PG-IC-03` (stop precedence: policy 404 →
BLOCKED, not workaround) · `PG-IC-07` (live UTC clock at each step; logs) ·
`PG-IC-08` (counts in both directions, above) · `PG-IC-09` (every packet premise
re-verified; two contradicted live → F-SG158-1/2) · `PG-PR-10` (3 append-only
ledger rows; storage volume untouched).

**INTENT lines (behaviour-changing):**
`INTENT: code adds a paid send path that refuses without the explicit grant, ledgers every sent request, stores the downloaded image and adds Authorization only at send; the checks expect exactly those outcomes offline via scripted transports; the approved packet says "add the send path: key at send time only, POST, immediate download …, Evidence row … + ledger row per billed call INCLUDING billed failures" (G0) — they agree.`
Vacuity check (loud): the fail-pre is a real collection error on base; the
pass-post exercises the real `render_scene` through real SQLite; the 3 live
sends really left the machine (ledger rows + 404 body + 200 usage on record);
nothing passed by empty set — the Evidence count is honestly 0 and the D7 pick
is honestly absent.

## Receipt

Mechanism: note on `refs/notes/storagegenie-coder-reports`. Work commit
`04d26a7` pushed at 14:44:00Z (elapsed 940s of 2100s; half-bound 1050s); the
note was published on it and read back from the **remote** at 14:44:12Z
(elapsed 952s — publish-before-bound honored). Verbatim transcript:

    $ git push origin automation
       b118649..04d26a7  automation -> automation
    $ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-158 | Report: docs/worklogs/SG-158_report.md | Work-HEAD: 04d26a7" 04d26a7
    $ git push origin refs/notes/storagegenie-coder-reports
       57af1b1..ba7cdb1  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg158-fetched
       * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg158-fetched
    $ git notes --ref=refs/notes/sg158-fetched show 04d26a7
    Dispatch-ID: SG-158 | Report: docs/worklogs/SG-158_report.md | Work-HEAD: 04d26a7
    note_show_exit=0

`note=yes` — read back from the remote (mapped fetch), not the local store.
This receipt-evidence commit (the tip carrying this section) is annotated with
the same note body after it is committed (dual annotation, SG-092/SG-154/SG-157
precedent). Production writes this slice: 3 `provider_call` rows, 0 Evidence
rows, 0 others; spend $0.000758925.

## UNCLEAR

- **FIRST READ:** whether "one `openai/gpt-5*` slug" was a hard G1 constraint or
  a hypothesis adjustable on live evidence. Resolved: hard constraint →
  impossible under the account policy → BLOCKED, per the packet's own rule; the
  alternative (inventing a substitute slug) is explicitly banned (A3/G-A9).
- **DURING EXECUTION:** whether R1's 404 was a malformed envelope (my bug) or an
  account policy; resolved by capturing the response body on a second identical
  send (404 → body names the account allowed-providers setting; $0, no
  generation). Also whether R2's empty-image 200 meant "no image generated" or
  "URL shape unparsed"; unresolved — the 2xx body was not persisted and a third
  send would be a 4th render (STOP), so it ships as `image_url_missing` with
  the full `usage` on record.
- **REMAINING:** owner decision on the account's allowed-providers setting (add
  `openai`/`google` to unblock R1 and the T0 orchestrators, or accept a
  Google-only D7); after that decision, a re-dispatch can run R1/R2/R3 and
  produce the D7 pick. Also owed: 2xx raw-body persistence (or dedicated Image
  API path) if the server-tool response shape is to be pinned.
