SG-280 model=opencode-go/muse-spark-1.3-contributor effort=xhigh wdir=/home/andrei/StorageGenie remote=git@github.com:Andovol/StorageGenie.git BASE=origin/automation BASE_COMMIT=b39629e294d8ddb50b89a3ae8b61d674dd013257 WORK_HEAD=b39629e294d8ddb50b89a3ae8b61d674dd013257
Provenance: model and effort from the dispatch task text (AGENTS.md policy: Muse 1.3 Contributor on xhigh). BASE_COMMIT is `git rev-parse origin/automation` at slice start; HEAD was identical (clean). WORK_HEAD is the pre-report tip; this slice changes no product byte, so BASE==HEAD==WORK_HEAD pre-report. Report commit hash never appears in its own report per CO-55b; the publish notes carry the report commit.

Contract echo: **Contract version: 0.56.0** from /home/andrei/storagegenie-contract/CODER.md line 3. AGENTS.md records 0.56.0. Published contract-v0.56.0 matches by version string. No finding.

Authority: owner D16 ("D16 - ok.") and D20 ("D20 - ok.") per docs/decisions/2026-10-30-session-approvals.md. Design SG-277, SG-278, SG-282, SG-283; audit docs/worklogs/SG-279_audit.md I2 and I3.

## Outcome

STOPPED in S0 before G4. The app was never stopped, never migrated, never restarted. Live database, live containers, and live schema are exactly as found. No retained backup was taken because G4 never started (nothing to retain). All rehearsal copies held only under output/SG-280-scratch/ and are removed by exact path before the report commit.

Reason: the recovery image is gone. The running container's image id `sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22` (recorded from `docker inspect storagegenie-backend-1` in G0, matching the SG-270 release) no longer exists as an image object: `docker run --rm <old-id> true` returns `RC=125 No such image`, and `docker create` the same. S1 ("start the old image by its immutable id") is therefore unexecutable, and G3 step 4 (old image reads the restored file) fails the same way. Per PG-IC-03 and the packet's STOP rules, any result other than expected stops the work in S0. A partial slice with a receipt is a success.

