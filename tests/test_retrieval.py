import json
from pathlib import Path
import pytest
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import Chunk, User
from app.retrieval.hybrid import _load_bm25, dense_search, lexical_search, hybrid_search
from app.retrieval.rerank import rerank

DATASET_PATH = Path(__file__).resolve().parent.parent / "backend" / "app" / "eval" / "dataset.json"

@pytest.mark.asyncio
async def test_lexical_and_dense_retrieval():
    query = "remote work policy days per week"
    dense_hits = dense_search(query, top_k=10)
    assert len(dense_hits) > 0, "Dense search returned no results"
    for faiss_id, rank in dense_hits:
        assert rank >= 1
        assert faiss_id >= 0

    lexical_hits = lexical_search(query, top_k=10)
    assert len(lexical_hits) > 0, "Lexical search returned no results"
    for chunk_id, rank in lexical_hits:
        assert rank >= 1
        assert chunk_id > 0

@pytest.mark.asyncio
async def test_hybrid_vs_individual_across_10_queries():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Pick 10 factual or conflict queries (where an answer is expected)
    test_queries = [d for d in dataset if not d.get("should_abstain")][:10]
    assert len(test_queries) >= 10, "Not enough test queries in dataset.json"

    async with AsyncSessionLocal() as session:
        # Load chunks to map chunk_id -> source filename
        chunk_res = await session.execute(select(Chunk.id, Chunk.source))
        chunk_source_map = {cid: Path(src).name.lower() for cid, src in chunk_res.all() if src}

        bm25_data = _load_bm25()
        chunk_ids_by_pos = bm25_data["chunk_ids"] if bm25_data else []

        # Executive user has access to all documents
        exec_user = (await session.execute(select(User).where(User.role == "Executive"))).scalars().first()
        assert exec_user is not None

        bm25_recall_hits = 0
        dense_recall_hits = 0
        hybrid_recall_hits = 0

        for item in test_queries:
            q = item["question"]
            expected = [doc.lower() for doc in item["expected_source_docs"]]

            # 1. BM25 top 6
            bm25_top = lexical_search(q, top_k=6)
            bm25_sources = {chunk_source_map.get(cid) for cid, _ in bm25_top}
            if any(exp in bm25_sources for exp in expected):
                bm25_recall_hits += 1

            # 2. Dense top 6
            dense_top = dense_search(q, top_k=6)
            dense_sources = {chunk_source_map.get(chunk_ids_by_pos[fid]) for fid, _ in dense_top if fid < len(chunk_ids_by_pos)}
            if any(exp in dense_sources for exp in expected):
                dense_recall_hits += 1

            # 3. Hybrid top 6
            hybrid_top = await hybrid_search(q, exec_user, session, top_fusion=6)
            hybrid_sources = {Path(c.source).name.lower() for c in hybrid_top if c.source}
            if any(exp in hybrid_sources for exp in expected):
                hybrid_recall_hits += 1

        print(f"\n[Retrieval 10-query benchmark] BM25: {bm25_recall_hits}/10, Dense: {dense_recall_hits}/10, Hybrid: {hybrid_recall_hits}/10")
        assert hybrid_recall_hits >= bm25_recall_hits, f"Hybrid ({hybrid_recall_hits}) should beat or match BM25 ({bm25_recall_hits})"
        assert hybrid_recall_hits >= dense_recall_hits, f"Hybrid ({hybrid_recall_hits}) should beat or match Dense ({dense_recall_hits})"
        assert hybrid_recall_hits >= 9, f"Hybrid recall should be >= 90% on benchmark, got {hybrid_recall_hits}/10"

@pytest.mark.asyncio
async def test_reranker_reordering():
    async with AsyncSessionLocal() as session:
        exec_user = (await session.execute(select(User).where(User.role == "Executive"))).scalars().first()
        query = "What is the password length requirement under Acme Corp IT Security Policy?"
        
        candidates = await hybrid_search(query, exec_user, session, top_fusion=10)
        assert len(candidates) >= 2, "Need at least 2 candidates to test reranker"

        original_order = [c.chunk_id for c in candidates]
        reranked = rerank(query, candidates, top_k=len(candidates))

        # Check all reranked have rerank_score
        for c in reranked:
            assert c.rerank_score is not None, "Rerank score was not assigned"
            
        reranked_order = [c.chunk_id for c in reranked]
        # Verify the scores are descending
        scores = [c.rerank_score for c in reranked]
        assert scores == sorted(scores, reverse=True), "Reranked scores must be monotonically descending"
        
        # Verify top item is relevant to passwords/security
        top_text = reranked[0].text.lower()
        assert "password" in top_text or "security" in top_text or "12" in top_text
