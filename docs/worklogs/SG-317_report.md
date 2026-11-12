# SG-317 report — deploy rider: serve SG-307 on release-sg317

Slice: SG-317 | Model: opencode-go/claude-haiku-5-5 (session identity; no model or effort field in the process arguments, so effort is not stated) | Working directory: /home/andrei/StorageGenie | Remote: origin git@github.com:Andovol/StorageGenie.git | BASE ref: origin/automation | Resolved commit: b9b5f3eeee5597c37076b85b7ab443e7db4f144b | WORK_HEAD: b9b5f3eeee5597c37076b85b7ab443e7db4f144b (the product state deployed; the report commit follows it)
Own contract version line (as received): none received.

## Outcome

State reached: **S1, no rollback.** The new container (`e61b3784941f`) became healthy in 10 s with restart count 0. No product byte changed; the only runtime change is the `static/` bundle. The release-sg317 tag was created on the new image.

## Phase timing (from `date +%s` stamps)

| Phase | Start | End | Seconds |
|---|---|---|---|
| G0 socket, docker version, pre-state, git, health | 1794511734 | 1794511756 | 22 |
| Census before + one backend build (cache-satisfied) | 1794511773 | 1794511776 | 3 |
| Hash new tree and runtime diff | 1794511785 | 1794511787 | 2 |
| One recreate | 1794511795 | 1794511797 | 2 |
| Recreate to healthy | 1794511797 | 1794511807 | 10 (12 from recreate start) |
| Tag, G2 served checks, G3 health/routes/API, startup log, census after | 1794511835 | 1794511837 | 2 |

Engine elapsed, first to last stamp: 123 s (1794511734 to 1794511857). The expectation was about 200 s, so the run finished well under it. Budget ceiling 2100 s; publish point 1200 s; no hang bound was reached.

## G0 — socket and pre-state

- Literal socket block run: `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-317/docker.sock`; `docker version` printed a Server section (Engine 29.9.2), rc 0.
- Health before: `{"status":"ok","db":"ok","storage":"ok"}`.
- Pre-state matched the hypotheses: container `5cd1079878a8353356c434636f24ea769fc390b6e65bb09be28afc6f45614945`, image `sha256:91b0969e9e0bf42dd0f10b666109ddbfb5706e3fc9b7bd82945446c6e1999655`, restart count 0, healthy, Cmd `uvicorn app.server:app --host 0.0.0.0 --port 8000`.
- `storagegenie-backend:release-sg314` resolves to `sha256:91b0969e...`. `docker compose -f docker-compose.yml -f output/SG-317-scratch/rollback.override.yml config --images` (with `--images`) printed `storagegenie-backend:release-sg314` for backend.
- Alembic head before: `20261102_sg279_candidate_state`.
- Git: origin/automation fetched; HEAD = origin/automation = b9b5f3e; worktree clean. 614f61b is an ancestor of HEAD.
- Derived sets (from `614f61b..HEAD`): backend (excluding alembic) EMPTY; alembic EMPTY; frontend package.json and lock EMPTY. Expectation "empty" matched. Changed files in the range were frontend, docs and STATE only.

## G1 — one build, one recreate

- `docker compose build backend`: rc 0. Frontend layers `COPY frontend/` and `npm run build` were CACHED. BuildKit keys a COPY layer on file content, so a cache hit means the frontend context matches the current worktree; the served strings in G2 confirm the bundle content. The worktree equals HEAD (clean).
- `storagegenie-backend:latest` before: `sha256:91b0969e...` (release-sg314). After build: `sha256:1bdf6799b90cd6797bf01333b4e75c0179cc48a4cb7b750fe84547878faadc5f`.
- Runtime diff (evidence: `docs/worklogs/SG-317_runtime-diff.txt`): 4069 files in each image; only `static/` differs. Changed: `static/index.html`; added and removed one JS bundle and one CSS bundle each. Instrument Sans `.woff2` files byte-identical (sizes 11144 and 30092). No path outside `static/` changed.
- Alembic head unchanged; no migration command run.
- `docker compose up -d --no-deps --force-recreate backend`: rc 0.

## Identities before and after

| | Before | After |
|---|---|---|
| Container | `5cd1079878a8353356c434636f24ea769fc390b6e65bb09be28afc6f45614945` | `e61b3784941f1088bc508e4aa2a027b4702e40a4ea01d14cbf5b930205ef923d` |
| Image | `sha256:91b0969e9e0bf42dd0f10b666109ddbfb5706e3fc9b7bd82945446c6e1999655` | `sha256:1bdf6799b90cd6797bf01333b4e75c0179cc48a4cb7b750fe84547878faadc5f` |
| Restart count | 0 | 0 |
| Health | healthy | healthy (10 s) |
| `:latest` | 91b0969e | 1bdf6799 (moved by the build) |
| `:release-sg314` | 91b0969e | 91b0969e (unchanged) |
| `:release-sg317` | absent | created on 1bdf6799 |

