# Enrich — worked Jina request example (SG-097)

Names only. This example carries **no key value**: the `Authorization` header is
added at send time by `authorize()` and is never part of the builder's output,
a snapshot, a log line, or this file.

The request below is exactly what
`backend/app/services/enrich/jina.py:build_jina_request(name, brand)` builds for
brand `Jacobs` and name `Jacobs Cronat Gold`. The EU base is the default
(`JINA_EU_BASE_URL`); the global base (`JINA_GLOBAL_BASE_URL`) is a named
constant only and is never switched to silently.

```
GET https://eu.s.jina.ai/Jacobs+Jacobs+Cronat+Gold?site=mega-image.ro&site=emag.ro&site=farmaciatei.ro&num=5&type=web&gl=ro
```

Query (`site` is repeated; the values are the three researched Romanian retail
domains in `SITE_FILTERS`):

| Parameter | Value(s) |
|---|---|
| `site` | `mega-image.ro`, `emag.ro`, `farmaciatei.ro` |
| `num` | `5` (`JINA_NUM`) |
| `type` | `web` (`JINA_TYPE`) |
| `gl` | `ro` (`JINA_GL`) |

Headers (names and values as built; the key is not one of them):

| Header | Value |
|---|---|
| `Accept` | `application/json` |
| `X-Token-Budget` | `6000` (`TOKEN_BUDGET`) |
| `X-Timeout` | `15` (`PAGE_TIMEOUT`) |
| `X-Respond-With` | `content` (`RESPOND_WITH`) |

At send time the client resolves the key (explicit argument → `Settings.jina_api_key`
→ `JINA_API_KEY` environment) and calls `authorize(headers, key)`, which adds
`Authorization: Bearer <key>`. A missing key degrades to a loud `missing_key:`
snapshot with **zero sends**; the request is never sent unauthenticated.

`backend/tests/test_sg082_enrich_jina.py::test_worked_example_artifact_matches_the_real_driver`
asserts that the URL line above equals the request the real driver builds, derived
from the real module constants (`PG-SC-12`).
