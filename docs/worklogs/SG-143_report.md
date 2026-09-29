SG-143 — Port the 3 blocked HouseholdSelector pages (className passthrough) — report

**Verdict: PARTIAL SHIP with a committed call-site STOP — 2 of 3 call-sites ported byte-identically
(Capture, Inbox), the 3rd (CatalogToolbar) STOPped in-ceiling, served live.** The `selectClassName`
passthrough is added and `tsc`/244-suite/eslint are green; the two themed-class guards are green
UNCHANGED. Rebuild + exactly ONE recreate + verify green; the served bundle now carries the SG-143
marker. This closes the useful remainder of `F-SG138-1` (see (g)).

**Dispatch-ID:** SG-143 · **Work dir:** `/home/andrei/StorageGenie` · **origin:**
`git@github.com:Andovol/StorageGenie.git`.
**Contract:** `0.40.0` — source path `/home/andrei/storagegenie-contract/VERSION`; `RULES.md` sha256
`5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c` == the installed payload hash
recorded in `AGENTS.md`. Recorded == published (D4 adoption).
**BASE** (`origin/automation` requested; resolved at start — two fields): requested
`origin/automation`, resolved `08bdd1e8ac802de11dbf461dc5d7a31a55fee197` (== local HEAD, worktree
clean). **WORK_HEAD:** `50304f0ff01fc2a4104f3b200ad3b906601a49ac` (product + tests + verify log; the
receipt-note target). G0 map commit `8587d06218fa110e50206c1a1dd69e531b8b3266`. This report lives in
the following worklogs commit, so it does not carry its own hash (CO-55b).
**Model/effort (CO-78, from process arguments — never the identity line):** pid `725282`,
`/proc/725282/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie --model
opencode-go/deepseek-v4.1-flash --variant high` -> model `opencode-go/deepseek-v4.1-flash`, effort
`high`. Coder `opencode` (env CODER=opencode, OPENCODE_PID=725282, RUN_BUDGET_S=2100).
**Spend:** REAL **$0.000000 USD**; **zero metered calls** on every path (`PG-PR-06` stated upfront:
no USD-metered call exists — the slice is local edits + tests + one image rebuild/recreate + served
reads; no provider/model/Jina call).
**Gates:** **DATABASE** read-only (`alembic current` + mode=ro counts) · **Restart** exactly ONE
recreate of the served stack (D145 owned refresh; production restart named plainly per `G-K2`) ·
**Deploy** that one recreate.
**Role guard held:** Coder only; no dispatch verb run for any ID, own unit never started or polled;
`gh` untouched.
**Guards (Architect copies to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` ·
`PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` ·
`PG-PR-04` · `PG-PR-06`.

## (a) Issues / deviations / findings

- **F-SG143-1 (premise correction — path level, no harm).** The packet writes
  `frontend/src/pages/*.tsx`; the real tree uses `frontend/src/routes/*.tsx` plus
  `frontend/src/components/shell/CatalogToolbar.tsx`. The Architect's substance (line numbers, class,
  styles) all matched once the directory segment was corrected. The real SET of household selects not
  already on the shared selector is exactly three — Capture, Inbox, CatalogToolbar — matching the
  packet's expected three.
- **F-SG143-2 (the load-bearing finding — CatalogToolbar call-site STOP, committed).** The packet
  lists `CatalogToolbar.tsx` as an expected call-site. Its select (`CatalogToolbar.tsx:123-136`)
  DIFFERS from the page-level selector in ways that make a byte-identical port impossible inside the
  packet's ceiling: (a) it carries `aria-label="Household"` and no `<label>` wrapper — the shared
  component has no accessible-name prop at all; (b) it renders `No households` ONLY when the list is
  empty, whereas `HouseholdSelector` renders `emptyOptionLabel` as a PERMANENT first option whenever
  truthy (or nothing when falsy) — it cannot express "fallback only when empty". Reproducing (a)+(b)
  requires at least TWO API changes beyond the allowed single class passthrough ("the passthrough prop
  ONLY"; "no other API change"). Dropping either breaks output identity, and (a) additionally breaks
  the existing guard `frontend/src/components/shell/shell.test.tsx:602`
  (`getByLabelText("Household")`). Per the packet's own G0 clause ("if the port becomes impossible
  inside the ceiling, STOP that call-site and ship the rest with the STOP committed"), CatalogToolbar
  is left **byte-untouched**.
- **F-SG143-3 (packet defect — the "stated choice" is not actually stated).** The packet's Context
  line says "The className-prop API word rides this L3 chain — the choice below is stated, never
  re-asked", but no choice appears in the packet (nor in the design/plan: the plan says `className`,
  the packet's G1 says expected `selectClassName`). Resolved as an in-scope design call and reported:
  the prop is named **`selectClassName`** (precise — the component renders both a label and a select).
- **F-SG143-4 (scope boundary — no CatalogPage edit).** `CatalogPage.tsx:197-260` renders no household
  select; it forwards the household state to `AppShell` -> `CatalogToolbar`. No in-scope edit exists
  there, so it is unchanged.
- **No other writes.** Backend diff EMPTY (backend suite therefore not re-run). No hook, style-token,
  config, other component or other test touched. No secret in any fixture (CO-100).

## (b) Actions

- Changed product (3): `frontend/src/components/HouseholdSelector.tsx` (+`selectClassName?: string`,
  `className={selectClassName}` on the `<select>`; every old prop byte-compatible),
  `frontend/src/routes/CapturePage.tsx` (inline select -> shared component), `frontend/src/routes/InboxPage.tsx`
  (inline select -> shared component).
- Changed tests (1): `frontend/src/components/HouseholdSelector.test.tsx` (+1 focused test: default
  render has NO class attribute; `selectClassName` applies the class). The two themed-class guards
  were NOT edited.
- Untouched by decision: `frontend/src/components/shell/CatalogToolbar.tsx` (F-SG143-2 STOP).
- Worklogs (3): `docs/worklogs/SG-143.log`, `SG-143_report.md`, `SG-143_verify.log`.
- Commits: G0 map `8587d06` · G1 port `50304f0` · worklogs commit (this report) = final tip.
- External/production: 1 image rebuild + exactly ONE recreate (D145). No live row written (counts
  delta 0); no migration; no provider/model call. Retry count 0.

## (c) Verification (raw captures in `docs/worklogs/SG-143_verify.log`)

- **G0 (committed BEFORE any edit, `8587d06`):** verbatim markup of all 3 call-sites + on-target test
  assertions (`theme-adoption.test.tsx:219-228`; `InboxPage.test.tsx:75-81`) + the CatalogToolbar
  difference. Confirmed the real set is 3.
- **G1 fail-post (`PG-SC-12`, real configs):** `tsc --noEmit` -> **EXIT=0** (zero diagnostics; the
  package `build` runs the same `tsc`); targeted vitest -> **6 files / 57 tests passed** incl. the two
  themed-class guards green UNCHANGED; **full frontend suite 27 files / 244 tests passed** (243 BASE
  + 1 new) -> no reds, so no bare-BASE stash-repro was applicable; `eslint` on the 4 touched files ->
  **EXIT=0**; `git diff --stat -- backend` -> **empty** (stated reason the backend suite was not run).
- **Mapping table** (call-site -> props -> identical to G0): Capture YES (label style/fontSize 13,
  class, `...CONTROL_STYLE, marginLeft:6`, no empty option, localStorage write); Inbox YES (plain
  label, class, `CONTROL_STYLE`, default `Select household` empty option, localStorage write);
  Chat/Planning UNCHANGED (no prop passed -> no class attribute; proven by the new test's
  `class === null` assertion); Catalog N/A (byte-untouched).
- **G2 served (`PG-EV-08`, `PG-PR-04`):** BEFORE (old container `229da27d…`) bundle
  `index-BnyUlS-i.js` sha256 `fc696d21…` 318415 B, `selectClassName` grep **0**; rebuild
  `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` **BUILD_EXIT=0**; exactly ONE
  recreate `docker compose up -d --no-deps backend` **REC_EXIT=0**, container-id change
  `229da27d…` -> `55d398ed7625cf637f587d863d60c0d114355ca9312b554becdfccd59e71a4de` (M42 — the proof,
  never RestartCount), image `5f5b3ac3…` -> `76917528…`; health ×6 exact
  `{"status":"ok","db":"ok","storage":"ok"}` HTTP 200; gate `http:80 301` / `https:443 401`; alembic
  head `20260924_sg114_relation (head)` unmoved; **counts delta exactly 0** (provider_call 18, job 9,
  enrich_snapshot 4, candidate 8, evidence 13, guardrail_event 2, audit_event 68, asset 6, household
  1); the 3 pages `/capture` `/inbox` `/catalog` -> **200** each; AFTER bundle
  `index-CTQCofuO.js` sha256 `d9dbdef3…` 318152 B with `selectClassName` grep **1** and
  `Select household` grep 1. **Marker delta:** `fc696d21…` -> `d9dbdef3…` = exactly the SG-143 build
  (BEFORE lacked the marker, AFTER carries it). CSS entry unchanged (`index-DO0gjGV6.css`).
- **No vacuous pass:** the fail-post is a quoted exit-0 + file/test counts, not silence; the port
  identity is a props->render mapping backed by the unedited guards; the `selectClassName` change is
  proven effective (grep 1 in served bytes) AND proven non-invasive (default render has no class);
  the recreate is a changed full container id; counts are delta-zero by explicit re-read.

## (g) Recommendation (Architect decision, not a Coder action)

Disposition `F-SG138-1` as **partially closed**: the Capture/Inbox half is ported + served. The
Catalog half is blocked by the packet's own "single class passthrough" ceiling. Options for a future
slice: (1) authorize a second API surface on `HouseholdSelector` (`selectAriaLabel` + a
fallback-only-when-empty option mode) and port the toolbar; or (2) accept the toolbar's select as its
own control (it is a shell control with an aria-label and a "No households" fallback) and close
`F-SG138-1` with the toolbar explicitly excluded. This slice does not pick between them — it reports
the gap.

## Receipt (note on `refs/notes/storagegenie-coder-reports`) — pasted verbatim

Work pushed to `origin/automation` (`08bdd1e..50304f0`), worktree clean (`CO-55`). No push to
`storagegenie-evidence`; `{{RECEIPT_CMD}}` not run. Note added on WORK_HEAD `50304f0`, notes ref
pushed, refspec fetched into the mapped name `refs/notes/sg143-fetched` (a bare refspec would only
rewrite `FETCH_HEAD`), `show` pasted:

```text
$ git notes --ref=refs/notes/storagegenie-coder-reports show 50304f0
error: no note found for object 50304f0ff01fc2a4104f3b200ad3b906601a49ac.
pre_show_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-143 | Report: docs/worklogs/SG-143_report.md | Work-HEAD: 50304f0ff01fc2a4104f3b200ad3b906601a49ac" 50304f0
add_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   48a32d1..84519f9  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg143-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg143-fetched
fetch2_exit=0

$ git notes --ref=refs/notes/sg143-fetched show 50304f0
Dispatch-ID: SG-143 | Report: docs/worklogs/SG-143_report.md | Work-HEAD: 50304f0ff01fc2a4104f3b200ad3b906601a49ac
show_exit=0
```

The final tip is dual-annotated with the same message (note-anchor inoculation, SG-092 precedent);
that annotation's fetched `show` is executed and pasted in `SG-143.log`. Final line: `note=yes`.

## Actual versus budget (units: seconds, live clock UTC)

| Goal | Budget | Actual (approx) | Note |
|---|---|---|---|
| G0 reads + map | 120s ordinary/cmd | ~60s | path correction + Catalog difference found |
| G1 tsc + eslint | 600s / 120s | ~15s | both exit 0 |
| G1 targeted vitest | 600s | ~3.1s | 6 files / 57 tests |
| G1 full suite | 600s | ~6.2s | 27 files / 244 tests |
| G2 rebuild | 600s | **11s** | BUILD_EXIT=0 |
| G2 recreate + verify | 300s / 120s | ~10s | one recreate + health/gate/counts/bundle |
| G3 worklog + push + note | 120s / 300s | ~90s | 3 files + note |
| Overall | 2400s | ~250s | no command killed, no hang |
| Spend | $0.000000 USD | **$0.000000 USD** | zero metered calls |

## UNCLEAR

- **FIRST READ:** whether "port all 3 call-sites" required the Catalog toolbar select to be forced
  through `HouseholdSelector` even at the cost of extending its API beyond the single class
  passthrough. I read the packet's explicit per-call-site STOP clause as governing and shipped the two
  achievable call-sites, leaving Catalog byte-untouched with the finding committed (F-SG143-2). If the
  intent was "add aria-label too", that is a second API change the packet forbids — hence the STOP
  rather than a guess.
- **DURING EXECUTION:** the packet's "the choice below is stated" was not actually stated anywhere
  (F-SG143-3); I named the prop `selectClassName` and reported it. Paths were `routes/`, not `pages/`
  (F-SG143-1). Neither changed the outcome.
- **REMAINING:** the Catalog toolbar household select remains a shell control outside the shared
  selector; closing `F-SG138-1` fully needs an owner/Architect decision between a second API surface
  on `HouseholdSelector` and accepting the toolbar control as-is (see (g)). The hue visual verdict on
  fresh screenshots (finish-chain Task 5) is untouched by this slice.
