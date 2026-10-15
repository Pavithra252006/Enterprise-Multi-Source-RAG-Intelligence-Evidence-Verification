"""service.py – ingest one document (load -> chunk -> store) and shared helpers."""
import logging
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.chunker import chunk_segments
from app.ingestion.registry import get_loader
from app.models import Chunk, Document

log = logging.getLogger("ingestion")

# access_level -> roles allowed (None = everyone), mirrors manifest.json
ROLES_BY_LEVEL = {
    1: None,
    2: ["analyst", "manager", "executive"],
    3: ["manager", "executive"],
    4: ["executive"],
}


async def ingest_document(
    session: AsyncSession,
    *,
    path: str,
    source_type: str,
    title: str,
    version: str | None,
    doc_date: str | None,
    access_level: int,
    allowed_roles: list[str] | None,
    source_name: str | None = None,
    **loader_kwargs,
) -> tuple[Document, int]:
    """Idempotent: an existing doc with same (source_name, version) has its chunks replaced.

    Does NOT rebuild indexes (caller does, once per batch).
    """
    source_name = source_name or Path(path).name
    segments = get_loader(source_type)(path, **loader_kwargs)
    chunks = chunk_segments(segments, title, version, doc_date)

    doc = (
        await session.execute(
            select(Document).where(
                Document.source_path == source_name, Document.version == version
            )
        )
    ).scalar_one_or_none()

    if doc is None:
        doc = Document(source_path=source_name)
        session.add(doc)
    else:
        await session.execute(delete(Chunk).where(Chunk.document_id == doc.id))

    doc.title = title
    doc.source_type = source_type
    doc.version = version
    doc.doc_date = doc_date
    doc.access_level = access_level
    doc.allowed_roles = allowed_roles
    await session.flush()

    session.add_all(
        Chunk(
            document_id=doc.id,
            chunk_index=c["chunk_index"],
            text=c["text"],
            page_or_row=c["page_or_row"],
            source=source_name,
            doc_date=doc_date,
            version=version,
            access_level=access_level,
            allowed_roles=allowed_roles,
        )
        for c in chunks
    )
    await session.commit()
    log.info("%-32s %-5s segments=%-3d chunks=%d", source_name, source_type, len(segments), len(chunks))
    return doc, len(chunks)
