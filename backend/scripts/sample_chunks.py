"""Print 3 sample chunks per source type (run from backend/):  python -m scripts.sample_chunks"""
import asyncio

from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import Chunk, Document


async def main() -> None:
    async with AsyncSessionLocal() as s:
        types = (await s.execute(select(Document.source_type).distinct())).scalars().all()
        for t in sorted(types):
            print(f"\n{'=' * 78}\nSOURCE TYPE: {t}\n{'=' * 78}")
            rows = (
                await s.execute(
                    select(Chunk, Document.title)
                    .join(Document, Document.id == Chunk.document_id)
                    .where(Document.source_type == t)
                    .order_by(Chunk.id)
                    .limit(3)
                )
            ).all()
            for c, title in rows:
                print(
                    f"- chunk#{c.id} faiss_id={c.faiss_id} source={c.source} "
                    f"loc={c.page_or_row!r} v{c.version} {c.doc_date} "
                    f"access={c.access_level} roles={c.allowed_roles}"
                )
                print("  " + c.text[:300].replace("\n", "\n  ") + ("..." if len(c.text) > 300 else ""))


if __name__ == "__main__":
    asyncio.run(main())
