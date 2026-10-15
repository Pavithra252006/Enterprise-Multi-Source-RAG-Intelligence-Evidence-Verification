"""
ingestion/router.py – Document ingestion endpoints.
Parses, chunks, embeds, and indexes documents into FAISS + PostgreSQL.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"module": "ingestion", "status": "stub – not yet implemented"}


@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and ingest a single document.
    Pipeline: parse -> chunk -> embed -> upsert FAISS -> upsert DB
    """
    raise HTTPException(status_code=501, detail="Ingestion pipeline not yet implemented")


@router.post("/ingest-manifest")
async def ingest_from_manifest(db: AsyncSession = Depends(get_db)):
    """
    Ingest all files listed in backend/data/raw/manifest.json.
    Uses manifest metadata for access_level, version, doc_date, etc.
    """
    raise HTTPException(status_code=501, detail="Manifest ingestion not yet implemented")
