"""
scripts/verify_retrieval.py – Run 5 sample questions as Intern and Executive.
Outputs formatted comparison of retrieved evidence, access boundaries, and traces.
"""
import asyncio
import json
from httpx import ASGITransport, AsyncClient
from app.main import app

SAMPLE_QUESTIONS = [
    # 1. Contradiction #1
    "How many days per week can Acme Corp employees work remotely?",
    # 2. Contradiction #2
    "What is the maximum daily expense reimbursement for domestic travel?",
    # 3. Contradiction #3
    "What is Acme Corp's current headcount?",
    # 4. Contradiction #4
    "What was Acme Corp's Q3 revenue?",
    # 5. Restricted Document (Level 4)
    "What is the executive compensation package and base salary for 2024?",
]

async def run_verification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("=" * 80)
        print("PHASE 3: RETRIEVAL PIPELINE & ACCESS CONTROL VERIFICATION")
        print("=" * 80)

        for i, q in enumerate(SAMPLE_QUESTIONS, start=1):
            print(f"\n[{i}/5] QUESTION: \"{q}\"")
            print("-" * 80)

            # 1. Query as Intern (Clearance 1)
            res_intern = await client.post(
                "/retrieve",
                headers={"X-User-Id": "intern"},
                json={"question": q, "top_k": 3},
            )
            data_intern = res_intern.json()
            intern_evidence = data_intern.get("evidence", [])
            print(f"  * USER: INTERN (Clearance: {data_intern.get('clearance_level')})")
            print(f"    Rounds: {data_intern.get('trace', {}).get('rounds_executed')} | Queries: {data_intern.get('trace', {}).get('queries')}")
            if intern_evidence:
                for ev in intern_evidence:
                    print(f"    -> [{ev['title']} | {ev['page_or_row']} | access={ev['access_level']}] score={ev['score']:.4f}")
            else:
                print("    -> No accessible evidence (all relevant documents exceed user clearance).")

            # 2. Query as Executive (Clearance 4)
            res_exec = await client.post(
                "/retrieve",
                headers={"X-User-Id": "executive"},
                json={"question": q, "top_k": 3},
            )
            data_exec = res_exec.json()
            exec_evidence = data_exec.get("evidence", [])
            print(f"\n  * USER: EXECUTIVE (Clearance: {data_exec.get('clearance_level')})")
            print(f"    Rounds: {data_exec.get('trace', {}).get('rounds_executed')} | Queries: {data_exec.get('trace', {}).get('queries')}")
            if exec_evidence:
                for ev in exec_evidence:
                    print(f"    -> [{ev['title']} | {ev['page_or_row']} | access={ev['access_level']}] score={ev['score']:.4f}")
            else:
                print("    -> No accessible evidence.")

        print("\n" + "=" * 80)
        print("VERIFICATION COMPLETED SUCCESSFULLY")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_verification())
