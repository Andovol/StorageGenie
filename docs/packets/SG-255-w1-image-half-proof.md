# SG-255 — W1's image half, proven on the repaired lane runtime (no code change)

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.** No database is opened, read or written; the tests use temporary SQLite files.
**Restart: none.** The running container, its image tag, the daemon and the host are untouched.
**Provider: none.** No provider is called, no key is read or printed, **no spend**. Target: **$0**.

**Contract chain:** recorded `0.53.0` (this packet's commit) == published payload `contract-v0.53.0` == the host's contract `0.53.0` (the SG-252 receipt echo) == the echo this report must carry from `/home/andrei/storagegenie-contract/CODER.md` line 3.

## Why this exists

SG-252 landed W1's host half and built the prover image, but every `docker run` returned rc=125 before a container started: `failed to start shim: io.containerd.runc.v2: bootstrap parameters do not match command-line arguments … if you upgraded containerd, you may need to restart the daemon`. The desk restarted the lane's rootless `docker.service` on 2026-10-27 23:50 Bucharest (Launcher issue **#97**, closed): server now 29.9.2, `docker run --rm busybox true` rc 0, the app's container came back by itself (same ID `a831fbd0`, image `e8c73735`), `/v1/health` 200. The same reply says the root-owned `~/.docker` is still to be fixed in the engine arc, so **keep `DOCKER_CONFIG`** until then.

So the four measurements SG-252 could not start — the image proof's PASS, the gate PASS twice, the wrong-image control and the whole-suite/mount trial — run now, with **no code change**. The audit also recorded packet defect I2: the base count is **2 failed / 742 passed** (`docs/worklogs/SG-250_g7_suite.log:114`), not 740.

## G0 — Docker preflight: prove the runtime before any claim

1. `docker version` must show a **Server** section; report the version. The lane's socket is expected at `/run/dispatch-storagegenie-SG-255/docker.sock`; verify it — a difference is a finding, not a stop.
2. `docker run --rm busybox true` must return **rc 0**. If either step fails, **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). Do not restart the daemon or a service, do not use another socket or runtime, do not sudo.
3. Set `DOCKER_CONFIG` to a writable temp directory if the default fails with the `mkdir /home/andrei/.docker: permission denied` error SG-252 hit (`D536`); report which path was used. This is CLI state, not a privileged action.
4. Run `curl -s http://127.0.0.1:8003/v1/health` at start and end and report both bodies. The running app must stay untouched.

## G1 — Guard FAIL on the host (`PG-EV-01`)

On the host, run the two marked tests with `SG_IMAGE_PROOF=1`: both must **fail** (not skip) with the capability messages — zbar unavailable; tesseract and DejaVuSans.ttf unavailable. Commit the log. This is the FAIL half of the guard, captured fresh in this session.

## G2 — Image proof PASS

Build the prover image from the worktree and run the marked set:

```
make backend-test-image
```

Expected: **2 passed, 0 skipped**. A `2 skipped` result is a failed proof. Commit the log. Report the image Id and `Created`, the build wall time and whether it was cache-satisfied or cold, and the image's `tests/test_signals.py` and `app/services/signals.py` sha256 against the worktree's — a cached build is proved fresh by the file hashes, never by the timestamp.

## G3 — Gate PASS twice (`PG-DP-04`)

Run `make backend-test` twice in a row. Both must return **rc 0**: the host suite first (minus the marker), then the image proof. The second run proves the first left no state that breaks the entry point; its build is expected to be cache-satisfied — say whether it was. Commit both logs and quote the host-suite line.

Host-suite expectation from SG-252, no code changed since: **743 passed / 2 deselected / 0 failed**. If a count differs in either direction, report the difference and do not force it (`PG-IC-08`), against the base **2 failed / 742 passed**.

The dispatch shell has no `python` on PATH; SG-252 ran make with `PATH=$PWD/backend/venv/bin:$PATH`. Do the same and report it.

## G4 — Wrong-image control: the gate fails for the RIGHT reason

SG-252's control returned non-zero only because the runtime was broken (rc=125) — that did not prove the gate. Now:

1. `make backend-test-image PROVER_IMAGE=busybox` must return **non-zero**, and the log must show the **busybox image's own failure** — its shell/Python cannot run `python -m pytest` (e.g. `python: not found`, rc 127), **not** a runtime/shim error and **not** a missing image. Quote the failing line verbatim.
2. `make backend-test PROVER_IMAGE=busybox` must return **non-zero after the host suite passed**; quote both the host-suite line and the failing image line.

If either fails with rc=125 or another runtime error, **STOP and report**: a non-zero exit alone is not proof of this control.

## G5 — The whole-suite image trial (one run; it does not gate the slice)

In the built prover image, `--network none`, **no bind mount**:

```
docker run --rm --network none storagegenie-backend:prover python -m pytest -q
```

Record return code, wall duration (box clock), pass/fail/skip counts and the **failure list** if any. Do not change product code to make it pass — its failures are the measurement.

Then the worktree-mount variant:

```
docker run --rm --network none -v "$PWD/backend:/app" -e SG_IMAGE_PROOF=1 storagegenie-backend:prover python -m pytest -q -m requires_native_libs tests/test_signals.py
```

Record rc and whether `/app/tests/test_signals.py` inside the container is the worktree file (sha256). A failure is a finding, not a slice failure.

**The SG-243 decision rule, quoted for the report:** A (the whole suite in the image) holds if the whole suite greens with a duration comparable to the host's measured `61.96 s` and within `RUN_BUDGET_S`, with no extra mounts, network or services; if it reds or needs any of those, A's premise is false and D (host suite + gated two) stands. **State which case the numbers show. Do not move the whole suite this slice.**

## Acceptance criteria

- **A1** — `docker version` shows a Server section, `docker run --rm busybox true` rc 0, health 200 before and after; else the slice stops BLOCKED with the verbatim error (`PB-2`).
- **A2** — guard FAIL captured in a committed log: 2 failed on the host under `SG_IMAGE_PROOF=1`, messages naming zbar and tesseract+font (`PG-EV-09`).
- **A3** — image proof PASS captured in a committed log: **2 passed, 0 skipped**; image Id, `Created`, build time, cache status and both file sha256 pairs stated.
- **A4** — `make backend-test` returns 0 **twice in a row**; both logs committed; host-suite line quoted (expect 743 passed / 2 deselected / 0 failed; base 2 failed / 742 passed).
- **A5** — the wrong-image control returns non-zero from both targets **for the busybox image's own reason**; the failing lines are quoted; a runtime rc=125 is a STOP, not a pass.
- **A6** — the whole-suite trial's rc, duration, counts and failure list are recorded; the mount variant's rc and file identity are recorded; both logs committed.
- **A7** — the A-vs-D verdict is stated from the numbers per the SG-243 rule quoted above.
- **A8** — no product change: `git diff --name-only` against the base shows **only** `docs/worklogs/SG-255*`; zero Makefile, `backend/**`, Dockerfile, compose, lockfile, dependency, migration or schema bytes; zero host package, sudo, service, database, provider or running-container action.
- **A9** — `PB-3` vacuity: say what each check would have looked like if it failed — the proof printing `2 skipped`; the gate returning 0 on the wrong image; the wrong image failing at the runtime instead of in the image; the whole-suite trial red; the image files differing from the worktree. None of these may be the observed result.
- **A10** — the report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Changed product files: none.** Reads of any file, and of the image's own files, are allowed and expected.
- Evidence: `docs/worklogs/SG-255*` only.
- **No** `Makefile`, `backend/**`, `backend/Dockerfile`, `docker-compose.yml`, `backend/requirements.lock`, `backend/alembic/**`, any migration, any dependency, the running container, its image tag, the host's packages, the database, or any provider.
- Docker: through the lane's socket only; the build tags only `storagegenie-backend:prover`; no production tag is overwritten. Never restart the daemon, a service or the app's container.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`): never route around the socket, sudo or a missing package.
- No browser, no frontend build other than the image's own Dockerfile layer, no network in the proof runs.

## Hang bounds

`docker version` / `docker run busybox` **120 s**; `docker build` **900 s**; host suite per run **600 s**; image proof **300 s**; whole-suite trial **900 s**; mount trial **900 s**; ordinary commands **120 s**. Nothing may reach the lane's idle kill; longer work runs in the background and is checked with short calls. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1200 s.** Expected ≈400 s, bracketed from this lane's recent actuals (149, 398, 569 s) and SG-252's 468 s: two ≈68 s host suites, one build (likely cache-satisfied), two proofs, two wrong-image runs, the whole-suite trial and the evidence dominate. If new work passes 1200 s, stop starting, commit, write the report, publish the receipt.

## Report

Destination: `docs/worklogs/SG-255_report.md`, evidence logs beside it (`docs/worklogs/SG-255_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈400 s expectation and names every phase over 60 s.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-255 | Report: docs/worklogs/SG-255_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
