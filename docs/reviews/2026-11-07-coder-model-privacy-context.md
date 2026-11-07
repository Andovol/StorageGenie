# Second-opinion context pack — which Coder model may read the live host and the owner's data

**Prepared by:** the Architect, 2026-11-07. **Committed before Phase A runs** (`AGENTS.md`: every 🟠 or 🔴 item, and a 🟡 on the owner's data or the live host, goes through the two-phase review).
**Decision:** which model builds the next slices, SG-286 (recovery image on the live host), SG-287 (deploy rider on the live database) and SG-271 (code).
**Why it matters now:** contract 0.58.0, adopted today, states that the provider of the model the owner chose trains on what that model reads. The next slice reads the live container's configuration, which holds the app's secrets.

## The problem in plain words

The owner chose Muse 1.3 Contributor for builder slices. The shared contract now says Muse's provider trains on its prompts and completions, and makes a different model the default for any lane holding a `.env` file or personal data. This lane holds both. Anything a Muse run reads, including command output, may become training data, and that cannot be undone.

## The evidence, verbatim

**Contract 0.58.0 (in this lane at `.contract/`; the Architect's copy is `.rules-cache/`), `CODERS.md:96-97`:**

> **THE CODER ROTATION — EVERY LANE'S DEFAULT (`D577`, `D580`).** Slots, in order: `opencode-go/muse-spark-1.3-contributor` `xhigh` · `opencode-go/claude-haiku-5-5` `high` … **A lane whose `ROOT/.env` exists, or whose filing declares personal data, defaults to Haiku `high` and skips the Muse slot, because the provider trains on Muse's prompts and completions (`D594`). A slice command may still name Muse.** A project's owner may set another list, each slot in the catalogue.

**Contract 0.58.0 (in this lane at `.contract/`; the Architect's copy is `.rules-cache/`), `SECOND_OPINION.md:39`:** *"never Muse 1.3, which trains on what it reads, unless the project's owner chooses it (`D597`)"*.

**Owner, `AGENTS.md` Configuration table, Model policy, 2026-11-02:** *"Lets use Muse 1.3 Contributor on xhigh for the next Coder slices."* Repeated in the owner's session prompt, 2026-11-07: *"then SG-271, on Muse 1.3 Contributor at xhigh (AGENTS.md)."*

**The lane holds a `.env` and personal data:** `docker-compose.yml:17-18` loads `env_file: .env` into the backend; `AGENTS.md` Sensitive areas names the stored photos and files and the app database. `UNVERIFIED — inference:` the host checkout has `.env`, since the live app starts under that compose file.

**What the next slices touch (D23, owner-approved):** SG-286 inspects the live container, including its configuration (environment values, compared by hash only in the plan); SG-287 copies the live database to scratch and checks it by counts, hashes and schema text; SG-271 changes code and tests.

**History:** every SG slice before today ran on Muse or earlier models (`docs/ratings.md`). Haiku 5.5 has never run on this lane. Contract: Haiku `max` fails within seconds; `high` runs through an engine override (`CODERS.md:97`).

## Where it lives

| Thing | File |
|---|---|
| The rule | `.contract/CODERS.md` § Coder rotation; `.contract/SECOND_OPINION.md` § The reviewer |
| The models the lane accepts | `.contract/coder_models.tsv` |
| The owner's choice | `AGENTS.md`, Configuration table, Model policy |
| What the next slices read | `docs/reviews/2026-11-07-recovery-image-context.md`; `docs/packets/SG-280-deploy-rider-candidate-state-migration.md`; `docker-compose.yml`; `backend/app/config.py` |
| Past slice quality per model | `docs/ratings.md` |

**Do not read `STATE.md` or `docs/decisions/`.** They carry the Architect's view.

## What binds it

- **Model and provider choices are the owner's** (`AGENTS.md`; a standing owner decision).
- D23 is decided and not reopened: what SG-286 and SG-287 do.
- The owner's photos, files, database, the dispatch key and the host are sensitive areas (`AGENTS.md`).

## The options as I see them, without a pick

| Option | What happens |
|---|---|
| **C1 Muse everywhere** | As the owner said. Packets forbid printing environment values or owner data. |
| **C2 Haiku 5.5 `high` everywhere** | The lane's new default. A model never measured on this lane. |
| **C3 Split by what the slice reads** | Haiku for slices on the live host or the owner's data (SG-286, SG-287 and every rider); Muse for slices that read only the repository's code. |

**Q1 — the pick.** **Q2 —** can a packet instruction alone keep secrets and owner data out of a model's context, given that the Coder runs shell commands on a host holding them? **Q3 —** does a code-only slice on this lane really read nothing private?

## What would make the whole approach wrong

Name it if the training claim does not apply to this account's use, if Haiku 5.5 `high` cannot run on this lane, or if the repository itself already holds owner data a code slice would read.
