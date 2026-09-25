SG-132 — Jina cost-ledger wiring: report (CHANGED — WIRED)

**Dispatch-ID:** SG-132 · **Verdict:** WIRED — every sent Jina search appends ONE `provider_call` row carrying the estimator's $0.0005 figure, the household month-boxed spend moves by it, and the served build proves it on a real search.

**Contract:** `Contract version: 0.37.0`. Source path `/home/andrei/storagegenie-contract/VERSION` (`0.37.0`); contract HEAD `1acd7730e5fa6de5b7403aacce71207e9946461d`; `RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` (matches installed). Recorded == published.
**BASE** (`origin/automation` requested; resolved at start): `af36fa25e0ff42224428c7be131fdb3012fa5c53` · **WORK_HEAD:** `4fde90ce49118c898f238c1c128d3b04bffb5e26` (product + tests). Evidence log `8245d574` + refusal-quote append `2792ff32`; report at the final tip.
**Model/effort (CO-78, from process args/provider metadata):** providerID `opencode-go`, modelID `deepseek-v4.1-flash` (provider metadata line `> build · deepseek-v4.1-flash`, from the runner's own UNTRACKED dispatch log `output/dispatch/SG-132.log`); **effort `high`** from process argv, pid `1698059`, `/proc/1698059/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie --variant high`.
**Spend:** real **$0.000000 USD**; **1 Jina live search of <=2** (~$0.0005 in token credits, not USD).
**Authoring date (metadata only):** 2026-09-25.

## (a) Issues / deviations / surprises
- **F-SG132-1 (vendor re-check: no movement).** Keyless GETs at `2026-09-25T20:07:36Z`: `https://jina.ai/api-dashboard/pricing/` HTTP 200, "starting from 10,000 tokens"; `https://dash.jina.ai/api/v1/product` HTTP 200, 17 active packs parsed to $0.016949-$1.00 per 1M — the SAME spread SG-124 recorded in F-SG124-3. The constant did **not** move against the live table, so **NOT BLOCKED**. The pre-existing caveat stands (0.05/1M is not the max pack rate); it is SG-124's, not introduced here.
- **F-SG132-2 (design call: the monthly gate did not exist on the enrich path).** The packet's success-delta ("a household at cap will see enrich refuse") is impossible at BASE: `api/v1/enrich.py` checked only the caller-fed per-press cap; `settings.sg_monthly_cap` was read only by `reader.run_ai_extraction`. I wired the missing gate: `monthly_cap_refusal(db, household_id)` = `reader._recorded_spend(...) + estimate_jina_search_cost()` vs `sg_monthly_cap`, refused 402 `monthly_cap_exceeded`. **No cap VALUE changed**; the gate is inert while `sg_monthly_cap is None` (the live `.env` default). The per-press gate is byte-unchanged.
- **F-SG132-3 (ordering call).** The ledger row must join a job (`provider_call -> job -> household_id`) or the month reader cannot see it, and the job did not exist until after the search. I create the enrichment Job first, then write the row through `snapshots.record_jina_search_call`. Consequence disclosed: a press that fails after the search keeps its job+cost row — correct, the search was already paid for.
- **F-SG132-4 (live search degraded, still charged).** The single live Jina request `https://s.jina.ai/Toothpaste` read-timed-out after 15 s (`transport: ReadTimeout`). The request **was sent**, so the floor estimate is charged (conservative). The live leg therefore proves the transport-degraded path; row + estimate + month delta + snapshot are all observed, so a second search was **not** run.
- **F-SG132-5 (pre-existing, out of scope).** `reader._recorded_spend` INNER-joins `Job`, so `provider_call` rows with `job_id IS NULL` (the chat/analytics/planning/synthesis writers) are invisible to the monthly cap. The live household's reader month sum is `0.0067005`; the sum over ALL its September rows is `0.010368` (the exact SG-131 figure) — the difference `0.003668` is the None-job rows. Reported, not fixed (outside this slice's scope; Jina rows are job-linked by design).
- **F-SG132-6 (pre-existing, external).** OpenFoodFacts returned HTTP 503 for several live queries during this slice (service-side page); unrelated to the change.
- **F-SG132-7 (carried, minor).** `AGENTS.md` still binds no `{{VENV}}`/`{{VTEST}}`/`{{EVIDENCE_DIR}}` (F-SG124-5); I used `backend/venv/bin/python` and committed mypy output in the verify log. No value invented.

