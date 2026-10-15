"""
verification/router.py – Evidence verification and contradiction detection.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Chunk
from app.retrieval.hybrid import RetrievedChunk
from app.verification.conflicts import detect_conflicts, ConflictItem

router = APIRouter()


class VerifyRequest(BaseModel):
    chunk_ids: list[int]


@router.get("/ping")
async def ping():
    return {"module": "verification", "status": "ok"}


@router.post("/check", response_model=list[ConflictItem])
async def check_contradictions(req: VerifyRequest, db: AsyncSession = Depends(get_db)):
    """
    Given a list of chunk IDs, fetch them and detect:
    - Factual contradictions & version discrepancies
    - Temporal conflicts
    - Superseded resolutions
    """
    if not req.chunk_ids:
        return []

    stmt = select(Chunk).options(selectinload(Chunk.document)).where(Chunk.id.in_(req.chunk_ids))
    res = await db.execute(stmt)
    db_chunks = res.scalars().all()

    retrieved = [
        RetrievedChunk(
            chunk_id=c.id,
            document_id=c.document_id,
            title=c.document.title if c.document else (c.source or "Unknown"),
            source=c.source or (c.document.source_path if c.document else "unknown"),
            version=c.version or (c.document.version if c.document else None),
            doc_date=c.doc_date or (c.document.doc_date if c.document else None),
            page_or_row=c.page_or_row,
            access_level=c.access_level,
            allowed_roles=c.allowed_roles,
            text=c.text,
        )
        for c in db_chunks
    ]

    return detect_conflicts(retrieved)

