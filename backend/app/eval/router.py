"""
eval/router.py - Answer quality evaluation endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class EvalRequest(BaseModel):
    query_log_id: int


@router.get("/ping")
async def ping():
    return {"module": "eval", "status": "stub - not yet implemented"}


@router.post("/evaluate")
async def evaluate_answer(req: EvalRequest):
    """
    Evaluate a logged answer for faithfulness, relevance, and hallucination risk.
    """
    raise HTTPException(status_code=501, detail="Evaluation not yet implemented")


@router.get("/logs")
async def get_eval_logs():
    """Return all evaluated query logs with scores."""
    raise HTTPException(status_code=501, detail="Eval logs not yet implemented")