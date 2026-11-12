# SG-314 audit — SG-312 served live as `release-sg314`; static-only diff, census identical, S1 without rollback

**Score 93/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high` (receipt note `Settings: … model_source=command effort_source=command`). Diff `614f61b..361d545`: `docs/worklogs/SG-314*` only. Engine elapsed 159 s (expected ≈250 s).

## Holds — checked against the evidence files

- **Runtime diff** (`SG-314_runtime-diff.txt`): JS, CSS and `index.html` only; both `.woff2` files same sha256 before and after. Backend derived set empty, as expected.
- **Census** before and after: `diff` empty, 29 tables (I ran the same `diff` here).
- **Served strings** (`SG-314_served-check.sh` on the served container and on `release-sg310`): the five step names 0 → 1, `nav-menu-toggle` 0 → 1, `evidence state` and `per-press` 1 → 0; `body` on `--paper`; `button,input,select,textarea{font:inherit}`.
- Health ×6, five routes 200, startup log clean by named lines, tag created, no tag moved, scratch removed.

## Findings (session IDs)

I6. **Contract line mislabelled.** The report gives `Rule-set version recorded here: 0.59.0 (D30, 2026-11-12)` as its "own copy as received" — that is `AGENTS.md`'s line, which the packet said not to echo. **Coder. Disposition: profile; the next packets repeat "if you received none, say exactly that".**
I7. **Effort not read** — no `opencode run` process visible to `ps`; stated, not inferred. Second slice in a row unable to read its own arguments (SG-313 too). **Lane, minor. Disposition: report to the desk in the END report.**
I8. **Unknown tag `storagegenie-backend:prover`** (`665caf31…`, created 2026-11-12 15:07 UTC, 17:07 GTB Standard Time). Not this slice's, not touched. **Disposition: host-cleanup step names it; ask the desk whose it is.**
I9. Restart count not re-read after the six probes; *Menu*'s media context not checked in the served CSS (proven in SG-313's DOM). Minor.

## Model note

Haiku's twelfth rotated slice: fast, exact, clean evidence files; one honesty slip in labelling a line it did not receive.
