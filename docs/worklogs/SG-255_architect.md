# SG-255 architect note — W1's image half on the repaired lane runtime (L3; launch record)

Stage: the W1 slice approved by the owner on 2026-10-26 (`D1`, `docs/decisions/2026-10-26-session-approvals.md`), at L3. SG-255 is the unexecuted image half SG-252's audit left blocked; the replacement for the audit's "SG-253" placeholder, on the owner's numbering.

Planned envelope: `SG-255 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (the project's standing model policy; settings ride the trigger, never the packet).

Packet: `docs/packets/SG-255-w1-image-half-proof.md` (commit `c6ef05b`, pushed before the trigger).

Blocker verdict: Launcher issue **#97 CLOSED** — the desk restarted the lane's rootless `docker.service` on 2026-10-27 23:50 Bucharest; server 29.9.2; `docker run --rm busybox true` rc 0; the app container came back by itself (same ID `a831fbd0`, image `e8c73735`); `/v1/health` 200. The desk says keep `DOCKER_CONFIG` until the root-owned `~/.docker` is fixed in the engine arc. No code change is in scope.

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`. The remote command carries the VERB only — no `dispatch` prefix.

Expected duration: ~400 s, bracketed from this lane's recent actuals (149, 398, 569 s) and SG-252's 468 s; two host suites, one build, two proofs, the wrong-image controls and the whole-suite trial dominate (`D369`).

Version chain: recorded `0.53.0` == published payload `contract-v0.53.0` == host `0.53.0` (the SG-252 receipt echo) == the echo the report must carry. `rules_check.sh` this session: CLEAN ×3, VERSION CURRENT 0.53.0.

Checklist (`DISPATCH.md` §2): scope = the owner-approved W1 stage · packet committed + pushed before the trigger (`c6ef05b`) · worktree clean · no dispatch in flight (`SG-255 --status` = `result=inactive id=SG-255 receipt=absent`) · nothing pushed while running · `PB-1`–`PB-6` cited · receipt = notes ref `refs/notes/storagegenie-coder-reports` + `Work-HEAD`, read back from the fetched remote ref.

Production basis (`G-K2`/`G-K3`): the host is a declared sensitive surface. **This slice changes nothing on it:** no package install, no sudo, no host configuration, no daemon or service restart, no app-database or stored-file access, no provider call, $0. Docker is used through the lane's socket for one isolated build and throwaway runs; the build tags only `storagegenie-backend:prover` and **never** the running app's image tag. The running container is not recreated. Health is read at start and end.

Design calls SG-255 inherits (so the next session does not re-derive them): one pytest marker `requires_native_libs` is the gated set; the guard skips when a capability is absent on a host but **fails** when `SG_IMAGE_PROOF=1`; the pure-Python EAN coverage lives in an unmarked host test; `make backend-test` = host suite minus the marker, then the image proof, with the prover image built from the worktree under a dedicated tag; the whole-suite image trial is one measured run and its A-vs-D verdict follows SG-243's published rule.
