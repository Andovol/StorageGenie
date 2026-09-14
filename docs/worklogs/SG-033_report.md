# SG-033 report — multi-item split: one candidate → per-item candidates + review UI

**Dispatch-ID:** SG-033 · **Coder:** opencode · **Effort:** medium
**BASE REF:** `automation` → resolved commit `042e9c75ec891f97fd136e18cebceb6ef6840c31` (two fields, as required).
**WORK_HEAD:** the commit carrying this file; its hash is recorded by the G5 receipt note on `refs/notes/storagegenie-coder-reports` (a committed file cannot contain its own commit hash).
**Work dir** `/home/andrei/StorageGenie` · **origin** `git@github.com:Andovol/StorageGenie.git`.
**DATABASE:** none — temp SQLite only, zero live rows. **Restart:** none — no service touched, nothing deployed. **NETWORK:** none; **spend $0**.

**Model/effort per `CO-78`** — read from process arguments, never an identity line. Parent argv (`/proc/$PPID/cmdline`), quoted verbatim (leading tokens):

```
opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-033 — Multi-item split: ...
```

Coder `opencode`, effort `medium` (`--variant medium`), **model `unknown`** — the CLI default IS the model and is omitted per policy; no model id appears in argv or packet, so I write `unknown` rather than a guess. Grandparent: `bash /usr/local/lib/dispatch/run-coder SG-033`.

## Verdict

GREEN. `POST /v1/candidates/{candidate_id}/split` turns a multi-item candidate into one `proposed`
child per item, each carrying its own extraction fields, the shared evidence ids, and the origin's
provider provenance + call ids; the origin leaves the decidable set (later decision → 409) and its
`candidate.multi_item` task resolves. Empty, single, partial, duplicate, and out-of-range selections
are all `422` with nothing created. The Review screen shows the split action exactly when an open
`candidate.multi_item` task exists and presents the resulting children as links. `npm run build` is
green; the backend suite is green modulo the 2 known decoder env reds (re-verified at BASE); `ruff`
clean; secret scan 0; zero network, `$0` spend.

## Findings (packet premises verified; differences stated, not bent)

### F-SG033-1 — the packet's "proposal carries `evidence_ids`" premise is inaccurate (CORRECTION)
`G1` says "the origin proposal carries `ai_items`, `ai_unknowns`, `provider_call_ids`, `evidence_ids`,
`ai_provider/ai_model/prompt_template_version` (`candidates.py:232-245`)". Read at BASE, the proposal
dict (`candidates.py:232-245`) has **no `evidence_ids` key**. Evidence ids live on the `Candidate`
row: `evidence_ids_json` (`candidates.py:248`). The split therefore shares
`candidate.evidence_ids_json` — the real source — and the child test asserts it equals the origin's
`[evidence_id]`. No behaviour is bent to the wrong premise; recorded as a correction.

### F-SG033-2 — an origin `expiry.manual_entry` task is not resolved by the split (limitation, reported)
The packet names only the `candidate.multi_item` task as resolving. `split_candidate` resolves exactly
the open `candidate.multi_item` task(s) on the origin. If an origin also carried an open
`expiry.manual_entry` task (it can, when `needs_evidence`), that task is left on the now-retired
origin. Children carry the per-item unknowns (`child["ai_unknowns"]`, `needs_evidence`), but no child
review task is created and the origin's manual-entry task is not re-pointed. This is outside the
packet's stated property and was left untouched rather than widening scope; flagged for the Architect.

### Non-vacuity notes
- Pre-change backend tests fail on the **route** (`404`), quoted raw — not on an unrelated assertion.
- Pre-change frontend tests fail on the **absent action** (`Unable to find role="button" and name /split/i`), quoted raw.
- The split test asserts per-item `display_name`, the item-1 `expiry_date` present and the item-2
  `expiry_date` **absent** (no guessed value for an unknown), the shared deterministic `identifier`,
  shared evidence, full provider provenance, per-item unknowns, resolved task, and the 409 origin
  decision — a property, not a command echo.
- The child index list is derived in the UI from the task's `item_count` (data), and the service
  refuses any partial coverage — so the happy path cannot pass by ignoring unspecified items.

## G1 — split operation (candidate → per-item candidates)

New route `POST /v1/candidates/{candidate_id}/split` in `backend/app/api/v1/candidates.py`, beside the
decision route; request `{item_indexes: [int]}`. Operation in `backend/app/services/candidates.py`
(`split_candidate`, `_split_child_fields`, `CandidateSplitError`, `SPLIT_ORIGIN_STATE`).

- Refusals (all before any write, so nothing is created): candidate missing → `404`; household
  mismatch → `403`; state not `proposed` → `409`; `ai_items` absent or `< 2` → `422`; `item_indexes`
  not ints, empty, `< 2`, duplicated, out of range, or not covering every item exactly once → `422`.
  `PG-SC-07` empty selection is the enforced stop; a single-item split (one named index, or a
  single-item candidate) is `422`.
- Each child is `state="proposed"` with `fields` rebuilt from the origin's deterministic fields plus
  **its** item's `display_name`/`expiry_date`/`lot` (omitted when the item has no value, never
  guessed), `ai_items=[that item]`, per-item `ai_unknowns` remapped to `items.0.*`, derived
  `needs_evidence`, the origin's `ai_provider`/`ai_model`/`prompt_template_version`/`provider_call_ids`,
  `split_from` + `split_item_index` provenance, and an empty `dedup_matches` (dedup was not computed
  per item; `review_task_ids` empty).
