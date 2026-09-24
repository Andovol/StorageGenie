SG-112 report — Candidate merge: one proposed survivor, terminal losers, asset MERGED redirect
============================================================================================

Verdict: SHIPPED. `POST /v1/candidates/merge` merges one-or-more `proposed` duplicates into one
survivor that KEEPS its fields, STAYS `proposed` (merge never auto-accepts) and takes the exact union
of every participant's evidence; each loser ends terminal (`merged`) carrying `merged_into`, readable
back through the candidates route, and is undecidable (409). Every illegal shape is refused BEFORE any
write. `POST /v1/assets/{id}/merge` makes SG-111's reserved `ACTIVE -> MERGED` meaningful with no new
table: status plus a `merge.merged_into` assertion naming the winner plus an audit row; a MERGED asset
with no redirect reads terminal, never dangling. The served backend was rebuilt and recreated exactly
once; the live data stood still. $0.000000 — no metered call exists on any path.

Contract echo + source path
---------------------------
Contract 0.33.0 — installed global rules file hashed against the payload, never checkout-vs-stamp (G-L1/M3).
- source: `/home/andrei/storagegenie-contract/VERSION` = `0.33.0`
- source HEAD: `b232b845d74e89cb346c60fa4b9a40ec401c42dd` = "Contract payload 0.33.0"
- `sha256sum /home/andrei/storagegenie-contract/RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`
- payload `/home/andrei/storagegenie-contract/RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46 RULES.md` -> match.
- recorded `0.33.0` == published `b232b84`. Clean.

Model / effort / spend (CO-78)
------------------------------
Read from the process arguments, never a system-prompt identity line.
- argv (`/proc/3825216/cmdline`): `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>`
- effort = `high` (from `--variant high`)
- model = `unknown` — no `--model` flag present and no provider metadata readable; the packet states
  the CLI default model is omitted by policy, and I refuse to guess a plausible id.
- Spend real $ = `$0.000000` (zero provider calls; no metered call exists on any path).

Refs
----
- Work dir `/home/andrei/StorageGenie`, origin `git@github.com:Andovol/StorageGenie.git`
- BASE_REF = `origin/automation`
- BASE_RESOLVED = `7043285f079966afb5c6e511d9a0f5e78cc79df4` (== start HEAD; the packet commit)
- WORK_HEAD = `31e58f82558e649fc0fdf9ad19ac2274cb746747`

Premise verification — corrections are worth more than agreement
----------------------------------------------------------------
Every packet premise re-verified against the tree; the counts, paths and line numbers held. Two
nuances are reported rather than bent:

1. **The decision guard refused `{"rejected", "split"}` at `api/v1/candidates.py:37` — VERIFIED, and
   the `Literal` at `:17` is exactly `["accept","edit","hold","reject"]` — VERIFIED.** No merge route
   and no `merge_candidates` def existed. The only `merge` in the candidates paths was
   `merge_web_fields` (`services/candidates.py:347`), the SG-082 web-field conflict rule — a DIFFERENT
   concept that shares the word. The packet's "no `merge` route/def in candidates paths" is true of
   the review action; the raw grep is quoted in full in `SG-112_verify.log` so the shared word is
   visible, not hidden.
2. **"open duplicate tasks on losers resolved" vs "losers carry no open review tasks" needed a
   decision.** The tree has one duplicate task type: `identifier_collision`
   (`services/dedup.py:184`, `subject_ref=candidate.id`); there is NO generic "duplicate" task type.
   I read the two sentences as: the task types that must be CLEAR on a loser are every open task
   type EXCEPT the duplicate-identifier collision, which the merge itself resolves (with an audit
   row, the split `candidate.multi_item` shape at `:1096-1111`). Concretely
   `MERGE_RESOLVED_TASK_TYPES = ("identifier_collision",)` resolves; `candidate.multi_item`,
   `expiry.manual_entry` and anything else BLOCK. Both behaviours are tested. A literal
   "refuse if any open task exists" reading would make the resolve step unreachable dead code; this
   reading keeps both statements load-bearing. Named as a design call.

G1 — BEFORE (raw, in `SG-112_verify.log`)
-----------------------------------------
- image `sha256:ace2b17a5e85…` created 2026-09-24T10:49:29Z; container `91fab66e675a…`, restart 0, healthy
- `alembic current` (in container) = `20260923_sg100_enrich_snapshot (head)` — single head, VERIFIED
- `select count(*) from sqlite_master where type='table'` = `25` — VERIFIED
- 25-table counts captured; asset status census `ACTIVE|6`; all byte-identical AFTER
- health exact: `{"status":"ok","db":"ok","storage":"ok"}`
- gate (canonical vhost): http:80 `code=301 redirect=https://storagegenie.dynv6.net/`; https:443 `code=401`
- merge-absence grep: decision `Literal["accept","edit","hold","reject"]`; POST routes only
  `/candidates/{id}/decision` + `/candidates/{id}/split`; no `merge` route and no `merge_candidates`.

G2 — merge review action + MERGED redirect
------------------------------------------

