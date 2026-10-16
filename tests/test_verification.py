import pytest
from app.generation.answer import GeneratedClaim
from app.retrieval.hybrid import RetrievedChunk
from app.verification.verifier import verify_single_claim, verify_claims

@pytest.mark.asyncio
async def test_verifier_catches_false_claim():
    # Real chunk text about IT Security password requirements
    chunk = RetrievedChunk(
        chunk_id=1,
        document_id=1,
        title="Acme Corp IT Security Policy",
        source="it_security_policy.html",
        version="2.1",
        doc_date="2024-01-15",
        page_or_row="section 2",
        access_level=1,
        allowed_roles=None,
        text="[Acme Corp IT Security Policy | v2.1 | 2024-01-15] All employee passwords must be a minimum of 12 characters, including uppercase, lowercase, numbers, and special symbols.",
    )
    chunk_map = {"E1": chunk}

    # 1. True claim supported by text
    true_claim = GeneratedClaim(
        claim_text="Employee passwords must be at least 12 characters under the IT Security Policy.",
        citation_ids=["E1"],
        importance="high"
    )
    result_true = await verify_single_claim(true_claim, chunk_map)
    assert result_true.verdict == "SUPPORTED", f"Expected SUPPORTED, got {result_true.verdict}"
    assert result_true.supporting_span is not None

    # 2. False / hallucinated claim contradicted or absent from text
    false_claim = GeneratedClaim(
        claim_text="Employees are permitted to use 4-character passwords written on physical sticky notes.",
        citation_ids=["E1"],
        importance="high"
    )
    result_false = await verify_single_claim(false_claim, chunk_map)
    assert result_false.verdict == "UNSUPPORTED", f"Verifier failed to catch false claim! Got: {result_false.verdict}"

    # 3. Fabricated numbers not in chunk
    invented_numeric_claim = GeneratedClaim(
        claim_text="The minimum password length is 45 characters with 9 factor authentication.",
        citation_ids=["E1"],
        importance="high"
    )
    result_invented = await verify_single_claim(invented_numeric_claim, chunk_map)
    assert result_invented.verdict == "UNSUPPORTED", f"Verifier failed to catch fabricated claim! Got: {result_invented.verdict}"

    # 4. Multi-claim verification confidence drops when false claim is present
    batch_res = await verify_claims([true_claim, false_claim], chunk_map)
    assert batch_res.all_supported is False
    assert batch_res.confidence == 0.5, f"Expected 0.5 confidence for 1/2 supported, got {batch_res.confidence}"