My inference (UNVERIFIED): the G0 `docker tag <old-id> scratch-tag` + `docker rmi scratch-tag` combined with the G1 `docker compose build` retagging `:latest` left the old id untagged, and the object was then garbage-collected despite the running container. The G1 build itself was cache-satisfied (all steps CACHED, new image Created 2026-11-02T16:27:38Z, before this session's 18:03Z start), so the new image predates this slice.

## Time, budget, hang bounds

- Start 2026-11-02T18:03:32Z (epoch 1793642612). G3 rehearsal done ~18:11Z; elapsed at STOP decision ~461 s. Report/publish adds minutes; total stays far under RUN_BUDGET_S=2100.
- Expected ≈800 s (UNVERIFIED estimate from packet). Actual engine work ≈460 s to STOP + report time. Under budget.
- Phases over 60 s: G1 `docker compose build backend` (one invocation, within its 900 s bound; cache-satisfied, fast) and G3 rehearsal script (three docker one-shots plus host sqlite, within per-one-shot 300 s bounds). No phase hit its hang bound. `docker version` well under 120 s; health/routes under 120 s; ordinary commands under 120 s. No interactive command.
- Time guard: G4 was never started; elapsed at decision (~461 s) was under the 1200 s do-not-start-G4 guard in any case. The guard did not fire; the missing recovery image did.

## State reached and each constraint

- Recovery state: S0. Before the backend was stopped: stop. The app was never touched. S1/S2/S3 never entered. S4 never entered (no recovery step attempted on live). Denials: none from the lane (no PB-2 denial); the only refusal is the daemon's `No such image` for the old id, which is a finding, not a lane denial, and it correctly routes to STOP, never to another route.
- S0 held throughout: backend `d972bc75` continuously `Up (healthy)`; health 200 before, during (rehearsal), and after; census identical.
- Scope ceiling kept: written only `docs/worklogs/SG-280*` in git; scratch only under `output/SG-280-scratch/`; no `data/db/SG-280-backup-*` was created (G4 never started); the live `candidate` table untouched; no product/config/schema/migration/dependency/test byte; no other service touched; no data repair; stored photos/files untouched (no real storage mount in any scratch container); authorised runtimes only (the docker commands named in the packet plus the rehearsal script).
- Restart: zero stops, zero starts of the backend (one stop/start was authorised for G4 only; it never happened).
- Provider: none. No key read or printed, no `.env` opened, no spend. Scratch containers got no `env_file`.
- Sensitive surface: live app database touched read-only only (ro mounts, `?mode=ro`, backup API source). This packet is the written plan the owner approved (D16/D20); anything else would have stopped the work.

## G0 — socket, pre-state, rights (all S0, changing nothing live)

- `DOCKER_CONFIG=output/SG-280-scratch/docker-config`, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-280/docker.sock`; `docker version` shows Client 29.9.2 plus a Server section (Engine 29.9.2, containerd v2.4.2, runc 1.5.2). Quoted in full in the shell record; Server present.
- Health quoted: `{"status":"ok","db":"ok","storage":"ok"}` (start; six more identical in G5 checks).
- Pre-state hypotheses from docs/releases/2026-11-02-sg270.md all hold: container `d972bc752fa0` (`d972bc75`), image `sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22` (`96a66241`), head `20261023_sg233_reminder`, 29 tables, `asset` 7, `candidate` 10. Full old image id recorded as the recovery image. `docker compose ps` shows only `storagegenie-backend-1` (`127.0.0.1:8003->8000`, healthy); no unaccounted running image beyond the one container.
- `git check-ignore -v data/db/SG-280-backup-probe.db` reads `.gitignore:19:data/db/*.db data/db/SG-280-backup-probe.db` (PG-SC-10). `output/` is not in `.gitignore` (grep `^output` empty, as expected).
- Rights proven only on throwaway objects (PG-PR-01): scratch `busybox` container with bind mount under the scratch path and label `sg280-scratch` ran, was stopped by name, removed by name; `docker tag <old-id> sg280-scratch-probe-tag` succeeded (showing `96a662414c23`) and `docker rmi` removed that tag. Never probed by stopping/restarting anything of the app's. `docker compose stop` on live was never attempted (accepted as unprovable in advance).
- Deviation disclosed: `--user 1000:1000` (own uid/gid) cannot write to the scratch bind mount under this rootless daemon (`touch: Permission denied`; `sqlite3 OperationalError: unable to open database file`; empty dir). Default (root-inside, host-owned 1000:1000 files) writes fine and host `rm` removes it (`host-rm-ok`). All scratch containers that needed writes ran with the default user and label `sg280-scratch`; every file they wrote was removed by exact host path. Intent met (removable scratch), letter deviated for writes; the failing `--user` attempts are in the shell record.

## G1 — build the new image, no recreate

- One `docker compose build backend`, RC=0. Running container untouched (`d972bc75`, still `Up (healthy)` on the old digest afterwards).
- New image: `storagegenie-backend:latest` = `sha256:e3e74a6151305531acd4994fa1ce26c41469758b87b2caee3de8a46fd7c2ed97` (manifest list), image config `sha256:bd046bffa67f8ddf0e92fbf88ce2ffe91ac5f36db6cf296f51d89efb7bb98387` (`:prover` tag, same Created 2026-11-02T16:27:38Z — predates this slice; the build was cache-satisfied). New id differs from old `96a66241` as required.
- Runtime diff over the served Python tree via `docker export` of the running (old) container vs `docker create`+`export` of the new image: `app/app/` changed exactly `app/app/services/candidates.py`; `app/alembic/` adds exactly `app/alembic/versions/20261102_sg279_candidate_state.py`. No other served-tree difference. Static identical: 3 files, `app/static/assets/index-C07VbG0m.css` and `index-FB7x-XIy.js` byte-identical (hash prefixes `c3b58cda`, `8743733b` match both sides). JS/CSS byte-identical as required.
- Disclosed, not counted against the served tree: the image also carries two new non-served test files under `app/tests/` (`test_sg279_candidate_state.py`, `test_sg279_rehearsal.py`). They are outside the served tree (`app/app/`, `app/alembic/`) and expected from SG-279's scope; the packet's "exactly" is read as the served tree, and the extras are named here rather than hidden.

## G2 — live inventory, read-only

- Live opened read-only only (`file:...?mode=ro`): `journal_mode=wal`; `-wal` (0 B) and `-shm` (32768 B) present beside `storagegenie.db` (765952 B); revision `20261023_sg233_reminder`.
- `sqlite_master`: 95 rows recorded in full (type, name, tbl_name, sql); 29 tables listed by name (alembic_version, assertion, asset, asset_evidence, asset_fts, asset_fts_config, asset_fts_data, asset_fts_docsize, asset_fts_idx, asset_location, asset_relation, audit_event, candidate, enrich_snapshot, evidence, guardrail_event, household, idempotency_key, job, job_step, location, observation, planning_suggestion, provider_call, reminder, review_task, saved_search, source_attribution, user). Every table's count recorded: `asset` 7, `candidate` 10, `reminder` 4, `provider_call` 39, plus the full 29-line census (in the shell record; identical again in G5).
- Reference database built in scratch with the new image and scratch `DATABASE_URL` (`alembic upgrade 20261023_sg233_reminder`, RC=0, 12 migrations from `0201cf10c56c` to head).
- Whole-`sqlite_master` comparison with whitespace normalised: live 95 rows vs reference 95 rows, diff count 0. Live `candidate` text equals reference text, which equals the expected `SG279_CANDIDATE_SQL_BEFORE` (docs/worklogs/SG-279_rehearsal.log:47-60): five-state `ck_candidate_state`, FK order job-then-household. No object difference, so no S0 STOP here; G2 passes.

## G3 — rehearse on copies while the app keeps running (script + log)

Script `docs/worklogs/SG-280_rehearse.py` (contains no data) and output `docs/worklogs/SG-280_rehearsal.log`. The app stayed up and serving throughout (health 200 around the rehearsal). All copies under `output/SG-280-scratch/`; counts and hashes only.

1. Upgrade on real data: PASS. Copy via SQLite backup API in a one-shot container with the live folder mounted read-only (`src.backup(dst)`, `backup-ok`; read-only mount with `journal_mode=wal` established first: `ro-mount-ok 10`). `live-copy sha256=3aa4e1f5…`, 29 tables, candidate 10, rowhash `81af8de2…`. Fresh `step1.db` upgraded to head with the new image (RC=0, only `20261023_sg233_reminder -> 20261102_sg279_candidate_state`). Post: rev new, `integrity_check=ok`, `foreign_key_check` 0 violations, all table counts equal, candidate row hash equal, master changed exactly `('table','candidate')`. Rolled-back transaction: `split` accepted, `merged` accepted, bogus refused naming `ck_candidate_state`.
2. Interrupted migration at the worst point: PASS (damage landed). One-shot wrapper kills with `os._exit(99)` keyed on the rename statement text through a `before_cursor_execute` listener (args[2] is the statement under SQLAlchemy 2.x; two earlier script revisions failed honestly — wrong 4-arg signature, then args[1] instead of args[2] — and are superseded by the passing run in the final log). Exit `RC=99`, `KILLPOINT rename seen; exiting`; damaged file shows `_alembic_tmp_candidate` present, revision still `20261023_sg233_reminder`. (Candidate still listed present; the OR condition `candidate missing OR tmp present` holds via tmp present, revision old, non-zero exit.) Had damage not landed the rehearsal would prove nothing and stop — it did land.
3. Restore by the exact S2 procedure: PASS. Damaged file replaced by the backup copy with `-wal`/`-shm` beside it removed. Proof: sha256 equal to backup, `integrity_check=ok`, `foreign_key_check` 0, revision old, all table counts equal to pre-damage.
4. Old image reads the restored file: NOT executable — STOP in S0. `docker create <old-id>` returns `Error response from daemon: No such image: sha256:96a66241…` (RC=1). Same for `docker run`. The recovery image recorded in G0 cannot be started by its immutable id. Nothing was stopped, replaced, or restarted; the app keeps running on the live database, which was never touched. This is the slice's STOP.
5. The check can fail (PG-EV-01): PASS. A deliberately truncated copy (`trunc.db`, half bytes) is refused: hash unequal plus `DatabaseError` on read. A refused restore is S4 — left stopped, to the owner; demonstrated here on a scratch copy only.

## G4 — not started (by the STOP)

Order held by not starting: no `docker compose stop backend`, no live backup file, no live `alembic upgrade head`, no `up -d --force-recreate`. Live `sqlite_master` therefore still differs from nothing; candidate still five-state; counts still G2; no `_alembic_tmp_candidate` live. State at STOP: S0. Time guard obeyed independently (elapsed ~461 s < 1200 s).

## G5 — the app answers (as an S0 census, not a post-migration gate)

- `/v1/health` six times, each quoted `{"status":"ok","db":"ok","storage":"ok"}`.
- Shell routes `/`, `/expiry`, `/inbox`, `/planning` each 200.
- Startup log: zero `traceback`/`configuration error`; daily pass quoted: `app.services.reminders.daily - Daily reminder pass completed as_of=2026-11-02 households_visited=1 reminders_created=0 errors=0`.
- Census after equals G2 exactly (29 lines; `reminder` 4, unchanged, as the daily line's `reminders_created=0` accounts for; no other table moved). No split or merge was exercised live: the first real use is the owner's.
- Old container/image quoted: container `d972bc752fa0`, image `sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22`, `Cmd=[uvicorn app.server:app --host 0.0.0.0 --port 8000]`, restarts 0, healthy. New image quoted in G1. Downtime: zero (no stop); stop-to-healthy not applicable.

## Acceptance criteria

- A1 — socket and rights proven before any live step, on throwaway objects only: yes (Server section; stop/remove/tag/rmi on `sg280-scratch` label; the `--user` deviation disclosed). No live stop was ever needed for proof.
- A2 — G2 comparison shown, no STOP: yes, 95 vs 95, diff 0, candidate text equals the rehearsal log's BEFORE text verbatim in the shell record.
- A3 — G3's five steps in the log: damage landed (RC=99, tmp present, rev old), restore matched by hash, old image attempted and missing (honest STOP, not a pass), truncated copy refused. Step 4 is a documented failure, which is the slice's STOP reason.
- A4 — G4's order held by never starting; state S0 named at each step; zero stops, zero migrations, zero starts; no live backup path or hash because none was taken; restore proof shown only on scratch (step 3).
- A5 — no live migration ran, so the "only candidate changed" criterion is met vacuously on live (nothing changed); on the scratch upgrade (step 1) only `candidate` changed by the accepted set (quoting/FK-order non-semantics as the rehearsal showed), counts and row hash equal.
- A6 — health and routes 200; old container/image ids quoted; census compared (identical). Post-migration gate not applicable after a STOP; reported as S0 census.
- A7 — no name, id, or field value of the owner's in any log or report (counts, hashes, schema text, revisions only); no key or `.env` read; no provider; no browser; scratch removed by exact path (removal shown before the report commit).
- A8 — PB-3 vacuity: a failure would look like an object difference (checked: diff 0), damage that did not land (checked: landed, and two earlier script bugs honestly failed first), a hash mismatch (checked: equal on restore, unequal on truncated), a truncated copy accepted (checked: refused), a count that moved (checked: identical), a restart loop (checked: restarts 0, healthy), a traceback (checked: zero). Named as checked.
- A9 — `HEAD` equals `origin/automation` after push, both hashes quoted in the final message (see publish block; both `b39629e…` pre-report, plus the report commit hash after).
- A10 — last line below.

## What the owner must decide

1. Re-provision the recovery image before any future stop: the running `96a66241` object is gone from the daemon. Options belong to the owner (e.g. rebuild and re-tag from the release commit, or accept the new image as the new baseline after a fresh review) — no restore, retry, or restart was attempted, per S3/S4.
2. Whether to re-dispatch the live migration once S1 is possible again; the scratch rehearsal (steps 1–3, 5) already proves the migration, restore, and refusal paths on real data.

Next steps: owner approves a new rider with a present recovery image; that rider re-runs G0–G5 on the live database; no code change is needed for the migration itself.

Verification: STOPPED in S0 — recovery image sha256:96a66241… not present (No such image), S1 unexecutable, app untouched.