### Candidate merge (`POST /v1/candidates/merge`, `{winner_id, loser_ids[]}`)

- Validate FIRST, write nothing before a refusal: winner exists (404) / same household (403) /
  `proposed` (409); `loser_ids` a list of ids (422) / non-empty (422) / unique (422); winner not among
  losers (422); each loser exists (404) / same household (403) / `proposed` (409) / carries no open
  task outside `MERGE_RESOLVED_TASK_TYPES` (409). The service is `candidates.merge_candidates`
  (`services/candidates.py`), the route catches `CandidateMergeError`, `db.rollback()`s and maps
  `status_code` — the split-route shape (`api/v1/candidates.py:99-111`).
- Write: winner KEEPS its fields and its `proposed` state (invariant stated in code: "the survivor
  stays `proposed` after a merge -- merge never auto-accepts; the review still decides"); winner
  `evidence_ids` becomes the exact union (dedupe, winner-first order), each loser -> `merged` with
  `merged_into` in its proposal; open `identifier_collision` tasks on losers resolve with
  `review_task.resolve` audit rows; one `candidate.merge` audit row summaries before/after.
- Read-back (`PG-SC-02`): writer = merge route, reader = the candidates route. `GET
  /v1/candidates/{id}` now returns `merged_into` (string or null), tested end to end.
- Decision guard: `api/v1/candidates.py:37` learns `"merged"`; a merged loser re-decided is 409
  (`"Candidate is merged"`), proven.
- The merge set is the request's EXPLICIT ids, validated one by one on target; `dedup_matches` is
  never trusted as the set (untouched, still reviewer evidence).

### Asset MERGED redirect (`POST /v1/assets/{id}/merge`, `{merged_into}`)

- `asset_service.merge_asset_redirect`: winner exists (404) / same household (403) / not itself /
  not itself MERGED (422); source not already MERGED (409); `ACTIVE -> MERGED` validated through
  `lifecycle.validate_transition` — an illegal edge (e.g. DRAFT -> MERGED) is a 422 with the legal
  set. Writes status `MERGED`, a `merge.merged_into` assertion whose value is `{"merged_into": <id>}`,
  a `status` assertion (the delete-route precedent), and an `asset.merge` audit row. Read-back through
  the existing `GET /v1/assets/{id}` names the winner; no new table.
- `field_path` naming (my call, inside the `merge.*` namespace): `merge.merged_into`, reported.
- `PG-SC-07`: a MERGED asset with no redirect assertion reads terminal (200, status MERGED, no
  `merge.*` assertion), tested.

### Tests (fail-then-pass; BOTH runs committed raw, `PG-EV-09`)

- File `backend/tests/test_sg112_merge.py` (7 tests). The task-type and terminal-state oracles are
  typed in the test file, never imported from the module under test.
- Coverage: union evidence + winner stays proposed + losers merged with `merged_into` readable; a
  duplicate `identifier_collision` task resolves with an audit row; illegals (decided loser,
  cross-household loser, winner==loser, empty losers, loser with a blocking open task, unknown winner,
  decided winner) each refused with `before == after` counts of candidate + review_task + audit_event;
  merged-losor re-decision 409; asset redirect round trip through the asset read path; MERGED with no
  redirect reads terminal; asset refusals (self, missing target, cross-household target, DRAFT source,
  already MERGED, source household mismatch) write nothing.
- **FAIL run** (candidate test file against BASE `7043285`, isolated `git archive`, `PYTHONPATH`
  forced to the base app — verified `import app` -> base path): `6 failed, 1 passed`. The 1 pass is
  `test_merged_asset_without_redirect_reads_terminal`, a `PG-SC-07` read the base already satisfies
  (base has no merge route so it cannot be a fail-half of a NEW action), disclosed as such. The 6 are
  genuine behavioural fails (base answers 405/404 where the candidate answers 200). **PASS run**:
  `7 passed`.

### Gates (raw in `SG-112_verify.log`)

- **Full backend suite**: `2 failed, 563 passed` (base was `2 failed, 556 passed`; +7 = this slice's
  tests). The 2 reds are the known decoder env reds
  (`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
  `test_ocr_has_text_boxes_and_mean_confidence`). STASH-PROVED on this slice: both fail identically on
  the BASE archive with `pyzbar/libzbar` and `tesseract` absent on the host. Not caused here.
- **ruff**: `All checks passed!` (whole backend).
- **mypy**: candidate `41 errors in 9 files (checked 86 source files)` vs base
  `41 errors in 9 files (checked 86 source files)` — delta 0. The new route is fully annotated so it
  adds no error (the merge service is `# noqa: C901`, the `deduplicate_job` precedent).
- **Secret gate** (`PG-SC-05`): pattern over every changed/new file -> 0 real secrets (only the
  constant definition `MERGE_REDIRECT_FIELD = "merge.merged_into"` and the SG-082 source constants,
  quoted). Host `.env` never printed, never read into any artifact.
- **Scope**: `git diff --stat origin/automation -- backend/app/models backend/alembic frontend` is
  empty. Changed: `services/candidates.py`, `api/v1/candidates.py`, `services/asset_service.py`,
  `api/v1/assets.py` + new `tests/test_sg112_merge.py` + three `docs/worklogs` files. `.gitignore`
  re-verified, all committable. `docker compose config` never run.

Cross-product (`PG-IC-01`): no criterion demanded schema change, merge-map table, auto-accept,
frontend, a second recreate, a live merge, a press, or any metered call — no cell collides. Reads
were pytest/TestClient + host commands + the authorised image build and ONE recreate; no other image
was pulled or run, no unnamed runtime launched.

G3 — refresh + verify (BEFORE -> AFTER)
---------------------------------------
- image id: `sha256:ace2b17a5e85…` -> `sha256:f1d9f99affd1…` (differs)
- container: `91fab66e675a…` -> `d184fbc0becd…` (exactly ONE recreate; RestartCount 0, healthy)
- `alembic current`: `20260923_sg100_enrich_snapshot` unchanged (no migration; `models/` + `alembic/`
  empty diff)
- 25-table counts: byte-identical, delta exactly 0; asset status census `ACTIVE|6` -> `ACTIVE|6`
- health: `{"status":"ok","db":"ok","storage":"ok"}` x6
- gate (canonical vhost): `301` / `401`
- fresh image carries the merge code: `grep` in the container finds `POST /candidates/merge` and
  `POST /assets/{asset_id}/merge`; the four served files' sha256 match the host byte for byte
- fresh-server behavioural proof (temp DB inside the recreated container, NO live write): legal merge
  `200` (winner proposed, loser merged), illegal `winner==loser` `422` `"the winner cannot also be a
  loser"`, and the winner was still `proposed` after — nothing written to the live DB (counts
  re-checked identical after the probe).

Post-restart sweep waived (`PG-DP-02`, restart-gated). Substitute authority: the in-process full suite
pre-restart + the post-restart live probes + the fresh-container behavioural proof. Browser-driven
tests on this path: none exist — the derived set is empty and differed nowise (no frontend change).

Actual-versus-budget per leg (`PG-PR-06`; units = wall seconds)
--------------------------------------------------------------
- G1 BEFORE capture: ~60 s actual (bound 120 s ordinary).
- G2 implement + tests + gates: ~430 s actual, dominated by the full suite (24.96 s), two full mypy
  runs, the base-archive fail run and the base decoder stash-proof (bound 600 s suite+lint).
- G3 build + ONE recreate + verify: ~240 s actual, dominated by the classic-builder image build
  (bound 600 s build+recreate+verify).
- G4 worklog/report/receipt: ~150 s actual (bound 1500 s early-close).
- Overall: ~880 s actual vs 2100 s overall bound.

Issues / disagreements / unanswered
-----------------------------------
- Corrected above: the word "merge" already exists in the candidates service (`merge_web_fields`),
  unrelated to candidate merge; and the "losers carry no open review tasks" / "resolve duplicate
  tasks" pair needed the `identifier_collision`-resolves reading to stay non-vacuous.
- Design calls reported: redirect `field_path` = `merge.merged_into`; a winner that is itself MERGED
  is refused (no redirect chains); the asset source already MERGED is a 409; a `status` assertion is
  written on the merged asset (the delete-route precedent).
- `model` reported `unknown` (no `--model` in argv, no provider metadata). A refusal to guess, not a
  failure.
- The buildkit EROFS condition from SG-111 still holds; used `DOCKER_BUILDKIT=0` (classic builder).
- No privileged operation was denied; nothing was left unanswered.

Receipt (notes ref)
-------------------
Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. Note added on WORK_HEAD; notes ref pushed and read back from a MAPPED fetch. Pasted
executed output:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg112-fetched show 31e58f82558e649fc0fdf9ad19ac2274cb746747
Dispatch-ID: SG-112 | Report: docs/worklogs/SG-112_report.md | Work-HEAD: 31e58f82558e649fc0fdf9ad19ac2274cb746747
```

Full raw transcript (precheck, add, push, mapped fetch, show) is in `SG-112_verify.log` -> `RECEIPT
NOTE VERIFY`. The final tip (the report/receipt commit) is dual-annotated with the same note (SG-092
inoculation). final line: `note=yes`.

Three UNCLEAR lines
-------------------
- FIRST READ: whether "losers carry no open review tasks" meant ALL open tasks (which would make the
  "resolve open duplicate tasks" write step dead code) or all-except-the-duplicate ones. I chose the
  non-vacuous reading and named it; both a blocking task and a resolvable duplicate are tested.
- DURING EXECUTION: whether the asset redirect writer should be reachable from the candidate merge
  automatically. The packet scopes it to "a materialized duplicate asset", so I exposed it as its own
  `POST /assets/{id}/merge` route and left the candidate path asset-free (candidates are not assets).
- REMAINING: the model id (CLI default, unreadable from argv/metadata); whether the winner should also
  be able to be non-`proposed` in some future flow; and whether a same-status re-merge should be a
  no-op rather than the 409 I chose.
