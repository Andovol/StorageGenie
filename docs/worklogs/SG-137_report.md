SG-137 report — fold #11–#14 into one client.test.ts coverage slice, dedupe updateAiModel

Dispatch-ID: SG-137
Work dir:    /home/andrei/StorageGenie
origin:      git@github.com:Andovol/StorageGenie.git
BASE ref:    origin/automation
BASE commit: 251cca5e1d38d965bd648531fd9529cc759a6388  (start HEAD; tree clean at start)
WORK_HEAD:   9b585fddf5c0eb19e4324da101700085d279ca3f  (fold commit; receipt note target)
Model:       opencode-go/deepseek-v4.1-flash   (per process args /proc/107947/cmdline `--model`)
Effort:      high                              (per process args /proc/107947/cmdline `--variant high`)
Coder:       opencode  (env CODER=opencode; OPENCODE_PID=107947; RUN_BUDGET_S=2100)
Contract:    echo 0.40.0 — source `/home/andrei/storagegenie-contract/VERSION` (published tip f26dbd3).
             Recorded 0.40.0 == published.
Spend:       real $0.000000 USD · zero metered calls · no serving · no rebuild/recreate · no migration.
Gates:       DATABASE none · Restart none · Deploy none.
             Role guard held (Coder only; no dispatch verb run, own unit never started/polled; `gh` untouched).
Guards:      PG-EV-01 · PG-EV-02 · PG-EV-05 · PG-EV-10 · PG-SC-09 · PG-SC-12 · PG-IC-01 · PG-IC-07
             · PG-IC-09 · PG-PR-03 · PG-PR-04 · PG-PR-06.
Money:       PG-PR-06 stated upfront — no USD-metered call exists on any path; real spend $0.000000 USD.

## 0. Method and evidence

- Every packet premise was verified before building on it. All four heads re-hashed match the
  packet; every merge-base is `c849088`; every diff touches exactly `client.test.ts`; the BASE
  file is byte-identical to the PR base. No premise differed.
- No vacuous pass: the union was applied and then **run** (`30 passed`), and the full suite was
  **run** in-bound (`26 files / 240 tests passed`). Every ported test imports and calls the real
  `client.ts` export and asserts on the returned value (`PG-EV-07`). The `updateAiModel` loser's
  assertions were line-compared and found byte-equal, so zero coverage was silently dropped.
- Units are wall-clock seconds on the live clock (`PG-IC-07`). Raw captures live in
  `docs/worklogs/SG-137_verify.log`.

## 1. G0 — per-PR blocks table + keeper

**Refs.** `origin/automation` → `251cca5e1d38d965bd648531fd9529cc759a6388`. Heads: `#11 c59338250fa478e46d2e24b9bd44f318a367e676`, `#12 03487ee2476e873ad9f985bde3d512d280ca20dc`, `#13 08baa1db6d68c18bb6f2bbddf610afcdd8240d7d`, `#14 7356f9d7cbfbf9ee3b2303c6551895c91e772871` — all match. Merge-base for all four = `c8490886f2cdac0688c37c42080417168fedb1e2`.

| PR | head | base | file(s) | describes / tests added |
|---|---|---|---|---|
| #11 | c593382 | c849088 | client.test.ts | `describe("apiPatch")` — 3 tests (success method/headers/body/params; detail failure; empty-statusText JSON fallback). Import `+apiPatch`. |
| #12 | 03487ee | c849088 | client.test.ts | `describe("apiPut")` — 3 tests; `describe("updateAiModel")` — 1 test (success via PUT). Import `+apiPut, +updateAiModel`. |
| #13 | 08baa1d | c849088 | client.test.ts | failure test added inside the EXISTING `describe("fetchAiSettings")`; `describe("updateAiModel")` — 2 tests (success + failure). Import `+updateAiModel`. |
| #14 | 7356f9d | c849088 | client.test.ts | `describe("apiPost")` — 6 tests; `describe("apiPost helpers")` — 4 tests (candidateDecision/sendChat/runPlanning/resolveReviewTask). Import `+apiPost, +candidateDecision, +sendChat, +runPlanning, +resolveReviewTask`. |

