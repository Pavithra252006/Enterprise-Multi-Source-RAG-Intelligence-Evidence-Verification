"""indexer.py – (re)build the FAISS (dense) and BM25 (lexical) indexes from the chunks table.

The indexes are always rebuilt from *all* chunks in the DB, which keeps the
faiss_id <-> chunk mapping consistent after replacing / adding documents.
faiss_id == row position in the FAISS index (and in the BM25 corpus).
"""
import logging
import pickle
import re
from pathlib import Path

import numpy as np
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Chunk

log = logging.getLogger("ingestion.indexer")

BACKEND_DIR = Path(__file__).resolve().parents[2]
INDEX_DIR = BACKEND_DIR / "data" / "index"
FAISS_PATH = INDEX_DIR / "faiss.index"
BM25_PATH = INDEX_DIR / "bm25.pkl"
BATCH_SIZE = 32

_model = None


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        name = get_settings().EMBED_MODEL
        log.info("Loading embedding model %s", name)
        _model = SentenceTransformer(name)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """Normalized float32 embeddings, batch size 32."""
    emb = _get_model().encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    return np.asarray(emb, dtype="float32")


def embed_query(query: str) -> np.ndarray:
    """BGE retrieval instruction for queries (used by Phase 3)."""
    q = "Represent this sentence for searching relevant passages: " + query
    return embed_texts([q])


def _build_and_save(ids: list[int], texts: list[str]) -> None:
    import faiss
    from rank_bm25 import BM25Okapi

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    vecs = embed_texts(texts)
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    faiss.write_index(index, str(FAISS_PATH))

    tokenized = [tokenize(t) for t in texts]
    bm25 = BM25Okapi(tokenized)
    with open(BM25_PATH, "wb") as f:
        pickle.dump({"bm25": bm25, "chunk_ids": ids}, f)


async def rebuild_indexes(session: AsyncSession) -> int:
    """Rebuild both indexes over every chunk; (re)assign faiss_id. Returns chunk count."""
    import asyncio

    rows = (await session.execute(select(Chunk.id, Chunk.text).order_by(Chunk.id))).all()
    if not rows:
        for p in (FAISS_PATH, BM25_PATH):
            p.unlink(missing_ok=True)
        return 0
    ids = [r[0] for r in rows]
    texts = [r[1] for r in rows]

    await asyncio.to_thread(_build_and_save, ids, texts)

    # faiss_id is UNIQUE: clear first so reassignment can't collide.
    await session.execute(update(Chunk).values(faiss_id=None))
    for pos, cid in enumerate(ids):
        await session.execute(update(Chunk).where(Chunk.id == cid).values(faiss_id=pos))
    await session.commit()
    log.info("Indexed %d chunks -> %s, %s", len(ids), FAISS_PATH.name, BM25_PATH.name)
    return len(ids)
