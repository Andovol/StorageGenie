SG-173 — Live review-to-catalog story walk before the approved repair chain

**RESULT: DIAGNOSIS COMPLETE. All four suspected defects measured; two live hypotheses fully
confirmed, one confirmed with a corrected root cause, one disproved as an ordering defect (real gap is
visibility). Product tree unchanged, running service unchanged, production writes NONE, tree UNSERVED.**

**Dispatch identity (`PB-4`, read from `/proc/674769/cmdline`, never a system-prompt line):**
`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash
--variant max` (wrapper `bash /usr/local/lib/dispatch/run-coder SG-173`) → **model
`opencode-go/deepseek-v4.1-flash`, effort `max`** (D-1012-15). Work dir `/home/andrei/StorageGenie` ·
origin `git@github.com:Andovol/StorageGenie.git`. **Authoring-date metadata 2026-10-12; live UTC clock
throughout.**

**BASE ref requested:** `automation` → **resolved commit `dd35165e8b363a93c1d20ae4ccdc302d39c07778`**
(== local HEAD at start == `origin/automation`; worktree clean at start). **WORK_HEAD:
`901caf324c8421e5c276b3132ed4265bcf948c78`** (diagnostic-artifacts commit: probe + all observation
logs). **Report commit:** the commit carrying this file (noted on the notes ref after publication).

**Contract echo (verbatim + source):** `/home/andrei/storagegenie-contract/VERSION` = **`0.46.0`**;
contract HEAD `925cb575c0ef0e1c5a15b6112041a270c2dbd730`; `git ls-remote --tags origin
'refs/tags/contract-v0.46.0*'` (re-verified this slice) → annotated tag `4c23869c…` peels to
`925cb575…`; `RULES.md` sha256 `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef` ==
`RULES.sha256` == the installed `487841B1…` payload recorded for 0.46.0. **Recorded == published ==
host. Zero contract delta.** `bash /home/andrei/storagegenie-contract/rules_check.sh` exits **3**,
re-measured (transcript in `SG-173_live_logs.log`):

    G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract
    G-L5 UNCHECKED gh-unauthenticated
    G-L7 UNCHECKED gh-unauthenticated
    G-L6 BYTES /home/andrei/.codex/AGENTS.md 2275
    G-L6 BYTES /home/andrei/.config/opencode/AGENTS.md 1933
    G-L6 BYTES total[codex]=2275 unseen=architect-layer,state-file,other-ritual-files
    G-L6 BYTES total[opencode]=1933 unseen=architect-layer,state-file,other-ritual-files

`G-L1 UNCHECKED` is the **local tag-ref shape** — the checkout sits *at* the tag's peeled commit
`925cb575…` but carries no local tag object (tag lives on the Launcher contract remote) — **not**
payload drift, per `F-SG168-4`/`F-SG170-5`/`F-SG171-1`/`F-SG172-3`; the contract bytes are
independently verified above. L5/L7 are the unauthenticated `gh` on this host. Delta vs SG-172's
4-line quote: the current script additionally prints the two `G-L6 BYTES total[…]` summary lines —
same 0.46.0 payload, richer output shape, **same exit 3, no version delta** (`F-SG173-6`). No host
configuration was repaired or touched.

---

## (a) Findings / premise corrections (reported, not bent — `PB-1`)

- **F-SG173-1 — `.rules-cache/` is still absent from the workspace** (AGENTS.md Loading line
  instructs `bash .rules-cache/rules_check.sh`). Ran from the host contract path; same shape as
  `F-SG172-3`, re-measured. Not a contract drift.
- **F-SG173-2 (tooling) — the backend test interpreter is `backend/venv`, not the repo-root `venv`.**
  Root `venv` lacks `pillow_heif` (app import fails); `backend/venv/bin/python -m pytest` is the
  precedent from `SG-169_passpost_backend.log`. Reported so the runner's environment is known
  (related to the standing `F-SG144-1` venv follow-up).
