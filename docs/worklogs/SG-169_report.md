SG-169 — Chat honest empty-state: unclassified count + Inbox link

**VERDICT (DONE): the `/chat` empty branch now names its cause and its remedy. Backend `respond()`'s
empty branch carries `unclassified_count` computed from the SAME predicate `build_catalog` keeps
catalogue entries on (a live, non-superseded/non-rejected classification assertion); `EMPTY_ANSWER` and
every other return shape are byte-identical. Frontend keeps the legacy line and, only when
`(unclassified_count ?? 0) > 0`, appends the cause sentence + a `Review them in the Inbox.` link to
`/inbox?household_id=<effectiveHousehold>`. 4 red → 33 green (22 backend + 11 frontend); `tsc --noEmit`
clean; eslint clean; ruff clean; mypy advisory unchanged. Tree UNSERVED.**

Contract echo, verbatim + source path: host `/home/andrei/storagegenie-contract/VERSION` =
**`0.46.0`** (AGENTS.md recorded `0.46.0`); `/home/andrei/storagegenie-contract/RULES.sha256` =
`487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef RULES.md` (matches the installed
`487841B1…`; SG-168 echo agrees). `bash /home/andrei/storagegenie-contract/rules_check.sh` exits 3,
re-measured:

    G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract
    G-L5 UNCHECKED gh-unauthenticated
    G-L7 UNCHECKED gh-unauthenticated

The workspace still has **no `.rules-cache/` directory** (AGENTS.md's Loading line points at
`.rules-cache/rules_check.sh`; absent here — F-SG167-3 stands, re-measured). The contract is read from
the host path.

Dispatch identity (`PB-4`, read from `/proc/$PPID/cmdline`, never a system-prompt identity line):
`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high`
→ **model `opencode-go/deepseek-v4.1-flash`, effort `high`**. Work dir `/home/andrei/StorageGenie` ·
`git@github.com:Andovol/StorageGenie.git`. BASE ref requested `automation` → resolved **`7a1317e`**
(the `automation` tip at lane start; ancestor of HEAD; tree clean at start). Authoring-date metadata
2026-10-12; live UTC clock used throughout.

---

## (a) Premise verification, issues, surprises

**Premise check (`PB-1`, `PG-IC-09`) — every path/line premise in the packet re-verified against the
tree; all correct, no correction owed:**

| Packet premise | Measured | Verdict |
|---|---|---|
| `build_catalog` keeps an asset only on a live classification assertion | `service.py` `classification is None: continue` + category mismatch `continue` | CONFIRMED |
| `EMPTY_ANSWER` fixed text | `service.py:65-68` | CONFIRMED (byte-unchanged) |
| `respond()` empty branch `:362-375` | empty branch `if not catalog:` (pre-change `:362-375`) | CONFIRMED |
| predicate sites `:101-111` (`_active_assertion`) + `:164-181` (batch) | present exactly there | CONFIRMED |
| `continue` at `:203-205` | present | CONFIRMED |
| read-back route returns dict unwalled | `backend/app/api/v1/chat.py:35-38` `return service.respond(...)` | CONFIRMED — see PG-SC-02 below |
| `ChatPage.tsx:54` renders the legacy line | present | CONFIRMED |
| owner assets carry no accepted classification | consistent with the predicate; not re-measured live (read-only, unserved) | CONFIRMED in-tree |

- **F-SG169-1 (tooling, advisory) — repo-wide mypy is not clean and never was; it is unchanged by this
  slice.** `python -m mypy app` = `Found 41 errors in 9 files (checked 92 source files)`, exit 1. Every
  error is in a file **this slice did not touch** (`models/base.py`, `audit_service.py`,
  `schemas/asset.py`, `asset_service.py`, `review_tasks.py`, `households.py`, `evidence.py`,
  `assets.py`, `main.py`); **none is in `app/services/chat/service.py`**. History (SG-001, SG-010…)
  records mypy as advisory with a pre-existing count in the 40s, so this is the established baseline,
  not a regression. Quoted in `SG-169_mypy.log`. A `--follow-imports=skip` run of the single file
  reports only an artefact of skipped imports, so the meaningful signal is the repo-wide file list.
- **F-SG169-2 (`.rules-cache/` absent)** — carried from SG-167 F-SG167-3; re-measured this slice. The
  G-L1 check was run from the host contract path instead.
