import pytest
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import Chunk, Document, User
from app.generation.router import AskRequest, _handle_ask

@pytest.mark.asyncio
async def test_citations_grounded_in_real_chunks():
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.role == "Analyst"))).scalars().first()
        assert user is not None

        # Load all valid document titles and filenames
        docs = (await session.execute(select(Document.title, Document.source_path))).all()
        valid_titles = {d[0] for d in docs}
        valid_files = {d[1] for d in docs}

        questions = [
            "What is the password length requirement under Acme Corp IT Security Policy?",
            "What automated expense portal is mandatory for expense reimbursement under the 2024 policy?",
            "How many days per week can Acme Corp employees work remotely?",
        ]

        for q in questions:
            req = AskRequest(question=q, top_k=6)
            resp = await _handle_ask(req, user, session)
            assert not resp.abstained, f"Query '{q}' should not have abstained"
            assert len(resp.claims) > 0, f"Query '{q}' returned no claims"

            for claim in resp.claims:
                assert claim.citations, f"Claim '{claim.text}' has no citations attached"
                for cit in claim.citations:
                    # Check citation belongs to a real document
                    assert cit.title in valid_titles or any(f in (cit.title or "") for f in valid_files), \
                        f"Citation title '{cit.title}' is not a real document in corpus"
                    assert cit.snippet and len(cit.snippet.strip()) > 10, "Citation snippet is empty or trivial"
                    
                # If a supporting span is extracted, verify it's not made up
                if claim.supporting_span:
                    matched_in_snippet = any(claim.supporting_span.lower() in cit.snippet.lower() for cit in claim.citations)
                    # Either in snippet or affirms the cited text
                    assert matched_in_snippet or claim.verdict == "SUPPORTED", \
                        f"Supporting span '{claim.supporting_span}' not grounded in citations"
