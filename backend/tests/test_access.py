"""
tests/test_access.py – Access control verification tests.

Core requirements tested:
1. Level-1 user (intern) never receives a level-4 (or >1) chunk via /retrieve,
   including after query rewrites.
2. Level-4 user (executive) CAN access level-4 executive compensation chunks.
3. Role-based restrictions (vendor contracts accessible only to manager & executive).
4. Unauthenticated (missing X-User-Id) and non-existent users rejected with appropriate error codes.
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.db import init_db
from app.main import app, seed_users


@pytest.fixture(autouse=True)
async def setup_database():
    """Ensure database and demo users are present."""
    await init_db()
    await seed_users()


@pytest.mark.asyncio
async def test_intern_cannot_access_executive_compensation():
    """
    Level-1 user ('intern') requesting executive compensation should NEVER
    receive any Level-4 chunks from executive_compensation.pdf.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/retrieve",
            headers={"X-User-Id": "1"},  # Intern, clearance 1
            json={"question": "What is the executive compensation package and base salary for 2024?", "top_k": 10},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["clearance_level"] == 1
        assert data["user_role"].lower() == "intern"

        evidence = data["evidence"]
        for item in evidence:
            assert item["access_level"] <= 1, (
                f"Security breach! Intern received chunk with access_level={item['access_level']} "
                f"from document '{item['title']}' (chunk_id={item['chunk_id']})"
            )
            assert "executive_compensation" not in item["source"].lower()
            assert "executive compensation" not in item["title"].lower()


@pytest.mark.asyncio
async def test_executive_can_access_executive_compensation():
    """
    Level-4 user ('executive') requesting executive compensation SHOULD receive
    the Level-4 executive compensation chunks.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/retrieve",
            headers={"X-User-Id": "4"},  # Executive, clearance 4
            json={"question": "What is the executive compensation package and base salary for 2024?", "top_k": 5},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["clearance_level"] == 4
        assert data["user_role"].lower() == "executive"

        evidence = data["evidence"]
        assert len(evidence) > 0

        # At least one returned chunk must be the level-4 executive compensation document
        exec_chunks = [item for item in evidence if item["access_level"] == 4]
        assert len(exec_chunks) > 0, "Executive was unable to retrieve level-4 executive compensation"
        assert any("executive_compensation" in c["source"].lower() for c in exec_chunks)


@pytest.mark.asyncio
async def test_intern_never_receives_level_4_even_with_query_rewrites():
    """
    Even when an ambiguous/low-confidence query triggers adaptive multi-round
    query rewrites, a Level-1 user must NEVER be exposed to restricted chunks.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Use a high threshold to force query rewrites
        res = await client.post(
            "/retrieve",
            headers={"X-User-Id": "intern"},
            json={
                "question": "CEO salary C-suite incentive bonus compensation plan",
                "top_k": 10,
                "threshold": 0.99,  # Forces adaptive rewriting
                "max_rounds": 2,
            },
        )
        assert res.status_code == 200
        data = res.json()
        trace = data["trace"]

        # Confirm that multiple queries/rounds ran
        assert len(trace["queries"]) > 1 or trace["rounds_executed"] > 1

        # Confirm NO returned chunk has clearance > 1
        for item in data["evidence"]:
            assert item["access_level"] <= 1
            assert "executive_compensation" not in item["source"].lower()


@pytest.mark.asyncio
async def test_role_based_access_vendor_contracts():
    """
    Vendor contracts (access_level=3, allowed_roles=['manager', 'executive']):
    - Analyst (clearance 2) must NOT see vendor contracts.
    - Manager (clearance 3) CAN see vendor contracts.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Analyst query
        analyst_res = await client.post(
            "/retrieve",
            headers={"X-User-Id": "2"},  # Analyst
            json={"question": "What active vendor contracts exist with CloudNest?", "top_k": 5},
        )
        assert analyst_res.status_code == 200
        for item in analyst_res.json()["evidence"]:
            assert item["access_level"] <= 2
            assert "vendor_contracts" not in item["source"].lower()

        # 2. Manager query
        manager_res = await client.post(
            "/retrieve",
            headers={"X-User-Id": "3"},  # Manager
            json={"question": "What active vendor contracts exist with CloudNest?", "top_k": 5},
        )
        assert manager_res.status_code == 200
        manager_chunks = manager_res.json()["evidence"]
        vendor_chunks = [c for c in manager_chunks if "vendor_contracts" in c["source"].lower()]
        assert len(vendor_chunks) > 0, "Manager should be able to view vendor contracts register"


@pytest.mark.asyncio
async def test_missing_and_invalid_auth_headers():
    """
    Verify endpoint security when authentication headers are missing or invalid.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Missing header
        res_missing = await client.post(
            "/retrieve",
            json={"question": "What is Acme Corp headcount?"},
        )
        assert res_missing.status_code == 401

        # Non-existent user
        res_invalid = await client.post(
            "/retrieve",
            headers={"X-User-Id": "99999"},
            json={"question": "What is Acme Corp headcount?"},
        )
        assert res_invalid.status_code == 404
