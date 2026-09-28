SG-134 report — outside-PR audit, tests + cleanup family: 10 diffs read, verdicts, no merges

Dispatch-ID: SG-134
Work dir:   /home/andrei/StorageGenie
origin:     git@github.com:Andovol/StorageGenie.git
BASE ref:   origin/automation
BASE commit: d8077b3c7925be44ae5c8e8f561dc0196b324de6 (start HEAD; tree clean at start)
WORK_HEAD:  <filled in the receipt-paste commit> (work commit; receipt note target)
Model:      opencode-go/deepseek-v4.1-flash   (per process arguments /proc/21363/cmdline `--model`)
Effort:     high                              (per process arguments /proc/21363/cmdline `--variant`)
Coder:      opencode  (env CODER=opencode; OPENCODE_PID=21363)
Contract:   echo 0.40.0 — source `/home/andrei/storagegenie-contract/VERSION` (published tip `f26dbd3`);
            `RULES.md` sha256 `5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`
            equals payload `RULES.sha256`. Recorded 0.40.0 == published. (`.rules-cache/` absent on host.)
Spend:      real $0.000000 USD · zero metered calls · zero suite runs · zero live calls · zero container execs.
Gates:      DATABASE none · Restart none · Deploy none. Role guard held (Coder only; no dispatch verb).
Guards:     PG-EV-01 · PG-EV-02 · PG-EV-05 · PG-EV-10 · PG-IC-01 · PG-IC-07 · PG-IC-09 · PG-SC-09

## 0. Method and evidence

- `gh` is **unauthenticated** on this host (SG-133 F1, re-confirmed; `GH_TOKEN`/`GITHUB_TOKEN` unset and no
  `~/.config/gh/hosts.yml`). Not retried, not worked around. Substituted the git-native equivalent, which is
  still bytes: `git ls-remote origin 'refs/pull/*'` → `refs/pull/N/head` mapped to local `refs/audit/pr/N`,
  then `git diff <merge-base>...<head>` per PR. Branch names recovered by SHA match against
  `git ls-remote origin 'refs/heads/*'`.
- Every PR number, head SHA, branch, merge-base and diffstat was **re-measured on the target** (`PG-IC-09`).
  All 10 `refs/pull/N/head` resolved — **none closed or retargeted** between the packet and this run.
- **8 of 10 measured diffstats equal the packet table exactly.** Two differ (F1): `#28`/`#29` are new-file
  additions with **0 deletions** each; the packet's `-1` is wrong. No other difference to report.
- All 10 diffs were fetched and read (bytes). No vacuous pass: every verdict cites the hunk it rests on.
- Suites deliberately **not** run (forbidden by this packet); the audit is static (source/config reads +
  diff reads), which is why "does the test drive the real function" is answered from the export surface, not
  a green run. Where a test's validity depends on a matcher/import existing, that was verified by reading the
  target source and `vite.config.ts`/`test-setup.ts` — not assumed.

## 1. Per-PR table (10 rows, measured from the commit)

