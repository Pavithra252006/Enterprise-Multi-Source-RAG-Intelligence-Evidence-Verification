"""Test the ingestion endpoints: GET /documents, POST /ingest/upload"""
import asyncio
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        print(f"Health: {res.status_code} -> {res.json()}")
        assert res.status_code == 200

        # 2. GET /documents
        res = await client.get("/documents")
        print(f"GET /documents: {res.status_code} -> found {len(res.json())} documents")
        assert res.status_code == 200
        docs = res.json()
        assert len(docs) >= 8
        first_doc = docs[0]
        print(f"Sample Doc: {first_doc['title']} (chunks: {first_doc['chunk_count']})")

        # 3. POST /ingest/upload with a dummy test CSV
        csv_content = "item,cost\nLaptop,1200\nMouse,25\n"
        files = {"file": ("test_hardware.csv", csv_content.encode("utf-8"), "text/csv")}
        data = {
            "title": "Hardware Assets 2024",
            "version": "1.0",
            "doc_date": "2024-11-01",
            "access_level": "2",
        }
        res = await client.post("/ingest/upload", data=data, files=files)
        print(f"POST /ingest/upload: {res.status_code} -> {res.json()}")
        assert res.status_code == 200
        upload_resp = res.json()
        assert upload_resp["title"] == "Hardware Assets 2024"
        assert upload_resp["chunks"] > 0
        assert upload_resp["total_indexed_chunks"] >= 24

        print("\nAll endpoints verified successfully!")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
