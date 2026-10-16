"""
config.py – Centralised settings loaded from environment / .env file.
All secrets and tuneable parameters live here.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── LLM ──────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = "sk-ant-REPLACE_ME"
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://rag_user:rag_pass@127.0.0.1:5432/ragdb?ssl=false"

    # ── Embedding & Reranking models (HuggingFace) ────────────────────────
    EMBED_MODEL: str = "BAAI/bge-small-en-v1.5"
    RERANK_MODEL: str = "BAAI/bge-reranker-base"

    # ── FAISS index path ─────────────────────────────────────────────────
    FAISS_INDEX_PATH: str = "backend/data/index/faiss.index"
    FAISS_META_PATH: str = "backend/data/index/faiss_meta.json"

    # ── Chunking ─────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # ── Retrieval ────────────────────────────────────────────────────────
    TOP_K_DENSE: int = 30
    TOP_K_BM25: int = 30
    TOP_K_FUSION: int = 20
    RRF_K: int = 60
    TOP_K_RERANK: int = 6
    ADAPTIVE_RERANK_THRESHOLD: float = 0.25
    MAX_ADAPTIVE_ROUNDS: int = 1

    # ── App ──────────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
