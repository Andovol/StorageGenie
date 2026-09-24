SG-111 report — Lifecycle states: vocabulary + transition enforcement + readers, backfill proven on temp
========================================================================================================

Verdict: SHIPPED. One transition table enforces `DRAFT -> PENDING_REVIEW -> ACTIVE -> ARCHIVED ->
DISPOSED` + reserved `ACTIVE -> MERGED`; illegal edges answer 422 with the legal set; every ACTIVE-only
reader (incl. the SG-107 engine) goes through one shared predicate; the backfill is proven on a temp copy
and its production command recorded for the owner word; the served backend was rebuilt and recreated
exactly once; the live data stood still.

Contract echo + source path
---------------------------
Contract 0.33.0 — installed global rules file hashed against the payload, never checkout-vs-stamp (G-L1/M3).
- source: `/home/andrei/storagegenie-contract/VERSION` = `0.33.0`
- source HEAD: `b232b845d74e89cb346c60fa4b9a40ec401c42dd` = "Contract payload 0.33.0"
- `sha256sum /home/andrei/storagegenie-contract/RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`
- payload `/home/andrei/storagegenie-contract/RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46 RULES.md` -> match.
- recorded `0.33.0` == published `b232b84`. Clean.

Model / effort / spend (CO-78)
-----------------------------
Read from the process arguments, never a system-prompt identity line.
- argv (`/proc/3800821/cmdline`): `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>`
- effort = `high` (from `--variant high`)
- model = `unknown` — no `--model` flag present and no provider metadata readable; the packet states the
  CLI default model is omitted by policy, and I refuse to guess a plausible id.
- Spend real $ = `$0.000000` (zero provider calls; no metered call exists on any path).

Refs
----
- Work dir `/home/andrei/StorageGenie`, origin `git@github.com:Andovol/StorageGenie.git`
- BASE_REF = `origin/automation`
- BASE_RESOLVED = `046ce7fa75de0e51084bb6633efcdd7c5380e988` (== start HEAD)
- WORK_HEAD = `391338170f7ffc8ae833620160565f06961d17d2`

Premise verification — corrections are worth more than agreement
---------------------------------------------------------------
Every packet premise re-verified. Most held; four differed and are reported rather than bent to match:

1. **The live `status` census is `ACTIVE` only — no `ARCHIVED`.** The packet hypothesised "only ACTIVE +
   ARCHIVED". `SELECT status, COUNT(*) FROM asset GROUP BY status` = `ACTIVE|6`. So there are no
   out-of-vocabulary values live, and the backfill's own dry-run on the real shape plans zero changes
   (non-vacuity supplied by a synthetic seed on the TEMP copy, disclosed).
2. **The "gate 301/401" holds only for the canonical vhost `storagegenie.dynv6.net`, not for
   `Host: localhost`.** With `--resolve localhost ... http://localhost/` the host answers `404` / `303 ->
   /login` (a different vhost on the same ports). With the dynv6 Host the gate is exactly `301` (http->https)
   / `401` (https), matching SG-110. Canonical BEFORE and AFTER are both `301/401`.
3. **The "only lifecycle writer is delete" is right for writes to `Asset.status`, but the delete path was
   not the only place the literal `"ACTIVE"` lived.** The grep-gate named in the packet cannot be literally
   zero: `models/asset.py:23` holds the column default `"ACTIVE"` and `models/` is forbidden by the scope
   ceiling (empty diff). Every other `"ACTIVE"`/`"ARCHIVED"` literal in `backend/app` is now the vocabulary
   constant; the single remaining literal is reported with its reason. (A packet constraint and a packet
   grep-gate collided; the ceiling wins, the exception is named, `PG-SC-09`.)
4. **The buildkit path is broken on this host (EROFS), not this slice.** `docker compose build backend`
   failed with `failed to update builder last activity time: open /home/andrei/.docker/buildx/activity/
   .tmp-default...: read-only file system`; `mount` shows `/dev/vda1 on / type ext4 (ro,...)`. Resolved
   with `DOCKER_BUILDKIT=0` (classic builder), which does not write buildx activity. Not a denied
   privilege; a host filesystem state. See STATE open thread "EROFS".