## (b) Actions
- Changed paths (4): `backend/app/services/enrich/snapshots.py` (+`record_jina_search_call`, ledger identity constants), `backend/app/services/enrich/jina.py` (+`request_was_sent` pure predicate), `backend/app/api/v1/enrich.py` (+`monthly_cap_refusal`, monthly gate, job-first reorder, ledger call), new `backend/tests/test_sg132_jina_ledger_wiring.py` (7 offline tests). `synthesize.py` byte-untouched; `models/`+`alembic/` empty diff.
- Commits: work `4fde90c` (product + tests) · evidence `8245d57`, `2792ff3` · report final tip. Pushed `origin automation` (`af36fa2..8245d57`, then report tip).
- External/production effects: 1 Jina live search (sent, timed out; token credit ~$0.0005) · 1 backend image rebuild + exactly ONE recreate · live press rows left in place (identifiers in (c)). No USD-metered call on any path.
- Retry count 0; test-command count 7 (fail-pre, pass-post, targeted, candidate suite, base suite, base mypy, candidate mypy) + ruff; provider-call count 1; health delta unchanged.
- Highest-impact action: writing the Jina cost row through the real production writer joined to the enrichment job, so the existing month-boxed reader counts it with no reader change.

## (c) Verification
Every block runs against the immutable BASE worktree `/tmp/opencode/sg132-base` @ `af36fa2` or the candidate `4fde90c`; raw captures in `docs/worklogs/SG-132_verify.log` (committed `8245d57`, `2792ff3`).

Vendor re-check (figure + URL + time):
    capture 2026-09-25T20:07:36Z
    https://jina.ai/api-dashboard/pricing/ HTTP 200 -> "starting from 10,000 tokens"
    https://dash.jina.ai/api/v1/product HTTP 200 -> 17 packs, MIN 0.016949 MAX 1.00 USD/1M
    => unchanged vs SG-124 F-SG124-3; 0.05/1M still offered.

FAIL-then-PASS (both runs committed, PG-EV-09):
    FAIL-pre (BASE af36fa2, candidate test copied in): 5 failed, 2 passed in 1.35s
      test_jina_search_ledgers_estimate_and_moves_month_spend  -> assert 0 == 1  (no ledger row at base)
      test_degraded_jina_http_status_still_records_estimate    -> assert 0 == 1
      test_jina_spend_trips_enrich_monthly_refusal             -> assert 0.0 == 0.0005
      test_two_jina_searches_are_two_rows_and_double_spend     -> assert 0 == 2
      test_production_writer_prices_the_caller_token_bound     -> ImportError (new symbol absent)
    PASS-post (candidate 4fde90c): 7 passed in 1.27s
    Targeted (every jina-referencing file + new): 118 passed in 4.68s
    Suite candidate (33.99s/600s): 2 failed, 624 passed
    Suite base (36.24s/600s): 2 failed, 617 passed  -> same 2 reds (test_signals OCR/barcode decoder env), candidate delta +7.
    ruff check . -> All checks passed!   mypy app candidate == base: 41 errors in 9 files (checked 90); no touched file among them.

Empty diffs (quoted):
    git diff af36fa2..4fde90c -- backend/app/models backend/alembic | wc -l   -> 0
    git diff af36fa2..4fde90c -- backend/app/services/enrich/synthesize.py | wc -l   -> 0

Cap proof without a live burn (BEFORE/AFTER month total + refusal quoted):
    pre_seed_spend= 0.0
    row_cost= 0.0005 job_id= 01a0da3c-5c97-7fd2-9910-211ec847f67a
    post_seed_spend= 0.0005
    REFUSAL= monthly_cap_exceeded: estimated monthly cost 0.001000 exceeds monthly cap 0.0007 (0.000500 already recorded for this household)
    (offline: seed via production writer, read via the real reader, refuse via the real endpoint helper; zero live searches)

G3 rebuild + ONE recreate + verify (in order):
    BEFORE: container 6b606c6a… ; image 665d200ba183 ; provider_call=17 job=8 snapshot=2 candidate=7 ; spend=0.0067005 ; alembic 20260924_sg114_relation
    BUILD: BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend -> exit 0
    RECREATE (exactly one): docker compose up -d --no-deps --force-recreate backend -> Recreated/Started
    AFTER: container 40a117eaff0c54f7275a419ad39d417e962aaa6b89ccc274759888d31f60039d ; image ca29a3dc9a07 (665d200ba183 -> ca29a3dc9a07) ; RestartCount=0 (not the proof)
    in-container symbols record_jina_search_call/request_was_sent/monthly_cap_refusal all present; counts unchanged pre-press
    health exact-shape x6: {"status":"ok","db":"ok","storage":"ok"} HTTP 200
    gate: http:80 Host=storagegenie.dynv6.net -> 301 ; https:443 -> 401
    alembic head unchanged 20260924_sg114_relation

