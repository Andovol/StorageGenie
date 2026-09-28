SG-133 report — outside-PR audit, perf family: 14 diffs read, verdicts, no merges

Dispatch-ID: SG-133
Work dir:   /home/andrei/StorageGenie
origin:     git@github.com:Andovol/StorageGenie.git
BASE ref:   origin/automation
BASE commit: 3ce5ba1218d7254726eb9077908746adaa4528ff (start HEAD; tree clean at start)
WORK_HEAD:  69d98266c28492dbc5a7b298d0b69bc2892cc87e (work commit; receipt note target)
Model:      opencode-go/deepseek-v4.1-flash   (per process arguments /proc/2028/cmdline `--model`)
Effort:     high                              (per process arguments /proc/2028/cmdline `--variant`)
Coder:      opencode  (env CODER=opencode; wrapper /usr/local/lib/dispatch/run-coder SG-133)
Contract:   echo 0.40.0 — source `/home/andrei/storagegenie-contract/VERSION` (published tip `f26dbd3`);
            `RULES.md` sha256 `5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`
            equals payload `RULES.sha256`. Recorded 0.40.0 == published. (`.rules-cache/` absent on host.)
Spend:      real $0.000000 USD · zero metered calls · zero suite runs · zero live calls · zero container execs.
Gates:      DATABASE none · Restart none · Deploy none. Role guard held (Coder only; no dispatch verb).
Guards:     PG-EV-01 · PG-EV-02 · PG-EV-05 · PG-EV-10 · PG-IC-01 · PG-IC-07 · PG-IC-09 · PG-SC-09

## 0. Method and evidence

- `gh` is **unauthenticated** on this host (`GH_TOKEN`/`GITHUB_TOKEN` unset, no `~/.config/gh/hosts.yml`)
  → FINDING **F1**. `gh pr view`/`gh pr diff` were therefore unavailable; substituted the git-native
  equivalent, which is still bytes: `git ls-remote origin 'refs/pull/*'` → `refs/pull/N/head` mapped
  to local `refs/audit/pr/N`, then `git diff <merge-base>...<head>` per PR.
- Every PR number, head SHA, branch, merge-base and diffstat was **re-measured on the target**
  (`PG-IC-09`). **All 14 diffstats equal the packet table exactly** (`+/-` and file count) — no
  difference to report; branch names not given in the packet are quoted below.
- No PR was closed/retargeted between the packet and this run: `refs/pull/N/head` resolved for all 14.
- Verification of behaviour-preservation used the immutable `merge-base...head` diff plus reads of the
  base source at `origin/automation`; no working tree was modified (`git apply --check` only).
- No vacuous pass: all 14 diffs were fetched and read (bytes); every verdict below cites the hunk it
  rests on. Suites deliberately **not** run (`CO-101` not engaged; forbidden by this packet).

## 1. Per-PR table (14 rows, measured from the commit)

