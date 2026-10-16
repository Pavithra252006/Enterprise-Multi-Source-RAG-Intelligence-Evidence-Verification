import pytest
from pathlib import Path
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import Chunk, User
from app.generation.router import AskRequest, _handle_ask
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.service import ingest_document
from app.ingestion.indexer import rebuild_indexes

@pytest.mark.asyncio
async def test_empty_query():
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.role == "Analyst"))).scalars().first()
        req = AskRequest(question="   ", top_k=6)
        resp = await _handle_ask(req, user, session)
        assert resp.abstained is True
        assert "insufficient evidence" in resp.answer.lower()

@pytest.mark.asyncio
async def test_very_long_query():
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.role == "Analyst"))).scalars().first()
        long_q = "What is the policy for remote work? " + ("explain in extreme detail " * 150)
        req = AskRequest(question=long_q, top_k=6)
        resp = await _handle_ask(req, user, session)
        assert resp is not None
        assert isinstance(resp.answer, str)
        assert resp.confidence >= 0.0

@pytest.mark.asyncio
async def test_non_english_queries():
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.role == "Analyst"))).scalars().first()
        
        # Spanish query
        spanish_q = "¿Cuántos días a la semana pueden los empleados trabajar de forma remota?"
        req = AskRequest(question=spanish_q, top_k=6)
        resp = await _handle_ask(req, user, session)
        assert resp is not None
        assert isinstance(resp.answer, str)

        # Chinese query
        chinese_q = "员工每周可以在家工作几天？"
        req_cn = AskRequest(question=chinese_q, top_k=6)
        resp_cn = await _handle_ask(req_cn, user, session)
        assert resp_cn is not None
        assert isinstance(resp_cn.answer, str)

@pytest.mark.asyncio
async def test_duplicate_document_idempotency():
    RAW_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "raw"
    pdf_path = RAW_DIR / "policy_handbook_v2_2024.pdf"

    async with AsyncSessionLocal() as session:
        # Initial chunk count for this source
        q_count = select(Chunk).where(Chunk.source == "policy_handbook_v2_2024.pdf")
        initial_chunks = len((await session.execute(q_count)).scalars().all())

        # Ingest again with same version
        doc, count = await ingest_document(
            session,
            path=str(pdf_path),
            source_type="pdf",
            title="Acme Corp Employee Policy Handbook v2.0 (2024)",
            version="2.0",
            doc_date="2024-03-01",
            access_level=2,
            allowed_roles=["analyst", "manager", "executive"],
        )

        # Verify chunk count did NOT double
        after_chunks = len((await session.execute(q_count)).scalars().all())
        assert after_chunks == initial_chunks, f"Chunk count changed on re-ingest: {initial_chunks} -> {after_chunks}"

        # Maintain index integrity for subsequent tests
        await rebuild_indexes(session)

def test_unreadable_file_handling():
    with pytest.raises(Exception):
        load_pdf("non_existent_file_12345.pdf")
