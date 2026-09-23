# SG-097 — Parked Enrich remainder: Jina settings field + .env.example + docs + example

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE REF (packet ref `origin/automation`):** resolved `ff2f3c09edf657e6cc4f540e61e47ff24f30d8aa` (the packet requested the ref; it resolved there at start HEAD — two fields, not one)
**WORK_HEAD:** `4397d7f73fe558e3c4f80380d78b582e7405b1d2` (the work commit: `config.py` + tests + `.env.example` + README + the example artifact; the report/verify/log ride the docs-only receipt commit after it)
**Contract:** recorded `0.33.0` == published `0.33.0`; source path `/home/andrei/storagegenie-contract/VERSION` (contract repo HEAD `b232b84` = "Contract payload 0.33.0"); payload `RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`. **Echo verbatim: `0.33.0`.**
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`; provider metadata `/home/andrei/.local/state/opencode/model.json` `recent[0] = {"providerID":"opencode-go","modelID":"deepseek-v4.1-flash"}` — **not** a system-prompt identity line) · effort `high` (process argv `/proc/2751227/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant high # SG-097 …`).
**Spend (real $):** **$0.000000 actual.** Zero network calls: no live Jina call, no provider call, no metered resource touched.
**Autonomy:** `L2` (slice autonomy, 1 retry per `ARCHITECT.md:78-88`). No retry needed.
**DATABASE: none. Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`). The running service is untouched.

D130-approved parked Enrich remainder (the config/docs leg of SG-082's REMAINING). This slice declares the `Settings.jina_api_key` field, documents the key seam where an operator looks, and commits one worked example whose shape is asserted against the real driver. Endpoint+trigger, synthesis prompt+caller, and persistence model+migration remain out of scope.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on tree | Verdict |
|---|---|---|
| `jina.py:resolve_api_key` probes `settings.jina_api_key` via `getattr` then `JINA_API_KEY` env | `jina.py:91-104`: explicit → `getattr(settings, "jina_api_key", None)` (when a non-empty `str`) → `os.environ[JINA_API_KEY]` | **confirmed** |
| `Settings` declares no Jina field; `extra="ignore"` | `config.py` `Settings` had `opencode_api_key` only; `model_config = {"env_file": ".env", "extra": "ignore"}` | **confirmed** |
| `opencode_api_key` at `config.py:29` | exactly `config.py:29` | **confirmed** |
| `backend/app/models/` + `backend/alembic/` untouched | `git diff --stat BASE WORK_HEAD -- backend/app/models backend/alembic` → empty (R-MODELS-ALEMBIC) | **confirmed** |
| `.env.example` lacks `JINA_API_KEY`; NAMES-only line 1 convention | confirmed before; line 1 reads `NAMES only; copy to .env` | **confirmed** |
| 2 known decoder env reds (stash-proved) | bare-BASE run of the 2 `test_signals` tests → both fail (`pyzbar/libzbar is not installed`, `tesseract is not installed`) | **confirmed** |
| `origin/automation` == start HEAD | both `ff2f3c0…` | **confirmed** |
| Contract 0.33.0 == published `b232b84` | VERSION `0.33.0`; contract HEAD `b232b84` | **confirmed** |
| Adding the field breaks no other test | `test_privacy_audit.py::test_g2_web_senders_are_the_two_researched_sources` asserts **exactly two** files contain `jina`; the new `config.py` field is a third → suite collision. See **F-SG097-1** | **difference — M45 repair** |

## G1 — Jina settings field (one field)

- **Declared:** `jina_api_key: str | None = None` in `Settings` directly beside `opencode_api_key` (`config.py:32`), with a two-line comment naming SG-097 and the env fallback. No other settings change.
- **The seam (enumerated, with its criterion):** the function that turns configuration into the send-time key is `resolve_api_key(explicit)` (`backend/app/services/enrich/jina.py:91`). Its criterion, in order: (1) a truthy `explicit` argument → returned verbatim; (2) a truthy `settings.jina_api_key` **str** → returned; (3) `os.environ["JINA_API_KEY"]` → returned, else `None`. `fetch_jina_search` calls it at `jina.py:252` and degrades to a loud `missing_key:` snapshot with **zero sends** when it is `None`; the key is passed to `authorize()` (`jina.py:138`) which adds `Authorization: Bearer …` at send time only. **The seam matched the premise exactly, so `jina.py` was not modified** (see F-SG097-2 for the now-stale module docstring).
- **Live proof** (not only tests), raw in the transcript: with `jina_api_key=None` + env `test-env-check` → `resolve_api_key()` = env; field `test-field-check` + env → field; `resolve_api_key("test-explicit-check")` → explicit; nothing set → `None`.
- **No-migration claim by diff:** `git diff --stat BASE WORK_HEAD -- backend/app/models backend/alembic` is **empty** (R-MODELS-ALEMBIC). No migration is needed or written.
- **Question answered (`PG-SC-09`):** does configuration reach the sender through the declared field? **Yes** — `resolve_api_key` reads the declared field through the real `settings` singleton, and the send path uses its return value.

## G2 — precedence tests through the REAL seam

Four tests appended to `backend/tests/test_sg082_enrich_jina.py` (all drive the **real** `jina_mod.resolve_api_key` over the **real** `app.config.settings` — `PG-SC-12`; no re-implemented seam):

| Test | Precedence leg | Post-change assertion |
|---|---|---|
| `test_settings_field_beats_the_environment` | field vs env | returns `test-field-key` |
| `test_explicit_argument_beats_the_settings_field` | explicit vs field | returns `test-explicit-key` |
| `test_absent_field_falls_through_to_the_environment` | declared-but-`None` field vs env | returns `test-env-key` |
| `test_no_field_no_env_resolves_to_none` | nothing set | returns `None` |

- **FAIL-then-pass, both raw committed (`PG-EV-09` / `PG-EV-01`):** pre-change run (config unmodified) = **4 failed, 28 passed**; each new test fails **at its own `monkeypatch.setattr` line** with `AttributeError: Settings(...) has no attribute 'jina_api_key'` (per-test tracebacks at `test_sg082_enrich_jina.py:534, 541, 547, 554` — quoted individually in R-FAILPRE, not one shared paraphrase). Post-change = **32 passed** for the file (R-PASSPOST; 43 passed with `test_privacy_audit.py`).
- **Dummy literals only:** every key literal is `test-`-prefixed (`test-field-key`, `test-env-key`, `test-explicit-key`); no test interpolates a real value (R-GATES). The `JINA_API_KEY` **name** is used via `jina_mod.JINA_API_KEY_ENV`.
- **Gates:** full suite **2 failed, 461 passed** in 20.36 s — the 2 known `test_signals` decoder env reds, stash-proved on bare BASE (R-REDS-PROOF); `ruff check .` → **All checks passed**; `mypy app` → **41 errors in 9 files** == baseline (delta **0**); secret value-shape scan → **0 real-looking key values**.
- **Question answered:** does the precedence hold against the real seam? **Yes** — explicit > field > env is asserted on the real function and real `Settings`, and genuinely failed before the field existed.

## G3 — `.env.example` + docs + worked example

- **`.env.example`:** added the names-only line `JINA_API_KEY=` at **line 4**, immediately after `OPENCODE_API_KEY=` (R-ENV-EXAMPLE). The file's line 1 convention ("NAMES only; copy to `.env` and fill in") is preserved; no value is committed. End-relative grep (`PG-SC-11` family: `\[-1\]|HEAD~|\.endswith|\btail\b|\blatest\b`) over all touched files → **0 hits (exit 1)** (R-GATES). The line is inserted in the key block, not literally appended at EOF; the numbered listing shows the exact position, and no ordered-sequence tail reference was introduced.
- **Documented seam — the file the operator opens:** `README.md` gains a `## Enrich runbook — Jina fallback key (JINA_API_KEY)` section (after the Phase 3 runbook): how to rotate the key (`.env`), the precedence explicit → `Settings.jina_api_key` → `JINA_API_KEY` env, the send-time-only `Authorization` header, names-only builders/snapshots/logs, and the loud `missing_key:` zero-send degradation. This is the operator-facing home (the `OPENCODE_API_KEY` runbook sits in the same file); the enrich design doc (`docs/superpowers/specs/2026-09-21-ai-ingestion-enrichment-design.md`) is a design artifact, not a key-rotation page.
- **Worked example committed:** `docs/enrich-jina-request-example.md` — the exact `GET` URL the driver builds (EU-default base, repeated `site:` query, the four header names/values), names only, no key. `test_worked_example_artifact_matches_the_real_driver` reads that artifact and asserts the URL line equals the request the **real** `build_jina_request` builds, with the base/params/headers derived from the **real module constants** (`JINA_EU_BASE_URL`, `SITE_FILTERS`, `JINA_NUM`, `JINA_TYPE`, `JINA_GL`, `TOKEN_BUDGET`, `PAGE_TIMEOUT`, `RESPOND_WITH`) — never a re-typed copy. No live call.
- **`PG-SC-05` (key material excluded by rule):** the literal `JINA_API_KEY` appears only in names-only contexts — code identifiers (`jina_api_key`, `JINA_API_KEY_ENV`), the `.env.example` name line, docs prose, and the test env-name constant. Tree-wide hits over the diff are quoted in R-GATES; the refined value-shape scan over added diff lines (and the untracked artifact) finds **0** key-shaped tokens (no `jina_`-prefixed token, no unbroken 40+ alnum token, no quoted literal ≥ 24 chars). The real key remains only in the gitignored root `.env`.
- **Question answered:** can the next operator rotate the key from docs alone? **Yes** — README names the file, the variable, the precedence, and the failure mode; `.env.example` carries the name; the example shows the request shape.