| PR | branch | merge-base | measured diffstat | verdict | reason (one line) | lesson |
|----|--------|-----------|-------------------|---------|-------------------|--------|
| #5 | `bolt-optimize-asset-evidence-query-8373180077199252319` | `33460cd` | +21/-19, 2 files | **CLOSE** | Product change already on `origin/automation` (`assets.py:104-108` JOIN is identical); only remaining delta is an add/add conflict on `.jules/bolt.md`. | PR body merged but PR left open — no close-on-merge discipline for the bot PR; found only by comparing head content against the live tree. |
| #15 | `perf/optimize-evidence-id-validation-4026608314611835728` | `c849088` | +3/-1, 1 file | **MERGE** | `evs = db.query(Evidence).filter(id.in_(evidence_ids))` + `ev_map` preserves per-id 404 order, household check and duplicates; applies clean. | N/A |
| #16 | `perf/asset-assertions-relationship-13770567831920213516` | `c849088` | +31/-17, 3 files | **REWRITE-AS-SLICE** | `asset.assertions` is a lazy relationship → the **same per-asset SELECT**, so "N+1 moved, not removed"; import hunk conflicts with current `assets.py`. | N/A |
| #17 | `bolt-optimize-asset-subqueries-13542091513951877465` | `9baba79` | +9/-4, 1 file | **MERGE** | Core `select(asset_evidence.c.asset_id)` ≡ `db.query(...)` subquery in `_apply_asset_filters`/`asset_facets`; applies clean; no query-semantics drift. | N/A |
| #18 | `bolt/batch-catalog-context-queries-14803786461694813844` | `9baba79` | +90/-9, 3 files | **MERGE** | Batches assertions + attributions in chat **and** planning; `_date_assertion_value` (str-only) and `_source_attributions` (retrieved_at desc) semantics preserved; applies clean; superset of #19. | N/A |
| #19 | `bolt-batch-planning-catalog-assertions-7675598486104915559` | `9baba79` | +71/-46, 1 file | **CLOSE** | Same planning `build_catalog` batching as #18's planning half; #18 also covers chat, so #19 is a strict subset. | N/A |
| #20 | `bolt/optimize-dedup-queries-75216830359788930` | `9baba79` | +68/-27, 2 files | **MERGE** | Pre-fetch of household phash rows + identifier map preserves `_similar_matches`/`_identifier_collisions` semantics (default `None` keeps standalone paths); applies clean. | N/A |
| #21 | `bolt/batch-analytics-assertions-16194283105033862914` | `1d8e9a9` | +43/-6, 3 files | **CLOSE** | Stale duplicate of #24 (base analytics blob `1c0c550` vs current `94e3c85`) **and** smuggles an unrelated tesseract `skipif` into a perf PR. | Defect fixed: OCR test hard-fails where `tesseract` is absent. Let through because the bot PR was never read as a slice, so scope creep rode a perf change; see `D336`. |
| #22 | `bolt/optimize-google-taxonomy-inverted-index-14097243351672316017` | `fe7d31f` | +30/-1, 2 files | **CLOSE** | Inverted-index variant superseded by #27 (which adds `_score_candidates` LRU + empty-token guard); both rewrite the same `resolve_google_type` lines. | N/A |
| #23 | `bolt/analytics-batch-assertions-10419505610984377970` | `3cdf563` | +34/-20, 2 files | **CLOSE** | Stale duplicate of #24; deletes `_active_assertion`/`_classification_slug`/`_active_expiry_date` (no external importer, so harmless) — pure churn vs #24. | N/A |
| #24 | `bolt/batch-analytics-assertions-15609253117918485373` | `43cd544` | +73/-3, 2 files | **MERGE** | Freshest base (analytics blob == current `94e3c85`); `_parse_category_slug`/`_parse_expiry_date` semantics match `_classification_slug`/`_active_expiry_date`; applies clean. | N/A |
| #25 | `bolt-taxonomy-lru-cache-14439831709962882905` | `7d207bf` | +20/-7, 2 files | **CLOSE** | Full-scan `_score_proposal` LRU conflicts with #22/#27 on the same lines and is dominated by #27's index+cache. *(Packet placed #25 in "singles" — see F3.)* | N/A |
| #26 | `bolt/memoize-product-card-7303002050292754265` | `7d207bf` | +9/-3, 1 file | **MERGE** | `memo(function ProductCard(...))` is behaviour-preserving (React component identity/name kept); applies clean. Impact **unproven** — depends on parent prop identity (`item`/`onSelect`). | N/A |
| #27 | `jules-12599582609388419957-f869741f` | `7d207bf` | +46/-7, 2 files | **MERGE** | Inverted token-index + `_score_candidates` LRU + empty-token guard; sort key `(-score, node_id)` unchanged so result order is preserved; best of the three taxonomy variants. | N/A |

