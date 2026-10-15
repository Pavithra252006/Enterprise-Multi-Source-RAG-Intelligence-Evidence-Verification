"""
scripts/verify_ask.py – Terminal verification of Phase 4 requirements:
(a) Remote-work policy question returns both versions as a conflict and prefers v2.
(b) Executive compensation question:
    - Intern (clearance 1) ABSTAINS with "Insufficient evidence in the sources you can access"
    - Executive (clearance 4) GETS a cited answer.
(c) Out-of-scope question ABSTAINS with "Insufficient evidence in the sources you can access".
"""
import asyncio
import json
from httpx import ASGITransport, AsyncClient
from app.main import app


async def test_phase4():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("=" * 80)
        print("PHASE 4: ANSWER GENERATION, VERIFICATION, CONFLICTS & ABSTENTION")
        print("=" * 80)

        # ----------------------------------------------------------------------
        # TEST A: Remote-work policy conflict
        # ----------------------------------------------------------------------
        print("\n[TEST A] Question: 'How many days per week can Acme Corp employees work remotely?' (as Executive)")
        print("-" * 80)
        res_a = await client.post(
            "/ask",
            headers={"X-User-Id": "executive"},
            json={"question": "How many days per week can Acme Corp employees work remotely?", "top_k": 5},
        )
        assert res_a.status_code == 200
        data_a = res_a.json()
        print(f"Answer: {data_a['answer']}")
        print(f"Abstained: {data_a['abstained']} | Confidence: {data_a['confidence']}")
        print(f"Claims count: {len(data_a['claims'])}")
        for cl in data_a["claims"]:
            print(f"  - Claim: {cl['text']}")
            print(f"    Verdict: {cl['verdict']} | Reason: {cl['reason']}")
            for cit in cl.get("citations", []):
                print(f"    Citation: [{cit['id']}] {cit['title']} (v{cit['version']}) {cit['location']}")

        print(f"Conflicts detected: {len(data_a['conflicts'])}")
        for cf in data_a["conflicts"]:
            print(f"  * Topic: {cf['topic']}")
            print(f"    Side A: {cf['side_a']['source']} (v{cf['side_a']['version']}) -> {cf['side_a']['value']}")
            print(f"    Side B: {cf['side_b']['source']} (v{cf['side_b']['version']}) -> {cf['side_b']['value']}")
            print(f"    Resolution: {cf['resolution']}")
            print(f"    Explanation: {cf['explanation']}")

        assert len(data_a["conflicts"]) > 0, "Expected a conflict to be detected for remote work policy"
        assert any("v2" in cf["resolution"].lower() or "prefer" in cf["resolution"].lower() for cf in data_a["conflicts"]), "Expected resolution to prefer newer version (v2)"

        # ----------------------------------------------------------------------
        # TEST B: Executive compensation – Intern vs Executive
        # ----------------------------------------------------------------------
        q_exec = "What is the executive compensation package and base salary for 2024?"
        print(f"\n[TEST B.1] Question: '{q_exec}' as INTERN (Clearance 1)")
        print("-" * 80)
        res_b1 = await client.post(
            "/ask",
            headers={"X-User-Id": "intern"},
            json={"question": q_exec, "top_k": 5},
        )
        assert res_b1.status_code == 200
        data_b1 = res_b1.json()
        print(f"Answer: {data_b1['answer']}")
        print(f"Abstained: {data_b1['abstained']} | Confidence: {data_b1['confidence']}")
        assert data_b1["abstained"] is True, "Intern MUST abstain on restricted executive compensation"
        assert data_b1["answer"] == "Insufficient evidence in the sources you can access.", f"Unexpected abstention message: {data_b1['answer']}"
        assert len(data_b1["claims"]) == 0

        print(f"\n[TEST B.2] Question: '{q_exec}' as EXECUTIVE (Clearance 4)")
        print("-" * 80)
        res_b2 = await client.post(
            "/ask",
            headers={"X-User-Id": "executive"},
            json={"question": q_exec, "top_k": 5},
        )
        assert res_b2.status_code == 200
        data_b2 = res_b2.json()
        print(f"Answer: {data_b2['answer']}")
        print(f"Abstained: {data_b2['abstained']} | Confidence: {data_b2['confidence']}")
        print(f"Claims: {len(data_b2['claims'])}")
        for cl in data_b2["claims"]:
            print(f"  - [{cl['verdict']}] {cl['text']}")
            for cit in cl.get("citations", []):
                print(f"    Cited: [{cit['id']}] {cit['title']} | {cit['location']}")
        assert data_b2["abstained"] is False, "Executive should NOT abstain on executive compensation"
        assert len(data_b2["claims"]) > 0, "Executive should receive verified claims"
        assert any("650,000" in cl["text"] or "salary" in cl["text"].lower() for cl in data_b2["claims"])

        # ----------------------------------------------------------------------
        # TEST C: Out-of-scope question
        # ----------------------------------------------------------------------
        q_oos = "What is the capital city of Mars and its atmospheric temperature?"
        print(f"\n[TEST C] Out-of-scope Question: '{q_oos}' (as Executive)")
        print("-" * 80)
        res_c = await client.post(
            "/ask",
            headers={"X-User-Id": "executive"},
            json={"question": q_oos, "top_k": 5},
        )
        assert res_c.status_code == 200
        data_c = res_c.json()
        print(f"Answer: {data_c['answer']}")
        print(f"Abstained: {data_c['abstained']} | Confidence: {data_c['confidence']}")
        assert data_c["abstained"] is True, "Out-of-scope question MUST abstain"
        assert data_c["answer"] == "Insufficient evidence in the sources you can access.", f"Unexpected abstention message: {data_c['answer']}"

        print("\n" + "=" * 80)
        print("ALL THREE PHASE 4 SCENARIOS PASSED VERIFICATION!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_phase4())
