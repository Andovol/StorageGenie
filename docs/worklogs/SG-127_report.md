SG-127 — Follow-up batch: thumbnail bytes, brand promotion, job→candidates route (serve it)

**Dispatch-ID:** SG-127 · **Coder:** opencode · **Effort:** `high` (argv
`opencode run --auto --dir /home/andrei/StorageGenie --variant high "$(cat docs/packets/SG-127-followup-batch.md)"`,
from the trigger per D302/D120) · **Model:** `deepseek-v4.1-flash` (provider metadata banner
`> build · deepseek-v4.1-flash` in `output/dispatch/SG-127.log`; no `--model` on argv = the
contract-legal omitted-model subset — never a system-prompt identity line).
**Contract (verbatim echo + source path):** recorded `0.37.0` == published `0.37.0`.
Source `/home/andrei/storagegenie-contract/VERSION` reads `0.37.0`; checkout HEAD
`1acd7730e5fa6de5b7403aacce71207e9946461d` (== packet's `1acd773`, D15 adoption); `RULES.md` sha256
`18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == payload `RULES.sha256`.
`.rules-cache/` is absent on this host (standing, SG-121 F-SG121-1); the contract checkout above is the
source path used.
**BASE REF:** `origin/automation` — **BASE COMMIT (resolved):** `29391674433b4e4cbeed1410dd286bbb4374b5a4`
(start HEAD; worktree clean).
**WORK_HEAD:** `1902c4460bccb2aba9eb370fa358202c1c61dfbd` (the commit carrying this report + log + verify log).
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `git@github.com:Andovol/StorageGenie.git` (as on host).
**Spend:** real `$0.000000` vs `$0` bound — zero provider calls, no metered call exists on any path.
**Network:** none (no fetch, no foreign image, no named runtime). **DB:** no feature writes; live reads only
for served verify. **Deploy:** rebuild + **exactly ONE** recreate (`PG-PR-04`).

**Verdict: GO.** Three features + serve shipped; suite green-except-base-proved-reds; ruff clean; mypy delta 0;
one rebuild + one recreate; served proofs on the live routes. Worktree clean.

## G1 — thumbnail bytes match the name (F-SG118-2) — MET

Fix (chosen: flatten every source to JPEG — the first option the packet offered): `_thumbnail_bytes`
(`backend/app/services/evidence_service.py:139`) now runs the RGBA/P/other→RGB flatten and
`save(format="JPEG")` for **every** decodable source; the png/webp `{"image/png": "PNG", "image/webp":
"WEBP"}` branch is removed. `thumbnail_path` stays `.jpg` (`local_store.py:10`), the reader stays
`image/jpeg` (`api/v1/evidence.py:120`) — the type did not need to move; the bytes moved to meet it.

- **Fail-then-pass, real fixtures per source type** (`PG-EV-09`; both runs in `SG-127_verify.log`):
  FAIL `5 failed, 4 passed` (png/webp magic mismatched before the fix); PASS `69 passed`. The per-type test
  asserts served `content-type == image/jpeg`, body magic `ffd8ff`, Pillow format `JPEG`, and the on-disk
  artifact suffix `.jpg` for **jpeg / png / webp / heic**.
- **HEIC fate (stated):** unchanged and correct — HEIC/HEIF already took the JPEG flatten branch; name
  `.jpg`, bytes JPEG, reader `image/jpeg`. Asserted by the same per-type test.
- Deployed image, in-memory (no write): png/webp/jpeg all `ffd8ff` (`SG-127_verify.log`).

## G2 — extraction brand promotion (F-SG119-3) — MET

- `build_candidate_from_extraction` (`candidates.py:607`) promotes `("brand", item.brand)` through the
  existing `_extraction_value_field` (null stays null; no invented/substituted brand).
- **Label-assertion writer:** no new writer was needed — `brand` is already in `ALLOWED_CANDIDATE_FIELDS`
  (`candidates.py:95`), so the existing `_create_asset_for_candidate` (`candidates.py:877-900`) writes the
  `field_path="brand"` assertion once the value is in `fields` (`source_type="extraction"`). Proven.
- **`PG-SC-02` trace to the served read:** `GET /v1/candidates/{candidate_id}` returns
  `fields.brand == {"value": "DairyGold", "source_type": "extraction", …}`; the new G3 route lists the same
  `fields` payload. Fail-then-pass both committed (test asserts the served read AND the committed assertion).
- **Split-child discipline:** `brand` joined `_split_child_fields`'s item-derived set + per-item loop, so a
  split child takes **its own** item's brand or none — never the origin's (no substitution). Test:
  child[0]="DairyGold", child[1] has no brand.
- **Pin flip (finding F-SG127-3):** `test_sg080_ingest_pipeline.py:387-392` asserted the SG-080 deferral
  (`brand not in proposal["fields"]`). That property is intentionally retired by G2; the test now keeps the
  TRUE remaining property (every OTHER v3 field stays deferred) and asserts the promotion. SG-119 precedent
  (F-SG119-1).

## G3 — GET job→candidates route — MET

- New `GET /v1/jobs/{job_id}/candidates` (`api/v1/jobs.py`), gated by the neighboring read's exact helper
  `_owned_job` (unknown job → 404 "Job not found"; foreign household → 403 "Household mismatch"), returning
  `{"items": [...], "total": n}` ordered by `(created_at, id)`. No invented gate.
- Served legs (live): known job → **200** `total=1`; unknown job → **404**; foreign household → **403**;
  missing `household_id` → **422** (the flag gate — not 301/401).

## G4 — serve + verify + worklog — MET

- Rebuild `docker compose build backend` exit 0 (14:02:36Z→14:02:48Z, 12 s of a 600 s bound). Image
  `b5a71b8bc20a…` → `665d200ba183…`.
- **Exactly ONE recreate** `docker compose up -d backend` (Recreate→Recreated→Starting→Started, 14:02:56Z).
  **Container id changed** `e9b999e2f658…` → `6b606c6a61e9…` (the authorized proof). Health exact
  `{"status":"ok","db":"ok","storage":"ok"}` at 14:03:00Z (~3 s, well under the 60 s STOP bound).
- Alembic head `20260924_sg114_relation` **unchanged**; 28 tables; **sum_rows 284 → 284 (delta 0)**.
  Seed rows stay (quoted): household `01a0a029-1477-7ca0-b200-bce78a96c679` "Popescu Household";
  evidence 13 (`image/jpeg,image/png,text/plain`); jobs 8; candidates 7; assets 6; assertions 28.
- Served proofs: thumbnail `GET /v1/evidence/01a0a467…/thumb/256` → 200 `image/jpeg`, magic `ffd8ff`;
  candidate read 200; new route 200/404/403/422 above; deployed-image in-memory G1+G2 proof.
- **`PG-DP-02` waiver (stated with substitute location):** no full end-to-end sweep — the recreate gates it.
  Substitute authority = the targeted live served probes above + the in-process fail-then-pass suite in
  `SG-127_verify.log`.

## Money posture

`$0.000000` actual vs `$0` bound. No metered call exists on any path: no provider SDK call, no key, no network.
A metered call would have been a STOP-and-report; none was made.

## Findings (loud, including out-of-scope)

- **F-SG127-1 (live-data, honest):** the live DB carries **no** brand in any candidate `fields` and **no**
  `brand` assertion; 4 candidates carry extraction brands only in `ai_items` (`Pilos`, `Milbona`, `VITASIA`,
  `BARONI/PIKOK`). Promotion is a **build-time** act, so a live served brand read is impossible without a
  production write, which this packet forbids. Substitute proof: deployed-image in-memory build produced
  `fields.brand = DairyGold/source_type extraction` (`SG-127_verify.log`) + the G2 fail→pass served-read test.
  The served live candidate read still returns 200 (shape correct); brand is correctly absent from it (data).
- **F-SG127-2 (live-data, honest):** every live PNG evidence carries **legacy `.png` thumbnails** (pre-SG-118
  naming). The reader looks for `.jpg`, so those live PNG thumbs 404; only the JPEG evidence has served `.jpg`
  thumbs. They were **not** deleted (SG-128 owns storage writes; orphan deletion is out of ceiling). This is
  why the live served thumbnail proof exercises the JPEG path; the png/webp fix is proven in-process and on
  the deployed image in memory.
- **F-SG127-3 (pin flip, in-ceiling):** SG-080 deferral pin updated for the intentional brand promotion (G2).
- **F-SG127-4 (minor, out of scope):** `STATE.md:2/4` still reads contract `0.36.0` while AGENTS/packet/checkout
  read `0.37.0` (carried from SG-121 F-SG121-3; Architect's file).
- **F-SG127-5 (minor, uncertain):** the local `/home/andrei/storagegenie-contract` repo has 14 tags, max
  `contract-v0.33.0`; **no local `contract-v0.37.0` tag** (AGENTS.md:4 says it is published). The tag may
  simply be unfetched locally; VERSION + HEAD were used as the authoritative echo. Not bent to match.
- **F-SG127-6 (out of scope, carried):** legacy `.png` orphan thumbnails remain on the storage volume; a
  storage-write slice (SG-128) owns their enumeration/deletion.

## Vacuous-pass statement (`PG-EV-01`/`PG-SC-09`)

No pass is vacuous. Every new/changed gate was **seen to fail** on the unchanged source at its own assertion
(the FAIL run: png/webp thumbnail magic, brand promotion, split-child brand, route 404). The new route tests
drive the real `_owned_job` gate (404/403) and the real handler (200 + items), not a mock. The thumbnail test
asserts **served bytes** (`content-type` + magic + Pillow format) against the **served name** (`.jpg`
suffix), per source type — not a helper in isolation. The base-2 `test_signals.py` reds are stash-reproved on
the pristine BASE tree (`2 failed, 5 passed`), so they are environment reds, never inherited from this slice.

## Receipt note on the notes ref (M20-corrected block)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`; no
`{{RECEIPT_CMD}}`. Note added on WORK_HEAD (`1902c4460bccb2aba9eb370fa358202c1c61dfbd`); notes ref pushed; verified against the
explicitly fetched **mapped** ref (`refs/notes/sg127-verify`); executed output pasted verbatim below
(`SG-127_verify.log` also carries it). Existing-note refusal is a STOP; the precheck showed no existing note.
Final tip dual-annotated (SG-092 precedent, note-anchor inoculation). Final line `note=yes`.

```text
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   2939167..1902c44  automation -> automation
push_automation_exit=0

$ git notes --ref=refs/notes/storagegenie-coder-reports show 1902c4460bccb2aba9eb370fa358202c1c61dfbd   # precheck
error: no note found for object 1902c4460bccb2aba9eb370fa358202c1c61dfbd.
precheck_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-127 | Report: docs/worklogs/SG-127_report.md | Work-HEAD: 1902c4460bccb2aba9eb370fa358202c1c61dfbd" 1902c4460bccb2aba9eb370fa358202c1c61dfbd
note_add_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   0003b55..6945140  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg127-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg127-verify
fetch_exit=0

$ git notes --ref=refs/notes/sg127-verify show 1902c4460bccb2aba9eb370fa358202c1c61dfbd
Dispatch-ID: SG-127 | Report: docs/worklogs/SG-127_report.md | Work-HEAD: 1902c4460bccb2aba9eb370fa358202c1c61dfbd
show_exit=0
```

## Budget — actual vs bound (units; live clock, `PG-PR-06`)

- Orientation + premise verification + baseline suite: ~25 min wall of the session / 1800 s overall — under
  (baseline suite itself 30 s of a 600 s bound).
- G1+G2+G3 implementation + fail/pass test runs: focused run 3.92 s, fail run 1.50 s (both of a 600 s bound).
- G4 build+recreate: build 12 s + health ~3 s = ~15 s / 600 s build bound — under.
- Full suite (post-change): 31.99 s / 600 s; ruff < 5 s; mypy ~30 s.
- Overall: session well under 1800 s expected ~1200 s. No command killed; no interactive command.

## UNCLEAR

- **FIRST READ:** whether `brand` needed a new assertion writer (it did not — `ALLOWED_CANDIDATE_FIELDS`
  already contained it, so the existing commit path writes it), and whether the live DB held any promoted
  brand (it does not; brands live only in `ai_items`).
- **DURING EXECUTION:** how to satisfy the live "brand on a served read" probe under the no-production-writes
  rule with zero live brands. Chose: deployed-image in-memory build proof + fail→pass served-read test, and
  reported the data limitation as F-SG127-1 rather than performing a forbidden write. Also chose the
  JPEG-flatten option over renaming, and extended the split-child discipline (in-ceiling) to avoid a brand
  substitution on split.
- **REMAINING:** (1) legacy `.png` thumbnail orphans on the volume → SG-128; (2) `STATE.md` contract stamp
  `0.36.0` → Architect; (3) local `contract-v0.37.0` tag absent → confirm/fetch; (4) no live candidate
  demonstrates a promoted brand until a future import runs on the deployed image.
