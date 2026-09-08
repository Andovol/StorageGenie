# ADR-005: Versioned, isolated plugin contract

Status: accepted for Phase 1 · SG-015

## Decision

Plugins are registered by an exact `plugin_id` and semantic version. The
registry stores the implementation at `backend/app/plugins/registry.py:17-31`
and rejects an unknown id or a requested version other than the registered
version at `backend/app/plugins/registry.py:34-42`. The Expiry Tracker is the
only registered built-in, at `backend/app/plugins/registry.py:45-48`, and is
`expiry-tracker` version `1.0.0` (`backend/app/plugins/expiry_tracker.py:26-31`).

Plugin HTTP operations are additive and namespaced. The router prefix and all
classification, expiry, and extension routes are in
`backend/app/api/v1/plugins.py:19,66-199`; mounting is explicit in
`backend/app/main.py:13,57`. No core route is overridden.

Classification and extension values reuse the core `assertion` table under the
reserved `plugin:expiry-tracker/` field prefix
(`backend/app/plugins/expiry_tracker.py:28-31`). This avoids a migration in
this skeleton while preserving core assertion provenance, review state, and
asset ownership. `backend/app/plugins/expiry_tracker.py:280-314` supersedes
the prior plugin assertion and writes the new source and review state
explicitly.

The plugin owns taxonomy/profile data, enums, and a JSON-Schema-shaped data
contract at `backend/app/plugins/expiry_tracker.py:34-152`. The validator at
`backend/app/plugins/expiry_tracker.py:198-219` rejects unknown properties,
invalid enum values, wrong types, and all four core-field names
(`identifier`, `condition`, `location`, `status`) at lines 201-205. Core fields
remain owned by the generic asset API.

## Second-plugin contract

A second plugin must:

1. define a stable id/version and implementation module, then call
   `register_plugin` (`backend/app/plugins/registry.py:27-31`);
2. define its taxonomy, behavior profile, enums, and extension schema without
   mutating core fields (`backend/app/plugins/expiry_tracker.py:62-152` is the
   reference shape);
3. use its own namespaced router mounted from `backend/app/main.py:48-57`;
4. validate its payloads before writing and use explicit assertion provenance
   and review states, following `backend/app/plugins/expiry_tracker.py:280-314`;
5. prove a write-to-namespaced-GET round trip and household isolation in its
   tests, following `backend/tests/test_plugin_expiry.py:67-98`.

Prompt fragments, agents, provider calls, and marketplace behavior are not
part of this Phase 1 contract. AI extraction remains a Phase 2 concern.
