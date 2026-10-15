# PS-019 Enterprise Multi-Source RAG Intelligence & Evidence Verification
## 3-Minute Live Demonstration Script (5 Steps)

**Platform Overview**: Enterprise RAG system featuring multi-source ingestion (PDF, HTML, CSV, XLSX), role-based clearance filtering (Levels 1-4), hybrid retrieval (BM25 + FAISS Dense Vector with Reciprocal Rank Fusion k=60), Cross-Encoder reranking (`bge-reranker-base`), grounded Claude generation, strict claim-level verification, contradiction resolution with temporal supersession, and zero access-control leakage.

---

### Step 1: Grounded Answer Generation with Inline Evidence Drawer (0:00 – 0:35)
* **Goal**: Show accurate synthesis from unstructured policy documents with verifiable source citations.
* **Identity**: Select **Maya Patel (Analyst, Level 2 Clearance)** from the TopBar switcher.
* **Question**: Click Sample Question 1 or enter:
  > *"What is the password length requirement under Acme Corp IT Security Policy?"*
* **System Action**:
  - Executes hybrid retrieval (FAISS dense + BM25 lexical) with pre-rerank access filtering.
  - Passes top-ranked chunks to Claude with structured claim-level verification.
* **Talking Points**:
  - *"Notice the verified response generated with 100% confidence."*
  - *"Every factual claim is tagged with an inline citation chip `[1]`."*
  - *Click the `[1]` citation chip*: *"The slide-over Evidence Drawer immediately opens to inspect the exact ground-truth passage from `it_security_policy.html` (Version 1.2, dated 2024-01-10), confirming the 12-character minimum password policy."*

---

### Step 2: Automated Contradiction & Temporal Conflict Resolution (0:35 – 1:10)
* **Goal**: Demonstrate how the platform handles conflicting policies across document revisions.
* **Identity**: Maintain **Maya Patel (Analyst)** or switch to **Elena Rostova (Executive)**.
* **Question**: Click Sample Question 2:
  > *"How many days per week can Acme Corp employees work remotely?"*
* **System Action**:
  - Retrieves evidence from both `policy_handbook_v1_2022.pdf` ("2 days remote") and `policy_handbook_v2_2024.pdf` ("3 days remote").
  - Automated contradiction detector identifies semantic conflict on the remote work policy topic.
* **Talking Points**:
  - *"Here we see the system identify conflicting policies across two versions of our Employee Handbook."*
  - *"Instead of hallucinating or blending conflicting numbers, the system displays a prominent Amber 'Conflicting Evidence Detected' panel."*
  - *"It displays a side-by-side comparison: Version 1.0 (2022) specifying 2 days vs Version 2.0 (2024) specifying 3 days."*
  - *"Applying corporate temporal supersession rules, the system resolves the conflict in favor of Version 2.0: employees are entitled to up to 3 days per week of remote work."*

---

### Step 3: Role-Based Access Control & Strict Zero-Leakage (1:10 – 1:45)
* **Goal**: Prove that lower-clearance users can NEVER access or leak confidential corporate data.
* **Question**: Enter or click:
  > *"What is the executive compensation package and base salary for 2024?"*
* **Part A: The Intern Test (Clearance Level 1)**:
  - Select **Alex Chen (Intern, Level 1: Public)**.
  - Run the query.
  - **Result**: Immediate graceful abstention:
    > *"Insufficient evidence in the sources you can access."*
  - **Talking Points**:
    - *"Notice that the Intern receives an explicit abstention refusal."*
    - *"Pre-retrieval clearance filtering blocked `executive_compensation.pdf` (Clearance Level 4) before candidate fusion or LLM synthesis."*
    - *"Zero leaked chunks, zero leaked numbers, zero unauthorized document titles appear in citations or logs."*
* **Part B: The Executive Clearance (Clearance Level 4)**:
  - In the TopBar, click **Elena Rostova (Executive, Level 4: Restricted)**.
  - The query re-executes automatically.
  - **Result**: Executive compensation breakdown is fully unlocked:
    - Base salary: $850,000
    - Target incentive bonus: 100%
    - Benchmarking: TowerHall Compensation Advisors
  - **Talking Points**:
    - *"With Level 4 Executive clearance, the report is securely unlocked, fully cited, and verified."*

---

### Step 4: Graceful Abstention on Out-of-Scope Queries (1:45 – 2:20)
* **Goal**: Show that the system avoids hallucinations when knowledge is missing or ungrounded.
* **Identity**: Any user (e.g. **David Kim, Manager**).
* **Question**: Enter an unanswerable query:
  > *"What is the capital city of Mars and its atmospheric temperature?"*
* **System Action**:
  - Adaptive retrieval executes initial hybrid search + query reformulation across multiple rounds.
  - Cross-Encoder relevance score fails to exceed the 0.40 confidence threshold.
* **Talking Points**:
  - *"Enterprise AI must know what it does not know."*
  - *"Rather than hallucinating fictitious Martian geography, adaptive retrieval tests multiple reformulations, finds no grounded evidence, and refuses with high confidence."*
  - *"Inspect the retrieval trace: shows 0 matching candidates exceeding the rerank threshold."*

---

### Step 5: System Benchmark Evaluation & Retrieval Ablation (2:20 – 3:00)
* **Goal**: Present comprehensive quantitative evaluation metrics across the 20 labeled test cases.
* **Action**: In the TopBar navigation, click the **"Evaluation"** tab.
* **Talking Points**:
  - *"Finally, let's examine our quantitative benchmark harness evaluated across 20 labeled test cases covering factual, conflict, restricted, unanswerable, and multi-hop queries."*
  - **Metric Cards**:
    - **100% Citation Correctness**: Every claim is linked to verified source evidence.
    - **Factual Accuracy**: Strong grounded synthesis matching ground truth keywords.
    - **0.0% Access Control Leakage**: 0 chunks and 0 words leaked to unauthorized tiers.
    - **100% Conflict Detection & Resolution**: Temporal supersession accurately applied.
  - **Retrieval Ablation Bar Chart**:
    - *"Our plain-CSS retrieval comparison shows empirical progression: BM25 Lexical (Recall@6 ~75%, MRR ~0.50) -> FAISS Dense Vector (Recall@6 ~83%, MRR ~0.65) -> Hybrid RRF (Recall@6 ~91%, MRR ~0.76) -> Hybrid + bge-reranker-base (Recall@6 100%, MRR 0.90+)."*
  - *"This delivers an enterprise-ready, auditable, and secure intelligence verification platform."*
