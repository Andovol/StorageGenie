---
status: proposed
applied: NO
from: StorageGenie
raised: 2026-09-17
target: shared packet contract (`PACKET.md`, new `PG-EV-13`-class guard) or `RULES.md` byte-level clause
---

## Proposed rule

**Angle-bracket token integrity (the renderer-eats-the-token class).** Any file a slice edits that is known to contain angle-bracket tokens (think-tag, `<think>`, HTML-ish literals in string constants) is re-probed BY CHARACTER CODES after every edit — and tests exercising such strings CONSTRUCT them from character codes (`chr(60)`, `chr(62)`), never a typed escape.

## Evidence

SG-062 (StorageGenie, 2026-09-17): the edit-apply pipeline silently corrupted the THINK-TAG token in `strip_single_think` — guard condition, message and docstring each lost the `<…>` angle bytes and the guard started checking a literal `" thinking"` string that can never match real content (unbalanced-think fail-loud leg dead). Invisible in every text channel the Coder ran (their own diff/grep/read render the token the same way their editor mangles it); the backend suite stayed green because no test drove that leg with a real token; the report could not name the hunk. The Architect's byte-probe (char-code comparison across commits) caught it — the probe is what AUDIT.md §4's "text output of any tool is a rendering, not the bytes" already prescribes, and the `AUDIT.md` placeholder case (`#37`-family) is the report-side twin of the same mechanism. The repair protocol (char-code payload replacement + chr()-built pin test) is proven in SG-064's G0 (98): restored + mangler-immune pin.

## Generalisation test

1. Different stack? Yes — any codebase whose string constants contain `<…>` tokens (error messages, templates, regex literals) in any language/toolchain that renders those tokens in tool output or editing channels; the channel mangling is tool-class, not language-class.
2. Without naming things? Partly — the shared wording stays token-free ("an angle-bracket token a tool renders as markup"); the payload detail (char codes 60/116/104/105/110/107/62) is the project's example, not the rule.
3. What generalises: (a) probe-by-char-codes after edit for KNOWN token-carrying files; (b) tests build such strings from chr() codes; (c) a probe whose instrument crashes prints UNRELIABLE flags — fix the instrument, re-run, then read the verdict (`G-T6` extension, M38 instance).

## Cost

One standing packet line + one char-code probe per in-scope token-carrying file edit (seconds); replaces silent detection-free corruption that cost one below-95 rating, one repair fold, and one audit probe (SG-062 → SG-064 G0). Advisory at first: it fires only on files known to carry the token.