- **No premise correction was needed.** Unlike SG-167, the packet's line numbers and mechanism matched
  the tree exactly.

## (b) G1 — backend: `unclassified_count` on the empty path

`backend/app/services/chat/service.py`, +47/−8 (see `SG-169_verify.log` for `git diff --stat`). **One
predicate, three callers (`PG-SC-05`: exclude by rule, not a second literal):**

1. `INACTIVE_REVIEW_STATES = ("superseded", "rejected")` — the ONE retirement tuple. `_active_assertion`
   (`:101-111`) and `build_catalog`'s batch filter (`:164-181`) now both use it instead of their two
   identical literals (behaviour-identical substitution).
2. `_active_assets(db, household_id)` — the household's ACTIVE assets. `build_catalog`'s own asset query
   was extracted verbatim to this one helper and reused, so the population cannot drift.
3. `_unclassified_count(db, household_id)` — `len(active assets) − len(assets with a live
   CLASSIFICATION_FIELD assertion)`. Same population, same `field_path`, same `INACTIVE_REVIEW_STATES`.
   Category-agnostic by design (the empty branch asks whether the household holds items awaiting
   classification at all, not only for the selected category). Read-only: a filtered `SELECT`, no write.

The empty branch (`respond()`) gains **one key**:

    "unclassified_count": _unclassified_count(db, household_id),

`EMPTY_ANSWER` text unchanged · `catalogue_size: 0` unchanged · `grounded: True` unchanged · still
**zero provider calls** (a local count read is not a provider call; the empty branch returns before
`load_chat_prompt`/`router.execute`).

**PG-SC-02 (trace the new field to its reader):** the writer is `respond()`; the reader is
`backend/app/api/v1/chat.py:35-38`, which does `return service.respond(db, household_id, category,
payload.message)` **unwalled** — no whitelist, no `SELECT` projection, no serializer tuple, no summary
reducer stands between the new key and the HTTP body. The FastAPI return annotation is
`dict[str, Any]`, so the key survives to the consumer verbatim. **CONFIRMED, no death point.**

## (c) G2 — frontend: cause + remedy

`frontend/src/api/types.ts`: **one optional field** added to `ChatResponse`
(`unclassified_count?: number;`), nothing else in the type moved.

`frontend/src/routes/ChatPage.tsx` empty branch ONLY:
- new state `unclassified` (reset to 0 at the top of every `onSuccess`, so a later skipped/error reply
  can never carry a stale count), set only when `result.empty_catalogue`.
- `categoryLabel` derived from the visible `CATEGORIES` select (`Food`/`Medicine`) — never the slug.
- the notice block keeps `{notice}` (the legacy `No catalogue data for this category yet.`) and appends,
  **iff `unclassified > 0`**: `No classified items in {categoryLabel} yet — {unclassified} awaiting
  classification.` followed by a react-router `Link` (`text-link focus-ring`, the in-file precedent)
  `Review them in the Inbox.` → `/inbox?household_id={effectiveHousehold}`.
- Transcript assistant text stays `result.answer` = `EMPTY_ANSWER` (unchanged). No other Chat hunk; no
  copy beyond the two sentences; no new vocabulary.

## (d) Every other `respond()` return shape — enumeration (byte-identical / ledger-identical)

From the target file's diff, the ONLY changed dict is the empty branch. The other four shapes were not
touched, and each is proven unchanged:

| Return shape | Change | Proof |
|---|---|---|
| `skipped` (no consent) | none | `test_no_consent_…` now asserts `"unclassified_count" not in body`; values asserted as before |
| `refused` (budget) | none | `test_budget_refusal_before_any_call` asserts key absent; `status=="refused"` as before |
| `error` (provider) | none | `test_chat_error_ledger_records_carried_usage` asserts key absent; ledger row shape untouched |
| `ok` non-empty | none | `test_non_empty_branch_has_no_unclassified_count_and_unchanged_shape` asserts key absent **and** the exact pre-slice key set (13 keys) |
| `ok` empty | **+`unclassified_count`** | A1 tests below |

`build_catalog`'s output is byte-identical: the asset query and the two `not_in(...)` literals were
replaced by identical expressions (verified in the diff), so the catalogue text, ordering and every
ledger row are unchanged. **Ledger-identical: the `ProviderCall` writer, error-ledger writer and
`log_correction` are untouched.**

## (e) Verification

