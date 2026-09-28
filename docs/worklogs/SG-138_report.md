BLOCKED: 3 of the 7 PR-#4 source files cannot be landed inside this slice's ceiling. The current tree is
477 commits ahead of PR #4's base `33460cd`; intervening slices (SG-045/064/068/075/105/118) refactored
every page the PR touched. `CatalogPage.tsx` no longer renders an inline household `<select>` at all (it
moved to `CatalogToolbar.tsx`, out of the write ceiling), and `CapturePage.tsx`/`InboxPage.tsx` now carry
the SG-105 themed control class on that select — the PR hunk drops it, which two existing passing tests
assert. A faithful in-ceiling port of those three would either regress behaviour or require a prop-API
extension the packet forbids. Shipped instead (in-ceiling, byte-faithful): `HouseholdSelector.tsx` +
`HouseholdSelector.test.tsx` (verbatim, sha256 == PR head) + the two cleanly-equivalent page adopters
(`ChatPage.tsx`, `PlanningPage.tsx`) + the single `frontend/*.log` ignore line. The three page hunks are
left unapplied.

SG-138 report — port PR #4's HouseholdSelector extraction minus `preview.log` (D8)

Dispatch-ID: SG-138
Work dir:    /home/andrei/StorageGenie
origin:      git@github.com:Andovol/StorageGenie.git
BASE ref:    origin/automation
BASE commit: 756a53b059466eb29985ac26794c8dfa04cb455c  (start HEAD; worktree clean at start)
WORK_HEAD:   6d5d53a6c09bbc95a0ffe9d08c0a57b7e81942e3  (port commit; receipt note target; this report lives in the following worklog commit, so the report does not carry its own hash — CO-55b)
Model:       opencode-go/deepseek-v4.1-flash  (per process args: /proc/117150/cmdline `--model`)
Effort:      high                             (per process args: /proc/117150/cmdline `--variant high`)
Coder:       opencode  (env CODER=opencode; OPENCODE_PID=117150; RUN_BUDGET_S=2100)
Contract:    echo 0.40.0 — source `/home/andrei/storagegenie-contract/VERSION` (published tip f26dbd3).
             Recorded 0.40.0 == published. RULES.md sha256 `5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`
             == the AGENTS.md-recorded installed payload hash (0.39.0+0.40.0).
Spend:       real $0.000000 USD · zero metered calls · no serving · no rebuild/recreate · no migration.
Gates:       DATABASE none · Restart none · Deploy none.
             Role guard held (Coder only; no dispatch verb run for any ID, own unit never started/polled; `gh` untouched).
Guards:      PG-EV-01 · PG-EV-02 · PG-EV-05 · PG-EV-10 · PG-SC-02 · PG-SC-09 · PG-SC-10 · PG-SC-12
             · PG-IC-01 · PG-IC-07 · PG-IC-09 · PG-PR-03 · PG-PR-04 · PG-PR-06.
Money:       PG-PR-06 stated upfront — no USD-metered call exists on any path; real spend $0.000000 USD.

## (a) Issues / deviations / findings

- **F-1 — premise falsified (CO-07).** The packet says "SG-135/136/137 touched no page files — VERIFY,
  never inherit". That is true but insufficient: the divergence is far older and larger. PR #4's base
  `33460cd` is **477 commits behind** HEAD. All five page files changed after the PR base (`CatalogPage`
  +194/-62, `InboxPage` +23/-5, `ChatPage` +16/-5, `CapturePage` +14/-9, `PlanningPage` +6/-5), via
  SG-045/064/068/075/105/118. The packet's per-page equivalence spec describes the **pre-refactor** PR
  base, not this tree.
- **F-2 — `CatalogPage.tsx` hunk cannot apply (STOP for that file).** The current `CatalogPage.tsx`
  renders no household `<select>`: it passes `householdId` / `households` / `onHouseholdChange` to
  `AppShell` (`frontend/src/components/shell/AppShell.tsx:20-22,68-70`), which renders
  `CatalogToolbar`'s select at `frontend/src/components/shell/CatalogToolbar.tsx:123-136`. The PR's
  target code no longer exists in the file. Adapting it would mean reverting the shell refactor (product
  behaviour change) or editing `CatalogToolbar.tsx` (out of ceiling) — both STOPs.
