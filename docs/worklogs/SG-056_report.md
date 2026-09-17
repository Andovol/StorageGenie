# SG-056 — FakeProvider signature drift: conform to the `(image_bytes, prompt)` surface

**Dispatch-ID:** SG-056 · **Coder:** opencode · **Effort:** medium (read from process args: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-056 …`) · **Model:** `unknown` (no model id on argv; CLI default per policy — not guessed from any identity line).
**Contract:** 0.27.0. **Spend:** real `$0.000000` actual vs `$0` bound (zero provider calls; fake only).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`.

- **BASE REF requested:** `origin/automation`; **resolved commit:** `8f9847f4d5baa80a60c9a2c6a48dbad22e8b8f9c` (`SG-056 packet (FakeProvider signature drift, defect, D78 chain)`).
- **WORK_HEAD:** the commit carrying this report + `SG-056.log` + `SG-056_verify.log` + the code/tests — **stated in the delivery message** (it cannot be stated inside a file that is itself part of that commit, same convention as SG-053/SG-054). The receipt note is attached to it; the verified note output is then appended verbatim by a docs-only follow-up commit (§11).
- **Slice wall-clock:** start `2026-09-17T12:23:55Z` (coder process start); report frozen on the next line's clock reading (~4 min).

## 1. Starting tree (clean expected; dirt = STOP first)

```
$ git status --porcelain=v1        # (also untracked-files=all)
$ git branch --show-current
automation
$ git rev-parse HEAD ; git rev-parse origin/automation
8f9847f4d5baa80a60c9a2c6a48dbad22e8b8f9c
8f9847f4d5baa80a60c9a2c6a48dbad22e8b8f9c
```

Clean and level (`HEAD == origin/automation`, empty porcelain) — no STOP. The final tree carries exactly: 2 production files (`fake.py`, `protocols.py`), 2 test call-site files, 1 new test file, 3 worklogs. No hunk outside the ceiling.

## 2. Premises re-verified in-slice (quoted reads, `PG-IC-09`)

- **Write path** `router.py:52` `def execute(self, operation, *args, estimated_cost=0.0, **kwargs)`; call at `router.py:67` `return getattr(primary, operation)(*args, **kwargs)`. **Matches** the packet's "read, no hunk" — with one correction in F-SG056-1.
- **Read path** `reader.py:308-310` `result = router.execute("extract_items", image_bytes, call_prompt, estimated_cost=estimated_cost)`. **Matches.**
- **Stale defs** `fake.py:52` `def extract_items(self, image_ref: str) -> ProviderResult` and `protocols.py:29` `def extract_items(self, image_ref: str) -> ProviderResult`. **Matches.**
- **Conformant defs** `fake.py:104-110` `ScriptedProvider.extract_items(self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0)`; `opencode_go.py:235-241` identical surface. **Matches.**
- **Test doubles** `test_ai_pipeline.py:569,680,742`; `test_phase2_e2e.py:202`; `test_planning.py:60`; `test_phase3_e2e.py:278` — all `(self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0)`. **Matches.**
- **Direct old-shape calls** exactly two: `test_extraction_contract.py:158` `fake.extract_items("img-1")` and `test_provider_gateway.py:159` `needs.extract_items("img-1")`. **Matches** the packet's count.
- **Docstring mention** `planning/service.py:4` names `extract_items(image_bytes, prompt)`; `planning/service.py:51` is `PLANNING_OPERATION = "extract_items"` (a string constant), not a def. Considered-and-excluded.

**No premise required correction beyond F-SG056-1.** All line numbers quoted are the pre-hunk tree.

## 3. Provider enumeration — `extract_items` defs and call sites vs the packet's expectation

**Criterion:** every `extract_items` definition and call site in the tree, by grep, on the pre-hunk tree.

| # | Kind | Location | Shape | Disposition |
|---|---|---|---|---|
| 1 | def (Protocol) | `protocols.py:29` | `image_ref` — STALE | **G1 hunk** |
| 2 | def | `fake.py:52` `FakeProvider` | `image_ref` — STALE | **G1 hunk** |
| 3 | def | `fake.py:104` `ScriptedProvider` | 3-arg | conformant, untouched |
| 4 | def | `opencode_go.py:235` `OpenCodeGoProvider` | 3-arg | conformant, untouched |
| 5 | docstring only | `planning/service.py:4` (`:51` is a string constant) | n/a | excluded; the rail asserts `not hasattr(service, "extract_items")` |
| 6 | test double | `test_ai_pipeline.py:569, 680, 742` | 3-arg | conformant, untouched |
| 7 | test double | `test_phase2_e2e.py:202` | 3-arg | conformant, untouched |
| 8 | test double | `test_planning.py:60` | 3-arg | conformant, untouched |
| 9 | test double | `test_phase3_e2e.py:278` | 3-arg | conformant, untouched |
| 10 | call site | `reader.py:309` (via router) | 3-arg | conformant, untouched |
| 11 | call site | `test_extraction_contract.py:158` | old 1-arg | **hunk** |
| 12 | call site | `test_provider_gateway.py:159` | old 1-arg | **hunk** |
| 13 | call site | `test_opencode_go.py:130` | 3-arg | conformant, untouched |

**Diff vs the packet's expectation:** the packet's named sets are all present and matching. Extras it did not list: `planning/service.py:51` (`PLANNING_OPERATION` constant) and `test_opencode_go.py:130` (a 3-arg call). Nothing the packet expected is missing. The only two stale call sites are exactly the two named.

## 4. Goal outcomes

- **G1** — `fake.py:52` now `extract_items(self, image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0)`; payload semantics unchanged — still no `confidence`, extra `source`, now keyed off `image_bytes`, i.e. still schema-invalid by SG-028 design (`pg` accepts-and-ignores `prompt`/`estimated_cost`; no recording added because no test needs it). `protocols.py:29` carries the same surface. `reader.py` / `router.py` / `opencode_go.py` **no hunk** (each verified conformant). Two call-site hunks keep every assertion; only the argument shape changed.
- **G2** — `backend/tests/test_provider_conformance.py` (new): protocol signature; `FakeProvider` all four modes **through `router.execute`** (never the method directly); `FakeProvider` signature; `ScriptedProvider` called directly; `OpenCodeGoProvider` **signature-only** via `inspect.signature` (no instance, no key, no call, no network); `planning/service.py` excluded by assertion. FAIL-then-PASS raw in `SG-056_verify.log` V1/V2, both committed.
- **G3** — backend suite, ruff, mypy, frontend suite, eslint, `tsc && vite build` — see §5.
- **G4** — rebuilt + redeployed + on-box smoke against the **deployed** container — see §6.
- **G5** — this file, `SG-056.log`, `SG-056_verify.log`.

## 5. Tests / FAIL-then-PASS (`PG-EV-01`, `PG-EV-09`, `PG-EV-02`, `PG-EV-05`)

Raw runs committed to `SG-056_verify.log`.

- **FAIL-first (new rail, pre-hunk code), V1:** `6 failed, 3 passed in 0.29s`, exit 1. The six failures are exactly the drift:
  - `test_protocol_declares_the_3arg_surface` — `['image_ref']` vs `['image_bytes','prompt']`;
  - 4 × `test_fake_provider_accepts_3arg_surface_through_router` — the live crash quoted at `router.py:67`:
    `TypeError: FakeProvider.extract_items() takes 2 positional arguments but 3 were given`;
  - `test_fake_provider_signature_accepts_keyword_estimated_cost` — `['image_ref']`.
  Passing pre-hunk (correctly): `ScriptedProvider` direct, `OpenCodeGoProvider` signature-only, planning-exclusion.
- **GREEN (post-hunk), V2:** `9 passed in 0.25s`, exit 0.
- **Backend suite post-hunk, V3:** `2 failed, 235 passed in 15.15s`. Both reds are **BASE-proven pre-existing** (V4, BASE worktree `8f9847f`): `tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `::test_ocr_has_text_boxes_and_mean_confidence` fail identically at BASE (`2 failed, 5 passed in 2.80s`) — barcode/OCR environment, nothing to do with providers. `mypy app` reports `41 errors in 9 files` **at BASE too**; no error is in a changed file (changed files: `fake.py`, `protocols.py`, two tests). These are cited base+command+output, not new findings.
- **Lint, V5:** `ruff check .` → `All checks passed!` exit 0. **Frontend, V6:** `152 passed (21 files)` exit 0; `eslint src` exit 0; `tsc && vite build` exit 0 (`dist/assets/index-DgwxPRqe.js`, 293.57 kB).
- **Properties, not commands (`PG-EV-05`):** (a) "the fake accepts the 3-arg surface **through the router**" — proven by calling `router.execute` for all four modes; (b) "the fake output is **still schema-invalid**" — V9 smoke parses it and gets the designed `ValidationError`; (c) "no other provider file touched" — the diff touches only `fake.py`/`protocols.py` under `providers/`.
- **Vacuity check:** none. The rail exercises the function (a hit counter is not needed because the pre-hunk run actually raised the TypeError). The `ScriptedProvider` and `OpenCodeGoProvider` checks passed pre-hunk by design and become regression guards; that is stated, not passed off as fail-first. The signature helper strips a leading `self` only when present.

## 6. Live deploy + on-box smoke (`PG-PR-04`, `PG-PR-06`, `PG-DP-02`)

Raw before/after in `SG-056_verify.log` V7–V9.

**BEFORE (V7):** container `342513af7fcc`, image `sha256:fe509cf0519909fca2a3256689988353466bcf20b3f2b9a61825436b92f5da54`, health `healthy`, restart 0, publish `127.0.0.1:8003`, health `{"status":"ok","db":"ok","storage":"ok"}`.

**REBUILD (V8):** `BUILDX_CONFIG=/run/user/1000/sg056-buildx docker compose build backend` → exit 0 in 13 s. The `BUILDX_CONFIG` relocation is the same sandbox adaptation SG-054 `F-SG054-3` documented (dispatch sandbox makes `~/.docker` read-only; same rootless daemon, no sudo, no privilege sought). New image digest `sha256:d2f19cf510185022b828bd718568a9f5a945573feaa3fe6d21f32849e7c7f485`.

**UP (V9):** `docker compose up -d backend` recreated `342513af7fcc → 54d97025e74d367c47cee353bd3d873e3020ed68cea30aa3d40f5ea72dcf0bc8`; health became `healthy` in <20 s. Idempotent re-`up -d` → `Container … Running`, **same container**, `RestartCount=0`. Health exact; `8000/tcp -> 127.0.0.1:8003` (loopback-only).

**SMOKE (V9), no production writes:** `docker exec -i storagegenie-backend-1 python -` built a `ProviderRouter` over `reader.provider_registry()["fake"]` and called

```
router.execute("extract_items", b"smoke", "smoke", estimated_cost=0.0)
```

→ returned `ProviderResult` with `normalized_output = {'needs_evidence': False, 'items': [{'name': 'fake-item', 'source': b'smoke'}]}` (call **SUCCEEDED**), then `parse_extraction_output(result.normalized_output)` → `ValidationError: 3 validation errors for ExtractionOutput` — the designed SG-028 downstream rejection. **Never a TypeError.** No `Session` was constructed anywhere in the smoke, so zero rows were written (the production SQLite was not opened). A full live end-to-end import is out of scope (would write prod rows without production-write authority, `PG-EV-06`). Full sweep **waived** per `PG-DP-02`; substitute = the G2 conformance rail + this deployed-container smoke.

## 7. Findings / disagreements

- **F-SG056-1 (packet premise imprecision — headline).** The packet states the write path is "pure `*args` passthrough". It is not: `estimated_cost` is a **keyword-only parameter of `execute` itself** (`router.py:52`) and is consumed by the pre-call budget check; `router.py:67` forwards only `*args, **kwargs`, so the provider never sees `estimated_cost` through the router. The reader supplies the estimate to the router (which enforces `cost_budget`), but `OpenCodeGoProvider`'s own `per_job_cap`/`monthly_cap` guard (`opencode_go.py:242-253`) then always compares against `0.0` — the adapter-level cap is unreachable via the reader. This does **not** change the fix (the fake still needed the two positional parameters) and the router is outside the ceiling, so it was **not** modified. Reported because "correcting me is worth more than agreeing": the router is a budget consumer, not a transparent passthrough, and the adapter cap has a latent dead path.
- **F-SG056-2 (pre-existing, proven at BASE — not ours).** `tests/test_signals.py` barcode + OCR (2 failures) and `mypy app` (41 errors in 9 files) reproduce at BASE `8f9847f`; none in a changed file. Destinations unchanged; only base-proven reds permitted.
- **F-SG056-3 (environment/doc discrepancy).** This host has no `.rules-cache/`, and `/opt/storagegenie-dispatch/` holds only `dispatch_coder.sh` (+`.bak`) and `finalize_dispatch_report.sh` — no `CODER.md`, `VERSION`, or `RULES.sha256`. The `AGENTS.md` G-L1 session-start version ritual cannot run as written here; the packet's contract-0.27.0 statement is the only version source. Reported, not routed around.
- **F-SG056-4 (PG-SC-09, name-the-world).** World where the conformance rail passes yet the live crash persists: **(a)** a fourth caller (or a newly added provider implementation) uses a different shape and is never added to the rail — the rail enumerates today's three implementations plus the protocol; it does not AST-scan the tree for new defs; **(b)** a stale container still runs pre-deploy code. Why the slice still ships: **(b)** is closed by the G4 smoke, which ran against the **deployed** post-rebuild container (`54d97025`, image `d2f19cf5…`), not local code; **(a)** is a named limitation, mitigated for the present tree by §3's full enumeration (all production defs are conformant after the fix). A future provider file must be added to `test_provider_conformance.py`; that is the rail's known edge.

## 8. Guards invoked (0.27.0) — evidence

| Guard | Status |
|---|---|
| `PG-SC-01` read-both-paths | MET — write path `router.py:52-72` and read path `reader.py:308-310` read and quoted; one premise corrected (F-SG056-1). |
| `PG-EV-01` gate-seen-failing | MET — the new rail failed pre-hunk (6 reds, TypeError quoted); green post-hunk. |
| `PG-EV-02` artifact-not-command | MET — parsed `ValidationError`, provider `normalized_output`, container/image IDs, committed raw logs; no bare exit code. |
| `PG-EV-05` property-not-command | MET — three properties named in §5, each exercised. |
| `PG-EV-09` both-runs-committed | MET — RED and GREEN raw committed (`SG-056_verify.log` V1/V2). |
| `PG-SC-09` name-the-world | MET — F-SG056-4. |
| `PG-SC-10` no-ignored-commit | MET — only the ceiling files staged; `.cache/`, `data/`, `.env`, `venv/` stay ignored (`git status` clean after commit). |
| `PG-IC-01` cross-product | MET — G-hunks share no condition with any remediation step; no blanket exclusion issued; stops win (`PG-IC-03`, none triggered). |
| `PG-IC-03` stop-wins | MET — no stop occurred; the only candidate (F-SG056-1) is outside the ceiling and non-blocking. |
| `PG-IC-07` no-fixed-dates | MET — only the header authoring date; all clocks are live `date -u` readings. |
| `PG-IC-09` premises-live | MET — every premise re-read live and quoted in §2. |
| `PG-PR-03` denied-is-stop | MET — no privileged operation was denied; no privilege sought. |
| `PG-PR-04` code-becomes-live | MET — rebuild + `up -d`; container and image digests changed; smoke ran in the deployed container. |
| `PG-PR-06` runtime-vs-budget | MET — every leg under its stated bound; no command killed. |
| `PG-DP-02` no-sweep-waiver | MET — full sweep waived with substitute named (G2 rail + G4 smoke). |

## 9. Acceptance criteria

- [x] Starting tree clean and quoted; premises re-verified with quoted reads (`reader.py:309`, `router.py:52-72`, `fake.py:52+104`, `opencode_go.py:235-241`, `protocols.py:29`, six test-double defs).
- [x] Provider enumeration with diff vs expectation either way (§3); no hunk outside the ceiling.
- [x] FAIL-then-PASS honest: pre-hunk RED (TypeError quoted) + post-hunk GREEN, both raw committed; on-box smoke against the deployed container quoted (call succeeds, downstream `ValidationError`, never TypeError).
- [x] Suite + lint + build green (only BASE-proven reds); secret scan 0; no migration; dep list unchanged; prod DB untouched (smoke constructs no Session); no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## 10. Budget (actual vs cap, per leg, units)

| Leg | Actual | Cap |
|---|---|---|
| Conformance red / green | 0.29 s / 0.25 s | 600 s (suite+lint+build) |
| Backend suite (post-hunk) | 15.15 s | 600 s |
| ruff / mypy | 0 s / 2 s | 600 s |
| Frontend test / lint / build | 6 s / 2 s / 4 s | 600 s |
| BASE proof (test_signals + mypy) | ~3 s | — |
| Host build / up / re-up / smoke | 13 s / 2 s / 1 s / <1 s | 900 s |
| Overall wall-clock | ~5 min (frozen at commit) | 2400 s (early-close 1500 s) |

No command was killed. Real metered spend: `$0.000000` actual vs `$0` bound (zero provider calls).

## 11. Receipt note (M20-corrected block)

Work is pushed to `automation` with the worktree clean (`CO-55`). **No** push to `storagegenie-evidence`, **no** `{{RECEIPT_CMD}}`. A note is added on WORK_HEAD under `refs/notes/storagegenie-coder-reports` with first line `Dispatch-ID: SG-056 | Report: docs/worklogs/SG-056_report.md | Work-HEAD: <hash>` (`CO-97`), then pushed, then verified against the **explicitly fetched** refspec mapped to a local name (default fetch never carries notes), by listing the note contents, grepping for `SG-056`, and `git notes --ref=… show <WORK_HEAD>`. The executed output is pasted verbatim in the **follow-up docs-only commit** appended below (a file inside the noted commit cannot contain its own note's `show` output). `note=yes`.


### 11.1 Receipt verification — executed output pasted verbatim (docs-only follow-up commit)

Noted WORK_HEAD = `6456497788720941ba1f35becbe2a41ba4478729`; the note cannot contain its own `show` output, so the raw run below is committed by a docs-only follow-up (no code/hunk change). Command sequence and output:

```
=== [FETCH notes ref into MAPPED local name] 2026-09-17T12:28:49Z ===
From github.com:Andovol/StorageGenie
   dee4654..c780487  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-verify
fetch_exit=0
=== [LIST fetched note objects] ===
91a7b8aafd7c41f24c184f8d3b7638f4e9a7cbaf 009bf1145b9ace5f2b73ba7451bc2e9b5e5ba76b
e985c99c0b12e0596a8d5bf83d04ade84746c95d 0be0315020544c83aff2fb3dec066f0ac68789bb
e324a572c55b60812bbeaf1fc8bb4a16938d3c31 0c3b5702a7fede00cb939b88aa605fdd766b9062
19d0b0ba721fc6bcbedce67a6e703ee29b15aa2d 0c6100f5081d04f0e15f38d69d53132875b64d12
5ba54eebf0593388f1495b0676439acb0fb6ef04 174206cd1c7ac7bc2c4758255b20c164f753f6a3
501f7107ed6f3950820550f60c63db361fa24eb6 1932f8ac27fca0ffd614e4fa83d1b70a946d3416
f3e3436d358d684f358c464024e97fb454e6c3fd 1dc63ec26cc531ca88c36f7d240f7b5354fdfb8f
4479859e706a15e0b5975d3f365e8ef5ada062f6 1e0f5b3d8935c455d9c0c9dba5657eb97e3a9ae2
5654e125af5787c80a78d5293f8ac4c3dc5744b6 203d97dafb1022797b2693e0b038cb40ab6046f9
ad81baf5636a5ede0da009fc39d2627eaa89b9ea 212cb1c2a982a3afcc7c177cf618349af17f3790
edb884074789127baef9108a903ef24692a3f182 275a62626a0b7d5dfd960b775175ded71b631ad4
9b1523c85913d28b7e910b0ab5bc6ed0eb2eb017 307ae8c8698a2950fe22d8f7f04d67be30b16f8f
ff5def7e81de4cf7f6a52e2b97a2862e01d07e89 32363ac426cb37ed998846421748c60de3e3fe8b
e78764bf2ccb2cc9e1d71744665fb36d028c377b 3993c369dd8bffd1ecd7f8bd4ae96f9cda726e80
91a9f4bd1f4e3c626cdcd2562c96ac4895d8c266 40ae5e875cf76840d40aebf7a1a3f86d1bd11af9
b9eb80919fb3547ea77c58182abcc1690c545375 450c85024299fdf57aecf12cbb263ca780b064f7
99cb1b087b2d00313a138dd61c1b1066e25a7ece 4ad3ff18bb64c9e69571e4f41aa6e9f7006aae2c
d5b35b568859b2dbf2bb2479c6765ac77e5cad20 53abefeb2813f3f8d18a7f32ba9a994d1bb796fe
8251a17c5002ae44bdab408ab209bf47b9d79471 5429556ef0ce94d10a481e2eba7b2d3e66edb2ff
11f0fdeb531eb70c3818d4a5a024531acfc5db03 5a744adee8c74d4f698c372348e135275ecac97f
15c98f9c87b042776818cda7e37c47f44c3b94aa 5d61d43b2708813e25ddca0772da1d43e6021f36
2a3805ebf5433cb0747e6b155ef93e4328b07f2c 6419c9e1c5e1958b64115842ab0dd690abb451b3
5cfaf7d6516f74c5559219fdc49df97bfce59201 6456497788720941ba1f35becbe2a41ba4478729
2c56f9d9f0eb62e3c11b409f377da70fcdd50fa7 649cedffa1bc86baee5a89ade770acd147db472a
ed112e6a589185a8bfba7374b0e383c579eb4504 655f75a272aad918e6a2f68c54c910deb472a837
67f26aa234d703d632394f3536bf5c30dbe14b9d 6a07c62be63248e7a001176f81af8f11c201931d
54314465c7b868a11e20dceb22098ee8ca180f8c 70e19437c8a8602388b541ee23aa0a4c70f1efee
4bac342b1a47e33b8da2f77a8286d36f2af234f8 82312ef1c15639d953df1f70c3c594560affd2eb
784ed63becac452053491cc37186cae73a6bc556 8715d4e5592f52de81b45efe03081c788a02ecca
a7c1feb5c2c24e88cfc8aad144cf09b254497861 9a5f5623cdc1de141dd8fdb9bdbc172757efb6b8
d88e43b7b785afd2a81a1c46ee25ed9d75f5f56f 9e91363efc87c982fda0ab949d9b0f188823aa38
cb63bd217e9d9d50e615ba9856022bd51a9b51db a10083f7f0cb873610322ce2f8f9f774cc733897
8b896e67eea8b5da7434d9d5e3e62f992e704d7e a2e1f5c972f5ff95b33dfc25be54c4c2de4bc0d0
260751cdfbd71dc753bf6af447f9c4fbc90a4bac a8c3958527fe4df5e68e61199af9ecc7b718eb81
6cca52d11ba54516d4babecda22502d73f457dc7 a94397d0d09ce086fba45d37eda8b34c2420cf2d
1799e705207becceb214a7dc07fe9cf4e9dce251 aeda142dbfbffc3ff3b2509ef7ea0c87de474065
dc32d32d275b272347bfc8295c98cf86b0a4378e b2b9c9383e02ca45e0f8ecf955b3ead11ab8e2e4
fe1c330e993913b2f1d393c8823940aef068f618 b3f73e59985fabeb22737751e83d1fd6998a411b
238c1d3703cd931813b347cec426250621dfbdd5 b4dcdc8aa791ca5180b7649a31ecf107f1e1ffb1
799625af24b22cd2db582957186101e826448a6e b7bd8635372e98bb12138ecdd837047bef16b533
f853faa89f89245c78cf1b6fb5294cb7ae85622c b8eee6c0f84db2378f66d269e49952085e8616c4
8ea66122dbbe9e4e8b091ec3132e032251dc3c21 ca70574ac2a1e092fa9a1514234700059cb8bd54
011256ac94ffb0e8ed70fb01ce0e2f2a5bf82041 d0f022593b2ea640c04d6eec989701d6c66adb86
67fe15eca62a1222a994ae39a07f0aa3fbfe0bbe d25257a94e1edb2a5b007942c4686d3c82cd4b1f
c326309242ead9b10ebcf30e83cd6d71e2a957b4 d70b6f7e9db91d5eb4d37fcd2dfb39170d20f91a
c8d4729c46530a180d0b4f8ca73becdc3d44a591 dafac6ce841b87da1415b0fffc176af37504e293
4a43dc0fb81b0985cd569dfaab6f8c913e05853b e060f6c29569d6b043be35e2b879d1eeb6245168
04915f43f950541e6cdc67eba1dbefa30d65b77f e0b5362236f0f90118503beabf84f8f2edd32172
917d322082567b459f36ed2b5190238c103b8d1b e9f83797d7e5e854ab0a3b75b832ed9c2f46ccd6
a6ed9780b5bdde70f5d334fa6b90e56d4147d914 ed7abc691dd375efd3247a41fcfcf0d2b811aa06
65883d817a9da858a530384e62a1715db18b8aeb edf3cdcd3832675b2ea3f7a5302a5ff21888e080
710be4a7419123d626013f014cceab5d769c582e f0071bafb8572348a7d46fe703fc5079fcf585b7
11e2f16eafb775fd531843984a13c9671d843d0d f0709f7224f8f040967f2716070204d0e154bdfa
888ae91b110750e77c9ec15825746de5b07cdb4b fefe3eb42e60410d4e1e206348da822f5e8a715c
=== [GREP note bodies for SG-056] ===
30:Dispatch-ID: SG-056 | Report: docs/worklogs/SG-056_report.md | Work-HEAD: 6456497788720941ba1f35becbe2a41ba4478729
grep_exit=0
=== [SHOW note on WORK_HEAD from the fetched ref] ===
Dispatch-ID: SG-056 | Report: docs/worklogs/SG-056_report.md | Work-HEAD: 6456497788720941ba1f35becbe2a41ba4478729
show_exit=0
```

Verified: `fetch_exit=0`, the note body was listed and grepped (`grep_exit=0`, hit at line 30 of concatenated notes), and `git notes --ref=refs/notes/storagegenie-coder-reports-verify show 6456497788720941ba1f35becbe2a41ba4478729` printed the first line carrying BOTH `Dispatch-ID: SG-056` and `Report: docs/worklogs/SG-056_report.md` (`CO-97`). `note=yes`.