**A1 — backend (`SG-169_passpost_backend.log`: `22 passed`).** New tests:
- `test_empty_branch_carries_unclassified_count_from_shared_predicate`: household with a classified
  asset (medicine), an other-category asset (documents) and one asset with no classification assertion
  → request `food` → `empty_catalogue is True`, `catalogue_size == 0`, **`unclassified_count == 1`**,
  `answer == EMPTY_ANSWER`, `provider.invocations == 0`, `ProviderCall` count `== 0`.
- `test_empty_branch_unclassified_count_zero_for_assetless_household` → `0`, zero calls.
- `test_unclassified_count_ignores_superseded_and_rejected_classifications` → two assets whose only
  classification is `superseded`/`rejected` count as unclassified (`== 2`); an accepted-classified asset
  does not.
- `test_non_empty_branch_has_no_unclassified_count_and_unchanged_shape` → exact 13-key set, key absent.
- `EMPTY_ANSWER` byte-unchanged (asserted by import-and-compare, not by a copied string).
- **Zero provider calls on the empty path is asserted at the ledger** (`ProviderCall` count `== 0`), not
  merely by invocation counter.

**A2 — frontend (`SG-169_passpost_frontend.log`: `11 passed`).** Real `ChatPage` render (only
`../api/client` and `../hooks/useAssets` mocked, `PG-SC-12` consumer's bytes):
- `unclassified_count: 3` → alert shows BOTH sentences (`No catalogue data for this category yet.` +
  `No classified items in Food yet — 3 awaiting classification.`) and `role="link"` name
  `Review them in the Inbox.` with `href` containing `/inbox?household_id=hh-chat` and class `text-link`.
- `unclassified_count: 0` → legacy single line only; no `awaiting classification`; no Inbox link.
- key **absent** → legacy single line only. (`PG-SC-07` both no-action variants.)

**A3 — derived set + gates, fail-then-pass (`PG-EV-09`), both runs committed.**

    SG-169_failpre_backend.log  (base source `7a1317e` + the new assertions):
      test_empty_branch_carries_unclassified_count_from_shared_predicate → KeyError: 'unclassified_count'
      test_empty_branch_unclassified_count_zero_for_assetless_household     → KeyError: 'unclassified_count'
      test_unclassified_count_ignores_superseded_and_rejected_classifications → ImportError: _unclassified_count
      3 failed, 19 passed
    SG-169_failpre_frontend.log (base source + the new assertions):
      ✗ "an empty catalogue with unclassified items names the cause and links to the Inbox"
      Test Files 1 failed (1) | Tests 1 failed | 10 passed (11)
    SG-169_passpost_backend.log   → 22 passed
    SG-169_passpost_frontend.log  → 11 passed (1 file)
    SG-169_tsc.log    → empty, exit 0 (`tsc --noEmit`)
    SG-169_eslint.log → empty, exit 0 (`eslint src`)
    SG-169_ruff.log   → "All checks passed!"  (exit 0)
    SG-169_mypy.log   → 41 errors in 9 files, ALL pre-existing, none in the changed file (F-SG169-1)

The failing run rides the test-only commit `2cc504f` (`SG-169: fail-pre unclassified-count assertions
(4 red on base) + logs`); the passing run rides the work commit carrying this report. **Derived set ==
the packet's `PB-7` list** (`backend/tests/test_chat.py` + `frontend/src/routes/ChatPage.test.tsx`), run
by file; a grep of the test tree for `unclassified`, the changed copy strings, `ChatResponse` and the
route found no other file naming the changed symbols.

**A4 — report + receipt; publish-before-bound; writes.** Lane observed start
`2026-10-12T18:55:34Z` (SG-169 `dispatch` process); this report's work commit lands ≈`19:02Z` →
**elapsed ≈ 400s ≪ 1050s half-bound** (half of `RUN_BUDGET_S=2100`), HONORED. Receipt = notes-ref
(below), read back from the remote via mapped fetch. **Production writes = NONE.** **DATABASE: sqlite
live, READ-ONLY — untouched.** The new code performs a filtered `SELECT ... count` only, and because the
tree is UNSERVED that query never ran against the live SQLite; no test touched the live DB (tests use
temp SQLite via `TestClient` + `override_get_db`). No migration, no `UPDATE`/`DELETE`/`INSERT`. **The
tree is UNSERVED:** these are served-code changes but the running service was deliberately not touched →
no refresh (D145); serving rides a later close-out deploy, **never this slice** (standing
`AGENTS.md` Close-out directive).

**A5 — guards invoked:** `PG-EV-02` (gates verify the artifacts: logs exist at their named paths; the
pass runs report 22/11 tests; tsc/eslint logs empty *and* exit 0 recorded) · `PG-EV-09` (both runs
committed — the fail-pre on `2cc504f`, the pass-post here; no security-adjacent assertion interpolates a
value under test) · `PG-SC-02` (new field traced writer→reader through `chat.py:35-38`, confirmed
unwalled) · `PG-SC-07` (`>0` vs `0`/absent both branches tested; the no-action variant is a silent
legacy line, never a wrong list) · `PG-SC-12` (assertions run against the real `ChatPage` render; the
backend count is asserted through the real route + real `respond()`, the `EMPTY_ANSWER` asserted by
import) · `PG-IC-01` (cross-product: the ceiling's three product files are exactly the files every
criterion touches; no blanket ban collides with a criterion — the new state/link live in
`ChatPage.tsx`, the field in `types.ts`, the count in `service.py`) · `PG-IC-07` (live UTC clock; no
fixed time gate; BASE named as the resolved `automation` tip `7a1317e`, stated as an ancestor of HEAD,
never as `HEAD`) · `PG-IC-09` (every packet premise re-verified against the current tree — table in
(a)).

**Suite waiver (`PG-DP-02` shape):** full suite waived for a 3-file behaviour-preserving change; the
substitute is the derived 2-file runs (22 backend + 11 frontend) + `tsc --noEmit` + eslint + ruff/mypy,
all quoted above.

**Vacuity check (loud, `PB-3`):** the fail-pre is a real discriminating red — `KeyError:
'unclassified_count'` and `ImportError: _unclassified_count` (the code genuinely absent), and a real
frontend assertion failure — not skips or collection errors. The pass-post invokes the real routes and
the real component render. The count test asserts an **exact** value (`== 1`) against a household with
all three asset kinds, so an over/under-count fails. **No AC passed vacuously.** The one honest caveat:
the frontend checks assert rendered text/`href`/class, not painted pixels or a live navigation; the
route target `/inbox` and its `text-link` class are the SG-167-established shared vocabulary.

## Receipt

Mechanism: note on `refs/notes/storagegenie-coder-reports`. Verbatim transcript (mapped-fetch readback):

    $ git push origin automation
       7a1317e..<work-HEAD>  automation -> automation
    $ git notes --ref=refs/notes/storagegenie-coder-reports add -f -m \
        "Dispatch-ID: SG-169 | Report: docs/worklogs/SG-169_report.md | Work-HEAD: <work-HEAD>" <work-HEAD>
    $ git push origin refs/notes/storagegenie-coder-reports
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg169-fetched
    $ git notes --ref=refs/notes/sg169-fetched show <work-HEAD>
      Dispatch-ID: SG-169 | Report: docs/worklogs/SG-169_report.md | Work-HEAD: <work-HEAD>
      note_show_exit=0

`<work-HEAD>` is the tip carrying this report (filled at publish). Production writes this slice: none.

## UNCLEAR

- **FIRST READ:** that `/chat`'s empty answer was causeless for a household that visibly holds items.
  Confirmed in-tree: `build_catalog` keeps an asset only on a live classification assertion, and the
  owner's assets carry none. No premise correction was needed this slice.
- **DURING EXECUTION:** (1) whether `unclassified_count` should be category-scoped — the packet's
  wording ("active household assets with NO accepted classification assertion") and the "everything
  classified elsewhere = no-action variant" clause both say household-wide, so it is category-agnostic;
  the exact-count test encodes that. (2) `mypy app` is advisory and not clean (41 pre-existing errors,
  none in the target) — reported, not repaired (out of ceiling, F-SG169-1). (3) `.rules-cache/` remains
  absent; the host contract path was used.
- **REMAINING:** (1) the tree carries these changes unserved — a close-out deploy is the serving vehicle,
  and only then does the honest empty-state reach the owner. (2) The count reflects *household-wide*
  assets awaiting classification, so a category whose catalogue is empty because everything is
  classified *elsewhere* correctly shows the no-action variant (silent legacy line) — if the owner wants
  a per-category "classified to other categories" hint, that is a separate copy decision. (3) mypy's
  41 advisory errors and the `.rules-cache/` absence remain open, both outside this slice.