- **F-SG173-3 — there is no `backend/tests/conftest.py`; fixtures are defined per test module.**
  The defining modules used/reused: `test_candidate_read.py::candidate_read_db` (candidate read +
  job run helper pattern), `test_plugin_expiry.py::plugin_db` (classification/manual entry),
  `test_sg107_expiry_engine.py::engine_db` (expiry engine, boundary table, no-write proof). The
  disposable probe mirrors those fixtures rather than mutating them (no shared-fixture mutation).
- **F-SG173-4 (premise refinement) — `ExpiryEntryForm` has TWO hosts, not one.**
  `ReviewPage.tsx:56` (post-Accept) **and** `AssetDetailPage.tsx:403`. Both render the form; neither
  can succeed before classification (`422`), so the missing-classification wall is present on both
  surfaces. `CatalogPage.tsx` exists as the packet expected; `types.ts`/`client.ts` matched.
- **F-SG173-5 — headless Chrome cannot start under the lane sandbox with the default `$HOME`.**
  `/home/andrei` is read-only here (the wrapper's `mkdir ~/.local/share/applications` fails;
  chrome aborts SIGTRAP). Worked around **inside the slice** by `HOME=/tmp/opencode/chromehome
  XDG_DATA_HOME=… --user-data-dir=/tmp/…`; Chrome 150 then rendered the real SPA read-only. The
  browser was therefore available; the limitation removed, reported transparently.
- **F-SG173-6 — rules_check output shape vs SG-172 quote** (two extra `G-L6 BYTES total[…]` lines,
  same exit 3): explained above; not a contract delta.
