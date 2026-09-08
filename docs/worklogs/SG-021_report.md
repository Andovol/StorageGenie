SG-021 — BLOCKED: rootless builder activity path is read-only; 8001 is foreign occupied

Status: BLOCKED — this fresh D12 manual compose pass verified rootless Docker access
and the read-only shape probes, but it cannot continue to image proof because the
rootless BuildKit activity directory is read-only. G4 is independently stopped by a
foreign service on the D14-authorized 8001 port. No workaround, privileged fallback,
rebind, or foreign-service action was used.

BASE requested ref: `automation`

BASE resolved at slice start: `592ba42fc8c5232ff6a6041bfd2f3d55b179eb0d`

WORK_HEAD: `a2e1f5c` (the evidence content commit; the metadata fix below is a
separate record-only commit so this report can name the immutable work commit).

Work dir: `/home/andrei/StorageGenie`

Origin: `git@github.com:Andovol/StorageGenie.git`

Coder: `codex`

Model: `unknown` — no model ID appeared in the live process arguments or available
provider metadata. The process arguments did prove the requested effort.

Reasoning effort: `high` — proven from the live process arguments:
`/usr/local/bin/codex exec --sandbox danger-full-access -c model_reasoning_effort=high -C /home/andrei/StorageGenie`.

Autonomy: L2, D12 single slice.

Overall elapsed: approximately 1 s of observed command wall time / 2100 s (35 min)
overall bound; no command was killed and no command lacked observable progress.

## G1 — capability, collision, and shape probe

All ordinary G1 commands had a 120 s bound. Tool resolution was explicit:
`/usr/bin/docker`, `/usr/bin/curl`, `/usr/bin/git`, `/usr/bin/ps`, `/usr/bin/ss`,
`/usr/bin/python3`, and `/usr/local/bin/npm`; `pytest` was not on the host PATH.

Docker capability passed:

```text
Context:    rootless
Server Version: 29.6.2
Storage Driver: overlayfs
Security Options:
  rootless
Docker Root Dir: /home/andrei/.local/share/docker
```

`timeout 120s docker info` exited 0 in approximately 0.057 s. `timeout 120s docker
compose config --quiet` exited 0 in approximately 0.058 s. Both emitted observable
exit evidence; the config criterion is not vacuous.

`.env` presence passed without content access:

```text
env_present=yes mode=600 owner=andrei:andrei size=203 bytes
```

`frontend/Dockerfile` was present:

```text
frontend_Dockerfile=present mode=664 owner=andrei:andrei size=181 bytes
```

The ports were probed read-only using curl (10 s request bound within the 120 s
ordinary-command bound):

8000 returned the foreign shared-host response:

```text
HTTP/1.1 404 Not Found
server: uvicorn
content-length: 9
content-type: text/plain; charset=utf-8
Not Found
```

This is consistent with the desk Ask 2 identification of the foreign `finnhub-mcp`
tenant. `ss` exposed no owning PID in this confined process view. Port 8000 was not
touched.

8001 returned:

```text
HTTP/1.1 303 See Other
server: uvicorn
location: /login
```

Its owning process was exposed as:

```text
PID 761216 user andrei
/home/andrei/ShoperOS/venv/bin/python3 /home/andrei/ShoperOS/venv/bin/uvicorn services.api.app.main:app --host 127.0.0.1 --port 8001
cwd=/home/andrei/ShoperOS
```

`GET /v1/health` on 8001 returned `HTTP/1.1 404 Not Found` with JSON body
`{"detail":"Not Found"}`. This is foreign to StorageGenie. Docker reported zero
containers, so the packet's G4 collision stop applies. No rebind was attempted.

5173 was closed:

```text
curl: (7) Failed to connect to 127.0.0.1 port 5173 after 0 ms: Couldn't connect to server
```

Final `ss` output exposed listeners only on 8000 and 8001; 5173 was free.

G1 elapsed approximately 0.18 s / 120 s bound, with approximately 0.10 s for the
read-only process identity/fingerprint follow-up. No command was killed.

## G2 — image build

Docker access granted this leg, so `timeout 1500s docker compose build backend` was
invoked. It exited 1 in approximately 0.20 s before any Dockerfile layer ran. The
exact builder failure was:

