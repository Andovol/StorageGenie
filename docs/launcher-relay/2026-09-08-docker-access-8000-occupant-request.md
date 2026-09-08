# Desk request: docker access for the dispatch identity + identify the :8000 occupant (StorageGenie SG-021 follow-up)

**From:** StorageGenie Architect (project `Andovol/StorageGenie`, branch `automation`)
**Date:** 2026-09-08 · **Owner-approved:** D13 ("D13 - ok")
**Blocking:** SG-021 manual compose pass (receipt `009bf114`, rated 96) — whole-slice STOP at its G1 probe, no workaround attempted.

## Ask 1 — docker API access for the dispatch identity

The confined run resolves `/usr/bin/docker` (client 29.6.2, compose v5.3.1) but the daemon refuses it:

```text
permission denied while trying to connect to the Docker API at unix:///var/run/docker.sock
```

(`timeout 120s docker info` exit 1, 0.13 s; `docker compose ps` same denial.) No `sudo`/socket/group change was attempted — that is your call. What the pass needs once granted: `docker compose build backend` (apt layer with `tesseract-ocr` + `libzbar0`), `compose run --rm --no-deps` for the ISS-1 decoder re-proof, `compose up -d`, `compose exec` suites, `compose restart backend`. Requested scope is this project's compose file only; the packet forbids volume/server inspection beyond the probe, catalog writes, and teardown ambiguity (running state gets reported either way).

## Ask 2 — identify the :8000 listener

Read-only probes from confinement show a listener at `127.0.0.1:8000` answering a foreign Uvicorn 404 (`HTTP/1.1 404 Not Found`, `server: uvicorn`, 9-byte `Not Found` body) with no owning PID visible, while `5173` is closed. The slice packet makes rebinding an owner decision (it cascades to hardcoded `VITE_API_BASE` + runbook), so no rebind was attempted. Please report the occupant (PID/process/project); the port decision returns to the owner with that evidence, then SG-021 re-runs fresh.

## What happens after you answer

Fresh SG-021 packet/base → image build → ISS-1 green in-image → compose-up/health/suites/UI/restart (or the owner-decided port outcome). No host action is requested from this project beyond the two asks above; nothing is expected back except the grant + occupant identity.