## G4 — worklog and report

- `docs/worklogs/SG-097.log`, `SG-097_report.md`, `SG-097_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + the receipt). First token `SG-097` in each.
- **Elapsed vs budget (live clock, process start `2026-09-23T14:03:33Z`):** recon/premise ~60 s; G1+G2 (fail-pre, field, M45 repair, pass-post) ~90 s; G3 (`.env.example`, README, artifact) ~110 s; gates (suite 20.36 s + ruff + mypy + stash-proof + greps) ~100 s; G4 (worklogs + receipt) ~90 s; overall **~450 s / 1200 s**. Ordinary commands ≤ 300 s each, suite 20.36 s ≤ 600 s. No command was killed.
- **`PG-IC-01` cross-product:** no criterion demands an endpoint, synthesis call, migration write, live call, deploy, or container act — no cell collides. The slice is config + tests + docs; `DATABASE/Restart/Deploy/Container = none`.
- **`PG-IC-07`:** no fixed dates in the shipped artifacts; every timestamp in the logs is the live clock.
- `PG-PR-03`: no privileged operation attempted; nothing needed privilege.

## Findings

1. **F-SG097-1 (M45 suite collision — privacy-audit allow-set).** `test_privacy_audit.py:474` asserted `jina_files == {"services/candidates.py", "services/enrich/jina.py"}` — every app file whose lowercased source contains `jina`. Declaring `jina_api_key` in `config.py` makes it a third legitimate hit (a settings **name**, not a sender). Per M45 (suite-green binds), repaired minimally at root cause: `config.py` added to the allow-set and the docstring updated. No weakening: the web-search ban (`web_search`/`websearch`) and the excluded detection-source scan are unchanged; the single POST send site is still `opencode_go.py:252`. This is the only file touched outside the packet's explicit ceiling, and it is the collision repair the packet pre-authorized.
2. **F-SG097-2 (stale `jina.py` module docstring — out of ceiling, reported not edited).** `jina.py:20-24` still says "The installed settings module (`app.config.Settings`) declares neither field (extra fields are ignored), so on this tree the environment is the carrier; that is a disclosed finding (`F-SG082-2`)." After this slice the first clause is false. The packet's ceiling lists `jina.py` only for a *logic* change and only if the seam differs (it does not); a docstring edit is outside the ceiling, so I did not touch it. **Recommended follow-up:** a one-line docstring correction in a later slice. Flagged loudly rather than silently repaired.
3. **F-SG097-3 (pre-existing README `.gitignore` line reference).** README `:19` and `:240` cite `.gitignore:7` for `.env`; the actual line is **6** (`.gitignore:6`). Pre-existing, out of scope; my new section uses the correct `:6`. Not repaired.
4. **F-SG097-4 (packet Report-line wording).** The Report line calls `WORK_HEAD` the "work hash (docs-only diff)". This slice's diff is config+tests+docs, so following the SG-082 precedent (rated 98) `WORK_HEAD` is the work commit and the worklogs/receipt ride the docs-only commit after it.
5. **F-SG097-5 (`.env.example` position).** The new line sits at line 4 in the key block (after `OPENCODE_API_KEY=`), not at EOF. The packet's "append-discipline" is satisfied in spirit (no ordered-sequence tail reference introduced; PG-SC-11 regex 0 hits); the numbered listing shows the position.

## Vacuity check (loud)

No acceptance criterion passed vacuously. The four precedence tests genuinely fail pre-change (each with its own `AttributeError` traceback, R-FAILPRE) and pass post-change; the worked-example test reads the committed artifact and would fail if the artifact's URL line diverged from the real driver; the no-migration claim is an empty-diff check over the named paths; the secret gate is a value-shape scan over the actual added lines, not a name-only grep. **Where this slice is weaker than it looks:** (1) `jina_api_key` is read by `resolve_api_key` at runtime but no endpoint/sender is wired, so the field's effect is proven by unit seam + a live REPL check, not by an HTTP request (the endpoint is explicitly out of scope); (2) the ambient test environment has no `backend/.env` and no `JINA_API_KEY`, so the env-fallback tests set the variable explicitly — if a future run exports `JINA_API_KEY` process-wide, `test_missing_key_degrades_loudly_with_zero_sends` could be affected (it deletes the env var but not the now-declared field); noted, not hidden. (3) The `jina.py` docstring now contradicts the tree (F-SG097-2).

## Receipt note (notes ref, M20-corrected block)

Pushed the work to `automation`; worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. The note is added on WORK_HEAD, pushed to `refs/notes/storagegenie-coder-reports`, then fetched into a **mapped** local name and verified with `git notes --ref=… show`; executed output pasted verbatim below.

WORK_HEAD = `4397d7f73fe558e3c4f80380d78b582e7405b1d2`.

```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   ff2f3c0..4397d7f  automation -> automation
push_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports show 4397d7f73fe558e3c4f80380d78b582e7405b1d2   # pre-check
error: no note found for object 4397d7f73fe558e3c4f80380d78b582e7405b1d2.
existing_exit=1
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-097 | Report: docs/worklogs/SG-097_report.md | Work-HEAD: 4397d7f73fe558e3c4f80380d78b582e7405b1d2" 4397d7f73fe558e3c4f80380d78b582e7405b1d2
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   0ff745c..6d7a3b7  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg097-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg097-verify
fetch_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg097-verify show 4397d7f73fe558e3c4f80380d78b582e7405b1d2
Dispatch-ID: SG-097 | Report: docs/worklogs/SG-097_report.md | Work-HEAD: 4397d7f73fe558e3c4f80380d78b582e7405b1d2
show_exit=0
```

No existing note was found before adding (`existing_exit=1`), so this was not an existing-note refusal. The final tip (the docs-only receipt commit) is dual-annotated with the same note body (SG-092 note-anchor inoculation precedent).

Final tip D1 = `e0ba05f4e9abf1983724115df8063ac8dc76909f` (worklogs/report/verify). Its note was added, pushed, fetched into a mapped ref (`c4f5fbcedf38428dc73d4b882583dec8e41e0e93`), and read back:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-097 | Report: docs/worklogs/SG-097_report.md | Work-HEAD: 4397d7f73fe558e3c4f80380d78b582e7405b1d2" e0ba05f4e9abf1983724115df8063ac8dc76909f
add_tip_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
   6d7a3b7..c4f5fbc  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg097-verify
   6d7a3b7..c4f5fbc  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg097-verify
fetch_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg097-verify show e0ba05f4e9abf1983724115df8063ac8dc76909f
Dispatch-ID: SG-097 | Report: docs/worklogs/SG-097_report.md | Work-HEAD: 4397d7f73fe558e3c4f80380d78b582e7405b1d2
show_tip_exit=0
```

Final line: `note=yes`

## UNCLEAR

- **FIRST READ:** whether the packet intended `jina.py`'s stale module docstring (F-SG097-2) to be corrected here. The ceiling lists `jina.py` only for a logic change and only if the seam differs; the seam matched exactly, so I left the file byte-untouched and reported the contradiction. If the Architect wants the docstring corrected in this slice, that is the item to correct.
- **DURING EXECUTION:** the packet's "Suite-green binds on collision (M45)" was load-bearing: declaring the field broke `test_privacy_audit.py`'s exactly-two-`jina`-files assertion. I applied the minimal root-cause repair (allow-set + docstring) and disclosed it as F-SG097-1. Also, the packet's Report-line "(docs-only diff)" wording did not fit a config+tests+docs slice; I followed the SG-082 precedent and stated both hashes.
- **REMAINING:** the Enrich endpoint + trigger wiring (button `onRun`), the synthesis prompt + caller, snapshot persistence (model + migration), surfacing `web_alternates` as first-class review rows, and re-confirming the EU base / populated accept at the next live opportunity — all still out of scope and owed by later slices.
