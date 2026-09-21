# Enrich source research (owner, 2026-09-21)

Provenance: owner chat message 2026-09-21 (verbatim below, formatting preserved). This satisfies D102's gate
("no Enrich packet until owner source research names the web sources"). Design spec
`docs/superpowers/specs/2026-09-21-ai-ingestion-enrichment-design.md` §7 ("source policy under separate owner
research") is now decided as: **OFF primary (food) → Jina fallback (non-food + OFF misses, Romanian retail
domains, EU endpoint option) → Google Vision Web Detection rare fallback (EXCLUDED from the Enrich stage per
D108 — see STATE; conflicts with the D83 one-provider rule).**

--- owner text begins ---

#### The baseline “Enrich” architecture is viable and stays low‑complexity/low‑cost if you lean on OFF for structured food data, Jina for targeted web retail pages, and use Google Vision Web Detection only as a rare fallback. You’ll need clear query construction and a deterministic scoring layer to pick a single product record when OFF returns multiple hits. [openfoodfacts.github](https://openfoodfacts.github.io/openfoodfacts-server/api/tutorial-off-api/)
***

## High‑level architecture evaluation

- **Multimodal LLM first, Cloud Vision second**: Using a multimodal LLM to read packaging and only calling Google Vision `WEB_DETECTION` when OCR confidence is low keeps GCP spend down and simplifies image handling. [docs.cloud.google](https://docs.cloud.google.com/vision/docs/detecting-web)
- **OFF v2 search as primary product DB**: OFF’s `/api/v2/search` exposes faceted search with `search_terms`, `brands_tags`, `countries_tags_en`, and `fields` filters, which you can exploit with brand+name text queries and country scoping. [apis](https://apis.io/apis/open-food-facts/open-food-facts-search-api/)
- **Jina Search (`s.jina.ai`) for non‑food & OFF misses**: Jina’s Search API returns LLM‑ready summaries of top web results and supports domain filtering via `site` plus token budget headers, which is ideal for hitting Romanian retailers like Mega Image, eMAG, or local pharmacies. [github](https://github.com/jina-ai/reader)
- **Single LLM synthesis pass**: One final LLM call over OFF JSON + Jina content + LLM’s own visual/OCR outputs can reliably normalize to your JSON schema with explicit source attribution (URL + retrieval date).

***

## 1. API contracts & integration specs

### Open Food Facts Search API

**Endpoint (v2 structured search)**  
- `GET https://world.openfoodfacts.org/api/v2/search` [openfoodfacts.github](https://openfoodfacts.github.io/openfoodfacts-server/api/)

**Key parameters for text‑based brand+name search scoped to Romania/EU**

OFF’s v2 search supports: [wiki.openfoodfacts](https://wiki.openfoodfacts.org/Open_Food_Facts_Search_API_Version_2)

- `search_terms`: free‑text query (name + brand); used by newer deployments and documented in their OpenAPI spec and examples. [zingu](https://zingu.ai/endpoints/openfoodfacts.org:open-food-facts-api:GET:_api_v2_search)
- `brands_tags`: brand filter (taxonomy values, but plain brand strings also work). [openfoodfacts.github](https://openfoodfacts.github.io/documentation/docs/Product-Opener/v2/search/get-search/)
- `countries_tags_en`: country filter in English (e.g. `romania`, `france`, `italy`). [apis](https://apis.io/apis/open-food-facts/open-food-facts-search-api/)
- `page`, `page_size`: pagination; set `page_size` to a small number (e.g. 10) to limit candidates. [openfoodfacts.github](https://openfoodfacts.github.io/openfoodfacts-server/api/tutorial-off-api/)
- `fields`: comma‑separated list of fields to keep. [openfoodfacts.github](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-cheatsheet/)

A typical food search for a Romanian product:

```http
GET https://world.openfoodfacts.org/api/v2/search
  ?search_terms=Jacobs%20Cronat%20Gold
  &brands_tags=jacobs
  &countries_tags_en=romania
  &page=1
  &page_size=10
  &fields=code,product_name,brands,ingredients_text,nutriments,packaging,countries_tags_en
```

This returns a JSON object with keys like `count`, `page`, and `products` (list of product objects), each containing the requested fields. [wiki.openfoodfacts](https://wiki.openfoodfacts.org/Open_Food_Facts_Search_API_Version_2)

**Response fields to retain**

For your Enrich schema, you can restrict to: [wiki.openfoodfacts](https://wiki.openfoodfacts.org/API_Fields)

- `product_name` – display name.  
- `ingredients_text` – raw ingredients string.  
- `nutriments` – nested object with energy, fat, sugar, salt, etc., per 100 g/serving. [openfoodfacts.github](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-cheatsheet/)
- `packaging` – free‑text packaging description (often “Jar”, “Bottle”, “Plastic film” etc.). [openfoodfacts.github](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-cheatsheet/)
- Optionally `brands`, `code`, `countries_tags_en` for scoring and provenance. [wiki.openfoodfacts](https://wiki.openfoodfacts.org/API_Fields)

> Note: official docs state that v2 search is filter‑based and “full‑text search is not available”, but the v2 OpenAPI spec and Zingu example show `search_terms` is accepted and works in current deployments; treat `search_terms` + filters as best‑effort text search. [zingu](https://zingu.ai/endpoints/openfoodfacts.org:open-food-facts-api:GET:_api_v2_search)

***

### Jina Search (`s.jina.ai`)

**Base URL & methods**

- Basic GET search: `GET https://s.jina.ai/{urlencoded_query}`. [elastic](https://www.elastic.co/search-labs/tutorials/jina-tutorial/jina-reader)
- Search with JSON response: `GET https://s.jina.ai/{urlencoded_query}` with `Accept: application/json`. [clawhub](https://clawhub.ai/adhishthite/jina-ai)
- Search with POST body: `POST https://s.jina.ai/` with JSON `{"q": "...query..."}`. [github](https://github.com/jina-ai/meta-prompt/blob/main/v10.txt)
- EU‑only processing: `https://eu.s.jina.ai/` as base if you want EU data residency for all processing. [github](https://github.com/jina-ai/meta-prompt/blob/main/v10.txt)

**Query syntax**

- Simple query: `https://s.jina.ai/Jacobs+Cronat+Gold+instant+coffee`. [github](https://github.com/jina-ai/reader)
- With domain filters (in‑site search): `site` query param can be repeated to limit to specific domains: [clawhub](https://clawhub.ai/adhishthite/skills/jina-ai)

```http
GET https://s.jina.ai/Jacobs+Cronat+Gold+instant+coffee
  ?site=mega-image.ro
  &site=emag.ro
  &site=farmaciatei.ro
  &num=5
  &type=web
```

Supported query params include: [deepwiki](https://deepwiki.com/jina-ai/reader/1.2-api-reference)

- `site`: domain filter (can appear multiple times).  
- `num` / `count`: number of results (0–20).  
- `type`: `web`, `images`, or `news`.  
- `gl`: country code for localization (e.g. `ro`).  
- `filetype`, `intitle`, etc., for extra filtering.  

**Token optimization headers**

From Jina’s API reference: [jina](https://jina.ai/)

- `X-Token-Budget`: maximum tokens for the response.  
- `X-Timeout`: page load timeout (seconds).  
- `X-Respond-With`: output format, e.g. `markdown`, `content`, `no-content`.  
- `X-No-Cache`: bypass cached content if you suspect stale pages.  

Typical low‑cost call for downstream LLM use:

```http
GET https://s.jina.ai/Jacobs+Cronat+Gold+instant+coffee?site=mega-image.ro&site=emag.ro&num=5&type=web
Authorization: Bearer {JINA_API_KEY}
Accept: application/json
X-Token-Budget: 6000
X-Timeout: 15
X-Respond-With: content
```

JSON response is a list of up to 5 entries, each with `url`, `title`, `content`, and optionally `timestamp`. [jina](https://jina.ai/)

***

### Google Cloud Vision `WEB_DETECTION`

**Endpoint**

- `POST https://vision.googleapis.com/v1/images:annotate`. [cloud.google](https://cloud.google.com/vision/docs/detecting-web?hl=pt-br)

**Minimal payload for base64 image + Web Detection**

From the official docs: [docs.cloud.google](https://docs.cloud.google.com/vision/docs/internet-detection)

```json
{
  "requests": [
    {
      "image": {
        "content": "<BASE64_ENCODED_IMAGE_DATA>"
      },
      "features": [
        { "type": "WEB_DETECTION" }
      ]
    }
  ]
}
```

You send this with:

- `Authorization: Bearer {GCP_ACCESS_TOKEN}`  
- `x-goog-user-project: {PROJECT_ID}`  
- `Content-Type: application/json; charset=utf-8`. [docs.cloud.google](https://docs.cloud.google.com/vision/docs/detecting-web)

**Response fields to parse**

The `webDetection` annotation contains: [cloud.google](https://cloud.google.com/php/docs/reference/cloud-vision/latest/V1.WebDetection)

- `webEntities`: array of inferred entities (`description`, `score`) from similar images.  
- `pagesWithMatchingImages`: array of pages (`url`, `pageTitle`, `fullMatchingImages`, `partialMatchingImages`).  
- `fullMatchingImages`, `partialMatchingImages`, `visuallySimilarImages`: image URLs.  
- `bestGuessLabels`: text labels for the image.  

For Enrich, you mainly care about:

- Top `webEntities[*].description` as product name hints.  
- `pagesWithMatchingImages[*].url` as candidate retail pages for Jina or direct scraping.

***

## 2. Query construction & disambiguation strategy

### Vision LLM prompt for search‑optimized keywords

You want the multimodal LLM to produce structured, searchable fields: brand, product line, variant (flavor/scent), net weight/volume, and category. Example instruction (adapt for your model):

> You are parsing a photo of a retail product package to build search queries.  
>  
> Extract the following fields from the visible text and graphics, even if some are partial or approximate:  
> - `brand_guess`: the brand printed on the package (e.g., “Jacobs”, “Persil”, “Mega Image 365”).  
> - `line_guess`: product line or series (e.g., “Cronat Gold”, “K-Classic”, “Pilos”).  
> - `variant_guess`: flavor, scent, or specific variant (e.g., “Vanilla”, “Lemon Fresh”, “500 mg tablets”).  
> - `size_guess`: net weight or volume with unit (e.g., “250 g”, “1 L”, “30 tablets”).  
> - `category_guess`: one of {“food”, “beverage”, “household_cleaning”, “personal_care”, “otc_pharma”, “other”}.  
> - `canonical_query`: a single concise string for web/product search of the form:  
>   `[brand_guess] [line_guess] [variant_guess] [size_guess]`  
>  
> Rules:  
> - Ignore marketing slogans, health claims, and generic text (“new”, “extra fresh”, “super value”, etc.).  
> - Prefer the largest or most prominent brand text when multiple logos appear.  
> - If the brand is a private label (supermarket name or logo), use that as `brand_guess`.  
> - If weight/volume is missing, skip `size_guess` instead of guessing.  
> - Return strictly JSON with those keys and string values (lowercased except brand), with empty string for unknown values.

This gives you search‑ready strings while keeping the JSON small and deterministic.

### Heuristic for selecting the best OFF product match

When OFF’s `/api/v2/search` returns multiple candidates, implement a scoring function over each product in `products[]`: [openfoodfacts.github](https://openfoodfacts.github.io/documentation/docs/Product-Opener/v2/search/get-search/)

Let:

- `q_brand`, `q_name` be the LLM’s `brand_guess` and `canonical_query`.  
- For each OFF product `p`:

  - `brand_score`: 1.0 if `p.brands` contains `q_brand` (case‑insensitive); 0.5 if similar (Levenshtein distance below threshold); else 0.0.  
  - `name_score`: normalized string similarity (e.g. token Jaccard or cosine similarity) between `q_name` and `p.product_name`.  
  - `country_score`: 0.5 if `countries_tags_en` includes `romania`, else 0.0. [apis](https://apis.io/apis/open-food-facts/open-food-facts-search-api/)
  - Optional `category_score`: if your category mapping (e.g. “household_cleaning”) agrees with OFF’s `categories_tags_en` (“detergents”, “household-cleaners”), add 0.25. [wiki.openfoodfacts](https://wiki.openfoodfacts.org/Open_Food_Facts_Search_API_Version_2)

Overall score:

\[
score(p) = 0.4 \cdot brand\_score + 0.4 \cdot name\_score + 0.2 \cdot (country\_score + category\_score)
\]

Heuristic:

- Sort products by `score(p)` descending.  
- If top score < 0.6, treat OFF as “no confident match” and fall back to Jina search.  
- If top score ≥ 0.6 and margin to second place ≥ 0.15, accept first candidate.  
- If ambiguity remains (scores within 0.15), either:  
  - Ask the LLM to re‑rank with more context (image crop + OFF candidates); or  
  - Prefer the product with `countries_tags_en` including `romania` and more complete `nutriments` fields.

***

## 3. Failure mode & edge‑case matrix

### Edge cases & handling table

| Case | Pipeline behavior | Primary failure risks | Recommended handling |
|------|-------------------|-----------------------|----------------------|
| Private‑label grocery (Mega Image “365”, Kaufland “K‑Classic”, Lidl “Pilos”) | LLM extracts `brand_guess = "365"`, `category_guess = food`, `canonical_query` including retailer LOGO (if seen). OFF search with `brands_tags=365` + `search_terms` often misses or is noisy, since many private labels are imperfectly captured. [wiki.openfoodfacts](https://wiki.openfoodfacts.org/Barcodes) Jina search scoped to `site=mega-image.ro` or `site=lidl.ro` returns product detail pages with clear name, weight, and ingredients. [clawhub](https://clawhub.ai/adhishthite/skills/jina-ai) | OFF gaps for private labels; ambiguous brand naming (numeric brands); multiple flavors with similar names. | Add retailer detection to the LLM prompt (recognize supermarket logo and set `retailer_guess`). For OFF miss or low score, build Jina query: `[retailer_guess] [canonical_query] [size_guess]` with `site=<retailer domain>` and extract ingredients/nutrition via LLM from the Jina “content” field. |
| Unbranded produce / bulk goods | LLM sees no barcode, no brand; category likely “fresh produce” or “bakery” with handwritten label. OFF search by brand/name will fail or return generic items. [openfoodfacts.github](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-cheatsheet/) Jina search may find supermarket pages for “Bananas loose 1 kg”, but mapping is fuzzy. | No GTIN/EAN; label not standardized; high ambiguity in product identity. | Treat such items as non‑GTIN assets: skip OFF/Jina, store only `category`, `approx_weight`, and maybe “origin” if legible. Mark enrichment as “generic” and avoid nutrition/ingredients claims unless you use standardized tables (e.g. USDA/EU generic nutrition DB) keyed by category, not brand. |
| OTC medicine blister without cardboard box | LLM reads active ingredient and dosage (“Ibuprofen 200 mg”) but not brand, pack size, or manufacturer; barcodes often on outer box only. OFF likely has no entry (pharma coverage minimal). [selfhostednutrition](https://selfhostednutrition.org/API/open-food-facts-api-tutorial/) Jina search scoped to `site=farmaciatei.ro` or `site=emag.ro` will surface product pages but can mix Romanian brands with generic terms. | Missing EAN, incomplete text, high risk of mis‑identification (wrong strength or formulation). | If barcode absent, require explicit human confirmation before saving enriched medicine metadata. Use Jina search with query `[active ingredient] [dose] comprimate` + `site=farmaciatei.ro`, then ask the LLM to extract only non‑critical attributes (e.g. brand, pack size) and avoid dosage/regimen suggestions. For accurate regulatory/contraindication info, defer to a dedicated medicines DB (NAMMDR) in a later iteration. [anm](https://www.anm.ro/en/) |
| Rate limiting / downtime on OFF or Jina | OFF: no strict documented limits, but service can return 5xx or timeouts; v2 search can be temporarily degraded. [wiki.openfoodfacts](https://wiki.openfoodfacts.org/API/Read) Jina: token budget exhaustion, network timeouts, or quota errors from the Search Foundation API. [jina](https://jina.ai/) | Hard dependency on external APIs; inconsistent latency in the enrichment step. | Implement per‑service circuit breakers and fallbacks: if OFF fails, skip food enrichment and rely on bare LLM packaging interpretation; if Jina fails, mark enrichment as partial and persist raw LLM text only. Cache past successful OFF/Jina results by brand+name+size so repeat scans of the same product do not re‑hit APIs. Add offline batch jobs (nightly) to backfill enrichment when services are healthy. |

***

## 4. Minimal Python implementation (OFF → Jina cascade)

Below is a single‑file Python sketch using `httpx` and `pydantic` that takes `{brand, name, category}` and performs:

1. OFF search with brand+name.  
2. Candidate scoring.  
3. Jina search fallback if OFF has no confident match.  

It returns a Pydantic model containing enriched fields and per‑source attribution (URL + retrieval timestamp).

```python
import os
import urllib.parse
from datetime import datetime, timezone
from typing import Optional, List, Dict

import httpx
from pydantic import BaseModel, Field


OFF_BASE_URL = "https://world.openfoodfacts.org"
JINA_SEARCH_URL = os.getenv("JINA_SEARCH_URL", "https://s.jina.ai/")
JINA_API_KEY = os.getenv("JINA_API_KEY")


class SourceAttribution(BaseModel):
    source_name: str
    url: str
    retrieved_at: str  # ISO-8601


class EnrichedProduct(BaseModel):
    brand: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None

    product_name: Optional[str] = None
    ingredients_text: Optional[str] = None
    nutriments: Optional[Dict[str, float]] = None
    packaging: Optional[str] = None

    # Raw web context from Jina fallback (first result)
    jina_content: Optional[str] = None

    sources: List[SourceAttribution] = Field(default_factory=list)


class EnrichRequest(BaseModel):
    brand: str
    name: str
    category: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def search_off(brand: str, name: str) -> Dict:
    """
    Call OFF v2 search with search_terms + brand + Romania country filter.
    """
    params = {
        "search_terms": name,
        "brands_tags": brand,
        "countries_tags_en": "romania",
        "page": 1,
        "page_size": 10,
        "fields": "code,product_name,brands,ingredients_text,nutriments,packaging,countries_tags_en",
    }
    url = f"{OFF_BASE_URL}/api/v2/search"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params, headers={"User-Agent": "PantryPlus/0.1 (contact@example.com)"})
        resp.raise_for_status()
        data = resp.json()
        data["_request_url"] = str(resp.url)
        return data


def score_off_product(p: Dict, q_brand: str, q_name: str) -> float:
    brand_score = 0.0
    brands = (p.get("brands") or "").lower()
    if q_brand.lower() in brands:
        brand_score = 1.0

    name_score = 0.0
    pname = (p.get("product_name") or "").lower()
    if pname and q_name:
        # simple token overlap for minimal complexity
        q_tokens = set(q_name.lower().split())
        p_tokens = set(pname.split())
        inter = len(q_tokens & p_tokens)
        union = len(q_tokens | p_tokens)
        name_score = inter / union if union else 0.0

    country_score = 0.0
    countries = p.get("countries_tags_en") or []
    if isinstance(countries, list) and "romania" in [c.lower() for c in countries]:
        country_score = 0.5

    return 0.4 * brand_score + 0.4 * name_score + 0.2 * country_score


async def search_jina(brand: str, name: str, category: str) -> Dict:
    """
    Call Jina Search with site filters for Romanian retailers.
    """
    q = f"{brand} {name} {category}"
    encoded_q = urllib.parse.quote_plus(q)
    url = f"{JINA_SEARCH_URL}{encoded_q}"
    params = {
        "site": "mega-image.ro",
        "site": "emag.ro",
        "site": "farmaciatei.ro",
        "num": 5,
        "type": "web",
    }
    headers = {
        "Accept": "application/json",
        "X-Token-Budget": "6000",
        "X-Timeout": "15",
    }
    if JINA_API_KEY:
        headers["Authorization"] = f"Bearer {JINA_API_KEY}"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        data["_request_url"] = str(resp.url)
        return data


async def enrich(req: EnrichRequest) -> EnrichedProduct:
    enriched = EnrichedProduct(
        brand=req.brand,
        name=req.name,
        category=req.category,
    )

    # 1. Try OFF search
    try:
        off_resp = await search_off(req.brand, req.name)
        products = off_resp.get("products", []) or []
        scored = []
        for p in products:
            scored.append((score_off_product(p, req.brand, req.name), p))

        scored.sort(key=lambda t: t[0], reverse=True)
        if scored and scored[0][0] >= 0.6:
            best_score, best = scored[0]
            enriched.product_name = best.get("product_name")
            enriched.ingredients_text = best.get("ingredients_text")
            enriched.nutriments = best.get("nutriments")
            enriched.packaging = best.get("packaging")
            enriched.sources.append(
                SourceAttribution(
                    source_name="OpenFoodFacts",
                    url=off_resp.get("_request_url", f"{OFF_BASE_URL}/api/v2/search"),
                    retrieved_at=now_iso(),
                )
            )
            return enriched
    except Exception:
        # OFF error: fall through to Jina
        pass

    # 2. Fallback: Jina Search
    try:
        jina_resp = await search_jina(req.brand, req.name, req.category)
        # Jina search returns a list of entries; take the first one
        entries = jina_resp if isinstance(jina_resp, list) else jina_resp.get("results") or []
        if entries:
            first = entries[0]
            enriched.jina_content = first.get("content") or ""
            enriched.sources.append(
                SourceAttribution(
                    source_name="JinaSearch",
                    url=jina_resp.get("_request_url", ""),
                    retrieved_at=now_iso(),
                )
            )
    except Exception:
        # Jina error: leave enriched with only brand/name/category
        pass

    return enriched


# Example usage (async context):
#   req = EnrichRequest(brand="Jacobs", name="Cronat Gold", category="beverage")
#   result = asyncio.run(enrich(req))
#   print(result.model_dump())
```

This script deliberately keeps logic minimal:

- No external dependencies beyond `httpx` and `pydantic`.  
- Deterministic scoring and a simple “≥ 0.6” threshold for OFF confidence.  
- Jina fallback only enriches `jina_content` + source attribution; your final LLM synthesis pass would consume this content plus the base `EnrichedProduct` fields and generate the final normalized JSON for your app.

If you want, we can next iterate on:

- A stricter OFF scoring model (including category alignment).  
- A small extraction prompt for parsing `jina_content` into ingredients/nutrition/packaging in a second LLM step.

--- owner text ends ---
