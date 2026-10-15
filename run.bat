@echo off
REM ==============================================================================
REM PS-019 Enterprise Multi-Source RAG Intelligence & Evidence Verification
REM Windows Launcher Script
REM ==============================================================================

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

echo ================================================================================
echo  Starting PS-019 Enterprise RAG Intelligence & Evidence Verification Platform
echo ================================================================================

REM 1. Activate Python virtual environment
if exist "%ROOT_DIR%\.venv\Scripts\activate.bat" (
    call "%ROOT_DIR%\.venv\Scripts\activate.bat"
    echo [OK] Python virtual environment activated.
)

REM 2. Run Database Ingestion
echo [1/3] Initializing Database and Indexing Synthetic Corpus...
cd /d "%ROOT_DIR%\backend"
python -c "import asyncio; from app.db import init_db; from app.main import seed_users; asyncio.run(init_db()); asyncio.run(seed_users())"
python -m app.ingestion.pipeline

REM 3. Launch Backend
echo [2/3] Launching FastAPI Backend on port 8000...
start "PS-019 Backend" cmd /k "cd /d %ROOT_DIR%\backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM 4. Launch Frontend
echo [3/3] Launching Vite Frontend on port 5173...
cd /d "%ROOT_DIR%\frontend"
start "PS-019 Frontend" cmd /k "npm run dev"

echo [OK] Services launched! Open http://localhost:5173 in your browser.
pause
