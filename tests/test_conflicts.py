import pytest
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import User
from app.generation.router import AskRequest, _handle_ask

@pytest.mark.asyncio
async def test_remote_work_conflict_resolution():
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.role == "Analyst"))).scalars().first()
        req = AskRequest(question="How many days per week can Acme Corp employees work remotely?", top_k=6)
        resp = await _handle_ask(req, user, session)

        assert not resp.abstained
        assert len(resp.conflicts) > 0, "No conflict detected for remote work version mismatch"
        
        conflict = resp.conflicts[0]
        assert "Remote Work" in conflict.topic
        
        # Verify both values are extracted
        values = {conflict.side_a.value, conflict.side_b.value}
        assert any("2" in v for v in values), f"Missing 2 days/week in conflict values: {values}"
        assert any("3" in v for v in values), f"Missing 3 days/week in conflict values: {values}"

        # Verify both sources are listed
        sources = {conflict.side_a.source, conflict.side_b.source}
        assert any("v1" in s for s in sources), f"Missing v1 source in {sources}"
        assert any("v2" in s for s in sources), f"Missing v2 source in {sources}"

        # Verify dates are present
        dates = {conflict.side_a.date, conflict.side_b.date}
        assert None not in dates and len(dates) == 2, f"Expected 2 dates, got: {dates}"

        # Verify resolution prefers newer version
        assert conflict.is_superseded is True
        assert "v2" in conflict.resolution or "newer" in conflict.resolution.lower()

        # Verify the answer itself recommends the current/newer policy (3 days)
        assert "3 days" in resp.answer

@pytest.mark.asyncio
async def test_headcount_temporal_conflict_resolution():
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.role == "Analyst"))).scalars().first()
        req = AskRequest(question="What is Acme Corp's current workforce headcount?", top_k=6)
        resp = await _handle_ask(req, user, session)

        assert not resp.abstained
        assert len(resp.conflicts) > 0, "No conflict detected for headcount mismatch"

        conflict = resp.conflicts[0]
        assert "Headcount" in conflict.topic

        # Verify both values (290 vs 312)
        values_str = f"{conflict.side_a.value} {conflict.side_b.value}"
        assert "290" in values_str and "312" in values_str, f"Missing 290 or 312 in {values_str}"

        # Verify resolution prefers 2024 over 2021
        assert conflict.is_superseded is True
        assert "2024" in conflict.resolution

        # Verify answer specifies 312 as current
        assert "312" in resp.answer
