# SG-174 — Close-out deploy audit, 98/100

Immutable base f53fcd554544421641fe41a8d9751f8becc4f5b1 → work ab55c0163d2025470bb81c2ea1253521c9cfdc33 → report 924eb57. Diff contains exactly eight SG-174 worklog files, zero product/schema/configuration hunks. Explicit notes-ref fetch and remote note readback identify Dispatch-ID SG-174, report path, Work-HEAD and command-selected opencode / opencode-go/deepseek-v4.1-flash / max. One post-deadline status query returned done/inactive.

Holistic score **98/100**, audit judgement under LEDGER.md; no safety/trust flag. Deduction: one corrected capture attempt from a guessed schema column and a host-expanded glob. Final committed evidence is complete and discriminating; no product/data impact. Actual report-writing duration is 409s against observed 2100s lane budget; final engine elapsed is not exposed by the compact done status. Coder-platform cost unavailable; application provider calls zero per report.

Direct evidence: build log exit 0; recreate log exactly one Recreate/Recreated/Starting/Started sequence, exit 0; before/after distinct container Id/Created/StartedAt and unchanged running healthy status. New image d5da5684 is a manifest/attestation re-export of cached product layers; served JS/CSS/index hashes are identical, so image movement is not treated as product movement. New container 23d31ff5 proves recreation independently.

Health six GETs each side all 200 with DB/storage ok; authoritative enumeration gives 28 table names with equal counts on both sides. Read-only SQLite hash is unchanged and nonempty. Schema head unchanged. GET story pages and positive/negative CORS preflight controls unchanged. Original logs were inspected as well as the emitter's verification summary; health/count/hash comparison was independently recomputed during this audit with a changed-count control. No new browser or live mutating request was needed to validate this diagnostic-only deploy.

## Findings and remaining dispositions

| Finding | Status / destination |
|---|---|
| SG-174-I1 manifest moves while served bytes identical | RESOLVED measured premise; no code change or repair claimed. |
| SG-174-I2 bare-IP versus pinned-vhost gate | RESOLVED by SNI/Host-sensitive readings captured both sides; future deploys use pinned vhost. |
| SG-174-I3 guessed column/glob capture | RESOLVED in final capture; next compatible packet reads schema before querying and keeps container globs inside container shell. |
| SG-174-I4 / F-SG173-1/6 host cache/tag/auth shape | OPEN inherited observation, no host mutation authorized; independent contract bytes/echo 0.46.0 remain evidence. |
| SG-174-I5 Docker capability | RESOLVED read-only capability observation; granted lane socket used, no sudo/default root-only socket. |
| Owner visual verdict | OPEN, observational follow-up with next repair's actual deployed-URL story proof; does not prevent this code-unchanged deploy from completing. |
| SG-175..178 repair chain | FIX QUEUED in STATE, already-approved scope, L2 sequential audit/checkpoints. D-1012-13 in SG-177; duplicate blocked sentence and probe-label correction in SG-175. |
| F-SG144-1 venv / parked Scene arc | OPEN in docs/backlog.md on existing triggers. |
| Report-commit notes receipt | RESOLVED by current mapped fetch/readback at 924eb57. |

All FIRST READ / DURING EXECUTION issues are answered above; REMAINING has named STATE/backlog destinations. Context-size reading unavailable in this harness. No new shared-rule proposal: existing schema-before-query and harness-specific transport obligations already cover the observed mistakes.