- **F-3 — `CapturePage.tsx` / `InboxPage.tsx` hunks would regress the SG-105 themed control (STOP).**
  Both current selects carry `className={THEMED_CONTROL_CLASS}` (`bg-background text-foreground
  border-border focus-ring`) plus `CONTROL_STYLE`. The PR hunk passes only `labelStyle`/`selectStyle`
  and **drops the class** (the pre-refactor base had no class). Two existing, passing tests assert the
  class: `frontend/src/routes/theme-adoption.test.tsx:219-228` (Capture) and
  `frontend/src/routes/InboxPage.test.tsx:75-81` (Inbox). Porting as-is is a product behaviour change;
  preserving current output would require adding a `className` prop to `HouseholdSelector`, which the
  packet's simplicity rail forbids ("No prop-API redesign"). Both files are therefore left unapplied.
- **Adaptation clause did not rescue these three.** G0 says "a hunk that no longer applies is adapted by
  hand… never force-merged" — but adaptation here is impossible inside the ceiling: it needs either an
  out-of-ceiling file or a new component prop. Reported as blocked, not force-merged.
- **Cast decision (packet asked: keep or drop — report).** Kept `households as Household[] | undefined`
  verbatim as in the PR. It is redundant noise: `useHouseholds()` returns `UseQueryResult<Household[]>`
  (`frontend/src/hooks/useAssets.ts:53-58`), so `data` is already `Household[] | undefined`. Kept to
  stay byte-faithful to the PR source; no configured lint rule flags it.
- **No other writes.** No backend, no test-framework change, no page-behaviour tweak, no merge/close/
  rebase of PR #4, no `preview.log`, no `{{RECEIPT_CMD}}`, no push to `storagegenie-evidence`.

## (b) Port table (shipped set; CO-101)

| PR source file | status | evidence |
|---|---|---|
| `frontend/src/components/HouseholdSelector.tsx` | **PORTED** verbatim | sha256 `699258fc…db25` == PR head |
| `frontend/src/components/HouseholdSelector.test.tsx` | **PORTED** verbatim | sha256 `827752e3…bc4ef` == PR head; 59 lines |
| `frontend/src/routes/ChatPage.tsx` | **PORTED** (hunk applied cleanly) | pre-change block byte-identical to PR base |
| `frontend/src/routes/PlanningPage.tsx` | **PORTED** (hunk applied cleanly) | pre-change block byte-identical to PR base |
| `frontend/src/routes/CapturePage.tsx` | **NOT PORTED (BLOCKED, F-3)** | themed-class regression vs SG-105 test |
| `frontend/src/routes/InboxPage.tsx` | **NOT PORTED (BLOCKED, F-3)** | themed-class regression vs SG-105 test |
| `frontend/src/routes/CatalogPage.tsx` | **NOT PORTED (BLOCKED, F-2)** | select moved to CatalogToolbar (out of ceiling) |
| `frontend/preview.log` (artifact) | **NEVER created / not ported** | absent from tree and status |
| root `.gitignore` | **ADDED** one line `frontend/*.log` | `check-ignore` IGNORED proof below |

## (c) Mapping table (page → emptyOption / showLabel / styles / onChange), quoted against shipped code

`HouseholdSelector` defaults (`frontend/src/components/HouseholdSelector.tsx:14-41`, shipped verbatim):
`showLabel = true`, `emptyOptionLabel = "Select household"`, `labelStyle`/`selectStyle` = undefined,
`onChange={(event) => onChange(event.target.value)}`, empty option rendered iff `emptyOptionLabel` truthy.

| page | shipped props | rendered result | onChange |
|---|---|---|---|
| ChatPage (`ChatPage.tsx:79-86`) | `value`, `onChange`, `households as Household[] \| undefined` — all presentation props default | `<label>Household <select>` + `<option value="">Select household</option>` + hh options | `setHouseholdId(id); localStorage.setItem("household_id", id)` |
| PlanningPage (`PlanningPage.tsx:71-78`) | same as ChatPage | same | `setHouseholdId(id); localStorage.setItem("household_id", id)` |

