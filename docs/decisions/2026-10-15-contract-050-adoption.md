# 2026-10-15 — Contract adoption 0.50.0 (D-2)

Owner decision, recorded the moment issued (`G-O4`). Session item **D-2** (hyphenated; distinct from project D2 recovery grant).

Question put: adopt contract 0.50.0 or stay on 0.47.0 — recorded 0.47.0 ≠ published 0.50.0 blocked every further dispatch (controlled-axis mismatch per DISPATCH §2); host already ran 0.50.0 (SG-193 echo).

Owner reply, quoted byte-identical: "D2 - approved." (2026-10-15, this chat). Read as approval of D-2 as recommended: **adopt 0.50.0**. The only live decision in the turn.

## Delta review (tag `contract-v0.50.0` read-only before checkout; adoption note quoted verbatim below)

Adoption note: "Contract payload 0.50.0 / PROJECT ADOPTION: None required. Each slice now leaves `<RUN_DIR>/<ID>.growth` beside its log; nothing reads it unless you do. Optional lane conf key `GROWTH_HEARTBEAT_S` (default 30; `0` disables the heartbeat)."

Doc diff 0.47.0 → 0.50.0 (12 files, +749/−56; RULES.md hash unchanged `49338e39…`):
- ARCHITECT §6: stage defined (`D448`) — the owner-approved slice set toward one named outcome; inside an approved stage flow without asking; audits wait for no go. This session's arc (deploy + micro-slice + candidates per the starter) is one stage under D16.
- ARCHITECT routing: `SECOND_OPINION.md` binds before any 🟡/🟠/🔴 decision (`D451`). D-2 itself was brought under 0.47.0, no violation; the duty starts now.
- AUDIT §4: slowest-waste duty (`D434`/`D436`) into LEDGER `slowest_waste`. SG-193 was rated pre-D436 (no column owed); first D436 row will be SG-194's.
- CODER.md: version line + `CO-103` skipped-list (SG-193's report already carried one — consistent).
- CODERS.md: opencode `agent=plan` read-only launch form (`D419`).
- DISPATCH §2: `agent=<a>` envelope setting (optional; defaults unchanged).
- LEDGER: twelve fields; `slowest_waste` never blank from this project's first D436 row on.
- ONBOARDING: `second_opinion:` project value.
- PACKET Structure: cut one measured waste per slice (`D434`/`D436`); full suite once on the candidate, base only the new rows' FAIL half (`D443`).
- Lane scripts (`dispatch/dispatch`, `dispatch/run-coder` +641): adopted wholesale by checkout; host-executed, not Architect-read. Growth heartbeat file: lane-side, nothing reads it unless tasked.

## Execution (this file's plan; owner confirmation above is the one confirmation)

`git -C .rules-cache checkout -q contract-v0.50.0` (approved tag, never the branch); drift check before/after (`status --porcelain` clean); grep OLD version string across the project and update live pointers only (AGENTS.md version record + loading line; STATE next-scope line); history (decisions, packets, reports, audits, ratings rows) stays byte-identical. Re-run `rules_check.sh`, expect VERSION CURRENT 0.50.0. Commit + push.

Live-pointer updates: AGENTS.md `0.47.0` record → `0.50.0` (D2 adoption 2026-10-15); loading line contract `contract-v0.47.0` → `contract-v0.50.0`.

## Standing consequences recorded here (consulted state, not cold-start)

- Ratings table converts to twelve columns section-by-section: older `###` sections keep 11-col shape (D415 precedent — never back-filled); each new section from SG-194 on carries `slowest_waste`.
- SG-194 packet obeys `D443` (candidate full suite; base only new rows' FAIL half) and notes no `slowest_waste` named yet.
- Reviewer value declared in AGENTS.md: `second_opinion: coder=opencode model=opencode-go/deepseek-v4.1-flash effort=max` — explicit rather than `default` because the Architect's own model (muse-spark-1.3 family) is ambiguously inside/outside the rule's "Muse 1.3" condition, and the explicit pick satisfies "never the Architect's own model" under both readings (`G-A2`). Reversible config; owner may set `default`/`off` (`G-K1`: decided, done, reported here). **SUPERSEDED 2026-10-17 (D-7): the value is now `default`, because this session's engine declares the Architect model `opencode/deepseek-v4.1-flash-free` — the explicit deepseek value was then the Architect's own family, the very thing `D451` forbids. Record: `docs/decisions/2026-10-17-d5-d6-d7-answers-l4-window.md`.**
- No project review ledger file created (only owed when a review runs). **Created 2026-10-17: `docs/reviews/review-ledger.md` (first review SG-200/201, D-5/D-6/D-7).**