- **F-SG173-7 (premise correction to repair item 4) — expiry *ordering* is NOT defective.** The
  engine's ordering is deterministic and correct: accepted-only rows sorted `(days_remaining asc,
  asset_id)`, expired first; unresolved separated and reason-tagged
  (`test_sg107_expiry_engine.py` boundary/ordering tests + probe T3 re-measured). The real gap is
  **visibility**: an ACTIVE asset with **no accepted classification** appears in *neither* `rows`
  *nor* `unresolved_rows` (probe T3: invisible; only the analytics *Uncategorized* count sees it).
  The fourth repair should therefore preserve ordering and scope to explicit missing/unresolved
  handling, not re-sort anything.
- **F-SG173-8 (live data inventory, sanitized)** — the live story was walked by the owner and the
  data shows the aftermath: 10 candidates (4 proposed / 6 edited), **8 review tasks — ALL resolved,
  zero open**, 7 ACTIVE assets with **0 accepted classifications, 0 accepted expiry assertions, 0
  `needs_evidence` assertions**, 18 evidence rows. Audit: **8/8 resolutions are bare**
  (`actor=api`, `after_json {"status": "resolved", "resolution": {}}`); **zero `expiry.manual_entry`
  audit events exist — the manual-entry route has never been invoked live**; **zero
  `plugin.assertion.write` events**. An earlier-resolution `candidate.multi_item` task is among the
  8 (one candidate had 2 embedded ids).

---

## G1 — Served story walk: first failed transition

**Serving identity re-observed live (not inherited):** container
`91a073730e495dae222f179710879199237398040926adbbf8c57602fe97ef3f`, image
`sha256:9064d2ced325220a4e7a2a16670cf678651e142c032c840e6e1e2d059c0cd4bf` (expected prefix
`9064d2ce` — confirmed), started `2026-10-12T20:03:58Z`, RestartCount 0, healthy; served bundle
`assets/index-CYyuxefG.js` sha256 `1b4680a0…` == SG-172's deployed record; the served JS contains
`review_task_ids` ×2, the blocked sentence ×2, the Inbox affordance ×1 — the SG-171/172 gating code
is the code being observed. All observations below exercised **this image**; GET-only (zero mutating
requests sent by SG-173; server log lines quoted in `SG-173_live_logs.log`).

| # | transition | entry state (live) | visible action / route | prerequisite | observable result | status |
|---|---|---|---|---|---|---|
| 1 | capture/import → candidate | 18 evidence, 10 candidates, 9 jobs | Inbox → import jobs (`GET /v1/jobs`, `/v1/imports/{id}`) | job pipeline | candidates exist in `proposed`/`edited`; Inbox renders | **OBSERVED LIVE** (data + DOM) |
| 2 | candidate Review | 7/10 candidates embed 1–2 `review_task_ids`; every embedded task is resolved; live open tasks = 0 | `/review/{id}` → `GET /v1/candidates/{id}` | household id | blocked sentence rendered ×1, **Accept disabled**, Inbox link rendered — a state that cannot be cleared because… | **OBSERVED LIVE** |
| 3 | task completion from Inbox | all 8 tasks resolved (7 `expiry.manual_entry`, 1 `candidate.multi_item`), audit = 8× bare resolve | Inbox "Resolve" → `POST /v1/review-tasks/{id}/resolve` | open task | the Inbox default view renders **"No open review tasks."** — the page's advertised remedy for transition 2 does not exist; the live data shows resolutions happened **without any completion data** | **OBSERVED LIVE** (end state + audit); the act itself is a write and was **not** reproduced live (**limitation**, isolated repro in G2) |
| 4 | Accept | Accept rendered disabled on stale candidates; one live candidate already carries a committed `asset_id` | Review → `POST /v1/candidates/{id}/decision` | zero open tasks (server check) + client `review_task_ids` empty (stale) | live write forbidden — not performed; **OBSERVED ISOLATED**: 409 with open task (control) → resolve → POST 200 (server allows) while the GET still returns the stale ids and the served client keeps the button disabled | OBSERVED LIVE (render) + OBSERVED ISOLATED (route) |
| 5 | classification | every live asset has 0 accepted classifications; **no frontend caller exists** (grep: `classify`/`classification` appears only as copy text in `ExpiryPage`/`ChatPage`; `client.ts` has no classification request) | none in UI | — | **stop point**: nothing calls `POST /v1/plugins/expiry-tracker/assets/{id}/classification` | **OBSERVED LIVE (absence)**; consequence reproduced isolated (T2 422; T3/T4 with classification 200) |
| 6 | expiry entry | candidate-B's Review page renders the form (`expiry-state: needs_evidence`), still blocked | `ExpiryEntryForm` → `POST …/assets/{id}/expiry` (Review page **and** asset detail) | accepted classification (`store_manual_expiry` gate, `expiry_tracker.py:501-506`) | live submit is a write — not performed (**limitation**); **OBSERVED ISOLATED**: without classification → `422 "Asset must be classified before manual expiry entry"`; with classification → 200 + task resolved with data | OBSERVED LIVE (render) + OBSERVED ISOLATED |
| 7 | Catalog / expiry visibility | `/expiry` live: rows 0, unresolved 0, "No expiry items for this household", Uncategorized **7** | `GET /v1/plugins/expiry-tracker/status` (+ analytics) | accepted classification + accepted date | the catalog serves assets, but the expiry stream is empty because no classification exists; unclassified assets are invisible even as unresolved | **OBSERVED LIVE** |

**First failed transition.** For the *current live population* the first wall is in transition 2→3:
Review says acceptance is blocked "until the open review task(s) are resolved", but every task is
already resolved (Inbox: "No open review tasks.") and the page keeps the stale block forever — a
dead-end the user cannot clear. For a *fresh* story walk, immediately after clearing that wall the
first data wall is transition 5: Accept succeeds, then the manual-expiry form on Review/Asset detail
**cannot succeed** because classification has no UI anywhere ("Asset must be classified before manual
expiry entry"). Both are exact stop points, both measured; neither is inferred from source.

**Live reproductions that needed a write were stopped at the boundary** — accept-click, resolve-click,
expiry submit. The story is therefore *not* claimed as a fully passed live walk; those legs are
covered by the isolated reproduction (G2) and the live render/end-state evidence above.

**Contemporaneous server logs** (`SG-173_live_logs.log`, sanitized): the slice's GETs
(`/v1/candidates/<uuid>`, `/v1/review-tasks`, `/v1/plugins/expiry-tracker/status`, `/v1/assets…`) all
`200 OK`; **no mutating request on the story routes appears in the current container's logs** — the
owner's walk (task `updated_at` 19:40–19:52) predates the 20:03:58 recreate, which is why the audit
table, not the logs, is the discriminator for the historical resolves.

---

## G2 — Isolated story exercise (disposable SQLite; synthetic evidence)

**Command (actual):**
`cd /home/andrei/StorageGenie/backend && ../backend/venv/bin/python docs/worklogs/SG-173_probe.py`
— full output in `SG-173_probe_out.log`; probe source in `SG-173_probe.py` (worklog namespace).

**Isolation proof (before any write):** probe DB `/tmp/sg173-probe-u6gunuh1/probe.db`; production DB
`/home/andrei/StorageGenie/data/db/storagegenie.db` sha256
`e6bef157440fb8b4a3262577362b071dcae07507ea9a7e04a614e11be28ee5bd` captured **before** the first
write and **after** the last: **identical — production DB untouched**. All mutations (real
`TestClient` routes, real engine) hit the `/tmp` database only. Fixture infrastructure: mirrored from
the per-module fixtures named in F-SG173-3; no shared fixture mutated.

**Key outputs (verbatim, sanitized):**

    [T1] GET candidate -> 200 review_task_ids(embedded)=2 state=proposed
    [T1] accept with OPEN task -> 409 detail='Candidate has unresolved review tasks' (control)
    [T1] bare POST resolve ... -> 200 {'status': 'resolved', ...}   (×2: multi_item + expiry.manual_entry)
    [T1] GET candidate after resolve -> embedded review_task_ids=2 live_open_tasks=0
    [T1] stale_membership_present=True
    [T1] accept after resolve -> 200 state=accepted ... asset exists=True
    [T2] asset assertions after accept path -> [('asset_type','proposed'),('display_name','accepted'),('status','accepted')]
    [T2] manual expiry without classification -> 422 detail='Asset must be classified before manual expiry entry'
    [T3] rows=[["0df7ce5a", -1, "expired", null], ["2adc1914", 2, "this-week", "urgent"]]
    [T3] unresolved=[["4f25209c", "needs_evidence"], ["f5a80f0f", "needs_evidence"]]
    [T3] summary={"by_tier": {"none": 1, "urgent": 1}, "by_bucket": {"expired": 1, "this-week": 1}, "unresolved": 2, "total": 4}
    [T3] asset_without_classification_invisible=True
    [T4] manual expiry WITH classification -> 200 resolved_ids_contains_own_task=True
    [ISO] prod_db_untouched=True
    [RESULT] PROBE_OK

**Verdicts (evidence = command outputs above + live audit + component tests):**

| suspected defect | verdict | discriminating evidence |
|---|---|---|
| Stale task membership breaks blocked-Accept (client/server desync) | **CONFIRMED** | T1: embedded ids survive resolve; live_open=0; server accepts (200) while the same GET still returns the stale list at route level; live: 7/7 candidates with embedded ids all resolved; served component disabled-Accept test pair green (`CandidateCard.test.tsx` blocked→disabled, unblocked→no block) |
| Classification has no UI; post-Accept expiry entry is impossible | **CONFIRMED** | grep: zero frontend callers of the classification route; T2: real accept path produces an asset with **no classification/expiry assertions**, then the real manual-expiry route 422s; live: 0 classifications in prod, 7/7 assets unclassified |
| Bare Resolve erases `expiry.manual_entry` with zero data | **CONFIRMED** | `review_tasks.py:71-98` resolves any type with `payload=None`; live audit 8/8 `{"resolution": {}}`; T1 resolves dataless; T4 control resolves the same task type **with** data via the real entry route (own task id returned) |
| Expiry **ordering** wrong | **DISPROVED** (ordering correct; visibility gap real) | T3 expired-first ascending + unresolved separated; `test_sg107_expiry_engine.py` boundary/sort tests green; engine `expiry_engine.py:292` `rows.sort(key=(days_remaining, asset_id))`; unclassified assets invisible (F-SG173-7) |

**Targeted existing tests run (the real consumers; no full suite — diagnostic slice):**
`backend/venv/bin/python -m pytest -q tests/test_candidate_read.py tests/test_candidates.py
tests/test_plugin_expiry.py tests/test_sg107_expiry_engine.py` → **30 passed** in 4.92 s
(`SG-173_backend_tests.log`). `node node_modules/vitest/vitest.mjs run
src/components/CandidateCard.test.tsx src/routes/ReviewPage.test.tsx src/routes/InboxPage.test.tsx
src/components/ExpiryEntryForm.test.tsx` → **4 files / 23 passed** in 1.93 s
(`SG-173_frontend_tests.log`). Exclusions: full backend/frontend suites (reason: diagnosis-only
ceiling + budget; the consumers are exactly the four files per leg). No new product tests were
authored. **Browser leg:** headless Chrome 150 rendered the live story pages (read-only) after the
`HOME=/tmp` workaround (F-SG173-5); structural extract in `SG-173_live_dom_extract.log` — the DOM
observations in G1 are real renders, not source inference.

---

## G3 — Repair chain handoff (smallest sequential; dependencies measured)

**Order stands as the packet listed it — measured dependencies confirm it:** (2) is a prerequisite
for both the (3) completion UX (the entry form 422s until classified) and the useful half of (4)
(visibility). (1) is independent. No reorder needed; no parallel workflow proposed.

1. **Live blocked-state derivation + server/client consistency.**
   Root cause: `GET /v1/candidates/{id}` returns the proposal-embedded `review_task_ids`
   (`candidates.py:164`) written at proposal time (`services/candidates.py:722/771`,
   `dedup.py:199/232/241`, split children `candidates.py:1134`); the client's `blocked`
   (`CandidateCard.tsx:48`) and the keyboard guard (`ReviewPage.tsx:48`) read it, while the server
   gate checks **live** tasks (`candidates.py:50`). Readers to keep whole (`G-T6`):
   `candidates.py:164` (the fix site), `jobs.py:158`, `enrich.py:276`, `services/candidates.py:792`
   (job-step snapshot — leave historical). **Repair:** project the live open-task ids into the GET
   response (same field, no API change), leaving proposal writes untouched. **Verify:** repair-slice
   stale-control test on `test_candidate_read.py` + the green `CandidateCard` blocked/unblocked pair
   + `ReviewPage` keyboard guard (accept must be offered once live tasks are zero).
2. **Classification action in Review (existing taxonomy semantics).**
   Root cause: `classify_asset` (`expiry_tracker.py:414`) is reachable only via
   `POST /v1/plugins/expiry-tracker/assets/{id}/classification` (`plugins.py:98-126`) and **no screen
   calls it**. **Repair:** a minimal post-Accept classification control in Review (and reuse on
   asset detail), reading categories from the existing taxonomy source already consumed by
   `ExpiryPage` (`useTaxonomy`); `canonical_category`/`Category.profile` supply labels+profiles and
   the route already returns the expiry assertion/task result. No new backend route. **Verify:**
   `test_plugin_expiry.py` round-trip green; new UI test for the control; then the manual-entry 422
   disappears (T2→T4 control flips).
3. **Task-type-aware Resolve with data-required expiry completion.**
   Root cause: `resolve_review_task` (`review_tasks.py:71-98`) accepts `payload=None` and resolves
   **any** type; `expiry.manual_entry` carries a data requirement that only
   `store_manual_expiry` (`expiry_tracker.py:498`) satisfies (and it resolves the task(s) with data,
   including SG-033 split-origin orphans). **Repair (preserves D-1012-13 inside D-1012-14):** make
   the bare route refuse dataless resolution of `expiry.manual_entry` (409/422 with pointer) and
   route the Inbox action to the existing `ExpiryEntryForm` (Review `ReviewPage.tsx:56` / asset
   detail `AssetDetailPage.tsx:403`); the completing POST is the resolve. **Verify:** T4 control +
   a refusal test; keep `test_plugin_expiry.py` orphan-resolution green.
4. **Expiry ordering with explicit missing/unresolved handling (scope corrected — F-SG173-7).**
   No ordering change: keep `expiry_engine.py:292` and the accepted-only rule; repair only the
   explicit-handling edges the fixes above expose — after (2) most assets stop being invisible, and
   any remaining `needs_evidence`/`dateless` rows stay in `unresolved_rows` with their reason; ensure
   the Expiry page's unresolved links reach a surface with the entry form (already true via
   `AssetDetailPage`). **Verify:** `test_sg107_expiry_engine.py` suite unchanged green.

**Reuse vs one simpler alternative (`G-A7`):**

| repair | reuse (machinery cost) | simpler alternative | call |
|---|---|---|---|
| 1 | live projection inside the existing GET (small server change, zero new endpoints, fixes `jobs.py`/`enrich.py` readers too) | client-side join on `tasksQuery` already fetched in `ReviewPage.tsx:39` (zero server change; other readers stay stale; direct Review navigation still stale) | reuse — server projection; client join is the fallback if server change is unwanted |
| 2 | existing classification route + taxonomy; one small UI control + one client fn | auto-classify on accept from `category_proposed` (no UI, but removes the user acceptance the owner asked for) | reuse route + minimal control; auto-propose only as optional pre-fill, never silent |
| 3 | existing completion route + existing form; a guard + Inbox routing | date-entry modal in Inbox (new component, duplicates the form) | reuse |
| 4 | existing engine + Unresolved section; verify-only | re-sorting (unnecessary; would contradict green boundary tests) | no change |

**Out of scope, untouched:** Scene/UI wiring (D-1012-6 parked), taxonomy redesign (D-1012-8 separate),
unrelated PRs #43–#49, schema/migrations/deploy files.

---

## Acceptance criteria — question answered

| criterion | question | result |
|---|---|---|
| **A1** | served-story observations identify transitions + current image; missing observations have limitations; live evidence discriminates | YES — image `9064d2ce` re-observed; transitions 1–7 tabulated with OBSERVED LIVE / ISOLATED / limitations for write-gated legs; stale-block dead-end and classification wall both live-observed; logs + DOM committed sanitized |
| **A2** | isolated story shows failure/control pairs, DB isolation, actual commands/outputs, nonempty inputs; each suspected defect CONFIRMED/DISPROVED/UNVERIFIED | YES — probe with real routes; prod hash before==after `e6bef157…`; T1 stale vs live-accept control, T2 missing-classification 422 vs T4 classified 200, T3 resolved/unresolved matrix; verdicts table above; ordering **DISPROVED**, rest CONFIRMED |
| **A3** | repair chain names symbols/consumers/completion semantics/targeted verification; preserves D-1012-13; no product change claimed | YES — G3 order with `G-T6` readers/writers named, reuse table, D-1012-13 folded into repair 3; zero product files changed (`git status` clean of product paths) |
| **A4** | ref+hash, contract echo, start/end health, constraints, elapsed, remaining, notes receipt reported; UNCLEAR dispositions | YES — below; every UNCLEAR item dispositioned |

**Health (`CO-92`):** start: `{"status":"ok","db":"ok","storage":"ok"}` HTTP 200 (slice start batch);
end: same body ×2, HTTP 200 (quoted in `SG-173_live_logs.log`) — **delta none**.

**Guard invocation:** `PG-DP-03` (live-before-source walk honored; source reads only after live
predicates/DOM); `PB-2`/`PG-PR-03` (no denied operation, no privilege route-around — lane docker
socket is the grant, no sudo used, no host config touched); `PB-3` (vacuity: no criterion passes on
an empty set — every leg quotes nonempty inputs/outputs; exclusions stated); `PB-5` (bounds:
reads 120 s, probe 300 s, tests 600 s; nothing killed, nothing hung; vite dev server started/stopped
deliberately, chrome each under `timeout 40`); `PB-6` (no STOP condition arose; work shipped
normally); `CO-60` receipt below.

**Money posture:** **$0.000000 USD, zero application provider/model calls** — probe and tests run
offline against SQLite; no image calls, no metered inference; the only network egress was
git note push/read-back to GitHub.

**Budget (actual):** lane start `20:29:30Z`; work commit `20:36:5xZ`; report commit ≈`20:40Z` —
**elapsed ≈ 11 min ≪ 1050 s half-bound** of `RUN_BUDGET_S=2100`. No command hit its bound.

**Artifacts (committed, all under `docs/worklogs/SG-173*`):** `SG-173_probe.py` (disposable probe),
`SG-173_probe_out.log` (PROBE_OK), `SG-173_backend_tests.log` (30 passed),
`SG-173_frontend_tests.log` (23 passed), `SG-173_live_logs.log` (identity, contract echo, rules_check,
health, image, sanitized server logs), `SG-173_live_dom_extract.log` (structural DOM extract).
Raw DOMs and Chrome profiles stayed in `/tmp/opencode` (not committed).

---

## Receipt (`CO-60`, `CO-79`)

Notes-ref mechanism; refspec fetched into a **mapped** local name (`refs/notes/sg173-fetched`; a
default fetch never carries notes). **WORK_HEAD = `901caf324c8421e5c276b3132ed4265bcf948c78`**.
Published and read back **before this file was committed**:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -f -m "Dispatch-ID: SG-173 | Report: docs/worklogs/SG-173_report.md | Work-HEAD: 901caf324c8421e5c276b3132ed4265bcf948c78" 901caf324c8421e5c276b3132ed4265bcf948c78
add_wh_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
   2d110d1..0ed450d  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
notes_push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg173-fetched
fetch_exit=0

$ git notes --ref=refs/notes/sg173-fetched show 901caf324c8421e5c276b3132ed4265bcf948c78
Dispatch-ID: SG-173 | Report: docs/worklogs/SG-173_report.md | Work-HEAD: 901caf324c8421e5c276b3132ed4265bcf948c78
show_wh_exit=0
```