G1 — BEFORE (raw, in `SG-111_verify.log`)
-----------------------------------------
- image `sha256:147a2651fb48…` created 2026-09-24T10:29:20Z; container `6a2b9ea6972d…`, RestartCount 0, healthy
- `alembic current` (live DB, read-only sqlite3) = `20260923_sg100_enrich_snapshot` — single head, VERIFIED
- `select count(*) from sqlite_master where type='table'` = `25` — VERIFIED
- 25-table counts captured (asset=6, evidence=13, household=1, audit_event=68, …); all byte-identical AFTER
- health exact: `{"status":"ok","db":"ok","storage":"ok"}`
- gate (canonical vhost): http:80 `code=301 redirect=https://storagegenie.dynv6.net/`; https:443 `code=401`
- live status census: `ACTIVE|6`

Reader inventory (the set enumerated on target, `PG-EV-08`)
-----------------------------------------------------------
`grep -rn '\.status' backend/app` + the `status` query params + FTS/saved-search predicates. Per hit:
- CHANGED to the shared predicate (ACTIVE-only): `analytics/service.py:188` -> `lifecycle.is_active`;
  `chat/service.py:152` -> `lifecycle.active_clause()`; `planning/service.py:113` -> `active_clause()`;
  `expiry_engine.py:172` (no predicate) -> `+ active_clause()` (**WIDEN — ISS-2 fixed**).
- CHANGED to the vocabulary constant (creation default; bypasses the map by decision G1, stated in code):
  `asset_service.py:46`, `candidates.py:582`, `candidates.py:818`, `dedup.py:151`, `schemas/asset.py:9`.
- CHANGED through the map (writer): `assets.py` PATCH status validates via `validate_transition`;
  `assets.py` delete validates `ACTIVE -> ARCHIVED` and writes `lifecycle.ARCHIVED`.
- UNTOUCHED and why: `analytics/service.py:189` full by-status census (not ACTIVE-only) ·
  `analytics/service.py:223,238` human-readable stat `source` description strings (not predicates) ·
  serializers `planning/service.py:158`, `chat/service.py:190`, `assets.py:145,289`, `exports.py:64` ·
  `assets.py:186` `?status=` caller-supplied generic filter (not ACTIVE-only) · `assets.py:222-223` facet
  census · `candidates.py:195` / `review_tasks.py` / `planning.py` a DIFFERENT model's status ·
  `models/asset.py:23` column default (models/ forbidden) · saved_search `status` is a stored filter key.

G2 — vocabulary + transitions + readers
---------------------------------------

### Transition module

