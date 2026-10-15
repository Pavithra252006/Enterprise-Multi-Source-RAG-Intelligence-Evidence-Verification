# PS-019 PROJECT_CONTEXT.md

> **Purpose:** Onboarding document for developers, evaluators, and demo presenters.
> Describes the full system architecture, access model, demo users, corpus files,
> and the deliberate contradictions planted for testing the evidence-verification pipeline.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Query                           │
│              (question + user_id + top_k)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  AUTH / Access Control                                      │
│  • Look up clearance_level for user_id                     │
│  • Filter retrieved chunks to clearance ≤ user level       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  RETRIEVAL – Hybrid                                         │
│  • Dense:  FAISS (BAAI/bge-small-en-v1.5 embeddings)       │
│  • Lexical: BM25 (rank-bm25)                               │
│  • Fusion: Reciprocal Rank Fusion (RRF)                    │
│  • Rerank: BAAI/bge-reranker-base (cross-encoder)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  VERIFICATION – Evidence Checker                            │
│  • Detect contradictions between retrieved chunks           │
│  • Flag temporal conflicts (old vs. new document dates)    │
│  • Flag version mismatches (v1 vs. v2 policy)              │
│  • Flag access-level boundary violations                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  GENERATION – Claude API                                    │
│  • System prompt: grounding, citation, abstention rules    │
│  • Injects verified chunks + contradiction flags            │
│  • Returns: answer, sources[], contradictions[], abstained  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  LOGGING                                                    │
│  • Persist to query_logs table                             │
│  • Tracks: user_id, question, answer_json, abstained       │
└─────────────────────────────────────────────────────────────┘
```

---

## Access Level System

| Level | Label | Description |
|-------|-------|-------------|
| 1 | **Public** | Visible to everyone, including unauthenticated users |
| 2 | **Internal** | Visible to all employees (analysts, managers, executives) |
| 3 | **Confidential** | Visible to managers and executives only |
| 4 | **Restricted** | Visible to executives only (board-level data) |

**Enforcement rule:** A user with `clearance_level = N` may only see chunks where `chunk.access_level ≤ N`.

---

## Demo Users (seeded on startup)

| user_id | name | role | clearance_level | Can access |
|---------|------|------|----------------|------------|
| 1 | intern | Intern | 1 | Public docs only (IT security policy) |
| 2 | analyst | Analyst | 2 | Public + Internal |
| 3 | manager | Manager | 3 | Public + Internal + Confidential |
| 4 | executive | Executive | 4 | All documents |

---

## Corpus Files (backend/data/raw/)

| File | Type | Version | Date | Access Level | Notes |
|------|------|---------|------|-------------|-------|
| policy_handbook_v1_2022.pdf | PDF | 1.0 | 2022-01-01 | 2 (Internal) | Superseded by v2 |
| policy_handbook_v2_2024.pdf | PDF | 2.0 | 2024-03-01 | 2 (Internal) | Current policy |
| q3_sales_headcount.xlsx | XLSX | 1.0 | 2024-10-01 | 2 (Internal) | 3 sheets |
| it_security_policy.html | HTML | 3.2 | 2024-01-15 | 1 (Public) | All employees |
| vendor_contracts.csv | CSV | 1.0 | 2024-10-01 | 3 (Confidential) | Managers+ only |
| executive_compensation.pdf | PDF | 1.0 | 2024-01-01 | 4 (Restricted) | Executive only |
| annual_report_2021.pdf | PDF | 2021 | 2022-03-15 | 2 (Internal) | OUTDATED |
| annual_report_2024.pdf | PDF | 2024 | 2024-12-01 | 2 (Internal) | Current |

---

## 🔴 Planted Contradictions

These contradictions are intentionally embedded in the corpus to test the verification pipeline.

### Contradiction #1 – Remote Work Days

| | Source | Value |
|-|--------|-------|
| **Old (2022)** | `policy_handbook_v1_2022.pdf` § Remote Work | **2 days/week** |
| **New (2024)** | `policy_handbook_v2_2024.pdf` § Remote Work | **3 days/week** |

**Test query:** *"How many days per week can Acme Corp employees work remotely?"*

**Expected behaviour:** System should surface both values, flag the version conflict, and cite v2 as authoritative.

---

### Contradiction #2 – Daily Expense Limit (Domestic)

| | Source | Value |
|-|--------|-------|
| **Old (2022)** | `policy_handbook_v1_2022.pdf` § Expense Reimbursement | **$150/day** |
| **New (2024)** | `policy_handbook_v2_2024.pdf` § Expense Reimbursement | **$200/day** |

**Test query:** *"What is the maximum daily expense reimbursement for domestic travel?"*

**Expected behaviour:** Flag v1 as superseded, cite v2's $200 limit as current.

---

### Contradiction #3 – Company Headcount

| | Source | Value |
|-|--------|-------|
| **Outdated (2021)** | `annual_report_2021.pdf` § Workforce | **290 employees** |
| **Current (2024)** | `q3_sales_headcount.xlsx` Sheet: Headcount + `annual_report_2024.pdf` | **312 employees** |

**Test query:** *"What is Acme Corp's current headcount?"*

**Expected behaviour:** Flag the 2021 report as outdated/superseded, return 312 from current sources.

---

### Contradiction #4 – Q3 Revenue Label Ambiguity

| | Source | Value |
|-|--------|-------|
| **Old context** | `annual_report_2021.pdf` § Financial Highlights | Annual Revenue 2021: **$3.1 M** |
| **New context** | `q3_sales_headcount.xlsx` + `annual_report_2024.pdf` | Q3 2024 Revenue: **$4.2 M** |

**Test query:** *"What was Acme Corp's Q3 revenue?"* (without specifying year)

**Expected behaviour:** System should surface both, flag the temporal ambiguity (2021 annual vs 2024 Q3), and ask for year clarification or present both values with dates.

---

## Retrieval Pipeline Details

### Hybrid Search (RRF Fusion)

```
Dense candidates (FAISS top-K)  ─┐
                                  ├─► RRF Fusion ─► Reranker ─► Top-N chunks
BM25 candidates (BM25 top-K)   ─┘
```

**RRF formula:** `score(d) = Σ 1 / (k + rank_i(d))`  where `k = 60`

### Contradiction Detection Algorithm

1. For every pair of top-N retrieved chunks that share a semantic topic:
   - Compare `doc_date` fields — flag if dates differ by > 180 days
   - Compare `version` fields — flag if versions differ on same document family
   - Run NLI or embedding-similarity check for factual inconsistency

2. Pass `contradictions[]` list to Claude in the system prompt with instruction to acknowledge conflicts and cite the most recent/authoritative source.

---

## Abstention Rules

The Claude system prompt instructs the model to abstain (return `abstained: true`) when:

- No retrieved chunk has similarity above threshold
- All relevant chunks are above the user's clearance level
- The question requires synthesis across contradictory sources without a clear authoritative resolution

---

## Development Notes

- **Python version:** 3.11+
- **Database migrations:** Use Alembic (`alembic init alembic`, `alembic revision --autogenerate`)
- **FAISS index:** Rebuilt by running the ingestion pipeline; persisted to `backend/data/index/`
- **BM25 index:** Rebuilt in-memory at startup from all chunk texts
- **Model loading:** `sentence-transformers` downloads models to `~/.cache/huggingface/` on first use
