"""ingestion/router.py – upload + document listing endpoints."""
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.ingestion.indexer import BACKEND_DIR, rebuild_indexes
from app.ingestion.registry import guess_source_type
from app.ingestion.service import ROLES_BY_LEVEL, ingest_document
from app.auth.access import get_current_user
from app.models import Chunk, Document, User

router = APIRouter()  # mounted at /api/v1/ingestion
api_router = APIRouter(tags=["ingestion"])  # mounted at root: /ingest/upload, /documents

UPLOAD_DIR = BACKEND_DIR / "data" / "uploads"


@router.get("/ping")
async def ping():
    return {"module": "ingestion", "status": "ok"}


@api_router.post("/ingest/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    version: str = Form("1.0"),
    doc_date: str = Form(...),
    access_level: int = Form(1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Ingest an uploaded file, then rebuild the FAISS + BM25 indexes."""
    if user.clearance_level < 3:
        raise HTTPException(403, "Your role is not permitted to ingest documents.")
    if access_level not in ROLES_BY_LEVEL:
        raise HTTPException(422, "access_level must be 1-4")
    filename = Path(file.filename or "").name
    try:
        source_type = guess_source_type(filename)
    except ValueError as e:
        raise HTTPException(415, str(e))

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = UPLOAD_DIR / filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc, n = await ingest_document(
        db,
        path=str(dest),
        source_type=source_type,
        title=title,
        version=version,
        doc_date=doc_date,
        access_level=access_level,
        allowed_roles=ROLES_BY_LEVEL[access_level],
        source_name=filename,
    )
    total = await rebuild_indexes(db)
    return {"document_id": doc.id, "title": title, "chunks": n, "total_indexed_chunks": total}


@api_router.get("/documents")
async def list_documents(db: AsyncSession = Depends(get_db)):
    """All documents with metadata (access filtering is added in Phase 3)."""
    q = (
        select(Document, func.count(Chunk.id))
        .outerjoin(Chunk, Chunk.document_id == Document.id)
        .group_by(Document.id)
        .order_by(Document.id)
    )
    return [
        {
            "id": d.id,
            "title": d.title,
            "source_type": d.source_type,
            "source": d.source_path,
            "version": d.version,
            "doc_date": d.doc_date,
            "access_level": d.access_level,
            "allowed_roles": d.allowed_roles,
            "chunk_count": n,
        }
        for d, n in (await db.execute(q)).all()
    ]
