# SG-119 — Brand alternates: OFF `brands` into the merge vocabulary + visible render

- **Dispatch-ID:** SG-119
- **Coder:** `opencode`
- **Effort:** `high` — read from the process arguments (`opencode run --auto --dir /home/andrei/StorageGenie --variant high`)
- **Model:** `unknown` — no `--model` flag is present on argv and no provider metadata is readable; the CLI default is the model (per policy). Not guessed.
- **Contract (verbatim echo + source path):** `recorded 0.36.0 == published (a9324d5)` — source `/home/andrei/storagegenie-contract/VERSION` = `0.36.0`; `git -C /home/andrei/storagegenie-contract rev-parse HEAD` = `a9324d5e1782384c036c1411ec8adac6bb2acaa1`; `sha256sum RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == payload `RULES.sha256`. (The repo's `.rules-cache/` directory is absent on this VPS copy; the host contract dir above is the authority the prior slices used.)
- **BASE_REF:** `origin/automation` → **BASE_RESOLVED:** `114876888e0e817d2f73472107854ea9181c7fd9` (== start HEAD; two fields, never one).
- **WORK_HEAD:** `3b53a191f0ee77e6bee654f1be887de8788642a9` (the docs-only receipt commit is a later tip; the note anchors this work HEAD).
- **DATABASE:** none touched (behavioural proofs on temp DBs + read-only live reads) · **Restart:** exactly ONE recreate (D10-authorized) · **Deploy:** rebuild + recreate + verify, this slice.
- **Spend (real $):** **$0.000000** — zero provider calls; every HTTP leg is a scripted `httpx.MockTransport`; no live OFF/Jina search.

## Premises re-verified against the tree (a difference is a finding, not an obstacle)

| Packet premise | Reality on the tree | Action |
|---|---|---|
| `map_off_decision_fields` emits `display_name`/`identifier`/`category_proposed` but drops `brands` | Confirmed (pre-change def `candidates.py:268`, body mapped exactly those three) | Mapped `brands` with `_web_provenance` |
| `client.py:26` `OFF_FIELDS` includes `brands` | Confirmed verbatim | — |
| `scoring.py:141` reads `product.get("brands")` | Confirmed | — |
| Jina mapper emits no brand | Confirmed (`map_jina_result_fields` maps `title`/derived category only; Jina payloads carry no brand) | Left untouched (population 3) |
| `enrich.py:112-113` records the gap citing `PG-SC-07` | Confirmed (docstring "`brand` is NOT in that vocabulary and no web path emits a brand…") | Now STALE — read-only file, reported as F-SG119-2 |
| `merge_web_fields` label-wins → alternates | Confirmed; rule code untouched | Vocabulary extended instead |
| enrich route attaches `web_alternates` (`enrich.py:216,226,252`); candidates route serves (`candidates.py:173-187`) | Confirmed | Served round-trip tested |
| frontend renders NO alternates anywhere | Confirmed — `Candidate` type had no `web_alternates`; grep found zero render hits | New `WebAlternates.tsx` + two surfaces |
| "label-visible brand present → alternate" with "no merge change" | `brand` was NOT in `LABEL_VISIBLE_FIELDS`; the vocabulary had to be extended for the alternate branch to fire | F-SG119-1 |

## G1 — OFF `brands` into the merge vocabulary (both populations, `PG-SC-07`)

**BEFORE capture (`PG-EV-08`).** The committed OFF fixture `off_hit.json` carries `"brands": "Jacobs"`; on the pre-change tree the endpoint produced NO brand field and NO brand alternate. Raw fail-pre quote:

```
E       AssertionError: assert [] == ['brand']
tests/test_sg103_web_alternates.py:239: AssertionError
```

**Change.** `map_off_decision_fields` now maps `product["brands"]` — a non-empty string used verbatim, or a non-empty list/tuple joined with `", "` — through the same `_web_provenance(value, source_type=OFF_WEB_SOURCE, source_url, retrieved_at)` envelope as its siblings. Absent/empty `brands` emits NOTHING (guard, not a fallback). `brand` was added to `LABEL_VISIBLE_FIELDS` (so the untouched `merge_web_fields` alternate branch fires) and to `ALLOWED_CANDIDATE_FIELDS` (so a committed proposal cannot crash on the field). `merge_web_fields` CODE is untouched.

**Populations (each with a named outcome):**

| Population | Outcome | Test |
|---|---|---|
| label brand present + OFF brands | label wins the field; web brand = ONE alternate with source triple | `test_label_brand_present_makes_web_brand_an_alternate`, `test_endpoint_brand_present_surfaces_and_roundtrips_brand_alternate` |
| brand-absent asset + OFF brands | **gap-fill** (decision below) | `test_brand_absent_asset_gap_fills_from_web` |
| OFF-miss / empty brands | no brand field, gap stays, no alternate | `test_mapper_emits_no_brand_when_brands_absent`, `test_off_miss_empty_brands_yields_no_brand_field_or_alternate`, `test_endpoint_off_miss_emits_no_brand_alternate` |

**Brand-absent decision (stated).** **Gap-fill wins.** `synthesize.py`'s `brand_absent` refusal is scoped to LLM-emitted facts with no payload grounding (`parse_synthesis` refuses a `brand` fact when the CALLER's brand input is absent); no synthesis runs in this slice, and the OFF snapshot IS the grounding, so mapping the payload's own `brands` is grounded, not invented. The two guards agree on the only real fabric point: OFF-miss/empty `brands` emits no brand (population 3). There is no substitute behaviour — nothing is invented and nothing is silently swapped.

## G2 — render the brand alternate (trace to the screen, `PG-SC-02`)

**Enumeration of every surface showing asset brand today** (criterion, not the packet's list):

| Surface | Shows brand how | Decision |
|---|---|---|
| `CandidateCard` (ReviewPage) | candidate `fields` (now includes `brand` when a label brand exists) | **RENDERED** — `WebAlternates` below the fields/evidence grid |
| `AssetDetailPage` (Enrich button) | press response `fields`/`web_alternates` were previously discarded | **RENDERED** — capture `EnrichResponse` and show `WebAlternates` beside the button |
| `AssetDetailPage` Assertions table | generic `field_path="brand"` row only | **named follow-up** — no GET route returns an asset's latest enrich candidate/alternates; the ceiling forbids adding one. A GET job→candidate path is the honest fix |
| `ItemInspectorDrawer` | raw JSON only; no first-class brand | not a brand surface; raw payload already carries everything |
| Catalog / Expiry / Chat / Planning | no brand rendered | not brand surfaces |

New `frontend/src/components/WebAlternates.tsx` renders `field: value · source_type · <a href=source_url>source</a> · retrieved_at`. The source URL lives in the anchor `href` and `title` only — never as visible text (SG-118 discipline). Fail-then-pass is quoted in the verify log (2 new tests fail without the render, pass with it).

## G3 — pins + suites (both runs committed, `PG-EV-09`)

- Backend: new `tests/test_sg119_brand_alternates.py` (10 tests: mapper provenance, list-join, both populations, miss→absent, endpoint round-trip, real commit path, vocabulary pin). Fail-pre `10 failed, 15 passed` → pass-post `25 passed` (focused SG-119/SG-103/SG-098). Full suite after: `2 failed, 593 passed`; the 2 reds are the SAME `test_signals` decoder — environment pair observed on the pre-change BASE run (`2 failed, 581 passed`).
- SG-103 updated: the conflict fixture now surfaces TWO alternates (`display_name` + `brand`); the no-conflict fixture now surfaces the label-brand conflict as exactly one `brand` alternate. SG-080's whitelist pin updated (see F-SG119-1).
- Frontend: 2 new render tests fail-pre → pass-post; full `vitest` `24 files / 211 tests passed`. `tsc` + `vite build` clean; `eslint src` exit 0. Runtime boot (`tsc` + vite) would be proven by `npm run build`, which succeeded.
- Backend `ruff` clean; `mypy app` = 41 errors / 9 files (baseline 41/9, delta 0).

## G4 — rebuild + exactly ONE recreate + served proof

One rebuild (`BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend`, exit 0, 10:48:44Z→10:49:01Z) then exactly ONE recreate (`docker compose up -d backend`: Recreate→Recreated→Started). **Container id changed** `16a07ae1af25…` → `e9b999e2f658…` (the authorized proof; `RestartCount+1` never asserted — M42). Image `b92210feb120…` → `b5a71b8bc20a…`.

- Served bundle `index-CYlI1-ao.js` (317045 B, `f15d01cc…`) → `index-DXSEg7CT.js` (318414 B, `f435cbc1…`); loopback GET bytes == in-image bytes (`f435cbc1…`); marker `web_alternates` 0→2 and `"Web alternates"` 0→2.
- Alembic `20260924_sg114_relation` unchanged; 28-table counts `3c7cd88d…` identical (DELTA 0); `provider_call` 17→17 (no press ran); health 6× exact; gate http 301 / https 401 (first two tries returned `000` — transient DNS; third answered).
- **GET-only served read (narrowest, reported):** I did NOT drive a brand-alternate fixture through the live route (that would write rows). Instead: `GET /openapi.json` asserts the unchanged route contract (`/v1/candidates/{candidate_id}` + `/v1/enrich/{asset_id}` present), `GET /assets/index-DXSEg7CT.js` carries the new render marker, and `GET /v1/candidates/<existing id>` returns the `web_alternates` key (`[]` on the pre-change row). No POST, no rows created.

**Containment (`PG-PR-06`, per leg, units):** G1+G2+G3 ~900 s (budget 1200 s); G4 ~110 s (budget 1200 s); overall ~1000 s wall clock (budget 1200 s). No command killed; none hung.

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| BEFORE/AFTER brand pair quoted; brand-absent decision explicit with discipline cited; miss→absent no alternate | **MET** | `assert [] == ['brand']` pre; populations table + gap-fill decision; miss tests |
| Brand alternate visible on every brand-showing surface (enumerated) with source, or named follow-up; ids never visible text | **MET** | CandidateCard + AssetDetailPage render; assertion-table GET path named follow-up; URL in href only |
| Fail-pre red + pass-post green quoted, both committed, backend + frontend; suites green modulo base reds; build+lint clean | **MET** | 10 fail-pre → 25 pass; 2 frontend fail-pre → pass; 2 base env reds stash-same; tsc/vite/eslint clean |
| Exactly ONE recreate (container-id change); bundle/health/gate/alembic/counts as stated; GET-only served read quoted | **MET** | container `16a07ae1…`→`e9b999e2…`; all AFTER values above; openapi + bundle + candidate GET |
| $0; no press; no writes outside ceiling; no vacuous pass | **MET** | MockTransport only; provider_call 17→17; diff limited to ceiling; every new gate seen to fail pre |

**Vacuous-pass check (`PG-EV-01`, loudly):** every new backend gate was seen to fail on the unmodified source at its own assertion (10 failures), and the 2 new frontend gates failed without the render. The 4 "absence" tests (miss→absent) legitimately pass on BASE because absence is what BASE also produced — they are NOT the proof of the feature; the paired positive tests are, and those failed pre. **Where this slice is weaker than it looks:** (a) the brand-absent-asset population is UNREACHABLE through the real endpoint (empty query brand caps OFF at 0.55 < 0.60), so it is proven at the mapper/merge unit level only; (b) the asset-detail alternates are visible only after a live press (no GET read path), so a page reload loses them — named as the follow-up; (c) no writer currently produces a `brand` label assertion on this tree, so the label side of a real conflict depends on a future writer (F-SG119-3).

## Design calls (mine, reported)

- **G1 vocabulary:** `brand` added to BOTH `LABEL_VISIBLE_FIELDS` and `ALLOWED_CANDIDATE_FIELDS`; `merge_web_fields` code untouched. This is the mechanical consequence of the slice title ("into the merge vocabulary") and is required for the enrich commit path to stay green.
- **G1 brand-absent:** gap-fill over a gap-stay, for the grounding reason above.
- **G1 list brands:** joined verbatim with `", "` rather than dropped — a silent drop of a payload-carrying brand would be the defect the packet names.
- **G2 asset detail:** render the PRESS RESPONSE rather than adding a GET route (ceiling), and name the on-load path as a follow-up.

## Findings / disagreements

- **F-SG119-1 (forced a pin update):** the packet's "no merge change: label-visible brand present → alternate" is impossible without extending the vocabulary, and adding `brand` to `LABEL_VISIBLE_FIELDS` puts the label brand into the merged `fields`, which the REAL commit path (`_create_asset_for_candidate`) rejects unless `brand` is also in `ALLOWED_CANDIDATE_FIELDS` (base-green `test_sg098` commits an enrich proposal). I therefore added both. That breaks `test_sg080`'s pin "none of OTHER_V3_FIELDS is in the candidate whitelist"; I updated that assertion to keep the true property (the EXTRACTION builder still does not emit `brand` into `fields`) while allowing the SG-119 WEB path whitelist. Classified as a candidate test (scope: "backend enrich/candidate tests").
- **F-SG119-2 (read-only, reported not fixed):** `api/v1/enrich.py:112-114`'s docstring still says "`brand` is NOT in that vocabulary and no web path emits a brand" — now false. `enrich.py` is READ-only under the ceiling; a one-block docstring correction is owed.
- **F-SG119-3 (pre-existing):** the v3 extraction `brand` field (`schemas.py:83`) is not promoted into candidate `fields` by `build_candidate_from_extraction`, and no writer produces a `brand` label assertion. So the label side of a brand conflict exists only if seeded (tests) or written by a future path. Candidate: a later slice could promote the extraction `brand` (SG-080 explicitly deferred it).
- **F-SG119-4 (pre-existing, honest):** with an empty query brand, OFF's maximum score is `0.4*1 + 0.2*(0.5+0.25) = 0.55 < 0.60`, so a brand-absent asset can never get an accepted OFF decision through this scoring. The packet's middle population is thus unreachable in production; it is decided and unit-tested, and the observation is reported.
- **F-SG119-5 (transient):** the external health gate returned `000` twice right after the recreate before answering `301/401`. No action; reported for the record.

## Receipt note on the notes ref (M20-corrected block)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on the work HEAD; notes ref pushed; verified against the explicitly fetched, MAPPED ref (`refs/notes/storagegenie-coder-reports-sg119-verify`). Existing-note refusal is a STOP; the precheck showed no existing note. Executed, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show 3b53a191f0ee77e6bee654f1be887de8788642a9   # precheck
error: no note found for object 3b53a191f0ee77e6bee654f1be887de8788642a9.
precheck_exit=1

$ git push origin automation
To github.com:Andovol/StorageGenie.git
   1148768..3b53a19  automation -> automation
PUSH_EXIT=0

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-119 | Report: docs/worklogs/SG-119_report.md | Work-HEAD: 3b53a191f0ee77e6bee654f1be887de8788642a9" 3b53a191f0ee77e6bee654f1be887de8788642a9
note_add_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   73db1b4..8ba2509  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg119-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg119-verify
fetch_exit=0

$ git rev-parse refs/notes/storagegenie-coder-reports-sg119-verify
8ba250971bd458e94dc43122df916bb89eaa8faa

$ git notes --ref=refs/notes/storagegenie-coder-reports-sg119-verify show 3b53a191f0ee77e6bee654f1be887de8788642a9
Dispatch-ID: SG-119 | Report: docs/worklogs/SG-119_report.md | Work-HEAD: 3b53a191f0ee77e6bee654f1be887de8788642a9
show_exit=0
```

First line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). The final tip (this docs-only receipt commit) is dual-annotated with the same note (SG-092 inoculation).

## Three UNCLEAR lines

- **FIRST READ:** whether "brand-absent asset + OFF brands" should gap-fill or keep the gap under `synthesize.py`'s refusal discipline. I chose gap-fill because that discipline governs LLM-emitted facts without payload grounding and no synthesis runs here; the OFF payload is the grounding. A different reading (gap-stays) would need asset state threaded into the mapper or a merge-rule change, neither in this ceiling.
- **DURING EXECUTION:** whether `brand` belonged in `ALLOWED_CANDIDATE_FIELDS`. The base-green enrich-commit test forced it (otherwise every enrich commit with a label brand raises), which then forced the SG-080 whitelist-pin update. I treated the SG-080 file as a "candidate test" within the ceiling; if the Architect considers it out of scope, the alternative is unbounded (either the commit path skips brand silently — the defect class the packet forbids — or the whole alternate becomes uncommittable).
- **REMAINING:** the asset-detail alternates are only visible after a live press; an on-load GET job→candidate/alternates route is the honest follow-up. And no writer produces a `brand` label assertion yet, so the label side of the conflict is latent until that writer exists.

note=yes