**Union named.** apiPatch(#11) · apiPut(#12) · updateAiModel ONE(#12 vs #13) · fetchAiSettings
failure(#13) · apiPost(#14) · apiPost helpers(#14). Matches the packet expectation exactly; no
block missing. (Note: five are new `describe` blocks; the sixth requested item — the
`fetchAiSettings` failure test — is an inner test added to an already-existing `describe`, so the
XLS shipped as 5 new describes + 1 modified describe, not 6 new describes.)

**updateAiModel keeper = #13.** It carries the success test AND a failure test
(`rejects.toThrow("Unsupported model_id")`); #12 carries only the success test. The success
assertions are byte-equal across both (res `toEqual {provider:"openai", model_id:"gpt-4o"}`;
fetch called with `buildUrl("/v1/settings/ai", {})` and `{method:"PUT",
headers:{"Content-Type":"application/json"}, body: JSON.stringify({model_id:"gpt-4o"})}`), so the
dropped #12 block's delta is **zero unique assertions** — nothing was lost.

## 2. G1 — union + proof

**Shape.** One write to `frontend/src/api/client.test.ts`: the import line extended to the union of
12 used symbols (`buildUrl, apiGet, apiPatch, apiPut, apiPost, fetchAiSettings, updateAiModel,
fetchPlanningSuggestions, candidateDecision, sendChat, runPlanning, resolveReviewTask`), plus the
five new describes and the `fetchAiSettings` failure test. Covered module named explicitly:
`client.test.ts` tests `./client` (= `frontend/src/api/client.ts`) through vitest (`PG-EV-07`).
11 pre-existing tests + 19 ported = 30.

**File-level green (600s bound), verbatim:**
```
 ✓ src/api/client.test.ts  (30 tests) 21ms
 Test Files  1 passed (1)
      Tests  30 passed (30)
```

**Full frontend suite (600s bound), completed in-bound, verbatim close:**
```
 Test Files  26 passed (26)
      Tests  240 passed (240)
   Duration  5.43s
```
No red, therefore no stash-repro was needed — the suite is green, not green-except-reds. (Only
React Router future-flag stderr warnings appear.)

**Placebo read.** All 12 imported symbols are genuine exports of `client.ts` (grep of `^export
(async )?function`), each ported `describe` calls its function and asserts on the result. No block
was left out.

**Checks.** `eslint src/api/client.test.ts` → exit 0. `tsc --noEmit` → 3 errors, all in
`src/components/WebAlternates.test.tsx` — an untouched file identical to BASE, hence base-resident,
not introduced here (and not a slice gate). CO-100 secret scan on the union file → no
key/secret/token/password/bearer/`sk-` match.

**Diff `--stat` ceiling proof:**
```
 frontend/src/api/client.test.ts | 408 +++++++++++++++++++++++++++++++++++++++-
 1 file changed, 407 insertions(+), 1 deletion(-)
```
Exactly one test file changed; the only other members are the 3 worklog files.

## 3. Findings

- **F1 — "six describes" is 5 new + 1 modified.** The `fetchAiSettings` failure case from #13 is an
  inner `test` added to the pre-existing `describe("fetchAiSettings")`, not a new describe. I folded
  it into that existing block rather than creating a duplicate describe; the union still carries all
  six requested coverage items and no duplicate `updateAiModel`.
- **F2 — `tsc --noEmit` is not clean at BASE.** Three `WebAlternates.test.tsx` TS2739 errors exist on
  the untouched tree. Out of scope; reported, not fixed (would breach the write ceiling).
- No other divergence. PRs #11–#14 remain open, unmerged, unrebased (as required).

## 4. Actual vs budget (units = wall-clock seconds, live clock `PG-IC-07`)

| goal | budget | actual | unit |
|---|---|---|---|
| G0 recon + four diff reads + keeper compare | 120s class | ~110s | elapsed |
| G1 union edit + file vitest + full suite + lint/tsc | 600s class | ~40s | elapsed |
| G2 worklog + report + receipt | 120s class | ~remaining | elapsed |
| overall | packet 2400s / env `RUN_BUDGET_S=2100` | <300s at report write | elapsed |

Real metered spend **$0.000000 USD**, zero metered calls. No command killed; every command ran under
its class bound (120s ordinary / 600s suite / 2400s overall).

## 5. Receipt

- Work commit `WORK_HEAD = 9b585fddf5c0eb19e4324da101700085d279ca3f` (the union edit + the 3 worklog
  files), pushed to `origin/automation`; worktree clean (`CO-55`).
- No push to `storagegenie-evidence`; `{{RECEIPT_CMD}}` not run.
- Note added on WORK_HEAD on `refs/notes/storagegenie-coder-reports`, pushed, then re-fetched into
  the **mapped** local ref `refs/notes/sg137-verify` (`M20`; a default fetch carries no notes).
- Final tip dual-annotated (note-anchor inoculation, SG-092 precedent).
- `note=yes`

Executed output, pasted verbatim:
```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   251cca5..9b585fd  automation -> automation
$ git notes --ref=refs/notes/storagegenie-coder-reports add \
    -m "Dispatch-ID: SG-137 | Report: docs/worklogs/SG-137_report.md | Work-HEAD: 9b585fddf5c0eb19e4324da101700085d279ca3f" \
    9b585fddf5c0eb19e4324da101700085d279ca3f
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   4984a27..35f883d  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg137-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg137-verify
$ git notes --ref=refs/notes/sg137-verify show 9b585fddf5c0eb19e4324da101700085d279ca3f
Dispatch-ID: SG-137 | Report: docs/worklogs/SG-137_report.md | Work-HEAD: 9b585fddf5c0eb19e4324da101700085d279ca3f
```
The final tip is dual-annotated with the same note (note-anchor inoculation, SG-092 precedent);
its `show` is executed and pasted in the final log line. `note=yes`.

## UNCLEAR

- **FIRST READ:** read as a straight fold: take the four one-file diffs, dedupe the one shared
  `describe("updateAiModel")`, ship one file. The tree matched that read exactly — all four diff only
  `client.test.ts`, all four share base `c849088`, BASE is byte-identical to that base.
- **DURING EXECUTION:** the only shape surprise was that the requested "sixth describe" (the
  `fetchAiSettings` failure case, #13) is an inner test on an existing describe, not a new block (F1);
  folded in place. Also `tsc --noEmit` is red at BASE on an untouched file (F2) — reported, untouched.
- **REMAINING:** (a) PRs #11–#14 stay open for the Architect/workstation to close after this lands;
  (b) serving/deploy is out of scope (`PG-PR-04`, packet: no deploy); (c) the `WebAlternates.test.tsx`
  TS2739 base errors remain for a separate slice.
