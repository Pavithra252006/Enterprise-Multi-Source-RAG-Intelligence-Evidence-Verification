"""
models.py – SQLAlchemy ORM models.

Access / clearance levels
--------------------------
1 = public       (intern)
2 = internal     (analyst)
3 = confidential (manager)
4 = restricted   (executive)
"""
from datetime import datetime, timezone

from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    clearance_level: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="1=public 2=internal 3=confidential 4=restricted"
    )

    query_logs: Mapped[list["QueryLog"]] = relationship(back_populates="user")


# ─────────────────────────────────────────────────────────────────────────────
# Employees (individual login credentials) + login audit trail
# ─────────────────────────────────────────────────────────────────────────────
class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    code_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class LoginEvent(Base):
    __tablename__ = "login_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[str] = mapped_column(String(30), nullable=True)  # null = unknown code
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )


# ─────────────────────────────────────────────────────────────────────────────
# Documents
# ─────────────────────────────────────────────────────────────────────────────
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)   # pdf|xlsx|html|csv
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=True)
    doc_date: Mapped[str] = mapped_column(String(20), nullable=True)        # YYYY-MM-DD
    access_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    allowed_roles: Mapped[list] = mapped_column(ARRAY(String).with_variant(JSON, "sqlite"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete")


# ─────────────────────────────────────────────────────────────────────────────
# Chunks
# ─────────────────────────────────────────────────────────────────────────────
class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page_or_row: Mapped[str] = mapped_column(String(30), nullable=True)    # "page 3" | "row 42"
    source: Mapped[str] = mapped_column(Text, nullable=True)               # originating file name / URL
    doc_date: Mapped[str] = mapped_column(String(20), nullable=True)
    version: Mapped[str] = mapped_column(String(20), nullable=True)
    access_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    allowed_roles: Mapped[list] = mapped_column(ARRAY(String).with_variant(JSON, "sqlite"), nullable=True)
    faiss_id: Mapped[int] = mapped_column(Integer, nullable=True, unique=True)

    document: Mapped["Document"] = relationship(back_populates="chunks")


# ─────────────────────────────────────────────────────────────────────────────
# Query Logs
# ─────────────────────────────────────────────────────────────────────────────
class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    abstained: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="query_logs")
