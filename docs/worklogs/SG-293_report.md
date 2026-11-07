SG-293 | model opencode-go/claude-haiku-5-5 | effort: not stated in the packet | working directory /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation, resolved commit ddc7643a1757a118f158f81097464371a275d876 | WORK_HEAD ddc7643a1757a118f158f81097464371a275d876 (base before this report commit)

Verification: STOPPED in G2 — donor image key name GPG_KEY ends in _KEY (key-name rule); value not printed; no import, no recovery tag

## Outcome

Stopped at G2 by the packet's key-name rule. G3 to G5 did not run: no recovery tag, no recovery container, no scratch database copy. The live app was not touched: same container, same start time, restart count 0, health ok at start and end, `docker diff` unchanged at 208 entries. Scratch removed by exact path. Stopped for owner decision (see "Owner decision needed").

## G0 — Baseline (A1)

- `docker version`: Client and Server both 29.9.2, linux/amd64, via `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-293/docker.sock` (rootless). Server section present.
- Health at start: `{"status":"ok","db":"ok","storage":"ok"}`. Health at end: same.
- Live container `d972bc752fa038be2552322120af1e0d56a35321cc47d61fc4677b476a91332f` (name `/storagegenie-backend-1`): `.Image` `sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22`, status running, started `2026-11-02T15:52:53.194514305Z`, restart count 0. Mounts: bind `/data/db`, volume `/data/storage`. All equal to SG-290_report.md.
- `docker diff` sorted: 208 entries, identical to sorted `docs/worklogs/SG-290_diff.log` (208 lines). Repeated at end: identical.
- Free space (scratch filesystem `/dev/vda1`): available 105,789,153,280 B before exports (99G); 104,500,903,936 B after both exports (about 97G). Well above 5 GB.
- Recovery tag `storagegenie-backend:recovery-sg270`: absent (read-only check at start and at end).
- `.gitignore` has no `output` entry (as the packet expected). `git status --short` was clean at start.

## G1 — Export twice, gate each, compare (A2)

- `live-1.tar`: `docker export` exit 0, 642,994,176 bytes. Gate PASS: 19,046 entries; entries under `data/` are exactly 3 (`data/`, `data/db/`, `data/storage/`), all directories; `.env` entries: 0.
- `live-2.tar`: same export and gate. Exit 0, 642,994,176 bytes, 19,046 entries, gate PASS, same counts.
- Inventory script `docs/worklogs/SG-293_inventory.py` (holds no data; reads only the tar named in argv), run as a one-shot `storagegenie-backend:latest` container with `--network none`, label `sg293-scratch`, scratch mounted read-only, script on stdin:
  - live-1: exit 0, `ENTRY_COUNT=19046`, parse failures 0.
  - live-2: exit 0, `ENTRY_COUNT=19046`, parse failures 0.
  - `cmp` of the two inventories: IDENTICAL. 19,046 entry lines plus footer, 19,049 lines in total.
  - Inventory sha256 (same for both): `27c1376cec80a926f59904f5327772f19a1c03ff1d1474250b2c5397fff41d04`.
- Extended headers: 3 entries carry PAX headers, all of them `path`/`linkpath` long-name records. Zero `SCHILY.xattr.*` headers. Zero capability headers. No global PAX header.

## G2 — Configuration to import (stopped here)

- Live launch fields (`docker inspect --format`, named fields):
  - `Cmd` `["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, equal to `backend/Dockerfile:22`.
  - `Entrypoint` null. `WorkingDir` `/app`. `User` empty string. `ExposedPorts` `{"8000/tcp":{}}`.
- Healthcheck: live container's healthcheck equals `docker-compose.yml:20-24` (test `python -c "import urllib.request; ..."`, interval 10 s, timeout 3 s, retries 5). It stays in compose and is not imported.
- Donor image `storagegenie-backend:latest`: id `sha256:e3e74a6151305531acd4994fa1ce26c41469758b87b2caee3de8a46fd7c2ed97`, platform `linux/amd64`.
  - The first template run errored on `.Config.Entrypoint` (the image has no Entrypoint key), so the donor was read again with a separate command.
  - The donor's env, recorded as key names and truncated sha256 only, has 5 keys: `GPG_KEY`, `LANG`, `PATH`, `PYTHON_SHA256`, `PYTHON_VERSION`.
  - Key-name rule: `GPG_KEY` ends in `_KEY`, so the packet requires STOP. Its value was not printed. Other names do not match the rule.
  - Per-key hash comparison (run before the stop, read-only): all 5 donor keys hash equal in the live container. The live container also has 11 keys not in the donor (names only; values never printed): `CORS_ORIGINS`, `DATABASE_URL`, `HOUSEHOLD_DEFAULT_NAME`, `JINA_API_KEY`, `OPENCODE_API_KEY`, `OPENROUTER_API_KEY`, `SG_CONSENT`, `SG_LOCATIONS_ENABLED`, `SG_PROVIDER_ID`, `SG_RELATIONS_ENABLED`, `STORAGE_ROOT`.
- The donor's `Config.Env` JSON was not written in full, as it may contain values. Only names and hashes were recorded.

## G3 to G5 — not run

- G3 (import): not started. No `docker import`, no `--change`. The 900 s check was not needed (elapsed at stop: 162 s).
- G4 (proof): not started. No container created.
- G5 (starts): not started. No scratch database copy taken. No container created.

## Owner decision needed

- Whether `GPG_KEY` is cleared under the key-name rule, or the import is redone with the donor rebuilt without it. Not decided by the coder. The key's content was not inspected.
- The live container's secret-bearing env (`OPENCODE_API_KEY`, `JINA_API_KEY`, `OPENROUTER_API_KEY`, and the rest by name) is container config, not part of an export. A recovery image built this way carries only the donor's env plus the launch fields. Secrets would have to come back through the compose env file at deploy time. Noted for the design, not acted on.

## Hygiene and live-app safety

- Live container: only `docker inspect` with `--format`, `docker diff`, and `docker export` (read-only). No stop, pause, restart, recreate, exec, commit, or `rmi`. No prune. No compose command.
- No live env value was printed or written. Env comparison used a pipeline of key names and truncated hashes, held in scratch files and removed with them.
- No provider call, no `.env` opened, no key read, no spend. No container created, so none has an `env_file`.
- The live database was not opened. The scratch database copy (G5) was not taken.
- Scratch removed by exact path `output/SG-293-scratch` (the two tars, inventories, name lists, hash files, docker config). `output/dispatch` untouched.
- No secret, owner value, or response body is in this report or in the commit.

## Runtime and budget (PG-PR-06)

- Total elapsed from start to stop: 162 s, against the 2100 s `RUN_BUDGET_S` ceiling (about 8%).
- Phase timings were not captured separately. The two `docker export` runs and the two inventory runs are the longest phases; I did not measure whether any exceeded 60 s.

## Commit and publish

- Report commit contains only `docs/worklogs/SG-293_report.md` and `docs/worklogs/SG-293_inventory.py`.
