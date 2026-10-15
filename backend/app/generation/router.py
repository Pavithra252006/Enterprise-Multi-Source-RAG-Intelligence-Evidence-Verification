"""
generation/router.py – Claude-powered answer generation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"module": "generation", "status": "stub – not yet implemented"}


@router.post("/query", response_model=QueryResponse)
async def generate_answer(req: QueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Full RAG pipeline:
      1. Retrieve chunks (hybrid, access-filtered)
      2. Detect contradictions
      3. Build Claude prompt with grounding + contradiction flags
      4. Stream/collect Claude response
      5. Log to query_logs table
      6. Return structured QueryResponse
    """
    raise HTTPException(status_code=501, detail="RAG generation not yet implemented")
