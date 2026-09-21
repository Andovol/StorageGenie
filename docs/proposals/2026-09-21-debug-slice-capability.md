---
status: proposed
applied: NO
from: StorageGenie
raised: 2026-09-21
target: dispatch engine (run-coder / unit confinement) — trigger-loaded debug-slice capability, not an always-loaded rule
---

## Proposed rule
Provide a debug-slice kind: a confined slice dispatched against a failed ID may read that ID's unit status, unit journal, and engine residue, read-only. Scope is own-ID only — never another ID's output, never host-wide logs.

## Evidence
- StorageGenie SG-066 (2026-09-21): the trigger reported `result=no_receipt`, the status verb `failed`/`receipt=absent`, and `--attach` repeated the same line. Three dispatches plus a full read-only probe slice (SG-071) could not name the cause; the Notes ref held only a Negative-Receipt. Diagnosis required the owner to open the host journal by hand: the unit had actually run 299 s and died on a transient upstream `server_error` mid-repair, with work stranded uncommitted. Cost: one owner host access + one probe slice + one delayed retry.
- StorageGenie SG-027 attempt-2 (2026-09-12): "failure with no project-readable evidence" (unit `failed`, no commits, no receipt, trigger line lost) — same class, relayed to the desk then.
- Possible title-overlap with Launcher#30 ("self-diagnosis proposal"); body not opened per PR-01 — desk to merge or separate.

## Generalisation test
1. Different stack: yes — any project on this dispatch engine meets unit failures with only the result line visible; a scoped debug read helps regardless of language, provider, or product.
2. Without naming: yes — stated in engine concepts (failed ID, unit status/journal, residue). Only the origin project is named, per the deliberate exception.

## Cost
Adds: a unit-scoped read grant (own ID's status/journal/residue) usable by slices carrying a debug marker; documented in the dispatch procedure at the point where `--attach` repeats the result line. Trigger-loaded — billed only on debug slices, never on product slices. Replaces: owner-pasted journals and inference probe slices (SG-071 class). Looked at: packet-side workarounds — none available; the confinement boundary is desk-owned, and the Coder cannot grant itself reads.
