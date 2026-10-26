# SG-252 architect note — W1: the image-route test gate (L3; launch record)

Stage: the W1 slice, approved by the owner on 2026-10-26 (`D1`, `docs/decisions/2026-10-26-session-approvals.md`), at L3.

Planned envelope: `SG-252 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (the project's standing model policy; settings ride the trigger, never the packet).

Packet: `docs/packets/SG-252-w1-image-route-test-gate.md` (commit `bedb712`, pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`. The remote command carries the VERB only — no `dispatch` prefix.

Expected duration: ~500 s, bracketed from this lane's recent actuals (149, 398, 569 s); the two ≈62 s suites, one build and the evidence dominate (`D369`).

Version chain: recorded `0.53.0` == published payload `contract-v0.53.0` == host `0.53.0` (the SG-251 receipt echo) == the echo the report must carry. `rules_check.sh` this session: CLEAN ×3, VERSION CURRENT 0.53.0.

Checklist (`DISPATCH.md` §2): scope = the owner-approved W1 slice · packet committed + pushed before the trigger (`bedb712`) · worktree clean verified (`git status` empty; HEAD == `origin/automation`) · no dispatch in flight (`SG-252 --status` = `result=inactive id=SG-252 receipt=absent`) · nothing pushed while running · `PB-1`–`PB-6` cited · receipt = notes ref `refs/notes/storagegenie-coder-reports` + `Work-HEAD`, read back from the fetched remote ref.

Production basis (`G-K2`/`G-K3`): the host is a declared sensitive surface. **This slice changes nothing on it:** no package install, no sudo, no host configuration, no app-database or stored-file access, no provider call, $0. Docker is used through the lane's socket for one isolated build and throwaway runs; the build tags only `storagegenie-backend:prover` and **never** the running app's image tag. The running container is not recreated.

Design calls SG-252 makes (so the next session does not re-derive them): one pytest marker `requires_native_libs` is the gated set; the guard skips when a capability is absent on a host but **fails** when `SG_IMAGE_PROOF=1` (the proof cannot pass on a skip); the pure-Python EAN coverage splits into an unmarked host test; `make backend-test` = host suite minus the marker, then the image proof, with the prover image built from the worktree under a dedicated tag; the whole-suite image trial is one measured run, and its A-vs-D verdict follows SG-243's published rule.
