"""
schemas.py – Pydantic v2 request/response schemas for the API.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


# ─────────────────────────────────────────────────────────────────────────────
# User schemas
# ─────────────────────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    name: str
    role: str
    clearance_level: int


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ─────────────────────────────────────────────────────────────────────────────
# Document schemas
# ─────────────────────────────────────────────────────────────────────────────
class DocumentBase(BaseModel):
    title: str
    source_type: str
    source_path: str
    version: str | None = None
    doc_date: str | None = None
    access_level: int = 1
    allowed_roles: list[str] | None = None


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# Chunk schemas
# ─────────────────────────────────────────────────────────────────────────────
class ChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    document_id: int
    chunk_index: int
    text: str
    page_or_row: str | None = None
    doc_date: str | None = None
    version: str | None = None
    access_level: int
    faiss_id: int | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Query / RAG schemas
# ─────────────────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    user_id: int
    top_k: int = 5


class SourceCitation(BaseModel):
    document_title: str
    chunk_id: int
    page_or_row: str | None
    doc_date: str | None
    version: str | None
    access_level: int
    snippet: str


class ContradictionFlag(BaseModel):
    chunk_a_id: int
    chunk_b_id: int
    description: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    abstained: bool
    sources: list[SourceCitation]
    contradictions: list[ContradictionFlag]
    model_used: str
    latency_ms: float


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    env: str
    db: str
    version: str = "0.1.0"