No tag was removed or moved; release-sg310, sg309, sg303, sg299, sg296, sg295, recovery-sg270 unchanged. No `docker rmi`, prune, or `docker compose config` without `--images`. The `storagegenie-backend:prover` tag (created 18:58 today) was not touched.

## G2 — the new behaviour is in the served artifact

Counts taken from each image's own `/app/static/assets` (served files; `release-sg314` as the "before", `release-sg317` as the "after"):

| String | sg314 (before) | sg317 (after) |
|---|---|---|
| JS `Photo only` | 0 | 1 |
| JS `Cut-out ready` | 0 | 1 |
| JS `No cut-out yet.` | 0 | 1 |
| JS `In a scene` | 0 | 1 |
| JS `Food & beverages` | 0 | 1 |
| JS `Source Only` | 1 | 0 |
| JS `Isolated Cutout` | 1 | 0 |
| JS `Bounding-box overlay omitted` | 1 | 0 |
| CSS `.sg-paper-control` | 0 | 1 |

Quoted from the served CSS (after): `@media (max-width: 480px){.sg-import-label,.sg-header-count{display:none}.sg-header{flex-wrap:nowrap!important;gap:8px!important;padding:10px 12...` (the media rule hides `.sg-import-label` at max-width 480px).

Font: `GET /assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2` http 200, `Content-Type: application/octet-stream`, 30092 bytes. `GET /assets/instrument-sans-latin-ext-wght-normal-B5bTHO_g.woff2` http 200, `application/octet-stream`, 11144 bytes. The CSS names both files under `/assets/`.

**Honest limit:** no screen was viewed in a browser in this run. The screens were seen in SG-316 on a scratch build of the same commit (`docs/worklogs/SG-316_audit.md`, `docs/worklogs/SG-307_shots/`).

## G3 — the app answers, nothing moved

- `/v1/health` six times: each `{"status":"ok","db":"ok","storage":"ok"}`, http 200.
- Routes: `/` 200, `/pantry` 200, `/expiry` 200, `/inbox` 200, `/planning` 200.
- `GET /v1/assets?household_id=<id>&category=food_beverages&limit=5`: http 200, first page 1 item. The household id was read from the database into a shell variable and not printed.
- `GET /v1/plugins/expiry-tracker/status?household_id=<id>&category=food_beverages`: http 200.
- Startup log, named lines only (`grep -E 'Traceback|Application startup complete|Daily reminder pass'` on `docker logs --since 10m`):
  - `INFO:     Application startup complete.`
  - `INFO:     app.services.reminders.daily - Daily reminder pass completed as_of=2026-11-12 households_visited=1 reminders_created=0 errors=0`
  - No `Traceback` line.
- Census (read-only, `mode=ro` on the live database; SELECT counts only). Before and after are identical for all 29 tables and for `alembic_version` (`20261102_sg279_candidate_state`). Evidence: `docs/worklogs/SG-317_census-before.txt`, `docs/worklogs/SG-317_census-after.txt`; `diff` empty, rc 0. `reminder` stayed at 4, consistent with the reminder pass creating 0.

## Constraints, one line each

- A1 socket-first: literal block run, `docker version` Server section printed; pre-state quoted; rollback override names `release-sg314`; no rights probe on any real object.
- A2 one build, one recreate, rc 0 each; no migration (head unchanged, alembic diff empty); ids before and after quoted.
- A3 runtime diff equals the derived set (derived: backend empty; expectation: empty, matched). JS and CSS changed, `.woff2` byte-identical with sizes and hashes; served tree = the build's tree; worktree = HEAD (clean).
- A4 G2 strings quoted from the served artifact; honest-limit sentence stated.
- A5 health 200 x6, routes 200, census compared (identical), startup log clean.
- A6 `release-sg317` created on the new image (branch: `automation`, the work branch; the tag is a local image tag, not a git tag). No tag removed or moved. State reached: S1, no rollback.
- A7 no owner name, id or field value printed; no key or `.env` read or printed; no provider call; no browser; no database write; scratch `output/SG-317-scratch/` removed by exact path (shown in the commit step).
- A8 `PB-3` vacuity: checked for an extra file in the runtime diff (none), an unchanged JS hash (changed), a missing string (present), a moved count (none), a route not 200 (all 200), a restart loop (restarts 0), a traceback (none).
- A9 HEAD vs origin/automation: quoted in the publish step.
- A10 last line of this report: `Verification: PASS`.

Verification: PASS
