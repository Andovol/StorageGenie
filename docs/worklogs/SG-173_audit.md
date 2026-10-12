# SG-173 — Architect audit: diagnosis accepted, repairs remain pending

Immutable audit: base dd35165e8b363a93c1d20ae4ccdc302d39c07778 → work 901caf324c8421e5c276b3132ed4265bcf948c78 → report 3c6cbfd. Mapped notes fetch/readback identifies Dispatch-ID SG-173, report path and Work-HEAD; the report note records command-selected opencode / opencode-go/deepseek-v4.1-flash / max. Forced-command status is done/inactive. Checkout fast-forwarded to the audited report commit; diff contains exactly seven SG-173 worklog artifacts and no product change.

Holistic rating: **97/100**, author judgement under LEDGER.md; no flag. All material diagnostic criteria have evidence. Deductions: diagnostic-label/documentation accuracy and browser provenance. No application provider usage claimed; actual Codex/Coder platform cost is unavailable.

## Accepted evidence and limitations

- Live image 9064d2ce and health were re-observed. Backend GET/audit observations show the stale blocked-state dead-end. Isolated real-route controls reproduce 409 with open tasks, stale embedded IDs after resolving tasks, 200 acceptance despite those stale IDs, 422 expiry without classification and 200 completion with classification.
- Expiry ordering is correct on the observed matrix and existing boundary/sort tests. The actual fourth gap is unclassified assets absent from both resolved and unresolved expiry rows. No ordering rewrite is warranted.
- Existing backend tests: 30 passed; frontend: 23 passed across four files. These are diagnostic regression controls, not proof of repaired code. No repair has been implemented.
- Browser observations used a temporary Vite build against the live backend, not the deployed frontend URL. The artifact discloses that bridge and verifies zero backend/frontend source diff against the deployed base. Treat it as equivalent-source browser evidence; direct deployed-URL browser proof remains owed after the repairs.
- `SG-173_probe.py` T4 prints the literal suffix `expiry accepted assertion exists=True`; it does not measure that assertion. This suffix and the unconditional PROBE_OK footer are excluded from accepted verification. The observed task status/route response remain usable. The independent, unchanged control `backend/tests/test_plugin_expiry.py::test_dateless_import_requires_manual_entry_and_reads_back` actually GETs the asset, selects accepted EXPIRY_FIELD rows and asserts one persisted row plus one resolved task. Its body was read and its executed file is among the 30 green tests. The material completion criterion therefore has non-vacuous independent evidence; no false completion of a required criterion is accepted.
- Probe docstring references the root venv, while the actual working interpreter is backend/venv. Next packet must use the working path; do not execute that docstring command.

## Dispositions and next packet facts

| Finding | Disposition |
|---|---|
| F-SG173-1/6 host cache/tag/auth shape | OPEN, inherited host observation; no host change authorized. Independently verified contract bytes/echo 0.46.0 suffice on the controlled axis. |
| F-SG173-2/3 interpreter and local fixtures | RESOLVED for this diagnostic; fold working interpreter and per-module fixture definitions into next packets. Long-horizon F-SG144-1 stays in backlog. |
| F-SG173-4 expiry form on Review and AssetDetail | RESOLVED premise; both consumers go in classification/Resolve packets. |
| F-SG173-5 browser writable HOME | RESOLVED within sandbox writable scratch; no privilege elevation or host permission change. |
| F-SG173-7 ordering premise | RESOLVED: preserve ordering; explicit missing/unresolved visibility remains in repair chain. |
| ISS-173-3 literal probe suffix / docstring | FIX QUEUED in SG-175's isolated verification: measure the accepted assertion and assert each criterion before success; retain raw observations. Discard old literal label now. |
| ISS-173-4 browser provenance | OPEN for the post-repair deploy: use actual deployed URL for final story proof; distinguish source-equivalent observation from deployed-build observation. |
| Stale blocked-state, classification UI, Resolve semantics, visibility | FIX QUEUED: SG-175 → SG-176 → SG-177 → SG-178 in STATE ordered work. D-1012-14 already authorizes the scope; L2 checkpoints still bind. |
| D-1012-13, F-SG171-5 duplicated blocked text | Fold into SG-177 and SG-175 respectively; no additional owner approval for the already-approved scope. |
| D-1012-8 taxonomy mapping, Scene UI, F-SG144-1 | Existing backlog triggers; no separate new scope grant inferred. |

FIRST READ and DURING EXECUTION ambiguities are answered in the report and dispositions above. REMAINING resolves to STATE's ordered SG-175..178 and existing docs/backlog.md triggers. Harness context-size reading is unavailable in this session; no size threshold claim is made.

Next: standing close-out deploy SG-174, then close; next implementation session opens SG-175.
