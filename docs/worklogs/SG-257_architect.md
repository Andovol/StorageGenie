# SG-257 architect note — close-deploy rider for SG-256 (L3; launch record)

Stage: roadmap row 11, approved as an L3 stage on 2026-10-24 (D-1024-8); the polish plan (including "then its own deploy rider") approved by the owner on 2026-10-28 (`"D4 - approved"`, D4 in `STATE.md`). SG-256 is the work slice (audited 96); SG-257 is the rider.

Planned envelope: `SG-257 coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` (the project's standing model policy; settings ride the trigger, never the packet).

Packet: `docs/packets/SG-257-close-deploy-rider-for-sg256.md` (commit `896beff`, pushed before the trigger).

Trigger class: OpenCode `job_spawn`, wake on exit. ONE backgrounded call; call cap 2160 s (lane `RUN_BUDGET_S=2100` + 60 s stop window). SSH client, key `~/.ssh/storagegenie-architect-dispatch`, `-p 2222`, user `andrei`, host `87.106.66.242`, `-o BatchMode=yes`. The remote command carries the VERB only — no `dispatch` prefix.

Expected duration: ≈400 s, from SG-251's actual 257 s (one build, one recreate, full verify) plus the SG-256 frontend-layer rebuild and the bundle/census comparison; this lane's recent actuals are 149, 398, 447, 540 and 569 s.

Version chain: recorded `0.53.0` == published payload `contract-v0.53.0` == host `0.53.0` (the SG-256 receipt echo) == the echo the report must carry. `rules_check.sh` this session: CLEAN ×3, VERSION CURRENT 0.53.0.

Checklist (`DISPATCH.md` §2): scope = the owner-approved D4 rider · packet committed + pushed before the trigger (`896beff`) · worktree clean · no dispatch in flight (`SG-257 --status` checked before the trigger) · nothing pushed while running · `PB-1`–`PB-6` cited · receipt = notes ref `refs/notes/storagegenie-coder-reports` + `Work-HEAD`, read back from the fetched remote ref.

Production basis (`G-K2`/`G-K3`): the host, the app database and the live service are declared sensitive surfaces. **The owner's D4 approval covers this rider** ("then its own deploy rider"), and the packet is the written plan for it. The rider makes **one build and one recreate** of the backend container from the approved tree; **no migration**; the app database is opened **read-only** for the schema head and the 29-table census, with every count required identical; **no production row is written**; the new edit/clear controls are **not exercised live** (that would write the owner's data); no provider call, no key or `.env` read, $0. Health is read at the start, six times after the recreate and at the end. The release record and its tag are written by the Architect after this slice is audited, from the rider's evidence.

Design calls SG-257 inherits (recorded so the next session does not re-derive them): the served runtime diff must be exactly the two SG-256 backend files; the frontend JS bundle must change (the component/client/types are in it) while the index/CSS may not; the served code and bundle are grepped from the served artifact, not the worktree; the live clear/edit is proven by the served bytes, not by a data write; the census is the production-safety proof.
