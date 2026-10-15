"""
retrieval/router.py – Retrieval endpoints:
- POST /retrieve (and /api/v1/retrieval/retrieve)
- POST /api/v1/retrieval/search
"""
import logging
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.access import get_current_user
from app.db import get_db
from app.models import User
from app.retrieval.adaptive import adaptive_retrieve

log = logging.getLogger("retrieval.router")

router = APIRouter()  # Mounted at /api/v1/retrieval
api_router = APIRouter(tags=["retrieval"])  # Mounted at root /


class RetrieveRequest(BaseModel):
    question: str = Field(..., description="The query or question to retrieve evidence for.")
    top_k: int = Field(6, ge=1, le=50, description="Number of evidence chunks to return.")
    threshold: float | None = Field(None, description="Optional override for adaptive rerank threshold.")
    max_rounds: int | None = Field(None, description="Max extra adaptive rounds.")


class EvidenceItem(BaseModel):
    chunk_id: int
    document_id: int
    title: str
    source: str
    version: str | None
    doc_date: str | None
    page_or_row: str | None
    access_level: int
    score: float
    text: str


class RetrieveResponse(BaseModel):
    question: str
    user_id: int
    user_role: str
    clearance_level: int
    evidence: list[EvidenceItem]
    trace: dict[str, Any]


@router.get("/ping")
async def ping():
    return {"module": "retrieval", "status": "ok"}


async def _handle_retrieve(
    req: RetrieveRequest,
    user: User,
    db: AsyncSession,
) -> RetrieveResponse:
    ranked_chunks, trace = await adaptive_retrieve(
        query=req.question,
        user=user,
        db=db,
        top_k=req.top_k,
        threshold=req.threshold,
        max_rounds=req.max_rounds,
    )

    evidence = [
        EvidenceItem(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            title=c.title,
            source=c.source,
            version=c.version,
            doc_date=c.doc_date,
            page_or_row=c.page_or_row,
            access_level=c.access_level,
            score=c.rerank_score if c.rerank_score is not None else c.rrf_score,
            text=c.text,
        )
        for c in ranked_chunks
    ]

    return RetrieveResponse(
        question=req.question,
        user_id=user.id,
        user_role=user.role,
        clearance_level=user.clearance_level,
        evidence=evidence,
        trace=trace,
    )


@api_router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_root(
    req: RetrieveRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Primary evidence retrieval endpoint (POST /retrieve).
    Enforces user clearance via X-User-Id header before reranking.
    """
    return await _handle_retrieve(req, user, db)


@router.post("/retrieve", response_model=RetrieveResponse)
@router.post("/search", response_model=RetrieveResponse)
async def retrieve_namespaced(
    req: RetrieveRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Namespaced retrieval endpoint (/api/v1/retrieval/retrieve and /search).
    """
    return await _handle_retrieve(req, user, db)