Equivalent to the previous inline markup for these two pages: the defaults reproduce exactly the prior
`<label>Household <select>` + `"Select household"` empty option + `localStorage` write (verified
pre-change blocks byte-identical to PR base, so the PR's own equivalence case analysis transfers).

## (d) Test evidence (pasted summaries; full raw in `docs/worklogs/SG-138_verify.log`)

- Targeted (`18:26:58Z`, bounds 600s): `HouseholdSelector` (3) + `ChatPage` (6) + `PlanningPage` (4) +
  `InboxPage` (8) + `theme-adoption` (12) → **5 files / 33 tests passed**.
- Full suite (`18:27:04Z`, exit 0): **27 files / 243 tests passed**, no reds → no BASE stash-repro needed.
- `eslint` on the four touched files → **exit 0**.
- **Honesty on coverage (no vacuous pass).** `HouseholdSelector.test.tsx` proves the component's default
  render (label, combobox value/options, `onChange(img)`, `showLabel={false}`, custom empty label).
  The **ChatPage/PlanningPage page-level household combobox is not independently asserted** by their page
  tests (those drive the hook id / `localStorage`, not the select DOM). So the selector output is
  COMPONENT-PROVEN and the page integration is green-by-render, but there is **no page-level selector
  assertion** for Chat/Planning — stated, not hidden. `Capture`/`Inbox`/`Catalog` are NOT PORTED, hence
  UNPROVEN for this slice by construction.
- No fail-pre red was manufactured: this is a behaviour-preserving extraction (green/green + mapping
  proof is the correct shape).
- `git status` shows **no `.log` file** anywhere; `frontend/preview.log` exists in neither tree nor status.

## (e) Acceptance criteria — answered, including the failed ones

- **ported** — NO: 4 of the 7 source hunks are present (2 new + 2 modified) + the ignore line; 3 are
  blocked (F-2/F-3). **This criterion is reported FAILED, not hidden.**
- **equivalent** — PARTIAL: ChatPage/PlanningPage map to identical output (mapping table) with
  component-level proof; Capture/Inbox/Catalog UNPROVEN (not ported).
- **clean** — diff is exactly the 4 shipped sources + 1 ignore line + 3 worklogs — **not** the packet's
  7-source shape (F-1).
- `check-ignore` IGNORED proof: `.gitignore:16:frontend/*.log	frontend/preview.log` (exit 0).
- `git status` no-log proof: no `.log` entry.
- Spend: $0.000000 USD, zero metered calls.

## (f) Actual-versus-budget per goal (units: wall-clock seconds, live clock; PG-IC-07)

| goal | budget | actual (approx) | note |
|---|---|---|---|
| G0 reads/verification | 120s ord. per cmd | ~120s | 477-commit divergence found |
| G1 port + eslint | 120s per cmd | ~60s | eslint exit 0 |
| G1 targeted vitest | 600s | ~1.6s | 5 files / 33 tests |
| G1 full suite | 600s | ~5.1s | 27 files / 243 tests |
| G2 worklog + receipt | remainder | ~120s | |
| overall | 2400s | ~360s (process start 18:22:29Z → ~18:28Z) | under `RUN_BUDGET_S=2100` |

## (g) Recommendation (Architect decision, not a Coder action)

Land the shipped subset as the useful part of PR #4. Re-spec the three blocked pages as their own slice
(one that may either extend `HouseholdSelector` with a `className`/`aria-label` passthrough — an API
change — or move the Catalog select out of `CatalogToolbar`). The `frontend/*.log` ignore plus the
component are independently valuable. PR #4 can then be closed by the workstation (not done here).

## UNCLEAR

- **FIRST READ** — Was this "port the 7 files" or "land the extraction"? I read it as the latter, so when
  faithful porting of 3 files proved impossible in-ceiling I shipped the rest and declared BLOCKED rather
  than force-merge them. If the intent was strictly "touch exactly these 7 paths", this slice is
  incomplete.
- **DURING EXECUTION** — The packet's per-page equivalence spec was written against PR #4's
  pre-theming base. I treated the current tree's SG-105 themed-select tests as authoritative behaviour
  (authority #4/#5) and refused to regress them. An alternative would have been to add a `className` prop
  to `HouseholdSelector` (forbidden here); if that is actually preferred, say so and it unblocks
  Capture/Inbox.
- **REMAINING** — `CatalogPage`'s household select lives in `CatalogToolbar.tsx`; any future extraction
  there must edit that file (out of this ceiling). Whether the owner still wants `HouseholdSelector` used
  in Catalog at all, given the shell now owns that control, is an open product question.
