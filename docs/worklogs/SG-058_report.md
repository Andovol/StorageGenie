# SG-058 — consistency: unify Untitled label + per-item quantity/unit/asset_type on split

- **Dispatch:** SG-058 (L3 stage D80, consistency batch slice 2 of 4)
- **Coder / effort:** opencode · **medium** (read from process argv `--variant medium`)
- **Model:** `unknown` — the argv carries no model id (policy: CLI default IS model) and no
  provider metadata exposing the Coder model was observable. Not guessed.
- **Work dir:** `/home/andrei/StorageGenie`; remote `origin git@github.com:Andovol/StorageGenie.git`
- **BASE ref:** `origin/automation` → resolved commit `412acc9952f4212cf2331bbe2774793730d39190` (two fields)
- **WORK_HEAD:** `<set at receipt>` (the note is added on this commit; a docs-only receipt append follows)
- **Contract:** 0.27.0
- **DB:** none — every test uses scratch temp SQLite; no live import/write; production SQLite untouched
- **Verdict:** **GO** — label unified, split fields now per-item, suite/lint/build green, deploy verified.

## G0 — starting tree + premises (re-verified in-slice)

- `git status --porcelain` → **empty** (clean); branch `automation`; HEAD = `origin/automation` = `412acc9…`.
- Premises, quoted: `asset.py:11` `UNTITLED_LABEL = "Untitled"`; `product.ts:25`
  `UNTITLED_ASSET_NAME = "Untitled asset"`; `candidates.py:528-596` `_split_child_fields` replaced
  `display_name`/`expiry_date`/`opened_date`/`lot` but shared `quantity`/`unit`/`asset_type`. **All match.**
- `Untitled` enumeration (regex over `*.py`/`*.ts`/`*.tsx`): backend constant `asset.py:11`, assertion
  `test_sg049_v2_extraction.py:295`, docstring `test_sg049_v2_extraction.py:14`; frontend already
  `"Untitled asset"` (`product.ts:25`, `AssetCard.test.tsx:22`, `drawer.test.tsx:218`,
  `product.test.ts:93`). **Diff vs the packet's expectation: NONE.**
- `planning/service.py:153` and `chat/service.py:179` both read `asset.display_name or UNTITLED_LABEL` —
  **no hunk** (verified by quoted read, not silently added). No frontend hunk.

## G1 — label unification (`UNTITLED_LABEL = "Untitled asset"`)

- One constant hunk: `backend/app/models/asset.py:11`. Its only two backend consumers are the catalog
  builders named above; both inherit the new value with no code change. The frontend already used
  `"Untitled asset"`; the served production bundle still contains that string (see G3 deploy checks).
- Test hunks, exactly the enumerated set, every assertion kept: `test_sg049_v2_extraction.py:14`
  (docstring `Untitled` → `Untitled asset`) and `:295` (`assert UNTITLED_LABEL == "Untitled asset"`).
  The two fallback-behaviour assertions at `:290,294` read the constant and still hold.
- **`PG-SC-09` — the world where unifying is wrong:** if the label fed the extraction/grounding
  *prompt text*, swapping `"Untitled"` for `"Untitled asset"` could shift model output and break the
  eval. It does not: the constant is only the display fallback substituted for a nameless asset in the
  planning/chat **catalogue DATA** turn, never a prompt instruction and never a candidate field
  (`build_candidate_from_extraction` uses `_deterministic_display_name`, not this constant). No prompt
  file changed; `test_sg049_v2_extraction.py` (parse/prompt/score) plus `test_ai_pipeline.py` guard
  extraction behaviour and stay green. The slice ships because the change is prompt-inert by construction.

## G2 — split propagation (`_split_child_fields`)

