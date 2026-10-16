"""
eval/run_eval.py – Standalone benchmark evaluation harness for PS-019 RAG platform.
Can be executed from root: python eval/run_eval.py
"""
import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.eval.run_eval import evaluate_all

if __name__ == "__main__":
    asyncio.run(evaluate_all())