| PR | branch | merge-base | measured diffstat | verdict | reason (one line) | lesson |
|----|--------|-----------|-------------------|---------|-------------------|--------|
| #30 | `code-health/planning-exports-4909125834173332214` | `7d207bf` | **+0/-0, 0 files** | **CLOSE** | Provably empty: `git diff` = 0 bytes and head tree `2ddb1f7737c67c0033b4b95b4cdd8b1303f6c59e` == merge-base tree (`7d207bf`); the `__all__` change was already on automation — nothing to land. | Bot branch re-committed an already-landed change as a no-op; a bot PR must be diff-checked before it is filed (process hygiene). |
| #2 | `code-health/chat-init-imports-43131338201651046` | `33460cd` | +7/-7, 1 file | **MERGE** | Explicit `X as X` re-export aliases for the exact 7 names already listed in `__all__`; Python binding is identical (`as` does not change the bound object), so behaviour is preserved. | N/A |
| #31 | `fix/health-check-logger-3533530181709914815` | `7d207bf` | +8/-3, 2 files | **MERGE** | `db_status`→`{"status","db","storage"}` body + 200/503 shape unchanged; logged exception is the `SELECT 1` probe error (credentialless SQLite DSN, no rows). Evidence below. | **Defect fixed:** `except Exception: pass` on the `G-T9` proof route silently swallowed DB health failures (F6). Let through because `test_health.py` asserted only status/body, never the log — no packet/audit checked exception silence. |
| #13 | `test/add-fetch-ai-settings-tests-3203092785360383794` | `c849088` | +55/-1, 1 file | **REWRITE-AS-SLICE** | Real tests (`fetchAiSettings` failure + `updateAiModel`), but same file **and same insert region** as #11/#12/#14; duplicates `describe("updateAiModel")` with #12. Fold into one combined test slice. | Packet overlap premise false (F2); four PRs on one file cannot each land as-is. |
| #11 | `test/api-patch-unit-tests-9040774963283596966` | `c849088` | +75/-1, 1 file | **REWRITE-AS-SLICE** | Real `apiPatch` success/detail/JSON-fallback tests, but collides with #12/#13/#14 on the shared import line 2 and the same insert region. Fold into one combined test slice. | Packet overlap premise false (F2). |
| #29 | `test/add-page-container-style-unit-tests-7012541858369455202` | `7d207bf` | **+90/-0**, 1 file | **MERGE** | New file; drives the real `pageContainerStyle`/`PageContainer` exports (all 5 imported names verified present in `PageContainer.tsx`); `toBeInTheDocument`/`toHaveStyle` backed by `test-setup.ts` jest-dom. | Packet diffstat `-1` wrong (measured 0) — F1. |
| #28 | `add-web-alternates-unit-tests-8021906607013009028` | `7d207bf` | **+93/-0**, 1 file | **MERGE** | New file; drives the real `WebAlternates` component + `WebAlternate` type (verified); asserts the SG-118 discipline (raw source URL never visible text). | Packet diffstat `-1` wrong (measured 0) — F1. |
| #12 | `test/add-api-put-tests-5989383413136137443` | `c849088` | +95/-1, 1 file | **REWRITE-AS-SLICE** | Real `apiPut` tests, but collides with #11/#13/#14 and duplicates `describe("updateAiModel")` with #13. Fold into one combined test slice. | Packet overlap premise false (F2); duplicate coverage (F5). |
| #14 | `test/add-api-post-tests-10427039796881282869` | `c849088` | +210/-1, 1 file | **REWRITE-AS-SLICE** | Real `apiPost` + helper tests (`candidateDecision`/`sendChat`/`runPlanning`/`resolveReviewTask`), but collides on the shared import line and insert region. Fold into one combined test slice. | Packet overlap premise false (F2). |
| #4 | `refactor/household-selector-7969942473370878659` | `33460cd` | +167/-66, 8 files | **REWRITE-AS-SLICE** | Extraction equivalence across the 5 pages holds (see §1b), but the diff also **commits `frontend/preview.log`**, a `vite preview` console artifact (not gitignored). Drop it; the refactor itself is sound. | Committed build artifact / scope creep (F4). |

