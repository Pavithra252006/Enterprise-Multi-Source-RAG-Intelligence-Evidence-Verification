"""Offline check (no DB / models needed): python -m scripts.check_loaders  (from backend/)"""
import json
from pathlib import Path

from app.ingestion.chunker import chunk_segments, count_tokens
from app.ingestion.registry import get_loader

raw = Path(__file__).resolve().parents[1] / "data" / "raw"
seen: dict[str, int] = {}
for e in json.loads((raw / "manifest.json").read_text(encoding="utf-8")):
    segs = get_loader(e["source_type"])(str(raw / e["filename"]))
    chunks = chunk_segments(segs, e["title"], e.get("version"), e.get("doc_date"))
    big = max((count_tokens(c["text"]) for c in chunks), default=0)
    print(f"{e['filename']:34} segments={len(segs):3} chunks={len(chunks):3} max_tokens={big}")
    if seen.get(e["source_type"], 0) < 3:
        for c in chunks[: 3 - seen.get(e["source_type"], 0)]:
            seen[e["source_type"]] = seen.get(e["source_type"], 0) + 1
            print(f"   [{e['source_type']}] {c['page_or_row']!r}: {c['text'][:140]!r}")