The report commit (this file) receives the same note **after** this file is committed and the commit
exists (its hash cannot appear inside itself, `CO-79`): same `add -f` + `push` + mapped `fetch` +
`show`, output recorded by the runner. **note=yes** (WORK_HEAD read back on remote; report commit
annotated post-commit). The legacy `finalize_dispatch_report.sh` was **not** used.

**State of the world:** product code unchanged (diff ceiling = `docs/worklogs/SG-173*` only);
running service unchanged (no rebuild/recreate/restart); **production writes: NONE** (only GETs and
read-only SQLite reads against production; all mutations confined to the disposable `/tmp` DB). The
tree remains **UNSERVED** relative to any future repair — nothing here was deployed.

---

## UNCLEAR — every item dispositioned

- **FIRST READ:** whether "bare Resolve" was a UI affordance bug or deliberate route design.
  *Disposition:* route design — `resolve_review_task` takes an optional payload and ignores it for
  state (`review_tasks.py:83-97`); the Inbox sends `{}` (`client.ts:218-224`). Live audit proves
  every historical resolve was dataless. Design decision needed in repair 3 (refuse vs redirect),
  recorded, not guessed.
- **FIRST READ:** whether the walk would show "task completion" as an available transition.
  *Disposition:* no — all live tasks are already resolved; the observable is the **stale blocked
  state** plus the audit trail. The live act was not repeated (write boundary); isolated T1 covers it.
- **DURING EXECUTION:** whether the first failed transition is the stale block or the classification
  wall. *Disposition:* both are exact stop points at different stages; live population stops at the
  stale block first, a fresh walk stops at classification after Accept. Both reported.
- **DURING EXECUTION:** Chrome unavailable under the sandbox `$HOME`. *Disposition:* resolved with
  `HOME=/tmp/opencode/chromehome` (F-SG173-5); DOM walks are real renders.
- **DURING EXECUTION:** contract check exit 3 differences vs SG-172 quote. *Disposition:* same exit,
  same G-L1 tag-ref shape, added summary lines; bytes independently verified (F-SG173-6). No host
  repair.
- **REMAINING:** the four-repair chain (G3) awaits packets; owner verdict on the stale-block
  dead-end; `F-SG171-5` (duplicated blocked sentence for blocked+dedup candidates) still present;
  `D-1012-8` taxonomy mapping; parked Scene UI arc (`D-1012-6`); `F-SG144-1` venv follow-up
  (F-SG173-2 adds the root-venv pitfall).
