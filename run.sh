#!/usr/bin/env bash
# ==============================================================================
# PS-019 Enterprise Multi-Source RAG Intelligence & Evidence Verification
# Launcher Script: Starts database, ingests corpus, and launches backend + frontend
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================================"
echo " Starting PS-019 Enterprise RAG Intelligence & Evidence Verification Platform"
echo "================================================================================"

# 1. Environment & Virtualenv Setup
if [ -d ".venv" ]; then
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    fi
    echo "[OK] Python virtual environment activated."
else
    echo "[WARN] .venv directory not found; using active python environment."
fi

# 2. Database Services
echo "[1/4] Checking Database Services..."
if command -v docker &> /dev/null && [ -f "docker-compose.yml" ]; then
    echo "Starting PostgreSQL via Docker Compose..."
    docker compose up -d db || echo "Proceeding with local/SQLite database."
else
    echo "Using configured SQLAlchemy database (SQLite/PostgreSQL fallback)."
fi

# 3. Database Initialization & Corpus Ingestion
echo "[2/4] Initializing Database & Ingesting Multi-Source Synthetic Corpus..."
cd "$SCRIPT_DIR/backend"
python -c "import asyncio; from app.db import init_db; from app.main import seed_users; asyncio.run(init_db()); asyncio.run(seed_users())"
python -m app.ingestion.pipeline
cd "$SCRIPT_DIR"
echo "[OK] Ingestion completed and FAISS + BM25 indexes ready."

# 4. Launch Backend Daemon
echo "[3/4] Launching FastAPI Backend on http://0.0.0.0:8000..."
cd "$SCRIPT_DIR/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for backend to be ready
echo "Waiting for backend health check..."
until curl -s http://localhost:8000/health > /dev/null; do
    sleep 1
done
echo "[OK] Backend is healthy and responding on port 8000."

# 5. Launch Frontend
echo "[4/4] Launching React Vite Frontend on http://localhost:5173..."
cd "$SCRIPT_DIR/frontend"

cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    echo "Services stopped cleanly."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

npm run dev -- --host 0.0.0.0 --port 5173