```text
failed to update builder last activity time: open /home/andrei/.docker/buildx/activity/.tmp-default1766839524: read-only file system
```

The SG-013 dependency line exists at `backend/Dockerfile:3`:

```text
RUN apt-get update && apt-get install -y --no-install-recommends curl tesseract-ocr libzbar0 && rm -rf /var/lib/apt/lists/*
```

It was not executed. Therefore the apt installation is unanswered, not green and
not an apt-layer failure. No Dockerfile redesign was attempted.

G2 elapsed approximately 0.20 s / 1500 s bound.

## G3 — ISS-1 and full backend suite in the image

UNANSWERED after G2. Since no image was built, neither the decoder test command nor
the full in-image backend suite was invoked. The two required decoder nodes remain
unproved:

```text
tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier
tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence
```

No test gate emitted output, so no count or green result is claimed. This is not a
vacuous pass. G3 elapsed 0 s executed / 600 s bound for each suite leg.

## G4 — remap, up, health, suite, UI, restart

UNANSWERED/STOPPED. The packet permits the D14 remap only when 8001 is free of a
foreign occupant. It was not free: PID 761216 from `/home/andrei/ShoperOS` answered
on 8001. Accordingly, this run did not edit `docker-compose.yml`, did not change
`VITE_API_BASE`, did not edit README runbook URLs, and did not attempt `up`, health,
compose exec, UI serving, or backend restart.

G4 elapsed 0 s executed / 1800 s early-close bound.

No README correction is justified. The live StorageGenie service was never reached,
and the only established contradiction was the already-known shared-host occupancy,
not a StorageGenie runbook behavior.

## Scope, side effects, and vacuity check

Only these permitted output files changed:

- `docs/worklogs/SG-021.log`
- `docs/worklogs/SG-021_report.md`

No product, migration, compose, frontend, port, or configuration file changed. No
`.env` content was read or printed. No catalog/database write, live service write,
volume/server inspection, sudo, socket chmod, group change, restart, or teardown
occurred. `mypy` was not run because later gates were stopped; no code change was
made and no mypy result is claimed.

No acceptance criterion passed vacuously. G1 capability/config/file/port checks had
observable outputs; the G4 collision and G2 builder failure are quoted; G3/G4 are
explicitly unanswered.

## Live-state ledger

- Containers: none. `docker ps -a` emitted only its header; Docker reported 0 running and 0 stopped.
- Port 8000: foreign Uvicorn 404; PID not exposed in this view; untouched.
- Port 8001: foreign ShoperOS Uvicorn, PID 761216; untouched.
- Port 5173: closed/free at the final probe.
- StorageGenie health: unanswered; no project container exists.
- Backend restart: not attempted; state unchanged.

Exact remaining delta: make `/home/andrei/.docker/buildx/activity` writable for the
rootless builder and clear 8001 owner-side. Then make a fresh SG-021 attempt to build
the image, re-prove both ISS-1 decoder nodes plus the full in-image suite, apply the
authorized D14 `8001:8000`/`VITE_API_BASE`/runbook cascade, bring up Compose, prove
health and served UI bytes, and prove backend restart recovery. Port 8000 remains
foreign and must never be reclaimed.

## Receipt

The final work commit will be pushed to `automation`; the notes ref is
`refs/notes/storagegenie-coder-reports`. The note must be attached last, with no
later commit, and its first line must be:

```text
Dispatch-ID: SG-021 | Report: docs/worklogs/SG-021_report.md | Work-HEAD: <hash>
```

The note will be verified locally and from the pushed notes ref. This direct process
has no external dispatch-result artifact, so no runner `note=yes` line is claimed
unless one is actually observed.

UNCLEAR — FIRST READ: Rootless Docker capability was provisioned and passed, but the
expected free D14 port 8001 was occupied by a foreign ShoperOS Uvicorn service; the
prior blocked-run model metadata was not reused, so this run records model unknown.
UNCLEAR — DURING EXECUTION: The G4 collision prevented rebind/up, while the G2
rootless BuildKit activity path failed read-only before the apt layer; no workaround
or privileged route was attempted.
UNCLEAR — REMAINING: Make the rootless builder activity path writable and clear 8001
owner-side, then rerun the remaining image, ISS-1, Compose, UI, and restart proofs.
