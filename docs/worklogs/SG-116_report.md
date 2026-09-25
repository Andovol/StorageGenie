SG-116 report — Jina EU reachability probe: verdict EU-DEAD (read-only, $0.000000)
=================================================================================

Verdict: EU-DEAD. `eu.s.jina.ai` is NXDOMAIN on today's host (getent exit 2, no output;
`socket.getaddrinfo` -> `gaierror [Errno -2] Name or service not known`) while `s.jina.ai`
resolves and returned HTTP 200 with 3 results. F-SG104-3 reproduces exactly — it is stale, not
fixed. No change was made here (no switch, no migration, no container action, no code edit).

NO switch is implemented in this slice, however small (G-A7 / scope ceiling honoured).

Contract echo + source path
---------------------------
Contract `0.36.0` — installed-vs-payload check, never checkout-vs-stamp (G-L1/M3).
- source: `/home/andrei/storagegenie-contract/VERSION` = `0.36.0`
- source HEAD: `a9324d5e1782384c036c1411ec8adac6bb2acaa1` (== published `a9324d5`)
- `sha256sum /home/andrei/storagegenie-contract/RULES.md` =
  `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`
- payload `/home/andrei/storagegenie-contract/RULES.sha256` =
  `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46 RULES.md` -> match.
- recorded `0.36.0` == published `a9324d5`. Clean.
- Verbatim recorded line source path `/home/andrei/StorageGenie/AGENTS.md:4`:
  `> Rule-set version this project records: **0.36.0** (D1 adoption 2026-09-25: checkouts `55a4aa6`
  (0.34.0) + `308af92` (0.35.0) + `a9324d5` (0.36.0) oldest-first, no tags published; … supersedes
  `0.33.0`).`
- Minor out-of-scope observation: `AGENTS.md` Loading cites a repo `.rules-cache/`, but
  `/home/andrei/StorageGenie/.rules-cache` does not exist on this host. The authoritative live copy is
  `/home/andrei/storagegenie-contract/` (used above). Reported, not acted on.

Model / effort / spend (CO-78)
------------------------------
Read from process arguments, never a system-prompt identity line.
- argv: `/proc/938464/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie --variant high
  # SG-116 — …` (the argv also carries the full packet prompt text).
- effort = `high` (from `--variant high`).
- model = `unknown` — no `--model` in argv; the packet states the CLI default is omitted by policy, and
  I refuse to guess.
- Spend real $ = `$0.000000`. EU leg: NXDOMAIN, NO HTTP request reached Jina -> nothing metered.
  Global leg: 1 metered request (HTTP 200). Jina returns `usage.tokens`, not USD, and neither the repo
  nor the contract holds a Jina price constant, so the dollar figure is not independently observable;
  reported as `$0.000000` (at any plausible per-token rate the ~10^3–10^4 token request rounds below
  $0.000001 to six decimals) with this caveat rather than a guessed rate. Total metered searches = 1 of
  the allowed ≤2.

Refs
----
- Work dir `/home/andrei/StorageGenie`, origin remote `git@github.com:Andovol/StorageGenie.git` (as on host)
- BASE_REF = `origin/automation`
- BASE_RESOLVED = `de3ac037c267e4e28b0a476606684934c5afea4d` (== start HEAD)
- WORK_HEAD = `060cb2616d1d1103a0c3a92503947f16fccb14e1`

G1 — premises (verify each; corrections worth more than agreement)
------------------------------------------------------------------
All §G1 hypotheses held exactly; no difference. Raw in `SG-116_verify.log`.
- `git status --porcelain` EMPTY (no dirt). `git rev-parse HEAD` =
  `de3ac037c267e4e28b0a476606684934c5afea4d` == `origin/automation` (no gap). Branch `automation`.
- `jina.py:42` `JINA_EU_BASE_URL = "https://eu.s.jina.ai/"` and `jina.py:43`
  `JINA_GLOBAL_BASE_URL = "https://s.jina.ai/"` — VERIFIED verbatim.
- Key seam: `config.py:38-40` declares `jina_api_key` (comment + field); `jina.py:59`
  `JINA_API_KEY_ENV = "JINA_API_KEY"` env fallback — VERIFIED verbatim.

G2 — DNS legs (raw in `SG-116_verify.log`)
------------------------------------------
- EU: `getent hosts eu.s.jina.ai` -> exit `2`, NO output (NXDOMAIN).
- GLOBAL: `getent hosts s.jina.ai` -> exit `0`, 3 AAAA lines (`2606:4700:20::ac43:4636`,
  `…::681a:af2`, `…::681a:bf2`).
