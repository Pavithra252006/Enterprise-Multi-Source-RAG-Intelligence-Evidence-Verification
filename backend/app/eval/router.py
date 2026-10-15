"""
eval/router.py – Evaluation endpoints:
- GET /eval/results (and /api/v1/eval/results)
- POST /eval/run (and /api/v1/eval/run)
"""
import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.eval.run_eval import RESULTS_PATH, evaluate_all

log = logging.getLogger("eval.router")

router = APIRouter()  # Mounted at /api/v1/eval
api_router = APIRouter(tags=["eval"])  # Mounted at root: /eval/results, /eval/run


@router.get("/ping")
async def ping():
    return {"module": "eval", "status": "ok"}


@api_router.get("/eval/results")
@router.get("/results")
async def get_eval_results():
    """
    Returns latest benchmark evaluation results.
    If results.json does not exist yet, executes evaluate_all() dynamically.
    """
    if RESULTS_PATH.exists():
        try:
            with open(RESULTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.warning("Failed to read %s (%s); regenerating...", RESULTS_PATH, e)

    # Regenerate if file missing or corrupt
    return await evaluate_all()


@api_router.post("/eval/run")
@router.post("/run")
async def run_evaluation():
    """
    Triggers an end-to-end benchmark evaluation run across the 20 labeled test cases.
    """
    try:
        return await evaluate_all()
    except Exception as e:
        log.exception("Evaluation execution failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))