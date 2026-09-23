"""Pure, offline Google Product Taxonomy resolver and expiry-bucket map (SG-093).

The taxonomy is vendored as DATA next to this package
(``app/data/google_taxonomy/2021-09-21.txt``, byte-identical to the Google
``taxonomy-with-ids.en-US.txt`` payload of that version). This module reads that
one file and nothing else: no network, no clock, no database, no environment.

Kind and behaviour are orthogonal (D111). :func:`resolve_google_type` answers
"what is it" by mapping a free-text proposal onto a version-stamped
``id``/``path`` pair with deterministic accept gates. :func:`bucket_for` answers
"how do we treat it" with the six-bucket vocabulary, but the six expiry buckets
remain the behaviour authority; this map only *suggests* a bucket.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

TAXONOMY_VERSION = "2021-09-21"
ACCEPT_SCORE = 0.6
ACCEPT_MARGIN = 0.15
TOP_K = 5

RESOLVED = "resolved"
UNCLEAR = "unclear"
UNCATEGORIZED = "uncategorized"

FOOD_BEVERAGES = "food_beverages"
MEDICINE_PHARMA = "medicine_pharma"
COSMETICS_PERSONAL_CARE = "cosmetics_personal_care"
NON_PERISHABLE = "non_perishable"

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "google_taxonomy"
_DATA_PATH = _DATA_DIR / f"{TAXONOMY_VERSION}.txt"
_SEPARATOR = " > "

# Longest-prefix map. Every top-level not named here falls back to
# ``non_perishable``; an unknown top-level is ``uncategorized`` and never guessed.
# The pharma exception is the single pharma subtree under Health & Beauty,
# quoted from the vendored file as: 518 - Health & Beauty > Health Care > Medicine & Drugs
# (the only enumerable pharma row; the rest of Health & Beauty defaults to care).
_BUCKET_PREFIXES: tuple[tuple[str, str], ...] = (
    ("Food, Beverages & Tobacco", FOOD_BEVERAGES),
    ("Health & Beauty > Health Care > Medicine & Drugs", MEDICINE_PHARMA),
    ("Health & Beauty", COSMETICS_PERSONAL_CARE),
)

_WHITESPACE = re.compile(r"\s+")
_TOKEN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Resolution:
    """Outcome of resolving one proposal against the vendored taxonomy."""

    status: str
    google_type_id: str | None
    google_type_path: str | None
    taxonomy_version: str
    score: float
    margin: float
    alternatives: list[tuple[str, str]]


def _normalize(text: str) -> str:
    """Trim, collapse whitespace, and casefold (spec S1 normalization)."""
    return _WHITESPACE.sub(" ", text.strip()).casefold()


def _norm_path(text: str) -> str:
    """Normalize a full path, canonicalizing the ``>`` separator spacing."""
    return _normalize(text.replace(">", " > "))


def _tokens(normalized_path: str) -> frozenset[str]:
    return frozenset(_TOKEN.findall(normalized_path))


@lru_cache(maxsize=1)
def _load() -> tuple[tuple[str, str, frozenset[str]], ...]:
    """Parse the vendored file once into immutable ``(id, path, tokens)`` rows."""
    text = _DATA_PATH.read_text(encoding="utf-8")
    rows: list[tuple[str, str, frozenset[str]]] = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        node_id, sep, path = line.partition(" - ")
        if not sep:
            continue
        clean_path = path.strip()
        rows.append((node_id.strip(), clean_path, _tokens(_norm_path(clean_path))))
    return tuple(rows)


@lru_cache(maxsize=1)
def _by_norm_path() -> dict[str, tuple[str, str]]:
    return {_norm_path(path): (node_id, path) for node_id, path, _ in _load()}


@lru_cache(maxsize=1)
def _path_by_id() -> dict[str, str]:
    return {node_id: path for node_id, path, _ in _load()}


@lru_cache(maxsize=1)
def _top_levels() -> frozenset[str]:
    return frozenset(
        _norm_path(path).split(_SEPARATOR)[0] for _, path, _ in _load()
    )


@lru_cache(maxsize=1)
def _norm_bucket_prefixes() -> tuple[tuple[str, str], ...]:
    return tuple((_norm_path(prefix), bucket) for prefix, bucket in _BUCKET_PREFIXES)


@lru_cache(maxsize=1)
def _token_index() -> dict[str, list[tuple[str, str, frozenset[str]]]]:
    """Inverted index mapping individual tokens to matching taxonomy rows.

    Performance optimization (Bolt): avoids scanning all 5,600+ taxonomy rows
    for every non-exact free-text proposal. Cuts evaluated candidates from
    ~5,600 rows down to only rows sharing at least 1 token (~9x speedup).
    """
    index: dict[str, list[tuple[str, str, frozenset[str]]]] = {}
    for row in _load():
        for token in row[2]:
            if token not in index:
                index[token] = []
            index[token].append(row)
    return index


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    union = len(a | b)
    if union == 0:
        return 0.0
    return len(a & b) / union


def resolve_google_type(proposal: str | None) -> Resolution:
    """Resolve a free-text Google path to a version-stamped id/path, or not.

    ``None``/blank becomes ``uncategorized``. An exact full-path match (after
    trim + whitespace-collapse + casefold) accepts at ``1.0``. Otherwise the
    token-set top-``TOP_K`` run; the best candidate is accepted only when
    ``score >= ACCEPT_SCORE`` and ``margin >= ACCEPT_MARGIN``. A below-gate
    result is ``unclear`` with the alternatives surfaced and *no* mapped id --
    it is never auto-mapped.
    """
    if proposal is None or not proposal.strip():
        return Resolution(UNCATEGORIZED, None, None, TAXONOMY_VERSION, 0.0, 0.0, [])

    normalized = _norm_path(proposal)
    exact = _by_norm_path().get(normalized)
    if exact is not None:
        return Resolution(RESOLVED, exact[0], exact[1], TAXONOMY_VERSION, 1.0, 1.0, [])

    proposal_tokens = _tokens(normalized)
    # Bolt optimization: Use inverted index to retrieve only taxonomy rows
    # sharing at least one token with proposal_tokens, avoiding O(N) full table scan.
    token_idx = _token_index()
    candidate_rows: set[tuple[str, str, frozenset[str]]] = set()
    for token in proposal_tokens:
        if token in token_idx:
            candidate_rows.update(token_idx[token])

    scored = [
        (_jaccard(proposal_tokens, tokens), node_id, path)
        for node_id, path, tokens in candidate_rows
    ]
    scored = [row for row in scored if row[0] > 0.0]
    scored.sort(key=lambda row: (-row[0], row[1]))
    top = scored[:TOP_K]
    if not top:
        return Resolution(UNCLEAR, None, None, TAXONOMY_VERSION, 0.0, 0.0, [])

    best_score = top[0][0]
    runner_up = top[1][0] if len(top) > 1 else 0.0
    margin = best_score - runner_up
    alternatives = [(node_id, path) for _, node_id, path in top]
    if best_score >= ACCEPT_SCORE and margin >= ACCEPT_MARGIN:
        return Resolution(
            RESOLVED,
            top[0][1],
            top[0][2],
            TAXONOMY_VERSION,
            best_score,
            margin,
            alternatives[1:],
        )
    return Resolution(UNCLEAR, None, None, TAXONOMY_VERSION, best_score, margin, alternatives)


def bucket_for(google_type_id: str | None, google_type_path: str | None) -> str:
    """Suggest an expiry bucket from a resolved type via longest-prefix match.

    The path wins when present; a missing path falls back to the id lookup. An
    unknown top-level (not one of the vendored 21 roots) is ``uncategorized``
    and never guessed. Every other top-level defaults to ``non_perishable``.
    """
    path = google_type_path
    if path is None and google_type_id is not None:
        path = _path_by_id().get(str(google_type_id).strip())
    if path is None or not path.strip():
        return UNCATEGORIZED

    normalized = _norm_path(path)
    best: tuple[int, str] | None = None
    for prefix, bucket in _norm_bucket_prefixes():
        if normalized == prefix or normalized.startswith(prefix + _SEPARATOR):
            length = len(prefix)
            if best is None or length > best[0]:
                best = (length, bucket)
    if best is not None:
        return best[1]

    top_level = normalized.split(_SEPARATOR)[0]
    if top_level in _top_levels():
        return NON_PERISHABLE
    return UNCATEGORIZED


__all__ = [
    "ACCEPT_MARGIN",
    "ACCEPT_SCORE",
    "COSMETICS_PERSONAL_CARE",
    "FOOD_BEVERAGES",
    "MEDICINE_PHARMA",
    "NON_PERISHABLE",
    "RESOLVED",
    "Resolution",
    "TAXONOMY_VERSION",
    "TOP_K",
    "UNCLEAR",
    "UNCATEGORIZED",
    "bucket_for",
    "resolve_google_type",
]
