"""
verification/router.py – Evidence verification and contradiction detection.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class VerifyRequest(BaseModel):
    chunk_ids: list[int]


@router.get("/ping")
async def ping():
    return {"module": "verification", "status": "stub – not yet implemented"}


@router.post("/check")
async def check_contradictions(req: VerifyRequest):
    """
    Given a list of chunk IDs, detect:
    - Factual contradictions (NLI / embedding similarity)
    - Temporal conflicts (doc_date delta > 180 days)
    - Version mismatches (same doc family, different version)
    - Access-level boundary violations
    """
    raise HTTPException(status_code=501, detail="Contradiction detection not yet implemented")
