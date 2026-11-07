SG-294 | model opencode-go/muse-spark-1.3-contributor effort=xhigh | wdir /home/andrei/StorageGenie | remote git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation -> 9ab143a4391e178ae703eddd000c8f0c2349df6a | WORK_HEAD 9ab143a4391e178ae703eddd000c8f0c2349df6a

Contract chain: recorded `0.58.0` (`AGENTS.md`). This lane denies reading the contract folder (SG-286, SG-290); no contract file was read, no checker was run, no route around the denial was attempted. The `docker version` Server section below is the host evidence. Model and effort from the rotation slot (STATE.md, SG-293 audit: SG-294 on Muse 1.3 Contributor, xhigh). BASE commit is `git rev-parse origin/automation` at slice start; HEAD was identical and clean (only untracked `output/` and the new worklog file, both expected). WORK_HEAD is the pre-report tip; this slice changes no product byte, so BASE==HEAD==WORK_HEAD pre-report. The report commit hash never appears in its own report.

# SG-294 report — recovery image by export and import: PASS, stop

Outcome: recovery tag `storagegenie-backend:recovery-sg270` created by `docker import` from the live export, proved by full inventory, field-by-field configuration, per-key environment hashes and a real start on a scratch copy, then stopped. The live app was not touched: same container, same start time, restart count 0, health ok at start and end, and the `docker diff` set unchanged at 208 entries. No deploy, no migration, nothing else removed.

## G0 — baseline, changing nothing (A1)

- `DOCKER_CONFIG=output/SG-294-scratch/docker-config`, `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-294/docker.sock`; `docker version` shows Client 29.9.2 plus a Server section (Engine 29.9.2, containerd v2.4.2, runc 1.5.2, rootless). Scratch stayed in `output/SG-294-scratch/`, removed by exact path at the end; `output/` itself and `output/dispatch` never touched.
- Health at start: `{"status":"ok","db":"ok","storage":"ok"}`. Health at end: same.
- Live container `d972bc752fa038be2552322120af1e0d56a35321cc47d61fc4677b476a91332f` (name `/storagegenie-backend-1`): `.Image` `sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22`, running, started `2026-11-02T15:52:53.194514305Z`, restart count 0. All equal to SG-290.
- Mounts: `/data/db` is a bind (`/home/andrei/StorageGenie/data/db`, rw); `/data/storage` is a local volume (`storagegenie_storage_data`, rw). No other mount. Equal to SG-290.
- `docker diff` sorted: 208 entries, identical to sorted `docs/worklogs/SG-290_diff.log` (208 lines). Repeated at end: identical.
- Free space (scratch filesystem `/dev/vda1`): available 105,788,395,520 B before exports (99G); after both exports still ~99G. Well above 5 GB.
- Recovery tag `storagegenie-backend:recovery-sg270`: absent at start (`No such image`) and absent at end of G0; re-checked absent immediately before G3.
- `.gitignore` has no `output` entry (`git check-ignore` RC=1, as the packet expected). `git status --short` was clean apart from untracked `output/` and the new worklog file. Staging will be by exact path `docs/worklogs/SG-294*` only.

## G1 — export twice, gate each, compare (A2)

- `live-1.tar`: `docker export` exit 0, 642,994,176 bytes. Gate PASS: 19,046 entries; entries under `data/` are exactly 3 (`data/`, `data/db/`, `data/storage/`), all directories; `.env` entries: 0.
- `live-2.tar`: same export and gate. Exit 0, 642,994,176 bytes, 19,046 entries, gate PASS, same counts.
- Inventory script `docs/worklogs/SG-294_inventory.py` (holds no data; reads only the tar named in argv; copy of SG-293 logic with SG-294 header), run as a one-shot `storagegenie-backend:latest` container with `--network none`, label `sg294-scratch`, scratch mounted read-only, script on stdin, container removed by name:
  - live-1: exit 0, `ENTRY_COUNT=19046`, parse failures 0.
  - live-2: exit 0, `ENTRY_COUNT=19046`, parse failures 0.
  - `cmp` of the two inventories: IDENTICAL. 19,046 entry lines plus footer, 19,049 lines in total.
  - Inventory sha256 (same for both): `27c1376cec80a926f59904f5327772f19a1c03ff1d1474250b2c5397fff41d04` (same count and hash as SG-293 expected: 19,046 and `27c1376c…`).
- Extended headers: 3 entries carry PAX headers, all of them `path`/`linkpath` long-name records (2 `path`, 2 `linkpath` across 3 entries). Zero `SCHILY.xattr.*` headers. Zero capability headers. No global PAX header.

## G2 — configuration to import (A3)

