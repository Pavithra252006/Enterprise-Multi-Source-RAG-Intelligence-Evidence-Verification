"""
retrieval/rerank.py – Cross-encoder reranking using BAAI/bge-reranker-base.

Features:
- Lazy singleton loading of CrossEncoder model
- Predicts semantic relevance scores for (query, passage) pairs
- Sorts descending and retains top-K (default 6) candidates
"""
import logging
from typing import Sequence

from app.config import get_settings
from app.retrieval.hybrid import RetrievedChunk

log = logging.getLogger("retrieval.rerank")

_reranker = None


def get_reranker():
    """
    Lazy singleton accessor for the CrossEncoder model.
    """
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder

        model_name = get_settings().RERANK_MODEL
        log.info("Initializing CrossEncoder: %s", model_name)
        _reranker = CrossEncoder(model_name, max_length=512)
    return _reranker


def rerank(
    query: str,
    candidates: Sequence[RetrievedChunk],
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """
    Reranks candidates using the CrossEncoder model.
    Assigns candidate.rerank_score and returns top_k sorted descending.
    """
    if not candidates:
        return []

    settings = get_settings()
    k = top_k if top_k is not None else settings.TOP_K_RERANK

    reranker = get_reranker()
    pairs = [(query, c.text) for c in candidates]

    log.debug("Reranking %d pairs with cross-encoder for query: %r", len(pairs), query)
    raw_scores = reranker.predict(pairs)

    # CrossEncoder.predict can return float (single item) or numpy array
    if hasattr(raw_scores, "tolist"):
        scores = [float(s) for s in raw_scores.tolist()]
    elif isinstance(raw_scores, (list, tuple)):
        scores = [float(s) for s in raw_scores]
    else:
        scores = [float(raw_scores)]

    for candidate, score in zip(candidates, scores):
        candidate.rerank_score = score

    # Sort descending by rerank_score
    ranked = sorted(candidates, key=lambda c: c.rerank_score if c.rerank_score is not None else -999.0, reverse=True)
    return ranked[:k]
