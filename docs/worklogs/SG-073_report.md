# SG-073 — remaining categories: Household/Documents chat fallback + classify activation + nav on landing

**Dispatch:** SG-073 · coder: opencode · effort: **medium** (read from process argv `/proc/<coder-pid>/cmdline` → `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Model:** `deepseek-v4.1-flash` — **provider metadata**, source `~/.local/share/opencode/log/opencode.log`, run=`8230b33f`, line `llm.provider=opencode-go llm.model=deepseek-v4.1-flash`. No `--model` on argv (CLI default, omitted per policy); not read from any system-prompt identity line.
**Contract:** recorded `0.28.2` == published (`0.28.2`); source path `/home/andrei/storagegenie-contract/VERSION`; contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2` (`contract-v0.28.2`).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`
**BASE ref:** `origin/automation` · **resolved:** `47c2f68e1dd0b94bcfb430d1cc5c111c197bcf87`
**WORK_HEAD:** `<WORK_HEAD>` (work commit; note target. The post-note receipt commit is HEAD after it.)
**Spend:** real **$0.000000** (zero metered calls; scripted provider through the real route only).

---

## Outcome (one line)

All three activations shipped: `household`/`documents` chat answer through the ONE shared generic `chat-v1` prompt grounded in their own catalogue (422-before → 200-after), Household chemicals + Documents/other classify through the existing path with pilot profiles (422-`Phase 3` → 200) and the served taxonomy now advertises both `active:true`, and `/` renders the App nav (Analytics link) unconditionally. Suites/build/lint green; 2 base-proved env reds; `$0`.

---

## Legs — actual vs budget (units per leg)

| Leg | Actual | Bound | Margin |
|---|---|---|---|
| Recon + premise reads | ~6 min | — | n/a |
| G1 chat gate + tests | ~4 min | 120 s/command | under |
| G2 activation + pinning inversion | ~6 min | 120 s/command | under |
| G3 nav line + landing test | ~3 min | 120 s/command | under |
| Full backend suite | **17.05 s** | 600 s | under |
| Frontend build + full vitest | **1.68 s + 4.42 s** | 600 s | under |
| **Overall (proc ~10:29Z → final)** | **well under** | 1800 s | under |

No command was killed; no interactive command was run.

---

## Enumerated sets (a set is a fact — criterion + enumeration)

- **Chat gate keys changed** (criterion: `chat:"fallback"` descriptor categories not yet accepted by `SUPPORTED_CATEGORIES`). Enumerated on the descriptor: `household_chemicals` (fallback), `documents_other` (fallback). Set = exactly those two; `cosmetics_personal_care` is `chat:"none"` and stays gated. Matches the packet's expectation exactly.
- **CATEGORIES rows flipped** (criterion: shipped rows whose `active` was False with `phase="Phase 3"`). Enumerated on `expiry_tracker.CATEGORIES`: `household_chemicals`, `documents_other`. Set = exactly those two. Matches.
- **Descriptor `active` flags flipped** (same two). Matches.
- **Landing route nav branches** (criterion: conditional `<Nav/>` renders). Enumerated in `App.tsx`: the single `pathname === "/"` branch. Set = one line. Matches.

---

## G1 — fallback chat for Household + Documents (generic agent, `$0`)

- `backend/app/services/chat/service.py`: `SUPPORTED_CATEGORIES` gains `"household": "household_chemicals"` and `"documents": "documents_other"`. The rest of the service (`respond`, `build_catalog`, `log_correction`) needed **no change** — it is already slug-keyed.
- **Prompt decision (design call, reported):** the fallback reuses the existing versioned `chat-v1.md` as the **shared generic template** — no new prompt file. Rationale: the descriptor's `category` vs `fallback` distinction is data only (there are no dedicated agents in code); `chat-v1` is already category-agnostic and contains the untrusted-DATA discipline; the scope ceiling bars "other prompts". No per-category fork was created. The category is injected through the catalogue block (`build_catalog` filters by slug and each entry carries `"category"`), and the route answers from that one category only.
- **FAIL-then-PASS (`PG-EV-09`):** pre-change `POST /v1/chat/household` → **422** `{"detail":"unknown chat category: household"}` (raw, quoted in `SG-073_verify.log`); post-change → **200** grounded, `catalogue_size=1`, one ledger row, scripted provider through the real route (`PG-SC-12`).
- **Prompt-shape pin** (`SG-066` precedent): `test_fallback_prompt_is_versioned_and_carries_catalogue_and_question` — `load_chat_prompt()` is `chat-v1` with the untrusted-DATA rule, and `build_user_content` carries the catalogue + the question. The delimiter is built from `chr(60)`/`chr(62)` (SG-062 lineage).
- **Isolation + corrections proven with the same leg shapes:** household grounding contains `Bleach` and not `Passport`/`Ibuprofen`; documents grounding contains `Passport` and not `Bleach`; `/v1/chat/household/corrections` → 200 with one `correction` event (`detail.category == "household"`). Cosmetics **still 422** (raw quoted).

## G2 — classify-path activation for Household chemicals + Documents/other (F-SG065-2)

- `backend/app/plugins/expiry_tracker.py`: rows `household_chemicals` (active True; `HOUSEHOLD_TIERS={upcoming:30}`) and `documents_other` (active True; `DOCUMENTS_TIERS={long_lead:60, upcoming:30}`, `has_expiry` stays False per the shipped row/blueprint). No new task type, route, or table.
- `backend/app/plugins/descriptor.py`: `active` flags for the two pilots `False → True`; comment updated because it claimed "inactive Phase-3 placeholders — see F-SG065-2" (text now matches inventory, `PG-SC-02` last clause).
- **Pinning inversion (`M9` reason per edit):** `test_classification_profiles_round_trip_and_inactive_phase` → renamed `test_classification_profiles_round_trip_and_activated_phase`. The rename is the M9 reason: a test named `..._inactive_phase` that asserts activation would be text contradicting behaviour. Its `inactive` list (asserting 422-`Phase 3`) is replaced with 200 assertions: household `tier_defaults == {"upcoming": 30}`, documents `tier_defaults == {"long_lead": 60, "upcoming": 30}`, both `opened_date_tracking is False`, slug read-back from the classification endpoint. The food/medicine/cosmetics asserts are **byte-unchanged**.
- **Manual-entry + extensions (acceptance):** added **inside the same pinning test** (the ceiling allows "pinning-test inversion only", so no second test file edit): household manual expiry entry → 200 (`expiry_date` read back, `date_type:"use_by"`); extensions → 200 for household and documents. Documents manual expiry entry is correctly **422 `non-perishable`** because the shipped `has_expiry` is False and blueprint §9.1 says Documents has "no consumption/expiry concept in the strict sense; reminder-only" — reported, not bent.
- **Inversion proof:** baseline original test green (asserts 422); new tests red against unchanged source (`assert 422 == 200`); source + tests green after. Both runs raw-quoted.
- **Served taxonomy:** `GET /v1/taxonomy` now reports `household_chemicals active=True` and `documents_other active=True` (raw body in verify log).

## G3 — nav renders on the landing route (D95)

- `frontend/src/App.tsx`: removed the `pathname === "/"` branch so `<Nav />` renders unconditionally, and dropped the now-dead `useLocation` import/binding (required by the one-line change; `tsc` build clean).
- **Landing-nav test (derived-set named file `frontend/src/components/shell/shell.test.tsx`):** the pre-existing `"the catalog route renders ONE StorageGenie wordmark (legacy nav gone)"` asserted the OLD D95-adjacent behaviour (no nav on `/`). It is inverted in place to `"the landing route renders the App nav with the Analytics link (D95)"` — Analytics link present, `Phase 0 · local-first` present, two `StorageGenie` wordmarks. Pre-change vitest `1 failed | 19 passed`; post-change `20 passed`. Raw quoted.
- **Visible consequence (reported):** `/` now shows both the App `<Nav>` and the CatalogPage shell header, so the wordmark appears twice and the legacy `Phase 0 · local-first` line returns to the landing route. That is the intended D95 effect (owner-reported missing nav), and the obsolete "ONE wordmark" assertion was the only test encoding the old state.

## G4 — worklog and report

`SG-073.log`, `SG-073_report.md`, `SG-073_verify.log` (this file set); first token `SG-073`; elapsed-vs-budget per leg; MODEL + effort from process args/metadata; real spend `$0.000000`; contract echo + source path; three UNCLEAR lines.

---

## Findings / disagreements (a difference is a finding, not an obstacle)

- **F-SG073-1 (packet premise impossible as written — the load-bearing finding).** G2 says "tier values read from the shipped rows/descriptor — quote them, never invent". **No numbers exist in-tree to read.** The shipped `CATEGORIES` rows carry `tier_defaults {}` and `phase "Phase 3"`; the descriptor carries only the mode NAME (`basic-expiry`, `long-lead-60-30`) and no numeric windows. I therefore declared them, as the SG-036 cosmetics precedent explicitly authorises (`G-A9`, "implement, mark uncalibrated, do not tune"): `HOUSEHOLD_TIERS = {upcoming: 30}` (blueprint §9.1 "Basic expiry only — Minimal special logic" = one basic window; the number 30 is the platform's default horizon, **not** read from any shipped row), and `DOCUMENTS_TIERS = {upcoming: 30, long_lead: 60}` (the mode name's own 60/30 pair). Both are marked UNCALIBRATED in code and here. This is a correction to the packet, not agreement.
- **F-SG073-2 (`unknown-household 404` premise false).** The packet lists "unknown-household 404" among the legs that must behave like food/medicine. There is **no household-existence gate** on `POST /v1/chat/{category}` (nor on the food/medicine legs historically): an unknown `household_id` returns **200** `status:"ok", empty_catalogue:true`, zero calls. Measured and pinned in `test_chat_unknown_household_answers_empty_catalogue_not_404`. The "same leg shape" is the empty-catalogue path, not a 404.
- **F-SG073-3 (scope-ceiling path naming gap, `M6`).** The ceiling names `backend/app/services/chat/ (service + its test file)`, but the chat service package contains no test file; the SG-038 test lives at `backend/tests/test_chat.py`. I treated that as the named test file. No other `backend/app/services/chat/` file was edited.
- **F-SG073-4 (prompt-file decision).** No new prompt file: the shared generic template is the already-versioned `chat-v1.md`. This is the packet's preferred "shared generic template" and avoids the "other prompts" STOP. There is no per-category fork.
- **F-SG073-5 (Documents has no expiry concept — manual entry correctly rejected).** The acceptance's "manual expiry entry + extensions accept the two newly-active categories" is met as one leg each across the set: manual expiry entry accepts **household** (the only newly-active category with `has_expiry=True`); extensions accept **both**. Documents manual entry returns 422 `non-perishable`, faithful to the shipped `has_expiry=False` and blueprint §9.1 "reminder-only". An alternative (flip documents to `has_expiry=True`) would have invented a different shipped value; not done.
- **F-SG073-6 (obsolete landing test inverted).** `shell.test.tsx` encoded the pre-D95 landing behaviour; inverted in place (the "derived set's named file"). Reported so the diff is not mistaken for unrelated shell work.
- **F-SG073-7 (descriptor comment stale).** The comment above `EXPIRY_TRACKER_TAXONOMY` described the pilots as "inactive Phase-3 placeholders — see F-SG065-2"; updated because the flags it describes are now True.

## Vacuous-pass check

The pass is **not vacuous**: the pre-change runs are red with the exact raw 422 / missing-link discriminators (`3 failed, 24 passed`; `1 failed | 19 passed`) and the post-change runs are green; the chat tests drive the REAL route + REAL service through the reader seam with a scripted provider (never the builder alone); isolation asserts a negative (`Passport` absent from household grounding and vice-versa); the pinning test asserts concrete tier_defaults and slug read-back, not just status; the taxonomy `active:true` was read from the served HTTP body; `mypy` was run at BASE and at work HEAD (41 vs 41, delta 0) rather than restated; the 2 suite reds were reproduced with the changes stashed. No gate was skipped and no empty set was reported.

## Receipt — notes ref (M20-corrected block; executed output pasted verbatim)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on WORK_HEAD, notes ref pushed, then fetched into a **mapped** local name and verified with `show`:

```
<RECEIPT_OUTPUT>
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`). Final line `<note=yes>`.

## UNCLEAR

- **FIRST READ:** whether "generic fallback prompt" required a second prompt file distinct from `chat-v1`. Re-read against the ceiling ("other prompts" is a STOP) and the "shared generic template is preferred" clause: reusing `chat-v1` is the intended shape; recorded as a decision, not hidden.
- **DURING EXECUTION:** that the shipped tree contains no numeric tier windows for the two pilot `CATEGORIES` rows, so the packet's "tier values read from the shipped rows/descriptor" is not literally satisfiable — resolved by declaring them uncalibrated (F-SG073-1) rather than inventing them silently.
- **REMAINING:** whether Documents/other should eventually carry `has_expiry=True` so its `long-lead-60-30` windows can drive a real reminder; this slice kept the shipped `has_expiry=False` (blueprint "reminder-only") and the question is left for the owner/Architect.