Verdict counts: **MERGE 4** (#2, #31, #29, #28) · **REWRITE-AS-SLICE 5** (#11, #12, #13, #14, #4) ·
**CLOSE 1** (#30). Merges are recommendations only — owner yes required; nothing merged, closed or rebased.

### 1a. Representative hunks the verdicts rest on

**#30 — the CLOSE proof (empty diffstat + empty diff, quoted verbatim):**
```
$ git diff --numstat 7d207bf...refs/audit/pr/30
(no output)
$ git diff 7d207bf...refs/audit/pr/30 | wc -c
0
$ git rev-parse refs/audit/pr/30^{tree}  ->  2ddb1f7737c67c0033b4b95b4cdd8b1303f6c59e
$ git rev-parse 7d207bf^{tree}           ->  2ddb1f7737c67c0033b4b95b4cdd8b1303f6c59e
```
The head commit `7a2ad05` ("Ensure __all__ re-exports in planning module") has the *identical tree* to its
merge-base: a no-op commit. This is a CLOSE, not a pass.

**#2 — behaviour-preserving alias form:**
```
-    SUPPORTED_CATEGORIES,
-    UnsupportedCategoryError,
+    SUPPORTED_CATEGORIES as SUPPORTED_CATEGORIES,
+    UnsupportedCategoryError as UnsupportedCategoryError,
```
`__all__` is byte-for-byte unchanged and lists the same 7 names; `as` only re-binds the same object.

**#31 — exception no longer silent (defect fix):**
```
-    except Exception:
-        pass
+    except Exception as exc:
+        logger.warning("Database health check probe failed: %s", exc, exc_info=True)
```
Body/status unchanged (still `{"status","db","storage"}` with 200/503). Test delta only adds `caplog`:
```
+    assert "Database health check probe failed" in caplog.text
+    assert "database probe failed" in caplog.text
```

**#11–#14 — all four mutate the same import line and insert in the same region:**
```
-import { buildUrl, apiGet, fetchAiSettings, fetchPlanningSuggestions } from "./client";
+import { buildUrl, apiGet, apiPatch, fetchAiSettings, fetchPlanningSuggestions } from "./client";   (#11)
+import { buildUrl, apiGet, apiPut, fetchAiSettings, updateAiModel, fetchPlanningSuggestions } ...   (#12)
+import { buildUrl, apiGet, fetchAiSettings, updateAiModel, fetchPlanningSuggestions } ...           (#13)
+import { buildUrl, apiGet, apiPost, fetchAiSettings, fetchPlanningSuggestions, candidateDecision,
+         sendChat, runPlanning, resolveReviewTask } ...                                              (#14)
```
All four insert after `describe("apiGet", …)` (line ~112); #13/#12 both add a `describe("updateAiModel")`.

**#4 — the artifact that blocks an as-is merge:**
```
diff --git a/frontend/preview.log b/frontend/preview.log
new file mode 100644
+> storagegenie-frontend@0.1.0 preview
+> vite preview
+  ➜  Local:   http://localhost:4173/
```
Absent from `.gitignore`/`frontend/.gitignore` (`git check-ignore` says NOT ignored).

### 1b. #4 extraction equivalence (across its 8 files) — no behaviour drift found

Callers updated: `CapturePage`, `CatalogPage`, `ChatPage`, `InboxPage`, `PlanningPage` → the new
`HouseholdSelector`. Checked case-by-case against the base source at `origin/automation`:

- `CatalogPage`: base rendered `<option value="">No households</option>` **only** when
  `(!households || households.length === 0)`; the extraction passes `emptyOptionLabel={… ? "No households" : ""}`
  and the component renders the empty option only when the label is truthy (`""` is falsy, and `undefined`
  default is never reached because the prop is always supplied). Equivalent. `showLabel={false}` reproduces
  the bare `<select>` (base had no label).
- `CapturePage`: base had **no** empty option; extraction passes `emptyOptionLabel=""` → falsy → no empty
  option. `labelStyle={{fontSize:13}}` and `selectStyle={{padding:6,borderRadius:6,marginLeft:6}}` preserved
  verbatim. Equivalent.
- `ChatPage` / `PlanningPage` / `InboxPage`: base `<label>Household <select>…<option value="">Select
  household</option>…`; extraction relies on the defaults `showLabel=true`, `emptyOptionLabel="Select
  household"` and renders `Household {select}`. `onChange` still writes `household_id` to `localStorage`.
  Equivalent.
- The only non-equivalent code is the artifact `frontend/preview.log` (not product behaviour). The
  `households as Household[] | undefined` cast is a no-op (`useHouseholds()` already returns
  `UseQueryResult<Household[]>`), so it is noise, not drift.

### 1c. #31 secret scan (log-line carries no credential/row bytes) — asserted

- The logged exception comes from `db.execute(text("SELECT 1"))`. The configured DSN is credentialless
  local SQLite (`sqlite:////data/db/storagegenie.db`), and `SELECT 1` returns no rows, so the `%s` argument
  and the `exc_info=True` traceback cannot carry a credential or row bytes. Assertion holds for the current
  datastore.
- **Residual (out of slice):** `exc_info=True` will print whatever the driver puts in the exception text. If
  the datastore is ever declared with a credentialed DSN (the `CODER_PRODUCTION.md` trigger), the SQLAlchemy
  error text can echo the connection URL including its password. Recommend redaction *if and when* that
  trigger fires; not a blocker today.

## 2. Overlap

### 2a. Within this 10-PR set

| cluster | measured | relation | resolution |
|---|---|---|---|
| `client.test.ts` {#11,#12,#13,#14} | **CONFIRMED** — all four edit `frontend/src/api/client.test.ts`, hit the **same import line (2)** and insert in the same region (~line 112) | **CONFLICT / SERIALIZER** — only one can land as-is; the other three rebase or are folded in | Fold #11–#14 into **one** combined test-coverage slice; de-duplicate the `updateAiModel` block (#12 == #13, F5) |
| `PageContainer.test.tsx` {#29} | new file, no other PR touches it | independent | MERGE |
| `WebAlternates.test.tsx` {#28} | new file, no other PR touches it | independent | MERGE |
| `chat/__init__.py` {#2} · `health.py`+`test_health.py` {#31} · routes/components {#4} | mutually disjoint files | independent | MERGE #2/#31; REWRITE #4 (drop artifact) |

**The packet's expectation that the test PRs are "independent single files (no overlap expected)" is false
(F2):** each is a single file, but **four of the six share one file** (`client.test.ts`) with same-region
hunks. This is the one real serializer in the set.

### 2b. Against SG-133's merge order (the 14 perf PRs)

SG-133's landable set touches: `backend/app/api/v1/assets.py`, `dedup.py`,
`frontend/src/components/ProductCard.tsx`, `google_taxonomy.py`, `analytics/service.py`,
`planning/service.py`, `chat/service.py`, `.jules/bolt.md`.

- `#2` edits `backend/app/services/chat/__init__.py` — the **same package** as SG-133's #18
  (`chat/service.py`) but a **different file**, so no textual conflict and no forced rebase; adjacent, not
  serializing.
- `#31` (`health.py`, `test_health.py`), `#4` (routes + `HouseholdSelector.*` + `preview.log`), and all six
  test PRs touch **no** file in SG-133's set. `#4` adds a component in the same directory as SG-133's
  `ProductCard.tsx` but a distinct file.
- **Conclusion: nothing in this slice serializes against SG-133's merge order.** The two families are
  file-disjoint.

## 3. Findings (numbered; correcting the packet counts as a result)

- **F1 — two diffstats differ from the packet.** `#28` measured `+93/-0` and `#29` measured `+90/-0`; the
  packet says `+93/-1` and `+90/-1`. Both are `new file mode` additions, so 0 deletions is correct. The
  other 8 rows equal the packet exactly. (A difference is a finding.)
- **F2 — the overlap premise is false.** "test PRs are independent single files (no overlap expected)" —
  measured truth: #11/#12/#13/#14 are four PRs on the *same* file with same-region hunks (real serializer).
  The set is **not** 6 independent tests; it is 2 independent new files + 1 four-way-contended file.
- **F3 — #30 is provably empty** (head tree == merge-base tree, 0-byte diff), so it is a CLOSE, quoted with
  proof rather than a pass.
- **F4 — #4 commits a build artifact.** `frontend/preview.log` (vite `preview` stdout) rides a refactor PR
  and is not gitignored. Scope creep; the refactor is otherwise equivalent. The slice must drop the file
  (and consider a `*.log` gitignore rule).
- **F5 — duplicate coverage** between #12 and #13 (`describe("updateAiModel")`); a side effect of the
  four-way split. The combined slice should keep one.
- **F6 — the slice's one defect-fix lesson (#31).** The `G-T9` health route had
  `except Exception: pass`, silently degrading `db:"error"` with zero operator signal. It was let through
  because `test_health.py` asserted the response body only (never the log), and no packet/audit inspected
  exception-silence on the health proof route. Lesson applied: a proof route must both surface and *log*
  failure; test the log, not just the body.
- **F7 — `gh` remains unauthenticated** (SG-133 F1 re-confirmed). All metadata came from the git-native path;
  PR titles/authors/`OPEN|CLOSED` API state were not readable, though bytes and refs sufficed.
- **F8 — contract echo clean and equals published** (0.40.0, hash `5b656293…`); not an echo-diff finding.

## 4. Read-only proof

- Writes in this slice: only `docs/worklogs/SG-134.log`, `docs/worklogs/SG-134_report.md`,
  `docs/worklogs/SG-134_verify.log`. No product-file edit, no merge, no close, no push except the worklog
  commit + notes receipt, no suite run, no container exec, no live call, no credential copied (`CO-100`).
- `git status` at commit time (before staging) shows only the three worklog paths; `git diff` over the rest
  of the tree is empty. Evidence pasted in `SG-134_verify.log` and reproduced at receipt time.
- The many `git fetch` calls wrote only local refs (`refs/audit/pr/N`, `refs/remotes/origin/automation`),
  never the worktree.

## 5. Actual vs budget

| goal | budget | actual | unit |
|---|---|---|---|
| G0 fetch + enumerate 10 PRs | ~300s | ~120s | elapsed |
| G1 audit 10 diffs + overlap + order | ~700s | ~110s | elapsed |
| G2 worklog + report + receipt | ~200s | (this step) | elapsed |
| overall | 2400s cap / ~1200s expected | well under cap at all transitions | elapsed |

`RUN_BUDGET_S` lane cap not approached; the 1500s stop point was not reached (all 10 audited well before
it). No command was killed; every command ran under a 120s ordinary bound. Real metered spend $0.000000 USD,
zero metered calls.

## 6. Receipt

- Work commit `WORK_HEAD = 0f02d7089ec7d5f5562f9e10d5f778d8a6bb5cf5`, pushed to `origin/automation`
  (`d8077b3..0f02d70`).
- Note added on WORK_HEAD on `refs/notes/storagegenie-coder-reports`, pushed, then re-fetched into the
  **mapped** local ref `refs/notes/sg134-verify` (a default fetch carries no notes; a bare refspec rewrites
  only FETCH_HEAD — mapped per `M20`). `show` output pasted verbatim (filled in the receipt-paste commit).
- Final tip dual-annotated with the same note (note-anchor inoculation, SG-092 precedent).
- `note=yes`

<!-- RECEIPT-PASTE -->

## UNCLEAR

- **FIRST READ:** the packet's "test PRs are independent single files (no overlap expected)" read as a
  *fact about the set*; on the target it is false — four of six share `client.test.ts` at the same import
  line and insert region, so the six collapse to three independent units (one of which is four-way contended).
  The packet also carried `-1` deletions for two new-file PRs that have none.
- **DURING EXECUTION:** `#4`'s extraction is genuinely equivalent across all five pages, yet the diff is not
  mergeable as-is purely because of one stray `frontend/preview.log`; and `#31` — the only PR that fixes a
  real defect — is also the one touching the `G-T9` proof route, so its merge should carry the redaction
  caveat if the datastore DSN ever gains credentials.
- **REMAINING:** owner decision on (a) folding #11–#14 into one combined `client.test.ts` coverage slice
  (dropping the duplicate `updateAiModel` block), (b) dropping `frontend/preview.log` from #4 (plus a
  `*.log` gitignore), and (c) closing #30 as an empty no-op. The `health.py` credentialed-DSN redaction and
  the bot-PR diff-check hygiene are out of this slice's write ceiling.
