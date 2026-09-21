# AI Ingestion + Web Enrichment — design (approved 2026-09-21)

Owner direction: photo ingest derives the category and fuller product properties; every
product page gains an **Enrich** button that searches the web (photo of a soup can →
ingredients, manufacturer, as much as found). All web data is **proposed, never
auto-accepted**. Architecture: hybrid (option C). Source policy under separate owner
research (not decided here).

## 1. Property model

One extended schema feeds photo ingest and Enrich alike: identity (brand, product,
variant, size), codes (barcode, lot/batch), dates (expiry, best-before, manufacture,
opened), quantity/unit, category (taxonomy descriptor ids), verbatim label transcript
(evidence only, never a fact), care (storage, warnings, allergens), nutrition (per 100g
+ serving). Every field carries `source` (`photo` / `web:<source>` / `manual`), snapshot
version, review state. Web snapshots are versioned rows, never overwrites. Corrections
remembered per product.

## 2. Photo ingest

Same pipeline, wider schema: frozen extraction prompt v3 (fail-then-pass on the
corpus), transcript stored as evidence, split-first multi-item, category as a proposed
field. Consent gate, ledger, candidate flow unchanged. Nothing auto-accepts.

## 3. Enrich service (new, fetch-only)

Manual button per product. Barcode/name query → raw response snapshotted verbatim →
mapped to proposed candidates (`source_type=web:<source>`). Barcode-exact links
identity; fuzzy matches arrive as proposals. Spend shown on the button under a
per-press cap. Sends identifiers only, never photos, never GPS.

## 4. Review lifecycle

Web proposals land in the existing candidate UI, per-field accept. Conflicts:
label photo wins for label-visible facts, web fills gaps; both stay visible with
sources. Snapshots versioned, refresh manual. No new review UX.

## 5. Cost / privacy / safety

Consent-gated, ledgered provider spend; monthly ledger as today. Human confirmation
mandatory throughout (standing guardrail rule). Nothing outside the house except
identifiers to the researched sources.

## 6. Testing

Corpus fail-then-pass for the extended schema; scripted-provider tests for
fetch/mapping/snapshot/conflict rules; at most one metered live leg; full suites
green; secret scan 0.

## Decisions recorded

web-proposed (a) · all eight property groups · transcribe+derive · split-first ·
manual-only trigger · exact-first/fuzzy-as-proposal · label-wins-visible ·
shown+capped spend · per-product corrections · versioned snapshots, manual refresh ·
identifiers-only privacy · hybrid architecture (C).