- One function hunk in `backend/app/services/candidates.py`: `quantity`/`unit`/`asset_type` moved into
  the item-derived set, emitted with the **same `_provenance` pattern as `lot`** (source_type
  `"extraction"`, the item's own confidence, provider/model/template/call provenance); a null/absent
  item value is **omitted**, never guessed and never inherited. `display_name` keeps its explicit block;
  the five optional fields share one loop, so `expiry_date`/`opened_date`/`lot` behaviour is unchanged.
  Docstring corrected (it previously promised only name/expiry/lot replacement).
- **Design note (loud):** the origin's deterministic `asset_type="unknown"` fallback is now excluded and
  NOT inherited; a child whose item has no `asset_type` therefore carries no `asset_type` field at all.
  That is the packet's explicit rule ("null/absent → omitted … never inherited"); at commit time
  `_create_asset_for_candidate` already defaults a missing `asset_type` to `"unknown"`
  (`candidates.py:409`), so no consumer breaks. `test_sg049_v2_extraction.py::test_deterministic_asset_type_default_value_unchanged`
  still proves the origin default `"unknown"` (deterministic) is untouched.

### FAIL-then-PASS (`PG-EV-09`, both runs raw in `SG-058_verify.log` [4]/[5])

- Test hunks **extended, not added**: `test_review_split.py::test_split_yields_per_item_children_with_shared_evidence_and_provenance`
  (its `_proposal` origin now carries extraction `quantity=2.0`/`unit="L"`/`asset_type="food"` from item 0;
  the two seeded items carry their own `quantity`/`unit`/`asset_type`, item 1 with `quantity=None`) and
  `test_ai_pipeline.py::test_split_children_keep_their_item_opened_date` (same, through the full scripted
  pipeline at line 305). No new test file was needed.
- **RED (source hunk absent):** both fail — `assert 'quantity' not in {…'asset_type': {'value': 'food'…},
  …'unit': {'value': 'L'…}}` — the second child literally carries the origin's value. 2 failed / 1.34 s.
- **GREEN (source hunk applied):** 4 passed (2 split + label + deterministic-default); raw probe prints
  child 2 with `unit=cup`, `asset_type=cosmetics`, item `confidence=0.8`, call provenance, and
  **`quantity` absent**. 1.47 s.

## G3 — suite, lint, build, deploy, hygiene

- **Backend:** `cd backend && ../venv/bin/python -m pytest -q` → **2 failed, 235 passed in 14.28 s**
  (wall 16.39 s / 600 s). The 2 reds are **base-proven environmental** at BASE `412acc9…`
  (`tests/test_signals.py::{test_generated_codes…,test_ocr_has_text_boxes…}`) caused by missing
  `pyzbar/libzbar` + `pytesseract` ABIs in the host venv; baseline run was **identical (2 failed / 235
  passed)** and both raw runs are in the verify log. No new red.
- **Ruff:** `ruff check app tests` → `All checks passed!` (0.07 s / 600 s).
- **Frontend:** `npm test -- --run` → 21 files / **152 passed** (4.64 s); `npm run lint` → clean
  (1.51 s); `npm run build` (`tsc && vite build`) → **built** (4.24 s). No frontend file touched.
- **Deploy (`PG-PR-04`, backend code changed):** `BUILDX_CONFIG=/home/andrei/StorageGenie/.cache docker
  compose up --build -d backend` → exit 0 (11.73 s / 900 s). Container recreated
  `9194c50e… → 694f56de…` on image `sha256:8f832433…`; `RestartCount=0`, `Health=healthy`. Idempotent
  re-`up -d` → `Container … Running`, **same Id, same StartedAt, RestartCount=0**.
- **Targeted checks:** `curl -s http://127.0.0.1:8003/v1/health` →
  `{"status":"ok","db":"ok","storage":"ok"}` (exact); `docker port` → `8000/tcp -> 127.0.0.1:8003`
  (loopback only, no `0.0.0.0`, no 5173). **Served bundle hash UNCHANGED**: `assets/index-nugWvqun.js`,
  sha256 `e5c99c02…` pre- and post-deploy (no frontend hunk — distinct from SG-049's bundle change);
  the served bundle contains `"Untitled asset"`.
  *(The local `npm run build` hash differs because it omits the Dockerfile's
  `VITE_API_BASE=https://storagegenie.dynv6.net` build arg; the property is served-pre vs served-post.)*
- **Hygiene:** prod DB untouched — construction: no import route, no evidence upload, no write route
  called; only `GET /v1/health` (read) and `GET /`. No migration / no `alembic upgrade` / no `app.seed`.
  Dependency files unchanged (`git status` shows only the 5 ceiling files). Secret scan **n/a** — no
  secret-bearing file touched. No ignored file staged (`git status --porcelain` lists only tracked
  source/worklog paths). Nothing pushed to `storagegenie-evidence`; `{{RECEIPT_CMD}}` never run.
  Full sweep **WAIVED** per `PG-DP-02`; substitute = the G2 red→green run + the named suite/lint/build
  and deploy checks above.
- **No vacuous pass:** the G2 gate was seen failing first ([4]) and the targeted assertions invoke
  `_split_child_fields` through both the service route and the API route; the suite count is unchanged
  (235) because tests were extended rather than added; the deploy property compares two fetched bundle
  hashes, not a command exit.

## Constraints / budget

- Scope: exactly 5 files changed — `backend/app/models/asset.py`, `backend/app/services/candidates.py`,
  and the 3 named test files; plus the 3 `docs/worklogs` files. No hunk outside the ceiling
  (no `planning/service.py`, `chat/service.py`, frontend, prompts, migrations, or dependencies).
- Budget (uncalibrated, `G-A9`): ordinary 120 s · suite+lint+build 600 s · host build/up 900 s ·
  early-close 1500 s · overall 2400 s. Actual: base suite 16.02 s; RED 1.34 s; GREEN 1.47 s; post-change
  suite 16.39 s; ruff 0.07 s; frontend 4.64 + 1.51 + 4.24 s; deploy 11.73 s; **overall ≈ 217 s / 2400 s**
  (early-close not reached). No command was killed.
- `PG-IC-01` no blanket exclusion; stops win (`PG-IC-03`) — none taken. No provider call; no `PG-PR-03`
  denial. Time read the live clock (`PG-IC-07`); only the header authoring date is fixed.

## Spend (REAL $)

- **This slice actual: $0.000000** (zero provider calls, zero metered routes) vs **$0 bound** — the
  packet's posture. No provider client was constructed, no key read, no adapter touched. $0.000000.

## Receipt note (`refs/notes/storagegenie-coder-reports`)

WORK_HEAD = `3cbe6ea420e57d33186f3b2d49a33139395acecd`. Commands executed (raw), bounds 120 s add /
300 s push (completed in seconds):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-058 | Report: docs/worklogs/SG-058_report.md | Work-HEAD: 3cbe6ea420e57d33186f3b2d49a33139395acecd" 3cbe6ea420e57d33186f3b2d49a33139395acecd
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   66980a5..3da7331  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-verify
From github.com:Andovol/StorageGenie
   00dcc36..3da7331  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-verify
fetch_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports-verify list | while read -r note obj; do body=$(git cat-file -p "$note" | head -1); printf '%s -> %s\n' "$obj" "$body"; done
$ grep -n "SG-058" <note-contents-list>
16:3cbe6ea420e57d33186f3b2d49a33139395acecd -> Dispatch-ID: SG-058 | Report: docs/worklogs/SG-058_report.md | Work-HEAD: 3cbe6ea420e57d33186f3b2d49a33139395acecd
grep_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports-verify show 3cbe6ea420e57d33186f3b2d49a33139395acecd
Dispatch-ID: SG-058 | Report: docs/worklogs/SG-058_report.md | Work-HEAD: 3cbe6ea420e57d33186f3b2d49a33139395acecd
show_exit=0
```

Verified against the fetched, mapped ref: `fetch_exit=0`; the note bodies were dereferenced and listed
(`log --grep` does not match note bodies); the grep hit at line 16 carries BOTH `Dispatch-ID: SG-058`
and `Report: docs/worklogs/SG-058_report.md` (`CO-97`); `show` printed that first line. Fresh hash, no
existing note overwritten. **note=yes.**

## UNCLEAR

- **FIRST READ:** whether unifying the label was expected to also change any *prompt* string; it did not
  (the constant is display-only), and the packet's own `PG-SC-09` framing confirms that reading.
- **DURING EXECUTION:** the local `npm run build` bundle hash differs from the served hash because the
  Docker frontend stage injects `VITE_API_BASE`; reconciled by comparing served-pre to served-post.
- **REMAINING:** the Coder model id is not derivable from argv or observable metadata; reported `unknown`.
