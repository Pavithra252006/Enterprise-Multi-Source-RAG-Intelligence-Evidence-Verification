"""
retrieval/hybrid.py – Hybrid retrieval combining FAISS dense search + BM25 lexical search.

Pipeline:
1. FAISS top 30 dense candidates
2. BM25 top 30 lexical candidates
3. Reciprocal Rank Fusion (RRF, k=60) -> top 20 candidates
4. Strict Access Filter applied right after fusion (can_access check)
"""
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.access import can_access
from app.config import get_settings
from app.ingestion.indexer import BM25_PATH, FAISS_PATH, embed_query, tokenize
from app.models import Chunk, Document, User

log = logging.getLogger("retrieval.hybrid")

_faiss_index = None
_faiss_mtime: float | None = None
_bm25_data = None
_bm25_mtime: float | None = None


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    title: str
    source: str
    version: str | None
    doc_date: str | None
    page_or_row: str | None
    access_level: int
    allowed_roles: list[str] | None
    text: str
    rrf_score: float = 0.0
    dense_rank: int | None = None
    lexical_rank: int | None = None
    rerank_score: float | None = None


def _load_faiss():
    global _faiss_index, _faiss_mtime
    import faiss

    if not FAISS_PATH.exists():
        return None
    mtime = FAISS_PATH.stat().st_mtime
    if _faiss_index is None or _faiss_mtime != mtime:
        log.info("Loading FAISS index from %s", FAISS_PATH)
        _faiss_index = faiss.read_index(str(FAISS_PATH))
        _faiss_mtime = mtime
    return _faiss_index


def _load_bm25():
    global _bm25_data, _bm25_mtime
    if not BM25_PATH.exists():
        return None
    mtime = BM25_PATH.stat().st_mtime
    if _bm25_data is None or _bm25_mtime != mtime:
        log.info("Loading BM25 data from %s", BM25_PATH)
        with open(BM25_PATH, "rb") as f:
            _bm25_data = pickle.load(f)
        _bm25_mtime = mtime
    return _bm25_data


def dense_search(query: str, top_k: int = 30) -> list[tuple[int, int]]:
    """
    Search FAISS index. Returns list of (faiss_id, rank) with rank 1..N.
    """
    index = _load_faiss()
    if index is None or index.ntotal == 0:
        return []

    q_emb = embed_query(query)
    k = min(top_k, index.ntotal)
    distances, indices = index.search(q_emb, k)
    results: list[tuple[int, int]] = []
    for rank, idx in enumerate(indices[0], start=1):
        if idx != -1:
            results.append((int(idx), rank))
    return results


def lexical_search(query: str, top_k: int = 30) -> list[tuple[int, int]]:
    """
    Search BM25 index. Returns list of (chunk_id, rank) with rank 1..N.
    """
    data = _load_bm25()
    if data is None:
        return []

    bm25 = data["bm25"]
    chunk_ids = data["chunk_ids"]
    tokens = tokenize(query)
    if not tokens:
        return []

    scores = bm25.get_scores(tokens)
    # Get top_k indices sorted by score descending
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
        : min(top_k, len(scores))
    ]
    results: list[tuple[int, int]] = []
    for rank, idx in enumerate(ranked_indices, start=1):
        if scores[idx] > 0.0:  # Only include non-zero lexical matches
            results.append((chunk_ids[idx], rank))
    return results


async def hybrid_search(
    query: str,
    user: User,
    db: AsyncSession,
    top_dense: int | None = None,
    top_lexical: int | None = None,
    top_fusion: int | None = None,
    rrf_k: int | None = None,
) -> list[RetrievedChunk]:
    """
    Executes hybrid dense + lexical retrieval, merges with RRF,
    and applies strict clearance/access filtering before returning candidates.
    """
    settings = get_settings()
    top_dense = top_dense or settings.TOP_K_DENSE
    top_lexical = top_lexical or settings.TOP_K_BM25
    top_fusion = top_fusion or settings.TOP_K_FUSION
    k = rrf_k or settings.RRF_K

    # 1. Retrieve Dense Candidates (faiss_id -> chunk_id)
    dense_hits = dense_search(query, top_k=top_dense)
    bm25_data = _load_bm25()
    chunk_ids_by_pos = bm25_data["chunk_ids"] if bm25_data else []

    # Map dense hits to (chunk_id, rank)
    dense_by_cid: dict[int, int] = {}
    for faiss_id, rank in dense_hits:
        if 0 <= faiss_id < len(chunk_ids_by_pos):
            cid = chunk_ids_by_pos[faiss_id]
            dense_by_cid[cid] = rank

    # 2. Retrieve Lexical Candidates (chunk_id, rank)
    lexical_hits = lexical_search(query, top_k=top_lexical)
    lexical_by_cid: dict[int, int] = {cid: rank for cid, rank in lexical_hits}

    # 3. Reciprocal Rank Fusion (RRF)
    all_cids = set(dense_by_cid.keys()) | set(lexical_by_cid.keys())
    if not all_cids:
        return []

    rrf_scores: dict[int, float] = {}
    for cid in all_cids:
        score = 0.0
        if cid in dense_by_cid:
            score += 1.0 / (k + dense_by_cid[cid])
        if cid in lexical_by_cid:
            score += 1.0 / (k + lexical_by_cid[cid])
        rrf_scores[cid] = score

    # Sort descending by RRF score and take top candidates
    sorted_cids = sorted(all_cids, key=lambda c: rrf_scores[c], reverse=True)[:top_fusion]

    # 4. Fetch DB models and enforce Access Filter right after fusion
    stmt = (
        select(Chunk)
        .options(selectinload(Chunk.document))
        .where(Chunk.id.in_(sorted_cids))
    )
    result = await db.execute(stmt)
    chunks_by_id = {c.id: c for c in result.scalars().all()}

    filtered_candidates: list[RetrievedChunk] = []
    for cid in sorted_cids:
        chunk = chunks_by_id.get(cid)
        if chunk is None:
            continue

        # CRITICAL RULE: filter by access BEFORE reranking and BEFORE anything reaches the LLM.
        if not can_access(user, chunk):
            log.debug(
                "Access denied for user %s (clearance=%d) to chunk %d (level=%d)",
                user.name,
                user.clearance_level,
                chunk.id,
                chunk.access_level,
            )
            continue

        doc = chunk.document
        filtered_candidates.append(
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                title=doc.title if doc else (chunk.source or "Unknown"),
                source=chunk.source or (doc.source_path if doc else "unknown"),
                version=chunk.version or (doc.version if doc else None),
                doc_date=chunk.doc_date or (doc.doc_date if doc else None),
                page_or_row=chunk.page_or_row,
                access_level=chunk.access_level,
                allowed_roles=chunk.allowed_roles,
                text=chunk.text,
                rrf_score=rrf_scores[cid],
                dense_rank=dense_by_cid.get(cid),
                lexical_rank=lexical_by_cid.get(cid),
            )
        )

    return filtered_candidates