New file `backend/app/services/lifecycle.py` (design call: NOT inside `asset_service.py`, because the
reader services and the API layer import the vocabulary and `asset_service` drags in the write-side graph
candidates/audit/assertions; this module's only import is the model). It holds the six EXACT literals, the
single `TRANSITIONS` table, `allowed_next`, `validate_transition`, and the two forms of the one ACTIVE
predicate (`is_active` for Python, `active_clause()` for SQL). Same-status is a no-op (reaches no new
state); terminal states map to the empty set. A `MERGED` asset with no redirect yet is terminal, never a
dangling pointer (`PG-SC-07`).

### Enforcement

- `PATCH /v1/assets/{id}`: a `status` in the payload is validated through `validate_transition`; illegal ->
  `422` whose body detail carries `illegal status transition '<cur>' -> '<req>'; legal from '<cur>': [...]`.
- `DELETE /v1/assets/{id}`: validates `current -> ARCHIVED` through the SAME table (not around it);
  re-archiving an ARCHIVED asset is a no-op and stays green; a DRAFT delete is 422.
- Creation writes bypass the transition map only for the decided `ACTIVE` default (G1), now stated via the
  constant at every creation site, never a bare literal.

### Readers

ACTIVE-only readers use the shared predicate; the engine now admits ACTIVE assets only (excluded from rows
AND unresolved — lifecycle-terminal, not date-missing; dashboard unchanged). `?status=` and the full
by-status census are deliberately not ACTIVE-only and are untouched.

### Tests (fail-then-pass; BOTH runs committed raw)

- File `backend/tests/test_sg111_lifecycle.py` (13 tests). The expected transition set is an INDEPENDENT
  oracle typed from the blueprint, never imported from the module under test.
- Transition matrix: all 36 ordered pairs driven through the REAL `PATCH /v1/assets/{id}` route; each
  illegal edge asserted 422 WITH the legal set in the body. Unit legs: exact vocabulary, table==oracle,
  every ordered pair, legal chain end to end + terminals closed.
- API legs: PATCH forward chain DRAFT..DISPOSED through the route, backward `DISPOSED -> ARCHIVED` 422;
  delete ACTIVE->ARCHIVED through the map, re-delete no-op, DRAFT delete 422.
- Reader legs: engine excludes non-ACTIVE from rows AND unresolved; assets list `?status=`; analytics /
  chat / planning ACTIVE semantics unchanged.
- Backfill: real script bytes loaded from source (importlib), temp DB, dry-run writes nothing, apply
  converts, idempotent on a clean vocabulary.
- **FAIL run** (candidate test file against BASE `046ce7f`, isolated `git archive`, `PYTHONPATH` forced to
  the base app — verified `import app` -> base path): `11 failed, 2 passed`. Five are GENUINE behavioural
  fails (base answers 200 where the candidate answers 422; base tiers the archived engine row). Six are
  artifact-absence fails (the new module/script do not exist on base) and are explicitly NOT the baseline
  (`lang/python.md`). **PASS run**: `13 passed`.

### Backfill (temp-proven; live is owner-word)

`backend/scripts/backfill_asset_lifecycle.py` reads the vocabulary from the single source, is dry-run by
default, and maps an out-of-vocabulary value to the nearest legal state (exact kept; case/whitespace
canonicalised; anything else -> `ARCHIVED`, conservative — an unknown status is never promoted to ACTIVE).
Proved on a consistent temp copy of the live shape (SQLite backup API, read-only source): dry-run wrote
nothing; after seeding `active` + `DELETED` on the TEMP copy, apply converted both
(`ACTIVE|6 DELETED|1 active|1` -> `ACTIVE|7 ARCHIVED|1`). The live DB was never written (`ACTIVE|6` before
and after). Production command recorded for the owner word:

    docker exec storagegenie-backend-1 python /app/scripts/backfill_asset_lifecycle.py \
        --db /data/db/storagegenie.db --apply

Before/after census queries for that word:
`sqlite3 "file:/data/db/storagegenie.db?mode=ro" "SELECT status, COUNT(*) FROM asset GROUP BY status;"`

Gates (raw in `SG-111_verify.log`)
----------------------------------
- **Full backend suite**: `2 failed, 556 passed` — the 2 known decoder env reds
  (`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
  `test_ocr_has_text_boxes_and_mean_confidence`). STASH-PROVED: both fail identically on the BASE archive
  (`2 failed`), with `pyzbar/libzbar` and `tesseract` absent on the host. Not caused by this slice.
- **ruff**: `All checks passed!` (whole backend).
- **mypy**: candidate `41 errors in 9 files (checked 86 source files)` vs base
  `41 errors in 9 files (checked 85 source files)`; the error multiset is IDENTICAL after sorting -> delta 0.
  Every error in a touched file (`schemas/asset.py`, `asset_service.py`, `assets.py`) is present at BASE.
- **Secret gate** (`PG-SC-05`): over the changed/new files the pattern matches only pre-existing
  identifier text (`jina_result_category` etc. in `candidates.py`) and the word "secrets" in docstrings;
  a value-assignment-only grep finds 0 real secrets; host `.env` never printed or read into any artifact.
- **Literal gate**: `grep -rn '"ACTIVE"' backend/app` -> only `lifecycle.py:27` (the vocabulary) and
  `models/asset.py:23` (forbidden file, reported). `grep -rn '"ARCHIVED"' backend/app` -> only
  `lifecycle.py:28`.
- **Scope**: `git diff --stat origin/automation -- backend/app/models backend/alembic frontend` = empty.
  Changed paths: the 9 modified app files + `lifecycle.py` + `tests/test_sg111_lifecycle.py` +
  `scripts/backfill_asset_lifecycle.py` + the three `docs/worklogs` files. `.gitignore` re-verified, all
  worklog files committable. `docker compose config` never run.

G3 — refresh + verify (BEFORE -> AFTER)
---------------------------------------
- image id: `sha256:147a2651fb48…` -> `sha256:ace2b17a5e85…` (differs)
- container: `6a2b9ea6972d…` -> `91fab66e675a…` (exactly ONE recreate)
- `alembic current`: `20260923_sg100_enrich_snapshot` unchanged (no migration; `models/`+`alembic/` empty diff)
- 25-table counts: byte-identical, delta exactly 0; status census `ACTIVE|6` -> `ACTIVE|6`
- health: `{"status":"ok","db":"ok","storage":"ok"}` ×6
- gate (canonical vhost): `301` / `401`
- fresh server behavioural proof (temp DB inside the recreated container; no live write): the image carries
  `lifecycle.py` (sha256 `96093c94…`); `PATCH` legal `ACTIVE->ARCHIVED` = 200; illegal
  `ARCHIVED->ACTIVE` = 422 `legal from 'ARCHIVED': ['DISPOSED']`; unknown `BOGUS` = 422.

Post-restart sweep waived (`PG-DP-02`, restart-gated). Substitute authority: in-process suite pre-restart +
post-restart live probes + the fresh-container behavioural proof. No browser-driven tests exist on this
path — the derived set is empty and differed nowise.

Issues / disagreements / unanswered
-----------------------------------
- Corrected above: census is ACTIVE-only; the gate is Host-dependent; the `"ACTIVE"` grep-gate cannot be
  zero because `models/` is forbidden; buildkit is EROFS-broken on the host and the classic builder works.
- Design call reported: same-status PATCH is a no-op (reaches no new state); creation status values other
  than the default are still accepted as an initial state (G1 decided creation keeps writing ACTIVE and
  the packet did not name creation among the enforcement points) — so a POST with a free-text status is the
  one remaining path that is not a transition. Named rather than silently changed.
- `model` is reported `unknown` (no `--model` in argv, no provider metadata). Not a failure, a refusal to guess.
- No privileged operation was denied; nothing was left unanswered.

Receipt (notes ref)
-------------------
Work pushed to `automation` (`046ce7f..3913381`), remote head observed at
`391338170f7ffc8ae833620160565f06961d17d2` on `refs/heads/automation`; worktree clean. No push to
`storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on WORK_HEAD
`391338170f7ffc8ae833620160565f06961d17d2`; notes ref `refs/notes/storagegenie-coder-reports` pushed
(`ad03653..b5fc35a`) and read back from a MAPPED fetch (`refs/notes/storagegenie-coder-reports-sg111-fetched`
at `b5fc35a3823c5d2dd8cded9416304f3f7cdb3a4e`). Pasted executed output:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg111-fetched show 391338170f7ffc8ae833620160565f06961d17d2
Dispatch-ID: SG-111 | Report: docs/worklogs/SG-111_report.md | Work-HEAD: 391338170f7ffc8ae833620160565f06961d17d2
```

Full raw transcript (precheck, add, push, mapped fetch, show) is in `SG-111_verify.log` -> `RECEIPT NOTE
VERIFY`. The final tip (this receipt commit) is dual-annotated with the same note (SG-092 inoculation).
final line: `note=yes`.

Three UNCLEAR lines
-------------------
- FIRST READ: whether "creation writes bypass validation ONLY for the ACTIVE default" meant creation should
  also reject non-vocabulary statuses. I kept creation accepting a caller-supplied initial status (G1:
  no creation-flow change) and only routed the default through the constant; the free-text POST path is
  named as the one non-transition writer.
- DURING EXECUTION: whether the G3 fresh-server 422 proof could PATCH a live asset. I ran it on a temp DB
  inside the recreated container, leaving the live DB byte-identical, because `DATABASE: none live`.
- REMAINING: model id (CLI default, unreadable from argv/metadata); whether same-status PATCH should be a
  422 rather than a no-op (I chose no-op to preserve idempotent delete/re-archive); and the host EROFS
  condition (buildkit `~/.docker` read-only) that future deploy slices will hit again.
