# ADR-009: Expiry Tracker taxonomy and manual-entry doctrine

Status: accepted for Phase 1 · SG-015

## Decision

The first active categories are Food & beverages and Medicine/pharma, with
canonical slugs and profiles defined at
`backend/app/plugins/expiry_tracker.py:93-110`. Food resolves the explicit
upcoming/urgent/critical defaults 30/7/1 days at lines 93-97. Medicine uses
the shorter 14/3/1-day profile at lines 98-102. The selected tier and all
defaults are returned by `Category.profile` at lines 72-90 and are asserted by
`backend/tests/test_plugin_expiry.py:82-93`.

Cosmetics/personal care, Household chemicals, and Documents/other are present
in the taxonomy but inactive until Phase 3, with the phase marker stored at
`backend/app/plugins/expiry_tracker.py:111-119` and the 422 behavior enforced
at lines 168-180 and tested at `backend/tests/test_plugin_expiry.py:78-98`.
Non-perishable is an explicit no-expiry category at
`backend/app/plugins/expiry_tracker.py:120`; its classification creates no
expiry assertion and manual entry rejects it, as proved at
`backend/tests/test_plugin_expiry.py:211-225`.

Date types and units are plugin enums at
`backend/app/plugins/expiry_tracker.py:34-52`. Manual input is strictly
ISO-8601 calendar text and validates date type and optional unit at
`backend/app/plugins/expiry_tracker.py:222-238`; invalid enum writes are
tested at `backend/tests/test_plugin_expiry.py:192-208`.

## Manual-entry doctrine

The plugin never fabricates a resolved date. It contains no `today`, `now`, or
`timedelta` call; its module-level statement at
`backend/app/plugins/expiry_tracker.py:1-5` makes the boundary explicit. If
an active perishable asset has no date-bearing observation, classification
writes an explicit `needs_evidence` assertion and an open manual-entry task
at `backend/app/plugins/expiry_tracker.py:351-357`. The test proves the
absence of an accepted/resolved assertion before entry and the real task at
`backend/tests/test_plugin_expiry.py:147-189`.

Manual entry supersedes the unresolved assertion, writes a user-sourced
`accepted` assertion, links supplied evidence ids, and resolves the open task
at `backend/app/plugins/expiry_tracker.py:382-410`; the read-back and source
link are asserted at `backend/tests/test_plugin_expiry.py:176-189`.

## Deferred behavior

Opened-date/period-after-opening countdown behavior is deliberately disabled
in the profile (`opened_date_tracking: false`,
`backend/app/plugins/expiry_tracker.py:84-89`). Cosmetics interaction,
dashboard/notification UI, agents, web enrichment, prompt fragments, and
provider-backed extraction remain later-phase work. This slice provides only
the deterministic taxonomy, validated extension data, review fallback, and
manual resolution route (`backend/app/api/v1/plugins.py:107-149`).
