"""
pipeline.py - Convenience entry point to run full ingestion pipeline over raw corpus manifest.
"""
import asyncio
import logging
from pathlib import Path
from app.ingestion.ingest import run

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    manifest_path = Path(__file__).resolve().parents[2] / "data" / "raw" / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")
    print(f"Ingesting documents from manifest: {manifest_path}")
    asyncio.run(run(manifest_path))


if __name__ == "__main__":
    main()
