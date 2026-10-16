import pytest
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import Chunk, Document

@pytest.mark.asyncio
async def test_chunk_metadata_completeness():
    async with AsyncSessionLocal() as session:
        chunks = (await session.execute(select(Chunk))).scalars().all()
        assert len(chunks) > 0, "No chunks found in database. Run ingestion first."
        
        for c in chunks:
            assert c.source is not None and len(str(c.source).strip()) > 0, f"Chunk {c.id} has null or empty source"
            assert c.doc_date is not None and len(str(c.doc_date).strip()) > 0, f"Chunk {c.id} has null or empty doc_date"
            assert c.version is not None and len(str(c.version).strip()) > 0, f"Chunk {c.id} has null or empty version"
            assert c.access_level in (1, 2, 3, 4), f"Chunk {c.id} has invalid access_level: {c.access_level}"
            assert c.page_or_row is not None and len(str(c.page_or_row).strip()) > 0, f"Chunk {c.id} has missing location (page_or_row)"
            assert c.text is not None and len(c.text.strip()) > 20, f"Chunk {c.id} has empty or trivial text"
            assert c.chunk_index is not None and c.chunk_index >= 0, f"Chunk {c.id} has invalid chunk_index"
            # Verify prefix contains title/version/date
            assert "[" in c.text and "]" in c.text, f"Chunk {c.id} text lacks standard context prefix: {c.text[:50]}"

@pytest.mark.asyncio
async def test_document_metadata_completeness():
    async with AsyncSessionLocal() as session:
        docs = (await session.execute(select(Document))).scalars().all()
        assert len(docs) > 0, "No documents found in database."
        
        for d in docs:
            assert d.title is not None and len(d.title.strip()) > 0, f"Document {d.id} missing title"
            assert d.source_type in ("pdf", "xlsx", "csv", "html"), f"Document {d.id} invalid source_type: {d.source_type}"
            assert d.source_path is not None and len(d.source_path.strip()) > 0, f"Document {d.id} missing source_path"
            assert d.version is not None and len(d.version.strip()) > 0, f"Document {d.id} missing version"
            assert d.doc_date is not None and len(d.doc_date.strip()) > 0, f"Document {d.id} missing doc_date"
            assert d.access_level in (1, 2, 3, 4), f"Document {d.id} invalid access_level: {d.access_level}"