- Origin: `state="split"`; the decision route rejects it — the non-decidable guard is now
  `if candidate.state in {"rejected", "split"} → 409` (message `Candidate is split`). The origin's
  open `candidate.multi_item` task(s) are set `resolved` with a `review_task.resolve` audit row, and
  a `candidate.split` audit row records the child ids + named indexes (`PG-SC-02` trace).

**Ceiling note (M6):** the `api/v1/candidates.py` parenthetical is "split route only". The split
route is the only route added; the two-line non-decidable guard in the existing decision handler is
the G1 requirement "the origin leaves the decidable set", and `candidates.py` is in the ceiling. No
other route or service was touched.

## G2 — review UI split action

- `types.ts` gains `CandidateSplitChild` + `CandidateSplitResponse`; `client.ts` gains
  `candidateSplit()` beside `candidateDecision`.
- `ReviewPage.tsx` fetches `/v1/review-tasks` (existing route) and finds the open
  `candidate.multi_item` task whose `subject_ref` is this candidate; the button appears **iff** that
  task exists. The split indexes are `[0 .. item_count-1]` from the task's `proposed_change`
  (rendered from data, no hardcoded list). The split mutation invalidates the candidate and
  review-tasks queries and stores the returned children; the page renders them as links to
  `/review/{childId}`.
- `CandidateCard.tsx` gains optional `splitItemCount`/`onSplit`/`splitBusy`; it renders
  `Split into {n} items` iff `splitItemCount` (>= 2) is supplied.

**Ceiling note:** `ai_items` was **not** added to the candidate GET route, to respect "split route
only". "Options render from data" is satisfied by the task's `item_count` (pre-split) and the split
response's child fields (post-split). A pre-split item-name list would need a GET response change
outside the stated ceiling; flagged here rather than done.

## G3 — proof (raw runs in `docs/worklogs/SG-033_verify.log`)

| Gate | Result |
|---|---|
| PRE backend `pytest tests/test_review_split.py` | **5 failed** in 0.93s (route 404) |
| POST backend `pytest tests/test_review_split.py` | **5 passed** in 1.08s |
| PRE frontend `vitest` (card + page) | **3 failed \| 5 passed** ("Unable to find role button /split/i") |
| POST frontend `vitest` (card + page) | **8 passed** in 842ms |
| Full backend suite (`pytest -q`, 600s) | **2 failed, 126 passed** in 8.69s |
| BASE `042e9c7` — same 2 reds | **2 failed, 121 passed** in 7.48s (pyzbar/libzbar + pytesseract absent) — base-proved, not inherited |
| `ruff check app tests` | `All checks passed!` |
| `mypy app` | 40 errors in 9 files (baseline 40-in-9 unchanged; none in the edited files) |
| `npm run build` | green, 93 modules, built in 864ms |
| `vitest run` | 9 files, **25 passed** |
| Secret scan | **0** real-key matches (SG-031 sentinel only, confined to `test_settings.py`) |
| Health probe `CO-92` | unanswered — compose 0 services; `/v1/health` → 404; delta 0 |

No migration; no prompt diff; no ignored file staged; no network (in-process TestClient only).

## Budget (actual versus budget)

| Leg | Budget | Actual |
|---|---|---|
| Ordinary probes / single test runs (120s) | 120s | ≤ 1.1s each |
| Backend suite (600s) | 600s | 8.69s |
| `npm run build` (600s) | 600s | 864ms (plus `tsc` ~2s) |
| `vitest run` (600s) | 600s | 1.76s |
| Overall (2400s) | 2400s | minute scale, well under |

## Live-state ledger

- Provider spend: **$0** (no live call; no provider seam touched in the split path).
- Network attempts: **0** (all proofs in-process via `fastapi.testclient`; the only socket attempt is the health probe, refused/404).
- Key reads: **0**.
- Deployments / migrations / restarts: **0**.
- Secrets: scanned by shape, **0** real matches; the only hit is the SG-031 test sentinel (`backend/tests/test_settings.py:47`).

## Guards

`PG-EV-01` FAIL-then-PASS raw for every new test (verify log §3-4) · `PG-EV-02` new test file exists and is committed · `PG-EV-05` the child-per-item provenance property is asserted, not a command echo · `PG-EV-09` both runs committed raw · `PG-SC-02` child `ai_items` traced origin → child via the read-back route, named and tested · `PG-SC-07` empty/single/partial selection → 422 with nothing created · `PG-SC-10` nothing staged as ignored · `PG-IC-01` cross-product (route + service + task-resolve / page + card + client / proofs) · `PG-IC-03` no remediation shares a condition with a stop-gate; stops win (the 422/409 refusals are the stops) · `PG-IC-07` no fixed dates in code · `PG-IC-09` premises re-verified; F-SG033-1 correction named · `PG-PR-03/04/06/10` scope ceiling, zero live calls, per-leg bounds, disposition.

## Role guard

Coder role only. I did not run any dispatch verb, did not start or poll any unit. No SSH performed.

## UNCLEAR

- FIRST READ: the split request's selection semantics. The packet names item indexes and rejects
  empty/single but does not state whether a partial selection is allowed. I required full coverage
  (every index exactly once) so the retiring origin cannot silently drop an item; a partial split is
  therefore a `422`. Flagged for the Architect to confirm or relax.
- DURING EXECUTION: the frontend needs the pre-split item list to render "options from data", but the
  candidate GET route (`get_candidate`) does not expose `ai_items` and the ceiling says "split route
  only". I derived the split from the task's `item_count` instead. If a pre-split item-name list is
  required, that is a GET-response change outside this ceiling.
- REMAINING: `mypy` remains 40 errors in 9 files — unchanged from BASE and none in the edited files;
  reducing the pre-existing set is outside this ceiling.
