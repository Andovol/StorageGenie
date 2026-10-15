# SG-194 — jobs.py cursor twin closed, rated 98

Immutable audit: base `03d24b4` → work `8a67ce3` (G1 hunk + 1 test module) → evidence `e2e2693` (12 logs) → paste `db663b5`. Trigger exit 0, `result=done id=SG-194 exit=0`. TWO receipts read back (WORK_HEAD note + paste dual-annotation note, identical trailer + Work-HEAD); paste note carries envelope-sourced settings (coder/model/effort all `*_source=command`, matching the trigger). Local `--ff-only` to the exact paste HEAD (`db663b5` == origin/automation). Scope: product diff exactly 2 files (+149/−6) + 13 worklog files; no other route/service/schema/migration/config/frontend. No restart, no deploy, production datastore never opened (two health GETs, delta none). Contract 0.50.0 echoed == packet expectation, sha match; host rules_check exit-3 known shape.

Holistic rating: **98/100**, no flag. Deduction attribution: coder (−2 duplicated pre/post-commit focused leg). First `D436` row: `slowest_waste` = `5s precommit-focused` (below); ratings table converts section-by-section from here.

## Evidence accepted

- A1: hunk read in diff — exact SG-188 mirror (`is not None` + `is None → 422 "malformed cursor"`), filter arithmetic untouched. Test module read in full — real routes on disposable SQLite (POST /v1/imports seeding, GET /v1/jobs assertions), discriminating row (malformed+empty 422 with detail) + two unchanged-behavior controls (db-order exact, lossless 25-job walk). FAIL half genuine (`assert 200 == 422` with page-1 body quoted); both runs committed (`PG-EV-09`).
- A2: diff scope exact; twin census 3/3 `decode_cursor` sites (1 fixed here + 2 SG-188) + 2 out-of-class reported-not-widened. Full backend suite once on candidate: 722 passed, 2 failed (test_signals barcode/OCR) → each run alone on base per `D443`, identical failure + host missing-lib warnings → environment, base-identical, correctly classified; no carried count. mypy 41/9 == base (jobs.py zero errors); ruff clean on touched files. Frontend untouched/unrun, stated.
- A3: 13 logs + report; elapsed 497 s vs ~300 s uncalibrated expectation (+66%; legs attributed: 203 s orientation+FIRST READ incl. mandated loading, 26 s implement+commit, 144 s `D443` verification, remainder freeze/receipt); constraints each answered; dispositions complete; first token SG-194.
- A4: receipts verified (both notes present at ref tip); pushes complete; bound lane receipt, retired finalizer untouched.
- Deduction (−2): pre-commit focused run (20 passed, 4.47 s) duplicated by the post-commit authoritative run — a needless loop, however cheap; the report itself downgrades it to ladder evidence.
- `slowest_waste` (`D434`/`D436`): `5s precommit-focused` — the only committed leg output this audit did not use (the post-commit run is authoritative). Next packet removes it: no pre-commit focused pass; the post-commit run gates acceptance. (Orientation output was used — premise confirmation is load-bearing. Suite/mypy/ruff conclusions were used.)

## Dispositions

| Item | Destination |
|---|---|
| jobs.py:116 twin | **RESOLVED** — all three list surfaces now 422 malformed cursors |
| Full-suite env rows (pyzbar/tesseract absent on host) | STATE known-host condition (host provisioning is Launcher's; no project action available) |
| Serving the repair | Session-close deploy rider (standing directive; unserved delta is now SG-194 only) |
| SG-194 REMAINING (no-deploy by design; nothing else open) | Closed here |

Harness context-size reading unavailable; no conclusion made.