- Live launch fields (`docker inspect --format`, named fields):
  - `Cmd` `["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, equal to `backend/Dockerfile:22`.
  - `Entrypoint` null. `WorkingDir` `/app`. `User` empty string. `ExposedPorts` `{"8000/tcp":{}}`.
- Healthcheck: live container's healthcheck equals `docker-compose.yml:20-24` (test `python -c "import urllib.request; ..."`, interval 10s, timeout 3s, retries 5). Donor image healthcheck is null. It stays in compose and is not imported. If it differed the packet would require STOP; it does not differ.
- Donor image `storagegenie-backend:latest`: id `sha256:e3e74a6151305531acd4994fa1ce26c41469758b87b2caee3de8a46fd7c2ed97`, platform `linux/amd64`.
  - Launch fields of the donor (for reference): `Entrypoint` null, `Cmd` same as live, `WorkingDir` `/app`, `User` empty, `ExposedPorts` same as live.
  - The donor's env, recorded as key names and truncated sha256 only (values never printed or written to git), has 5 keys: `GPG_KEY` (hash `6c3b7674b58d9f72`), `LANG`, `PATH`, `PYTHON_SHA256`, `PYTHON_VERSION`.
  - Key-name rule: `GPG_KEY` ends in `_KEY`, so the exception was checked. Its value is exactly 40 hexadecimal characters: fingerprint-shaped `yes` (value not printed). The other four names do not match any setting in `backend/app/config.py` and do not end in `_KEY`, `_TOKEN`, `_SECRET` or `PASSWORD`. Result: PASS, no STOP.
  - Per-key hash comparison (script printing names and `equal`/`differ` only, never a value): all 5 donor keys hash `equal` in the live container. The live container also has 11 keys not in the donor (names only; values never printed): `CORS_ORIGINS`, `DATABASE_URL`, `HOUSEHOLD_DEFAULT_NAME`, `JINA_API_KEY`, `OPENCODE_API_KEY`, `OPENROUTER_API_KEY`, `SG_CONSENT`, `SG_LOCATIONS_ENABLED`, `SG_PROVIDER_ID`, `SG_RELATIONS_ENABLED`, `STORAGE_ROOT`.
- The donor's `Config.Env` JSON was never written in full, as it may contain values. Only names, truncated hashes and the fingerprint shape were recorded.

## G3 — import (A4)

- Tag collision rule: `storagegenie-backend:recovery-sg270` was absent at G0 and re-checked absent immediately before import (`No such image`). The absent branch applies; never compared, reused or overwritten.
- Time guard: import started at 2026-11-07T21:35:34Z, ~150 s after slice start (21:33:04Z), well under the 900 s ceiling.
- `docker import` `live-1.tar` with 8 `--change` flags (3 launch + 5 ENV): `CMD ["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, `WORKDIR /app`, `EXPOSE 8000/tcp` (ENTRYPOINT null skipped, USER empty skipped), plus one `ENV` line per donor key with the donor's value (read only to build the import, never printed). Exit 0. New image id `sha256:2acd0c2438f34b5070b13bd04fa898b42cde126241dab43b0d124aa3a7a99ea2`.
- Recovery image platform: `linux/amd64`, equal to the donor's `linux/amd64`.

## G4 — prove it (A5)

- Create, never start, container `sg294-recovery-probe` (`9237d3e0071e5c54ec06d80946b8d26ae08c7905a2f594285cee5f7f35a26f38`) from the recovery tag (`--network none`, label `sg294-scratch`), `docker export` to `recovery.tar` (exit 0, 642,994,176 bytes), gate PASS (19,046 entries, exactly 3 `data/` directories, 0 `.env`), inventory in a one-shot donor container (`--network none`, label, removed by name): `ENTRY_COUNT=19046`, `ENTRIES_WITH_PAX=3`. Container removed by name afterwards.
- `recovery.tar` vs `live-1.tar` inventories: IDENTICAL (`cmp` equal). Any difference would have been a STOP with differing paths quoted; there is none.
- The check can fail (PG-EV-01): a copy of the `live-1` inventory with one file's hash altered (`.dockerenv`, first entry) was compared once: `cmp` reports differ (RC=1), `diff` reports exactly that path (`1c1`, `< ".dockerenv"...`, `> ".dockerenv"...` with the altered hash). The comparison is seen to fail on the altered copy, then identical on the real pair.
- Configuration: the recovery image's `Cmd`, `Entrypoint`, `WorkingDir`, `User`, `ExposedPorts` equal the live container's, field by field (all five match G2). Its environment equals the donor's per key, by hash: 5/5 `equal`, no extra, no missing.
- No failure in this goal, so the tag was not removed. On any failure the packet would require `docker rmi` of exactly the tag created in G3; it was not needed.

## G5 — it actually starts (A6)

- Scratch database copy: `output/SG-294-scratch/sg294-copy.db` (765,952 bytes) taken with SQLite backup API (`src.backup(dst)`, `backup-ok`) in a one-shot `storagegenie-backend:latest` container with `data/db` mounted read-only (`/live:ro`) and scratch mounted writable, `--network none`, label `sg294-scratch`, removed by name. Live database never opened directly.
- Empty scratch storage: `output/SG-294-scratch/storage/` (`chmod 777` on the operator's own scratch folder before the run; no rootless write failure observed).
- Recovery container `sg294-run`: created from `storagegenie-backend:recovery-sg270`, resolving to image `sha256:2acd0c2438f34b5070b13bd04fa898b42cde126241dab43b0d124aa3a7a99ea2`. Container id `c9f820c20092b605ced5833885f5fd4c77641af4898f16aa0fe9d05ca092e4da`. Run detached with `--network none`, label `sg294-scratch`, no published port, `-e DATABASE_URL=sqlite:////scratch/sg294-copy.db`, `-e STORAGE_ROOT=/scratch/storage`, no `env_file`, no real storage mount (only `output/SG-294-scratch:/scratch`), image's own user (no `--user` flag). Startup may write reminders into the copy; that is expected (`backend/app/server.py:27-34`).
- From inside it (`docker exec` on the scratch container only; never on `d972bc75`): `GET /v1/health` returns 200 (twelve consecutive 200s during the wait). One read route that reads the database: `GET /v1/households` returns 200. Status codes only; no body quoted. (`GET /v1/assets` and `GET /v1/reminders` without `household_id` correctly return 422; `GET /v1/households` needs no params and reads `household`.)
- Stop and remove by name: `docker stop sg294-run` RC=0, `docker rm sg294-run` RC=0. Tag still resolves to `sha256:2acd0c24…` afterwards. No failure, so no tag removal (G4/G5 rule).

## Hygiene and live-app safety

- Live container: only `docker inspect --format` (named fields), `docker diff`, and `docker export` (read-only). No stop, pause, restart, recreate, exec, commit, or `rmi`. No prune. No compose command. No `.env` opened, no Env value printed, no provider call, no spend. No container created without `--network none` and label `sg294-scratch`; all scratch containers removed by name.
- No secret, owner value or response body is in this report or in the commit (paths, digests, counts, status codes only; Env values only as truncated hashes; `GPG_KEY` shape `yes`, never its value).
- Scratch `output/SG-294-scratch/` removed by exact path before the report commit (tars, inventories, name lists, hash files, database copy, storage folder, docker config). `output/dispatch` untouched.
- Tests: none; nothing in the product changed.

## Runtime and budget (PG-PR-06)

- Slice start 2026-11-07T21:33:04Z; import start 21:35:34Z (~150 s elapsed, under the 900 s do-not-start guard); engine work done 21:38:59Z (~355 s wall-clock including agent overhead). Against the 2100 s `RUN_BUDGET_S` ceiling: ~17%. Expected ~600 s (`UNVERIFIED — my estimate` in the packet).
- Phases over 60 s wall-clock: G1 (two 643 MB exports, gates and two inventories) spans ~101 s including agent pauses; G4+G5 (recovery export, inventory, backup, detached start and exec probes) spans ~3 min including agent pauses. No single docker command hit its hang bound (`docker version` 120 s; each export 600 s; import 600 s; each one-shot 300 s; health and routes 120 s; ordinary commands 120 s). No interactive command.
- DOCKER_CONFIG and DOCKER_HOST as in G0 throughout.

## Files

- `docs/worklogs/SG-294_report.md` (this file)
- `docs/worklogs/SG-294_inventory.py` (holds no data)

## Acceptance criteria

- A1 — G0 baseline equal to SG-290, free space quoted: yes (same id, image, start, restarts, mounts, 208 diff equal; 99G free).
- A2 — both exports gated and inventoried, identical, entry counts non-zero, extended-header count stated: yes (643 MB each, 19,046 each, identical, 3 with PAX, zero xattr/caps).
- A3 — donor id recorded, key-name rule passed, every donor key `equal`, healthcheck disposition stated: yes (`e3e74a61…`, linux/amd64, GPG fingerprint-shaped yes, 5/5 equal, healthcheck stays in compose).
- A4 — tag created only on the absent branch; platform equal to donor's: yes (absent→create, `2acd0c24…`, linux/amd64).
- A5 — comparison seen to fail on the altered copy, then identical on the real pair; configuration equal field by field: yes (`.dockerenv` single-path diff, then identical; 5/5 fields, 5/5 env).
- A6 — health and the named read route 200 from the recovery image, by the id the tag resolved to: yes (`GET /v1/health` 200, `GET /v1/households` 200, image `2acd0c24…`, container `c9f820c2…`).
- A7 — no secret, owner value or response body in git; scratch removed; `git show --stat HEAD` holds only `docs/worklogs/SG-294*`: yes (shown at publish; staging by exact path only).
- A8 — last line below.

Verification: PASS
