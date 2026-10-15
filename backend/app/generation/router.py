"""
generation/router.py – Full RAG pipeline endpoints:
- POST /ask (and /api/v1/generation/ask, /api/v1/generation/query)

Pipeline execution order:
1. Authenticate user via X-User-Id header.
2. Hybrid retrieval (FAISS + BM25 + RRF) with strict clearance access gating.
3. Cross-encoder reranking (BAAI/bge-reranker-base) + adaptive reformulation if low confidence.
4. Contradiction / Conflict detection across retrieved chunks.
5. Answer generation with labeled evidence citations [E1], [E2]...
6. Parallel claim verification via second-judge Claude / verifier.
7. Abstention evaluation (threshold, confidence < 0.6, or model flag).
8. Logging to query_logs table.
9. Return structured response.
"""
import logging
import time
from typing import Any
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.access import get_current_user
from app.config import get_settings
from app.db import get_db
from app.generation.answer import generate_answer
from app.models import QueryLog, User
from app.retrieval.adaptive import adaptive_retrieve
from app.verification.conflicts import ConflictItem, detect_conflicts
from app.verification.verifier import VerifiedClaim, verify_claims

log = logging.getLogger("generation.router")

router = APIRouter()  # Mounted at /api/v1/generation
api_router = APIRouter(tags=["generation"])  # Mounted at root /

ABSTAIN_MESSAGE = "Insufficient evidence in the sources you can access."


class AskRequest(BaseModel):
    question: str = Field(..., description="The query or question to answer.")
    top_k: int = Field(6, ge=1, le=20, description="Max evidence chunks to evaluate.")
    threshold: float | None = Field(None, description="Override for adaptive/abstention score threshold.")


class AskResponse(BaseModel):
    question: str
    user_id: int
    user_role: str
    clearance_level: int
    answer: str
    claims: list[VerifiedClaim]
    conflicts: list[ConflictItem]
    abstained: bool
    confidence: float
    retrieval_trace: dict[str, Any]


async def _handle_ask(
    req: AskRequest,
    user: User,
    db: AsyncSession,
) -> AskResponse:
    settings = get_settings()
    threshold = req.threshold if req.threshold is not None else (settings.ADAPTIVE_RERANK_THRESHOLD or 0.40)

    # 1. Hybrid retrieval with clearance access gating
    evidence_chunks, trace = await adaptive_retrieve(
        query=req.question,
        user=user,
        db=db,
        top_k=req.top_k,
        threshold=threshold,
    )

    best_score = trace.get("scores_per_round", [{}])[-1].get("best_score", -999.0)

    # 2. Check initial abstention condition: No accessible evidence or best score below threshold
    if not evidence_chunks or best_score < threshold:
        log.info(
            "Abstaining for user %s: best_score=%.4f < threshold=%.4f (or 0 accessible evidence)",
            user.name,
            best_score,
            threshold,
        )
        response_data = AskResponse(
            question=req.question,
            user_id=user.id,
            user_role=user.role,
            clearance_level=user.clearance_level,
            answer=ABSTAIN_MESSAGE,
            claims=[],
            conflicts=[],
            abstained=True,
            confidence=0.0,
            retrieval_trace=trace,
        )
        # Log to query_logs
        db_log = QueryLog(
            user_id=user.id,
            question=req.question,
            answer_json=response_data.model_dump(),
            abstained=True,
        )
        db.add(db_log)
        await db.commit()
        return response_data

    # 3. Detect conflicts between retrieved chunks
    conflicts = detect_conflicts(evidence_chunks)

    # 4. Generate answer grounded in evidence
    gen_result, chunk_map = await generate_answer(req.question, evidence_chunks)

    # 5. Verify claims in parallel
    ver_result = await verify_claims(gen_result.claims, chunk_map)

    # 6. Evaluate final abstention conditions:
    #    - confidence < 0.6
    #    - gen_result.insufficient_evidence == True
    abstained = False
    final_answer = gen_result.answer_summary

    if gen_result.insufficient_evidence or ver_result.confidence < 0.6:
        abstained = True
        final_answer = ABSTAIN_MESSAGE
        active_claims = []
        active_conflicts = []
    else:
        # Filter out or keep verified claims
        active_claims = ver_result.verified_claims
        active_conflicts = conflicts

    response_data = AskResponse(
        question=req.question,
        user_id=user.id,
        user_role=user.role,
        clearance_level=user.clearance_level,
        answer=final_answer,
        claims=active_claims,
        conflicts=active_conflicts,
        abstained=abstained,
        confidence=ver_result.confidence,
        retrieval_trace=trace,
    )

    # 7. Persist to query_logs table
    db_log = QueryLog(
        user_id=user.id,
        question=req.question,
        answer_json=response_data.model_dump(),
        abstained=abstained,
    )
    db.add(db_log)
    await db.commit()

    return response_data


@api_router.post("/ask", response_model=AskResponse)
async def ask_root(
    req: AskRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Primary RAG Q&A endpoint (POST /ask).
    Processes question, executes access-controlled hybrid retrieval,
    conflict detection, claim verification, and logging.
    """
    return await _handle_ask(req, user, db)


@router.post("/ask", response_model=AskResponse)
@router.post("/query", response_model=AskResponse)
async def ask_namespaced(
    req: AskRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Namespaced RAG Q&A endpoint (/api/v1/generation/ask and /query).
    """
    return await _handle_ask(req, user, db)


@router.get("/ping")
async def ping():
    return {"module": "generation", "status": "ok"}
