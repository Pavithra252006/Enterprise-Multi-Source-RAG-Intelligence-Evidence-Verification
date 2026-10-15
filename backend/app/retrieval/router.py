"""
retrieval/router.py – Hybrid retrieval endpoints.
FAISS dense + BM25 lexical, RRF fusion, cross-encoder reranking.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db

router = APIRouter()


class RetrievalRequest(BaseModel):
    query: str
    user_id: int
    top_k: int = 5


@router.get("/ping")
async def ping():
    return {"module": "retrieval", "status": "stub – not yet implemented"}


@router.post("/search")
async def hybrid_search(req: RetrievalRequest, db: AsyncSession = Depends(get_db)):
    """
    Hybrid retrieval: FAISS (dense) + BM25 (lexical) -> RRF fusion -> reranker.
    Access-filtered by user clearance level.
    """
    raise HTTPException(status_code=501, detail="Hybrid retrieval not yet implemented")
