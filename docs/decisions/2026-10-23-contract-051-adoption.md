# 2026-10-23 — Contract adoption 0.51.0 (D3)

Question put: adopt contract 0.51.0 or stay on 0.50.0 — recorded 0.50.0 ≠ shared 0.51.0 on the controlled axis (same shape that blocked dispatches at D-2); installed harness copies and the host contract copy already echo 0.51.0.

Owner reply, quoted byte-identical: "D3 - approved." (2026-10-23, this chat). Read as approval of D3 as recommended: **adopt 0.51.0**.

## Delta review (tag `contract-v0.51.0` read-only before checkout; adoption note quoted verbatim below)

Adoption note: "Contract payload 0.51.0 / PROJECT ADOPTION: Add a Roadmap if the project has none; decision items now list numbered Actions; messages use plain words and explain any term the owner did not use first; never raise a secret only because it appeared in an LLM chat; check the workstation's harness plugins against ONBOARDING.md Architect portability."

Project-side work check: Roadmap exists (`docs/ROADMAP.md`, top item is the default next action — complies); numbered Actions and plain words already the message shape (D1/D2 this session — complies); no secret raised from chat (nothing to retract); harness-plugin check is workstation-side, recorded as owed, not blocking.

Doc diff 0.50.0 → 0.51.0 (16 files; RULES.md reworked; lane `dispatch`/`run-coder` reworked; `rules_check.sh` touched).

`git -C .rules-cache checkout -q contract-v0.51.0` (approved tag, never the branch); drift check clean before and after; grep of the OLD version string across the project updates live pointers only (AGENTS.md version record; STATE next-scope line); history (decisions, packets, reports, audits, ratings rows) stays byte-identical. Re-ran the version read: cache tag `contract-v0.51.0`, `VERSION` 0.51.0. Commit + push.

Live-pointer updates: AGENTS.md `0.50.0` record → `0.51.0` (D3 adoption 2026-10-23); `0.50.0` note moved to the history file. No Coder-rulebook pointer lives in this repo (the Coder reads its own copy on the server, already 0.51.0 per the SG-233 receipt echo).