Verdict counts: **MERGE 8** (#15,#17,#18,#20,#24,#26,#27 + note #16 needs rewrite), **REWRITE-AS-SLICE 1** (#16), **CLOSE 6** (#5,#19,#21,#22,#23,#25). Merges are recommendations only — owner yes required; nothing merged.

### 1a. Representative hunks the verdicts rest on

#5 already merged (`origin/automation:backend/app/api/v1/assets.py:104-108`):
```
evs = (
    db.query(Evidence)
    .join(asset_evidence, Evidence.id == asset_evidence.c.evidence_id)
    .filter(asset_evidence.c.asset_id == asset.id)
    .all()
)
```
#16 relationship (the lazy-load that does not batch):
```
+    assertions = [ ... for ass in asset.assertions ]
```
plus `Asset.assertions: Mapped[List["Assertion"]] = relationship(..., order_by="Assertion.field_path")`
#17 subquery swap:
```
+        evidence_subquery = select(asset_evidence.c.asset_id)
-            query = query.filter(Asset.id.in_(db.query(asset_evidence.c.asset_id)))
+            query = query.filter(Asset.id.in_(evidence_subquery))
```
#24 batch fetch (latest-per-asset via desc + first-wins):
```
+ _fetch_active_assertion_maps(db, active_ids): .order_by(Assertion.created_at.desc())
+    for assertion in assertions:
+        if assertion.field_path == CLASSIFICATION_FIELD and assertion.asset_id not in classification_map:
```
#27 winner (index + cached scoring + empty guard):
```
+ top = list(_score_candidates(proposal_tokens))
+    if not proposal_tokens: return Resolution(UNCLEAR, ...)
```

## 2. Overlap matrix

| cluster (packet) | measured | relation | resolution |
|---|---|---|---|
| analytics-assertion batching {#21,#23,#24} | **CONFIRMED** — all rewrite `_aggregate_assets` in `backend/app/services/analytics/service.py` | **CONFLICT** (same region); #24 base blob = current automation (`94e3c85`), #21/#23 base `1c0c550` stale | MERGE **#24**; CLOSE #21,#23 |
| taxonomy inverted index {#22,#27} | **CONFIRMED**, **plus unlisted #25** (also `google_taxonomy.py`, same `resolve_google_type`) | **CONFLICT** (three-way, same lines) | MERGE **#27**; CLOSE #22,#25 |
| planning-catalog assertion batching {#18,#19} | **CONFIRMED** — both rewrite `planning/service.py:build_catalog` | **CONFLICT**; #18 also edits `chat/service.py` (unique) | MERGE **#18**; CLOSE #19 |
| asset-evidence/subquery {#5,#16,#17} | **PARTIAL** — #5/#17 hit evidence/subquery; **#16 does not** (assertions relationship) | #5 already merged; #16 conflicts on imports | CLOSE #5; REWRITE #16; MERGE #17 |
| singles {#15,#20,#25,#26} | #15,#20,#26 truly single; **#25 is not** | #25 collides with taxonomy cluster | MERGE #15,#20,#26; CLOSE #25 |

**Unlisted cross-cutting overlap — `.jules/bolt.md` (F5):** eight PRs append a journal entry to the same
file (#18,#20,#21,#22,#23,#24,#25,#27) and #5 adds an entirely different file. Two insertion points exist
(after the title: #24,#25,#27; at EOF: #18,#20,#21,#22,#23), so **every pair among the appenders conflicts**
at the append/insert hunk. This is a merge-mechanics conflict, not a code conflict; each landing PR forces
a rebase of the others' journal line.

## 3. Safe merge order (owner yes required; sequence, with the reason each later step needs a rebase)

1. **#15** — isolated `assets.py:post_asset_evidence`; clean.
2. **#17** — isolated `assets.py` filter/facets regions; clean.
3. **#20** — isolated `dedup.py`; clean.
4. **#26** — isolated frontend `ProductCard.tsx`; clean.
5. **#27** — taxonomy winner; then #22 and #25 are CLOSED (cannot land in any order together).
6. **#24** — analytics winner; then #21 and #23 are CLOSED (cannot land in any order together).
7. **#18** — chat+planning; then #19 is CLOSED (same-region duplicate).
8. **#16** — **only after REWRITE** (batch-load via `selectinload` or drop the relationship) **and a rebase**
   (its import hunk conflicts with current `assets.py`; current file already carries SG-113 locations +
   `lifecycle` imports absent from its base).

**Pairs that cannot go in any order:** {#21,#23,#24} (analytics), {#22,#25,#27} (taxonomy), {#18,#19}
(planning) — same-region rewrites; and #5 against anything (already merged + `.jules/bolt.md` add/add).
After each landing of an appender (#18,#20,#24,#27), the remaining appenders must rebase `.jules/bolt.md`
(F5). #15/#17/#16 all touch `assets.py` but distinct, non-adjacent regions; #16's blocker is its own stale
imports, not #15/#17.

## 4. Findings / disagreements with the packet (reported, not bent)

- **F1 — `gh` unauthenticated.** No `GH_TOKEN`/`GITHUB_TOKEN`, empty `~/.config/gh/hosts.yml`. `gh pr view`
  could not run; git-native `refs/pull/*` reads used instead. Not a STOP — `git` reached all 14 heads.
- **F2 — #5 is already merged.** Its product hunk is present verbatim on `origin/automation`; the open PR
  is stale. Packet listed it as an audit target.
- **F3 — #25 is mis-labelled "single".** It rewrites the taxonomy resolver and conflicts with #22/#27.
- **F4 — #16 is mis-labelled "asset-evidence/subquery".** It adds an `Asset.assertions` relationship and
  rewrites assertion serialization; it does not touch the evidence/subquery path.
- **F5 — `.jules/bolt.md` pairwise conflict** across 8 PRs (unlisted in the packet's overlap expectation).
- **F6 — #21 bundles an unrelated test fix** (`@pytest.mark.skipif(shutil.which("tesseract") is None)`) in
  a perf PR; recorded as the slice's one defect-fix lesson.
- **F7 — cluster bases differ by age:** #24 == current automation; #21/#23 stale; #22/#25/#27 == current
  taxonomy blob (so those three conflict with each other directly).
- **F8 — contract echo is clean and equals published** (0.40.0, hash `5b656293…`); not an echo-diff finding.
- All 14 diffstats re-measured **equal** the packet's table; no numeric difference to report.

## 5. Read-only proof

- Writes in this slice: only `docs/worklogs/SG-133.log`, `docs/worklogs/SG-133_report.md`,
  `docs/worklogs/SG-133_verify.log`. No product-file edit, no merge, no close, no push except the worklog
  commit + notes receipt, no suite run, no container exec, no live call, no credential copied (`CO-100`).
- `git status` / `git diff` evidence pasted in `SG-133_verify.log` and reproduced at receipt time.
- Working-tree writes came only from the `write` tool into the three worklog paths; the many `git fetch`
  calls wrote only local refs (`refs/audit/pr/N`), never the worktree.

## 6. Actual vs budget

| goal | budget | actual | unit |
|---|---|---|---|
| G0 fetch + enumerate 14 PRs | ~300s | ~120s | elapsed |
| G1 audit 14 diffs + overlap + order | ~1000s | ~340s | elapsed |
| G2 worklog + report + receipt | ~200s | (this step) | elapsed |
| overall | 2400s cap | well under cap at all transitions | elapsed |

`RUN_BUDGET_S` lane cap not approached; no 1800s stop point reached (all 14 audited). Real metered spend
$0.000000 USD, zero metered calls.

## 7. Receipt

- Work commit `WORK_HEAD = 69d98266c28492dbc5a7b298d0b69bc2892cc87e`, pushed `3ce5ba1..69d9826`.
- Notes ref `refs/notes/storagegenie-coder-reports` advanced `cb1e170..6c940df`; note added on WORK_HEAD,
  pushed, then re-fetched into the **mapped** local ref `refs/notes/sg133-verify` (a default fetch carries
  no notes; a bare refspec rewrites only FETCH_HEAD — mapped per `M20`). `show` output pasted verbatim:

```
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg133-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg133-verify
$ git notes --ref=refs/notes/sg133-verify show 69d98266c28492dbc5a7b298d0b69bc2892cc87e
Dispatch-ID: SG-133 | Report: docs/worklogs/SG-133_report.md | Work-HEAD: 69d98266c28492dbc5a7b298d0b69bc2892cc87e
```
- Final tip dual-annotated with the same note (note-anchor inoculation, SG-092 precedent).
- `note=yes`

## UNCLEAR

- **FIRST READ:** `gh` was expected usable ("gh reads existing auth only"); it is unauthenticated on this
  host, so all PR metadata came from `git ls-remote` + `refs/pull/*` — enough for bytes, insufficient to
  read PR titles/authors/state (`OPEN`/`CLOSED`) via the API.
- **DURING EXECUTION:** the effective merge surface is smaller than the PR count implies — 6 of 14 are
  duplicate/superseded variants of 3 optimizations, and an unlisted `.jules/bolt.md` append conflict
  couples 8 of them; the packet's "singles" and "asset-evidence" clusters each contain one mis-clustered PR.
- **REMAINING:** owner decision on which variant per cluster to land (#24 over #21/#23; #27 over #22/#25;
  #18 over #19) and the #16 rewrite/rebase; no destination beyond this report was written for the bot-PR
  close-on-merge hygiene (F2) or the `.jules/bolt.md` journal-conflict (F5), which are out of this slice's
  write ceiling.