Live Jina search (1 of <=2) — request shape + row + figures:
    POST /v1/enrich/01a0a467-eb0e-7b83-a227-af122dc9268b?household_id=01a0a029-1477-7ca0-b200-bce78a96c679 -> 200
    request_url https://s.jina.ai/Toothpaste ; no_result_reason "transport: ReadTimeout: The read operation timed out"
    ledger row 01a0da39-6e4a-7b10-bbb4-b915d4dd4b75 provider=JinaSearch model=jina-search cost=0.0005 job_id=01a0da39-6e42-7193-b477-50a0043e58e4
    recorded_spend BEFORE 0.006700500000000001 -> AFTER 0.0072005 (delta ~0.0005)
    snapshot 01a0da39-6e49-72d2-8a7a-7f28961d2072 (source=jina) recorded
    press rows (PG-EV-06, left in place): Job 01a0da39-6e42-7193-b477-50a0043e58e4 · Candidate 01a0da39-6e4d-7210-b28d-380d8bd2ed92 · OFF snapshot 01a0da39-6e44-7302-8830-70ac0d4827e3 · Jina snapshot 01a0da39-6e49-72d2-8a7a-7f28961d2072 · provider_call 01a0da39-6e4a-7b10-bbb4-b915d4dd4b75
    end health {"status":"ok","db":"ok","storage":"ok"} HTTP 200 -> HEALTH: unchanged, OK

## INTENT
- INTENT: `snapshots.record_jina_search_call` writes one `provider_call` at `estimate_jina_search_cost()` for each sent Jina request; the check expects exactly one job-linked row of $0.0005 and `_recorded_spend` to move by it; the packet says "every Jina search path records one provider_call row carrying the estimator's figure" and "a Jina row recorded through the production writer is counted with no reader change". X/Y/Z agree.
- INTENT: the enrich monthly gate refuses when recorded spend + Jina floor crosses `sg_monthly_cap`; the check expects 402 `monthly_cap_exceeded`; the packet says "a household at cap will see enrich refuse". Agree (cap value unchanged; inert while None).
## TWINS
- Twin search for other Jina senders: whole-tree grep found exactly one production call site (`api/v1/enrich.py:191`); no twin left un-wired. Out-of-scope class: `_recorded_spend` ignores all `job_id IS NULL` provider rows (F-SG132-5); total such sites = 4 ledger writers (chat/planning/analytics/synthesize), reported, not fixed.

## Receipt (note on `refs/notes/storagegenie-coder-reports`) — pasted verbatim
Work committed and pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}` (packet's M20-corrected block). Note added on WORK_HEAD `4fde90c`, notes ref pushed, refspec fetched into the mapped name `refs/notes/sg132-verify` (a bare refspec would only rewrite `FETCH_HEAD`), `show` pasted:

```text
$ git notes --ref=refs/notes/storagegenie-coder-reports show 4fde90ce49118c898f238c1c128d3b04bffb5e26
error: no note found for object 4fde90ce49118c898f238c1c128d3b04bffb5e26.
pre_show_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-132 | Report: docs/worklogs/SG-132_report.md | Work-HEAD: 4fde90ce49118c898f238c1c128d3b04bffb5e26" 4fde90ce49118c898f238c1c128d3b04bffb5e26
add_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   de5f557..025eab3  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg132-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg132-verify
fetch_exit=0

$ git notes --ref=refs/notes/sg132-verify show 4fde90ce49118c898f238c1c128d3b04bffb5e26
Dispatch-ID: SG-132 | Report: docs/worklogs/SG-132_report.md | Work-HEAD: 4fde90ce49118c898f238c1c128d3b04bffb5e26
show_exit=0
```

The final tip is dual-annotated with the same message (note-anchor inoculation, SG-092 precedent). Final line: `note=yes`.

## Actual versus budget (units: seconds, live clock UTC)
- G0 vendor re-check: ~40s (keyless GETs) / 120s ordinary — within.
- G0 enumeration + caps + trace, G1 implementation, tests: ~5 min. 
- G2 fail-pre/pass-post/targeted + suites + ruff/mypy: ~150s (suites 33.99s + 36.24s) / 600s suite bound — within.
- G3 rebuild + recreate + served verify: ~90s (build 12.0s) / 600s.
- G4 worklog + report + receipt: ~6 min.
- No command killed or timed out. Real spend $0.000000 / $0 bound; Jina 1 / <=2 bound.

## UNCLEAR
- **FIRST READ:** whether the "enrich cap" the packet wanted on Jina spend was the month-boxed `_recorded_spend` cap or the caller-fed per-press cap. Read both paths; the per-press gate cannot see durable spend by construction, so I wired the monthly gate (F-SG132-2) and kept the per-press gate unchanged. Corrected against the packet's own success-delta wording ("consume the household's monthly cap").
- **DURING EXECUTION:** `_recorded_spend` returned 0.0067005 while the sum over all September rows was 0.010368 (SG-131's figure); investigated and found the reader inner-joins `Job`, excluding `job_id IS NULL` rows (F-SG132-5). Also, the live Jina request read-timed-out; I decided a sent attempt is chargeable and quoted it rather than burning a second search.
- **REMAINING:** the monthly cap is inert in live until `SG_MONTHLY_CAP` is set (a config value, out of scope); `_recorded_spend` still ignores None-job provider rows (F-SG132-5); the 0.05/1M constant is not the max pack rate (F-SG124-3, carried); OFF external 503s (F-SG132-6).
