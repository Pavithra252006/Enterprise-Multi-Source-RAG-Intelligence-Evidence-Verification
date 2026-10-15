"""
main.py – FastAPI application entry-point.

Startup sequence
----------------
1. init_db()   – creates tables if they don't exist
2. seed_users() – inserts the 4 demo users (idempotent)

Routers (stubbed for ingestion, retrieval, generation, verification, auth, eval)
are imported and included so the URL namespaces are reserved.
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.db import AsyncSessionLocal, init_db
from app.models import User
from app.schemas import HealthResponse

# ── Router imports (stubbed modules expose empty routers) ─────────────────────
from app.ingestion.router import router as ingestion_router, api_router as ingestion_api_router
from app.retrieval.router import router as retrieval_router
from app.generation.router import router as generation_router
from app.verification.router import router as verification_router
from app.auth.router import router as auth_router
from app.eval.router import router as eval_router

settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# Seed data
# ─────────────────────────────────────────────────────────────────────────────
DEMO_USERS = [
    {"name": "intern", "role": "Intern", "clearance_level": 1},
    {"name": "analyst", "role": "Analyst", "clearance_level": 2},
    {"name": "manager", "role": "Manager", "clearance_level": 3},
    {"name": "executive", "role": "Executive", "clearance_level": 4},
]


async def seed_users() -> None:
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        for data in DEMO_USERS:
            result = await session.execute(
                select(User).where(User.name == data["name"])
            )
            if result.scalar_one_or_none() is None:
                session.add(User(**data))
        await session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_users()
    yield


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PS-019 Enterprise Multi-Source RAG Intelligence & Evidence Verification",
    version="0.1.0",
    description="Multi-source RAG with FAISS + BM25 hybrid retrieval, reranking, "
                "contradiction detection, and clearance-level access control.",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(ingestion_router, prefix="/api/v1/ingestion", tags=["ingestion"])
app.include_router(ingestion_api_router)  # /ingest/upload, /documents
app.include_router(retrieval_router, prefix="/api/v1/retrieval", tags=["retrieval"])
app.include_router(generation_router, prefix="/api/v1/generation", tags=["generation"])
app.include_router(verification_router, prefix="/api/v1/verification", tags=["verification"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(eval_router, prefix="/api/v1/eval", tags=["eval"])


# ─────────────────────────────────────────────────────────────────────────────
# Health endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    db_status = "unknown"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  # noqa: BLE001
        db_status = f"error: {exc}"

    return HealthResponse(
        status="ok",
        env=settings.APP_ENV,
        db=db_status,
    )


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "PS-019 RAG API – visit /docs for OpenAPI UI"}
