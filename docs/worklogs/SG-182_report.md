SG-182 report — full recovery audit: operations, test trust and consolidated recovery scope

Model / effort: coder opencode, model opencode-go/deepseek-v4.1-flash, effort max — read from own process args
(/proc/$PPID/cmdline: "opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash
--variant max"). Served-model response metadata was not available; no substitute value claimed. `max` is
catalogue-valid but uncalibrated vs D120/D15-high (G-A9, stated).
Working dir: /home/andrei/StorageGenie (branch automation). Remote: git@github.com:Andovol/StorageGenie.git.
BASE (packet requested `automation`, resolved at dispatch, clean): d0591dc83810e987f656894a037dda8f633e208b.
WORK_HEAD (work commit as of report writing): 7a16bae; the report lands in the next commit by design (CO-55b) and
the notes receipt carries the published head. Write ceiling respected: docs/worklogs/SG-182* only; no product,
config, lock, test, migration or operator-script change; scratch outputs were /tmp/opencode scratch and are removed
after verified containment.

Contract (G-L1): on-host checkout /home/andrei/storagegenie-contract — VERSION=0.47.0, sha256(RULES.md)=
49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed equals RULES.sha256 payload, HEAD bdbbaa75df06,
`git describe` reachable tags: none (tag-object peel still not done — limitation retained from SG-181).
rules_check.sh output: `G-L1 UNCHECKED the cache is not checked out at a contract tag`; `G-L5 UNCHECKED
gh-unauthenticated`; `G-L7 UNCHECKED gh-unauthenticated`; G-L6 bytes codex 2275 / opencode 1933; exit 3.
Contract version 0.47.0 echoed in the receipt.

Health (CO-92): START `{"status":"ok","db":"ok","storage":"ok"}` -> END identical; delta none.
Lane budget/deadline/elapsed (own-dispatch metadata only): unit cgroup dispatch-storagegenie@SG-182.service;
ancestor runner pid 1525733 starttime ticks 668440626, btime 1785224168, CLK_TCK 100 -> start epoch 1791908574;
RUN_BUDGET_S=2100 from world-readable /etc/dispatch/storagegenie.conf -> deadline epoch 1791910674; report written
at epoch 1791909159, elapsed 585 s of 2100 s. No command hit its bound; no hang; no watcher. No privileged
operation was attempted (all optional environment/Docker probes excluded) -> no denial -> no PB-2 stop.

(a) Issues / deviations / surprises
1. PB-1 correction: the packet says alembic.ini line 23; the `sqlalchemy.url` line is line 3 (file is 35 lines).
   The override statement itself is right: env.py:23 calls config.set_main_option with settings.database_url, and
   the probe proves the env override is effective (ini-path DB backend/data/db never created).
2. F-SG182-1 CONFIRMED hypothesis with a direction detail: `_guard` rejects work==prod and prod-inside-work
   (message in that case names the opposite geometry), but ALLOWS work-inside-prod — the case its message claims.
   With that shape the drill's storage destination lands inside its own copy source. Consumers: the SG-086 drill
   itself; the README runbook invokes it with the default mkdtemp work dir (disjoint). No production incident
   inferred; the drill was deliberately NOT executed on that shape; operator script untouched (Twin: no other
   `_guard`-style comparator found in repo scripts; class count of similar copy-into-source guards = 1).
3. F-SG182-2: same-length DB corruption can keep `PRAGMA integrity_check=ok` (observed) — only byte equality/hash
   detects it; evidence-store names+sizes fingerprints are blind to same-length content corruption (re-proved).
   This strengthens SG-180 F-SG180-3 framing: hash comparison is the load-bearing control, not integrity_check.
4. F-SG182-5: production schema is AT this tree's single head (`20260924_sg114_relation`) and the served CSS hash
   equals a fresh scratch build's CSS hash, while the JS differs — deployed build differs from current source but
   shares the theme stylesheet. Effective deployed AI config: provider opencode-go, model deepseek-v4-flash-vision-exp,
   consent true, caps null, category food (config.py defaults are fake/false — env makes them differ).
5. F-SG182-6: README lint gate `mypy app` is RED at this tree (41 errors / 9 files) while ruff and frontend tsc
   are green. No CI exists to catch it; introducing commit not established -> root cause unknown (CO-37), not
   "pre-existing".
6. Two probe-side assumption bugs of my own were found and preserved: (i) fingerprint compare used different
   filenames; (ii) alembic logs to stderr and /v1/assets returns a cursor envelope. Both failed runs are committed
   (`SG-182_g1_run_failed_2026-10-13.log`, `SG-182_migrations_run_failed_2026-10-13.log`) and reruns used new
   paths — no earlier run was overwritten (SG-181 recurrence lever honoured). Both are probe defects; product
   untouched.
7. Coverage limits retained: container/image identity UNVERIFIED (Docker excluded); gh unauthenticated so remote
   workflow/run provenance UNVERIFIED (NOT proof of no remote CI); production volume contents not fingerprinted;
   native zbar/tesseract absent in the audit venv (deployed image installs them at Dockerfile line 14); no
   vulnerability certification from a lockfile alone (no advisory tooling/config in repo; prior elevation-only
   Dependency-Graph observation REC-ISS08); true concurrency, authenticated public URL, normal Tab/zoom/touch/
   320 px reflow remain unexercised.

(b) Actions
- Pages read/reconciled (not re-derived): canonical register, user scenarios, recovery plan, SG-173/174/175/179/
  180/181/183 audits, ratings, STATE, decisions, backlog, dispatch conf, contracts.
- Wrote and ran committed probes: SG-182_probe_g1.py (guard + real drill), SG-182_probe_migrations.py (fresh
  upgrade + real readers), SG-182_probe_served.py (GET-only served identity + mode=ro schema read).
- Build/type gates run offline with existing tooling: frontend tsc 5.9.3 rc=0; vite build rc=0 (3.04 s, scratch
  outDir; local frontend/dist untouched); backend ruff 0.16.5 rc=0; backend mypy 2.3.1 rc=1 (41 errors).
- Focused test nodes run once: backend/tests/test_backup_drill.py + test_runbook_commands.py = 6 passed, 0.10 s.
- External/production effects: NONE written. Read-only production observations only: health GETs, /v1/settings/ai
  GET, index/asset GETs, and a mode=ro sqlite read of alembic_version/table count. No production backup/restore,
  no deploy/restart, no provider call, no installs, no auth/credential/infra change, no other-project/env read.
- Commits (all evidence-only): 1e17c20 G1, 8b71da6 G2, e7ddf41 G3 consolidation, 7a16bae limits note; report in
  the next commit. Push + notes receipt with remote readback follow the report.
- Durations (UTC, from box clock): engine start 1791908574; report write 1791909159; elapsed 585 s. Test-command
  count: 1 focused pytest invocation (plus 3 probe executions, each with preserved failed/running logs).
  Retry count: 0 slice retries; 2 probe reruns after probe-side fixes (verification_attempts, not retries).
  Provider-call count: 0 (all scripted/off). Health delta: none. Highest-impact action: the guard defect proof
  on the ACTUAL helper + the production-schema-at-head observation.

(c) Verification — verbatim blocks (full logs committed; labels per invocation)

G1 guard + drill (docs/worklogs/SG-182_g1_run_2026-10-13.log):
[PASS] guard[equal] expected=rejected actual=rejected ... msg='STOP: work-dir .../guard/stor is inside production storage .../guard/stor'
[PASS] guard[source-inside-work] expected=rejected actual=rejected ... msg='STOP: work-dir .../guard/enclose is inside production DB .../guard/enclose/db2/prod.db'
[PASS] guard[work-inside-source] expected=allowed actual=allowed ... msg=''
[PASS] guard[work-inside-source] drill storage destination lands INSIDE its own source (recursive copy shape the guard missed; drill intentionally not executed) backup_dir=.../guard/stor3/work/backup
[PASS] guard[disjoint] expected=allowed actual=allowed ...
[PASS] guard[missing-db] expected=rejected actual=rejected ... msg='STOP: production DB not found: ...'
[PASS] synthetic prod has WAL-resident committed state wal_bytes=61832
[value] control (raw single-file copy is not a backup): raw-cp-of-only-main-file cannot even read schema: OperationalError: no such table: household
[PASS] full drill exit code 0
[PASS] drill reports production-untouched
[PASS] built-in same-length corruption gate observed failing
[PASS] backup integrity_check ok
[PASS] backup counts == live BEFORE counts (WAL-resident state captured) {"asset": 5, "evidence": 3, "household": 1}
[PASS] backup real row reader returns all synthetic rows [('a0','h1','Asset 0'),...('a4','h1','Asset 4')]
[PASS] backup == restored byte-equal
[PASS] missing source DB => STOP (differs from normal control) rejected: STOP: production DB not found: ...
[PASS] same-length DB corruption keeps identical size
[PASS] same-length DB corruption changes sha256 (names/sizes-blind check misses it)
[PASS] byte-equality gate rejects same-length DB corruption
[value] integrity_check on same-length corrupted DB = ok
[PASS] same-length evidence corruption keeps name+size fingerprint identical ('h1/ab/photo.bin', 19)
[PASS] same-length evidence corruption changes content hash (names/sizes fingerprint misses it)
[summary] checks=22 fails=0

G1 migrations + readers (docs/worklogs/SG-182_migrations_run_2026-10-13.log):
[PASS] revision graph has exactly one head heads=['20260924_sg114_relation'] revisions=11
[PASS] alembic history rc=0
[PASS] alembic heads agrees with source-derived head 20260924_sg114_relation (head)
[PASS] fresh upgrade to head rc=0
[PASS] upgrade executed real revision steps (alembic logs on stderr)
[PASS] second upgrade head is a no-op (already at head; both streams checked)
[PASS] settings override effective: ini-path DB not created ini_path_db_exists=False
[PASS] upgraded DB integrity_check ok
[PASS] DB alembic_version == expected head [('20260924_sg114_relation',)]
[PASS] settings.database_url == scratch override sqlite:////tmp/opencode/sg182-mig-.../fresh.db
[PASS] all 20 metadata tables/columns present after upgrade
[PASS] app.seed runbook step rc=0
[PASS] real app health GET on migrated DB {"status":"ok","db":"ok","storage":"ok"}
[PASS] real reader /v1/households returns seeded household (no rows exposed here) status=200 count=1
[PASS] real reader /v1/assets on empty migrated catalog (cursor envelope) status=200 body={"items":[],"next_cursor":null}
[PASS] real reader /v1/settings/ai on migrated DB status=200
[summary] checks=16 fails=0

Served identity (docs/worklogs/SG-182_served_identity_2026-10-13.log):
[PASS] GET / served status=200 bytes=944
[value] index.html sha256=2f035becd05b63e226af82e2e8fe60c8f3b5effb9f37e49dd95a2265c4da0d55
[value] served asset /assets/index-CYyuxefG.js status=200 bytes=322255 sha256=1b4680a0eddadff3c95a64b6bc00d744764d127a72cd5690ebea948b7664a29d
[value] served asset /assets/index-DO0gjGV6.css status=200 bytes=3911 sha256=37b25dbdd4b0ecfdedb8255bc7f8af286726334e95a1a3a9e85b9ba381b3d57c
[PASS] GET /v1/settings/ai effective deployment AI config status=200
[value] effective AI settings: {"allowed_model_ids":["deepseek-v4-flash-vision-exp"],"consent":true,"model_id":"deepseek-v4-flash-vision-exp","monthly_cap":null,"per_job_cap":null,"prompt_category":"food","provider_id":"opencode-go"}
[value] production DB file readable: True
[value] served schema: alembic_version=[('20260924_sg114_relation',)] table_count=28
[summary] checks=7 fails=0

Focused mapped tests (docs/worklogs/SG-182_focused_tests_2026-10-13.log):
"...... [100%]  6 passed in 0.10s" (rc=0) — tests/test_backup_drill.py + tests/test_runbook_commands.py

Build/type gates (existing tooling, no installs):
frontend: ./node_modules/.bin/tsc rc=0 (TypeScript 5.9.3); ./node_modules/.bin/vite build rc=0 (built in 3.04s, scratch outDir)
backend: venv/bin/python -m ruff check --no-cache app tests rc=0 "All checks passed!" (ruff 0.16.5)
backend: venv/bin/python -m mypy app rc=1 "Found 41 errors in 9 files (checked 92 source files)" (mypy 2.3.1) — committed log SG-182_mypy_2026-10-13.log

INTENT: none (read-only audit; no behaviour-changing item, no product diff). TWINS: not applicable to fixes; the
guard twin search is reported in (a)2 (class count 1, the audited helper itself).

UNCLEAR
FIRST READ: packet premises checked: guard condition/line range accurate (115-125); alembic line number wrong
(line 3, not 23); requirements.txt/.github absent, requirements.lock present, confirmed; compose topology
reconciled (single production service; frontend dev-profile only); backend image serves UI + pinned digest +
locked requirements, confirmed; .github absent and `git log --all -- .github` empty — remote-run provenance left
UNVERIFIED, not inferred absent. SG-181 outcomes (receipt b0dd968, 94 no flag, F-1 defect, rollback correction)
were read from the audit before reusing. Prepared draft re-reviewed: its scope map and exclusions held; this
slice adds F-SG182-1/2/3/6 and the production-schema-at-head observation.
DURING EXECUTION: the guard defect is real but bounded to explicit `--work-dir` inside the storage root (documented
runbook form uses mkdtemp -> disjoint); no production path was pointed at, no recursive copy executed. Alembic logs
on stderr, so the first "executed real revision steps" check and the rerun no-op check were corrected before the
green run (failed log preserved, no vacuous stream check kept). Production schema/`served bundle` identification is
read-only; Docker was never attempted.
REMAINING (exact destinations): Architect audit/rating of SG-182 -> canonical register merge (G3 consolidation is
the input, not the register); owner decisions R1 SG-175 safety hold, F-SG181-1 repair grant, F-SG181-3/4/6/7/8 +
F-SG180-8/11 semantics, per-field/concurrency scope, R8 design grant, R5 production release -> register/backlog;
F-SG182-1 minimal operator fix (guard direction + message) -> R7 proposal in consolidation, needs its own grant,
no operator edit in this audit; F-SG182-6 mypy-red gate -> canonical register quality-gate item, introducing
commit unknown; container/image + remote-CI + production-volume + live-quality UNVERIFIED -> consolidated plan
limits, no widening of grants; STANDING CLOSE DEPLOY CONFLICT: SG-175 held code cannot ship under the standing
close-out deploy, no deploy/restart performed, no waiver invented — Architect alone records CLOSE_BLOCKED if it
cannot discharge the obligation. This slice is not END/close.
