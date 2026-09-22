"""Deterministic Open Food Facts candidate scoring (SG-081, D108).

Pure, offline, no I/O. The formula is exactly research §2
(`score = 0.4*brand + 0.4*name + 0.2*(country + category)`) and the accept rule
is exactly ``top >= 0.6 AND margin-to-second >= 0.15``. There is no
nearest-guess accept: an ambiguous, below-threshold or empty field returns an
explicit no-confident-match with a named reason.

`category` is accepted so the formula stays whole, but this slice's OFF request
deliberately omits `categories_tags_en`, so the category term is inert on the
SG-081 path (stated, not hidden).
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

WEIGHT_BRAND = 0.4
WEIGHT_NAME = 0.4
WEIGHT_CONTEXT = 0.2

BRAND_EXACT = 1.0
BRAND_SIMILAR = 0.5
COUNTRY_ROMANIA = 0.5
CATEGORY_MATCH = 0.25

MIN_SCORE = 0.6
MIN_MARGIN = 0.15

MAX_BRAND_EDIT_DISTANCE = 2
MIN_TOKEN_LENGTH_FOR_SIMILARITY = 4

REASON_ACCEPTED = "accepted"
REASON_NO_CANDIDATES = "no_candidates"
REASON_BELOW_THRESHOLD = "below_threshold"
REASON_AMBIGUOUS = "ambiguous_margin"

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def _tokens(value: Any) -> list[str]:
    return _TOKEN_RE.findall(str(value or "").lower())


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        current = [i]
        for j, char_b in enumerate(b, start=1):
            cost = 0 if char_a == char_b else 1
            current.append(
                min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
            )
        previous = current
    return previous[-1]


def brand_score(q_brand: str, p_brands: Any) -> float:
    """1.0 when the query brand is a case-insensitive substring; 0.5 when an
    edit-distance-similar brand token is present; 0.0 otherwise."""
    query = _normalize(q_brand)
    if not query:
        return 0.0
    candidates = _as_str_list(p_brands)
    for candidate in candidates:
        if query and query in _normalize(candidate):
            return BRAND_EXACT
    if len(query) < MIN_TOKEN_LENGTH_FOR_SIMILARITY:
        return 0.0
    for candidate in candidates:
        for token in _tokens(candidate):
            if len(token) < MIN_TOKEN_LENGTH_FOR_SIMILARITY:
                continue
            if _levenshtein(query, token) <= MAX_BRAND_EDIT_DISTANCE:
                return BRAND_SIMILAR
    return 0.0


def name_score(q_name: str, p_name: Any) -> float:
    """Token Jaccard overlap between the query name and the product name."""
    query_tokens = set(_tokens(q_name))
    if not query_tokens:
        return 0.0
    product_tokens = set(_tokens(p_name))
    if not product_tokens:
        return 0.0
    union = query_tokens | product_tokens
    return len(query_tokens & product_tokens) / len(union)


def country_score(p_countries: Any) -> float:
    """0.5 when the product's countries include Romania, else 0.0."""
    for value in _as_str_list(p_countries):
        if "romania" in _normalize(value):
            return COUNTRY_ROMANIA
    return 0.0


def category_score(q_category: str | None, p_categories: Any) -> float:
    """0.25 when the query category agrees with a product category, else 0.0."""
    query = _normalize(q_category)
    if not query:
        return 0.0
    for value in _as_str_list(p_categories):
        normalized = _normalize(value)
        if normalized and (query == normalized or query in normalized):
            return CATEGORY_MATCH
    return 0.0


def score_candidate(
    product: Mapping[str, Any],
    *,
    brand: str,
    name: str,
    category: str | None = None,
) -> float:
    """The D108 formula over one OFF product (pure)."""
    return (
        WEIGHT_BRAND * brand_score(brand, product.get("brands"))
        + WEIGHT_NAME * name_score(name, product.get("product_name"))
        + WEIGHT_CONTEXT
        * (
            country_score(product.get("countries_tags_en"))
            + category_score(category, product.get("categories_tags_en"))
        )
    )


@dataclass(frozen=True)
class ScoredCandidate:
    product: Mapping[str, Any]
    score: float


@dataclass(frozen=True)
class MatchDecision:
    accepted: bool
    best: Mapping[str, Any] | None
    best_score: float
    margin: float
    reason: str


def rank_candidates(
    products: Sequence[Mapping[str, Any]],
    *,
    brand: str,
    name: str,
    category: str | None = None,
) -> list[ScoredCandidate]:
    """Score and sort high-to-low; ties broken by `code` for determinism."""
    scored = [
        ScoredCandidate(
            product=product,
            score=score_candidate(product, brand=brand, name=name, category=category),
        )
        for product in products
    ]
    scored.sort(key=lambda candidate: (-candidate.score, str(candidate.product.get("code") or "")))
    return scored


def decide(
    scored: Sequence[ScoredCandidate],
    *,
    min_score: float = MIN_SCORE,
    min_margin: float = MIN_MARGIN,
) -> MatchDecision:
    """Accept the top candidate iff it clears the score bar AND the margin bar."""
    if not scored:
        return MatchDecision(False, None, 0.0, 0.0, REASON_NO_CANDIDATES)
    top = scored[0]
    second_score = scored[1].score if len(scored) > 1 else 0.0
    margin = top.score - second_score
    if top.score < min_score:
        return MatchDecision(False, None, top.score, margin, REASON_BELOW_THRESHOLD)
    if margin < min_margin:
        return MatchDecision(False, None, top.score, margin, REASON_AMBIGUOUS)
    return MatchDecision(True, top.product, top.score, margin, REASON_ACCEPTED)


def select_candidate(
    products: Sequence[Mapping[str, Any]],
    *,
    brand: str,
    name: str,
    category: str | None = None,
    min_score: float = MIN_SCORE,
    min_margin: float = MIN_MARGIN,
) -> MatchDecision:
    """Rank + decide in one call; never returns a nearest guess."""
    return decide(
        rank_candidates(products, brand=brand, name=name, category=category),
        min_score=min_score,
        min_margin=min_margin,
    )
