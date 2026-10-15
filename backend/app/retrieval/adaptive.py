"""
retrieval/adaptive.py – Adaptive multi-round retrieval with query rewriting & decomposition.

Mechanism:
1. Run initial hybrid search + reranking.
2. If best rerank score < threshold:
   - Ask Claude to rewrite or decompose the query (with robust local heuristic fallback).
   - Execute retrieval again for the reformulated queries.
   - Merge candidate sets (deduplicated) and re-evaluate.
   - Allows up to MAX_ADAPTIVE_ROUNDS (default 2 extra rounds).
3. Returns ranked evidence and a detailed trace (queries attempted, scores, rounds).
"""
import logging
import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User
from app.retrieval.hybrid import RetrievedChunk, hybrid_search
from app.retrieval.rerank import rerank

log = logging.getLogger("retrieval.adaptive")


async def generate_query_variations(query: str, round_num: int) -> list[str]:
    """
    Generates rewritten or decomposed variations of the query.
    Attempts Claude API first if key configured; falls back to structured rule-based expansion.
    """
    settings = get_settings()
    variations: list[str] = []

    # 1. Try Claude if configured
    if settings.ANTHROPIC_API_KEY and not settings.ANTHROPIC_API_KEY.startswith("sk-ant-REPLACE"):
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            prompt = (
                f"You are a search query optimizer. The following query yielded poor or low-confidence search results:\n"
                f"Query: \"{query}\"\n\n"
                f"Rewrite or decompose this into 1 or 2 distinct, highly specific keyword search queries "
                f"tailored to corporate policy, headcount, financial reports, or vendor data.\n"
                f"Output ONLY the search queries, one per line, with no explanations, numbering, or quotes."
            )
            response = await client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text if response.content else ""
            lines = [line.strip().strip('"').strip("'") for line in text.splitlines() if line.strip()]
            for line in lines:
                clean = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
                if clean and clean != query:
                    variations.append(clean)
        except Exception as e:
            log.warning("Claude query rewrite failed: %s; using heuristic fallback.", e)

    # 2. Heuristic fallback / augmentation
    if not variations:
        clean_q = re.sub(r"^(what\s+is|what\s+are|how\s+many|can\s+you\s+tell\s+me|show\s+me|find)\s+", "", query, flags=re.I).strip(" ?.")
        if round_num == 1:
            variations.append(f"Acme Corp {clean_q}")
            if "remote" in query.lower() or "work" in query.lower():
                variations.append("employee policy handbook remote work telecommuting")
            elif "expense" in query.lower() or "travel" in query.lower():
                variations.append("employee policy reimbursement domestic travel limit")
            elif "headcount" in query.lower() or "employees" in query.lower():
                variations.append("workforce headcount employees annual report Q3 sales")
            elif "revenue" in query.lower() or "sales" in query.lower():
                variations.append("financial highlights revenue Q3 annual report")
            elif "compensation" in query.lower() or "salary" in query.lower() or "executive" in query.lower():
                variations.append("executive compensation report base salary incentive")
            else:
                variations.append(clean_q)
        else:
            # Round 2: token decomposition
            words = [w for w in clean_q.split() if len(w) > 3 and w.lower() not in {"acme", "corp", "corporation"}]
            if words:
                variations.append(" ".join(words))

    # Deduplicate and remove original query
    out = [v for v in variations if v.lower().strip() != query.lower().strip()]
    return out[:2] if out else [query]


async def adaptive_retrieve(
    query: str,
    user: User,
    db: AsyncSession,
    top_k: int | None = None,
    threshold: float | None = None,
    max_rounds: int | None = None,
) -> tuple[list[RetrievedChunk], dict[str, Any]]:
    """
    Executes hybrid search + reranking with multi-round adaptive reformulation if score < threshold.
    Returns (ranked_chunks, trace).
    """
    settings = get_settings()
    top_k = top_k if top_k is not None else settings.TOP_K_RERANK
    thresh = threshold if threshold is not None else settings.ADAPTIVE_RERANK_THRESHOLD
    max_r = max_rounds if max_rounds is not None else settings.MAX_ADAPTIVE_ROUNDS

    trace: dict[str, Any] = {
        "original_query": query,
        "threshold": thresh,
        "max_rounds": max_r,
        "rounds_executed": 1,
        "queries": [query],
        "scores_per_round": [],
        "rewrites_triggered": False,
    }

    # Round 0: Initial retrieval
    candidates = await hybrid_search(query, user, db)
    reranked = rerank(query, candidates, top_k=top_k) if candidates else []
    best_score = reranked[0].rerank_score if reranked else -999.0

    trace["scores_per_round"].append({
        "round": 0,
        "query": query,
        "candidates_found": len(candidates),
        "best_score": best_score,
        "scores": [c.rerank_score for c in reranked[:top_k]],
    })

    # Track seen chunk IDs and all candidates
    pool_by_id: dict[int, RetrievedChunk] = {c.chunk_id: c for c in candidates}
    current_round = 0

    # Adaptive loop
    while best_score < thresh and current_round < max_r:
        current_round += 1
        trace["rewrites_triggered"] = True
        trace["rounds_executed"] = current_round + 1

        new_queries = await generate_query_variations(query, current_round)
        log.info(
            "Adaptive retrieval round %d: best_score=%.4f < threshold=%.4f. Trying rewrites: %s",
            current_round,
            best_score,
            thresh,
            new_queries,
        )

        for nq in new_queries:
            if nq not in trace["queries"]:
                trace["queries"].append(nq)
            new_candidates = await hybrid_search(nq, user, db)
            for nc in new_candidates:
                if nc.chunk_id not in pool_by_id:
                    pool_by_id[nc.chunk_id] = nc

        # Rerank full pool against the original query
        if pool_by_id:
            reranked = rerank(query, list(pool_by_id.values()), top_k=top_k)
            best_score = reranked[0].rerank_score if reranked else -999.0
        else:
            reranked = []
            best_score = -999.0

        trace["scores_per_round"].append({
            "round": current_round,
            "queries": new_queries,
            "pool_size": len(pool_by_id),
            "best_score": best_score,
            "scores": [c.rerank_score for c in reranked[:top_k]],
        })

    return reranked[:top_k], trace
