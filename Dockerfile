# ==============================================================================
# PS-019 Enterprise Multi-Source RAG Platform - Production Dockerfile
# Optimized for Render, Cloud Run, VPS, and Docker Compose
# ==============================================================================

FROM python:3.12-slim

# Set environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    PORT=8000 \
    APP_ENV=production

WORKDIR /app

# Install system dependencies required by PyTorch, FAISS, and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install CPU-only PyTorch first to save ~2.5GB and prevent OOM during build
RUN pip install --no-cache-dir torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install remaining python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code and raw corpus
COPY backend/ /app/backend/
COPY generate_corpus.py /app/

# Ensure runtime directories exist
RUN mkdir -p /app/backend/data/index /app/backend/data/uploads

WORKDIR /app/backend

# Expose default port
EXPOSE 8000

# Health check against FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start Uvicorn server binding dynamically to Render's $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
