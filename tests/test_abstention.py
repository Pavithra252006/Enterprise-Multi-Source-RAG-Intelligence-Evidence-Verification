import pytest
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import User
from app.generation.router import AskRequest, _handle_ask

UNGROUNDED_QUESTIONS = [
    "What is the capital city of Mars and its atmospheric temperature?",
    "How many penguins live in Antarctica according to Acme Corp archives?",
    "What is the secret recipe for medieval Byzantine bread?",
    "What was the weather forecast in Tokyo on July 4, 1892?",
    "What is the quantum teleportation protocol used by Atlantis?",
]

@pytest.mark.asyncio
async def test_abstention_on_5_uncovred_questions():
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.role == "Analyst"))).scalars().first()
        assert user is not None

        for q in UNGROUNDED_QUESTIONS:
            req = AskRequest(question=q, top_k=6)
            resp = await _handle_ask(req, user, session)

            assert resp.abstained is True, f"System should have abstained for ungrounded query: '{q}'"
            assert "insufficient evidence" in resp.answer.lower(), f"Answer does not state insufficient evidence: '{resp.answer}'"
            assert resp.confidence == 0.0, f"Confidence should be 0.0 for abstained query, got {resp.confidence}"
            assert len(resp.claims) == 0, f"Abstained response should have 0 claims, got {len(resp.claims)}"
            assert len(resp.conflicts) == 0, f"Abstained response should have 0 conflicts, got {len(resp.conflicts)}"
