"""CLI:  python -m app.ingestion.ingest --manifest data/raw/manifest.json   (run from backend/)"""
import argparse
import asyncio
import json
import logging
from pathlib import Path

from app.db import AsyncSessionLocal, init_db
from app.ingestion.indexer import rebuild_indexes
from app.ingestion.service import ingest_document

log = logging.getLogger("ingestion")


async def run(manifest_path: Path) -> dict[str, int]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = manifest_path.parent
    await init_db()

    counts: dict[str, int] = {}
    async with AsyncSessionLocal() as session:
        for entry in manifest:
            _, n = await ingest_document(
                session,
                path=str(base / entry["filename"]),
                source_type=entry["source_type"],
                title=entry["title"],
                version=entry.get("version"),
                doc_date=entry.get("doc_date"),
                access_level=entry.get("access_level", 1),
                allowed_roles=entry.get("allowed_roles"),
            )
            counts[entry["filename"]] = n
        total = await rebuild_indexes(session)

    log.info("Done: %d documents, %d chunks indexed", len(counts), total)
    return counts


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest documents listed in a manifest")
    ap.add_argument("--manifest", required=True, type=Path)
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    asyncio.run(run(args.manifest.resolve()))


if __name__ == "__main__":
    main()