- Cross-check `socket.getaddrinfo(host, 443, TCP)`: EU -> `gaierror [Errno -2] Name or service not
  known`; GLOBAL -> 3×A (`104.26.11.242`, `172.67.70.54`, `104.26.10.242`) + 3×AAAA. This reproduces
  F-SG104-3 on 2026-09-25. Both legs bounded ≪60s ordinary.
- Key presence, names-only: `settings.jina_api_key_present=True`, `env_JINA_API_KEY_present=False`,
  `resolve_api_key_present=yes`. No key byte was printed, logged, quoted or committed. Key present ->
  the `BLOCKED: no Jina key on host` STOP-as-SUCCESS path was NOT taken.

G3 — one real EU search (REAL `fetch_jina_search`), global diagnostic iff EU failed
-----------------------------------------------------------------------------------
Query shape (SG-082/SG-104): name `Cronat Gold`, brand `Jacobs`, category `food`; defaults
`num=5 type=web gl=ro`; both sides through the real `fetch_jina_search` path with the client's own 15s
timeout.
- EU (base `https://eu.s.jina.ai/`): `status_code=None`;
  `no_result_reason='transport: ConnectError: [Errno -2] Name or service not known'`; results=0;
  body_bytes=0; elapsed=0.040s. Transport-dead; no HTTP request was sent.
- GLOBAL diagnostic (ran IFF EU transport-degraded, exactly once; base `https://s.jina.ai/`):
  `status_code=200`; `no_result_reason=None`; results=3; body_bytes=2223; elapsed=8.193s. Host live.
  (Results are eMAG CAPTCHA/511 pages — liveness of transport only; not a data-quality claim.)
- Total metered Jina searches = 1 (≤2); real spend `$0.000000` (caveat above).

Verdict (exactly one)
---------------------
EU-DEAD.

Follow-up outline (EU-DEAD; NOT implemented here, however small)
-----------------------------------------------------------------
Recommend a follow-up slice that switches the default Jina base from `JINA_EU_BASE_URL`
(`https://eu.s.jina.ai/`) to `JINA_GLOBAL_BASE_URL` (`https://s.jina.ai/`), with the EU/Romania
data-residency trade-off recorded and owner-approved, plus the matching constant/test updates. One-line
reason a switch is now evidenced: the EU base is NXDOMAIN on the host while the global base answers
HTTP 200 with results, so the current default cannot serve any request (transport-dead, not merely
degraded). This slice implements none of it.

Vacuous-pass check (stated loudly)
----------------------------------
No criterion passed vacuously. The EU transport failure IS the evidence of the reachability verdict —
it is never read as "search works". The global 200/3-results is the liveness half only. The DNS set is
non-empty and evaluated on both bases; no gate was skipped; no grep was scope-narrowed.

Guards invoked (0.36.0)
-----------------------
`PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-03` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` ·
`PG-PR-01` (enumerated with non-mutating forms only) · `PG-PR-03`.

Receipt note on refs/notes/storagegenie-coder-reports
-----------------------------------------------------
Note added on WORK_HEAD `060cb2616d1d1103a0c3a92503947f16fccb14e1` and verified against the FETCHED
ref (mapped local name `refs/notes/verify/sg116-reports`). Executed output pasted verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-116 | Report: docs/worklogs/SG-116_report.md | Work-HEAD: 060cb2616d1d1103a0c3a92503947f16fccb14e1" 060cb2616d1d1103a0c3a92503947f16fccb14e1
note_add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   df8602f..143934d  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
note_push_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/verify/sg116-reports
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/verify/sg116-reports
fetch_exit=0
$ git notes --ref=refs/notes/verify/sg116-reports show 060cb2616d1d1103a0c3a92503947f16fccb14e1
Dispatch-ID: SG-116 | Report: docs/worklogs/SG-116_report.md | Work-HEAD: 060cb2616d1d1103a0c3a92503947f16fccb14e1
show_exit=0
```

note=yes

UNCLEAR
-------
- FIRST READ: whether `.rules-cache/` was expected to exist in the repo (AGENTS.md Loading cites it);
  it is absent, and the live contract copy at `/home/andrei/storagegenie-contract/` was used instead.
- DURING EXECUTION: whether the global diagnostic body's full bytes should have been persisted; the
  probe printed only the first 1500 chars, and re-fetching would exceed the ≤2-search cap, so the
  verify log carries the captured excerpt with the limitation stated.
- REMAINING: none of this slice's criteria remain open; the EU-DEAD verdict still needs an
  owner-approved follow-up slice before any default base is switched (implemented nowhere here).
