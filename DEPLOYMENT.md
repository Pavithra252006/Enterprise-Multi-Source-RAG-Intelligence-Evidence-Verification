# Deployment Guide: Render (Backend) + Vercel (Frontend)

This guide walks you through deploying the **PS-019 Enterprise Multi-Source RAG Platform** into production using:
- **Render** for the containerized FastAPI backend, FAISS vector search, and database.
- **Vercel** for the high-performance React 19 + Vite frontend.

---

## Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │             User Browser               │
                      └──────────────────┬─────────────────────┘
                                         │
                   HTTPS Request         │ (VITE_API_URL)
                                         ▼
┌───────────────────────────────┐        ┌──────────────────────────────────────┐
│        Vercel (Edge)          │        │            Render (Web Service)      │
│  • React 19 + Vite Frontend   │        │  • FastAPI Python 3.12 (Docker)      │
│  • Auto-routing (vercel.json) │        │  • FAISS Dense Vector Index          │
│  • Global CDN                 │        │  • BM25 Lexical Index                │
└───────────────────────────────┘        │  • BAAI/bge Reranker & Embeddings    │
                                         │  • SQLite / Render PostgreSQL        │
                                         └──────────────────────────────────────┘
```

---

## Step 1: Deploy Backend on Render

The repository includes a production-ready `Dockerfile` and `render.yaml` (Render Blueprint) configured specifically for CPU-optimized PyTorch and FAISS.

### Option A: Automatic Deployment using Render Blueprint (Recommended)

1. Push your latest code changes to your GitHub repository:
   ```bash
   git add .
   git commit -m "feat: add Render and Vercel deployment configurations"
   git push origin main
   ```
2. Log in to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** in the top navigation and select **Blueprint**.
4. Connect your GitHub repository: `Enterprise-Multi-Source-RAG-Intelligence-Evidence-Verification`.
5. Render will automatically detect `render.yaml`:
   - Service Name: `enterprise-rag-backend`
   - Runtime: `Docker`
   - Health Check Path: `/health`
6. Under **Environment Variables**, provide your `ANTHROPIC_API_KEY`:
   - Key: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-...` (or leave placeholder if using offline evaluation/fallback mode)
7. Click **Apply**. Render will build the container and deploy the service.

---

### Option B: Manual Web Service Setup on Render

If you prefer setting up the web service manually:

1. In the Render Dashboard, click **New +** -> **Web Service**.
2. Select **Build and deploy from a Git repository** and connect this repository.
3. Configure the settings:
   - **Name**: `enterprise-rag-backend`
   - **Region**: Oregon (or your preferred region)
   - **Branch**: `main`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Instance Type**: Starter (or Free tier)
4. Scroll down to **Environment Variables** and add:

   | Variable | Recommended Value | Description |
   |---|---|---|
   | `APP_ENV` | `production` | Production environment flag |
   | `LOG_LEVEL` | `INFO` | Application log level |
   | `ANTHROPIC_API_KEY` | `your_claude_api_key` | Claude 3.5 Sonnet API key |
   | `CLAUDE_MODEL` | `claude-3-5-sonnet-20241022` | Generation model version |
   | `DATABASE_URL` | `sqlite+aiosqlite:///backend/data/rag.db` | Default database (or Render Postgres URL) |
   | `CORS_ORIGINS` | `https://*.vercel.app,http://localhost:5173` | Allowed frontend origins |
   | `EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | Embedding model |
   | `RERANK_MODEL` | `BAAI/bge-reranker-base` | Cross-encoder reranker model |

5. Under **Advanced Settings**:
   - Set **Health Check Path** to `/health`.
6. Click **Create Web Service**.

---

### Verifying Backend Health

Once Render finishes building and the status shows **Live**:

1. Open `https://<your-render-backend-name>.onrender.com/health` in your browser.
   You should receive:
   ```json
   {
     "status": "ok",
     "env": "production",
     "db": "ok"
   }
   ```
2. Interactive Swagger UI is available at `https://<your-render-backend-name>.onrender.com/docs`.
3. Note your Render backend URL (e.g. `https://enterprise-rag-backend.onrender.com`). You will need this for Vercel in Step 2.

---

## Step 2: Deploy Frontend on Vercel

The frontend is built with React 19, Vite, and Tailwind CSS. The repository contains `frontend/vercel.json` and a root `vercel.json` for seamless Single Page Application (SPA) routing.

### Step-by-Step Vercel Deployment

1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository: `Enterprise-Multi-Source-RAG-Intelligence-Evidence-Verification`.
4. In the **Configure Project** screen:
   - **Project Name**: `enterprise-rag-intelligence` (or your preferred name)
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click `Edit` and select `frontend` (or leave as root if using the root `vercel.json`).
5. Expand the **Environment Variables** section and add:

   | Name | Value |
   |---|---|
   | `VITE_API_URL` | `https://<your-render-backend-name>.onrender.com` |

   *(Important: Do NOT include a trailing slash; e.g. use `https://enterprise-rag-backend.onrender.com`)*

6. Click **Deploy**.
7. Vercel will install dependencies, run `vite build`, and publish your app to a global CDN (e.g. `https://enterprise-rag-intelligence.vercel.app`).

---

## Step 3: End-to-End Verification Checklist

Once both Render and Vercel are deployed:

1. **System Health Indicator**:
   - Open your Vercel URL.
   - The top header should display **"API Online"** with a green pulse badge.
2. **Access Control Clearance Switching**:
   - Switch between demo users:
     - **Intern (Alex Chen, Level 1)**: Can query IT security policy; restricted from vendor contracts & executive compensation.
     - **Analyst (Maya Patel, Level 2)**: Can access internal employee handbook & headcount reports.
     - **Manager (David Kim, Level 3)**: Can access vendor contract pricing.
     - **Executive (Elena Rostova, Level 4)**: Has full access to Executive Compensation Report.
3. **Contradiction Resolution Verification**:
   - As Analyst or Manager, ask:
     > *"How many days per week are employees permitted to work remotely?"*
   - Verify the system detects the conflict between Handbook v1.0 (2 days) and Handbook v2.0 (3 days), cites v2.0 as superseding, and states **3 days per week**.
4. **Document Registry**:
   - Navigate to the Documents tab or modal to confirm the 8 synthetic enterprise documents are indexed and queryable.

---

## Optional: Upgrading to Render Managed PostgreSQL

If you prefer managed PostgreSQL over SQLite:

1. In Render Dashboard, click **New +** -> **PostgreSQL**.
2. Name it `enterprise-rag-postgres`.
3. Copy the **Internal Database URL** (or External Database URL).
4. In your Backend Web Service's **Environment** tab:
   - Update `DATABASE_URL` to the copied URL.
   - The application automatically converts `postgres://` to `postgresql+asyncpg://` and establishes SSL encryption.
5. The backend will automatically create tables and re-index the corpus on startup.

---

## Troubleshooting

- **Cold Starts on Render Free Tier**:
  Free tier instances spin down after 15 minutes of inactivity. The initial request might take 30-50 seconds to wake the instance. The frontend shows a reconnecting indicator during this period. Upgrading to a Starter instance eliminates cold starts.
- **CORS Errors**:
  The backend is configured with `allow_origin_regex=r"^https://.*\.vercel\.app$"`. Any deployment from Vercel (including preview branches) is allowed by default. If using a custom domain (e.g. `rag.yourcompany.com`), add it to `CORS_ORIGINS` on Render.
- **Index Persistence**:
  The FAISS vector and BM25 index files (`backend/data/index/`) are baked directly into the Docker image, guaranteeing zero-downtime search availability immediately upon container start.
